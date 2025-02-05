from collections import Counter
import math
from preprocessing import tokenize

def compute_bm25(query, documents, k1=1.5, b=0.75):
    """Computes BM25 scores for each document."""
    N = len(documents)
    avgdl = sum(len(tokenize(doc['description'])) for doc in documents) / N
    df = Counter()
    
    for doc in documents:
        words = set(tokenize(doc['description']))
        for word in words:
            df[word] += 1
    
    scores = []
    for doc in documents:
        doc_tokens = tokenize(doc['description'])
        freq = Counter(doc_tokens)
        score = 0
        
        for term in tokenize(query):
            if term in freq:
                idf = math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1)
                tf = freq[term]
                score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (len(doc_tokens) / avgdl))))
        
        scores.append((doc, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

