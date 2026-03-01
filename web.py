import pickle
import yaml
from flask import Flask, request, redirect, abort
import urllib.request
from urllib.parse import urlparse
from lxml import etree

app = Flask(__name__)

@app.route("/greet")
def greet():
    # XSS (CWE-79)
    name = request.args.get("name", "")
    return f"<h1>Welcome, {escape(name)}!</h1>"

@app.route("/search")
def search():
    # XSS (CWE-79)
    query = request.args.get("q", "")
    return f"<p>Search results for: {escape(query)}</p>"

ALLOWED_REDIRECT_DOMAINS = {"example.com", "www.example.com"}

@app.route("/redirect")
def open_redirect():
    # Open Redirect (CWE-601) - Fixed: validate against allowlist
    url = request.args.get("url")
    if not url:
        abort(400, description="Missing 'url' parameter")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.hostname not in ALLOWED_REDIRECT_DOMAINS:
        abort(400, description="Redirect to untrusted domain is not allowed")
    return redirect(url)

@app.route("/fetch")
def fetch_url():
    # SSRF (CWE-918)
    url = request.args.get("url")
    response = urllib.request.urlopen(url)
    return response.read()

@app.route("/parse_xml", methods=["POST"])
def parse_xml():
    # XXE (CWE-611)
    xml_data = request.data
    parser = etree.XMLParser(resolve_entities=True, no_network=False)
    tree = etree.fromstring(xml_data, parser=parser)
    return etree.tostring(tree)

def load_user_session(session_data):
    # Insecure Deserialization (CWE-502)
    return pickle.loads(session_data)

def parse_config(config_str):
    # Insecure Deserialization (CWE-502)
    return yaml.load(config_str)

@app.route("/upload", methods=["POST"])
def upload():
    # Insecure Deserialization (CWE-502)
    data = pickle.loads(request.data)
    return str(escape(data))
