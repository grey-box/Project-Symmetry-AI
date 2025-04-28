from typing import List
from pydantic import BaseModel

# Class defines the API reponse format for source article (output)
class SourceArticleResponse(BaseModel):
    sourceArticle: str
    articleLanguages: List[str]

# Class defines the API reponse format for source article (output)
class TranslateArticleResponse(BaseModel):
    translatedArticle: str

# Class defines the API response format for comparison endpoint
class CompareResponse(BaseModel):
    missing: List[str]
    extra: List[str]