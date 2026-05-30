import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "6,7"
# os.environ["TRANSFORMERS_CACHE"] = "/data/shubham/hf_cache"

import json
import torch
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
from datasets import Dataset
import pandas as pd
from torch.utils.data import DataLoader
import numpy as np

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
            # Get context and combine into a single paragraph
            context_list = item.get('context', [])
            if context_list and len(context_list) > 0:
                context_paragraph = ' '.join(context_list)
                context_section = f"Context: {context_paragraph}\n\n"
            else:
                context_section = ""

            # Check if this is a Regular-Bail application to include custody days
            is_regular_bail = "Regular-Bail" in case_details
            
            if is_regular_bail:
                days_in_custody = self.calculate_days_in_custody(
                    item.get("date_of_arrest", ""),
                    item.get("date_of_judgement", "")
                )
                user_content = f"""{context_section}Case Details: {case_details}
Days in Police Custody: {days_in_custody}

Based on the above case details and custody duration, provide the bail decision and reasoning."""
            else:
                # For non-Regular-Bail cases, don't include custody days
                user_content = f"""{context_section}Case Details: {case_details}

Based on the above case details, provide the bail decision and reasoning."""
            
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
    def __init__(self, model_name="microsoft/Phi-4", max_length=16384):
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
        """Tokenize the training examples"""
        # Tokenize the full text (input + output)
        tokenized = self.tokenizer(
            examples['full_text'],
            truncation=True,
            padding=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # For causal language modeling, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
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
    
    def train(self, train_dataset, output_dir="./phi4_bail_model_context", num_epochs=1):
        """Train the model"""
        print("Starting training...")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            #max_steps=1000,  # Adjust based on your dataset size
            learning_rate=2e-4,
            fp16=True,
            logging_steps=10,
            save_steps=200,
            eval_steps=200,
            save_total_limit=2,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            gradient_checkpointing=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            report_to=None,  # Disable wandb/tensorboard
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
    
#     def load_trained_model(self, model_path):
#         """Load a trained PEFT model"""
#         print(f"Loading trained model from {model_path}")
        
#         # Load base model
#         base_model = AutoModelForCausalLM.from_pretrained(
#             self.model_name,
#             torch_dtype=torch.float16,
#             device_map="auto",
#             trust_remote_code=True
#         )
        
#         # Load PEFT model
#         self.peft_model = PeftModel.from_pretrained(base_model, model_path)
#         self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
#         print("Model loaded successfully!")
    
#     def generate_response(self, case_details, days_in_custody=None, max_new_tokens=512):
#         """Generate bail judgment response"""
#         # Determine if this is regular bail based on case details
#         is_regular_bail = "Regular-Bail" in case_details if case_details else False
        
#         if is_regular_bail and days_in_custody is not None:
#             user_content = f"""Case Details: {case_details}
# Days in Police Custody: {days_in_custody}

# Based on the above case details and custody duration, provide the bail decision and reasoning."""
#         else:
#             user_content = f"""Case Details: {case_details}

# Based on the above case details, provide the bail decision and reasoning."""
        
#         input_text = f"""<|im_start|>system<|im_sep|>
# You are an expert legal assistant specializing in bail judgment analysis. Provide clear and structured bail decisions with proper reasoning based on case details.<|im_end|>
# <|im_start|>user<|im_sep|>
# {user_content}<|im_end|>
# <|im_start|>assistant<|im_sep|>
# """
        
#         inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1536)
#         inputs = {k: v.to(self.peft_model.device) for k, v in inputs.items()}
        
#         with torch.no_grad():
#             outputs = self.peft_model.generate(
#                 **inputs,
#                 max_new_tokens=max_new_tokens,
#                 temperature=0.7,
#                 do_sample=True,
#                 top_p=0.9,
#                 pad_token_id=self.tokenizer.eos_token_id,
#                 eos_token_id=self.tokenizer.encode("<|im_end|>")[0] if "<|im_end|>" in self.tokenizer.get_vocab() else self.tokenizer.eos_token_id
#             )
        
#         response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
#         # Extract only the generated part
#         generated_text = response[len(input_text):].strip()
        
#         # Remove the ending token if present
#         if generated_text.endswith("<|im_end|>"):
#             generated_text = generated_text[:-10].strip()
        
#         return generated_text

def main():
    # Configuration
    JSON_FILE_PATH = "train_data.json"  # Update with your file path
    MODEL_OUTPUT_DIR = "./phi4_bail_context_finetuned"
    
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
    train_dataset = trainer.prepare_dataset(processed_data)
    print(f"Dataset prepared with {len(train_dataset)} examples")
    
    # Step 4: Train the model
    print("\nStep 4: Training model...")
    trainer.train(train_dataset, output_dir=MODEL_OUTPUT_DIR, num_epochs=1)
    
    print("\n=== Training completed! ===")
    
main()
#     # Step 5: Test the model (optional)
#     print("\nStep 5: Testing the trained model...")
    
#     # Example test case - Regular Bail
#     test_case_regular = """Applicant applied for Regular-Bail.
# Is it a withdrawal application? No.
# Age of the accused is 35 years.
# Health issues for the accused are None.  
# There are no past criminal records of the accused.
# Statutes mentioned in the judgement are [Section 420 IPC, Section 406 IPC].
# Details of the incident are The accused allegedly cheated individuals by taking money for fake investment schemes."""
    
#     test_days = 45
    
#     response_regular = trainer.generate_response(test_case_regular, test_days)
#     print(f"\nRegular Bail Test:")
#     print(f"Case: {test_case_regular}")
#     print(f"Days in custody: {test_days}")
#     print(f"Generated Response: {response_regular}")
    
#     # Example test case - Other Bail Type
#     test_case_other = """Applicant applied for Anticipatory-Bail.
# Age of the accused is 28 years.
# Statutes mentioned in the judgement are [Section 498A IPC].
# Details of the incident are Domestic violence case filed by wife."""
    
#     response_other = trainer.generate_response(test_case_other)
#     print(f"\nAnticipatory Bail Test:")
#     print(f"Case: {test_case_other}")
#     print(f"Generated Response: {response_other}")

# # Usage for inference with VLLM (separate script)
# def create_vllm_inference_script():
#     vllm_script = '''
# # vllm_inference.py - Separate script for VLLM inference
# from vllm import LLM, SamplingParams
# import json

# class VLLMBailJudgment:
#     def __init__(self, model_path):
#         """Initialize VLLM with the fine-tuned model"""
#         self.llm = LLM(
#             model=model_path,
#             tensor_parallel_size=1,  # Adjust based on your GPU setup
#             dtype="float16",
#             trust_remote_code=True
#         )
        
#         self.sampling_params = SamplingParams(
#             temperature=0.7,
#             top_p=0.9,
#             max_tokens=512,
#             stop=["<|im_end|>", "\n\nCase Details:", "system<|im_sep|>"]
#         )
    
#     def predict_bail_outcome(self, case_details, days_in_custody=None):
#         """Predict bail outcome using VLLM"""
#         # Determine if this is regular bail
#         is_regular_bail = "Regular-Bail" in case_details if case_details else False
        
#         if is_regular_bail and days_in_custody is not None:
#             user_content = f"""Case Details: {case_details}
# Days in Police Custody: {days_in_custody}

# Based on the above case details and custody duration, provide the bail decision and reasoning."""
#         else:
#             user_content = f"""Case Details: {case_details}

# Based on the above case details, provide the bail decision and reasoning."""
        
#         prompt = f"""<|im_start|>system<|im_sep|>
# You are an expert legal assistant specializing in bail judgment analysis. Provide clear and structured bail decisions with proper reasoning based on case details.<|im_end|>
# <|im_start|>user<|im_sep|>
# {user_content}<|im_end|>
# <|im_start|>assistant<|im_sep|>
# """
        
#         outputs = self.llm.generate([prompt], self.sampling_params)
        
#         result = outputs[0].outputs[0].text.strip()
        
#         # Clean up the response
#         if result.endswith("<|im_end|>"):
#             result = result[:-10].strip()
            
#         return result

# # Example usage
# if __name__ == "__main__":
#     model_path = "./phi4_bail_finetuned"  # Your fine-tuned model path
    
#     predictor = VLLMBailJudgment(model_path)
    
#     # Test case - Regular Bail
#     regular_case = "Applicant applied for Regular-Bail. Accused involved in financial fraud case..."
#     days = 30
    
#     result_regular = predictor.predict_bail_outcome(regular_case, days)
#     print(f"Regular Bail Prediction: {result_regular}")
    
#     # Test case - Other Bail Type
#     other_case = "Applicant applied for Anticipatory-Bail. Domestic violence case..."
    
#     result_other = predictor.predict_bail_outcome(other_case)
#     print(f"Other Bail Prediction: {result_other}")
# '''
    
#     with open("vllm_inference.py", "w") as f:
#         f.write(vllm_script)
#     print("VLLM inference script created: vllm_inference.py")

# if __name__ == "__main__":
#     main()
#     create_vllm_inference_script()