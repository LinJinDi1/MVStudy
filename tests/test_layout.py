import unittest
from pathlib import Path

from tools.check_layout import host_routes, placement, private_imports


class LayoutTest(unittest.TestCase):
    def test_host_registers_blueprints_instead_of_implementing_routes(self):
        self.assertEqual(list(host_routes("app.register_blueprint(platform)")), [])
        self.assertTrue(list(host_routes("@app.post('/login')\ndef login(): pass")))

    def test_host_and_domain_files(self):
        domains = {"assistant", "experiments"}
        for path in ("frontend/src/App.vue", "frontend/vite.config.ts",
                     "frontend/src/features/experiments/RunPanel.vue",
                     "backend/mvstudy/domains/assistant/dispatch.py"):
            self.assertIsNone(placement(Path(path), domains), path)
        for path in ("backend/grading.py", "frontend/src/RunPanel.vue", "modules/task-06/backend/app.py",
                     "frontend/src/features/experiments.ts", "backend/mvstudy/domains/misc/run.py"):
            self.assertIsNotNone(placement(Path(path), domains), path)

    def test_cross_domain_call_uses_public_package(self):
        path = Path("backend/mvstudy/domains/assistant/dispatch.py")
        source = """from mvstudy.domains.experiments import submit_run
from .prompt import instructions
from ..experiments.models import Run
import mvstudy.domains.experiments.queue
"""
        errors = list(private_imports(path, source))
        self.assertEqual(len(errors), 2)
        self.assertIn("第 3 行", errors[0])
        self.assertIn("第 4 行", errors[1])
