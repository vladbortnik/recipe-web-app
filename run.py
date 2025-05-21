from app import create_app

app = create_app()

if __name__ == "__main__":
    # Change FLASK_ENV and FLASK_ENV only in .env file
    app.run(host='0.0.0.0', port=5001, debug=app.config['DEBUG'])
