import json
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

# Load input and output file paths
INPUT_FILE = "extracted_products.json"
OUTPUT_FILE = "tokenized_products.json"

# Load extracted products data
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

# Initialize NLTK tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Function to tokenize and lemmatize text
def tokenize(text):
    """Tokenize, remove stopwords, and lemmatize text."""
    text = text.lower()
    words = word_tokenize(text)
    words = [w for w in words if w.isalnum()]
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return words

# Function to generate synonyms
def get_synonyms(word):
    """Retrieve synonyms for a given word using WordNet."""
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace("_", " "))  # Convert to readable format
    return list(synonyms)[:3]  # Limit to 3 synonyms

# Process products and generate tokens
tokenized_products = []
for product in products:
    # Tokenize fields
    title_tokens = tokenize(product["title"])
    variant_tokens = tokenize(product["variant"])
    description_tokens = tokenize(product["description"])
    brand_tokens = tokenize(product["brand"])
    country_tokens = tokenize(product["country_of_origin"])

    # Get synonyms for important fields
    synonym_tokens = []
    for token in title_tokens + country_tokens:
        synonym_tokens.extend(get_synonyms(token))

    # Replicate title and variant tokens for weighting
    weighted_tokens = (
        title_tokens * 10 +  # More weight for title
        variant_tokens * 10 +  # More weight for variant
        description_tokens +
        brand_tokens * 10 +
        country_tokens * 10 +
        synonym_tokens * 5  # Add synonyms
    )

    # Store tokenized result with `product_id`
    tokenized_products.append({
        "product_id": product["product_id"],  # ✅ Keep the unique identifier
        "url": product["url"],
        "title": product["title"],
        "variant": product["variant"],
        "tokens": weighted_tokens
    })

# Save tokenized data
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(tokenized_products, f, indent=4)

print(f"✅ Tokenization complete! Results saved in {OUTPUT_FILE}.")
