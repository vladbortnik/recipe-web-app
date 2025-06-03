import os
import requests
from flask_login import current_user
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from . import db
from .models import ImgSet, Recipe
import uuid, os
import datetime
from flask import url_for, current_app, jsonify, request
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import requests
from . import mail

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
    # Initial endpoint to get recipes based on ingredients
    endpoint = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={product_string}&number=5&apiKey={api_key}'
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        # Store the full recipe data
        data = response.json()
        
        # For backwards compatibility, still store recipe titles as comma-separated string
        recipe_titles = [recipe['title'] for recipe in data]
        
        # Create a list to store enriched recipe data
        enriched_recipes = []
        
        # Get more details for each recipe
        for recipe_basic in data:
            recipe_id = recipe_basic['id']
            # Get detailed recipe information including instructions
            info_endpoint = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}'
            info_response = requests.get(info_endpoint, headers=headers)
            
            if info_response.status_code == 200:
                recipe_info = info_response.json()
                # Combine basic and detailed info
                recipe_data = {
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
        
        # Store both the legacy format and new detailed format
        recipe_entry = Recipe(
            user_id=current_user.id,
            recipes=','.join(recipe_titles),
            recipe_data=enriched_recipes
        )
        db.session.add(recipe_entry)
        db.session.commit()
        
        return enriched_recipes
    else:
        return [{"title": "Error fetching recipes, please try again later.", "error": True}]


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
    recipe_entries = Recipe.query.filter_by(user_id=current_user.id).all()
    
    # First try to get detailed recipe data from JSON field
    all_recipes = []
    recipe_ids_seen = set()  # Track recipe IDs to avoid duplicates
    
    for entry in recipe_entries:
        if entry.recipe_data:  # Use the new JSON data field if available
            for recipe in entry.recipe_data:
                # Skip recipes we've already seen (avoid duplicates)
                if recipe.get('id') and recipe.get('id') in recipe_ids_seen:
                    continue
                    
                # Add this recipe ID to our tracking set
                if recipe.get('id'):
                    recipe_ids_seen.add(recipe.get('id'))
                    
                all_recipes.append(recipe)
        elif entry.recipes:  # Fall back to legacy data if no JSON data
            # For legacy entries, create a simple format matching the new structure
            for title in [r.strip() for r in entry.recipes.split(',')]:
                # Only add if we don't already have a recipe with this title
                if not any(r.get('title') == title for r in all_recipes):
                    all_recipes.append({
                        'title': title,
                        'readyInMinutes': 30,  # Default values
                        'difficulty': 'Easy',
                        'legacy': True  # Mark as legacy data
                    })
    
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
        
        # Store token and expiration in user record (optional, for extra security)
        user.verification_token = token
        user.token_expiration = calculate_token_expiry(hours=1)  # e.g., 1 hour expiry for reset
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
