# %%
from vllm import LLM, SamplingParams
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["VLLM_LOGGING_LEVEL"] = "DEBUG"

# %%
llm = LLM(
    model="microsoft/phi-4",
    dtype="bfloat16",
    trust_remote_code=True,
    max_model_len=16384, 
    gpu_memory_utilization=0.87,
    tensor_parallel_size=2,
    enable_prefix_caching=False,  
    block_size=16,  
    swap_space=8,  
    enable_chunked_prefill=True,
    enforce_eager=True
)

# %%
import json

with open("./data/rest_all_fine_tuning_sorted.json", "r") as f:
    data_ = json.load(f)

# %%
print(len(data_))

# %%
import random

# data_ = random.sample(data_, 128)
data = data_[:75000]


# %%
example = """
given below is a python dictionary format which is to be filled with information about the case given in the raw judgement text. replace the text between the < and > with the information extracted from the raw judgement text.
**DO NOT COPY THE TEXT BETWEEN < AND >, INSTEAD REPLACE IT WITH THE EXTRACTED INFORMATION.**
python dict format :
{
    "case":"Applicant applied for <type of application, "Regular-Bail" OR "Anticipatory-Bail" OR "Bail-Cancellation", (one of these)>.\nIs it a withdrawal application? <"Yes" or "No" depending upon if it is application for withdrawal>.\nAge of the accused is <age of the accused if provided, else write "not provided">.\nHealth issues for the accused are <description of health issues if provided, else "None">.\nThere are <"no" if there are no past criminal records, else "some"> past criminal records of the accused.\nStatutes mentioned in the judgement are <list of statutes, eg: [Section 438 CrPC, Section 294(a) IPC, Section 506(1)(b) IPC, Section 34 IPC, Section 25 Arms Act], do not include the acts or acts/codes/sections that were removed or replaced later>.\nPrecedents mentioned in the judgement are <list of precedents, if any, else "None">.\nDetails of the incident are <details of the incident if provided, else "None">.\nArguments supporting the bail application are <arguments supporting the bail application, if any, else "None">.\nArguments opposing the bail application are <arguments opposing the bail application, if any, else "None">."
    "outcome": "The outcome of the case is <status of the outcome, "Bail granted" OR "Bail not granted" OR "Bail cancelled" OR "Bail not cancelled", (one of these)>. The bail conditions are <list of bail conditions, if any, else "None">."
    "reasoning": "The reasoning for the judgement is <list of reasoning, if any, else "None">."
    "date_of_arrest": "<date of arrest, if provided, else "not provided">."
    "date_of_judgement": "<date of judgement, if provided, else "not provided">."
}

For example, if the raw judgement text is as follows:

IN THE HIGH COURT OF KERALA AT ERNAKULAM
PRESENT:
THE HONOURABLE MR.JUSTICE M.SASIDHARAN NAMBIAR
MONDAY, THE 9TH DAY OF APRIL 2012/20TH CHAITHRA 1934
Bail Appl..No. 2123 of 2012 ()
-----------------------------------
AGAINST THE ORDER/JUDGMENT IN BA.1412/2012 DATED 09-03-2012
CRIME NO.51/2012 OF PAVARATTY POLICE STATION, THRISSUR DISTRICT
--------------
PETITIONERS/ACCUSED:
------------------------------
1. VISHNU
AGED 19 YEARS, S/O.VALSALAN, KANNARAMBIL HOUSE
MULLASSERY, TRISSUR DISTRICT.
2. RAHUL
AGED 22 YEARS, S/O.SURENDRAN, NEDIYATH HOUSE
MULLASSERY, TRISSUR DISTRICT.
3. NIKHIL
AGED 21 YEARS, S/O.GOPI, KUTTAD HOUSE
MULLASSERY, TRISSUR DISTRICT.
4. SREEKHIL
AGED 20 YEARS, S/O.BABU, KAMBARATH HOUSE
MULLASSERY, TRISSUR DISTRICT.
5. SHAJI
AGED 24 YEARS, S/O.SASIKUMAR, VADERI HOUSE
MULLASSERY, TRISSUR DISTRICT.
BY ADV. SRI.P.K.VARGHESE
RESPONDENT/COMPLAINANT:
------------------------------------
STATE OF KERALA
REPRESENTED BY THE PUBLIC PROSECUTOR
HIGH COURT OF KERALA.
BY PUBLIC PROSECUTOR SRI. C. RASHEED
THIS BAIL APPLICATION HAVING COME UP FOR ADMISSION ON
09-04-2012, THE COURT ON THE SAME DAY PASSED THE FOLLOWING:
svs
2012:KER:15460
M.SASIDHARAN NAMBIAR, J
...........................................
B.A.No.2123 of 2012
............................................
Dated 9th April, 2012
ORDER
Petitioners are accused in Crime No.51 of 2012 of
Pavaratty Police Station registered for the offences under
Section 143, 147, 148, 341, 323, 324 and 307 read with 149
of IPC. As subsequently the injured succumbed to the
injuries, the offence under Section 307 of IPC was deleted
and offence under Section 302 of IPC was incorporated.
Petitioners were arrested on 22.1.2012 and have been in
custody since then.
2. The argument of learned counsel appearing for the
petitioners is that as petitioners have been in custody since
22.1.2012, they be released on bail and they are prepared
to abide by any condition. Learned counsel submitted that
prosecution case is that it was the first accused who stabbed
the deceased and the allegations as against the petitioners 2
to 5 are only that they attacked the deceased with their
2012:KER:15460
Ba 2123/12 2
hands and in such circumstances, petitioners be released on
bail. Learned Public Prosecutor opposed the petition and
made available the case diary and submitted that as
investigation is in progress, release of the petitioners would
adversely affect proper investigation. Learned Public
Prosecutor also pointed out that the death was the result of
a political clash and even subsequently there was political
clash and in such circumstances, petitioners may not be
released on bail.
3. Considering the nature of the offences, the
possibility of the petitioners interfering in the investigation
by intimidating or inducing the witnesses, it is not in the
interest of justice to release the petitioners on bail. If
petitioners are entitled to statutory bail, they are at liberty
to approach the learned Magistrate at appropriate time.
Petition is dismissed.
M.SASIDHARAN NAMBIAR,
JUDGE
lgk
2012:KER:15460

the output should be as follows:
```json
{
    "case": "Applicant applied for Regular-Bail.\nIs it a withdrawal application? No.\nAge of the accused is 19, 22, 21, 20, 24 years.\nHealth issues for the accused are None.\nThere are no past criminal records of the accused.\nStatutes mentioned in the judgement are [Section 143 IPC, Section 147 IPC, Section 148 IPC, Section 341 IPC, Section 323 IPC, Section 324 IPC, Section 307 IPC, Section 149 IPC, Section 302 IPC].\nPrecedents mentioned in the judgement are None.\nDetails of the incident are The petitioners are accused in Crime No.51 of 2012 of Pavaratty Police Station registered for the offences under Section 143, 147, 148, 341, 323, 324 and 307 read with 149 of IPC. As subsequently the injured succumbed to the injuries, the offence under Section 307 of IPC was deleted and offence under Section 302 of IPC was incorporated.\nArguments supporting the bail application are The argument of learned counsel appearing for the petitioners is that as petitioners have been in custody since 22.1.2012, they be released on bail and they are prepared to abide by any condition. Learned counsel submitted that prosecution case is that it was the first accused who stabbed the deceased and the allegations as against the petitioners 2 to 5 are only that they attacked the deceased with their hands and in such circumstances, petitioners be released on bail.\nArguments opposing the bail application are Learned Public Prosecutor opposed the petition and made available the case diary and submitted that as investigation is in progress, release of the petitioners would adversely affect proper investigation. Learned Public Prosecutor also pointed out that the death was the result of a political clash and even subsequently there was political clash and in such circumstances, petitioners may not be released on bail.",
    "outcome": "The outcome of the case is Bail not granted. The bail conditions are None.",
    "reasoning": "Considering the nature of the offences, the possibility of the petitioners interfering in the investigation by intimidating or inducing the witnesses, it is not in the interest of justice to release the petitioners on bail. If petitioners are entitled to statutory bail, they are at liberty to approach the learned Magistrate at appropriate time.",
    "date_of_arrest": "22.1.2012",
    "date_of_judgement": "9th April, 2012"
}
```

similarly given a raw judgement text, extract the information and convert it into given json format. 
Respond **ONLY** with valid JSON matching the schema. Do not add explanations or data from example itself into the JSON.

Raw Judgement to process: :

"""

