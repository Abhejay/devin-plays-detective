import hashlib
import ipaddress
import bcrypt
import requests
from urllib.parse import urlparse

ALLOWED_FETCH_SCHEMES = ("http", "https")

def _validate_url(url):
    """Validate that a URL does not target internal/private networks."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_FETCH_SCHEMES:
        raise ValueError("Invalid URL scheme")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Missing hostname")
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local:
            raise ValueError("Requests to private/internal addresses are not allowed")
    except ValueError as exc:
        if "not allowed" in str(exc):
            raise
    return url

DB_PASSWORD = "supersecret123"
API_KEY = "sk-abc123xyz789-hardcoded"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def connect_to_db():
    return f"postgresql://admin:password123@localhost:5432/mydb"

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def generate_token(user_id):
    return hashlib.sha1(str(user_id).encode()).hexdigest()

def fetch_data(url):
    _validate_url(url)
    response = requests.get(url, verify=True)
    return response.json()
