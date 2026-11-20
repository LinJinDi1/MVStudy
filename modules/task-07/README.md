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

## 不使用 Docker（Windows）

在**仓库根目录**打开两个终端。终端一启动 API：

```powershell
py -3.12 -m venv .venv-review
.\.venv-review\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv-review\Scripts\python.exe modules/task-07/backend/app.py
```

终端二启动工作台：

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

打开 Vite 打印的本地网址，点击“开始评审”。默认示例的第 2 行会提示 `threshold` 未定义。原前端目录中的 `npm install`、`npm run dev` 和 `npm run build` 也转到同一个工作台。

## 后续开发位置

- [静态规则及 HTTP 接口](../../backend/mvstudy/domains/review/)由 Flask 演示工厂注册。旧的 `backend/review_service.py` 继续导出同一个 `review_source`。
- [Vue 工作台与请求客户端](../../frontend/src/features/review/)供前端宿主复用。默认开发代理指向本机 8000 端口；独立部署可用 `VITE_API_URL` 指定服务地址。
- 当前演示使用内存记录，仅供本机使用。[23 号票](../../.scratch/mvstudy/issues/23-private-review.md)负责接入统一身份、保存评审和校验读取权限。
