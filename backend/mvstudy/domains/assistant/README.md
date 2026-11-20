# G1 助教编排（06 号票）

在仓库根目录，以 Python 3.12 运行离线公共入口测试：

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements.txt pytest
$env:PYTHONPATH = "backend"
.venv/Scripts/python -m pytest backend/mvstudy/domains/assistant -q
.venv/Scripts/python tools/check_layout.py
```

本票的测试模型只实现 SDK 的 `Model` 边界；请求实际经过 Flask G1 路由及 OpenAI Agents SDK 的 Runner。无需模型密钥，不调用外部模型。测试工具记录调用而不启动算法。

## 宿主装配边界

`mvstudy.domains.assistant.create_assistant_blueprint` 供正式宿主注册，不能挂到匿名的 review demo：

- `actor_provider`：每次请求从服务端当前登录态取得 actor；未登录返回 `None`。请求体不能设置身份。权限与资源归属由能力提供方逐次核对。
- `tools`：按接口清单五个工具名提供异步函数，签名为 `async provider(actor, **params)`，返回原接口结果。必须非阻塞、可取消；同步数据库/SDK 的接入方式由真实提供方联调确定。
- `model`：由获准环境构造的 Agents SDK Model；显式 intent 不需要模型。模型端点、模型名和凭证不写入源码。

22/28 号票负责接入真实身份、A1–A3、Q1、R1、E2/E1 与获准模型，本票不提供伪造的线上工具或身份。缺少工具或模型配置时失败关闭。粘贴源码/源码差异走 7 号本地评审入口，不经 G1。

## 运行与失败语义

- `timeout_s` 默认 30 秒，覆盖模型与工具的整个回合。提供方需遵守异步取消；超时为 503 `service_unavailable`，不会自动重试有副作用的调用。
- 提供方适配层可抛 `AssistantError(code, message, status)` 保留目标接口的 400/403/404 等错误；未知异常只返回通用 503，不暴露内部错误文本。
- G1 检查字段名、类型、必填与工具白名单。算法自己的 JSON Schema、版本绑定、阈值关系和资源授权由 A1/A2 提供方验证（22 号真实接入）；G1 不复制 Canny 业务规则。
- 一次 HTTP 回合只建立一个运行提交任务，模型同批重复调用复用该任务的结果；跨 HTTP 重试不承诺幂等，客户端续答需带回已有选择。超时后若提供方已受理，后续需按真实运行记录核对，不应盲目再次提交。
- 工具结果直接返回，不再经模型改写；模型自己生成的结果文本不会成为 G1 结果。SDK tracing 被关闭，避免隐式发送调用内容。
- 每个实际工具调用记录本地 `tool.finished` 日志，含工具名、成功/失败、已有运行编号；不记录正文/源码/参数。E1 持久化与补发属于 28 号接入。
- 源码专用字段、Markdown 代码围栏、完整 Python 片段在模型调用前被拒绝，并提示本地评审入口。自由文本中的混杂片段不是可靠的隐私检测边界；含源码材料必须使用本地评审，正式 UI 不应把源码拼入 message。

## 本票 TDD 记录

所有行为断言经过 `POST /api/assistant/turns`，SDK Runner 未替换：

1. 原理问答：缺少公开入口的 ImportError → 1 项通过。
2. 显式运行缺图/补图：错误调用问答工具 → 2 项通过。
3. 其余三工具：SDK 报工具未登记 → 5 项通过。
4. 请求与身份边界：12 项失败 → 17 项通过。
5. 模型参数与已选上下文：6 项失败 → 23 项通过。
6. 同批重复提交：实际调用两次 → 24 项通过。
7. 超时与服务失败：4 项失败 → 29 项通过（超时用 0.5 秒容纳 SDK 启动开销）。
8. 模型伪造结果、裸 Python：2 项失败 → 31 项通过。
9. 工具完成日志：缺少日志 → 32 项通过；随后补充自然语言缺图与逐请求身份回归。
