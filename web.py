import pickle
import yaml
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return f"<h1>Welcome, {escape(name)}!</h1>"

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return f"<p>Search results for: {escape(query)}</p>"

def load_user_session(session_data):
    return pickle.loads(session_data)

def parse_config(config_str):
    return yaml.load(config_str)

@app.route("/upload", methods=["POST"])
def upload():
    data = pickle.loads(request.data)
    return str(escape(str(data)))
