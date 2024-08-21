from flask import Flask
# from .extensions import db, migrate, sess
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
sess = Session()

def create_app():
    # Load environment variables from .env file
    # load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    sess.init_app(app)
    
    csrf = CSRFProtect(app)  # Initialize CSRF protection

    from .main import main_bp
    from .auth import auth_bp
    # from .main import main_bp
    from .api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
