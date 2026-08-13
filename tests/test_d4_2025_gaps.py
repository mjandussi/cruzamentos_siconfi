import unittest

import pandas as pd

from api_ranking.analysis.d4 import d4_00043, d4_00046, d4_00047


def _resposta(resultado):
    return resultado.iloc[0]['Resposta']


class D400043Tests(unittest.TestCase):
    @staticmethod
    def _fontes():
        linhas = (
            ('Recursos Não Vinculados de Impostos', '1.500'),
            ('Outros Recursos não Vinculados', '1.501'),
        )
        colunas = (
            ('111110000', 'DisponibilidadeDeCaixaBruta'),
            ('632100000', 'RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores'),
            ('632700000', 'RestosAPagarLiquidadosENaoPagosDoExercicio'),
            ('631100000', 'RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores'),
        )
        msc = []
        rgf = []
        valor = 10
        for conta_rgf, fonte in linhas:
            for conta_msc, codigo_rgf in colunas:
                msc.append({
                    'tipo_valor': 'ending_balance',
                    'conta_contabil': conta_msc,
                    'fonte_recursos': fonte,
                    'poder_orgao': '10131',
                    'valor': valor,
                })
                rgf.append({
                    'cod_conta': codigo_rgf,
                    'conta': conta_rgf,
                    'valor': valor,
                })
                valor += 10
        return pd.DataFrame(msc), pd.DataFrame(rgf)

    def test_compara_as_oito_celulas_da_matriz(self):
        msc, rgf = self._fontes()

        resultado, detalhe = d4_00043(msc, rgf)

        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(len(detalhe), 8)
        self.assertTrue((detalhe['Diferença (MSC − RGF)'] == 0).all())

    def test_qualquer_celula_divergente_retorna_erro(self):
        msc, rgf = self._fontes()
        rgf.loc[0, 'valor'] += 1

        resultado, detalhe = d4_00043(msc, rgf)

        self.assertEqual(_resposta(resultado), 'ERRO')
        self.assertEqual((detalhe['Diferença (MSC − RGF)'] != 0).sum(), 1)
        self.assertIn('1 de 8', resultado.iloc[0]['OBS'])

    def test_restringe_a_msc_ao_poder_executivo(self):
        msc, rgf = self._fontes()
        fora_do_executivo = msc.iloc[[0]].copy()
        fora_do_executivo['poder_orgao'] = '20131'
        fora_do_executivo['valor'] = 999

        resultado, _ = d4_00043(pd.concat([msc, fora_do_executivo]), rgf)

        self.assertEqual(_resposta(resultado), 'OK')

    def test_fonte_indisponivel_retorna_na(self):
        _, rgf = self._fontes()

        resultado, detalhe = d4_00043(None, rgf)

        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertTrue(pd.isna(resultado.iloc[0]['Nota']))
        self.assertTrue(detalhe.empty)


class D400046Tests(unittest.TestCase):
    codigos_rreo = (
        'RREO3ReceitaDeContribuicoes',
        'RREO3ReceitaPatrimonial',
        'RREO3ReceitaAgropecuaria',
        'RREO3ReceitaIndustrial',
        'RREO3ReceitaDeServicos',
    )
    codigos_dca = (
        'RO1.2.0.0.00.0.0',
        'RO1.3.0.0.00.0.0',
        'RO1.4.0.0.00.0.0',
        'RO1.5.0.0.00.0.0',
        'RO1.6.0.0.00.0.0',
    )

    @classmethod
    def _fontes(cls):
        rreo = pd.DataFrame([
            {
                'coluna': 'TOTAL (ÚLTIMOS 12 MESES)',
                'cod_conta': conta,
                'valor': valor,
            }
            for conta, valor in zip(cls.codigos_rreo, (10, 20, 30, 40, 50))
        ])
        dca = pd.DataFrame(
            [
                {
                    'coluna': 'Receitas Brutas Realizadas',
                    'cod_conta': conta,
                    'valor': valor,
                }
                for conta, valor in zip(cls.codigos_dca, (20, 30, 40, 50, 60))
            ]
            + [
                {
                    'coluna': 'Outras Deduções da Receita',
                    'cod_conta': conta,
                    'valor': -10,
                }
                for conta in cls.codigos_dca
            ]
        )
        return rreo, dca

    def test_compara_receita_rreo_com_receita_liquida_dca(self):
        rreo, dca = self._fontes()

        resultado, detalhe = d4_00046(rreo, dca)

        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[-1]['valor'], 0)
        self.assertEqual(detalhe.loc[3, 'valor'], 150)

    def test_divergencia_retorna_erro(self):
        rreo, dca = self._fontes()
        rreo.loc[0, 'valor'] += 1

        resultado, _ = d4_00046(rreo, dca)

        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_linhas_alvo_ausentes_retornam_na(self):
        fonte_irrelevante = pd.DataFrame([
            {'coluna': 'outra', 'cod_conta': 'outra', 'valor': 0},
        ])

        resultado, _ = d4_00046(fonte_irrelevante, fonte_irrelevante)

        self.assertEqual(_resposta(resultado), 'N/A')


class D400047Tests(unittest.TestCase):
    @staticmethod
    def _fontes(valor_rreo=100, valor_dca=-100):
        rreo = pd.DataFrame([{
            'coluna': 'TOTAL (ÚLTIMOS 12 MESES)',
            'cod_conta': 'DeducaoDeReceitaParaFormacaoDoFUNDEB',
            'valor': valor_rreo,
        }])
        dca = pd.DataFrame([{
            'coluna': 'Deduções - FUNDEB',
            'cod_conta': 'TotalReceitas',
            'valor': valor_dca,
        }])
        return rreo, dca

    def test_considera_o_sinal_negativo_da_deducao_na_dca(self):
        rreo, dca = self._fontes()

        resultado, detalhe = d4_00047(rreo, dca)

        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[-1]['valor'], 0)

    def test_divergencia_retorna_erro(self):
        rreo, dca = self._fontes(valor_dca=-90)

        resultado, _ = d4_00047(rreo, dca)

        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_fonte_indisponivel_retorna_na(self):
        rreo, _ = self._fontes()

        resultado, _ = d4_00047(rreo, None)

        self.assertEqual(_resposta(resultado), 'N/A')


if __name__ == '__main__':
    unittest.main()
