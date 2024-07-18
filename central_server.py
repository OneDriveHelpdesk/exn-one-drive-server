from flask import Flask, request, jsonify
from threading import Thread
import subprocess
import queue
import time
import re

app = Flask(__name__)
url_queue = queue.Queue()

def manage_git_operations():
    while True:
        if not url_queue.empty():
            url_data = url_queue.get()
            try:
                # Update the authRoutes.js with the new ngrok URL
                subprocess.run(['sed', '-i', f"s|https://.*\.ngrok.io|{url_data['ngrok_url']}|", 'path/to/authRoutes.js'], check=True)
                # Commit and push the update to GitHub
                subprocess.run(['git', 'add', 'path/to/authRoutes.js'], check=True)
                subprocess.run(['git', 'commit', '-m', 'Update ngrok URL'], check=True)
                subprocess.run(['git', 'push'], check=True)
                print(f"Updated and committed ngrok URL: {url_data['ngrok_url']}")
            except subprocess.CalledProcessError as e:
                print(f"Error during Git operations: {e}")
        time.sleep(1)  # Polling interval

@app.route('/submit', methods=['POST'])
def submit_url():
    url_data = request.get_json()
    url_queue.put(url_data)
    return jsonify({"message": "URL queued for update"}), 202

@app.route('/list_urls', methods=['GET'])
def list_urls():
    # This endpoint would need to fetch current URLs from a database or file
    return jsonify({"urls": ["list", "of", "current", "ngrok", "urls"]})

if __name__ == '__main__':
    git_thread = Thread(target=manage_git_operations, daemon=True)
    git_thread.start()
    app.run(host='0.0.0.0', port=5002)
