from api_ranking.renders.result_dashboard import render_dimension_panel


def render_tab_d4(tab, ctx):
    """Mantém a API histórica da página e usa o painel compacto compartilhado."""
    with tab:
        render_dimension_panel(
            ctx,
            "D4_",
            "D4 · Consistência entre demonstrativos e MSC",
            key_prefix="d4",
        )
