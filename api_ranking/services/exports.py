"""Transformações puras usadas nas exportações do resultado do ranking.

Este módulo não conhece Streamlit nem ``session_state``. Isso mantém a geração
dos arquivos testável e impede que detalhes de interface se misturem à regra de
serialização dos demonstrativos.
"""

from io import BytesIO
import re

import numpy as np
import pandas as pd


COLUNAS_COMPARACAO_RESULTADOS = [
    "Dimensão",
    "Resposta",
    "Descrição da Dimensão",
    "Nota",
    "OBS",
]

_EXCEL_SHEET_INVALID_RE = re.compile(r"[\\/*?:\[\]]")


def sanitizar_nome_aba_excel(raw: str) -> str:
    """Produz um nome aceito pelo Excel, limitado aos 31 caracteres permitidos."""
    nome = _EXCEL_SHEET_INVALID_RE.sub("_", str(raw or "")).strip()
    return nome[:31] or "Aba"


def preparar_msc_12_13_para_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Copia e limita a MSC a dezembro corrente e ao encerramento.

    A API identifica MSCC e MSCE com mês 12. Somente na cópia destinada ao
    Excel a MSCE recebe o mês semântico 13, sem alterar a entrada das regras.
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

    resultado = df.copy()
    eh_mscc = pd.Series(False, index=resultado.index)
    eh_msce = pd.Series(False, index=resultado.index)
    for coluna in colunas_tipo:
        tipo = resultado[coluna].astype("string").str.strip().str.upper()
        eh_mscc |= tipo.eq("MSCC").fillna(False)
        eh_msce |= tipo.eq("MSCE").fillna(False)

    resultado.loc[eh_msce, "mes_referencia"] = 13
    mes = pd.to_numeric(resultado["mes_referencia"], errors="coerce")
    resultado = resultado.loc[
        (eh_mscc & mes.eq(12)) | (eh_msce & mes.eq(13))
    ].copy()
    return resultado.reset_index(drop=True)


def gerar_excel_msc_12_13(df: pd.DataFrame) -> bytes:
    """Gera o Excel com somente MSCC/12 e MSCE/13."""
    msc = preparar_msc_12_13_para_excel(df)
    if msc.empty:
        raise ValueError("Não há dados da MSC dos meses 12 e 13 para exportar.")
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


def gerar_excel_demonstrativos(bundle: dict) -> bytes:
    """Gera o arquivo DCA/RREO/RGF a partir do bundle preparado pela página.

    A MSC não entra neste arquivo: os meses 12 e 13 são exportados em separado
    porque usam uma rotina de preparação própria e podem produzir um arquivo
    consideravelmente maior.
    """
    try:
        output = BytesIO()
        cod = bundle["cod"]
        ente = bundle["ente"]
        ano = bundle["ano"]
        tipo_ente = bundle["tipo_ente"]
        total_ok = bundle["total_ok"]
        total_faltando = bundle["total_faltando"]
        df_dca_ab = bundle["df_dca_ab"]
        df_dca_c_orig = bundle["df_dca_c_orig"]
        df_dca_d = bundle["df_dca_d"]
        df_dca_e = bundle["df_dca_e"]
        df_dca_f = bundle["df_dca_f"]
        df_dca_g = bundle["df_dca_g"]
        df_dca_hi = bundle["df_dca_hi"]
        rreo = bundle["rreo"]
        rgf = bundle["rgf"]

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            resumo = pd.DataFrame(
                [
                    {"Informação": "Ente", "Valor": cod},
                    {"Informação": "Nome", "Valor": ente},
                    {"Informação": "Ano", "Valor": ano},
                    {
                        "Informação": "Tipo",
                        "Valor": "Estado" if tipo_ente == "E" else "Município",
                    },
                    {
                        "Informação": "Data de Extração",
                        "Valor": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    },
                    {"Informação": "Demonstrativos Disponíveis", "Valor": total_ok},
                    {"Informação": "Demonstrativos Faltantes", "Valor": total_faltando},
                    {
                        "Informação": "Observação",
                        "Valor": (
                            "MSC consolidada dos meses 12 (dezembro) e 13 "
                            "(encerramento) exportada em arquivo Excel separado."
                        ),
                    },
                ]
            )
            resumo.to_excel(
                writer,
                sheet_name=sanitizar_nome_aba_excel("Resumo"),
                index=False,
            )

            abas_dca = (
                ("DCA_Anexo_I-AB", df_dca_ab),
                ("DCA_Anexo_I-C", df_dca_c_orig),
                ("DCA_Anexo_I-D", df_dca_d),
                ("DCA_Anexo_I-E", df_dca_e),
                ("DCA_Anexo_I-F", df_dca_f),
                ("DCA_Anexo_I-G", df_dca_g),
                ("DCA_Anexo_I-HI", df_dca_hi),
            )
            for nome_aba, dataframe in abas_dca:
                if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
                    dataframe.to_excel(
                        writer,
                        sheet_name=sanitizar_nome_aba_excel(nome_aba),
                        index=False,
                    )

            if isinstance(rreo, pd.DataFrame) and not rreo.empty:
                rreo.to_excel(
                    writer,
                    sheet_name=sanitizar_nome_aba_excel("RREO"),
                    index=False,
                )
            elif isinstance(rreo, dict):
                for key, dataframe in rreo.items():
                    if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
                        dataframe.to_excel(
                            writer,
                            sheet_name=sanitizar_nome_aba_excel(f"RREO_{key}"),
                            index=False,
                        )

            if isinstance(rgf, dict):
                for key, dataframe in rgf.items():
                    if isinstance(dataframe, pd.DataFrame) and not dataframe.empty:
                        dataframe.to_excel(
                            writer,
                            sheet_name=sanitizar_nome_aba_excel(f"RGF_{key}"),
                            index=False,
                        )

        output.seek(0)
        return output.getvalue()
    except Exception as exc:
        # A camada de interface apresenta esta mensagem; encapsular aqui evita
        # downloads silenciosos de arquivos vazios quando o openpyxl falha.
        raise RuntimeError(
            f"Falha ao montar Excel de demonstrativos: {type(exc).__name__}: {exc}"
        ) from exc


