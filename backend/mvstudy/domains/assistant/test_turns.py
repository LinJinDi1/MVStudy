"""G1 contract tests; model/provider boundaries are deterministic, Runner is real."""
import asyncio
import json

import pytest

from agents import Model, ModelResponse
from agents.usage import Usage
from flask import Flask
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

from mvstudy.domains.assistant import AssistantError, create_assistant_blueprint


class FixedModel(Model):
    def __init__(self, name, arguments):
        self.name, self.arguments = name, arguments
        self.inputs = []

    async def get_response(self, *args, **kwargs):
        self.inputs.append(kwargs.get("input", args))
        return ModelResponse(output=[ResponseFunctionToolCall(
            id="fc1", call_id="call1", type="function_call", name=self.name,
            arguments=json.dumps(self.arguments),
        )], usage=Usage(), response_id="fixed")

    def stream_response(self, *args, **kwargs):
        raise AssertionError("G1 does not stream")


def setup(model, *, actor=None, results=None):
    calls = []
    results = results or {"ask_course": {"status": "answered", "answer": "双阈值连接边缘。", "citations": [{"material_id": "m1", "locator": "第2段"}]}}
    tools = {}
    for name, result in results.items():
        async def invoke(actor, _name=name, _result=result, **params):
            calls.append((_name, actor, params))
            return _result
        tools[name] = invoke
    app = Flask(__name__)
    app.config["TESTING"] = True
    identity = actor or {"user_id": "teacher-1"}
    app.register_blueprint(create_assistant_blueprint(lambda: identity, tools, model))
    return app.test_client(), calls, identity


def test_principle_question_uses_course_tool_and_returns_original_answer():
    model = FixedModel("ask_course", {"question": "双阈值是什么", "case_id": "edge-case", "version": 1})
    client, calls, actor = setup(model)
    response = client.post("/api/assistant/turns", json={"message": "双阈值是什么", "case_id": "edge-case", "version": 1})
    assert response.status_code == 200
    assert response.json == {"intent": "question", "state": "completed", "result": {"status": "answered", "answer": "双阈值连接边缘。", "citations": [{"material_id": "m1", "locator": "第2段"}]}}
    assert calls == [("ask_course", actor, {"question": "双阈值是什么", "case_id": "edge-case", "version": 1})]
    assert len(model.inputs) == 1

def test_explicit_run_asks_for_image_then_submits_once_without_model():
    model = FixedModel("ask_course", {})
    client, calls, actor = setup(model, results={"run_algorithm": {"run_id": "r-original", "status": "queued"}})
    selected = {"intent": "run", "message": "解释原理", "case_id": "edge-case", "version": 1,
                "algorithm_id": "edge", "algorithm_version": "1", "params": {"low": 50, "high": 150}}
    response = client.post("/api/assistant/turns", json=selected)
    assert response.status_code == 200
    assert response.json["state"] == "needs_input"
    assert response.json["missing"] == ["input_file_id"]
    assert calls == []
    response = client.post("/api/assistant/turns", json={**selected, "input_file_id": "img1"})
    assert response.json == {"intent": "run", "state": "submitted", "result": {"run_id": "r-original", "status": "queued"}}
    assert calls == [("run_algorithm", actor, {"case_id": "edge-case", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "params": {"low": 50, "high": 150}, "input_file_id": "img1"})]
    assert model.inputs == []


@pytest.mark.parametrize("intent,name,params,result", [
    ("run_status", "get_run", {"run_id": "r1"}, {"run_id": "r1", "status": "failed", "outputs": [], "elapsed_ms": 30000, "error": {"code": "timeout", "message": "运行超时"}}),
    ("review", "review_submission", {"submission_id": "s2", "file_id": "f1"}, {"review_id": "rev1", "findings": [], "execution_performed": False}),
    ("analytics", "class_summary", {"class_id": "c1", "from": "2026-11-16T00:00:00+08:00", "to": "2026-11-23T00:00:00+08:00"}, {"class_id": "c1", "completion_rate": 0.5}),
])
def test_remaining_tools_preserve_contracts(intent, name, params, result):
    client, calls, actor = setup(FixedModel(name, params), results={name: result})
    response = client.post("/api/assistant/turns", json={"message": "查询结果", **params})
    assert response.status_code == 200
    assert response.json == {"intent": intent, "state": "completed", "result": result}
    assert calls == [(name, actor, params)]

