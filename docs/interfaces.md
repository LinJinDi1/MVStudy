# 接口清单｜提供方、消费方和联调样例

[开工索引](development.md) · [数据库字段和枚举](database.md)。以下为 **v1.0 目标契约**；7 号原型差异见 [7 号 Spec](task-07-spec.md)。同一进程可直接调用同名业务能力；HTTP 面只暴露给有权使用它的入口。

## 通用读法

所有 HTTP 路径加前缀 `/api`。表中对象是联调用例的简写（字符串用引号，正文已命名的对象用大写名引用）；字段类型、取值和关系按字典。GET 的输入在路径或查询参数，其余为 JSON；文件上传单独走 multipart。列表返回 `{items:[...]}`，无内容返回空数组。除登录与最小存活探针外，每次请求都从当前登录态取得身份。班级范围取当前关系，文件按实际关联资源再次授权。

| 共通响应 | 示例及使用场景 |
|---|---|
| 200 / 201 / 202 | 查询或更新成功 / 创建资源 / 已受理异步运行。创建时返回服务端编号。 |
| 400 / 409 / 413 | `{"error":{"code":"invalid_params","message":"低阈值应小于高阈值。"}}`；表内其他错误码沿用这个结构；409 表示当前状态冲突，413 表示体积超限。 |
| 401 / 403 / 404 | `unauthenticated`：请登录；`forbidden`：无功能权限；`not_found`：指定私有资源不存在或不在可读范围。 |
| 503 | `service_unavailable`：调用服务暂不可用；界面保留输入并提供重试。已受理的运行失败用运行终态返回。 |

**类型与缺省：** `*_id`、算法版本、枚举、名称和说明为字符串；案例 version、revision、计数和毫秒耗时为整数；score 与比例是数值；时间为带时区的 ISO 8601 字符串。数组为空用 []；可空值用 null；写接口只接收列出的可写字段，身份、状态和时间由服务端设置（事件发生时间由生产方设置）。POST 默认字段按数据库字典；PATCH 只更新传入的可写键。

### 身份、管理和文件｜1 号提供
| 键 · 方法/路径 | 调用方、权限与输入 | 成功示例 | 失败示例 |
|---|---|---|---|
| U1 POST /login | 登录页，login/password | 200 {access_token:"…"}；后续用 Bearer 凭证 | 401 invalid_credentials |
| U2 GET /me | 各模块，已登录；无入参 | {user_id:"u1",display_name:"李同学",role_id:"student",permissions:["case.read"],classes:[{class_id:"c1",relation:"student"}]} | 401 unauthenticated（含账号停用） |
| U3 GET /admin/users；POST /admin/users；PATCH /admin/users/{user_id} | 管理员；查询或创建 login/display_name/password/role_id，更新 display_name/role_id/enabled | 列表 items 或单个 {user_id:"u1",login:"s01",display_name:"李同学",role_id:"student",enabled:true}；创建 201 | 409 login_taken；403 forbidden |
| U4 GET /admin/roles；POST /admin/roles；PATCH /admin/roles/{role_id} | 管理员；创建 role_id/name/permissions 或修改 name/permissions | 角色数组包装在 items 或单个 {role_id:"teacher",name:"教师",permissions:["grade.write"]} | 400 invalid_permission；409 role_exists |
| U5 GET /classes/{class_id}/members | 4 发布名单、8、管理页；仅管理权限或所教班级，按 relation 筛选 | {items:[{user_id:"u1",display_name:"李同学",relation:"student"}]} | 404 not_found |
| F1 POST /files；GET /files/{file_id} | 2/3/9 上传 multipart 的 file；读者按资源授权下载。3 的产物、9 的解包文本可经同一内部存取函数写入 | 201 {file_id:"f1",name:"main.py",media_type:"text/x-python",byte_size:84}；GET 返回内容流，下载使用安全文件名 | 413 payload_too_large；404 not_found |

**P1 · GET /home（1 号提供给三类首页）。** 无请求体；凭当前用户返回对应角色的指标。学生示例：{role_id:"student",case_count:15,assignment_count:3,to_submit:1}（只计本人应交任务）；教师增加 pending_grades、active_students（所教班级、近 7 日有学习事件的去重学生）；管理员返回 user_count、case_count、running_runs、open_assignments，运行状态另读 H1。计数的 case_count 取可见案例，open_assignments 取已发布且未截止的任务；无活动为 0。失败：401 unauthenticated。个人任务由 T2 读取，班级完成率、成绩和高频问题由 E2 提供。

