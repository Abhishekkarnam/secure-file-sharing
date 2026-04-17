from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# 1. Generate Private Key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# 2. Save Private Key to 'private.pem'
with open("private.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 3. Save Public Key to 'public.pem'
with open("public.pem", "wb") as f:
    f.write(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("Keys generated successfully: private.pem and public.pem")