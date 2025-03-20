import requests
import json

# address = "http://localhost:8000/comparison/semantic_comparison"

params = {
    'text_a': "The quick silly fox jumped over the blue fence. The fox clipped the top of the fence, causing it to fall and hurt its leg.",
    'text_b': "The quick fox jumped over the tall fence. The fox hurt its leg upon landing."
}

address = "http://localhost:8000/comparison/semantic_comparison"

response = requests.get(address, params=params)





print(f'Server responded with: {response.status_code}')
print(f'Source Texts:')
print(f'Text A: {params["text_a"]}')
print(f'Text B: {params["text_b"]}\n\n')
if response.status_code == 200:
    content = json.loads(response.content)
    missing_info = content['missing_info']
    extra_info = content['extra_info']
    print(f'Missing Info: {missing_info}')
    print(f'Extra Info: {extra_info}')
