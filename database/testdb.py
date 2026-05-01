import sys
import os

# Add root folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.models import FileMetadata

# Create Flask app instance
app = create_app()

with app.app_context():
    files = FileMetadata.query.all()

    if not files:
        print("No files found in DB")
    else:
        for f in files:
            print("ID:", f.id)
            print("Filename:", f.filename)
            print("Encrypted AES Key:", f.encrypted_aes_key)
            print("-" * 40)