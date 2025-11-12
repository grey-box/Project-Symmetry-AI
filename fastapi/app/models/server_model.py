from sentence_transformers import SentenceTransformer
from dataclasses import dataclass, field
from typing import List, Optional
import wikipediaapi
from ..ai.synthesis import ArticleModel
import re
import json
from pathlib import Path

def load_saved_models(domain: str, model_type: str):
    with open("saved_models.json", 'r') as file:
        data = json.load(file)
        return data[domain][model_type]

@dataclass
class ServerModel:
    hf_comparison_models: List[str] = field(default_factory=lambda: load_saved_models("huggingface", "comparison")) 
    hf_translation_models: List[str] = field(default_factory=lambda: load_saved_models("huggingface", "translation"))

    custom_comparison_models: List[str] = field(default_factory=lambda: load_saved_models("custom", "comparison"))
    custom_translation_models: List[str] = field(default_factory=lambda: load_saved_models("custom", "translation"))

    selected_comparison_model: str = field(default="sentence-transformers/LaBSE")
    selected_translation_model: str = field(default="/path/to/T5-custom")

    wikipedia: Optional[wikipediaapi.Wikipedia] = field(default=None)

    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        self.wikipedia = wikipediaapi.Wikipedia(user_agent='MyApp/2.0 (contact@example.com)', language='en')



    def import_new_translation_model(self, model: str, from_hub: bool) -> bool:
        if not from_hub:
            model_filepath = Path(model)
            if not model_filepath.exists():
                return False

            if model in self.custom_translation_models:
                return True
            
            with open('saved_models.json', 'r') as f:
                data = json.load(f)
            data["custom"]['translation'].append(str(model_filepath))
            with open('saved_models.json', 'w') as f:
                json.dump(data, f, indent=2)
            self.custom_translation_models.append(str(model_filepath))

            return True
        
        try:
            model = SentenceTransformer(model)
        except:
            return False

        if model in self.hf_translation_models:
            return True
        
        # write model name to comparison models in json
        with open('saved_models.json', 'r') as f:
            data = json.load(f)
        data["huggingface"]['translation'].append(model)
        with open('saved_models.json', 'w') as f:
            json.dump(data, f, indent=2)
        self.hf_comparison_models.append(model)
        
        return True

    def import_new_comparison_model(self, model: str, from_hub: bool) -> bool:
        if not from_hub:
            model_filepath = Path(model)
            if not model_filepath.exists():
                return False

            if model in self.custom_comparison_models:
                return True
            
            with open('saved_models.json', 'r') as f:
                data = json.load(f)
            data["custom"]['comparison'].append(str(model_filepath))
            with open('saved_models.json', 'w') as f:
                json.dump(data, f, indent=2)
            self.custom_comparison_models.append(str(model_filepath))

            return True
        
        try:
            model = SentenceTransformer(model)
        except:
            return False

        if model in self.hf_comparison_models:
            return True
        
        # write model name to comparison models in json
        with open('saved_models.json', 'r') as f:
            data = json.load(f)
        data["huggingface"]['comparison'].append(model)
        with open('saved_models.json', 'w') as f:
            json.dump(data, f, indent=2)
        self.hf_comparison_models.append(model)
        
        return True

    def select_comparison_model(self, model_name: str) -> bool:
        if model_name in self.hf_comparison_models:
            self.selected_comparison_model = model_name
            return True

        start_ptr = 0
        end_ptr = len(self.custom_comparison_models) - 1

        while start_ptr <= end_ptr:
            filename = self.custom_comparison_models[start_ptr].split("/")
            if filename == model_name:
                self.selected_comparison_model = self.custom_comparison_models[start_ptr]
                return True
            start_ptr += 1

            filename = self.custom_comparison_models[end_ptr].split("/")
            if filename == model_name:
                self.selected_comparison_model = self.custom_comparison_models[end_ptr]
                return True
            end_ptr -= 1
        return False

    def select_translation_model(self, model_name: str) -> bool: 
        if model_name in self.hf_translation_models:
            self.selected_translation_model = model_name
            return True

        start_ptr = 0
        end_ptr = len(self.custom_translation_models) - 1

        while start_ptr <= end_ptr:
            filename = self.custom_translation_models[start_ptr].split("/")
            if filename == model_name:
                self.selected_translation_model = self.custom_translation_models[start_ptr]
                return True
            start_ptr += 1

            filename = self.custom_translation_models[end_ptr].split("/")
            if filename == model_name:
                self.selected_translation_model = self.custom_translation_models[end_ptr]
                return True
            end_ptr -= 1
        return False

    def delete_translation_model(self, model:str) -> bool:
        if model in self.hf_translation_models:
            # remove from json
            with open('saved_models.json', 'r') as f:
                data = json.load(f)
            data["huggingface"]['translation'].remove(model)
            with open('saved_models.json', 'w') as f:
                json.dump(data, f, indent=2)
            self.hf_translation_models.remove(model)
            return True

        start_ptr = 0
        end_ptr = len(self.custom_translation_models) - 1
        found = None

        while start_ptr <= end_ptr:
            filename = self.custom_translation_models[start_ptr].split("/")
            if filename == model:
                found = self.custom_translation_models[start_ptr]
                break
            start_ptr += 1

            filename = self.custom_translation_models[end_ptr].split("/")
            if filename == model:
                found = self.custom_translation_models[end_ptr]
                break
            end_ptr -= 1

        if not found:
            return False  
        
        with open('saved_models.json', 'r') as f:
            data = json.load(f)
        data["custom"]['translation'].remove(found)
        with open('saved_models.json', 'w') as f:
            json.dump(data, f, indent=2)
        self.custom_translation_models.remove(found)

        return True

    def delete_comparison_model(self, model:str) -> bool:
        if model in self.hf_comparison_models:
            # remove from json
            with open('saved_models.json', 'r') as f:
                data = json.load(f)
            data["huggingface"]['comparison'].remove(model)
            with open('saved_models.json', 'w') as f:
                json.dump(data, f, indent=2)
            self.hf_comparison_models.remove(model)
            return True

        start_ptr = 0
        end_ptr = len(self.custom_comparison_models) - 1
        found = None

        while start_ptr <= end_ptr:
            filename = self.custom_comparison_models[start_ptr].split("/")
            if filename == model:
                found = self.custom_comparison_models[start_ptr]
                break
            start_ptr += 1

            filename = self.custom_comparison_models[end_ptr].split("/")
            if filename == model:
                found = self.custom_comparison_models[end_ptr]
                break
            end_ptr -= 1

        if not found:
            return False  
        
        with open('saved_models.json', 'r') as f:
            data = json.load(f)
        data["custom"]['comparison'].remove(found)
        with open('saved_models.json', 'w') as f:
            json.dump(data, f, indent=2)
        self.custom_comparison_models.remove(found)

        return True

    def available_comparison_models_list(self) -> List[str]:
        return self.hf_comparison_models + self.custom_comparison_models

    def available_translation_model(self) -> List[str]:
        return self.hf_translation_models + self.custom_translation_models

    def extract_title_from_url(self, url: str) -> str:
        match = re.search(r'/wiki/([^#?]*)', url)
        if match:
            return match.group(1).replace('_', ' ')
        return None

