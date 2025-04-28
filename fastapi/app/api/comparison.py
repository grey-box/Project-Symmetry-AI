# Location: fastapi/app/api/comparison_endpoint.py

from fastapi import APIRouter
from app.model.request import CompareRequest
from app.model.response import CompareResponse
from typing import List
# Call semantic_compare function from their LLM code:
from app.ai.semantic_comparison import perform_semantic_comparison

router = APIRouter(prefix="/api/v1", tags=["comparison"])
@router.get("/test")

@router.post("/article/compare", response_model=CompareResponse)
def compare_articles(payload: CompareRequest):
    missing_list, extra_list = perform_semantic_comparison(
        text_a = payload.sourceArticle,
        text_b = payload.translatedArticle,
        similarity_threshold = payload.simThreshold,
        model_name = "sentence-transformers/LaBSE"
    )
    return CompareResponse(missing = missing_list, extra = extra_list) 