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
