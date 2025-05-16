# python gpt4_eval.py --prompt_fp prompts/story_eval_prompt.txt --save_fp results/story_eval_results.json --summeval_fp data/generated_stories_with_images.json --model llama3 --temperature 0.5 --top_p 0.9 --max_tokens 400

import requests
import json
import argparse
import tqdm
import time

if __name__ == '__main__':

    # --- Argument Parsing ---
    argparser = argparse.ArgumentParser(description="G-Eval Pipeline: Evaluate Generated Stories with LLM")

    argparser.add_argument('--prompt_fp', type=str, required=True, help='Path to G-Eval prompt template file')
    argparser.add_argument('--save_fp', type=str, required=True, help='Where to save evaluated results JSON')
    argparser.add_argument('--summeval_fp', type=str, required=True, help='Input file with generated stories')
    argparser.add_argument('--model', type=str, default='llama3', help='Model name to use for evaluation')

    # New optional arguments for generation control
    argparser.add_argument('--temperature', type=float, default=0.2, help='Sampling temperature (default=0.7)')
    argparser.add_argument('--top_p', type=float, default=1.0, help='Top-p nucleus sampling (default=1.0)')
    argparser.add_argument('--top_k', type=int, default=50, help='Top-k sampling (default=50)')
    argparser.add_argument('--max_tokens', type=int, default=400, help='Maximum number of tokens in output')

    args = argparser.parse_args()

    # --- Config: API URL ---
    # LLM_API_URL = "http://100.64.216.93:11434/api/chat"  

    # --- Config: llm.srv webis URL ---
    LLM_API_URL = "https://llm.srv.webis.de/api/chat"

    # --- Load prompt and stories ---
    with open(args.summeval_fp) as f:
        generated_stories = json.load(f)
    with open(args.prompt_fp) as f:
        prompt_template = f.read()

    ct, ignore = 0, 0
    new_json = []

    for instance in tqdm.tqdm(generated_stories):
        try:
            
            story_parts = instance['generated_story']
            story_text = story_parts['intro'] + "\n\n" + story_parts['section'] + "\n\n" + story_parts['outro']

            
            cur_prompt = prompt_template.replace('{{Story}}', story_text)

            
            _response = requests.post(
                LLM_API_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "model": args.model,
                    "temperature": args.temperature,
                    "top_p": args.top_p,
                    "top_k": args.top_k,
                    "max_tokens": args.max_tokens,
                    "messages": [
                        {"role": "user", "content": cur_prompt}
                    ],
                    "stream": False
                }
            )

            if _response.status_code == 200:
                _response_json = _response.json()
                response_content = _response_json.get("message", {}).get("content", "")

                instance['prompt_for_eval'] = cur_prompt
                try:
                    parsed_response = json.loads(response_content)
                    instance['scores'] = parsed_response['scores']
                except json.JSONDecodeError:
                    print(f"Warning : Failed to decode to model output for prompt :{instance['prompt']}")
                    instance['scores'] = {"coherence": None}
                new_json.append(instance)
                ct += 1
            else:
                print(f"LLM server error: {_response.status_code}, {_response.text}")
                ignore += 1
        except Exception as e:
            print(f"Exception: {e}")
            ignore += 1
            time.sleep(1)
            continue

    print('Total ignored instances:', ignore)

    # --- Save results ---
    with open(args.save_fp, 'w') as f:
        json.dump(new_json, f, indent=4)

