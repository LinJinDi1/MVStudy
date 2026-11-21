import contextlib
import io
import unittest

from mvstudy.app import create_review_demo


class StaticReviewContractTest(unittest.TestCase):
    def setUp(self):
        self.client = create_review_demo().test_client()

    def test_rule_categories_versions_and_display_fields(self):
        source = "try:\n    print(missing)\nexcept:\n    pass\n#" + "x" * 121
        response = self.client.post("/api/reviews", json={"source": source})
        self.assertEqual(response.status_code, 201)
        review = response.json
        by_rule = {finding["rule"]: finding for finding in review["findings"]}
        self.assertEqual(set(by_rule), {"python/bare-except", "python/undefined-name", "style/line-length"})
        self.assertEqual(review["rule_version"], "1.0")
        for rule, line, category in (
            ("python/bare-except", 3, "potential_correctness"),
            ("python/undefined-name", 2, "potential_correctness"),
            ("style/line-length", 5, "style"),
        ):
            with self.subTest(rule=rule):
                finding = by_rule[rule]
                self.assertEqual((finding["category"], finding["line_start"], finding["line_end"]),
                                 (category, line, line))
                self.assertEqual(finding["file"], "submission.py")
                for field in ("id", "severity", "title", "description", "suggestion", "confidence"):
                    self.assertTrue(finding[field])
        saved = self.client.get("/api/reviews/" + review["review_id"])
        self.assertEqual(saved.json, review)

    def test_valid_python_is_not_executed_and_returns_empty_findings(self):
        source = 'try:\n    print("do not execute")\nexcept ValueError:\n    pass\n'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            response = self.client.post("/api/reviews", json={"source": source})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["findings"], [])
        self.assertIs(response.json["execution_performed"], False)
        self.assertEqual(output.getvalue(), "")

    def test_other_supported_languages_keep_line_length_checks(self):
        for language in ("javascript", "typescript", "java", "c", "cpp"):
            with self.subTest(language=language):
                response = self.client.post("/api/reviews", json={"source": "x" * 121, "language": language})
                self.assertEqual(response.status_code, 201)
                self.assertEqual(
                    [(item["rule"], item["category"], item["line_start"]) for item in response.json["findings"]],
                    [("style/line-length", "style", 1)],
                )
