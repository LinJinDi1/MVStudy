# 24 — 从指定作业版本生成静态评审

**Parent:** [7 号 Spec](../../../docs/task-07-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** R1 的作业模式经 S3 取有限文本；R2 重查原提交权限。评审绑定不可变提交文件与规则版本。

**Blocked by:** [17 — 上传并重交不可变的作业版本](17-submit.md)；[23 — 登录后找回自己的粘贴评审](23-private-review.md)

**Status:** ready-for-agent

- [ ] 学生重交后原 review_id 指向原文件；教师失去该班权限后按原编号读取返回 404。
- [ ] 混传文本与作业模式、拼接其他提交的附件、提交任意 URL 均被拒；输出有实际文件名和行号。
