import requests
from html_to_markdown import convert_to_markdown
import re
from typing import List, Tuple

def html_to_md(page_name):
    params = {
        "action": "parse",
        "page": "Pet door", #replace
        "prop": "text",
        "format": "json",
        "formatversion": 2,
        "redirects": 1
    }
    r = requests.get("https://en.wikipedia.org/w/api.php", params=params, headers={"User-Agent": "YourAppName/1.0 (contact@example.com)"}, timeout=30)
    html = r.json()["parse"]["text"]
    out_path = "page.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    markdown = convert_to_markdown(html)
    md_pth = "page.md"
    with open(md_pth, "w", encoding="utf-8") as f:
        f.write(markdown)

    return markdown


import re
from typing import List, Tuple


import re
from typing import List, Tuple

def split_markdown_advanced(content: str) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Returns:
      - image_lines: full lines like [<img ...>](...) captured verbatim
      - tables: raw Markdown table blocks
      - paragraphs: remaining paragraphs after filtering
      - references_blocks: a list with one element containing the entire References section as a single string
                           (or empty if not found), with '/wiki/' links stripped to plain text and edit line removed

    Behaviors:
      - Remove any Markdown links whose URL contains '/wiki/' (preserve label).
      - Remove any line that starts with '[[edit]'.
      - Remove inline citation anchors like '[[5]](#cite_note-5)' or '[[12]](#cite_note-12)'.
      - Image lines that start with '[<img ...>](...)' are returned in image_lines and removed from paragraphs.
      - References section (from its heading to before the next heading or EOF) is extracted and returned as one string.
    """
    if not content:
        return [], [], [], []

    original = content



    # Utility: strip wiki links "[label](/wiki/...)" -> "label"
    wiki_link_pattern = re.compile(
        r'\[([^\]]+)\]\(\s*(?:[^)\s]*?/wiki/[^)\s]*)(?:\s+"[^"]*")?\s*\)'
    )
    def strip_wiki_links(text: str) -> str:
        return wiki_link_pattern.sub(r'\1', text)

    # Utility: remove inline citation links of the form [[5]](#cite_note-5) or [[7]](#cite_note-7)
    # Be lenient about the fragment suffix: #cite_note-7, #cite_note-7-0, etc.
    citation_pattern = re.compile(
        r'\[*\\\[\s*\d+\s*\]\s*\]\(\s*#cite_note-\d+(?:-[^)]+)?\s*\)'
    )
    def remove_inline_citations(text: str) -> str:
        return citation_pattern.sub('', text)

    # 1) Extract the References section first, so it can be returned verbatim (with requested cleanups).
    refs_heading_pattern = re.compile(
        r'(?m)^(?:#{1,6}\s*References\s*$|References\s*\n[-=]{3,}\s*$)'
    )
    references_blocks: List[str] = []
    text = original

    m = refs_heading_pattern.search(text)
    if m:
        start = m.start()
        # Find end: next heading (ATX or Setext) after start, else EOF
        next_heading_pattern = re.compile(
            r'(?m)^(?:#{1,6}\s*\S.*$|[^\n]+\n[-=]{3,}\s*$)'
        )
        next_m = next_heading_pattern.search(text, m.end())
        end = next_m.start() if next_m else len(text)
        refs_raw = text[start:end]

        # Inside references: remove the edit line and inline citation anchors, strip /wiki/ links
        refs_lines = []
        for line in refs_raw.splitlines():
            if line.lstrip().startswith('[[edit]'):
                continue
            refs_lines.append(line)
        refs_clean = "\n".join(refs_lines)
        refs_clean = remove_inline_citations(refs_clean)
        refs_clean = strip_wiki_links(refs_clean)

        # Keep as a single string
        refs_clean = refs_clean.strip()
        if refs_clean:
            references_blocks.append(refs_clean)

        # Remove the references block from main text
        text = text[:start] + text[end:]

    # 3) Extract full image lines of the form [<img ...>](...)
    image_lines: List[str] = []
    remaining_lines = []
    img_line_pattern = re.compile(r'^\s*\[\s*<img\b[^>]*>\s*\]\([^)]+\)\s*$', re.IGNORECASE)
    for line in text.splitlines():
        if img_line_pattern.match(line):
            image_lines.append(line.rstrip())
            continue
        remaining_lines.append(line)
    text = "\n".join(remaining_lines)

    # 2) Global removals/rewrites on the remaining text
    # 2a) Remove any line that starts with '[[edit]'
    kept_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith('\\[[edit]'):
            continue
        kept_lines.append(line)
    text = "\n".join(kept_lines)

    # 2b) Remove inline citation anchors like [[5]](#cite_note-5)
    text = remove_inline_citations(text)

    # 2c) Strip /wiki/ links globally, preserving label
    text = strip_wiki_links(text)



    # 4) Extract Markdown tables as blocks
    lines = text.splitlines()
    tables: List[str] = []
    used_line_idx = set()

    def is_table_sep(line: str) -> bool:
        return bool(re.match(
            r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$',
            line
        ))

    i = 0
    while i < len(lines):
        if "|" in lines[i]:
            j = i + 1
            found_sep = False
            while j < len(lines) and (j - i) <= 5 and "|" in lines[j]:
                if is_table_sep(lines[j]):
                    found_sep = True
                    break
                j += 1
            if found_sep:
                start = i
                end = j + 1
                while end < len(lines) and "|" in lines[end]:
                    end += 1
                block = "\n".join(lines[start:end]).strip()
                if block:
                    tables.append(block)
                    for idx in range(start, end):
                        used_line_idx.add(idx)
                i = end
                continue
        i += 1

    # 5) Build paragraphs from remaining lines (excluding table lines and blank separators)
    paragraphs: List[str] = []
    buf: List[str] = []

    def flush_buf():
        if buf:
            block = "\n".join(buf).strip()
            if block:
                paragraphs.append(block)
            buf.clear()

    for idx, line in enumerate(lines):
        if idx in used_line_idx:
            flush_buf()
            continue
        if line.strip() == "":
            flush_buf()
        else:
            buf.append(line)
    flush_buf()

    # Remove accidental table separators in paragraphs if any
    cleaned_paragraphs = []
    for block in paragraphs:
        if any(is_table_sep(l) for l in block.splitlines()):
            continue
        cleaned_paragraphs.append(block)

    return image_lines, tables, cleaned_paragraphs, references_blocks

md = html_to_md("")
dedup_images, tables, cleaned_paragraphs, references = split_markdown_advanced(md)

print(dedup_images)
print(tables)
print(cleaned_paragraphs)
print(references)