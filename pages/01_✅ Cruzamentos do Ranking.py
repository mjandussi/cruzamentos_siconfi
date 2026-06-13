# ┌───────────────────────────────────────────────────────────────
# │ pages/01_✅ Cruzamentos do Ranking.py
# └───────────────────────────────────────────────────────────────
#
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  POLÍTICA DE CACHE (Streamlit) — leia antes de alterar produção vs local   ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  • DESENVOLVIMENTO LOCAL: ao mudar ente/ano NÃO limpamos st.cache_data      ║
# ║    automaticamente (ver bloco ~“CONTROLE DE MUDANÇA DE ENTE/ANO”).         ║
# ║    Assim podes alternar vários entes/anos sem refazer download completo.   ║
# ║                                                                             ║
# ║  • PRODUÇÃO (VPS com pouca RAM, vários entes pesados): descomenta no       ║
# ║    mesmo bloco as linhas st.cache_data.clear() e gc.collect() para evitar  ║
# ║    acumular dois carregamentos enormes no mesmo processo (custo: próximo   ║
# ║    “Processar” volta à API). O botão “Limpar Cache” continua disponível.  ║
# ║                                                                             ║
# ║  • api_ranking/services/api_loader.py — funções get_extratos /             ║
# ║    load_all_data_cached: comentário no topo da secção sobre max_entries   ║
# ║    (LRU) opcional em VPS.                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

import gc
import re

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from pathlib import Path
from core.utils import convert_df_to_excel, convert_df_to_csv
from core.layout import setup_page, page_brand
from core.auth import is_authed, restricted_ranking_fixed_ente

import api_ranking.analysis.d1 as d1_analysis
import api_ranking.analysis.d2_antecipada as d2_ant_analysis
import api_ranking.analysis.d2_dca as d2_dca_analysis
import api_ranking.analysis.d3 as d3_analysis
import api_ranking.analysis.d4 as d4_analysis

from api_ranking.services.api_loader import get_extratos, load_all_data_cached, load_base_ranking

from api_ranking.services.check_types import (detectar_tipo_relatorio, 
            verificar_disponibilidade_demonstrativos, verificacao_disponivel,)

from api_ranking.services.formatting import eh_verificacao_capag, highlight_resposta

from api_ranking.renders.render_d1 import render_tab_d1
from api_ranking.renders.render_d2_antecipada import render_d2_antecipada
from api_ranking.renders.render_d2 import render_tab_d2
from api_ranking.renders.render_d3 import render_tab_d3
from api_ranking.renders.render_d4 import render_tab_d4


def render_main_nav(active: str = "Cruzamentos") -> None:
    items = [
        ("Home", "🏠", "pages/00_🏠 Home.py"),
        ("Cruzamentos", "✅", "pages/01_✅ Cruzamentos do Ranking.py"),
    ]
    cols = st.columns(len(items))
    for idx, (label, icon, path) in enumerate(items):
        with cols[idx]:
            if st.button(
                f"{icon} {label}",
                key=f"main_nav_v2_{idx}_{label}",
                type="primary" if label == active else "secondary",
                use_container_width=True,
            ) and label != active:
                st.switch_page(path)
    st.markdown("<div class='top-nav-spacer'></div>", unsafe_allow_html=True)



# ----------------- Setup / Auth / Navbar -----------------

setup_page(
    page_title="CRUZAMENTOS SICONFI - Cruzamentos",
    logo_path="assets/logo-mark.svg",
    show_top_nav=False,
)
if not is_authed():
    st.switch_page("app.py")

# ----------------- Página Brand -----------------
page_brand(
    title="CRUZAMENTOS SICONFI",
    logo_path="assets/logo-mark.svg",
    show_logout=True, 
)

render_main_nav(active="Cruzamentos")

