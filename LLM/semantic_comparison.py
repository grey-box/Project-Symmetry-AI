from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

'''
The base code to build API for semantic comparison b/w langauges.
In this example, we are using 'sentence-transformers/LaBSE' model which is train on French and English.
Provides sentences which are missing in both the contents.
Use this to build API for semantic comparison under FastAPI.

'''

# Load a multilingual sentence transformer model (LaBSE or XLM-R)
model = SentenceTransformer('sentence-transformers/LaBSE')

# Step 1: Split the English and French texts into sentences
english_sentences = ["This is the first sentence.", "This is the second sentence.", "Hello World"]  # Add all sentences here
french_sentences = ["Ceci est la première phrase.", "Je vais bien.", "Ceci est la deuxième phrase."]  # Add all sentences here

# Step 2: Encode all sentences using the multilingual model
english_embeddings = model.encode(english_sentences)
french_embeddings = model.encode(french_sentences)

# Step 3: Compare sentences using cosine similarity
missing_info = []
extra_info = []

for i, eng_embedding in enumerate(english_embeddings):
    # Calculate similarity between the current English sentence and all French sentences
    similarities = cosine_similarity([eng_embedding], french_embeddings)[0]
    
    # Find the best matching French sentence
    max_sim = max(similarities)
    
    if max_sim < 0.75:  # Threshold for missing information
        missing_info.append(english_sentences[i])  # This sentence might be missing in the French text

# Step 4: Check for extra information in the French text
for i, fr_embedding in enumerate(french_embeddings):
    similarities = cosine_similarity([fr_embedding], english_embeddings)[0]
    
    # Find the best matching English sentence
    max_sim = max(similarities)
    
    if max_sim < 0.75:  # Threshold for extra information
        extra_info.append(french_sentences[i])  # This sentence might be extra in the French translation

# Output the missing and extra information
print("Missing information from English text:", missing_info)
print("Extra information in French text:", extra_info)