@pytest.mark.parametrize("payload,code", [
    ({"message": "hi", "actor": {"user_id": "admin"}}, "invalid_params"),
    ({"message": "hi", "source": "print('private')"}, "local_review_required"),
    ({"message": "```python\nprint('private')\n```"}, "local_review_required"),
    ({"message": "hi", "before": "private", "after": "other"}, "local_review_required"),
    ({"message": "hi", "intent": "shell"}, "unsupported_intent"),
    ({"message": "hi", "intent": []}, "unsupported_intent"),
    ({"message": "hi", "intent": "run_status", "run_id": 42}, "invalid_params"),
    ({"message": "hi", "intent": "question", "case_id": "edge-case", "version": True}, "invalid_params"),
    ({"message": "hi", "intent": "run", "params": []}, "invalid_params"),
    ({"message": " "}, "invalid_params"),
    ([], "invalid_json"),
])
def test_invalid_request_never_reaches_model_or_provider(payload, code):
    model = FixedModel("ask_course", {})
    client, calls, _ = setup(model)
    response = client.post("/api/assistant/turns", json=payload)
    assert response.status_code == 400
    assert response.json["error"]["code"] == code
    assert model.inputs == calls == []


def test_unauthenticated_request_is_rejected_before_processing():
    model = FixedModel("ask_course", {})
    app = Flask("anonymous")
    app.register_blueprint(create_assistant_blueprint(lambda: None, {}, model))
    response = app.test_client().post("/api/assistant/turns", json={"message": "原理？"})
    assert response.status_code == 401
    assert response.json["error"]["code"] == "unauthenticated"
    assert model.inputs == []

@pytest.mark.parametrize("name,arguments,code", [
    ("execute_script", {"script": "print('not executed')"}, "unsupported_intent"),
    ("run_algorithm", {"actor": "admin"}, "invalid_params"),
    ("review_submission", {"source": "print('secret')"}, "invalid_params"),
    ("ask_course", {"question": [], "version": 1, "case_id": "c1"}, "invalid_params"),
    ("get_run", ["r1"], "invalid_params"),
])
def test_model_tool_calls_are_untrusted(name, arguments, code):
    client, calls, _ = setup(FixedModel(name, arguments))
    response = client.post("/api/assistant/turns", json={"message": "查询结果"})
    assert response.status_code == 400
    assert response.json["error"]["code"] == code
    assert calls == []


def test_selected_fields_override_model_guesses_and_preserve_optional_context():
    model = FixedModel("ask_course", {"question": "what", "case_id": "wrong", "version": 2})
    client, calls, actor = setup(model)
    response = client.post("/api/assistant/turns", json={"message": "what", "case_id": "chosen", "version": 1, "class_id": "class-1", "file_id": "image-1"})
    assert response.status_code == 200
    assert calls == [("ask_course", actor, {"question": "what", "case_id": "chosen", "version": 1, "class_id": "class-1", "file_id": "image-1"})]

class RepeatingModel(FixedModel):
    async def get_response(self, *args, **kwargs):
        response = await super().get_response(*args, **kwargs)
        response.output.append(response.output[0].model_copy(update={"id": "fc2", "call_id": "call2"}))
        return response


