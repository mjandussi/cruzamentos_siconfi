"""Testes pequenos do escopo metodológico e do resumo diagnóstico."""

from __future__ import annotations

import ast
import math
from pathlib import Path
import unittest

import api_ranking.analysis.d2_dca as d2
import api_ranking.analysis.d3 as d3
import api_ranking.analysis.d4 as d4
from core.diagnostics import DiagnosticStatus, classify_result, summarize_results
from core.methodology import (
    DIMENSOES_CRUZAMENTO_2023,
    DIMENSOES_CRUZAMENTO_2024,
    DIMENSOES_CRUZAMENTO_2025,
    DIMENSOES_CRUZAMENTO_SEM_MSC_2025,
    classify_icf,
    eh_verificacao_capag,
    get_crosscheck_counts,
    get_crosschecks,
    get_crosschecks_without_msc,
)


class MethodologyTests(unittest.TestCase):
    def test_authoritative_counts(self) -> None:
        self.assertEqual(
            get_crosscheck_counts(2023),
            {"D2": 7, "D3": 17, "D4": 24, "total": 48},
        )
        self.assertEqual(
            get_crosscheck_counts(2024),
            {"D2": 7, "D3": 28, "D4": 26, "total": 61},
        )
        self.assertEqual(
            get_crosscheck_counts(2025),
            {"D2": 17, "D3": 28, "D4": 27, "total": 72},
        )

    def test_lists_are_unique_and_immutable(self) -> None:
        for codes in (
            DIMENSOES_CRUZAMENTO_2023,
            DIMENSOES_CRUZAMENTO_2024,
            DIMENSOES_CRUZAMENTO_2025,
        ):
            self.assertIsInstance(codes, tuple)
            self.assertEqual(len(codes), len(set(codes)))

        self.assertEqual(get_crosschecks(2025, "D2")[-1], "D2_00104")
        self.assertEqual(get_crosschecks(2025, 3)[-1], "D3_00047")
        self.assertEqual(get_crosschecks(2025, "4")[-1], "D4_00047")
        with self.assertRaises(ValueError):
            get_crosschecks(2026)

    def test_2025_without_msc(self) -> None:
        self.assertEqual(len(DIMENSOES_CRUZAMENTO_SEM_MSC_2025), 36)
        self.assertEqual(len(get_crosschecks_without_msc(2025, "D3")), 23)
        self.assertEqual(len(get_crosschecks_without_msc(2025, "D4")), 13)
        self.assertTrue(
            set(get_crosschecks_without_msc(2025)).issubset(get_crosschecks(2025))
        )
        with self.assertRaises(ValueError):
            get_crosschecks_without_msc(2024)

    def test_icf_exact_boundaries(self) -> None:
        percent_cases = {
            95: "A", 94.999: "B", 85: "B", 84.999: "C",
            75: "C", 74.999: "D", 65: "D", 64.999: "E",
        }
        for score, expected in percent_cases.items():
            with self.subTest(score=score):
                self.assertEqual(classify_icf(score, scale="percent"), expected)

        for score, expected in ((0.95, "A"), (0.85, "B"), (0.75, "C"), (0.65, "D")):
            self.assertEqual(classify_icf(score, scale="proportion"), expected)
        self.assertEqual(classify_icf(None), "N/A")
        self.assertEqual(classify_icf(math.nan), "N/A")

    def test_capag_usa_catalogo_e_descricao_explicita(self) -> None:
        self.assertTrue(eh_verificacao_capag("D2_00044"))
        self.assertTrue(eh_verificacao_capag("D9_99999", "Regra CAPAG nova"))
        self.assertFalse(eh_verificacao_capag("D4_00047", "FUNDEB"))

    def test_all_2025_crosschecks_have_concrete_functions(self) -> None:
        modules = {"D2": d2, "D3": d3, "D4": d4}
        codes = get_crosschecks(2025)
        missing = [
            code
            for code in codes
            if code.lower() not in vars(modules[code[:2]])
        ]
        self.assertEqual(missing, [])
        self.assertEqual(
            {
                dimension: sum(
                    code.lower() in vars(modules[dimension])
                    for code in codes
                    if code.startswith(dimension)
                )
                for dimension in modules
            },
            {"D2": 17, "D3": 28, "D4": 27},
        )

    def test_all_2025_crosschecks_are_called_by_online_page(self) -> None:
        page = Path(__file__).parents[1] / "pages" / "01_✅ Cruzamentos do Ranking.py"
        tree = ast.parse(page.read_text(encoding="utf-8"))
        module_names = {"d2_dca_analysis", "d3_analysis", "d4_analysis"}
        called = {
            node.func.attr.upper()
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in module_names
        }
        self.assertEqual(set(get_crosschecks(2025)) - called, set())


class DiagnosticTests(unittest.TestCase):
    def test_status_vocabulary(self) -> None:
        cases = (
            ("OK", "", DiagnosticStatus.CONFORME),
            ("⚠️ OK (Dif. Centavos)", "", DiagnosticStatus.CONFORME),
            ("ERRO", "Diferença de R$ 10", DiagnosticStatus.DIVERGENCIA),
            ("Divergência encontrada", "", DiagnosticStatus.DIVERGENCIA),
            ("N/A", "DCA não enviada", DiagnosticStatus.DADOS_INSUFICIENTES),
            ("N/A", "Não se aplica ao ente", DiagnosticStatus.NAO_APLICAVEL),
            ("ERRO", "Erro ao executar a análise", DiagnosticStatus.FALHA_TECNICA),
        )
        for response, observation, expected in cases:
            with self.subTest(response=response, observation=observation):
                self.assertIs(classify_result(response, observation), expected)

    def test_summary_uses_authoritative_denominator(self) -> None:
        expected = ("D2_00044", "D3_00002", "D4_00001", "D4_00002")
        summary = summarize_results(
            [
                {"Dimensão": "D2_00044", "Resposta": "OK"},
                {"Dimensão": "D3_00002", "Resposta": "ERRO"},
                {"Dimensão": "D4_00001", "Resposta": "N/A", "OBS": "Não se aplica"},
            ],
            expected,
        )
        overall = summary["overall"]
        self.assertEqual(overall["expected"], 4)
        self.assertEqual(overall["received"], 3)
        self.assertEqual(overall["conclusive"], 2)
        self.assertEqual(overall["missing"], 1)
        self.assertEqual(overall["coverage_percent"], 50.0)
        self.assertEqual(overall["conformity_percent"], 50.0)
        self.assertEqual(summary["by_dimension"]["D4"]["expected"], 2)


if __name__ == "__main__":
    unittest.main()
