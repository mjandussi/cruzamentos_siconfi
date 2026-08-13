"""Diagnóstico retrospectivo da base anual encerrada do Ranking Siconfi."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from core.auth import is_authed
from core.layout import (
    app_footer,
    page_brand,
    page_intro,
    render_main_nav,
    setup_page,
)
from core.methodology import (
    DIMENSOES_CRUZAMENTO_2025,
    classify_icf,
    get_crosschecks_without_msc,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RANKING_PATH = PROJECT_ROOT / "data" / "ranking_rj_2025.csv"
METHODOLOGY_PATH = PROJECT_ROOT / "data" / "metodologia_cruzamentos_2025.csv"

EXERCISE = 2025
RANKING_EDITION = 2026
OFFICIAL_CUTOFF = "10/05/2026"
OFFICIAL_MUNICIPAL_DENOMINATOR = 195
RANKING_SNAPSHOT_SHA256 = "e7cbb20e50f20b6adcacefb24deb9f70960341e293fcdd2fba92af6b04a6e097"
METHODOLOGY_SNAPSHOT_SHA256 = "29ed2280f10636c50265729fae13cd32e770d7a8d1bc17f227e006a8a422f5a4"
DELIVERY_CHECKS = (
    "D1_00001",
    "D1_00002",
    "D1_00003",
    "D1_00004",
    "D1_00016",
)

CROSSCHECKS_WITHOUT_MSC_2025 = get_crosschecks_without_msc(EXERCISE)


def _numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return series
    return pd.to_numeric(
        series.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def _validate_snapshot_hash(path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(
            f"Integridade do arquivo {path.name} não confirmada: SHA-256 divergente."
        )


@st.cache_data(show_spinner=False)
def load_ranking() -> pd.DataFrame:
    _validate_snapshot_hash(RANKING_PATH, RANKING_SNAPSHOT_SHA256)
    frame = pd.read_csv(
        RANKING_PATH,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        low_memory=False,
    )
    numeric_columns = [
        *DELIVERY_CHECKS,
        *DIMENSOES_CRUZAMENTO_2025,
        "per_acertos",
        "class_ranking",
    ]
    required = {
        "exercicio",
        "Ente",
        "nome",
        "sigla",
        "per_acertos",
        "nota_ranking",
        "class_ranking",
        *DELIVERY_CHECKS,
        *DIMENSOES_CRUZAMENTO_2025,
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(
            "Esquema do snapshot histórico incompleto: " + ", ".join(missing)
        )
    for column in numeric_columns:
        frame[column] = _numeric(frame[column])
    frame["Ente"] = frame["Ente"].astype(str).str.replace(r"\.0$", "", regex=True)
    if len(frame) != 92 or frame["Ente"].nunique() != 92:
        raise ValueError("O snapshot deve conter exatamente 92 municípios únicos do RJ.")
    if set(frame["exercicio"].dropna().astype(int)) != {EXERCISE}:
        raise ValueError(f"O snapshot deve conter somente o exercício {EXERCISE}.")
    domain = set(
        pd.unique(frame[list(DIMENSOES_CRUZAMENTO_2025)].to_numpy().ravel())
    )
    if not domain.issubset({0, 1, 0.0, 1.0}):
        raise ValueError("As 72 verificações devem conter somente pontuações 0 ou 1.")
    frame["entrega_completa"] = frame[list(DELIVERY_CHECKS)].eq(1).all(axis=1)
    return frame.sort_values("nome", kind="stable").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_methodology() -> pd.DataFrame:
    _validate_snapshot_hash(METHODOLOGY_PATH, METHODOLOGY_SNAPSHOT_SHA256)
    frame = pd.read_csv(
        METHODOLOGY_PATH,
        sep=";",
        encoding="utf-8-sig",
    ).fillna("")
    required = {"codigo", "titulo", "relatorio"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(
            "Esquema dos metadados incompleto: " + ", ".join(missing)
        )
    if len(frame) != 72 or frame["codigo"].nunique() != 72:
        raise ValueError("A metodologia preservada deve conter 72 códigos únicos.")
    if set(frame["codigo"]) != set(DIMENSOES_CRUZAMENTO_2025):
        raise ValueError("Os códigos dos metadados divergem do escopo metodológico.")
    return frame


def scope_statistics(
    frame: pd.DataFrame,
    dimensions: tuple[str, ...],
    methodology: pd.DataFrame,
) -> pd.DataFrame:
    metadata = methodology.set_index("codigo").to_dict("index")
    records: list[dict[str, object]] = []
    for code in dimensions:
        values = pd.to_numeric(frame[code], errors="coerce")
        valid = int(values.notna().sum())
        conforms = int(values.eq(1).sum())
        failures = int(values.lt(1).sum())
        item = metadata.get(code, {})
        records.append(
            {
                "Código": code,
                "Dimensão oficial": code.split("_")[0],
                "Descrição": item.get("titulo", code),
                "Relatórios": item.get("relatorio", ""),
                "Taxa de acerto": (conforms / valid) if valid else None,
                "Falhas equivalentes": failures,
                "Municípios avaliados": valid,
            }
        )
    return pd.DataFrame(records).sort_values(
        ["Falhas equivalentes", "Código"],
        ascending=[False, True],
        kind="stable",
    )


def individual_diagnostics(
    row: pd.Series,
    dimensions: tuple[str, ...],
    methodology: pd.DataFrame,
) -> pd.DataFrame:
    metadata = methodology.set_index("codigo").to_dict("index")
    fast_scope = set(CROSSCHECKS_WITHOUT_MSC_2025)
    records: list[dict[str, object]] = []
    delivery_complete = bool(row.get("entrega_completa", False))
    for code in dimensions:
        value = pd.to_numeric(pd.Series([row.get(code)]), errors="coerce").iloc[0]
        if not delivery_complete:
            status = "Entrega essencial ausente"
        elif pd.isna(value):
            status = "Sem dado na base"
        elif value == 1:
            status = "Pontuação integral"
        else:
            status = "Não pontuada"
        item = metadata.get(code, {})
        records.append(
            {
                "Prioridade": (
                    "1 · Conciliação direta"
                    if code in fast_scope
                    else "2 · Revisão com MSC"
                ),
                "Código": code,
                "Status na base fechada": status,
                "Descrição": item.get("titulo", code),
                "Relatórios": item.get("relatorio", ""),
                "Impacto máximo (p.p.)": (
                    100 / OFFICIAL_MUNICIPAL_DENOMINATOR
                    if delivery_complete and status == "Não pontuada"
                    else None
                ),
            }
        )
    return pd.DataFrame(records).sort_values(
        ["Prioridade", "Código"],
        kind="stable",
    ).reset_index(drop=True)


def format_percent(value: float) -> str:
    return f"{value:.2f}%".replace(".", ",")


setup_page(
    page_title="CRUZAMENTOS SICONFI - Diagnóstico histórico",
    logo_path="assets/logo-mark.svg",
    show_top_nav=False,
)
if not is_authed():
    st.switch_page("app.py")

page_brand(
    title="CRUZAMENTOS SICONFI",
    logo_path="assets/logo-mark.svg",
    show_logout=True,
)
render_main_nav(active="Diagnóstico histórico")
page_intro(
    "Diagnóstico histórico",
    eyebrow="Ranking anual encerrado",
    description=(
        "Explore a base oficial já divulgada, localize as não pontuações e estime "
        "cenários contrafactuais sem confundi-los com uma nova apuração da STN."
    ),
    icon="📚",
)

if not RANKING_PATH.exists() or not METHODOLOGY_PATH.exists():
    st.error("A base retrospectiva preservada não foi encontrada no deploy.")
    st.stop()

try:
    ranking = load_ranking()
    methodology = load_methodology()
except (OSError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Não foi possível validar o snapshot histórico: {exc}")
    st.stop()
complete = ranking[ranking["entrega_completa"]].copy()

st.markdown(
    f"""
    <div class="context-strip" role="note">
      <span><strong>Modo:</strong> retrospectivo</span>
      <span><strong>Edição:</strong> Ranking {RANKING_EDITION}</span>
      <span><strong>Exercício:</strong> {EXERCISE}</span>
      <span><strong>Recorte:</strong> municípios do RJ</span>
      <span><strong>Data de corte:</strong> {OFFICIAL_CUTOFF}</span>
      <span><strong>Fonte:</strong> base anual encerrada</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Este modo **não recalcula o Ranking** e não consulta demonstrativos atuais. "
    "Aqui, uma nota zero é chamada de **não pontuação** ou **falha equivalente**; "
    "ela só se torna divergência comprovada após exame dos dados de origem."
)

