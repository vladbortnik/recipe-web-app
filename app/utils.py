import os
import requests
from datetime import datetime
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from . import db
from .models import ImgSet, Recipe
from . import logger, console

### DEBUG ####################
# from pprint import pprint as pp
##############################

# helper function
def load_whitelist():
    whitelist_file = os.getenv('WHITELIST_FILE')
    with open(whitelist_file, 'r') as file:
        return set(line.strip() for line in file)



def process_imgset(path_to_imgset_dir):
    endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    key = os.getenv('AZURE_COMPUTERVISION_KEY')

    # Create a client for Azure Vision API
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    # Create a set of products items 
    # lookup time == O(1)
    whitelist = load_whitelist()

    # Retrive list of products (Azure Vision API tags) 
    # from images uploaded in one shot (wtforms.fields.MultipleFileField)
    detected_products = set()
    for filename in os.listdir(path_to_imgset_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(path_to_imgset_dir, filename)

            with open(file_path, 'rb') as image_file:
                analysis = client.tag_image_in_stream(image_file)

            for tag in analysis.tags:
                # Filter out tags with more than one word
                if ' ' not in tag.name:
                    detected_products.add(tag.name)
    
    # Filter out products against whitelist
    filtered_products = [product for product in detected_products if product in whitelist]

    filtered_products_str = ', '.join(filtered_products)

    # Add recognized products to ImgSet Table
    img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
    if img_set:
        img_set.products = filtered_products_str
        db.session.commit()




def get_recipe(products):
    api_key = os.getenv('SPOONACULAR_API_KEY')
    headers = {
        'Content-Type': 'application/json',
    }

    product_string = ','.join(products)
    endpoint = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={product_string}&number=5&apiKey={api_key}'

    # console.print(f'===>>>   utils::get_recipe::product_string == {product_string}   <<<===')
    # console.print(f'===>>>   utils::get_recipe::endpoint == {endpoint}   <<<===')
    
    response = requests.get(endpoint, headers=headers)

    # console.print(f'===>>>   utils::get_recipe::response.status_code == {response.status_code}   <<<===')
    # console.print(f'===>>>   utils::get_recipe::response.json() == {response.json()}   <<<===')

    logger.debug(f"===>>>   utils::get_recipe::response.status_code == {response.status_code}   <<<===")
    logger.debug(f"===>>>   utils::get_recipe::response.json() == {response.json()}   <<<===")
    
    if response.status_code == 200:
        data = response.json()
        recipes = [recipe['title'] for recipe in data]

        
        
        # Assuming every user has a unique ImgSet ID
        imgset_id = ImgSet.query.first().id 
        new_recipe = Recipe(set_id=imgset_id, recipe=','.join(recipes), date_created=datetime.now())
        db.session.add(new_recipe)
        db.session.commit()
        
        return recipes
    else:
        return ["Error fetching recipes, please try again later."]


    ##### DEBUG ######################
    # pp(f'/utils::get_recipe::response == {response}')
    ##################################

    ##### DEBUG ######################
    # pp(f'__PP__ ==>> /utils::get_recipe::product_string == {product_string}')
    # pp(f'__PP__ ==>> /utils::get_recipe::endpoint == {endpoint}')

    # Log messages with variable data
    # logger.debug(f"[bold red]__LOGGER:Debug__ ==>> /utils::get_recipe::product_string == {product_string}[/bold red]")
    # logger.debug(f"[bold blue]__LOGGER:Debug__ ==>> /utils::get_recipe::endpoint ==[/bold blue] {endpoint}")
    # logger.warning("[green]This is a === GREEN === warning message[/green]")
    
    # console.print("[bold red]This is red and bold[/bold red]")

    # logger.debug(f"__EXAMPLE 'debug' => product_string: {product_string}__")
    # logger.info(f"__User {headers} made a request to {headers}__")
    # logger.warning("__EXAMPLE 'warning' => This is a warning message__")
    # logger.error(f"__EXAMPLE 'error' => Received error status {endpoint} from the server__")
    # logger.critical("__EXAMPLE 'critical' => Critical issue occurred__")
    ##################################
