# 17 — 上传并重交不可变的作业版本

**Parent:** [9 号 Spec](../../../docs/task-09-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 接入 T2/F1/S1～S3/E1；名单内学生提交，教师可按确切版本取得附件列表和有限源码。

**Blocked by:** [09 — 在提交前查看可评审源码清单](09-inspect-files.md)；[16 — 发布面向固定名单的教学任务](16-assign.md)

**Status:** ready-for-agent

- [ ] 同一学生交两次得到不同编号和递增版本；并发重交不产生重复 revision，历史源码仍可读取。
- [ ] 截止后返回 409；上传失败无成功提交事件；混配 submission_id/file_id 或访问他人文件得 404。
- [ ] 独立 .py 与合法包内成员都可经 S3 读取；原包可按权限下载。