scope_label = st.segmented_control(
    "Escopo analítico",
    options=["Completo · 72 cruzamentos", "Conciliações diretas · 36"],
    default="Completo · 72 cruzamentos",
    help=(
        "O escopo de 36 regras exclui dependência da MSC/matriz e tende a gerar "
        "conferências mais imediatas entre DCA, RREO e RGF."
    ),
)
dimensions = (
    CROSSCHECKS_WITHOUT_MSC_2025
    if scope_label == "Conciliações diretas · 36"
    else DIMENSOES_CRUZAMENTO_2025
)
scope_slug = "sem_msc_36" if len(dimensions) == 36 else "completo_72"
scope_description = "Sem MSC/matriz (36)" if len(dimensions) == 36 else "Completo (72)"

tab_overview, tab_municipality, tab_method = st.tabs(
    ["Visão geral do RJ", "Diagnóstico por município", "Método e limites"]
)

with tab_overview:
    values = complete[list(dimensions)].apply(pd.to_numeric, errors="coerce")
    valid_count = int(values.notna().sum().sum())
    conforms = int(values.eq(1).sum().sum())
    failures = int(values.lt(1).sum().sum())
    accuracy = (conforms / valid_count * 100) if valid_count else 0.0

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Municípios do RJ", len(ranking))
    metric_2.metric(
        "Entrega essencial completa",
        f"{len(complete)} de {len(ranking)}",
        help="D1_00001, D1_00002, D1_00003, D1_00004 e D1_00016 com pontuação integral.",
    )
    metric_3.metric("Taxa de acerto no escopo", format_percent(accuracy))
    metric_4.metric("Falhas equivalentes", failures)

    st.caption(
        f"Foram observadas {valid_count:,} combinações município–verificação "
        f"no recorte selecionado. A média foi de {failures / max(len(complete), 1):.2f} "
        "falhas equivalentes por município com entrega completa."
    )

    statistics = scope_statistics(complete, dimensions, methodology)
    top = statistics.head(10).copy()
    st.subheader("Verificações que mais exigem atenção")
    st.bar_chart(
        top,
        x="Código",
        y="Falhas equivalentes",
        color="#d97706",
        horizontal=True,
        sort="-Falhas equivalentes",
        width="stretch",
    )
    st.dataframe(
        top,
        hide_index=True,
        width="stretch",
        column_config={
            "Taxa de acerto": st.column_config.ProgressColumn(
                "Taxa de acerto",
                min_value=0.0,
                max_value=1.0,
                format="percent",
            ),
            "Descrição": st.column_config.TextColumn(width="large"),
            "Relatórios": st.column_config.TextColumn(width="medium"),
        },
    )
    statistics_export = statistics.copy()
    statistics_export.insert(0, "Edição", RANKING_EDITION)
    statistics_export.insert(1, "Exercício", EXERCISE)
    statistics_export.insert(2, "Data de corte", OFFICIAL_CUTOFF)
    statistics_export.insert(3, "Escopo", scope_description)
    statistics_export["SHA-256 do snapshot"] = RANKING_SNAPSHOT_SHA256
    statistics_export["SHA-256 da metodologia"] = METHODOLOGY_SNAPSHOT_SHA256
    st.download_button(
        "Baixar diagnóstico agregado (CSV)",
        data=statistics_export.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"diagnostico_cruzamentos_rj_{EXERCISE}_{scope_slug}.csv",
        mime="text/csv",
        width="stretch",
    )

