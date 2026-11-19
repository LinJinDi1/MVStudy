"""Standalone MVP API. Reviews source text only; it never executes submissions."""
from __future__ import annotations

import difflib
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

if __package__:
    from .review_service import review_source
else:
    from review_service import review_source

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("WEB_ORIGIN", "http://localhost:5173")}})
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024

ALLOWED_LANGUAGES = {"python", "javascript", "typescript", "java", "c", "cpp"}
reviews: dict[str, dict[str, Any]] = {}


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "task-seven-review-api"})


@app.post("/api/reviews")
def create_review():
    body = request.get_json(silent=True) or {}
    source = body.get("source")
    language = body.get("language", "python")
    if not isinstance(source, str) or not source.strip():
        return jsonify({"error": {"code": "invalid_source", "message": "source 必须是非空文本。"}}), 400
    if language not in ALLOWED_LANGUAGES:
        return jsonify({"error": {"code": "unsupported_language", "message": "暂不支持该语言。"}}), 400
    findings = review_source(source, language)
    review_id = str(uuid.uuid4())
    result = {"review_id": review_id, "submission_id": body.get("submission_id"), "status": "completed",
              "language": language, "dimensions": ["static_correctness_hints", "style"], "findings": findings,
              "summary": f"静态检查完成，发现 {len(findings)} 项可供参考的建议。",
              "is_ai_assisted": False, "execution_performed": False,
              "created_at": datetime.now(timezone.utc).isoformat()}
    reviews[review_id] = result
    return jsonify(result), 201


@app.get("/api/reviews/<review_id>")
def get_review(review_id: str):
    result = reviews.get(review_id)
    if result is None:
        return jsonify({"error": {"code": "not_found", "message": "评审记录不存在。"}}), 404
    return jsonify(result)


@app.post("/api/reviews/diff")
def compare_submissions():
    body = request.get_json(silent=True) or {}
    before, after = body.get("before"), body.get("after")
    if not isinstance(before, str) or not isinstance(after, str):
        return jsonify({"error": {"code": "invalid_diff", "message": "before 和 after 必须是文本。"}}), 400
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), fromfile="提交前", tofile="提交后", lineterm=""))
    return jsonify({"summary": f"共 {sum(x.startswith('+') and not x.startswith('+++') for x in diff)} 行新增，{sum(x.startswith('-') and not x.startswith('---') for x in diff)} 行删除。",
                    "diff": diff[:1000]})


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": {"code": "payload_too_large", "message": "请求内容不能超过512KB。"}}), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
