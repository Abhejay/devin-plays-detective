import hashlib
import ipaddress
import socket
import bcrypt
import requests
from urllib.parse import urlparse, urlunparse

ALLOWED_FETCH_SCHEMES = ("http", "https")

def _validate_url(url):
    """Validate that a URL does not target internal/private networks.

    Resolves the hostname to an IP address and checks that it is not
    a private, loopback, reserved, or link-local address.  Returns a
    *sanitized* URL whose hostname has been replaced with the resolved
    IP so that the subsequent HTTP request cannot be redirected to an
    internal host via DNS rebinding.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_FETCH_SCHEMES:
        raise ValueError("Invalid URL scheme")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Missing hostname")

    # Resolve hostname to IP to prevent DNS rebinding attacks
    try:
        resolved_ip = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)[0][4][0]
    except socket.gaierror:
        raise ValueError("Unable to resolve hostname")

    addr = ipaddress.ip_address(resolved_ip)
    if addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local:
        raise ValueError("Requests to private/internal addresses are not allowed")

    # Reconstruct URL with resolved IP to prevent TOCTOU / DNS rebinding
    port_suffix = f":{parsed.port}" if parsed.port else ""
    safe_netloc = f"{resolved_ip}{port_suffix}"
    safe_parsed = parsed._replace(netloc=safe_netloc)
    safe_url = urlunparse(safe_parsed)
    return safe_url

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
    safe_url = _validate_url(url)
    response = requests.get(safe_url, verify=True)
    return response.json()
