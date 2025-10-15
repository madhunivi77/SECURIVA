apfrom flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from openai import OpenAI
from groq import Groq
from uuid import uuid4

from flask import request
import requests
from .telesign_auth import get_token  # Adjust import if needed for other functionalities

# Load environment variables
load_dotenv()

# --- Flask setup ---
flask_app = Flask(__name__)
flask_app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Needed for sessions
CORS(flask_app, origins=["http://localhost:5173"], supports_credentials=True)

# --- Load config.json ---
config_path = Path(__file__).parent / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

api = config.get("api")
model = config.get("model")

# --- Initialize API client ---
if api == "openai":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elif api == "groq":
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
else:
    raise ValueError(f"Invalid API selection in config.json: {api}")

# --- Global in-memory conversation store ---
conversations = {}

# --- Helper function to get session id ---
def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid4())
    return session["session_id"]

# --- Routes ---
@flask_app.route("/")
def index():
    return "<h1>Hello from your Flask App!</h1><p>Visit /api/status to see a JSON response.</p>"

@flask_app.route("/api/status")
def api_status():
    return jsonify({"status": "ok", "source": "Flask", "api": api, "model": model})

@flask_app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    session_id = get_session_id()

    # Initialize chat history if new session
    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": "You are a helpful assistant. You can remember past messages in the current conversation."}
        ]

    # Add user message
    conversations[session_id].append({"role": "user", "content": user_message})

    try:
        # --- Call appropriate API ---
        if api == "openai":
            response = client.chat.completions.create(
                model=model,
                messages=conversations[session_id],
            )
            reply = response.choices[0].message.content

        elif api == "groq":
            response = client.chat.completions.create(
                model=model,
                messages=conversations[session_id],
            )
            reply = response.choices[0].message["content"]

        else:
            reply = "Configuration error: Unsupported API."

        # Add assistant reply to memory
        conversations[session_id].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error during chat request: {e}")
        return jsonify({"error": "Internal server error"}), 500

@flask_app.route("/reset", methods=["POST"])
def reset_conversation():
    """Resets the conversation memory for the user session."""
    session_id = get_session_id()
    if session_id in conversations:
        del conversations[session_id]
    return jsonify({"status": "reset successful"})

###WhatsaApp
    @flask_app.route("/send_whatsapp", methods=["POST"])
def send_whatsapp():
    """Send WhatsApp message via TeleSign API"""
    data = request.get_json()
    phone = data.get("phone")
    message = data.get("message", "Hello from Telesign!")

    # Validate input
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    # Get authentication token
    try:
        token = get_token()
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "x-API-key": os.getenv("TELESIGN_API_KEY", ""),  # Use env variable for security
        "Content-Type": "application/json"
    }

    # Prepare payload
    payload = {
        "phone_number": phone,
        "message": message,
        "message_type": "ARN"  # Adjust to TeleSign WhatsApp API specs
    }

    # Make API request
    try:
        res = requests.post(
            "https://rest-api.telesign.com/v1/messaging",
            headers=headers,
            json=payload,
            timeout=10
        )
        return jsonify(res.json()), res.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flask_app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200