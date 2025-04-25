import logging
import re

import wikipediaapi
from fastapi import APIRouter, Query, HTTPException
from ..model.response import SourceArticleResponse, TranslateArticleResponse

router = APIRouter()

wiki_wiki = wikipediaapi.Wikipedia(user_agent='MyApp/2.0 (contact@example.com)', language='en')  # English Wikipedia instance

@router.get("/get_article", response_model=SourceArticleResponse)
def get_article(query: str = Query(..., description="Either a full Wikipedia URL or a keyword/title")):
    logging.info("Calling get article endpoint with query parameter")

    # If the query contains “wikipedia.org”, we assume it’s a URL and extract the title
    if "wikipedia.org" in query:
        title = extract_title_from_url(query)
        if not title:
            logging.info("Invalid Wikipedia URL provided.")
            raise HTTPException(status_code=400, detail="Invalid Wikipedia URL provided.")
    else:
        # else: we assume the query is the title
        title = query

    page = wiki_wiki.page(title)

    # Check if Wikipedia page exists
    if not page.exists():
        logging.info("Article not found.")
        raise HTTPException(status_code=404, detail="Article not found.")

    article_content = page.text  # Get the article text

    # Fetch available languages
    languages = list(page.langlinks.keys())

    return {"sourceArticle": article_content, "articleLanguages": languages}

def extract_title_from_url(url: str) -> str:
    match = re.search(r'/wiki/([^#?]*)', url)
    if match:
        return match.group(1).replace('_', ' ')
    return None

@router.get("translate/sourceArticle", response_model=TranslateArticleResponse)
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

    return {"translatedArticle": translated_content}
