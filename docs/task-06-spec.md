# 06｜助教编排与整套部署

[本地 tracker 与执行约定](development.md) · [字段字典](database.md) · [接口契约](interfaces.md)

## Problem Statement

一句“看看这个算法”既可能是问原理也可能想运行；部署时还要让同一套代码、文件和运行环境在答辩机器上恢复。

## Solution

按明确意图调用平台已有能力；缺少输入时追问。部署给出可复现的启动、健康检查和恢复办法。

## User Stories

1. 作为教师，我希望提问算法原理，以便得到课程回答和引用。
2. 作为学生或教师，我希望提供图片后要求运行算法，以便取得一次运行的编号和实际产物。
3. 作为教师，我希望要求查看评审或班级表现，以便用本人权限取得对应结果。
4. 作为管理员，我希望区分存活、降级和未就绪，以便及时发现服务故障。
5. 作为交付成员，我希望在新环境恢复课程、作业与成绩，以便完成实际答辩。

## Implementation Decisions

- G1 按 question/run/run_status/review/analytics 路由；显式 intent 先于模型分类。自由文本用一个工具循环，工具白名单、每轮最多一次有副作用的运行提交；只读调用和追问按接口清单。
- 身份始终取服务端；源码保留在 7 号本地入口。RAG 答案直接传回，运行以 A3 为准；记录 tool.finished。
- Docker Compose 编排 Flask、Vue 静态资源/网关、数据库、worker 与持久卷；启动迁移用 Alembic。备份同时涵盖 PostgreSQL 与文件，恢复到隔离目标再走用户路径。
- 对接范围：G1/H1 → Q1、A1～A3、R1、E2、E1。

## Testing Decisions

以 G1 为主，通过固定模型输出验证五类请求、缺参数、失败及拒绝任意执行；在获准真实服务验证自然语言调用。在独立数据库和文件卷执行恢复演练。

## Out of Scope

| 本模块范围外 |
|---|
| 通用命令执行、未经授权的线上发布 |

## Further Notes

模型账号、实验室算力与目标机是对应真实调用和部署票的外部输入。

**关联工单（按依赖领取）：** [06 从一次请求选对教学工具](../.scratch/mvstudy/issues/06-route.md) · [22 从助教运行实验并查看真实进度](../.scratch/mvstudy/issues/22-agent-run.md) · [28 从自然语言请求取得课程、评审和班级结果](../.scratch/mvstudy/issues/28-all-tools.md) · [33 在获准主机交付并恢复整个平台](../.scratch/mvstudy/issues/33-deployment.md)
