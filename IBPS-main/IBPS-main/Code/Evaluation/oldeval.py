# %%

import nltk
nltk.download('wordnet', quiet=True)
import csv
from rapidfuzz import fuzz, process  # pip install rapidfuzz
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from rouge_score import rouge_scorer  # pip install rouge-score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from bert_score import score as bert_score  # pip install bert-score
import numpy as np
import re
from vllm import LLM, SamplingParams
import json
from datetime import datetime
import os
# Update outcome extraction for the new format
OUTCOME_REGEX_NEW = re.compile(
    r'Outcome status:\s*(Bail granted|Bail not granted|Bail cancelled|Bail not cancelled)', re.IGNORECASE
)

def extract_outcome_new_format(text):
    m = OUTCOME_REGEX_NEW.search(text)
    return m.group(1) if m else ""

# Update reasoning extraction for the new format
def extract_reasoning_new_format(output_text):
    pattern = re.compile(r"Reasoning:\s*([\s\S]*?)(?:\<\|im_end\|\>|$)", re.IGNORECASE)
    m = pattern.search(output_text)
    if m:
        return m.group(1).strip()
    if "Reasoning:" in output_text:
        return output_text.split("Reasoning:", 1)[-1].strip()
    return output_text.strip()

def extract_bail_conditions_new_format(output_text):
    """Extract bail conditions from the new format where each condition is on a separate line"""
    pattern = re.compile(r"Bail Conditions:\s*(.*?)(?:\nReasoning:|$)", re.IGNORECASE | re.DOTALL)
    m = pattern.search(output_text)
    if m:
        conditions_text = m.group(1).strip()
        # Split by lines and clean up
        lines = conditions_text.split('\n')
        conditions = []
        for line in lines:
            line = line.strip()
            # Remove bullet points or dashes at the beginning
            line = re.sub(r'^[-•*]\s*', '', line)
            if line:  # Only add non-empty lines
                conditions.append(line)
        return conditions
    return []