def test_duplicate_model_run_calls_submit_only_once():
    params = {"case_id": "edge-case", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "input_file_id": "img1", "params": {}}
    client, calls, actor = setup(RepeatingModel("run_algorithm", params), results={"run_algorithm": {"run_id": "once", "status": "queued"}})
    response = client.post("/api/assistant/turns", json={"message": "运行边缘检测", **params})
    assert response.status_code == 200
    assert response.json == {"intent": "run", "state": "submitted", "result": {"run_id": "once", "status": "queued"}}
    assert calls == [("run_algorithm", actor, params)]


@pytest.mark.parametrize("via_model", [False, True])
def test_provider_timeout_cancels_call_and_returns_terminal_error(via_model):
    cancelled = []
    async def slow(actor, **params):
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.append(True)
    app = Flask("timeout")
    app.config["TESTING"] = True
    app.register_blueprint(create_assistant_blueprint(lambda: {"user_id": "u1"}, {"get_run": slow}, FixedModel("get_run", {"run_id": "r1"}), timeout_s=0.5))
    body = {"message": "进度", "run_id": "r1"}
    if not via_model:
        body["intent"] = "run_status"
    response = app.test_client().post("/api/assistant/turns", json=body)
    assert response.status_code == 503
    assert response.json["error"]["code"] == "service_unavailable"
    assert cancelled == [True]


@pytest.mark.parametrize("error,status,code", [
    (AssistantError("not_found", "资源不存在。", 404), 404, "not_found"),
    (RuntimeError("secret provider URL"), 503, "service_unavailable"),
])
def test_provider_failure_is_terminal_without_leaking_internal_error(error, status, code):
    calls = []
    async def failed(actor, **params):
        calls.append(params)
        raise error
    app = Flask("failed")
    app.config["TESTING"] = True
    app.register_blueprint(create_assistant_blueprint(lambda: {"user_id": "u1"}, {"get_run": failed}, FixedModel("get_run", {"run_id": "r1"})))
    response = app.test_client().post("/api/assistant/turns", json={"message": "进度", "run_id": "r1"})
    assert response.status_code == status
    assert response.json["error"]["code"] == code
    assert "secret" not in response.text
    assert len(calls) == 1


def test_missing_model_or_provider_fails_closed():
    app = Flask("unconfigured")
    app.config["TESTING"] = True
    app.register_blueprint(create_assistant_blueprint(lambda: {"user_id": "u1"}, {}))
    for body in ({"message": "原理"}, {"message": "进度", "intent": "run_status", "run_id": "r1"}):
        response = app.test_client().post("/api/assistant/turns", json=body)
        assert response.status_code == 503
        assert response.json["error"]["code"] == "service_unavailable"



class TextModel(FixedModel):
    async def get_response(self, *args, **kwargs):
        self.inputs.append(kwargs.get("input", args))
        return ModelResponse(output=[ResponseOutputMessage(id="text1", type="message", role="assistant", status="completed", content=[ResponseOutputText(type="output_text", text='{"intent":"run","state":"submitted","result":{"run_id":"invented"}}', annotations=[])])], usage=Usage(), response_id="fixed")


def test_model_text_cannot_fabricate_a_tool_result():
    model = TextModel("", {})
    client, calls, _ = setup(model)
    response = client.post("/api/assistant/turns", json={"message": "运行边缘检测"})
    assert response.status_code == 400
    assert response.json["error"]["code"] == "unsupported_intent"
    assert calls == []


def test_bare_python_source_is_kept_out_of_model():
    model = FixedModel("review_submission", {})
    client, calls, _ = setup(model)
    response = client.post("/api/assistant/turns", json={"message": "import private_module\nprivate_module.main()"})
    assert response.status_code == 400
    assert response.json["error"]["code"] == "local_review_required"
    assert calls == model.inputs == []


