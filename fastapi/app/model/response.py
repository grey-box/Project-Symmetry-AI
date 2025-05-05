from typing import List
from pydantic import BaseModel


"""
This is the beta schema that is used to pass data from the backend to the front end.

The source article is passed, along with the languages of the article in 'SourceArticleResponse'.
The UI then selects a language of the article and requests a Wikipedia-provided translation.
The target article is passed back in a second 'SourceArticleResponse'.

The source article and the target article are then passed as array of sentences in 'ComparisonResult',
with the indices of the sentences that are 'missing' from the source article and the sentences that are
'extra' in the source article.

'missing' -> sentences that are found in the source article but not in the target article
'extra' -> sentences that are found in the target article but not in the source article

The final response is then passed as 'CompareResponse' which contains the list of comparison results.
"""


# Class defines the API reponse format for source article (output)
class SourceArticleResponse(BaseModel):
    sourceArticle: str
    """
       Future maintainer: This needs to be modified!
       Currently it returns a list of available short language codes.
       The UI expects a map of short language codes to user-friendly language names, but that isn't
       enough! The UI will also need a title or (ideally) URL to query the correct page in another
       language. This information is available through the request made in wiki_article.py, but is
       not currently returned or expected on the UI side.
    """
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
