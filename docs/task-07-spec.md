# 07｜代码静态评审与独立助教入口

[本地 tracker 与执行约定](development.md) · [字段字典](database.md) · [接口契约](interfaces.md)

## Problem Statement

教师要知道建议指向哪次提交、哪个文件和哪一行；同一评审从批改页或独立入口打开，应受相同的权限约束。

## Solution

保留已有粘贴评审，新增可追溯的作业评审和参考对比。教师⑨整合问答、算法和评审，独立首页按身份再提供学情。

## User Stories

1. 作为教师，我希望从批改页带入版本和文件，以便定位该次提交的问题。
2. 作为用户，我希望粘贴 Python 查看理由和修改建议，以便可以在提交前自行改正。
3. 作为教师，我希望把学生版本与获准参考进行行差异比较，以便了解改动而不影响评分。
4. 作为用户，我希望重新打开已保存的评审，以便保留原规则版本和建议。
5. 作为教师，我希望在两个入口看到一致的回答、运行和建议，以便按同一标准教学。

## Implementation Decisions

- 沿用 PR #2 的 review_source、Flask 路由与 Vue 工作台：AST/Pyflakes 的括号、语法、未定义名称，以及多语言超长行检查；补 PR #1 的裸 except、category、真实文件名、rule_version。
- R1/R2 同时服务两个入口。粘贴与作业模式互斥；后者经 S3 读取指定快照；前者仅创建者读，后者按当前提交权限复核。保存 findings 和来源，文本仅在本地内存分析。
- R3 以参考为旧侧，先计全文再取前 1000 行。summary、diff、既有 finding 字段继续保留，新增状态、计数与 truncated；具体请求和返回只在公共接口清单维护。
- 对接范围：R1～R3 → U2、S2/S3、T2、Q1、G1、E2；reviews。

## Testing Decisions

用同一输入从教师与独立入口对照行号和类别；检查超限 413、空输入 400、未知或越权 404、无参考空差异和一行替换。保存后重启并撤权再读，同时验证原型粘贴入口。

## Out of Scope

| 本模块范围外 |
|---|
| 自动给分、运行或外发作业、同一学生两次提交的历史差异提案 |

## Further Notes

起点是已合入 PR #1/#2：文本评审、内存查询、文本 diff 和工作台已存在；正式身份、持久化、作业读取及页面整合从各自的票接续。

**关联工单（按依赖领取）：** [07 从已有工作台定位裸 except 与未定义名称](../.scratch/mvstudy/issues/07-review-code.md) · [23 登录后找回自己的粘贴评审](../.scratch/mvstudy/issues/23-private-review.md) · [24 从指定作业版本生成静态评审](../.scratch/mvstudy/issues/24-submission-review.md) · [25 从批改页比较参考与学生版本](../.scratch/mvstudy/issues/25-reference-diff.md) · [27 从教师和独立入口使用同一组能力](../.scratch/mvstudy/issues/27-assistant-ui.md)
