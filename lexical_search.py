import json
import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi

# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

# Initialize NLTK tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Load tokenized product data
with open("tokenized_products.json", "r", encoding="utf-8") as f:
    tokenized_products = json.load(f)

def tokenize(text):
    """Tokenize, remove stopwords, and lemmatize."""
    text = text.lower()
    words = word_tokenize(text)
    words = [w for w in words if w.isalnum()]
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return words

def get_synonyms(word):
    """Retrieve up to 3 synonyms for a given word."""
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace("_", " "))

    return sorted(list(synonyms))[:3]  # **Sort synonyms to make results stable**

def expand_query(query_tokens):
    """Expand the query using synonyms."""
    expanded_tokens = query_tokens[:]
    for token in query_tokens:
        expanded_tokens.extend(get_synonyms(token))

    return sorted(expanded_tokens)  # **Sorting ensures stable results**

# **Initialize TF-IDF and BM25 ONCE to keep scores consistent**
product_texts = [" ".join(product["tokens"]) for product in tokenized_products]

tfidf_vectorizer = TfidfVectorizer(norm='l2', use_idf=True, smooth_idf=True)  # **Fix TF-IDF variability**
tfidf_matrix = tfidf_vectorizer.fit_transform(product_texts)  # Compute once

bm25_corpus = [product["tokens"] for product in tokenized_products]
bm25_model = BM25Okapi(bm25_corpus)  # **Ensure BM25 is initialized once**

def lexical_search(query):
    """Search products using TF-IDF + BM25 and return scores for all products."""
    query_tokens = tokenize(query)
    expanded_query_tokens = expand_query(query_tokens)

    # Pre-filter products: Keep only those that share at least one token with the query
    filtered_products = [
        product for product in tokenized_products
        if any(token in product["tokens"] for token in expanded_query_tokens)
    ]

    if not filtered_products:
        return []  # No relevant products found

    # Continue with existing scoring process...
    product_texts = [" ".join(product["tokens"]) for product in filtered_products]
    tfidf_matrix = tfidf_vectorizer.fit_transform(product_texts)
    query_vector = tfidf_vectorizer.transform([" ".join(expanded_query_tokens)])
    cosine_similarities = (tfidf_matrix @ query_vector.T).toarray().flatten()

    bm25_corpus = [product["tokens"] for product in filtered_products]
    bm25_model = BM25Okapi(bm25_corpus)
    bm25_scores = bm25_model.get_scores(expanded_query_tokens)

    final_scores = 0.5 * cosine_similarities + 0.5 * np.array(bm25_scores)

    # Normalize scores
    min_score, max_score = np.min(final_scores), np.max(final_scores)
    if max_score > min_score:
        final_scores = (final_scores - min_score) / (max_score - min_score)
    else:
        final_scores = np.zeros_like(final_scores)

    # Rank and return results
    ranked_products = sorted(
        zip(final_scores, filtered_products),
        key=lambda x: x[0],
        reverse=True
    )

    return [(score, {"product_id": product["product_id"], **product}) for score, product in ranked_products]


# Example search
query = "red energy drink"
results = lexical_search(query)

# Display results with stable scores between 0 and 1 (excluding `product_id` in output)
print(f"\n🔍 ** Lexical Search Results for « {query} » ** 🔍\n")
for score, result in results:
    print(f"Score: {score:.4f} | Product: {result['title']} | Variant: {result.get('variant', 'N/A')} | URL: {result.get('url', 'N/A')}")