with tab_municipality:
    selected_name = st.selectbox(
        "Município",
        options=ranking["nome"].tolist(),
        index=0,
    )
    municipality = ranking.loc[ranking["nome"].eq(selected_name)].iloc[0]
    diagnostics = individual_diagnostics(municipality, dimensions, methodology)
    not_scored = diagnostics[diagnostics["Status na base fechada"].eq("Não pontuada")].copy()

    official_ratio = float(municipality.get("per_acertos", 0) or 0)
    official_percent = official_ratio * 100
    official_band = str(municipality.get("nota_ranking", "N/A"))
    potential_gain = len(not_scored) / OFFICIAL_MUNICIPAL_DENOMINATOR * 100
    simulated_percent = min(100.0, official_percent + potential_gain)
    simulated_band = classify_icf(simulated_percent, scale="percent")

    st.markdown(f"### {selected_name}")
    if not bool(municipality["entrega_completa"]):
        st.warning(
            "Este município não atendeu às cinco entregas essenciais. A ausência de "
            "informação pode dominar o resultado; por rigor metodológico, o what-if abaixo "
            "não é apresentado e as regras são rotuladas como bloqueadas pela entrega."
        )

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("ICF oficial", f"{official_band} · {format_percent(official_percent)}")
    kpi_2.metric("Não pontuações no escopo", len(not_scored))
    kpi_3.metric(
        "Ganho máximo contrafactual",
        format_percent(potential_gain) if municipality["entrega_completa"] else "Não estimado",
    )
    kpi_4.metric(
        "Faixa simulada",
        f"{simulated_band} · {format_percent(simulated_percent)}"
        if municipality["entrega_completa"]
        else "Não estimada",
    )

    if municipality["entrega_completa"]:
        st.warning(
            "O cenário pressupõe recuperação integral de todas as não pontuações "
            "selecionadas e mantém as demais regras constantes. Ele **não garante** aceitação "
            "de retificação, mudança da nota oficial ou efeito automático na CAPAG."
        )

    if municipality["entrega_completa"]:
        show_only_pending = st.toggle("Mostrar somente não pontuadas", value=True)
        table = not_scored if show_only_pending else diagnostics
    else:
        st.markdown("#### Entregas essenciais que bloquearam o diagnóstico")
        table = pd.DataFrame(
            [
                {
                    "Código": code,
                    "Status": "Pontuação integral" if municipality.get(code) == 1 else "Ausente/não pontuada",
                }
                for code in DELIVERY_CHECKS
            ]
        )
    if table.empty:
        st.success("Nenhuma não pontuação foi encontrada no escopo selecionado.")
    else:
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "Descrição": st.column_config.TextColumn(width="large"),
                "Relatórios": st.column_config.TextColumn(width="medium"),
                "Impacto máximo (p.p.)": st.column_config.NumberColumn(format="%.2f"),
            },
        )
        table_export = table.copy()
        table_export.insert(0, "Edição", RANKING_EDITION)
        table_export.insert(1, "Exercício", EXERCISE)
        table_export.insert(2, "Data de corte", OFFICIAL_CUTOFF)
        table_export.insert(3, "Escopo", scope_description)
        table_export.insert(4, "Ente", municipality["Ente"])
        table_export.insert(5, "Município", selected_name)
        table_export["SHA-256 do snapshot"] = RANKING_SNAPSHOT_SHA256
        file_kind = (
            "entregas_essenciais"
            if not municipality["entrega_completa"]
            else ("pendentes" if show_only_pending else "completa")
        )
        st.download_button(
            "Baixar fila de conferência (CSV)",
            data=table_export.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
            file_name=(
                f"fila_conferencia_{municipality['Ente']}_{EXERCISE}_"
                f"{scope_slug}_{file_kind}.csv"
            ),
            mime="text/csv",
            width="stretch",
        )

    with st.expander("Como transformar a fila em plano de ação", expanded=False):
        st.markdown(
            """
            1. Confirme a entrega e a homologação dos demonstrativos.
            2. Comece pelas conciliações diretas entre DCA, RREO e RGF.
            3. Nas regras com MSC, confira contas, fonte/destinação, natureza, função e De/Para.
            4. Registre responsável, prazo, evidência e providência em sua rotina interna.
            5. Use a validação on-line para reexecutar as regras após o ajuste.
            """
        )

