# 09 — 在提交前查看可评审源码清单

**Parent:** [9 号 Spec](../../../docs/task-09-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 学生选择源码、压缩包或结果图，看到待提交文件名和可评审的 UTF-8 成员；用固定版本样例打通选择与失败反馈。

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] 原包与包内 main.py 可区分；同名不同目录成员有独立身份，重选不污染上一版。
- [ ] 超限、越界路径、链接、重复成员均按文件策略处理；可读限制含展开字节数和成员数。
