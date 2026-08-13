from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime
import html
from pathlib import Path
import streamlit as st

from core.auth import get_current_user, is_auth_enabled, logout, require_login

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ASSETS_CSS = _PROJECT_ROOT / "assets" / "theme.css"
LOGO_PATH = str(_PROJECT_ROOT / "assets" / "logo-mark.svg")

_MAIN_NAV_ITEMS = (
    ("Home", "🏠", "pages/00_🏠 Home.py"),
    ("Validação on-line", "✅", "pages/01_✅ Cruzamentos do Ranking.py"),
    ("Diagnóstico histórico", "📚", "pages/02_📚 Diagnóstico Histórico.py"),
)

# Menu compartilhado do app
APP_MENU = {
    "Home": [
        {"path": "pages/00_🏠 Home.py", "label": "Início", "icon": "🏠"},
    ],
    "Cruzamentos": [
        {"path": "pages/01_✅ Cruzamentos do Ranking.py", "label": "Validação on-line", "icon": "✅"},
    ],
    "Diagnóstico": [
        {"path": "pages/02_📚 Diagnóstico Histórico.py", "label": "Diagnóstico histórico", "icon": "📚"},
    ],
}


def _resolve_project_path(path: str | Path) -> Path:
    """Resolve caminhos relativos a partir da raiz do projeto."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else _PROJECT_ROOT / candidate


def get_app_menu() -> dict:
    menu = deepcopy(APP_MENU)
    for section, links in list(menu.items()):
        menu[section] = [
            item for item in links
            if _resolve_project_path(item["path"]).exists()
        ]
        if not menu[section]:
            del menu[section]
    return menu


def _img_data_uri(path: str | Path) -> str:
    p = _resolve_project_path(path)
    if not p.exists():
        return ""
    data = p.read_bytes()
    ext = p.suffix.lower().strip(".")
    mime = {
        "svg": "image/svg+xml",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }.get(ext, f"image/{ext}")
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _load_global_css():
    if _ASSETS_CSS.exists():
        st.markdown(f"<style>{_ASSETS_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def _infer_active_label(page_title: str) -> str:
    t = (page_title or "").lower()
    if "diagnóstico" in t or "diagnostico" in t or "histórico" in t or "historico" in t:
        return "Diagnóstico histórico"
    if "msc" in t or "matriz" in t:
        return "MSC"
    if "valida" in t or "ranking" in t or "cruzamento" in t:
        return "Validação on-line"
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
        lp = _resolve_project_path(logo_path)
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
        render_main_nav(active=active_nav or _infer_active_label(page_title))


def _render_nav_buttons(active: str) -> None:
    items = [
        item for item in _MAIN_NAV_ITEMS
        if _resolve_project_path(item[2]).exists()
    ]
    if not items:
        return

    active_label = {
        "Cruzamentos": "Validação on-line",
        "Início": "Home",
        "Diagnóstico Histórico": "Diagnóstico histórico",
    }.get(active, active)
    cols = st.columns(len(items))
    for idx, (label, icon, path) in enumerate(items):
        with cols[idx]:
            clicked = st.button(
                f"{icon} {label}",
                key=f"top_nav_{idx}_{label}",
                type="primary" if label == active_label else "secondary",
                width="stretch",
            )
            if clicked and label != active_label:
                st.switch_page(path)


def render_main_nav(active: str = "Home") -> None:
    """Renderiza a navegação principal compartilhada entre as páginas."""
    with st.container(key="app_main_navigation"):
        _render_nav_buttons(active)
    st.markdown("<div class='top-nav-spacer' aria-hidden='true'></div>", unsafe_allow_html=True)


def navbar(
    active: str = "Home",
    show_title_next_to_logo: bool = False,
    show_brand_in_nav: bool = False,
) -> None:
    """Alias compatível da navegação antiga."""
    if not show_brand_in_nav:
        render_main_nav(active)
        return

    c_logo, c_menu = st.columns([0.18, 0.82], vertical_alignment="center")
    with c_logo:
        src = html.escape(st.session_state.get("_brand_data_uri", ""), quote=True)
        title_html = (
            '<span class="nav-brand__title">CRUZAMENTOS SICONFI</span>'
            if show_title_next_to_logo else ""
        )
        st.markdown(
            f'<div class="nav-brand"><img src="{src}" alt="" aria-hidden="true"/>{title_html}</div>',
            unsafe_allow_html=True,
        )
    with c_menu:
        _render_nav_buttons(active)
    st.markdown("<div class='top-nav-spacer' aria-hidden='true'></div>", unsafe_allow_html=True)


def page_brand(
    title: str,
    logo_path: str | None = None,
    show_logout: bool = False,
    logout_target: str = "app.py",
) -> None:
    """Exibe o cabeçalho da marca com conteúdo escapado e layout responsivo."""
    _ = logout_target  # mantido na assinatura por compatibilidade
    safe_title = html.escape(str(title))
    logo_src = _img_data_uri(logo_path) if logo_path else ""
    logo_html = (
        f'<img class="app-brand-logo" src="{html.escape(logo_src, quote=True)}" '
        'alt="" aria-hidden="true"/>'
        if logo_src else ""
    )

    current_user = get_current_user()
    safe_user = html.escape(str(current_user)) if current_user else ""
    user_html = (
        '<span class="user-pill" title="Usuário conectado">'
        '<span aria-hidden="true">👤</span>'
        f'<span class="user-pill__name">{safe_user}</span>'
        '</span>'
        if safe_user else ""
    )
    logout_html = (
        '<a class="btn-sair-link" href="?logout=1" aria-label="Sair do aplicativo">'
        '<span aria-hidden="true">⎋</span> Sair</a>'
        if show_logout and is_auth_enabled()
        else ""
    )
    actions_html = (
        f'<div class="app-brand-actions">{user_html}{logout_html}</div>'
        if user_html or logout_html else ""
    )

    st.markdown(
        f"""
        <header class="app-brandbar" aria-label="Cabeçalho do aplicativo">
          <div class="app-brand-main">
            {logo_html}
            <span class="app-brand-name">{safe_title}</span>
          </div>
          {actions_html}
        </header>
        """,
        unsafe_allow_html=True,
    )


def page_intro(
    title: str,
    eyebrow: str | None = None,
    description: str | None = None,
    *,
    icon: str | None = None,
) -> None:
    """Renderiza uma abertura de página semanticamente consistente."""
    eyebrow_html = (
        f'<p class="page-hero__eyebrow">{html.escape(str(eyebrow))}</p>'
        if eyebrow else ""
    )
    icon_html = (
        f'<span class="page-hero__icon" aria-hidden="true">{html.escape(str(icon))}</span>'
        if icon else ""
    )
    description_html = (
        f'<p class="page-hero__description">{html.escape(str(description))}</p>'
        if description else ""
    )
    st.markdown(
        f"""
        <section class="page-hero">
          {eyebrow_html}
          <h1>{icon_html}{html.escape(str(title))}</h1>
          {description_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def resolve_analysis_step(
    *,
    context_selected: bool,
    extract_ready: bool,
    processing: bool,
    results_ready: bool,
) -> int:
    """Resolve a etapa atual a partir do estado real do fluxo."""
    if not context_selected:
        return 1
    if results_ready:
        return 4
    if processing:
        return 3
    if extract_ready:
        return 2
    return 1


def analysis_stepper(
    current_step: int = 1,
    steps: tuple[str, ...] | list[str] | None = None,
) -> None:
    """Mostra o progresso do fluxo analítico em etapas, sem controlar estado."""
    labels = steps or [
        "Selecionar ente",
        "Validar entregas",
        "Processar análise",
        "Revisar resultados",
    ]
    if not labels:
        return

    current = max(1, min(int(current_step), len(labels)))
    items = []
    for index, label in enumerate(labels, start=1):
        if index < current:
            state = "complete"
            state_label = "Concluída"
            marker = "✓"
        elif index == current:
            state = "active"
            state_label = "Etapa atual"
            marker = str(index)
        else:
            state = "pending"
            state_label = "Pendente"
            marker = str(index)
        aria_current = ' aria-current="step"' if state == "active" else ""
        items.append(
            f'<li class="analysis-step analysis-step--{state}"{aria_current}>'
            f'<span class="analysis-step__marker" aria-hidden="true">{marker}</span>'
            '<span class="analysis-step__content">'
            f'<span class="sr-only">{state_label}: </span>{html.escape(str(label))}'
            '</span></li>'
        )

    st.markdown(
        '<nav class="analysis-stepper" aria-label="Progresso da análise">'
        f'<ol>{"".join(items)}</ol></nav>',
        unsafe_allow_html=True,
    )


def app_footer(
    *,
    product_name: str = "CRUZAMENTOS SICONFI",
    developer: str = "Marcelo Jandussi",
    contact_email: str = "mjandussi@gmail.com",
    github_url: str = "https://github.com/mjandussi",
    source_label: str = "Fontes oficiais: STN/Siconfi.",
    year: int | None = None,
) -> None:
    """Renderiza um rodapé compartilhado, legível e acessível."""
    safe_product = html.escape(str(product_name))
    safe_developer = html.escape(str(developer))
    safe_source = html.escape(str(source_label))
    safe_email = html.escape(str(contact_email), quote=True)
    safe_github = html.escape(str(github_url), quote=True)
    display_year = int(year) if year is not None else datetime.now().year

    contact_links = []
    if contact_email:
        contact_links.append(
            f'<a href="mailto:{safe_email}">E-mail</a>'
        )
    if github_url:
        contact_links.append(
            f'<a href="{safe_github}" target="_blank" rel="noopener noreferrer">'
            'GitHub<span class="sr-only"> (abre em nova aba)</span></a>'
        )
    contact_separator = '<span aria-hidden="true">•</span>'
    contacts_html = (
        '<nav class="app-footer__links" aria-label="Contato">'
        f'{contact_separator.join(contact_links)}</nav>'
        if contact_links else ""
    )

    st.markdown(
        f"""
        <footer class="app-footer" role="contentinfo">
          <p><strong>{safe_product}</strong> · Desenvolvido por {safe_developer} · © {display_year}</p>
          <p>{safe_source}</p>
          {contacts_html}
        </footer>
        """,
        unsafe_allow_html=True,
    )


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
    page_intro(
        "CRUZAMENTOS SICONFI",
        description="Dados e análises do SICONFI — use o menu superior para navegar.",
    )


# Nome anterior preservado para integrações que já o tenham importado.
page_footer = app_footer
