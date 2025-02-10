import json
import numpy as np
from lexical_search import lexical_search
from semantic_search import semantic_search
from sklearn.preprocessing import MinMaxScaler

# Load extracted product data
with open("extracted_products.json", "r", encoding="utf-8") as f:
    product_data = json.load(f)

# Extract price and review statistics
prices = np.array([p["price ($)"] for p in product_data])
mean_ratings = np.array([p["mean_mark"] for p in product_data])
total_reviews = np.array([p["total_reviews"] for p in product_data])
last_ratings = np.array([p["last_rating"] for p in product_data])

# Normalize scores (scales values between 0 and 1)
scaler = MinMaxScaler()

# Normalize price scores (Lower price = higher score)
price_scores = scaler.fit_transform(prices.reshape(-1, 1)).flatten()
price_scores = 1 - price_scores  # Invert so lower prices get higher scores

# Normalize review scores based on (mean rating * total reviews + latest rating)
review_scores_raw = mean_ratings * total_reviews + last_ratings
if review_scores_raw.max() > review_scores_raw.min():  # Prevent division by zero
    review_scores = scaler.fit_transform(review_scores_raw.reshape(-1, 1)).flatten()
else:
    review_scores = np.zeros_like(review_scores_raw)  # If all are the same, set to 0

def hybrid_search(query, top_n=None, lambda_lexical=0.4, lambda_semantic=0.4, lambda_reviews=0.1, lambda_price=0.1):
    """Perform a hybrid search combining lexical, semantic, price, and review-based ranking."""
    
    # Get results from both search methods
    lexical_results = {p["product_id"]: score for score, p in lexical_search(query)}
    semantic_results = {p["product_id"]: score for score, p in semantic_search(query)}

    # Check missing scores
    for product in product_data:
        product_id = product["product_id"]
        found_in_lexical = product_id in lexical_results
        found_in_semantic = product_id in semantic_results
        print(f"Checking Product ID: {product_id}")
        print(f"  Found in Lexical Search? {found_in_lexical}")
        print(f"  Found in Semantic Search? {found_in_semantic}")
        if not found_in_lexical or not found_in_semantic:
            print(f"⚠️ WARNING: Missing score for {product['title']} - {product['variant']}")
        print("-" * 50)

    # Aggregate scores
    final_scores = []
    for i, product in enumerate(product_data):
        product_id = product["product_id"]  # Use consistent identifier

        # Retrieve lexical and semantic scores (default to 0 if not found)
        lexical_score = lexical_results.get(product_id, 0)
        semantic_score = semantic_results.get(product_id, 0)
        
        # Get normalized price and review scores
        price_score = price_scores[i]  # Between 0 and 1
        review_score = review_scores[i]  # Between 0 and 1
        real_price = product["price ($)"]

        # Compute weighted final score
        final_score = (
            lambda_lexical * lexical_score +
            lambda_semantic * semantic_score +
            lambda_price * price_score +
            lambda_reviews * review_score
        )

        final_scores.append((final_score, lexical_score, semantic_score, review_score, price_score, real_price, product))

    # Sort all products by highest score
    ranked_results = sorted(final_scores, key=lambda x: x[0], reverse=True)

    # **Apply `top_n` if specified**
    if top_n is not None:
        ranked_results = ranked_results[:top_n]

    return ranked_results  # ✅ Returns scores for all products


# Example query
query = "red energy drink"
results = hybrid_search(query)

# Display only the clean output 
print(f"\n🔍 ** Hybrid Search Results for « {query} » ** 🔍\n")
for rank, (total_score, lexical_score, semantic_score, review_score, price_score, real_price, result) in enumerate(results, start=1):
    print(f"🏆 Rank {rank}")
    print(f"   Score: {total_score:.4f} (Lexical {lexical_score:.4f}, Semantic {semantic_score:.4f}, Reviews {review_score:.4f}, Price {price_score:.4f} ($ {real_price:.2f}))")
    print(f"   {result['title']} - {result['variant']}")
    print(f"   {result['url']}")
    print("-" * 80)  # Separator for better readability
