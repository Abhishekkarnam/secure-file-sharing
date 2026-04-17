import os
from dotenv import load_dotenv

# This line loads the variables from the .env file
load_dotenv()

class Config:
    # 1. Database Connection String
    # It pulls the details from the .env file automatically
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    
    # 2. Security Settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # 3. File Settings
    # This finds your 'uploads' folder automatically
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit uploads to 16MB