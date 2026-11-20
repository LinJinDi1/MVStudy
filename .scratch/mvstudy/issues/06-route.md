# 06 — 从一次请求选对教学工具

**Parent:** [6 号 Spec](../../../docs/task-06-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 用确定性的模型响应和记录调用的测试工具跑通 G1 公共入口；显式入口优先使用已选操作。保留正式实现会沿用的参数校验和结果展示。

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] 原理题只选问答，运行缺图返回 needs_input；补图后只提交一次并原样返回运行编号。
- [ ] 未登记工具、要求执行脚本及工具超时各有终态；受信身份来自服务端，粘贴源码只进入本地评审。