with tab_method:
    st.subheader("Escopos que não devem ser confundidos")
    method_rows = pd.DataFrame(
        [
            {"Escopo": "Ranking 2026 (exercício 2025)", "Quantidade": 207, "Uso": "Referência metodológica geral"},
            {"Escopo": "Aplicável a municípios", "Quantidade": 195, "Uso": "Denominador do what-if municipal"},
            {"Escopo": "Cruzamentos", "Quantidade": 72, "Uso": "17 D2 + 28 D3 + 27 D4"},
            {"Escopo": "Sem MSC/matriz", "Quantidade": 36, "Uso": "23 D3 + 13 D4"},
        ]
    )
    st.dataframe(method_rows, hide_index=True, width="stretch")
    st.caption(
        "As 72 verificações representam uma tipologia funcional de cruzamento; "
        "elas não correspondem à dimensão oficial D4."
    )

    st.subheader("Fórmula do cenário what-if")
    st.latex(
        r"G_m = \frac{\sum_{j \in C}(1-s_{mj})}{195}\times 100"
    )
    st.latex(r"P_m^{sim} = \min(100, P_m + G_m)")
    st.markdown(
        "A simulação é um **limite máximo contrafactual**. Ela não reproduz interações "
        "entre regras, não comprova a causa da não pontuação e não altera o Ranking anual encerrado."
    )

    st.subheader("Rastreabilidade")
    st.code(
        "Base de origem (SHA-256):\n"
        "4cf62c7cd0ad963969f334c9c76927064c9807e43f5f772427e61a6722c14f29\n\n"
        "Metodologia de origem (SHA-256):\n"
        "b4a6d9fec75338908223f59eee2736b667b945e7253a530f30dda9472fd3c021",
        language=None,
    )
    st.caption(
        "O recorte preservado contém 92 municípios, as cinco entregas essenciais, "
        f"as 72 verificações de cruzamento e os campos oficiais do ICF; corte em {OFFICIAL_CUTOFF}."
    )

app_footer()
