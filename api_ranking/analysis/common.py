"""Normalizações pequenas compartilhadas pelas regras contábeis."""

from __future__ import annotations

import pandas as pd


def fonte_msc_codigo_e_tres_digitos(
    series: pd.Series,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Retorna a fonte da MSC em quatro dígitos e suas formas de três dígitos.

    A API pode entregar ``1500`` como ``1500.0``. O sufixo decimal precisa ser
    removido antes dos caracteres não numéricos; caso contrário, o código seria
    interpretado incorretamente como ``15000``.
    """
    text = series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    digits = text.str.replace(r"\D", "", regex=True)
    code_4 = digits.where(digits.str.len() >= 4, digits.str.zfill(4)).str[-4:]
    code_3_text = code_4.str[-3:]
    code_3_number = pd.to_numeric(code_3_text, errors="coerce")
    return code_4, code_3_number, code_3_text
