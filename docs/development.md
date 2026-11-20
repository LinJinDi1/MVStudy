# 开工索引｜给 implement-spec 的本地 tracker

从下表选择自己的 Spec。动手前在[项目骨架与归属表](../README.md#九个业务域)找到自己的前后端目录，以及本票会调用的其他域。每份 Spec 维护产品行为、实现取舍、测试入口和所属票；每张票单独记录交付、阻塞和可勾选的验收条件。数据字段与 HTTP 示例分别以[字段字典](database.md)和[接口契约](interfaces.md)为准。产品范围见 [PRD](PRD.md)。

## 直接使用

在包含这套文件的 Git 提交上调用技能，例如执行 6 号：

```text
$implement-spec docs/task-06-spec.md
Issue tracker: 本地 .scratch/mvstudy/issues/；只执行该 Spec 在 Further Notes 关联的票。跨模块前置按全局票号读取。
```

团队统一推进时，可将本索引作为九份 Spec 的清单，指定执行全图；个人推进时，遇到外部模块未关闭的票，把票号交给对应成员，不代做其他模块。

| 成员 Spec | 无模块前置，先领这一票 | 本模块后续票（打开即见前置及验收） |
|---|---|---|
| [1 号 · 身份、权限与平台首页](task-01-spec.md) | [01 从空库登录并识别所属班级](../.scratch/mvstudy/issues/01-login.md) | [10 在管理页启停账号并调整角色](../.scratch/mvstudy/issues/10-admin.md)、[11 凭文件编号上传和取回受控内容](../.scratch/mvstudy/issues/11-file-store.md)、[32 三种首页读取真实数据](../.scratch/mvstudy/issues/32-role-home.md) |
| [2 号 · 版本化案例库](task-02-spec.md) | [02 从目录读 Markdown 和 notebook](../.scratch/mvstudy/issues/02-read-case.md) | [12 发布新版本并重开旧版](../.scratch/mvstudy/issues/12-publish.md)、[14 从指定案例版本启动匹配的实验](../.scratch/mvstudy/issues/14-launch.md)、[29 交付十五项实际课程案例](../.scratch/mvstudy/issues/29-course-catalog.md) |
| [3 号 · 在线实验与算法执行](task-03-spec.md) | [03 运行一个预登记的本地教学样例](../.scratch/mvstudy/issues/03-single-run.md) | [13 按版本查找登记算法](../.scratch/mvstudy/issues/13-registry.md)、[20 把实验变成可追踪的运行记录](../.scratch/mvstudy/issues/20-jobs.md)、[30 从十五个案例运行配套教学算法](../.scratch/mvstudy/issues/30-course-algorithms.md) |
| [4 号 · 教师教学任务、批改与成绩](task-04-spec.md) | [04 用四人班级展示批改名单](../.scratch/mvstudy/issues/04-gradebook.md) | [16 发布面向固定名单的教学任务](../.scratch/mvstudy/issues/16-assign.md)、[18 批改教师实际选定的提交](../.scratch/mvstudy/issues/18-grade.md) |
| [5 号 · 课程检索、问答和评测](task-05-spec.md) | [05 从教学材料定位一条可引用证据](../.scratch/mvstudy/issues/05-citation.md) | [21 从可见课程版本获得分层回答](../.scratch/mvstudy/issues/21-rag.md)、[31 在课程材料上检验检索与图像讲解](../.scratch/mvstudy/issues/31-course-eval.md) |
| [6 号 · 助教编排与整套部署](task-06-spec.md) | [06 从一次请求选对教学工具](../.scratch/mvstudy/issues/06-route.md) | [22 从助教运行实验并查看真实进度](../.scratch/mvstudy/issues/22-agent-run.md)、[28 从自然语言请求取得课程、评审和班级结果](../.scratch/mvstudy/issues/28-all-tools.md)、[33 在获准主机交付并恢复整个平台](../.scratch/mvstudy/issues/33-deployment.md) |
| [7 号 · 代码静态评审与独立助教入口](task-07-spec.md) | [07 从已有工作台定位裸 except 与未定义名称](../.scratch/mvstudy/issues/07-review-code.md) | [23 登录后找回自己的粘贴评审](../.scratch/mvstudy/issues/23-private-review.md)、[24 从指定作业版本生成静态评审](../.scratch/mvstudy/issues/24-submission-review.md)、[25 从批改页比较参考与学生版本](../.scratch/mvstudy/issues/25-reference-diff.md)、[27 从教师和独立入口使用同一组能力](../.scratch/mvstudy/issues/27-assistant-ui.md) |
| [8 号 · 学情分析与教师周报](task-08-spec.md) | [08 用已知班级数据生成可复算的周报](../.scratch/mvstudy/issues/08-weekly-metrics.md) | [15 幂等接收班级学习事件](../.scratch/mvstudy/issues/15-events.md)、[26 教师读取真实班级统计和周报](../.scratch/mvstudy/issues/26-analytics.md) |
| [9 号 · 学生任务、不可变提交与成绩](task-09-spec.md) | [09 在提交前查看可评审源码清单](../.scratch/mvstudy/issues/09-inspect-files.md) | [17 上传并重交不可变的作业版本](../.scratch/mvstudy/issues/17-submit.md)、[19 学生查看自己各版成绩](../.scratch/mvstudy/issues/19-results.md) |

## 领票与关闭

- Tracker 采用本地 Markdown，每票一个文件，编号全项目唯一。Parent 指向所属 Spec；Blocked by 列的是必须先合入的交付。ready-for-agent 是分流标签；只有前置票均已完成，且该票列出的外部输入可用时才领取。01～09 是初始可开工的九张票。
- 执行前，Spec、公共契约和工单须已在 Git 基线中：技能会从提交创建独立 worktree。一次调用在一条集成分支上完成；跨模块前置须同时有 done 状态及其实现提交在当前基线上。团队分别开分支时，先合入依赖模块的实现再解锁。
- 测试范围以所选 Spec 的 Testing Decisions 为准；调用方确认该范围后，按 TDD 逐条通过验收：先在 Spec 的公开测试入口记录失败，再实现至通过；合入集成分支后勾选条件，在票内附测试命令、结果和实现提交，将 Status 改为 done。最后按技能进行集成分支 code-review。缺少真实材料、权限或机器时保留票与解锁条件，继续执行无关的就绪票。
- 例：16 发布带班级快照的任务 → 17 保存不可变提交 → 18 给指定版本评分 → 19 学生看成绩。24 号评审票也读 17 的提交，与 18 可并行；25 的参考对比才需要教师批改入口。

## 统一实现基线

| 决策 | 执行约定 |
|---|---|
| 平台宿主 | Python 3.12 + Flask，按域注册 Blueprint；Vue 3 + TypeScript/Vite 共用宿主。01 接入登录、路由和根级迁移配置。并行票直接在[正式业务域](../README.md#九个业务域)实现和测试；评审演示已使用两端的 review 域，23 号票接入统一身份与持久化。 |
| 建库与演进 | PostgreSQL 16，SQLAlchemy 2.x Declarative 定义模型、psycopg 3 连接、Alembic 管理一个迁移历史。具体建库、升级、测试与合并规则见[数据库实施约定](database.md#建库升级和测试)。 |
| 任务与文件 | 3 号用持久 runs 表领取排队任务（行锁 + SKIP LOCKED）和独立计算进程；文件存私有持久卷，经 F1 授权读取。首版这两项无需 Redis。 |
| 工具与模型 | 6 号用 OpenAI Agents SDK 的单一工具循环及明确工具名；模型地址、名称、密钥由获准环境注入，兼容性在 28 号票验证。5 号以 Sentence-Transformers + pgvector 检索；嵌入模型及视觉供应方按课程授权确定。7 号静态评审完全本地。 |
| 测试入口 | 后端用 pytest + Flask test client，仓储走迁移后的独立 PostgreSQL 16；公开的领域函数可直接测试。前端用 Vitest + Vue Test Utils 检查可见行为。7 号现有 Flask API 和粘贴工作台是行为基准；仓库尚无通用测试套件，首个使用方交付本模块测试及运行说明。真实材料、外部模型和目标机各留单独验收结果。 |

## 边界条件、缺口与负责方
| 条件或提案 | 本轮采用的处理 | 影响哪一步，由谁落实 |
|---|---|---|
| 课程材料、算法运行条件 | 2 号登记获准使用的 15 项、缺件及版本；3 号取得命令、依赖、权重与预期产物，先交同一案例。未提供的材料在界面标明。 | 12/14/29、13/20/30；2、3 号对接实验室材料/算法持有人 |
| 模型、费用与材料外发 | 仅向获准服务发送准许的课程材料；作业评审全程本地。图片/标注图/曲线理解在文本代码检索后按真实样例接入。 | 21/31、22/28；5、6 号联系账号与数据管理方 |
| 教师参考、作业与助教角色 | 2 号维护版本化参考文件，4 号发布时选定，7 号按当前班级和材料权限取用。作业评审首版开放给获准的任课教师；专设助教角色须由 1 号配置权限及班级范围。账号禁用或撤权后，下一请求生效。 | 01/10、12、16、24/25；未绑定参考时走 no_reference |
| 学生提交和代码执行 | 作业进入 9 号的受控文件存储；7 号只解析文本。3 号只运行由课程方登记的算法版本。 | 20/30、17、24；评分权属于任课教师 |
| 压缩包、编码与体积 | 9 号保留原包；登记可评审的 UTF-8 源文件，每个文件独立编号，拒绝越界名称、链接、重复路径，按解压后的成员数和字节数限额。超出评审范围的附件保留作业下载用途并提示原因。联调默认单个可评审文本 ≤512 KiB；7 号 JSON 请求体上限 512 KiB（含编码和字段）。 | 1/9 号在真实上传前按目标存储设定整包、展开大小、成员数上限并公布；7 号优先用单个 .py 打通 S3 |
| 评审阶段与后续提案 | 本轮采用“获准参考实现 → 学生代码”的差异。7 号另提“同一学生两次提交比较”，留待 4/7/9 单独讨论。 | 25；历史提交仍按 17 保留 |
| 真实数据与保留期 | 事件保留必要标识和状态；学情日志保留期和可访问者由 1、8 号在真实学生数据启用前确定。学生从个人任务入口查看本人结果。 | 01/10、15/26；假数据开发可立即开始 |
| 运行容量、技术栈和目标机 | 共享后端、前端与数据库按下方执行基线。CPU/GPU 并发数、队列容量、运行时限与文件限额由 3/6 号实测后配置；线上启动须取得目标机与网络权限。 | 13/20/30、33；各号提交自己的运行说明 |
| 正式交付日期 | 以正式通知为准；本表用于安排开发和逐项联调。 | 发起人补入 PRD；最终一次完整成品交付与答辩 |

**7 号评审工作台：** [启动说明](../modules/task-07/README.md) · [静态规则](../backend/mvstudy/domains/review/review_service.py) · [Vue 工作台](../frontend/src/features/review/ReviewWorkbench.vue)。
