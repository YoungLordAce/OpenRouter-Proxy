from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import time
import json
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://janitorai.com"]}})  # ✅ Allow JanitorAI to connect

# OpenRouter API key (Set this as an environment variable in Docker)
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default AI parameters
AI_SETTINGS = {
    "min_p": 0.17,
    "top_p": 0.92,
    "top_k": 75,
    "repetition_penalty": 1.05,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "message": "OpenRouter Reverse Proxy is running."})

@app.route("/update_settings", methods=["POST"])
def update_settings():
    global AI_SETTINGS
    AI_SETTINGS = {key: float(request.form[key]) for key in AI_SETTINGS.keys()}
    return jsonify({"status": "success", "new_settings": AI_SETTINGS})

@app.route("/models", methods=["GET"])
def modelcheck():
    return {"object": "list",
            "data": [{
                "id": "Use Openrouter website setting",
                "object": "model",
                "created": 1685474247,
                "owned_by": "openai",
                "permission": [{}],
                "root": "Use Openrouter website setting"
            }]}

@app.route("/chat/completions", methods=["POST", "OPTIONS"])
@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def chat_completions():
    if request.method == "OPTIONS":
        response = jsonify({"message": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "https://janitorai.com")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response, 200

    if not API_KEY:
        return jsonify({"error": "API key is missing. Set the OPENROUTER_API_KEY environment variable."}), 500

    data = request.json
    if "model" not in data:
        data["model"] = None

    for key, value in AI_SETTINGS.items():
        if key not in data:
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