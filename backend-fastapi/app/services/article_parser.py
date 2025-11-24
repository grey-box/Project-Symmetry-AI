import requests
from bs4 import BeautifulSoup
from typing import List, Optional

# Import Pydantic models from centralized location
from app.models.wiki_structure import Citation, Reference, Section, Article


# --- article_fetcher
def article_fetcher(title, lang):
    url = f"https://{lang}.wikipedia.org/w/api.php"  # Base URL for MediaWiki Action API
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "disableeditsection": True,
        "disabletoc": True
    }
    r = requests.get(url, params=params, headers={"User-Agent": "SymmetryFetcher/1.0"})
    r.raise_for_status()
    data = r.json()

    html = data.get("parse", {}).get("text", {}).get("*", "")
    soup = BeautifulSoup(html, "html.parser")

    sections = []
    current_title = "Lead section"
    rich_current = ""
    clean_current = ""
    current_citations = []  # List of Citation objects (internal links)
    current_citation_positions = [] # List of strings for positional data
    current_references = [] # List of Reference objects (in-text reference markers)

    content_tags = soup.find_all(["h2", "h3", "p"])

    # --- Step 1: Parse Sections and Capture Citations/References/Positions ---
    for tag in content_tags:
        if tag.name in ["h2", "h3"]:
            # Save previous section
            if clean_current.strip():
                section = Section(
                    title=current_title,
                    raw_content=rich_current.strip(),
                    clean_content=clean_current.strip(),
                    citations=current_citations,
                    citation_position=current_citation_positions
                )
                sections.append(section)

            # Start a new section
            current_title = tag.get_text(strip=True)
            rich_current = ""
            clean_current = ""
            current_citations = []
            current_citation_positions = []
            current_references = [] # Clear references for the new section

        elif tag.name == "p":
            char_count = len(clean_current.strip()) # Starting position for elements in this paragraph
            
            # The paragraph content must be parsed element by element
            for element in tag.contents:
                
                # Element is a BeautifulSoup Tag (e.g., <a> or <sup>)
                if hasattr(element, 'name'):
                    
                    # A. Handle Reference Markers (e.g., [1])
                    if element.name == "sup" and element.has_attr("class") and "reference" in element["class"]:
                        label = element.get_text(strip=True)
                        link = element.find("a", href=True)
                        ref_id = link["href"].replace("#", "") if link else None
                        
                        # Store the in-text reference marker data
                        current_references.append(Reference(label=label, id=ref_id))
                        
                        # Add the label to rich_current but NOT clean_content
                        rich_current += f" {label}"
                        continue 

                    # B. Handle Internal Hyperlinks (Citations in this model structure)
                    elif element.name == "a" and element.get('href', '').startswith('/wiki/'):
                        text = element.get_text(strip=True)
                        
                        # Determine position before appending the text to clean_content
                        # Add 1 space if char_count > 0, otherwise start at 0
                        position = char_count + 1 if char_count > 0 else char_count
                        
                        # Store the link data (Citation object)
                        hyperlink = f"https://{lang}.wikipedia.org{element.get('href', '')}"
                        current_citations.append(Citation(label=text, url=hyperlink))
                        
                        # Store positional data
                        current_citation_positions.append(f"{text}:{position}")
                        
                        # Append text to content strings
                        clean_current += " " + text
                        rich_current += f" ({hyperlink}, {len(text.split())})" # Rich content gets link details
                        rich_current += " " + text
                        
                        # Update char_count based on what was added to clean_content
                        char_count += (1 + len(text))
                        continue
                        
                    # C. Handle Other Elements (like <b>, <i>, etc.)
                    else:
                        text = element.get_text(strip=True)
                        if text:
                            clean_current += " " + text
                            rich_current += " " + text
                            char_count += (1 + len(text))

                # Element is a NavigableString (simple text)
                else:
                    text = str(element).strip()
                    if text:
                        clean_current += " " + text
                        rich_current += " " + text
                        char_count += (1 + len(text))


    # Append last section if any
    if clean_current.strip():
        section = Section(
            title=current_title,
            raw_content=rich_current.strip(),
            clean_content=clean_current.strip(),
            citations=current_citations,
            citation_position=current_citation_positions
        )
        sections.append(section)

    # --- Step 2: Parse Full Reference Data ---
    full_references_data = []
    reference_map = {} 
    references_list = soup.select("ol.references > li")

    for ref in references_list:
        ref_id = ref.get("id", None)
        
        # Remove back-link markers (e.g., ^ a b c) for clean text
        backlinks = ref.select("span.mw-cite-backlink")
        for bl in backlinks:
            bl.decompose()
            
        ref_text = ref.get_text(" ", strip=True)
        
        # Try to find the external URL
        link_tag = ref.find("a", href=lambda href: href and href.startswith("http"))
        link = link_tag["href"] if link_tag else None
        
        # The Reference model for the Article list will store the full citation text
        reference = Reference(label=ref_text, id=ref_id, url=link)
        full_references_data.append(reference)
        if ref_id:
            reference_map[ref_id] = reference # Store map for optional future use


    article = Article(
        title=title,
        lang=lang,
        source="action_api",
        sections=sections,
        references=full_references_data
    )
    return article


if __name__ == "__main__":
    article = article_fetcher("Sheikh Hasina", "en")
    print(f"Title: {article.title}\n")

    for sec in article.sections:
        print(f"## {sec.title}")
        print("Clean Content:", sec.clean_content.strip()[:200] + "...")
        
        if sec.citations:
            print("\n### Citations (Internal Links)")
            for citation in sec.citations:
                print(f"* Label: '{citation.label}' | URL: {citation.url}")
            
            print("\n### Citation Positions")
            print(sec.citation_position)
        
        print("\n---")
    
    print("\n## Full References List (Footnotes)")
    for r in article.references:
        print(f"ID: {r.id}")
        print(f"Text: {r.label[:80]}...")
        print(f"URL: {r.url}\n")
