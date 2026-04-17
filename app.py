import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# These imports must match your folder and variable names exactly
from config import Config
from database.db import db
from auth.auth_routes import auth_bp
from files.file_routes import file_bp

def create_app():
    app = Flask(__name__)
    
    # 1. Load Configuration
    app.config.from_object(Config)
    
    # 2. Initialize Extensions
    CORS(app)
    db.init_app(app)
    JWTManager(app)
    Bcrypt(app)

    # 3. Register Blueprints (The "Links" to your folders)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(file_bp, url_prefix='/files')

    # 4. Create Tables Automatically
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)