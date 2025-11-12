from pydantic import BaseModel
from typing import List

class ComparisonResponse(BaseModel):
    missing_info: List[str]
    extra_info: List[str]

class TranslationResponse(BaseModel):
    translated_text: str
    successful: bool

class ArticleResponse(BaseModel):
    source_article: str
    article_languages: List[str]

class ModelSelectionResponse(BaseModel):
    successful: str