def gerar_excel_resultados(resultados: pd.DataFrame) -> bytes:
    """Serializa a tabela final no mesmo formato aceito pelo comparador."""
    output = BytesIO()
    resultados.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output.read()


def ler_planilha_resultados_comparacao(uploaded_file) -> pd.DataFrame:
    """Lê e normaliza uma exportação antes de comparar resposta e nota."""
    dataframe = pd.read_excel(uploaded_file)
    faltam = [
        coluna
        for coluna in COLUNAS_COMPARACAO_RESULTADOS
        if coluna not in dataframe.columns
    ]
    if faltam:
        raise ValueError(
            "Colunas em falta no Excel: "
            f"{faltam}. Esperado: {COLUNAS_COMPARACAO_RESULTADOS}"
        )

    resultado = dataframe[COLUNAS_COMPARACAO_RESULTADOS].copy()
    resultado["Dimensão"] = resultado["Dimensão"].astype(str).str.strip()
    resultado["Resposta"] = resultado["Resposta"].astype(str).str.strip()
    resultado["Nota"] = pd.to_numeric(resultado["Nota"], errors="coerce")
    return resultado.drop_duplicates(subset=["Dimensão"], keep="last")


def _rank_resposta_comparacao(resposta) -> int:
    resposta = str(resposta).strip().upper()
    if resposta == "OK":
        return 2
    if resposta == "N/A":
        return 1
    if resposta == "ERRO":
        return 0
    return 1


