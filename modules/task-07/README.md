# 任务七：代码评审与助教入口

七号模块可以独立启动，供团队提前体验代码评审流程。

## 第一版功能

- 粘贴 Python 代码，查看括号不匹配、其他语法错误和未定义名称的提示。代码无法解析时，先修正语法，再检查名称。
- 提示过长的代码行；后端也提供比较两份代码文本的接口。
- 原型只分析代码文本。评审结果暂存在内存中，后端重启后清空。

## 本地启动

启动 Docker Desktop，在本 README 所在目录运行：

```sh
docker compose up --build
```

在浏览器访问 `http://localhost:5173` 打开演示页面，Flask API 使用 8000 端口。

## 后续接入 MVStudy

- `backend/review_service.py` 提供 `review_source(source, language)`，返回带行号的静态检查建议。该函数依赖 Python 标准库和 Pyflakes，可由团队后端直接调用。
- `backend/app.py` 保留演示用的 Flask 接口，负责读取请求、调用检查函数和返回结果。
- 07 号票继续在此原型完善规则。[23 号票](../../.scratch/mvstudy/issues/23-private-review.md)将规则接入正式 `review` 域，并保留本地演示入口；正式目录和接口所有者见[平台骨架](../../README.md#九个业务域)。
