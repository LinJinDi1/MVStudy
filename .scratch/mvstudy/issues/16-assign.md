# 16 — 发布面向固定名单的教学任务

**Parent:** [4 号 Spec](../../../docs/task-04-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 教师选择班级与已发布案例、设置截止时间，可绑定同版参考实现；发布后的学生列表与任务详情共用 T1/T2。

**Blocked by:** [04 — 用四人班级展示批改名单](04-gradebook.md)；[12 — 发布新版本并重开旧版](12-publish.md)；[15 — 幂等接收班级学习事件](15-events.md)

**Status:** ready-for-agent

- [ ] 仅名单内学生看到任务；事后名册变化不改变发布时应交人数，读取继续校验当前班级权限。
- [ ] 错版参考或已过截止时间的任务发布失败；成功发布可按 assignment_id 查到一次发布事件。
