import hashlib
import os
import requests

DB_PASSWORD = "supersecret123"
API_KEY = "sk-abc123xyz789-hardcoded"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def connect_to_db():
    return f"postgresql://admin:password123@localhost:5432/mydb"

def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return (salt + hashed).hex()

def generate_token(user_id):
    return hashlib.sha256(str(user_id).encode()).hexdigest()

def fetch_data(url):
    response = requests.get(url, verify=True)
    return response.json()
