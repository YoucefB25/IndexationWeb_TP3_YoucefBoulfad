Student : Youcef Boulfrad, master SDDP-STD.

I implement this TP through several steps : 

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

Then I use the reviews_index.json file to extract total_reviews, mean_mark et last_rating, by using the URLs present in that file, which serve for the jointure. I do the same for "country_of_origin" from the origin_index.json file. 

I later discover that many different product URLs actually point to the same products : same title, same variant, same price, same country of origin, same brand, but with different URLs, like here https://web-scraping.dev/product/1 and here https://web-scraping.dev/product/13. I treat these as duplicates and finally get 46 unique products (unique title-variant associations) out of 132 unique URLs of products. 

I then store the constituted file under the name "extracted_products.json". It will be used later for tokenization, embedding, and search.

I also add a unique identifier to each of the 46 products, because I later discover that it's more practical when aggregating different search results containing the same products. 

On the other hand, the initial index files used for this process are stored in the folder "initial_index_files", and essentially not used for the rest of the code. 

2) Tokenization of the extracted_products file : extracted_products.json --> product_tokenization.py --> tokenized_products.json : 

Here I use lemmatization, stop words and synonyms, by using libraries from the nltk package. I tokenize the text fields of the 46 unique products from the extracted_products.json file. By "text fields" I mean title, variant, description, brand and country of origin. Numerical values (price, total_reviews, mean_mark and last_rating) are obviously not tokenized, but will serve later as search criteria. URLs are not tokenized either, nor IDs obivously. 

However, we can notice here that the field "description" will always produce much more tokens than the other fields, being much longer, despite being "less important" for a search than fields like "title", "variant", "brand" and "country of origin", which have a higher product-characterization power with less words. To deal with this issue, I choose to duplicate the tokens from those fields. Hence, the tokenization output for a product contains : 1 * the tokens from "description" + 10 * the tokens from "title" + 5 * the tokens from "variant" + 10 * the tokens from "brand" + 10 * the tokens from "country of origin". I also add synonyms for the "title" tokens and the "country of origin" tokens, which I duplicate 5 times (being more cautious with synonyms than with original tokens).

As for the country of origin specifically, I use two sources of synonyms : the WordNet library used also for title synonyms, and the origin_synonyms.json file provided for this TP. I check for duplicates between these two sources, and then I aggregate the country synonyms and get a unique synonym list per country, before duplicating it 5 times for the relevant products as described earlier. 

All those steps can be found on the file "product_tokenization.py". The output of this process is in "tokenized_products.json", that for each of the 46 products contains a bag of tokens, with no distinction between title tokens, country tokens, description tokens, etc, except for the fact that some are repeated multiple times (like title tokens *10 and title synonym tokens *5) to be given more weight during the searches. 

3) Computing embeddings for the tokenized products : tokenized_products.json --> product_embedding.py --> embeddings_of_products.json

This process is carried out in the perspective of performing semantic searches, based on the meanings of queries rather than simply on their lexical structure. This approach will complement the lexical searches, which can be carried out simply by using the tokens. 

To compute embeddings for each product I use, from the SentenceTransformer library, the NLP model "multi-qa-MiniLM-L6-cos-v1". It returns for each product's bag of tokens 384 numerical values, corresponding to dimensions on which those tokens are projected, and which capture their meaning. 

For this vectorization process I choose to use the already produced tokens (tokenized_products.json) rather than the products file itself(extracted_products.json), so that the embeddings will reflect the already duplicated tokens (for title, variant, brand and country of origin), allowing this adjustment to be taken into account when performing semantic searches, as much as for lexical searches. 

This process can be found in the "product_embedding.py" module, and its output in the "embeddings_of_products.json" file. 

4) Performing a lexical search : tokenized_products.json + search query --> lexical_search.py --> ranked results of lexical search

To perform a lexical search I first tokenize the query, using the same process as for the tokenization of products. This process uses the NLTK library, with lemmatization, stop words, and synonyms expansion. 

Once the query is tokenized, I first apply a hard filter to the tokenized products : if a product doesn't have at least one common token with the query, it is eliminated from the results. 

Then, for the remaining products, the Best Matching 25 model of ranking is used (from the rank_bm25 library) to compare the query tokens to all the tokens of these products, and give a score of similarity per product. 

This model gives scores of similarity based on TF (Term Frequency : query tokens frequency in the documents) and IDF (Inverse Document Frequency : query tokens scarcity in the documents).

I choose to normalize these scores to values between 0 and 1 (the top score being always 1), for comparability with the semantic search results, explained in the next section, which are also normalized between 0 and 1. 

5) Performing a semantic search : embeddings_of_products + search query --> semantic_search.py --> ranked results of semantic search

The purpose of this process is to perform a search based on semantic similarity and not textual matching. This can be useful when a query doesn't contain an explicit token of the searched product, like for example : walk (query) --> shoes (product). 

As this process isn't based on textual matching, I choose not to apply any hard filter to it, unlike the lexical search. So, for every query, all 46 products are given a semantic similarity score and ranked. 

