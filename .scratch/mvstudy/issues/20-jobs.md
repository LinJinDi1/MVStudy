# 20 — 把实验变成可追踪的运行记录

**Parent:** [3 号 Spec](../../../docs/task-03-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** A2 入队并固定所有输入；有容量的独立进程执行，A3 供刷新和查询，F1 返回可下载产物。

**Blocked by:** [14 — 从指定案例版本启动匹配的实验](14-launch.md)；[15 — 幂等接收班级学习事件](15-events.md)

**Status:** ready-for-agent

- [ ] 两人同时提交各得 run_id 和各自结果；越界参数在入队前返回 400，产物与 succeeded 同事务登记。
- [ ] 超时、启动失败、worker 重启后失去进程均进入 failed，资源释放，产生唯一终态事件。
