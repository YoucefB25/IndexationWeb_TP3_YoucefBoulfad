import math
from collections import Counter
from urllib.parse import urlparse
from src.preprocessing import tokenize

def normalize_url(url):
    """Removes variant parameters from the URL to avoid duplicate products."""
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"  # Remove query parameters
    return base_url

def compute_bm25(query_tokens, documents, df_counter, N, avgdl, k1=None, b=0.75):
    """Computes BM25 scores for ranked retrieval with a boost for important words."""
    if k1 is None:
        k1 = 2.0 if len(query_tokens) > 2 else 1.5  # ✅ Increase BM25 weight for longer queries

    BOOST_WORDS = {"good", "best", "top", "recommended"}  # ✅ Words that should be weighted higher

    scores = []
    for doc in documents:
        doc_tokens = doc['tokens']
        doc_len = len(doc_tokens)
        freq = Counter(doc_tokens)
        score = 0

        for term in query_tokens:
            idf = math.log((N - df_counter.get(term, 0) + 0.5) / (df_counter.get(term, 0) + 0.5) + 1)
            tf = freq.get(term, 0)
            
            # ✅ Boost words like "good", "best", etc.
            weight_boost = 1.5 if term in BOOST_WORDS else 1.0
            
            score += idf * ((tf * (k1 + 1) * weight_boost) / (tf + k1 * (1 - b + b * (doc_len / avgdl))))

        scores.append((doc, score))
    
    return sorted(scores, key=lambda x: x[1], reverse=True)

def rank_documents(query, data_loader, bm25=True, review_weight=0.4, title_weight=0.5, token_weight=0.2):
    """Ranks documents using BM25 and additional heuristics."""
    query_tokens = tokenize(query)
    df_counter = data_loader.get_df()
    N = len(data_loader.documents)
    avgdl = sum(len(doc['tokens']) for doc in data_loader.documents) / N

    bm25_scores = compute_bm25(query_tokens, data_loader.documents, df_counter, N, avgdl) if bm25 else []
    
    normalized_urls = set()  # ✅ Track unique URLs to avoid duplicates
    ranked_docs = []

    for doc, bm25_score in bm25_scores:
        score = bm25_score
        title_match_score = sum(1 for token in query_tokens if token in doc['title'])
        score += title_match_score * title_weight

        review = data_loader.load_reviews_index().get(doc['url'], {"mean_mark": 0, "total_reviews": 0})
        review_score = review["mean_mark"] * review_weight if review["total_reviews"] > 0 else 0
        score += review_score

        clean_url = normalize_url(doc["url"])
        if clean_url not in normalized_urls:
            normalized_urls.add(clean_url)
            ranked_docs.append((doc, score))

    return sorted(ranked_docs, key=lambda x: x[1], reverse=True)
