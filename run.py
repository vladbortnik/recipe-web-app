from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

if __name__ == "__main__":
    # Change host, port, and debug only via .env file
    app.run(host='0.0.0.0', port=5002, debug=app.config['DEBUG'])   # DO NOT MODIFY
