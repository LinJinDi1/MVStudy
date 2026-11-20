# 01｜身份、权限与平台首页

[本地 tracker 与执行约定](development.md) · [字段字典](database.md) · [接口契约](interfaces.md)

## Problem Statement

同一个人可以从平台或独立助教进入。如果两个入口各自判断身份，禁用账号后还可能读到旧班级的作业。

## Solution

一次登录后按角色进入学①、师①或管①～④。共用一个当前身份，并为每次敏感操作重新核对权限和班级范围。

## User Stories

1. 作为学生，我希望看到自己的任务和成绩入口，以便只处理分配给我的教学活动。
2. 作为教师，我希望看到自己所教班级的名册和待批数，以便决定先批哪份作业。
3. 作为管理员，我希望新建及停用账号、调整角色权限，以便下一次请求就能执行新的授权。
4. 作为文件上传者，我希望用不随文件名改变的编号读取内容，以便让同名的两份提交各自可追溯。
5. 作为运维人员，我希望从管理首页看到服务状态及数据截止情况，以便区分确实为空和服务异常。

## Implementation Decisions

- 正式服务采用 Flask 应用工厂；领域能力按 Blueprint 注册。1 号拥有共享身份、文件读写、应用初始化和数据库迁移入口。
- PostgreSQL 16 + SQLAlchemy 2.x Declarative + psycopg 3；Alembic 是唯一建表、升级入口。同一 Base.metadata 注册各模块模型，业务事务使用 Session。
- JWT 标识用户，权限、enabled、班级关系逐次查库；账号密码仅存摘要。文件字节走私有持久卷，数据库保存不可变编号、所有者和对象键；读取时校验关联资源。
- 对接范围：U1～U5、F1、P1；H1 用于管理页。

## Testing Decisions

从公开登录与管理 API 走停用→重放旧凭证、跨班读、同名上传；从三种角色的浏览器首页核对计数。以迁移 CLI 在空 PostgreSQL 及上一版本库验证建表、升级与数据保留。

## Out of Scope

| 本模块范围外 |
|---|
| 教务排课、公开文件盘 |

## Further Notes

班级以预置名册开始；文件下载范围随关联资源的当前授权变化。

**关联工单（按依赖领取）：** [01 从空库登录并识别所属班级](../.scratch/mvstudy/issues/01-login.md) · [10 在管理页启停账号并调整角色](../.scratch/mvstudy/issues/10-admin.md) · [11 凭文件编号上传和取回受控内容](../.scratch/mvstudy/issues/11-file-store.md) · [32 三种首页读取真实数据](../.scratch/mvstudy/issues/32-role-home.md)
