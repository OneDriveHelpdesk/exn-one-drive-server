from flask import Flask, request, jsonify
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

@app.route('/remove', methods=['POST'])
def remove_url():
    url_data = request.get_json()
    ngrok_url = url_data.get('ngrok_url')
    if not ngrok_url:
        return jsonify({"error": "No ngrok_url provided"}), 400

    try:
        result = url_collection.delete_one({"ngrok_url": ngrok_url})
        if result.deleted_count == 1:
            return jsonify({"message": "URL removed successfully"}), 200
        else:
            return jsonify({"error": "URL not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
