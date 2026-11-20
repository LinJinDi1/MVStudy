"""Local review demo; the authenticated platform host is delivered by ticket 01."""
import os

from flask import Flask
from flask_cors import CORS

from .domains.review.routes import review_api


def create_review_demo() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 512 * 1024
    CORS(app, resources={r"/api/*": {"origins": os.getenv("WEB_ORIGIN", "http://localhost:5173")}})
    app.extensions["review_demo_records"] = {}
    app.register_blueprint(review_api)
    return app