# ----------------- Título com cor de fundo -----------------
st.markdown(
    """
    <h1>
      <span style="background:none;-webkit-text-fill-color:initial;">✅</span>
      Cruzamentos
    </h1>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")


####  Variáveis  ####
# Configurações padrão (podem ser sobrescritas pela interface)
CAMINHO_BASE_ESTADOS = "api_ranking/base_ranking/estados_analitico_base.csv"
CAMINHO_BASE_MUNICIPIOS = "api_ranking/base_ranking/municipios_bspn_base.csv"

UF_IBGE_PREFIXOS = {
    "11": "Rondônia",
    "12": "Acre",
    "13": "Amazonas",
    "14": "Roraima",
    "15": "Pará",
    "16": "Amapá",
    "17": "Tocantins",
    "21": "Maranhão",
    "22": "Piauí",
    "23": "Ceará",
    "24": "Rio Grande do Norte",
    "25": "Paraíba",
    "26": "Pernambuco",
    "27": "Alagoas",
    "28": "Sergipe",
    "29": "Bahia",
    "31": "Minas Gerais",
    "32": "Espírito Santo",
    "33": "Rio de Janeiro",
    "35": "São Paulo",
    "41": "Paraná",
    "42": "Santa Catarina",
    "43": "Rio Grande do Sul",
    "50": "Mato Grosso do Sul",
    "51": "Mato Grosso",
    "52": "Goiás",
    "53": "Distrito Federal",
}
UF_PADRAO_MUNICIPIO = "33"

VERIFICACOES_CRUZAMENTOS = frozenset({
    "D2_00044", "D2_00046", "D2_00048", "D2_00049", "D2_00050", "D2_00058",
    "D2_00069", "D2_00070", "D2_00071", "D2_00072", "D2_00073", "D2_00074",
    "D3_00001", "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009",
    "D3_00010", "D3_00014", "D3_00015", "D3_00016", "D3_00022", "D3_00023",
    "D3_00024", "D3_00025",
    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005", "D4_00006",
    "D4_00007", "D4_00010", "D4_00012", "D4_00017", "D4_00019", "D4_00020",
    "D4_00022", "D4_00024", "D4_00025", "D4_00026", "D4_00027", "D4_00028",
    "D4_00029", "D4_00030", "D4_00031", "D4_00032", "D4_00033", "D4_00034",
    "D4_00038", "D4_00040",
})


def filtrar_verificacoes_cruzamentos(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or "Dimensão" not in df.columns:
        return df
    return df[df["Dimensão"].astype(str).isin(VERIFICACOES_CRUZAMENTOS)].copy()

# ----------------- Configuração central de comportamento -----------------
# Consulta pública: desligar esta flag quando a base oficial 2025 estiver homologada.
FLAG_MODO_CONSULTA_PUBLICA = True
ANO_INICIO_CONSULTA_PUBLICA = 2025



#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################

# --- Exportações: fragmentos para não reexecutar o pipeline ao interagir com widgets ---

_COLS_COMPARAR_RESULTADO = ["Dimensão", "Resposta", "Descrição da Dimensão", "Nota", "OBS"]


def _limpar_bundles_exportacao_session():
    for _k in (
        "_bundle_demonstrativos",
        "_final_df_export",
        "_export_meta",
    ):
        st.session_state.pop(_k, None)
    # Bytes cacheados de Excel/CSV (chaveados por cod_ano) — usados pelo fragment
    # de exportação para evitar regenerar a cada re-render.
    for _prefix in (
        "_xlsx_demo_bytes::",
        "_xlsx_demo_err::",
        "_csv_demo_bytes::",
        "_csv_demo_err::",
    ):
        for _kk in [k for k in st.session_state.keys() if str(k).startswith(_prefix)]:
            st.session_state.pop(_kk, None)


_EXCEL_SHEET_INVALID_RE = re.compile(r"[\\/\\?\\*\\[\\]:]")


def _sanitiza_nome_aba_excel(raw: str) -> str:
    """Excel proíbe ``: \\ / ? * [ ]`` em nomes de aba e limita a 31 caracteres."""
    nome = _EXCEL_SHEET_INVALID_RE.sub("_", str(raw or "")).strip()
    nome = nome[:31] or "Aba"
    return nome


def _bytes_excel_demonstrativos_de_bundle(b: dict) -> bytes:
    """Gera o Excel DCA/RREO/RGF a partir do bundle guardado em session_state.

    Levanta ``RuntimeError`` com mensagem amigável em qualquer falha — quem
    chama deve capturar e reportar via ``st.error`` para evitar o sintoma
    'botão inerte' (geração silenciosa de bytes vazios).
    """
    try:
        output = BytesIO()
        cod = b["cod"]
        ente = b["ente"]
        ano = b["ano"]
        tipo_ente = b["tipo_ente"]
        total_ok = b["total_ok"]
        total_faltando = b["total_faltando"]
        df_dca_ab = b["df_dca_ab"]
        df_dca_c_orig = b["df_dca_c_orig"]
        df_dca_d = b["df_dca_d"]
        df_dca_e = b["df_dca_e"]
        df_dca_f = b["df_dca_f"]
        df_dca_g = b["df_dca_g"]
        df_dca_hi = b["df_dca_hi"]
        rreo = b["rreo"]
        rgf = b["rgf"]
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            resumo = pd.DataFrame(
                [
                    {"Informação": "Ente", "Valor": cod},
                    {"Informação": "Nome", "Valor": ente},
                    {"Informação": "Ano", "Valor": ano},
                    {"Informação": "Tipo", "Valor": "Estado" if tipo_ente == "E" else "Município"},
                    {"Informação": "Data de Extração", "Valor": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")},
                    {"Informação": "Demonstrativos Disponíveis", "Valor": total_ok},
                    {"Informação": "Demonstrativos Faltantes", "Valor": total_faltando},
                    {"Informação": "Observação", "Valor": "MSC exportada em arquivo CSV separado (devido ao tamanho)"},
                ]
            )
            resumo.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("Resumo"), index=False)
            if isinstance(df_dca_ab, pd.DataFrame) and not df_dca_ab.empty:
                df_dca_ab.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-AB"), index=False)
            if isinstance(df_dca_c_orig, pd.DataFrame) and not df_dca_c_orig.empty:
                df_dca_c_orig.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-C"), index=False)
            if isinstance(df_dca_d, pd.DataFrame) and not df_dca_d.empty:
                df_dca_d.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-D"), index=False)
            if isinstance(df_dca_e, pd.DataFrame) and not df_dca_e.empty:
                df_dca_e.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-E"), index=False)
            if isinstance(df_dca_f, pd.DataFrame) and not df_dca_f.empty:
                df_dca_f.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-F"), index=False)
            if isinstance(df_dca_g, pd.DataFrame) and not df_dca_g.empty:
                df_dca_g.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-G"), index=False)
            if isinstance(df_dca_hi, pd.DataFrame) and not df_dca_hi.empty:
                df_dca_hi.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("DCA_Anexo_I-HI"), index=False)
            if isinstance(rreo, pd.DataFrame) and not rreo.empty:
                rreo.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel("RREO"), index=False)
            elif isinstance(rreo, dict):
                for key, df in rreo.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        df.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel(f"RREO_{key}"), index=False)
            if isinstance(rgf, dict):
                for key, df in rgf.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        df.to_excel(writer, sheet_name=_sanitiza_nome_aba_excel(f"RGF_{key}"), index=False)
        output.seek(0)
        return output.getvalue()
    except Exception as _exc:
        raise RuntimeError(
            f"Falha ao montar Excel de demonstrativos: {type(_exc).__name__}: {_exc}"
        ) from _exc


def _ler_planilha_resultado_cmp(uploaded_file):
    df = pd.read_excel(uploaded_file)
    faltam = [c for c in _COLS_COMPARAR_RESULTADO if c not in df.columns]
    if faltam:
        raise ValueError(f"Colunas em falta no Excel: {faltam}. Esperado: {_COLS_COMPARAR_RESULTADO}")
    out = df[_COLS_COMPARAR_RESULTADO].copy()
    out["Dimensão"] = out["Dimensão"].astype(str).str.strip()
    out["Resposta"] = out["Resposta"].astype(str).str.strip()
    out["Nota"] = pd.to_numeric(out["Nota"], errors="coerce")
    out = out.drop_duplicates(subset=["Dimensão"], keep="last")
    return out


def _rank_resposta_cmp(s):
    s = str(s).strip().upper()
    if s == "OK":
        return 2
    if s == "N/A":
        return 1
    if s == "ERRO":
        return 0
    return 1


def _chave_ordenacao_dimensao(codigo_dimensao):
    """Retorna chave estável para ordenar códigos D1_00001 ... D4_99999."""
    codigo = str(codigo_dimensao or "").strip().upper()
    m = re.match(r"^D([1-4])_(\d+)$", codigo)
    if m:
        return (0, int(m.group(1)), int(m.group(2)), codigo)
    # Fallback: códigos não padronizados (ex.: D2_NA) ficam ao final.
    return (1, 99, 999999, codigo)


def _formata_tamanho_bytes(n: int) -> str:
    """Formata tamanho em B/KB/MB para diagnóstico."""
    n = int(n or 0)
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _diagnostico_ambiente_exportacao() -> None:
    """Mostra Python + versões dos pacotes críticos para exportação.

    Útil para comparar máquinas (casa × trabalho) quando a exportação
    apresentar comportamento inconsistente.
    """
    import sys
    import platform
    try:
        import openpyxl  # noqa: WPS433
        v_openpyxl = openpyxl.__version__
    except Exception as _e:
        v_openpyxl = f"(indisponível: {_e})"
    try:
        import pyarrow  # noqa: WPS433
        v_pyarrow = pyarrow.__version__
    except Exception as _e:
        v_pyarrow = f"(indisponível: {_e})"
    info = (
        f"Python: `{sys.version.split()[0]}` ({platform.python_implementation()}) | "
        f"pandas: `{pd.__version__}` | openpyxl: `{v_openpyxl}` | "
        f"pyarrow: `{v_pyarrow}` | streamlit: `{st.__version__}`"
    )
    st.caption("🔧 **Diagnóstico do ambiente:** " + info)


@st.fragment
def fragmento_exportar_demonstrativos():
    st.markdown("---")
    st.subheader("📥 Exportar Demonstrativos para Excel")
    b = st.session_state.get("_bundle_demonstrativos")
    if not b:
        st.warning("⚠️ Sem dados de demonstrativos em memória. Execute **Processar Análise**.")
        return
    st.info("💡 **Excel:** DCA, RREO e RGF | **CSV:** MSC Consolidada (arquivo grande, não cabe no Excel)")

    _key_export = f"{b.get('cod','')}_{b.get('ano','')}"
    _ck_xlsx = f"_xlsx_demo_bytes::{_key_export}"
    _ck_xlsx_err = f"_xlsx_demo_err::{_key_export}"
    _ck_csv = f"_csv_demo_bytes::{_key_export}"
    _ck_csv_err = f"_csv_demo_err::{_key_export}"

    col1, col2 = st.columns(2)
    with col1:
        if _ck_xlsx not in st.session_state and _ck_xlsx_err not in st.session_state:
            with st.spinner("Gerando Excel (DCA/RREO/RGF)..."):
                try:
                    st.session_state[_ck_xlsx] = _bytes_excel_demonstrativos_de_bundle(b)
                except Exception as _exc:
                    st.session_state[_ck_xlsx_err] = (
                        f"{type(_exc).__name__}: {_exc}"
                    )
        if st.session_state.get(_ck_xlsx_err):
            st.error(
                "❌ Erro ao gerar Excel (DCA/RREO/RGF): "
                f"{st.session_state[_ck_xlsx_err]}"
            )
            if st.button("🔁 Tentar gerar novamente", key=f"retry_xlsx_{_key_export}"):
                st.session_state.pop(_ck_xlsx_err, None)
                st.session_state.pop(_ck_xlsx, None)
                st.rerun(scope="fragment")
        else:
            _xlsx_bytes = st.session_state.get(_ck_xlsx) or b""
            _xlsx_n = len(_xlsx_bytes)
            if _xlsx_n == 0:
                st.warning(
                    "⚠️ O Excel foi gerado, mas ficou **vazio** (0 bytes). "
                    "O navegador não dispara o download neste caso. Use o botão abaixo para regerar."
                )
            st.download_button(
                label="📥 Baixar Excel (DCA/RREO/RGF)",
                data=_xlsx_bytes,
                file_name=f"demonstrativos_{b['cod']}_{b['ano']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key=f"dl_xlsx_demo_{_key_export}",
                disabled=(_xlsx_n == 0),
            )
            st.caption(f"📦 Tamanho do Excel: **{_formata_tamanho_bytes(_xlsx_n)}**")
            if st.button(
                "🔄 Regerar Excel",
                key=f"regen_xlsx_{_key_export}",
                help="Útil se o navegador não disparar o download.",
            ):
                st.session_state.pop(_ck_xlsx, None)
                st.session_state.pop(_ck_xlsx_err, None)
                st.rerun(scope="fragment")
    with col2:
        msc = b.get("msc_consolidada")
        if msc is None or (isinstance(msc, pd.DataFrame) and msc.empty):
            st.caption("MSC consolidada indisponível para exportação CSV.")
        else:
            if _ck_csv not in st.session_state and _ck_csv_err not in st.session_state:
                with st.spinner("Gerando CSV (MSC Consolidada)..."):
                    try:
                        out = BytesIO()
                        msc.to_csv(out, index=False, encoding="utf-8-sig")
                        st.session_state[_ck_csv] = out.getvalue()
                    except Exception as _exc:
                        st.session_state[_ck_csv_err] = (
                            f"{type(_exc).__name__}: {_exc}"
                        )
            if st.session_state.get(_ck_csv_err):
                st.error(
                    "❌ Erro ao gerar CSV (MSC Consolidada): "
                    f"{st.session_state[_ck_csv_err]}"
                )
                if st.button("🔁 Tentar gerar novamente", key=f"retry_csv_{_key_export}"):
                    st.session_state.pop(_ck_csv_err, None)
                    st.session_state.pop(_ck_csv, None)
                    st.rerun(scope="fragment")
            else:
                _csv_bytes = st.session_state.get(_ck_csv) or b""
                _csv_n = len(_csv_bytes)
                if _csv_n == 0:
                    st.warning(
                        "⚠️ O CSV foi gerado, mas ficou **vazio** (0 bytes). "
                        "O navegador não dispara o download neste caso. Use o botão abaixo para regerar."
                    )
                st.download_button(
                    label="📥 Baixar CSV (MSC Consolidada)",
                    data=_csv_bytes,
                    file_name=f"msc_consolidada_{b['cod']}_{b['ano']}.csv",
                    mime="text/csv",
                    width="stretch",
                    key=f"dl_csv_msc_{_key_export}",
                    disabled=(_csv_n == 0),
                )
                st.caption(f"📦 Tamanho do CSV: **{_formata_tamanho_bytes(_csv_n)}**")
                if st.button(
                    "🔄 Regerar CSV",
                    key=f"regen_csv_{_key_export}",
                    help="Útil se o navegador não disparar o download.",
                ):
                    st.session_state.pop(_ck_csv, None)
                    st.session_state.pop(_ck_csv_err, None)
                    st.rerun(scope="fragment")

    _diagnostico_ambiente_exportacao()


@st.fragment
def fragmento_resultados_excel_e_comparar():
    fin = st.session_state.get("_final_df_export")
    meta = st.session_state.get("_export_meta") or {}
    if fin is None or getattr(fin, "empty", True):
        return
    cod = meta.get("cod", "")
    ente = meta.get("ente", "")
    ano = meta.get("ano", "")
    _ts_export = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    _slug_ente = re.sub(r"[^\w\-.]+", "_", str(ente), flags=re.UNICODE).strip("._")[:50] or "ente"
    _nome_arquivo = f"resultado_analises_{cod}_{_slug_ente}_ex{ano}_{_ts_export}.xlsx"
    try:
        output = BytesIO()
        fin.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        excel_bytes = output.read()
    except Exception as _exc_excel:
        st.error(f"Erro ao gerar Excel: {_exc_excel}")
        excel_bytes = b""
    if excel_bytes:
        st.download_button(
            label="📥 Exportar resultados (Excel)",
            data=excel_bytes,
            file_name=_nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
            key=f"download_resultados_excel_{cod}_{ano}",
        )
    else:
        st.warning("Não foi possível gerar o arquivo Excel para exportação.")
    with st.expander("📊 Comparar duas exportações de resultados (Excel antes × depois)", expanded=False):
        st.caption(
            "Carregue dois ficheiros `.xlsx` obtidos com **Exportar resultados (Excel)** — por exemplo "
            "a análise da semana passada e a de hoje, após corrigir dados no SICONFI — para ver alterações "
            "em **Resposta** e **Nota** por dimensão (o texto de **OBS** não entra na deteção de mudanças)."
        )
        u1, u2 = st.columns(2)
        with u1:
            f_antes = st.file_uploader("Ficheiro **antes** (referência)", type=["xlsx"], key="cmp_resultados_antes")
        with u2:
            f_depois = st.file_uploader("Ficheiro **depois** (mais recente)", type=["xlsx"], key="cmp_resultados_depois")
        if f_antes is not None and f_depois is not None:
            try:
                dfa = _ler_planilha_resultado_cmp(f_antes)
                dfb = _ler_planilha_resultado_cmp(f_depois)
            except Exception as e:
                st.error(f"Não foi possível comparar os ficheiros: {e}")
            else:
                merged = dfa.merge(
                    dfb,
                    on="Dimensão",
                    how="outer",
                    suffixes=("_antes", "_depois"),
                    indicator=True,
                )
                ambos = merged[merged["_merge"] == "both"].drop(columns=["_merge"]).copy()
                so_antes = merged[merged["_merge"] == "left_only"]["Dimensão"].tolist()
                so_depois = merged[merged["_merge"] == "right_only"]["Dimensão"].tolist()
                na_a = pd.to_numeric(ambos["Nota_antes"], errors="coerce")
                na_b = pd.to_numeric(ambos["Nota_depois"], errors="coerce")
                _idx = ambos.index
                _a = np.asarray(na_a, dtype=np.float64)
                _b = np.asarray(na_b, dtype=np.float64)
                # numpy evita TypeError do pandas (| / ^ com boolean nullable ou escalares)
                _diff = np.abs(_a - _b) > 0.005
                _nan_mudou = np.logical_xor(np.isnan(_a), np.isnan(_b))
                nota_mudou = pd.Series(np.logical_or(_diff, _nan_mudou), index=_idx, dtype=bool)
                resp_mudou = pd.Series(
                    ambos["Resposta_antes"].astype(str).to_numpy()
                    != ambos["Resposta_depois"].astype(str).to_numpy(),
                    index=_idx,
                    dtype=bool,
                )
                # Só Resposta e Nota: mudanças só em OBS não aparecem (não impactam pontuação)
                _muda = np.logical_or(resp_mudou.to_numpy(), nota_mudou.to_numpy())
                linhas_mud = ambos[_muda].copy()
                ra = pd.to_numeric(ambos["Resposta_antes"].map(_rank_resposta_cmp), errors="coerce").fillna(1)
                rb = pd.to_numeric(ambos["Resposta_depois"].map(_rank_resposta_cmp), errors="coerce").fillna(1)
                sobe_resposta = pd.Series(rb.to_numpy(dtype=np.float64) > ra.to_numpy(dtype=np.float64), index=_idx, dtype=bool)
                desce_resposta = pd.Series(rb.to_numpy(dtype=np.float64) < ra.to_numpy(dtype=np.float64), index=_idx, dtype=bool)
                sobe_nota = pd.Series((_b - _a) > 0.005, index=_idx, dtype=bool).fillna(False)
                desce_nota = pd.Series((_a - _b) > 0.005, index=_idx, dtype=bool).fillna(False)
                mud_resp_ou_nota = pd.Series(
                    np.logical_or(resp_mudou.to_numpy(dtype=bool), nota_mudou.to_numpy(dtype=bool)),
                    index=_idx,
                    dtype=bool,
                )
                melhorou = pd.Series(
                    np.logical_and(
                        mud_resp_ou_nota.to_numpy(dtype=bool),
                        np.logical_or(
                            sobe_resposta.to_numpy(dtype=bool),
                            np.logical_and(
                                sobe_nota.to_numpy(dtype=bool),
                                np.logical_not(desce_resposta.to_numpy(dtype=bool)),
                            ),
                        ),
                    ),
                    index=_idx,
                    dtype=bool,
                )
                piorou = pd.Series(
                    np.logical_and(
                        mud_resp_ou_nota.to_numpy(dtype=bool),
                        np.logical_or(
                            desce_resposta.to_numpy(dtype=bool),
                            np.logical_and(
                                desce_nota.to_numpy(dtype=bool),
                                np.logical_not(sobe_resposta.to_numpy(dtype=bool)),
                            ),
                        ),
                    ),
                    index=_idx,
                    dtype=bool,
                )
                st.markdown("##### Resumo")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Dimensões só no «antes»", len(so_antes))
                m2.metric("Dimensões só no «depois»", len(so_depois))
                m3.metric("Melhorou (resposta/nota)", int(melhorou.sum()))
                m4.metric("Piorou (resposta/nota)", int(piorou.sum()))
                if so_antes:
                    st.caption("Só no ficheiro **antes**: " + ", ".join(so_antes[:30]) + ("…" if len(so_antes) > 30 else ""))
                if so_depois:
                    st.caption("Só no ficheiro **depois**: " + ", ".join(so_depois[:30]) + ("…" if len(so_depois) > 30 else ""))
                if linhas_mud.empty and not so_antes and not so_depois:
                    st.success("Nenhuma diferença encontrada nas colunas comparadas (dimensões comuns).")
                elif not linhas_mud.empty:
                    linhas_mud["Δ Nota"] = (na_b - na_a).reindex(linhas_mud.index)
                    idx = linhas_mud.index
                    m_m = melhorou.reindex(idx).fillna(False)
                    p_m = piorou.reindex(idx).fillna(False)
                    linhas_mud["Tendência"] = np.where(
                        m_m,
                        "Melhorou",
                        np.where(p_m, "Piorou", "Alterado"),
                    )
                    cols_show = [
                        "Dimensão",
                        "Resposta_antes",
                        "Resposta_depois",
                        "Nota_antes",
                        "Nota_depois",
                        "Δ Nota",
                        "Tendência",
                        "Descrição da Dimensão_antes",
                    ]
                    cols_show = [c for c in cols_show if c in linhas_mud.columns]
                    st.markdown("##### Alterações por dimensão")
                    _ordem = ["Melhorou", "Alterado", "Piorou"]
                    _tbl = linhas_mud[cols_show].copy()
                    _tbl["_ord"] = pd.Categorical(_tbl["Tendência"], categories=_ordem, ordered=True)
                    _tbl = _tbl.sort_values(["_ord", "Dimensão"]).drop(columns=["_ord"])
                    st.dataframe(_tbl, use_container_width=True, hide_index=True)


########################################################################################################
########################################################################################################
########################################################################################################    


########################
### Função principal ###
########################

def main():
    ### Configuração Inicial - Seleção de Ente e Ano ###

    st.header("Seleção de Parâmetros")

    fixed_ente = restricted_ranking_fixed_ente()
    if fixed_ente and fixed_ente[0] != "M":
        fixed_ente = None

    col1, col2, col3, col4 = st.columns([1, 1, 1.2, 1.8])

    # 1️⃣ Tipo de Ente: este app confere somente municípios
    with col1:
        if fixed_ente:
            tipo_ente = fixed_ente[0]
            st.text_input(
                "Tipo de Ente:",
                value="Município",
                disabled=True,
                help=(
                    "Este perfil de acesso permite apenas análise para o "
                    "município autorizado."
                ),
            )
            st.caption("Perfil restrito: município fixo.")
        else:
            tipo_ente = "M"
            st.text_input(
                "Tipo de Ente:",
                value="Município",
                disabled=True,
                help="O CRUZAMENTOS SICONFI confere apenas municípios.",
            )

    # 2. Carregar base correspondente (com cache de 24 horas)
    try:
        df_base, coluna_codigo, coluna_nome = load_base_ranking(
            tipo_ente, CAMINHO_BASE_ESTADOS, CAMINHO_BASE_MUNICIPIOS
        )


        
        # 2️⃣ Ano de Exercício
        with col2:
            # 3. Obter anos disponíveis
            anos_disponiveis = [2025, 2024, 2023]

            # 4. Selecionar Ano (2025 como padrão)
            ano = st.selectbox(
                "Exercício (Ano) de análise:",
                options=anos_disponiveis,
                index=0,
            )

        # 5. Filtrar base pelo ano selecionado
        # Para anos em andamento (como 2025) que não estão na base de ranking,
        # usar o ano mais recente disponível para obter a lista de entes
        df_ano = df_base[df_base['VA_EXERCICIO'] == ano].copy()

        if df_ano.empty:
            # Ano não existe na base de ranking - usar ano mais recente apenas para lista de entes
            anos_na_base = sorted(df_base['VA_EXERCICIO'].unique(), reverse=True)
            if anos_na_base:
                ano_base_entes = anos_na_base[0]
                df_ano = df_base[df_base['VA_EXERCICIO'] == ano_base_entes].copy()
                st.caption(f"📋 Lista de entes baseada no ranking {ano_base_entes}")

        # 6. Preparar lista de entes para seleção
        df_ano['display_name'] = df_ano.apply(
            lambda row: f"{row[coluna_nome]} ({row[coluna_codigo]})",
            axis=1
        )
        # A base pode ter várias linhas por ente/ano (ex.: por dimensão); o selectbox precisa de um ente por opção
        df_ano = (
            df_ano.drop_duplicates(subset=[coluna_codigo], keep='first')
            .sort_values(by=coluna_nome, kind='stable')
            .reset_index(drop=True)
        )

        if fixed_ente:
            _, cod_fixo = fixed_ente
            uf_fixa = str(cod_fixo).zfill(7)[:2]
            with col3:
                st.text_input(
                    "Estado do Município:",
                    value=f"{UF_IBGE_PREFIXOS.get(uf_fixa, uf_fixa)} ({uf_fixa})",
                    disabled=True,
                )
            match = df_ano[df_ano[coluna_codigo].astype(str) == str(cod_fixo)]
            if match.empty:
                st.error(
                    "❌ O ente autorizado para este perfil não foi encontrado na base de ranking "
                    "para o período considerado."
                )
                st.stop()
            ente_row = match.iloc[0]
            ente_selecionado = ente_row["display_name"]
            with col4:
                st.text_input(
                    f"{'Estado' if tipo_ente == 'E' else 'Município'}:",
                    value=ente_selecionado,
                    disabled=True,
                )
            ente = str(ente_row[coluna_codigo])
            cod = ente_row[coluna_nome]
        else:
            # 7. Selecionar Ente
            df_ano["_uf_codigo"] = df_ano[coluna_codigo].astype(str).str.zfill(7).str[:2]
            ufs_disponiveis = [
                uf for uf in UF_IBGE_PREFIXOS
                if uf in set(df_ano["_uf_codigo"].astype(str))
            ]
            if not ufs_disponiveis:
                st.error("❌ Nenhum estado foi identificado na base de municípios.")
                st.stop()

            uf_default = UF_PADRAO_MUNICIPIO if UF_PADRAO_MUNICIPIO in ufs_disponiveis else ufs_disponiveis[0]
            uf_labels = {uf: f"{UF_IBGE_PREFIXOS.get(uf, uf)} ({uf})" for uf in ufs_disponiveis}

            with col3:
                uf_selecionada = st.selectbox(
                    "Estado do Município:",
                    options=ufs_disponiveis,
                    index=ufs_disponiveis.index(uf_default),
                    format_func=lambda uf: uf_labels.get(uf, uf),
                )

            df_ano = df_ano[df_ano["_uf_codigo"] == uf_selecionada].copy()
            if df_ano.empty:
                st.error(
                    f"❌ Nenhum município encontrado para {UF_IBGE_PREFIXOS.get(uf_selecionada, uf_selecionada)}."
                )
                st.stop()

            # 3️⃣ Estado / Município
            with col4:
                ente_selecionado = st.selectbox(
                    f"{'Estado' if tipo_ente == 'E' else 'Município'}:",
                    options=df_ano['display_name'].tolist(),
                    index=0
                )

            # 8. Extrair código do ente selecionado
            ente_row = df_ano[df_ano['display_name'] == ente_selecionado].iloc[0]
            ente = str(ente_row[coluna_codigo])
            cod = ente_row[coluna_nome]

        st.markdown("---")
        st.caption("💡 **Cache:**\n- Bases de ranking: 24 horas\n- Dados da API: 12 horas")

    except FileNotFoundError as e:
        st.error(f"❌ Erro: Arquivo não encontrado")
        st.info(f"📁 Certifique-se de que o arquivo existe em:\n- Estados: `{CAMINHO_BASE_ESTADOS}`\n- Municípios: `{CAMINHO_BASE_MUNICIPIOS}`")
        st.stop()
    except pd.errors.ParserError as e:
        st.error(f"❌ Erro ao processar arquivo CSV: {str(e)}")
        st.info("💡 **Possíveis soluções:**\n"
                "1. Verifique se o arquivo tem vírgulas extras em alguma linha\n"
                "2. Verifique se há quebras de linha dentro de campos\n"
                "3. Tente abrir o CSV em um editor e verificar a estrutura\n"
                "4. Certifique-se de que todas as linhas têm o mesmo número de colunas")
        with st.expander("📋 Ver detalhes do erro"):
            st.code(str(e))
        st.stop()
    except KeyError as e:
        st.error(f"❌ Erro: Coluna não encontrada no arquivo CSV")
        st.info(f"🔍 Coluna esperada: {str(e)}\n\n"
                f"📊 Verifique se o arquivo contém as colunas corretas:\n"
                f"- Estados: VA_EXERCICIO, COD_IBGE, NO_ESTADO\n"
                f"- Municípios: VA_EXERCICIO, ID_ENTE, NOME_ENTE")
        if 'df_base' in locals():
            with st.expander("📋 Colunas encontradas no arquivo"):
                st.write(list(df_base.columns))
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro inesperado: {type(e).__name__}")
        with st.expander("📋 Ver detalhes do erro"):
            st.code(str(e))
        st.stop()

    # Exibir informações do ente selecionado
    st.info(f"**Ente:** {cod} ({ente})\n**Ano:** {ano}\n**Tipo:** {'Estado' if tipo_ente == 'E' else 'Município'}")

    #############################################################################
    # CONTROLE DE MUDANÇA DE ENTE/ANO - Limpa dados ao trocar
    #############################################################################
    #
    #   >>> Ver também o quadro "POLÍTICA DE CACHE" no topo deste ficheiro. <<<
    #
    #   Limpeza de session_state (extrato, bundles, etc.) — SEMPRE ativa.
    #
    #   Limpeza de st.cache_data ao mudar ente/ano — DESATIVADA por defeito
    #   (melhor para testes locais com vários entes). Para VPS apertada:
    #   descomentar st.cache_data.clear() e gc.collect() no bloco abaixo.
    #

    # Inicializar controles de ente/ano anterior
    if 'ente_anterior' not in st.session_state:
        st.session_state.ente_anterior = None
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = None
    if 'extrato_ente' not in st.session_state:
        st.session_state.extrato_ente = None
    if 'extrato_ano' not in st.session_state:
        st.session_state.extrato_ano = None

    # Detectar mudança de ente ou ano
    ente_mudou = st.session_state.ente_anterior != ente
    ano_mudou = st.session_state.ano_anterior != ano

    if ente_mudou or ano_mudou:
        # =====================================================================
        # OPCIONAL — VPS / RAM: descomentar as 2 linhas seguintes
        # =====================================================================
        # st.cache_data.clear()
        # gc.collect()
        # Motivo: sem isto, o cache guarda payloads por (ente, ano, …) e ao
        # testar RJ+GO no mesmo processo a RAM do SO pode subir até OOM.
        # Com isto, cada troca de ente/ano liberta cache; o próximo Processar
        # demora mais (vai de novo à API). Local: manter comentado.
        # =====================================================================
        # Limpar dados do ente/ano anterior
        if 'extrato_df' in st.session_state:
            del st.session_state['extrato_df']
        if 'tipo_relatorio' in st.session_state:
            del st.session_state['tipo_relatorio']
        if 'analise_processada' in st.session_state:
            st.session_state.analise_processada = False
        _limpar_bundles_exportacao_session()

        # Atualizar ente/ano anterior
        st.session_state.ente_anterior = ente
        st.session_state.ano_anterior = ano
        st.session_state.extrato_ente = None
        st.session_state.extrato_ano = None

    #############################################################################
    # SEÇÃO: EXTRATO DE ENTREGAS (OBRIGATÓRIO)
    #############################################################################

    st.markdown("---")
    st.subheader("📋 Extrato de Entregas SICONFI")

    # Verificar se extrato carregado é do ente/ano correto
    extrato_valido = (
        st.session_state.get('extrato_df') is not None and
        not st.session_state.get('extrato_df', pd.DataFrame()).empty and
        st.session_state.get('extrato_ente') == ente and
        st.session_state.get('extrato_ano') == ano
    )

    if not extrato_valido:
        st.warning("⚠️ **É necessário carregar o Extrato de Entregas** para verificar os demonstrativos enviados e detectar o tipo de relatório.")

    # Botão para carregar extratos
    col1, col2 = st.columns([3, 1])
    with col1:
        carregar_extratos = st.button("🚀 Carregar Extrato de Entregas", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Limpar Extrato", use_container_width=True):
            if "extrato_df" in st.session_state:
                del st.session_state["extrato_df"]
            st.session_state.extrato_ente = None
            st.session_state.extrato_ano = None
            if 'tipo_relatorio' in st.session_state:
                del st.session_state['tipo_relatorio']
            st.rerun()

    # Processar carregamento de extratos
    if carregar_extratos:
        progress_bar = st.progress(0)
        status_text = st.empty()
        try:
            status_text.info(f"🔄 Buscando extratos — Ente: {cod} ({ente}) • Ano: {ano}...")
            progress_bar.progress(20)

            extrato = get_extratos(ente, int(ano))
            progress_bar.progress(70)

            if extrato.empty:
                st.warning("⚠️ Não foram encontrados extratos para o ente/período informado.")
                st.session_state.extrato_ente = None
                st.session_state.extrato_ano = None
            else:
                # Converter coluna de data se existir
                if "dt_homologacao" in extrato.columns:
                    extrato["dt_homologacao"] = pd.to_datetime(extrato["dt_homologacao"], errors="coerce")

                st.session_state["extrato_df"] = extrato
                # Registrar qual ente/ano foi carregado
                st.session_state.extrato_ente = ente
                st.session_state.extrato_ano = ano
                status_text.success(f"✅ Extrato carregado com sucesso! Total de registros: {len(extrato)}")
                progress_bar.progress(100)
        except Exception as e:
            st.error(f"❌ Erro ao acessar a API: {e}")
        except Exception as e:
            st.error(f"❌ Erro ao processar os dados: {e}")
        finally:
            progress_bar.empty()
            status_text.empty()

    # Exibir e filtrar extratos se disponíveis
    df_extrato = st.session_state.get("extrato_df")
    if df_extrato is not None and not df_extrato.empty:
        st.markdown("---")
        st.markdown("### 🔍 Filtrar Resultados do Extrato")

        # Identificar colunas disponíveis para filtro
        colunas_filtro_possiveis = ["instituicao", "entregavel", "exercicio", "bimestre"]
        colunas_para_filtrar = [col for col in colunas_filtro_possiveis if col in df_extrato.columns]

        if colunas_para_filtrar:
            cols = st.columns(len(colunas_para_filtrar))
            filtros = {}

            for i, col in enumerate(colunas_para_filtrar):
                opcoes = ["Todos"] + sorted(df_extrato[col].dropna().astype(str).unique().tolist())
                filtros[col] = cols[i].selectbox(f"Filtrar {col.replace('_', ' ').title()}", opcoes, key=f"filter_{col}")

            # Aplicar filtros
            extrato_filtrado = df_extrato.copy()
            for col, val in filtros.items():
                if val and val != "Todos":
                    extrato_filtrado = extrato_filtrado[extrato_filtrado[col].astype(str) == val]
        else:
            extrato_filtrado = df_extrato.copy()

        # Exibir tabela
        st.markdown("### 📊 Dados do Extrato")
        st.dataframe(extrato_filtrado, use_container_width=True, height=420)

        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Registros", len(extrato_filtrado))
        with col2:
            if "instituicao" in extrato_filtrado.columns:
                st.metric("Instituições Únicas", extrato_filtrado["instituicao"].nunique())
        with col3:
            if "entregavel" in extrato_filtrado.columns:
                st.metric("Tipos de Entregáveis", extrato_filtrado["entregavel"].nunique())

        # Botão de download
        csv = extrato_filtrado.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar CSV",
            data=csv,
            file_name=f"extratos_{ente}_{ano}.csv",
            mime="text/csv",
            width="content",
        )

    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################


    #############################################################################
    # DETECÇÃO AUTOMÁTICA DO TIPO DE RELATÓRIO PARA MUNICÍPIOS
    #############################################################################

    # Inicializar session_state para tipo de relatório
    if 'tipo_relatorio' not in st.session_state:
        st.session_state.tipo_relatorio = None

    # Para Estados: sempre "Completo"
    # Para Municípios: detectar via Extrato
    if tipo_ente == "E":
        st.session_state.tipo_relatorio = "Completo"
    else:
        # Município: verificar se extrato foi carregado para detectar tipo
        df_extrato = st.session_state.get("extrato_df")
        if df_extrato is not None and not df_extrato.empty:
            tipo_detectado = detectar_tipo_relatorio(df_extrato)
            if tipo_detectado:
                st.session_state.tipo_relatorio = tipo_detectado

    st.markdown("---")
    st.markdown("---")

    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################


    

    #############################################################################
    # SEÇÃO: ANÁLISE D1 - QUALIDADE DOS DADOS
    #############################################################################

    st.subheader("📊 Análise Ranking SICONFI")

    # Verificar se extrato foi carregado para o ente/ano correto (OBRIGATÓRIO para todos)
    extrato_carregado = (
        st.session_state.get('extrato_df') is not None and
        not st.session_state.get('extrato_df', pd.DataFrame()).empty and
        st.session_state.get('extrato_ente') == ente and
        st.session_state.get('extrato_ano') == ano
    )

    if not extrato_carregado:
        st.error("⚠️ **É necessário carregar o Extrato de Entregas antes de processar a análise.**")
        st.info(f"👆 Por favor, clique no botão **'🚀 Carregar Extrato de Entregas'** na seção acima para o ente **{cod}** ({ano}).")
        st.stop()

    # Mostrar tipo de relatório detectado
    tipo_rel = st.session_state.get("tipo_relatorio", "Não detectado")
    if tipo_ente == "E":
        st.success(f"✅ **Extrato carregado para:** {cod} ({ano})\n\n"
                  f"📋 **Tipo de Relatório:** Completo (Estados sempre usam formato completo)")
    else:
        if tipo_rel == "Simplificado":
            st.success(f"✅ **Extrato carregado para:** {cod} ({ano})\n\n"
                      f"📋 **Tipo de Relatório Detectado:** {tipo_rel} (periodicidade semestral)")
        else:
            st.success(f"✅ **Extrato carregado para:** {cod} ({ano})\n\n"
                      f"📋 **Tipo de Relatório Detectado:** {tipo_rel} (periodicidade quadrimestral)")

    #############################################################################
    # PAINEL: STATUS DOS DEMONSTRATIVOS DISPONÍVEIS
    #############################################################################

    # Verificar disponibilidade dos demonstrativos
    df_extrato_atual = st.session_state.get("extrato_df")
    disponibilidade = verificar_disponibilidade_demonstrativos(df_extrato_atual, tipo_ente, tipo_rel)

    # Armazenar disponibilidade no session_state para uso posterior
    st.session_state['disponibilidade_demonstrativos'] = disponibilidade

    # Extrair meses disponíveis da MSC para uso no carregamento
    meses_disponiveis = disponibilidade['msc']['periodos'] if disponibilidade['msc']['disponivel'] else []
    st.session_state['meses_disponiveis'] = meses_disponiveis

    # Criar painel de status
    with st.expander("📊 **Status dos Demonstrativos Disponíveis**", expanded=True):
        # Criar DataFrame para exibição
        status_data = []

        # MSC Agregada
        status_msc = "✅ Completa" if disponibilidade['msc']['completo'] else ("⚠️ Parcial" if disponibilidade['msc']['disponivel'] else "❌ Ausente")
        status_data.append({
            'Demonstrativo': 'MSC Agregada',
            'Status': status_msc,
            'Detalhes': disponibilidade['msc']['mensagem']
        })

        # MSC Encerramento
        status_msce = "✅ Enviada" if disponibilidade['msc_encerramento']['disponivel'] else "❌ Ausente"
        status_data.append({
            'Demonstrativo': 'MSC Encerramento',
            'Status': status_msce,
            'Detalhes': disponibilidade['msc_encerramento']['mensagem']
        })

        # DCA
        status_dca = "✅ Enviada" if disponibilidade['dca']['disponivel'] else "❌ Ausente"
        status_data.append({
            'Demonstrativo': 'DCA (Balanço Anual)',
            'Status': status_dca,
            'Detalhes': disponibilidade['dca']['mensagem']
        })

        # RREO
        status_rreo = "✅ Completo" if disponibilidade['rreo']['completo'] else ("⚠️ Parcial" if disponibilidade['rreo']['disponivel'] else "❌ Ausente")
        status_data.append({
            'Demonstrativo': 'RREO',
            'Status': status_rreo,
            'Detalhes': disponibilidade['rreo']['mensagem']
        })

        # RGF
        status_rgf = "✅ Completo" if disponibilidade['rgf']['completo'] else ("⚠️ Parcial" if disponibilidade['rgf']['disponivel'] else "❌ Ausente")
        status_data.append({
            'Demonstrativo': 'RGF',
            'Status': status_rgf,
            'Detalhes': disponibilidade['rgf']['mensagem']
        })

        df_status = pd.DataFrame(status_data)
        st.dataframe(df_status, use_container_width=True, hide_index=True)

        # Resumo das dimensões que serão executadas
        st.markdown("---")
        st.markdown("**📋 Resumo dos extratos disponíveis e das análises que podem ser executadas:**")

        st.info("ℹ️ **Dimensão D1** removida/desativada neste aplicativo.")

        # D2 Antecipada - sempre executa se MSC disponível
        if disponibilidade['msc']['disponivel']:
            ultimo_mes = max(meses_disponiveis) if meses_disponiveis else 0
            st.info(f"🔮 **D2 Antecipada (Matriz)** - Análise prévia disponível (mês {ultimo_mes})")

        # D2: pode executar parcialmente com MSC/MSC Encerramento mesmo sem DCA
        base_d2_msc = disponibilidade['msc']['disponivel'] or disponibilidade['msc_encerramento']['disponivel']
        if disponibilidade['dca']['disponivel']:
            st.success("✅ **Dimensão D2** será executada com verificações da DCA e da MSC")
        elif base_d2_msc:
            st.warning(
                "⚠️ **Dimensão D2 (parcial):** sem DCA, serão executadas as verificações que dependem "
                "apenas da MSC mensal e/ou da MSC de encerramento; as que exigem DCA ficarão em N/A."
            )
        else:
            faltam = []
            if not disponibilidade['dca']['disponivel']:
                faltam.append("DCA")
            if not disponibilidade['msc']['disponivel']:
                faltam.append("MSC")
            if not disponibilidade['msc_encerramento']['disponivel']:
                faltam.append("MSC Encerramento")
            st.warning(f"⚠️ **Dimensão D2** não será executada (falta: {', '.join(faltam)})")

        # D3 - precisa de RREO completo na maioria
        if disponibilidade['rreo']['completo'] and disponibilidade['msc']['disponivel']:
            st.success("✅ **Dimensão D3** será executada")
        else:
            faltam = []
            if not disponibilidade['rreo']['completo']:
                faltam.append("RREO 6º bimestre")
            if not disponibilidade['msc']['disponivel']:
                faltam.append("MSC")
            st.error(f"❌ **Dimensão D3** não será executada (falta: {', '.join(faltam)})")

        # D4: RREO 6º + MSC são base; DCA só para cruzamentos RREO×DCA e RGF×DCA
        base_d4 = disponibilidade['rreo']['completo'] and disponibilidade['msc']['disponivel']
        if base_d4 and disponibilidade['dca']['disponivel']:
            st.success("✅ **Dimensão D4** será executada (inclui cruzamentos com DCA)")
        elif base_d4:
            st.warning(
                "⚠️ **Dimensão D4 (parcial):** sem DCA, serão executadas as verificações MSC×RREO, "
                "RGF×MSC e demais que não dependem do Balanço Anual; as que exigem DCA ficarão em N/A."
            )
        else:
            faltam = []
            if not disponibilidade['rreo']['completo']:
                faltam.append("RREO 6º bimestre")
            if not disponibilidade['msc']['disponivel']:
                faltam.append("MSC")
            st.error(f"❌ **Dimensão D4** não será executada (falta: {', '.join(faltam)})")

    # Inicializar session_state para controle de análise
    if 'analise_processada' not in st.session_state:
        st.session_state.analise_processada = False
    if 'analise_ente' not in st.session_state:
        st.session_state.analise_ente = None
    if 'analise_ano' not in st.session_state:
        st.session_state.analise_ano = None
    st.markdown("---")

    # Botões para processar análise e limpar cache
    col1, col2 = st.columns([3, 1])
    with col1:
        processar = st.button("▶️ Processar Análise", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Limpar Cache", use_container_width=True, help="Limpa o cache e recarrega os dados da API"):
            st.cache_data.clear()
            st.session_state.analise_processada = False
            _limpar_bundles_exportacao_session()
            gc.collect()
            st.success("✅ Cache limpo!")
            st.info("🔄 Recarregue a página para aplicar as mudanças.")
            st.stop()

    # Se clicou em processar, atualiza o estado
    if processar:
        _limpar_bundles_exportacao_session()
        st.session_state.analise_processada = True
        st.session_state.analise_ente = ente
        st.session_state.analise_ano = ano

    # Se mudou o ente ou ano, reseta o estado
    if (st.session_state.analise_ente != ente or st.session_state.analise_ano != ano):
        st.session_state.analise_processada = False
        _limpar_bundles_exportacao_session()

    # Verificar se a análise foi processada
    if not st.session_state.analise_processada:
        # Só avisa "troca de ente" quando já havia ente/ano anterior (evita ruído na 1ª seleção).
        _ja_havia_contexto = (
            st.session_state.get('ente_anterior') is not None
            or st.session_state.get('ano_anterior') is not None
        )
        if (ente_mudou or ano_mudou) and _ja_havia_contexto:
            st.warning(
                "🔄 **Ente ou ano alterado:** os demonstrativos em memória e os bytes da exportação "
                "(Excel/CSV) do **contexto anterior** foram descartados por segurança — não misturamos dados "
                "de dois entes. Clique em **▶️ Processar Análise** para carregar o novo ente/ano e voltar a "
                "ver o quadro de demonstrativos e **Exportar Demonstrativos para Excel**."
            )
        st.info("👆 Clique no botão **▶️ Processar Análise** acima para iniciar a análise dos dados.")
        st.stop()


    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################


    tipos_balanco = ['ending_balance', 'beginning_balance', 'period_change']

    # Cruzamentos usam apenas a MSC corrente de dezembro (MSCC/12).
    # A MSC de encerramento é carregada separadamente como MSCE/12 pelo loader.
    meses_disponiveis = st.session_state.get('meses_disponiveis', list(range(1, 13)))
    if not meses_disponiveis:
        meses_disponiveis = list(range(1, 13))  # Fallback para 1-12 se não detectado
    meses = [12]
    if 12 not in set(meses_disponiveis):
        st.warning(
            "⚠️ MSC corrente de dezembro não aparece no extrato. "
            "A API será consultada apenas para o mês 12; se não houver dados, "
            "as verificações dependentes da MSC corrente ficarão sem base."
        )

    # Obter disponibilidade dos demonstrativos
    disponibilidade = st.session_state.get('disponibilidade_demonstrativos', {})

    # Criar indicadores de progresso ANTES de carregar
    st.markdown("#### Aguarde o processamento da análise (pode levar alguns minutos).")
    st.caption(f"**Ente:** {cod} ({ente}) · **Ano:** {ano}")
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Carregar dados (com cache)
    # Obter tipo de relatório do session_state (para Municípios pode ser Simplificado ou Completo)
    tipo_relatorio = st.session_state.get("tipo_relatorio", "Completo")

    # Determinar quais demonstrativos carregar baseado na disponibilidade
    carregar_msce = disponibilidade.get('msc_encerramento', {}).get('disponivel', True)
    carregar_dca = disponibilidade.get('dca', {}).get('disponivel', True)
    carregar_rreo = disponibilidade.get('rreo', {}).get('disponivel', True)
    carregar_rgf = disponibilidade.get('rgf', {}).get('disponivel', True)

    status_text.text(
        f"🔄 Carregando dados da API SICONFI — Ente: {cod} ({ente}) · Ano: {ano} · "
        f"Tipo: {tipo_relatorio} · MSC corrente: mês 12 · MSC encerramento: "
        f"{'sim' if carregar_msce else 'não'}"
    )
    progress_bar.progress(5)

    dados = load_all_data_cached(
        ente, ano, meses, tipos_balanco,
        tipo_ente=tipo_ente, tipo_relatorio=tipo_relatorio,
        carregar_msce=carregar_msce, carregar_dca=carregar_dca,
        carregar_rreo=carregar_rreo, carregar_rgf=carregar_rgf
    )

    status_text.text("✅ Dados carregados com sucesso!")
    progress_bar.progress(10)

    # Extrair dados do dicionário
    status_text.text("⏳ Processando MSC Corrente...")
    progress_bar.progress(15)

    msc_patrimonial = dados['msc_patrimonial']
    msc_orcam = dados['msc_orcam']
    msc_ctr = dados['msc_ctr']
    msc_patrimonial_orig = msc_patrimonial.copy()
    msc_orcam_orig = msc_orcam.copy()
    msc_ctr_orig = msc_ctr.copy()

    status_text.text("✅ MSC Corrente carregada! Processando ajustes...")
    progress_bar.progress(35)

    # Ajustes de sinal (iguais ao seu código)
    mascara_retificadora1 = (
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '1') & (msc_patrimonial['natureza_conta'] == 'C')) |
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '2') & (msc_patrimonial['natureza_conta'] == 'D')) |
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '3') & (msc_patrimonial['natureza_conta'] == 'C')) |
        ((msc_patrimonial['conta_contabil'].astype(str).str[0] == '4') & (msc_patrimonial['natureza_conta'] == 'D'))
    )
    if not (msc_patrimonial.loc[mascara_retificadora1, 'valor'] < 0).any():
        msc_patrimonial.loc[mascara_retificadora1, 'valor'] *= -1

    mascara_retificadora2 = (
        ((msc_orcam['conta_contabil'].astype(str).str[0] == '5') & (msc_orcam['natureza_conta'] == 'C') & (~msc_orcam['tipo_valor'].eq('period_change'))) |
        ((msc_orcam['conta_contabil'].astype(str).str[0] == '6') & (msc_orcam['natureza_conta'] == 'D') & (~msc_orcam['tipo_valor'].eq('period_change')))
    )
    if not (msc_orcam.loc[mascara_retificadora2, 'valor'] < 0).any():
        msc_orcam.loc[mascara_retificadora2, 'valor'] *= -1

    mascara_retificadora3 = (
        ((msc_ctr['conta_contabil'].astype(str).str[0] == '7') & (msc_ctr['natureza_conta'] == 'C') & (~msc_ctr['tipo_valor'].eq('period_change'))) |
        ((msc_ctr['conta_contabil'].astype(str).str[0] == '8') & (msc_ctr['natureza_conta'] == 'D') & (~msc_ctr['tipo_valor'].eq('period_change')))
    )
    if not (msc_ctr.loc[mascara_retificadora3, 'valor'] < 0).any():
        msc_ctr.loc[mascara_retificadora3, 'valor'] *= -1

    msc = pd.concat([msc_patrimonial, msc_orcam, msc_ctr])

    # MSC de Encerramento (MSCE, mês 12) - só processa se disponível
    msc_orig = pd.concat([msc_patrimonial_orig, msc_orcam_orig, msc_ctr_orig])

    if carregar_msce:
        status_text.text("⏳ Processando MSC de Encerramento (Dezembro)...")
        progress_bar.progress(40)
        msc_patrimonial_encerr = dados['msc_patrimonial_encerr']
        msc_orcam_encerr = dados['msc_orcam_encerr']
        msc_ctr_encerr = dados['msc_ctr_encerr']
        msc_patr_encerr_orig = msc_patrimonial_encerr.copy()
        msc_orcam_encerr_orig = msc_orcam_encerr.copy()
        msc_ctr_encerr_orig = msc_ctr_encerr.copy()

        # Só aplica transformações se há dados
        if not msc_patrimonial_encerr.empty and 'conta_contabil' in msc_patrimonial_encerr.columns:
            mascara_retificadora7 = (
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '1') & (msc_patrimonial_encerr['natureza_conta'] == 'C') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '2') & (msc_patrimonial_encerr['natureza_conta'] == 'D') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '3') & (msc_patrimonial_encerr['natureza_conta'] == 'C') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_patrimonial_encerr['conta_contabil'].astype(str).str[0] == '4') & (msc_patrimonial_encerr['natureza_conta'] == 'D') & (~msc_patrimonial_encerr['tipo_valor'].eq('period_change')))
            )
            if not (msc_patrimonial_encerr.loc[mascara_retificadora7, 'valor'] < 0).any():
                msc_patrimonial_encerr.loc[mascara_retificadora7, 'valor'] *= -1

        if not msc_orcam_encerr.empty and 'conta_contabil' in msc_orcam_encerr.columns:
            mascara_retificadora8 = (
                ((msc_orcam_encerr['conta_contabil'].astype(str).str[0] == '5') & (msc_orcam_encerr['natureza_conta'] == 'C') & (~msc_orcam_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_orcam_encerr['conta_contabil'].astype(str).str[0] == '6') & (msc_orcam_encerr['natureza_conta'] == 'D') & (~msc_orcam_encerr['tipo_valor'].eq('period_change')))
            )
            if not (msc_orcam_encerr.loc[mascara_retificadora8, 'valor'] < 0).any():
                msc_orcam_encerr.loc[mascara_retificadora8, 'valor'] *= -1

        if not msc_ctr_encerr.empty and 'conta_contabil' in msc_ctr_encerr.columns:
            mascara_retificadora9 = (
                ((msc_ctr_encerr['conta_contabil'].astype(str).str[0] == '7') & (msc_ctr_encerr['natureza_conta'] == 'C') & (~msc_ctr_encerr['tipo_valor'].eq('period_change'))) |
                ((msc_ctr_encerr['conta_contabil'].astype(str).str[0] == '8') & (msc_ctr_encerr['natureza_conta'] == 'D') & (~msc_ctr_encerr['tipo_valor'].eq('period_change')))
            )
            if not (msc_ctr_encerr.loc[mascara_retificadora9, 'valor'] < 0).any():
                msc_ctr_encerr.loc[mascara_retificadora9, 'valor'] *= -1

        msc_encerr = pd.concat([msc_patrimonial_encerr, msc_orcam_encerr, msc_ctr_encerr])
        msc_consolidada = pd.concat([msc, msc_encerr])

        msc_orig_encerr = pd.concat([msc_patr_encerr_orig, msc_orcam_encerr_orig, msc_ctr_encerr_orig])
        msc_orig_consolidada = pd.concat([msc_orig, msc_orig_encerr])

        status_text.text("✅ MSC Encerramento processada!")
        progress_bar.progress(55)
    else:
        # MSCE não disponível - usar apenas MSC mensal
        status_text.text("⏳ MSC de Encerramento não disponível, usando apenas MSC mensal...")
        progress_bar.progress(55)
        msc_patrimonial_encerr = pd.DataFrame()
        msc_orcam_encerr = pd.DataFrame()
        msc_ctr_encerr = pd.DataFrame()
        msc_encerr = pd.DataFrame()
        msc_consolidada = msc.copy()
        msc_orig_encerr = pd.DataFrame()
        msc_orig_consolidada = msc_orig.copy()

    # DCA - só processa se disponível
    if carregar_dca:
        status_text.text("⏳ Processando DCA (Demonstrativo de Contas Anuais)...")
        progress_bar.progress(60)
        dca = dados['dca']
        df_dca_ab = dca.get("ab", pd.DataFrame())
        df_dca_c = dca.get("c", pd.DataFrame())
        df_dca_d = dca.get("d", pd.DataFrame())
        df_dca_e = dca.get("e", pd.DataFrame())
        df_dca_f = dca.get("f", pd.DataFrame())
        df_dca_g = dca.get("g", pd.DataFrame())
        df_dca_hi = dca.get("hi", pd.DataFrame())
        df_dca_ab_orig = df_dca_ab.copy()
        df_dca_c_orig = df_dca_c.copy()
        # Ajustes DCA
        if not df_dca_c.empty and "coluna" in df_dca_c.columns and "valor" in df_dca_c.columns:
            df_dca_c['valor'] = df_dca_c.apply(lambda row: -row['valor'] if 'Deduções' in str(row.get('coluna', '')) else row['valor'], axis=1)
        if not df_dca_ab.empty and "conta" in df_dca_ab.columns and "valor" in df_dca_ab.columns:
            df_dca_ab['valor'] = df_dca_ab.apply(lambda row: -row['valor'] if '(-)' in str(row.get('conta', '')) else row['valor'], axis=1)
        status_text.text("✅ DCA processado!")
        progress_bar.progress(70)
    else:
        status_text.text("⏳ DCA não disponível, pulando...")
        progress_bar.progress(70)
        dca = dados['dca']
        df_dca_ab = pd.DataFrame()
        df_dca_c = pd.DataFrame()
        df_dca_d = pd.DataFrame()
        df_dca_e = pd.DataFrame()
        df_dca_f = pd.DataFrame()
        df_dca_g = pd.DataFrame()
        df_dca_hi = pd.DataFrame()
        df_dca_ab_orig = pd.DataFrame()
        df_dca_c_orig = pd.DataFrame()

    # RREO
    status_text.text("⏳ Processando RREO (Relatório Resumido de Execução Orçamentária)...")
    progress_bar.progress(75)
    rreo = dados['rreo']
    status_text.text("✅ RREO processado!")
    progress_bar.progress(80)
    if isinstance(rreo, dict):
        df_rreo_1 = rreo.get("1", pd.DataFrame())
        df_rreo_2 = rreo.get("2", pd.DataFrame())
        df_rreo_3 = rreo.get("3", pd.DataFrame())
        df_rreo_4 = rreo.get("4", pd.DataFrame())
        df_rreo_4_rpps = rreo.get("4_rpps", pd.DataFrame())
        df_rreo_6 = rreo.get("6", pd.DataFrame())
        df_rreo_7 = rreo.get("7", pd.DataFrame())
        df_rreo_9 = rreo.get("9", pd.DataFrame())
    else:
        df_rreo_1 = pd.DataFrame()
        df_rreo_2 = pd.DataFrame()
        df_rreo_3 = pd.DataFrame()
        df_rreo_4 = pd.DataFrame()
        df_rreo_4_rpps = pd.DataFrame()
        df_rreo_6 = pd.DataFrame()
        df_rreo_7 = pd.DataFrame()
        df_rreo_9 = pd.DataFrame()

    # RGF
    status_text.text("⏳ Processando RGF (Relatório de Gestão Fiscal)...")
    progress_bar.progress(85)
    rgf = dados['rgf']
    status_text.text("✅ RGF processado! Finalizando análises...")
    progress_bar.progress(90)
    if isinstance(rgf, dict):
        df_rgf_1e = rgf.get("1e", pd.DataFrame())
        df_rgf_2e = rgf.get("2e", pd.DataFrame())
        df_rgf_3e = rgf.get("3e", pd.DataFrame())
        df_rgf_4e = rgf.get("4e", pd.DataFrame())
        df_rgf_5e = rgf.get("5e", pd.DataFrame())
    else:
        df_rgf_1e = pd.DataFrame()
        df_rgf_2e = pd.DataFrame()
        df_rgf_3e = pd.DataFrame()
        df_rgf_4e = pd.DataFrame()
        df_rgf_5e = pd.DataFrame()

    # RGF Anexo 1 consolidado (todos os poderes do ente),
    # com tag _poder_origem injetada para detalhamento por poder nas verificações.
    if isinstance(rgf, dict):
        if tipo_ente == "E":
            _rgf_1_chaves = [("1e", "E"), ("1l", "L"), ("1j", "J"), ("1m", "M"), ("1d", "D")]
        else:
            _rgf_1_chaves = [("1e", "E"), ("1l", "L")]
        _rgf_1_partes = []
        for _k, _sigla in _rgf_1_chaves:
            _df_p = rgf.get(_k, pd.DataFrame())
            if isinstance(_df_p, pd.DataFrame) and not _df_p.empty:
                _df_p = _df_p.copy()
                _df_p['_poder_origem'] = _sigla
                _rgf_1_partes.append(_df_p)
        df_rgf_1 = (
            pd.concat(_rgf_1_partes, ignore_index=True) if _rgf_1_partes else pd.DataFrame()
        )
    else:
        df_rgf_1 = pd.DataFrame()
    
    # Agregações RGF - diferenciadas por tipo de ente
    # Estados: todos os poderes (E, L, J, M, D)
    # Municípios: apenas Executivo e Legislativo (E, L)
    if tipo_ente == "E":
        # Estados - todos os poderes
        rgf_total = pd.concat([
            rgf.get("5e", pd.DataFrame()),
            rgf.get("5l", pd.DataFrame()),
            rgf.get("5j", pd.DataFrame()),
            rgf.get("5m", pd.DataFrame()),
            rgf.get("5d", pd.DataFrame())
        ], ignore_index=True)
        df_rgf_5 = rgf_total.copy()
        rgf_o = pd.concat([
            rgf.get("5l", pd.DataFrame()),
            rgf.get("5j", pd.DataFrame()),
            rgf.get("5m", pd.DataFrame()),
            rgf.get("5d", pd.DataFrame())
        ], ignore_index=True)
    else:
        # Municípios - apenas Executivo e Legislativo
        rgf_5e = rgf.get("5e", pd.DataFrame())
        rgf_5l = rgf.get("5l", pd.DataFrame())
        rgf_total = pd.concat([rgf_5e, rgf_5l], ignore_index=True)
        df_rgf_5 = rgf_total.copy()
        rgf_o = rgf_5l.copy() if not rgf_5l.empty else pd.DataFrame(columns=['cod_conta', 'conta', 'anexo', 'valor'])  # Outros poderes = apenas Legislativo

    #############################################################################
    # VALIDAÇÃO DE DEMONSTRATIVOS ENVIADOS AO SICONFI
    #############################################################################
    status_text.text("🔍 Validando demonstrativos enviados...")
    progress_bar.progress(70)

    # Verificar quais demonstrativos estão disponíveis
    demonstrativos_status = {
        'MSC Patrimonial': not msc_patrimonial.empty,
        'MSC Orçamentária': not msc_orcam.empty,
        'MSC Controle': not msc_ctr.empty,
        'MSC Encerramento Patrimonial': not msc_patrimonial_encerr.empty,
        'MSC Encerramento Orçamentária': not msc_orcam_encerr.empty,
        'MSC Encerramento Controle': not msc_ctr_encerr.empty,
        'DCA - Anexo I-AB': not df_dca_ab.empty,
        'DCA - Anexo I-C': not df_dca_c.empty,
        'DCA - Anexo I-D': not df_dca_d.empty,
        'DCA - Anexo I-E': not df_dca_e.empty,
        'DCA - Anexo I-F': not df_dca_f.empty,
        'DCA - Anexo I-G': not df_dca_g.empty,
        'DCA - Anexo I-HI': not df_dca_hi.empty,
    }

    status_rreo = {
        'RREO - Anexo 1': not df_rreo_1.empty,
        'RREO - Anexo 2': not df_rreo_2.empty,
        'RREO - Anexo 3': not df_rreo_3.empty,
        'RREO - Anexo 4': not df_rreo_4.empty,
        'RREO - Anexo 6': not df_rreo_6.empty,
        'RREO - Anexo 7': not df_rreo_7.empty,
        'RREO - Anexo 9': not df_rreo_9.empty,
    }

    status_rgf = {
        'RGF - Anexo 1 (E)': not df_rgf_1e.empty,
        'RGF - Anexo 2 (E)': not df_rgf_2e.empty,
        'RGF - Anexo 3 (E)': not df_rgf_3e.empty,
        'RGF - Anexo 4 (E)': not df_rgf_4e.empty,
        'RGF - Anexo 5 (E)': not df_rgf_5e.empty,
    }
    if tipo_ente == "E":
        # Estados: E, L, J, M, D
        status_rgf.update({
        'RGF - Anexo 5 (L)': not rgf.get('5l', pd.DataFrame()).empty,
        'RGF - Anexo 5 (J)': not rgf.get('5j', pd.DataFrame()).empty,
        'RGF - Anexo 5 (M)': not rgf.get('5m', pd.DataFrame()).empty,
        'RGF - Anexo 5 (D)': not rgf.get('5d', pd.DataFrame()).empty,
        })
    else:
        # Municípios: apenas E e L
        status_rgf.update({
        'RGF - Anexo 5 (L)': not rgf.get('5l', pd.DataFrame()).empty,
        })

    demonstrativos_status.update(status_rreo)
    demonstrativos_status.update(status_rgf)

    # Classificar demonstrativos por criticidade
    criticos_d1 = ['MSC Patrimonial', 'MSC Orçamentária', 'MSC Controle']
    criticos_d2 = ['DCA - Anexo I-AB', 'DCA - Anexo I-C', 'DCA - Anexo I-D', 'MSC Encerramento Patrimonial', 'MSC Encerramento Orçamentária']

    # Verificar demonstrativos faltantes
    faltantes = [k for k, v in demonstrativos_status.items() if not v]
    faltantes_d1 = [f for f in faltantes if f in criticos_d1]
    faltantes_d2 = [f for f in faltantes if f in criticos_d2]

    # Flags de controle
    pode_executar_d1 = len(faltantes_d1) == 0
    pode_executar_d2 = len(faltantes_d2) == 0

    status_text.text("✅ Validação concluída!")
    progress_bar.progress(75)

    # Exibir painel de status dos demonstrativos
    st.markdown("---")
    st.subheader("📋 Status dos Demonstrativos SICONFI")

    # Mostrar resumo em colunas
    col1, col2, col3 = st.columns(3)
    total_ok = sum(demonstrativos_status.values())
    total_faltando = len(demonstrativos_status) - total_ok

    with col1:
        st.metric("✅ Disponíveis", total_ok)
    with col2:
        st.metric("❌ Não Encontrados", total_faltando)
    with col3:
        if total_faltando == 0:
            st.metric("📊 Status Geral", "Completo")
        else:
            st.metric("📊 Status Geral", "Incompleto")

    # Expander com detalhes
    with st.expander("🔍 Ver Detalhes dos Demonstrativos", expanded=total_faltando > 0):
        col_msc, col_dca, col_rreo, col_rgf = st.columns(4)

        with col_msc:
            st.markdown("**MSC (Matriz de Saldos Contábeis)**")
            for demo in ['MSC Patrimonial', 'MSC Orçamentária', 'MSC Controle',
                        'MSC Encerramento Patrimonial', 'MSC Encerramento Orçamentária', 'MSC Encerramento Controle']:
                if demonstrativos_status.get(demo, False):
                    st.markdown(f"✅ {demo}")
                else:
                    st.markdown(f"❌ {demo}")

        with col_dca:
            st.markdown("**DCA (Demonst. Contas Anuais)**")
            for demo in ['DCA - Anexo I-AB', 'DCA - Anexo I-C', 'DCA - Anexo I-D',
                        'DCA - Anexo I-E', 'DCA - Anexo I-F', 'DCA - Anexo I-G', 'DCA - Anexo I-HI']:
                if demonstrativos_status.get(demo, False):
                    st.markdown(f"✅ {demo}")
                else:
                    st.markdown(f"❌ {demo}")

        with col_rreo:
            st.markdown("RREO (Relatório Resumido de Execução Orçamentária)")
            for nome, ok in status_rreo.items():
                st.markdown(f"{'✅' if ok else '❌'} {nome}")

        with col_rgf:
            st.markdown("**RGF (Relatório de Gestão Fiscal)**")
            for nome, ok in status_rgf.items():
                st.markdown(f"{'✅' if ok else '❌'} {nome}")


    # Alertas específicos
    if faltantes:
        st.warning(f"⚠️ **Atenção:** {len(faltantes)} demonstrativo(s) não encontrado(s) no SICONFI para o ente/período selecionado.")

        if not pode_executar_d1:
            st.error(f"🚫 **Análise D1 prejudicada:** Faltam demonstrativos críticos: {', '.join(faltantes_d1)}")

        if not pode_executar_d2:
            st.error(f"🚫 **Análise D2 prejudicada:** Faltam demonstrativos críticos: {', '.join(faltantes_d2)}")

        # Listar verificações prejudicadas
        verificacoes_prejudicadas = []
        if not pode_executar_d2:
            if 'DCA - Anexo I-C' in faltantes:
                verificacoes_prejudicadas.extend(['D2_00044', 'D2_00045', 'D2_00046', 'D2_00010', 'D2_00011', 'D2_00012'])
            if 'DCA - Anexo I-AB' in faltantes:
                verificacoes_prejudicadas.extend(['D2_00013', 'D2_00014', 'D2_00015', 'D2_00040'])
            if 'DCA - Anexo I-D' in faltantes:
                verificacoes_prejudicadas.extend(['D2_00002', 'D2_00003', 'D2_00004', 'D2_00005', 'D2_00006', 'D2_00007', 'D2_00008'])

        if verificacoes_prejudicadas:
            with st.expander("📋 Verificações Prejudicadas pela Falta de Demonstrativos"):
                st.markdown("As seguintes verificações podem apresentar erros ou resultados incorretos:")
                for v in sorted(set(verificacoes_prejudicadas)):
                    st.markdown(f"- {v}")

    #############################################################################
    # EXPORTAÇÃO DOS DEMONSTRATIVOS (fragmento: não reexecuta o pipeline ao clicar/baixar)
    #############################################################################
    st.session_state["_bundle_demonstrativos"] = {
        "cod": cod,
        "ente": ente,
        "ano": ano,
        "tipo_ente": tipo_ente,
        "total_ok": total_ok,
        "total_faltando": total_faltando,
        "df_dca_ab": df_dca_ab,
        "df_dca_c_orig": df_dca_c_orig,
        "df_dca_d": df_dca_d,
        "df_dca_e": df_dca_e,
        "df_dca_f": df_dca_f,
        "df_dca_g": df_dca_g,
        "df_dca_hi": df_dca_hi,
        "rreo": rreo,
        "rgf": rgf,
        "msc_consolidada": msc_consolidada,
    }
    fragmento_exportar_demonstrativos()

    status_text.text("⏳ Executando análises...")
    progress_bar.progress(85)

    ##############################################################################################################################
    ##############################################################################################################################
    # Criando matrizes Específicas para as análises
    
    msc_dez = msc.query('mes_referencia == 12')

    msc_consolidada_e = msc_consolidada.query('tipo_valor == "ending_balance"')
    msc_consolidada_b = msc_consolidada.query('tipo_valor == "beginning_balance"')

    msc_e = msc.query('tipo_valor == "ending_balance"')
    msc_b = msc.query('tipo_valor == "beginning_balance"')
    
    msc_orig_e = msc_orig.query('tipo_valor == "ending_balance"')
    msc_orig_b = msc_orig.query('tipo_valor == "beginning_balance"')
    
    msc_orig_consolidada_e = msc_orig_consolidada.query('tipo_valor == "ending_balance"')
    msc_orig_consolidada_b = msc_orig_consolidada.query('tipo_valor == "beginning_balance"')
    
    
    ##########################################################################################################
    # Criando AJUSTES
    # Função para extrair o terceiro e quarto dígito com verificação de comprimento
    def extrair_terceiro_quarto_digito(valor):
        valor_str = str(valor)
        if len(valor_str) >= 4:
            return valor_str[2:4]  # Extrai do índice 2 até o índice 3 (terceiro e quarto dígito)
        else:
            return None  # Ou qualquer valor padrão que você queira usar
        
    # Criando Variáveis da MSC
    # Variáveis da MSC       
    # Receita não pegar o Saldo Final da Matriz de Encerramento (por isso não usa a "msc_consolidada_e")
    receita = msc_e[msc_e['conta_contabil'].str.match(r"^(6212|6213)")]
    receita_dez = receita.query('mes_referencia == 12')

    receita_dez['cat_receita'] = receita_dez['natureza_receita'].astype(str).str[0]
    receita_corr = receita_dez.query('cat_receita == "1"')
    receita_capi = receita_dez.query('cat_receita == "2"')
    
    ## Criando Despesa Corrente e de Capital 
    despesa = msc_dez[msc_dez['conta_contabil'].str.match(r"^(6221)")]
    
    # Aplicando a função ao DataFrame
    despesa['DIGITO_INTRA'] = despesa['natureza_despesa'].apply(extrair_terceiro_quarto_digito)
    
    # Despesa empenhada dez (62213… + natureza preenchida; alinhado a emp_msc_encerr / D4_00025 MSC)
    _emp_tb = despesa['tipo_valor'] == 'ending_balance'
    _emp_cc = despesa['conta_contabil'].astype(str).str.startswith('62213')
    if 'natureza_despesa' in despesa.columns:
        _emp_nd = despesa['natureza_despesa']
        _emp_nd_ok = _emp_nd.notna() & (_emp_nd.astype(str).str.strip() != '')
        emp_msc_dez = despesa.loc[_emp_tb & _emp_cc & _emp_nd_ok].copy()
    else:
        emp_msc_dez = despesa.loc[_emp_tb & _emp_cc].copy()
    
    despesa_corr = despesa[despesa['natureza_despesa'].str.match(r"^3", na=False)]
    despesa_capi = despesa[despesa['natureza_despesa'].str.match(r"^4", na=False)]
    
    
    #################################################################################

    #Pegando a Depesa Empenhada na Matriz e quebrando a Informação da Modalidade em Não Intra e Intra
    # Só processa se msc_encerr não estiver vazio (empenhado MSC encerr.: contas 622130… + natureza preenchida)
    if (
        not msc_encerr.empty
        and 'tipo_valor' in msc_encerr.columns
        and 'natureza_despesa' in msc_encerr.columns
    ):
        _tb_e = msc_encerr['tipo_valor'] == 'beginning_balance'
        _cc_e = msc_encerr['conta_contabil'].astype(str).isin([
            '622130100', '622130200', '622130300', '622130400',
            '622130500', '622130600', '622130700',
        ])
        _nd_e = msc_encerr['natureza_despesa']
        _nd_ok_e = _nd_e.notna() & (_nd_e.astype(str).str.strip() != '')
        emp_msc_encerr = msc_encerr.loc[_tb_e & _cc_e & _nd_ok_e].copy()
        if not emp_msc_encerr.empty:
            emp_msc_encerr['DIGITO_INTRA'] = emp_msc_encerr['natureza_despesa'].apply(extrair_terceiro_quarto_digito)
    else:
        emp_msc_encerr = pd.DataFrame()

    # Base específica de RP da MSC de encerramento (beginning_balance)
    # para cruzamentos com DCA Anexo I-G (D2_00101 a D2_00105).
    if not msc_encerr.empty and {'tipo_valor', 'conta_contabil'}.issubset(msc_encerr.columns):
        rp_encerramento = msc_encerr.query('tipo_valor == "beginning_balance"').copy()
        rp_encerramento = rp_encerramento[
            rp_encerramento['conta_contabil'].astype(str).str.match(r'^(6313|6314|6319|6322|6329)')
        ].copy()
        # A função deve vir da própria matriz (mesmo padrão usado nas D2 já existentes).
        if 'funcao' not in rp_encerramento.columns:
            rp_encerramento['funcao'] = ''

        # DIGITO_INTRA é derivado da natureza da despesa para separar intra vs exceto-intra.
        if 'natureza_despesa' in rp_encerramento.columns:
            rp_encerramento['DIGITO_INTRA'] = rp_encerramento['natureza_despesa'].apply(extrair_terceiro_quarto_digito)
        elif 'DIGITO_INTRA' not in rp_encerramento.columns:
            rp_encerramento['DIGITO_INTRA'] = ''
    else:
        rp_encerramento = pd.DataFrame()

    # Só processa se msc_orig_encerr não estiver vazio
    if not msc_orig_encerr.empty and 'tipo_valor' in msc_orig_encerr.columns:
        msc_orig_encerr_b = msc_orig_encerr.query('tipo_valor == "beginning_balance"')
        msc_orig_encerr_e = msc_orig_encerr.query('tipo_valor == "ending_balance"')
    else:
        msc_orig_encerr_b = pd.DataFrame()
        msc_orig_encerr_e = pd.DataFrame()
    
    
    # Criando uma junção dos Saldos Finais das matrizes de JAN a DEZ e a de Saldo Inicial da matriz de encerramento
    msc_original_e_b_p_13 = pd.concat([msc_orig_e, msc_orig_encerr_b], ignore_index=True)
    
    # Criando Grupo de Contas
    msc_consolidada["Grupo_Contas"] = msc_consolidada["conta_contabil"].str[0]
    
    # Aplicando a fórmula para trocar o sinal do period_change
    msc_consolidada['valor'] = msc_consolidada.apply(lambda x: x['valor'] * -1
    if (x['Grupo_Contas'] == '1' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '2' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '3' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '4' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '5' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '6' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '7' and x['natureza_conta'] == 'C' and x['tipo_valor'] == 'period_change')
    or (x['Grupo_Contas'] == '8' and x['natureza_conta'] == 'D' and x['tipo_valor'] == 'period_change')
    else x['valor'], axis=1)
    
    # Condição para selecionar as linhas onde 'mes_referencia' é 12 e 'tipo_matriz' é 'MSCE'
    condicao_alt_msc = (msc_consolidada['mes_referencia'] == 12) & (msc_consolidada['tipo_matriz'] == 'MSCE')
    # Substituir o valor de 'mes_referencia' para 13 nas linhas selecionadas
    msc_consolidada.loc[condicao_alt_msc, 'mes_referencia'] = 13

    msc_consolidada_sem_msc_encerr = msc_consolidada.query('tipo_matriz != "MSCE"')
    
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################

    #############################################################################
    #                         DIMENSÃO D1 - MSC                                 #
    #############################################################################
    #############################################################################

    if ano < 2024:
        d1_00017, d1_00017_t = d1_analysis.d1_00017(msc_orig_consolidada)
        d1_00018, d1_00018_t = d1_analysis.d1_00018(msc_orig_consolidada)
    else:
        d1_00017 = None
        d1_00017_t = pd.DataFrame()
        resposta_d1_00017 = 'N/A'
        d1_00018 = None
        d1_00018_t = pd.DataFrame()
        resposta_d1_00018 = 'N/A'
    d1_00019, d1_00019_t = d1_analysis.d1_00019(msc_orig_consolidada, ano, tipo_ente)
    d1_00020, d1_00020_t = d1_analysis.d1_00020(msc_orig_consolidada)
    d1_00021, d1_00021_t, pc_estendido = d1_analysis.d1_00021(msc_consolidada, ano)
    d1_00022, d1_00022_t = d1_analysis.d1_00022(msc_consolidada)
    d1_00023, d1_00023_t = d1_analysis.d1_00023(msc_consolidada, tipo_ente)
    d1_00024, d1_00024_t = d1_analysis.d1_00024(msc_consolidada, tipo_ente)
    d1_00025, d1_00025_t, pc_estendido = d1_analysis.d1_00025(msc_consolidada, pc_estendido)
    d1_00026, d1_00026_t = d1_analysis.d1_00026(msc_consolidada, pc_estendido)
    d1_00027, d1_00027_t = d1_analysis.d1_00027(msc_consolidada)
    d1_00028, d1_00028_t = d1_analysis.d1_00028(msc_consolidada)
    d1_00029, d1_00029_t = d1_analysis.d1_00029(msc_consolidada)
    d1_00030, d1_00030_t = d1_analysis.d1_00030(msc_consolidada)
    d1_00031, d1_00031_t = d1_analysis.d1_00031(msc_consolidada)
    d1_00032, d1_00032_t = d1_analysis.d1_00032(msc_consolidada)
    d1_00033, d1_00033_t = d1_analysis.d1_00033(msc_consolidada)
    d1_00034, d1_00034_t = d1_analysis.d1_00034(msc_consolidada_e, pc_estendido)
    d1_00035, d1_00035_t = d1_analysis.d1_00035(msc_consolidada_e, pc_estendido)
    d1_00036, d1_00036_t = d1_analysis.d1_00036(msc_encerr, disponibilidade)
    d1_00037, d1_00037_t = d1_analysis.d1_00037(msc_consolidada_e)
    d1_00038, d1_00038_ta, d1_00038_det = d1_analysis.d1_00038(msc_orig_e, pc_estendido)
    d1_00039, d1_00039_t = d1_analysis.d1_00039(msc_consolidada)
    d1_00040, d1_00040_t = d1_analysis.d1_00040(msc_consolidada)
    d1_00044, d1_00044_t = d1_analysis.d1_00044(msc_consolidada)
    d1_00041, d1_00041_dados, d1_00041_detalhe = d1_analysis.d1_00041(msc_consolidada)
    d1_00042, d1_00042_dados, d1_00042_detalhe = d1_analysis.d1_00042(msc_consolidada)
    d1_00043, d1_00043_dados, d1_00043_detalhe = d1_analysis.d1_00043(msc_consolidada)

    if d1_00017 is not None:
        resposta_d1_00017 = d1_00017['Resposta'].iloc[0]
    if d1_00018 is not None:
        resposta_d1_00018 = d1_00018['Resposta'].iloc[0]
    resposta_d1_00019 = d1_00019['Resposta'].iloc[0]
    resposta_d1_00020 = d1_00020['Resposta'].iloc[0]
    resposta_d1_00021 = d1_00021['Resposta'].iloc[0]
    resposta_d1_00022 = d1_00022['Resposta'].iloc[0]
    resposta_d1_00023 = d1_00023['Resposta'].iloc[0]
    resposta_d1_00024 = d1_00024['Resposta'].iloc[0]
    resposta_d1_00025 = d1_00025['Resposta'].iloc[0]
    resposta_d1_00026 = d1_00026['Resposta'].iloc[0]
    resposta_d1_00027 = d1_00027['Resposta'].iloc[0]
    resposta_d1_00028 = d1_00028['Resposta'].iloc[0]
    resposta_d1_00029 = d1_00029['Resposta'].iloc[0]
    resposta_d1_00030 = d1_00030['Resposta'].iloc[0]
    resposta_d1_00031 = d1_00031['Resposta'].iloc[0]
    resposta_d1_00032 = d1_00032['Resposta'].iloc[0]
    resposta_d1_00033 = d1_00033['Resposta'].iloc[0]
    resposta_d1_00034 = d1_00034['Resposta'].iloc[0]
    resposta_d1_00035 = d1_00035['Resposta'].iloc[0]
    resposta_d1_00036 = d1_00036['Resposta'].iloc[0]
    resposta_d1_00037 = d1_00037['Resposta'].iloc[0]
    resposta_d1_00038 = d1_00038['Resposta'].iloc[0]
    resposta_d1_00039 = d1_00039['Resposta'].iloc[0]
    resposta_d1_00040 = d1_00040['Resposta'].iloc[0]
    resposta_d1_00044 = d1_00044['Resposta'].iloc[0]
    resposta_d1_00041 = d1_00041['Resposta'].iloc[0]
    resposta_d1_00042 = d1_00042['Resposta'].iloc[0]
    resposta_d1_00043 = d1_00043['Resposta'].iloc[0]



    #############################################################################
    #      DIMENSÃO D2 ANTECIPADA - ANÁLISE PRÉVIA PELA MATRIZ (MSC)           #
    #############################################################################
    #############################################################################
    d2_antecipada, d2_ant_00002, d2_ant_00002_t, resposta_d2_ant_00002, ultimo_mes_msc, executar_d2_ant = (
        d2_ant_analysis.run_d2_antecipada(msc_consolidada, meses, disponibilidade)
    )


    #############################################################################
    #                         DIMENSÃO D2 - DCA                                 #
    #############################################################################
    #############################################################################

    # Verificar disponibilidade dos demonstrativos usados na D2
    dca_disponivel_d2 = disponibilidade.get('dca', {}).get('disponivel', False)
    msc_disponivel_d2 = disponibilidade.get('msc', {}).get('disponivel', False)
    msce_disponivel_d2 = disponibilidade.get('msc_encerramento', {}).get('disponivel', False)
    executar_d2 = dca_disponivel_d2 or msc_disponivel_d2 or msce_disponivel_d2

    def criar_d2_na(codigo, descricao, obs='DCA não disponível para este exercício'):
        return pd.DataFrame([{
            'Dimensão': codigo,
            'Resposta': 'N/A',
            'Descrição da Dimensão': descricao,
            'Nota': None,
            'OBS': obs
        }])

    # Inicializar todas as variáveis D2 com N/A; os blocos de execução abaixo
    # sobrescrevem apenas as verificações que puderem ser calculadas.
    if True:
        d2_00002 = criar_d2_na('D2_00002', 'Valor de VPD do FUNDEB informado')
        d2_00003 = criar_d2_na('D2_00003', 'Deduções de receita do FUNDEB informadas')
        d2_00004 = criar_d2_na('D2_00004', 'Receitas do FUNDEB informadas')
        d2_00005 = criar_d2_na('D2_00005', 'Obrigações Patronais informadas')
        d2_00006 = criar_d2_na('D2_00006', 'Despesas com Pessoal informadas')
        d2_00007 = criar_d2_na('D2_00007', 'Passivo Atuarial informado')
        d2_00008 = criar_d2_na('D2_00008', 'VPD de Depreciação informado')
        d2_00010 = criar_d2_na('D2_00010', 'Investimentos informados')
        d2_00011 = criar_d2_na('D2_00011', 'Inversões Financeiras informadas')
        d2_00012 = criar_d2_na('D2_00012', 'Amortização de Dívida informada')
        d2_00013 = criar_d2_na('D2_00013', 'Verificação de Ativo x Passivo')
        d2_00014 = criar_d2_na('D2_00014', 'Verificação de VPA x VPD')
        d2_00015 = criar_d2_na('D2_00015', 'Verificação DCA I-AB x I-C')
        d2_00016 = criar_d2_na('D2_00016', 'Verificação DCA I-AB x I-D')
        d2_00017 = criar_d2_na('D2_00017', 'Verificação DCA I-C x I-D')
        d2_00018 = criar_d2_na('D2_00018', 'Verificação DCA I-E x I-D')
        d2_00019 = criar_d2_na('D2_00019', 'Verificação DCA I-F x I-D')
        d2_00020 = criar_d2_na('D2_00020', 'Verificação DCA I-G x I-D')
        d2_00021 = criar_d2_na('D2_00021', 'Verificação de Restos a Pagar')
        d2_00023 = criar_d2_na('D2_00023', 'Verificação MSC x DCA Receita')
        d2_00024 = criar_d2_na('D2_00024', 'Verificação MSC x DCA Despesa')
        d2_00028 = criar_d2_na('D2_00028', 'Verificação MSC x DCA Ativo')
        d2_00029 = criar_d2_na('D2_00029', 'Verificação MSC x DCA Passivo')
        d2_00030 = criar_d2_na('D2_00030', 'Verificação MSC x DCA VPA')
        d2_00031 = criar_d2_na('D2_00031', 'Verificação MSC x DCA VPD')
        d2_00032 = criar_d2_na('D2_00032', 'Verificação MSC x DCA Resultado')
        d2_00033 = criar_d2_na('D2_00033', 'Caixa e Equivalentes informados')
        d2_00034 = criar_d2_na('D2_00034', 'Verificação DCA Receita Intra')
        d2_00035 = criar_d2_na('D2_00035', 'Verificação DCA Despesa Intra')
        d2_00036 = criar_d2_na('D2_00036', 'Verificação MSCE x DCA')
        d2_00037 = criar_d2_na('D2_00037', 'Verificação MSCE x DCA Patrimônio')
        d2_00038 = criar_d2_na('D2_00038', 'Créditos Previdenciários a Receber')
        d2_00039 = criar_d2_na('D2_00039', 'Verificação DCA x RREO Receita')
        d2_00040 = criar_d2_na('D2_00040', 'Verificação DCA x RREO Despesa')
        d2_00044 = criar_d2_na('D2_00044', 'Receita Realizada MSC x DCA')
        d2_00045 = criar_d2_na('D2_00045', 'Receita de Impostos Estaduais MSC x DCA')
        d2_00046 = criar_d2_na('D2_00046', 'Receita de Impostos Municipais MSC x DCA')
        d2_00047 = criar_d2_na('D2_00047', 'Transferências Constitucionais Estaduais MSC x DCA')
        d2_00048 = criar_d2_na('D2_00048', 'Transferências Constitucionais Municipais MSC x DCA')
        d2_00049 = criar_d2_na('D2_00049', 'Despesas Orçamentárias MSC x DCA')
        d2_00050 = criar_d2_na('D2_00050', 'Restos a Pagar MSC x DCA')
        d2_00051 = criar_d2_na('D2_00051', 'Ajuste para perdas em Estoques (DCA)')
        d2_00052 = criar_d2_na('D2_00052', 'Equivalência Patrimonial (DCA)')
        d2_00053 = criar_d2_na('D2_00053', 'Ajuste para perdas em Estoques (MSC Encerramento)')
        d2_00054 = criar_d2_na('D2_00054', 'Investimentos permanentes (MSC Encerramento)')
        d2_00055 = criar_d2_na('D2_00055', 'Amortização de ativos intangíveis (MSC Encerramento)')
        d2_00058 = criar_d2_na('D2_00058', 'VPA FUNDEB (MSC x DCA)')
        d2_00059 = criar_d2_na('D2_00059', 'Ajuste perdas - Créditos CP/LP (MSC Encerramento)')
        d2_00060 = criar_d2_na('D2_00060', 'Ajuste perdas - Demais créditos CP/LP (MSC Encerramento)')
        d2_00061 = criar_d2_na('D2_00061', 'VPA FUNDEB informada (DCA)')
        d2_00066 = criar_d2_na('D2_00066', 'Amortização de intangíveis (DCA)')
        d2_00067 = criar_d2_na('D2_00067', 'Depreciação bens móveis (MSC Encerramento)')
        d2_00068 = criar_d2_na('D2_00068', 'Depreciação bens imóveis (MSC Encerramento)')
        d2_00069 = criar_d2_na('D2_00069', 'Despesas função 09 (MSC Encerramento x DCA E)')
        d2_00070 = criar_d2_na('D2_00070', 'Despesas função 10 (MSC Encerramento x DCA E)')
        d2_00071 = criar_d2_na('D2_00071', 'Despesas função 12 (MSC Encerramento x DCA E)')
        d2_00072 = criar_d2_na('D2_00072', 'Despesas demais funções (MSC Encerramento x DCA E)')
        d2_00073 = criar_d2_na('D2_00073', 'Despesas intraorçamentárias (MSC Encerramento x DCA E)')
        d2_00074 = criar_d2_na('D2_00074', 'RPPP/RPNPP Pagos (MSC Encerramento x DCA F)')
        d2_00076 = criar_d2_na('D2_00076', 'Créditos previdenciários parcelados — VPA juros x ativo (MSC Encerramento)')
        d2_00077 = criar_d2_na('D2_00077', 'Comparativo saldo contas 227/228 (MSC Jan/Dez)')
        d2_00079 = criar_d2_na('D2_00079', 'Comparativo saldo contas 119 (MSC Jan/Dez)')
        d2_00080 = criar_d2_na('D2_00080', 'Saldo contas 1156 em todos os meses (MSC)')
        d2_00081 = criar_d2_na('D2_00081', 'Movimento credor contas 2.1.1.1.1.01.02/03 (MSC)')
        d2_00082 = criar_d2_na('D2_00082', 'Movimento credor contas 1.2.3.8.1.01/03/05 (MSC)')
        d2_00083 = criar_d2_na('D2_00083', 'Integridade DDR — saldos finais 721 = 821 (MSC Dezembro)')
        d2_00084 = criar_d2_na('D2_00084', 'CAPAG — Passivo Financeiro + Permanente (DCA AB) ≥ Passivo Circulante + Não Circulante (MSC Dezembro)')
        d2_00085 = criar_d2_na('D2_00085', 'CAPAG — Passivo Financeiro + Permanente (DCA AB) ≥ Passivo Circulante + Não Circulante (DCA AB)')
        d2_00086 = criar_d2_na('D2_00086', 'VPD com material de consumo em todos os meses — contas 3311 (MSC)')
        d2_00087 = criar_d2_na('D2_00087', 'VPD com serviços em todos os meses — contas 332 (MSC)')
        d2_00088 = criar_d2_na('D2_00088', 'VPD com transferências intergovernamentais em todos os meses — contas 352 (MSC)')
        d2_00093 = criar_d2_na('D2_00093', 'Movimento credor contas grupo 11561 — almoxarifado (MSC)')
        d2_00094 = criar_d2_na('D2_00094', 'Despesas previdenciárias RPPS — saldo final contas 3.1.1.1.1.01.01 e 3.1.2.1.2.01.00 (MSC Dezembro)')
        d2_00095 = criar_d2_na('D2_00095', 'Despesas previdenciárias RGPS — saldo final contas 3.1.1.2.1.01.01, 3.1.2.2.1.01.00 e 3.1.2.2.3.01.00 (MSC Dezembro)')
        d2_00089 = criar_d2_na('D2_00089', 'Verificar VPD de Variações Monetárias e Cambiais Externas quando houver obrigações de empréstimos e financiamentos externos')
        d2_00099 = criar_d2_na('D2_00099', 'Avalia a informação de deduções com transferências constitucionais por municípios')
        d2_00100 = criar_d2_na('D2_00100', 'Redução ao valor recuperável (investimentos, imobilizado e intangível) — VPD x Ativo (DCA HI x DCA AB)')
        d2_00101 = criar_d2_na('D2_00101', 'RP função 10 Saúde (MSC Encerramento x DCA G)')
        d2_00102 = criar_d2_na('D2_00102', 'RP função 12 Educação (MSC Encerramento x DCA G)')
        d2_00103 = criar_d2_na('D2_00103', 'RP função 09 Previdência Social (MSC Encerramento x DCA G)')
        d2_00104 = criar_d2_na('D2_00104', 'RP demais funções exceto 09/10/12 (MSC Encerramento x DCA G)')
        d2_00105 = criar_d2_na('D2_00105', 'RP intraorçamentário (MSC Encerramento x DCA G)')

        # Criar tabelas vazias para os detalhamentos
        d2_00002_t = pd.DataFrame()
        d2_00003_t = pd.DataFrame()
        d2_00004_t = pd.DataFrame()
        d2_00005_t = pd.DataFrame()
        d2_00006_t = pd.DataFrame()
        d2_00007_t = pd.DataFrame()
        d2_00008_t = pd.DataFrame()
        d2_00010_t = pd.DataFrame()
        d2_00011_t = pd.DataFrame()
        d2_00012_t = pd.DataFrame()
        d2_00012_ta = pd.DataFrame()  # Tabela auxiliar para D2_00012
        d2_00013_t = pd.DataFrame()
        d2_00014_t = pd.DataFrame()
        d2_00015_t = pd.DataFrame()
        d2_00016_t = pd.DataFrame()
        d2_00017_t = pd.DataFrame()
        d2_00018_t = pd.DataFrame()
        d2_00019_t = pd.DataFrame()
        d2_00020_t = pd.DataFrame()
        d2_00021_t = pd.DataFrame()
        d2_00023_t = pd.DataFrame()
        d2_00024_t = pd.DataFrame()
        d2_00028_t = pd.DataFrame()
        d2_00029_t = pd.DataFrame()
        d2_00030_t = pd.DataFrame()
        d2_00031_t = pd.DataFrame()
        d2_00032_t = pd.DataFrame()
        d2_00033_t = pd.DataFrame()
        d2_00034_t = pd.DataFrame()
        d2_00035_t = pd.DataFrame()
        d2_00036_t = pd.DataFrame()
        d2_00037_t = pd.DataFrame()
        d2_00039_t = pd.DataFrame()
        d2_00040_t = pd.DataFrame()
        d2_00038_t = pd.DataFrame()
        d2_00044_t = pd.DataFrame()
        d2_00045_t = pd.DataFrame()
        d2_00046_t = pd.DataFrame()
        d2_00047_t = pd.DataFrame()
        d2_00048_t = pd.DataFrame()
        d2_00049_t = pd.DataFrame()
        d2_00050_t = pd.DataFrame()
        d2_00051_t = pd.DataFrame()
        d2_00052_t = pd.DataFrame()
        d2_00053_t = pd.DataFrame()
        d2_00054_t = pd.DataFrame()
        d2_00055_t = pd.DataFrame()
        d2_00058_t = pd.DataFrame()
        d2_00059_t = pd.DataFrame()
        d2_00060_t = pd.DataFrame()
        d2_00061_t = pd.DataFrame()
        d2_00066_t = pd.DataFrame()
        d2_00067_t = pd.DataFrame()
        d2_00068_t = pd.DataFrame()
        d2_00069_t = pd.DataFrame()
        d2_00070_t = pd.DataFrame()
        d2_00071_t = pd.DataFrame()
        d2_00072_t = pd.DataFrame()
        d2_00073_t = pd.DataFrame()
        d2_00074_t = pd.DataFrame()
        d2_00076_t = pd.DataFrame()
        d2_00077_t = pd.DataFrame()
        d2_00079_t = pd.DataFrame()
        d2_00080_t = pd.DataFrame()
        d2_00081_t = pd.DataFrame()
        d2_00082_t = pd.DataFrame()
        d2_00083_t = pd.DataFrame()
        d2_00084_t = pd.DataFrame()
        d2_00085_t = pd.DataFrame()
        d2_00086_t = pd.DataFrame()
        d2_00087_t = pd.DataFrame()
        d2_00088_t = pd.DataFrame()
        d2_00093_t = pd.DataFrame()
        d2_00094_t = pd.DataFrame()
        d2_00095_t = pd.DataFrame()
        d2_00089_t = pd.DataFrame()
        d2_00099_t = pd.DataFrame()
        d2_00100_t = pd.DataFrame()
        d2_00101_t = pd.DataFrame()
        d2_00102_t = pd.DataFrame()
        d2_00103_t = pd.DataFrame()
        d2_00104_t = pd.DataFrame()
        d2_00105_t = pd.DataFrame()

        # Respostas N/A
        resposta_d2_00002 = 'N/A'; resposta_d2_00003 = 'N/A'; resposta_d2_00004 = 'N/A'
        resposta_d2_00005 = 'N/A'; resposta_d2_00006 = 'N/A'; resposta_d2_00007 = 'N/A'
        resposta_d2_00008 = 'N/A'; resposta_d2_00010 = 'N/A'; resposta_d2_00011 = 'N/A'
        resposta_d2_00012 = 'N/A'; resposta_d2_00013 = 'N/A'; resposta_d2_00014 = 'N/A'
        resposta_d2_00015 = 'N/A'; resposta_d2_00016 = 'N/A'; resposta_d2_00017 = 'N/A'
        resposta_d2_00018 = 'N/A'; resposta_d2_00019 = 'N/A'; resposta_d2_00020 = 'N/A'
        resposta_d2_00021 = 'N/A'; resposta_d2_00023 = 'N/A'; resposta_d2_00024 = 'N/A'
        resposta_d2_00028 = 'N/A'; resposta_d2_00029 = 'N/A'; resposta_d2_00030 = 'N/A'
        resposta_d2_00031 = 'N/A'; resposta_d2_00032 = 'N/A'; resposta_d2_00033 = 'N/A'
        resposta_d2_00034 = 'N/A'; resposta_d2_00035 = 'N/A'; resposta_d2_00036 = 'N/A'
        resposta_d2_00037 = 'N/A'; resposta_d2_00038 = 'N/A'; resposta_d2_00039 = 'N/A'
        resposta_d2_00040 = 'N/A'; resposta_d2_00044 = 'N/A'; resposta_d2_00045 = 'N/A'
        resposta_d2_00046 = 'N/A'; resposta_d2_00047 = 'N/A'; resposta_d2_00048 = 'N/A'
        resposta_d2_00049 = 'N/A'; resposta_d2_00050 = 'N/A'
        resposta_d2_00051 = 'N/A'; resposta_d2_00052 = 'N/A'; resposta_d2_00053 = 'N/A'
        resposta_d2_00054 = 'N/A'; resposta_d2_00055 = 'N/A'
        resposta_d2_00058 = 'N/A'; resposta_d2_00059 = 'N/A'; resposta_d2_00060 = 'N/A'
        resposta_d2_00061 = 'N/A'; resposta_d2_00066 = 'N/A'
        resposta_d2_00067 = 'N/A'; resposta_d2_00068 = 'N/A'; resposta_d2_00069 = 'N/A'
        resposta_d2_00070 = 'N/A'
        resposta_d2_00071 = 'N/A'; resposta_d2_00072 = 'N/A'; resposta_d2_00073 = 'N/A'
        resposta_d2_00074 = 'N/A'
        resposta_d2_00076 = 'N/A'
        resposta_d2_00077 = 'N/A'; resposta_d2_00079 = 'N/A'; resposta_d2_00080 = 'N/A'
        resposta_d2_00081 = 'N/A'; resposta_d2_00082 = 'N/A'; resposta_d2_00083 = 'N/A'; resposta_d2_00084 = 'N/A'; resposta_d2_00085 = 'N/A'
        resposta_d2_00086 = 'N/A'; resposta_d2_00087 = 'N/A'; resposta_d2_00088 = 'N/A'
        resposta_d2_00093 = 'N/A'
        resposta_d2_00094 = 'N/A'
        resposta_d2_00095 = 'N/A'
        resposta_d2_00089 = 'N/A'
        resposta_d2_00099 = 'N/A'
        resposta_d2_00100 = 'N/A'
        resposta_d2_00101 = 'N/A'
        resposta_d2_00102 = 'N/A'
        resposta_d2_00103 = 'N/A'
        resposta_d2_00104 = 'N/A'
        resposta_d2_00105 = 'N/A'

        # Variáveis auxiliares para condições específicas
        condicao_negativa_cp = False
        condicao_negativa_lp = False
        condicao_negativa = False
        diferencas_cp = []
        dif_cred_lp = 0
        diferenca_passivo = 0
        emprest = pd.DataFrame()
        vpd_juros = pd.DataFrame()

    ############################################
    #########  PARTE QUE EXECUTA A D2  #########
    ############################################

    if executar_d2:
        # Bloco 1: verificações que dependem da DCA
        if dca_disponivel_d2:
            d2_00002, d2_00002_t = d2_dca_analysis.d2_00002(df_dca_hi)
            d2_00003, d2_00003_t = d2_dca_analysis.d2_00003(df_dca_c)
            d2_00004, d2_00004_t = d2_dca_analysis.d2_00004(df_dca_c, ano)
            d2_00005, d2_00005_t = d2_dca_analysis.d2_00005(df_dca_d)
            d2_00006, d2_00006_t = d2_dca_analysis.d2_00006(df_dca_d)
            d2_00007, d2_00007_t = d2_dca_analysis.d2_00007(df_dca_d)
            d2_00008, d2_00008_t = d2_dca_analysis.d2_00008(df_dca_e)

            resposta_d2_00002 = d2_00002['Resposta'].iloc[0]
            resposta_d2_00003 = d2_00003['Resposta'].iloc[0]
            resposta_d2_00004 = d2_00004['Resposta'].iloc[0]
            resposta_d2_00005 = d2_00005['Resposta'].iloc[0]
            resposta_d2_00006 = d2_00006['Resposta'].iloc[0]
            resposta_d2_00007 = d2_00007['Resposta'].iloc[0]
            resposta_d2_00008 = d2_00008['Resposta'].iloc[0]

            d2_00010, d2_00010_t = d2_dca_analysis.d2_00010(df_dca_c)
            d2_00011, d2_00011_t = d2_dca_analysis.d2_00011(df_dca_c)
            d2_00012, d2_00012_t, d2_00012_ta = d2_dca_analysis.d2_00012(df_dca_c)
            d2_00013, d2_00013_t, condicao_negativa_cp, condicao_negativa_lp, diferencas_cp = (
                d2_dca_analysis.d2_00013(df_dca_ab)
            )
            d2_00014, d2_00014_t, condicao_negativa = d2_dca_analysis.d2_00014(df_dca_ab)
            d2_00015, d2_00015_t = d2_dca_analysis.d2_00015(df_dca_ab)
            d2_00016, d2_00016_t = d2_dca_analysis.d2_00016(df_dca_ab)
            d2_00017, d2_00017_t = d2_dca_analysis.d2_00017(df_dca_hi)
            d2_00018, d2_00018_t = d2_dca_analysis.d2_00018(df_dca_ab)
            d2_00019, d2_00019_t = d2_dca_analysis.d2_00019(df_dca_ab)
            d2_00020, d2_00020_t = d2_dca_analysis.d2_00020(df_dca_ab)
            d2_00021, d2_00021_t = d2_dca_analysis.d2_00021(df_dca_ab)

            resposta_d2_00010 = d2_00010['Resposta'].iloc[0]
            resposta_d2_00011 = d2_00011['Resposta'].iloc[0]
            resposta_d2_00012 = d2_00012['Resposta'].iloc[0]
            resposta_d2_00013 = d2_00013['Resposta'].iloc[0]
            resposta_d2_00014 = d2_00014['Resposta'].iloc[0]
            resposta_d2_00015 = d2_00015['Resposta'].iloc[0]
            resposta_d2_00016 = d2_00016['Resposta'].iloc[0]
            resposta_d2_00017 = d2_00017['Resposta'].iloc[0]
            resposta_d2_00018 = d2_00018['Resposta'].iloc[0]
            resposta_d2_00019 = d2_00019['Resposta'].iloc[0]
            resposta_d2_00020 = d2_00020['Resposta'].iloc[0]
            resposta_d2_00021 = d2_00021['Resposta'].iloc[0]

            d2_00023, d2_00023_t = d2_dca_analysis.d2_00023(df_dca_d)
            d2_00024, d2_00024_t = d2_dca_analysis.d2_00024(df_dca_d)
            d2_00028, d2_00028_t, valor_pass_circ, valor_pass_circ_fin, diferenca_passivo = d2_dca_analysis.d2_00028(df_dca_ab)
            d2_00029, d2_00029_t, vpd_juros, emprest = d2_dca_analysis.d2_00029(df_dca_hi, df_dca_ab)
            d2_00030, d2_00030_t = d2_dca_analysis.d2_00030(df_dca_ab)
            d2_00031, d2_00031_t = d2_dca_analysis.d2_00031(df_dca_hi)
            d2_00032, d2_00032_t = d2_dca_analysis.d2_00032(df_dca_ab)
            d2_00033, d2_00033_t = d2_dca_analysis.d2_00033(df_dca_c, tipo_ente)
            if ano >= 2024 and tipo_ente == "M":
                d2_00099, d2_00099_t = d2_dca_analysis.d2_00099(df_dca_c)
                resposta_d2_00099 = d2_00099['Resposta'].iloc[0]
            else:
                d2_00099 = criar_d2_na(
                    'D2_00099',
                    'Avalia a informação de deduções com transferências constitucionais por municípios',
                    'Aplicável somente a municípios a partir de 2024 (metodologia STN/CAPAG)',
                )
                d2_00099_t = pd.DataFrame()
                resposta_d2_00099 = 'N/A'
            d2_00034, d2_00034_t = d2_dca_analysis.d2_00034(df_dca_hi)
            d2_00035, d2_00035_t = d2_dca_analysis.d2_00035(df_dca_c_orig)
            d2_00036, d2_00036_t = d2_dca_analysis.d2_00036(df_dca_ab, df_dca_hi)
            d2_00037, d2_00037_t = d2_dca_analysis.d2_00037(df_dca_hi)
            d2_00039, d2_00039_t = d2_dca_analysis.d2_00039(df_dca_ab, df_dca_hi)
            d2_00040, d2_00040_t = d2_dca_analysis.d2_00040(df_dca_ab_orig)

            resposta_d2_00023 = d2_00023['Resposta'].iloc[0]
            resposta_d2_00024 = d2_00024['Resposta'].iloc[0]
            resposta_d2_00028 = d2_00028['Resposta'].iloc[0]
            resposta_d2_00029 = d2_00029['Resposta'].iloc[0]
            resposta_d2_00030 = d2_00030['Resposta'].iloc[0]
            resposta_d2_00031 = d2_00031['Resposta'].iloc[0]
            resposta_d2_00032 = d2_00032['Resposta'].iloc[0]
            resposta_d2_00033 = d2_00033['Resposta'].iloc[0]
            resposta_d2_00034 = d2_00034['Resposta'].iloc[0]
            resposta_d2_00035 = d2_00035['Resposta'].iloc[0]
            resposta_d2_00036 = d2_00036['Resposta'].iloc[0]
            resposta_d2_00037 = d2_00037['Resposta'].iloc[0]
            resposta_d2_00039 = d2_00039['Resposta'].iloc[0]
            resposta_d2_00040 = d2_00040['Resposta'].iloc[0]

            if ano == 2023:
                d2_00038, d2_00038_t = d2_dca_analysis.d2_00038(df_dca_ab, ano)
                resposta_d2_00038 = d2_00038['Resposta'].iloc[0]
            else:
                d2_00038 = criar_d2_na('D2_00038', 'Créditos Previdenciários a Receber', 'Aplicável somente em 2023')
                d2_00038_t = pd.DataFrame()
                resposta_d2_00038 = 'N/A'

            d2_00051, d2_00051_t = d2_dca_analysis.d2_00051(df_dca_ab)
            resposta_d2_00051 = d2_00051['Resposta'].iloc[0]

            d2_00052, d2_00052_t = d2_dca_analysis.d2_00052(df_dca_ab, df_dca_hi)
            resposta_d2_00052 = d2_00052['Resposta'].iloc[0]
            if ano >= 2024:
                d2_00089, d2_00089_t = d2_dca_analysis.d2_00089(df_dca_ab, df_dca_hi)
                resposta_d2_00089 = d2_00089['Resposta'].iloc[0]
            else:
                d2_00089 = criar_d2_na(
                    'D2_00089',
                    'Verificar VPD de Variações Monetárias e Cambiais Externas quando houver obrigações de empréstimos e financiamentos externos',
                    'Aplicável somente a partir de 2024 (metodologia STN/CAPAG)',
                )
                d2_00089_t = pd.DataFrame()
                resposta_d2_00089 = 'N/A'

            if ano >= 2025:
                d2_00100, d2_00100_t = d2_dca_analysis.d2_00100(df_dca_hi, df_dca_ab)
                resposta_d2_00100 = d2_00100['Resposta'].iloc[0]
            else:
                d2_00100 = criar_d2_na(
                    'D2_00100',
                    'Redução ao valor recuperável (investimentos, imobilizado e intangível) — VPD x Ativo (DCA HI x DCA AB)',
                    'Aplicável somente a partir de 2025 (metodologia STN — E/DF/M)',
                )
                d2_00100_t = pd.DataFrame()
                resposta_d2_00100 = 'N/A'

            d2_00061, d2_00061_t = d2_dca_analysis.d2_00061(df_dca_hi)
            resposta_d2_00061 = d2_00061['Resposta'].iloc[0]

            d2_00066, d2_00066_t = d2_dca_analysis.d2_00066(df_dca_ab)
            resposta_d2_00066 = d2_00066['Resposta'].iloc[0]

            if ano >= 2023:
                d2_00085, d2_00085_t = d2_dca_analysis.d2_00085(df_dca_ab)
                resposta_d2_00085 = d2_00085['Resposta'].iloc[0]
            else:
                d2_00085 = criar_d2_na(
                    'D2_00085',
                    'CAPAG — Passivo Financeiro + Permanente (DCA AB) ≥ Passivo Circulante + Não Circulante (DCA AB)',
                    'Aplicável somente a partir de 2023 (metodologia STN/CAPAG — E/DF/M)',
                )
                d2_00085_t = pd.DataFrame()
                resposta_d2_00085 = 'N/A'
        else:
            obs_dca = 'DCA não disponível — verificação exige o Balanço Anual'
            for codigo, descricao in [
                ('D2_00002', 'Valor de VPD do FUNDEB informado'),
                ('D2_00003', 'Deduções de receita do FUNDEB informadas'),
                ('D2_00004', 'Receitas do FUNDEB informadas'),
                ('D2_00005', 'Obrigações Patronais informadas'),
                ('D2_00006', 'Despesas com Pessoal informadas'),
                ('D2_00007', 'Passivo Atuarial informado'),
                ('D2_00008', 'VPD de Depreciação informado'),
                ('D2_00010', 'Investimentos informados'),
                ('D2_00011', 'Inversões Financeiras informadas'),
                ('D2_00012', 'Amortização de Dívida informada'),
                ('D2_00013', 'Verificação de Ativo x Passivo'),
                ('D2_00014', 'Verificação de VPA x VPD'),
                ('D2_00015', 'Verificação DCA I-AB x I-C'),
                ('D2_00016', 'Verificação DCA I-AB x I-D'),
                ('D2_00017', 'Verificação DCA I-C x I-D'),
                ('D2_00018', 'Verificação DCA I-E x I-D'),
                ('D2_00019', 'Verificação DCA I-F x I-D'),
                ('D2_00020', 'Verificação DCA I-G x I-D'),
                ('D2_00021', 'Verificação de Restos a Pagar'),
                ('D2_00023', 'Verificação MSC x DCA Receita'),
                ('D2_00024', 'Verificação MSC x DCA Despesa'),
                ('D2_00028', 'Verificação MSC x DCA Ativo'),
                ('D2_00029', 'Verificação MSC x DCA Passivo'),
                ('D2_00030', 'Verificação MSC x DCA VPA'),
                ('D2_00031', 'Verificação MSC x DCA VPD'),
                ('D2_00032', 'Verificação MSC x DCA Resultado'),
                ('D2_00033', 'Caixa e Equivalentes informados'),
                ('D2_00099', 'Avalia a informação de deduções com transferências constitucionais por municípios'),
                ('D2_00034', 'Verificação DCA Receita Intra'),
                ('D2_00035', 'Verificação DCA Despesa Intra'),
                ('D2_00036', 'Verificação MSCE x DCA'),
                ('D2_00037', 'Verificação MSCE x DCA Patrimônio'),
                ('D2_00038', 'Créditos Previdenciários a Receber'),
                ('D2_00039', 'Verificação DCA x RREO Receita'),
                ('D2_00040', 'Verificação DCA x RREO Despesa'),
                ('D2_00051', 'Ajuste para perdas em Estoques (DCA)'),
                ('D2_00052', 'Equivalência Patrimonial (DCA)'),
                ('D2_00089', 'Verificar VPD de Variações Monetárias e Cambiais Externas quando houver obrigações de empréstimos e financiamentos externos'),
                ('D2_00100', 'Redução ao valor recuperável (investimentos, imobilizado e intangível) — VPD x Ativo (DCA HI x DCA AB)'),
                ('D2_00061', 'VPA FUNDEB informada (DCA)'),
                ('D2_00066', 'Amortização de intangíveis (DCA)'),
                ('D2_00085', 'CAPAG — Passivo Financeiro + Permanente (DCA AB) ≥ Passivo Circulante + Não Circulante (DCA AB)'),
            ]:
                locals()[codigo.lower()] = criar_d2_na(codigo, descricao, obs_dca)
                locals()[f"{codigo.lower()}_t"] = pd.DataFrame()
                locals()[f"resposta_{codigo.lower()}"] = 'N/A'
            d2_00012_ta = pd.DataFrame()
            condicao_negativa_cp = False
            condicao_negativa_lp = False
            condicao_negativa = False
            diferencas_cp = []
            dif_cred_lp = 0
            diferenca_passivo = 0
            emprest = pd.DataFrame()
            vpd_juros = pd.DataFrame()

        # Bloco 2: verificações que dependem de DCA + MSC de encerramento
        if dca_disponivel_d2 and msce_disponivel_d2:
            d2_00044, d2_00044_t = d2_dca_analysis.d2_00044(msc_encerr, df_dca_c)
            resposta_d2_00044 = d2_00044['Resposta'].iloc[0]

            if tipo_ente == "E":
                d2_00045, d2_00045_t = d2_dca_analysis.d2_00045(msc_encerr, df_dca_c)
                resposta_d2_00045 = d2_00045['Resposta'].iloc[0]
            else:
                d2_00045 = pd.DataFrame()

            if tipo_ente == "M":
                d2_00046, d2_00046_t = d2_dca_analysis.d2_00046(msc_encerr, df_dca_c)
                resposta_d2_00046 = d2_00046['Resposta'].iloc[0]
            else:
                d2_00046 = pd.DataFrame()
                d2_00046_t = pd.DataFrame()
                resposta_d2_00046 = 'N/A'

            if tipo_ente == "E":
                d2_00047, d2_00047_t = d2_dca_analysis.d2_00047(msc_encerr, df_dca_c)
                resposta_d2_00047 = d2_00047['Resposta'].iloc[0]
            else:
                d2_00047 = pd.DataFrame()
                d2_00047_t = pd.DataFrame()
                resposta_d2_00047 = 'N/A'

            if tipo_ente == "M":
                d2_00048, d2_00048_t = d2_dca_analysis.d2_00048(msc_encerr, df_dca_c)
                resposta_d2_00048 = d2_00048['Resposta'].iloc[0]
            else:
                d2_00048 = pd.DataFrame()
                d2_00048_t = pd.DataFrame()
                resposta_d2_00048 = 'N/A'

            d2_00049, d2_00049_t = d2_dca_analysis.d2_00049(msc_encerr, df_dca_d)
            resposta_d2_00049 = d2_00049['Resposta'].iloc[0]

            d2_00050, d2_00050_t = d2_dca_analysis.d2_00050(msc_encerr, df_dca_d)
            resposta_d2_00050 = d2_00050['Resposta'].iloc[0]

            d2_00058, d2_00058_t = d2_dca_analysis.d2_00058(msc_encerr, df_dca_hi)
            resposta_d2_00058 = d2_00058['Resposta'].iloc[0]

            d2_00069, d2_00069_t = d2_dca_analysis.d2_00069(emp_msc_encerr, df_dca_e)
            resposta_d2_00069 = d2_00069['Resposta'].iloc[0]
            d2_00070, d2_00070_t = d2_dca_analysis.d2_00070(emp_msc_encerr, df_dca_e)
            resposta_d2_00070 = d2_00070['Resposta'].iloc[0]
            d2_00071, d2_00071_t = d2_dca_analysis.d2_00071(emp_msc_encerr, df_dca_e)
            resposta_d2_00071 = d2_00071['Resposta'].iloc[0]
            d2_00072, d2_00072_t = d2_dca_analysis.d2_00072(emp_msc_encerr, df_dca_e)
            resposta_d2_00072 = d2_00072['Resposta'].iloc[0]
            d2_00073, d2_00073_t = d2_dca_analysis.d2_00073(emp_msc_encerr, df_dca_e)
            resposta_d2_00073 = d2_00073['Resposta'].iloc[0]
            d2_00074, d2_00074_t = d2_dca_analysis.d2_00074(msc_encerr, df_dca_f)
            resposta_d2_00074 = d2_00074['Resposta'].iloc[0]

            if ano >= 2025:
                d2_00101, d2_00101_t = d2_dca_analysis.d2_00101(rp_encerramento, df_dca_g)
                resposta_d2_00101 = d2_00101['Resposta'].iloc[0]
                d2_00102, d2_00102_t = d2_dca_analysis.d2_00102(rp_encerramento, df_dca_g)
                resposta_d2_00102 = d2_00102['Resposta'].iloc[0]
                d2_00103, d2_00103_t = d2_dca_analysis.d2_00103(rp_encerramento, df_dca_g)
                resposta_d2_00103 = d2_00103['Resposta'].iloc[0]
                d2_00104, d2_00104_t = d2_dca_analysis.d2_00104(rp_encerramento, df_dca_g)
                resposta_d2_00104 = d2_00104['Resposta'].iloc[0]
                d2_00105, d2_00105_t = d2_dca_analysis.d2_00105(rp_encerramento, df_dca_g)
                resposta_d2_00105 = d2_00105['Resposta'].iloc[0]
            else:
                d2_00101 = criar_d2_na(
                    'D2_00101',
                    'RP função 10 Saúde (MSC Encerramento x DCA G)',
                    'Aplicável somente a partir de 2025 (metodologia STN — E/DF/M)',
                )
                d2_00102 = criar_d2_na(
                    'D2_00102',
                    'RP função 12 Educação (MSC Encerramento x DCA G)',
                    'Aplicável somente a partir de 2025 (metodologia STN — E/DF/M)',
                )
                d2_00103 = criar_d2_na(
                    'D2_00103',
                    'RP função 09 Previdência Social (MSC Encerramento x DCA G)',
                    'Aplicável somente a partir de 2025 (metodologia STN — E/DF/M)',
                )
                d2_00104 = criar_d2_na(
                    'D2_00104',
                    'RP demais funções exceto 09/10/12 (MSC Encerramento x DCA G)',
                    'Aplicável somente a partir de 2025 (metodologia STN — E/DF/M)',
                )
                d2_00105 = criar_d2_na(
                    'D2_00105',
                    'RP intraorçamentário (MSC Encerramento x DCA G)',
                    'Aplicável somente a partir de 2025 (metodologia STN — E/DF/M)',
                )
                d2_00101_t = pd.DataFrame()
                d2_00102_t = pd.DataFrame()
                d2_00103_t = pd.DataFrame()
                d2_00104_t = pd.DataFrame()
                d2_00105_t = pd.DataFrame()
                resposta_d2_00101 = 'N/A'
                resposta_d2_00102 = 'N/A'
                resposta_d2_00103 = 'N/A'
                resposta_d2_00104 = 'N/A'
                resposta_d2_00105 = 'N/A'
        else:
            obs_dca_msce = 'DCA e/ou MSC Encerramento não disponíveis — verificação exige ambos'
            for codigo, descricao in [
                ('D2_00044', 'Receita Realizada MSC x DCA'),
                ('D2_00045', 'Receita de Impostos Estaduais MSC x DCA'),
                ('D2_00046', 'Receita de Impostos Municipais MSC x DCA'),
                ('D2_00047', 'Transferências Constitucionais Estaduais MSC x DCA'),
                ('D2_00048', 'Transferências Constitucionais Municipais MSC x DCA'),
                ('D2_00049', 'Despesas Orçamentárias MSC x DCA'),
                ('D2_00050', 'Restos a Pagar MSC x DCA'),
                ('D2_00058', 'VPA FUNDEB (MSC x DCA)'),
                ('D2_00069', 'Despesas função 09 (MSC Encerramento x DCA E)'),
                ('D2_00070', 'Despesas função 10 (MSC Encerramento x DCA E)'),
                ('D2_00071', 'Despesas função 12 (MSC Encerramento x DCA E)'),
                ('D2_00072', 'Despesas demais funções (MSC Encerramento x DCA E)'),
                ('D2_00073', 'Despesas intraorçamentárias (MSC Encerramento x DCA E)'),
                ('D2_00074', 'RPPP/RPNPP Pagos (MSC Encerramento x DCA F)'),
                ('D2_00101', 'RP função 10 Saúde (MSC Encerramento x DCA G)'),
                ('D2_00102', 'RP função 12 Educação (MSC Encerramento x DCA G)'),
                ('D2_00103', 'RP função 09 Previdência Social (MSC Encerramento x DCA G)'),
                ('D2_00104', 'RP demais funções exceto 09/10/12 (MSC Encerramento x DCA G)'),
                ('D2_00105', 'RP intraorçamentário (MSC Encerramento x DCA G)'),
            ]:
                locals()[codigo.lower()] = criar_d2_na(codigo, descricao, obs_dca_msce)
                locals()[f"{codigo.lower()}_t"] = pd.DataFrame()
                locals()[f"resposta_{codigo.lower()}"] = 'N/A'

        # Bloco 3: verificações que dependem apenas da MSC de encerramento
        if msce_disponivel_d2:
            d2_00053, d2_00053_t = d2_dca_analysis.d2_00053(msc_encerr)
            resposta_d2_00053 = d2_00053['Resposta'].iloc[0]
            d2_00054, d2_00054_t = d2_dca_analysis.d2_00054(msc_encerr)
            resposta_d2_00054 = d2_00054['Resposta'].iloc[0]
            d2_00055, d2_00055_t = d2_dca_analysis.d2_00055(msc_encerr)
            resposta_d2_00055 = d2_00055['Resposta'].iloc[0]
            d2_00059, d2_00059_t = d2_dca_analysis.d2_00059(msc_encerr)
            resposta_d2_00059 = d2_00059['Resposta'].iloc[0]
            d2_00060, d2_00060_t = d2_dca_analysis.d2_00060(msc_encerr)
            resposta_d2_00060 = d2_00060['Resposta'].iloc[0]
            d2_00067, d2_00067_t = d2_dca_analysis.d2_00067(msc_encerr)
            resposta_d2_00067 = d2_00067['Resposta'].iloc[0]
            d2_00068, d2_00068_t = d2_dca_analysis.d2_00068(msc_encerr)
            resposta_d2_00068 = d2_00068['Resposta'].iloc[0]
            d2_00076, d2_00076_t = d2_dca_analysis.d2_00076(msc_encerr)
            resposta_d2_00076 = d2_00076['Resposta'].iloc[0]
        else:
            obs_msce = 'MSC Encerramento não disponível — verificação exige a matriz de encerramento'
            for codigo, descricao in [
                ('D2_00053', 'Ajuste para perdas em Estoques (MSC Encerramento)'),
                ('D2_00054', 'Investimentos permanentes (MSC Encerramento)'),
                ('D2_00055', 'Amortização de ativos intangíveis (MSC Encerramento)'),
                ('D2_00059', 'Ajuste perdas - Créditos CP/LP (MSC Encerramento)'),
                ('D2_00060', 'Ajuste perdas - Demais créditos CP/LP (MSC Encerramento)'),
                ('D2_00067', 'Depreciação bens móveis (MSC Encerramento)'),
                ('D2_00068', 'Depreciação bens imóveis (MSC Encerramento)'),
                ('D2_00076', 'Créditos previdenciários parcelados — VPA juros x ativo (MSC Encerramento)'),
            ]:
                locals()[codigo.lower()] = criar_d2_na(codigo, descricao, obs_msce)
                locals()[f"{codigo.lower()}_t"] = pd.DataFrame()
                locals()[f"resposta_{codigo.lower()}"] = 'N/A'

        # Bloco 4: verificações que dependem apenas da MSC mensal/consolidada
        if msc_disponivel_d2:
            if ano < 2024:
                d2_00077, d2_00077_t = d2_dca_analysis.d2_00077(msc_consolidada)
                resposta_d2_00077 = d2_00077['Resposta'].iloc[0]
            else:
                d2_00077 = criar_d2_na('D2_00077', 'Comparativo do saldo das contas começadas por 227 e 228', 'Aplicável somente ate 2023')
                d2_00077_t = pd.DataFrame()
                resposta_d2_00077 = 'N/A'

            d2_00079, d2_00079_t = d2_dca_analysis.d2_00079(msc_consolidada)
            resposta_d2_00079 = d2_00079['Resposta'].iloc[0]

            if ano < 2024:
                d2_00080, d2_00080_t = d2_dca_analysis.d2_00080(msc_consolidada)
                resposta_d2_00080 = d2_00080['Resposta'].iloc[0]
            else:
                d2_00080 = criar_d2_na('D2_00080', 'Avaliação do saldo das contas contábeis começadas por 1156', 'Aplicável somente ate 2023')
                d2_00080_t = pd.DataFrame()
                resposta_d2_00080 = 'N/A'

            d2_00081, d2_00081_t = d2_dca_analysis.d2_00081(msc_consolidada)
            resposta_d2_00081 = d2_00081['Resposta'].iloc[0]

            d2_00082, d2_00082_t = d2_dca_analysis.d2_00082(msc_consolidada)
            resposta_d2_00082 = d2_00082['Resposta'].iloc[0]

            if ano >= 2023:
                d2_00083, d2_00083_t = d2_dca_analysis.d2_00083(msc_consolidada)
                resposta_d2_00083 = d2_00083['Resposta'].iloc[0]
            else:
                d2_00083 = criar_d2_na(
                    'D2_00083',
                    'Integridade DDR — saldos finais 721 = 821 (MSC Dezembro)',
                    'Aplicável somente a partir de 2023 (metodologia STN — E/DF/M)',
                )
                d2_00083_t = pd.DataFrame()
                resposta_d2_00083 = 'N/A'

            if ano >= 2023 and dca_disponivel_d2:
                d2_00084, d2_00084_t = d2_dca_analysis.d2_00084(df_dca_ab, msc_consolidada)
                resposta_d2_00084 = d2_00084['Resposta'].iloc[0]
            else:
                d2_00084 = criar_d2_na(
                    'D2_00084',
                    'CAPAG — Passivo Financeiro + Permanente (DCA AB) ≥ Passivo Circulante + Não Circulante (MSC Dezembro)',
                    'Aplicável somente a partir de 2023 (exige DCA AB e MSC mensal — E/DF/M)',
                )
                d2_00084_t = pd.DataFrame()
                resposta_d2_00084 = 'N/A'

            if ano >= 2024:
                d2_00086, d2_00086_t = d2_dca_analysis.d2_00086(msc_consolidada)
                resposta_d2_00086 = d2_00086['Resposta'].iloc[0]
                d2_00087, d2_00087_t = d2_dca_analysis.d2_00087(msc_consolidada)
                resposta_d2_00087 = d2_00087['Resposta'].iloc[0]
                d2_00088, d2_00088_t = d2_dca_analysis.d2_00088(msc_consolidada)
                resposta_d2_00088 = d2_00088['Resposta'].iloc[0]
                d2_00093, d2_00093_t = d2_dca_analysis.d2_00093(msc_consolidada)
                resposta_d2_00093 = d2_00093['Resposta'].iloc[0]
                d2_00094, d2_00094_t = d2_dca_analysis.d2_00094(msc_consolidada)
                resposta_d2_00094 = d2_00094['Resposta'].iloc[0]
                d2_00095, d2_00095_t = d2_dca_analysis.d2_00095(msc_consolidada)
                resposta_d2_00095 = d2_00095['Resposta'].iloc[0]
            else:
                d2_00086 = criar_d2_na(
                    'D2_00086',
                    'Reconhecimento de VPD com material de consumo em todos os meses (MSC)',
                    'Aplicável somente a partir de 2024 (metodologia STN — E/DF/M)',
                )
                d2_00086_t = pd.DataFrame()
                resposta_d2_00086 = 'N/A'
                d2_00087 = criar_d2_na(
                    'D2_00087',
                    'Reconhecimento de VPD com serviços em todos os meses (MSC)',
                    'Aplicável somente a partir de 2024 (metodologia STN — E/DF/M)',
                )
                d2_00087_t = pd.DataFrame()
                resposta_d2_00087 = 'N/A'
                d2_00088 = criar_d2_na(
                    'D2_00088',
                    'Reconhecimento de VPD com transferências intergovernamentais em todos os meses (MSC)',
                    'Aplicável somente a partir de 2024 (metodologia STN — E/DF/M)',
                )
                d2_00088_t = pd.DataFrame()
                resposta_d2_00088 = 'N/A'
                d2_00093 = criar_d2_na(
                    'D2_00093',
                    'Movimentação patrimonial de consumo nas contas de almoxarifado — grupo 11561 (MSC)',
                    'Aplicável somente a partir de 2024 (metodologia STN — E/DF/M)',
                )
                d2_00093_t = pd.DataFrame()
                resposta_d2_00093 = 'N/A'
                d2_00094 = criar_d2_na(
                    'D2_00094',
                    'Despesas previdenciárias RPPS — saldo final 3.1.1.1.1.01.01 e 3.1.2.1.2.01.00 (MSC Dezembro)',
                    'Aplicável somente a partir de 2024 (metodologia STN — E/DF/M)',
                )
                d2_00094_t = pd.DataFrame()
                resposta_d2_00094 = 'N/A'
                d2_00095 = criar_d2_na(
                    'D2_00095',
                    'Despesas previdenciárias RGPS — saldo final 3.1.1.2.1.01.01, 3.1.2.2.1.01.00 e 3.1.2.2.3.01.00 (MSC Dezembro)',
                    'Aplicável somente a partir de 2024 (metodologia STN — E/DF/M)',
                )
                d2_00095_t = pd.DataFrame()
                resposta_d2_00095 = 'N/A'
        else:
            obs_msc = 'MSC mensal não disponível — verificação exige a matriz consolidada do exercício'
            for codigo, descricao in [
                ('D2_00077', 'Comparativo saldo contas 227/228 (MSC Jan/Dez)'),
                ('D2_00079', 'Comparativo saldo contas 119 (MSC Jan/Dez)'),
                ('D2_00080', 'Saldo contas 1156 em todos os meses (MSC)'),
                ('D2_00081', 'Movimento credor contas 2.1.1.1.1.01.02/03 (MSC)'),
                ('D2_00082', 'Movimento credor contas 1.2.3.8.1.01/03/05 (MSC)'),
                ('D2_00083', 'Integridade DDR — saldos finais 721 = 821 (MSC Dezembro)'),
                ('D2_00084', 'CAPAG — Passivo Financeiro + Permanente (DCA AB) ≥ Passivo Circulante + Não Circulante (MSC Dezembro)'),
                ('D2_00086', 'VPD material de consumo — movimento devedor 3311 em todos os meses (MSC)'),
                ('D2_00087', 'VPD serviços — movimento devedor 332 em todos os meses (MSC)'),
                ('D2_00088', 'VPD transferências intergovernamentais — movimento devedor 352 em todos os meses (MSC)'),
                ('D2_00093', 'Movimento credor — grupo 11561 almoxarifado em todos os meses (MSC)'),
                ('D2_00094', 'Despesas previdenciárias RPPS — saldo final 3.1.1.1.1.01.01 e 3.1.2.1.2.01.00 (MSC Dezembro)'),
                ('D2_00095', 'Despesas previdenciárias RGPS — saldo final 3.1.1.2.1.01.01, 3.1.2.2.1.01.00 e 3.1.2.2.3.01.00 (MSC Dezembro)'),
            ]:
                locals()[codigo.lower()] = criar_d2_na(codigo, descricao, obs_msc)
                locals()[f"{codigo.lower()}_t"] = pd.DataFrame()
                locals()[f"resposta_{codigo.lower()}"] = 'N/A'


    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################




    #############################################################################
    #                         DIMENSÃO D3 - RREO / RGF                          #
    #############################################################################

    # Verificar se RREO está disponível para executar verificações D3
    rreo_disponivel_d3 = disponibilidade.get('rreo', {}).get('completo', False)
    executar_d3 = rreo_disponivel_d3  # D3 depende principalmente de RREO completo (6º bimestre)

    @st.cache_data(show_spinner=False)
    def _carregar_vigencia_csv():
        """
        Carrega regras de vigência a partir de config/verificacoes_vigencia.csv.
        Formato esperado: codigo,dimensao,inicio,fim
        """
        config_dir = Path(__file__).resolve().parent.parent / "config"
        caminho_gerado = config_dir / "verificacoes_vigencia_generated.csv"
        caminho_padrao = config_dir / "verificacoes_vigencia.csv"
        caminho = caminho_gerado if caminho_gerado.exists() else caminho_padrao
        if not caminho.exists():
            return {}
        try:
            vig_df = pd.read_csv(caminho)
            if vig_df.empty or 'codigo' not in vig_df.columns:
                return {}

            vig_df['codigo'] = vig_df['codigo'].astype(str).str.strip().str.upper()
            if 'inicio' in vig_df.columns:
                vig_df['inicio'] = pd.to_numeric(vig_df['inicio'], errors='coerce')
            else:
                vig_df['inicio'] = np.nan
            if 'fim' in vig_df.columns:
                vig_df['fim'] = pd.to_numeric(vig_df['fim'], errors='coerce')
            else:
                vig_df['fim'] = np.nan

            return {
                row['codigo']: (
                    int(row['inicio']) if pd.notna(row['inicio']) else None,
                    int(row['fim']) if pd.notna(row['fim']) else None,
                )
                for _, row in vig_df.iterrows()
            }
        except Exception:
            return {}

    def _verificacao_vigente(ano_ref: int, inicio: int | None = None, fim: int | None = None) -> bool:
        if inicio is not None and ano_ref < inicio:
            return False
        if fim is not None and ano_ref > fim:
            return False
        return True

    def _mensagem_vigencia(inicio: int | None = None, fim: int | None = None) -> str:
        if inicio is not None and fim is not None:
            return f'Verificação vigente de {inicio} até {fim}'
        if inicio is not None:
            return f'Verificação vigente a partir de {inicio}'
        if fim is not None:
            return f'Verificação vigente até {fim}'
        return 'Verificação sem regra de vigência definida'

    def _aplicar_vigencia(
        codigo: str,
        descricao: str,
        resultado_df: pd.DataFrame,
        tabela_df: pd.DataFrame,
        ano_ref: int,
        mapa_vigencia_padrao: dict,
        mapa_vigencia_csv: dict,
    ):
        inicio, fim = mapa_vigencia_csv.get(codigo, mapa_vigencia_padrao.get(codigo, (None, None)))
        if _verificacao_vigente(ano_ref, inicio, fim):
            return resultado_df, tabela_df
        return (
            pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': _mensagem_vigencia(inicio, fim)
            }]),
            pd.DataFrame()
        )

    def _inferir_ano_max_metodologia_stn(vigencia_csv: dict) -> int | None:
        """Maior ano (início/fim) no CSV de vigência — proxy do último ano catalogado na metodologia."""
        if not vigencia_csv:
            return None
        anos: list[int] = []
        for ini, fi in vigencia_csv.values():
            if ini is not None:
                anos.append(int(ini))
            if fi is not None:
                anos.append(int(fi))
        return max(anos) if anos else None

    def _ler_ano_cap_metodologia_stn() -> int | None:
        """Override opcional: config/metodologia_ano_referencia_stn.txt (uma linha, ex.: 2024)."""
        config_dir = Path(__file__).resolve().parent.parent / "config"
        p = config_dir / "metodologia_ano_referencia_stn.txt"
        if not p.exists():
            return None
        try:
            t = p.read_text(encoding="utf-8").strip()
            if not t:
                return None
            return int(t)
        except (ValueError, OSError):
            return None

    def _ano_para_vigencia_ranking(ano_exercicio: int, vigencia_csv: dict) -> int:
        """
        Ano usado só para regras de vigência STN. Enquanto não existir lista oficial para o
        exercício selecionado, limita ao último ano de metodologia conhecido (ex.: 2025 → 2024).
        O exercício contábil/API continua sendo ano_exercicio.
        """
        cap = _ler_ano_cap_metodologia_stn()
        if cap is None:
            cap = _inferir_ano_max_metodologia_stn(vigencia_csv)
        if cap is None:
            return ano_exercicio
        return min(ano_exercicio, cap)

    vigencia_csv_ranking = _carregar_vigencia_csv()
    ano_vigencia_ranking = _ano_para_vigencia_ranking(ano, vigencia_csv_ranking)

    if not executar_d3:
        # RREO não completo - criar todas as variáveis D3 com N/A
        def criar_d3_na(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'RREO 6º bimestre não disponível para este exercício'
            }])

        d3_00001 = criar_d3_na('D3_00001', 'Resultado Orçamentário RREO')
        d3_00002 = criar_d3_na('D3_00002', 'RREO Anexo 1 x Anexo 2')
        d3_00005 = criar_d3_na('D3_00005', 'RCL RREO x RGF')
        d3_00006 = criar_d3_na('D3_00006', 'Despesa com Pessoal RREO x RGF')
        d3_00008 = criar_d3_na('D3_00008', 'Disponibilidade de Caixa RREO x RGF')
        d3_00009 = criar_d3_na('D3_00009', 'RP RREO x RGF')
        d3_00010 = criar_d3_na('D3_00010', 'Dívida Consolidada RREO x RGF')
        d3_00011 = criar_d3_na('D3_00011', 'Dedução inativos/pensionistas recursos vinculados')
        d3_00012 = criar_d3_na('D3_00012', 'Informação de valores negativos no RREO')
        d3_00013 = criar_d3_na('D3_00013', 'CAPAG: Informação de valores negativos no RGF (todos os poderes/órgãos)')
        d3_00014 = criar_d3_na('D3_00014', 'Emendas individuais entre anexos RGF')
        d3_00015 = criar_d3_na('D3_00015', 'Emendas individuais RREO x RGF')
        d3_00016 = criar_d3_na('D3_00016', 'Emendas de bancada RREO x RGF')
        d3_00017 = criar_d3_na('D3_00017', 'RP pagos RREO 6 x RREO 7')
        d3_00022 = criar_d3_na('D3_00022', 'Receitas correntes MSC x RREO Anexo 1')
        d3_00023 = criar_d3_na('D3_00023', 'Receitas de capital MSC x RREO Anexo 1')
        d3_00024 = criar_d3_na('D3_00024', 'Despesas correntes MSC x RREO Anexo 1')
        d3_00025 = criar_d3_na('D3_00025', 'Despesas de capital MSC x RREO Anexo 1')
        d3_00026 = criar_d3_na('D3_00026', 'CAPAG: Caixa Bruta por grupos FR (MSC dez x RGF Anexo 5 Executivo)')
        d3_00027 = criar_d3_na('D3_00027', 'RREO Anexo 1 x Anexo 6 — dotação, empenhadas e liquidadas')
        d3_00028 = criar_d3_na('D3_00028', 'RREO Anexo 1 x Anexo 6 — receitas realizadas e previsão')
        d3_00029 = criar_d3_na('D3_00029', 'Piso enfermagem: RGF 1 (E) x MSC (90%)')
        d3_00030 = criar_d3_na('D3_00030', 'Receitas previdenciárias RREO Anexo 4 x Anexo 6')
        d3_00032 = criar_d3_na('D3_00032', 'Recursos Arrecadados em Exercícios Anteriores (RPPS) RREO Anexo 1 x Anexo 4 x Anexo 6')
        d3_00033 = criar_d3_na('D3_00033', 'Superávit financeiro RREO Anexo 1 x Anexo 6 (previsão)')
        d3_00034 = criar_d3_na('D3_00034', 'Reserva Orçamentária do RPPS (Previdenciário) RREO Anexo 1 x Anexo 4 x Anexo 6')
        d3_00035 = criar_d3_na('D3_00035', 'Reserva de contingência RREO Anexo 1 x Anexo 6 (dotação)')
        d3_00037 = criar_d3_na('D3_00037', 'Investimentos RREO Anexo 1 x Anexo 9')
        d3_00038 = criar_d3_na('D3_00038', 'Inversões Financeiras RREO Anexo 1 x Anexo 9')
        d3_00039 = criar_d3_na('D3_00039', 'Amortização da Dívida RREO Anexo 1 x Anexo 9')
        d3_00021 = criar_d3_na('D3_00021', 'CAPAG: Passivo Financeiro MSC Dez >= Restos a Pagar MSC Dez')
        d3_00040 = criar_d3_na('D3_00040', 'Receitas de Operações de Crédito RREO Anexo 1 x Anexo 9')
        d3_00044 = criar_d3_na('D3_00044', 'Transferências da União — Agentes Comunitários de Saúde (RREO Anexo 3 x RGF Anexo 1 E)')
        d3_00045 = criar_d3_na('D3_00045', 'Valores negativos em Restos a Pagar — RGF Anexo 5 (Executivo)')
        d3_00046 = criar_d3_na('D3_00046', 'Contribuição do Servidor para Previdência RREO Anexo 3 x Anexo 4')
        d3_00048 = criar_d3_na('D3_00048', 'Despesas com Compensação Financeira entre regimes (MSC dez x RREO Anexo 4)')
        d3_00049 = criar_d3_na('D3_00049', 'Caixa e Equivalentes de Caixa (MSC dez x RREO Anexo 4)')
        d3_00050 = criar_d3_na('D3_00050', 'Reserva Orçamentária do RPPS RREO Anexo 4 x Anexo 6')
        d3_00051 = criar_d3_na('D3_00051', 'Despesas de inativos no CO 1002 (ASPS) na MSC de dezembro')
        d3_00052 = criar_d3_na('D3_00052', 'Despesas de inativos no CO 1001 (MDE) na MSC de dezembro')
        d3_00054 = criar_d3_na('D3_00054', 'Qualidade do CO 1002: função Saúde/Encargos e fontes 500/502/761 na MSC de dezembro')
        d3_00055 = criar_d3_na('D3_00055', 'Qualidade do CO 1001: função Educação/Encargos e fontes 500/502/761 na MSC de dezembro')
        d3_00056 = criar_d3_na('D3_00056', 'Despesas Previdenciárias RREO Anexo 4 x RGF Anexo 1 (todos os poderes)')

        # Tabelas vazias
        d3_00001_t = pd.DataFrame()
        d3_00002_t = pd.DataFrame()
        d3_00005_t = pd.DataFrame()
        d3_00006_t = pd.DataFrame()
        d3_00008_t = pd.DataFrame()
        d3_00009_t = pd.DataFrame()
        d3_00010_t = pd.DataFrame()
        d3_00011_t = pd.DataFrame()
        d3_00012_t = pd.DataFrame()
        d3_00013_t = pd.DataFrame()
        d3_00014_t = pd.DataFrame()
        d3_00015_t = pd.DataFrame()
        d3_00016_t = pd.DataFrame()
        d3_00017_t = pd.DataFrame()
        d3_00022_t = pd.DataFrame()
        d3_00023_t = pd.DataFrame()
        d3_00024_t = pd.DataFrame()
        d3_00025_t = pd.DataFrame()
        d3_00026_t = pd.DataFrame()
        d3_00027_t = pd.DataFrame()
        d3_00028_t = pd.DataFrame()
        d3_00029_t = pd.DataFrame()
        d3_00030_t = pd.DataFrame()
        d3_00032_t = pd.DataFrame()
        d3_00033_t = pd.DataFrame()
        d3_00034_t = pd.DataFrame()
        d3_00035_t = pd.DataFrame()
        d3_00037_t = pd.DataFrame()
        d3_00038_t = pd.DataFrame()
        d3_00039_t = pd.DataFrame()
        d3_00021_t = pd.DataFrame()
        d3_00040_t = pd.DataFrame()
        d3_00044_t = pd.DataFrame()
        d3_00045_t = pd.DataFrame()
        d3_00046_t = pd.DataFrame()
        d3_00048_t = pd.DataFrame()
        d3_00049_t = pd.DataFrame()
        d3_00050_t = pd.DataFrame()
        d3_00051_t = pd.DataFrame()
        d3_00052_t = pd.DataFrame()
        d3_00054_t = pd.DataFrame()
        d3_00055_t = pd.DataFrame()
        d3_00056_t = pd.DataFrame()

        # Respostas N/A
        resposta_d3_00001 = 'N/A'; resposta_d3_00002 = 'N/A'; resposta_d3_00005 = 'N/A'
        resposta_d3_00006 = 'N/A'; resposta_d3_00008 = 'N/A'; resposta_d3_00009 = 'N/A'
        resposta_d3_00010 = 'N/A'; resposta_d3_00011 = 'N/A'; resposta_d3_00012 = 'N/A'; resposta_d3_00013 = 'N/A'; resposta_d3_00014 = 'N/A'; resposta_d3_00015 = 'N/A'; resposta_d3_00016 = 'N/A'; resposta_d3_00017 = 'N/A'
        resposta_d3_00022 = 'N/A'
        resposta_d3_00023 = 'N/A'
        resposta_d3_00024 = 'N/A'
        resposta_d3_00025 = 'N/A'
        resposta_d3_00026 = 'N/A'
        resposta_d3_00027 = 'N/A'
        resposta_d3_00028 = 'N/A'
        resposta_d3_00029 = 'N/A'
        resposta_d3_00030 = 'N/A'
        resposta_d3_00032 = 'N/A'
        resposta_d3_00033 = 'N/A'
        resposta_d3_00034 = 'N/A'
        resposta_d3_00035 = 'N/A'
        resposta_d3_00037 = 'N/A'
        resposta_d3_00038 = 'N/A'
        resposta_d3_00021 = 'N/A'
        resposta_d3_00039 = 'N/A'
        resposta_d3_00040 = 'N/A'
        resposta_d3_00044 = 'N/A'
        resposta_d3_00045 = 'N/A'
        resposta_d3_00046 = 'N/A'
        resposta_d3_00048 = 'N/A'
        resposta_d3_00049 = 'N/A'
        resposta_d3_00050 = 'N/A'
        resposta_d3_00051 = 'N/A'
        resposta_d3_00052 = 'N/A'
        resposta_d3_00054 = 'N/A'
        resposta_d3_00055 = 'N/A'
        resposta_d3_00056 = 'N/A'

    ############################################
    #########  PARTE QUE EXECUTA A D3  #########
    ############################################

    if executar_d3:
        vigencia_csv = vigencia_csv_ranking
        d3_00001, d3_00001_t = d3_analysis.d3_00001(df_rreo_1)
        d3_00002, d3_00002_t = d3_analysis.d3_00002(df_rreo_1, df_rreo_2)
        d3_00005, d3_00005_t = d3_analysis.d3_00005(df_rreo_3, df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e)
        d3_00006, d3_00006_t = d3_analysis.d3_00006(df_rgf_2e, df_rreo_6, ano)
        d3_00008, d3_00008_t = d3_analysis.d3_00008(df_rgf_5e, rgf_o, df_rreo_1, tipo_ente)
        d3_00009, d3_00009_t = d3_analysis.d3_00009(df_rgf_5e, rgf_o, df_rreo_7, tipo_ente)
        d3_00010, d3_00010_t = d3_analysis.d3_00010(df_rgf_1e, rgf, tipo_ente)
        d3_00011, d3_00011_t = d3_analysis.d3_00011(rgf, tipo_ente)
        d3_00012, d3_00012_t = d3_analysis.d3_00012(
            df_rreo_1=df_rreo_1,
            df_rreo_2=df_rreo_2,
            df_rreo_3=df_rreo_3,
            df_rreo_4=df_rreo_4,
            df_rreo_4_rpps=df_rreo_4_rpps,
            df_rreo_6=df_rreo_6,
            df_rreo_7=df_rreo_7,
            df_rreo_9=df_rreo_9,
        )
        d3_00013, d3_00013_t = d3_analysis.d3_00013(rgf, tipo_ente)
        d3_00014, d3_00014_t = d3_analysis.d3_00014(df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e)
        d3_00015, d3_00015_t = d3_analysis.d3_00015(df_rgf_1e, df_rreo_3)
        d3_00016, d3_00016_t = d3_analysis.d3_00016(df_rgf_1e, df_rreo_3)
        d3_00017, d3_00017_t = d3_analysis.d3_00017(df_rreo_6, df_rreo_7)
        d3_00021, d3_00021_t = d3_analysis.d3_00021(msc_dez, tipo_ente)
        d3_00022, d3_00022_t = d3_analysis.d3_00022(receita_corr, df_rreo_1)
        d3_00023, d3_00023_t = d3_analysis.d3_00023(receita_capi, df_rreo_1)
        d3_00024, d3_00024_t = d3_analysis.d3_00024(despesa_corr, df_rreo_1)
        d3_00025, d3_00025_t = d3_analysis.d3_00025(despesa_capi, df_rreo_1)
        d3_00026, d3_00026_t = d3_analysis.d3_00026(msc_dez, df_rgf_5e)
        d3_00027, d3_00027_t = d3_analysis.d3_00027(df_rreo_1, df_rreo_6)
        d3_00028, d3_00028_t = d3_analysis.d3_00028(df_rreo_1, df_rreo_6)
        d3_00029, d3_00029_t = d3_analysis.d3_00029(despesa, df_rgf_1e, tipo_ente)
        d3_00030, d3_00030_t = d3_analysis.d3_00030(df_rreo_4, df_rreo_6, df_rreo_4_rpps)
        d3_00032, d3_00032_t = d3_analysis.d3_00032(df_rreo_1, df_rreo_4, df_rreo_6)
        d3_00033, d3_00033_t = d3_analysis.d3_00033(df_rreo_1, df_rreo_6)
        d3_00034, d3_00034_t = d3_analysis.d3_00034(df_rreo_1, df_rreo_4, df_rreo_6)
        d3_00035, d3_00035_t = d3_analysis.d3_00035(df_rreo_1, df_rreo_6)
        d3_00037, d3_00037_t = d3_analysis.d3_00037(df_rreo_1, df_rreo_9)
        d3_00038, d3_00038_t = d3_analysis.d3_00038(df_rreo_1, df_rreo_9)
        d3_00039, d3_00039_t = d3_analysis.d3_00039(df_rreo_1, df_rreo_9)
        d3_00040, d3_00040_t = d3_analysis.d3_00040(df_rreo_1, df_rreo_9)
        d3_00044, d3_00044_t = d3_analysis.d3_00044(df_rreo_3, df_rgf_1e)
        d3_00045, d3_00045_t = d3_analysis.d3_00045(df_rgf_5e)
        d3_00046, d3_00046_t = d3_analysis.d3_00046(df_rreo_3, df_rreo_4)
        d3_00048, d3_00048_t = d3_analysis.d3_00048(msc_dez, df_rreo_4)
        d3_00049, d3_00049_t = d3_analysis.d3_00049(msc_dez, df_rreo_4)
        d3_00050, d3_00050_t = d3_analysis.d3_00050(df_rreo_4, df_rreo_6)
        d3_00051, d3_00051_t = d3_analysis.d3_00051(msc_dez)
        d3_00052, d3_00052_t = d3_analysis.d3_00052(msc_dez)
        d3_00054, d3_00054_t = d3_analysis.d3_00054(msc_dez)
        d3_00055, d3_00055_t = d3_analysis.d3_00055(msc_dez)
        d3_00056, d3_00056_t = d3_analysis.d3_00056(df_rreo_4, df_rgf_1, tipo_ente, df_rreo_4_rpps)

        d3_vigencia = {
            'D3_00012': (2019, None),
            'D3_00013': (2019, None),
            'D3_00017': (2023, None),
            'D3_00021': (2023, None),
            'D3_00022': (2023, None),
            'D3_00023': (2023, None),
            'D3_00024': (2023, None),
            'D3_00025': (2023, None),
            'D3_00026': (2023, None),
            'D3_00027': (2023, None),
            'D3_00028': (2023, None),
            'D3_00029': (2024, None),
            'D3_00030': (2024, None),
            'D3_00032': (2024, None),
            'D3_00033': (2024, None),
            'D3_00034': (2024, None),
            'D3_00035': (2024, None),
            'D3_00037': (2024, None),
            'D3_00038': (2024, None),
            'D3_00039': (2024, None),
            'D3_00040': (2024, None),
            'D3_00044': (2024, None),
            'D3_00045': (2024, None),
            'D3_00046': (2025, None),
            'D3_00048': (2025, None),
            'D3_00049': (2025, None),
            'D3_00050': (2025, None),
            'D3_00051': (2025, None),
            'D3_00052': (2025, None),
            'D3_00054': (2025, None),
            'D3_00055': (2025, None),
            'D3_00056': (2025, None),
        }

        d3_00012, d3_00012_t = _aplicar_vigencia('D3_00012', 'Informação de valores negativos no RREO', d3_00012, d3_00012_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00013, d3_00013_t = _aplicar_vigencia('D3_00013', 'CAPAG: Informação de valores negativos no RGF (todos os poderes/órgãos)', d3_00013, d3_00013_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00017, d3_00017_t = _aplicar_vigencia('D3_00017', 'RP pagos RREO 6 x RREO 7', d3_00017, d3_00017_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00021, d3_00021_t = _aplicar_vigencia('D3_00021', 'CAPAG: Passivo Financeiro MSC Dez >= Restos a Pagar MSC Dez', d3_00021, d3_00021_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00022, d3_00022_t = _aplicar_vigencia('D3_00022', 'Receitas correntes MSC x RREO Anexo 1', d3_00022, d3_00022_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00023, d3_00023_t = _aplicar_vigencia('D3_00023', 'Receitas de capital MSC x RREO Anexo 1', d3_00023, d3_00023_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00024, d3_00024_t = _aplicar_vigencia('D3_00024', 'Despesas correntes MSC x RREO Anexo 1', d3_00024, d3_00024_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00025, d3_00025_t = _aplicar_vigencia('D3_00025', 'Despesas de capital MSC x RREO Anexo 1', d3_00025, d3_00025_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00026, d3_00026_t = _aplicar_vigencia('D3_00026', 'CAPAG: Caixa Bruta por grupos FR (MSC dez x RGF Anexo 5 Executivo)', d3_00026, d3_00026_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00027, d3_00027_t = _aplicar_vigencia('D3_00027', 'RREO Anexo 1 x Anexo 6 — dotação, empenhadas e liquidadas', d3_00027, d3_00027_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00028, d3_00028_t = _aplicar_vigencia('D3_00028', 'RREO Anexo 1 x Anexo 6 — receitas realizadas e previsão', d3_00028, d3_00028_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00029, d3_00029_t = _aplicar_vigencia('D3_00029', 'Piso enfermagem: RGF 1 (E) x MSC (90%)', d3_00029, d3_00029_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00030, d3_00030_t = _aplicar_vigencia('D3_00030', 'Receitas previdenciárias RREO Anexo 4 x Anexo 6', d3_00030, d3_00030_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00032, d3_00032_t = _aplicar_vigencia('D3_00032', 'Recursos Arrecadados em Exercícios Anteriores (RPPS) RREO Anexo 1 x Anexo 4 x Anexo 6', d3_00032, d3_00032_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00033, d3_00033_t = _aplicar_vigencia('D3_00033', 'Superávit financeiro RREO Anexo 1 x Anexo 6 (previsão)', d3_00033, d3_00033_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00034, d3_00034_t = _aplicar_vigencia('D3_00034', 'Reserva Orçamentária do RPPS (Previdenciário) RREO Anexo 1 x Anexo 4 x Anexo 6', d3_00034, d3_00034_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00035, d3_00035_t = _aplicar_vigencia('D3_00035', 'Reserva de contingência RREO Anexo 1 x Anexo 6 (dotação)', d3_00035, d3_00035_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00037, d3_00037_t = _aplicar_vigencia('D3_00037', 'Investimentos RREO Anexo 1 x Anexo 9', d3_00037, d3_00037_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00038, d3_00038_t = _aplicar_vigencia('D3_00038', 'Inversões Financeiras RREO Anexo 1 x Anexo 9', d3_00038, d3_00038_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00039, d3_00039_t = _aplicar_vigencia('D3_00039', 'Amortização da Dívida RREO Anexo 1 x Anexo 9', d3_00039, d3_00039_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00040, d3_00040_t = _aplicar_vigencia('D3_00040', 'Receitas de Operações de Crédito RREO Anexo 1 x Anexo 9', d3_00040, d3_00040_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00044, d3_00044_t = _aplicar_vigencia('D3_00044', 'Transferências da União — Agentes Comunitários de Saúde (RREO Anexo 3 x RGF Anexo 1 E)', d3_00044, d3_00044_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00045, d3_00045_t = _aplicar_vigencia('D3_00045', 'Valores negativos em Restos a Pagar — RGF Anexo 5 (Executivo)', d3_00045, d3_00045_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00046, d3_00046_t = _aplicar_vigencia('D3_00046', 'Contribuição do Servidor para Previdência RREO Anexo 3 x Anexo 4', d3_00046, d3_00046_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00048, d3_00048_t = _aplicar_vigencia('D3_00048', 'Despesas com Compensação Financeira entre regimes (MSC dez x RREO Anexo 4)', d3_00048, d3_00048_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00049, d3_00049_t = _aplicar_vigencia('D3_00049', 'Caixa e Equivalentes de Caixa (MSC dez x RREO Anexo 4)', d3_00049, d3_00049_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00050, d3_00050_t = _aplicar_vigencia('D3_00050', 'Reserva Orçamentária do RPPS RREO Anexo 4 x Anexo 6', d3_00050, d3_00050_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00051, d3_00051_t = _aplicar_vigencia('D3_00051', 'Despesas de inativos no CO 1002 (ASPS) na MSC de dezembro', d3_00051, d3_00051_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00052, d3_00052_t = _aplicar_vigencia('D3_00052', 'Despesas de inativos no CO 1001 (MDE) na MSC de dezembro', d3_00052, d3_00052_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00054, d3_00054_t = _aplicar_vigencia('D3_00054', 'Qualidade do CO 1002: função Saúde/Encargos e fontes 500/502/761 na MSC de dezembro', d3_00054, d3_00054_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00055, d3_00055_t = _aplicar_vigencia('D3_00055', 'Qualidade do CO 1001: função Educação/Encargos e fontes 500/502/761 na MSC de dezembro', d3_00055, d3_00055_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)
        d3_00056, d3_00056_t = _aplicar_vigencia('D3_00056', 'Despesas Previdenciárias RREO Anexo 4 x RGF Anexo 1 (todos os poderes)', d3_00056, d3_00056_t, ano_vigencia_ranking, d3_vigencia, vigencia_csv)

        resposta_d3_00001 = d3_00001['Resposta'].iloc[0]
        resposta_d3_00002 = d3_00002['Resposta'].iloc[0]
        resposta_d3_00005 = d3_00005['Resposta'].iloc[0]
        resposta_d3_00006 = d3_00006['Resposta'].iloc[0]
        resposta_d3_00008 = d3_00008['Resposta'].iloc[0]
        resposta_d3_00009 = d3_00009['Resposta'].iloc[0]
        resposta_d3_00010 = d3_00010['Resposta'].iloc[0]
        resposta_d3_00011 = d3_00011['Resposta'].iloc[0]
        resposta_d3_00012 = d3_00012['Resposta'].iloc[0]
        resposta_d3_00013 = d3_00013['Resposta'].iloc[0]
        resposta_d3_00014 = d3_00014['Resposta'].iloc[0]
        resposta_d3_00015 = d3_00015['Resposta'].iloc[0]
        resposta_d3_00016 = d3_00016['Resposta'].iloc[0]
        resposta_d3_00017 = d3_00017['Resposta'].iloc[0]
        resposta_d3_00021 = d3_00021['Resposta'].iloc[0]
        resposta_d3_00022 = d3_00022['Resposta'].iloc[0]
        resposta_d3_00023 = d3_00023['Resposta'].iloc[0]
        resposta_d3_00024 = d3_00024['Resposta'].iloc[0]
        resposta_d3_00025 = d3_00025['Resposta'].iloc[0]
        resposta_d3_00026 = d3_00026['Resposta'].iloc[0]
        resposta_d3_00027 = d3_00027['Resposta'].iloc[0]
        resposta_d3_00028 = d3_00028['Resposta'].iloc[0]
        resposta_d3_00029 = d3_00029['Resposta'].iloc[0]
        resposta_d3_00030 = d3_00030['Resposta'].iloc[0]
        resposta_d3_00032 = d3_00032['Resposta'].iloc[0]
        resposta_d3_00033 = d3_00033['Resposta'].iloc[0]
        resposta_d3_00034 = d3_00034['Resposta'].iloc[0]
        resposta_d3_00035 = d3_00035['Resposta'].iloc[0]
        resposta_d3_00037 = d3_00037['Resposta'].iloc[0]
        resposta_d3_00038 = d3_00038['Resposta'].iloc[0]
        resposta_d3_00039 = d3_00039['Resposta'].iloc[0]
        resposta_d3_00040 = d3_00040['Resposta'].iloc[0]
        resposta_d3_00044 = d3_00044['Resposta'].iloc[0]
        resposta_d3_00045 = d3_00045['Resposta'].iloc[0]
        resposta_d3_00046 = d3_00046['Resposta'].iloc[0]
        resposta_d3_00048 = d3_00048['Resposta'].iloc[0]
        resposta_d3_00049 = d3_00049['Resposta'].iloc[0]
        resposta_d3_00050 = d3_00050['Resposta'].iloc[0]
        resposta_d3_00051 = d3_00051['Resposta'].iloc[0]
        resposta_d3_00052 = d3_00052['Resposta'].iloc[0]
        resposta_d3_00054 = d3_00054['Resposta'].iloc[0]
        resposta_d3_00055 = d3_00055['Resposta'].iloc[0]
        resposta_d3_00056 = d3_00056['Resposta'].iloc[0]




    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################
    #############################################################################





    #############################################################################
    # DIMENSÃO 4 - CRUZAMENTO DCA x RREO
    #############################################################################

    # Verificar se DCA e RREO estão disponíveis para executar verificações D4
    #############################################################################
    #                         DIMENSÃO D4 - DCA x RREO                          #
    #############################################################################

    dca_disponivel_d4 = disponibilidade.get('dca', {}).get('disponivel', False)
    rreo_disponivel_d4 = disponibilidade.get('rreo', {}).get('completo', False)
    # Sem 6º RREO não há base para D4. Sem DCA ainda rodam cruzamentos MSC×RREO e RGF×MSC.
    executar_d4 = rreo_disponivel_d4
    executar_d4_cruzamentos_dca = dca_disponivel_d4 and rreo_disponivel_d4

    if not executar_d4:
        # RREO 6º não disponível — todas as verificações D4 em N/A
        def criar_d4_na(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'RREO 6º bimestre não disponível para este exercício'
            }])

        d4_00001 = criar_d4_na('D4_00001', 'Receita Realizada RREO x DCA')
        d4_00002 = criar_d4_na('D4_00002', 'Execução da Despesa RREO x DCA')
        d4_00003 = criar_d4_na('D4_00003', 'Despesa por Função RREO x DCA')
        d4_00004 = criar_d4_na('D4_00004', 'Despesa por Função Intra RREO x DCA')
        d4_00005 = criar_d4_na('D4_00005', 'Restos a Pagar RREO x DCA')
        d4_00006 = criar_d4_na('D4_00006', 'Restos a Pagar NP RREO x DCA')
        d4_00007 = criar_d4_na('D4_00007', 'Dívida Consolidada RREO x DCA')
        d4_00009 = criar_d4_na('D4_00009', 'Receita de Impostos RREO x DCA')
        d4_00010 = criar_d4_na('D4_00010', 'Receita de Impostos RREO x DCA')
        d4_00011 = criar_d4_na('D4_00011', 'Transferências estaduais RREO x DCA')
        d4_00012 = criar_d4_na('D4_00012', 'Transferências municipais RREO x DCA')
        d4_00017 = criar_d4_na('D4_00017', 'Contribuições e compensações previdenciárias RREO x DCA')
        d4_00019 = criar_d4_na('D4_00019', 'Despesas de capital RREO x DCA')
        d4_00020 = criar_d4_na('D4_00020', 'Receita arrecadada MSC x RREO')
        d4_00021 = criar_d4_na('D4_00021', 'Receita de impostos estaduais MSC x RREO')
        d4_00022 = criar_d4_na('D4_00022', 'Receita de impostos municipais MSC x RREO')
        d4_00023 = criar_d4_na('D4_00023', 'Transferências constitucionais estaduais MSC x RREO')
        d4_00024 = criar_d4_na('D4_00024', 'Transferências constitucionais municipais MSC x RREO')
        d4_00025 = criar_d4_na('D4_00025', 'Despesas empenhadas, liquidadas e pagas MSC x RREO')
        d4_00026 = criar_d4_na('D4_00026', 'Inscrição de RPNP MSC x RREO')
        d4_00027 = criar_d4_na('D4_00027', 'Disponibilidade de Caixa Bruta RGF 2 x DCA AB')
        d4_00028 = criar_d4_na('D4_00028', 'Disponibilidade de Caixa Bruta RGF 5 x DCA AB')
        d4_00029 = criar_d4_na('D4_00029', 'Previdência Social RREO 02 x MSC Dez')
        d4_00030 = criar_d4_na('D4_00030', 'Saúde RREO 02 x MSC Dez')
        d4_00031 = criar_d4_na('D4_00031', 'Educação RREO 02 x MSC Dez')
        d4_00032 = criar_d4_na('D4_00032', 'Demais Funções RREO 02 x MSC Dez')
        d4_00033 = criar_d4_na('D4_00033', 'Despesas intraorçamentárias RREO 02 x MSC Dez')
        d4_00034 = criar_d4_na('D4_00034', 'RPP/RPNP pagos MSC Dez x RREO 07')
        d4_00035 = criar_d4_na('D4_00035', 'Disponibilidade de Caixa Bruta RGF 5 x MSC Encerramento')
        d4_00036 = criar_d4_na('D4_00036', 'Disponibilidade de Caixa Bruta RGF 2 x MSC Encerramento')
        d4_00037 = criar_d4_na('D4_00037', 'Receitas com tributos estaduais MSC x RREO 06')
        d4_00038 = criar_d4_na('D4_00038', 'Receitas com tributos municipais MSC x RREO 06')
        d4_00039 = criar_d4_na('D4_00039', 'Transferências constitucionais estaduais MSC x RREO 06')
        d4_00040 = criar_d4_na('D4_00040', 'Transferências constitucionais municipais MSC x RREO 06')
        d4_00041 = criar_d4_na('D4_00041', 'Passivo Financeiro DCA AB >= RP inscritos + pendentes MSC Dez')
        d4_00042 = criar_d4_na('D4_00042', 'CAPAG: OFE RGF 5 Executivo >= valores restituíveis MSC Dez')
        d4_00043 = criar_d4_na('D4_00043', 'CAPAG: Recursos Não Vinculados (Disp. Caixa Bruta + RPs) — MSC Dez x RGF 5 Executivo')
        d4_00045 = criar_d4_na('D4_00045', 'CAPAG: Recursos Extraorçamentários RGF 5 Executivo >= valores restituíveis MSC Dez (1113*, FR 860–862/869)')
        d4_00046 = criar_d4_na('D4_00046', 'Contribuições dos segurados RREO Anexo 4 x DCA Anexo I-C')
        d4_00047 = criar_d4_na('D4_00047', 'Contribuições patronais RREO Anexo 4 x DCA Anexo I-C')
        d4_00048 = criar_d4_na('D4_00048', 'Restos a Pagar empenhados e não liquidados RGF 5 x DCA Anexo I-D')
        d4_00049 = criar_d4_na('D4_00049', 'Restos a Pagar liquidados e não pagos RGF 5 x DCA Anexo I-D')
        d4_00050 = criar_d4_na('D4_00050', 'Receitas de contribuições/patrimonial/agropecuária/industrial/serviços RREO 3 x DCA Anexo I-C')
        d4_00051 = criar_d4_na('D4_00051', 'Dedução da receita para formação do FUNDEB RREO 3 x DCA Anexo I-C')

        # Tabelas vazias
        d4_00001_t = pd.DataFrame()
        d4_00002_t = pd.DataFrame()
        d4_00003_t = pd.DataFrame()
        d4_00004_t = pd.DataFrame()
        d4_00005_t = pd.DataFrame()
        d4_00006_t = pd.DataFrame()
        d4_00007_t = pd.DataFrame()
        d4_00009_t = pd.DataFrame()
        d4_00010_t = pd.DataFrame()
        d4_00011_t = pd.DataFrame()
        d4_00012_t = pd.DataFrame()
        d4_00017_t = pd.DataFrame()
        d4_00019_t = pd.DataFrame()
        d4_00020_t = pd.DataFrame()
        d4_00021_t = pd.DataFrame()
        d4_00022_t = pd.DataFrame()
        d4_00023_t = pd.DataFrame()
        d4_00024_t = pd.DataFrame()
        d4_00025_t = pd.DataFrame()
        d4_00026_t = pd.DataFrame()
        d4_00027_t = pd.DataFrame()
        d4_00028_t = pd.DataFrame()
        d4_00029_t = pd.DataFrame()
        d4_00030_t = pd.DataFrame()
        d4_00031_t = pd.DataFrame()
        d4_00032_t = pd.DataFrame()
        d4_00033_t = pd.DataFrame()
        d4_00034_t = pd.DataFrame()
        d4_00035_t = pd.DataFrame()
        d4_00036_t = pd.DataFrame()
        d4_00037_t = pd.DataFrame()
        d4_00038_t = pd.DataFrame()
        d4_00039_t = pd.DataFrame()
        d4_00040_t = pd.DataFrame()
        d4_00041_t = pd.DataFrame()
        d4_00042_t = pd.DataFrame()
        d4_00043_t = pd.DataFrame()
        d4_00045_t = pd.DataFrame()
        d4_00046_t = pd.DataFrame()
        d4_00047_t = pd.DataFrame()
        d4_00048_t = pd.DataFrame()
        d4_00049_t = pd.DataFrame()
        d4_00050_t = pd.DataFrame()
        d4_00051_t = pd.DataFrame()

        # Respostas N/A
        resposta_d4_00001 = 'N/A'
        resposta_d4_00002 = 'N/A'
        resposta_d4_00003 = 'N/A'
        resposta_d4_00004 = 'N/A'
        resposta_d4_00005 = 'N/A'
        resposta_d4_00006 = 'N/A'
        resposta_d4_00007 = 'N/A'
        resposta_d4_00009 = 'N/A'
        resposta_d4_00010 = 'N/A'
        resposta_d4_00011 = 'N/A'
        resposta_d4_00012 = 'N/A'
        resposta_d4_00017 = 'N/A'
        resposta_d4_00019 = 'N/A'
        resposta_d4_00020 = 'N/A'
        resposta_d4_00021 = 'N/A'
        resposta_d4_00022 = 'N/A'
        resposta_d4_00023 = 'N/A'
        resposta_d4_00024 = 'N/A'
        resposta_d4_00025 = 'N/A'
        resposta_d4_00026 = 'N/A'
        resposta_d4_00027 = 'N/A'
        resposta_d4_00028 = 'N/A'
        resposta_d4_00029 = 'N/A'
        resposta_d4_00030 = 'N/A'
        resposta_d4_00031 = 'N/A'
        resposta_d4_00032 = 'N/A'
        resposta_d4_00033 = 'N/A'
        resposta_d4_00034 = 'N/A'
        resposta_d4_00035 = 'N/A'
        resposta_d4_00036 = 'N/A'
        resposta_d4_00037 = 'N/A'
        resposta_d4_00038 = 'N/A'
        resposta_d4_00039 = 'N/A'
        resposta_d4_00040 = 'N/A'
        resposta_d4_00041 = 'N/A'
        resposta_d4_00042 = 'N/A'
        resposta_d4_00043 = 'N/A'
        resposta_d4_00045 = 'N/A'
        resposta_d4_00046 = 'N/A'
        resposta_d4_00047 = 'N/A'
        resposta_d4_00048 = 'N/A'
        resposta_d4_00049 = 'N/A'
        resposta_d4_00050 = 'N/A'
        resposta_d4_00051 = 'N/A'

    ############################################
    #########  PARTE QUE EXECUTA A D4  #########
    ############################################

    else:
        def criar_d4_na_sem_dca(codigo, descricao):
            return pd.DataFrame([{
                'Dimensão': codigo,
                'Resposta': 'N/A',
                'Descrição da Dimensão': descricao,
                'Nota': None,
                'OBS': 'DCA não disponível — verificação exige cruzamento com o Balanço Anual (DCA)'
            }])

        if executar_d4_cruzamentos_dca:
            d4_00001, d4_00001_t = d4_analysis.d4_00001(df_rreo_1, df_dca_c)
            d4_00002, d4_00002_t = d4_analysis.d4_00002(df_rreo_1, df_dca_d)
            d4_00003, d4_00003_t = d4_analysis.d4_00003(df_rreo_2, df_dca_e)
            d4_00004, d4_00004_t = d4_analysis.d4_00004(df_rreo_2, df_dca_e)
            d4_00005, d4_00005_t = d4_analysis.d4_00005(df_rreo_7, df_dca_f)
            d4_00006, d4_00006_t = d4_analysis.d4_00006(df_rreo_7, df_dca_g)
            d4_00007, d4_00007_t = d4_analysis.d4_00007(df_rreo_7, df_dca_g)
            d4_00009, d4_00009_t = d4_analysis.d4_00009(df_rreo_3, df_dca_c, tipo_ente)
            d4_00010, d4_00010_t = d4_analysis.d4_00010(df_rreo_3, df_dca_c, tipo_ente)
            d4_00011, d4_00011_t = d4_analysis.d4_00011(df_rreo_3, df_dca_c, tipo_ente)
            d4_00012, d4_00012_t = d4_analysis.d4_00012(df_rreo_3, df_dca_c, tipo_ente)
            d4_00017, d4_00017_t = d4_analysis.d4_00017(df_rreo_3, df_dca_c)
            d4_00046, d4_00046_t = d4_analysis.d4_00046(df_rreo_4, df_dca_c)
            d4_00047, d4_00047_t = d4_analysis.d4_00047(df_rreo_4, df_dca_c)
            d4_00048, d4_00048_t = d4_analysis.d4_00048(df_dca_d, rgf_total)
            d4_00049, d4_00049_t = d4_analysis.d4_00049(df_dca_d, rgf_total)
            d4_00050, d4_00050_t = d4_analysis.d4_00050(df_rreo_3, df_dca_c)
            d4_00051, d4_00051_t = d4_analysis.d4_00051(df_rreo_3, df_dca_c)
            d4_00019, d4_00019_t = d4_analysis.d4_00019(df_rreo_9, df_dca_d)
            d4_00027, d4_00027_t = d4_analysis.d4_00027(df_dca_ab, df_rgf_2e)
            d4_00028, d4_00028_t = d4_analysis.d4_00028(df_dca_ab, rgf_total)
            d4_00041, d4_00041_t = d4_analysis.d4_00041(df_dca_ab, msc_dez)
        else:
            d4_00001 = criar_d4_na_sem_dca('D4_00001', 'Receita Realizada RREO x DCA')
            d4_00001_t = pd.DataFrame()
            d4_00002 = criar_d4_na_sem_dca('D4_00002', 'Execução da Despesa RREO x DCA')
            d4_00002_t = pd.DataFrame()
            d4_00003 = criar_d4_na_sem_dca('D4_00003', 'Despesa por Função RREO x DCA')
            d4_00003_t = pd.DataFrame()
            d4_00004 = criar_d4_na_sem_dca('D4_00004', 'Despesa por Função Intra RREO x DCA')
            d4_00004_t = pd.DataFrame()
            d4_00005 = criar_d4_na_sem_dca('D4_00005', 'Restos a Pagar RREO x DCA')
            d4_00005_t = pd.DataFrame()
            d4_00006 = criar_d4_na_sem_dca('D4_00006', 'Restos a Pagar NP RREO x DCA')
            d4_00006_t = pd.DataFrame()
            d4_00007 = criar_d4_na_sem_dca('D4_00007', 'Dívida Consolidada RREO x DCA')
            d4_00007_t = pd.DataFrame()
            d4_00009 = criar_d4_na_sem_dca('D4_00009', 'Receita de Impostos RREO x DCA')
            d4_00009_t = pd.DataFrame()
            d4_00010 = criar_d4_na_sem_dca('D4_00010', 'Receita de Impostos RREO x DCA')
            d4_00010_t = pd.DataFrame()
            d4_00011 = criar_d4_na_sem_dca('D4_00011', 'Transferências estaduais RREO x DCA')
            d4_00011_t = pd.DataFrame()
            d4_00012 = criar_d4_na_sem_dca('D4_00012', 'Transferências municipais RREO x DCA')
            d4_00012_t = pd.DataFrame()
            d4_00017 = criar_d4_na_sem_dca('D4_00017', 'Contribuições e compensações previdenciárias RREO x DCA')
            d4_00017_t = pd.DataFrame()
            d4_00046 = criar_d4_na_sem_dca('D4_00046', 'Contribuições dos segurados RREO Anexo 4 x DCA Anexo I-C')
            d4_00046_t = pd.DataFrame()
            d4_00047 = criar_d4_na_sem_dca('D4_00047', 'Contribuições patronais RREO Anexo 4 x DCA Anexo I-C')
            d4_00047_t = pd.DataFrame()
            d4_00048 = criar_d4_na_sem_dca('D4_00048', 'Restos a Pagar empenhados e não liquidados RGF 5 x DCA Anexo I-D')
            d4_00048_t = pd.DataFrame()
            d4_00049 = criar_d4_na_sem_dca('D4_00049', 'Restos a Pagar liquidados e não pagos RGF 5 x DCA Anexo I-D')
            d4_00049_t = pd.DataFrame()
            d4_00050 = criar_d4_na_sem_dca('D4_00050', 'Receitas de contribuições/patrimonial/agropecuária/industrial/serviços RREO 3 x DCA Anexo I-C')
            d4_00050_t = pd.DataFrame()
            d4_00051 = criar_d4_na_sem_dca('D4_00051', 'Dedução da receita para formação do FUNDEB RREO 3 x DCA Anexo I-C')
            d4_00051_t = pd.DataFrame()
            d4_00019 = criar_d4_na_sem_dca('D4_00019', 'Despesas de capital RREO x DCA')
            d4_00019_t = pd.DataFrame()
            d4_00027 = criar_d4_na_sem_dca('D4_00027', 'Disponibilidade de Caixa Bruta RGF 2 x DCA AB')
            d4_00027_t = pd.DataFrame()
            d4_00028 = criar_d4_na_sem_dca('D4_00028', 'Disponibilidade de Caixa Bruta RGF 5 x DCA AB')
            d4_00028_t = pd.DataFrame()
            d4_00041 = criar_d4_na_sem_dca('D4_00041', 'Passivo Financeiro DCA AB >= RP inscritos + pendentes MSC Dez')
            d4_00041_t = pd.DataFrame()

        d4_00020, d4_00020_t = d4_analysis.d4_00020(msc_dez, df_rreo_1)
        d4_00025, d4_00025_t = d4_analysis.d4_00025(msc_dez, df_rreo_1)
        d4_00026, d4_00026_t = d4_analysis.d4_00026(msc_dez, df_rreo_1)
        d4_00029, d4_00029_t = d4_analysis.d4_00029(df_rreo_2, emp_msc_dez)
        d4_00030, d4_00030_t = d4_analysis.d4_00030(df_rreo_2, emp_msc_dez)
        d4_00031, d4_00031_t = d4_analysis.d4_00031(df_rreo_2, emp_msc_dez)
        d4_00032, d4_00032_t = d4_analysis.d4_00032(df_rreo_2, emp_msc_dez)
        d4_00033, d4_00033_t = d4_analysis.d4_00033(df_rreo_2, emp_msc_dez)
        d4_00034, d4_00034_t = d4_analysis.d4_00034(msc_dez, df_rreo_7)
        d4_00035, d4_00035_t = d4_analysis.d4_00035(msc_encerr, rgf_total)
        d4_00036, d4_00036_t = d4_analysis.d4_00036(msc_encerr, df_rgf_2e)
        d4_00042, d4_00042_t = d4_analysis.d4_00042(msc_dez, df_rgf_5e, tipo_ente)
        d4_00043, d4_00043_t = d4_analysis.d4_00043(msc_dez, df_rgf_5e)
        d4_00045, d4_00045_t = d4_analysis.d4_00045(msc_dez, df_rgf_5e)
        if tipo_ente == "E":
            d4_00037, d4_00037_t = d4_analysis.d4_00037(receita, df_rreo_6)
            d4_00038 = pd.DataFrame([{
                'Dimensão': 'D4_00038',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade das receitas com tributos municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00038_t = pd.DataFrame()
            d4_00039, d4_00039_t = d4_analysis.d4_00039(receita, df_rreo_6)
            d4_00040 = pd.DataFrame([{
                'Dimensão': 'D4_00040',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00040_t = pd.DataFrame()
        else:
            d4_00038, d4_00038_t = d4_analysis.d4_00038(msc_dez, df_rreo_6)
            d4_00037 = pd.DataFrame([{
                'Dimensão': 'D4_00037',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade das receitas com tributos estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00037_t = pd.DataFrame()
            d4_00040, d4_00040_t = d4_analysis.d4_00040(msc_dez, df_rreo_6)
            d4_00039 = pd.DataFrame([{
                'Dimensão': 'D4_00039',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00039_t = pd.DataFrame()

        d4_vigencia = {
            'D4_00037': (2023, None),
            'D4_00038': (2023, None),
            'D4_00039': (2023, None),
            'D4_00040': (2023, None),
            'D4_00041': (2023, None),
            'D4_00042': (2024, None),
            'D4_00043': (2024, None),
            'D4_00045': (2024, None),
            'D4_00046': (2025, None),
            'D4_00047': (2025, None),
            'D4_00048': (2025, None),
            'D4_00049': (2025, None),
            'D4_00050': (2025, None),
            'D4_00051': (2025, None),
        }
        d4_00037, d4_00037_t = _aplicar_vigencia('D4_00037', 'Receitas com tributos estaduais MSC x RREO 06', d4_00037, d4_00037_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00038, d4_00038_t = _aplicar_vigencia('D4_00038', 'Receitas com tributos municipais MSC x RREO 06', d4_00038, d4_00038_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00039, d4_00039_t = _aplicar_vigencia('D4_00039', 'Transferências constitucionais estaduais MSC x RREO 06', d4_00039, d4_00039_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00040, d4_00040_t = _aplicar_vigencia('D4_00040', 'Transferências constitucionais municipais MSC x RREO 06', d4_00040, d4_00040_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00041, d4_00041_t = _aplicar_vigencia('D4_00041', 'Passivo Financeiro DCA AB >= RP inscritos + pendentes MSC Dez', d4_00041, d4_00041_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00042, d4_00042_t = _aplicar_vigencia('D4_00042', 'CAPAG: OFE RGF 5 Executivo >= valores restituíveis MSC Dez', d4_00042, d4_00042_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00043, d4_00043_t = _aplicar_vigencia('D4_00043', 'CAPAG: Recursos Não Vinculados (Disp. Caixa Bruta + RPs) — MSC Dez x RGF 5 Executivo', d4_00043, d4_00043_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00045, d4_00045_t = _aplicar_vigencia('D4_00045', 'CAPAG: Recursos Extraorçamentários RGF 5 Executivo >= valores restituíveis MSC Dez (1113*, FR 860–862/869)', d4_00045, d4_00045_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00046, d4_00046_t = _aplicar_vigencia('D4_00046', 'Contribuições dos segurados RREO Anexo 4 x DCA Anexo I-C', d4_00046, d4_00046_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00047, d4_00047_t = _aplicar_vigencia('D4_00047', 'Contribuições patronais RREO Anexo 4 x DCA Anexo I-C', d4_00047, d4_00047_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00048, d4_00048_t = _aplicar_vigencia('D4_00048', 'Restos a Pagar empenhados e não liquidados RGF 5 x DCA Anexo I-D', d4_00048, d4_00048_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00049, d4_00049_t = _aplicar_vigencia('D4_00049', 'Restos a Pagar liquidados e não pagos RGF 5 x DCA Anexo I-D', d4_00049, d4_00049_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00050, d4_00050_t = _aplicar_vigencia('D4_00050', 'Receitas de contribuições/patrimonial/agropecuária/industrial/serviços RREO 3 x DCA Anexo I-C', d4_00050, d4_00050_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        d4_00051, d4_00051_t = _aplicar_vigencia('D4_00051', 'Dedução da receita para formação do FUNDEB RREO 3 x DCA Anexo I-C', d4_00051, d4_00051_t, ano_vigencia_ranking, d4_vigencia, vigencia_csv)
        if tipo_ente == "E":
            d4_00021, d4_00021_t = d4_analysis.d4_00021(msc_dez, df_rreo_3)
            d4_00022 = pd.DataFrame([{
                'Dimensão': 'D4_00022',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas receitas com tributos municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00022_t = pd.DataFrame()
            d4_00023, d4_00023_t = d4_analysis.d4_00023(msc_dez, df_rreo_3)
            d4_00024 = pd.DataFrame([{
                'Dimensão': 'D4_00024',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais municipais',
                'Nota': None,
                'OBS': 'Aplicável apenas para municípios'
            }])
            d4_00024_t = pd.DataFrame()
        else:
            d4_00022, d4_00022_t = d4_analysis.d4_00022(msc_dez, df_rreo_3)
            d4_00021 = pd.DataFrame([{
                'Dimensão': 'D4_00021',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas receitas com tributos estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00021_t = pd.DataFrame()
            d4_00024, d4_00024_t = d4_analysis.d4_00024(msc_dez, df_rreo_3)
            d4_00023 = pd.DataFrame([{
                'Dimensão': 'D4_00023',
                'Resposta': 'N/A',
                'Descrição da Dimensão': 'Igualdade nas transferências constitucionais estaduais',
                'Nota': None,
                'OBS': 'Aplicável apenas para estados'
            }])
            d4_00023_t = pd.DataFrame()

        resposta_d4_00001 = d4_00001['Resposta'].iloc[0]
        resposta_d4_00002 = d4_00002['Resposta'].iloc[0]
        resposta_d4_00003 = d4_00003['Resposta'].iloc[0]
        resposta_d4_00004 = d4_00004['Resposta'].iloc[0]
        resposta_d4_00005 = d4_00005['Resposta'].iloc[0]
        resposta_d4_00006 = d4_00006['Resposta'].iloc[0]
        resposta_d4_00007 = d4_00007['Resposta'].iloc[0]
        resposta_d4_00009 = d4_00009['Resposta'].iloc[0]
        resposta_d4_00010 = d4_00010['Resposta'].iloc[0]
        resposta_d4_00011 = d4_00011['Resposta'].iloc[0]
        resposta_d4_00012 = d4_00012['Resposta'].iloc[0]
        resposta_d4_00017 = d4_00017['Resposta'].iloc[0]
        resposta_d4_00019 = d4_00019['Resposta'].iloc[0]
        resposta_d4_00020 = d4_00020['Resposta'].iloc[0]
        resposta_d4_00021 = d4_00021['Resposta'].iloc[0]
        resposta_d4_00022 = d4_00022['Resposta'].iloc[0]
        resposta_d4_00023 = d4_00023['Resposta'].iloc[0]
        resposta_d4_00024 = d4_00024['Resposta'].iloc[0]
        resposta_d4_00025 = d4_00025['Resposta'].iloc[0]
        resposta_d4_00026 = d4_00026['Resposta'].iloc[0]
        resposta_d4_00027 = d4_00027['Resposta'].iloc[0]
        resposta_d4_00028 = d4_00028['Resposta'].iloc[0]
        resposta_d4_00029 = d4_00029['Resposta'].iloc[0]
        resposta_d4_00030 = d4_00030['Resposta'].iloc[0]
        resposta_d4_00031 = d4_00031['Resposta'].iloc[0]
        resposta_d4_00032 = d4_00032['Resposta'].iloc[0]
        resposta_d4_00033 = d4_00033['Resposta'].iloc[0]
        resposta_d4_00034 = d4_00034['Resposta'].iloc[0]
        resposta_d4_00035 = d4_00035['Resposta'].iloc[0]
        resposta_d4_00036 = d4_00036['Resposta'].iloc[0]
        resposta_d4_00037 = d4_00037['Resposta'].iloc[0]
        resposta_d4_00038 = d4_00038['Resposta'].iloc[0]
        resposta_d4_00039 = d4_00039['Resposta'].iloc[0]
        resposta_d4_00040 = d4_00040['Resposta'].iloc[0]
        resposta_d4_00041 = d4_00041['Resposta'].iloc[0]
        resposta_d4_00042 = d4_00042['Resposta'].iloc[0]
        resposta_d4_00043 = d4_00043['Resposta'].iloc[0]
        resposta_d4_00045 = d4_00045['Resposta'].iloc[0]
        resposta_d4_00046 = d4_00046['Resposta'].iloc[0]
        resposta_d4_00047 = d4_00047['Resposta'].iloc[0]
        resposta_d4_00048 = d4_00048['Resposta'].iloc[0]
        resposta_d4_00049 = d4_00049['Resposta'].iloc[0]
        resposta_d4_00050 = d4_00050['Resposta'].iloc[0]
        resposta_d4_00051 = d4_00051['Resposta'].iloc[0]


    #############################################################################
    #############################################################################
    #############################################################################

    # Limpar mensagens de progresso após alguns segundos (opcional)
    st.markdown("---")
   

    # D1 removida/desativada neste aplicativo.
    d1 = pd.DataFrame(columns=["Dimensão", "Resposta", "Descrição da Dimensão", "Nota", "OBS"])

    # Consolidando a D2
    if executar_d2:
        # DCA disponível - consolidar verificações D2 normalmente
        if ano < 2024:
            d2_lista = [d2_00002, d2_00003, d2_00004, d2_00005, d2_00006, d2_00007, d2_00008, d2_00010,
                       d2_00011, d2_00012, d2_00013, d2_00014, d2_00015, d2_00016, d2_00017, d2_00018,
                       d2_00019, d2_00020, d2_00021, d2_00023, d2_00024, d2_00028, d2_00029, d2_00030,
                       d2_00031, d2_00032, d2_00033, d2_00034, d2_00035, d2_00036, d2_00037, d2_00038,
                       d2_00039, d2_00040, d2_00044]
            if tipo_ente == "E":
                d2_lista.append(d2_00045)
                d2_lista.append(d2_00047)
            else:
                d2_lista.append(d2_00046)
                d2_lista.append(d2_00048)
            d2_lista.append(d2_00049)
            d2_lista.append(d2_00050)
            d2_lista.append(d2_00051)
            d2_lista.append(d2_00052)
            d2_lista.append(d2_00053)
            d2_lista.append(d2_00054)
            d2_lista.append(d2_00055)
            d2_lista.append(d2_00058)
            d2_lista.append(d2_00059)
            d2_lista.append(d2_00060)
            d2_lista.append(d2_00061)
            d2_lista.append(d2_00066)
            d2_lista.append(d2_00067)
            d2_lista.append(d2_00068)
            d2_lista.append(d2_00069)
            d2_lista.append(d2_00070)
            d2_lista.append(d2_00071)
            d2_lista.append(d2_00072)
            d2_lista.append(d2_00073)
            d2_lista.append(d2_00074)
            d2_lista.append(d2_00076)
            d2_lista.append(d2_00077)
            d2_lista.append(d2_00079)
            d2_lista.append(d2_00080)
            d2_lista.append(d2_00081)
            d2_lista.append(d2_00082)
            d2_lista.append(d2_00083)
            d2_lista.append(d2_00084)
            d2_lista.append(d2_00085)
            d2_lista.append(d2_00086)
            d2_lista.append(d2_00087)
            d2_lista.append(d2_00088)
            d2_lista.append(d2_00093)
            d2_lista.append(d2_00094)
            d2_lista.append(d2_00095)
            d2_lista.append(d2_00089)
            if tipo_ente == "M":
                d2_lista.append(d2_00099)
            if ano >= 2025:
                d2_lista.append(d2_00100)
                d2_lista.append(d2_00101)
                d2_lista.append(d2_00102)
                d2_lista.append(d2_00103)
                d2_lista.append(d2_00104)
                d2_lista.append(d2_00105)
            d2 = pd.concat(d2_lista, ignore_index=True)
        else:
            d2_lista = [d2_00002, d2_00003, d2_00004, d2_00005, d2_00006, d2_00007, d2_00008, d2_00010,
                       d2_00011, d2_00012, d2_00013, d2_00014, d2_00015, d2_00016, d2_00017, d2_00018,
                       d2_00019, d2_00020, d2_00021, d2_00023, d2_00024, d2_00028, d2_00029, d2_00030,
                       d2_00031, d2_00032, d2_00033, d2_00034, d2_00035, d2_00036, d2_00037,
                       d2_00039, d2_00040, d2_00044]
            if tipo_ente == "E":
                d2_lista.append(d2_00045)
                d2_lista.append(d2_00047)
            else:
                d2_lista.append(d2_00046)
                d2_lista.append(d2_00048)
            d2_lista.append(d2_00049)
            d2_lista.append(d2_00050)
            d2_lista.append(d2_00051)
            d2_lista.append(d2_00052)
            d2_lista.append(d2_00053)
            d2_lista.append(d2_00054)
            d2_lista.append(d2_00055)
            d2_lista.append(d2_00058)
            d2_lista.append(d2_00059)
            d2_lista.append(d2_00060)
            d2_lista.append(d2_00061)
            d2_lista.append(d2_00066)
            d2_lista.append(d2_00067)
            d2_lista.append(d2_00068)
            d2_lista.append(d2_00069)
            d2_lista.append(d2_00070)
            d2_lista.append(d2_00071)
            d2_lista.append(d2_00072)
            d2_lista.append(d2_00073)
            d2_lista.append(d2_00074)
            d2_lista.append(d2_00076)
            d2_lista.append(d2_00079)
            d2_lista.append(d2_00081)
            d2_lista.append(d2_00082)
            d2_lista.append(d2_00083)
            d2_lista.append(d2_00084)
            d2_lista.append(d2_00085)
            d2_lista.append(d2_00086)
            d2_lista.append(d2_00087)
            d2_lista.append(d2_00088)
            d2_lista.append(d2_00093)
            d2_lista.append(d2_00094)
            d2_lista.append(d2_00095)
            d2_lista.append(d2_00089)
            if tipo_ente == "M":
                d2_lista.append(d2_00099)
            if ano >= 2025:
                d2_lista.append(d2_00100)
                d2_lista.append(d2_00101)
                d2_lista.append(d2_00102)
                d2_lista.append(d2_00103)
                d2_lista.append(d2_00104)
                d2_lista.append(d2_00105)
            d2 = pd.concat(d2_lista, ignore_index=True)
    else:
        # DCA não disponível - criar DataFrame N/A para D2
        d2 = pd.DataFrame([{
            'Dimensão': 'D2_NA',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Dimensão D2 não disponível - Requer DCA (Balanço Anual)',
            'Nota': 0,
            'OBS': 'DCA não enviada para este exercício'
        }])

    # Consolidando a partir da D2
    d1 = pd.concat([d1, d2], ignore_index=True)

    # Consolidando a D3
    if executar_d3:
        # RREO completo disponível - consolidar verificações D3 normalmente
        d3 = pd.concat([d3_00001, d3_00002, d3_00005, d3_00006, d3_00008, d3_00009, d3_00010, d3_00011, d3_00012, d3_00013, d3_00014, d3_00015, d3_00016, d3_00017, d3_00021, d3_00022, d3_00023, d3_00024, d3_00025, d3_00026, d3_00027, d3_00028, d3_00029, d3_00030, d3_00032, d3_00033, d3_00034, d3_00035, d3_00037, d3_00038, d3_00039, d3_00040, d3_00044, d3_00045, d3_00046, d3_00048, d3_00049, d3_00050, d3_00051, d3_00052, d3_00054, d3_00055, d3_00056], ignore_index=True)
    else:
        # RREO não completo - criar DataFrame N/A para D3
        d3 = pd.DataFrame([{
            'Dimensão': 'D3_NA',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Dimensão D3 não disponível - Requer RREO completo (6º bimestre)',
            'Nota': 0,
            'OBS': 'RREO 6º bimestre não enviado para este exercício'
        }])

    # Consolidando D2 + D3
    d1 = pd.concat([d1, d3], ignore_index=True)

    # Consolidando a D4 (lista base): com RREO 6º; verificações sem DCA entram como N/A ou resultado conforme o caso
    if executar_d4:
        d4_lista = [d4_00001, d4_00002, d4_00003, d4_00004, d4_00005, d4_00006, d4_00007, d4_00017, d4_00046, d4_00047, d4_00048, d4_00049, d4_00050, d4_00051, d4_00019, d4_00020,
                    d4_00025, d4_00026, d4_00027, d4_00028, d4_00029, d4_00030, d4_00031, d4_00032,
                    d4_00033, d4_00034, d4_00035, d4_00036, d4_00041, d4_00042, d4_00043, d4_00045]
        # Adicionar D4_00009 apenas para Estados
        if tipo_ente == "E":
            d4_lista.append(d4_00009)
            d4_lista.append(d4_00011)
            d4_lista.append(d4_00021)
            d4_lista.append(d4_00023)
            d4_lista.append(d4_00037)
            d4_lista.append(d4_00039)
        else:
            d4_lista.append(d4_00010)
            d4_lista.append(d4_00012)
            d4_lista.append(d4_00022)
            d4_lista.append(d4_00024)
            d4_lista.append(d4_00038)
            d4_lista.append(d4_00040)
        d4 = pd.concat(d4_lista, ignore_index=True)
    else:
        d4 = pd.DataFrame([{
            'Dimensão': 'D4_NA',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Dimensão D4 não disponível — requer RREO completo (6º bimestre)',
            'Nota': 0,
            'OBS': 'RREO 6º bimestre não enviado para este exercício'
        }])

    # Consolidando TODAS (D2 + D3 + D4)
    final = pd.concat([d1, d4], ignore_index=True)
    final["_ord_dim"] = final["Dimensão"].map(_chave_ordenacao_dimensao)
    final = final.sort_values("_ord_dim").drop(columns=["_ord_dim"]).reset_index(drop=True)
    final = filtrar_verificacoes_cruzamentos(final)



    st.divider()


    # Acertos/erros por dimensão — calculados após dimensoes_configuradas (ver abaixo).
    # Variáveis inicializadas aqui para que referências anteriores a dimensoes_configuradas
    # não gerem NameError; os valores definitivos são atribuídos logo após _mask_configuradas.
    d1_acertos = d2_acertos = d3_acertos = d4_acertos = 0
    d1_erros   = d2_erros   = d3_erros   = d4_erros   = 0
    total_acertos_geral = total_erros_geral = 0

    _mask_capag_resumo = final.apply(
        lambda r: eh_verificacao_capag(str(r.get("Dimensão", "")), r.get("Descrição da Dimensão")),
        axis=1,
    )
    _final_capag_resumo = final.loc[_mask_capag_resumo]
    _resp_capag = _final_capag_resumo["Resposta"].astype(str)
    capag_acertos = int(_resp_capag.str.startswith("OK").sum())
    capag_erros = int((_resp_capag == "ERRO").sum())
    capag_classificadas = capag_acertos + capag_erros
    capag_total_linhas = int(len(_final_capag_resumo))

    def _eh_d1_entrega_ou_tempestividade(codigo):
        if not (isinstance(codigo, str) and codigo.startswith('D1_')):
            return False
        sufixo = codigo.split('_')[-1]
        if not sufixo.isdigit():
            return False
        numero = int(sufixo)
        return 1 <= numero <= 16

    verificacoes_base_total = set()
    # Ano efetivamente usado como referência da base oficial.
    # Quando há base do próprio ano, é igual a `ano`; caso contrário, vira o
    # ano fechado mais recente disponível para o ente (fallback).
    ano_base_oficial = None
    try:
        codigo_ente_base = str(ente_row[coluna_codigo])
        if tipo_ente == "E":
            base_filtro = df_base[
                (df_base['VA_EXERCICIO'] == ano)
                & (df_base[coluna_codigo].astype(str) == codigo_ente_base)
            ]
            if not base_filtro.empty:
                ano_base_oficial = ano
            else:
                base_filtro = df_base[df_base[coluna_codigo].astype(str) == codigo_ente_base]
                if not base_filtro.empty:
                    ano_ref = int(base_filtro['VA_EXERCICIO'].max())
                    base_filtro = base_filtro[base_filtro['VA_EXERCICIO'] == ano_ref]
                    ano_base_oficial = ano_ref
            if 'NO_VERIFICACAO' in base_filtro.columns:
                verificacoes_base_total = set(base_filtro['NO_VERIFICACAO'].dropna().astype(str).unique())
        else:
            base_filtro = df_base[
                (df_base['VA_EXERCICIO'] == ano)
                & (df_base[coluna_codigo].astype(str) == codigo_ente_base)
            ]
            if not base_filtro.empty:
                ano_base_oficial = ano
            else:
                base_filtro = df_base[df_base[coluna_codigo].astype(str) == codigo_ente_base]
                if not base_filtro.empty:
                    ano_ref = int(base_filtro['VA_EXERCICIO'].max())
                    base_filtro = base_filtro[base_filtro['VA_EXERCICIO'] == ano_ref]
                    ano_base_oficial = ano_ref
            if not base_filtro.empty:
                linha_base = base_filtro.iloc[0]
                colunas_verificacao_base = [
                    col for col in df_base.columns
                    if col.startswith(('D1_', 'D2_', 'D3_', 'D4_')) and len(col) == 8
                ]
                verificacoes_base_total = {
                    col for col in colunas_verificacao_base
                    if pd.notna(linha_base.get(col))
                }
    except Exception:
        verificacoes_base_total = set()
        ano_base_oficial = None
    verificacoes_base_total = verificacoes_base_total.intersection(VERIFICACOES_CRUZAMENTOS)

    base_e_fallback = (ano_base_oficial is not None) and (ano_base_oficial != ano)
    _label_ano_base = f"{ano_base_oficial}" if ano_base_oficial else str(ano)
    # Derivada da configuração central no topo do arquivo.
    modo_consulta_publica = FLAG_MODO_CONSULTA_PUBLICA and (ano >= ANO_INICIO_CONSULTA_PUBLICA)

    verificacoes_passiveis = {
        v for v in verificacoes_base_total if not _eh_d1_entrega_ou_tempestividade(v)
    }

    _respostas_definitivas = final['Resposta'].astype(str)
    dimensoes_configuradas = {
        d
        for d, r in zip(final['Dimensão'].dropna().astype(str), _respostas_definitivas)
        if d.startswith(('D1_', 'D2_', 'D3_', 'D4_'))
        and len(d) == 8
        and d.split('_')[-1].isdigit()
        and (r.startswith('OK') or r == 'ERRO')
    }
    dimensoes_configuradas = {
        d for d in dimensoes_configuradas if not _eh_d1_entrega_ou_tempestividade(d)
    }
    # Verificações novas do app (OK/ERRO) que ainda não constam na base oficial da STN.
    _novas_app_ok_erro = {
        d for d in dimensoes_configuradas
        if d not in verificacoes_base_total
    }
    if verificacoes_passiveis:
        _config_oficial = dimensoes_configuradas.intersection(verificacoes_passiveis)
    else:
        _config_oficial = set()
    if modo_consulta_publica:
        dimensoes_configuradas = _config_oficial | _novas_app_ok_erro
    else:
        dimensoes_configuradas = _config_oficial

    total_ranking_ano = len(verificacoes_base_total)
    # Inclui as novas verificações do app (fora da base oficial) no denominador passível,
    # garantindo que o percentual não ultrapasse 100%.
    total_passiveis_analise = len(verificacoes_passiveis) + (
        len(_novas_app_ok_erro) if modo_consulta_publica else 0
    )
    total_configuradas = len(dimensoes_configuradas)
    perc_configuradas = (
        (total_configuradas / total_passiveis_analise) * 100
        if total_passiveis_analise > 0 else 0.0
    )

    _mask_configuradas = final['Dimensão'].astype(str).isin(dimensoes_configuradas)
    soma_notas_obtidas = pd.to_numeric(
        final.loc[_mask_configuradas, 'Nota'], errors='coerce'
    ).fillna(0).sum()
    perc_pontos_obtidos = (
        (soma_notas_obtidas / total_configuradas) * 100
        if total_configuradas > 0 else 0.0
    )

    # Recalcula acertos/erros somente sobre as verificações em dimensoes_configuradas,
    # garantindo coerência com total_configuradas (exclui N/A, D1_00001-16 e não-passíveis).
    _resp_config = final.loc[_mask_configuradas, 'Resposta'].astype(str)
    _dim_config  = final.loc[_mask_configuradas, 'Dimensão'].astype(str)
    total_acertos_geral = int(_resp_config.str.startswith('OK').sum())
    total_erros_geral   = int((_resp_config == 'ERRO').sum())
    d1_acertos = int(_resp_config[_dim_config.str.startswith('D1_')].str.startswith('OK').sum())
    d1_erros   = int((_resp_config[_dim_config.str.startswith('D1_')] == 'ERRO').sum())
    d2_acertos = int(_resp_config[_dim_config.str.startswith('D2_')].str.startswith('OK').sum())
    d2_erros   = int((_resp_config[_dim_config.str.startswith('D2_')] == 'ERRO').sum())
    d3_acertos = int(_resp_config[_dim_config.str.startswith('D3_')].str.startswith('OK').sum())
    d3_erros   = int((_resp_config[_dim_config.str.startswith('D3_')] == 'ERRO').sum())
    d4_acertos = int(_resp_config[_dim_config.str.startswith('D4_')].str.startswith('OK').sum())
    d4_erros   = int((_resp_config[_dim_config.str.startswith('D4_')] == 'ERRO').sum())

    # Exibir cards de métricas com destaque visual
    st.markdown("### 📊 Resultados das Verificações")
    _badge_fallback = (
        f'<span style="background:#fff4e6; border:1px solid #ffd8a8; border-radius:999px; '
        f'padding:4px 10px; font-size:0.82rem; color:#c2410c;">'
        f'⚠️ Sem ranking oficial publicado para {ano} — referência da última base oficial fechada ({_label_ano_base})'
        f'</span>'
        if base_e_fallback else '<!-- sem fallback -->'
    )
    _label_total_ranking = (
        f"Total do Ranking {_label_ano_base} (base oficial fechada)"
        if base_e_fallback else f"Total do Ranking {_label_ano_base}"
    )
    _consulta_com_novas = bool(modo_consulta_publica and _novas_app_ok_erro)
    _passiveis_partes = []
    if base_e_fallback:
        _passiveis_partes.append(f"base {_label_ano_base}")
    if _consulta_com_novas:
        _passiveis_partes.append("novas verificações configuradas no app")
    _label_passiveis = (
        f"Passíveis de análise ({' + '.join(_passiveis_partes)})"
        if _passiveis_partes else "Passíveis de análise"
    )
    _legenda_passiveis = (
        f"Excluindo D1_00001 a D1_00016. Inclui {len(_novas_app_ok_erro)} novas em consulta pública configurada(s) no app."
        if (modo_consulta_publica and _novas_app_ok_erro) else "(exclui D1_00001 a D1_00016)"
    )
    if total_passiveis_analise > 0:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f5 100%); border: 1px solid #dee2e6;
                        border-radius: 12px; padding: 14px 16px; margin: 0 0 14px 0;">
                <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px; color:#495057;">
                    <span style="background:#ffffff; border:1px solid #dee2e6; border-radius:999px; padding:4px 10px; font-size:0.86rem;">
                        <strong>Ano selecionado:</strong> {ano}
                    </span>
                    <span style="background:#ffffff; border:1px solid #dee2e6; border-radius:999px; padding:4px 10px; font-size:0.86rem;">
                        <strong>Ente:</strong> {cod} ({ente})
                    </span>
                    {_badge_fallback}
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:10px;">
                    <div style="background:#ffffff; border:1px solid #e9ecef; border-radius:10px; padding:10px 12px;">
                        <div style="font-size:0.78rem; color:#6c757d; text-transform:uppercase; letter-spacing:0.4px;">{_label_total_ranking}</div>
                        <div style="font-size:1.35rem; color:#212529; font-weight:700;">{total_ranking_ano}</div>
                    </div>
                    <div style="background:#ffffff; border:1px solid #e9ecef; border-radius:10px; padding:10px 12px;">
                        <div style="font-size:0.78rem; color:#6c757d; text-transform:uppercase; letter-spacing:0.4px;">{_label_passiveis}</div>
                        <div style="font-size:1.35rem; color:#212529; font-weight:700;">{total_passiveis_analise}</div>
                        <div style="font-size:0.75rem; color:#868e96;">{_legenda_passiveis}</div>
                    </div>
                    <div style="background:#ffffff; border:1px solid #e9ecef; border-radius:10px; padding:10px 12px;">
                        <div style="font-size:0.78rem; color:#6c757d; text-transform:uppercase; letter-spacing:0.4px;">Analisadas no app</div>
                        <div style="font-size:1.35rem; color:#0b7285; font-weight:700;">{total_configuradas} ({perc_configuradas:.1f}%)</div>
                    </div>
                    <div style="background:#fff9db; border:1px solid #ffe066; border-radius:10px; padding:10px 12px;">
                        <div style="font-size:0.78rem; color:#6c757d; text-transform:uppercase; letter-spacing:0.4px;">Pontos obtidos (estimativa aproximada do app)</div>
                        <div style="display:flex; align-items:baseline; gap:8px;">
                            <div style="font-size:1.8rem; color:#5f3dc4; font-weight:800;">{perc_pontos_obtidos:.1f}%</div>
                            <div style="font-size:0.9rem; color:#868e96; font-weight:500;">{soma_notas_obtidas:.2f} / {total_configuradas} pts</div>
                        </div>
                        <div style="font-size:0.72rem; color:#e67700; margin-top:4px;">
                            ⚠️ Valor estimado (não oficial) com base nos dados calculados e configurados no app (sujeito a variações em relação ao resultado oficial)
                        </div>
                    </div>
                </div>
                <div style="margin-top:10px; font-size:0.95rem; color:#495057;">
                    Das <strong>{total_configuradas}</strong> verificações:
                    <span style="color:#198754; font-weight:600;">✅ {total_acertos_geral} acerto(s)</span> ·
                    <span style="color:#dc3545; font-weight:600;">❌ {total_erros_geral} erro(s)</span>
                </div>
                <div style="margin-top:10px; padding-top:10px; border-top:1px solid #e9ecef; font-size:0.92rem; color:#495057;">
                    <strong style="color:#5f3dc4;">CAPAG</strong> — entre as verificações deste escopo no resultado (base oficial {_label_ano_base})
                    (<strong>{capag_total_linhas}</strong> linha(s) na tabela abaixo),
                    <strong>{capag_classificadas}</strong> com resultado <strong>OK/ERRO</strong>:
                    <span style="color:#198754; font-weight:600;">✅ {capag_acertos} acerto(s)</span>
                    ·
                    <span style="color:#dc3545; font-weight:600;">❌ {capag_erros} erro(s)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.caption(
            f'Nenhuma verificação passível de análise automática para {cod} ({ente}) no exercício {ano}.'
        )

    # Expander: verificações passíveis mas sem resultado OK/ERRO para este ente
    if verificacoes_passiveis:
        nao_analisadas = sorted(verificacoes_passiveis - dimensoes_configuradas)
        if nao_analisadas:
            label_exp = (
                f"⚠️ {len(nao_analisadas)} verificação(ões) da base oficial {_label_ano_base} sem análise concluída para este ente"
            )
            with st.expander(label_exp, expanded=False):
                _texto_origem = (
                    f"da base oficial fechada de **{_label_ano_base}** (referência usada enquanto "
                    f"o ranking de {ano} não é publicado)"
                    if base_e_fallback
                    else f"da base oficial do ranking **{_label_ano_base}**"
                )
                st.caption(
                    f"Estas verificações constam {_texto_origem} para o ente selecionado, "
                    "mas não produziram resultado OK ou ERRO no app. "
                    "Isso pode ocorrer por pendência de implementação ou porque a metodologia "
                    "exige cruzamento com bases externas que não estão disponíveis na API pública do SICONFI."
                )
                codigos_base_externa = {"D2_00097"}
                nao_analisadas_base_externa = sorted(set(nao_analisadas) & codigos_base_externa)
                if nao_analisadas_base_externa:
                    st.info(
                        "ℹ️ **Casos com dependência de base externa à API**: "
                        + ", ".join(nao_analisadas_base_externa)
                    )
                    st.caption(
                        "Exemplo — **D2_00097 (CAPAG)**: a metodologia STN compara o total de "
                        "transferências especiais de emendas individuais transferidas pela União "
                        "com o total de receitas dessas transferências registradas pelo ente. "
                        "Parte desse cruzamento depende de dados do Tesouro/Portal da Transparência, "
                        "que não vêm no endpoint `msc_orcamentaria`."
                    )
                # Agrupa por dimensão para leitura mais fácil
                grupos: dict[str, list[str]] = {}
                for cod_v in nao_analisadas:
                    dim = cod_v.split('_')[0]
                    grupos.setdefault(dim, []).append(cod_v)
                for dim, codigos in sorted(grupos.items()):
                    st.markdown(f"**{dim}** — {len(codigos)} verificação(ões)")
                    st.code(", ".join(codigos), language=None)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D2 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d2_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d2_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D3 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d3_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d3_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #ced4da;">
            <h4 style="color: #343a40; margin: 0;">D4 - Análise</h4>
            <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                <div>
                    <div style="color: #28a745; font-weight: 700;">✅ Acertos</div>
                    <div style="font-size: 28px; color: #155724;">{d4_acertos}</div>
                </div>
                <div>
                    <div style="color: #dc3545; font-weight: 700;">❌ Erros</div>
                    <div style="font-size: 28px; color: #721c24;">{d4_erros}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        (
            f"Os cards D2–D4 e CAPAG consideram a base oficial de {_label_ano_base} "
            f"(fallback enquanto o ranking {ano} não está publicado)."
            if base_e_fallback
            else f"Os cards D2–D4 e CAPAG consideram a base oficial de {_label_ano_base}."
        )
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------------------
    # Painel: Novas verificações sob consulta pública STN 2025.
    # Controlado por `modo_consulta_publica`, derivado da configuração central.
    # ---------------------------------------------------------------------------------
    if modo_consulta_publica:
        _novas_consulta_2025_d1 = {
            'D1_00039', 'D1_00040', 'D1_00041', 'D1_00042', 'D1_00043', 'D1_00044',
        }
        _novas_consulta_2025_d2 = {
            'D2_00100', 'D2_00101', 'D2_00102', 'D2_00103', 'D2_00104', 'D2_00105',
        }
        _novas_consulta_2025_d3 = {'D3_00046', 'D3_00048', 'D3_00049', 'D3_00050', 'D3_00051', 'D3_00052', 'D3_00054', 'D3_00055', 'D3_00056'}
        _novas_consulta_2025_d4 = {'D4_00046', 'D4_00047', 'D4_00048', 'D4_00049', 'D4_00050', 'D4_00051'}
        # Total de verificações novas sob consulta pública (todas as dimensões)
        _total_novas_consulta = 46
        # Passíveis de análise automática (confirmadas na metodologia sob consulta)
        _passiveis_novas_consulta = 41
        # Configuradas no app até o momento
        _novas_consulta_todas = (
            _novas_consulta_2025_d1
            | _novas_consulta_2025_d2
            | _novas_consulta_2025_d3
            | _novas_consulta_2025_d4
        )
        _novas_configuradas_no_app = {
            d for d, r in zip(final['Dimensão'].dropna().astype(str), final['Resposta'].astype(str))
            if d in _novas_consulta_todas and (r.startswith('OK') or r == 'ERRO')
        }
        _n_config = len(_novas_configuradas_no_app)
        _n_config_d1 = len(_novas_configuradas_no_app & _novas_consulta_2025_d1)
        _n_config_d2 = len(_novas_configuradas_no_app & _novas_consulta_2025_d2)
        _n_config_d3 = len(_novas_configuradas_no_app & _novas_consulta_2025_d3)
        _n_config_d4 = len(_novas_configuradas_no_app & _novas_consulta_2025_d4)

        _acertos_novas = sum(
            1 for d, r in zip(final['Dimensão'].astype(str), final['Resposta'].astype(str))
            if d in _novas_configuradas_no_app and r.startswith('OK')
        )
        _erros_novas = sum(
            1 for d, r in zip(final['Dimensão'].astype(str), final['Resposta'].astype(str))
            if d in _novas_configuradas_no_app and r == 'ERRO'
        )

        with st.expander("🔎 Novas verificações – Sob Consulta Pública STN 2025 (prévia)", expanded=False):
            st.caption(
                "Estas verificações integram a metodologia do ranking 2025 divulgada pela STN "
                "e estão sendo progressivamente configuradas no app. "
                "Os números abaixo são separados do painel principal, que segue referenciado "
                f"na base oficial fechada (exercício {_label_ano_base}). "
                "Quando a base de 2025 for homologada, desative FLAG_MODO_CONSULTA_PUBLICA no topo da página para ocultar este painel."
            )
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #e8f4fd 0%, #dbeafe 100%);
                            border: 1px solid #93c5fd; border-radius: 12px;
                            padding: 14px 16px; margin: 6px 0 10px 0;">
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:10px;">
                        <div style="background:#fff; border:1px solid #bfdbfe; border-radius:10px; padding:10px 12px;">
                            <div style="font-size:0.76rem; color:#6c757d; text-transform:uppercase;">Total sob consulta</div>
                            <div style="font-size:1.4rem; color:#1e40af; font-weight:700;">{_total_novas_consulta}</div>
                        </div>
                        <div style="background:#fff; border:1px solid #bfdbfe; border-radius:10px; padding:10px 12px;">
                            <div style="font-size:0.76rem; color:#6c757d; text-transform:uppercase;">Passíveis de análise</div>
                            <div style="font-size:1.4rem; color:#1e40af; font-weight:700;">{_passiveis_novas_consulta}</div>
                        </div>
                        <div style="background:#fff; border:1px solid #bfdbfe; border-radius:10px; padding:10px 12px;">
                            <div style="font-size:0.76rem; color:#6c757d; text-transform:uppercase;">Configuradas no app</div>
                            <div style="font-size:1.4rem; color:#1e40af; font-weight:700;">{_n_config}</div>
                            <div style="font-size:0.75rem; color:#868e96;">D1: {_n_config_d1} · D2: {_n_config_d2} · D3: {_n_config_d3} · D4: {_n_config_d4}</div>
                        </div>
                        <div style="background:#fff; border:1px solid #bfdbfe; border-radius:10px; padding:10px 12px;">
                            <div style="font-size:0.76rem; color:#6c757d; text-transform:uppercase;">Resultado (app)</div>
                            <div style="font-size:0.95rem; margin-top:4px;">
                                <span style="color:#198754; font-weight:600;">✅ {_acertos_novas} acerto(s)</span>
                                &nbsp;·&nbsp;
                                <span style="color:#dc3545; font-weight:600;">❌ {_erros_novas} erro(s)</span>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    


    # Coluna CAPAG só na visualização (export Excel mantém colunas originais)
    _capag_series = final.apply(
        lambda r: 'Sim'
        if eh_verificacao_capag(str(r.get('Dimensão', '')), r.get('Descrição da Dimensão'))
        else '',
        axis=1,
    )
    final_view = final.copy()
    final_view.insert(1, 'CAPAG', _capag_series)

    # Formatar a nota com 2 casas decimais e ocultar o índice
    final_styled = final_view.style.apply(highlight_resposta, axis=1).format({
        'Nota': '{:.2f}'
    }).hide(axis='index')

    # Configurar larguras das colunas (usar pixels para maior controle)
    # Ajustar altura da tabela automaticamente conforme quantidade de linhas
    # Fórmula: altura do cabeçalho (38px) + (número de linhas × altura da linha (35px)) + margem (10px)
    num_linhas = len(final_view)
    altura_tabela = 38 + (num_linhas * 35) + 10

    # Definir altura mínima de 100px e máxima de 500px
    altura_tabela = max(100, min(altura_tabela, 500))

    st.dataframe(
        final_styled,
        use_container_width=True,
        height=altura_tabela,
        hide_index=True,
        column_config={
            "Dimensão": st.column_config.TextColumn("Dimensão", width=80),
            "CAPAG": st.column_config.TextColumn("CAPAG", width=52, help="Sim = métrica no escopo CAPAG (Ranking STN)"),
            "Resposta": st.column_config.TextColumn("Resposta", width=80),
            "Descrição da Dimensão": st.column_config.TextColumn("Descrição da Dimensão", width=280),
            "Nota": st.column_config.NumberColumn("Nota", width=80, format="%.2f"),
            "OBS": st.column_config.TextColumn("OBS", width=250)
        }
    )


    #####################################################################################
    #####################################################################################

    # Exportar resultados + comparação (fragmento: não reexecuta API/análises ao baixar ou carregar ficheiros)
    st.session_state["_final_df_export"] = final.copy()
    st.session_state["_export_meta"] = {"cod": cod, "ente": ente, "ano": ano}
    fragmento_resultados_excel_e_comparar()

    status_text.text("📊 Gerando resultados...")
    progress_bar.progress(92)


    


    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################
    #####################################################################################


    #############################################################################
    # EXPANDERS AGRUPADOS POR DIMENSÃO (USANDO TABS)
    #############################################################################

    # Contar acertos/erros de cada dimensão
    d2_apenas = final[final['Dimensão'].str.startswith('D2_')]
    d2_acertos_tab = len(d2_apenas[d2_apenas['Nota'] >= 0.99])
    d2_total_tab = len(d2_apenas)

    d3_apenas = final[final['Dimensão'].str.startswith('D3_')]
    d3_acertos_tab = len(d3_apenas[d3_apenas['Nota'] >= 0.99])
    d3_total_tab = len(d3_apenas)

    d4_apenas = final[final['Dimensão'].str.startswith('D4_')]
    d4_acertos_tab = len(d4_apenas[d4_apenas['Nota'] >= 0.99])
    d4_total_tab = len(d4_apenas)

    st.divider()

    st.markdown("### 🧮 Análise das Verificações por Dimensão")

    # Criar tabs para cada dimensão ativa
    tab_d2, tab_d3, tab_d4 = st.tabs([
        f"🔍 D2 - DCA ({d2_acertos_tab}/{d2_total_tab} OK)",
        f"🔍 D3 - RREO/RGF ({d3_acertos_tab}/{d3_total_tab} OK)",
        f"🔍 D4 - DCA x RREO ({d4_acertos_tab}/{d4_total_tab} OK)"
    ])


    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################

    # =========================================================================
    # TAB D2 - QUALIDADE DOS DADOS DCA E MSC
    # =========================================================================
    with tab_d2:
        render_tab_d2(tab_d2, locals())

    # =========================================================================
    # TAB D3 - CRUZAMENTO RREO/RGF
    # =========================================================================
    with tab_d3:
        render_tab_d3(tab_d3, locals())

    # =========================================================================
    # TAB D4 - CRUZAMENTO DCA x RREO
    # =========================================================================
    with tab_d4:
        render_tab_d4(tab_d4, locals())




    # Finalizar
    progress_bar.progress(100)
    status_text.text("✅ Análise concluída com sucesso!")
    st.success("🎉 Todos os dados foram carregados e processados!")


    # Rodapé
    st.markdown("---")
    st.markdown(
        f"""
    <div style='text-align: center; color: #666;'>
        <small>CRUZAMENTOS SICONFI | Desenvolvido por Marcelo Jandussi | © {pd.Timestamp.today().year}</small>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Executar a função principal
if __name__ == "__main__":
    main()