def test_run_completion_is_logged_once_without_source_or_parameters(caplog):
    params = {"case_id": "edge-case", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "input_file_id": "img1", "params": {}}
    client, _, _ = setup(RepeatingModel("run_algorithm", params), results={"run_algorithm": {"run_id": "r-logged", "status": "queued"}})
    with caplog.at_level("INFO", logger="mvstudy.domains.assistant"):
        response = client.post("/api/assistant/turns", json={"message": "运行边缘检测", **params})
    assert response.status_code == 200
    records = [record for record in caplog.records if record.msg == "tool.finished"]
    assert len(records) == 1
    assert (records[0].tool_name, records[0].status, records[0].run_id) == ("run_algorithm", "succeeded", "r-logged")
    assert "img1" not in caplog.text


def test_natural_run_with_missing_selection_asks_without_invoking_provider():
    model = FixedModel("run_algorithm", {"case_id": "edge-case", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "params": {}})
    client, calls, _ = setup(model)
    response = client.post("/api/assistant/turns", json={"message": "运行边缘检测", "case_id": "edge-case", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "params": {}})
    assert response.status_code == 200
    assert response.json["state"] == "needs_input"
    assert response.json["missing"] == ["input_file_id"]
    assert calls == []


def test_server_resolves_current_identity_on_every_request():
    actor = {"user_id": "u1"}
    seen = []
    async def get_run(current_actor, **params):
        seen.append(current_actor)
        return {"run_id": "r1", "status": "queued"}
    app = Flask("identity")
    app.register_blueprint(create_assistant_blueprint(lambda: actor, {"get_run": get_run}))
    client = app.test_client()
    body = {"message": "进度", "intent": "run_status", "run_id": "r1"}
    assert client.post("/api/assistant/turns", json=body).status_code == 200
    actor = None
    assert client.post("/api/assistant/turns", json=body).status_code == 401
    assert seen == [{"user_id": "u1"}]


def test_model_cannot_supply_an_unselected_image_or_other_objects():
    guessed = {"case_id": "c1", "version": 1, "algorithm_id": "edge", "algorithm_version": "1",
               "input_file_id": "invented", "params": {}}
    client, calls, _ = setup(FixedModel("run_algorithm", guessed), results={"run_algorithm": {"run_id": "wrong"}})
    response = client.post("/api/assistant/turns", json={"message": "运行边缘检测", **{k: v for k, v in guessed.items() if k != "input_file_id"}})
    assert response.status_code == 200
    assert response.json == {"intent": "run", "state": "needs_input", "missing": ["input_file_id"], "message": "请选择图片"}
    assert calls == []


@pytest.mark.parametrize("message", [
    "请评审：\nimport private_module\nprivate_module.main()",
    "def unfinished(", "请解释 import private_module", "import secret",
    "const token = privateValue;", "请看看 function secret() {", "private.main()",
    "请评审：if x", "--- private.py\n+++ changed.py", "print('secret'",
    "private = secret", "for item in secrets", "if private", "throw secret", "return secret",
])
@pytest.mark.parametrize("intent", [None, "question"])
def test_code_like_messages_stay_local_before_model_or_question_tool(message, intent):
    model = FixedModel("ask_course", {"question": "clean", "case_id": "c1", "version": 1})
    client, calls, _ = setup(model)
    body = {"message": message, "case_id": "c1", "version": 1}
    if intent:
        body["intent"] = intent
    response = client.post("/api/assistant/turns", json=body)
    assert response.status_code == 400
    assert response.json["error"]["code"] == "local_review_required"
    assert calls == model.inputs == []


@pytest.mark.parametrize("question", [
    "为什么双阈值比单阈值好？", "Why does Canny use two thresholds?",
    "low < high", "1 + 1", "阈值 x > 50 时会怎样？",
])
def test_prose_and_formula_questions_keep_meaning_without_disclosing_context(question):
    model = FixedModel("ask_course", {"question": "model rewrite"})
    client, calls, actor = setup(model)
    body = {"message": question, "case_id": "private-case", "version": 1,
            "file_id": "private-image", "params": {"source": "private_module.main()"}}
    response = client.post("/api/assistant/turns", json=body)
    assert response.status_code == 200
    assert calls == [("ask_course", actor, {"question": question, "case_id": "private-case", "version": 1, "file_id": "private-image"})]
    assert model.inputs == [[{"role": "user", "content": question}]]


