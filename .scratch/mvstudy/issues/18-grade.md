# 18 — 批改教师实际选定的提交

**Parent:** [4 号 Spec](../../../docs/task-04-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 用 T3 显示真实名单，用 T4 保存教师分数及评语；批改页将 S2 中的指定提交/文件传往教师评审入口。

**Blocked by:** [17 — 上传并重交不可变的作业版本](17-submit.md)

**Status:** ready-for-agent

- [ ] 0 分写入后重新加载仍为 graded；未交、待批分别显示。
- [ ] 批改期间出现新版本时保存旧版得 409；班外教师读写都失败；成功评分产生一次 grade.saved。
