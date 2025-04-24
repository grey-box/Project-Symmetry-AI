import logging
import re
import sys
from traceback import format_exc

import wikipediaapi
from fastapi import APIRouter, Query, HTTPException
from ..model.response import SourceArticleResponse, TranslateArticleResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

router = APIRouter()

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="MyApp/2.0 (contact@example.com)", language="en"
)  # English Wikipedia instance


async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for HTTPExceptions to include stack trace in debug mode."""
    if app.debug:
        return JSONResponse(
            {"detail": exc.detail, "stack_trace": format_exc()},
            status_code=exc.status_code,
        )
    else:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def generic_exception_handler(request: Request, exc: Exception):
    """Custom handler for generic Exceptions to provide a standardized error and stack trace in debug mode."""
    logging.error(f"Unhandled exception: {exc}")
    if app.debug:
        return JSONResponse(
            {"detail": "Internal Server Error", "stack_trace": format_exc()},
            status_code=500,
        )
    else:
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)


@router.get("/get_article", response_model=SourceArticleResponse)
def get_article(url: str = Query(None), title: str = Query(None)):
    logging.info("Calling get article endpoint")
    try:
        if url:
            title = extract_title_from_url(url)
            if not title:
                logging.info("Invalid Wikipedia URL provided.")
                raise HTTPException(
                    status_code=400, detail="Invalid Wikipedia URL provided."
                )

        if not title:
            logging.info("Either 'url' or 'title' must be provided.")
            raise HTTPException(
                status_code=400, detail="Either 'url' or 'title' must be provided."
            )

        page = wiki_wiki.page(title)

        if not page.exists():
            logging.info("Article not found.")
            raise HTTPException(status_code=404, detail=f"Article {title} not found.")

        article_content = page.text  # Get the article text

        # Fetch available languages
        languages = list(page.langlinks.keys())

        return {"sourceArticle": article_content, "articleLanguages": languages}
    except HTTPException:
        raise  # Re-raise HTTPExceptions as they are already handled
    except Exception as e:
        logging.error(f"Error fetching article: {e}")
        raise


def extract_title_from_url(url: str) -> str:
    match = re.search(r"/wiki/([^#?]*)", url)
    if match:
        return match.group(1).replace("_", " ")
    return None


@router.get("translate/sourceArticle", response_model=TranslateArticleResponse)
def translate_article(
    url: str = Query(None), title: str = Query(None), language: str = Query(...)
):
    logging.info(
        f"Calling translate article endpoint for title: {title}, url: {url} and language: {language}"
    )
    try:
        if url:
            title = extract_title_from_url(url)
            if not title:
                logging.info("Invalid Wikipedia URL provided.")
                raise HTTPException(
                    status_code=400, detail="Invalid Wikipedia URL provided."
                )

        if not title:
            logging.info("Either 'url' or 'title' must be provided.")
            raise HTTPException(
                status_code=400, detail="Either 'url' or 'title' must be provided."
            )

        translated_wiki = wikipediaapi.Wikipedia(
            user_agent="MyApp/1.0 (contact@example.com)", language=language
        )
        translated_page = translated_wiki.page(title)

        if not translated_page.exists():
            logging.info("Translated article not found.")
            raise HTTPException(status_code=404, detail="Translated article not found.")

        translated_content = translated_page.text if translated_page.text else ""

        return {"translatedArticle": translated_content}
    except HTTPException:
        raise  # Re-raise HTTPExceptions as they are already handled
    except Exception as e:
        logging.error(f"Error fetching translated article: {e}")
        raise
