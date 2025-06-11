from flask_login import UserMixin
from . import db
from datetime import datetime
from typing import List, Optional

class User(db.Model, UserMixin):
    """User model for authentication and account management.
    
    This model stores user account information including email, password hash,
    verification status, and security tokens for email verification and password reset.
    Supports both local authentication and Google OAuth.
    
    Attributes:
        id: Primary key for the user.
        email: User's email address, must be unique.
        password: Hashed password for authentication (nullable for OAuth users).
        google_id: Google OAuth user ID (nullable for local users).
        auth_provider: Authentication provider ('local' or 'google').
        is_verified: Boolean indicating if the email has been verified.
        verification_token: Token for email verification or password reset.
        token_expiration: Datetime when the token expires.
        date_created: Datetime when the user account was created.
    """
    __tablename__ = 'users'
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(70), unique=True, nullable=False)
    password: Optional[str] = db.Column(db.String(256), nullable=True)  # Nullable for OAuth users
    google_id: Optional[str] = db.Column(db.String(100), unique=True, nullable=True)
    auth_provider: str = db.Column(db.String(20), default='local', nullable=False)  # 'local' or 'google'
    is_verified: bool = db.Column(db.Boolean, default=False, nullable=False)
    verification_token: Optional[str] = db.Column(db.String(100), nullable=True)
    token_expiration: Optional[datetime] = db.Column(db.DateTime, nullable=True)
    date_created: datetime = db.Column(db.DateTime, default=db.func.current_timestamp())

class ImgSet(db.Model):
    """Image set model for storing uploaded images and recognized products.
    
    This model tracks sets of images uploaded by users and the products recognized
    in those images by the Azure Vision API.
    
    Attributes:
        id: Primary key for the image set.
        user_id: Foreign key to the user who uploaded the images.
        folder_path: Path to the directory containing the uploaded images.
        products: Comma-separated list of product names recognized in the images.
        upload_date: Datetime when the images were uploaded.
        user: Relationship to the User model.
    """
    __tablename__ = 'imgsets'
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    folder_path: str = db.Column(db.String(255), nullable=False)
    products: Optional[str] = db.Column(db.Text, nullable=True)
    upload_date: datetime = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('imgsets', lazy=True))

class Recipe(db.Model):
    """
    Recipe model for storing a single recipe fetched from Spoonacular API.

    Attributes:
        id: Primary key for the recipe entry.
        spoonacular_id: Unique Spoonacular API ID for the recipe.
        recipe_data: JSON field storing the full recipe data from Spoonacular.
        date_created: Datetime when the recipe entry was created.
    """
    __tablename__ = 'recipes'
    id: int = db.Column(db.Integer, primary_key=True)
    spoonacular_id: str = db.Column(db.String(50), unique=True, nullable=False)
    recipe_data: dict = db.Column(db.JSON, nullable=False)
    date_created: datetime = db.Column(db.DateTime, default=db.func.current_timestamp())


class Favorite(db.Model):
    """
    Model for user favorite recipes.

    This model tracks which recipes a user has favorited. It links a User to a Recipe
    via the unique Spoonacular ID.

    Attributes:
        id: Primary key for the favorite entry.
        user_id: Foreign key to the user who favorited the recipe.
        spoonacular_id: Foreign key to the unique recipe in the recipes table.
    """
    __tablename__ = 'favorites'
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spoonacular_id: str = db.Column(db.String(50), db.ForeignKey('recipes.spoonacular_id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'spoonacular_id', name='_user_spoonacular_uc'),)

    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    recipe = db.relationship('Recipe', backref=db.backref('favorited_by', lazy=True), primaryjoin="Favorite.spoonacular_id==Recipe.spoonacular_id")
