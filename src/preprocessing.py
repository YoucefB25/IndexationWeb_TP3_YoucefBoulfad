import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Download necessary resources
nltk.download('punkt')
nltk.download('stopwords')

# Load English and French stopwords
stop_words = set(stopwords.words('english') + stopwords.words('french'))

def tokenize(text):
    """Tokenizes text, converts to lowercase, and removes stopwords and punctuation."""
    text = text.lower().translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenization
    return [token for token in tokens if token not in stop_words]  # Remove stopwords

def expand_query(query, synonyms):
    """Expands a query by adding synonyms from the synonym dictionary."""
    tokens = tokenize(query)
    expanded_query = set(tokens)
    for token in tokens:
        if token in synonyms:
            expanded_query.update(synonyms[token])
    return list(expanded_query)
