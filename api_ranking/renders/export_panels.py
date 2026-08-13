"""Painéis Streamlit das exportações e da comparação de resultados."""

import re

import pandas as pd
import streamlit as st

from api_ranking.services.exports import (
    comparar_resultados,
    gerar_excel_demonstrativos,
    gerar_excel_msc_12_13,
    gerar_excel_resultados,
    ler_planilha_resultados_comparacao,
)


def limpar_estado_exportacoes() -> None:
    """Descarta somente dados e arquivos cacheados pelos painéis de exportação."""
    for chave in (
        "_bundle_demonstrativos",
        "_final_df_export",
        "_export_meta",
    ):
        st.session_state.pop(chave, None)

    # Os bytes são chaveados por ente e exercício para que um rerender do
    # fragmento não refaça arquivos grandes sem necessidade.
    for prefixo in (
        "_xlsx_demo_bytes::",
        "_xlsx_demo_err::",
        "_xlsx_msc_bytes::",
        "_xlsx_msc_err::",
    ):
        chaves = [
            chave
            for chave in st.session_state.keys()
            if str(chave).startswith(prefixo)
        ]
        for chave in chaves:
            st.session_state.pop(chave, None)


def _formata_tamanho_bytes(n: int) -> str:
    """Formata tamanho em B/KB/MB para exibição."""
    n = int(n or 0)
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


