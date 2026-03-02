import json
import yaml
from flask import Flask, request, redirect, escape, abort, Response, url_for
from urllib.parse import urlparse
import urllib.request
from lxml import etree
import db
import system
import auth

app = Flask(__name__)

@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return f"<h1>Welcome, {escape(name)}!</h1>"

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return f"<p>Search results for: {escape(query)}</p>"

@app.route("/redirect")
def open_redirect():
    url = request.args.get("url")
    if not url:
        abort(400, "Missing url parameter")

    parsed = urlparse(url)

    # Reject URLs with a scheme or network location (external redirects)
    if parsed.scheme or parsed.netloc:
        abort(400, "Redirect to external or unsafe URL is not allowed")

    target_path = parsed.path or "/"

    # Block protocol-relative URLs ("//…" or "/\…")
    if target_path.startswith("//") or target_path.startswith("/\\"):
        abort(400, "Redirect to external or unsafe URL is not allowed")

    # Match the requested path against registered application routes.
    # This rejects any path that does not correspond to a known endpoint.
    try:
        adapter = app.url_map.bind("")
        endpoint, _values = adapter.match(target_path)
    except Exception:
        return abort(400, "Redirect to unknown or unsafe URL is not allowed")

    # Build the redirect target from the matched endpoint name via url_for.
    # The value passed to redirect() is generated from Flask's own route
    # table — not from user input — which breaks the taint chain that
    # CodeQL flags as an open-redirect vulnerability (CWE-601).
    safe_url = url_for(endpoint)
    return redirect(safe_url)

@app.route("/fetch")
def fetch_url():
    url = request.args.get("url")
    safe_url = auth._validate_url(url)
    response = urllib.request.urlopen(safe_url)
    return response.read()

@app.route("/parse_xml", methods=["POST"])
def parse_xml():
    xml_data = request.data
    parser = etree.XMLParser(resolve_entities=False, no_network=True, dtd_validation=False, load_dtd=False)
    tree = etree.fromstring(xml_data, parser=parser)
    return Response(etree.tostring(tree), content_type="application/xml")

def load_user_session(session_data):
    return json.loads(session_data)

def parse_config(config_str):
    return yaml.safe_load(config_str)

@app.route("/upload", methods=["POST"])
def upload():
    data = json.loads(request.data)
    return str(escape(data))

@app.route("/user")
def get_user():
    username = request.args.get("username", "")
    return str(db.get_user(username))

@app.route("/delete_user", methods=["POST"])
def delete_user():
    user_id = request.form.get("id", "")
    db.delete_user(user_id)
    return "Deleted"

@app.route("/shop")
def shop():
    kw = request.args.get("kw", "")
    return str(db.search_products(kw))

@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    system.ping_host(host)
    return "Pinged"

@app.route("/info")
def file_info():
    filename = request.args.get("filename", "")
    return system.get_file_info(filename)

@app.route("/read")
def read_file():
    filepath = request.args.get("filepath", "")
    return system.read_file(filepath)

@app.route("/download")
def download_file():
    filename = request.args.get("filename", "")
    return system.download_file(filename)

@app.route("/login", methods=["POST"])
def login():
    pw = request.form.get("password", "")
    return auth.hash_password(pw)

@app.route("/fetch_data")
def fetch_external_data():
    url = request.args.get("url", "")
    data = auth.fetch_data(url)
    return Response(json.dumps(data), content_type="application/json")
