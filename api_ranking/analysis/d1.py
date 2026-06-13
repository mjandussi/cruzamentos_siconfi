"""Compatibilidade para execução sem as análises D1.

As regras D1 foram removidas do app, mas D4 ainda usa o normalizador de fonte
e a página principal referencia funções D1 durante a consolidação. Este módulo
mantém esses pontos estáveis retornando verificações N/A para D1.
"""

from __future__ import annotations

import re

import pandas as pd


def _fonte_msc_codigo_e_tres_digitos(series: pd.Series):
    """Normaliza fonte de recursos da MSC e extrai os 3 últimos dígitos."""
    s = series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    digitos = s.str.replace(r"\D", "", regex=True)
    quatro = digitos.where(digitos.str.len() >= 4, digitos.str.zfill(4)).str[-4:]
    tres_txt = quatro.str[-3:]
    tres_num = pd.to_numeric(tres_txt, errors="coerce")
    return quatro, tres_num, tres_txt


def _na_result(codigo: str):
    df = pd.DataFrame([{
        "Dimensão": codigo,
        "Resposta": "N/A",
        "Descrição da Dimensão": "Dimensão D1 removida do aplicativo",
        "Nota": None,
        "OBS": "Análise D1 desativada",
    }])
    return df, pd.DataFrame()


def __getattr__(name: str):
    match = re.fullmatch(r"d1_(\d{5})", name)
    if not match:
        raise AttributeError(name)

    codigo = f"D1_{match.group(1)}"

    def _stub(*args, **kwargs):
        result, detail = _na_result(codigo)
        if name in {"d1_00021", "d1_00025"}:
            pc_estendido = args[-1] if args else pd.DataFrame()
            return result, detail, pc_estendido
        if name in {"d1_00038", "d1_00041", "d1_00042", "d1_00043"}:
            return result, detail, pd.DataFrame()
        return result, detail

    return _stub
