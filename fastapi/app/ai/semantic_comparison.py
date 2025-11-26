from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

def semantic_compare(
        original_blob,
        translated_blob,
        source_language,
        target_language,
        sim_threshold,
        model_name
    ):
    """
    Performs semantic comparison between two articles in 
    different languages.
    
    Expected parameters:
    {
        "original_article": "string - original article text",
        "translated_article": "string - translated article text",
        "source_language": "string - language code of original article",
        "target_language": "string - language code of translated article",
        "sim_threshold": "float - similarity threshold value"
    }
    
    Returns:
    {
        "source_sentences": [sentences from original article],
        "target_sentences": [sentences from translated article],
        "missing_info_index": [indices of missing content],
        "extra_info_index": [indices of extra content]
        "success": [true or false depending on if request was successful]
    }
    """
    success = True

    # Load a multilingual sentence transformer model (LaBSE or cmlm)
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        print(f"Could not load comparison model: {model_name},\n{e}")
        return {
            "original_sentences": [],
            "translated_sentences": [],
            "missing_info": [],
            "extra_info": [],
            "missing_info_indices": [],
            "extra_info_indices": [],
            "success": False
        }

    try: 
        original_sentences = preprocess_input(
            original_blob,
            source_language
        )
        translated_sentences = preprocess_input(
            translated_blob,
            target_language
        )
    except Exception as e:
        print("1.")
        print(e)
        return {
            "original_sentences": [],
            "translated_sentences": [],
            "missing_info": [],
            "extra_info": [],
            "missing_info_indices": [],
            "extra_info_indices": [],
            "success": False
        }

    try: 
        # encode the sentences
        original_embeddings = model.encode(original_sentences)
        translated_embeddings = model.encode(translated_sentences)

        if sim_threshold is None:
            sim_threshold = 0.75

        missing_info, missing_info_indices = sentences_diff(
            original_sentences,
            original_embeddings,
            translated_embeddings,
            sim_threshold
        )

        extra_info, extra_info_indices = sentences_diff(
            translated_sentences,
            translated_embeddings,
            original_embeddings,
            sim_threshold
        )
    except Exception as e:
        print("2.")
        print(e)
        return {
            "original_sentences": [],
            "translated_sentences": [],
            "missing_info": [],
            "extra_info": [],
            "missing_info_indices": [],
            "extra_info_indices": [],
            "success": False
        }

    return {
        "original_sentences": original_sentences,
        "translated_sentences": translated_sentences,
        "missing_info": missing_info,
        "extra_info": extra_info,
        "missing_info_indices": missing_info_indices,
        "extra_info_indices": extra_info_indices,
        "success": success
    }

def universal_sentences_split(text):
    """
    Splits text into sentences using universal splitting rules.
    
    Expected parameters:
    {
        "text": "string - text to be split into sentences"
    }
    
    Returns:
    {
        "sentences": [array of split sentences]
    }
    """
    sentences = []
    for sentence in text.replace('!', '.').replace('?', '.').split('.'):
        if sentence.strip():
            sentences.append(sentence.strip())
    return sentences

def preprocess_input(article, language):
    """
    Preprocesses input text based on language using appropriate 
    spaCy model.
    
    Expected parameters:
    {
        "article": "string - article text to preprocess",
        "language": "string - language code for the article"
    }
    
    Returns:
    {
        "sentences": [array of preprocessed sentences]
    }
    """

    # Define a mapping of languages to spaCy model names
    language_model_map = {
        "en": "en_core_web_sm",   # English
        "de": "de_core_news_sm",  # German
        "fr": "fr_core_news_sm",  # French
        "es": "es_core_news_sm",  # Spanish
        "it": "it_core_news_sm",  # Italian
        "pt": "pt_core_news_sm",  # Portuguese
        "nl": "nl_core_news_sm",  # Dutch
    }
    
    # Acommodate for TITLES
    # temporarily replace double newlines
    cleaned_article = article.replace(
        '\n\n', 
        '<DOUBLE_NEWLINE>'
    )

    cleaned_article = cleaned_article.replace('\n', '.')

    cleaned_article = cleaned_article.replace(
        '<DOUBLE_NEWLINE>', 
        ' '
    ).strip()

    try: 
        if language in language_model_map:
            # Load the appropriate spaCy model
            model_name = language_model_map[language]
            print(f"model_name is: {model_name}")
            nlp = spacy.load(model_name)

            # Process the article and extract sentences
            doc = nlp(cleaned_article)
            sentences = [sent.text for sent in doc.sents]
            return sentences
    except:
        # Fallback to universal sentence splitting
        sentences = universal_sentences_split(cleaned_article)  
        return sentences


def sentences_diff(
        article_sentences,
        first_embeddings,
        second_embeddings,
        sim_threshold
    ):
    """
    Compares sentence embeddings to find semantic differences.
    
    Expected parameters:
    {
        "article_sentences": [array of sentences],
        "first_embeddings": [array of sentence embeddings from 
                             first article],
        "second_embeddings": [array of sentence embeddings from second 
                              article],
        "sim_threshold": "float - similarity threshold value"
    }
    
    Returns:
    {
        "diff_info": [array of differing sentences],
        "indices": [array of indices where differences occur]
    }
    """
    diff_info = []
    indices = []  # track the indices of differing sentences
    for i, eng_embedding in enumerate(first_embeddings):
        similarities = cosine_similarity(
            [eng_embedding], second_embeddings)[0]

        # find the best matching sentences
        max_sim = max(similarities)

        if max_sim < sim_threshold:
            # this sentence might be missing or extra
            diff_info.append(article_sentences[i])
            indices.append(i)
            
    return diff_info, indices

# def main():
#     print("pre begin")
#     # Example test request data
#     test_request = {
#         "article_text_blob_1": "This is the first sentence.\n\nThis is the second sentence\nThis is the third sentence.",
#         "article_text_blob_2": "\n\nCeci est la première phrase\nJe vais bien. Ceci est la deuxième phrase.",
#         "article_text_blob_1_language": "en",
#         "article_text_blob_2_language": "fr",
#         "comparison_threshold": 0.65,
#         "model_name": "sentence-transformers/LaBSE"
#     }
    
#     print("begin")
#     result = perform_semantic_comparison(test_request)
#     print("Comparison Results:", result)


# if __name__ == "__main__":
#     print("pre pre begin")
#     main()