# %%
def calculate_days_in_custody(date_arrest, date_judgment):
    if not date_arrest or not date_judgment or \
       date_arrest.lower() == "unknown" or date_judgment.lower() == "unknown":
        return "Unknown"
    try:
        for fmt in ("%d-%m-%Y", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y", "%d.%m.%y"):
            try:
                arrest_date = datetime.strptime(date_arrest, fmt)
                judgment_date = datetime.strptime(date_judgment, fmt)
                break
            except ValueError:
                continue
        else:
            return "Unknown"
        days_diff = (judgment_date - arrest_date).days
        return max(0, days_diff)
    except Exception:
        return "Unknown"


# %%
SYSTEM_PROMPT = (
    "You are an expert legal assistant specializing in bail judgment analysis. Provide clear and structured bail decisions, bail conditions, with proper reasoning based on case details. "
    "Produce output in the exact same format as the following example for the input given."
)

EXAMPLE_INPUT = (
    "Type of application: Regular-Bail\n"
    "Statutes imposed: Section 406 IPC, Section 420 IPC, Section 34 IPC\n"
    "Number of days in custody: 41 days\n"
    "Age of accused: 44\n"
    "Health of accused: None\n"
    "Past criminal records: No\n"
    "Precedents: None\n"
    "Details of the incident: The accused, in furtherance of common intention with other co-accused, obtained spurious gold and pledged them in different financial institutions and with individuals, dishonestly inducing them to pay money. The fake gold could not be identified immediately due to a thick covering of gold plating and non-penetrative scan machines. The accused, including the applicant, visited financial institutions and individuals to physically pledge the gold ornaments, which were entrusted to him by two ladies and one Makkar.\n"
    "Arguments Supporting the application: The applicant has already been interrogated, and therefore, no purpose would be served by his incarceration. The learned Public Prosecutor admits that the applicant was subjected to interrogation but states that one of the main accused, Makkar, is yet to be identified and arrested. The ill-gotten money is yet to be recovered, and the accused persons' investments are unknown. The applicant has been incarcerated since 26.09.2020, and his interrogation is over. The only apprehension of the Prosecutor is that once he is released on bail, there is every possibility of his getting involved in offences of similar nature and also absconding. No purpose will be served by incarcerating a person for such a long period. The investigation is yet to be completed. The applicant can be prevented from not getting involved in other crimes by imposing certain stringent conditions.\n"
    "Arguments opposing the application: The learned Public Prosecutor admits that the applicant was subjected to interrogation but states that one of the main accused, Makkar, is yet to be identified and arrested. The ill-gotten money is yet to be recovered, and it is not understood where the accused persons have invested it. The learned Public Prosecutor has also pointed out that the applicant is also involved in other crimes; the details of which are not readily available. The only apprehension of the Prosecutor is that once he is released on bail, there is every possibility of his getting involved in offences of similar nature and also absconding."
)

EXAMPLE_OUTPUT = (
    "Outcome status: Bail granted\n"
    "Bail Conditions:\n"
    "- He shall appear before the investigating officers concerned on all Mondays between 9.00 AM and 12.00 noon in all the cases for a period of two months or till the final report is filed, whichever is earlier.\n"
    "- He shall not leave the jurisdiction of his residence without intimation to the investigating officers and permission of the jurisdictional court.\n"
    "- He shall surrender his passport in the jurisdictional court, and in case he does not have a passport, shall file an affidavit to that effect.\n"
    "- He shall not attempt to influence or intimidate the witnesses.\n"
    "- He shall not get involved in similar offences during the currency of the bail.\n"
    "Reasoning: The applicant has already been interrogated, and therefore, no purpose would be served by his incarceration. The learned Public Prosecutor admits that the applicant was subjected to interrogation but states that one of the main accused, Makkar, is yet to be identified and arrested. The ill-gotten money is yet to be recovered, and it is not understood where the accused persons have invested it. The applicant can be prevented from not getting involved in other crimes by imposing certain stringent conditions."
)


EXAMPLE_BLOCK = (
    f"<|im_start|>system<|im_sep|>\n{SYSTEM_PROMPT}<|im_end|>\n"
    f"<|im_start|>user<|im_sep|>\n"
    f"Based on the below case details, provide the bail decision, bail conditions and reasoning.\n\n"
    f"{EXAMPLE_INPUT}\n"
    "<|im_end|>\n"
    "<|im_start|>assistant<|im_sep|>\n"
    f"{EXAMPLE_OUTPUT}<|im_end|>\n"
)
def convert_structured_to_new_format(text_data):
    """Convert the structured JSON format to the new text format"""
    
    # Type of application
    app_type = text_data['type_of_application']
    
    # Statutes
    statutes = ', '.join(text_data['statutes'])
    
    # Days in custody
    days = calculate_days_in_custody(text_data['date_of_arrest'], text_data['date_of_judgement'])
    days_text = f"{days} days" if days != "Unknown" else "Unknown"
    
    # Age (first accused detail only)
    age = text_data['accused_details']['Age']
    age_text = str(age) if age != 0 else "Unknown"
    
    # Health (description part of first entry)
    health = text_data['accused_details']['health_info']['description']
    
    # Past criminal records
    criminal_records = text_data['past_criminal_records']
    
    # Precedents
    precedents = text_data['precendents'] if text_data['precendents'] else "None"
    if isinstance(precedents, list) and len(precedents) == 0:
        precedents = "None"
    elif isinstance(precedents, list):
        precedents = ', '.join(precedents)
    
    # Details of incident
    incident = text_data['details of the incident']
    
    # Arguments
    args_supporting = text_data['Arguments']['Arguments Supporting the application']
    args_opposing = text_data['Arguments']['Arguments opposing the application']
    
    # Format the input text
    formatted_input = (
        f"Type of application: {app_type}\n"
        f"Statutes imposed: {statutes}\n"
        f"Number of days in custody: {days_text}\n"
        f"Age of accused: {age_text}\n"
        f"Health of accused: {health}\n"
        f"Past criminal records: {criminal_records}\n"
        f"Precedents: {precedents}\n"
        f"Details of the incident: {incident}\n"
        f"Arguments Supporting the application: {args_supporting}\n"
        f"Arguments opposing the application: {args_opposing}"
    )
    
    return formatted_input

def build_actual_prompt_new_format(case_text):
    return (
        f"<|im_start|>user<|im_sep|>\n"
        f"Based on the below case details, provide the bail decision, bail conditions and reasoning.\n\n"
        f"{case_text}\n"
        "<|im_end|>\n"
        "<|im_start|>assistant<|im_sep|>\n"
    )

def full_prompt_new_format(record):
    case_text = convert_structured_to_new_format(record["text"])
    return EXAMPLE_BLOCK + build_actual_prompt_new_format(case_text)


# %%
def prepare_prompts_and_refs_updated_format(test_json_path):
    with open(test_json_path, "r", encoding='utf-8') as f:
        test_data = json.load(f)
    
    prompts, golds = [], []
    for ex in test_data:
        # Check if it's a withdrawal application
        if ex["text"]["application_for_withdrawal"].lower() == "yes":
            continue
            
        prompts.append(full_prompt_new_format(ex))
        golds.append({
            "outcome": ex["text"]["outcome"]["status"],
            "reasoning": " ".join(ex["text"]["Reasoning"]) if isinstance(ex["text"]["Reasoning"], list) else ex["text"]["Reasoning"],
            "bail_conditions": ex["text"]["outcome"]["bail_conditions"]
        })
    return prompts, golds

def run_vllm_batch(prompts, model_path, max_tokens=1024, batch_size=32):
    llm = LLM(model=model_path, tokenizer="microsoft/phi-4",dtype="float16", tensor_parallel_size=1)
    sampling_params = SamplingParams(temperature=0.0, max_tokens=max_tokens, stop=["<|im_end|>"])
    outputs = []
    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i+batch_size]
        results = llm.generate(batch_prompts, sampling_params)
        outputs.extend([o.outputs[0].text for o in results])
    return outputs

