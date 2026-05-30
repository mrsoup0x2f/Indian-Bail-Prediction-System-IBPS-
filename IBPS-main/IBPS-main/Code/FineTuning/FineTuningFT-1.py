import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "3"
#os.environ["TRANSFORMERS_CACHE"] = "/data/shubham/hf_cache"
#os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json
import torch, gc
# torch.cuda.empty_cache()
# gc.collect()
from datetime import datetime
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
    PeftModel
)
from datasets import Dataset, load_from_disk
import pandas as pd
from torch.utils.data import DataLoader
import numpy as np
from transformers import BitsAndBytesConfig


class BailJudgmentDataProcessor:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path

        self.data = self.load_data()
        
    def load_data(self):
        """Load and process the JSON data"""
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def calculate_days_in_custody(self, date_arrest, date_judgment):
        """Calculate days between arrest and judgment"""
        # Handle unknown or blank dates
        if not date_arrest or not date_judgment or date_arrest.lower() == "unknown" or date_judgment.lower() == "unknown":
            return "Unknown"
        
        try:
            # Try DD-MM-YYYY format first
            try:
                arrest_date = datetime.strptime(date_arrest, "%d-%m-%Y")
                judgment_date = datetime.strptime(date_judgment, "%d-%m-%Y")
            except ValueError:
                # Try DD.MM.YYYY format
                try:
                    arrest_date = datetime.strptime(date_arrest, "%d.%m.%Y")
                    judgment_date = datetime.strptime(date_judgment, "%d.%m.%Y")
                except ValueError:
                    # Try other common formats
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y", "%d.%m.%y"]:
                        try:
                            arrest_date = datetime.strptime(date_arrest, fmt)
                            judgment_date = datetime.strptime(date_judgment, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        return "Unknown"
            
            days_diff = (judgment_date - arrest_date).days
            return max(0, days_diff)  # Ensure non-negative
            
        except Exception:
            return "Unknown"
    
    def prepare_training_data(self):
        """Prepare data for fine-tuning"""
        processed_data = []
        
        for item in self.data:
            case_details = item.get('case', '')
            
            # Check if this is a Regular-Bail application to include custody days
            is_regular_bail = "Regular-Bail" in case_details
            
            if is_regular_bail:
                days_in_custody = self.calculate_days_in_custody(
                    item.get("date_of_arrest", ""),
                    item.get("date_of_judgement", "")
                )
                
                user_content = f"The accused has been in custody for {days_in_custody} days." if days_in_custody != "Unknown" else ""  + f"""Case Details: {case_details}
Based on the above information, provide the bail decision and reasoning."""
            else:
                # For non-Regular-Bail cases, don't include custody days
                user_content = f"""Case Details: {case_details}

Based on the above information, provide the bail decision and reasoning."""
            
            # Create output text
            assistant_content = f"""Outcome: {item.get('outcome', '')}
Reasoning: {item.get('reasoning', '')}"""
            
            # Format using the specified chat template
            full_text = f"""<|im_start|>system<|im_sep|>
You are an expert legal assistant specializing in bail judgment analysis. Provide clear and structured bail decisions , bail conditions, with proper reasoning based on case details.<|im_end|>
<|im_start|>user<|im_sep|>
{user_content}<|im_end|>
<|im_start|>assistant<|im_sep|>
{assistant_content}<|im_end|>"""
            
            processed_data.append({
                'full_text': full_text
            })
        
        return processed_data

class BailJudgmentTrainer:
    def __init__(self, model_name="microsoft/phi-4", max_length=4096):
        self.model_name = model_name
        self.max_length = max_length
        self.tokenizer = None
        self.model = None
        self.peft_model = None
        
    def setup_model_and_tokenizer(self):
        """Initialize tokenizer and model"""
        print("Loading tokenizer and model...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map=None,
            trust_remote_code=True
        )
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map=None,
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )

        #self.model = torch.nn.DataParallel(self.model)
        print(f"Model loaded: {self.model_name}")
    
    def setup_peft(self):
        """Setup PEFT configuration with LoRA"""
        print("Setting up PEFT with LoRA...")
        
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,  # Rank
            lora_alpha=32,  # LoRA scaling parameter
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],  # Phi-4 attention modules
            bias="none",
        )
        
        self.peft_model = get_peft_model(self.model, peft_config)
        self.peft_model.print_trainable_parameters()
        
        return peft_config
    
    def tokenize_function(self, examples):
        """Highly optimized vectorized tokenization"""
        assistant_sep = '<|im_start|>assistant<|im_sep|>\n'
        
        # Batch process all texts
        full_tokenized = self.tokenizer(
            examples['full_text'],
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_attention_mask=True
        )
        
        # Vectorized label creation
        labels = []
        assistant_sep_encoded = self.tokenizer.encode(assistant_sep, add_special_tokens=False)
        
        for input_ids in full_tokenized['input_ids']:
            # Find assistant separator position efficiently
            input_len = 0
            for i in range(len(input_ids) - len(assistant_sep_encoded) + 1):
                if input_ids[i:i+len(assistant_sep_encoded)] == assistant_sep_encoded:
                    input_len = i + len(assistant_sep_encoded)
                    break
            
            # Create labels: -100 for input, actual tokens for output
            label = [-100] * input_len + input_ids[input_len:]
            
            # Handle padding tokens
            for j in range(len(label)):
                if input_ids[j] == self.tokenizer.pad_token_id:
                    label[j] = -100
                    
            labels.append(label)
        
        return {
            "input_ids": full_tokenized['input_ids'],
            "attention_mask": full_tokenized['attention_mask'],
            "labels": labels
        }

    
    def prepare_dataset(self, processed_data):
        """Convert processed data to HuggingFace Dataset"""
        # We only need the full_text for training - everything else is redundant
        dataset_dict = {
            'full_text': [item['full_text'] for item in processed_data]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        
        # Tokenize dataset
        tokenized_dataset = dataset.map(
            self.tokenize_function,
            batched=True,
            remove_columns=['full_text']  # Remove the text column after tokenization
        )
        
        return tokenized_dataset
    
    def train(self, train_dataset, output_dir="./phi4_bail_finetuned_long", num_epochs=1):
        """Train the model"""
        print("Starting training...")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=16,
            warmup_steps=100,
            max_steps=7550,  # Adjust based on your dataset size
            learning_rate=2e-4,
            fp16=True,
            logging_steps=10,
            save_steps=200,
            eval_steps=200,
            save_total_limit=2,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            #gradient_checkpointing=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            report_to=None,  # Disable wandb/tensorboard
            label_names=["labels"]      # <— add this!
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # We're doing causal LM, not masked LM
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.peft_model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
            
        )
        
        # Train
        trainer.train()
        
        # Save the model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        print(f"Model saved to {output_dir}")
    

