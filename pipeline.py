import os
import json
import logging
import math
import string
import nltk
import tensorflow_hub as hub
import numpy as np
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_product_id(url):
    """Extracts the product ID from a URL."""
    match = re.search(r"/product/(\d+)", url)
    return match.group(1) if match else None

def extract_variant_from_url(url):
    """Extracts the product variant from the URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("variant", [""])[0]  # Get first variant if exists

def get_product_details(url, title_cache={}):
    """Fetches the product title via scraping and extracts variant from URL."""
    product_id = extract_product_id(url)
    
    if product_id in title_cache:
        return title_cache[product_id], extract_variant_from_url(url)

    try:
        print(f"🔍 Scraping: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        # 🛠 Extract title correctly from <h3 class="product-title">
        title_element = soup.select_one("h3.product-title")  # Correct selector
        if not title_element:
            title_element = soup.find("meta", {"property": "og:title"})  # Fallback
        if not title_element:
            title_element = soup.find("title")  # Another fallback

        # Clean title if extracted from <meta> or <title>
        title = title_element.text.strip() if title_element else "Unknown Title"

        # Cache title to avoid duplicate scrapes
        title_cache[product_id] = title  

        return title, extract_variant_from_url(url)
    
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
    
    return "Unknown Title", extract_variant_from_url(url)







# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Download necessary NLTK resources
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

# Load Stopwords and Lemmatizer
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# Load Universal Sentence Encoder (USE)
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

def extract_product_id(url):
        """Extracts the product ID from a URL."""
        match = re.search(r"/product/(\d+)", url)
        return match.group(1) if match else None
    
class DataLoader:
    """Loads and processes data from JSON index files."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.df_counter = Counter()
        self.title_index = self.load_title_index()  # Load product titles
        self.documents = self.load_description_index()
        self.avgdl = self.calculate_avgdl()  # 🚀 Fix: Add this back

    def _load_json(self, filename):
        """Loads a JSON file from the data directory."""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logging.warning(f"Warning: {filename} not found, returning empty dictionary.")
            return {}
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_title_index(self):
        """Retrieves product titles from URLs or scrapes them if missing."""
        raw_data = self._load_json("description_index.json")
        title_mapping = {}

        for keyword, url_dict in raw_data.items():
            for url in url_dict.keys():
                product_id = extract_product_id(url)
                if product_id and product_id not in title_mapping:
                    # Try to get a title via scraping if not found in description index
                    title_mapping[product_id] = get_product_details(url)

        logging.info(f"Extracted {len(title_mapping)} product titles from URLs.")
        return title_mapping



    def load_description_index(self):
        """Loads descriptions and assigns real titles using the title index."""
        raw_data = self._load_json("description_index.json")
        structured_data = []

        for keyword, url_dict in raw_data.items():
            for url, metadata in url_dict.items():
                product_id = extract_product_id(url)
                product_title = self.title_index.get(product_id, keyword.capitalize())  # Use extracted title

                tokens = tokenize(f"{product_title} {keyword} {url}")
                self.df_counter.update(set(tokens))

                structured_data.append({
                    "id": hash(url),
                    "title": product_title,  # Now using the extracted product title
                    "description": f"Contains keyword '{keyword}' (score: {metadata[0]})",
                    "url": url,
                    "tokens": tokens,
                })

        logging.info(f"Loaded {len(structured_data)} descriptions.")
        return structured_data



    
    def calculate_avgdl(self):
        """Computes the average document length."""
        total_length = sum(len(doc["tokens"]) for doc in self.documents)
        avgdl = total_length / len(self.documents) if self.documents else 0
        logging.info(f"Calculated average document length: {avgdl}")
        return avgdl



def tokenize(text):
    """Tokenizes and normalizes text (lowercasing, punctuation removal, stopwords)."""
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return [lemmatizer.lemmatize(token) for token in word_tokenize(text) if token not in stop_words]


def get_sentence_embedding(text):
    """Returns a normalized sentence embedding from USE."""
    embedding = embed([text]).numpy()[0]
    return embedding / np.linalg.norm(embedding)  # Normalize


def compute_bm25(query_tokens, documents, df_counter, N, avgdl, k1=1.5, b=0.75):
    """Computes BM25 scores for all documents."""
    scores = []
    for doc in documents:
        doc_tokens = doc["tokens"]
        doc_len = len(doc_tokens)
        freq = Counter(doc_tokens)
        score = 0

        for term in query_tokens:
            df = df_counter.get(term, 0)
            idf = max(math.log(1 + (N - df + 0.5) / (df + 0.5)), 0)  # Ensure idf ≥ 0
            tf = freq.get(term, 0)
            term_score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avgdl))))
            score += term_score

        scores.append((doc, score))
    return sorted(scores, key=lambda x: x[1], reverse=True)


def rank_documents(query, data_loader, bm25_weight=0.6, similarity_weight=0.4):
    """Ranks documents, scrapes titles, extracts variants, and removes duplicates while keeping different variants."""
    query_tokens = tokenize(query)
    query_embedding = get_sentence_embedding(query)
    
    bm25_scores = compute_bm25(query_tokens, data_loader.documents, data_loader.df_counter,
                               len(data_loader.documents), data_loader.avgdl)

    title_cache = {}  # Prevents redundant scraping
    unique_results = {}  # Store best result per (title, variant)

    for doc, bm25_score in bm25_scores:
        doc_embedding = get_sentence_embedding(doc["description"])
        similarity_score = cosine_similarity([query_embedding], [doc_embedding])[0][0]
        final_score = float(bm25_weight * bm25_score + similarity_weight * similarity_score)

        # Get product title and variant
        title, variant = get_product_details(doc["url"], title_cache)

        # 🚀 Deduplication: Keep the highest-scoring result per (title, variant)
        key = (title, variant)  # Unique key: title + variant
        if key not in unique_results or final_score > unique_results[key]["score"]:
            unique_results[key] = {
                "title": title,
                "variant": variant,
                "url": doc["url"],  # Keep one URL (highest score)
                "score": final_score
            }

    # Sort by score and return top results
    return sorted(unique_results.values(), key=lambda x: x["score"], reverse=True)[:10]










def search(queries, data_loader):
    """Processes multiple queries and returns ranked results."""
    results = {}
    for query in queries:
        logging.info(f"Processing query: {query}")
        results[query] = rank_documents(query, data_loader)
    return results


def main():
    """Runs the search pipeline using queries from 'test_queries.json' and saves results to 'test_results.json'."""
    data_loader = DataLoader()

    # Load queries from test_queries.json
    query_file = "test_queries.json"
    if not os.path.exists(query_file):
        logging.error(f"{query_file} not found! Exiting.")
        return

    with open(query_file, "r", encoding="utf-8") as file:
        queries = json.load(file)

    # Process queries and get results
    results = search(queries, data_loader)

    # Save results to test_results.json
    with open("test_results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    logging.info("Search results saved to 'test_results.json'")


if __name__ == "__main__":
    main()
