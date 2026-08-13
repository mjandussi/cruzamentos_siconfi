from api_ranking.renders.result_dashboard import render_dimension_panel


def render_tab_d2(tab, ctx):
    """Mantém a API histórica da página e usa o painel compacto compartilhado."""
    with tab:
        render_dimension_panel(
            ctx,
            "D2_",
            "D2 · Qualidade da DCA e cruzamentos com a MSC",
            key_prefix="d2",
        )
