import json
from hybrid_search import hybrid_search  # Import the hybrid search function

# File paths
QUERY_FILE = "queries.json"  # Input queries
OUTPUT_FILE = "search_results.json"  # Output results

def perform_batch_search(queries, weights, save_top_n=None):
    """
    Performs hybrid search on multiple queries and outputs results in JSON format.

    :param queries: List of query strings
    :param weights: Dictionary with weights for lexical, semantic, reviews, and price
    :param save_top_n: Number of top results to save per query (None = save all)
    :return: Dictionary with search results
    """
    # Unpack weights
    lambda_lexical = weights["lexical"]
    lambda_semantic = weights["semantic"]
    lambda_reviews = weights["reviews"]
    lambda_price = weights["price"]

    results = {}

    for query in queries:
        print(f"\n🔍 Searching for: **{query}** ...")

        # Run hybrid search with new weights
        search_results = hybrid_search(query,
                                       lambda_lexical=lambda_lexical,
                                       lambda_semantic=lambda_semantic,
                                       lambda_reviews=lambda_reviews,
                                       lambda_price=lambda_price)

        # Keep all 46 products but limit saving based on `save_top_n`
        if save_top_n is not None:
            search_results = search_results[:save_top_n]  # Keep only top `save_top_n` results

        # Store results
        results[query] = [
            {
                "rank": rank + 1,
                "title": product["title"],
                "variant": product["variant"],
                "brand": product.get("brand", "Unknown"),  
                "country_of_origin": product.get("country_of_origin", "Unknown"), 
                "url": product["url"],
                "total_score": round(score, 4),
                "lexical_score": round(lexical, 4),
                "semantic_score": round(semantic, 4),
                "review_score": round(review, 4),
                "price_score": round(price, 4),
                "real_price": f"${real_price:.2f}"
            }
            for rank, (score, lexical, semantic, review, price, real_price, product) in enumerate(search_results)
        ]

    return results

# Load queries from JSON file
with open(QUERY_FILE, "r", encoding="utf-8") as f:
    queries = json.load(f)

# Set custom weights (modify here directly)
weights = {
    "lexical": 0.4,   # Adjust BM25 + TF-IDF weight
    "semantic": 0.4,  # Adjust sentence embedding weight
    "reviews": 0.1,   # Adjust review influence
    "price": 0.1      # Adjust price influence
}

# Set how many results to save per query (None = save all 46)
save_top_n = 10  # Change this value to limit saved results

# Run batch search
search_results = perform_batch_search(queries, weights, save_top_n=save_top_n)

# Save results to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(search_results, f, indent=4)

print(f"\n✅ Search results saved to `{OUTPUT_FILE}` with top {save_top_n} results per query.")
