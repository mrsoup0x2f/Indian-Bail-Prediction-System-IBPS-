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
OUTCOME_REGEX = re.compile(
    r'The outcome of the case is (Bail granted|Bail not granted|Bail cancelled|Bail not cancelled)', re.IGNORECASE
)

def extract_outcome(text):
    m = OUTCOME_REGEX.search(text)
    # query = text.lower()
    # possible_outcomes = ["bail granted", "bail not granted", "bail cancelled", "bail not cancelled"]
    # match = process.extractOne(query, possible_outcomes, scorer=fuzz.partial_ratio)
    return m.group(1) if m else ""
    # return match[0].capitalize()

def extract_reasoning(output_text):
    pattern = re.compile(r"Reasoning:([\s\S]*?)(?:\nThe outcome of the case|\<\|im_end\|\>|$)", re.IGNORECASE)
    m = pattern.search(output_text)
    if m:
        return m.group(1).strip()
    if "Reasoning:" in output_text:
        return output_text.split("Reasoning:",1)[-1].strip()
    return output_text.strip()


def extract_bail_conditions(outcome_text):
    pattern = re.compile(r"The bail conditions are\s+(.*?)(?:\nReasoning:|$)", re.IGNORECASE | re.DOTALL)
    m = pattern.search(outcome_text)    
    if m:
        return [s.strip() for s in m.group(1).split('.') if s.strip()]
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
"You are an expert legal assistant specializing in bail judgment analysis. Provide clear and structured bail decisions, bail conditions, with proper reasoning based on case details."
    "Produce output in the exact same format as the following example for the input given."
)
EXAMPLE_CASE = "Applicant applied for Regular-Bail.\nIs it a withdrawal application? No.\nAge of the accused is unknown.\nHealth issues for the accused are None.\nThere are no past criminal records of the accused.\nStatutes mentioned in the judgement are [Section 409 IPC, Section 420 IPC, Section 465 IPC, Section 468 IPC, Section 471 IPC, Section 34 IPC].\nPrecedents mentioned in the judgement are Velji Raghavji Patel V. State of Maharashtra 1 AIR 1965 SC 1433, State of Gujarat Vs. Vora Jayantilal Chhotalal and Ors. 2 (1975) 16GLR661.\nDetails of the incident are The applicant, Rajeshkumar Ghisulal Munot, is accused of criminal breach of trust and other charges related to the business of sale and purchase of gold in partnership with the informant. Allegations include misappropriation of gold and false entries in the Day Register.\nArguments supporting the bail application are Before invoking the offence of criminal breach of trust, it must be established that the person was entrusted with dominion over property, which he is said to have converted to his own use. The mere existence of dominion over property by a partner is not enough; it must be shown that this dominion was the result of entrustment. The prosecution must establish that dominion over the assets or a particular aspect of the partnership was entrusted to the accused person by a special agreement.\nArguments opposing the bail application are The State argued that the Applicant, as a partner, was involved in misappropriation and false entries, causing financial loss to the informant. The State relied on the decision of Gujarat High Court in State of Gujarat Vs. Vora Jayantilal Chhotalal and Ors., but the court noted that the decision concedes to the position that the decision in Velji Raghavji Patel still continues to be binding law."
EXAMPLE_DAYS = "683"
EXAMPLE_OUTCOME = "The outcome of the case is Bail granted. The bail conditions are Applicant shall be released on bail in C.R.No.281 of 2019 on furnishing P.R. bond to the extent of Rs.25,000/- with one or two sureties of the like amount. The Applicant shall not directly or indirectly make any inducement, threat or promise to any person acquainted with facts of case so as to dissuade him from disclosing the facts to Court or any Police Officer and shall not tamper with the prosecution evidence. The Applicant shall report to the concerned Police Station on first Thursday of every month between 10.00 a.m. and 2.00 p.m. till framing of the charge and thereafter he shall abide by the directions issued by the Trial Court."
EXAMPLE_REASON = "The ingredients of Section 405 cannot be said to be made out prima facie. The offence under Section 405 can be said to be committed by a person in respect of the property, which has been specifically entrusted by another person and which he owns in a fiduciary capacity. The position of law clearly emerging is that the partner cannot be held liable only because he is a partner and, therefore, has dominion over the partnership property or monies. The entrustment of the property has to be proved by demonstrating that he was in-charge of the partnership property or monies and it must exist in form of a special agreement, which is conspicuously absent in the present case."
EXAMPLE_BLOCK = (
    f"<|im_start|>system<|im_sep|>\n{SYSTEM_PROMPT}<|im_end|>\n"
    f"<|im_start|>user<|im_sep|>\n"
    f"Based on the below case details, provide the bail decision, bail conditions and reasoning.\n"
    f"Case Details: {EXAMPLE_CASE}\n"
    f"Days in Police Custody: {EXAMPLE_DAYS}\n\n"
    "<|im_end|>\n"
    "<|im_start|>assistant<|im_sep|>\n"
    f"Outcome: {EXAMPLE_OUTCOME}\nReasoning: {EXAMPLE_REASON}<|im_end|>\n"
)

