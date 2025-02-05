import nltk
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import string

# Set custom NLTK data path to /data/nltk_data/
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nltk_data")
nltk.data.path = [NLTK_DATA_PATH]  # Make sure it ONLY searches in /data/nltk_data/

# Ensure the directory exists
os.makedirs(NLTK_DATA_PATH, exist_ok=True)

# Download necessary resources to /data/nltk_data/
nltk.download('punkt', download_dir=NLTK_DATA_PATH)
nltk.download('punkt_tab', download_dir=NLTK_DATA_PATH)
nltk.download('stopwords', download_dir=NLTK_DATA_PATH)
nltk.download('wordnet', download_dir=NLTK_DATA_PATH)

# Load English stopwords from the new directory
stop_words = stopwords.words('english')

# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def tokenize(text):
    """Tokenizes text, converts to lowercase, removes stopwords and punctuation, and applies normalization."""
    text = text.lower().translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenization
    print(f"DEBUG: Tokenized '{text}' -> {tokens}")  # ✅ Debugging tokenization
    return tokens


def expand_query(query, synonyms):
    """Expands a query by adding synonyms from the synonym dictionary."""
    tokens = tokenize(query)
    expanded_query = set(tokens)
    for token in tokens:
        if token in synonyms:
            expanded_query.update(synonyms[token])
    return list(expanded_query)
