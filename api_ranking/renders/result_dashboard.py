"""Painel compacto para os resultados das dimensões D2, D3 e D4.

Este módulo cuida somente da apresentação. As respostas e evidências continuam
sendo produzidas pelas regras existentes em ``api_ranking.analysis``.
"""

from __future__ import annotations

from collections.abc import Mapping
import re
import unicodedata

import pandas as pd
import streamlit as st

from core.diagnostics import DiagnosticStatus, classify_result
from core.utils import formatar_reais
from api_ranking.services.formatting import eh_verificacao_capag


STATUS_LABELS = {
    DiagnosticStatus.DIVERGENCIA: "Divergência",
    DiagnosticStatus.FALHA_TECNICA: "Falha técnica",
    DiagnosticStatus.DADOS_INSUFICIENTES: "Dados insuficientes",
    DiagnosticStatus.CONFORME: "Conforme",
    DiagnosticStatus.NAO_APLICAVEL: "Não aplicável",
}

STATUS_ICONS = {
    DiagnosticStatus.DIVERGENCIA: "🔴",
    DiagnosticStatus.FALHA_TECNICA: "🟠",
    DiagnosticStatus.DADOS_INSUFICIENTES: "🟡",
    DiagnosticStatus.CONFORME: "🟢",
    DiagnosticStatus.NAO_APLICAVEL: "⚪",
}

STATUS_ORDER = {
    DiagnosticStatus.DIVERGENCIA: 0,
    DiagnosticStatus.FALHA_TECNICA: 1,
    DiagnosticStatus.DADOS_INSUFICIENTES: 2,
    DiagnosticStatus.CONFORME: 3,
    DiagnosticStatus.NAO_APLICAVEL: 4,
}

FILTER_STATUSES = {
    "Prioridades": {
        DiagnosticStatus.DIVERGENCIA,
        DiagnosticStatus.FALHA_TECNICA,
        DiagnosticStatus.DADOS_INSUFICIENTES,
    },
    "Divergências": {DiagnosticStatus.DIVERGENCIA},
    "Inconclusivos": {
        DiagnosticStatus.FALHA_TECNICA,
        DiagnosticStatus.DADOS_INSUFICIENTES,
    },
    "Conformes": {DiagnosticStatus.CONFORME},
    "Todos": set(DiagnosticStatus),
}

DIMENSION_OPTIONS = ("Todas", "D2", "D3", "D4")

STATUS_BADGE_COLORS = {
    DiagnosticStatus.DIVERGENCIA: "red",
    DiagnosticStatus.FALHA_TECNICA: "orange",
    DiagnosticStatus.DADOS_INSUFICIENTES: "yellow",
    DiagnosticStatus.CONFORME: "green",
    DiagnosticStatus.NAO_APLICAVEL: "gray",
}

STATUS_SLUGS = {
    DiagnosticStatus.DIVERGENCIA: "divergencia",
    DiagnosticStatus.FALHA_TECNICA: "falha_tecnica",
    DiagnosticStatus.DADOS_INSUFICIENTES: "dados_insuficientes",
    DiagnosticStatus.CONFORME: "conforme",
    DiagnosticStatus.NAO_APLICAVEL: "nao_aplicavel",
}

STATUS_RESPONSE_LABELS = {
    DiagnosticStatus.DIVERGENCIA: "ERRO",
    DiagnosticStatus.FALHA_TECNICA: "SEM CONCLUSÃO",
    DiagnosticStatus.DADOS_INSUFICIENTES: "SEM CONCLUSÃO",
    DiagnosticStatus.CONFORME: "OK",
    DiagnosticStatus.NAO_APLICAVEL: "N/A",
}

DIMENSION_TITLES = {
    "D2": "DCA x MSC",
    "D3": "RREO/RGF",
    "D4": "DCA x RREO",
}

_IDENTIFIER_COLUMNS = {
    "index",
    "id",
    "ano",
    "exercicio",
    "mes",
    "quantidade",
    "qtd",
    "anexo",
    "cod",
    "codigo",
    "cod conta",
    "fonte",
    "grupo de fr",
    "linha",
    "coluna",
    "conta",
    "conta msc",
    "poder orgao",
    "nota",
}


def _normalized_column_name(column: object) -> str:
    text = unicodedata.normalize("NFKD", str(column))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.casefold().replace("_", " ").split())


