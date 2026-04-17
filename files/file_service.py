import os
from datetime import datetime
from werkzeug.utils import secure_filename
from crypto.aes_utils import encrypt_file_data, decrypt_file_data
from crypto.rsa_utils import (
    decrypt_aes_key_with_rsa,
    encrypt_aes_key_with_rsa,
    load_private_key,
    load_public_key,
)
from database.models import FileMetadata, User, db
from flask import current_app


def _crypto_key_path(filename):
    return os.path.join(current_app.root_path, 'crypto', filename)


def _resolve_stored_aes_key(stored_key):
    # Backward compatibility: older uploads stored the raw 32-byte AES key directly.
    if len(stored_key) == 32:
        return stored_key

    private_key = load_private_key(_crypto_key_path('private.pem'))
    return decrypt_aes_key_with_rsa(stored_key, private_key)

# --- UPLOAD LOGIC ---
def save_secure_file(file, username):
    filename = secure_filename(file.filename)
    file_data = file.read()
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"msg": "User not found"}

    # 1. Encrypt File Data (AES)
    aes_key, encrypted_data = encrypt_file_data(file_data)
    public_key = load_public_key(_crypto_key_path('public.pem'))
    encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, public_key)

    # 2. Save physical encrypted file to /uploads
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)

    # 3. Store metadata and AES key in MySQL
    existing_file = FileMetadata.query.filter_by(
        filename=filename,
        owner_id=user.id
    ).order_by(FileMetadata.id.desc()).first()

    if existing_file:
        existing_file.encrypted_aes_key = encrypted_aes_key
        existing_file.upload_date = datetime.utcnow()
    else:
        new_file = FileMetadata(
            filename=filename,
            encrypted_aes_key=encrypted_aes_key,
            owner_id=user.id
        )
        db.session.add(new_file)

    db.session.commit()

    return {"msg": "File encrypted and saved successfully", "filename": filename}

# --- DOWNLOAD/DECRYPT LOGIC (The missing function) ---
def get_secure_file(filename):
    # 1. Get metadata from DB
    file_record = FileMetadata.query.filter_by(filename=filename).order_by(FileMetadata.id.desc()).first()
    if not file_record:
        return None

    # 2. Read the encrypted file from disk
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    # 3. Decrypt using the stored AES key
    aes_key = _resolve_stored_aes_key(file_record.encrypted_aes_key)
    decrypted_data = decrypt_file_data(aes_key, encrypted_data)
    
    return decrypted_data