def build_actual_prompt(case_txt, days):
    return (
        f"<|im_start|>user<|im_sep|>\n"
        f"Based on the below case details, provide the bail decision and reasoning.\n"
        f"Case Details: {case_txt}\n"
        f"Days in Police Custody: {days}\n\n"        
    )

def full_prompt(record):
    context_list = record.get('context', [])
    if context_list and len(context_list) > 0:
        context_paragraph = ' '.join(context_list)
        context_section = f"Context: {context_paragraph}\n\n"
    else:
        context_section = ""
    reg_bail = "Regular-Bail" in record.get("case", "")
    days = calculate_days_in_custody(record.get("date_of_arrest", ""), record.get("date_of_judgement", "")) if reg_bail else "Unknown"
    return EXAMPLE_BLOCK + build_actual_prompt(record["case"], days) + f"{context_section} <|im_end|>\n<|im_start|>assistant<|im_sep|>\n"


# %%
def prepare_prompts_and_refs(test_json_path):
    with open(test_json_path, "r", encoding='utf-8') as f:
        test_data = json.load(f)
    prompts, golds = [], []
    for ex in test_data:
        if "Is it a withdrawal application? Yes." in ex["case"]:
            continue
        prompts.append(full_prompt(ex))
        golds.append({
            "outcome": ex["outcome"],
            "reasoning": ex["reasoning"],
            "bail_conditions": extract_bail_conditions(ex["outcome"])
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
    plt.savefig("confusion_matrix_newftrag.png")  # Save to PNG file
    plt.show()  # Display if running interactively

    
    # 2. CREATE CSV FILE
    csv_filename = 'outcomes_newftrag.csv'
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

# Example usage with your existing code integration:
def main():
    test_json = "evaluation/100_GoldSTD.json"
    legal_eval_json = "evaluation/legal_expert.json"  # Path to your evaluation data
    model_path = "Split_Data/phi4_bail_finetuned_long-merged"  # Path to your finetuned model dir
    
    # Use your existing prompt preparation and model inference functions
    prompts, refs = prepare_prompts_and_refs(test_json)
    prompts2, refs2 = prepare_prompts_and_refs(legal_eval_json)
    pred_texts = run_vllm_batch(prompts, model_path)

    with open("evaluation/newfteval_newftrag.txt", "w", encoding="utf-8") as f:
        for i, (prompt, pred) in enumerate(zip(prompts, pred_texts)):
            f.write(f"--- Prompt {i+1} ---\n")
            f.write(prompt.strip() + "\n")
            f.write(f"--- Prediction {i+1} ---\n")
            f.write(pred.strip() + "\n\n")
    # Load the legal_eval_json file to get the list of dicts
    with open(legal_eval_json, "r", encoding="utf-8") as f:
        legal_eval_data = json.load(f)
    cnrs = [item['CNR'] for item in legal_eval_data]
    # Extract fields using your existing functions
    pred_outcomes = [extract_outcome(t) for t in pred_texts]
    pred_reasonings = [extract_reasoning(t) for t in pred_texts]
    pred_conditions = [extract_bail_conditions(t) for t in pred_texts]
    
    ref_outcomes = [extract_outcome(t['outcome']) for t in refs2]
    ref_reasonings = [t['reasoning'] for t in refs2]
    ref_conditions = [t['bail_conditions'] for t in refs2]
    
    # Prepare data for evaluation
    examples = []
    for i in range(len(prompts)):
        examples.append({
            'cnr': cnrs[i],  # Or extract actual CNR if available
            'actual_outcome': ref_outcomes[i],
            'predicted_outcome': pred_outcomes[i],
            'actual_reasoning': ref_reasonings[i],
            'predicted_reasoning': pred_reasonings[i],
            'actual_bail_conditions': ref_conditions[i],
            'predicted_bail_conditions': pred_conditions[i]
        })
    
    # Run comprehensive evaluation
    results = evaluate_bail_system(examples)
    
    # Print results
    print("\n===== COMPREHENSIVE EVALUATION RESULTS =====")
    print(f"\n1. OUTCOME METRICS:")
    print(f"   Accuracy: {results['outcome_metrics']['accuracy']:.4f}")
    print(f"   Precision: {results['outcome_metrics']['precision']:.4f}")
    print(f"   Recall: {results['outcome_metrics']['recall']:.4f}")
    print(f"   F1-Score: {results['outcome_metrics']['f1']:.4f}")
    print(f"   CSV File: {results['csv_file']}")
    
    print(f"\n2. REASONING METRICS:")
    for metric, value in results['reasoning_metrics'].items():
        print(f"   {metric.upper()}: {value:.4f}")
    
    print(f"\n3. BAIL CONDITIONS METRICS:")
    for metric, value in results['bail_conditions_metrics'].items():
        print(f"   {metric.upper()}: {value:.4f}")

if __name__ == "__main__":
    main()



