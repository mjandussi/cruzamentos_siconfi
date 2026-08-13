import unittest

import pandas as pd

from api_ranking.analysis.d2_dca import (
    d2_00100,
    d2_00101,
    d2_00102,
    d2_00103,
    d2_00104,
)


COLUNAS_RP = [
    'Restos a Pagar Não Processados Liquidados',
    'Restos a Pagar Não Processados Pagos',
    'Restos a Pagar Não Processados Cancelados',
    'Restos a Pagar Processados Pagos',
    'Restos a Pagar Processados Cancelados',
]


def _linhas_msc(funcao, digito_intra, fator=1):
    valores = {
        '631300000': 60 * fator,
        '631400000': 40 * fator,
        '631900000': 5 * fator,
        '632200000': 30 * fator,
        '632900000': 3 * fator,
    }
    return [
        {
            'conta_contabil': conta,
            'funcao': funcao,
            'DIGITO_INTRA': digito_intra,
            'valor': valor,
        }
        for conta, valor in valores.items()
    ]


def _linhas_dca(conta, fator=1):
    # RPNP liquidado corresponde a 6313* + 6314* na regra da MSC.
    valores = [100 * fator, 40 * fator, 5 * fator, 30 * fator, 3 * fator]
    return [
        {
            'cod_conta': 'TotalDespesas',
            'conta': conta,
            'coluna': coluna,
            'valor': valor,
        }
        for coluna, valor in zip(COLUNAS_RP, valores)
    ]


def _resposta(resultado):
    return resultado.iloc[0]['Resposta']


class D22025CrosschecksTests(unittest.TestCase):
    def test_codigos_00100_a_00102_usam_as_funcoes_corretas(self):
        msc = pd.DataFrame(
            _linhas_msc('10', '30', fator=1)
            + _linhas_msc('12', '30', fator=2)
            + _linhas_msc('09', '30', fator=3)
        )
        dca = pd.DataFrame(
            _linhas_dca('10 - Saúde', fator=1)
            + _linhas_dca('12 - Educação', fator=2)
            + _linhas_dca('09 - Previdência Social', fator=3)
        )

        for codigo, funcao in [
            ('D2_00100', d2_00100),
            ('D2_00101', d2_00101),
            ('D2_00102', d2_00102),
        ]:
            with self.subTest(codigo=codigo):
                resultado, detalhe = funcao(msc, dca)
                self.assertEqual(resultado.iloc[0]['Dimensão'], codigo)
                self.assertEqual(_resposta(resultado), 'OK')
                self.assertEqual(len(detalhe), 5)
                self.assertTrue((detalhe['dif'] == 0).all())

    def test_00103_soma_so_demais_funcoes_exceto_intra(self):
        msc = pd.DataFrame(
            _linhas_msc('04', '30', fator=1)
            + _linhas_msc('08', '30', fator=2)
            + _linhas_msc('10', '30', fator=9)
            + _linhas_msc('04', '91', fator=9)
        )
        dca = pd.DataFrame(
            _linhas_dca('04 - Administração', fator=1)
            + _linhas_dca('08 - Assistência Social', fator=2)
            + _linhas_dca('10 - Saúde', fator=9)
            + _linhas_dca('Despesas Exceto Intraorçamentárias', fator=50)
            + _linhas_dca('Despesas Intraorçamentárias', fator=9)
        )

        resultado, detalhe = d2_00103(msc, dca)

        self.assertEqual(resultado.iloc[0]['Dimensão'], 'D2_00103')
        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[0]['valor_dca'], 300)
        self.assertEqual(detalhe.iloc[0]['valor_msc'], 300)

    def test_00104_compara_apenas_intraorcamentario(self):
        msc = pd.DataFrame(
            _linhas_msc('04', '91', fator=4)
            + _linhas_msc('04', '30', fator=8)
        )
        dca = pd.DataFrame(
            _linhas_dca('Despesas Intraorçamentárias', fator=4)
            + _linhas_dca('04 - Administração', fator=8)
        )

        resultado, detalhe = d2_00104(msc, dca)

        self.assertEqual(resultado.iloc[0]['Dimensão'], 'D2_00104')
        self.assertEqual(_resposta(resultado), 'OK')
        self.assertEqual(detalhe.iloc[0]['valor_dca'], 400)
        self.assertEqual(detalhe.iloc[0]['valor_msc'], 400)

    def test_divergencia_em_um_item_retorna_erro(self):
        msc = pd.DataFrame(_linhas_msc('10', '30'))
        dca = pd.DataFrame(_linhas_dca('10 - Saúde'))
        dca.loc[dca['coluna'] == COLUNAS_RP[-1], 'valor'] = 4

        resultado, detalhe = d2_00100(msc, dca)

        self.assertEqual(_resposta(resultado), 'ERRO')
        linha = detalhe.loc[detalhe['item_rp'] == COLUNAS_RP[-1]].iloc[0]
        self.assertEqual(linha['dif'], 1)

    def test_fonte_ausente_retorna_na_em_vez_de_ok(self):
        dca = pd.DataFrame(_linhas_dca('10 - Saúde'))

        resultado, detalhe = d2_00100(pd.DataFrame(), dca)

        self.assertEqual(_resposta(resultado), 'N/A')
        self.assertIsNone(resultado.iloc[0]['Nota'])
        self.assertIn('MSC de encerramento ausente', resultado.iloc[0]['OBS'])
        self.assertTrue(detalhe.empty)


if __name__ == '__main__':
    unittest.main()
