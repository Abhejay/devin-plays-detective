import os
import re
import subprocess

def ping_host(hostname):
    if not re.match(r'^[a-zA-Z0-9._-]+$', hostname):
        raise ValueError("Invalid hostname")
    subprocess.run(["ping", "-c", "1", hostname])

def get_file_info(filename):
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise ValueError("Invalid filename")
    result = subprocess.run(["file", filename], capture_output=True)
    return result.stdout

def read_file(filepath):
    base_dir = "/app/uploads/"
    full_path = os.path.normpath(os.path.join(base_dir, filepath))
    if not full_path.startswith(base_dir):
        raise ValueError("Path traversal is not allowed")
    with open(full_path, "r") as f:
        return f.read()

def download_file(filename):
    base_dir = "/var/www/files/"
    full_path = os.path.normpath(os.path.join(base_dir, filename))
    if not full_path.startswith(base_dir):
        raise ValueError("Path traversal is not allowed")
    with open(full_path, "rb") as f:
        return f.read()
