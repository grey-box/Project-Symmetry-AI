from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

'''
The altered code to build API for semantic comparison b/w langauges.
In this example, we are using 'sentence-transformers/LaBSE' model which is train on French and English.
Provides sentences which are missing in both the contents.
Use this to build API for semantic comparison under FastAPI.

'''


def semantic_compare(model_name, og_article, translated_article, language, sim_threshold):  # main function
    # Load a multilingual sentence transformer model (LaBSE or cmlm)
    if model_name == "LaBSE":
        model = SentenceTransformer('sentence-transformers/LaBSE')
    else:
        model = SentenceTransformer('sentence-transformers/LaBSE')  # default

    og_article_sentences = preprocess_input(og_article, language[0])
    translated_article_sentences = preprocess_input(translated_article, language[1])

    # encode the sentences
    og_embeddings = model.encode(og_article_sentences)
    translated_embeddings = model.encode(translated_article_sentences)

    if sim_threshold is None:
        sim_threshold = 0.75

    missing_info = sentences_diff(og_article_sentences, og_embeddings, translated_embeddings, sim_threshold)
    extra_info = sentences_diff(translated_article_sentences, translated_embeddings, og_embeddings, sim_threshold)
    return missing_info, extra_info



def preprocess_input(article, language):
    # Define a mapping of languages to spaCy model names
    language_model_map = {
        "en": "en_core_web_sm",  # English
        "de": "de_core_news_sm",  # German
        "fr": "fr_core_news_sm",  # French
        "es": "es_core_news_sm",  # Spanish
        "it": "it_core_news_sm",  # Italian
        "pt": "pt_core_news_sm",  # Portuguese
        "nl": "nl_core_news_sm",  # Dutch
    }

    # Check if the language is supported
    if language not in language_model_map:
        nlp = spacy.load("xx_sent_ud_sm")# Multilingual (Universal Dependencies)

    # Load the appropriate spaCy model
    model_name = language_model_map[language]
    nlp = spacy.load(model_name)

    # Process the article and extract sentences
    doc = nlp(article)
    sentences = [sent.text for sent in doc.sents]

    return sentences

def sentences_diff(article_sentences, first_embeddings, second_embeddings, sim_threshold):
    diff_info = []
    for i, eng_embedding in enumerate(first_embeddings):
        # Calculate similarity between the current English sentence and all French sentences
        similarities = cosine_similarity([eng_embedding], second_embeddings)[0]

        # Find the best matching sentences
        max_sim = max(similarities)

        if max_sim < sim_threshold:  # Threshold for similarity
            diff_info.append(article_sentences[i])  # This sentence might be missing or extra
    return diff_info


def main():  # testing the fucntion
    model_name = "LaBSE"
    sim_thres = 0.65
    language = ["en", "fr"]
    english_article = "This is the first sentence. hi how are you. Hello World"  # Add all sentences here
    french_article = "Ceci est la première phrase. Je vais bien. Ceci est la deuxième phrase."  # Add all sentences here
    missing_info, extra_info = semantic_compare(model_name, english_article, french_article, language, sim_thres)

    # Output the missing and extra information
    print("Missing information from og text:", missing_info)
    print("Extra information in translated text:", extra_info)


if __name__ == "__main__":
    main()
