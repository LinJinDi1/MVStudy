"""G1 orchestration using the single Agents SDK tool loop."""
import asyncio
import json
import logging
import re

from agents import Agent, FunctionTool, ModelSettings, RunConfig, Runner
from flask import Blueprint, jsonify, request
from agents.exceptions import AgentsException, ModelBehaviorError


logger = logging.getLogger(__name__)

TOOLS = {
    "run_status": ("get_run", ("run_id",)),
    "review": ("review_submission", ("submission_id", "file_id")),
    "analytics": ("class_summary", ("class_id", "from", "to")),
    "question": ("ask_course", ("question", "case_id", "version")),
    "run": ("run_algorithm", ("case_id", "version", "algorithm_id", "algorithm_version", "input_file_id", "params")),
}

OPTIONAL = {"question": ("class_id", "file_id"), "run": ("class_id",)}


class AssistantError(AgentsException):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def require_prose(message):
    if re.search(r"脚本|命令|\b(script|shell|command|powershell|bash)\b", message, re.IGNORECASE):
        raise AssistantError("unsupported_intent", "不执行任意脚本或命令；请从课程选择登记算法。")
    # Deliberately bounded single-line prose, not a detector for arbitrary source code.
    prose = re.fullmatch(r"[a-zA-Z0-9\u3400-\u9fff ,.!?，。！？、+*%=<>≤≥≠×÷−-]+", message)
    syntax = re.search(
        r"\b(import|def|lambda|const|let|var|function|async|await|exec|eval|throw|return)\b"
        r"|^\s*(if|for|while|class|try|raise|pass|break|continue|yield)\b"
        r"|[a-zA-Z0-9]\.[a-zA-Z]|(?<![<>=!])=(?!=)", message)
    if not prose or syntax:
        raise AssistantError("local_review_required", "请用单行自然语言描述问题；源码、差异或含代码的说明请使用本地评审入口。")


def validate(params):
    for key, value in params.items():
        if key == "version":
            valid = type(value) is int and value > 0
        elif key == "params":
            valid = isinstance(value, dict)
        else:
            valid = isinstance(value, str) and bool(value.strip())
        if not valid:
            raise AssistantError("invalid_params", f"字段 {key} 格式无效。")


def create_assistant_blueprint(actor_provider, tools, model=None, *, timeout_s=30):
    api = Blueprint("assistant", __name__, url_prefix="/api")

    @api.errorhandler(AssistantError)
    def assistant_error(error):
        return jsonify({"error": {"code": error.code, "message": str(error)}}), error.status

    @api.post("/assistant/turns")
    def turn():
        actor = actor_provider()
        if actor is None:
            raise AssistantError("unauthenticated", "请登录。", 401)
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise AssistantError("invalid_json", "请求内容必须是 JSON 对象。")
        if {"source", "before", "after"} & body.keys():
            raise AssistantError("local_review_required", "粘贴源码及差异请使用本地评审入口。")
        allowed = {"message", "intent", "class_id", "file_id", "input_file_id", "algorithm_id", "algorithm_version", "params", "case_id", "version", "run_id", "submission_id", "from", "to"}
        if body.keys() - allowed:
            raise AssistantError("invalid_params", "请求包含未知字段。")
        if "intent" in body and (not isinstance(body["intent"], str) or body["intent"] not in TOOLS):
            raise AssistantError("unsupported_intent", "不支持该操作。")
        validate({key: value for key, value in body.items() if key != "intent"})
        if "message" not in body:
            raise AssistantError("invalid_params", "请提供 message。")
        require_prose(body["message"])

        async def run():
            async def call_provider(name, params):
                status, run_id = "failed", None
                try:
                    result = await tools[name](actor, **params)
                    status, run_id = "succeeded", result.get("run_id")
                    return result
                finally:
                    logger.info("tool.finished", extra={"tool_name": name, "status": status, "run_id": run_id})

            async def dispatch(intent):
                name, fields = TOOLS[intent]
                allowed_fields = set(fields + OPTIONAL.get(intent, ()))
                params = {key: body[key] for key in allowed_fields if key in body}
                if intent == "question":
                    params["question"] = body["message"]
                missing = [key for key in fields if key not in params]
                if missing:
                    return {"intent": intent, "state": "needs_input", "missing": missing,
                            "message": "请选择图片" if "input_file_id" in missing else "请补充：" + "、".join(missing)}
                if name not in tools:
                    raise AssistantError("service_unavailable", "工具尚未接入。", 503)
                result = await call_provider(name, params)
                return {"intent": intent, "state": "submitted" if intent == "run" else "completed", "result": result}

            if "intent" in body:
                return await dispatch(body["intent"])
            if model is None:
                raise AssistantError("service_unavailable", "模型尚未配置。", 503)
            sdk_tools = []
            selections = []
            for intent, (name, fields) in TOOLS.items():
                async def invoke(_context, arguments, _intent=intent):
                    try:
                        params = json.loads(arguments)
                    except (TypeError, ValueError):
                        raise AssistantError("invalid_params", "工具参数必须是 JSON 对象。") from None
                    allowed_fields = set(TOOLS[_intent][1] + OPTIONAL.get(_intent, ()))
                    if not isinstance(params, dict) or params.keys() - allowed_fields:
                        raise AssistantError("invalid_params", "工具参数包含未知字段。")
                    validate(params)
                    selections.append((_intent, params))
                    return "Selection recorded; no provider has been called."
                schema = {"type": "object", "properties": {
                    key: {"type": "integer" if key == "version" else "object" if key == "params" else "string"} for key in fields + OPTIONAL.get(intent, ())
                }, "required": [], "additionalProperties": False}
                sdk_tools.append(FunctionTool(name=name, description=intent,
                                              params_json_schema=schema, on_invoke_tool=invoke, strict_json_schema=False))
            agent = Agent(name="Teaching assistant", model=model, tools=sdk_tools,
                          instructions="Select exactly one teaching tool with empty arguments. The server supplies user selections. Never execute scripts.",
                          model_settings=ModelSettings(parallel_tool_calls=False),
                          tool_use_behavior="stop_on_first_tool")
            await Runner.run(agent, body["message"], max_turns=2,
                                      run_config=RunConfig(tracing_disabled=True))
            if not selections or any(selection != selections[0] for selection in selections):
                raise AssistantError("unsupported_intent", "请选择问答、运行、进度、评审或班级统计。")
            return await dispatch(selections[0][0])

        try:
            return jsonify(asyncio.run(asyncio.wait_for(run(), timeout=timeout_s)))
        except AssistantError:
            raise
        except ModelBehaviorError:
            raise AssistantError("unsupported_intent", "模型选择了未登记的工具或无效操作。") from None
        except Exception:
            raise AssistantError("service_unavailable", "工具或模型暂不可用，请保留输入。", 503) from None

    return api

