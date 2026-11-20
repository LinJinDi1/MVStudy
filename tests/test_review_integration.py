import runpy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from mvstudy.app import create_review_demo
from mvstudy.domains.review import review_source


class ReviewDemoTest(unittest.TestCase):
    def test_old_and_new_entries_share_rules_and_http_contract(self):
        legacy = ROOT / "modules/task-07/backend"
        self.assertIs(runpy.run_path(str(legacy / "review_service.py"))["review_source"], review_source)
        for app in (create_review_demo(), runpy.run_path(str(legacy / "app.py"))["app"]):
            with self.subTest(app=app):
                client = app.test_client()
                self.assertEqual(client.get("/api/health").json["service"], "task-seven-review-api")
                response = client.post("/api/reviews", json={"source": "print(threshold)"})
                self.assertEqual(response.status_code, 201)
                review = response.json
                self.assertFalse(review["execution_performed"])
                self.assertEqual(review["findings"][0]["rule"], "python/undefined-name")
                self.assertEqual(client.get("/api/reviews/" + review["review_id"]).json, review)
                self.assertEqual(client.post("/api/reviews/diff", json={"before": "x=1", "after": "x=2"}).json["summary"],
                                 "共 1 行新增，1 行删除。")
                self.assertEqual(client.post("/api/reviews", json={"source": " "}).status_code, 400)
                self.assertEqual(client.post("/api/reviews", json={"source": "x" * (512 * 1024)}).status_code, 413)
                self.assertEqual(create_review_demo().test_client().get("/api/reviews/" + review["review_id"]).status_code, 404)
