from pydantic import BaseModel
from typing import List, Optional

class Citation(BaseModel):
    label: str # The text that links (e.g., "Fonda Theatre")
    url: Optional[str] = None # URL that redirects to other Wikipedia page

# Holds reference content (Footnote/Source reference markers)
class Reference(BaseModel):
    label: str # The marker (e.g., "[1]") or full text of the reference
    id: Optional[str] = None # The HTML id (e.g., "cite_note-1")
    url: Optional[str] = None # Optional URL from the full reference text

# Holds section content
class Section(BaseModel):
    title: str
    raw_content: str
    clean_content: str
    citations: Optional[List[Citation]] = None # Citation objects (Internal Wikipedia links)
    citation_position: Optional[List[str]] = None # Positional data: formatted as "link_label:start_index"

# Head of Article
class Article(BaseModel):
    title: str
    lang: str
    source: str
    sections: List[Section]
    references: List[Reference] # Full list of footnotes/sources
