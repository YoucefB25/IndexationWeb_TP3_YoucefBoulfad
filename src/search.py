import logging
from src.load_data import DataLoader
from src.ranking import compute_bm25
from src.preprocessing import tokenize


data_loader = DataLoader()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search(query, data_loader, bm25=True, review_weight=0.4, title_weight=0.5, token_weight=0.2):
    """Executes a search query and returns ranked results."""
    logging.info(f"Executing search for query: '{query}'")
    query_tokens = tokenize(query)
    df_counter = data_loader.get_df()
    N = len(data_loader.documents)
    avgdl = sum(len(doc['tokens']) for doc in data_loader.documents) / N
    
    bm25_scores = compute_bm25(query_tokens, data_loader.documents, df_counter, N, avgdl) if bm25 else []
    return [{"title": doc['title'], "url": doc['url'], "score": score} for doc, score in bm25_scores]
