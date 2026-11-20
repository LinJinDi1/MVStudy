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

22 号票接入真实身份、A1–A3 与 E1；28 号票接入 Q1、R1、E2 与获准模型。本票不提供伪造的线上工具或身份。缺少工具或模型配置时失败关闭。粘贴源码/源码差异走 7 号本地评审入口，不经 G1。

## 运行与失败语义

- `timeout_s` 默认 30 秒，覆盖模型与工具的整个回合。提供方需遵守异步取消；超时为 503 `service_unavailable`，不会自动重试有副作用的调用。
- 提供方适配层可抛 `AssistantError(code, message, status)` 保留目标接口的 400/403/404 等错误；未知异常只返回通用 503，不暴露内部错误文本。
- G1 检查字段名、类型、必填与工具白名单。算法自己的 JSON Schema、版本绑定、阈值关系和资源授权由 A1/A2 提供方验证（22 号真实接入）；G1 不复制 Canny 业务规则。
- 模型只选择工具。对象标识、图片、算法版本和参数只取请求中的已有选择；问答内容只取用户原问题。模型补造的值不会进入提供方。未选图片返回 `needs_input` 和“请选择图片”；续答需带回已有选择。
- SDK 工具回调只收集选择；整批选择校验通过后才调用提供方。同批完全重复只调用一次，矛盾工具或参数整批拒绝，不会产生隐藏运行。跨 HTTP 重试不承诺幂等；超时后若提供方已受理，后续需按真实运行记录核对，不应盲目再次提交。
- 工具结果直接返回，不再经模型改写；模型自己生成的结果文本不会成为 G1 结果。SDK tracing 被关闭，避免隐式发送调用内容。
- 每个实际工具调用记录本地 `tool.finished` 日志，含工具名、成功/失败、已有运行编号；不记录正文/源码/参数。E1 持久化与补发属于 22 号接入。

## 自由文本的披露边界

- 分类模型只收到通过本地边界检查的 `message`，不收到整个请求、结构化 `params`、对象编号或文件上下文；工具返回值不会再次送模型。Q1 收到同一个原问题与其契约允许的已选上下文，资源权限仍由 Q1 验证。
- 中英文教学问题、括号、引号、冒号、空行、多句及公式保持原样；例如 `Explain Canny (edge detection)`、`What is a shell command?`、`y = x + 1`。提及函数、代码或脚本的原理讨论不会仅因术语被拒绝。句子整体交模型，未压缩成关键词。
- `source/before/after` 源材料通道始终在模型及 Q1 之前拒绝。对误粘贴到 message 的材料，逐行识别围栏、差异头、Python 语句/调用、残缺声明及典型 JavaScript 声明；带说明前缀的材料也提示本地评审。明确要求执行脚本或命令的请求返回 `unsupported_intent`，不因模型选择白名单运行而放行。显式 intent 遵守同一检查。
- 本地识别用于减少误粘贴，不是任意语言/伪装文本 DLP，也不是外发授权：公式与程序表达式存在重叠。28 号接入须先取得模型服务及输入数据的外发许可，正式宿主只装配获准模型与提供方；不能用“通过识别”替代授权。源码与差异仍应由本地评审入口收取。

所有回归通过 `POST /api/assistant/turns` 和真实 SDK Runner；覆盖矛盾批次零调用、重复提交的真实编号、模型捏造对象、源码/脚本零外发、普通教学问题、超时取消和逐请求身份。
