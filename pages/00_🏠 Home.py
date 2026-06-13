# pages/00_🏠 Home.py
import streamlit as st
import pandas as pd
from core.layout import setup_page, page_brand
from core.auth import get_current_user, is_authed


def render_main_nav(active: str = "Home") -> None:
    items = [
        ("Home", "🏠", "pages/00_🏠 Home.py"),
        ("Cruzamentos", "✅", "pages/01_✅ Cruzamentos do Ranking.py"),
    ]
    cols = st.columns(len(items))
    for idx, (label, icon, path) in enumerate(items):
        with cols[idx]:
            if st.button(
                f"{icon} {label}",
                key=f"main_nav_v2_{idx}_{label}",
                type="primary" if label == active else "secondary",
                use_container_width=True,
            ) and label != active:
                st.switch_page(path)
    st.markdown("<div class='top-nav-spacer'></div>", unsafe_allow_html=True)

setup_page(
    page_title="CRUZAMENTOS SICONFI - Home",
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
if current_user:
    st.title(f"Bem-vindo ao CRUZAMENTOS SICONFI, {current_user}!")
else:
    st.title("Bem-vindo ao CRUZAMENTOS SICONFI!")

st.divider()
st.markdown("#### Sobre o Aplicativo:")
st.markdown("###### Este aplicativo foi desenvolvido para auxiliar no cruzamento, acompanhamento e análise dos dados do SICONFI.")
st.divider()
st.markdown("#### Seções do Aplicativo")
st.markdown(
    """
<style>
.home-sections { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 1rem; }
.home-section { flex: 1 1 360px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 1.1rem 1.3rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); }
.home-section h4 { margin: 0 0 0.6rem 0; font-weight: 700; font-size: 1rem; }
.home-section ul { margin: 0; padding-left: 1.1rem; }
.home-section li { margin-bottom: 0.45rem; line-height: 1.45; }
.home-section li:last-child { margin-bottom: 0; }
</style>

<div class="home-sections">
  <div class="home-section">
    <h4>✅ Cruzamentos</h4>
    <ul>
      <li><strong>Objetivo:</strong> cruzar e analisar informações contábeis e fiscais com dados oficiais da API do SICONFI.</li>
      <li><strong>Seleção de parâmetros:</strong> define ente e exercício para execução da análise (com suporte a perfil restrito por município).</li>
      <li><strong>Extrato de Entregas:</strong> verifica envios e identifica automaticamente o tipo de relatório disponível.</li>
      <li><strong>Verificações:</strong> processa regras das dimensões D1, D2, D3 e D4 para consistência dos dados.</li>
      <li><strong>Resultados:</strong> exibe nota por dimensão, detalhamento por verificação e indicadores de divergência.</li>
      <li><strong>Fluxo recomendado:</strong> carregar extrato → processar análise → revisar inconsistências → exportar resultados.</li>
    </ul>
  </div>

  <div class="home-section">
    <h4>🔗 Links Úteis STN</h4>
    <ul>
      <li>
        <a href="https://ranking-municipios.tesouro.gov.br/" target="_blank">Ranking Siconfi</a><br>
        Consulta ao ranking da qualidade da informação contábil e fiscal.
      </li>
      <li>
        <a href="https://siconfi.tesouro.gov.br/siconfi/pages/public/conteudo/conteudo.jsf?id=12503" target="_blank">Mapeamentos da Matriz de Saldos Contábeis no Siconfi</a><br>
        Acesso aos mapeamentos da matriz.
      </li>
      <li>
        <a href="https://www.gov.br/tesouronacional/pt-br/contabilidade-e-custos/manuais/manual-de-demonstrativos-fiscais-mdf" target="_blank">Manual de Demonstrativos Fiscais (MDF)</a><br>
        Referência para elaboração e interpretação dos demonstrativos.
      </li>
      <li>
        <a href="https://www.tesourotransparente.gov.br/publicacoes/manual-de-contabilidade-aplicada-ao-setor-publico-mcasp/2025/26" target="_blank">Manual de Contabilidade Aplicada ao Setor Público (MCASP)</a><br>
        Normas e orientações contábeis para o setor público.
      </li>
      <li>
        <a href="https://www.gov.br/tesouronacional/pt-br/contabilidade-e-custos/federacao/consultas-publicas-federacao" target="_blank">Consultas Públicas de Normas Contábeis</a><br>
        Página de consultas públicas da federação.
      </li>
      <li>
        <a href="https://www.gov.br/tesouronacional/pt-br/contabilidade-e-custos/federacao/instrucoes-de-pronunciamentos-contabeis-ipcs" target="_blank">Instruções de Procedimentos Contábeis (IPCs)</a><br>
        Orientações e instruções publicadas pela STN.
      </li>
    </ul>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# Rodapé
st.markdown("---")
st.markdown(
    f"""
<div style='text-align: center; color: #666;'>
    <small>CRUZAMENTOS SICONFI | Desenvolvido por Marcelo Jandussi | © {pd.Timestamp.today().year}</small>
</div>
""",
    unsafe_allow_html=True,
)
