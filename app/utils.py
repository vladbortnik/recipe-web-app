import os
import requests
from datetime import datetime
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from . import db
from .models import ImgSet, Recipe
from . import logger, console

### DEBUG ####################
from pprint import pprint as pp
##############################

def process_imgset(path_to_imgset_dir):
    endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    key = os.getenv('AZURE_COMPUTERVISION_KEY')

    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    detected_products = []

    for filename in os.listdir(path_to_imgset_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(path_to_imgset_dir, filename)

            with open(file_path, 'rb') as image_file:
                analysis = client.tag_image_in_stream(image_file)

            for tag in analysis.tags:
                detected_products.append(tag.name)

    detected_products_str = ', '.join(set(detected_products))

    # Update the ImgSet entry in the database
    img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
    if img_set:
        img_set.products = detected_products_str
        db.session.commit()




def get_recipe(products):
    api_key = os.getenv('SPOONACULAR_API_KEY')
    headers = {
        'Content-Type': 'application/json',
    }

    product_string = ','.join(products)
    endpoint = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={product_string}&number=5&apiKey={api_key}'

    console.print(f'===>>>   utils::get_recipe::product_string == {product_string}   <<<===')
    console.print(f'===>>>   utils::get_recipe::endpoint == {endpoint}   <<<===')

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
    
    response = requests.get(endpoint, headers=headers)

    console.print(f'===>>>   utils::get_recipe::response.status_code == {response.status_code}   <<<===')
    console.print(f'===>>>   utils::get_recipe::response.json() == {response.json()}   <<<===')

    logger.debug(f"[bold blue]===>>>   utils::get_recipe::response.status_code == {response.status_code}   <<<===[/bold blue]")
    logger.debug(f"[bold red]===>>>   utils::get_recipe::response.json() == {response.json()}   <<<===[/bold red]")

    ##### DEBUG ######################
    # pp(f'/utils::get_recipe::response == {response}')
    ##################################
    
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









#     key = os.getenv('AZURE_COMPUTERVISION_KEY')
#     endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')

# def process_imgset(path_to_imgset_dir):
#     client = vision.ImageAnnotatorClient()

#     detected_products = []

#     for filename in os.listdir(path_to_imgset_dir):
#         if filename.endswith(('.jpg', '.jpeg', '.png')):
#             file_path = os.path.join(path_to_imgset_dir, filename)

#             with open(file_path, 'rb') as image_file:
#                 content = image_file.read()

#             image = vision.Image(content=content)
#             response = client.label_detection(image=image)
            
#             labels = response.label_annotations

#             for label in labels:
#                 detected_products.append(label.description)

#             if response.error.message:
#                 raise Exception(f'{response.error.message}')
    
#     detected_products_str = ', '.join(set(detected_products))

#     # Update the ImgSet entry in the database
#     img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
#     if img_set:
#         img_set.products = detected_products_str
#         db.session.commit()
