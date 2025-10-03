import requests
from html_to_markdown import convert_to_markdown
import re
from typing import List, Tuple
from dataclasses import dataclass, field

TITLE = 0
TEXT = 1
MEDIA = 2
TABULAR = 3
REFERENCES = 4

@dataclass
class TextFragment:
    text: str
    missing_info: List[str] = field(default_factory=list)

@dataclass
class ArticleModel:
    titles: list[str] = field(default_factory=list)
    text: list[TextFragment] = field(default_factory=list)
    media: list[str] = field(default_factory=list)
    tabular: list[str] = field(default_factory=list) 
    references: list[str] = field(default_factory=list)

    structure: List[Tuple[int, int]] = field(default_factory=list)

    def add_to_section(self, section_type: int, section_content: str):
        idx = 0
        if section_type == 0:
            self.titles.append(section_content)
            idx = len(self.titles)-1
        elif section_type == 1:
            self.text.append(TextFragment(text=section_content))
            idx = len(self.text)-1
        elif section_type == 2:
            self.media.append(section_content)
            idx = len(self.media)-1
        elif section_type == 3:
            self.tabular.append(section_content)
            idx = len(self.tabular)-1
        elif section_type == 4:
            self.references.append(section_content)
            idx = len(self.references)-1
        self.structure.append((section_type, idx))

def html_to_md(page_name):
    params = {
        "action": "parse",
        "page": page_name,
        "prop": "text",
        "format": "json",
        "formatversion": 2,
        "redirects": 1
    }

    r = requests.get("https://en.wikipedia.org/w/api.php", params=params, headers={"User-Agent": "YourAppName/1.0 (contact@example.com)"}, timeout=30)
    html = r.json()["parse"]["text"]
    markdown = convert_to_markdown(html)

    return markdown

def create_article_model(md_content: str) -> ArticleModel:
    def html_image_to_markdown(html_img):
        src_match = re.search(r'src=["\']([^"\']+)["\']', html_img)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', html_img)
        
        if not src_match:
            return html_img
        
        src = src_match.group(1)
        alt = alt_match.group(1) if alt_match else ''
        
        return f'![{alt}]({src})'

    def is_wiki_reference(text: str) -> bool:
        pattern = r'^\d+\.\s+(\*\*\[\^.*?\]\(#cite_ref-.*?\)\*\*|\^\s+\[)'
        return bool(re.match(pattern, text.strip(), re.DOTALL))

    def strip_wiki_links(text: str) -> str:
        wiki_link_pattern = re.compile(
            r'\[([^\]]+)\]\(\s*(?:[^)\s]*?/wiki/[^)\s]*)(?:\s+"[^"]*")?\s*\)'
        )
        return wiki_link_pattern.sub(r'\1', text)

    def remove_inline_citations(text: str) -> str:
        citation_pattern = re.compile(
            r'\[*\\\[\s*\d+\s*\]\s*\]\(\s*#cite_note-\d+(?:-[^)]+)?\s*\)'
        )
        return citation_pattern.sub('', text)

    def is_table_row(text: str) -> bool:
        pattern = r'^\|.*\|$|^[\|\s]*[-:]+[\|\s\-:]*$'
        return bool(re.match(pattern, text))

    def is_image(text: str) -> bool:
        pattern = r'<img\s+[^>]*?src=["\'].*?["\'][^>]*?/?>'
        return bool(re.match(pattern, text))

    def remove_wiki_edit_links(text):
        pattern = r'\[\[edit\]\([^)]+\)\]'
        return re.sub(pattern, '', text)

    model = ArticleModel()
    if not md_content:
        return model

    # clean article first
    content = strip_wiki_links(md_content)
    content = remove_inline_citations(content)
    content = content.replace("\\", "")    # todo: remove '\' characters
    content = remove_wiki_edit_links(content) # todo: remove wiki [edit] links

    # process references first
    refs_heading_pattern = re.compile(
        r'(?m)^(?:#{1,6}\s*References\s*$|References\s*\n[-=]{3,}\s*$)'
    )
    refstart = refs_heading_pattern.search(content)
    references_str_raw = content[refstart.start():len(content)]

    for ref in references_str_raw.split("\n"):
        if is_wiki_reference(ref):
            model.add_to_section(REFERENCES, ref.strip())

    # process rest of article
    article_content = content[0:refstart.start()]
    article_lines = article_content.split("\n")
    line_idx = 1
    article_end = len(article_lines)-1

    def peek(idx):
        if idx == article_end:
            return ""
        return article_lines[idx+1]

    def parse_table(start_idx):
        table_str = article_lines[start_idx] + "\n"
        idx = start_idx+1
        while idx <= article_end and is_table_row(article_lines[idx]):
            table_str += article_lines[idx] + "\n"
            idx += 1

        model.add_to_section(TABULAR, table_str)
        return idx

    def parse_image(start_idx):
        image_str = article_lines[start_idx] + "\n"
        idx = start_idx+1
        nextline = article_lines[idx]
        while nextline.strip() == "":
            idx+=1
            nextline = article_lines[idx]

        if nextline.startswith("*") and nextline.endswith("*"):
            image_str += nextline + "\n"

        model.add_to_section(MEDIA, image_str)
        return idx+1

    while line_idx <= article_end:
        if article_lines[line_idx] == "" or article_lines[line_idx].isspace():
            line_idx+=1
            continue

        if is_table_row(article_lines[line_idx]):
            line_idx = parse_table(line_idx)
            continue
        elif is_image(article_lines[line_idx]):
            line_idx = parse_image(line_idx)
            continue

        if peek(line_idx).startswith("-"):
            model.add_to_section(TITLE, article_lines[line_idx])
            line_idx += 2
            continue

        # else its text
        model.add_to_section(TEXT, article_lines[line_idx])
        line_idx += 1

    for x in model.tabular:
        print("-"*50)
        print(x)

    return model


# article_titles = ["Pet door", "Owner-occupancy"]
# 
# md = html_to_md(article_titles[1])
# model = create_article_model(md)

