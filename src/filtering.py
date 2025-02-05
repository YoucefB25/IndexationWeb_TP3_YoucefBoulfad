from preprocessing import tokenize, expand_query

def contains_any_token(query_tokens, document_tokens):
    """Checks if at least one token from the query is in the document."""
    return any(token in document_tokens for token in query_tokens)

def contains_all_tokens(query_tokens, document_tokens):
    """Checks if all query tokens (excluding stopwords) are in the document."""
    return all(token in document_tokens for token in query_tokens)


def filter_documents(query, documents, synonyms):
    """Filters documents based on query tokens."""
    expanded_query = expand_query(query, synonyms)
    filtered_docs = []

    print(f"DEBUG: Expanded query for '{query}' -> {expanded_query}")

    for doc in documents:
        title = doc.get('title', '').strip()
        description = doc.get('description', '').strip()

        if not title and not description:  # ✅ Skip empty docs
            print(f"WARNING: Skipping empty document {doc}")
            continue

        doc_tokens = tokenize(title + ' ' + description)

        if any(token in doc_tokens for token in expanded_query):
            filtered_docs.append(doc)

    print(f"DEBUG: {len(filtered_docs)} documents matched for query '{query}'")
    return filtered_docs

