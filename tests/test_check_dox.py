import unittest

from scripts.check_dox import evaluate_dox_guard


class CheckDoxTest(unittest.TestCase):
    def test_dox_guard_allows_non_critical_changes(self):
        self.assertEqual(evaluate_dox_guard(["README.md"]), [])

    def test_dox_guard_flags_critical_change_without_review_artifact(self):
        findings = evaluate_dox_guard(["app/modules/riesgo_fiscal.py"])

        self.assertEqual(len(findings), 1)
        self.assertIn("app/modules/riesgo_fiscal.py", findings[0])
        self.assertIn("app/modules/AGENTS.md", findings[0])

    def test_dox_guard_accepts_nearest_agents_review(self):
        self.assertEqual(
            evaluate_dox_guard(
                [
                    "app/modules/riesgo_fiscal.py",
                    "app/modules/AGENTS.md",
                ]
            ),
            [],
        )

    def test_dox_guard_accepts_docs_or_tests_review(self):
        self.assertEqual(
            evaluate_dox_guard(
                [
                    "scripts/importar_padron.py",
                    "tests/test_importar_padron_no_estandar.py",
                ]
            ),
            [],
        )

    def test_dox_guard_ignores_generated_dirs(self):
        self.assertEqual(
            evaluate_dox_guard(["salidas/reporte.xlsx", "uploads/origen.csv"]),
            [],
        )


if __name__ == "__main__":
    unittest.main()
