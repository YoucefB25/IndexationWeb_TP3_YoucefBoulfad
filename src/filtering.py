from preprocessing import tokenize, expand_query

def contains_any_token(query_tokens, document_tokens):
    """Checks if at least one token from the query is in the document."""
    return any(token in document_tokens for token in query_tokens)

def contains_all_tokens(query_tokens, document_tokens):
    """Checks if all query tokens (excluding stopwords) are in the document."""
    return all(token in document_tokens for token in query_tokens)


def filter_documents(query, documents, synonyms, strict=False):
    """Filters documents that match at least one token in the query.
       If strict=True, requires at least 2 query tokens in the title.
    """
    expanded_query = expand_query(query, synonyms)
    filtered_docs = []

    for doc in documents:
        doc_tokens = doc['tokens']
        title_match = sum(token in doc['title'].lower() for token in expanded_query)

        if strict and title_match < 2:  # ✅ Require at least 2 query tokens for stricter filtering
            continue

        if any(token in doc_tokens for token in expanded_query):
            filtered_docs.append(doc)

    return filtered_docs


