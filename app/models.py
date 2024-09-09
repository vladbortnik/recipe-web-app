from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    # def __repr__(self):
    #     return f'<User {self.email}>'

class ImgSet(db.Model):
    __tablename__ = 'imgsets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # unique_dir = db.Column(db.String(255), nullable=False)
    folder_path = db.Column(db.String(255), nullable=False)
    products = db.Column(db.Text)  # Store detected products as a comma-separated string
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('imgsets', lazy=True))

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('imgsets.id'), nullable=False)
    recipe = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    imgset = db.relationship('ImgSet', backref=db.backref('recipes', lazy=True))


###########  COPY OF ImgSet  ###########

# class ImgSet(db.Model):
#     __tablename__ = 'imgsets'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
#     folder_path = db.Column(db.String(255), nullable=False)
#     unique_folder = db.Column(db.String(255), nullable=False)
#     file_path = db.Column(db.String(255), nullable=False)

#     user = db.relationship('User', backref=db.backref('imgsets', lazy=True))

############################################



# class User(db.Model, UserMixin):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(70), unique=True, nullable=False)
#     password = db.Column(db.String(256), nullable=False)

#     def __repr__(self):
#         return f'<User {self.email}>'

# # models.py (additions)

# class ImgSet(db.Model):
#     __tablename__ = 'imgsets'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
#     folder_path = db.Column(db.String(255), nullable=False)
#     file_path = db.Column(db.String(255), nullable=False)

#     user = db.relationship('User', backref=db.backref('ImgSet', lazy=True))



# class Product(db.Model):
#     __tablename__ = 'products'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)

# class RecipeProduct(db.Model):
#     __tablename__ = 'recipe_products'
#     id = db.Column(db.Integer, primary_key=True)
#     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

#     recipe = db.relationship('Recipe', backref=db.backref('recipe_products', lazy=True))
#     product = db.relationship('Product', backref=db.backref('recipe_products', lazy=True))
