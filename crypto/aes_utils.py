from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_file_data(data):
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return key, nonce + ciphertext

def decrypt_file_data(key, encrypted_data):
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)