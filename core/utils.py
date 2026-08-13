# ┌───────────────────────────────────────────────────────────────
# │ core/utils.py - Funções Utilitárias Compartilhadas
# └───────────────────────────────────────────────────────────────

import numpy as np
import pandas as pd
from io import BytesIO
from typing import Dict, Optional


# ═══════════════════════════════════════════════════════════════
# Conversões e Formatações
# ═══════════════════════════════════════════════════════════════

def br_to_float(x: str) -> float:
    """
    Converte string no formato brasileiro (1.234,56) para float.

    Args:
        x: String representando um número no formato BR

    Returns:
        Float ou np.nan se conversão falhar
    """
    if x is None:
        return np.nan
    x = str(x).strip().replace('.', '').replace(',', '.')
    try:
        return float(x)
    except Exception:
        return np.nan


def formatar_reais(valor: float) -> str:
    """
    Formata um valor float para o formato brasileiro de moeda.

    Args:
        valor: Valor numérico

    Returns:
        String formatada como "R$ 1.234,56"
    """
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


# ═══════════════════════════════════════════════════════════════
# Conversões de DataFrame
# ═══════════════════════════════════════════════════════════════

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    Converte DataFrame para CSV em bytes (para download).

    Args:
        df: DataFrame do pandas

    Returns:
        Bytes do arquivo CSV
    """
    return df.to_csv(index=False).encode('utf-8')


def convert_df_to_csv_com_zfill(
    df: pd.DataFrame,
    zfill_map: Optional[Dict[str, int]] = None
) -> bytes:
    """
    Converte DataFrame para CSV com padding de zeros à esquerda em colunas específicas.

    Args:
        df: DataFrame a ser exportado.
        zfill_map: Dicionário opcional no formato {"coluna": largura}, usado para aplicar
                   padding com zeros à esquerda em colunas específicas.

    Returns:
        Bytes do arquivo CSV codificado em latin1 (para preservar acentos)
    """
    zfill_map = zfill_map or {}
    df_str = df.copy()

    for column in df_str.columns:
        series = df_str[column]
        series = series.fillna("")
        series = series.astype(str)
        if column in zfill_map:
            series = series.str.zfill(zfill_map[column])
        df_str[column] = series

    return df_str.to_csv(index=False, sep=';', encoding='latin1').encode('latin1')


def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """
    Converte DataFrame para Excel em bytes (para download).

    Args:
        df: DataFrame do pandas

    Returns:
        Bytes do arquivo Excel
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()


def prepare_msc_12_13_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara a MSC corrente/de encerramento para uma exportação estável.

    A API identifica tanto a MSCC de dezembro quanto a MSCE com mês 12.
    Para leitura humana, a matriz de encerramento é apresentada como mês 13.
    A cópia evita alterar o DataFrame utilizado pelas regras de análise.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=getattr(df, "columns", None))
    if "mes_referencia" not in df.columns:
        raise ValueError("A MSC não possui a coluna 'mes_referencia'.")

    colunas_tipo = [
        coluna
        for coluna in ("tipo_matriz", "co_tipo_matriz")
        if coluna in df.columns
    ]
    if not colunas_tipo:
        raise ValueError(
            "A MSC não possui as colunas 'tipo_matriz' ou 'co_tipo_matriz'."
        )

    out = df.copy()
    eh_mscc = pd.Series(False, index=out.index)
    eh_msce = pd.Series(False, index=out.index)
    for coluna in colunas_tipo:
        tipo = out[coluna].astype("string").str.strip().str.upper()
        eh_mscc |= tipo.eq("MSCC").fillna(False)
        eh_msce |= tipo.eq("MSCE").fillna(False)

    # O mês 13 é a representação semântica da matriz de encerramento.
    out.loc[eh_msce, "mes_referencia"] = 13
    mes = pd.to_numeric(out["mes_referencia"], errors="coerce")
    out = out.loc[(eh_mscc & mes.eq(12)) | (eh_msce & mes.eq(13))].copy()
    return out.reset_index(drop=True)


def convert_msc_12_13_to_excel(df: pd.DataFrame) -> bytes:
    """Converte somente MSCC/12 e MSCE/13 para um arquivo Excel."""
    msc = prepare_msc_12_13_for_excel(df)
    if msc.empty:
        raise ValueError("Não há dados da MSC dos meses 12 e 13 para exportar.")

    # O Excel comporta 1.048.576 linhas por aba; uma delas é o cabeçalho.
    if len(msc) > 1_048_575:
        raise ValueError(
            "A MSC dos meses 12 e 13 excede o limite de linhas de uma aba do Excel."
        )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        msc.to_excel(writer, index=False, sheet_name="MSC_Consolidada_12_13")
        worksheet = writer.sheets["MSC_Consolidada_12_13"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
    return output.getvalue()




# ═══════════════════════════════════════════════════════════════
# Helpers Específicos
# ═══════════════════════════════════════════════════════════════

def chunk_list(lst, n):
    """
    Divide uma lista em chunks de tamanho n.

    Args:
        lst: Lista a ser dividida
        n: Tamanho de cada chunk

    Yields:
        Sublistas de tamanho n
    """
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


def serie_6dig(s: pd.Series) -> pd.Series:
    """
    Extrai dígitos de uma série e formata com 6 dígitos (padding com zeros).

    Args:
        s: Série do pandas

    Returns:
        Série com valores formatados em 6 dígitos
    """
    return (
        s.astype(str)
         .str.extract(r'(\d+)', expand=False)
         .fillna('')
         .str.zfill(6)
    )
