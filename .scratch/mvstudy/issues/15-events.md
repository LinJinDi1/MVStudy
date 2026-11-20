# 15 — 幂等接收班级学习事件

**Parent:** [8 号 Spec](../../../docs/task-08-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 开放 E1 给各业务源，保留可归属用户和课堂的最少元信息。由引入领域表的工单补对应外键。

**Blocked by:** [01 — 从空库登录并识别所属班级](01-login.md)；[08 — 用已知班级数据生成可复算的周报](08-weekly-metrics.md)；[12 — 发布新版本并重开旧版](12-publish.md)

**Status:** ready-for-agent

- [ ] 同一 event_id、同内容重放只写一次；同编号异内容返回 event_conflict。
- [ ] 个人学习保留空 class_id；日志中无原图、学生代码和提示词；类型及来源按 E1 校验。
