from flask import Flask, request, jsonify
#from threading import Thread
#from git import Repo
from pymongo import MongoClient
import queue
import time
import os

app = Flask(__name__)
url_queue = queue.Queue()

# Use environment variables for sensitive information
client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
db = client.ngrok
url_collection = db.urls

# def manage_git_operations():
#    repo_url = "https://github.com/OneDriveHelpdesk/exn-one-drive.git"
#    file_path = "routes/authRoutes.js"
#    commit_message = "Update ngrok URL"
#    while True:
#        if not url_queue.empty():
#            url_data = url_queue.get()
#            try:
#                repo_dir = '/tmp/repo'
#                if os.path.exists(repo_dir):
#                    os.system(f'rm -rf {repo_dir}')
#               
#                # Get the GitHub token from environment variable
#                token = os.getenv('GITHUB_TOKEN')
#                if not token:
#                    print("GitHub token not found")
#                    return

                # Use the token in the repo URL
#                token_repo_url = repo_url.replace('https://', f'https://{token}@')

#                Repo.clone_from(token_repo_url, repo_dir)
#                auth_routes_path = os.path.join(repo_dir, file_path)
#                with open(auth_routes_path, 'r') as file:
#                    content = file.read()
#                new_content = content.replace('https://existing.ngrok.io', url_data['ngrok_url'])
#                with open(auth_routes_path, 'w') as file:
#                    file.write(new_content)
#                repo = Repo(repo_dir)
#                repo.index.add([auth_routes_path])
#                repo.index.commit(commit_message)
#                origin = repo.remote(name='origin')
#                origin.push()
#                print(f"Updated and committed ngrok URL: {url_data['ngrok_url']}")
#            except Exception as e:
#                print(f"Error during Git operations: {e}")
#        time.sleep(1)

def save_urls_to_db(url_data):
    try:
        url_collection.update_one(
            {"ngrok_url": url_data['ngrok_url']},
            {"$set": url_data},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving URL to database: {e}")

def load_urls_from_db():
    try:
        urls = list(url_collection.find({}, {"_id": 0}))
        return urls
    except Exception as e:
        print(f"Error loading URLs from database: {e}")
        return []

def remove_url_from_db(url):
    try:
        url_collection.delete_one({"ngrok_url": url})
        print(f"Removed ngrok URL from database: {url}")
    except Exception as e:
        print(f"Error removing URL from database: {e}")

@app.route('/submit', methods=['POST'])
def submit_url():
    url_data = request.get_json()
    url_queue.put(url_data)
    save_urls_to_db(url_data)
    return jsonify({"message": "URL queued for update"}), 202

@app.route('/list_urls', methods=['GET'])
def list_urls():
    urls = load_urls_from_db()
    return jsonify({"urls": urls})

@app.route('/remove', methods=['DELETE'])
def remove_url():
    url_data = request.get_json()
    url = url_data.get("ngrok_url")
    if url:
        remove_url_from_db(url)
        return jsonify({"message": "URL removed"}), 200
    return jsonify({"error": "Invalid URL"}), 400

if __name__ == '__main__':
#    git_thread = Thread(target=manage_git_operations, daemon=True)
#    git_thread.start()
    app.run(host='0.0.0.0', port=5002)
