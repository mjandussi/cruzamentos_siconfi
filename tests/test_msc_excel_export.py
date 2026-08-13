import unittest
from io import BytesIO
from pathlib import Path

import pandas as pd

from core.utils import (
    convert_msc_12_13_to_excel,
    prepare_msc_12_13_for_excel,
)


class MscExcelExportTests(unittest.TestCase):
    def setUp(self):
        self.msc = pd.DataFrame(
            [
                {
                    "tipo_matriz": "MSCC",
                    "co_tipo_matriz": "MSCC",
                    "mes_referencia": 1,
                    "me_referencia": 1,
                    "conta_contabil": "1",
                    "valor": 10.0,
                },
                {
                    "tipo_matriz": "MSCC",
                    "co_tipo_matriz": "MSCC",
                    "mes_referencia": 12,
                    "me_referencia": 12,
                    "conta_contabil": "2",
                    "valor": 20.0,
                },
                {
                    "tipo_matriz": "MSCE",
                    "co_tipo_matriz": "MSCE",
                    "mes_referencia": 12,
                    "me_referencia": 12,
                    "conta_contabil": "3",
                    "valor": 30.0,
                },
            ]
        )

    def test_prepara_somente_dezembro_e_encerramento_sem_mutar_origem(self):
        original = self.msc.copy(deep=True)

        resultado = prepare_msc_12_13_for_excel(self.msc)

        pd.testing.assert_frame_equal(self.msc, original)
        self.assertEqual(resultado["conta_contabil"].tolist(), ["2", "3"])
        self.assertEqual(resultado["mes_referencia"].tolist(), [12, 13])
        self.assertEqual(resultado["me_referencia"].tolist(), [12, 12])

    def test_excel_e_legivel_e_contem_a_aba_e_os_meses_corretos(self):
        arquivo = convert_msc_12_13_to_excel(self.msc)

        with pd.ExcelFile(BytesIO(arquivo), engine="openpyxl") as excel:
            self.assertEqual(excel.sheet_names, ["MSC_Consolidada_12_13"])
            resultado = pd.read_excel(excel, sheet_name="MSC_Consolidada_12_13")

        self.assertEqual(resultado["conta_contabil"].astype(str).tolist(), ["2", "3"])
        self.assertEqual(resultado["mes_referencia"].tolist(), [12, 13])
        self.assertEqual(resultado["me_referencia"].tolist(), [12, 12])

    def test_excel_recusa_recorte_sem_meses_12_e_13(self):
        apenas_janeiro = self.msc.iloc[[0]].copy()

        with self.assertRaisesRegex(ValueError, "meses 12 e 13"):
            convert_msc_12_13_to_excel(apenas_janeiro)

    def test_diagnostico_tecnico_nao_aparece_mais_na_pagina(self):
        raiz = Path(__file__).resolve().parents[1]
        pagina = next((raiz / "pages").glob("01_*Cruzamentos do Ranking.py"))
        codigo = pagina.read_text(encoding="utf-8")

        self.assertNotIn("Diagnóstico do ambiente", codigo)
        self.assertNotIn("_diagnostico_ambiente_exportacao", codigo)
        self.assertIn("Baixar Excel da MSC (meses 12 e 13)", codigo)


if __name__ == "__main__":
    unittest.main()
