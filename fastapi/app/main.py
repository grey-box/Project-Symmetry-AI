#!/bin/bash
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

from app.api import wiki_article
from app.model.request import Url
from fastapi import FastAPI

"""
This is the API which handles backend. It handles following features
1. Providing source article (with input as URL or Title)
2. Providing available translation languages list
3. Providing translated content

Note: You can run this API using 'python main.py' and use postman to get response while debugging

"""

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

""" 
Initialize FastAPI app (if debug=True, it will show detailed error messages with stack traces)
                       (if debug=False, it will show generic error messages)   
"""

app = FastAPI(debug=True)

# Import the exception handlers and pass the app instance
wiki_article.register_exception_handlers(app)

# Add endpoints from other modules
app.include_router(wiki_article.router)

# May not be necessary unless multiple domains are used
# Resource sharing middleware (allows cross-domain relationships)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8000",
                   "http://localhost:8000"],  # Specify domains that will need to communicate (i.e. if front-end is hosted separately from back-end)
    allow_credentials=True,
    allow_methods=["GET","HEAD"],
    allow_headers=["*"],
)


@app.post("/api/v1/article/original/")
def get_orginal_article_by_url(url: Url):
    return "hello"


if __name__ == "__main__":
    # Defines API URL (host, port)
    uvicorn.run(app, host="127.0.0.1", port=8000)