### 案例和算法｜2、3 号提供
| 键 · 方法/路径 | 调用方、权限与输入 | 成功示例 | 失败示例 |
|---|---|---|---|
| C1 GET /cases；GET /cases/{case_id}/versions/{version} | 学生/教师/授权管理员；列表筛 q/category/level；详情指定版 | 列表 items 含 case_id/version/title/category/level；详情另含 description、materials:[{material_id:"m1",kind:"lecture",file_id:"f1",title:"原理"}]、algorithms:[{algorithm_id:"edge",algorithm_version:"1"}] | 404 not_found |
| C2 POST /cases；POST /cases/{case_id}/versions | 案例维护权限；title/category/level/description、materials:[{kind,file_id,title,visibility}]、algorithms:[{algorithm_id,algorithm_version}]；2 写，3/4/5 引用 | 201 {case_id:"edge-case",version:1}；修订产生下一版本 | 400 unknown_algorithm / invalid_material |
| A1 GET /algorithms | 3 提供给 2/6 和实验页；已授权用户，可按 case_id/version 筛 | {items:[{algorithm_id:"edge",algorithm_version:"1",name:"边缘检测",input_schema:{…},output_schema:{…},timeout_s:30}]} | 404 not_found（指定案例版本不可见） |
| A2 POST /runs | 实验页、6；有运行权限。{case_id:"edge-case",version:1,algorithm_id:"edge",algorithm_version:"1",input_file_id:"img1",params:{low:50,high:150}}，课堂情境可附 class_id | 202 {run_id:"r1",status:"queued"} | 400 invalid_params；404 not_found（文件或绑定）；413 payload_too_large |
| A3 GET /runs/{run_id}；GET /runs | 实验页、6；按当前账号取单条或个人记录，列表可筛案例版本 | {run_id:"r1",status:"succeeded",outputs:[{file_id:"out1",label:"边缘图"}],elapsed_ms:320,error:null}；列表 items 同型 | 404 not_found；超时查询仍为 200，status:"failed",outputs:[],error:{code:"timeout",message:"运行超时"} |

A3 在 queued/running 时 outputs=[]、elapsed_ms=null、error=null；成功后经 F1 取产物。input_schema 采用 JSON Schema 描述输入文件类型及 params；3 号负责参数间限制和版本校验。这里的 Canny 参数和 30 秒是联调样例；各算法以实际登记值为准。

**算法目录样例（A1.items 中的一项）：** 3 号交这份定义后，实验页据此画出两个输入框，6 号据此校验工具参数。下例的 `input_schema.properties.params` 与 A2 的 `params` 对应，服务端还校验图片实际内容及 low < high。

```json
{"algorithm_id":"edge","algorithm_version":"1","name":"边缘检测",
 "input_schema":{"type":"object","required":["input_file_id","params"],"properties":{
   "input_file_id":{"type":"string","description":"获准读取的 PNG 或 JPEG 文件编号"},
   "params":{"type":"object","additionalProperties":false,"properties":{
     "low":{"type":"integer","minimum":0,"maximum":255,"default":50},
     "high":{"type":"integer","minimum":0,"maximum":255,"default":150}}}}},
 "output_schema":{"type":"array","items":{"type":"object","required":["file_id","label"],"properties":{"file_id":{"type":"string"},"label":{"type":"string"}}}},
 "timeout_s":30}
```

