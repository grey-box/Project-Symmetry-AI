import ollama as llama
import re
import json

def llm_semantic_comparison(buffer_a, buffer_b):
    def remove_think_section(text):
        # Uses regex to remove <think> section and its contents
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

    def comparison_prompt(buffer_a, buffer_b):
        try:
            file = open("prompts/system_prompt.txt", 'r') 
            system_prompt_text = file.read()
        except Exception:
            raise Exception("trouble opening system prompt file.")

        # NOTE: important to have the system prompt be the last thing the LLM reads
        system_prompt = f"""Given Input:\nText A: "{buffer_a}"\n\n---------------------------\nText B: "{buffer_b}"\n\n{system_prompt_text}""" 
        return system_prompt


    prompt = comparison_prompt(buffer_a, buffer_b)

    # temperature: 0.2
    server_response = llama.generate(model='deepseek-r1:8b', prompt=prompt, options={
        'temperature': 0.1
    })
    prompt_response = remove_think_section(server_response['response'])
    try:
        return json.loads(prompt_response.replace('```json', '').replace('```', ''))
    except Exception:
        print('-'*200)
        print(f'COULD NOT PARSE JSON STRING:\n{prompt_response}')
        print('-'*200)
        return {}

# text_a = "Bob went to the mall to buy ice cream. He ate ice cream there. The mall had a lot of traffic."
# text_b = "Bob went to the mall. He ate ice cream there. The mall had a lot of traffic."
# output = llm_semantic_comparison(text_a, text_b)
# missing = output['missing_info']
# extra = output['extra_info']
# print(f'Info in A that is NOT in B (A - B): {missing}')
# print(f'Info in B that is NOT in A (B - A): {extra}')
