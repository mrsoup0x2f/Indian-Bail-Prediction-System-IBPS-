
from fastapi import FastAPI, WebSocket
# from vllm import LLM, SamplingParams
import json
import openai
import traceback
import random
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import pickle

openai_client = openai.OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)

app = FastAPI()

nlp = spacy.load("en_core_web_sm")

cnn_model = load_model("bail_cnn_model.h5")
with open("tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)
    
def format_messages_as_prompt(messages: list[dict]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

EXTRACTION_INSTRUCTION = """
    You are a legal assistant named IBPS. You see a string of chat between a user and another legal assistant (called assistant in chats).
    They are talking about about for which a bail application is filed. Your task is to generate text in under 500 words with the following points in the following format: 
    ```
    1.    Application for Regular-Bail.

    2.    Age of accused: <age of accused if given else N/A>.

    3.    Accused has been suffering from <health conditions if given else "no health issues">.

    4.    Statutes involved: Section <section number> <code/statute name>, Section <section number> <code/statute name>, Section <section number> <code/statute name>, ...

    5.    Incident details: <all the details of the incident if given else "no details">.
            
    6.    Accused has past criminal records: <yes/no>.

    7.    Days in police custody: <days in police custody if given else "N/A">.
    ```
    for example:
    ```
    1.  Application for Regular-Bail.

    2.  Age of accused: N/A.

    3.  Accused has been suffering from no health issues..

    4.  Statutes involved: Section 409 IPC, Section 420 IPC, Section 120-B IPC, Section 34 IPC.

    5.  Incident details: The applicant represented to the Chairman and Director of the complainant's Company that one Dineshkumar Gupta, Nareshkumar Gupta and Satyendra Panwal have land admeasuring 32 Bighas at Gowharimati, Taluka-Hrishikesh, Dehradun, Uttarakhand, on the Bank of river Ganga and for the said transaction, the applicant took Rs.2,50,000/- towards his fees and Rs.1,00,00,000/- towards the token amount for sale of the land, from the complainant. However, subsequently, the applicant denied to take further steps regarding the said transaction. During the investigation, it was found that out of the total amount of Rs.1,02,50,000/- an amount of Rs.1,00,00,000/- was transferred to the account of Shri. Dineshkumar Gupta. However, subsequently, out of Rs.1,00,00,000/- an amount of Rs.50,00,000/- has been re-transferred to the account of applicant and further the applicant has purchased a property in Delhi.
            
    6.  Accused has past criminal records: No

    7.  Days in police custody: 0
    ```
    Write a paragraph containing these details and **ONLY THESE DETAILS** in the same order about the case for which the bail application is filed from the user's messages.  
    Do not include any other information or comment on the case.  
"""

def extract_info(messages: list[dict]) -> str:
    # messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
    message_chain = messages[1:] if messages[0]['role'] == 'system' else messages
    input_prompt = format_messages_as_prompt(message_chain)
    extracted_info = openai_client.chat.completions.create(
        # model="./phi-4_fine_tuned",
        model="microsoft/phi-4",
        messages=[
            {"role": "system", "content": EXTRACTION_INSTRUCTION},
            {"role": "user", "content": input_prompt}
        ],
        temperature=0.0,
        max_tokens=1200,
        stop=["<|end|>", "<|im_end|>"],
        stream=False
    )
    return extracted_info.choices[0].message.content

def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(tokens)

def preprocess_cnn_input(text):
    # Tokenize and pad the input text
    sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(sequence, maxlen=500, padding='post', truncating='post')
    return padded_sequence

def predict_outcome(text):
    processed_input = preprocess_cnn_input(text)
    prediction = cnn_model.predict(processed_input)
    return prediction[0][0]

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    # system_instruction = """ 
    #     Pose as a legal assistant whose name is IBPS and specializes in bail decisions (granted/denied). We need the following information: Type of bail application (regular/anticipatory/bail-cancellation), Statutes imposed on accused, Details of the incident, Past Criminal Record, Age and Health details, Date of arrest in case of Regular Bail Application. If any of these details are missing, politely ask the user to provide the missing information. Once you have the first three details, proceed to predict whether the bail application will be granted or denied, along with bail conditions and reasoning and for your prediction. Always give short, clear and concise response.
    # """
    # input_prompt = f"""
    # <|im_start|>system<|im_sep|>
    # """
    message_chain = ""
    confidence_score = random.uniform(0.55, 0.80)
    await websocket.accept()
    try:
        while True:
            try:
                message_chain = await websocket.receive_json()
            except Exception as e:
                print(f"Error receiving message: {repr(e)}")
                return
            
            ## cnn input extraction
            # try:
            #     input_to_cnn = extract_info(message_chain)
            #     print(f"Input to CNN: {input_to_cnn}")
            # except Exception as e:
            #     print(f"Error in extract_info(): {e}")
            #     await websocket.send_text("Error processing message. Please try again.")
            #     continue
            
            # ## cnn score prediction
            # input_to_cnn = preprocess_text(input_to_cnn)
            # ## load cnn model here and predict
            # confidence_score = predict_outcome(input_to_cnn) 
            
            # try:
            #     score = json.dumps({"type": "confidence_score", "value": float(confidence_score)})
            #     await websocket.send_text(score)
            # except Exception as e:
            #     print(f"Error sending confidence score: {e}")
            #     print(type(score), score)
            #     continue
            
            try:
                stream = openai_client.chat.completions.create(
                    # model="./phi-4_fine_tuned",
                    model="microsoft/phi-4",
                    messages=message_chain,
                    temperature=0.7,
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        try:
                            await websocket.send_text(delta)
                        except Exception as send_err:
                            print(f"Send error (client disconnected?): {send_err}")
                            return

                await websocket.send_text("__end__")

            except Exception as e:
                print("Streaming error:")
                traceback.print_exc()
                await websocket.send_text("Error generating response.")
                await websocket.send_text("__end__")
                
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}")
    



