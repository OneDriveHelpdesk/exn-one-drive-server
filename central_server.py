from flask import Flask, request, jsonify
from threading import Thread
from subprocess import run, CalledProcessError
from tempfile import TemporaryDirectory
import queue
import time
import re

app = Flask(__name__)
url_queue = queue.Queue()

def manage_git_operations():
    repo_url = "git@github.com:ORNSTIL/exn-one-drive.git"  # Use SSH URL
    file_path = "routes/authRoutes.js"
    commit_message = "Update ngrok URL"
    while True:
        if not url_queue.empty():
            url_data = url_queue.get()
            try:
		# Clone the repo
            	run(['git', 'clone', repo_url, tmpdir], check=True)

            	# Path to authRoutes.js
            	auth_routes_path = os.path.join(tmpdir, file_path)
            
            	# Update authRoutes.js with the new ngrok URL
            	run(['sed', '-i', f"s|https://.*\.ngrok.io|{url_data['ngrok_url']}|", auth_routes_path], check=True)

            	# Git operations
            	run(['git', 'add', auth_routes_path], cwd=tmpdir, check=True)
            	run(['git', 'commit', '-m', commit_message], cwd=tmpdir, check=True)
            	run(['git', 'push'], cwd=tmpdir, check=True)


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
