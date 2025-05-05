# Standard library imports
import logging
import re
import asyncio
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError
from typing import Dict, Optional, Annotated
import hashlib
from time import time
from typing import List

# Third-party imports
import wikipediaapi
from fastapi import APIRouter, Query, HTTPException

# Local imports
from ..model.response import SourceArticleResponse
from .cache import get_cached_article, set_cached_article

# Initialize the router for wiki related endpoints
router = APIRouter(prefix="/symmetry/v1/wiki")

# This caches short language codes existing on Wikipedia.
language_cache: Dict[str, bool] = {}

# GET request method with input validation
@router.get("/articles", response_model=SourceArticleResponse)
async def get_article(
    query: Annotated[Optional[str], Query(description="Either a full Wikipedia URL or a keyword/title"),] = None,
    lang: Annotated[Optional[str], Query(description="Article language code")] = None,):

    """
       This endpoint requests an article from Wikipedia.

       If the query is a URL, the lang parameter is overwritten with a value parsed from the URL.
       If the query is a title, the language parameter is used, defaulting to 'en' for English.

    EXPLANATION OF ENDPOINT CONCATENATION USING THE EXAMPLE QUERY:
       Consider the example query:
       http://127.0.0.1:8000/symmetry/v1/wiki/articles?query=https://en.wikipedia.org/wiki/covid

       1. Base URL (http://127.0.0.1:8000): This specifies the host (your local machine at IP address 127.0.0.1)
          and the port (8000) where your FastAPI application is running. This port is declared in main.py.

       2. Router Prefix (/symmetry/v1/wiki): The APIRouter is initialized with this prefix. It acts as a base path
          for all the endpoints defined within this router, creating a logical grouping for wiki-related functionality.

       3. Endpoint Path (/articles): The @router.get("/articles", ...) decorator registers the 'get_article' function
          to handle GET requests at this specific path. This path is appended to the router's prefix.

       4. Concatenated Endpoint (/symmetry/v1/wiki/articles): FastAPI automatically combines the router's prefix
          and the endpoint path to form the full URL path for this resource.

       5. Query Parameters (?query=https://en.wikipedia.org/wiki/covid): The part after the '?' consists of query
          parameters. In this case, 'query' is the parameter name, and 'https://en.wikipedia.org/wiki/covid' is its
          value. This is how you pass data to the GET request. The 'query' parameter is defined in the
          'get_article' function signature using FastAPI's 'Query' dependency.

       In summary, the endpoint "/symmetry/v1/wiki/articles" is constructed by joining the router's prefix and the
       path defined in the GET decorator. The data you want to send to this endpoint (like the Wikipedia URL) is
       then appended to this URL as a query parameter.

       In the future when Symmetry adds support for more platforms, it is suggested
       that this endpoint is phased out and transformed into a helper method.
    """

    logging.info("Calling get Wikipedia article endpoint (query='%s')", query)

    if not query:
        logging.info("No query parameter provided.")
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL provided.")

    if "wikipedia.org" in query:
        url = query
        title = extract_title_from_url(query)
        if not title:
            logging.info("Unable to parse title from URL.")
            raise HTTPException(status_code=400, detail="Invalid article path.")
    else:
        url = None
        title = query

    if url:
        parsed_lang = await validate_url(url)
        if not lang:
            lang = parsed_lang

    if not lang:
        lang = "en"

    cached_content, cached_languages = get_cached_article(lang + "." + title)
    if cached_content:
        return {"sourceArticle": cached_content, "articleLanguages": cached_languages}


    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent="Symmetry/2.0 (contact@grey-box.ca)", language=lang
    )

    page = wiki_wiki.page(title)

    if not page.exists():
        raise HTTPException(status_code=404, detail="Article not found.")

    article_content = page.text
    languages = list(page.langlinks.keys()) if page.langlinks else []

    set_cached_article(lang + "." + title, article_content, languages)

    return {"sourceArticle": article_content, "articleLanguages": languages}


async def validate_url(url):
    """
       This method is used to validate a Wikipedia article URL.
       The URL should match the general format <language_code>.wikipedia.org/wiki/<article_title>

       It returns the language code included in the URL.
    """

    parsed_url = urlparse(url)

    if not parsed_url.netloc.endswith(".wikipedia.org"):
        logging.info(
            "Invalid domain '%s', only 'wikipedia.org' is allowed.",
            parsed_url.netloc,
        )
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL.")

    split_url = parsed_url.netloc.split(".")

    if len(split_url) != 3:
        logging.info(
            "Invalid subdomain '%s', only '__.wikipedia.org' is allowed.",
            parsed_url.netloc,
        )
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL.")

    lang = split_url[0]
    if not lang.isalpha() or len(lang) > 2:
        logging.info("Invalid language code '%s'", lang)
        raise HTTPException(status_code=400, detail="Invalid language code in URL.")

    await validate_language_code(lang)

    if not parsed_url.path.startswith("/wiki/"):
        logging.debug("Invalid wiki article path '%s'", parsed_url.path)
        raise HTTPException(status_code=400, detail="Invalid wiki article path.")
    return lang


# Language validator and main page ping
async def validate_language_code(language_code: str):
    if language_code in language_cache:
        logging.info(f"Using cached validation for language code: {language_code}")
        return language_cache[language_code]

    url = f"https://{language_code}.wikipedia.org/wiki/Main_Page"

    try:
        response = await asyncio.to_thread(urllib.request.urlopen, url)

        if response.status == 200:
            logging.info(f"Valid language code: {language_code}")
            language_cache[language_code] = True
            return True
        else:
            language_cache[language_code] = False
            raise HTTPException(
                status_code=400, detail=f"Invalid language code '{language_code}'."
            )

    except URLError:
        language_cache[language_code] = False
        raise HTTPException(
            status_code=400, detail=f"Invalid language code '{language_code}'."
        )
    except Exception as e:
        language_cache[language_code] = False
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred during language code validation: {str(e)}",
        )


def extract_title_from_url(url: str) -> Optional[str]:
    match = re.search(r"/wiki/([^#?]*)", url)
    if match:
        return match.group(1).replace("_", " ")
    return None
