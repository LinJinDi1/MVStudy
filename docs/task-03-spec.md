# 03｜在线实验与算法执行

[本地 tracker 与执行约定](development.md) · [字段字典](database.md) · [接口契约](interfaces.md)

## Problem Statement

教学算法各有输入、运行环境和计算开销，学生与助教需要拿到同一次运行的真实状态及结果。

## Solution

学④、师④和助教共用登记目录、排队执行和产物查询。刷新页面仍能找到同一运行。

## User Stories

1. 作为学生，我希望上传图片并看到该算法的参数与范围，以便能正确开始实验。
2. 作为教师，我希望按指定案例版本重复运行，以便能解释同一算法和参数的结果。
3. 作为同时实验的学生，我希望分别收到运行编号，以便可以独立查询排队情况和自己的产物。
4. 作为助教调用方，我希望区分超时、失败和成功，以便只用真实产物回答。
5. 作为部署成员，我希望拿到全部 15 项的可复现输入和资源要求，以便在目标机配置并发。

## Implementation Decisions

- 只用登记的算法版本与受控文件编号；实验页和工具端共用 A1～A3。校验文件、绑定、参数及资源范围后写入 queued。
- PostgreSQL runs 作为持久任务队列，以行锁领取任务并置 running；专用 worker 在独立进程运行教学代码。按环境限制进程数与超时，完成后原子登记产物及终态。
- 单 worker 调度器启动时清理上次遗留的 running；未领取的 queued 继续执行。终态事件按运行编号去重。算法自己的依赖与平台 Python 环境隔离。
- 对接范围：A1/A2/A3 → C1、F1、E1；algorithms、runs、run_outputs。

## Testing Decisions

通过实验 UI/API 提交已知图像，等待终态后从 F1 读取并核对输出特征；交叉读取两人结果、重启 worker、制造超时，逐项断言状态与任务可恢复性。

## Out of Scope

| 本模块范围外 |
|---|
| 运行任意 Python 或学生作业 |

## Further Notes

先用受控小算子跑通软件路径；正式验收按实验室算子逐一登记。

**关联工单（按依赖领取）：** [03 运行一个预登记的本地教学样例](../.scratch/mvstudy/issues/03-single-run.md) · [13 按版本查找登记算法](../.scratch/mvstudy/issues/13-registry.md) · [20 把实验变成可追踪的运行记录](../.scratch/mvstudy/issues/20-jobs.md) · [30 从十五个案例运行配套教学算法](../.scratch/mvstudy/issues/30-course-algorithms.md)
