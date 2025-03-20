from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

'''
The base code to build API for semantic comparison b/w langauges.
In this example, we are using 'sentence-transformers/LaBSE' model which is train on French and English.
Provides sentences which are missing in both the contents.
Use this to build API for semantic comparison under FastAPI.

'''

comparison_models = [
    "sentence-transformers/LaBSE",
    "xlm-roberta-base",
    "multi-qa-distilbert-cos-v1",
    "multi-qa-MiniLM-L6-cos-v1",
    "multi-qa-mpnet-base-cos-v1"
]

def split_into_sentences(text):
    sentences = []
    for sentence in text.replace('!', '.').replace('?', '.').split('.'):
        if sentence.strip():
            sentences.append(sentence.strip())
    return sentences

def perform_semantic_comparison(text_a, text_b, similarity_threshold, model_name):
    model = SentenceTransformer(model_name)
    
    # Step 1: Split the texts into sentences
    a_sentences = split_into_sentences(text_a)
    b_sentences = split_into_sentences(text_b)
    
    # Step 2: Encode all sentences using the multilingual model
    a_embeddings = model.encode(a_sentences)
    b_embeddings = model.encode(b_sentences)
    
    # Step 3: Compare sentences using cosine similarity
    missing_info = []
    extra_info = []
    
    for i, a_embedding in enumerate(a_embeddings):
        # Calculate similarity between the current a_sentence and all b_sentences
        similarities = cosine_similarity([a_embedding], b_embeddings)[0]
        
        # Find the best matching b_sentence
        max_sim = max(similarities)
        
        if max_sim < similarity_threshold:  # Threshold for missing information
            missing_info.append(a_sentences[i])  # This sentence might be missing in text b
    
    # Step 4: Check for extra information in text b
    for i, b_embedding in enumerate(b_embeddings):
        similarities = cosine_similarity([b_embedding], a_embeddings)[0]
        
        # Find the best matching a_sentence
        max_sim = max(similarities)
        
        if max_sim < similarity_threshold:  # Threshold for extra information
            extra_info.append(b_sentences[i])  # This sentence might be extra in text b

    return missing_info, extra_info
