import json
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

# Initialize NLTK tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Load the same embedding model used for products
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")  # ✅ Ensure consistency

# Load product embeddings
with open("embeddings_of_products.json", "r", encoding="utf-8") as f:
    product_embeddings = json.load(f)

# Extract embeddings and product info
product_vectors = np.array([p["embeddings"] for p in product_embeddings])
product_info = [
    {
        "product_id": p["product_id"],  # ✅ Keep product_id for tracking
        "url": p["url"],
        "title": p["title"],
        "variant": p.get("variant", "N/A")
    }
    for p in product_embeddings
]

def tokenize(text):
    """Tokenize, remove stopwords, and lemmatize."""
    text = text.lower()
    words = word_tokenize(text)
    words = [w for w in words if w.isalnum()]
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return words

def get_synonyms(word):
    """Retrieve up to 3 synonyms for a given word."""
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    
    return sorted(list(synonyms))[:3]  # **Sort synonyms to make results stable**

def expand_query(query_tokens):
    """Expand the query using synonyms."""
    expanded_tokens = query_tokens[:]
    for token in query_tokens:
        expanded_tokens.extend(get_synonyms(token))
    
    return sorted(expanded_tokens)  # **Sorting ensures stable results**

def semantic_search(query):
    """Perform semantic search using cosine similarity with normalized scores for all products."""
    
    # Tokenize and expand the query before embedding
    query_tokens = tokenize(query)
    expanded_query_tokens = expand_query(query_tokens)
    expanded_query_text = " ".join(expanded_query_tokens)  # Convert back to text

    # Generate query embedding using the processed query
    query_embedding = model.encode(expanded_query_text).reshape(1, -1)

    # Compute cosine similarity with all product embeddings
    similarities = cosine_similarity(query_embedding, product_vectors)[0]

    # Normalize scores between 0 and 1
    min_score = np.min(similarities)
    max_score = np.max(similarities)

    if max_score > min_score:  # Avoid division by zero
        normalized_scores = (similarities - min_score) / (max_score - min_score)
    else:
        normalized_scores = np.zeros_like(similarities)  # If all scores are the same, set them to 0

    # Rank all products by normalized similarity score
    ranked_results = sorted(
        zip(normalized_scores, product_info),
        key=lambda x: x[0],
        reverse=True
    )

    # Return scores for all products (even those with score 0), keeping `product_id`
    return [(score, product) for score, product in ranked_results]

# Example search
query = "red energy drink"
results = semantic_search(query)

# Display results with scores between 0 and 1 (excluding `product_id` in output)
print(f"\n🔍 ** Semantic Search Results for « {query} » ** 🔍\n")
for score, result in results:
    print(f"Score: {score:.4f} | Product: {result['title']} | Variant: {result['variant']} | URL: {result['url']}")
