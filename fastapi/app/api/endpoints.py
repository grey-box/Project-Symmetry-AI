import logging

from fastapi import HTTPException
from fastapi import Query

from fastapi import APIRouter, Query, HTTPException
from ..models.api_models import ComparisonResponse, ModelSelectionResponse, TranslationResponse, ArticleResponse
from ..main import server
from ..ai.semantic_comparison import semantic_compare

router = APIRouter()

@router.get("/get_article", response_model=ArticleResponse)
def get_article(url: str = Query(None), title: str = Query(None)):
    logging.info("Calling get article endpoint")

    if url:
        title = server.extract_title_from_url(url)
        if not title:
            logging.info("Invalid Wikipedia URL provided.")
            raise HTTPException(status_code=400, detail="Invalid Wikipedia URL provided.")

    if not title:
        logging.info("Either 'url' or 'title' must be provided.")
        raise HTTPException(status_code=400, detail="Either 'url' or 'title' must be provided.")

    page = server.wikipedia.page(title)

    if not page.exists():
        logging.info("Article not found.")
        raise HTTPException(status_code=404, detail="Article not found.")

    article_content = page.text  # Get the article text

    # Fetch available languages
    languages = list(page.langlinks.keys())

    return {"source_article": article_content, "article_languages": languages}

@router.get("/translate", response_model=TranslationResponse)
def translate_article(
        source_language: str = Query(...),
        target_language: str = Query(...),
        text: str = Query(...)
    ):
    pass

@router.get("/comparison/semantic_comparison", response_model=ComparisonResponse)
def compare_articles(
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        similarity_threshold: float = 0.75
    ):
    logging.info("Calling semantic comparison endpoint.")

    if similarity_threshold < 0 or similarity_threshold > 1:
        err_msg = "Provided similarity threshold is out of the defined valid range [0,1]"
        logging.info(err_msg)
        raise HTTPException(
            status_code=400, 
            detail=err_msg
        )

    if original_text.isnumeric() or translated_text.isnumeric():
        err_msg = "Either text_a or text_b was not the correct input type."
        logging.info(err_msg)
        raise HTTPException(
            status_code=400, 
            detail=err_msg
        )

    output = semantic_compare(
        original_text,
        translated_text,
        source_language,
        target_language, 
        similarity_threshold
    )

    return output

@router.get("/models/translation/select", response_model=ModelSelectionResponse)
def select_model(modelname: str):
    return server.select_translation_model(modelname)

@router.get("/models/translation/delete", response_model=ModelSelectionResponse)
def delete_model(modelname: str):
    return server.delete_translation_model(modelname)

@router.get("/models/translation/import", response_model=ModelSelectionResponse)
def import_model(model: str, from_huggingface: bool):
    return server.import_new_translation_model(model, from_huggingface)

@router.get("/models/comparison/select", response_model=ModelSelectionResponse)
def select_model(modelname: str):
    return server.select_comparison_model(modelname)

@router.get("/models/comparison/delete", response_model=ModelSelectionResponse)
def delete_model(modelname: str):
    return server.delete_comparison_model(modelname)

@router.get("/models/comparison/import", response_model=ModelSelectionResponse)
def import_model(model: str, from_huggingface: bool):
    return server.import_new_comparison_model(model, from_huggingface)