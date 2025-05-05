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

# Initialize the router for wiki related endpoints
router = APIRouter(prefix="/symmetry/v1/wiki")

# Cache dictionaries with TTL mechanisms
article_cache: Dict[str, Dict] = {}
language_cache: Dict[str, bool] = {}


# GET request method with input validation
@router.get("/articles", response_model=SourceArticleResponse)
async def get_article(
    query: Annotated[
        Optional[str],
        Query(description="Either a full Wikipedia URL or a keyword/title"),
    ] = None,
    lang: Annotated[str, Query(description="Article language code")] = "en",
):
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

    # If the query contains “wikipedia.org”, we assume it’s a URL and extract the title
    if "wikipedia.org" in query:
        url = query
        title = extract_title_from_url(query)
        if not title:
            logging.info("Unable to parse title from URL.")
            raise HTTPException(status_code=400, detail="Invalid article path.")
    else:
        url = None
        title = query

    # Check cache before proceeding
    cached_content, cached_languages = get_cached_article(title)
    if cached_content:
        return {"sourceArticle": cached_content, "articleLanguages": cached_languages}

    # If the query is a URL, validate it and set language from it.
    if url:
        lang = await validate_url(url)

    # Dynamically create Wikipedia object for the selected language
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent="MyApp/2.0 (contact@example.com)", language=lang
    )

    page = wiki_wiki.page(title)

    # Check if Wikipedia page exists
    if not page.exists():
        raise HTTPException(status_code=404, detail="Article not found.")

    article_content = page.text
    languages = list(page.langlinks.keys()) if page.langlinks else []

    # Cache the article and languages
    set_cached_article(title, article_content, languages)

    return {"sourceArticle": article_content, "articleLanguages": languages}


async def validate_url(url):
    """
       This method is used to validate a Wikipedia article URL.
       The URL should match the general format <language_code>.wikipedia.org/wiki/<article_title>

       It returns the language code included in the URL.
    """

    # Parse the URL with urllib
    parsed_url = urlparse(url)

    # Domain validation
    if not parsed_url.netloc.endswith(".wikipedia.org"):
        logging.info(
            "Invalid domain '%s', only 'wikipedia.org' is allowed.",
            parsed_url.netloc,
        )
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL.")

    split_url = parsed_url.netloc.split(".")

    # Ensure that URL matches the format '<language_code>.wikipedia.org'
    if len(split_url) != 3:
        logging.info(
            "Invalid subdomain '%s', only '__.wikipedia.org' is allowed.",
            parsed_url.netloc,
        )
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL.")

    # Language code syntax validation
    lang = split_url[0]
    if not lang.isalpha() or len(lang) > 2:
        logging.info("Invalid language code '%s'", lang)
        raise HTTPException(status_code=400, detail="Invalid language code in URL.")

    # Validate language code through preflight check
    await validate_language_code(lang)

    # Validate the path starts with '/wiki/'
    if not parsed_url.path.startswith("/wiki/"):
        logging.debug("Invalid wiki article path '%s'", parsed_url.path)
        raise HTTPException(status_code=400, detail="Invalid wiki article path.")
    return lang


# Function to generate a unique key for each URL
def get_article_cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


# Check if article is cached and still valid
def get_cached_article(title: str):
    cache_key = get_article_cache_key(title)
    cached_data = article_cache.get(cache_key)

    if cached_data:
        if time() - cached_data["timestamp"] < 10000:  # TTL
            logging.info("Returning cached article")
            return cached_data["content"], cached_data["languages"]
        else:
            # Cache expired, remove it
            del article_cache[cache_key]

    return None, None


# Cache the article content and associated languages
def set_cached_article(url: str, content: str, languages: List[str]):
    cache_key = get_article_cache_key(url)
    article_cache[cache_key] = {
        "content": content,
        "languages": languages,
        "timestamp": time(),
    }


# Language validator and pre-flight request
async def validate_language_code(language_code: str):
    # Check cache first
    if language_code in language_cache:
        logging.info(f"Using cached validation for language code: {language_code}")
        return language_cache[language_code]

    # Ping main page for validation
    url = f"https://{language_code}.wikipedia.org/wiki/Main_Page"

    try:
        # Use asyncio.to_thread to run the blocking urllib request in a separate thread
        response = await asyncio.to_thread(urllib.request.urlopen, url)

        if response.status == 200:
            logging.info(f"Valid language code: {language_code}")
            language_cache[language_code] = True  # Cache the validation result
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
        # Handle generic exceptions
        language_cache[language_code] = False
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred during language code validation: {str(e)}",
        )


# Helper method to extract title from URL
def extract_title_from_url(url: str) -> Optional[str]:
    match = re.search(r"/wiki/([^#?]*)", url)
    if match:
        return match.group(1).replace("_", " ")
    return None
