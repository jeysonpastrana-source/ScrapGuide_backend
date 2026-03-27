from __future__ import annotations

import os

from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS

from app.db import init_db
from app.routers.auth import auth_bp
from app.routers.analyzer import analyzer_bp

app = Flask(__name__)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "ScrapGuide API",
        "description": "API para autenticacion JWT y analisis de scraping de ScrapGuide.",
        "version": "0.1.0",
    },
    "schemes": ["https", "http"],
}

Swagger(app, template=swagger_template)

CORS(
    app,
    resources={
        r"/*": {
            "origins": ["https://scrap-guide-frontend.vercel.app"]
        }
    },
    supports_credentials=True,
)

# 🔥 FIX preflight
@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 200

# 🔥 INIT DB (compatible con Flask 3)
try:
    init_db()
    print("✅ DB inicializada")
except Exception as e:
    print("❌ DB error:", e)

app.register_blueprint(auth_bp)
app.register_blueprint(analyzer_bp)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# 🔥 DEBUG GLOBAL
@app.errorhandler(Exception)
def handle_error(e):
    print("🔥 ERROR:", e)
    return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        debug=False,
    )
