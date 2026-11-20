# 02｜版本化案例库

[本地 tracker 与执行约定](development.md) · [字段字典](database.md) · [接口契约](interfaces.md)

## Problem Statement

材料更新后，教师布置的任务和学生看到的引用可能落到不同版本。

## Solution

学②③与师②③共用一个按版本发布的案例库。最新版本用于浏览，历史版本继续支撑已发布任务、引用和运行。

## User Stories

1. 作为学生，我希望按关键字、难度和类别找到案例，以便快速进入需要的实验。
2. 作为学生，我希望阅读 Markdown、notebook、代码及习题，以便能找到课堂所说的具体章节或单元格。
3. 作为教师，我希望修订案例并保留旧版，以便已布置的任务继续指向原材料。
4. 作为案例维护者，我希望逐项登记 15 个案例并标明缺件，以便查清课程交付的真实覆盖范围。
5. 作为教师，我希望将参考实现设为教师可读，以便学生仍可阅读对应题干。

## Implementation Decisions

- 案例和版本使用复合键；发布时在一次事务写版本、材料和 current_version。旧版地址保持可用。
- 从 F1 存取文件；C1 列表和下载使用同一可见范围。Markdown、ipynb 静态展示并清理活动内容；代码定位保留文件/符号。
- 允许先发布阅读版；绑定实验时通过 C2 发新版，验证 A1 的算法标识与版本。
- 对接范围：C1/C2 → F1/A1；表 cases、case_versions、materials、case_algorithms。

## Testing Decisions

以教师身份发布两版，再从学生详情页及文件接口分别读取；断言旧链接仍是 v1、教师答案不可取，启动实验携带与该案例版本相同的算法绑定。

## Out of Scope

| 本模块范围外 |
|---|
| 现场执行 notebook、补写未经确认的教师答案 |

## Further Notes

课程范围以获准的 15 项实际清单为准，阅读组件可用自制材料开工。

**关联工单（按依赖领取）：** [02 从目录读 Markdown 和 notebook](../.scratch/mvstudy/issues/02-read-case.md) · [12 发布新版本并重开旧版](../.scratch/mvstudy/issues/12-publish.md) · [14 从指定案例版本启动匹配的实验](../.scratch/mvstudy/issues/14-launch.md) · [29 交付十五项实际课程案例](../.scratch/mvstudy/issues/29-course-catalog.md)
