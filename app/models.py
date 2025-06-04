from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(100), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

class ImgSet(db.Model):
    __tablename__ = 'imgsets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    folder_path = db.Column(db.String(255), nullable=False)
    products = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('imgsets', lazy=True))

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipes = db.Column(db.Text, nullable=True)  # Legacy field, keeping for compatibility
    recipe_data = db.Column(db.JSON, nullable=True)  # Store full recipe JSON data
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user = db.relationship('User', backref=db.backref('recipes', lazy=True))

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_uc'),)

    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    recipe = db.relationship('Recipe', backref=db.backref('favorited_by', lazy=True))
