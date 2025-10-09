from synthesis import *
from deep_translator import GoogleTranslator
from tqdm import tqdm

test_article_titles = ["Pet door", "Owner-occupancy"]

model = create_article_model(test_article_titles[1])

for fragment in tqdm(model.text):
    translated = GoogleTranslator(
        source="en", 
        target="fr"
    ).translate(fragment.text)
    fragment.translation = translated

for heading in tqdm(model.titles):
    translated = GoogleTranslator(
        source="en", 
        target="fr"
    ).translate(heading.text)
    heading.translation = translated


target_file_name = "SYNTH_DEMO.md"
synthesized_md_text = ""

for section_type, idx in model.structure:
    if section_type == TITLE:
        synthesized_md_text += f"## {model.titles[idx].translation}\n\n"
    elif section_type == TEXT:
        synthesized_md_text += f"{model.text[idx].translation}\n\n"
    elif section_type == MEDIA:
        synthesized_md_text += model.media[idx] + "\n"
    elif section_type == TABULAR:
        synthesized_md_text += model.tabular[idx] + "\n"
    elif section_type == REFERENCES:
        synthesized_md_text += model.references[idx] + "\n"

with open(target_file_name, 'w') as file: 
    file.write(synthesized_md_text)
print("done.")
