The data files are hosted at https://drive.google.com/drive/folders/1SRAiRUWnTBgvC5GXjOifgBR75bVLK25r 

It includes the bail_data.json, train_data.json, test_data.json and val_data.json split.

# 📂 High Court Bail Judgments Dataset

This dataset contains detailed bail judgment records collected from five major High Courts in India: **Bombay**, **Kerala**, **Allahabad**, **Chhattisgarh**, and **Jharkhand**. These courts were selected based on data volume and diversity across bail categories.

---

## 📊 Dataset Overview

- **Total cases**: 208,983 bail judgment records
- **Jurisdictions**: 5 High Courts
- **Offense coverage**: From petty crimes to serious offenses (e.g., murder, rape, cybercrime)
- **Statutory basis**: Annotated with sections from IPC, CrPC, and relevant Acts
- **Contextual enrichment**: Includes law text scraped from [India Code](https://www.indiacode.nic.in) to support retrieval-augmented generation (RAG) systems

---

## 📁 Sample Fields

Each case record contains structured information, including:

| Field                 | Description |
|-----------------------|-------------|
| `CNR`                | Case reference number (unique ID) |
| `case`               | Structured summary of case facts and arguments |
| `outcome`            | Final bail decision and conditions (if any) |
| `reasoning`          | Judge’s reasoning for granting or denying bail |
| `date_of_arrest`     | Arrest date (if known) |
| `date_of_judgement`  | Date when judgment was delivered |
| `statutes`           | List of IPC/CrPC sections invoked |
| `context`            | Legal explanations for statutes cited |

---

## 🧠 Example Entry

```json
{
  "CNR": "CGHC010400882018",
  "case": "Applicant applied for Anticipatory-Bail. ...",
  "outcome": "The outcome of the case is Bail granted. The bail conditions are [...]",
  "reasoning": "It is an incident of scuffle between mob and the police personnel...",
  "date_of_arrest": "Unknown",
  "date_of_judgement": "07-01-2019",
  "statutes": [
    "147 IPC", "148 IPC", "149 IPC", "186 IPC", "189 IPC", "353 IPC", "332 IPC", "427 IPC"
  ],
  "context": [
    "Section 147 IPC: Punishment for rioting...",
    "...",
    "Section 427 IPC: Mischief causing damage..."
  ]
}

