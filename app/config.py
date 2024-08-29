import os

class Config:
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')





    # # Flask-Session configuration
    # SESSION_TYPE = 'filesystem'
    # SESSION_PERMANENT = False

    # # SMTP configuration
    # SMTP_SERVER = os.getenv('SMTP_SERVER')
    # SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    # SMTP_USER = os.getenv('SMTP_USER')
    # SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    # SMTP_FROM = os.getenv('SMTP_FROM')

    # Twilio configuration
    # TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    # TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    # TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
