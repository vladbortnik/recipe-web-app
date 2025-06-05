import uuid, os
from flask import current_app as app
from flask import request, render_template, redirect, url_for, flash, session, abort, jsonify, Response
from flask_login import login_user, current_user, logout_user, login_required
from . import db, bcrypt
from .forms import LoginForm, SignupForm, UploadImageForm, PasswordResetForm, EmptyForm, ForgotPasswordForm
from .models import User, ImgSet, Recipe, Favorite
from .utils import retrieve_product_labels, retrieve_recipes_by_ingredients, fetch_user_products, fetch_all_recipes, send_verification_email, verify_token
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

@app.route('/')
def index() -> 'flask.Response':
    """Display the application's home page.
    
    Returns:
        Response: Renders the index.html template.
    """
    return render_template('index.html')

def get_favorites_count() -> int:
    """Helper function to count favorite recipes for the current user.
    
    Returns:
        int: Count of favorite recipes for the current user.
    """
    return Favorite.query.filter_by(user_id=current_user.id).count()

def get_favorite_spoonacular_ids() -> list[str]:
    """Helper function to get all spoonacular recipe IDs favorited by the current user.
    
    Returns:
        list[str]: List of spoonacular recipe IDs (as strings) that are favorited by the user.
    """
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return [str(fav.spoonacular_id) for fav in favorites if fav.spoonacular_id]


