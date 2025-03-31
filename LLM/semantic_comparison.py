from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

'''
The altered code to build API for semantic comparison b/w langauges.
In this example, we are using 'sentence-transformers/LaBSE' model which is train on French and English.
Provides sentences which are missing in both the contents.
Use this to build API for semantic comparison under FastAPI.

'''
def semantic_compare(model_name, og_article, translated_article, sim_threshold):
    nlp = spacy.load("en_core_web_sm")
    # Load a multilingual sentence transformer model (LaBSE or cmlm)
    if model_name == "LaBSE":
        model = SentenceTransformer('sentence-transformers/LaBSE')
    else:
        model = SentenceTransformer('sentence-transformers/LaBSE')  # default

    og_article_sentences = preprocess_input(og_article, nlp)
    translated_article_sentences = preprocess_input(translated_article, nlp)

    # encode the sentences
    og_embeddings = model.encode(og_article_sentences)
    translated_embeddings = model.encode(translated_article_sentences)

    missing_info = semantic_diff(og_embeddings, translated_embeddings, sim_threshold)
    extra_info = semantic_diff(translated_embeddings, og_embeddings, sim_threshold)
    # Output the missing and extra information
    # print("Missing information from og text:", missing_info)
    # print("Extra information in translated text:", extra_info)
    return missing_info, extra_info


def preprocess_input(article, nlp):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(article)

    sentences = [sent.text for sent in doc.sents]
    return sentences

def semantic_diff(first_embeddings, second_embeddings, sim_threshold):
    diff_info = []
    for i, eng_embedding in enumerate(first_embeddings):
        # Calculate similarity between the current English sentence and all French sentences
        similarities = cosine_similarity([eng_embedding], second_embeddings)[0]

        # Find the best matching sentences
        max_sim = max(similarities)

        if max_sim < sim_threshold:  # Threshold for similarity
            diff_info.append(first_embeddings[i])  # This sentence might be missing or extra
    return diff_info
