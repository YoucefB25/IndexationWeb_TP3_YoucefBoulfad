import os
import json
import requests
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

# Step 1: Extract unique product URLs
urls = set()
for category in description_data.values():  # Iterate through categories
    urls.update(category.keys())  # Collect URLs

# Ensure only valid URLs (starting with "http")
urls = {url for url in urls if url.startswith("http")}
print(f"✅ Found {len(urls)} valid product URLs.")

# Function to fetch HTML content
def fetch_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text  # Return HTML content
        else:
            print(f"⚠️ Failed to fetch {url} (Status: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

# Function to parse product details from HTML
def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract Title
    title_tag = soup.find("title")
    title = title_tag.text.replace("web-scraping.dev product ", "").strip() if title_tag else "Unknown"

    # Extract Variant
    variant_tag = soup.find("button", class_="add-to-cart")
    variant = variant_tag["data-variant-id"] if variant_tag and "data-variant-id" in variant_tag.attrs else "Unknown"

    # Extract Description
    description_tag = soup.find("p", class_="product-description")
    description = description_tag.text.strip() if description_tag else "No description"

    # Extract Price and convert to float
    price_tag = soup.find("span", class_="product-price")
    if price_tag:
        price_text = price_tag.text.strip().replace("$", "").replace(",", "")
        try:
            price = float(price_text)
        except ValueError:
            price = "Unknown"
    else:
        price = "Unknown"

    # Extract Brand
    brand = "Unknown"
    feature_labels = soup.find_all("td", class_="feature-label")
    for label in feature_labels:
        if label.text.strip().lower() == "brand":
            brand_value = label.find_next_sibling("td", class_="feature-value")
            if brand_value:
                brand = brand_value.text.strip()
            break

    return title, variant, description, price, brand

# Step 2: Visit each URL, scrape details, and combine data
product_list = []
for url in urls:
    print(f"🔍 Scraping: {url}")

    html_content = fetch_html(url)
    if not html_content:
        print(f"⚠️ Skipping {url} (No HTML content)")
        continue  # Skip if no content

    # Parse HTML
    title, variant, description, price, brand = parse_html(html_content)

    # Get Review Data
    review_info = reviews_data.get(url, {"total_reviews": 0, "mean_mark": 0, "last_rating": 0})

    # Get Correct Country of Origin
    country_of_origin = "Unknown"
    for country, country_urls in origin_data.items():
        if url in country_urls:
            country_of_origin = country
            break

    # Create Product Entry
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

    # Respectful scraping: Random delay between requests (to avoid being blocked)
    sleep(randint(1, 3))

# Step 3: Remove duplicates
unique_products = []
seen = set()
for product in product_list:
    key = (product["url"], product["title"], product["variant"], product["description"], product["price ($)"], product["brand"])
    if key not in seen:
        seen.add(key)
        unique_products.append(product)

# Step 4: Save results to JSON in the ROOT directory
OUTPUT_FILE = "final_products.json"  # Saved to root directory
with open(OUTPUT_FILE, "w") as f:
    json.dump(unique_products, f, indent=4)

print(f"✅ Extraction complete! Results saved in {OUTPUT_FILE}.")