Before ranking, the query is tokenized (like for lexical search) and then the tokens are embedded, projected into the same 384 dimensions as the products' tokens, with the same NLP model (multi-qa-MiniLM-L6-cos-v1).

A measure of similarity is then computed (cosine similarity : the cosine of the angle between the two vectors of embeddings) and the 46 products are given scores and ranked, regarding their semantic similarity with the query.

6) Performing a hybrid search : tokens and embeddings of products + query --> hybrid search (hybrid_search.py) --> hybrid score and ranking. 

As the name suggests, hybrid search is a search process where scores from the lexical and from the semantic searches are aggregated into a unique score. 

However, as the semantic search outputs rankings for 46 products while the lexical search applies a hard filter (and removes results where no token is shared between query and product), I have to impute the value 0 for lexical search scores of products that are removed because they share no token with the query. Hence I have 46 scores for each query from both the semantic and the lexical searches. 

In addition to these two seach scores, I choose to add a score from reviews (the score being a function of high marks, number of reviews and latest mark, with an output between 0 and 1) and a score from the price (the lower prices being higher in score, also between 0 and 1, as I presume the consumer wants to spend less money, as much as possible). 

I give then aggregation weights to the four scores (by default 0.4 for lexical search, 0.4 for semantic search, 0.1 for reviews and 0.1 for price), weights that can be changed, and the function outputs a hybrid search score and ranking for all 46 products and for any query. 

Of course, we can choose not to display all 46 products as results, but this is implemented in the main.py module. 

7) The main.py module : queries.json + tokenized_products.py + embeddings_of_products --> main.py --> search_results.json

This main.py module allows to test many queries from a json file (queries.json) and outputs a json file with the rankings of products for each query. 

It simply calls the hybrid_search method, but on multiple queries instead of just one. And it allows to re-parametrize the weights of the lexical, semantic, price and reviews score; and to choose how many results to keep per query for the output, the default being set to 10 results per query (instead of 46).


TEST RESULTS

For the basic search modules (lexical_search.py, semantic_search.py, hybrid_search.py) : 

I use the same query for all three, for consistency, the query is "red energy drink". All three functions give the same first four results ("red energy potion" and "dark red energy potion" in variants "one" and "six-pack"). These are good results. The next results are non-red energy potions. 

Then, as expected, the lexical search gives only 13 results, as it filters out products that have no common token with the query (hard filter) before calculating similarity scores; and the semantic search gives 46 results as expected. The hybrid search imputes the value of 0 for lexical search score for products without a lexical search score, and returns 46 results, as expected. So far so good. 

For the main.py module : 

I keep the default weights (lexical 0.4, semantic 0.4, price 0.1, reviews 0.1) for my test and see the results. I also keep the default parameter of 10 stored results per query.

First, I decide to test some queries for lexical similarity.

For example, I test "I love chocodelight", chocodelight being a brand, present in many products (and we have seen that the brand tokens are duplicated 10 times in each product's token bag). Result : all the first six results are of the brand "ChocoDelight".

As another lexical similarity test, I use "what are the most affordable shoes?", as many products have the token "shoes" explicitely in their title. Result : the first four results all contain the word "shoes", and the next six contain synonyms or close parents of shoes (sneakers), maybe thanks to the use of synonyms among tokens and maybe thanks the use of semantic search (as the meanings are close). 

Second, I test for semantic similarity. I use a query like "walk" (not an explicit token in any product). Result : all the 10 results are about shoes, boots and sneakers. 

For the query "bananas" I get chocolate for the first six results, then cat-ear beanies for the four next. All of these results have 0 score for lexical similarity (which is normal, since no product has the token "banana") but their semantic similarity scores are high since chocolate and banana are both foods; and beanies might have a connection to the concept of banana (maybe in a metaphorical sense). 

For the query "sport" I get "running shoes" and "hiking boots" for eight out of the first nine results, and "energy potion" for one. The last result (number 10) seems irrelevant to sport (high heels sandals). These results suggest that the semantic search works fine and gets good results, though not perfect, despite weighing only 40% of the output score. 

Third, I test for the efficiency of the price and reviews criteria, despite weighing only 20% of the total score. For this I perform a "vanilla" query : "energy potion" (there are a lot of energy potions among the products). I get ten energy potion results. And indeed the first two have high price and review scores (cheap and well reviewed), but the next ones not so much. This is probably because of the low weight of these criteria. 

I change the weights in the main.py module to (lexical 0.25, semantic 0.25, price 0.25, reviews 0.25), I perform the same search ("energy potion"). Results : it's better, though not optimal (for this query), but the difference is stark for other queries like "sport" where indeed the cheapest and best reviewed results appear first (energy potions become better ranked than running shoes or hiking boots, as they are cheaper).

I go back to the default weights. 

Finally I test a search using a synonym of a country (to see if synonym tokenization is efficient). The query is "I'm American". Result : all ten results display products from the USA. Good. 

Thank you for reading ! 