# Wikipedia Translation API Documentation

This API allows you to retrieve Wikipedia articles, translate them to different languages, and compare content between different language versions semantically.

## Table of Contents

- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Get Article](#get-article)
  - [Translate Article](#translate-article)
  - [Semantic Comparison](#semantic-comparison)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Base URL

```
http://127.0.0.1:8000
```

## Endpoints

### 1. Get Article

Retrieves a Wikipedia article and lists available translation languages.

```
GET /get_article
```

#### Query Parameters

| Parameter | Type   | Required | Description                       |
|-----------|--------|----------|-----------------------------------|
| url       | string | No*      | URL of the Wikipedia article      |
| title     | string | No*      | Title of the Wikipedia article    |

\* Either `url` or `title` must be provided.

#### Response

```json
{
  "sourceArticle": "Full text content of the article",
  "articleLanguages": ["fr", "es", "de", "zh", ...]
}
```

#### Example Request

```
GET /get_article?title=Albert%20Einstein
```

or

```
GET /get_article?url=https://en.wikipedia.org/wiki/Albert_Einstein
```

#### Error Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 400         | Invalid Wikipedia URL provided          |
| 400         | Either 'url' or 'title' must be provided|
| 404         | Article not found                       |

### 2. Translate Article

Retrieves a translated version of a Wikipedia article.

```
GET /wiki_translate/source_article
```

#### Query Parameters

| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| url       | string | No*      | URL of the Wikipedia article         |
| title     | string | No*      | Title of the Wikipedia article       |
| language  | string | Yes      | Language code for the translation    |

\* Either `url` or `title` must be provided.

#### Response

```json
{
  "translated_article": "Full text content of the translated article"
}
```


#### Example Request

```
GET /wiki_translate/source_article?title=Albert%20Einstein&language=fr
```

#### Error Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 400         | Invalid Wikipedia URL provided          |
| 400         | Either 'url' or 'title' must be provided|
| 404         | Translated article not found            |

### 3. Semantic Comparison

Compares two text chunks and identifies missing and extra information.

```
GET /comparison/semantic_comparison
```

#### Query Parameters

| Parameter          | Type   | Required | Description                                        |
|--------------------|--------|----------|----------------------------------------------------|
| text_a             | string | Yes      | First text to compare                              |
| text_b             | string | Yes      | Second text to compare                             |
| similarity_threshold | float | No      | Threshold for similarity (default: 0.75)           |
| model_name         | string | No      | Model to use for comparison (default: "sentence-transformers/LaBSE") |

#### Available Models

- "sentence-transformers/LaBSE"
- "xlm-roberta-base"
- "multi-qa-distilbert-cos-v1"
- "multi-qa-MiniLM-L6-cos-v1"
- "multi-qa-mpnet-base-cos-v1"

#### Response

```json
{
  "missing_info": ["List of text chunks missing from text_b compared to text_a"],
  "extra_info": ["List of text chunks present in text_b but not in text_a"]
}
```
{
    changed_info: "<The>content is extra<added/>
}

#### Example Request

```
GET /comparison/semantic_comparison?text_a=The%20sky%20is%20blue&text_b=The%20sky%20is%20azure&similarity_threshold=0.8
```

#### Error Responses

| Status Code | Description                                                  |
|-------------|--------------------------------------------------------------|
| 400         | Similarity threshold out of valid range [0,1]                |
| 400         | Invalid input: text_a or text_b was found to be None         |
| 404         | Invalid model selected                                       |

## Data Models

### SourceArticleResponse

```json
{
  "sourceArticle": "string",
  "articleLanguages": ["string"]
}
```

### TranslateArticleResponse

```json
{
  "translated_article": "string"
}
```

### ArticleComparisonResponse

```json
{
  "missing_info": ["string"],
  "extra_info": ["string"]
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages in the following format:

```json
{
  "detail": "Error message description"
}
```

