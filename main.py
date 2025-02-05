import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.search import search
import json

if __name__ == "__main__":
    query = input("Enter your search query: ")
    results = search(query)

    output = {
        "total_documents": len(results),
        "results": results[:10]  # Show top 10 results
    }

    # Save results to JSON file
    with open("search_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print("Search results saved to 'search_results.json'")
