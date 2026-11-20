# 01 — 从空库登录并识别所属班级

**Parent:** [1 号 Spec](../../../docs/task-01-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 在正式 Flask 应用中，用预置学生或教师登录，页面显示当前身份与所属班级。此票交付共享应用工厂、数据库迁移入口、Vue 登录与路由宿主及 U1/U2/U5。1 号提供从仓库根运行 Alembic 的配置和幂等的开发种子入口。

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] 在新 PostgreSQL 16 数据库执行 alembic upgrade head，植入两班样例；正确口令返回凭证，U2 的授权来自数据库。
- [ ] 错误口令返回 401；学生查询他班名册得 404。刷新后仍是原身份。
- [ ] 第二次升到 head 后原用户仍可登录；测试走同一套迁移。
- [ ] 登录行为放在 `platform` 域；Flask 宿主只注册 Blueprint。用应用工厂生成的 URL 映射做集成检查：每对 HTTP 方法与路径只由一个处理器提供，后续注册新域时沿用此检查。