### 教学任务、提交、批改｜4、9 号提供
| 键 · 方法/路径 | 调用方、权限与输入 | 成功示例 | 失败示例 |
|---|---|---|---|
| T1 POST /assignments | 4；所教班级教师提交 class_id/case_id/version/kind/title/instructions/due_at，可附本版 reference_file_id | 201 {assignment_id:"a1",recipient_count:4}；按发布时名单生成应交记录 | 400 invalid_deadline / invalid_reference；404 not_found |
| T2 GET /assignments；GET /assignments/{assignment_id} | 4 提供给 4/9；学生仅被分配的任务，教师仅所教班级；列表可按 class_id 过滤 | 单条 {assignment_id:"a1",class_id:"c1",case_id:"edge-case",version:1,kind:"experiment",title:"边缘实验",instructions:"交源码及结果图",due_at:"2026-12-01T12:00:00Z"}；列表 items 同型。获准教师额外可见 reference_file_id | 404 not_found |
| S1 POST /assignments/{assignment_id}/submissions | 9；名单内本人，已上传附件 {files:[{file_id:"f1",kind:"code"}],note:"我的实验"} | 201 {submission_id:"s2",assignment_id:"a1",revision:2,submitted_at:"2026-11-21T10:00:00Z"} | 409 deadline_passed；400 invalid_files；404 not_found |
| S2 GET /assignments/{assignment_id}/submissions；GET /submissions/{submission_id} | 9 提供给 4/7/9；本人或该班授权教师；学生列表为本人历史，教师可按 student_id 筛选 | 详情 {submission_id:"s2",assignment_id:"a1",student_id:"u1",revision:2,note:"我的实验",submitted_at:"2026-11-21T10:00:00Z",files:[{file_id:"f1",name:"main.py",kind:"code",language:"python",encoding:"utf-8",byte_size:84,parent_file_id:null}]}；列表 items 同型 | 404 not_found |
| S3 服务函数 read_submission_text(actor,submission_id,file_id) | 9 提供给 7；每次核对当前权限及归属，在已选版本读取有限文本 | {file_id:"f1",name:"main.py",language:"python",encoding:"utf-8",source:"x = 1"} | 404 not_found；400 unsupported_encoding；413 payload_too_large |
| T3 GET /assignments/{assignment_id}/gradebook | 4；教师按应交名单批改和查看成绩 | {items:[{student_id:"u1",submission_id:"s2",revision:2,status:"pending",score:null,comment:null}]}；未交 missing、已批 graded | 404 not_found |
| T4 PUT /submissions/{submission_id}/grade；GET /submissions/{submission_id}/grade | 4 提供；教师写 {score:0,comment:"请补实验说明"}；教师或本人读指定版本 | {submission_id:"s2",status:"graded",score:0,comment:"请补实验说明"}；待批 GET 为 pending，score/comment=null | 400 invalid_score；404 not_found；409 stale_submission（教师保存前已有新版本） |

**4 → 9 → 7 的共用样例：** a1 分配给 u1，参考文件 ref1 属于 a1 固定的案例版本。u1 第一次交 s1，重交得到 s2，后者含 f1。教师从 T3 选 s2，S2 列出 f1，随后按下例请求。故意把 s1 和只属于 s2 的 f1 配在一起，预期 404。

```json
{"submission_id":"s2","file_id":"f1","reference_file_id":"ref1"}
```

以上是 R3 的作业模式；同一文件做 R1 时只传 submission_id 和 file_id。若 ref1 内容为 `x=1`、f1 为 `x=2`，则 R3 预期 added=1、removed=1、truncated=false。教师评分始终通过 T4 写入选定提交版本。

S1 的 code/archive/image 对应源码、代码包、截图。9 号保存提交和可评审文件映射后才返回成功。教师从 T3 取 submission_id、从 S2 选 file_id 进入评审；参考文件由 T2 取得，7 号校验任务绑定及材料权限后读取。详情中的代码来源只在本地服务间传递。

### 知识问答、路由与运行配置｜5、6 号提供
| 键 · 方法/路径 | 调用方、权限与输入 | 成功示例 | 失败示例 |
|---|---|---|---|
| Q1 POST /questions | 5 提供给学⑧、师⑨、独⑥及 6；问题 {question:"高阈值的作用？",case_id:"edge-case",version:1}，可附班级 class_id；图像理解阶段可附可读 file_id | {status:"answered",answer:"…",citations:[{material_id:"m1",locator:"参数设置/第2段"}]}；无依据为 insufficient_evidence，说明写入 answer，citations:[] | 400 empty_question；404 not_found；503 service_unavailable |
| G1 POST /assistant/turns | 6 提供给师⑨、独⑦及自由对话；{message:"运行边缘检测",case_id:"edge-case",version:1}，按需附 input_file_id/algorithm_id/algorithm_version/params 或 run_id、submission_id/file_id、class_id/from/to；显式入口可传 intent | {intent:"run",state:"submitted",result:{run_id:"r1",status:"queued"}}；缺图为 {intent:"run",state:"needs_input",missing:["input_file_id"],message:"请选择图片"} | 400 unsupported_intent；404 not_found；503 service_unavailable |
| H1 GET /health；GET /admin/health | 6 汇总，1 号首页读；前者仅存活，后者需运维权限 | {status:"ok"}；管理员另有 services:[{name:"runner",status:"ok"}]，故障为 degraded/down | 403 forbidden（详细状态）；503 service_unavailable（服务未就绪） |

