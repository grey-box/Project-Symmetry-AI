import uvicorn
import requests
import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models.api_models import ComparisonResponse, ListResponse, ModelSelectionResponse, TranslationResponse, ArticleResponse
from .models.server_model import ServerModel


'''
This is the API which handles backend. It handles following features
1. Providing source article (with input as URL or Title)
2. Providing available translation languages list
3. Providing translated content
4. Providing comparisons between articles

Note: You can run this API using 'python main.py' and use postman to get response while debugging
      OR you can simply run "fastapi dev main.py" in the same directory as this file

'''

app = FastAPI()

# Allow all origins (be cautious with this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server = ServerModel()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.get("/get_article", response_model=ArticleResponse)
def get_article(url: str = Query(None), title: str = Query(None)):
    logging.info("Calling get article endpoint")

    if url:
        title = server.extract_title_from_url(url)
        if not title:
            logging.info("Invalid Wikipedia URL provided.")
            raise HTTPException(status_code=400, detail="Invalid Wikipedia URL provided.")

    if not title:
        logging.info("Either 'url' or 'title' must be provided.")
        raise HTTPException(status_code=400, detail="Either 'url' or 'title' must be provided.")

    page = server.wikipedia.page(title)

    if not page.exists():
        logging.info("Article not found.")
        raise HTTPException(status_code=404, detail="Article not found.")

    article_content = page.text  # Get the article text

    # Fetch available languages
    languages = list(page.langlinks.keys())

    return {"source_article": article_content, "article_languages": languages}

@app.get("/translate", response_model=TranslationResponse)
def translate_article(
        source_language: str = Query(...),
        target_language: str = Query(...),
        text: str = Query(...)
    ):
    pass

@app.get("/comparison/semantic_comparison", response_model=ComparisonResponse)
def compare_articles(
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        similarity_threshold: float = 0.75
    ):
    logging.info("Calling semantic comparison endpoint.")

    if similarity_threshold < 0 or similarity_threshold > 1:
        err_msg = "Provided similarity threshold is out of the defined valid range [0,1]"
        logging.info(err_msg)
        raise HTTPException(
            status_code=400, 
            detail=err_msg
        )

    if original_text.isnumeric() or translated_text.isnumeric():
        err_msg = "Either text_a or text_b was not the correct input type."
        logging.info(err_msg)
        raise HTTPException(
            status_code=400, 
            detail=err_msg
        )

    output = server.perform_semantic_comparison(
        original_text,
        translated_text,
        source_language,
        target_language, 
        similarity_threshold
    )

    return output

@app.get("/models/translation/select", response_model=ModelSelectionResponse)
def select_translation_model(modelname: str):
    return {"successful": str(server.select_translation_model(modelname))}

@app.get("/models/translation/delete", response_model=ModelSelectionResponse)
def delete_translation_model(modelname: str):
    return {"successful": str(server.delete_translation_model(modelname))}

@app.get("/models/translation/import", response_model=ModelSelectionResponse)
def import_translation_model(model: str, from_huggingface: bool):
    return {"successful": str(server.import_new_translation_model(model, from_huggingface))}

@app.get("/models/comparison/select", response_model=ModelSelectionResponse)
def select_comparison_model(modelname: str):
    return {"successful": str(server.select_comparison_model(modelname))}

@app.get("/models/comparison/delete", response_model=ModelSelectionResponse)
def delete_comparison_model(modelname: str):
    return {"successful": str(server.delete_comparison_model(modelname))}

@app.get("/models/comparison/import", response_model=ModelSelectionResponse)
def import_comparison_model(model: str, from_huggingface: bool):
    return {"successful": str(server.import_new_comparison_model(model, from_huggingface))}

#check
@app.get("/models/translation", response_model=ListResponse)
def list_translation_models():
    return {"response": server.available_translation_models_list()}

#check
@app.get("/models/comparison", response_model=ListResponse)
def list_comparison_models():
    return {"response": server.available_comparison_models_list()}
#check
@app.get("/models/comparison/selected", response_model=ListResponse)
def get_selected_comparison_model():
    return {"response": [server.selected_comparison_model]}

#check
@app.get("/models/translation/selected", response_model=ListResponse)
def get_selected_translation_model():
    return {"response": [server.selected_translation_model]}



if __name__ == '__main__':
    # Defines API URL (host, port)
    uvicorn.run(app, host='127.0.0.1', port=8000)
























# Function to get the URL of Wikipedia page from title as input
# def get_wikipedia_url(title: str) -> str:
#     """Get the Wikipedia article URL for a given title using 
#        the Wikipedia API."""
#     api_url = 'https://en.wikipedia.org/w/api.php'
#     params = {
#         'action': 'query',
#         'format': 'json',
#         'titles': title,
#         'prop': 'info',
#         'inprop': 'url',
#     }
#     response = requests.get(api_url, params=params)
#     data = response.json()
#     pages = data.get('query', {}).get('pages', {})
#     page = next(iter(pages.values()), None)

#     if not page or 'missing' in page:
#         logging.error('Wikipedia article not found.')
#         raise HTTPException(
#             status_code=404, 
#             detail="Wikipedia article not found."
#         )

#     fullurl = page.get('fullurl')
#     if not fullurl:
#         logging.error('Wikipedia article URL not found.')
#         raise HTTPException(
#             status_code=404, 
#             detail="Wikipedia article URL not found."
#         )

#     return fullurl


























