import os
import json
import logging
from collections import Counter
from src.preprocessing import tokenize

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoader:
    """Handles loading and structuring JSON index files."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.df_counter = Counter()  # Precomputed document frequency
        self.documents = self.load_description_index()

    def _load_json(self, filename):
        """Generic method to load JSON files."""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logging.warning(f"Warning: {filename} not found, returning empty dictionary.")
            return {}
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_description_index(self):
        """Loads descriptions and precomputes document frequency."""
        raw_data = self._load_json("description_index.json")
        structured_data = []

        for keyword, urls in raw_data.items():
            for url, relevance_scores in urls.items():
                text = f"{keyword} {url}"  # Combine keyword + URL
                tokens = tokenize(text)
                self.df_counter.update(set(tokens))  # Count unique word occurrences
                structured_data.append({
                    "id": hash(url),
                    "title": f"{keyword.capitalize()} - {url}",
                    "description": f"Contains keyword '{keyword}' (score: {relevance_scores[0]})",
                    "url": url,
                    "tokens": tokens  # Store pre-tokenized text
                })

        logging.info(f"Loaded {len(structured_data)} descriptions.")
        return structured_data

    def load_reviews_index(self):
        """Loads product review scores."""
        return self._load_json("reviews_index.json")

    def get_df(self):
        """Returns precomputed document frequency."""
        return self.df_counter