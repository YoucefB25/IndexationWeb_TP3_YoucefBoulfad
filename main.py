import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.search import search
import json

def run_tests():
    """Runs test queries and saves results."""
    with open("test_queries.json", "r", encoding="utf-8") as file:
        test_queries = json.load(file)

    all_results = {}

    for query in test_queries:
        print(f"Running search for: {query}")
        results = search(query)
        all_results[query] = results[:5]  # Save only top 5 results for each query

    # Save results to JSON
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print("Test results saved to 'test_results.json'.")

if __name__ == "__main__":
    run_tests()

