import requests
import json
import os

with open("testdata/missingno_en.txt", 'r') as file:
    texta = file.read()
with open("testdata/missingno_fr.txt", 'r') as file:
    textb = file.read()

params = {
    'text_a': texta,
    'text_b': textb,
    'similarity_threshold': 0.75
}
address = "http://localhost:8000/comparison/semantic_comparison"
response = requests.get(address, params=params)

print(f'Server responded with: {response.status_code}')

if response.status_code == 200:
    print(f'Source Texts:')
    print(f'Text A: {params["text_a"]}')
    print(f'Text B: {params["text_b"]}\n\n')

    content = json.loads(response.content)
    missing_info = content['missing_info']
    extra_info = content['extra_info']
    print(f'Missing Info: {missing_info}')
    print("==================="*10)
    print(f'Extra Info: {extra_info}')

