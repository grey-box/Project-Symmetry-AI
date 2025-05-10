#!/bin/bash
import argparse
import logging
from traceback import format_exc

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

from app.api import wiki_article
from app.api import comparison

"""
This is the API which handles backend. It handles following features
1. Providing source article (with input as URL or Title)
2. Providing available translation languages list
3. Providing translated content

Note: You can run this API by cd'ing into 'fastapi' and running 'uvicorn app.main:app --reload' in terminal. Use postman to get response while debugging.

Here is a sample request to request an article using a URL:

GET http://127.0.0.1:8000/symmetry/v1/wiki/articles?query=https://en.wikipedia.org/wiki/covid

The response will be a JSON object with the source article and the languages available for translation.
Further documentation on how these requests are concatenated can be found in the wiki_article.py file.
"""

# This is how FastAPI recommends setting up debug logging
# to avoid accidentally leaving it enabled in production.
# https://www.starlette.io/config/
config = Config(".env")

LOG_LEVEL = config.get("LOG_LEVEL", default="INFO")
FASTAPI_DEBUG = config.get("FASTAPI_DEBUG", cast=bool, default=False)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Initialize FastAPI app. The 'debug' flag controls the level of error reporting.
# When 'debug' is True, detailed error messages including stack traces will be shown, which is helpful during development.
# When 'debug' is False, more generic error messages are returned to the client, suitable for production environments.
app = FastAPI(debug=FASTAPI_DEBUG)


# Custom exception handlers


# This handler is used to catch specifically HTTP exceptions and return a JSON response with the error details.
async def http_exception_handler(request: Request, exc: HTTPException):
    # Custom HTTPException handler to include stack trace in debug mode
    response_content = {"detail": exc.detail}
    if getattr(request.app, "debug", False):
        response_content["stack_trace"] = format_exc()
    return JSONResponse(response_content, status_code=exc.status_code)


# This handler is used to catch all other exceptions that are not HTTP exceptions.
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

# Add endpoints from other modules.
# Note that when adding more endpoints, they should follow a similar format!
# The current format is /symmetry/v1/<path>/<to>/<resource>
# A quick read on RESTful resource naming: https://restfulapi.net/resource-naming/
# For a more dense and in-depth view of the RESTful philosophy, the above article
# links Roy Fielding's dissertation:
# https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_2_1_1
app.include_router(wiki_article.router)
app.include_router(comparison.router)

# Resource sharing middleware (allows cross-domain relationships)
# May not be necessary unless multiple domains are used (e.g. front-end and back-end are hosted separately, which is not the case currently)
# CORS does not really have any security risks in this implementation, but it is good practice to limit the domains that can access the API
app.add_middleware(
    CORSMiddleware,
    # Specify domains that will need to communicate via API
    allow_origins=["https://localhost:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "HEAD"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    # Configure our port number.
    parser = argparse.ArgumentParser(
        prog="Project Symmetry",
        description="A semantic comparison tool")  # Simple command line description
    parser.add_argument("-p", "--port")
    args = vars(parser.parse_args())
    # If we don't get a port number, default to 8000
    if args["port"] is not None and args["port"].isnumeric():
        port = int(args["port"]) # If you don't cast this, the logger will freak out
    else:
        port = 8000
    # Defines API URL (host, port)
    uvicorn.run(app, host="127.0.0.1", port=port)
