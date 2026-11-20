# 07 — 从已有工作台定位裸 except 与未定义名称

**Parent:** [7 号 Spec](../../../docs/task-07-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 在已合入的 Vue/Flask 粘贴评审路径上补全规则分类、规则版本与空结果展示。继续使用 review_source 和原有端点。

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] 分别输入裸 except、未定义名称、超长行及干净代码；展示对应类别、1 起算行号、理由与建议，干净代码返回 []。
- [ ] 带 print 的文本仅被解析；保留原型响应字段、512 KiB 请求上限和既有语言的行长检查。
