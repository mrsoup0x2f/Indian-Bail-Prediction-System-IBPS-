
from fastapi import FastAPI, WebSocket
# from vllm import LLM, SamplingParams
import json
import openai
import traceback
import random
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import numpy as np
import pickle

openai_client = openai.OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)

app = FastAPI()


    
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
        model="./data/phi-4_fine_tuned",
        # model="microsoft/phi-4",
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

def predict_score(input_text: str) -> float:
    system = "look at the details of the case provided to you in the paragraph and predict the outcome of the bail application by outputting `0` or `1`."+" If the case type is 'regular-bail' or 'anticipatory-bail' application, output `0` if bail will not be granted and `1` if bail will be granted."+" If the case type is 'bail-cancellation' application, output `0` if bail will not be cancelled and `1` if bail will be cancelled."+" Do not output anything else."
    
    response = openai_client.chat.completions.create(
        model="./data/phi-4_fine_tuned",
        messages=[
            {"role": "user", "content": system},
            {"role": "assistant", "content": f" {input_text}\nPrediction:"}
        ],
        temperature=0.0,
        max_tokens=1,
        logprobs=True,
        stop=None
    )
    logprobs_content = response.choices[0].logprobs.content
    tokens = []
    token_logprobs = []
    for tok in logprobs_content:
        tokens.append(tok.token)
        token_logprobs.append(tok.logprob)
    token_probs = [float(np.exp(lp)) for lp in token_logprobs]
    
    # # Get top_logprobs for first step:
    # first_top_logprobs = logprobs_content[0].top_logprobs  # Dictionary: token string -> logprob
    # print(response.choices[0].logprobs)

    # # Clean all possible representations for '0' and '1' (sometimes there's leading space or byte prefix)
    # prob_0 = None
    # prob_1 = None
    # for tok, logp in first_top_logprobs.items():
    #     cleaned = tok.strip().replace("Ġ", "")  # Adjust as needed for your tokenizer
    #     if cleaned == "0":
    #         prob_0 = float(np.exp(logp))
    #     elif cleaned == "1":
    #         prob_1 = float(np.exp(logp))

    # print(f"Probability '0': {prob_0}")
    # print(f"Probability '1': {prob_1}")
    
    # Debug print for all generated tokens and their probabilities
    for i, (token, prob) in enumerate(zip(tokens, token_probs)):
        print(f"Token {i+1}: '{token}' -- Probability: {prob:.4f}")
    
    # Find first token that is 0 or 1 (as string)
    for t, p in zip(tokens, token_probs):
        candidate = t.strip()
        if candidate in ["0", "1"]:
            return candidate, p
    # fallback
    return tokens[0].strip(), token_probs[0]
    

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

            # input extraction for confidence score
            try:
                input_for_score = extract_info(message_chain)
                print(f"Input to scoring model: {input_for_score}")
            except Exception as e:
                print(f"Error in extract_info(): {e}")
                await websocket.send_text("Error processing message. Please try again.")
                continue
            
            ## cnn score prediction
            # input_for_score = preprocess_text(input_for_score)
            ## load cnn model here and predict
            prediction, confidence_score = predict_score(input_for_score)
            # print(f"Prediction: {prediction}, Confidence Score: {confidence_score}")

            try:
                score = json.dumps({"type": "confidence_score", "value": float(confidence_score)})
                await websocket.send_text(score)
            except Exception as e:
                print(f"Error sending confidence score: {e}")
                print(type(score), score)
                continue
            
            try:
                message_chain[-1]['content'] += f"\n\nAvailable information:\n{input_for_score}"
                stream = openai_client.chat.completions.create(
                    model="./data/phi-4_fine_tuned",
                    # model="microsoft/phi-4",
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
    