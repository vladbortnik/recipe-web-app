import uuid, os
from flask import current_app as app
from flask import request, render_template, redirect, url_for, flash, session, abort
from flask_login import login_user, current_user, logout_user, login_required
from . import db, bcrypt
from .forms import LoginForm, SignupForm, UploadImageForm
from .models import User, ImgSet
from .utils import retrieve_product_labels, retrieve_recipes_by_ingredients, fetch_user_products, fetch_user_recipes, send_verification_email, verify_token

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Check if user has verified their email
            if not user.is_verified:
                # Display message with a button to manually request verification email
                # Using safe filter in template to render HTML properly
                flash('Please verify your email address before logging in. Check your inbox for the verification link.', 'warning')
                # Store user ID in session to allow them to request a new verification email
                session['unverified_user_id'] = user.id  
                return render_template('login.html', form=form, show_resend=True, user_id=user.id)
            
            login_user(user, remember=form.remember.data)
            flash('You have been logged in', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Please check email and password.', 'danger')
            
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
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
        
    return render_template('signup.html', form=form)

@app.route('/resend-verification/<int:user_id>')
def resend_verification(user_id):
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
def verify_email(token):
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
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
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
def dashboard():
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
            recipes = fetch_user_recipes()
    
    return render_template('dashboard.html', products=products, recipes=recipes)
