from pydantic import BaseModel


"""
This is the schema that is used to pass data from the front end to the backend in order
to begin a comparison of two articles. The two articles and their languages are passed, along with
the comparison threshold (value which determines how similar the comparison should be) and the model name
the user would like to use from the ML comparison.
"""


class CompareRequest(BaseModel):
    article_text_blob_1: str
    article_text_blob_2: str
    article_text_blob_1_language: str
    article_text_blob_2_language: str
    comparison_threshold: float
    model_name: str
