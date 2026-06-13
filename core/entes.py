"""
Seleção de ente respeitando o perfil de login
=============================================
Helper compartilhado pelas páginas que analisam UM ente (dashboards RREO/RGF,
MSC mensal via API). Aplica a regra de escopo:

- Perfis restritos (ex.: belem, subcont) têm o ente TRAVADO no ente autorizado.
- Admin (sem ente fixo) escolhe livremente: Tipo (Estado/Município) → UF → Ente.

A base reaproveita os arquivos do ranking, onde, para municípios, ID_ENTE é o
código IBGE de 7 dígitos (= id_ente do SICONFI); para estados, COD_IBGE é o
código de 2 dígitos (ex.: 33 = RJ).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.auth import restricted_ranking_fixed_ente

CAMINHO_BASE_ESTADOS = "api_ranking/base_ranking/estados_analitico_base.csv"
CAMINHO_BASE_MUNICIPIOS = "api_ranking/base_ranking/municipios_bspn_base.csv"


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def carregar_entes(tipo_ente: str) -> pd.DataFrame:
    """Retorna 1 linha por ente, com colunas padronizadas: cod (str), nome (str), uf (str)."""
    if tipo_ente == "E":
        df = pd.read_csv(
            CAMINHO_BASE_ESTADOS, encoding="utf-8", sep=";",
            usecols=["COD_IBGE", "NO_ESTADO", "SG_ESTADO"],
            on_bad_lines="skip", low_memory=False,
        ).rename(columns={"COD_IBGE": "cod", "NO_ESTADO": "nome", "SG_ESTADO": "uf"})
    else:
        df = pd.read_csv(
            CAMINHO_BASE_MUNICIPIOS, encoding="utf-8", sep=";",
            usecols=["ID_ENTE", "NOME_ENTE", "UF"],
            on_bad_lines="skip", low_memory=False,
        ).rename(columns={"ID_ENTE": "cod", "NOME_ENTE": "nome", "UF": "uf"})

    df = df.dropna(subset=["cod"]).copy()
    df["cod"] = df["cod"].astype(int).astype(str)
    df["nome"] = df["nome"].astype(str).str.strip()
    df["uf"] = df["uf"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["cod"])
    return df.sort_values(["uf", "nome"]).reset_index(drop=True)


def render_ente_selector(*, key_prefix: str = "ente", uf_padrao: str = "RJ") -> dict:
    """
    Renderiza a seleção de ente conforme o perfil de login e retorna
    {"id_ente": str, "nome": str, "tipo_ente": "E"|"M"}.
    """
    fixed = restricted_ranking_fixed_ente()

    # ---- Perfil restrito: ente travado ----
    if fixed:
        tipo_ente, cod_fixo = fixed
        df = carregar_entes(tipo_ente)
        row = df[df["cod"] == str(cod_fixo)]
        nome = row.iloc[0]["nome"] if not row.empty else str(cod_fixo)
        st.text_input(
            "Estado" if tipo_ente == "E" else "Município",
            value=f"{nome} ({cod_fixo})",
            disabled=True,
            help="Seu perfil de acesso é restrito a este ente.",
            key=f"{key_prefix}_fixed",
        )
        return {"id_ente": str(cod_fixo), "nome": nome, "tipo_ente": tipo_ente}

    # ---- Admin: seleção livre ----
    c_tipo, c_uf, c_ente = st.columns([1, 1, 2])

    with c_tipo:
        tipo_ente = st.selectbox(
            "Tipo de Ente",
            options=["E", "M"],
            format_func=lambda x: "Estado" if x == "E" else "Município",
            index=0,
            key=f"{key_prefix}_tipo",
        )

    df = carregar_entes(tipo_ente)

    if tipo_ente == "M":
        with c_uf:
            ufs = sorted(df["uf"].unique().tolist())
            uf_idx = ufs.index(uf_padrao) if uf_padrao in ufs else 0
            uf_sel = st.selectbox("Estado (UF)", options=ufs, index=uf_idx, key=f"{key_prefix}_uf")
        df = df[df["uf"] == uf_sel].reset_index(drop=True)

    df = df.copy()
    df["display"] = df["nome"] + " (" + df["cod"] + ")"

    # padrão: Rio de Janeiro quando for estado
    default_index = 0
    if tipo_ente == "E":
        rj = df.index[df["nome"].str.contains("Rio de Janeiro", case=False, na=False)].tolist()
        if rj:
            default_index = int(df.index.get_loc(rj[0]))

    with c_ente:
        escolha = st.selectbox(
            "Estado" if tipo_ente == "E" else "Município",
            options=df["display"].tolist(),
            index=default_index if len(df) else 0,
            key=f"{key_prefix}_ente",
        )

    row = df[df["display"] == escolha].iloc[0]
    return {"id_ente": str(row["cod"]), "nome": str(row["nome"]), "tipo_ente": tipo_ente}
