import os

class Config:
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    AZURE_COMPUTERVISION_KEY = os.getenv('AZURE_COMPUTERVISION_KEY')
    AZURE_COMPUTERVISION_ENDPOINT = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
    DEBUG_TB_INTERCEPT_REDIRECTS = False  # Disable intercepting redirects
    SQLALCHEMY_RECORD_QUERIES = True  # Explicitly enable recording of SQLAlchemy queries
    # DEBUG_TB_PROFILER_ENABLED = True  # Enable profiler







    # GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

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
