import os
import requests
import uuid
import datetime
from typing import List, Set, Dict, Any, Optional, Union
from flask_login import current_user
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from . import db
from .models import ImgSet, Recipe
from flask import url_for, current_app, jsonify, request
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from . import mail

# helper function for 'retrieve_product_labels()'
def load_whitelist() -> Set[str]:
    """Load the whitelist of recognized grocery items from a file.
    
    Reads a file containing one grocery item name per line, and returns
    a set of these items for filtering product tags.
    
    Returns:
        Set[str]: A set of valid grocery item names from the whitelist.
    """
    whitelist_file = os.getenv('WHITELIST_FILE')
    with open(whitelist_file, 'r') as file:
        return set(line.strip() for line in file)

def retrieve_product_labels(path_to_imgset_dir: str) -> List[str]:
    """Process uploaded images via Azure Vision API and extract product labels.
    
    This function analyzes images in the specified directory using Azure Computer Vision API,
    extracts product tags, filters them against a predefined whitelist, and saves the results
    to the database.
    
    Args:
        path_to_imgset_dir: Path to the directory containing the uploaded images.
        
    Returns:
        List[str]: A list of recognized product names from the images.
    """
    # Client for Azure Vision API
    endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    key = os.getenv('AZURE_COMPUTERVISION_KEY')
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    # Retrieve 'product.tags'
    products: Set[str] = set()
    for filename in os.listdir(path_to_imgset_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(path_to_imgset_dir, filename)

            with open(file_path, 'rb') as image_file:
                analysis = client.tag_image_in_stream(image_file)

            for tag in analysis.tags:
                # Keep only 'single_word_products'
                if ' ' not in tag.name:
                    products.add(tag.name)
    
    # Filter out 'product.tags' against the whitelist (of a 100 predefined grocery items)
    whitelist = load_whitelist()
    filtered_products: List[str] = [product for product in products if product in whitelist]

    # Add recognized 'product.tags' to DB as CSV
    img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
    if img_set:
        img_set.products = ', '.join(filtered_products)
        db.session.commit()

    return filtered_products

def retrieve_recipes_by_ingredients(products: List[str]) -> List[Dict[str, Any]]:
    """Fetch recipe recommendations based on a list of ingredients using Spoonacular API.
    
    This function calls the Spoonacular API to find recipes that match the provided
    ingredients, enriches the data with detailed recipe information, and stores
    the results in the database.
    
    Args:
        products: A list of ingredient names to search for recipes.
        
    Returns:
        List[Dict[str, Any]]: A list of recipe dictionaries containing detailed recipe information.
            Each dictionary includes fields like id, title, image, ingredients, instructions, etc.
            If an error occurs, returns a single item with an error message.
    """
    product_string = ','.join(products)
    
    # Create Spoonacular API Endpoint
    api_key = os.getenv('SPOONACULAR_API_KEY')
    headers = {'Content-Type': 'application/json'}
    # Initial endpoint to get recipes based on ingredients
    endpoint = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={product_string}&number=5&apiKey={api_key}'
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        # Store the full recipe data
        data = response.json()
        
        # Create a list to store enriched recipe data
        enriched_recipes: List[Dict[str, Any]] = []
        
        # Get more details for each recipe
        for recipe_basic in data:
            recipe_id = recipe_basic['id']
            # Get detailed recipe information including instructions
            info_endpoint = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}'
            info_response = requests.get(info_endpoint, headers=headers)
            
            if info_response.status_code == 200:
                recipe_info = info_response.json()
                # Combine basic and detailed info
                recipe_data: Dict[str, Any] = {
                    'id': recipe_id,
                    'title': recipe_basic['title'],
                    'image': recipe_basic['image'],
                    'usedIngredients': recipe_basic['usedIngredients'],
                    'missedIngredients': recipe_basic['missedIngredients'],
                    'readyInMinutes': recipe_info.get('readyInMinutes', 0),
                    'servings': recipe_info.get('servings', 0),
                    'sourceUrl': recipe_info.get('sourceUrl', ''),
                    'summary': recipe_info.get('summary', ''),
                    'instructions': recipe_info.get('instructions', ''),
                    'analyzedInstructions': recipe_info.get('analyzedInstructions', []),
                    'difficulty': 'Easy' if recipe_info.get('readyInMinutes', 30) < 30 else 'Medium' 
                                if recipe_info.get('readyInMinutes', 60) < 60 else 'Hard'
                }
                enriched_recipes.append(recipe_data)
        
        # Store each recipe as a global entry if not already present
        for recipe in enriched_recipes:
            if not Recipe.query.filter_by(spoonacular_id=str(recipe['id'])).first():
                recipe_entry = Recipe(
                    spoonacular_id=str(recipe['id']),
                    recipe_data=recipe
                )
                db.session.add(recipe_entry)
        db.session.commit()
        
        return enriched_recipes
    else:
        return [{"title": "Error fetching recipes, please try again later.", "error": True}]


