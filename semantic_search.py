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
    """Perform semantic search using cosine similarity."""
    # Generate query embedding
    query_embedding = model.encode(query).reshape(1, -1)

    # Compute cosine similarity with all product embeddings
    similarities = cosine_similarity(query_embedding, product_vectors)[0]

    # Rank products by similarity score
    ranked_results = sorted(
        zip(similarities, product_info),
        key=lambda x: x[0],
        reverse=True
    )

    # Return top N results
    return ranked_results[:top_n]

# Example search
query = "red energy drink"
results = search_semantic(query)

# Display results
for score, result in results:
    print(f"Score: {score:.4f} | Product: {result['title']} | Variant: {result['variant']} | URL: {result['url']}")
