#!/bin/bash
import logging
from traceback import format_exc

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

from app.api import wiki_article
from app.api import comparison

from app.model.request import Url

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


# Exception Handlers
async def http_exception_handler(request: Request, exc: HTTPException):
    # Custom HTTPException handler to include stack trace in debug mode
    response_content = {"detail": exc.detail}
    if getattr(request.app, "debug", False):
        response_content["stack_trace"] = format_exc()
    return JSONResponse(response_content, status_code=exc.status_code)


async def generic_exception_handler(request: Request, exc: Exception):
    # Catch-all exception handler
    logging.error(f"Unhandled exception: {exc}")
    response_content = {"detail": "Internal Server Error"}
    if getattr(request.app, "debug", False):
        response_content["stack_trace"] = format_exc()
    return JSONResponse(response_content, status_code=500)


def register_exception_handlers():
    # Register custom exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


# Import the exception handlers
register_exception_handlers()

# Add endpoints from other modules
app.include_router(wiki_article.router)
app.include_router(comparison.router)

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


if __name__ == "__main__":
    # Defines API URL (host, port)
    uvicorn.run(app, host="127.0.0.1", port=8000)
