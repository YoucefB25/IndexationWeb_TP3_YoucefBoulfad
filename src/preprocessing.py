import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def tokenize(text):
    """Tokenizes text, removes stopwords, and applies normalization."""
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    tokens = [lemmatizer.lemmatize(token) for token in word_tokenize(text) if token not in stop_words]
    return tokens

def expand_query(query, synonyms):
    """Expands a query using weighted synonyms."""
    tokens = tokenize(query)
    expanded_query = set(tokens)

    for token in tokens:
        if token in synonyms:
            expanded_query.update(synonyms[token][:2])  # Limit to top 2 synonyms

    # ✅ Add custom synonyms manually
    manual_synonyms = {
        "headphones": ["earphones", "headset", "audio device"],
        "gaming monitor": ["gaming display", "144Hz screen"]
    }

    for token in tokens:
        if token in manual_synonyms:
            expanded_query.update(manual_synonyms[token])

    return list(expanded_query)
