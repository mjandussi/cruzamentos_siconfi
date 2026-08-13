import unittest
from io import BytesIO

import pandas as pd

from api_ranking.services.exports import (
    comparar_resultados,
    gerar_excel_demonstrativos,
    gerar_excel_msc_12_13,
    preparar_msc_12_13_para_excel,
    sanitizar_nome_aba_excel,
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

        resultado = preparar_msc_12_13_para_excel(self.msc)

        pd.testing.assert_frame_equal(self.msc, original)
        self.assertEqual(resultado["conta_contabil"].tolist(), ["2", "3"])
        self.assertEqual(resultado["mes_referencia"].tolist(), [12, 13])
        self.assertEqual(resultado["me_referencia"].tolist(), [12, 12])

    def test_excel_e_legivel_e_contem_a_aba_e_os_meses_corretos(self):
        arquivo = gerar_excel_msc_12_13(self.msc)

        with pd.ExcelFile(BytesIO(arquivo), engine="openpyxl") as excel:
            self.assertEqual(excel.sheet_names, ["MSC_Consolidada_12_13"])
            resultado = pd.read_excel(excel, sheet_name="MSC_Consolidada_12_13")

        self.assertEqual(resultado["conta_contabil"].astype(str).tolist(), ["2", "3"])
        self.assertEqual(resultado["mes_referencia"].tolist(), [12, 13])
        self.assertEqual(resultado["me_referencia"].tolist(), [12, 12])

    def test_excel_recusa_recorte_sem_meses_12_e_13(self):
        apenas_janeiro = self.msc.iloc[[0]].copy()

        with self.assertRaisesRegex(ValueError, "meses 12 e 13"):
            gerar_excel_msc_12_13(apenas_janeiro)

    def test_excel_demonstrativos_e_gerado_pelo_servico_de_exportacao(self):
        vazio = pd.DataFrame()
        bundle = {
            "cod": "3300100",
            "ente": "Angra dos Reis - RJ",
            "ano": 2025,
            "tipo_ente": "M",
            "total_ok": 3,
            "total_faltando": 1,
            "df_dca_ab": pd.DataFrame({"Conta": ["1"], "Valor": [10.0]}),
            "df_dca_c_orig": vazio,
            "df_dca_d": vazio,
            "df_dca_e": vazio,
            "df_dca_f": vazio,
            "df_dca_g": vazio,
            "df_dca_hi": vazio,
            "rreo": pd.DataFrame({"Linha": ["RREO"], "Valor": [20.0]}),
            "rgf": {"Q1": pd.DataFrame({"Linha": ["RGF"], "Valor": [30.0]})},
        }

        arquivo = gerar_excel_demonstrativos(bundle)

        with pd.ExcelFile(BytesIO(arquivo), engine="openpyxl") as excel:
            self.assertEqual(
                excel.sheet_names,
                ["Resumo", "DCA_Anexo_I-AB", "RREO", "RGF_Q1"],
            )
            resumo = pd.read_excel(excel, sheet_name="Resumo")

        observacao = resumo.loc[
            resumo["Informação"] == "Observação",
            "Valor",
        ].iloc[0]
        self.assertIn("MSC consolidada dos meses 12", observacao)
        self.assertNotIn("Diagnóstico do ambiente", observacao)

    def test_nome_de_aba_remove_caracteres_invalidos_e_respeita_limite(self):
        nome = sanitizar_nome_aba_excel(r"A/B:C?D*E[F]G\H")

        self.assertEqual(nome, "A_B_C_D_E_F_G_H")
        self.assertLessEqual(len(nome), 31)
        self.assertEqual(sanitizar_nome_aba_excel("x" * 40), "x" * 31)
        self.assertEqual(sanitizar_nome_aba_excel(""), "Aba")

    def test_comparador_ignora_obs_e_classifica_mudancas_de_resultado(self):
        colunas = [
            "Dimensão",
            "Resposta",
            "Descrição da Dimensão",
            "Nota",
            "OBS",
        ]
        antes = pd.DataFrame(
            [
                ["D2_00001", "ERRO", "Regra 1", 0.0, "observação antiga"],
                ["D3_00001", "OK", "Regra 2", 1.0, "sem alteração"],
                ["D4_00001", "OK", "Regra 3", 1.0, "texto antigo"],
            ],
            columns=colunas,
        )
        depois = pd.DataFrame(
            [
                ["D2_00001", "OK", "Regra 1", 1.0, "observação nova"],
                ["D3_00001", "ERRO", "Regra 2", 0.0, "sem alteração"],
                ["D4_00001", "OK", "Regra 3", 1.0, "texto novo"],
            ],
            columns=colunas,
        )

        comparacao = comparar_resultados(antes, depois)

        self.assertEqual(comparacao["quantidade_melhorou"], 1)
        self.assertEqual(comparacao["quantidade_piorou"], 1)
        self.assertEqual(
            comparacao["tabela_alteracoes"]["Dimensão"].tolist(),
            ["D2_00001", "D3_00001"],
        )


if __name__ == "__main__":
    unittest.main()
