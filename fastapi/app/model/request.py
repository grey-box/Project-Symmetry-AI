from pydantic import BaseModel


class CompareRequest(BaseModel):
    article_text_blob_1: str
    article_text_blob_2: str
    article_text_blob_1_language: str
    article_text_blob_2_language: str
    comparison_threshold: float
    model_name: str
