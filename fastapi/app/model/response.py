from typing import List
from pydantic import BaseModel


"""
This is the beta schema that is used to pass data from the backend to the front end post comparison.
The source article is passed, along with the languages of the article in 'SourceArticleResponse'.
The source article and the target article are then passed as array of sentences in 'ComparisonResult',
with the indices of the sentences that are 'missing' from the source article and the sentences that are
'extra' in the source article.

'missing' -> sentences that are found in the target article but not in the source article
'extra' -> sentences that are found in the source article but not in the target article

The final response is then passed as 'CompareResponse' which contains the list of comparison results.
"""


# Class defines the API reponse format for source article (output)
class SourceArticleResponse(BaseModel):
    sourceArticle: str
    articleLanguages: List[str]


# Schema for a single comparison
class ComparisonResult(BaseModel):
    left_article_array: List[str]
    right_article_array: List[str]
    left_article_missing_info_index: List[int]
    right_article_extra_info_index: List[int]


# Final response schema for the comparison endpoint
class CompareResponse(BaseModel):
    comparisons: List[ComparisonResult]
