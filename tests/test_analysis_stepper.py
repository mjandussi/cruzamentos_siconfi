import unittest

from core.layout import resolve_analysis_step


class AnalysisStepperTests(unittest.TestCase):
    def test_step_follows_workflow_state(self):
        cases = (
            ("sem contexto", False, True, True, True, 1),
            ("seleção", True, False, False, False, 1),
            ("extrato", True, True, False, False, 2),
            ("processamento", True, True, True, False, 3),
            ("resultados", True, True, False, True, 4),
        )

        for name, selected, extract, processing, results, expected in cases:
            with self.subTest(name=name):
                self.assertEqual(
                    resolve_analysis_step(
                        context_selected=selected,
                        extract_ready=extract,
                        processing=processing,
                        results_ready=results,
                    ),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