def main():
    # Configuration
    JSON_FILE_PATH = "train_data.json"  # Update with your file path
    MODEL_OUTPUT_DIR = "./phi4_bail_finetuned_long"
    
    print("=== Phi-4 Bail Judgment Fine-tuning ===")
    
    # Step 1: Process the data
    print("Step 1: Processing data...")
    processor = BailJudgmentDataProcessor(JSON_FILE_PATH)
    processed_data = processor.prepare_training_data()
    print(f"Processed {len(processed_data)} training examples")
    
    # Step 2: Setup trainer
    print("\nStep 2: Setting up trainer...")
    trainer = BailJudgmentTrainer()
    trainer.setup_model_and_tokenizer()
    trainer.setup_peft()
    
    # Step 3: Prepare dataset
    print("\nStep 3: Preparing dataset...")
    # train_dataset = trainer.prepare_dataset(processed_data)
    # print(f"Dataset prepared with {len(train_dataset)} examples")
    # train_dataset.save_to_disk("train_dataset_masked_4096")

    #print("train_dataset saved to train_dataset_simple")
    train_dataset = load_from_disk("train_dataset_masked_4096")

    # with open("train_dataset_context.pkl", "rb") as f:
    #     train_dataset = pickle.load(f)
    print("train_dataset loaded from train_dataset_masked_4096")
    #Step 4: Train the model
    print("\nStep 4: Training model...")
    trainer.train(train_dataset, output_dir=MODEL_OUTPUT_DIR, num_epochs=1)
    
    print("\n=== Training completed! ===")
    
main()
# if __name__ == "__main__":
#     main()