from flask import Flask, jsonify
from flask_cors import CORS

# 1. Create the Flask app instance
flask_app = Flask(__name__)
CORS(flask_app, origins=["http://localhost:5173"])

# 2. Define a simple root route
@flask_app.route("/")
def index():
    return "<h1>Hello from your Flask App!</h1><p>Visit /api/status to see a JSON response.</p>"

# 3. Define an API-style route
@flask_app.route("/api/status")
def api_status():
    return jsonify({"status": "ok", "source": "Flask"})