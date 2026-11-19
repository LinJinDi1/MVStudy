# 可独立推进的任务七内容

## 已实现骨架

- 助教工作台前端：代码输入、静态评审触发、反馈呈现、失败提示。
- Flask API：健康检查、静态评审、结果读取、文本差异摘要。
- 评审规则：Python 优先报告未闭合或不匹配的括号、其他解析错误和未定义名称。语法无法解析时，先修复语法再检查名称。各支持语言仍提供超长行提示。
- Docker Compose：独立启动 Web 与 API。
- 安全边界：输入限长；服务不导入、不运行学生代码；结果标注 `execution_performed: false`。

## 无需他人模块即可继续

1. 增加纯文本静态规则和语言适配器，配套规则说明与示例。
2. 完善前端文件/提交元信息展示、过滤和无结果状态。
3. 设计 Markdown 与 `.ipynb` 的本地解析器接口、章节/知识点/段落切分策略，并以假数据验证检索展示。
4. 编写工具调用契约：allow-list、JSON Schema、超时、输出长度限制、失败状态；以模拟教学算法实现端到端演示。
5. 为后续 JWT 接入预留认证中间件边界；当前原型不具备真实身份认证，不能用于线上部署。

## 等待协作确认后再接入

- 统一 JWT issuer/claims、课程和角色权限（平台模块）。
- 学生提交文件与作业 ID 的来源/格式（任务九）。
- B3-520 教学算法服务地址、算法清单、参数和结果 schema、并发/排队策略（任务三/六）。
- Postgres/pgvector、Redis 实际连接配置及数据模型。

## API 草案

- `GET /api/health`
- `POST /api/reviews`：`{ "source": "...", "language": "python", "submission_id": "optional" }`
- `GET /api/reviews/{review_id}`
- `POST /api/reviews/diff`：`{ "before": "...", "after": "..." }`

所有评审建议均为提示，教师需复核。任何实现都不得执行学生提交。
