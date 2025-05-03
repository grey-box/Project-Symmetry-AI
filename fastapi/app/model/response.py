from typing import List
from pydantic import BaseModel

# Class defines the API reponse format for source article (output)
class SourceArticleResponse(BaseModel):
    sourceArticle: str
    articleLanguages: List[str]

# Class defines the API reponse format for source article (output)
class TranslateArticleResponse(BaseModel):
    translatedArticle: str


class ComparisonResult(BaseModel):
    left_article_array: List[str]
    right_article_array: List[str]
    left_article_missing_info_index: List[int]
    right_article_extra_info_index: List[int]

# Final response schema for the comparison endpoint
class CompareResponse(BaseModel):
    comparisons: List[ComparisonResult]