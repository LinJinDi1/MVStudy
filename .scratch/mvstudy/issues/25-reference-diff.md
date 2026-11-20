# 25 — 从批改页比较参考与学生版本

**Parent:** [7 号 Spec](../../../docs/task-07-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 教师由选中的提交进入评审区；R3 支持两段文本或获准的同版参考文件，并把差异状态显示给教师。

**Blocked by:** [18 — 批改教师实际选定的提交](18-grade.md)；[24 — 从指定作业版本生成静态评审](24-submission-review.md)

**Status:** ready-for-agent

- [ ] 替换一行得一增一删；超过 1000 行时计数仍是全文结果，详情最多 1000 项。
- [ ] 缺参考走 no_reference；显式错误参考得 404；已有 before/after 客户端仍能读 summary 和 diff。
