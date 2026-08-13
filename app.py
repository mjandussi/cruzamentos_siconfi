"""Entrada e autenticação do CRUZAMENTOS SICONFI."""

import streamlit as st

from core.auth import authenticate, is_authed
from core.layout import app_footer, page_brand, page_intro, setup_page


setup_page(
    page_title="CRUZAMENTOS SICONFI - Acesso",
    logo_path="assets/logo-mark.svg",
    require_login_enabled=False,
    show_top_nav=False,
)
page_brand(
    title="CRUZAMENTOS SICONFI",
    logo_path="assets/logo-mark.svg",
)
page_intro(
    "Acesse o Cruzamentos Siconfi",
    eyebrow="Diagnóstico contábil e fiscal",
    description=(
        "Valide a consistência entre DCA, RREO, RGF e MSC e transforme "
        "não pontuações em uma fila objetiva de conferência."
    ),
)

if is_authed():
    st.switch_page("pages/00_🏠 Home.py")

left, center, right = st.columns([1, 1.15, 1])
with center:
    with st.container(border=True):
        st.markdown("## Entrar")
        st.caption("Use as credenciais fornecidas pelo administrador do aplicativo.")
        with st.form("login", clear_on_submit=False):
            username = st.text_input("Usuário", autocomplete="username")
            password = st.text_input(
                "Senha",
                type="password",
                autocomplete="current-password",
            )
            submitted = st.form_submit_button(
                "Entrar",
                type="primary",
                width="stretch",
            )
            if submitted:
                success, message = authenticate(username, password)
                if success:
                    st.success(message)
                    st.switch_page("pages/00_🏠 Home.py")
                else:
                    st.error(message)

app_footer()
