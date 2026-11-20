# 06 — 从一次请求选对教学工具

**Parent:** [6 号 Spec](../../../docs/task-06-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 用确定性的模型响应和记录调用的测试工具跑通 G1 公共入口；显式入口优先使用已选操作。保留正式实现会沿用的参数校验和结果展示。

**Blocked by:** None — can start immediately

**Status:** done

- [x] 原理题只选问答，运行缺图返回 needs_input；补图后只提交一次并原样返回运行编号。
- [x] 未登记工具、要求执行脚本及工具超时各有终态；受信身份来自服务端，粘贴源码只进入本地评审。

**验收证据：** 集成分支 `integrate/task-06-assistant`；实现 `0ccd789`，审查修复 `7000472`、`ba43c8c`。在 Python 3.12、`PYTHONPATH=backend` 下运行 `python -m pytest -q`：130 passed，另有 2 个子测试通过；`python tools/check_layout.py` 通过。

通过 Flask 的 `POST /api/assistant/turns` 使用真实 Agents SDK Runner、固定模型输出和记录调用的工具验收：模型猜测图片编号时不提交，混合工具批次没有副作用，重复运行选择只产生一个运行编号。中英文原理问题保留原文；显式源码字段及已覆盖的误粘贴样例不进入模型或问答工具。[运行说明](../../../backend/mvstudy/domains/assistant/README.md)列出了输入边界。真实算法、模型和部署不计入本票验收。
