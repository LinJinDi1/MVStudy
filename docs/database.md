# 数据库字段字典｜联调基线 v1.0

[回到分工和步骤索引](development.md) · [按操作查接口](interfaces.md)

1 号维护迁移顺序及命名；各表的业务写入方见各节。查询一律先按当前身份裁剪。这里用 PostgreSQL 类型表达数据含义，供建表和造样例使用。

## 建库、升级和测试

**选型定案：PostgreSQL 16 + SQLAlchemy 2.x（Declarative ORM）+ psycopg 3；Alembic 负责所有建表和升级。** 九个模块共享外键，答辩环境还要从已有数据升级，所以每次结构变更跟着业务票交付模型和迁移。开发、测试和部署执行同一份迁移历史。

| 场景 | 谁做、怎么做 | 通过标准 |
|---|---|---|
| 第一次建库 | 01 号票建立仓库根的 `alembic.ini`、`migrations/versions/` 和平台共用 DeclarativeBase；从 `DATABASE_URL` 读 `postgresql+psycopg://…`。运维先提供空数据库和迁移账号，在仓库根运行 `alembic upgrade head` 创建业务表，随后用单独的开发种子命令生成两班三类账号。 | 可用 U1 登录、U2 取身份、U5 取授权名册。再执行 upgrade 与种子命令，已有数据保留。 |
| 新增或改表 | 领域负责人改 ORM 模型，把领域模型注册到同一个 Base.metadata，生成并审阅 Alembic revision，显式写复合外键、CHECK、索引和必要的数据转换。1 号统筹命名，变更随本票合入。 | 迁移后 `alembic heads` 只有一个 head；模型与实际库结构一致；业务样例可通过公开入口写入和读回。 |
| 并行工单 | 从最新集成分支生成 revision；合并时遇到独立并行 heads 可用 Alembic merge revision 收敛；同表、同约束或数据依赖先协调顺序。已发布的 revision 保持不可变。 | 分别从空库及上一个已发布 revision（保留一份历史记录）执行 `alembic upgrade head`；二者得到同一结构且历史记录仍可读。 |
| PostgreSQL 专属能力 | 基础服务启动不依赖向量模型。21 号票引入 chunks 时，在配备 pgvector 的 PG16 上由获准迁移角色启用 vector 扩展；向量维度由该版嵌入模型固定并写进 revision。 | 同库验证模型版本、向量维度和带权限范围的检索。服务账号只持业务读写权限。 |
| 生产发布与恢复 | 迁移作为独立部署步骤，在新应用进程启动前执行一次。先备份数据库与文件卷，破坏性升级在恢复副本演练。 | 33 号票从备份恢复后能打开原提交、评语与产物。 |

**工程边界：** 应用启动与测试均不调用 `create_all()`。不维护第二套 `init.sql`；扩展和需要手写的 PostgreSQL DDL 放入所属 Alembic revision。集成测试使用隔离 PostgreSQL 数据库，SQLite 不替代复合外键、行锁、JSONB 或向量测试。

**跨域迁移顺序：** 01 身份 → 11 文件；12 建案例与材料，先建两张版本表再补延迟检查的当前版本外键；13 建算法目录；14 加案例－算法关联。15 在 01 和 12 之后建事件表及用户、班级、案例版本外键；16/17/20 在创建任务、提交、运行表的同一 revision 内补对应事件外键。23 建粘贴评审，两个来源字段均为空；24 在 17 和 23 之后加入作业模式和提交文件复合外键。18 在 17 后建成绩表。真实业务写入在对应约束生效后开放。