@app.route('/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite() -> 'flask.Response':
    """Toggle a recipe's favorite status for the current user.
    
    This endpoint handles adding or removing recipes from a user's favorites list.
    It expects a JSON payload with the Spoonacular recipe ID and optional recipe data.
    
    Request payload:
        {
            'spoonacular_id': '12345',  # Required: the Spoonacular recipe ID
            'recipe_data': {            # Optional: full recipe data if new
                'id': '12345',
                'title': 'Recipe Title',
                'image': 'image_url',
                ...
            }
        }
    
    Returns:
        flask.Response: JSON response with success status, action performed (added/removed),
        updated favorites count, and the Spoonacular ID that was toggled.
    """
    data = request.get_json()
    spoonacular_id = data.get('spoonacular_id')
    
    if not spoonacular_id:
        return jsonify({"success": False, "message": "Recipe ID is required"}), 400
    
    # Check if this spoonacular_id is already a favorite
    favorite_ids = get_favorite_spoonacular_ids()
    is_favorite = str(spoonacular_id) in favorite_ids
    
    if not is_favorite:
        # Need to add this recipe as a favorite
        # Find or create the recipe by spoonacular_id
        recipe_entry = Recipe.query.filter_by(spoonacular_id=spoonacular_id).first()
        if not recipe_entry and data.get('recipe_data'):
            new_recipe_data = data.get('recipe_data')
            recipe_entry = Recipe(
                spoonacular_id=str(spoonacular_id),
                recipe_data=new_recipe_data
            )
            db.session.add(recipe_entry)
            db.session.commit()
        if recipe_entry:
            fav = Favorite(user_id=current_user.id, spoonacular_id=spoonacular_id)
            db.session.add(fav)
            db.session.commit()
            return jsonify({
                "success": True,
                "action": "added",
                "favorites_count": get_favorites_count(),
                "spoonacular_id": spoonacular_id
            })
        else:
            return jsonify({"success": False, "message": "Could not add favorite - missing recipe data"}), 400
    else:
        # Need to remove this as a favorite
        fav = Favorite.query.filter_by(user_id=current_user.id, spoonacular_id=spoonacular_id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return jsonify({
                "success": True,
                "action": "removed",
                "favorites_count": get_favorites_count(),
                "spoonacular_id": spoonacular_id
            })
        else:
            return jsonify({"success": False, "message": "Favorite not found"}), 404


@app.route('/get-favorites', methods=['GET'])
@login_required
def get_favorites() -> 'flask.Response':
    """Get all favorite recipe IDs for the current user.
    
    This endpoint returns a JSON response containing an array of Spoonacular recipe IDs 
    that the current user has favorited.
    
    Returns:
        flask.Response: JSON response with favorite_spoonacular_ids array containing all favorited recipe IDs.
    """
    # Use our helper function to get the list of favorite IDs
    spoonacular_ids = get_favorite_spoonacular_ids()
    
    return jsonify({
        "success": True,
        "favorite_spoonacular_ids": spoonacular_ids,
        "favorites_count": len(spoonacular_ids)
    })

@app.route('/favorites')
@login_required
def favorites() -> 'flask.Response':
    """Show the dashboard with only favorite recipes.
    
    This route collects all recipes that the current user has favorited and displays them
    in the dashboard template. Each recipe is marked as a favorite for proper UI display.
    
    Returns:
        flask.Response: The dashboard template with only favorite recipes displayed.
    """
    # Get all favorite spoonacular IDs
    favorite_spoonacular_ids = get_favorite_spoonacular_ids()
    
    # Collect all global recipes that match the user's favorite spoonacular_ids
    recipes = []
    seen_ids = set()
    if favorite_spoonacular_ids:
        recipe_entries = Recipe.query.filter(Recipe.spoonacular_id.in_(favorite_spoonacular_ids)).all()
        for recipe_entry in recipe_entries:
            if recipe_entry and recipe_entry.recipe_data:
                recipe = recipe_entry.recipe_data.copy() if isinstance(recipe_entry.recipe_data, dict) else dict(recipe_entry.recipe_data)
                spoonacular_id = str(recipe.get('id'))
                if spoonacular_id in favorite_spoonacular_ids and spoonacular_id not in seen_ids:
                    recipe['is_favorite'] = True
                    recipes.append(recipe)
                    seen_ids.add(spoonacular_id)
    favorites_count = len(favorite_spoonacular_ids)
    return render_template('dashboard.html', 
                          recipes=recipes, 
                          products=None, 
                          favorites_count=favorites_count, 
                          show_favorites=True)

from . import limiter

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login() -> 'flask.Response':
    """Handle user login requests.
    
    This route displays the login form and processes login attempts.
    It validates the form submission, verifies reCAPTCHA, checks user credentials,
    and ensures email verification before allowing login.
    
    Returns:
        flask.Response: Redirects to index page on successful login, or returns the login template
        with appropriate flash messages on failure.
    """
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Verify reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA', 'danger')
            return render_template('login.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])
            
        from .utils import verify_recaptcha
        if not verify_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return render_template('login.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])
        
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not bcrypt.check_password_hash(user.password, form.password.data):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])
        # Check if user has verified their email
        if not user.is_verified:
            flash('Please verify your email address before logging in. Check your inbox for the verification link.', 'warning')
            session['unverified_user_id'] = user.id  
            return render_template('login.html', form=form, show_resend=True, user_id=user.id, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])
        login_user(user, remember=form.remember.data)
        flash('You have been logged in', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))

    return render_template('login.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup() -> 'flask.Response':
    """Handle user registration requests.
    
    This route displays the signup form and processes new user registrations.
    It validates the form submission, verifies reCAPTCHA, checks for existing accounts,
    and sends a verification email to new users.
    
    Returns:
        flask.Response: Redirects to login page with appropriate message after signup,
        or returns the signup template on GET requests or validation failure.
    """
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Verify reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA', 'danger')
            return render_template('signup.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])
            
        from .utils import verify_recaptcha
        if not verify_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return render_template('signup.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])
        
        email = form.email.data
        if email and User.query.filter_by(email=email).first() and not User.query.filter_by(email=email).first().is_verified:
            flash('Please verify your email address before logging in. Check your inbox for the verification link.', 'warning')
            return redirect(url_for('login'))
        elif email and User.query.filter_by(email=email).first() and User.query.filter_by(email=email).first().is_verified:
            flash('This email is already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(email=email, password=hashed_password, is_verified=False)
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user)
            
            flash('Your account has been created. Please check your email to verify your account.', 'success')
            return redirect(url_for('login'))
        
    return render_template('signup.html', form=form, recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'])

@app.route('/resend-verification/<int:user_id>')
def resend_verification(user_id: int) -> 'flask.Response':
    """Resend the email verification link to a user.
    
    This route handles requests to resend a verification email to the specified user.
    It checks if the user exists and whether they are already verified before sending.
    
    Args:
        user_id: The ID of the user requesting a new verification email.
    
    Returns:
        flask.Response: Redirects to login page with an appropriate flash message.
    """
    # Find user by ID
    user = User.query.get_or_404(user_id)
    
    # Don't resend if already verified
    if user.is_verified:
        flash('Your account is already verified. Please login.', 'info')
        return redirect(url_for('login'))
    
    # Send new verification email
    send_verification_email(user)
    
    flash('A new verification email has been sent to your email address.', 'success')
    return redirect(url_for('login'))

@app.route('/verify-email/<token>')
def verify_email(token: str) -> 'flask.Response':
    """Verify a user's email address using a token.
    
    This route validates the verification token, finds the corresponding user,
    and marks their email as verified if the token is valid.
    
    Args:
        token: The verification token from the email link.
    
    Returns:
        flask.Response: Redirects to login page with an appropriate flash message.
    """
    # Verify token is valid
    email = verify_token(token)
    if not email:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))
    
    # Check if already verified
    if user.is_verified:
        flash('Your account is already verified. Please login.', 'info')
        return redirect(url_for('login'))
    
    # Mark user as verified
    user.is_verified = True
    user.verification_token = None  # Clear the token
    user.token_expiration = None    # Clear the expiration
    db.session.commit()
    
    flash('Your email has been verified! You can now login.', 'success')
    return redirect(url_for('login'))

@app.route("/logout")
@login_required
def logout() -> 'flask.Response':
    """Log out the current user.
    
    This route ends the user's session and redirects them to the index page.
    
    Returns:
        flask.Response: Redirects to the index page with a logout confirmation message.
    """
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload() -> 'flask.Response':
    """Handle image uploads and product recognition.
    
    This route displays an image upload form and processes submitted images.
    It saves uploaded images to a unique folder, processes them with Azure Vision API
    to identify grocery products, and stores the results in the database.
    
    Returns:
        flask.Response: Redirects to dashboard with recognized products on successful upload,
        or returns the upload template for GET requests or failed submissions.
    """
    form = UploadImageForm()
    if form.validate_on_submit():
        if form.images.data:
            # Create a 'unique_folder' for a set of uploaded images
            unique_dir_name = str(uuid.uuid4())
            folder_path = os.path.join(os.getenv('UPLOAD_FOLDER'), str(current_user.id), unique_dir_name)
            os.makedirs(folder_path, exist_ok=True)

            # Save uploaded images to 'unique_folder'
            for file in form.images.data:
                filename = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)

            # Create an Entry in DB with the path to 'unique_folder'
            imgset = ImgSet(user_id=current_user.id, folder_path=folder_path)
            db.session.add(imgset)
            db.session.commit()

            # Process images in 'unique_folder' via Azure Vision API
            # ...then Add recognized 'product.tags' to (the same entry in) DB as CSV
            products = retrieve_product_labels(folder_path)
            
            # If no products found, redirect back to upload page
            if not products:
                flash('No products found in the uploaded images.', 'warning')
                return redirect(url_for('upload'))  # Redirect back to upload page

            # Pass recognized products to '/dashboard'
            session['products'] = products
            flash('Images uploaded and processed successfully.', 'success')
            return redirect(url_for('dashboard'))

    return render_template('upload.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard() -> 'flask.Response':
    """Display the user's dashboard with products and recipe suggestions.
    
    This route displays the user's ingredients and suggested recipes based on those
    ingredients. It also marks recipes that the user has favorited.
    
    Returns:
        flask.Response: The dashboard template with products, recipes, and favorite information.
    """
    if request.method == 'POST':
        # Get list of products a user checks on 'dashboard.html'
        # ...and obtain corresponding recipes via Spoonacular API
        products = request.form.getlist('product')
        if not products:
            flash('Please choose at least 1 product.', 'warning')
            return redirect(url_for('dashboard'))
        recipes = retrieve_recipes_by_ingredients(products)
        
    else:
        ## CASE 1: Redirected from '/upload'
        products = session.pop('products', default=None)
        if products:
            # Obtain corresponding recipes via Spoonacular API
            recipes = retrieve_recipes_by_ingredients(products)
        else:
            ## CASE 2: Default for "GET /dashboard"
            # Fetch ALL the 'products && recipes' for CURR_USER from DB
            products = fetch_user_products()
            recipes = fetch_all_recipes()
    
    # Get favorite spoonacular IDs
    favorite_spoonacular_ids = get_favorite_spoonacular_ids()
    
    # Mark recipes as favorites if their Spoonacular ID is in the favorites list
    if recipes:
        for recipe in recipes:
            if recipe.get('id') and str(recipe.get('id')) in favorite_spoonacular_ids:
                recipe['is_favorite'] = True
    
    # Count the number of distinct favorite recipes
    favorites_count = len(favorite_spoonacular_ids)
    
    return render_template('dashboard.html', products=products, recipes=recipes, favorites_count=favorites_count)

# --- Password Reset Request (Forgot Password) ---
@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password() -> 'flask.Response':
    """Handle password reset request.
    
    This route handles password reset request by sending a password reset link to the user's email address.
    
    Returns:
        flask.Response: The forgot password template with a form for the user to enter their email address.
    """
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        from .models import User
        from .utils import reset_password
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        # Always show the same message for privacy
        if user:
            reset_password(user)
        flash('If an account exists for this email, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot-password.html', form=form)

# --- My Account & Password Reset Routes ---
@app.route('/my-account')
@login_required
def my_account() -> 'flask.Response':
    """Display the user's account page.
    
    This route shows the user's account information and provides options
    for account management such as password reset.
    
    Returns:
        flask.Response: Renders the my-account template with the necessary form.
    """
    form = EmptyForm()
    return render_template('my-account.html', form=form)

@app.route('/send-password-reset', methods=['POST'])
@login_required
@limiter.limit("3 per minute")
def send_password_reset() -> 'flask.Response':
    """Send a password reset link to the current user's email.
    
    This route handles requests to send a password reset email to the
    currently logged-in user.
    
    Returns:
        flask.Response: Redirects to my-account page with a status message.
    """
    from .utils import reset_password
    success = reset_password(current_user)
    if success:
        flash('A password reset link has been sent to your email.', 'success')
    else:
        flash('Failed to send password reset email. Please try again later.', 'danger')
    return redirect(url_for('my_account'))

@app.route('/password-reset/<token>', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def password_reset(token: str) -> 'flask.Response':
    """Process a password reset request using a token.
    
    This route validates the password reset token, displays a form to set a new password,
    and processes the form submission including reCAPTCHA verification.
    
    Args:
        token: The password reset token from the email link.
    
    Returns:
        flask.Response: Redirects to login page after successful password reset,
        or renders the password reset form for GET requests or failed submissions.
    """
    form = PasswordResetForm()
    recaptcha_site_key = app.config['RECAPTCHA_SITE_KEY']
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=email).first()
    if not user or user.verification_token != token:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('login'))
    if form.validate_on_submit():
        recaptcha_response = request.form.get('g-recaptcha-response')
        from .utils import verify_recaptcha
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return render_template('password-reset.html', form=form, recaptcha_site_key=recaptcha_site_key)
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.verification_token = None
        user.token_expiration = None
        db.session.commit()
        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('password-reset.html', form=form, recaptcha_site_key=recaptcha_site_key)