def evaluate_bail_system(examples):
    """
    Complete evaluation function for legal bail decision system
    
    Args:
        examples: List of dictionaries with keys:
                 'cnr', 'actual_outcome', 'predicted_outcome',
                 'actual_reasoning', 'predicted_reasoning',
                 'actual_bail_conditions', 'predicted_bail_conditions'
    """
    
    # 1. OUTCOME EVALUATION: Accuracy, Precision, Recall, F1
    actual_outcomes = [ex["actual_outcome"] for ex in examples]
    predicted_outcomes = [ex["predicted_outcome"] for ex in examples]
    
    accuracy = accuracy_score(actual_outcomes, predicted_outcomes)
    precision, recall, f1, _ = precision_recall_fscore_support(
        actual_outcomes, predicted_outcomes, average='macro', zero_division=0
    )
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import confusion_matrix

    # Assuming actual_outcomes and predicted_outcomes are defined as in your snippet

    # Compute confusion matrix
    cm = confusion_matrix(actual_outcomes, predicted_outcomes)
    labels = sorted(list(set(actual_outcomes) | set(predicted_outcomes)))  # Unique sorted labels

    # Plot confusion matrix as heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.xlabel('Predicted Outcome')
    plt.ylabel('Actual Outcome')
    plt.title('Confusion Matrix')
    plt.tight_layout()

    # Save confusion matrix figure
    plt.savefig("confusion_matrix_newft.png")  # Save to PNG file
    plt.show()  # Display if running interactively

    
    # 2. CREATE CSV FILE
    csv_filename = 'outcomes_newft.csv'
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['cnr', 'actual_outcome', 'predicted_outcome'])
        for ex in examples:
            writer.writerow([ex['cnr'], ex['actual_outcome'], ex['predicted_outcome']])
    
    # 3. REASONING EVALUATION: ROUGE-1, ROUGE-2, ROUGE-L, BLEU, METEOR, BERTScore, BLANC
    rouge_scorer_inst = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    rouge1_scores, rouge2_scores, rougeL_scores = [], [], []
    bleu_scores, meteor_scores = [], []
    
    for ex in examples:
        ref = ex["actual_reasoning"]
        pred = ex["predicted_reasoning"]
        
        # ROUGE scores
        rouge_scores = rouge_scorer_inst.score(ref, pred)
        rouge1_scores.append(rouge_scores['rouge1'].fmeasure)
        rouge2_scores.append(rouge_scores['rouge2'].fmeasure)
        rougeL_scores.append(rouge_scores['rougeL'].fmeasure)
        
        # BLEU score
        bleu = sentence_bleu([ref.split()], pred.split(), 
                           smoothing_function=SmoothingFunction().method1)
        bleu_scores.append(bleu)
        
        # METEOR score
        meteor_scores.append(meteor_score([ref.split()], pred.split()))
    
    # BERTScore for reasoning
    refs_reasoning = [ex['actual_reasoning'] for ex in examples]
    preds_reasoning = [ex['predicted_reasoning'] for ex in examples]
    P_r, R_r, F1_r = bert_score(cands=preds_reasoning, refs=refs_reasoning, 
                               lang='en', rescale_with_baseline=True)
    bertscore_reasoning = float(F1_r.mean())
    
    # BLANC for reasoning (simplified as BLEU average for now)
    #blanc_reasoning = np.mean(bleu_scores)
    
    # 4. BAIL CONDITIONS EVALUATION: BLEU, METEOR, BLANC, BERTScore
    bleu_bail_scores, meteor_bail_scores = [], []
    
    for ex in examples:
        ref_conditions = ex['actual_bail_conditions']
        pred_conditions = ex['predicted_bail_conditions']
        
        # Join conditions to single strings for scoring
        ref = ' '.join(ref_conditions)
        pred = ' '.join(pred_conditions)
        
        # BLEU for bail conditions
        bleu_bail = sentence_bleu([ref.split()], pred.split(), 
                                smoothing_function=SmoothingFunction().method1)
        bleu_bail_scores.append(bleu_bail)
        
        # METEOR for bail conditions
        meteor_bail_scores.append(meteor_score([ref.split()], pred.split()))
    
    # BERTScore for bail conditions
    refs_bail = [' '.join(ex['actual_bail_conditions']) for ex in examples]
    preds_bail = [' '.join(ex['predicted_bail_conditions']) for ex in examples]
    P_b, R_b, F1_b = bert_score(cands=preds_bail, refs=refs_bail, 
                               lang='en', rescale_with_baseline=True)
    bertscore_bail = float(F1_b.mean())
    
    # BLANC for bail conditions (simplified as BLEU average)
    #blanc_bail = np.mean(bleu_bail_scores)
    
    return {
        "outcome_metrics": {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        },
        "csv_file": csv_filename,
        "reasoning_metrics": {
            "rouge1": np.mean(rouge1_scores),
            "rouge2": np.mean(rouge2_scores),
            "rougeL": np.mean(rougeL_scores),
            "bleu": np.mean(bleu_scores),
            "meteor": np.mean(meteor_scores),
            "bertscore": bertscore_reasoning
            #"blanc": blanc_reasoning
        },
        "bail_conditions_metrics": {
            "bleu": np.mean(bleu_bail_scores),
            "meteor": np.mean(meteor_bail_scores),
            "bertscore": bertscore_bail,
            #"blanc": blanc_bail
        }
    }
