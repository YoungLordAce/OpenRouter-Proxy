from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import json
import logging
import pprint

def load_env_var(key, default=None, required=False):
    """Loads environment variables, optionally making them required."""
    value = os.getenv(key, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value

def load_config():
    """Loads AI settings from config.json."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "default_model": None,  # Keep None so OpenRouter uses account default
            "models": [],  # Optional list of fallback models
            "min_p": 0.17,
            "top_p": 0.92,
            "top_k": 75,
            "repetition_penalty": 1.05,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

# Load essential environment variables
API_KEY = load_env_var("OPENROUTER_API_KEY", required=True)
ALLOWED_ORIGINS = load_env_var("ALLOWED_ORIGINS", "https://janitorai.com")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Flask App Setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS.split(",")}})
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "message": "OpenRouter Reverse Proxy is running."})

@app.route("/update_settings", methods=["POST"])
def update_settings():
    """Update AI settings dynamically without restarting the server."""
    try:
        data = request.json
        settings = load_config()
        settings.update(data)
        with open("config.json", "w") as f:
            json.dump(settings, f, indent=4)
        logging.info(f"Updated AI_SETTINGS: {json.dumps(settings, indent=4)}")
        return jsonify({"status": "success", "new_settings": settings})
    except Exception as e:
        return jsonify({"error": f"Invalid settings update: {str(e)}"}), 400

@app.route("/models", methods=["GET"])
def modelcheck():
    """Return the default model setting."""
    settings = load_config()
    return {"object": "list", "data": [{"id": settings.get("default_model", "Use OpenRouter website setting")}]}

@app.route("/chat/completions", methods=["POST", "OPTIONS"])
@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def chat_completions():
    """Proxy requests to OpenRouter."""
    if request.method == "OPTIONS":
        response = jsonify({"message": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "https://janitorai.com")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response, 200
    
    if not API_KEY:
        return jsonify({"error": "API key is missing. Set the OPENROUTER_API_KEY environment variable."}), 500
    
    data = request.json or {}
    settings = load_config()  # Reload config every request
    
    # 🚀 Log full incoming request data (Only uncomment these for debugging purposes)
    # logging.info(f"RAW REQUEST DATA: {request.data.decode('utf-8')}")
    # logging.info(f"PARSED REQUEST DATA:\n{pprint.pformat(data)}")
    
    # Ensure the model is correctly applied from config.json, even if JanitorAI sends an empty string
    if "model" not in data or not data["model"].strip():  # Treat empty string as missing
        if settings.get("default_model"):
            data["model"] = settings["default_model"]
        else:
            data.pop("model", None)  # Remove model field completely if None
    
    # Add fallback models if defined
    if settings.get("models"):
        data["models"] = settings["models"]
    
    for key, value in settings.items():
        if key not in data and key not in ["default_model", "models"]:
            data[key] = value
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://janitorai.com/"
    }
    
    stream = data.get("stream", False)
    config = {"url": API_URL, "headers": headers, "json": data}
    
    try:
        if stream:
            return Response(stream_with_context(stream_response(config)), content_type="text/event-stream")
        else:
            response = requests.post(**config, timeout=60)
            response.raise_for_status()
            json_response = jsonify(response.json())
            json_response.headers.add("Access-Control-Allow-Origin", "https://janitorai.com")
            return json_response
    except requests.exceptions.RequestException as error:
        return jsonify({"error": f"Request to OpenRouter failed: {error}"}), 500

@app.route("/v1", methods=["POST", "OPTIONS", "GET"])
@app.route("/v1/", methods=["POST", "OPTIONS", "GET"])
def v1_redirect():
    return jsonify({"error": "Invalid endpoint. Use /v1/chat/completions instead."}), 404

def stream_response(config):
    try:
        with requests.post(**config, stream=True, timeout=60) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    yield f"{line.decode('utf-8')}\n\n"
    except requests.exceptions.Timeout:
        yield "Error: Request timed out\n\n"
    except requests.exceptions.RequestException as error:
        yield f"Error: {error}\n\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)