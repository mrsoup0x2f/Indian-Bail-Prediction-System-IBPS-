FineTuningFT-1.py is the one used to fine tune our FT-1 model.

FineTuningFT-2.py is the one used to fine tune our FT-2 model(takes context from RAG as well).

Hyperparameters:


 Model Inference Settings
==========================
Parameter               | Value
------------------------|-------------------------------
temperature             | 0.0
max_tokens              | 1024
batch_size              | 32
stop_token              | <|im_end|>
model_path              | Split_Data/phi4_bail_finetuned_long-merged
tokenizer               | microsoft/phi-4
dtype                   | float16
tensor_parallel_size    | 1


 Evaluation Settings
==========================
Metric                  | Config
------------------------|-------------------------------
Precision/Recall/F1     | average = macro, zero_division = 0
ROUGE                   | rouge1, rouge2, rougeL (use_stemmer = True)
BLEU                    | nltk with SmoothingFunction.method1
METEOR                  | nltk default
BERTScore               | lang = 'en', rescale_with_baseline = True


 Prompt Settings
==========================
Parameter               | Description
------------------------|---------------------------------------------------
SYSTEM_PROMPT           | Legal assistant instruction prompt
Few-shot Example        | Includes example case, outcome, reasoning, days
Stop token              | <|im_end|>


 Preprocessing Settings
==========================
Parameter               | Description
------------------------|-----------------------------------------------
Skip cases              | If "withdrawal application? Yes" in case text
Date formats tried      | %d-%m-%Y, %d.%m.%Y, %d/%m/%Y, %Y-%m-%d, etc.
Outcome Regex           | "The outcome of the case is ..."
Reasoning Extract       | Between "Reasoning:" and "The outcome of the case"
Bail Conditions Split   | On "." and strip whitespace

