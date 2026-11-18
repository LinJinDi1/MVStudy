"""Standalone MVP API. Reviews source text only; it never executes submissions."""
from __future__ import annotations

import ast
import difflib
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from pyflakes.checker import Checker
from pyflakes.messages import UndefinedName

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("WEB_ORIGIN", "http://localhost:5173")}})
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024

ALLOWED_LANGUAGES = {"python", "javascript", "typescript", "java", "c", "cpp"}
reviews: dict[str, dict[str, Any]] = {}


def _finding(line: int, severity: str, title: str, detail: str, rule: str, suggestion: str) -> dict[str, Any]:
    return {"id": str(uuid.uuid4()), "rule": rule, "severity": severity, "file": "submission",
            "line_start": line, "line_end": line, "title": title, "description": detail,
            "suggestion": suggestion, "confidence": 0.65}


def _check_python(source: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(source, filename="submission.py")
    except SyntaxError as error:
        message = error.msg
        if "was never closed" in message:
            title = "括号未闭合"
            detail = "这一行有一个左括号，后面找不到与它配对的右括号。"
            suggestion = "从标出的左括号往后找，补上对应的右括号后再评审。"
        elif message.startswith("unmatched ") or "does not match opening parenthesis" in message:
            title = "括号不匹配"
            detail = "这里的右括号找不到同类型且位置正确的左括号。"
            suggestion = "按从内到外的顺序核对 ()、[] 或 {} 是否正确闭合。"
        else:
            return [_finding(
                error.lineno or 1, "warning", "Python 语法错误", message,
                "python/syntax-error", "先修正语法，再检查是否有未定义的名称。",
            )]
        return [_finding(error.lineno or 1, "warning", title, detail, "python/bracket-mismatch", suggestion)]
    except ValueError:
        return [_finding(
            1, "warning", "无法解析代码文本", "源码包含 Python 解析器无法处理的字符。",
            "python/syntax-error", "请重新复制或保存为纯文本后再评审。",
        )]

    findings = []
    for message in Checker(tree, filename="submission.py").messages:
        if isinstance(message, UndefinedName):
            name = message.message_args[0]
            findings.append(_finding(
                message.lineno, "warning", "使用了未定义的名称",
                f"此处使用了 「{name}」，但在提交代码的可见范围内找不到它的定义。",
                "python/undefined-name",
                "先检查拼写，再确认是否需要声明变量、补充函数参数或导入对应名称。",
            ))
    return findings


def review_source(source: str, language: str) -> list[dict[str, Any]]:
    """Analyze source text without importing or executing the submitted code."""
    findings = _check_python(source) if language == "python" else []
    for number, line in enumerate(source.splitlines(), start=1):
        if len(line) > 120:
            findings.append(_finding(
                number, "info", "行长度较长", "该行超过120个字符。",
                "style/line-length", "可考虑拆分这行以提升可读性。",
            ))
    return findings


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
