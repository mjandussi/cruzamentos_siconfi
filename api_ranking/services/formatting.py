import streamlit as st
import re
import pandas as pd


# Verificações cuja métrica integra o escopo CAPAG no Ranking Siconfi (quadro metodológico STN).
# Fonte: quadro descritivo das verificações em https://www.tesourotransparente.gov.br/ranking
# (somente verificações marcadas explicitamente como "CAPAG" no quadro). Verificações novas
# sob consulta pública (D4_00046+) não entram aqui até serem homologadas pela STN.
# Complementa `eh_verificacao_capag` quando a descrição na app não contém a palavra "CAPAG".
CODIGOS_VERIFICACAO_CAPAG_RANKING = frozenset({
    "D2_00003", "D2_00004", "D2_00010", "D2_00011", "D2_00012", "D2_00028", "D2_00029",
    "D2_00033", "D2_00035", "D2_00044", "D2_00045", "D2_00046", "D2_00047", "D2_00048", "D2_00049",
    "D2_00084", "D2_00085", "D2_00097", "D2_00099",
    "D3_00005", "D3_00008", "D3_00009", "D3_00010", "D3_00013", "D3_00014", "D3_00015", "D3_00016",
    "D3_00021", "D3_00022", "D3_00023", "D3_00024", "D3_00026", "D3_00028", "D3_00030",
    "D3_00044", "D3_00045",
    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00010", "D4_00012", "D4_00017", "D4_00020",
    "D4_00021", "D4_00023", "D4_00025", "D4_00028", "D4_00035", "D4_00037", "D4_00038", "D4_00039",
    "D4_00040", "D4_00041", "D4_00042", "D4_00043", "D4_00045",
})


def eh_verificacao_capag(dimensao: str | None, descricao: str | None = None) -> bool:
    """True se a verificação é ligada à CAPAG no ranking (código oficial ou texto explícito)."""
    cod = str(dimensao or "").strip().upper()
    if cod in CODIGOS_VERIFICACAO_CAPAG_RANKING:
        return True
    desc = str(descricao or "")
    return "CAPAG" in desc.upper()


def titulo_expander_verificacao(emoji: str, codigo_verificacao: str, titulo_curto: str) -> str:
    """Título padrão dos expanders de detalhe; acrescenta sufixo oficial quando for verificação CAPAG."""
    sux = " - CAPAG" if eh_verificacao_capag(codigo_verificacao) else ""
    return f"{emoji} Detalhes {codigo_verificacao} - {titulo_curto}{sux}"


def legenda_capag_na_aba_detalhe() -> None:
    """Legenda junto à lista de verificações (abas D1–D4), explicando CAPAG na tabela resumo e nos títulos."""
    st.caption(
        "Na **tabela resumo** da página, a coluna **CAPAG** indica as verificações desse escopo (metodologia STN). "
        "Nesta aba, o sufixo **- CAPAG** no título do painel marca o mesmo conjunto."
    )


############################################
############  CRUZAMENROS 2024  ############
############################################

dimensoes_cruzamento = {
    "D2_00044", "D2_00045", "D2_00046", "D2_00047", "D2_00048", "D2_00049", "D2_00050",
    "D2_00058", "D2_00074",
    "D3_00001", "D3_00002", "D3_00005", "D3_00006", "D3_00008", "D3_00009", "D3_00010",
    "D3_00014", "D3_00015", "D3_00016", "D3_00017", "D3_00022", "D3_00023", "D3_00024",
    "D3_00025", "D3_00026", "D3_00027", "D3_00028", "D3_00029", "D3_00030", "D3_00032", "D3_00033", "D3_00034",
    "D3_00035", "D3_00037", "D3_00038", "D3_00039", "D3_00040", "D3_00044", "D3_00048", "D3_00049", "D3_00050", "D3_00056",
    "D4_00001", "D4_00002", "D4_00003", "D4_00004", "D4_00005", "D4_00006", "D4_00007",
    "D4_00009", "D4_00010", "D4_00011", "D4_00012", "D4_00017", "D4_00019", "D4_00020",
    "D4_00021", "D4_00022", "D4_00023", "D4_00024", "D4_00025", "D4_00026", "D4_00034",
    "D4_00037", "D4_00038", "D4_00039", "D4_00040", "D4_00043", "D4_00044", "D4_00045",
    "D4_00046", "D4_00047", "D4_00048", "D4_00049", "D4_00050", "D4_00051",
}



###########################################
################  FUNÇÕES  ################
###########################################

# Aplicar cores condicionais na tabela consolidada
def highlight_resposta(row):
    resposta = str(row.get('Resposta', ''))
    dimensao = str(row.get('Dimensão', ''))
    if resposta == 'OK':
        return ['background-color: #d4edda; color: #155724'] * len(row)
    if resposta.startswith('OK (com dif') and (not dimensoes_cruzamento or dimensao in dimensoes_cruzamento):
        return ['background-color: #fff3cd; color: #856404'] * len(row)
    if resposta == 'N/A':
        return ['background-color: #d1ecf1; color: #0c5460'] * len(row)
    return ['background-color: #f8d7da; color: #721c24'] * len(row)


def emoji_por_resposta(resposta, dimensao=None):
    if resposta == 'OK':
        return "✅"
    if resposta.startswith('OK (com dif') and (not dimensoes_cruzamento or not dimensao or dimensao in dimensoes_cruzamento):
        return "⚠️"
    if resposta == 'N/A':
        return "⏸️"
    return "❌"


def exibir_status_validacao(
    resposta,
    mensagem_ok,
    mensagem_erro,
    mensagem_na=None,
    mensagem_alerta=None,
):
    if resposta == 'OK':
        st.success(mensagem_ok)
        return
    if resposta and resposta.startswith('OK (com dif'):
        st.warning(mensagem_alerta or "⚠️ Consistente, mas com diferença mínima de centavos.")
        return
    if resposta == 'N/A':
        st.info(mensagem_na or "⏸️ Análise não realizada para esta verificação.")
        return
    st.error(mensagem_erro)


def mostrar_tabela_formatada(df, resposta=None, dimensao=None):
        st.markdown("**📋 Detalhes:**")
        dim_inferida = None
        if df is not None and not df.empty and 'dimensao' in df.columns:
            dim_val = str(df['dimensao'].iloc[0])
            match_dim = re.match(r'^(D\\d+_\\d{5})', dim_val)
            if match_dim:
                dim_inferida = match_dim.group(1)
        if dimensao is None and dim_inferida:
            dimensao = dim_inferida
        if resposta is None and dimensao:
            resposta = globals().get(f"resposta_{dimensao.lower()}")
        if resposta and resposta.startswith('OK (com dif') and (not dimensoes_cruzamento or not dimensao or dimensao in dimensoes_cruzamento):
            st.warning("⚠️ Consistente, mas com diferença mínima de centavos")
        if df is None or df.empty:
            st.info("Sem registros para exibir.")
            return
        tabela = df.copy()
        tabela = tabela.rename(columns={'dimensao': 'Descrição'})
        for col in tabela.columns:
            if pd.api.types.is_numeric_dtype(tabela[col]):
                tabela[col] = tabela[col].apply(lambda x: f"R$ {x:,.2f}")
        tabela = tabela.rename(columns={col: col.replace('_', ' ').title() for col in tabela.columns})
        st.dataframe(tabela, use_container_width=True, hide_index=True)
