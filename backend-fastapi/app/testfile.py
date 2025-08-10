import requests
import json
import os

# https://en.wikipedia.org/wiki/Bear

TESTFLAG = 0

if TESTFLAG == 0:
    # semantic comparison

    with open("testdata/obama_A.txt", 'r') as file:
        texta = file.read()
    with open("testdata/obama_B.txt", 'r') as file:
        textb = file.read()
    
    params = {
        'text_a': texta,
        'text_b': textb,
        'similarity_threshold': 0.75,
        'model_name': 'sentence-transformers/LaBSE'
    }

    address = "http://localhost:8000/comparison/semantic_comparison"
    response = requests.get(address, params=params)
    
    print(f'Server responded with: {response.status_code}')
    
    if response.status_code == 200:
    
        content = json.loads(response.content)
        missing_info = content['missing_info']
        extra_info = content['extra_info']
        print('Info in A that is NOT in B (A - B):')
        for info in missing_info:
            print(info)
        print("==================="*10)
        print(f'Info in B that is NOT in A (B - A):')
        for info in extra_info:
            print(info)
    else:
        # content = json.loads(response.content)
        # error_message = content['detail']
        # print(f'HTTP Error: {error_message}')
        print(f'Error: {response}')

elif TESTFLAG == 1:
    # get article and available article languages

    URL = "https://en.wikipedia.org/wiki/Bear"
    TITLE = "Bear"
    
    address = "http://localhost:8000/get_article"
    response = requests.get(address, params={'url': URL, 'title': TITLE})
    
    if response.status_code == 200:
        content = json.loads(response.content)
        source_article = content['source_article']
        languages = content['article_languages']

        print(f'SOURCE_ARTICLE: {source_article}')
        print("==================="*10)
        print(f'ARTICLE_LANGUAGES: {languages}')

elif TESTFLAG == 2:
    # get wiki provided human translated article

    address = "http://localhost:8000/wiki_translate/source_article"
    URL = "https://en.wikipedia.org/wiki/Bear"
    TITLE = "Bear"
    LANGUAGE = "es"

    response = requests.get(address, params={'url': URL, 'title': TITLE, 'language': LANGUAGE})

    if response.status_code == 200:
        content = json.loads(response.content)
        translation = content['translated_article']

        print(f'TRANSLATED_ARTICLE: {translation}')




