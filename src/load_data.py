import os
import json


class DataLoader:
    """A class to handle loading and parsing various JSON index files."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root directory
    DATA_DIR = os.path.join(BASE_DIR, "data")  # Data directory where JSON files are stored

    def __init__(self):
        print("✅ DataLoader initialized.")

    def _load_json(self, filename):
        """Generic method to load a JSON file."""
        filepath = os.path.join(self.DATA_DIR, filename)
        print(f"DEBUG: Loading file {filepath}")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Error: {filename} not found!")

        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        print(f"DEBUG: JSON successfully loaded, type: {type(data)}")
        return data

    def load_description_index(self):
        """
        Loads and processes `description_index.json`, transforming it into a structured list of documents.
        """
        data = self._load_json("description_index.json")

        processed_data = []
        if isinstance(data, dict):
            for keyword, url_dict in data.items():
                if isinstance(url_dict, dict):
                    for url, values in url_dict.items():
                        if isinstance(values, list):
                            processed_data.append({
                                "id": hash(url),  # Unique identifier based on the URL
                                "title": f"{keyword.capitalize()} - Product at {url}",
                                "description": f"This product is associated with '{keyword}' (relevance score: {values})",
                                "url": url
                            })

        print(f"DEBUG: {len(processed_data)} documents processed")
        return processed_data

    def load_simple_dict(self, filename):
        """
        Loads a JSON file that is expected to be a simple dictionary and returns it as-is.
        """
        return self._load_json(filename)

    # Methods to load specific indexes
    def load_origin_synonyms(self):
        """Loads `origin_synonyms.json` (already a dictionary)."""
        return self.load_simple_dict("origin_synonyms.json")

    def load_origin_index(self):
        """Loads `origin_index.json`, a dictionary mapping origins to product URLs."""
        return self.load_simple_dict("origin_index.json")

    def load_reviews_index(self):
        """Loads `reviews_index.json`, containing review scores and total reviews per URL."""
        return self.load_simple_dict("reviews_index.json")

    def load_title_index(self):
        """Loads `title_index.json`, mapping keywords to product URLs."""
        return self.load_simple_dict("title_index.json")

    def load_brand_index(self):
        """Loads `brand_index.json`, mapping brands to product URLs."""
        return self.load_simple_dict("brand_index.json")

    def load_domain_index(self):
        """Loads `domain_index.json`, mapping domains to product URLs."""
        return self.load_simple_dict("domain_index.json")
