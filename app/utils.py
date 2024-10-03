import os
import requests
from flask_login import current_user
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from . import db
from .models import ImgSet, Recipe

# helper function for 'retrieve_product_labels()'
def load_whitelist():
    whitelist_file = os.getenv('WHITELIST_FILE')
    with open(whitelist_file, 'r') as file:
        return set(line.strip() for line in file)

# Process uploaded images via Azure Vision API
def retrieve_product_labels(path_to_imgset_dir):
    # Client for Azure Vision API
    endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    key = os.getenv('AZURE_COMPUTERVISION_KEY')
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    # Retrieve 'product.tags'
    products = set()
    for filename in os.listdir(path_to_imgset_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(path_to_imgset_dir, filename)

            with open(file_path, 'rb') as image_file:
                analysis = client.tag_image_in_stream(image_file)

            for tag in analysis.tags:
                # Keep only 'single_word_products'
                if ' ' not in tag.name:
                    products.add(tag.name)
    
    # Filter out 'product.tags' against the whitelist (of a 100 predifined grocery items)
    whitelist = load_whitelist()
    products = [product for product in products if product in whitelist]

    # Add recognized 'product.tags' to DB as CSV
    img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
    if img_set:
        img_set.products = ', '.join(products)
        db.session.commit()

    return list(products)

# Obtain recipes via the Spoonacular API
def retrieve_recipes_by_ingredients(products):
    product_string = ','.join(products)
    
    # Create Spoonacular API Endpoint
    api_key = os.getenv('SPOONACULAR_API_KEY')
    headers = {'Content-Type': 'application/json'}
    endpoint = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={product_string}&number=5&apiKey={api_key}'
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        ### For SIMPLICITY this APP stores ONLY "recipe[titles]"
        data = response.json()
        recipes = [recipe['title'] for recipe in data]

        recipe = Recipe(user_id=current_user.id, recipes=','.join(recipes))
        db.session.add(recipe)
        db.session.commit()
    else:
        return ["Error fetching recipes, please try again later."]

    return list(recipes)

# Obtain ALL the 'products' for CURR_USER from DB (less duplicates)
def fetch_user_products():
    imgsets = ImgSet.query.filter_by(user_id=current_user.id).all()

    products_with_duplicates = []
    for imgset in imgsets:
        if imgset.products:
            products_with_duplicates.extend([product.strip() for product in imgset.products.split(',')])

    return list(set(products_with_duplicates))

# Obtain ALL the 'recipes' for CURR_USER from DB (less duplicates)
def fetch_user_recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()

    recipes_with_duplicates = []
    for recipe in recipes:
        if recipe.recipes:
            recipes_with_duplicates.extend(recipe.strip() for recipe in recipe.recipes.split(','))
    
    return list(set(recipes_with_duplicates))
