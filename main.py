from __future__ import annotations

import os

from flasgger import Swagger
from flask import Flask, jsonify
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
    resources={r"/*": {"origins": ["https://scrap-guide-frontend-uyq9.vercel.app/"]}},
    supports_credentials=True,
)

app.register_blueprint(auth_bp)
app.register_blueprint(analyzer_bp)

# Ensure required tables exist in PostgreSQL.
init_db()


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
