"""Flask API اختياري."""
import os
import threading
import logging
from flask import Flask, jsonify
from flask_cors import CORS

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(32).hex())
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")}})


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


def start_api_server(host: str = None, port: int = None, debug: bool = None):
    from config import API_HOST, API_PORT, API_DEBUG

    host = host or API_HOST
    port = port or API_PORT
    debug = API_DEBUG if debug is None else debug

    def run():
        app.run(host=host, port=port, debug=debug, use_reloader=False)

    threading.Thread(target=run, daemon=True).start()
    logger.info("API %s:%s", host, port)
