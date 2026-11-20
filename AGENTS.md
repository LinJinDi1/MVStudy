# 模块开发

领 `implement-spec` 工单时，先在 [README 的业务域表](README.md#九个业务域) 确认接口提供方，再按[开工索引](docs/development.md)读所属 Spec 与前置票。页面入口归调用方，业务写入归提供方。

正式业务放入对应的 `backend/mvstudy/domains/<域>/`、`frontend/src/features/<域>/`。新增文件、跨域调用、共享代码或接入 7 号原型时，按 [README 的落点与拆分规则](README.md)处理；交付前从仓库根运行 `python tools/check_layout.py`。
