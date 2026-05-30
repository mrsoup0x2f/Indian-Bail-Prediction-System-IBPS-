from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

print("akkar")
# Load the base model
base_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/phi-4", 
    torch_dtype=torch.bfloat16,
    # load_in_4bit=True, 
    # load_in_8bit=False,
    # llm_int8_threshold=6.0,
    # llm_int8_skip_modules=None,
    # llm_int8_enable_fp32_cpu_offload=False,
    # llm_int8_has_fp16_weight=False,
    # bnb_4bit_quant_type="nf4",
    # bnb_4bit_use_double_quant=True,
    # bnb_4bit_compute_dtype="bfloat16",
    device_map="auto"
)
print("bakkar")
tokenizer =  AutoTokenizer.from_pretrained("microsoft/phi-4", use_fast=False)

print("bambe")
# Load the adapter weights
model = PeftModel.from_pretrained(base_model,  "./data/phi4-bail-lora-final")  # Replace with your checkpoint path

# Merge LoRA weights (optional, for better inference speed)
model = model.merge_and_unload()
# print(type(model))

# Save the model and tokenizer externally
output_model_dir = "./data/phi-4_fine_tuned"  # Specify the directory where you want to save the model
model.save_pretrained(output_model_dir)
tokenizer.save_pretrained(output_model_dir)

print(f"Model and tokenizer saved at {output_model_dir}")

# device = torch.device("cuda:0")
# model.to(device)


# # Test with a prompt
# inputs = tokenizer("What charges could be applied if you insult indian tricolor flag?", return_tensors="pt").to(device)
# outputs = model.generate(**inputs, max_length=2700)

# print(tokenizer.decode(outputs[0], skip_special_tokens=True))

