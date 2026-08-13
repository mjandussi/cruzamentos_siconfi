import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from api_ranking.renders.result_dashboard import (
    filter_dimension_results,
    format_currency_pt_br,
    format_decimal_pt_br,
    format_percentage_pt_br,
    prepare_dimension_results,
    result_option_label,
    sort_results_numerically,
    style_evidence_table,
    summarize_dimension,
)


class ResultDashboardTests(unittest.TestCase):
    def setUp(self):
        self.ctx = {
            "final": pd.DataFrame(
                [
                    {
                        "Dimensão": "D2_00001",
                        "Resposta": "OK",
                        "Descrição da Dimensão": "Receitas conferidas",
                        "Nota": 1,
                        "OBS": "",
                    },
                    {
                        "Dimensão": "D2_00002",
                        "Resposta": "ERRO",
                        "Descrição da Dimensão": "Despesas divergentes",
                        "Nota": 0,
                        "OBS": "Diferença de R$ 10,00",
                    },
                    {
                        "Dimensão": "D2_00003",
                        "Resposta": "N/A",
                        "Descrição da Dimensão": "Regra estadual",
                        "Nota": None,
                        "OBS": "Não se aplica a município",
                    },
                    {
                        "Dimensão": "D2_00004",
                        "Resposta": "N/A",
                        "Descrição da Dimensão": "Arquivo ausente",
                        "Nota": None,
                        "OBS": "Dados insuficientes",
                    },
                    {
                        "Dimensão": "D3_00001",
                        "Resposta": "ERRO",
                        "Descrição da Dimensão": "Outra dimensão",
                        "Nota": 0,
                        "OBS": "",
                    },
                ]
            ),
            "d2_00002_t": pd.DataFrame({"Valor A": [10], "Valor B": [20]}),
        }

    def test_prepare_filters_dimension_sorts_priorities_and_marks_evidence(self):
        data = prepare_dimension_results(self.ctx, "D2_")

        self.assertEqual(data["Dimensão"].tolist(), [
            "D2_00002", "D2_00004", "D2_00001", "D2_00003"
        ])
        evidence = data.set_index("Dimensão")["Evidência"].to_dict()
        self.assertEqual(evidence["D2_00002"], "Disponível")
        self.assertEqual(evidence["D2_00001"], "—")

    def test_summary_separates_conclusive_and_inconclusive(self):
        summary = summarize_dimension(prepare_dimension_results(self.ctx, "D2_"))

        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["divergences"], 1)
        self.assertEqual(summary["conforming"], 1)
        self.assertEqual(summary["inconclusive"], 1)
        self.assertEqual(summary["not_applicable"], 1)
        self.assertEqual(summary["conformity_percent"], 50.0)

    def test_priority_and_text_filters_are_combined(self):
        data = prepare_dimension_results(self.ctx, "D2_")

        priorities = filter_dimension_results(data, "Prioridades")
        self.assertEqual(priorities["Dimensão"].tolist(), ["D2_00002", "D2_00004"])

        inconclusive = filter_dimension_results(data, "Inconclusivos")
        self.assertEqual(inconclusive["Dimensão"].tolist(), ["D2_00004"])

        searched = filter_dimension_results(data, "Todos", "receitas")
        self.assertEqual(searched["Dimensão"].tolist(), ["D2_00001"])

    def test_option_label_contains_code_description_and_status(self):
        data = prepare_dimension_results(self.ctx, "D2_")
        row = data.loc[data["Dimensão"] == "D2_00002"].iloc[0]

        label = result_option_label(row)

        self.assertIn("D2_00002", label)
        self.assertIn("Despesas divergentes", label)
        self.assertIn("Divergência", label)

    def test_rules_are_sorted_by_numeric_code_not_lexicographically(self):
        data = pd.DataFrame(
            {
                "Dimensão": ["D2_10", "D2_2", "D2_001", "D2_11"],
                "Descrição da Dimensão": ["dez", "dois", "um", "onze"],
            }
        )

        ordered = sort_results_numerically(data)

        self.assertEqual(
            ordered["Dimensão"].tolist(),
            ["D2_001", "D2_2", "D2_10", "D2_11"],
        )

    def test_missing_final_returns_empty_dataframe(self):
        self.assertTrue(prepare_dimension_results({}, "D4_").empty)

    def test_financial_values_use_brazilian_format(self):
        self.assertEqual(format_currency_pt_br(2552509616.55), "R$ 2.552.509.616,55")
        self.assertEqual(format_currency_pt_br(-5218064.36), "R$ -5.218.064,36")
        self.assertEqual(format_decimal_pt_br(0), "0,00")
        self.assertEqual(format_currency_pt_br(float("nan")), "—")
        self.assertEqual(format_percentage_pt_br(float("nan")), "—")

    def test_evidence_styler_preserves_numeric_source(self):
        detail = pd.DataFrame(
            {
                "DCA C": [2552509616.55],
                "DIF": [-5218064.36],
                "cod_conta": [123],
                "Taxa": [12.345],
            }
        )

        styled = style_evidence_table(detail)

        self.assertEqual(detail.loc[0, "DCA C"], 2552509616.55)
        self.assertEqual(styled._display_funcs[(0, 0)](detail.iloc[0, 0]), "R$ 2.552.509.616,55")
        self.assertEqual(styled._display_funcs[(0, 1)](detail.iloc[0, 1]), "R$ -5.218.064,36")
        self.assertEqual(styled._display_funcs[(0, 2)](detail.iloc[0, 2]), "123")
        self.assertEqual(styled._display_funcs[(0, 3)](detail.iloc[0, 3]), "12,35%")

    def test_results_explorer_renders_as_fragment_without_exception(self):
        app = AppTest.from_string(
            """
import pandas as pd
from api_ranking.renders.result_dashboard import render_results_explorer

final = pd.DataFrame([
    {
        "Dimensão": "D2_00010",
        "Resposta": "ERRO",
        "Descrição da Dimensão": "Teste divergente",
        "Nota": 0,
        "OBS": "Diferença",
    },
    {
        "Dimensão": "D3_00001",
        "Resposta": "OK",
        "Descrição da Dimensão": "Teste conforme",
        "Nota": 1,
        "OBS": "",
    },
    {
        "Dimensão": "D2_00002",
        "Resposta": "OK",
        "Descrição da Dimensão": "Teste em ordem numérica",
        "Nota": 1,
        "OBS": "",
    },
])
details = {"D2_00010": pd.DataFrame({"Valor A": [1], "Valor B": [2]})}
render_results_explorer(final, details, "smoke")
"""
        ).run(timeout=20)

        self.assertEqual(list(app.exception), [])
        self.assertEqual(len(app.tabs), 3)
        # O AppTest 1.58 representa expanders stateful como ``status``.
        self.assertEqual(len(app.status), 2)
        self.assertIn("D2_00002", app.status[0].label)
        self.assertIn("OK", app.status[0].label)
        self.assertIn("D2_00010", app.status[1].label)
        self.assertIn("ERRO", app.status[1].label)
        self.assertEqual(len(app.dataframe), 0)
        self.assertEqual(len(app.metric), 0)

    def test_two_explorers_have_independent_widget_keys(self):
        app = AppTest.from_string(
            """
import pandas as pd
from api_ranking.renders.result_dashboard import render_results_explorer

final = pd.DataFrame([{
    "Dimensão": "D2_00044",
    "Resposta": "ERRO",
    "Descrição da Dimensão": "Teste CAPAG",
    "Nota": 0,
    "OBS": "Diferença",
}])
render_results_explorer(final, {}, "first")
render_results_explorer(final, {}, "second")
"""
        ).run(timeout=20)

        self.assertEqual(list(app.exception), [])
        self.assertEqual(len(app.tabs), 6)
        self.assertEqual(len(app.status), 2)
        self.assertEqual(len(app.dataframe), 0)

    def test_open_expander_renders_formatted_evidence_without_exception(self):
        app = AppTest.from_string(
            """
import pandas as pd
import streamlit as st
from api_ranking.renders.result_dashboard import render_results_explorer

st.session_state["result_toggle_open_D2_00001"] = True
final = pd.DataFrame([{
    "Dimensão": "D2_00001",
    "Resposta": "ERRO",
    "Descrição da Dimensão": "Teste aberto",
    "Nota": 0,
    "OBS": "Diferença",
}])
details = {"D2_00001": pd.DataFrame({"Valor": [2552509616.55]})}
render_results_explorer(final, details, "open")
"""
        ).run(timeout=20)

        self.assertEqual(list(app.exception), [])
        self.assertEqual(len(app.dataframe), 1)
        self.assertEqual(len(app.error), 1)

    def test_2025_tabs_render_only_the_17_28_27_crosschecks(self):
        app = AppTest.from_string(
            """
import pandas as pd
from core.methodology import get_crosschecks
from api_ranking.renders.result_dashboard import render_results_explorer

final = pd.DataFrame([
    {
        "Dimensão": code,
        "Resposta": "OK",
        "Descrição da Dimensão": f"Regra {code}",
        "Nota": 1,
        "OBS": "",
    }
    for code in get_crosschecks(2025)
])
render_results_explorer(final, {}, "scope")
"""
        ).run(timeout=20)

        self.assertEqual(len(app.status), 17)
        app.session_state["results_tabs_scope"] = "D3 - RREO/RGF (28)"
        app.run(timeout=20)
        self.assertEqual(len(app.status), 28)
        app.session_state["results_tabs_scope"] = "D4 - DCA x RREO (27)"
        app.run(timeout=20)
        self.assertEqual(len(app.status), 27)
        self.assertEqual(list(app.exception), [])


if __name__ == "__main__":
    unittest.main()
