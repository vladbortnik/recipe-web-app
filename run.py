from app import create_app, db

app = create_app()

# Create tables on startup if they don't exist
with app.app_context():
    # Import all models to ensure they're registered with SQLAlchemy
    from app.models import User, ImgSet, Recipe, Favorite
    
    # Create all tables that don't exist yet
    db.create_all()
    print("Database tables created/updated!")

if __name__ == "__main__":
    # Change FLASK_ENV and FLASK_ENV only in .env file
    app.run(host='0.0.0.0', port=5002, debug=app.config['DEBUG'])
