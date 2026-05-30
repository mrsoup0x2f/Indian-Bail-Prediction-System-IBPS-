from openai import OpenAI
import json
import argparse
import tqdm
import time

if __name__ == '__main__':
    with open('API_key.txt', 'r') as file:
        API_Key = file.readline().strip()
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--prompt_fp', type=str, default='data/comparision/eval_prompt.txt')
    argparser.add_argument('--save_fp', type=str, default='results/gpt4o_phi-4.json')
    argparser.add_argument('--summeval_fp', type=str, default='data/comparision/microsoft-phi-4-results-eval.json')
    argparser.add_argument('--key', type=str, default=API_Key)
    argparser.add_argument('--model', type=str, default='gpt-4o-mini-2024-07-18')
    args = argparser.parse_args()
    
    client = OpenAI(api_key=args.key)

    summeval = json.load(open(args.summeval_fp))
    prompt = open(args.prompt_fp).read()

    ct, ignore = 0, 0

    new_json = []
    for instance in tqdm.tqdm(summeval):
        full_case = instance['case']
        source = instance['ref']
        system_output = instance['res']
        cur_prompt = prompt.replace('{{full_case}}', full_case).replace('{{Actual_Document}}', source).replace('{{Generated_Document}}', system_output)
        instance['prompt'] = cur_prompt
        while True:
            try:
                _response = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "user", "content": cur_prompt}],
                    temperature=2,
                    max_tokens=5,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    # logprobs=40,
                    n=3
                )
                time.sleep(0.5)

                all_responses = [choice.message.content for choice in _response.choices]
                instance['all_responses'] = all_responses
                new_json.append(instance)
                ct += 1
                break
            except Exception as e:
                print(e)
                if ("limit" in str(e)):
                    time.sleep(2)
                else:
                    ignore += 1
                    print('ignored', ignore)

                    break

    print('ignored total', ignore)
    with open(args.save_fp, 'w') as f:
        json.dump(new_json, f, indent=4)
