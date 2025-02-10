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


# Normalize Price Scores (Lower Price = Higher Score) #
# Convert product prices into a NumPy array
prices = np.array([p["price ($)"] for p in product_data])

# Normalize prices between 0 and 1 (0 = lowest price, 1 = highest price)
price_scores = scaler.fit_transform(prices.reshape(-1, 1)).flatten()

# Invert scores so that lower prices have higher scores (1 - normalized value)
price_scores = 1 - price_scores  

# The cheapest product gets a score of 1.0, and the most expensive gets 0.0.



# Normalize Review Scores (More Reviews + High Ratings = Higher Score) #
# Extract rating-related values into NumPy arrays
mean_ratings = np.array([p["mean_mark"] for p in product_data])  # Average rating
total_reviews = np.array([p["total_reviews"] for p in product_data])  # Total number of reviews
last_ratings = np.array([p["last_rating"] for p in product_data])  # Most recent rating

# Compute a raw review score: a combination of review count & quality
# Formula: (mean rating * total reviews) + last rating
review_scores_raw = (mean_ratings * total_reviews) + last_ratings

# Check if there's variation in review scores (avoid division errors)
if review_scores_raw.max() > review_scores_raw.min():
    # Normalize raw review scores between 0 and 1
    review_scores = scaler.fit_transform(review_scores_raw.reshape(-1, 1)).flatten()
else:
    # If all review scores are the same, set them all to 0 (no useful ranking)
    review_scores = np.zeros_like(review_scores_raw)

# Products with the most positive & frequent reviews get scores closer to 1.0.


# Hybrid search function :
def hybrid_search(query, top_n=None, lambda_lexical=0.4, lambda_semantic=0.4, lambda_reviews=0.1, lambda_price=0.1):
    """Perform a hybrid search combining lexical, semantic, price, and review-based ranking."""
    
    # Get results from both search methods
    lexical_results = {p["product_id"]: score for score, p in lexical_search(query)}
    semantic_results = {p["product_id"]: score for score, p in semantic_search(query)}

    # Aggregate scores
    final_scores = []
    for i, product in enumerate(product_data):
        product_id = product["product_id"]  # Use consistent identifier

        # Retrieve scores (default lexical_score to 0 if not found)
        lexical_score = lexical_results.get(product_id, 0)  # ✅ Ensure missing lexical scores are 0
        semantic_score = semantic_results.get(product_id, 0)  # Semantic search always provides a score
        
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



if __name__ == "__main__":
    # Example query (only runs if script is executed directly)
    query = "red energy drink"
    results = hybrid_search(query)

    # Display only the clean output 
    print(f"\n🔍 ** Hybrid Search Results for « {query} » ** 🔍\n")
    for rank, (total_score, lexical_score, semantic_score, review_score, price_score, real_price, result) in enumerate(results, start=1):
        print(f"🏆 Rank {rank}")
        print(f"   Score: {total_score:.4f} (Lexical {lexical_score:.4f}, Semantic {semantic_score:.4f}, Reviews {review_score:.4f}, Price {price_score:.4f} ($ {real_price:.2f}))")
        print(f"   {result['title']} - {result['variant']}")
        print(f"   {result['url']}")
        print("-" * 80)

