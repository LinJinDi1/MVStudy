"""Check platform source placement and cross-domain Python imports."""

import ast
from importlib.util import resolve_name
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PY_DOMAINS = Path("backend/mvstudy/domains")
VUE_DOMAINS = Path("frontend/src/features")
SOURCES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".css"}
HOST_FILES = {
    "backend/mvstudy/__init__.py", "backend/mvstudy/app.py", "backend/mvstudy/db.py",
    "backend/mvstudy/config.py", "backend/mvstudy/domains/__init__.py",
    "frontend/src/main.ts", "frontend/src/App.vue", "frontend/src/router.ts",
    "frontend/src/vite-env.d.ts", "frontend/src/env.d.ts",
}


def placement(path, domains):
    if path.suffix not in SOURCES or path.as_posix() in HOST_FILES:
        return None
    if path.parts[0] == "modules" and not path.is_relative_to("modules/task-07"):
        return "独立原型仅保留 task-07；新业务请放入正式域"
    for base in (PY_DOMAINS, VUE_DOMAINS):
        if path.is_relative_to(base):
            parts = path.relative_to(base).parts
            if len(parts) > 1 and parts[0] in domains:
                return None
            return "请放入 README 已登记的域目录"
    if path.is_relative_to("frontend/src/shared") or path.is_relative_to("frontend/src/assets"):
        return None
    if path.parent == Path("frontend") and ".config." in path.name:
        return None
    if path.parts[0] in {"frontend", "backend"} or len(path.parts) == 1:
        return "该层只放宿主入口或配置；业务代码请放入所属域"
    return None


def private_imports(path, source):
    parts = path.relative_to(PY_DOMAINS).parts
    owner = parts[0]
    package = ".".join(("mvstudy", "domains", *parts[:-1]))
    for node in ast.walk(ast.parse(source, filename=str(path))):
        if isinstance(node, ast.Import):
            targets = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            target = "." * node.level + (node.module or "")
            targets = [resolve_name(target, package)]
        else:
            continue
        for name in targets:
            route = name.split(".")
            if len(route) >= 4 and route[:2] == ["mvstudy", "domains"] and route[2] != owner:
                yield f"第 {node.lineno} 行：请从 mvstudy.domains.{route[2]} 的公开入口导入"


def host_routes(source):
    for node in ast.walk(ast.parse(source)):
        for decorator in getattr(node, "decorator_list", ()):
            if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr in {"route", "get", "post", "put", "patch", "delete"}):
                yield f"第 {decorator.lineno} 行：将 HTTP 路由放入负责该契约的业务域"


def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    domains = re.findall(r"^\| \[\d\d\]\(docs/task-\d\d-spec\.md\) \| `(\w+)`", readme, re.M)
    errors = []
    if len(set(domains)) != 9 or len(domains) != 9:
        errors.append("README 需要登记九个唯一业务域")
    for base in (PY_DOMAINS, VUE_DOMAINS):
        for name in domains:
            if not (ROOT / base / name).is_dir():
                errors.append(f"缺少域目录：{base / name}")
    # Use Git's view so generated dependencies and private workspace files stay out.
    listing = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    )
    for entry in listing.decode("utf-8").split("\0"):
        if not entry:
            continue
        path = Path(entry)
        if not (ROOT / path).is_file():
            continue
        error = placement(path, domains)
        if error:
            errors.append(f"{path}: {error}")
        elif path.as_posix() in {"backend/mvstudy/app.py", "backend/mvstudy/__init__.py"}:
            errors.extend(f"{path}: {msg}" for msg in host_routes((ROOT / path).read_text(encoding="utf-8")))
        elif path.suffix == ".py" and path.parent != PY_DOMAINS and path.is_relative_to(PY_DOMAINS):
            errors.extend(f"{path}: {msg}" for msg in private_imports(path, (ROOT / path).read_text(encoding="utf-8")))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("项目结构检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
