# 04｜教师教学任务、批改与成绩

[本地 tracker 与执行约定](development.md) · [字段字典](database.md) · [接口契约](interfaces.md)

## Problem Statement

重交与批改同时发生时，教师容易给新版本记上旧版本的成绩；学生人员变化也会改变历史完成率。

## Solution

师⑤～⑦以发布时的应交名单呈现任务，以不可变的提交版本保存评分。

## User Stories

1. 作为教师，我希望为所教班级选择案例、设置截止时间和提交要求，以便一次发布实验或作业。
2. 作为教师，我希望区分未交、待批和已批，以便找到需要批改的学生。
3. 作为教师，我希望从所选提交进入静态评审，以便建议对应我正在看的代码。
4. 作为教师，我希望保存分数和评语时得知学生已经重交，以便避免批错版本。
5. 作为学生，我希望查看某次提交的真实成绩，以便区分零分和未批。

## Implementation Decisions

- 发布在一个事务中保存 assignments 与 assignment_recipients；可选参考文件属于所选案例版本。
- T3 按名单关联最新 submission_id；分数为 0 仍是已批。T4 的评分键是 submission_id。验证当前班级与最新版本后保存，与重提共享学生－任务粒度的事务锁。
- 参考绑定仅在教师可读上下文返回；批改页传 submission_id/file_id 给 7 号，成绩最终写回 T4。
- 对接范围：T1～T4 → U5、C1、S2、E1；assignments、assignment_recipients、grades。

## Testing Decisions

从教师发布入口开始，用名单变化、错版参考、重提时保存和零分样例验证；用另一个教师凭证请求同一成绩单。

## Out of Scope

| 本模块范围外 |
|---|
| 自动评分、教师直接运行学生提交 |

## Further Notes

服务器比较截止时间；旧版成绩从历史提交读取。

**关联工单（按依赖领取）：** [04 用四人班级展示批改名单](../.scratch/mvstudy/issues/04-gradebook.md) · [16 发布面向固定名单的教学任务](../.scratch/mvstudy/issues/16-assign.md) · [18 批改教师实际选定的提交](../.scratch/mvstudy/issues/18-grade.md)
