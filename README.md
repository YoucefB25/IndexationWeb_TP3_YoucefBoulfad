Pour ce TP j'ai procédé en plusieurs étapes : 

1) Constitution d'un fichier unique de 132 couples produit-variant, avec pour chaque couple : URL, titre complet, variant, description complète, prix (en $), marque (brand), nombre de reviews, note moyenne, dernière note et pays d'origine. Comme ceci :

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

Pour constituer ce fichier, je pars du fichier description_index.json, dont tous les URL pointent vers des pages de couples produit-variant. J'extrais tous les URL uniques de ce fichier. Puis, à partir de ces URLs j'accède aux pages HTML et je scrappe le titre, le variant, la description, le prix et la marque. 

Ensuite j'utilise le fichier reviews_index.json pour extraire total_reviews, mean_mark et last_rating, en me basant sur l'URL commune. J'en fais de même pour "country_of_origin" à partir du fichier origin_index.json. 

Je stocke ensuite mon fichier constitué, sous le nom "final_products.json". Il me servira pour mes recherches. Sans avoir besoin d'utiliser les index fournis au départ (et qui sont dans le dossier "initial_index_files"). 

Toutes ces étapes sont effectuées via des fonctions qui sont dans le module extraction.py. 