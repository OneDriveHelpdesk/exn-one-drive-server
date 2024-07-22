from flask import Flask, request, jsonify
from threading import Thread
from subprocess import run, CalledProcessError
from tempfile import TemporaryDirectory
import queue
import time
import os
import json

app = Flask(__name__)
url_queue = queue.Queue()
url_file = 'ngrok_urls.json'

def manage_git_operations():
    repo_url = "git@github.com:ORNSTIL/exn-one-drive.git"
    file_path = "routes/authRoutes.js"
    commit_message = "Update ngrok URL"
    while True:
        if not url_queue.empty():
            url_data = url_queue.get()
            try:
                with TemporaryDirectory() as tmpdir:
                    run(['git', 'clone', repo_url, tmpdir], check=True)
                    auth_routes_path = os.path.join(tmpdir, file_path)
                    run(['sed', '-i', f"s|https://.*\\.ngrok.io|{url_data['ngrok_url']}|", auth_routes_path], check=True)
                    run(['git', 'add', auth_routes_path], cwd=tmpdir, check=True)
                    run(['git', 'commit', '-m', commit_message], cwd=tmpdir, check=True)
                    run(['git', 'push'], cwd=tmpdir, check=True)
                print(f"Updated and committed ngrok URL: {url_data['ngrok_url']}")
            except CalledProcessError as e:
                print(f"Error during Git operations: {e}")
        time.sleep(1)

def save_urls_to_file(url_data):
    try:
        if os.path.exists(url_file):
            with open(url_file, 'r') as file:
                urls = json.load(file)
        else:
            urls = []

        # Append new URL if not already in the list
        if url_data['ngrok_url'] not in urls:
            urls.append(url_data['ngrok_url'])

        with open(url_file, 'w') as file:
            json.dump(urls, file)
    except Exception as e:
        print(f"Error saving URLs to file: {e}")

def load_urls_from_file():
    try:
        if os.path.exists(url_file):
            with open(url_file, 'r') as file:
                urls = json.load(file)
                return urls
        return []
    except Exception as e:
        print(f"Error loading URLs from file: {e}")
        return []

@app.route('/submit', methods=['POST'])
def submit_url():
    url_data = request.get_json()
    url_queue.put(url_data)
    save_urls_to_file(url_data)
    return jsonify({"message": "URL queued for update"}), 202

@app.route('/list_urls', methods=['GET'])
def list_urls():
    urls = load_urls_from_file()
    return jsonify({"urls": urls})

if __name__ == '__main__':
    git_thread = Thread(target=manage_git_operations, daemon=True)
    git_thread.start()
    app.run(host='0.0.0.0', port=5002)
