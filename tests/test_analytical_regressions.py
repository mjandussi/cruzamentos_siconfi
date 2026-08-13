import unittest

import pandas as pd

from api_ranking.analysis.d3 import d3_00009
from api_ranking.analysis.d4 import d4_00017, d4_00027, d4_00028


def _resposta(resultado):
    return resultado.iloc[0]['Resposta']


class D300009Tests(unittest.TestCase):
    @staticmethod
    def _rgf(rpnp, rpp):
        return pd.DataFrame([
            {
                'cod_conta': 'RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores',
                'conta': 'TOTAL (IV) = (I + II + III)',
                'anexo': 'RGF-Anexo 05',
                'valor': rpnp,
            },
            {
                'cod_conta': 'RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores',
                'conta': 'TOTAL (IV) = (I + II + III)',
                'anexo': 'RGF-Anexo 05',
                'valor': rpp,
            },
        ])

    @staticmethod
    def _rreo(rpnp, rpp):
        return pd.DataFrame([
            {
                'cod_conta': 'RestosAPagarNaoProcessadosAPagar',
                'conta': 'TOTAL (III) = (I + II)',
                'anexo': 'RREO-Anexo 07',
                'valor': rpnp,
            },
            {
                'cod_conta': 'RestosAPagarProcessadosENaoProcessadosLiquidadosAPagar',
                'conta': 'TOTAL (III) = (I + II)',
                'anexo': 'RREO-Anexo 07',
                'valor': rpp,
            },
        ])

    def test_rejeita_compensacao_entre_rpp_e_rpnp(self):
        rgf_outros = pd.DataFrame(columns=['cod_conta', 'conta', 'anexo', 'valor'])

        resultado, detalhe = d3_00009(
            self._rgf(rpnp=100, rpp=0),
            rgf_outros,
            self._rreo(rpnp=0, rpp=100),
            tipo_ente='M',
        )

        self.assertEqual(_resposta(resultado), 'ERRO')
        diferencas = detalhe.loc[detalhe['fonte'] == 'Diferença (RGF − RREO)'].iloc[0]
        self.assertEqual(diferencas['rpp_rpnp_total'], 0)
        self.assertEqual(diferencas['dif_rpp'], -100)
        self.assertEqual(diferencas['dif_rpnp'], 100)

    def test_aprova_quando_rpp_e_rpnp_conferem_individualmente(self):
        rgf_outros = pd.DataFrame(columns=['cod_conta', 'conta', 'anexo', 'valor'])

        resultado, _ = d3_00009(
            self._rgf(rpnp=80, rpp=20),
            rgf_outros,
            self._rreo(rpnp=80, rpp=20),
            tipo_ente='M',
        )

        self.assertEqual(_resposta(resultado), 'OK')


class D400017Tests(unittest.TestCase):
    @staticmethod
    def _rreo(contribuicao=100, compensacao=50):
        return pd.DataFrame([
            {
                'coluna': 'TOTAL (ÚLTIMOS 12 MESES)',
                'cod_conta': 'ContribuicaoDoServidorParaOPlanoDePrevidencia',
                'valor': contribuicao,
            },
            {
                'coluna': 'TOTAL (ÚLTIMOS 12 MESES)',
                'cod_conta': 'CompensacaoFinanceiraEntreRegimesPrevidencia',
                'valor': compensacao,
            },
        ])

    @staticmethod
    def _dca(contribuicao=100, compensacao=50):
        return pd.DataFrame([
            {'cod_conta': 'RO1.2.1.5.00.0.0', 'valor': contribuicao},
            {'cod_conta': 'RO1.9.9.9.03.0.0', 'valor': compensacao},
        ])

    def test_exige_que_todas_as_metricas_confiram(self):
        resultado, detalhe = d4_00017(
            self._rreo(contribuicao=100, compensacao=200),
            self._dca(contribuicao=100, compensacao=150),
        )

        self.assertEqual(_resposta(resultado), 'ERRO')
        self.assertEqual(detalhe['DIF'].tolist(), [0.0, 50.0])

    def test_aprova_todas_as_metricas_dentro_da_tolerancia(self):
        resultado, _ = d4_00017(
            self._rreo(contribuicao=100, compensacao=50),
            self._dca(contribuicao=100.005, compensacao=50),
        )

        self.assertEqual(_resposta(resultado), 'OK')

    def test_metrica_ausente_retorna_na(self):
        dca_sem_compensacao = self._dca().query("cod_conta != 'RO1.9.9.9.03.0.0'")

        resultado, detalhe = d4_00017(self._rreo(), dca_sem_compensacao)

        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertTrue(pd.isna(resultado.iloc[0]['Nota']))
        self.assertTrue(pd.isna(detalhe.iloc[1]['DCA']))

    def test_fonte_ausente_retorna_na(self):
        resultado, _ = d4_00017(None, self._dca())

        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertIn('RREO', resultado.iloc[0]['OBS'])


