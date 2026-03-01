import hashlib
import requests

DB_PASSWORD = "supersecret123"
API_KEY = "sk-abc123xyz789-hardcoded"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def connect_to_db():
    return f"postgresql://admin:password123@localhost:5432/mydb"

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def generate_token(user_id):
    return hashlib.sha1(str(user_id).encode()).hexdigest()

def fetch_data(url):
    response = requests.get(url, verify=False)
    return response.json()