"""Testes das normalizações compartilhadas pelas regras contábeis."""

import unittest

import pandas as pd

from api_ranking.analysis.common import fonte_msc_codigo_e_tres_digitos


class AnalysisCommonTests(unittest.TestCase):
    def test_fonte_msc_preserva_ausencias(self):
        source = pd.Series([float("nan"), None, pd.NA])

        code_4, code_3_number, code_3_text = (
            fonte_msc_codigo_e_tres_digitos(source)
        )

        self.assertTrue(code_4.isna().all())
        self.assertTrue(code_3_number.isna().all())
        self.assertTrue(code_3_text.isna().all())

    def test_fonte_msc_remove_sufixo_decimal_antes_de_extrair_digitos(self):
        source = pd.Series(["1500.0", 1605.0, "1.605.0"])

        code_4, code_3_number, code_3_text = (
            fonte_msc_codigo_e_tres_digitos(source)
        )

        self.assertEqual(code_4.tolist(), ["1500", "1605", "1605"])
        self.assertEqual(code_3_number.tolist(), [500, 605, 605])
        self.assertEqual(code_3_text.tolist(), ["500", "605", "605"])

    def test_fonte_msc_completa_codigos_curtos_com_zeros(self):
        source = pd.Series(["605", "5", 12])

        code_4, code_3_number, code_3_text = (
            fonte_msc_codigo_e_tres_digitos(source)
        )

        self.assertEqual(code_4.tolist(), ["0605", "0005", "0012"])
        self.assertEqual(code_3_number.tolist(), [605, 5, 12])
        self.assertEqual(code_3_text.tolist(), ["605", "005", "012"])


if __name__ == "__main__":
    unittest.main()