@st.fragment
def painel_exportar_demonstrativos() -> None:
    st.markdown("---")
    st.subheader("📥 Exportar Demonstrativos para Excel")
    bundle = st.session_state.get("_bundle_demonstrativos")
    if not bundle:
        st.warning(
            "⚠️ Sem dados de demonstrativos em memória. "
            "Execute **Processar Análise**."
        )
        return

    st.info(
        "📌 O primeiro Excel reúne **DCA, RREO e RGF**. O segundo contém "
        "somente a **MSC consolidada dos meses 12 (dezembro) e 13 "
        "(encerramento)**, utilizados nos cruzamentos desta análise."
    )

    chave_exportacao = f"{bundle.get('cod','')}_{bundle.get('ano','')}"
    chave_xlsx = f"_xlsx_demo_bytes::{chave_exportacao}"
    chave_xlsx_erro = f"_xlsx_demo_err::{chave_exportacao}"
    chave_xlsx_msc = f"_xlsx_msc_bytes::{chave_exportacao}"
    chave_xlsx_msc_erro = f"_xlsx_msc_err::{chave_exportacao}"

    coluna_demos, coluna_msc = st.columns(2)
    with coluna_demos:
        if (
            chave_xlsx not in st.session_state
            and chave_xlsx_erro not in st.session_state
        ):
            with st.spinner("Gerando Excel (DCA/RREO/RGF)..."):
                try:
                    st.session_state[chave_xlsx] = gerar_excel_demonstrativos(bundle)
                except Exception as exc:
                    st.session_state[chave_xlsx_erro] = (
                        f"{type(exc).__name__}: {exc}"
                    )

        if st.session_state.get(chave_xlsx_erro):
            st.error(
                "❌ Erro ao gerar Excel (DCA/RREO/RGF): "
                f"{st.session_state[chave_xlsx_erro]}"
            )
            if st.button(
                "🔁 Tentar gerar novamente",
                key=f"retry_xlsx_{chave_exportacao}",
            ):
                st.session_state.pop(chave_xlsx_erro, None)
                st.session_state.pop(chave_xlsx, None)
                st.rerun(scope="fragment")
        else:
            xlsx_bytes = st.session_state.get(chave_xlsx) or b""
            tamanho_xlsx = len(xlsx_bytes)
            if tamanho_xlsx == 0:
                st.warning(
                    "⚠️ O Excel foi gerado, mas ficou **vazio** (0 bytes). "
                    "O navegador não dispara o download neste caso. Use o botão "
                    "abaixo para regerar."
                )
            st.download_button(
                label="📥 Baixar Excel (DCA/RREO/RGF)",
                data=xlsx_bytes,
                file_name=(
                    f"demonstrativos_{bundle['cod']}_{bundle['ano']}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                width="stretch",
                key=f"dl_xlsx_demo_{chave_exportacao}",
                disabled=(tamanho_xlsx == 0),
            )
            st.caption(
                f"📦 Tamanho do Excel: **{_formata_tamanho_bytes(tamanho_xlsx)}**"
            )
            if st.button(
                "🔄 Regerar Excel",
                key=f"regen_xlsx_{chave_exportacao}",
                help="Útil se o navegador não disparar o download.",
            ):
                st.session_state.pop(chave_xlsx, None)
                st.session_state.pop(chave_xlsx_erro, None)
                st.rerun(scope="fragment")

    with coluna_msc:
        msc = bundle.get("msc_consolidada")
        if msc is None or (isinstance(msc, pd.DataFrame) and msc.empty):
            st.caption(
                "MSC consolidada dos meses 12 e 13 indisponível para exportação."
            )
        else:
            if (
                chave_xlsx_msc not in st.session_state
                and chave_xlsx_msc_erro not in st.session_state
            ):
                with st.spinner(
                    "Gerando Excel da MSC consolidada (meses 12 e 13)..."
                ):
                    try:
                        st.session_state[chave_xlsx_msc] = (
                            gerar_excel_msc_12_13(msc)
                        )
                    except Exception as exc:
                        st.session_state[chave_xlsx_msc_erro] = (
                            f"{type(exc).__name__}: {exc}"
                        )

            if st.session_state.get(chave_xlsx_msc_erro):
                st.error(
                    "❌ Erro ao gerar o Excel da MSC (meses 12 e 13): "
                    f"{st.session_state[chave_xlsx_msc_erro]}"
                )
                if st.button(
                    "🔁 Tentar gerar novamente",
                    key=f"retry_xlsx_msc_{chave_exportacao}",
                ):
                    st.session_state.pop(chave_xlsx_msc_erro, None)
                    st.session_state.pop(chave_xlsx_msc, None)
                    st.rerun(scope="fragment")
            else:
                xlsx_msc_bytes = st.session_state.get(chave_xlsx_msc) or b""
                tamanho_xlsx_msc = len(xlsx_msc_bytes)
                if tamanho_xlsx_msc == 0:
                    st.warning(
                        "⚠️ O Excel da MSC foi gerado, mas ficou **vazio** (0 bytes). "
                        "O navegador não dispara o download neste caso. Use o botão "
                        "abaixo para regerar."
                    )
                st.download_button(
                    label="📥 Baixar Excel da MSC (meses 12 e 13)",
                    data=xlsx_msc_bytes,
                    file_name=(
                        "msc_consolidada_meses_12_13_"
                        f"{bundle['cod']}_{bundle['ano']}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    width="stretch",
                    key=f"dl_xlsx_msc_{chave_exportacao}",
                    disabled=(tamanho_xlsx_msc == 0),
                )
                st.caption(
                    "📦 Tamanho do Excel da MSC: "
                    f"**{_formata_tamanho_bytes(tamanho_xlsx_msc)}**"
                )
                if st.button(
                    "🔄 Regerar Excel da MSC",
                    key=f"regen_xlsx_msc_{chave_exportacao}",
                    help="Útil se o navegador não disparar o download.",
                ):
                    st.session_state.pop(chave_xlsx_msc, None)
                    st.session_state.pop(chave_xlsx_msc_erro, None)
                    st.rerun(scope="fragment")


@st.fragment
def painel_exportar_resultados_e_comparar() -> None:
    resultados = st.session_state.get("_final_df_export")
    metadados = st.session_state.get("_export_meta") or {}
    if resultados is None or getattr(resultados, "empty", True):
        return

    cod = metadados.get("cod", "")
    ente = metadados.get("ente", "")
    ano = metadados.get("ano", "")
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    slug_ente = (
        re.sub(r"[^\w\-.]+", "_", str(ente), flags=re.UNICODE)
        .strip("._")[:50]
        or "ente"
    )
    nome_arquivo = (
        f"resultado_analises_{cod}_{slug_ente}_ex{ano}_{timestamp}.xlsx"
    )
    try:
        excel_bytes = gerar_excel_resultados(resultados)
    except Exception as exc_excel:
        st.error(f"Erro ao gerar Excel: {exc_excel}")
        excel_bytes = b""

    if excel_bytes:
        st.download_button(
            label="📥 Exportar resultados (Excel)",
            data=excel_bytes,
            file_name=nome_arquivo,
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            width="stretch",
            key=f"download_resultados_excel_{cod}_{ano}",
        )
    else:
        st.warning("Não foi possível gerar o arquivo Excel para exportação.")

    with st.expander(
        "📊 Comparar duas exportações de resultados (Excel antes × depois)",
        expanded=False,
    ):
        st.caption(
            "Carregue dois arquivos `.xlsx` obtidos com **Exportar resultados "
            "(Excel)** — por exemplo a análise da semana passada e a de hoje, "
            "após corrigir dados no SICONFI — para ver alterações em **Resposta** "
            "e **Nota** por dimensão (o texto de **OBS** não entra na detecção de "
            "mudanças)."
        )
        coluna_antes, coluna_depois = st.columns(2)
        with coluna_antes:
            arquivo_antes = st.file_uploader(
                "Ficheiro **antes** (referência)",
                type=["xlsx"],
                key="cmp_resultados_antes",
            )
        with coluna_depois:
            arquivo_depois = st.file_uploader(
                "Ficheiro **depois** (mais recente)",
                type=["xlsx"],
                key="cmp_resultados_depois",
            )

        if arquivo_antes is not None and arquivo_depois is not None:
            try:
                antes = ler_planilha_resultados_comparacao(arquivo_antes)
                depois = ler_planilha_resultados_comparacao(arquivo_depois)
            except Exception as exc:
                st.error(f"Não foi possível comparar os arquivos: {exc}")
            else:
                comparacao = comparar_resultados(antes, depois)
                so_antes = comparacao["dimensoes_so_antes"]
                so_depois = comparacao["dimensoes_so_depois"]
                tabela_alteracoes = comparacao["tabela_alteracoes"]

                st.markdown("##### Resumo")
                metrica_antes, metrica_depois, metrica_melhorou, metrica_piorou = (
                    st.columns(4)
                )
                metrica_antes.metric("Dimensões só no «antes»", len(so_antes))
                metrica_depois.metric("Dimensões só no «depois»", len(so_depois))
                metrica_melhorou.metric(
                    "Melhorou (resposta/nota)",
                    comparacao["quantidade_melhorou"],
                )
                metrica_piorou.metric(
                    "Piorou (resposta/nota)",
                    comparacao["quantidade_piorou"],
                )
                if so_antes:
                    st.caption(
                        "Só no arquivo **antes**: "
                        + ", ".join(so_antes[:30])
                        + ("…" if len(so_antes) > 30 else "")
                    )
                if so_depois:
                    st.caption(
                        "Só no arquivo **depois**: "
                        + ", ".join(so_depois[:30])
                        + ("…" if len(so_depois) > 30 else "")
                    )
                if tabela_alteracoes.empty and not so_antes and not so_depois:
                    st.success(
                        "Nenhuma diferença encontrada nas colunas comparadas "
                        "(dimensões comuns)."
                    )
                elif not tabela_alteracoes.empty:
                    st.markdown("##### Alterações por dimensão")
                    st.dataframe(
                        tabela_alteracoes,
                        width="stretch",
                        hide_index=True,
                    )
