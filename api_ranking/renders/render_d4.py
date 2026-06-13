import pandas as pd
import streamlit as st


def _render_dimension_tab(tab, ctx, prefix, title):
    with tab:
        st.subheader(title)

        final = ctx.get("final", pd.DataFrame())
        if not isinstance(final, pd.DataFrame) or final.empty or "Dimensão" not in final.columns:
            st.info("Nenhuma verificação disponível para este grupo.")
            return

        data = final[final["Dimensão"].astype(str).str.startswith(prefix)].copy()
        if data.empty:
            st.info("Nenhuma verificação disponível para este grupo.")
            return

        for row in data.to_dict("records"):
            code = str(row.get("Dimensão", "")).upper()
            resposta = row.get("Resposta", "")
            nota = row.get("Nota", "")
            descricao = row.get("Descrição da Dimensão", "")
            obs = row.get("OBS", "")
            detail = ctx.get(f"{code.lower()}_t", pd.DataFrame())

            with st.expander(f"{code} - {resposta}", expanded=False):
                if descricao:
                    st.markdown(f"**Descrição:** {descricao}")
                st.markdown(f"**Resposta:** {resposta}")
                if nota != "":
                    st.markdown(f"**Nota:** {nota}")
                if obs:
                    st.markdown(f"**OBS:** {obs}")
                if isinstance(detail, pd.DataFrame) and not detail.empty:
                    st.dataframe(detail, use_container_width=True, hide_index=True)


def render_tab_d4(tab, ctx):
    _render_dimension_tab(tab, ctx, "D4_", "D4 - Cruzamentos Demonstrativos x MSC")