def format_decimal_pt_br(value: object) -> str:
    """Formata um número com milhar e vírgula decimal, sem alterar o dado."""
    if value is None or bool(pd.isna(value)):
        return "—"
    number = float(value)
    if abs(number) < 0.005:
        number = 0.0
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_currency_pt_br(value: object) -> str:
    """Formata um valor monetário no padrão brasileiro."""
    if value is None or bool(pd.isna(value)):
        return "—"
    number = float(value)
    if abs(number) < 0.005:
        number = 0.0
    return formatar_reais(number)


def format_percentage_pt_br(value: object) -> str:
    """Formata percentual já expresso em pontos percentuais, sem reescalar."""
    formatted = format_decimal_pt_br(value)
    return formatted if formatted == "—" else f"{formatted}%"


def _format_identifier(value: object) -> str:
    if value is None or bool(pd.isna(value)):
        return "—"
    number = float(value)
    return str(int(number)) if number.is_integer() else format_decimal_pt_br(number)


def style_evidence_table(detail: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Aplica formatação pt-BR somente à apresentação das evidências."""
    formatters = {}
    for column in detail.select_dtypes(include="number").columns:
        normalized = _normalized_column_name(column)
        if normalized in _IDENTIFIER_COLUMNS:
            formatters[column] = _format_identifier
        elif any(token in normalized for token in ("percent", "perc", "taxa", "indice", "%")):
            formatters[column] = format_percentage_pt_br
        else:
            formatters[column] = format_currency_pt_br
    return detail.style.format(formatters, na_rep="—")


def _display_text(value: object, fallback: str = "") -> str:
    """Converte um valor escalar em texto sem exibir ``nan``/``None``."""
    if value is None:
        return fallback
    try:
        if bool(pd.isna(value)):
            return fallback
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    return text or fallback


def _natural_code_key(code: object) -> tuple[tuple[int, object], ...]:
    """Cria uma chave natural para ordenar ``D2_9`` antes de ``D2_10``."""
    text = _display_text(code).upper()
    return tuple(
        (0, int(token)) if token.isdigit() else (1, token)
        for token in re.findall(r"\d+|\D+", text)
    )


def sort_results_numerically(data: pd.DataFrame) -> pd.DataFrame:
    """Ordena códigos de regras numericamente, mantendo empates estáveis."""
    if not isinstance(data, pd.DataFrame) or data.empty or "Dimensão" not in data:
        return data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame()
    positions = sorted(
        range(len(data)),
        key=lambda position: _natural_code_key(data.iloc[position]["Dimensão"]),
    )
    return data.iloc[positions].reset_index(drop=True)


def _short_description(value: object, limit: int = 92) -> str:
    description = _display_text(value, "Descrição não informada")
    if len(description) <= limit:
        return description
    return f"{description[: limit - 1].rstrip()}…"


def _detail_for(
    detail_tables: Mapping[str, object],
    code: str,
) -> pd.DataFrame:
    """Aceita chaves por código (nova API) e ``dX_00000_t`` (legado)."""
    candidates = (code, code.upper(), code.lower(), f"{code.lower()}_t")
    for key in candidates:
        detail = detail_tables.get(key)
        if isinstance(detail, pd.DataFrame):
            return detail
    return pd.DataFrame()


def prepare_results(
    final: pd.DataFrame,
    detail_tables: Mapping[str, object] | None = None,
) -> pd.DataFrame:
    """Prepara a fila D2/D3/D4 para apresentação, sem mudar os resultados."""
    detail_tables = detail_tables or {}
    if (
        not isinstance(final, pd.DataFrame)
        or final.empty
        or "Dimensão" not in final.columns
    ):
        return pd.DataFrame()

    data = final[
        final["Dimensão"].astype(str).str.upper().str.startswith(("D2_", "D3_", "D4_"))
    ].copy()
    if data.empty:
        return data

    for column in ("Resposta", "Descrição da Dimensão", "Nota", "OBS"):
        if column not in data.columns:
            data[column] = ""

    data["Dimensão"] = data["Dimensão"].map(lambda value: _display_text(value).upper())
    data["Grupo"] = data["Dimensão"].str[:2]
    data["Descrição da Dimensão"] = data["Descrição da Dimensão"].map(
        lambda value: _display_text(value, "Descrição não informada")
    )
    data["_status"] = data.apply(
        lambda row: classify_result(row["Resposta"], row["OBS"]),
        axis=1,
    )
    data["Situação"] = data["_status"].map(STATUS_LABELS)
    data["Indicador"] = data["_status"].map(STATUS_ICONS)
    data["Status"] = data["Indicador"] + " " + data["Situação"]
    data["Evidência"] = data["Dimensão"].map(
        lambda code: "Disponível"
        if not _detail_for(detail_tables, code).empty
        else "—"
    )
    data["_status_order"] = data["_status"].map(STATUS_ORDER)
    return data.sort_values(
        ["_status_order", "Grupo", "Dimensão"], kind="stable"
    ).reset_index(drop=True)


def prepare_dimension_results(
    ctx: Mapping[str, object],
    prefix: str,
) -> pd.DataFrame:
    """Monta a visão de uma dimensão sem alterar o DataFrame consolidado."""
    final = ctx.get("final", pd.DataFrame())
    prepared = prepare_results(final, ctx)
    if prepared.empty:
        return prepared
    return prepared[
        prepared["Dimensão"].str.startswith(prefix.upper())
    ].reset_index(drop=True)


def summarize_dimension(data: pd.DataFrame) -> dict[str, float | int]:
    """Resume a dimensão com a mesma semântica do diagnóstico consolidado."""
    statuses = data.get("_status", pd.Series(dtype="object"))
    divergences = int((statuses == DiagnosticStatus.DIVERGENCIA).sum())
    conforming = int((statuses == DiagnosticStatus.CONFORME).sum())
    technical = int((statuses == DiagnosticStatus.FALHA_TECNICA).sum())
    insufficient = int((statuses == DiagnosticStatus.DADOS_INSUFICIENTES).sum())
    not_applicable = int((statuses == DiagnosticStatus.NAO_APLICAVEL).sum())
    conclusive = conforming + divergences
    return {
        "total": int(len(data)),
        "divergences": divergences,
        "conforming": conforming,
        "inconclusive": technical + insufficient,
        "not_applicable": not_applicable,
        "conclusive": conclusive,
        "conformity_percent": 100 * conforming / conclusive if conclusive else 0.0,
    }


def filter_dimension_results(
    data: pd.DataFrame,
    view: str,
    query: str = "",
) -> pd.DataFrame:
    """Filtra a fila visível por situação e busca textual."""
    allowed = FILTER_STATUSES.get(view, FILTER_STATUSES["Prioridades"])
    filtered = data[data["_status"].isin(allowed)].copy()
    normalized_query = query.casefold().strip()
    if normalized_query:
        searchable = (
            filtered["Dimensão"].map(_display_text)
            + " "
            + filtered["Descrição da Dimensão"].map(_display_text)
            + " "
            + filtered["Situação"].map(_display_text)
        ).str.casefold()
        filtered = filtered[searchable.str.contains(normalized_query, regex=False)]
    return filtered.reset_index(drop=True)


def filter_results(
    data: pd.DataFrame,
    view: str,
    dimension: str = "Todas",
    query: str = "",
) -> pd.DataFrame:
    """Aplica os filtros do explorador, preservando a ordenação de risco."""
    filtered = filter_dimension_results(data, view, query)
    if dimension in {"D2", "D3", "D4"}:
        filtered = filtered[filtered["Grupo"] == dimension]
    return filtered.reset_index(drop=True)


def result_option_label(row: pd.Series) -> str:
    """Rótulo completo usado no seletor de uma verificação."""
    description = _display_text(row.get("Descrição da Dimensão"), "Descrição não informada")
    if len(description) > 92:
        description = f"{description[:89].rstrip()}…"
    return (
        f"{_display_text(row.get('Indicador'))} "
        f"{_display_text(row.get('Dimensão'))} · {description} · "
        f"{_display_text(row.get('Situação'))}"
    )


def _render_status_message(status: DiagnosticStatus) -> None:
    messages = {
        DiagnosticStatus.DIVERGENCIA: (
            st.error,
            "Divergência encontrada — confira os valores e a memória de cálculo abaixo.",
        ),
        DiagnosticStatus.FALHA_TECNICA: (
            st.warning,
            "A regra não foi concluída por uma falha técnica. Revise a observação antes de decidir.",
        ),
        DiagnosticStatus.DADOS_INSUFICIENTES: (
            st.info,
            "Não há dados suficientes para uma conclusão nesta verificação.",
        ),
        DiagnosticStatus.CONFORME: (
            st.success,
            "Os valores comparados estão conformes segundo a regra executada.",
        ),
        DiagnosticStatus.NAO_APLICAVEL: (
            st.info,
            "Esta verificação não se aplica ao ente ou ao período selecionado.",
        ),
    }
    renderer, message = messages[status]
    renderer(message)


def _render_selected_result(
    row: pd.Series,
    detail_tables: Mapping[str, object],
    key_prefix: str,
) -> None:
    """Mantém o cartão de detalhe usado pelo painel legado."""
    code = _display_text(row.get("Dimensão"))
    status = row["_status"]
    status_slug = STATUS_SLUGS[status]

    with st.container(
        border=True,
        key=f"result_detail_{status_slug}_{key_prefix}_{code}",
    ):
        st.markdown(f"#### {code}")
        _render_result_content(row, detail_tables)


def _render_result_content(
    row: pd.Series,
    detail_tables: Mapping[str, object],
) -> None:
    """Renderiza o conteúdo comum de uma regra, sem criar outro expander."""
    code = _display_text(row.get("Dimensão"))
    status = row["_status"]
    description = _display_text(
        row.get("Descrição da Dimensão"), "Descrição não informada"
    )
    response = _display_text(row.get("Resposta"), "Sem resposta")
    observation = _display_text(row.get("OBS"))
    note = row.get("Nota")
    detail = _detail_for(detail_tables, code)
    is_capag = eh_verificacao_capag(code, description)

    st.badge(
        STATUS_LABELS[status],
        color=STATUS_BADGE_COLORS[status],
    )
    if is_capag:
        st.caption("🏛️ Verificação relacionada à CAPAG.")
    st.caption(description)
    _render_status_message(status)

    note_text = _display_text(note, "—")
    try:
        note_text = format_decimal_pt_br(note)
    except (TypeError, ValueError):
        pass
    st.markdown(f"**Resposta da regra:** {response}  ·  **Nota:** {note_text}")

    if observation:
        st.markdown("**Observação**")
        st.write(observation)

    if isinstance(detail, pd.DataFrame) and not detail.empty:
        st.caption(
            f"**Evidências e memória de cálculo:** {len(detail)} linha(s).  \n"
            "Valores financeiros em reais (R$), com formatação brasileira. "
            "A apresentação não altera os dados usados no cálculo."
        )
        st.dataframe(
            style_evidence_table(detail),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("Esta regra não retornou uma tabela adicional de evidências.")


def _render_result_expander(
    row: pd.Series,
    detail_tables: Mapping[str, object],
    context_key: str,
) -> None:
    """Renderiza uma regra com status visível e conteúdo carregado sob demanda."""
    code = _display_text(row.get("Dimensão"))
    status = row["_status"]
    status_slug = STATUS_SLUGS[status]
    response_label = STATUS_RESPONSE_LABELS[status]
    description = _short_description(row.get("Descrição da Dimensão"))
    label = f"**{code}** | **{response_label}** | {description}"

    with st.container(
        key=f"result_expander_{status_slug}_{context_key}_{code}",
    ):
        expander = st.expander(
            label,
            icon=STATUS_ICONS[status],
            key=f"result_toggle_{context_key}_{code}",
            on_change="rerun",
        )
        if expander.open:
            with expander:
                _render_result_content(row, detail_tables)


def _render_dimension_expanders(
    data: pd.DataFrame,
    dimension: str,
    detail_tables: Mapping[str, object],
    context_key: str,
) -> None:
    """Lista uma dimensão em ordem numérica usando um único loop compartilhado."""
    dimension_rows = sort_results_numerically(data[data["Grupo"] == dimension])
    if dimension_rows.empty:
        st.info(f"Nenhuma verificação {dimension} disponível neste resultado.")
        return

    summary = summarize_dimension(dimension_rows)
    st.caption(
        f"{len(dimension_rows)} verificações · "
        f"{summary['conforming']} OK · {summary['divergences']} com erro · "
        f"{summary['inconclusive']} sem conclusão · "
        f"{summary['not_applicable']} não aplicável(is)."
    )
    for _, row in dimension_rows.iterrows():
        _render_result_expander(row, detail_tables, context_key)


@st.fragment
def render_results_explorer(
    final: pd.DataFrame,
    detail_tables: Mapping[str, object],
    context_key: str = "analysis",
) -> None:
    """Renderiza as regras em abas por dimensão e expanders sob demanda.

    ``detail_tables`` é um mapeamento explícito ``{codigo: DataFrame}``. Também
    são aceitas chaves legadas como ``d2_00044_t``. Como este componente é um
    fragmento, abrir abas e regras não reexecuta a coleta nem as análises.
    """
    data = prepare_results(final, detail_tables)

    st.markdown("### Verificações por dimensão")
    st.caption(
        "As verificações estão na ordem numérica. O resultado aparece no "
        "cabeçalho; abra uma regra para consultar sua evidência e memória de cálculo."
    )
    if data.empty:
        st.info("Nenhum resultado D2, D3 ou D4 está disponível.")
        return

    dimensions = ("D2", "D3", "D4")
    labels = [
        (
            f"{dimension} - {DIMENSION_TITLES[dimension]} "
            f"({int((data['Grupo'] == dimension).sum())})"
        )
        for dimension in dimensions
    ]
    tabs = st.tabs(
        labels,
        key=f"results_tabs_{context_key}",
        on_change="rerun",
    )
    for dimension, tab in zip(dimensions, tabs):
        if tab.open:
            with tab:
                _render_dimension_expanders(
                    data,
                    dimension,
                    detail_tables,
                    context_key,
                )


def render_dimension_panel(
    ctx: Mapping[str, object],
    prefix: str,
    title: str,
    *,
    key_prefix: str | None = None,
) -> None:
    """Renderiza um dashboard de dimensão no contêiner Streamlit atual.

    Pode ser chamado dentro de uma aba, contêiner ou diretamente na página.
    ``key_prefix`` deve ser único quando mais de um painel estiver visível.
    """
    widget_key = key_prefix or prefix.rstrip("_").lower()
    data = prepare_dimension_results(ctx, prefix)

    st.subheader(title)
    if data.empty:
        st.info("Nenhuma verificação disponível para este grupo.")
        return

    summary = summarize_dimension(data)
    metric_columns = st.columns(4)
    metric_columns[0].metric("Divergências", summary["divergences"])
    metric_columns[1].metric("Conformes", summary["conforming"])
    metric_columns[2].metric("Inconclusivos", summary["inconclusive"])
    metric_columns[3].metric(
        "Conformidade",
        f"{summary['conformity_percent']:.1f}%",
        help="Percentual de conformes entre os resultados conclusivos.",
    )

    filter_column, search_column = st.columns([3, 2])
    view = filter_column.segmented_control(
        "Exibir",
        options=list(FILTER_STATUSES),
        default="Prioridades",
        key=f"{widget_key}_result_view",
        help="Prioridades reúne divergências, falhas técnicas e dados insuficientes.",
    )
    query = search_column.text_input(
        "Buscar verificação",
        placeholder="Código, descrição ou situação",
        key=f"{widget_key}_result_search",
    )
    filtered = filter_dimension_results(data, view or "Prioridades", query)

    if filtered.empty:
        if view == "Prioridades" and not query:
            st.success("Nenhuma prioridade nesta dimensão.")
        else:
            st.info("Nenhum resultado corresponde aos filtros selecionados.")
        return

    overview = filtered[
        ["Indicador", "Dimensão", "Descrição da Dimensão", "Situação", "Evidência"]
    ].copy()
    st.dataframe(
        overview,
        width="stretch",
        hide_index=True,
        height=max(122, min(367, 38 + len(overview) * 33)),
        column_config={
            "Indicador": st.column_config.TextColumn("", width="small"),
            "Dimensão": st.column_config.TextColumn("Código", width="small"),
            "Descrição da Dimensão": st.column_config.TextColumn(
                "Verificação", width="large"
            ),
            "Situação": st.column_config.TextColumn("Situação", width="medium"),
            "Evidência": st.column_config.TextColumn("Evidência", width="small"),
        },
    )

    records = filtered.to_dict("records")
    selected_code = st.selectbox(
        "Detalhar uma verificação",
        options=[row["Dimensão"] for row in records],
        format_func=lambda code: result_option_label(
            filtered.loc[filtered["Dimensão"] == code].iloc[0]
        ),
        key=f"{widget_key}_selected_result",
    )
    selected = filtered.loc[filtered["Dimensão"] == selected_code].iloc[0]
    _render_selected_result(selected, ctx, widget_key)


__all__ = [
    "FILTER_STATUSES",
    "STATUS_ICONS",
    "STATUS_LABELS",
    "filter_dimension_results",
    "filter_results",
    "prepare_results",
    "prepare_dimension_results",
    "render_dimension_panel",
    "render_results_explorer",
    "result_option_label",
    "format_currency_pt_br",
    "format_decimal_pt_br",
    "format_percentage_pt_br",
    "style_evidence_table",
    "sort_results_numerically",
    "summarize_dimension",
]