工具参考：[Alembic 迁移流程](https://alembic.sqlalchemy.org/en/latest/tutorial.html)、[候选迁移需要审阅的内容](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)。

**读法：** 每行是一张表；分号隔开字段。ID 类型统一为 `text`，视为不透明字符串（兼容 7 号现有 UUID）。`PK` 主键，`→表` 是与目标主键同类型的外键，`UQ` 唯一，`?` 可空且默认 NULL；其余字段必填、无默认。显式默认值写在等号后。下文“时间”为 `timestamptz`，“对象/数组”为 `jsonb`，`now` 为写入时刻。文件内容在受控存储中，数据库存元信息和引用。

## 身份、班级与文件

| 表 · 写方 / 读方 | 字段：类型与用途 | 约束及关系 |
|---|---|---|
| roles · 1 / 全组 | role_id PK 角色键；name text 显示名；permissions text[]={} 功能权限码 | 初始 student、teacher、admin；功能权限与班级范围分别检查 |
| users · 1 / 全组通过身份服务读 | user_id PK；login text UQ 登录名；display_name text 姓名；password_hash text 密码摘要；role_id →roles；enabled boolean=true 启用状态 | 接口只返回展示与授权所需字段 |
| classes · 1 / 4、8、9 | class_id PK；name text 班名 | 初始班级可从种子数据导入 |
| class_members · 1 / 4、7、8、9 | class_id →classes；user_id →users；relation text 班内身份 | 联合 PK(class_id,user_id)；relation 为 teacher/student |
| files · 1 提供存取能力，业务模块经该能力写 / 按用途授权读 | file_id PK；owner_id →users 上传或生成操作所属用户；name text 原文件名；media_type text 媒体类型；byte_size bigint 字节数；storage_key text UQ 内部对象键；created_at 时间=now | 文件内容不可覆盖；新内容产生新编号。授权按所有者或关联的材料、运行、提交判断；参考文件额外检查材料可见范围 |

## 案例、材料、算法

| 表 · 写方 / 读方 | 字段：类型与用途 | 约束及关系 |
|---|---|---|
| cases · 2 / 2、3、4、5、6 | case_id PK；current_version int 最新已发布版 | (case_id,current_version) 指向 case_versions；发布时同事务更新，可延迟检查 |
| case_versions · 2 / 上述模块 | case_id →cases；version int；title text 标题；category text 分类；level text 难度；description text 简介；published_at 时间=now | 联合 PK(case_id,version)，version 从 1 递增；已发布内容保留 |
| materials · 2 / 2、4、5、7 | material_id PK；case_id text；version int；kind text；file_id →files；title text；visibility text 可见范围 | (case_id,version) → case_versions；kind=lecture/code/dataset/exercise/answer/reference/image/annotation/curve；visibility=course/staff。答案、参考实现默认按 staff 创建 |
| algorithms · 3 / 2、3、6 | algorithm_id text 算法键；algorithm_version text 封装版；name text；input_schema 对象 输入格式及参数类型/范围/默认值；output_schema 对象 产物定义；timeout_s int 运行上限秒 | 联合 PK(algorithm_id,algorithm_version)；执行入口由 3 号在服务端登记，与版本绑定 |
| case_algorithms · 2 / 3、6 | case_id text；version int；algorithm_id text；algorithm_version text | 四列联合 PK；前两列 → case_versions，后两列 → algorithms；每次运行使用已发布的绑定 |
| runs · 3 / 3、6、8 | run_id PK；owner_id →users；class_id →classes? 课堂上下文；case_id text；version int；algorithm_id text；algorithm_version text；input_file_id →files；params 对象 实际使用的参数；status text=queued；created_at 时间=now；started_at 时间?；ended_at 时间?；error_code text?；error_message text? | 四个版本/标识列按上表绑定；queued → running → succeeded/failed；启动失败可 queued → failed；耗时由起止时间计算 |
| run_outputs · 3 / 3、6 | run_id →runs；file_id →files；label text 产物名 | 联合 PK(run_id,file_id)；成功时与终态一并写入 |

## 教学任务、提交、成绩

| 表 · 写方 / 读方 | 字段：类型与用途 | 约束及关系 |
|---|---|---|
| assignments · 4 / 4、7、8、9 | assignment_id PK；teacher_id →users；class_id →classes；case_id text；version int；kind text 任务类型；title text；instructions text 提交要求；due_at 时间；published_at 时间=now；reference_file_id →files? | kind 必填无默认，允许 experiment/homework；(case_id,version) → case_versions；选填参考文件必须属于本版 reference 材料 |
| assignment_recipients · 4 / 4、8、9 | assignment_id →assignments；student_id →users | 联合 PK，两列固定发布时的应交名单；当前班级授权另行校验 |
| submissions · 9 / 4、7、8、9 | submission_id PK 一次不可变提交；assignment_id →assignments；student_id →users；revision int 提交序号；note text='' 说明；submitted_at 时间=now | (assignment_id,student_id) → assignment_recipients；UQ(assignment_id,student_id,revision)；新版本用新 submission_id |
| submission_files · 9 / 4、7、9 | submission_id →submissions；file_id →files；kind text 附件用途；parent_file_id →files? 所属压缩包；member_path text? 包内相对名称；language text?；encoding text? | 联合 PK(submission_id,file_id)；kind 必填无默认。包内可评审文件绑定独立 file_id，父包也须属于该提交；唯一(submission_id,parent_file_id,member_path)。文本首版 UTF-8 |
| grades · 4 / 4、8、9 | submission_id PK →submissions；grader_id →users；score numeric(5,2) 0～100；comment text=''；graded_at 时间=now | 每个提交版本一份当前评分；待批为无记录。任务列表以最新提交版本为准，历史版本仍可回查 |

## 检索、代码评审、学情

| 表 · 写方 / 读方 | 字段：类型与用途 | 约束及关系 |
|---|---|---|
| chunks · 5 / 5 | chunk_id PK；material_id →materials；locator text 章节/函数/单元格定位；content text 片段；embedding 向量；model_version text 嵌入模型及版本 | 向量维度由选定模型决定，同版本索引维度一致；访问范围和案例版本从材料继承 |
| reviews · 7 / 7，经 7 号接口供 4、6 调用 | review_id PK；creator_id →users；mode text paste/submission；submission_id →submissions?；file_id →files?；language text；rule_version text；status text=completed；findings 数组；created_at 时间=now | paste 两个来源键均空；submission 两者必填且联合引用 submission_files。findings 子字段见接口 R1；summary、dimensions 与两个布尔标记由响应组装。原始代码只在源文件保存，粘贴文本仅在内存处理 |
| learning_events · 8 接收、各业务源产生 / 8 | event_id PK 生产方生成、重试复用；type text 事件名；occurred_at 时间；user_id →users；class_id →classes?；case_id text?；version int?；assignment_id →assignments?；run_id →runs?；submission_id →submissions?；status text；topic text? 知识点标签 | case_id/version 同空或联合引用 case_versions；类型和唯一生产方见 E1。指标从业务记录或事件择一计数。原问题、提示词、代码和图片均在学情日志字段之外 |

**派生值：** 首页计数、最新提交、问答引用、差异详情和周报可按需计算。问答使用 2 号的材料位置；静态差异复用两份输入；周报返回统计区间及生成时间。所选周报数据来自同一次统计快照。
