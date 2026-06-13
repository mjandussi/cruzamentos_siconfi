import streamlit as st
import pandas as pd
from core.layout import setup_page, page_brand
from core.auth import is_authed, authenticate

setup_page(
    page_title="CRUZAMENTOS SICONFI - Login",
    logo_path="assets/logo-mark.svg",
    require_login_enabled=False,
    show_top_nav=False,
)
page_brand(
    title="CRUZAMENTOS SICONFI",
    logo_path="assets/logo-mark.svg",
)


st.write("## Acesso ao APP")

if is_authed():
    st.switch_page("pages/00_🏠 Home.py")

with st.form("login", clear_on_submit=False):
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    ok = st.form_submit_button("Entrar")
    if ok:
        success, message = authenticate(u, p)
        if success:
            st.success(message)
            st.switch_page("pages/00_🏠 Home.py")
        else:
            st.error(message)


st.divider()

st.markdown(f"""
<div class="footer">
  <b>Contato</b><br>
  ✉️ <a href="mailto:mjandussi@gmail.com">mjandussi@gmail.com</a> &nbsp;•&nbsp;
  🐙 <a href="https://github.com/mjandussi" target="_blank">github.com/mjandussi</a>
  <br><br>
  <small>© {pd.Timestamp.today().year} — CRUZAMENTOS SICONFI >> Fontes oficiais: STN/Siconfi.</small>
</div>
""", unsafe_allow_html=True)
