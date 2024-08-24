from flask import Flask
from dotenv import load_dotenv
# import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
### from flask_session import Session
### from flask_wtf.csrf import CSRFProtect

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
### sess = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "logIn"
    login_manager.login_message_category = "info"
    ### sess.init_app(app)
    
    ### csrf = CSRFProtect(app)  # Initialize CSRF protection

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # @app.route('/')
    # def home():
    #     return "Hello, World!"

    with app.app_context():
        # Import routes
        from . import routes

    return app
