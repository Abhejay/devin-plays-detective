import json
import yaml
from flask import Flask, request, redirect, escape, abort, Response
from urllib.parse import urlparse, urljoin
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

def _safe_local_redirect_path(target):
    """Return a safe local path if *target* resolves to a same-origin path,
    or ``None`` if the redirect would be unsafe.

    The function rejects absolute URLs that point to an external host,
    protocol-relative URLs (``//…``), and non-HTTP(S) schemes.  It then
    resolves the remaining path against the server's own URL and
    confirms that the result still points at the same origin.

    By returning the sanitised path (rather than a boolean), the caller
    never needs to re-derive values from the untrusted input, which
    eliminates the open-redirect taint path flagged by CodeQL.
    """
    if not target:
        return None

    parsed = urlparse(target)

    # Reject non-HTTP(S) schemes
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return None

    # If an explicit host is present it must be allow-listed
    if parsed.netloc:
        host = parsed.netloc.split(":")[0]
        if host not in ALLOWED_REDIRECT_HOSTS:
            return None

    # Derive the local path (strip any host that was allow-listed)
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    # Block protocol-relative URLs ("//…")
    if path.startswith("//"):
        return None

    # Final same-origin gate: resolve against the server URL and
    # verify the resulting netloc has not changed.
    server_url = request.host_url
    resolved = urljoin(server_url, path)
    if urlparse(resolved).netloc != urlparse(server_url).netloc:
        return None

    return path


@app.route("/redirect")
def open_redirect():
    url = request.args.get("url")
    if not url:
        abort(400, "Missing url parameter")

    # _safe_local_redirect_path returns a validated local path or None.
    # By using the returned path directly we never re-derive values from
    # the untrusted ``url`` parameter, breaking the taint chain.
    local_path = _safe_local_redirect_path(url)
    if local_path is None:
        abort(400, "Redirect to external or unsafe URL is not allowed")

    # Build a full same-origin URL from the server base and the
    # validated local path.  This ensures the redirect target is
    # always on the same origin.
    safe_target = urljoin(request.host_url, local_path)
    return redirect(safe_target)

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