def extract_bail_type(case_text):
    pattern = r'\b(Regular-Bail|Anticipatory-Bail|Bail-Cancellation)\b'
    match = re.search(pattern, case_text, re.IGNORECASE)
    if match:
        return match.group(1).title()  # Normalize casing if needed
    return None
# Example usage with your existing code integration:
def main():
    test_json = "evaluation/new100_GoldSTD.json"
    model_path = "Split_Data/phi4-bail-lora-final-merged"
    
    # Use the updated format preparation function
    prompts, refs = prepare_prompts_and_refs_updated_format(test_json)
    pred_texts = run_vllm_batch(prompts, model_path)

    # Save prompts and predictions for debugging
    with open("evaluation/updated_format_eval.txt", "w", encoding="utf-8") as f:
        for i, (prompt, pred) in enumerate(zip(prompts, pred_texts)):
            f.write(f"--- Prompt {i+1} ---\n")
            f.write(prompt.strip() + "\n")
            f.write(f"--- Prediction {i+1} ---\n")
            f.write(pred.strip() + "\n\n")

    # Load data for metadata
    with open(test_json, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    # Filter out withdrawal applications
    filtered_data = [ex for ex in test_data if ex["text"]["application_for_withdrawal"].lower() != "yes"]
    
    cnrs = [item['cnr'] for item in filtered_data]
    bail_types = [item['text']['type_of_application'] for item in filtered_data]

    # Extract predictions using updated functions
    pred_outcomes = [extract_outcome_new_format(t) for t in pred_texts]
    pred_reasonings = [extract_reasoning_new_format(t) for t in pred_texts]
    pred_conditions = [extract_bail_conditions_new_format(t) for t in pred_texts]
    
    # Reference data
    ref_outcomes = [item['text']['outcome']['status'] for item in filtered_data]
    ref_reasonings = [" ".join(item['text']['Reasoning']) if isinstance(item['text']['Reasoning'], list) 
                     else item['text']['Reasoning'] for item in filtered_data]
    ref_conditions = [item['text']['outcome']['bail_conditions'] for item in filtered_data]
    
    # Prepare evaluation data
    examples = []
    for i in range(len(prompts)):
        examples.append({
            'cnr': cnrs[i],
            'bail_type': bail_types[i],
            'actual_outcome': ref_outcomes[i],
            'predicted_outcome': pred_outcomes[i],
            'actual_reasoning': ref_reasonings[i],
            'predicted_reasoning': pred_reasonings[i],
            'actual_bail_conditions': ref_conditions[i],
            'predicted_bail_conditions': pred_conditions[i]
        })
    
    # Run evaluation (same as before)
    results = evaluate_bail_system(examples)
    
    # Print results
    print("\n===== COMPREHENSIVE EVALUATION RESULTS (Updated Format) =====")
    print(f"\n1. OUTCOME METRICS:")
    print(f"   Accuracy: {results['outcome_metrics']['accuracy']:.4f}")
    print(f"   Precision: {results['outcome_metrics']['precision']:.4f}")
    print(f"   Recall: {results['outcome_metrics']['recall']:.4f}")
    print(f"   F1-Score: {results['outcome_metrics']['f1']:.4f}")
    
    print(f"\n2. REASONING METRICS:")
    for metric, value in results['reasoning_metrics'].items():
        print(f"   {metric.upper()}: {value:.4f}")
    
    print(f"\n3. BAIL CONDITIONS METRICS:")
    for metric, value in results['bail_conditions_metrics'].items():
        print(f"   {metric.upper()}: {value:.4f}")

if __name__ == "__main__":
    main()



