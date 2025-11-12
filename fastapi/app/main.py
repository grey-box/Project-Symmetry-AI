# import uvicorn
# import requests
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import router
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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()
# Add endpoints from other modules
app.include_router(router)

# Allow all origins (be cautious with this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server = ServerModel()

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


























