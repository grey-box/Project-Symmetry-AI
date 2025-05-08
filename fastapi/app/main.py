#!/bin/bash
import argparse
from fastapi import FastAPI
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

from app.api import wiki_article
from app.model.request import Url

'''
This is the API which handles backend. It handles following features
1. Providing source article (with input as URL or Title)
2. Providing available translation languages list
3. Providing translated content

Note: You can run this API using 'python main.py' and use postman to get response while debugging

'''

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()
# Add endpoints from other modules
app.include_router(wiki_article.router)

# Allow all origins (be cautious with this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/article/original/")
def get_orginal_article_by_url(url: Url):
    return 'hello'

if __name__ == '__main__':
    # Configure our port number.
    parser = argparse.ArgumentParser(
        prog='Project Symmetry',
        description='A semantic comparison tool')  # Simple command line description
    parser.add_argument('-p', '--port')
    args = vars(parser.parse_args())
    # If we don't get a port number, default to 8000
    if args["port"] is not None and args["port"].isnumeric():
        port = int(args["port"]) # If you don't cast this, the logger will freak out
    else:
        port = 8000

    # Defines API URL (host, port)
    uvicorn.run(app, host='127.0.0.1', port=port)