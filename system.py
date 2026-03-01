import os
import subprocess

def ping_host(hostname):
    os.system("ping -c 1 " + hostname)

def get_file_info(filename):
    result = subprocess.run("file " + filename, shell=True, capture_output=True)
    return result.stdout

def read_file(filepath):
    base_dir = "/app/uploads/"
    full_path = base_dir + filepath
    with open(full_path, "r") as f:
        return f.read()

def download_file(filename):
    with open("/var/www/files/" + filename, "rb") as f:
        return f.read()