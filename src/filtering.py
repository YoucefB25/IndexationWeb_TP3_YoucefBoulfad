from preprocessing import tokenize, expand_query

def filter_documents(query, documents, synonyms):
    """Filters documents based on query tokens."""
    expanded_query = expand_query(query, synonyms)
    filtered_docs = []
    
    for doc in documents:
        doc_tokens = tokenize(doc.get('title', '') + ' ' + doc.get('description', ''))
        if any(token in doc_tokens for token in expanded_query):
            filtered_docs.append(doc)
    
    return filtered_docs
