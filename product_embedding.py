import json
from sentence_transformers import SentenceTransformer

# File paths
TOKENIZED_FILE = "tokenized_products.json"
OUTPUT_FILE = "embeddings_of_products.json"

# Load data
with open(TOKENIZED_FILE, "r", encoding="utf-8") as f:
    tokenized_products = json.load(f)

# Load embedding model
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

# Generate embeddings with structured format
embeddings_index = [
    {
        "product_id": p["product_id"],  # ✅ Keep the unique identifier
        "url": p["url"],
        "title": p.get("title"),
        "variant": p.get("variant"),
        "embeddings": model.encode(" ".join(p["tokens"])).tolist()
    }
    for p in tokenized_products
]

# Save results
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(embeddings_index, f, indent=4)

print(f"✅ Embeddings saved in {OUTPUT_FILE}.")