**6 号工具映射：** ask_course(question,case_id,version) → Q1；run_algorithm(case_id,version,algorithm_id,algorithm_version,input_file_id,params) → A2；get_run(run_id) → A3；review_submission(submission_id,file_id) → R1；class_summary(class_id,from,to) → E2。actor 由服务端传递。G1 的 intent 为 question/run/run_status/review/analytics；除提交和追问外 state=completed，result 直接使用目标接口响应。续答时客户端带回已有选择和补齐字段。粘贴源码及源码差异直接走 7 号本地入口；自然语言评审仅传授权文件标识。H1 在平台网关汇总，原型探针留在 7 号服务内部。

### 代码静态评审｜7 号提供
| 键 · 方法/路径 | 调用方、权限与输入 | 成功示例 | 失败示例 |
|---|---|---|---|
| R1 POST /reviews | 创建者粘贴 {source:"x=1",language:"python"}（language 默认 python）；作业模式 {submission_id:"s2",file_id:"f1"}。教师页、独立页或 6 调用 | 201 Review，空建议为 findings:[] | 400 invalid_source / invalid_language / unsupported_language / invalid_json；404 not_found；413 payload_too_large |
| R2 GET /reviews/{review_id} | 同入口；粘贴仅创建者读，作业记录按原提交当前授权 | 200 同一 Review | 401 unauthenticated；404 not_found |
| R3 POST /reviews/diff | 文本 {before:"x=1",after:"x=2"} 或作业 {submission_id:"s2",file_id:"f1",reference_file_id:"ref1"}，参考为旧侧 | {status:"completed",added:1,removed:1,summary:"共 1 行新增，1 行删除。",diff:[…],truncated:false}；缺参考：no_reference，added/removed=null，diff:[]，truncated:false | 400 invalid_diff（形式混用）；404 not_found（显式参考不可读或错版）；413 payload_too_large |

**Review 对象**沿用原型供页面读取的 review_id、submission_id、language、status、dimensions、summary、findings、created_at、is_ai_assisted:false、execution_performed:false；正式版增加 file_id、rule_version。每条 finding 含 id、rule、category（potential_correctness/style）、severity（warning/info）、file、line_start、line_end、title、description、suggestion，保留原型的 confidence；行号从 1 起。差异先计算全文增删数，再截取至多 1000 行详情；替换一行按一增一删。作业模式对比可省略 reference_file_id 来取得 no_reference。独立原型的 GET /health 返回 status 和 service；权限、持久化及兼容性要求见[7 号 Spec](task-07-spec.md)。

### 学情与周报｜8 号提供
| 键 · 方法/路径 | 调用方、权限与输入 | 成功示例 | 失败示例 |
|---|---|---|---|
| E1 服务函数 record_event(event)，仅服务内部 | 3/4/5/6/9；必填 event_id/type/occurred_at/user_id/status，关联字段按字典；class_id 从已验证业务上下文取 | {event_id:"e1",inserted:true}；同编号同内容重试 inserted:false | 400 invalid_event；409 event_conflict（同编号内容不同） |
| E2 GET /classes/{class_id}/analytics | 授权教师/获数据权限管理员；1/7/8 使用。from、to 为区间端点 | {class_id:"c1",as_of:"2026-11-21T10:00:00Z",submitted_pairs:2,assigned_pairs:4,completion_rate:0.5,run_success_rate:null,top_topics:[{topic:"阈值",count:2}],weekly:[{week:"2026-11-16",submitted_pairs:2,assigned_pairs:4}],scores:[{band:"90–100",count:1}]} | 400 invalid_range；404 not_found |
| E3 POST /classes/{class_id}/weekly-report | 同 E2 权限，{from,to} 指定周区间，按同一统计快照生成 | {class_id:"c1",from:"2026-11-16T00:00:00+08:00",to:"2026-11-23T00:00:00+08:00",as_of:"…",summary:"4 个应交名额中已有 2 个提交。",suggestions:["课堂再演示双阈值效果"],metrics:〈E2 响应〉} | 404 not_found；400 invalid_range |

E1 单一生产方：3 号 run.finished（succeeded/failed，带 run_id）；4 号 assignment.published / grade.saved（published/graded，带 assignment_id，评分另带 submission_id）；5 号 question.answered（answered/insufficient_evidence，可带 topic）；6 号 tool.finished（succeeded/failed，仅统计工具调用，附已有运行编号）；9 号 submission.created（submitted，带 assignment_id、submission_id）。同一条提问经过 Agent 和 RAG 时，高频问题只数 5 号事件。提交、成绩以业务事务为准，事件发送失败使用原 event_id 补发。
