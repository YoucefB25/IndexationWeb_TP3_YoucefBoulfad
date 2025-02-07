import sys
import os
import json
from src.search import search
from src.load_data import DataLoader

# Ensure 'src' is in the Python path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run search tests.")
parser.add_argument("--bm25", type=bool, default=True, help="Enable or disable BM25 ranking")
parser.add_argument("--review_weight", type=float, default=0.3, help="Weight for review scores in ranking")
parser.add_argument("--title_weight", type=float, default=0.5, help="Weight for title matching in ranking")
parser.add_argument("--token_weight", type=float, default=0.2, help="Weight for token frequency in ranking")
parser.add_argument("--max_results", type=int, default=10, help="Number of results to return per query")

args = parser.parse_args()
config = vars(args)

def run_tests():
    """Runs test queries and saves results with a configurable limit."""
    
    data_loader = DataLoader()  # Load data

    with open("test_queries.json", "r", encoding="utf-8") as file:
        test_queries = json.load(file)

    all_results = {}

    for query in test_queries:
        print(f"Running search for: {query}")
        results = search(query, data_loader, bm25=config["bm25"], review_weight=config["review_weight"], 
                         title_weight=config["title_weight"], token_weight=config["token_weight"])[:config["max_results"]]
        all_results[query] = results

    # Save results
    filename = f"test_results_{config['max_results']}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"Test results saved to '{filename}'.")

if __name__ == "__main__":
    run_tests()
