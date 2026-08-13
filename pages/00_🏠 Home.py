"""Página inicial orientada aos dois modos analíticos do produto."""

import streamlit as st

from core.auth import get_current_user, is_authed
from core.layout import (
    analysis_stepper,
    app_footer,
    page_brand,
    page_intro,
    render_main_nav,
    setup_page,
)


setup_page(
    page_title="CRUZAMENTOS SICONFI - Início",
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
render_main_nav(active="Home")

current_user = (get_current_user() or "").strip()
welcome = f"Olá, {current_user}. " if current_user else ""
page_intro(
    "Da não pontuação à evidência",
    eyebrow="Qualidade da informação contábil e fiscal",
    description=(
        f"{welcome}Identifique inconsistências entre DCA, RREO, RGF e MSC, "
        "entenda o impacto potencial e organize a conferência antes de retificar."
    ),
    icon="◈",
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric(
    "Escopo metodológico 2025",
    "72/72",
    help="17 D2 + 28 D3 + 27 D4, todas com função concreta no motor.",
)
metric_2.metric("Conciliações sem MSC", "36", help="23 D3 + 13 D4.")
metric_3.metric("Municípios no recorte RJ", "92")
metric_4.metric("Critérios do artefato", "4", help="Funcionamento, rastreabilidade, reprodutibilidade e potencial analítico.")

st.markdown("## Escolha o momento da análise")
online_column, historical_column = st.columns(2)

with online_column:
    with st.container(border=True):
        st.markdown("### 🔎 Validação on-line")
        st.markdown(
            "Consulta os demonstrativos disponíveis **agora** na API do Siconfi, "
            "executa os cruzamentos do escopo e mostra os valores usados."
        )
        st.markdown(
            "**Use para:** conferência preventiva, investigação da origem e "
            "reexecução após ajustes."
        )
        if st.button(
            "Iniciar validação on-line",
            type="primary",
            width="stretch",
            key="home_online",
        ):
            st.switch_page("pages/01_✅ Cruzamentos do Ranking.py")

with historical_column:
    with st.container(border=True):
        st.markdown("### 📚 Diagnóstico histórico")
        st.markdown(
            "Lê a base anual encerrada do Ranking 2026 (exercício 2025) e "
            "analisa as 72 verificações de cruzamento nos municípios do RJ."
        )
        st.markdown(
            "**Use para:** contextualizar não pontuações, priorizar regras e simular "
            "um limite máximo de recuperação do ICF."
        )
        if st.button(
            "Explorar base encerrada",
            width="stretch",
            key="home_historical",
        ):
            st.switch_page("pages/02_📚 Diagnóstico Histórico.py")

st.markdown("## Fluxo recomendado")
analysis_stepper(
    current_step=1,
    steps=[
        "Definir ente, exercício e contexto temporal",
        "Confirmar entrega e homologação",
        "Executar e priorizar cruzamentos",
        "Investigar evidências e registrar providências",
        "Reexecutar após o ajuste",
    ],
)

st.markdown("## O que o produto analisa")
scope_1, scope_2, scope_3 = st.columns(3)
with scope_1:
    with st.container(border=True):
        st.markdown("### D2 · Informações contábeis")
        st.markdown("Confrontos entre DCA e MSC de encerramento, conforme a vigência da regra.")
with scope_2:
    with st.container(border=True):
        st.markdown("### D3 · Informações fiscais")
        st.markdown("Consistência dentro de RREO/RGF e entre relatórios fiscais e MSC.")
with scope_3:
    with st.container(border=True):
        st.markdown("### D4 · Contábil × fiscal")
        st.markdown("Compatibilidade entre DCA, RREO, RGF e MSC de dezembro.")

st.warning(
    "O aplicativo é uma ferramenta de **apoio à conferência**. Ele não audita "
    "as contas, não decide qual demonstrativo está correto, não recalcula a nota "
    "oficial e não substitui o julgamento do profissional contábil."
)

with st.expander("Referências oficiais e orientações", expanded=False):
    st.markdown(
        """
        - [Ranking da Qualidade da Informação Contábil e Fiscal](https://ranking-municipios.tesouro.gov.br/)
        - [Mapeamentos da Matriz de Saldos Contábeis](https://siconfi.tesouro.gov.br/siconfi/pages/public/conteudo/conteudo.jsf?id=12503)
        - [Manual de Demonstrativos Fiscais](https://www.gov.br/tesouronacional/pt-br/contabilidade-e-custos/manuais/manual-de-demonstrativos-fiscais-mdf)
        - [Manual de Contabilidade Aplicada ao Setor Público](https://www.tesourotransparente.gov.br/publicacoes/manual-de-contabilidade-aplicada-ao-setor-publico-mcasp/2025/26)
        - [Consultas públicas da Federação](https://www.gov.br/tesouronacional/pt-br/contabilidade-e-custos/federacao/consultas-publicas-federacao)
        """
    )

app_footer()