class D400027Tests(unittest.TestCase):
    @staticmethod
    def _dca(valor=100):
        return pd.DataFrame([
            {'cod_conta': 'P1.1.1.0.0.00.00', 'valor': valor},
        ])

    @staticmethod
    def _rgf(valor=90):
        return pd.DataFrame([
            {
                'cod_conta': 'DisponibilidadeDeCaixaBruta',
                'coluna': 'Até o 3º Quadrimestre',
                'valor': valor,
            },
        ])

    def test_compara_escalares_nomeados(self):
        resultado, detalhe = d4_00027(self._dca(100), self._rgf(90))

        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[0]['DCA'], 100)
        self.assertEqual(detalhe.iloc[0]['RGF'], 90)
        self.assertEqual(detalhe.iloc[0]['DIF'], -10)

    def test_rgf_maior_que_dca_retorna_erro(self):
        resultado, _ = d4_00027(self._dca(100), self._rgf(110))

        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_fonte_rgf_ausente_retorna_na(self):
        rgf_vazio = pd.DataFrame(columns=['cod_conta', 'coluna', 'valor'])

        resultado, detalhe = d4_00027(self._dca(100), rgf_vazio)

        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertTrue(pd.isna(resultado.iloc[0]['Nota']))
        self.assertTrue(pd.isna(detalhe.iloc[0]['RGF']))


class D400028Tests(unittest.TestCase):
    @staticmethod
    def _dca(valor=100):
        return pd.DataFrame([
            {'cod_conta': 'P1.1.1.0.0.00.00', 'valor': valor},
        ])

    @staticmethod
    def _rgf(valor_executivo=60, valor_outros=30):
        return pd.DataFrame([
            {
                'cod_conta': 'DisponibilidadeDeCaixaBrutaExecutivo',
                'conta': 'TOTAL (IV) = (I + II + III)',
                'valor': valor_executivo,
            },
            {
                'cod_conta': 'DisponibilidadeDeCaixaBrutaOutrosPoderes',
                'conta': 'TOTAL (III) = (I + II)',
                'valor': valor_outros,
            },
        ])

    def test_soma_componentes_rgf_em_um_escalar_nomeado(self):
        resultado, detalhe = d4_00028(self._dca(100), self._rgf(60, 30))

        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[0]['DCA'], 100)
        self.assertEqual(detalhe.iloc[0]['RGF'], 90)
        self.assertEqual(detalhe.iloc[0]['DIF'], -10)

    def test_rgf_maior_que_dca_retorna_erro(self):
        resultado, _ = d4_00028(self._dca(100), self._rgf(80, 30))

        self.assertEqual(_resposta(resultado), 'ERRO')

    def test_metrica_dca_ausente_retorna_na(self):
        dca_sem_conta_alvo = pd.DataFrame([
            {'cod_conta': 'P1.2.0.0.0.00.00', 'valor': 100},
        ])

        resultado, detalhe = d4_00028(dca_sem_conta_alvo, self._rgf())

        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertTrue(pd.isna(resultado.iloc[0]['Nota']))
        self.assertTrue(pd.isna(detalhe.iloc[0]['DCA']))


if __name__ == '__main__':
    unittest.main()