# %%
data_[0]

# %%
sampling_params = SamplingParams(
    temperature=0,
    max_tokens=1200,
    skip_special_tokens=False,
    stop=["<|end|>", "<|im_end|>"],
    ignore_eos=True,
)

# %%
batch_size = 128

# %%
processed_docs = []

# %%
import re

# %%
from tqdm import tqdm

# Total number of batches
total_batches = (len(data_) + batch_size - 1) // batch_size

for i in tqdm(range(0, len(data_), batch_size), total=total_batches, desc="Processing batches"):
    data_batch = data_[i:i + batch_size]
    cnr_nums = [case.get('CNR') or case.get('cnr_num') for case in data_batch]
    doc_batch = [f"<|user|>\n{example}\n{data.get('text') or data.get('case_text')}<|end|>\n<|assistant|>" for data in data_batch]
    try:
        results = llm.generate(doc_batch, sampling_params=sampling_params)
        structured_data = [ {
            "text": re.split(r"<\|end\|>|<\|im_end\|>", output.outputs[0].text)[0],
            "tokens": len(output.outputs[0].token_ids)
        } for output in results ]
        for j in range(len(structured_data)):
            response = structured_data[j]
            info = {
                "cnr": cnr_nums[j],
                "text": response['text']
            }
            processed_docs.append(info)
        
        if i % 128 == 0:
            with open("./data/to_be_cleaned_alt.json", "w", encoding='utf-8') as f:
                json.dump(processed_docs, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error processing batch {i // batch_size}: {e}")
        with open("gondogol_hoche.txt", "a") as f:
            for cnr in cnr_nums:
                f.write(cnr + "\n")
        continue


# # %%
# import json

# with open("Kerela/parsed/kerela.json", "w", encoding="utf-8") as f:
#     json.dump(processed_docs, f, ensure_ascii=False, indent=4)

# # %%


# # %%
# processed_docs = []

# # %%
# with open("bombay_sorted.json", "r") as f:
#     data_ = json.load(f)

# # %%
# from tqdm import tqdm

# # Total number of batches
# total_batches = (len(data_) + batch_size - 1) // batch_size

# for i in tqdm(range(0, len(data_), batch_size), total=total_batches, desc="Processing batches"):
#     data_batch = data_[i:i + batch_size]
#     cnr_nums = [case['CNR'] for case in data_batch] 
#     doc_batch = [f"<|user|>\n{example}\n{data['text']}<|end|>\n<|assistant|>" for data in data_batch]
#     try:
#         results = llm.generate(doc_batch, sampling_params=sampling_params)
#         structured_data = [ {
#             "text": re.split(r"<\|end\|>|<\|im_end\|>", output.outputs[0].text)[0],
#             "tokens": len(output.outputs[0].token_ids)
#         } for output in results ]
#         for j in range(len(structured_data)):
#             response = structured_data[j]
#             info = {
#                 "cnr": cnr_nums[j],
#                 "text": response['text']
#             }
#             processed_docs.append(info)
        
#         if i % 256 == 0:
#             with open("Bombay/parsed/bombay.json", "w", encoding='utf-8') as f:
#                 json.dump(processed_docs, f, ensure_ascii=False, indent=4)

#     except Exception as e:
#         print(f"Error processing batch {i // batch_size}: {e}")
#         with open("unprocessed_cases_Bombay.txt", "a") as f:
#             for cnr in cnr_nums:
#                 f.write(cnr + "\n")
#         continue


# # %%
# with open("Bombay/parsed/bombay.json", "w", encoding="utf-8") as f:
#     json.dump(processed_docs, f, ensure_ascii=False, indent=4)

# %%
exit()

# %%
# structured_data = [{
#     "text": output.outputs[0].text.split("<|end|>"),
#     "tokens": len(output.outputs[0].token_ids)
# } for output in results]

# %%
# print(results[0])
# print()
# print(results[1])

# %%
# print(structured_data[0]['text'][0])
# print()
# print(structured_data[1]['text'][0])

# %%



