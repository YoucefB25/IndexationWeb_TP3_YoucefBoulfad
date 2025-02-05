from load_data import DataLoader
from ranking import rank_documents

data_loader = DataLoader()
documents = data_loader.load_description_index()


def search(query):
    """Executes a search query and returns ranked results."""

    print(f"DEBUG: Loaded {len(documents)} documents")  # ✅ Check if documents are loaded
    if documents:
        print("DEBUG: Sample document:", documents[0])  # ✅ Print first document for verification

    ranked_results = rank_documents(query, documents)  # Rank documents
    
    return ranked_results

print(f"DEBUG: {len(documents)} documents chargés")
if documents:
    print("DEBUG: Exemple de document :", documents[0])
