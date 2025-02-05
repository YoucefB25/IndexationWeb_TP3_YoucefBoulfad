from load_data import (load_brand_index, load_description_index, load_domain_index, 
                           load_origin_index, load_reviews_index, load_title_index, load_origin_synonyms)
from filtering import filter_documents
from ranking import compute_bm25

def search(query):
    """Executes a search query and returns ranked results."""
    # Load indexes
    documents = load_description_index()  # Primary index for searching descriptions
    synonyms = load_origin_synonyms()
    
    # Step 1: Filtering
    filtered_docs = filter_documents(query, documents, synonyms)
    
    # Step 2: Ranking
    ranked_docs = compute_bm25(query, filtered_docs)
    
    # Format results
    return [
        {"title": doc['title'], "url": doc.get('url', ''), "description": doc['description'], "score": score}
        for doc, score in ranked_docs
    ]
