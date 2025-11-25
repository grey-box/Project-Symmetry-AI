# **Wikipedia Translation & Comparison API Documentation**

This API provides services to fetch Wikipedia articles, translate them, semantically compare texts, and manage the underlying Machine Learning models used for these tasks.

## **Getting Started**

### **Prerequisites**

Ensure you have the necessary dependencies installed:

pip install fastapi uvicorn requests nltk Wikipedia-API

### **Running the Server**

Since the code provided is an APIRouter module (endpoints.py), it must be mounted to a main FastAPI application instance.

1. **Run the main.py file**: python main.py  
2. **Access the API:**  
   * **Base URL:** http://127.0.0.1:8000

   

## **Endpoints**

### **1\. Article Retrieval**

Fetch the content and available languages of a Wikipedia article.

* **Endpoint:** /get\_article  
* **Method:** GET

#### **Parameters**

| Parameter | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| url | string | No\* | The full URL of the Wikipedia page. |
| title | string | No\* | The title of the Wikipedia page. |

*\*Note: Either url or title must be provided.*

#### **Responses**

* **200 OK:** Returns article content and language links.  
  {  
    "source\_article": "Article text content here...",  
    "article\_languages": \["es", "fr", "de", "ja"\]  
  }

* **400 Bad Request:** If neither title nor URL is provided, or URL is invalid.  
* **404 Not Found:** If the Wikipedia article does not exist.

### **2\. Translation**

Translate a given text segment from a source language to a target language.

* **Endpoint:** /translate  
* **Method:** GET

#### **Parameters**

| Parameter | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| source\_language | string | Yes | Language code of input text (e.g., "en"). |
| target\_language | string | Yes | Language code for output (e.g., "es"). |
| text | string | Yes | The text to translate. |

#### **Responses**

* **200 OK:** Returns the translated text.

### **3\. Semantic Comparison**

Compare the semantic similarity between an original text and a translated text.

* **Endpoint:** /comparison/semantic\_comparison  
* **Method:** GET

#### **Parameters**

| Parameter | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| original\_text | string | Yes | The source text. |
| translated\_text | string | Yes | The text to compare against the source. |
| source\_language | string | Yes | Language of the original text. |
| target\_language | string | Yes | Language of the translated text. |
| similarity\_threshold | float | No | Threshold for similarity (Default: 0.75). Must be between 0 and 1\. |

#### **Constraints**

* similarity\_threshold must be between 0 and 1\.  
* Input texts cannot be purely numeric strings.

#### **Responses**

* **200 OK:** Returns comparison metrics.  
* **400 Bad Request:** If the threshold is invalid or input texts are purely numeric.

### **4\. Model Management**

These endpoints allow you to load, delete, and import specific ML models for translation and comparison tasks.

#### **Translation Models**

| Action | Endpoint | Method | Parameters | Description |
| :---- | :---- | :---- | :---- | :---- |
| **Select** | /models/translation/select | GET | modelname (str) | Activates a specific translation model. |
| **Delete** | /models/translation/delete | GET | modelname (str) | Deletes a loaded translation model. |
| **Import** | /models/translation/import | GET | model (str), from\_huggingface (bool) | Downloads/Imports a new model. |

#### **Comparison Models**

| Action | Endpoint | Method | Parameters | Description |
| :---- | :---- | :---- | :---- | :---- |
| **Select** | /models/comparison/select | GET | modelname (str) | Activates a specific comparison model. |
| **Delete** | /models/comparison/delete | GET | modelname (str) | Deletes a loaded comparison model. |
| **Import** | /models/comparison/import | GET | model (str), from\_huggingface (bool) | Downloads/Imports a new model. |

