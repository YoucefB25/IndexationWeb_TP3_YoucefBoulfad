from collections import Counter
import math
from preprocessing import tokenize
from filtering import filter_documents
from load_data import load_description_index, load_origin_synonyms

def compute_bm25(query, documents, k1=1.5, b=0.75):
    """
    Computes BM25 scores for a list of documents based on the given query.
    
    Parameters:
    - query (str): The search query
    - documents (list): A list of documents (each containing title, description, etc.)
    - k1 (float): Controls term frequency scaling
    - b (float): Controls document length normalization

    Returns:
    - List of tuples (document, BM25 score), sorted by score in descending order
    """
    N = len(documents)  # Total number of documents
    avgdl = sum(len(tokenize(doc['description'])) for doc in documents) / N  # Average document length
    
    # Compute document frequencies
    df = Counter()
    for doc in documents:
        words = set(tokenize(doc['description']))  # Unique words in the document
        for word in words:
            df[word] += 1
    
    # Compute BM25 scores
    scores = []
    query_tokens = tokenize(query)

    for doc in documents:
        doc_tokens = tokenize(doc['description'])
        doc_len = len(doc_tokens)
        freq = Counter(doc_tokens)
        score = 0

        for term in query_tokens:
            if term in freq:
                idf = math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1)  # Inverse Document Frequency
                tf = freq[term]  # Term Frequency
                score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avgdl))))

        scores.append((doc, score))

    return sorted(scores, key=lambda x: x[1], reverse=True)  # Sort documents by score


def exact_match_boost(query, documents):
    """
    Boosts documents where the exact query appears in the title or description.
    
    Parameters:
    - query (str): The search query
    - documents (list): A list of documents (each containing title, description, etc.)
    
    Returns:
    - Dictionary mapping document IDs to boost values
    """
    boost_values = {}

    for doc in documents:
        boost = 0
        if query.lower() in doc['title'].lower():  # Exact match in title
            boost += 2
        if query.lower() in doc['description'].lower():  # Exact match in description
            boost += 1
        
        boost_values[doc['id']] = boost  # Store boost for this document

    return boost_values


def compute_linear_score(query, documents, bm25_scores, review_weight=0.2, title_weight=0.5):
    """
    Computes a linear scoring function combining:
    - BM25 score
    - Exact match boosting
    - Token frequency
    - Presence in title vs description
    - Review scores (if available)

    Parameters:
    - query (str): The search query
    - documents (list): A list of documents
    - bm25_scores (list): List of (document, BM25 score) tuples
    - review_weight (float): Weight assigned to reviews
    - title_weight (float): Weight assigned to title matches

    Returns:
    - List of tuples (document, final score), sorted by score in descending order
    """
    exact_boosts = exact_match_boost(query, documents)
    
    scores = []
    for doc, bm25_score in bm25_scores:
        doc_id = doc['id']
        score = bm25_score  # Start with BM25 score

        # Add exact match boost
        score += exact_boosts.get(doc_id, 0)

        # Prioritize documents with keywords in the title
        title_tokens = tokenize(doc['title'])
        query_tokens = tokenize(query)
        title_match_score = sum(1 for token in query_tokens if token in title_tokens)
        score += title_match_score * title_weight

        # Incorporate review score (if available)
        review_score = float(doc.get('review_score', 0))  # Default to 0 if not present
        score += review_score * review_weight

        scores.append((doc, score))

    return sorted(scores, key=lambda x: x[1], reverse=True)  # Sort by final score



def rank_documents(query, documents):
    """
    Ranks documents using BM25, exact match boosting, and additional scoring factors.

    Parameters:
    - query (str): The search query
    - documents (list): List of documents to rank

    Returns:
    - List of ranked documents
    """
    # Step 1: Filter documents
    synonyms = load_origin_synonyms()
    filtered_docs = filter_documents(query, documents, synonyms)

    if not filtered_docs:  # If no documents match, return empty
        return []

    # Step 2: Compute BM25 scores
    bm25_scores = compute_bm25(query, filtered_docs)

    # Step 3: Compute final ranking using linear scoring
    ranked_docs = compute_linear_score(query, filtered_docs, bm25_scores)

    return [
        {"title": doc['title'], "url": doc.get('url', ''), "description": doc['description'], "score": score}
        for doc, score in ranked_docs
    ]