def comparar_resultados(antes: pd.DataFrame, depois: pd.DataFrame) -> dict:
    """Compara duas exportações e devolve apenas dados, sem decisões de UI.

    A observação é carregada para contexto, mas não define mudança: somente
    ``Resposta`` e ``Nota`` influenciam a tendência, como na metodologia atual.
    """
    merged = antes.merge(
        depois,
        on="Dimensão",
        how="outer",
        suffixes=("_antes", "_depois"),
        indicator=True,
    )
    ambos = merged[merged["_merge"] == "both"].drop(columns=["_merge"]).copy()
    so_antes = merged[merged["_merge"] == "left_only"]["Dimensão"].tolist()
    so_depois = merged[merged["_merge"] == "right_only"]["Dimensão"].tolist()

    nota_antes = pd.to_numeric(ambos["Nota_antes"], errors="coerce")
    nota_depois = pd.to_numeric(ambos["Nota_depois"], errors="coerce")
    indice = ambos.index
    valores_antes = np.asarray(nota_antes, dtype=np.float64)
    valores_depois = np.asarray(nota_depois, dtype=np.float64)

    # NumPy evita TypeError do pandas com booleanos nullable ou escalares.
    diferenca = np.abs(valores_antes - valores_depois) > 0.005
    nan_mudou = np.logical_xor(
        np.isnan(valores_antes),
        np.isnan(valores_depois),
    )
    nota_mudou = pd.Series(
        np.logical_or(diferenca, nan_mudou),
        index=indice,
        dtype=bool,
    )
    resposta_mudou = pd.Series(
        ambos["Resposta_antes"].astype(str).to_numpy()
        != ambos["Resposta_depois"].astype(str).to_numpy(),
        index=indice,
        dtype=bool,
    )

    mudou = np.logical_or(resposta_mudou.to_numpy(), nota_mudou.to_numpy())
    linhas_mudaram = ambos[mudou].copy()

    rank_antes = pd.to_numeric(
        ambos["Resposta_antes"].map(_rank_resposta_comparacao),
        errors="coerce",
    ).fillna(1)
    rank_depois = pd.to_numeric(
        ambos["Resposta_depois"].map(_rank_resposta_comparacao),
        errors="coerce",
    ).fillna(1)
    resposta_subiu = pd.Series(
        rank_depois.to_numpy(dtype=np.float64)
        > rank_antes.to_numpy(dtype=np.float64),
        index=indice,
        dtype=bool,
    )
    resposta_desceu = pd.Series(
        rank_depois.to_numpy(dtype=np.float64)
        < rank_antes.to_numpy(dtype=np.float64),
        index=indice,
        dtype=bool,
    )
    nota_subiu = pd.Series(
        (valores_depois - valores_antes) > 0.005,
        index=indice,
        dtype=bool,
    ).fillna(False)
    nota_desceu = pd.Series(
        (valores_antes - valores_depois) > 0.005,
        index=indice,
        dtype=bool,
    ).fillna(False)
    resposta_ou_nota_mudou = pd.Series(
        np.logical_or(
            resposta_mudou.to_numpy(dtype=bool),
            nota_mudou.to_numpy(dtype=bool),
        ),
        index=indice,
        dtype=bool,
    )
    melhorou = pd.Series(
        np.logical_and(
            resposta_ou_nota_mudou.to_numpy(dtype=bool),
            np.logical_or(
                resposta_subiu.to_numpy(dtype=bool),
                np.logical_and(
                    nota_subiu.to_numpy(dtype=bool),
                    np.logical_not(resposta_desceu.to_numpy(dtype=bool)),
                ),
            ),
        ),
        index=indice,
        dtype=bool,
    )
    piorou = pd.Series(
        np.logical_and(
            resposta_ou_nota_mudou.to_numpy(dtype=bool),
            np.logical_or(
                resposta_desceu.to_numpy(dtype=bool),
                np.logical_and(
                    nota_desceu.to_numpy(dtype=bool),
                    np.logical_not(resposta_subiu.to_numpy(dtype=bool)),
                ),
            ),
        ),
        index=indice,
        dtype=bool,
    )

    tabela_alteracoes = pd.DataFrame()
    if not linhas_mudaram.empty:
        linhas_mudaram["Δ Nota"] = (
            nota_depois - nota_antes
        ).reindex(linhas_mudaram.index)
        indice_mudancas = linhas_mudaram.index
        mudou_para_melhor = melhorou.reindex(indice_mudancas).fillna(False)
        mudou_para_pior = piorou.reindex(indice_mudancas).fillna(False)
        linhas_mudaram["Tendência"] = np.where(
            mudou_para_melhor,
            "Melhorou",
            np.where(mudou_para_pior, "Piorou", "Alterado"),
        )
        colunas = [
            "Dimensão",
            "Resposta_antes",
            "Resposta_depois",
            "Nota_antes",
            "Nota_depois",
            "Δ Nota",
            "Tendência",
            "Descrição da Dimensão_antes",
        ]
        colunas = [coluna for coluna in colunas if coluna in linhas_mudaram.columns]
        tabela_alteracoes = linhas_mudaram[colunas].copy()
        ordem = ["Melhorou", "Alterado", "Piorou"]
        tabela_alteracoes["_ord"] = pd.Categorical(
            tabela_alteracoes["Tendência"],
            categories=ordem,
            ordered=True,
        )
        tabela_alteracoes = tabela_alteracoes.sort_values(
            ["_ord", "Dimensão"]
        ).drop(columns=["_ord"])

    return {
        "dimensoes_so_antes": so_antes,
        "dimensoes_so_depois": so_depois,
        "quantidade_melhorou": int(melhorou.sum()),
        "quantidade_piorou": int(piorou.sum()),
        "tabela_alteracoes": tabela_alteracoes,
    }
