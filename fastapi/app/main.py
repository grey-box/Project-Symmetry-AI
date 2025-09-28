#!/bin/bash
import argparse
import logging
from traceback import format_exc

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

from app.api import wiki_article
from app.api import comparison

from .ai.semantic_comparison import perform_semantic_comparison
from .ai.llm_comparison import llm_semantic_comparison

"""
This is the API which handles backend. It handles following features
1. Providing source article (with input as URL or Title)
2. Providing available translation languages list
3. Providing translated content
4. Providing comparisons between articles

Note: You can run this API using 'python main.py' and use postman to get response while debugging
      OR you can simply run "fastapi dev main.py" in the same directory as this file
"""

# This is how FastAPI recommends setting up debug logging
# to avoid accidentally leaving it enabled in production.
# https://www.starlette.io/config/
config = Config(".env")

LOG_LEVEL = config.get("LOG_LEVEL", default="INFO")
FASTAPI_DEBUG = config.get("FASTAPI_DEBUG", cast=bool, default=False)

comparison_models = [
    "sentence-transformers/LaBSE",
    "xlm-roberta-base",
    "multi-qa-distilbert-cos-v1",
    "multi-qa-MiniLM-L6-cos-v1",
    "multi-qa-mpnet-base-cos-v1"
]

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Initialize FastAPI app. The 'debug' flag controls the level of error reporting.
# When 'debug' is True, detailed error messages including stack traces will be shown, which is helpful during development.
# When 'debug' is False, more generic error messages are returned to the client, suitable for production environments.
app = FastAPI(debug=FASTAPI_DEBUG)


# Custom exception handlers


# This handler is used to catch specifically HTTP exceptions and return a JSON response with the error details.
async def http_exception_handler(request: Request, exc: HTTPException):
    # Custom HTTPException handler to include stack trace in debug mode
    response_content = {"detail": exc.detail}
    if getattr(request.app, "debug", False):
        response_content["stack_trace"] = format_exc()
    return JSONResponse(response_content, status_code=exc.status_code)


# This handler is used to catch all other exceptions that are not HTTP exceptions.
async def generic_exception_handler(request: Request, exc: Exception):
    # Catch-all exception handler
    logging.error(f"Unhandled exception: {exc}")
    response_content = {"detail": "Internal Server Error"}
    if getattr(request.app, "debug", False):
        response_content["stack_trace"] = format_exc()
    return JSONResponse(response_content, status_code=500)


def register_exception_handlers():
    # Register custom exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


# Import the exception handlers
register_exception_handlers()

# Add endpoints from other modules.
# Note that when adding more endpoints, they should follow a similar format!
# The current format is /symmetry/v1/<path>/<to>/<resource>
# A quick read on RESTful resource naming: https://restfulapi.net/resource-naming/
# For a more dense and in-depth view of the RESTful philosophy, the above article
# links Roy Fielding's dissertation:
# https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_2_1_1
app.include_router(wiki_article.router)
app.include_router(comparison.router)


# Class defines the API reponse format for source article (output)
class SourceArticleResponse(BaseModel):
    source_article: str
    article_languages: List[str]

class ArticleComparisonResponse(BaseModel):
    missing_info: List
    extra_info: List

# Class defines the API reponse format for source article (output)
class TranslateArticleResponse(BaseModel):
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


@app.get("/wiki_translate/source_article", response_model=TranslateArticleResponse)
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
    x = {"missing_info": output['missing_info'], "extra_info": output['extra_info']}
    print(x)
    return x

    # Defines API URL (host, port)
    uvicorn.run(app, host='127.0.0.1', port=8000)
