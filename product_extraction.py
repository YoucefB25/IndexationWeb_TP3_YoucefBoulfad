import os
import json
import requests
import hashlib
from bs4 import BeautifulSoup
from time import sleep
from random import randint

# Define file paths
DATA_DIR = "initial_index_files/"
DESCRIPTION_FILE = os.path.join(DATA_DIR, "description_index.json")
REVIEWS_FILE = os.path.join(DATA_DIR, "reviews_index.json")
ORIGIN_FILE = os.path.join(DATA_DIR, "origin_index.json")

# Load JSON files
with open(DESCRIPTION_FILE, "r") as f:
    description_data = json.load(f)

with open(REVIEWS_FILE, "r") as f:
    reviews_data = json.load(f)

with open(ORIGIN_FILE, "r") as f:
    origin_data = json.load(f)

# Extract unique product URLs
urls = set()
for category in description_data.values():
    urls.update(category.keys())

urls = {url for url in urls if url.startswith("http")}
print(f"✅ Found {len(urls)} valid product URLs.")

# Function to fetch and parse product details
def fetch_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        return response.text if response.status_code == 200 else None
    except requests.RequestException:
        return None

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title").text.replace("web-scraping.dev product ", "").strip() if soup.find("title") else "Unknown"
    variant_tag = soup.find("button", class_="add-to-cart")
    variant = variant_tag["data-variant-id"] if variant_tag and "data-variant-id" in variant_tag.attrs else "Unknown"
    description = soup.find("p", class_="product-description").text.strip() if soup.find("p", class_="product-description") else "No description"

    price_tag = soup.find("span", class_="product-price")
    try:
        price = float(price_tag.text.strip().replace("$", "").replace(",", "")) if price_tag else "Unknown"
    except ValueError:
        price = "Unknown"

    brand = "Unknown"
    for label in soup.find_all("td", class_="feature-label"):
        if label.text.strip().lower() == "brand":
            brand_value = label.find_next_sibling("td", class_="feature-value")
            brand = brand_value.text.strip() if brand_value else "Unknown"
            break

    return title, variant, description, price, brand

# Step 1: Scrape and process products (without assigning IDs)
product_list = []
for url in urls:
    print(f"🔍 Scraping: {url}")
    html_content = fetch_html(url)
    if not html_content:
        continue

    title, variant, description, price, brand = parse_html(html_content)
    review_info = reviews_data.get(url, {"total_reviews": 0, "mean_mark": 0, "last_rating": 0})
    country_of_origin = next((country for country, urls in origin_data.items() if url in urls), "Unknown")

    product_entry = {
        "url": url,
        "title": title,
        "variant": variant,
        "description": description,
        "price ($)": price,
        "brand": brand,
        "total_reviews": review_info["total_reviews"],
        "mean_mark": review_info["mean_mark"],
        "last_rating": review_info["last_rating"],
        "country_of_origin": country_of_origin,
    }
    product_list.append(product_entry)
    sleep(randint(1, 3))

# Step 2: Remove duplicates
unique_products = []
seen_products = set()

for product in product_list:
    key = (product["title"].lower(), product["variant"].lower(), product["price ($)"], product["brand"].lower())
    if key not in seen_products:
        seen_products.add(key)
        unique_products.append(product)

# Step 3: Assign unique IDs after removing duplicates
def generate_product_id(product):
    """Create a unique product ID using a hash of key attributes."""
    key = f"{product['title'].lower()}|{product['variant'].lower()}|{product['price ($)']}|{product['brand'].lower()}"
    return hashlib.md5(key.encode()).hexdigest()

for product in unique_products:
    product["product_id"] = generate_product_id(product)  # ✅ Assign unique ID

# Step 4: Save results
OUTPUT_FILE = "extracted_products.json"
with open(OUTPUT_FILE, "w") as f:
    json.dump(unique_products, f, indent=4)

print(f"✅ Extraction complete! {len(unique_products)} unique products saved in {OUTPUT_FILE}.")