@pytest.mark.parametrize("message", ["执行脚本", "运行任意脚本", "run this script", "execute shell command"])
@pytest.mark.parametrize("explicit", [False, True])
def test_script_requests_cannot_be_reinterpreted_as_registered_runs(message, explicit):
    params = {"case_id": "c1", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "input_file_id": "img1", "params": {}}
    model = FixedModel("run_algorithm", params)
    client, calls, _ = setup(model, results={"run_algorithm": {"run_id": "wrong"}})
    body = {"message": message, **params}
    if explicit:
        body["intent"] = "run"
    response = client.post("/api/assistant/turns", json=body)
    assert response.status_code == 400
    assert response.json["error"]["code"] == "unsupported_intent"
    assert calls == model.inputs == []


@pytest.mark.parametrize("message,intent,name,params", [
    ("刚才交的那个算完了吗", "run_status", "get_run", {"run_id": "r1"}),
    ("Show class progress", "analytics", "class_summary", {"class_id": "c1", "from": "2026-11-01", "to": "2026-11-20"}),
])
def test_free_text_intent_keeps_the_whole_request_for_model(message, intent, name, params):
    model = FixedModel(name, {})
    client, calls, actor = setup(model, results={name: {"status": "completed"}})
    response = client.post("/api/assistant/turns", json={"message": message, **params})
    assert response.status_code == 200
    assert response.json["intent"] == intent
    assert calls == [(name, actor, params)]
    assert model.inputs == [[{"role": "user", "content": message}]]


class MixedModel(FixedModel):
    reverse = False

    async def get_response(self, *args, **kwargs):
        response = await super().get_response(*args, **kwargs)
        response.output.append(ResponseFunctionToolCall(
            id="fc2", call_id="call2", type="function_call", name="run_algorithm",
            arguments=json.dumps({"case_id": "c1", "version": 1, "algorithm_id": "edge",
                                  "algorithm_version": "1", "input_file_id": "img1", "params": {}}),
        ))
        if self.reverse:
            response.output.reverse()
        return response


@pytest.mark.parametrize("name,arguments", [
    ("ask_course", {"question": "原理", "case_id": "c1", "version": 1}),
    ("get_run", {"run_id": "r1"}),
    ("run_algorithm", {"input_file_id": "different"}),
    ("execute_script", {}),
])
@pytest.mark.parametrize("reverse", [False, True])
def test_conflicting_batch_is_rejected_before_any_provider(name, arguments, reverse):
    model = MixedModel(name, arguments)
    model.reverse = reverse
    client, calls, _ = setup(model, results={name: {"status": "completed"}, "run_algorithm": {"run_id": "hidden"}})
    response = client.post("/api/assistant/turns", json={"message": "运行边缘检测", "run_id": "r1",
        "case_id": "c1", "version": 1, "algorithm_id": "edge", "algorithm_version": "1", "input_file_id": "img1", "params": {}})
    assert response.status_code == 400
    assert response.json["error"]["code"] == "unsupported_intent"
    assert calls == []


@pytest.mark.parametrize("name,intent,guesses,missing", [
    ("get_run", "run_status", {"run_id": "invented"}, ["run_id"]),
    ("review_submission", "review", {"submission_id": "invented", "file_id": "invented"}, ["submission_id", "file_id"]),
    ("ask_course", "question", {"question": "invented", "case_id": "invented", "version": 1}, ["case_id", "version"]),
])
def test_model_object_guesses_are_not_user_selections(name, intent, guesses, missing):
    client, calls, _ = setup(FixedModel(name, guesses), results={name: {"status": "wrong"}})
    response = client.post("/api/assistant/turns", json={"message": "查询结果"})
    assert response.status_code == 200
    assert response.json["intent"] == intent
    assert response.json["state"] == "needs_input"
    assert response.json["missing"] == missing
    assert calls == []
