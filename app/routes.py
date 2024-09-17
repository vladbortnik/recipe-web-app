from flask import current_app as app
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from .forms import LoginForm, SignupForm, UploadImageForm
from . import db, bcrypt, login_manager # Import 'db & bcrypt' from the app package
from .models import User, Recipe, ImgSet
import uuid, os
from .utils import process_imgset, get_recipe

### DEBUG ####################
from pprint import pprint as pp
##############################


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

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadImageForm()
    if form.validate_on_submit():
        if form.images.data:
            # Create a unique folder for this upload
            # unique_dir = os.path.join(str(current_user.id), str(uuid.uuid4()))
            unique_dir_name = str(uuid.uuid4())
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), unique_dir_name)
            os.makedirs(folder_path, exist_ok=True)

            for file in form.images.data:
                filename = f"{uuid.uuid4()}_{file.filename}"
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)

            imgset = ImgSet(user_id=current_user.id, folder_path=folder_path)
            db.session.add(imgset)
            db.session.commit()

            # Process images and generate recipes if needed
            process_imgset(folder_path)  # Assuming function exists in utils.py

            flash('Images uploaded and processed successfully.', 'success')
            return redirect(url_for('dashboard'))
            # return redirect(url_for('index'))

    return render_template('upload.html', form=form)




@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Let's assume each user has only one imgset
    imgset = ImgSet.query.filter_by(user_id=current_user.id).first()
    
    products = imgset.products.split(',') if imgset and imgset.products else []

    ##### DEBUG ######################
    # pp(f'/dashboard::dashboard::products == {products}')
    ##################################

    
    return render_template('dashboard.html', products=products)

@app.route('/dashboard', methods=['POST'])
@login_required
def get_dashboard_recipe():
    pressed_products = request.form.getlist('product')

    ##### DEBUG ######################
    # pressed_products = ['tomato', 'lettuce', 'olive oil', 'salt', 'pepper']
    # pp(f'/dashboard::get_dashboard_recipe::pressed_products == {pressed_products}')
    ##################################
    
    recipes = get_recipe(pressed_products)
    
    return render_template('dashboard.html', recipes=recipes, products=pressed_products)







# @app.route('/dashboard', methods=['GET'])
# @login_required
# def dashboard():
#     pass
    # imgsets = ImgSet.query.filter_by(user_id=current_user.id).all()
    # # Group images by unique_dir
    # grouped_imgsets = {}
    # for imgset in imgsets:
    #     if imgset.unique_dir not in grouped_imgsets:
    #         grouped_imgsets[imgset.unique_dir] = []
    #     grouped_imgsets[imgset.unique_dir].append(imgset)
    
    # return render_template('dashboard.html', grouped_imgsets=grouped_imgsets)




# @app.route('/dashboard', methods=['GET'])
# @login_required
# def dashboard():
#     image_sets = ImageSet.query.filter_by(user_id=current_user.id).all()
#     return render_template('dashboard.html', image_sets=image_sets)



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


# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload():
#     form = UploadImageForm()
#     if form.validate_on_submit():
#         if form.images.data:
#             filename = f"{uuid.uuid4()}_{form.images.data.filename}"
#             folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
#             os.makedirs(folder_path, exist_ok=True)
#             file_path = os.path.join(folder_path, filename)
#             form.images.data.save(file_path)
            
#             imageset = ImageSet(user_id=current_user.id, folder_path=folder_path, file_path=file_path)
#             db.session.add(imageset)
#             db.session.commit()
            
#             # Process images and generate recipes if needed
#             process_images(file_path)  # Assuming function exists in utils.py

#             flash('Images uploaded successfully', 'success')
#             return redirect(url_for('dashboard'))
    
#     return render_template('upload.html', form=form)