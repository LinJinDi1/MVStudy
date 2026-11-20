# 21 — 从可见课程版本获得分层回答

**Parent:** [5 号 Spec](../../../docs/task-05-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 通过 Q1 完成索引、权限过滤、向量检索、带引用的回答与问答事件。测试用可控嵌入/生成器；正式适配器从环境取得模型配置。

**Blocked by:** [05 — 从教学材料定位一条可引用证据](05-citation.md)；[12 — 发布新版本并重开旧版](12-publish.md)；[15 — 幂等接收班级学习事件](15-events.md)

**Status:** ready-for-agent

- [ ] 同版模型向量检索前三条；对有依据的题返回可定位引用，对无依据的题返回 insufficient_evidence。
- [ ] 替换讲义版本后旧引用仍可读；教师答案在学生候选外，一次回答只计一次事件。
