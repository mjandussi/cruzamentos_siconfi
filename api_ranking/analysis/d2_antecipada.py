"""Compatibilidade para execução sem a análise D2 antecipada."""

from __future__ import annotations

import pandas as pd


def run_d2_antecipada(*args, **kwargs):
    df = pd.DataFrame([{
        "Dimensão": "D2_ANT_NA",
        "Resposta": "N/A",
        "Descrição da Dimensão": "D2 antecipada removida do aplicativo",
        "Nota": None,
        "OBS": "Análise desativada",
    }])
    return df, df.copy(), pd.DataFrame(), "N/A", None, False
