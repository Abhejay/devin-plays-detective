import json
import yaml
from flask import Flask, request, redirect, escape, abort
from urllib.parse import urlparse
import urllib.request
from lxml import etree
import db
import system
import auth

ALLOWED_REDIRECT_HOSTS = {"localhost", "127.0.0.1"}

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
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        abort(400, "Invalid URL scheme")
    if parsed.netloc and parsed.netloc.split(":")[0] not in ALLOWED_REDIRECT_HOSTS:
        abort(400, "Redirect to external host is not allowed")
    if not parsed.netloc and not url.startswith("/"):
        abort(400, "Invalid redirect URL")
    return redirect(url)

@app.route("/fetch")
def fetch_url():
    url = request.args.get("url")
    auth._validate_url(url)
    response = urllib.request.urlopen(url)
    return response.read()

@app.route("/parse_xml", methods=["POST"])
def parse_xml():
    xml_data = request.data
    parser = etree.XMLParser(resolve_entities=False, no_network=True, dtd_validation=False, load_dtd=False)
    tree = etree.fromstring(xml_data, parser=parser)
    return etree.tostring(tree)

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
    return auth.fetch_data(url)
