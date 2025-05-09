from pydantic import BaseModel

class Url(BaseModel):
    address: str

class Comparator(BaseModel):
    source: str
    target: str