def fetch_user_products() -> List[str]:
    """Retrieve all unique products associated with the current user.
    
    This function fetches all ImgSet entries for the current user, extracts the
    products from each entry, and returns a deduplicated list of product names.
    
    Returns:
        List[str]: A list of unique product names associated with the current user.
    """
    imgsets = ImgSet.query.filter_by(user_id=current_user.id).all()

    products_with_duplicates: List[str] = []
    for imgset in imgsets:
        if imgset.products:
            products_with_duplicates.extend([product.strip() for product in imgset.products.split(',')])

    return list(set(products_with_duplicates))

def fetch_all_recipes() -> List[Dict[str, Any]]:
    """
    Retrieve all global recipes in the database.

    Returns:
        List[Dict[str, Any]]: A list of all recipe dictionaries in the database.
    """
    recipe_entries = Recipe.query.all()
    all_recipes: List[Dict[str, Any]] = []
    for entry in recipe_entries:
        if entry.recipe_data:
            all_recipes.append(entry.recipe_data)
    return all_recipes


# Email verification functions
def generate_verification_token(email):
    """Generate a secure token for email verification"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECRET_KEY'])

def verify_token(token, expiration=86400):  # 24 hours in seconds
    """Verify the token is valid and not expired"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECRET_KEY'],
            max_age=expiration
        )
        return email
    except:
        return None

def calculate_token_expiry(hours=None):
    """Calculate token expiration timestamp"""
    if hours is None:
        hours = int(current_app.config.get('VERIFICATION_TOKEN_EXPIRY', 24))
    return datetime.datetime.now() + datetime.timedelta(hours=hours)

def verify_recaptcha(recaptcha_response):
    """
    Verify reCAPTCHA v2 response with Google's API
    
    Args:
        recaptcha_response (str): The reCAPTCHA response token from the client
        
    Returns:
        bool: True if verification is successful, False otherwise
    """
    if not recaptcha_response:
        return False
        
    data = {
        'secret': current_app.config['RECAPTCHA_SECRET_KEY'],
        'response': recaptcha_response,
        'remoteip': request.remote_addr  # Optional: include user's IP for additional security
    }
    
    try:
        response = requests.post(
            current_app.config['RECAPTCHA_VERIFY_URL'],
            data=data,
            timeout=5  # Add timeout to prevent hanging
        )
        result = response.json()
        
        # Log the response for debugging (remove in production or reduce to debug level)
        current_app.logger.debug(f"reCAPTCHA verification response: {result}")
        
        # For v2, we only need to check the 'success' field
        return result.get('success', False)
        
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"reCAPTCHA verification request failed: {str(e)}")
        # In case of network errors, you might want to fail open or closed based on your security requirements
        return False  # Failing closed for security

def send_verification_email(user):
    """Send verification email to user"""
    token = generate_verification_token(user.email)
    
    # Store token and expiration time in user record
    user.verification_token = token
    user.token_expiration = calculate_token_expiry()
    db.session.commit()
    
    # Create verification URL
    verify_url = url_for('verify_email', token=token, _external=True)
    
    # Create and send email
    subject = "Please Verify Your Email Address"
    body = f"""Hello,

Thank you for registering with Recipe Hub. To verify your email address, please click on the link below:

{verify_url}

This link will expire in {current_app.config.get('VERIFICATION_TOKEN_EXPIRY', 24)} hours.

If you did not register for this service, please ignore this email.

Regards,
Recipe Hub Team
"""
    
    msg = Message(subject, recipients=[user.email], body=body)
    mail.send(msg)
    
    return True

def reset_password(user):
    """
    Send a password reset email to the user with a secure token link.
    Returns True if the email was sent successfully, False otherwise.
    """
    try:
        # Generate a secure token for password reset
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(user.email, salt='password-reset-salt')
        
        # Store token and expiration in user record (for extra security)
        user.verification_token = token
        user.token_expiration = calculate_token_expiry(hours=1)  # 1 hour expiry for reset
        db.session.commit()

        # Create password reset URL
        reset_url = url_for('password_reset', token=token, _external=True)
        
        # Compose and send email
        subject = "Reset Your Password"
        body = f"""Hello,

You requested a password reset for your Recipe Hub account. To reset your password, click the link below:

{reset_url}

This link will expire in 1 hour. If you did not request a password reset, please ignore this email.

Regards,
Recipe Hub Team
"""
        msg = Message(subject, recipients=[user.email], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {e}")
        return False
