import os
import json

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Goes up one level from /src/
DATA_DIR = os.path.join(BASE_DIR, 'data')  # Path to the data folder

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def load_json(filename):
    """Loads a JSON file and ensures it's properly parsed."""
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: The file {filename} was not found!")

    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)

            # ✅ Convert dictionary to list if needed
            if isinstance(data, dict):
                data = list(data.values())

            if not isinstance(data, list):
                raise ValueError(f"Error: {filename} should be a list of dictionaries, but got {type(data)}")

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Error: {filename} contains invalid JSON! {e}")
# Load specific indexes
def load_brand_index():
    return load_json('brand_index.json')

def load_description_index():
    return load_json('description_index.json')

def load_domain_index():
    return load_json('domain_index.json')

def load_origin_index():
    return load_json('origin_index.json')

def load_reviews_index():
    return load_json('reviews_index.json')

def load_title_index():
    return load_json('title_index.json')

def load_origin_synonyms():
    return load_json('origin_synonyms.json')
