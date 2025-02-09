import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the same embedding model used for products
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load product embeddings
with open("embeddings_of_products.json", "r", encoding="utf-8") as f:
    product_embeddings = json.load(f)

# Extract embeddings and product info
product_vectors = np.array([p["embeddings"] for p in product_embeddings])
product_info = [
    {"url": p["url"], "title": p["title"], "variant": p.get("variant", "N/A")}
    for p in product_embeddings
]

def search_semantic(query, top_n=10):
    """Perform semantic search using cosine similarity with normalized scores."""
    # Generate query embedding
    query_embedding = model.encode(query).reshape(1, -1)

    # Compute cosine similarity with all product embeddings
    similarities = cosine_similarity(query_embedding, product_vectors)[0]

    # Normalize scores between 0 and 1
    min_score = np.min(similarities)
    max_score = np.max(similarities)

    if max_score > min_score:  # Avoid division by zero
        normalized_scores = (similarities - min_score) / (max_score - min_score)
    else:
        normalized_scores = np.zeros_like(similarities)  # If all scores are the same, set them to 0

    # Rank products by normalized similarity score
    ranked_results = sorted(
        zip(normalized_scores, product_info),
        key=lambda x: x[0],
        reverse=True
    )

    # Return top N results
    return ranked_results[:top_n]

# Example search
query = "red energy drink"
results = search_semantic(query)

# Display results with scores between 0 and 1
print("\n🔍 **Top Search Results (Normalized Scores)** 🔍\n")
for score, result in results:
    print(f"Score: {score:.4f} | Product: {result['title']} | Variant: {result['variant']} | URL: {result['url']}")
