# 05 — 从教学材料定位一条可引用证据

**Parent:** [5 号 Spec](../../../docs/task-05-spec.md) · [共享契约与关闭规则](../../../docs/development.md)

**What to build:** 用自制课程材料建立可调用的切分与关键词检索基线，按用户能读的材料返回出处，供课程题集对照。

**Blocked by:** None — can start immediately

**Status:** done

**Implementation commit:** 90da4c8

- [x] 讲义定位到章节、代码到函数、notebook 到单元格；习题与答案分别授权。
- [x] 同一题教师可找到教师材料，学生的候选集合只含可见材料；无命中返回缺依据。

**Test command & result:**
```
PYTHONPATH=backend .venv/Scripts/python.exe -m unittest mvstudy.domains.knowledge.test_citation -v
Ran 9 tests ... OK

PYTHONPATH=backend .venv/Scripts/python.exe -m unittest mvstudy.domains.knowledge.test_citation mvstudy.domains.review.test_static_review
Ran 12 tests ... OK

python tools/check_layout.py        → 项目结构检查通过
pyflakes backend/mvstudy/domains/knowledge/  → 无告警
```
