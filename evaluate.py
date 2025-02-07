import sys
import os
import json
import logging
from src.search import search
from src.load_data import DataLoader

# Ensure 'src' is in the Python path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_ranking_methods(test_queries, config):
    """Evaluates different ranking configurations and saves results."""
    
    # ✅ Fix: Ensure `data_loader` is initialized **inside** the function
    data_loader = DataLoader()

    results = {}

    for config_name, config_values in config.items():
        print(f"\n🔎 Testing config: {config_name}")
        results[config_name] = {}

        for query in test_queries:
            print(f"  Running search for: {query}")

            # ✅ Fix: Pass `data_loader` properly
            retrieved = search(query, data_loader, bm25=config_values["bm25"], review_weight=config_values["review_weight"], 
                               title_weight=config_values["title_weight"], token_weight=config_values["token_weight"])[:10]

            results[config_name][query] = {
                "retrieved": [doc["url"] for doc in retrieved],
                "precision@10": len(retrieved) / 10 if retrieved else 0
            }

    # Save evaluation results
    with open("ranking_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("✅ Ranking evaluation completed. Results saved to 'ranking_results.json'.")

if __name__ == "__main__":
    with open("test_queries.json", "r", encoding="utf-8") as file:
        test_queries = json.load(file)

    ranking_config = {
        "bm25-True_rev-0_title-0_token-0": {"bm25": True, "review_weight": 0, "title_weight": 0, "token_weight": 0},
        "bm25-True_rev-0.3_title-0.5_token-0.2": {"bm25": True, "review_weight": 0.3, "title_weight": 0.5, "token_weight": 0.2}
    }

    test_ranking_methods(test_queries, ranking_config)
