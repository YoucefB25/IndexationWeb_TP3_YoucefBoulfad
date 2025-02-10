For this TP I have followed many steps : 

1) Product file constitution : product_extraction.py --> extracted_products.json

First, instead of using all the provided indexes (the six json files) for each search, I decide to create a single json file with all the relevant information on each product that the file "description_index.json" points to through an URL. The file will look like this, containing all the products : 
{
        "url": "https://web-scraping.dev/product/24?variant=pink-medium",
        "title": "Cat-Ear Beanie",
        "variant": "pink-medium",
        "description": "Add a touch of whimsy to your winter wardrobe with our Cat Ear Beanie. Crafted from warm, soft material, this cozy beanie features adorable cat ears that stand out, making it the perfect accessory for cat lovers and fashion enthusiasts alike. Available in a variety of colors like black, grey, white, pink, and blue, this beanie not only keeps you warm but also adds a playful element to your outfit. Wear it for a casual day out, or make it your go-to accessory for those chilly evening walks. Stay warm, look cute, and let your playful side shine with our Cat Ear Beanie.",
        "price ($)": 14.99,
        "brand": "CatCozies",
        "total_reviews": 5,
        "mean_mark": 4.2,
        "last_rating": 4,
        "country_of_origin": "usa"
    },

I choose the file "description_index.json" to parse the URLs of products, because the presence of at least one word of description is a characteristic of all the products, so they are all pointed to by "description_index.json at least once. Of course there are many duplicates, because descriptions have many words, and many words point to the same URLs. I remove duplicated URLs, and get 132 unique URLs of products. From each of these URLs I then scrap the title, the variant, the description, the price, and the brand, of the product (a product being a combination of a title and a variant, for example : title "Dragon Energy Potion", variant "Pack of six"), as can be seen above. 

Then I use the reviews_index.json file to extract total_reviews, mean_mark et last_rating, by using the URLs present in that file, which serves for the jointure. I do the same for "country_of_origin" from the origin_index.json file. 

I later discover that many different product URLs actually point to the same products : same title, same variant, same price, same country of origin, same brand, but with different URLs, like here https://web-scraping.dev/product/1 and here https://web-scraping.dev/product/13. I treat these as duplicates and finally get 46 unique products (unique title-variant associations) out of 132 unique URLs of products. 

I then store the constituted file under the name "extracted_products.json". It will be used later for tokenization, embedding, and search. 

On the other hand, the initial index files used for this process are stored in the folder "initial_index_files", and not used for the rest of the code. 

2) Tokenization of the extracted_products file : extracted_products.json --> product_tokenization.py --> tokenized_products.json : 

Here I use lemmatization, stop words and synonyms, by using libraries from the nltk package. I tokenize the text fields of the 46 unique products from the extracted_products.json file. By "text fields" I mean title, variant, description, brand and country of origin. Numerical values (price, total_reviews, mean_mark and last_rating) are obviously not tokenized, but will serve later as search criteria. URLs are not tokenized either. 

However, we can notice here that the field "description" will always produce much more tokens than the other fields, being much longer, despite being "less important" for a search than fields like "title", "variant", "brand" and "country of origin", which have a higher product-characterization power with less words. To deal with this issue, I choose to duplicate the tokens from those fields. Hence, the tokenization output for a product contains : 1 * the tokens from "description" + 10 * the tokens from "title" + 10 * the tokens from "variant" + 10 * the tokens from "brand" + 10 * the tokens from "country of origin". I also add synonyms for the "title" tokens and the "country of origin" tokens, which I duplicate 5 times (being more cautious with synonyms than with original tokens).

All those steps can be found on the file product_tokenization.py. The output of this process is tokenized_products.json. 

3) Computing embeddings for the tokenized products : tokenized_products.json --> product_embedding.py --> embeddings_of_products.json

This process is carried out in the perspective of performing semantic searches, based on the meanings of queries rather than simply on their lexical structure. This approach will complement the lexical searches, which can be carried out simply by using the tokens. 

To compute embeddings for each product I use, from the SentenceTransformer library, the NLP model "multi-qa-MiniLM-L6-cos-v1". It returns for each product's pack of tokens 384 numerical values, corresponding to dimensions on which those tokens are projected, and which capture their meaning. 

For this vectorization process I choose to use the already produced tokens (tokenized_products.json) rather than the products file (extracted_products.json)