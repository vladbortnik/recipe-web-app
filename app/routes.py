from flask import current_app as app
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from .forms import LoginForm, SignupForm, UploadImageForm
from . import db, bcrypt, login_manager # Import 'db & bcrypt' from the app package
from .models import User, Recipe, ImageSet, Product, RecipeProduct
import uuid, os
from .utils import process_images

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
        if email and User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('signup.html', form=form)
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created successfully.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/upload')
# @login_required
# def upload():
#     return render_template('upload.html')


# Ensure your upload folder is configured
# app.config['UPLOAD_FOLDER'] = 'path/to/upload/folder'

# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload():
#     form = UploadImageForm()
#     if form.validate_on_submit():
#         if form.images.data:
#             filename = secure_filename(form.images.data.filename)
#             folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), filename)
#             os.makedirs(os.path.dirname(folder_path), exist_ok=True)
#             form.images.data.save(folder_path)
            
#             imageset = ImageSet(user_id=current_user.id, folder_path=folder_path, file_path=folder_path)
#             db.session.add(imageset)
#             db.session.commit()
            
#             # After saving, you may want to process the images and generate recipes

#             flash('Images uploaded successfully', 'success')
#             return redirect(url_for('dashboard'))
    
#     return render_template('upload.html', form=form)

# # routes.py (additions)
# from flask import current_app as app
# import uuid


# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload():
#     form = UploadImageForm()
#     if form.validate_on_submit():
#         if form.images.data:
#             filename = f"{uuid.uuid4()}_{form.images.data.filename}"
#             user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
#             os.makedirs(user_folder, exist_ok=True)
#             file_path = os.path.join(user_folder, filename)
#             form.images.data.save(file_path)
            
#             imageset = ImageSet(user_id=current_user.id, folder_path=user_folder, file_path=file_path)
#             db.session.add(imageset)
#             db.session.commit()
            
#             # Process images and generate recipes if needed
#             process_images(file_path)  # Assuming function exists in utils.py

#             flash('Images uploaded successfully', 'success')
#             return redirect(url_for('dashboard'))
    
#     return render_template('upload.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadImageForm()
    if form.validate_on_submit():
        if form.images.data:
            # Create a unique folder for this upload
            unique_folder = str(uuid.uuid4())
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), unique_folder)
            os.makedirs(user_folder, exist_ok=True)

            for file in form.images.data:
                filename = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(user_folder, filename)
                file.save(file_path)

                imageset = ImageSet(user_id=current_user.id, folder_path=user_folder, file_path=file_path, unique_folder=unique_folder)
                db.session.add(imageset)
            db.session.commit()

            # Process images and generate recipes if needed
            process_images(user_folder)  # Assuming function exists in utils.py

            flash('Images uploaded successfully', 'success')
            return redirect(url_for('dashboard'))

    return render_template('upload.html', form=form)



# @app.route('/dashboard', methods=['GET'])
# @login_required
# def dashboard():
#     image_sets = ImageSet.query.filter_by(user_id=current_user.id).all()
#     return render_template('dashboard.html', image_sets=image_sets)

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    image_sets = ImageSet.query.filter_by(user_id=current_user.id).all()
    # Group images by unique_folder
    grouped_image_sets = {}
    for image_set in image_sets:
        if image_set.unique_folder not in grouped_image_sets:
            grouped_image_sets[image_set.unique_folder] = []
        grouped_image_sets[image_set.unique_folder].append(image_set)
    
    return render_template('dashboard.html', grouped_image_sets=grouped_image_sets)
