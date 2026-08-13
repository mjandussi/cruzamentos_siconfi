import unittest

import pandas as pd

from api_ranking.analysis import d3


def _resposta(resultado):
    return resultado.iloc[0]['Resposta']


def _linha(coluna, cod_conta, valor, **extra):
    return {
        'coluna': coluna,
        'cod_conta': cod_conta,
        'valor': valor,
        **extra,
    }


class D3Lacunas2025Tests(unittest.TestCase):
    def test_d3_00017_compara_rpp_e_rpnp_separadamente(self):
        rreo_6 = pd.DataFrame([
            _linha(
                'RESTOS A PAGAR PROCESSADOS PAGOS (b)',
                'DespesasCorrentesExcetoFontesRPPS',
                30,
            ),
            _linha('PAGOS (c)', 'DespesasCorrentesExcetoFontesRPPS', 20),
        ])
        rreo_7 = pd.DataFrame([
            {
                'cod_conta': 'RestosAPagarProcessadosENaoProcessadosLiquidadosPagos',
                'conta': 'TOTAL (III) = (I + II)',
                'valor': 30,
            },
            {
                'cod_conta': 'RestosAPagarNaoProcessadosPagos',
                'conta': 'TOTAL (III) = (I + II)',
                'valor': 20,
            },
        ])

        resultado, detalhe = d3.d3_00017(rreo_6, rreo_7)
        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[-1]['rpp_pagos'], 0)
        self.assertEqual(detalhe.iloc[-1]['rpnp_pagos'], 0)

        rreo_7.loc[rreo_7['cod_conta'] == 'RestosAPagarNaoProcessadosPagos', 'valor'] = 21
        resultado, _ = d3.d3_00017(rreo_6, rreo_7)
        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_d3_00017_nao_aprova_insumo_ausente(self):
        vazio_6 = pd.DataFrame(columns=['coluna', 'cod_conta', 'valor'])
        vazio_7 = pd.DataFrame(columns=['conta', 'cod_conta', 'valor'])
        resultado, detalhe = d3.d3_00017(vazio_6, vazio_7)
        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertTrue(detalhe.empty)

    def test_d3_00026_compara_caixa_por_grupo_de_fonte(self):
        msc = pd.DataFrame([{
            'tipo_valor': 'ending_balance',
            'conta_contabil': '111110000',
            'fonte_recursos': '1500',
            'poder_orgao': '10131',
            'valor': 100,
        }])
        rgf = pd.DataFrame([{
            'cod_conta': 'DisponibilidadeDeCaixaBruta',
            'conta': 'Recursos Não Vinculados de Impostos',
            'valor': 100,
        }])

        resultado, detalhe = d3.d3_00026(msc, rgf)
        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[0]['Diferença (MSC − RGF)'], 0)

        rgf.loc[0, 'valor'] = 90
        resultado, _ = d3.d3_00026(msc, rgf)
        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_d3_00027_e_00028_cruzam_anexos_1_e_6(self):
        rreo_1 = pd.DataFrame([
            _linha('DOTAÇÃO ATUALIZADA (e)', 'TotalDespesas', 100),
            _linha('DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)', 'TotalDespesas', 80),
            _linha('DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)', 'TotalDespesas', 70),
            _linha('Até o Bimestre (c)', 'TotalReceitas', 90),
            _linha('PREVISÃO ATUALIZADA (a)', 'TotalReceitas', 120),
        ])
        rreo_6 = pd.DataFrame([
            _linha('DOTAÇÃO ATUALIZADA', 'DespesasCorrentesExcetoFontesRPPS', 100),
            _linha('DESPESAS EMPENHADAS', 'DespesasCorrentesExcetoFontesRPPS', 80),
            _linha('DESPESAS LIQUIDADAS', 'DespesasCorrentesExcetoFontesRPPS', 70),
            _linha('RECEITAS REALIZADAS (a)', 'ReceitasCorrentesExcetoFontesRPPS', 90),
            _linha('PREVISÃO ATUALIZADA', 'ReceitasCorrentesExcetoFontesRPPS', 120),
        ])

        for funcao in (d3.d3_00027, d3.d3_00028):
            with self.subTest(funcao=funcao.__name__):
                resultado, detalhe = funcao(rreo_1, rreo_6)
                self.assertEqual(_resposta(resultado), 'OK')
                self.assertFalse(detalhe.empty)

        rreo_6.loc[rreo_6['coluna'] == 'DESPESAS LIQUIDADAS', 'valor'] = 71
        resultado, _ = d3.d3_00027(rreo_1, rreo_6)
        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_d3_00030_00032_00034_e_00047_cruzam_rpps(self):
        rreo_1 = pd.DataFrame([
            _linha('PREVISÃO ATUALIZADA (a)', 'RecursosArrecadadosEmExerciciosAnteriores', 50),
            _linha('DOTAÇÃO ATUALIZADA (e)', 'ReservaDoRPPS', 60),
        ])
        rreo_4 = pd.DataFrame([
            _linha('PREVISÃO ATUALIZADA (a)', 'TotalReceitasRPPSPrevidenciario', 100),
            _linha('RECEITAS REALIZADAS ATÉ O BIMESTRE (b)', 'TotalReceitasRPPSPrevidenciario', 80),
            _linha('PREVISÃO ORÇAMENTÁRIA', 'RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario', 50),
            _linha('PREVISÃO ORÇAMENTÁRIA', 'ReservaOrcamentariaDoRPPSPrevidenciario', 60),
        ])
        rreo_6 = pd.DataFrame([
            _linha('PREVISÃO ATUALIZADA', 'ReceitasPrimariasCorrentesComFontesRPPS', 100),
            _linha('RECEITAS REALIZADAS (a)', 'ReceitasPrimariasCorrentesComFontesRPPS', 80),
            _linha('PREVISÃO ORÇAMENTÁRIA', 'RecursosArrecadadosEmExerciciosAnteriores', 50),
            _linha('PREVISÃO ORÇAMENTÁRIA', 'ReservaOrcamentariaDoRPPSPrevidenciario', 60),
        ])

        casos = (
            (d3.d3_00030, (rreo_4, rreo_6)),
            (d3.d3_00032, (rreo_1, rreo_4, rreo_6)),
            (d3.d3_00034, (rreo_1, rreo_4, rreo_6)),
            (d3.d3_00047, (rreo_4, rreo_6)),
        )
        for funcao, argumentos in casos:
            with self.subTest(funcao=funcao.__name__):
                resultado, detalhe = funcao(*argumentos)
                self.assertEqual(_resposta(resultado), 'OK')
                self.assertFalse(detalhe.empty)

        rreo_6.loc[
            rreo_6['cod_conta'] == 'ReservaOrcamentariaDoRPPSPrevidenciario',
            'valor',
        ] = 61
        for funcao, argumentos in (
            (d3.d3_00034, (rreo_1, rreo_4, rreo_6)),
            (d3.d3_00047, (rreo_4, rreo_6)),
        ):
            with self.subTest(divergencia=funcao.__name__):
                resultado, _ = funcao(*argumentos)
                self.assertEqual(_resposta(resultado), 'ERRO')

    def test_linhas_obrigatorias_ausentes_retornam_na(self):
        irrelevante = pd.DataFrame([_linha('Outra coluna', 'OutraConta', 0)])
        casos = (
            (d3.d3_00030, (irrelevante, irrelevante)),
            (d3.d3_00032, (irrelevante, irrelevante, irrelevante)),
            (d3.d3_00034, (irrelevante, irrelevante, irrelevante)),
            (d3.d3_00044, (irrelevante, irrelevante)),
        )
        for funcao, argumentos in casos:
            with self.subTest(funcao=funcao.__name__):
                resultado, detalhe = funcao(*argumentos)
                self.assertEqual(_resposta(resultado), 'N/A')
                self.assertTrue(detalhe.empty)

    def test_d3_00033_e_00035_cruzam_saldos_do_rreo(self):
        rreo_1 = pd.DataFrame([
            _linha('PREVISÃO ATUALIZADA (a)', 'SuperavitFinanceiro', 25),
            _linha('DOTAÇÃO ATUALIZADA (e)', 'ReservaDeContingencia', 40),
        ])
        rreo_6 = pd.DataFrame([
            _linha('PREVISÃO ORÇAMENTÁRIA', 'SuperavitFinanceiro', 25),
            _linha('DOTAÇÃO ATUALIZADA', 'RREO6ReservaDeContingencia', 40),
        ])

        for funcao in (d3.d3_00033, d3.d3_00035):
            with self.subTest(funcao=funcao.__name__):
                resultado, detalhe = funcao(rreo_1, rreo_6)
                self.assertEqual(_resposta(resultado), 'OK')
                self.assertFalse(detalhe.empty)

        rreo_6.loc[rreo_6['cod_conta'] == 'SuperavitFinanceiro', 'valor'] = 24
        resultado, _ = d3.d3_00033(rreo_1, rreo_6)
        self.assertEqual(_resposta(resultado), 'ERRO')

    @staticmethod
    def _anexos_1_e_9(codigo_a1, codigo_a9):
        rreo_1 = pd.DataFrame([
            _linha('DOTAÇÃO ATUALIZADA (e)', codigo_a1, 100),
            _linha('DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)', codigo_a1, 80),
        ])
        rreo_9 = pd.DataFrame([
            _linha('DOTAÇÃO ATUALIZADA (d)', codigo_a9, 100),
            _linha('DESPESAS EMPENHADAS (e)', codigo_a9, 80),
        ])
        return rreo_1, rreo_9

    def test_d3_00037_00038_e_00039_cruzam_despesas_com_anexo_9(self):
        casos = (
            (d3.d3_00037, 'Investimentos', 'Investimentos'),
            (d3.d3_00038, 'InversoesFinanceiras', 'InversoesFinanceiras'),
            (d3.d3_00039, 'AmortizacaoDaDivida', 'AmortizacaoDaDivida'),
        )
        for funcao, codigo_a1, codigo_a9 in casos:
            with self.subTest(funcao=funcao.__name__):
                rreo_1, rreo_9 = self._anexos_1_e_9(codigo_a1, codigo_a9)
                resultado, detalhe = funcao(rreo_1, rreo_9)
                self.assertEqual(_resposta(resultado), 'OK')
                self.assertFalse(detalhe.empty)

                rreo_9.loc[rreo_9['coluna'] == 'DESPESAS EMPENHADAS (e)', 'valor'] = 79
                resultado, _ = funcao(rreo_1, rreo_9)
                self.assertEqual(_resposta(resultado), 'ERRO')

    def test_d3_00040_cruza_operacoes_de_credito(self):
        rreo_1 = pd.DataFrame([
            _linha('PREVISÃO ATUALIZADA (a)', 'ReceitasDeOperacoesDeCredito', 100),
            _linha('Até o Bimestre (c)', 'ReceitasDeOperacoesDeCredito', 70),
        ])
        rreo_9 = pd.DataFrame([
            _linha('PREVISÃO ATUALIZADA (a)', 'RREO9ReceitasDeOperacoesDeCredito', 100),
            _linha('RECEITAS REALIZADAS (b)', 'RREO9ReceitasDeOperacoesDeCredito', 70),
        ])

        resultado, detalhe = d3.d3_00040(rreo_1, rreo_9)
        self.assertEqual(_resposta(resultado), 'OK')
        self.assertFalse(detalhe.empty)

        rreo_9.loc[rreo_9['coluna'] == 'RECEITAS REALIZADAS (b)', 'valor'] = 71
        resultado, _ = d3.d3_00040(rreo_1, rreo_9)
        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_d3_00044_cruza_transferencias_para_agentes_comunitarios(self):
        rreo_3 = pd.DataFrame([_linha(
            'TOTAL (ÚLTIMOS 12 MESES)',
            'RREO3TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude',
            75,
        )])
        rgf_1e = pd.DataFrame([_linha(
            'Valor',
            'TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude',
            75,
        )])

        resultado, detalhe = d3.d3_00044(rreo_3, rgf_1e)
        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[-1]['valor'], 0)

        rgf_1e.loc[0, 'valor'] = 74
        resultado, _ = d3.d3_00044(rreo_3, rgf_1e)
        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_as_15_funcoes_estao_implementadas_e_fora_dos_stubs(self):
        codigos = (
            '00017', '00026', '00027', '00028', '00030',
            '00032', '00033', '00034', '00035', '00037',
            '00038', '00039', '00040', '00044', '00047',
        )
        for codigo in codigos:
            with self.subTest(codigo=codigo):
                funcao = getattr(d3, f'd3_{codigo}')
                self.assertEqual(funcao.__name__, f'd3_{codigo}')
                self.assertNotIn(f'd3_{codigo}', d3._REMOVED_ANALYSES_ARITY)


if __name__ == '__main__':
    unittest.main()
