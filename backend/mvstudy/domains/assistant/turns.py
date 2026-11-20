"""G1 orchestration using the single Agents SDK tool loop."""
import ast
import asyncio
import json
import logging

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


def contains_source(message):
    if not isinstance(message, str):
        return False
    if "```" in message or "~~~" in message:
        return True
    try:
        tree = ast.parse(message)
    except SyntaxError:
        return False
    return any(not isinstance(node, ast.Expr) or
               not isinstance(node.value, (ast.Name, ast.Constant)) for node in tree.body)


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
        if {"source", "before", "after"} & body.keys() or contains_source(body.get("message")):
            raise AssistantError("local_review_required", "粘贴源码及差异请使用本地评审入口。")
        allowed = {"message", "intent", "class_id", "file_id", "input_file_id", "algorithm_id", "algorithm_version", "params", "case_id", "version", "run_id", "submission_id", "from", "to"}
        if body.keys() - allowed:
            raise AssistantError("invalid_params", "请求包含未知字段。")
        if "intent" in body and (not isinstance(body["intent"], str) or body["intent"] not in TOOLS):
            raise AssistantError("unsupported_intent", "不支持该操作。")
        validate({key: value for key, value in body.items() if key != "intent"})
        if "message" not in body:
            raise AssistantError("invalid_params", "请提供 message。")

        async def run():
            run_task = None

            async def call_provider(name, params):
                status, run_id = "failed", None
                try:
                    result = await tools[name](actor, **params)
                    status, run_id = "succeeded", result.get("run_id")
                    return result
                finally:
                    logger.info("tool.finished", extra={"tool_name": name, "status": status, "run_id": run_id})

            async def dispatch(intent, params):
                nonlocal run_task
                name, fields = TOOLS[intent]
                allowed_fields = set(fields + OPTIONAL.get(intent, ()))
                if not isinstance(params, dict) or params.keys() - allowed_fields:
                    raise AssistantError("invalid_params", "工具参数包含未知字段。")
                validate(params)
                params.update({key: body[key] for key in allowed_fields if key in body})
                missing = [key for key in fields if key not in params]
                if missing:
                    return {"intent": intent, "state": "needs_input", "missing": missing,
                            "message": "请补充：" + "、".join(missing)}
                if name not in tools:
                    raise AssistantError("service_unavailable", "工具尚未接入。", 503)
                if intent == "run":
                    if run_task is None:
                        run_task = asyncio.create_task(call_provider(name, params))
                    result = await run_task
                else:
                    result = await call_provider(name, params)
                return {"intent": intent, "state": "submitted" if intent == "run" else "completed", "result": result}

            if "intent" in body:
                intent = body["intent"]
                fields = TOOLS[intent][1] + OPTIONAL.get(intent, ())
                params = {key: body[key] for key in fields if key in body}
                if intent == "question":
                    params["question"] = body["message"]
                return await dispatch(intent, params)
            if model is None:
                raise AssistantError("service_unavailable", "模型尚未配置。", 503)
            sdk_tools = []
            tool_results = []
            for intent, (name, fields) in TOOLS.items():
                async def invoke(_context, arguments, _intent=intent):
                    try:
                        params = json.loads(arguments)
                    except (TypeError, ValueError):
                        raise AssistantError("invalid_params", "工具参数必须是 JSON 对象。") from None
                    output = await dispatch(_intent, params)
                    tool_results.append(output)
                    return json.dumps(output)
                schema = {"type": "object", "properties": {
                    key: {"type": "integer" if key == "version" else "object" if key == "params" else "string"} for key in fields + OPTIONAL.get(intent, ())
                }, "required": [], "additionalProperties": False}
                sdk_tools.append(FunctionTool(name=name, description=intent,
                                              params_json_schema=schema, on_invoke_tool=invoke, strict_json_schema=False))
            agent = Agent(name="Teaching assistant", model=model, tools=sdk_tools,
                          instructions="Select the teaching tool for the request. Never execute scripts.",
                          model_settings=ModelSettings(parallel_tool_calls=False),
                          tool_use_behavior="stop_on_first_tool")
            await Runner.run(agent, json.dumps(body), max_turns=2,
                                      run_config=RunConfig(tracing_disabled=True))
            if not tool_results:
                raise AssistantError("unsupported_intent", "请选择问答、运行、进度、评审或班级统计。")
            return tool_results[0]

        try:
            return jsonify(asyncio.run(asyncio.wait_for(run(), timeout=timeout_s)))
        except AssistantError:
            raise
        except ModelBehaviorError:
            raise AssistantError("unsupported_intent", "模型选择了未登记的工具或无效操作。") from None
        except Exception:
            raise AssistantError("service_unavailable", "工具或模型暂不可用，请保留输入。", 503) from None

    return api

