from __future__ import annotations

import base64
from copy import deepcopy
from pathlib import Path
import streamlit as st

from core.auth import get_current_user, is_auth_enabled, logout, require_login

_ASSETS_CSS = Path("assets/theme.css")
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = str(_PROJECT_ROOT / "assets" / "logo-mark.svg")

# Menu compartilhado do app
APP_MENU = {
    "Home": [
        {"path": "pages/00_🏠 Home.py", "label": "Início", "icon": "🏠"},
    ],
    "Cruzamentos": [
        {"path": "pages/01_✅ Cruzamentos do Ranking.py", "label": "Cruzamentos", "icon": "✅"},
    ],
}


def get_app_menu() -> dict:
    menu = deepcopy(APP_MENU)
    for section, links in list(menu.items()):
        menu[section] = [item for item in links if Path(item["path"]).exists()]
        if not menu[section]:
            del menu[section]
    return menu


def _img_data_uri(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    data = p.read_bytes()
    ext = p.suffix.lower().strip(".")
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _load_global_css():
    if _ASSETS_CSS.exists():
        st.markdown(f"<style>{_ASSETS_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _infer_active_label(page_title: str) -> str:
    t = (page_title or "").lower()
    if "msc" in t or "matriz" in t:
        return "MSC"
    if "valida" in t or "ranking" in t or "cruzamento" in t:
        return "Cruzamentos"
    if "metodolog" in t or "vigenc" in t or "verifica" in t:
        return "Metodologia"
    if "dashboard" in t or "rreo" in t or "rgf" in t:
        return "Dashboards"
    if "índice" in t or "indice" in t:
        return "Índices"
    return "Home"


def setup_page(
    page_title: str = "CRUZAMENTOS SICONFI",
    layout: str = "wide",
    hide_default_nav: bool = False,  # mantido por compatibilidade
    require_login_enabled: bool = True,
    page_icon: str | None = None,
    logo_path: str = "assets/logo-mark.svg",
    active_nav: str | None = None,
    show_top_nav: bool = True,
) -> None:
    # Favicon da aba: Streamlit aceita o mesmo que st.image (incl. SVG em versões recentes).
    # Antes usávamos emoji quando era .svg — aí a aba não mostrava o logo.
    if page_icon is not None:
        resolved_icon = page_icon
    else:
        lp = Path(logo_path)
        resolved_icon = str(lp) if lp.exists() else "📊"

    st.set_page_config(
        page_title=page_title,
        page_icon=resolved_icon,
        layout=layout,
        initial_sidebar_state="collapsed",
    )

    _ = hide_default_nav

    try:
        qp = st.query_params
        has_logout = "logout" in qp
    except Exception:
        qp = st.experimental_get_query_params()
        has_logout = "logout" in qp

    if has_logout:
        logout()
        try:
            st.query_params.clear()
        except Exception:
            st.experimental_set_query_params()
        st.switch_page("app.py")

    _load_global_css()
    st.session_state["_brand_data_uri"] = _img_data_uri(logo_path)

    if require_login_enabled:
        require_login(app_name=page_title)

    if show_top_nav:
        navbar(active=active_nav or _infer_active_label(page_title))


def navbar(active: str = "Home", show_title_next_to_logo: bool = False, show_brand_in_nav: bool = False) -> None:
    # Navbar superior: páginas principais do app (a sidebar fica oculta neste tema).
    items = [
        ("Home", "🏠", "pages/00_🏠 Home.py"),
        ("Cruzamentos", "✅", "pages/01_✅ Cruzamentos do Ranking.py"),
    ]

    if show_brand_in_nav:
        c_logo, c_menu, _c_right = st.columns([0.12, 0.83, 0.05])
    else:
        c_menu = st.container()

    if show_brand_in_nav:
        with c_logo:
            src = st.session_state.get("_brand_data_uri", "")
            title_html = '<span class="title">CRUZAMENTOS SICONFI</span>' if show_title_next_to_logo else ""
            st.markdown(f'<div class="brand"><img src="{src}" alt="logo"/>{title_html}</div>', unsafe_allow_html=True)

    with c_menu:
        cols = st.columns(len(items))
        for idx, (lbl, icon, path) in enumerate(items):
            with cols[idx]:
                btn_type = "primary" if lbl == active else "secondary"
                if st.button(
                    f"{icon} {lbl}",
                    key=f"top_nav_{idx}_{lbl}",
                    type=btn_type,
                    use_container_width=True,
                ) and st.session_state.get("_current_page") != lbl:
                    st.session_state["_current_page"] = lbl
                    st.switch_page(path)
    st.markdown("<div class='top-nav-spacer'></div>", unsafe_allow_html=True)


def page_brand(title: str, logo_path: str | None = None, show_logout: bool = False, logout_target: str = "app.py"):
    left_col, right_col = st.columns([0.82, 0.18], vertical_alignment="center")
    with left_col:
        logo_col, title_col = st.columns([0.08, 0.92], vertical_alignment="center")
        with logo_col:
            if logo_path and Path(logo_path).exists():
                st.image(logo_path, width=52)
        with title_col:
            st.write(f"### {title}")

    with right_col:
        current_user = get_current_user()
        user_html = (
            f'<span class="user-pill">👤 {current_user}</span>'
            if current_user
            else ""
        )
        logout_html = (
            '<a class="btn-sair-link" href="?logout=1">⎋ Sair</a>'
            if show_logout and is_auth_enabled()
            else ""
        )
        separator_html = (
            '<span class="top-actions-separator" aria-hidden="true">|</span>'
            if user_html and logout_html
            else ""
        )
        if user_html or logout_html:
            st.markdown(
                f"""
                <div class="top-actions">
                  {user_html}
                  {separator_html}
                  {logout_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("<div class='brand-divider'></div>", unsafe_allow_html=True)


def sidebar_menu(structure: dict, *, use_expanders: bool = True, expanded: bool = True, show_env_info: bool = True):
    with st.sidebar:
        _ = show_env_info
        st.markdown("## 📚 Módulos")
        for section, links in structure.items():
            if use_expanders:
                with st.expander(section, expanded=expanded):
                    for item in links:
                        st.page_link(item["path"], label=f'{item.get("icon","")} {item["label"]}'.strip())
            else:
                st.markdown(f"### {section}")
                for item in links:
                    st.page_link(item["path"], label=f'{item.get("icon","")} {item["label"]}'.strip())
                st.divider()
        if is_auth_enabled():
            if st.button("⎋ Sair", key="sidebar_logout_btn"):
                logout()
                st.switch_page("app.py")


def hero():
    st.title("CRUZAMENTOS SICONFI")
    st.caption("Dados e análises do SICONFI — use o menu superior para navegar.")
