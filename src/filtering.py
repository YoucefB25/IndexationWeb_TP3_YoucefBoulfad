from preprocessing import tokenize, expand_query

def contains_any_token(query_tokens, document_tokens):
    """Checks if at least one token from the query is in the document."""
    return any(token in document_tokens for token in query_tokens)

def contains_all_tokens(query_tokens, document_tokens):
    """Checks if all query tokens (excluding stopwords) are in the document."""
    return all(token in document_tokens for token in query_tokens)

def filter_documents(query, documents, synonyms, match_all=False):
    """
    Filters documents based on query tokens.

    - If `match_all=True`, returns documents that contain all query tokens.
    - If `match_all=False`, returns documents that contain at least one query token.
    """
    expanded_query = expand_query(query, synonyms)
    filtered_docs = []

    for doc in documents:
        doc_tokens = tokenize(doc.get('title', '') + ' ' + doc.get('description', ''))
        
        # Choose filtering method
        if match_all:
            condition = contains_all_tokens(expanded_query, doc_tokens)
        else:
            condition = contains_any_token(expanded_query, doc_tokens)

        if condition:
            filtered_docs.append(doc)
    
    return filtered_docs


