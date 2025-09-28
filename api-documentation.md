# 📡 Project Symmetry API Documentation

This API allows you to retrieve Wikipedia articles, translate them to different languages, and compare content between different language versions semantically.

## 📚 Table of Contents

- [🔗 Base URL](#-base-url)
- [🚀 Endpoints](#-endpoints)
  - [📖 Get Article](#-get-article)
  - [🌍 Translate Article](#-translate-article)
  - [🔍 Semantic Comparison](#-semantic-comparison)
- [📋 Data Models](#-data-models)
- [⚠️ Error Handling](#-error-handling)
- [🔧 Authentication](#-authentication)
- [📊 Rate Limiting](#-rate-limiting)

## 🔗 Base URL

```
http://127.0.0.1:8000
```

**Note**: For production use, replace with your deployed server URL.

## 🚀 Endpoints

### 📖 Get Article

Retrieves a Wikipedia article and lists available translation languages.

```
GET /get_article
```

#### 📋 Query Parameters

| Parameter | Type   | Required | Description                       | Example |
|-----------|--------|----------|-----------------------------------|---------|
| `url`     | string | No*      | URL of the Wikipedia article      | `https://en.wikipedia.org/wiki/Albert_Einstein` |
| `title`   | string | No*      | Title of the Wikipedia article    | `Albert Einstein` |

\* Either `url` or `title` must be provided.

#### ✅ Success Response (200)

```json
{
  "sourceArticle": "Full text content of the article",
  "articleLanguages": ["fr", "es", "de", "zh", "ja", "ru", ...]
}
```

#### 🚫 Error Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 400         | Invalid Wikipedia URL provided          |
| 400         | Either 'url' or 'title' must be provided|
| 404         | Article not found                       |
| 500         | Server error processing request         |

#### 💡 Example Requests

```bash
# By title
curl -X GET "http://127.0.0.1:8000/get_article?title=Albert%20Einstein"

# By URL
curl -X GET "http://127.0.0.1:8000/get_article?url=https://en.wikipedia.org/wiki/Albert_Einstein"
```

### 🌍 Translate Article

Retrieves a translated version of a Wikipedia article.

```
GET /wiki_translate/source_article
```

#### 📋 Query Parameters

| Parameter | Type   | Required | Description                          | Example |
|-----------|--------|----------|--------------------------------------|---------|
| `url`     | string | No*      | URL of the Wikipedia article         | `https://en.wikipedia.org/wiki/Albert_Einstein` |
| `title`   | string | No*      | Title of the Wikipedia article       | `Albert Einstein` |
| `language`| string | Yes      | Language code for the translation    | `fr` |

\* Either `url` or `title` must be provided.

#### ✅ Success Response (200)

```json
{
  "translated_article": "Contenu complet de l'article traduit"
}
```

#### 🚫 Error Responses

| Status Code | Description                             |
|-------------|-----------------------------------------|
| 400         | Invalid Wikipedia URL provided          |
| 400         | Either 'url' or 'title' must be provided|
| 400         | Invalid language code provided          |
| 404         | Translated article not found            |
| 500         | Server error during translation        |

#### 💡 Example Requests

```bash
# By title with language
curl -X GET "http://127.0.0.1:8000/wiki_translate/source_article?title=Albert%20Einstein&language=fr"

# By URL with language
curl -X GET "http://127.0.0.1:8000/wiki_translate/source_article?url=https://en.wikipedia.org/wiki/Albert_Einstein&language=es"
```

### 🔍 Semantic Comparison

Compares two text chunks and identifies missing and extra information using advanced NLP models.

```
GET /comparison/semantic_comparison
```

#### 📋 Query Parameters

| Parameter             | Type   | Required | Description                                        | Default    |
|-----------------------|--------|----------|----------------------------------------------------|------------|
| `text_a`              | string | Yes      | First text to compare                              | -          |
| `text_b`              | string | Yes      | Second text to compare                             | -          |
| `similarity_threshold`| float  | No       | Threshold for similarity (0.0 to 1.0)             | `0.75`     |
| `model_name`          | string | No       | Model to use for comparison                        | `"sentence-transformers/LaBSE"` |

#### 🤖 Available Models

| Model Name | Description | Languages | Best For |
|------------|-------------|-----------|----------|
| `sentence-transformers/LaBSE` | Multilingual sentence embedding | 100+ | General semantic comparison |
| `xlm-roberta-base` | Cross-lingual model | 100+ | Fast comparison |
| `multi-qa-distilbert-cos-v1` | QA-optimized model | English | Question-answering tasks |
| `multi-qa-MiniLM-L6-cos-v1` | Lightweight QA model | English | Fast QA tasks |
| `multi-qa-mpnet-base-cos-v1` | High-quality QA model | English | High-accuracy QA |

#### ✅ Success Response (200)

```json
{
  "missing_info": [
    "Important historical context about Einstein's early life",
    "Details about his Nobel Prize achievements"
  ],
  "extra_info": [
    "Additional commentary on modern physics applications",
    "Recent developments in quantum theory"
  ],
  "similarity_score": 0.82,
  "model_used": "sentence-transformers/LaBSE"
}
```

#### 🚫 Error Responses

| Status Code | Description                                                  |
|-------------|--------------------------------------------------------------|
| 400         | Similarity threshold out of valid range [0,1]                |
| 400         | Invalid input: text_a or text_b was found to be None         |
| 400         | Text too long for processing (max: 5000 characters)          |
| 404         | Invalid model selected                                       |
| 500         | Server error during comparison                               |

#### 💡 Example Requests

```bash
# Basic comparison
curl -X GET "http://127.0.0.1:8000/comparison/semantic_comparison?text_a=The%20sky%20is%20blue&text_b=The%20sky%20is%20azure&similarity_threshold=0.8"

# With custom model
curl -X GET "http://127.0.0.1:8000/comparison/semantic_comparison?text_a=Hello%20world&text_b=Hi%20universe&model_name=xlm-roberta-base"
```

## 📋 Data Models

### SourceArticleResponse

```json
{
  "sourceArticle": "Full text content of the Wikipedia article",
  "articleLanguages": ["fr", "es", "de", "zh", "ja", "ru", "ar", "pt", ...]
}
```

**Fields:**
- `sourceArticle` (string): Complete text content of the requested article
- `articleLanguages` (array): List of available language codes for translations

### TranslateArticleResponse

```json
{
  "translated_article": "Contenu complet de l'article traduit dans la langue demandée"
}
```

**Fields:**
- `translated_article` (string): Complete translated text content

### ArticleComparisonResponse

```json
{
  "missing_info": ["Text chunks missing from text_b compared to text_a"],
  "extra_info": ["Text chunks present in text_b but not in text_a"],
  "similarity_score": 0.85,
  "model_used": "sentence-transformers/LaBSE"
}
```

**Fields:**
- `missing_info` (array): Text chunks present in text_a but missing from text_b
- `extra_info` (array): Text chunks present in text_b but not in text_a
- `similarity_score` (float): Overall similarity score between 0.0 and 1.0
- `model_used` (string): Name of the model used for comparison

## ⚠️ Error Handling

All endpoints return appropriate HTTP status codes and error messages in the following format:

```json
{
  "detail": "Human-readable error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server-side error |

## 🔧 Authentication

Currently, the API does not require authentication. For production deployment, consider implementing:

- **API Key Authentication**: Add `X-API-Key` header
- **JWT Tokens**: For user-specific endpoints
- **OAuth 2.0**: For third-party integrations

## 📊 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Requests per minute**: 60 requests per minute per IP
- **Requests per hour**: 1000 requests per hour per IP
- **Concurrent connections**: 10 concurrent connections per IP

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## 🚀 Quick Start Examples

### 1. Get an Article and Available Languages

```bash
# Get article by title
curl -X GET "http://127.0.0.1:8000/get_article?title=Machine%20Learning"

# Response will include article content and available languages
```

### 2. Translate an Article

```bash
# Translate to French
curl -X GET "http://127.0.0.1:8000/wiki_translate/source_article?title=Machine%20Learning&language=fr"
```

### 3. Compare Two Texts

```bash
# Compare English and French versions
curl -X GET "http://127.0.0.1:8000/comparison/semantic_comparison?text_a=Machine%20learning%20is%20a%20subset%20of%20AI&text_b=Le%20machine%20learning%20est%20un%20sous-ensemble%20de%20l%27IA"
```

## 🔗 Frontend Integration

### API Service Architecture

The frontend is structured with dedicated service modules for different API functionalities:

#### Fetch Article Service
**File**: [`ui/src/services/fetchArticle.ts`](../ui/src/services/fetchArticle.ts)

This service handles:
- Fetching Wikipedia articles by title or URL
- Getting available translation languages for an article
- Communicating with the `get_article` endpoint

**Key Functions**:
- `fetchArticleByTitle(title: string)` - Fetch article by title
- `fetchArticleByUrl(url: string)` - Fetch article by URL
- `getAvailableLanguages(title: string)` - Get available translation languages

#### Translate Article Service
**File**: [`ui/src/services/translateArticle.ts`](../ui/src/services/translateArticle.ts)

This service handles:
- Translating articles to specified languages
- Communicating with the `translate/targetArticle` endpoint

**Key Functions**:
- `translateArticle(title: string, language: string)` - Translate article to specified language
- `translateArticleByUrl(url: string, language: string)` - Translate article by URL

#### Compare Articles Service
**File**: [`ui/src/services/compareArticles.ts`](../ui/src/services/compareArticles.ts)

This service handles:
- Semantic comparison of texts
- Communicating with the `comparison/semantic_comparison` endpoint

**Key Functions**:
- `compareArticles(textA: string, textB: string)` - Compare two texts semantically
- `compareWithThreshold(textA: string, textB: string, threshold: number)` - Compare with similarity threshold

### Component Integration

#### TranslationSection Component
**File**: [`ui/src/components/TranslationSection.tsx`](../ui/src/components/TranslationSection.tsx)

This component handles:
- Rendering source article content
- Managing language selection dropdown
- Displaying translated articles
- User interface for translation workflow

#### ComparisonSection Component
**File**: [`ui/src/components/ComparisonSection.tsx`](../ui/src/components/ComparisonSection.tsx)

This component handles:
- Displaying comparison results
- Color-coding missed and added information
- Semantic comparison visualization

### Configuration

#### API Constants
**File**: [`ui/src/constants/AppConstants.ts`](../ui/src/constants/AppConstants.ts)

This file defines:
- Base API URL and port configuration
- Timeout settings
- API endpoint paths
- Request/response configurations

#### Data Models
**TypeScript Interfaces** (located in [`ui/src/models/`](../ui/src/models/)):

- `FetchArticleRequest` - Request structure for fetching articles
- `FetchArticleResponse` - Response structure for article data
- `TranslateArticleRequest` - Request structure for translation
- `TranslateArticleResponse` - Response structure for translation
- `ArticleComparisonRequest` - Request structure for comparison
- `ArticleComparisonResponse` - Response structure for comparison results

### Error Handling

The frontend implements comprehensive error handling:
- Network error handling with retry mechanisms
- API error response parsing and display
- Loading states during API calls
- User-friendly error messages

### Development Workflow

1. **Backend Development**: Start FastAPI server with `python -m app.main`
2. **Frontend Development**: Start Electron app with `npm run start`
3. **API Testing**: Use the provided curl examples or API documentation
4. **Component Testing**: Test individual components with mock data
5. **Integration Testing**: Test full workflow from article fetching to comparison

### Best Practices

- **Type Safety**: Use TypeScript interfaces for all API communications
- **Error Boundaries**: Implement React error boundaries for graceful error handling
- **Loading States**: Show appropriate loading indicators during API calls
- **Caching**: Implement client-side caching for frequently accessed data
- **Responsive Design**: Ensure UI works across different screen sizes

## 📝 API Testing

You can test the API interactively using the auto-generated documentation:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

These provide a user-friendly interface to test all endpoints without writing code.

---

**API Version**: 1.0.0  
**Last Updated**: November 2024  
**Base URL**: `http://127.0.0.1:8000`
