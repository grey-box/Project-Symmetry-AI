import requests
import json
import os

# https://en.wikipedia.org/wiki/Bear

TESTFLAG = 2

if TESTFLAG == 0:
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
        print(f'MISSING_INFO: {missing_info}')
        print("==================="*10)
        print(f'EXTRA_INFO: {extra_info}')

elif TESTFLAG == 1:
    URL = "https://en.wikipedia.org/wiki/Bear"
    TITLE = "Bear"
    
    address = "http://localhost:8000/get_article"
    response = requests.get(address, params={'url': URL, 'title': TITLE})
    
    if response.status_code == 200:
        content = json.loads(response.content)
        sourceArticle = content['sourceArticle']
        languages = content['articleLanguages']

        print(f'SOURCE_ARTICLE: {sourceArticle}')
        print("==================="*10)
        print(f'ARTICLE_LANGUAGES: {languages}')

elif TESTFLAG == 2:
    address = "http://localhost:8000/wiki_translate/source_article"
    URL = "https://en.wikipedia.org/wiki/Bear"
    TITLE = "Bear"
    LANGUAGE = "es"

    response = requests.get(address, params={'url': URL, 'title': TITLE, 'language': LANGUAGE})

    if response.status_code == 200:
        content = json.loads(response.content)
        translation = content['translated_article']

        print(f'TRANSLATED_ARTICLE: {translation}')




