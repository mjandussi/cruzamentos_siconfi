from api_ranking.renders.result_dashboard import render_dimension_panel


def render_tab_d3(tab, ctx):
    """Mantém a API histórica da página e usa o painel compacto compartilhado."""
    with tab:
        render_dimension_panel(
            ctx,
            "D3_",
            "D3 · Consistência entre RREO, RGF e MSC",
            key_prefix="d3",
        )
