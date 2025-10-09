#!/bin/bash
from fastapi import FastAPI, HTTPException
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Query
from pydantic import BaseModel
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse
import wikipediaapi
from typing import List

from .api import wiki_article
from .model.request import Url

from .ai.semantic_comparison import perform_semantic_comparison
from .ai.llm_comparison import llm_semantic_comparison


'''
This is the API which handles backend. It handles following features
1. Providing source article (with input as URL or Title)
2. Providing available translation languages list
3. Providing translated content
4. Providing comparisons between articles

Note: You can run this API using 'python main.py' and use postman to get response while debugging
      OR you can simply run "fastapi dev main.py" in the same directory as this file

'''



class BackendDataStore:
    comparison_models: list[str] = [
        "sentence-transformers/LaBSE",
        "xlm-roberta-base",
        "multi-qa-distilbert-cos-v1",
        "multi-qa-MiniLM-L6-cos-v1",
        "multi-qa-mpnet-base-cos-v1"
    ]
    selected_model: str = comparison_models[0]
    article_model: ArticleModel= None

    # todo: expose these functions to the api
    def set_selected_model(self, choice: str) -> bool:
        if choice not in comparison_models:
            return False

        selected_model = choice
        return True

    def available_models_list(self):
        return comparison_models


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()
# Add endpoints from other modules
app.include_router(wiki_article.router)

# Allow all origins (be cautious with this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Class defines the API reponse format for source article (output)
class SourceArticleResponse(BaseModel):
    source_article: str
    article_languages: List[str]

class ArticleComparisonResponse(BaseModel):
    missing_info: List
    extra_info: List

# Class defines the API reponse format for source article (output)
class ArticleResponse(BaseModel):
    translated_article: str



wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyApp/2.0 (contact@example.com)', language='en')  # English Wikipedia instance

# Function to get the URL of Wikipedia page from title as input
def get_wikipedia_url(title: str) -> str:
    """Get the Wikipedia article URL for a given title using the Wikipedia API."""
    api_url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'info',
        'inprop': 'url',
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    page = next(iter(pages.values()), None)

    if not page or 'missing' in page:
        logging.error('Wikipedia article not found.')
        raise HTTPException(status_code=404, detail="Wikipedia article not found.")

    fullurl = page.get('fullurl')
    if not fullurl:
        logging.error('Wikipedia article URL not found.')
        raise HTTPException(status_code=404, detail="Wikipedia article URL not found.")

    return fullurl

def extract_title_from_url(url: str) -> str:
    match = re.search(r'/wiki/([^#?]*)', url)
    if match:
        return match.group(1).replace('_', ' ')
    return None

# The API endpoint which is called from frontend to get source article and translated languages available
@app.get("/get_article", response_model=SourceArticleResponse)
def get_article(url: str = Query(None), title: str = Query(None)):
    logging.info("Calling get article endpoint")
    
    if url:
        title = extract_title_from_url(url)
        if not title:
            logging.info("Invalid Wikipedia URL provided.")
            raise HTTPException(status_code=400, detail="Invalid Wikipedia URL provided.")
    
    if not title:
        logging.info("Either 'url' or 'title' must be provided.")
        raise HTTPException(status_code=400, detail="Either 'url' or 'title' must be provided.")
    
    page = wiki_wiki.page(title)
    
    if not page.exists():
        logging.info("Article not found.")
        raise HTTPException(status_code=404, detail="Article not found.")
    
    article_content = page.text  # Get the article text
    
    # Fetch available languages
    languages = list(page.langlinks.keys())
    
    return {"source_article": article_content, "article_languages": languages}


@app.get("/wiki_translate/source_article", response_model=ArticleResponse)
def translate_article(url: str = Query(None), title: str = Query(None), language: str = Query(...)):
    logging.info(f"Calling translate article endpoint for title: {title}, url: {url} and language: {language}")
    
    if url:
        title = extract_title_from_url(url)
        if not title:
            logging.info("Invalid Wikipedia URL provided.")
            raise HTTPException(status_code=400, detail="Invalid Wikipedia URL provided.")
    
    if not title:
        logging.info("Either 'url' or 'title' must be provided.")
        raise HTTPException(status_code=400, detail="Either 'url' or 'title' must be provided.")
    
    translated_wiki = wikipediaapi.Wikipedia(user_agent='MyApp/1.0 (contact@example.com)', language=language)
    translated_page = translated_wiki.page(title)
    
    if not translated_page.exists():
        logging.info("Translated article not found.")
        raise HTTPException(status_code=404, detail="Translated article not found.")
    
    translated_content = translated_page.text if translated_page.text else ""
    
    return {"translated_article": translated_content}


@app.get("/comparison/semantic_comparison", response_model=ArticleComparisonResponse)
def compare_articles(text_a: str, text_b: str, similarity_threshold: float = 0.75, model_name="sentence-transformers/LaBSE"):
    logging.info("Calling semantic comparison endpoint.")

    if similarity_threshold < 0 or similarity_threshold > 1:
        logging.info("Provided similarity threshold is out of the defined valid range [0,1]")
        raise HTTPException(status_code=400, detail="Provided similarity threshold is out of the defined valid range [0,1]")

    if model_name not in comparison_models:
        logging.info(f"Invalid model selected. {model_name} does not exist.")
        raise HTTPException(status_code=404, detail=f"Invalid model selected. {model_name} does not exist.")

    if text_a is None or text_b is None:
        logging.info("Invalid input provided to semantic comparison.")
        raise HTTPException(status_code=400, detail="Either text_a or text_b (or both) was found to be None.")

    if text_a.isnumeric() or text_b.isnumeric():
        logging.info("Invalid input provided to semantic comparison.")
        raise HTTPException(status_code=400, detail="Either text_a or text_b was not the correct input type.")

    # missing_info, extra_info = perform_semantic_comparison(text_a, text_b, similarity_threshold, model_name)
    # return {"missing_info": missing_info, "extra_info": extra_info}

    output = llm_semantic_comparison(text_a, text_b)
    # response = {"missing_info": output['missing_info'], "extra_info": output['extra_info']}
    # return response
    return output

@app.get("/synthesis/full", response_model=ArticleResponse)
def synthesize_full_article(target_language: str, article_title_a: str, article_title_b: str, article_synth_base: int):
    # article_synth_base indicates which article model will be used as the base for the newly synthesized article

    if article_synth_base < 0 or article_synth_base >= 2:
        raise HTTPException(status_code=400, detail="article_synth_base must be 0 or 1")
    # todo: check if language target is supported

    model_a = create_article_model(article_title_a)
    model_b = create_article_model(article_title_b)

    target_base = model_a if article_synth_base == 0 else model_b
    comp_base = model_b if article_synth_base == 0 else model_a

    missing = {}
    extra = {}

    # todo: this full comparison code should be in the sem. comparison (underlying function) endpoint also
    for fragment_a in enumerate(target_base.text):
        for fragment_b in comp_base.text:
            output = llm_semantic_comparison(fragment_a.text, fragment_b.text)
            fragment_a.missing_info = output['missing_info']
            # missing[id] = output['missing_info']
            # extra[id] = output['extra_info']

    symmetrical_article_text = ""
    for pack in target_base.structure:
        section_type, index = pack

        section = target_base.get_section(section_type, index)
        if section_type == TEXT:

            # full_text = section.text + 
        else:


    # return synthesis

if __name__ == '__main__':
    # Defines API URL (host, port)
    uvicorn.run(app, host='127.0.0.1', port=8000)



