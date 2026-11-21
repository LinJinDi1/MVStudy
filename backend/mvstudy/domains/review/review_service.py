"""Static source checks shared by the review domain and its standalone launcher."""
from __future__ import annotations

import ast
import uuid
from typing import Any

from pyflakes.checker import Checker
from pyflakes.messages import UndefinedName

RULE_VERSION = "1.0"


def _finding(
    line: int, severity: str, title: str, detail: str, rule: str, suggestion: str,
    *, category: str = "potential_correctness", filename: str = "submission.py",
) -> dict[str, Any]:
    return {"id": str(uuid.uuid4()), "rule": rule, "category": category, "severity": severity, "file": filename,
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
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(_finding(
                node.lineno, "warning", "捕获范围过宽",
                "裸 except 会捕获所有异常，可能掩盖真正的错误。",
                "python/bare-except", "根据预期错误指定异常类型，例如 except ValueError:。",
            ))

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
                category="style", filename="submission.py" if language == "python" else "submission",
            ))
    return findings
