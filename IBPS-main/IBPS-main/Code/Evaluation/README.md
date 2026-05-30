evaluate.py is used to calculate performance metrices of models FT-1 and FT-2.

evaluate_rag.py is used to calculate performance metrices of models FT-1 and FT-2 when input is added with a context of relevant IPCs, CRPCs, State Acts and Central Acts.

These take the Gold Standard dataset and the corresponding extraction text as input, and generate the outputs in desired format for calculating the values of different metrices.

- Classification metrics: **Accuracy**, **Precision**, **Recall**, **F1**
- Text generation metrics: **ROUGE**, **BLEU**, **METEOR**, **BERTScore**
- Generates a **confusion matrix** for outcome prediction
- Supports batch evaluation using **vLLM**
