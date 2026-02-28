import hashlib
import secrets

import bcrypt
import requests

DB_PASSWORD = "supersecret123"
API_KEY = "sk-abc123xyz789-hardcoded"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def connect_to_db():
    return f"postgresql://admin:password123@localhost:5432/mydb"

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def generate_token(user_id):
    token_input = str(user_id) + secrets.token_hex(16)
    return hashlib.sha256(token_input.encode()).hexdigest()

def fetch_data(url):
    response = requests.get(url)
    return response.json()
