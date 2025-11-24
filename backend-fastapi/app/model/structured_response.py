from typing import List, Optional
from pydantic import BaseModel
from app.models.wiki_structure import Citation, Reference, Section


class StructuredArticleResponse(BaseModel):
    """Response model for structured Wikipedia articles with rich metadata."""
    title: str
    lang: str
    source: str
    sections: List[Section]
    references: List[Reference]
    total_sections: int
    total_citations: int
    total_references: int


class StructuredSectionResponse(BaseModel):
    """Response model for a single section with metadata."""
    title: str
    raw_content: str
    clean_content: str
    citations: Optional[List[Citation]] = None
    citation_position: Optional[List[str]] = None
    word_count: int
    citation_count: int


class StructuredCitationResponse(BaseModel):
    """Response model for citation analysis."""
    citations: List[Citation]
    total_citations: int
    unique_targets: int
    most_cited_articles: List[dict]  # List of {title: str, count: int}


class StructuredReferenceResponse(BaseModel):
    """Response model for reference analysis."""
    references: List[Reference]
    total_references: int
    references_with_urls: int
    reference_density: float  # references per 1000 words
