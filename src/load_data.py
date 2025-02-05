import os
import json

# Obtenir le chemin du dossier data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Remonte au projet
DATA_DIR = os.path.join(BASE_DIR, "data")  # Dossier data


def load_description_index():
    """Charge et reformate `description_index.json` pour en faire une liste de documents exploitables."""
    filepath = os.path.join(DATA_DIR, "description_index.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: {filepath} not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")

    # 🔍 On reformate si le fichier contient un dictionnaire imbriqué
    reconstructed_data = []
    if isinstance(data, dict):
        for keyword, url_dict in data.items():
            if isinstance(url_dict, dict):  # Vérifier que ce sont bien des sous-dictionnaires
                for url, values in url_dict.items():
                    if isinstance(values, list):  # Vérifier que la valeur est bien une liste
                        reconstructed_data.append({
                            "id": hash(url),  # 🔥 Ajouter un ID unique basé sur l'URL
                            "title": f"Product related to '{keyword}' at {url}",
                            "description": f"Found in keyword '{keyword}' with values {values}",
                            "url": url
                        })

    print(f"DEBUG: {len(reconstructed_data)} documents reconstruits")
    return reconstructed_data



def load_origin_synonyms():
    """Charge `origin_synonyms.json` sans modification, car c'est déjà un dictionnaire utilisable."""
    filepath = os.path.join(DATA_DIR, "origin_synonyms.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: origin_synonyms.json not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")
    return data  # On retourne directement le dictionnaire


def load_origin_index():
    """Charge `origin_index.json`, qui est un simple dictionnaire {origine: [URLs]}"""
    filepath = os.path.join(DATA_DIR, "origin_index.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: origin_index.json not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")
    return data  # C'est déjà un dictionnaire


def load_reviews_index():
    """Charge `reviews_index.json`, qui associe des URLs à des notes et nombres de reviews."""
    filepath = os.path.join(DATA_DIR, "reviews_index.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: reviews_index.json not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")
    return data  # On retourne tel quel


def load_title_index():
    """Charge `title_index.json`, qui associe des mots-clés aux URLs de produits."""
    filepath = os.path.join(DATA_DIR, "title_index.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: title_index.json not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")
    return data  # C'est déjà un dictionnaire


def load_brand_index():
    """Charge `brand_index.json`."""
    filepath = os.path.join(DATA_DIR, "brand_index.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: brand_index.json not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")
    return data  # C'est déjà un dictionnaire


def load_domain_index():
    """Charge `domain_index.json`."""
    filepath = os.path.join(DATA_DIR, "domain_index.json")
    print(f"DEBUG: Chargement du fichier {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: domain_index.json not found!")

    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"DEBUG: JSON chargé avec succès, type: {type(data)}")
    return data  # C'est déjà un dictionnaire
