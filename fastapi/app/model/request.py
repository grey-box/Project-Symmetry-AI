from pydantic import BaseModel
from typing import List

class Url(BaseModel):
    address: str

class Comparator(BaseModel):
    source: str
    target: str

class CompareRequest(BaseModel):
    sourceArticle: str
    translatedArticle: str
    language: List[str]
    simThreshold: float