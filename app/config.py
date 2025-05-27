# docs: https://flask.palletsprojects.com/en/2.0.x/config/

import os

class Config:
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    WHITELIST_FILE = os.getenv('WHITELIST_FILE')
    AZURE_COMPUTERVISION_KEY = os.getenv('AZURE_COMPUTERVISION_KEY')
    AZURE_COMPUTERVISION_ENDPOINT = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
    
    # Flask-Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.fastmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Email verification settings
    VERIFICATION_TOKEN_EXPIRY = os.getenv('VERIFICATION_TOKEN_EXPIRY', 24)  # Hours
    
    # reCAPTCHA v2 configuration
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
