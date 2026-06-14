
# --- 0. Importação das Bibliotecas ---
import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import html
from typing import Dict, List, Any

##########################################################################################
##########################################################################################
# --- 1. Constantes e Funções Auxiliares ---
##########################################################################################
##########################################################################################

URL_BASE_API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
ARQUIVO_ENTES = 'municipios_bspn_2024_GERAL.csv'  # Atualizado para CSV 2024
TIPOS_BALANCO = ['ending_balance', 'beginning_balance', 'period_change']
TOLERANCIA_CENTAVOS = 0.99999
TOLERANCIA_ZERO = 1e-3

def configurar_pagina():
    """Configura o layout e o estilo da página do Streamlit."""
    st.set_page_config(
        page_title="Análise de Dados SICONFI", page_icon="📊",
        layout="wide", initial_sidebar_state="expanded",
    )
    estilo = """
    <style>
        #MainMenu, footer, header {visibility: hidden;} 
        [data-testid="stSidebar"] {min-width: 300px !important;}
        
        /* Estilos Customizados para os Botões */
        .stButton>button {
            border-radius: 8px;
            border: 2px solid #0072C6;
            color: #0072C6;
            background-color: transparent;
            transition: all .3s ease-in-out;
            font-weight: bold;
        }
        
        .stButton>button:hover {
            background-color: #0072C6;
            color: white;
            border-color: #0072C6;
        }

        .stButton>button:disabled {
            background-color: #F0F2F6;
            color: #A0A0A0;
            border-color: #D0D0D0;
            cursor: not-allowed;
        }
    </style>
    """
    st.markdown(estilo, unsafe_allow_html=True)




@st.cache_data
def carregar_dados_entes(caminho_arquivo: str):
    """Carrega os dados dos municípios a partir de um arquivo CSV."""
    try:
        # Detecta o tipo de arquivo pela extensão
        if caminho_arquivo.endswith('.xlsx'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            # Carrega CSV com separador ; e decimal ,
            df = pd.read_csv(caminho_arquivo, sep=';', decimal=',', encoding='utf-8-sig')
        else:
            st.error(f"Formato de arquivo não suportado: {caminho_arquivo}")
            return None
    except FileNotFoundError:
        st.error(f"Arquivo '{caminho_arquivo}' não encontrado. Verifique se ele está na mesma pasta do script.")
        return None
    except Exception as e:
        st.error(f"Erro Crítico ao carregar '{caminho_arquivo}': {e}")
        return None

    # Padronizar nomes de colunas (pode ter variações entre arquivos)
    if 'NO_ENTE' in df.columns:
        df = df.rename(columns={'NO_ENTE': 'NOME_ENTE'})
    if 'CO_IBGE' in df.columns and 'ID_ENTE' not in df.columns:
        df = df.rename(columns={'CO_IBGE': 'ID_ENTE'})

    df['NOME_ENTE'] = df['NOME_ENTE'].astype(str).str.strip()
    df['ID_ENTE'] = df['ID_ENTE'].astype(str).str.strip()
    return df


@st.cache_data
def converter_df_para_csv(df: pd.DataFrame):
    """Converte um DataFrame para CSV codificado em UTF-8 para o botão de download."""
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')

##########################################################################################
##########################################################################################
# --- 2. Funções de Interação com a API ---
##########################################################################################
##########################################################################################

@st.cache_data
def buscar_dados_api(url: str):
    """Busca dados de uma URL da API (para endpoints não paginados)...como RREO, RGF e DCA."""
    try:
        resposta = requests.get(url, timeout=90)
        resposta.raise_for_status()
        dados = resposta.json()
        items = dados.get("items")
        return pd.DataFrame(items) if items else pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de Conexão para a URL: ...{url[-50:]}. Detalhes: {e}")
    except ValueError:
        st.error(f"Erro de Dados: A resposta da API não é um JSON válido para a URL: ...{url[-50:]}")
    return None


@st.cache_data
def buscar_dados_msc_paginado(tipo_msc: str, codigo_ente: str, ano: str, classes: List[int], matriz: str):
    """Busca dados de endpoints da MSC, que são paginados."""
    lista_dfs = []
    for classe_conta in classes:
        for tipo_balanco in TIPOS_BALANCO:
            pular = 0
            while True:
                link = (f'{URL_BASE_API}/msc_{tipo_msc}?id_ente={codigo_ente}&an_referencia={ano}'
                        f'&me_referencia=12&co_tipo_matriz={matriz}&classe_conta={classe_conta}'
                        f'&id_tv={tipo_balanco}&offset={pular}&limit=5000')
                df_parte = buscar_dados_api(link)
                if df_parte is None or df_parte.empty: break
                lista_dfs.append(df_parte)
                pular += 5000
                time.sleep(0.1)
    
    if not lista_dfs:
        return pd.DataFrame()

    return pd.concat(lista_dfs, ignore_index=True)


def construir_urls_api(ano: str, codigo_ente: str, tipo_rgf: str, tipo_rreo: str):
    """Constrói o dicionário de URLs para todos os anexos necessários para as análises."""
    periodo_rgf = "2" if "Simplificado" in tipo_rgf else "3"
    periodicidade = "S" if "Simplificado" in tipo_rgf else "Q"
    periodo_rreo = "6"
    
    urls = {}
    for anexo in ["01", "02", "03", "06", "07", "09"]:
        urls[f"rreo_{anexo}"] = f'{URL_BASE_API}/rreo?an_exercicio={ano}&nr_periodo={periodo_rreo}&co_tipo_demonstrativo={tipo_rreo}&no_anexo=RREO-Anexo%20{anexo}&co_esfera=M&id_ente={codigo_ente}'
    for anexo in ["01", "02", "03", "04", "05"]:
        urls[f"rgf_{anexo}_exec"] = f'{URL_BASE_API}/rgf?an_exercicio={ano}&in_periodicidade={periodicidade}&nr_periodo={periodo_rgf}&co_tipo_demonstrativo={tipo_rgf}&no_anexo=RGF-Anexo%20{anexo}&co_esfera=M&co_poder=E&id_ente={codigo_ente}'
        if anexo in ["01", "05"]:
             urls[f"rgf_{anexo}_leg"] = f'{URL_BASE_API}/rgf?an_exercicio={ano}&in_periodicidade={periodicidade}&nr_periodo={periodo_rgf}&co_tipo_demonstrativo={tipo_rgf}&no_anexo=RGF-Anexo%20{anexo}&co_esfera=M&co_poder=L&id_ente={codigo_ente}'
    for anexo in ["C", "D", "E", "F", "G", "HI"]:
        urls[f"dca_{anexo.lower()}"] = f'{URL_BASE_API}/dca?an_exercicio={ano}&no_anexo=DCA-Anexo%20I-{anexo}&id_ente={codigo_ente}'
        
    return urls


def obter_tipo_relatorio(df_extrato_entregas: pd.DataFrame):
    """Determina o tipo de relatório (Simplificado ou Completo) analisando o extrato."""
    entregaveis_unicos = df_extrato_entregas['entregavel'].unique()
    if "Relatório de Gestão Fiscal Simplificado" in entregaveis_unicos:
        st.success("Tipo de relatório detectado: **SIMPLIFICADO**")
        return "RGF%20Simplificado", "RREO%20Simplificado"
    if "Relatório de Gestão Fiscal" in entregaveis_unicos:
        st.success("Tipo de relatório detectado: **NÃO SIMPLIFICADO (Completo)**")
        return "RGF", "RREO"
    st.error("Não foi possível determinar o tipo de relatório a partir do extrato.")
    return None, None

##########################################################################################
##########################################################################################
# --- 3. Funções de Lógica de Negócio e Tratamento de Dados ---
##########################################################################################
##########################################################################################

def validar_entregas_obrigatorias(df_extrato, nome_ente, tipo_relatorio):
    """
    Verifica se todos os 8 relatórios essenciais foram entregues.
    Esta função atua como um "portão de entrada": se a verificação falhar,
    a análise não prossegue.
    """
    # Define os nomes dos relatórios com base no tipo (Simplificado ou Não)
    nome_rgf = "Relatório de Gestão Fiscal Simplificado" if tipo_relatorio == "Simplificado" else "Relatório de Gestão Fiscal"
    nome_rreo = "Relatório Resumido de Execução Orçamentária Simplificado" if tipo_relatorio == "Simplificado" else "Relatório Resumido de Execução Orçamentária"

    # Lista dos 8 relatórios obrigatórios que serão verificados
    relatorios_obrigatorios = [
        ("MSC Agregada", f"Prefeitura Municipal de {nome_ente}"),
        ("MSC Agregada", f"Câmara de Vereadores de {nome_ente}"),
        ("MSC Encerramento", f"Prefeitura Municipal de {nome_ente}"),
        ("MSC Encerramento", f"Câmara de Vereadores de {nome_ente}"),
        ("Balanço Anual (DCA)", None),  # DCA não tem instituição específica no filtro
        (nome_rgf, f"Prefeitura Municipal de {nome_ente}"),
        (nome_rgf, f"Câmara de Vereadores de {nome_ente}"),
        (nome_rreo, None) # RREO também não tem instituição específica
    ]

    encontrados = 0
    for entregavel, instituicao in relatorios_obrigatorios:
        # Filtra o extrato para encontrar a combinação de relatório e instituição
        if instituicao:
            filtro = df_extrato[(df_extrato['entregavel'] == entregavel) & (df_extrato['instituicao'] == instituicao)]
        else:
            filtro = df_extrato[df_extrato['entregavel'] == entregavel]
        
        # Se encontrou pelo menos uma entrada, conta como +1
        if not filtro.empty:
            encontrados += 1
            
    # Compara o número de relatórios encontrados com o total esperado
    if encontrados >= len(relatorios_obrigatorios):
        st.success(f"Validação de Entregas: **OK** ({encontrados}/{len(relatorios_obrigatorios)} relatórios essenciais encontrados).")
        return True
    else:
        st.error(f"Validação de Entregas: **FALHOU**. A aplicação não pode continuar pois nem todos os relatórios essenciais foram encontrados ({encontrados}/{len(relatorios_obrigatorios)}).")
        return False
    

def formatar_reais(valor: float):
    if isinstance(valor, (int, float)):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)

def determinar_resposta(diferenca: float):
    if pd.isna(diferenca): return "❓ Dados Insuficientes"
    if np.isclose(diferenca, 0, atol=TOLERANCIA_ZERO): return "✅ OK"
    if abs(diferenca) <= TOLERANCIA_CENTAVOS: return "⚠️ OK (Dif. Centavos)"
    return "❌ ERRO"

def _criar_dicionario_resultado(id_dimensao, titulo, grupo, resposta, df_detalhes):
    df_resumo = pd.DataFrame({"Dimensão": [id_dimensao], "Descrição da Dimensão": [titulo], "Resposta": [resposta], "Grupo": [grupo]})
    return {"id": id_dimensao, "titulo": titulo, "grupo": grupo, "df_resumo": df_resumo, "df_detalhes": df_detalhes}


#########  Funções para realizar os tratamento dos dados dos Demonstrativos  #########
def tratar_dados_brutos(dataframes: Dict):
    """
    Vai realizar a inversão do saldo das contas retificadoras na Matriz e na DCA
    """
    df_tratados = {k: v.copy() for k, v in dataframes.items() if v is not None}
    if 'dca_c' in df_tratados and not df_tratados['dca_c'].empty:
        df_tratados['dca_c']['valor'] = df_tratados['dca_c'].apply(
            lambda row: -row['valor'] if 'Deduções' in str(row['coluna']) else row['valor'], axis=1
        )
    if 'msc_encerramento' in df_tratados and not df_tratados['msc_encerramento'].empty:
        msc = df_tratados['msc_encerramento']
        msc['conta_contabil'] = msc['conta_contabil'].astype(str)
        mascara = (((msc['conta_contabil'].str[0].isin(['1', '3', '5', '7'])) & (msc['natureza_conta'] == 'C')) |
                   ((msc['conta_contabil'].str[0].isin(['2', '4', '6', '8'])) & (msc['natureza_conta'] == 'D'))) & \
                  (~msc['tipo_valor'].eq('period_change'))
        msc.loc[mascara, 'valor'] *= -1

    # Tratamento para MSC de Dezembro (MSCC)
    if 'msc_dezembro' in df_tratados and not df_tratados['msc_dezembro'].empty:
        msc_dez = df_tratados['msc_dezembro']
        msc_dez['conta_contabil'] = msc_dez['conta_contabil'].astype(str)
        # A mesma máscara é aplicada aqui
        mascara_dez = (((msc_dez['conta_contabil'].str.startswith(('1', '3', '5', '7'))) & (msc_dez['natureza_conta'] == 'C')) |
                       ((msc_dez['conta_contabil'].str.startswith(('2', '4', '6', '8'))) & (msc_dez['natureza_conta'] == 'D'))) & \
                      (~msc_dez['tipo_valor'].eq('period_change'))
        msc_dez.loc[mascara_dez, 'valor'] *= -1

    return df_tratados

def preparar_dataframes_analise(dataframes_tratados: Dict):
    """
    Vai criar variáveis e colunas para analises como por exemplo o Dígito INTRA
    """
    preparados = {}
    def extrair_digito_intra(valor):
        s = str(valor)
        return s[2:4] if len(s) >= 4 else None

    msc_encerramento = dataframes_tratados.get('msc_encerramento')
    if msc_encerramento is not None and not msc_encerramento.empty:
        df_empenhado = msc_encerramento[msc_encerramento['conta_contabil'].str.match(r"^(62213)", na=False)].copy()
        df_empenhado = df_empenhado[df_empenhado['natureza_despesa'].notna() & (df_empenhado['natureza_despesa'] != '')]
        if not df_empenhado.empty:
            df_empenhado = df_empenhado.query("tipo_valor == 'beginning_balance'").copy()
            df_empenhado['DIGITO_INTRA'] = df_empenhado['natureza_despesa'].apply(extrair_digito_intra)
            preparados['emp_msc_encerramento_com_intra'] = df_empenhado
    
    msc_dezembro = dataframes_tratados.get('msc_dezembro')
    if msc_dezembro is not None and not msc_dezembro.empty:
        preparados['msc_dezembro'] = msc_dezembro
        df_despesa = msc_dezembro[msc_dezembro['conta_contabil'].str.match(r"^(6221)", na=False)].copy()
        df_despesa['DIGITO_INTRA'] = df_despesa['natureza_despesa'].apply(extrair_digito_intra)
        preparados['despesa_msc_dezembro'] = df_despesa
        preparados['emp_msc_dezembro'] = df_despesa.query('tipo_valor == "ending_balance" and conta_contabil in ["622130500", "622130600", "622130700", "622130400"]')
        
    return preparados


#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


##############################################################################################
# --- Funções de Análise da Dimensão D2 ---
##############################################################################################

def analisar_D2_00044(df_msc, df_dca_c):
    titulo = "Receita Realizada (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_c is None or df_msc.empty or df_dca_c.empty: return None
    
    contas = ["621200000", "621310100", "621310200", "621320000", "621390000"]
    valor_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil in @contas")['valor'].sum()
    valor_dca = df_dca_c.query("cod_conta == 'TotalReceitas'")['valor'].sum()
    diferenca = valor_msc - valor_dca
    
    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-C", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D2_00044", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00046(df_msc, df_dca_c):
    titulo = "Receitas com Tributos (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_c is None or df_msc.empty or df_dca_c.empty: return None
    
    rec_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '621200000'").copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    codigos = ["111201", "111250", "111253", "111303", "111451", "1119"]
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos), na=False)]['valor'].sum()
    valor_dca = df_dca_c.query("cod_conta == 'RO1.1.1.0.00.0.0' and coluna == 'Receitas Brutas Realizadas'")['valor'].sum()
    diferenca = valor_msc - valor_dca
    
    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-C", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00046", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00048(df_msc, df_dca_c):
    titulo = "Receitas de Transferências Constitucionais (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_c is None or df_msc.empty or df_dca_c.empty: return None

    rec_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '621200000'").copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    codigos_msc = ["171151", "171152", "172150", "172151", "1751", "1715"]
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()
    
    codigos_dca = ["RO1.7.1.1.51.0.0", "RO1.7.1.1.52.0.0", "RO1.7.1.5.00.0.0", "RO1.7.2.1.50.0.0", "RO1.7.2.1.51.0.0", "RO1.7.5.1.00.0.0"]
    valor_dca = df_dca_c.query("cod_conta in @codigos_dca and coluna == 'Receitas Brutas Realizadas'")['valor'].sum()
    diferenca = valor_msc - valor_dca

    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-C", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00048", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00049(df_msc, df_dca_d):
    titulo = "Despesas Orçamentárias Empenhada, Liquidada e Paga (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_d is None or df_msc.empty or df_dca_d.empty: return None

    # Filtrar apenas registros com natureza_despesa não vazia/nula
    df_msc_filtrado = df_msc[df_msc['natureza_despesa'].notna() & (df_msc['natureza_despesa'] != '')]

    # Calcular valores do MSC com filtro de natureza_despesa
    valor_emp_msc = df_msc_filtrado.query("tipo_valor == 'beginning_balance' and conta_contabil in ['622130100', '622130300', '622130500','622130600','622130700','622130400']")['valor'].sum()
    valor_liq_msc = df_msc_filtrado.query("tipo_valor == 'beginning_balance' and conta_contabil in ['622130300', '622130700','622130400']")['valor'].sum()
    valor_pago_msc = df_msc_filtrado.query("tipo_valor == 'beginning_balance' and conta_contabil == '622130400'")['valor'].sum()

    valor_emp_dca = df_dca_d.query("coluna == 'Despesas Empenhadas' and cod_conta == 'TotalDespesas'")['valor'].sum()
    valor_liq_dca = df_dca_d.query("coluna == 'Despesas Liquidadas' and cod_conta == 'TotalDespesas'")['valor'].sum()
    valor_pago_dca = df_dca_d.query("coluna == 'Despesas Pagas' and cod_conta == 'TotalDespesas'")['valor'].sum()

    df_detalhes = pd.DataFrame({"Estágio da Despesa": ["Empenhado", "Liquidado", "Pago"],
                                "MSC Encerramento": [valor_emp_msc, valor_liq_msc, valor_pago_msc],
                                "DCA Anexo I-D": [valor_emp_dca, valor_liq_dca, valor_pago_dca]})
    df_detalhes["Diferença"] = df_detalhes["MSC Encerramento"] - df_detalhes["DCA Anexo I-D"]

    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00049", titulo, grupo, resposta, df_detalhes)

def analisar_D2_00050(df_msc, df_dca_d):
    titulo = "Inscrição de Restos a Pagar (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_d is None or df_msc.empty or df_dca_d.empty: return None

    valor_rpp_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '622130700'")['valor'].sum()
    valor_rpnp_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil in ['622130500', '622130600']")['valor'].sum()
    
    valor_rpp_dca = df_dca_d.query("coluna == 'Inscrição de Restos a Pagar Processados' and cod_conta == 'TotalDespesas'")['valor'].sum()
    valor_rpnp_dca = df_dca_d.query("coluna == 'Inscrição de Restos a Pagar Não Processados' and cod_conta == 'TotalDespesas'")['valor'].sum()
    
    df_detalhes = pd.DataFrame({"Tipo de Restos a Pagar": ["Processados (RPP)", "Não Processados (RPNP)"], 
                                "MSC Encerramento": [valor_rpp_msc, valor_rpnp_msc], 
                                "DCA Anexo I-D": [valor_rpp_dca, valor_rpnp_dca]})
    df_detalhes["Diferença"] = df_detalhes["MSC Encerramento"] - df_detalhes["DCA Anexo I-D"]
    
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]: 
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D2_00050", titulo, grupo, resposta, df_detalhes)


def analisar_D2_00058(df_msc, df_dca_hi):
    titulo = "VPA com FUNDEB (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_hi is None or df_msc.empty or df_dca_hi.empty: return None
    
    valor_msc_uniao = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '452230000'")['valor'].sum()
    valor_dca_uniao = df_dca_hi.query("cod_conta == 'P4.5.2.2.3.00.00'")['valor'].sum()
    valor_msc_estado = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '452240000'")['valor'].sum()
    valor_dca_estado = df_dca_hi.query("cod_conta == 'P4.5.2.2.4.00.00'")['valor'].sum()
    
    df_detalhes = pd.DataFrame({
        "Fonte FUNDEB": ["Inter OFSS - União", "Inter OFSS - Estado"], 
        "MSC Encerramento": [valor_msc_uniao, valor_msc_estado], 
        "DCA Anexo I-HI": [valor_dca_uniao, valor_dca_estado]
    })
    df_detalhes["Diferença"] = df_detalhes["MSC Encerramento"] - df_detalhes["DCA Anexo I-HI"]
    
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]: 
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D2_00058", titulo, grupo, resposta, df_detalhes)

def analisar_D2_00069(df_emp_msc, df_dca_e):
    titulo = "Despesa por Função: Previdência Social (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_emp_msc is None or df_dca_e is None or df_emp_msc.empty or df_dca_e.empty: return None
    
    valor_msc = df_emp_msc.query("funcao == '09' and DIGITO_INTRA != '91'")['valor'].sum()
    valor_dca = df_dca_e.query("coluna == 'Despesas Empenhadas' and conta == '09 - Previdência Social'")['valor'].sum()
    diferenca = valor_msc - valor_dca
    
    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-E", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D2_00069", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00070(df_emp_msc, df_dca_e):
    titulo = "Despesa por Função: Saúde (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_emp_msc is None or df_dca_e is None or df_emp_msc.empty or df_dca_e.empty: return None
    
    valor_msc = df_emp_msc.query("funcao == '10' and DIGITO_INTRA != '91'")['valor'].sum()
    valor_dca = df_dca_e.query("coluna == 'Despesas Empenhadas' and conta == '10 - Saúde'")['valor'].sum()
    diferenca = valor_msc - valor_dca

    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-E", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00070", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00071(df_emp_msc, df_dca_e):
    titulo = "Despesa por Função: Educação (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_emp_msc is None or df_dca_e is None or df_emp_msc.empty or df_dca_e.empty: return None

    valor_msc = df_emp_msc.query("funcao == '12' and DIGITO_INTRA != '91'")['valor'].sum()
    valor_dca = df_dca_e.query("coluna == 'Despesas Empenhadas' and conta == '12 - Educação'")['valor'].sum()
    diferenca = valor_msc - valor_dca

    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-E", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00071", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00072(df_emp_msc, df_dca_e):
    titulo = "Despesa por Função: Demais Funções (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_emp_msc is None or df_dca_e is None or df_emp_msc.empty or df_dca_e.empty: return None

    valor_msc = df_emp_msc.query("funcao not in ['09', '10', '12'] and DIGITO_INTRA != '91'")['valor'].sum()
    
    contas_dca_excluir = ["09 - Previdência Social", "10 - Saúde", "12 - Educação", "Despesas Exceto Intraorçamentárias", "Despesas Intraorçamentárias"]
    df_demais_dca = df_dca_e.query("coluna == 'Despesas Empenhadas' and conta not in @contas_dca_excluir").copy()
    df_demais_dca = df_demais_dca[df_demais_dca['conta'].str.match(r"^\d{2} - ", na=False)]
    valor_dca = df_demais_dca['valor'].sum()
    
    diferenca = valor_msc - valor_dca
    
    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-E", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00072", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00073(df_emp_msc, df_dca_e):
    titulo = "Despesa por Função: Intraorçamentárias (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_emp_msc is None or df_dca_e is None or df_emp_msc.empty or df_dca_e.empty: return None

    valor_msc = df_emp_msc.query("DIGITO_INTRA == '91'")['valor'].sum()
    valor_dca = df_dca_e.query("coluna == 'Despesas Empenhadas' and conta == 'Despesas Intraorçamentárias'")['valor'].sum()
    diferenca = valor_msc - valor_dca

    df_detalhes = pd.DataFrame({"Fonte": ["MSC Encerramento", "DCA Anexo I-E", "Diferença"], "Valor": [valor_msc, valor_dca, diferenca]})
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D2_00073", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D2_00074(df_msc, df_dca_f):
    titulo = "Pagamento de Restos a Pagar (MSC vs DCA)"
    grupo = "Dimensão II - Informações Contábeis"
    if df_msc is None or df_dca_f is None or df_msc.empty or df_dca_f.empty: return None

    valor_rpnp_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '631400000'")['valor'].sum()
    valor_rpp_msc = df_msc.query("tipo_valor == 'beginning_balance' and conta_contabil == '632200000'")['valor'].sum()
    
    valor_rpnp_dca = df_dca_f.query("coluna == 'Restos a Pagar Não Processados Pagos' and cod_conta == 'TotalDespesas'")['valor'].sum()
    valor_rpp_dca = df_dca_f.query("coluna == 'Restos a Pagar Processados Pagos' and cod_conta == 'TotalDespesas'")['valor'].sum()
    
    df_detalhes = pd.DataFrame({
        "Tipo de Restos a Pagar Pagos": ["Não Processados (RPNP)", "Processados (RPP)"], 
        "MSC Encerramento": [valor_rpnp_msc, valor_rpp_msc], 
        "DCA Anexo I-F": [valor_rpnp_dca, valor_rpp_dca]
    })
    df_detalhes["Diferença"] = df_detalhes["MSC Encerramento"] - df_detalhes["DCA Anexo I-F"]
    
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]: 
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D2_00074", titulo, grupo, resposta, df_detalhes)

##############################################################################################
# --- Funções de Análise da Dimensão D3 ---
##############################################################################################

def analisar_D3_00001(df_rreo_1):
    titulo = "Resultado Orçamentário (RREO Anexo 1)"
    grupo = "Dimensão III - Informações Fiscais"
    if df_rreo_1 is None or df_rreo_1.empty: return None

    try:
        valor_receita = df_rreo_1.query('coluna == "Até o Bimestre (c)" and cod_conta == "TotalReceitas"')['valor'].sum()
        valor_despesa = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" and cod_conta == "TotalDespesas"')['valor'].sum()
        valor_superavit_declarado = df_rreo_1.query('coluna == "Até o Bimestre (c)" and cod_conta == "Deficit"')['valor'].sum()
        valor_deficit_declarado = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" and cod_conta == "Superavit"')['valor'].sum()
        
        df_detalhes = pd.DataFrame([
            {"Item": "Total Receitas", "Valor": valor_receita},
            {"Item": "Total Despesas (-)", "Valor": -valor_despesa},
            {"Item": "Superávit Declarado (-)", "Valor": -valor_deficit_declarado},
            {"Item": "Déficit Declarado (+)", "Valor": valor_superavit_declarado}
        ])
        
        diferenca = df_detalhes['Valor'].sum()
        resposta = determinar_resposta(diferenca)
        
        # Formata para exibição, desfazendo a inversão de sinal
        df_detalhes.loc[1, "Valor"] *= -1
        df_detalhes.loc[2, "Valor"] *= -1
        df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
        df_detalhes = pd.concat([df_detalhes, pd.DataFrame([{"Item": "Diferença de Cálculo", "Valor": formatar_reais(diferenca)}])], ignore_index=True)

    except (KeyError, IndexError):
        return None # Retorna None se alguma query falhar
        
    return _criar_dicionario_resultado("D3_00001", titulo, grupo, resposta, df_detalhes)

def analisar_D3_00002(df_rreo_1, df_rreo_2):
    titulo = "Consistência da Despesa (RREO Anexo 1 vs 2)"
    grupo = "Dimensão III - Informações Fiscais"
    if df_rreo_1 is None or df_rreo_2 is None or df_rreo_1.empty or df_rreo_2.empty: return None

    def obter_valor(df, consulta):
        try:
            resultado = df.query(consulta)
            return resultado['valor'].sum() if not resultado.empty else 0.0
        except Exception:
            return 0.0

    comparacoes = {
        "Dotação Inicial": {
            "rreo1": obter_valor(df_rreo_1, 'coluna == "DOTAÇÃO INICIAL (d)" and cod_conta in ["DespesasExcetoIntraOrcamentarias", "AmortizacaoRefinanciamentoDaDivida"]'),
            "rreo2": obter_valor(df_rreo_2, 'coluna == "DOTAÇÃO INICIAL" and conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
        },
        "Dotação Atualizada": {
            "rreo1": obter_valor(df_rreo_1, 'coluna == "DOTAÇÃO ATUALIZADA (e)" and cod_conta in ["DespesasExcetoIntraOrcamentarias", "AmortizacaoRefinanciamentoDaDivida"]'),
            "rreo2": obter_valor(df_rreo_2, 'coluna == "DOTAÇÃO ATUALIZADA (a)" and conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
        },
        "Despesas Empenhadas": {
            "rreo1": obter_valor(df_rreo_1, 'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" and cod_conta in ["DespesasExcetoIntraOrcamentarias", "AmortizacaoRefinanciamentoDaDivida"]'),
            "rreo2": obter_valor(df_rreo_2, 'coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" and conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
        },
        "Despesas Liquidadas": {
            "rreo1": obter_valor(df_rreo_1, 'coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" and cod_conta in ["DespesasExcetoIntraOrcamentarias", "AmortizacaoRefinanciamentoDaDivida"]'),
            "rreo2": obter_valor(df_rreo_2, 'coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" and conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
        }
    }
    
    lista_detalhes = []
    for item, valores in comparacoes.items():
        diferenca = valores['rreo2'] - valores['rreo1']
        lista_detalhes.append({"Item": item, "RREO Anexo 2": valores['rreo2'], "RREO Anexo 1": valores['rreo1'], "Diferença": diferenca})
    
    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D3_00002", titulo, grupo, resposta, df_detalhes)

def analisar_D3_00005(df_rreo_3, df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e, periodo_rgf):
    titulo = "Consistência da Receita Corrente Líquida (RCL)"
    grupo = "Dimensão III - Informações Fiscais"
    if any(df is None or df.empty for df in [df_rreo_3, df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e]): return None

    # Determina dinamicamente o texto da coluna com base no período
    if periodo_rgf == "2":
        texto_coluna_periodo = f"Até o {periodo_rgf}º Semestre"
    else:
        texto_coluna_periodo = f"Até o {periodo_rgf}º Quadrimestre"

    valores = [
        ("RGF Anexo 1", df_rgf_1e.query('cod_conta == "ReceitaCorrenteLiquidaLimiteLegal"')['valor'].sum()),
        ("RGF Anexo 2", df_rgf_2e.query(f'cod_conta == "RGF2ReceitaCorrenteLiquida" and coluna == "{texto_coluna_periodo}"')['valor'].sum()),
        ("RGF Anexo 3", df_rgf_3e.query(f'cod_conta == "RGF3ReceitaCorrenteLiquida" and coluna == "{texto_coluna_periodo}"')['valor'].sum()),
        ("RGF Anexo 4", df_rgf_4e.query('cod_conta == "RGF4ReceitaCorrenteLiquida"')['valor'].sum()),
        ("RREO Anexo 3", df_rreo_3.query('cod_conta == "RREO3ReceitaCorrenteLiquida" and coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()),
    ]
    
    df_detalhes = pd.DataFrame(valores, columns=['Fonte', 'Valor'])
    df_detalhes['Diferença'] = df_detalhes['Valor'].diff().fillna(0)
    
    diferenca = df_detalhes['Diferença'].abs().max()
    resposta = determinar_resposta(diferenca)

    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    df_detalhes['Diferença'] = df_detalhes['Diferença'].apply(formatar_reais)

    return _criar_dicionario_resultado("D3_00005", titulo, grupo, resposta, df_detalhes)


def analisar_D3_00006(df_rreo_6, df_rgf_2e, periodo_rgf, ano):
    titulo = "Consistência da Dívida Consolidada Líquida (DCL)"
    grupo = "Dimensão III - Informações Fiscais"
    if df_rreo_6 is None or df_rgf_2e is None or df_rreo_6.empty or df_rgf_2e.empty: return None

    if periodo_rgf == "2":
        texto_coluna_periodo = f"Até o {periodo_rgf}º Semestre"
    else:
        texto_coluna_periodo = f"Até o {periodo_rgf}º Quadrimestre"

    valor_rgf2 = df_rgf_2e.query(f'cod_conta == "DividaConsolidadaLiquida" and coluna == "{texto_coluna_periodo}"')['valor'].sum()
    valor_rreo6 = df_rreo_6.query(f'cod_conta == "DividaConsolidadaLiquida" and coluna == "Até o Bimestre {ano} (b)"')['valor'].sum()
    
    diferenca = valor_rgf2 - valor_rreo6
    df_detalhes = pd.DataFrame([
        {"Fonte": "RGF Anexo 2", "Valor": valor_rgf2},
        {"Fonte": "RREO Anexo 6", "Valor": valor_rreo6},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D3_00006", titulo, grupo, determinar_resposta(diferenca), df_detalhes)


def analisar_D3_00008(df_rreo_1, df_rgf_5e, df_rgf_5l):
    # Passo 1: Metadados e Guarda de Segurança
    titulo = "Consistência de Restos a Pagar Não Processados Inscritos"
    grupo = "Dimensão III - Informações Fiscais"
    
    if df_rreo_1 is None or df_rgf_5e is None: return None
    
    # Passo 2: Extração de Dados do RREO Anexo 1
    valor_rreo1 = df_rreo_1.query(
        'coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" and cod_conta == "TotalDespesas"'
    )['valor'].sum()
    
    # Passo 3: Extração de Dados do RGF Anexo 5 (Poder Executivo)
    valor_rgf5e = df_rgf_5e.query(
        'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" and conta == "TOTAL (IV) = (I + II + III)"'
    )['valor'].sum()
    
    # Passo 4: Extração de Dados do RGF Anexo 5 (Poder Legislativo - Opcional e Seguro)
    valor_rgf5l = 0
    if df_rgf_5l is not None and not df_rgf_5l.empty:
        valor_rgf5l = df_rgf_5l.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" and conta == "TOTAL (III) = (I + II)"'
        )['valor'].sum()
    
    # Passo 5: Cálculo e Consolidação
    valor_rgf_total = valor_rgf5e + valor_rgf5l
    diferenca = valor_rgf_total - valor_rreo1
    
    # Passo 6: Montagem do Resultado Detalhado
    df_detalhes = pd.DataFrame([
        {"Fonte": "RGF Anexo 5 (Executivo + Legislativo)", "Valor": valor_rgf_total},
        {"Fonte": "RREO Anexo 1", "Valor": valor_rreo1},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    # Passo 7: Retorno Padronizado
    return _criar_dicionario_resultado("D3_00008", titulo, grupo, determinar_resposta(diferenca), df_detalhes)


def analisar_D3_00009(df_rreo_7, df_rgf_5e, df_rgf_5l):
    titulo = "Consistência de Restos a Pagar (a Pagar)"
    grupo = "Dimensão III - Informações Fiscais"
    if df_rreo_7 is None or df_rgf_5e is None: return None

    # RREO
    valor_rpnp_rreo = df_rreo_7.query('cod_conta == "RestosAPagarNaoProcessadosAPagar" and conta == "TOTAL (III) = (I + II)"')['valor'].sum()
    valor_rpp_rreo = df_rreo_7.query('cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosAPagar" and conta == "TOTAL (III) = (I + II)"')['valor'].sum()
    valor_rreo_total = valor_rpnp_rreo + valor_rpp_rreo
    
    # RGF
    rpnp_rgf5e = df_rgf_5e.query('cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" and conta == "TOTAL (IV) = (I + II + III)"')['valor'].sum()
    rpp_rgf5e = df_rgf_5e.query('cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" and conta == "TOTAL (IV) = (I + II + III)"')['valor'].sum()
    
    rpnp_rgf5l, rpp_rgf5l = 0, 0
    if df_rgf_5l is not None and not df_rgf_5l.empty:
        rpnp_rgf5l = df_rgf_5l.query('cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" and conta == "TOTAL (III) = (I + II)"')['valor'].sum()
        rpp_rgf5l = df_rgf_5l.query('cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" and conta == "TOTAL (III) = (I + II)"')['valor'].sum()

    valor_rgf_total = rpnp_rgf5e + rpp_rgf5e + rpnp_rgf5l + rpp_rgf5l
    diferenca = valor_rgf_total - valor_rreo_total
    
    df_detalhes = pd.DataFrame([
        {"Fonte": "RGF Anexo 5 (Executivo + Legislativo)", "Valor": valor_rgf_total},
        {"Fonte": "RREO Anexo 7", "Valor": valor_rreo_total},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D3_00009", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

##############################################################################################
# --- Funções de Análise da Dimensão D4 ---
##############################################################################################

def analisar_D4_00001(df_rreo_1, df_dca_c):
    """Verifica a igualdade da receita realizada entre o Anexo I-C da DCA e o Anexo 01 do RREO."""
    titulo = "Igualdade da receita realizada (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_1 is None or df_dca_c is None or df_rreo_1.empty or df_dca_c.empty: return None

    valor_rreo = df_rreo_1.query("coluna == 'Até o Bimestre (c)' and cod_conta == 'TotalReceitas'")['valor'].sum()
    valor_dca = df_dca_c.query("cod_conta == 'TotalReceitas'")['valor'].sum()
    diferenca = valor_rreo - valor_dca
    
    df_detalhes = pd.DataFrame([
        {"Fonte": "RREO Anexo 01", "Valor": valor_rreo},
        {"Fonte": "DCA Anexo I-C", "Valor": valor_dca},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00001", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00002(df_rreo_1, df_dca_d):
    """Verifica a igualdade da execução da despesa (empenhada, liquidada, paga, RPNP) entre o Anexo I-D da DCA e o Anexo 01 do RREO."""
    titulo = "Igualdade da execução da despesa (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_1 is None or df_dca_d is None or df_rreo_1.empty or df_dca_d.empty: return None

    mapeamento = {
        "Empenhado": ("DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)", "Despesas Empenhadas"),
        "Liquidado": ("DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)", "Despesas Liquidadas"),
        "Pago": ("DESPESAS PAGAS ATÉ O BIMESTRE (j)", "Despesas Pagas"),
        "Inscrição RPNP": ("INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)", "Inscrição de Restos a Pagar Não Processados")
    }
    
    lista_detalhes = []
    for estagio, (col_rreo, col_dca) in mapeamento.items():
        valor_rreo = df_rreo_1.query(f"coluna == '{col_rreo}' and cod_conta == 'TotalDespesas'")['valor'].sum()
        valor_dca = df_dca_d.query(f"coluna == '{col_dca}' and cod_conta == 'TotalDespesas'")['valor'].sum()
        lista_detalhes.append({
            "Estágio da Despesa": estagio,
            "RREO Anexo 01": valor_rreo,
            "DCA Anexo I-D": valor_dca,
            "Diferença": valor_rreo - valor_dca
        })
        
    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D4_00002", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00003(df_rreo_2, df_dca_e):
    """Verifica a igualdade da despesa por função (exceto intraorçamentária) entre o Anexo I-E da DCA e o Anexo 02 do RREO."""
    titulo = "Igualdade da despesa por função (exceto intra) (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_2 is None or df_dca_e is None or df_rreo_2.empty or df_dca_e.empty: return None

    mapeamento = {
        "Empenhado": ("DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)", "Despesas Empenhadas"),
        "Liquidado": ("DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)", "Despesas Liquidadas"),
        "Inscrição RPNP": ("INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)", "Inscrição de Restos a Pagar Não Processados")
    }

    lista_detalhes = []
    for estagio, (col_rreo, col_dca) in mapeamento.items():
        valor_rreo = df_rreo_2.query(f"coluna == '{col_rreo}' and conta == 'DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)'")['valor'].sum()
        valor_dca = df_dca_e.query(f"coluna == '{col_dca}' and conta == 'Despesas Exceto Intraorçamentárias'")['valor'].sum()
        lista_detalhes.append({
            "Estágio da Despesa": estagio,
            "RREO Anexo 02": valor_rreo,
            "DCA Anexo I-E": valor_dca,
            "Diferença": valor_rreo - valor_dca
        })

    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)

    return _criar_dicionario_resultado("D4_00003", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00004(df_rreo_2, df_dca_e):
    """Verifica a igualdade da despesa por função (intraorçamentária) entre o Anexo I-E da DCA e o Anexo 02 do RREO."""
    titulo = "Igualdade da despesa por função (intraorçamentária) (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_2 is None or df_dca_e is None or df_rreo_2.empty or df_dca_e.empty: return None

    mapeamento = {
        "Empenhado": ("DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)", "Despesas Empenhadas"),
        "Liquidado": ("DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)", "Despesas Liquidadas"),
        "Inscrição RPNP": ("INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)", "Inscrição de Restos a Pagar Não Processados")
    }

    lista_detalhes = []
    for estagio, (col_rreo, col_dca) in mapeamento.items():
        valor_rreo = df_rreo_2.query(f"coluna == '{col_rreo}' and conta == 'DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)' and cod_conta == 'RREO2TotalDespesas'")['valor'].sum()
        valor_dca = df_dca_e.query(f"coluna == '{col_dca}' and conta == 'Despesas Intraorçamentárias'")['valor'].sum()
        lista_detalhes.append({
            "Estágio da Despesa": estagio,
            "RREO Anexo 02": valor_rreo,
            "DCA Anexo I-E": valor_dca,
            "Diferença": valor_rreo - valor_dca
        })

    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)

    return _criar_dicionario_resultado("D4_00004", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00005(df_rreo_7, df_dca_f):
    """Verifica a igualdade dos Restos a Pagar (processados e não processados) entre o Anexo I-F da DCA e o Anexo 07 do RREO."""
    titulo = "Igualdade dos Restos a Pagar (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_7 is None or df_dca_f is None or df_rreo_7.empty or df_dca_f.empty: return None

    mapeamento = {
        "RPP Inscritos em Exerc. Anteriores": ("RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExerciciosAnteriores", "Restos a Pagar Processados Inscritos em Exercícios Anteriores"),
        "RPP Inscritos em 31/Dez Exerc. Anterior": ("RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExercicioAnterior", "Restos a Pagar Processados Inscritos em 31 de Dezembro do Exercício Anterior"),
        "RPP Pagos": ("RestosAPagarProcessadosENaoProcessadosLiquidadosPagos", "Restos a Pagar Processados Pagos"),
        "RPP Cancelados": ("RestosAPagarProcessadosENaoProcessadosLiquidadosCancelados", "Restos a Pagar Processados Cancelados"),
        "RPNP Inscritos em Exerc. Anteriores": ("RestosAPagarNaoProcessadosInscritosEmExerciciosAnteriores", "Restos a Pagar Não Processados Inscritos em Exercícios Anteriores"),
        "RPNP Inscritos em 31/Dez Exerc. Anterior": ("RestosAPagarNaoProcessadosInscritosEmExercicioAnterior", "Restos a Pagar Não Processados Inscritos em 31 de Dezembro do Exercício Anterior"),
        "RPNP Liquidados": ("RestosAPagarNaoProcessadosLiquidados", "Restos a Pagar Não Processados Liquidados"),
        "RPNP Pagos": ("RestosAPagarNaoProcessadosPagos", "Restos a Pagar Não Processados Pagos"),
        "RPNP Cancelados": ("RestosAPagarNaoProcessadosCancelados", "Restos a Pagar Não Processados Cancelados")
    }
    
    lista_detalhes = []
    for item, (cod_rreo, col_dca) in mapeamento.items():
        valor_rreo = df_rreo_7.query(f"cod_conta == '{cod_rreo}' and conta == 'TOTAL (III) = (I + II)'")['valor'].sum()
        valor_dca = df_dca_f.query(f"coluna == '{col_dca}' and conta == 'Total Despesas'")['valor'].sum()
        lista_detalhes.append({
            "Item de Restos a Pagar": item,
            "RREO Anexo 07": valor_rreo,
            "DCA Anexo I-F": valor_dca,
            "Diferença": valor_rreo - valor_dca
        })

    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D4_00005", titulo, grupo, resposta, df_detalhes)


def analisar_D4_00006(df_rreo_7, df_dca_g):
    """Verifica a igualdade dos Restos a Pagar Não Processados entre o Anexo I-G da DCA e o Anexo 07 do RREO."""
    titulo = "Igualdade dos Restos a Pagar Não Processados (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_7 is None or df_dca_g is None or df_rreo_7.empty or df_dca_g.empty: return None

    mapeamento = {
        "RPNP Inscritos em Exerc. Anteriores": ("RestosAPagarNaoProcessadosInscritosEmExerciciosAnteriores", "Restos a Pagar Não Processados Inscritos em Exercícios Anteriores"),
        "RPNP Inscritos em 31/Dez Exerc. Anterior": ("RestosAPagarNaoProcessadosInscritosEmExercicioAnterior", "Restos a Pagar Não Processados Inscritos em 31 de Dezembro do Exercício Anterior"),
        "RPNP Pagos": ("RestosAPagarNaoProcessadosPagos", "Restos a Pagar Não Processados Pagos"),
        "RPNP Cancelados": ("RestosAPagarNaoProcessadosCancelados", "Restos a Pagar Não Processados Cancelados")
    }

    lista_detalhes = []
    for item, (cod_rreo, col_dca) in mapeamento.items():
        valor_rreo = df_rreo_7.query(f"cod_conta == '{cod_rreo}' and conta == 'TOTAL (III) = (I + II)'")['valor'].sum()
        valor_dca = df_dca_g.query(f"coluna == '{col_dca}' and (conta == 'Despesas Exceto Intraorçamentárias' or conta == 'Despesas Intraorçamentárias')")['valor'].sum()
        lista_detalhes.append({
            "Item de RPNP": item,
            "RREO Anexo 07": valor_rreo,
            "DCA Anexo I-G": valor_dca,
            "Diferença": valor_rreo - valor_dca
        })
    
    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)

    return _criar_dicionario_resultado("D4_00006", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00007(df_rreo_7, df_dca_g):
    """Verifica a igualdade dos Restos a Pagar Processados entre o Anexo I-G da DCA e o Anexo 07 do RREO."""
    titulo = "Igualdade dos Restos a Pagar Processados (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_7 is None or df_dca_g is None or df_rreo_7.empty or df_dca_g.empty: return None

    mapeamento = {
        "RPP Inscritos em Exerc. Anteriores": ("RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExerciciosAnteriores", "Restos a Pagar Processados Inscritos em Exercícios Anteriores"),
        "RPP Inscritos em 31/Dez Exerc. Anterior": ("RestosAPagarProcessadosENaoProcessadosLiquidadosInscritosEmExercicioAnterior", "Restos a Pagar Processados Inscritos em 31 de Dezembro do Exercício Anterior"),
        "RPP Pagos": ("RestosAPagarProcessadosENaoProcessadosLiquidadosPagos", "Restos a Pagar Processados Pagos"),
        "RPP Cancelados": ("RestosAPagarProcessadosENaoProcessadosLiquidadosCancelados", "Restos a Pagar Processados Cancelados")
    }

    lista_detalhes = []
    for item, (cod_rreo, col_dca) in mapeamento.items():
        valor_rreo = df_rreo_7.query(f"cod_conta == '{cod_rreo}' and conta == 'TOTAL (III) = (I + II)'")['valor'].sum()
        valor_dca = df_dca_g.query(f"coluna == '{col_dca}' and (conta == 'Despesas Exceto Intraorçamentárias' or conta == 'Despesas Intraorçamentárias')")['valor'].sum()
        lista_detalhes.append({
            "Item de RPP": item,
            "RREO Anexo 07": valor_rreo,
            "DCA Anexo I-G": valor_dca,
            "Diferença": valor_rreo - valor_dca
        })

    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)

    return _criar_dicionario_resultado("D4_00007", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00010(df_rreo_3, df_dca_c):
    """Verifica a igualdade das receitas com tributos municipais entre o Anexo I-C da DCA e o Anexo 03 do RREO."""
    titulo = "Igualdade das receitas com tributos (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_3 is None or df_dca_c is None or df_rreo_3.empty or df_dca_c.empty: return None

    contas_rreo = ["IPTU", "ISS", "ITBI", "IRRF"]
    valor_rreo = df_rreo_3[df_rreo_3["conta"].str.contains('|'.join(contas_rreo), na=False)].query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()
    valor_dca = df_dca_c.query("(cod_conta == 'RO1.1.1.0.00.0.0' and coluna == 'Receitas Brutas Realizadas') or (cod_conta == 'RO1.1.1.0.00.0.0' and coluna == 'Outras Deduções da Receita')")['valor'].sum()

    diferenca = valor_rreo - valor_dca
    
    df_detalhes = pd.DataFrame([
        {"Fonte": "RREO Anexo 03", "Valor": valor_rreo},
        {"Fonte": "DCA Anexo I-C", "Valor": valor_dca},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00010", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00012(df_rreo_3, df_dca_c):
    """Verifica a igualdade das receitas com transferências constitucionais entre o Anexo I-C da DCA e o Anexo 03 do RREO."""
    titulo = "Igualdade das transferências constitucionais (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_3 is None or df_dca_c is None or df_rreo_3.empty or df_dca_c.empty: return None

    contas_rreo = ["Cota-Parte do FPM", "Cota-Parte do ICMS", "Cota-Parte do IPVA", "Cota-Parte do ITR", "Transferências do FUNDEB"]
    valor_rreo = df_rreo_3[df_rreo_3["conta"].str.contains('|'.join(contas_rreo), na=False)].query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()

    codigos_dca = ["RO1.7.1.1.51.0.0", "RO1.7.2.1.50.0.0", "RO1.7.2.1.51.0.0", "RO1.7.1.1.52.0.0", "RO1.7.5.1.00.0.0", "RO1.7.1.5.00.0.0"]
    valor_dca = df_dca_c.query("cod_conta in @codigos_dca and (coluna == 'Receitas Brutas Realizadas' or coluna == 'Outras Deduções da Receita')")['valor'].sum()

    diferenca = valor_rreo - valor_dca

    df_detalhes = pd.DataFrame([
        {"Fonte": "RREO Anexo 03", "Valor": valor_rreo},
        {"Fonte": "DCA Anexo I-C", "Valor": valor_dca},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)

    return _criar_dicionario_resultado("D4_00012", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00017(df_rreo_3, df_dca_c):
    """Verifica a igualdade das contribuições de servidores e compensações financeiras entre o Anexo I-C da DCA e o Anexo 03 do RREO."""
    titulo = "Igualdade das contribuições e compensações (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_3 is None or df_dca_c is None or df_rreo_3.empty or df_dca_c.empty: return None

    # Contribuições dos Servidores
    valor_contrib_rreo = df_rreo_3.query('cod_conta == "ContribuicaoDoServidorParaOPlanoDePrevidencia" and coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()
    valor_contrib_dca = df_dca_c.query('cod_conta == "RO1.2.1.5.00.0.0"')["valor"].sum()

    # Compensações Financeiras
    valor_comp_rreo = df_rreo_3.query('cod_conta == "CompensacaoFinanceiraEntreRegimesPrevidencia" and coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()
    valor_comp_dca = df_dca_c.query('cod_conta == "RO1.9.9.9.03.0.0"')["valor"].sum()
    
    lista_detalhes = [
        {
            "Item": "Contribuições dos Servidores", 
            "RREO Anexo 03": valor_contrib_rreo, 
            "DCA Anexo I-C": valor_contrib_dca, 
            "Diferença": valor_contrib_rreo - valor_contrib_dca
        },
        {
            "Item": "Compensações Financeiras", 
            "RREO Anexo 03": valor_comp_rreo, 
            "DCA Anexo I-C": valor_comp_dca, 
            "Diferença": valor_comp_rreo - valor_comp_dca
        }
    ]
    
    df_detalhes = pd.DataFrame(lista_detalhes)
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())

    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)

    return _criar_dicionario_resultado("D4_00017", titulo, grupo, resposta, df_detalhes)


def analisar_D4_00019(df_rreo_9, df_dca_d):
    """Igualdade do valor das despesas de capital (DCA-D vs RREO-09)"""
    titulo = "Igualdade do valor das despesas de capital (DCA vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_rreo_9 is None or df_dca_d is None or df_rreo_9.empty or df_dca_d.empty: return None

    valor_rreo = df_rreo_9.query('coluna == "DESPESAS EMPENHADAS (e)" and cod_conta == "RREO9DespesasDeCapital"')['valor'].sum()
    valor_dca = df_dca_d.query('coluna == "Despesas Empenhadas" and cod_conta == "DO4.0.00.00.00.00"')['valor'].sum()
    diferenca = valor_rreo - valor_dca
    
    df_detalhes = pd.DataFrame([
        {"Fonte": "RREO Anexo 09", "Valor": valor_rreo},
        {"Fonte": "DCA Anexo D", "Valor": valor_dca},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00019", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00020(df_msc_dez, df_rreo_1):
    """Igualdade nas receitas arrecadadas (MSC Dezembro vs RREO-01)"""
    titulo = "Igualdade nas receitas arrecadadas (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_1 is None or df_msc_dez.empty or df_rreo_1.empty: return None
    
    #contas_msc = ["621200000", "621310100", "621310200", "621320000", "621390000"]
    valor_msc = df_msc_dez.query('tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" or conta_contabil == "621310200" \
                                    or conta_contabil == "621320000" or conta_contabil == "621390000")')['valor'].sum()
    valor_rreo = df_rreo_1.query('coluna == "Até o Bimestre (c)" and cod_conta == "TotalReceitas"')['valor'].sum()
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 01", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00020", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00022(df_msc_dez, df_rreo_3):
    """Igualdade nas receitas com tributos municipais (MSC Dezembro vs RREO-03)"""
    titulo = "Igualdade nas receitas com tributos municipais (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_3 is None or df_msc_dez.empty or df_rreo_3.empty: return None

    codigos_msc = ["111201", "111250", "111253", "111303", "111451", "1119"]
    rec_msc = df_msc_dez.query('tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" or conta_contabil == "621310200" \
                                    or conta_contabil == "621320000" or conta_contabil == "621390000")').copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = ["IPTU", "ISS", "ITBI", "IRRF"]
    valor_rreo = df_rreo_3[df_rreo_3["conta"].str.contains('|'.join(contas_rreo), na=False)].query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()
    
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 03", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00022", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00024(df_msc_dez, df_rreo_3):
    """Igualdade nas receitas com transferências constitucionais (MSC Dezembro vs RREO-03)"""
    titulo = "Igualdade nas transferências constitucionais (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_3 is None or df_msc_dez.empty or df_rreo_3.empty: return None

    codigos_msc = ["171151", "172150", "172151", "171152", "17515", "17155"]
    rec_msc = df_msc_dez.query('tipo_valor == "ending_balance"').copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)].query('conta_contabil == "621200000" or conta_contabil == "621310200" or conta_contabil == "621390000"')['valor'].sum()

    contas_rreo = ["Cota-Parte do FPM", "Cota-Parte do ICMS", "Cota-Parte do IPVA", "Cota-Parte do ITR", "Transferências do FUNDEB"]
    valor_rreo = df_rreo_3[df_rreo_3["conta"].str.contains('|'.join(contas_rreo), na=False)].query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')['valor'].sum()

    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 03", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00024", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00025(df_msc_dez, df_rreo_1):
    """Igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas (MSC Dezembro vs RREO-01)"""
    titulo = "Igualdade das Despesas Orçamentárias (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_1 is None or df_msc_dez.empty or df_rreo_1.empty: return None

    # Valores MSC
    valor_emp_msc = df_msc_dez.query("tipo_valor == 'ending_balance' and conta_contabil in ['622130500','622130600','622130700','622130400']")['valor'].sum()
    valor_liq_msc = df_msc_dez.query("tipo_valor == 'ending_balance' and conta_contabil in ['622130700','622130400']")['valor'].sum()
    valor_pago_msc = df_msc_dez.query("tipo_valor == 'ending_balance' and conta_contabil == '622130400'")['valor'].sum()
    
    # Valores RREO
    valor_emp_rreo = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" and cod_conta == "TotalDespesas"')['valor'].sum()
    valor_liq_rreo = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" and cod_conta == "TotalDespesas"')['valor'].sum()
    valor_pago_rreo = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" and cod_conta == "TotalDespesas"')['valor'].sum()

    df_detalhes = pd.DataFrame({
        "Estágio da Despesa": ["Empenhado", "Liquidado", "Pago"],
        "MSC Dezembro": [valor_emp_msc, valor_liq_msc, valor_pago_msc],
        "RREO Anexo 01": [valor_emp_rreo, valor_liq_rreo, valor_pago_rreo]
    })
    df_detalhes["Diferença"] = df_detalhes["MSC Dezembro"] - df_detalhes["RREO Anexo 01"]
    
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D4_00025", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00026(df_msc_dez, df_rreo_1):
    """Igualdade dos Restos a Pagar não processados (MSC Dezembro vs RREO-01)"""
    titulo = "Igualdade dos Restos a Pagar não processados (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_1 is None or df_msc_dez.empty or df_rreo_1.empty: return None

    valor_msc = df_msc_dez.query("tipo_valor == 'ending_balance' and conta_contabil in ['622130500', '622130600']")['valor'].sum()
    valor_rreo = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" and cod_conta == "TotalDespesas"')['valor'].sum()
    diferenca = valor_msc - valor_rreo
    
    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 01", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00026", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00029(df_emp_msc_dez, df_rreo_2):
    """Avalia se o valor de despesas exceto-intra na função 09 (Prev. Social) é igual (MSC Dezembro vs RREO-02)"""
    titulo = "Despesa por Função: Previdência Social (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_emp_msc_dez is None or df_rreo_2 is None or df_emp_msc_dez.empty or df_rreo_2.empty: return None

    valor_msc = df_emp_msc_dez.query('funcao == "09" and DIGITO_INTRA != "91"')['valor'].sum()
    valor_rreo = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" and conta == "Previdência Social"')['valor'].sum()
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 02", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00029", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00030(df_emp_msc_dez, df_rreo_2):
    """Avalia se o valor de despesas exceto-intra na função 10 (Saúde) é igual (MSC Dezembro vs RREO-02)"""
    titulo = "Despesa por Função: Saúde (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_emp_msc_dez is None or df_rreo_2 is None or df_emp_msc_dez.empty or df_rreo_2.empty: return None

    valor_msc = df_emp_msc_dez.query('funcao == "10" and DIGITO_INTRA != "91"')['valor'].sum()
    valor_rreo = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" and conta == "Saúde" and cod_conta == "RREO2TotalDespesas"')['valor'].sum()
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 02", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00030", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00031(df_emp_msc_dez, df_rreo_2):
    """Avalia se o valor de despesas exceto-intra na função 12 (Educação) é igual (MSC Dezembro vs RREO-02)"""
    titulo = "Despesa por Função: Educação (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_emp_msc_dez is None or df_rreo_2 is None or df_emp_msc_dez.empty or df_rreo_2.empty: return None

    valor_msc = df_emp_msc_dez.query('funcao == "12" and DIGITO_INTRA != "91"')['valor'].sum()
    valor_rreo = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" and conta == "Educação" and cod_conta == "RREO2TotalDespesas"')['valor'].sum()
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 02", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00031", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00032(df_emp_msc_dez, df_rreo_2):
    """Avalia se o valor de despesas exceto-intra nas demais funções é igual (MSC Dezembro vs RREO-02)"""
    titulo = "Despesa por Função: Demais Funções (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_emp_msc_dez is None or df_rreo_2 is None or df_emp_msc_dez.empty or df_rreo_2.empty: return None

    valor_msc = df_emp_msc_dez.query('(funcao != "09" and funcao != "10" and funcao != "12") and DIGITO_INTRA != "91"')['valor'].sum()
    
    contas_demais_funcoes = [
        "Legislativa", "Judiciária", "Essencial à Justiça", "Administração", "Segurança Pública",
        "Assistência Social", "Trabalho", "Cultura", "Direitos da Cidadania", "Urbanismo",
        "Habitação", "Saneamento", "Gestão Ambiental", "Ciência e Tecnologia", "Agricultura",
        "Organização Agrária", "Indústria", "Comércio e Serviços", "Comunicações", "Energia", "Transporte",
        "Desporto e Lazer", "Encargos Especiais"
    ]
    valor_rreo = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" and conta in @contas_demais_funcoes and cod_conta == "RREO2TotalDespesas"')['valor'].sum()

    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 02", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00032", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00033(df_emp_msc_dez, df_rreo_2):
    """Avalia se o valor de despesas intraorçamentárias é igual (MSC Dezembro vs RREO-02)"""
    titulo = "Despesa por Função: Intraorçamentárias (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_emp_msc_dez is None or df_rreo_2 is None or df_emp_msc_dez.empty or df_rreo_2.empty: return None

    valor_msc = df_emp_msc_dez.query('DIGITO_INTRA == "91"')['valor'].sum()
    valor_rreo = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" and conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)" and cod_conta == "RREO2TotalDespesas"')['valor'].sum()
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 02", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00033", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00034(df_msc_dez, df_rreo_7):
    """Avalia a igualdade entre os saldos finais de RPP pagos e RPNP pagos (MSC Dezembro vs RREO-07)"""
    titulo = "Pagamento de Restos a Pagar (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_7 is None or df_msc_dez.empty or df_rreo_7.empty: return None

    # Valores MSC
    valor_rpnp_pago_msc = df_msc_dez.query('tipo_valor == "ending_balance" and conta_contabil == "631400000"')['valor'].sum()
    valor_rpp_pago_msc = df_msc_dez.query('tipo_valor == "ending_balance" and conta_contabil == "632200000"')['valor'].sum()
    
    # Valores RREO
    valor_rpnp_pago_rreo = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" and cod_conta == "RestosAPagarNaoProcessadosPagos"')['valor'].sum()
    valor_rpp_pago_rreo = df_rreo_7.query('conta == "TOTAL (III) = (I + II)" and cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosPagos"')['valor'].sum()

    df_detalhes = pd.DataFrame({
        "Tipo de RP Pago": ["Não Processados (RPNP)", "Processados (RPP)"],
        "MSC Dezembro": [valor_rpnp_pago_msc, valor_rpp_pago_msc],
        "RREO Anexo 07": [valor_rpnp_pago_rreo, valor_rpp_pago_rreo]
    })
    df_detalhes["Diferença"] = df_detalhes["MSC Dezembro"] - df_detalhes["RREO Anexo 07"]
    
    resposta = determinar_resposta(df_detalhes['Diferença'].abs().max())
    
    for coluna in df_detalhes.columns[1:]:
        df_detalhes[coluna] = df_detalhes[coluna].apply(formatar_reais)
        
    return _criar_dicionario_resultado("D4_00034", titulo, grupo, resposta, df_detalhes)

def analisar_D4_00038(df_msc_dez, df_rreo_6):
    """Igualdade das receitas com tributos (MSC Dezembro vs RREO-06)"""
    titulo = "Igualdade das receitas com tributos (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_6 is None or df_msc_dez.empty or df_rreo_6.empty: return None

    codigos_msc = ["111250", "111253", "111303", "111451"]
    rec_msc = df_msc_dez.query('tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100"\
                    or conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")').copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = ["IPTU", "ISS", "ITBI", "IRRF"]
    valor_rreo = df_rreo_6[df_rreo_6["conta"].str.contains('|'.join(contas_rreo), na=False)].query('coluna == "RECEITAS REALIZADAS (a)"')['valor'].sum()
    
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 06", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00038", titulo, grupo, determinar_resposta(diferenca), df_detalhes)

def analisar_D4_00040(df_msc_dez, df_rreo_6):
    """Igualdade nas transferências constitucionais (MSC Dezembro vs RREO-06)"""
    titulo = "Igualdade nas transferências constitucionais (MSC vs RREO)"
    grupo = "Dimensão IV - Informações Contábeis x Fiscais"
    if df_msc_dez is None or df_rreo_6 is None or df_msc_dez.empty or df_rreo_6.empty: return None

    codigos_msc = ["171151", "172150", "172151", "171152", "17515", "17155"]
    rec_msc = df_msc_dez.query('tipo_valor == "ending_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100"\
                    or conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")').copy()
    rec_msc['natureza_receita'] = rec_msc['natureza_receita'].astype(str)
    valor_msc = rec_msc[rec_msc['natureza_receita'].str.contains('|'.join(codigos_msc), na=False)]['valor'].sum()

    contas_rreo = ["Cota-Parte do FPM", "Cota-Parte do ICMS", "Cota-Parte do IPVA", "Cota-Parte do ITR", "Transferências do FUNDEB"]
    valor_rreo = df_rreo_6[df_rreo_6["conta"].str.contains('|'.join(contas_rreo), na=False)].query('coluna == "RECEITAS REALIZADAS (a)"')['valor'].sum()
    
    diferenca = valor_msc - valor_rreo

    df_detalhes = pd.DataFrame([
        {"Fonte": "MSC Dezembro", "Valor": valor_msc},
        {"Fonte": "RREO Anexo 06", "Valor": valor_rreo},
        {"Fonte": "Diferença", "Valor": diferenca}
    ])
    df_detalhes['Valor'] = df_detalhes['Valor'].apply(formatar_reais)
    
    return _criar_dicionario_resultado("D4_00040", titulo, grupo, determinar_resposta(diferenca), df_detalhes)


#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


#################################################################################################

def estilizar_tabela_resumo(df: pd.DataFrame):
    def destacar_erros(linha):
        cor = ''
        if '❌' in linha['Resposta']: cor = 'background-color: #A85151; color: white;'
        elif '⚠️' in linha['Resposta']: cor = 'background-color: #C2A261; color: white;'
        elif '✅' in linha['Resposta']: cor = 'background-color: #2F8F5B; color: white;'
        elif '❓' in linha['Resposta']: cor = 'background-color: #52616B; color: white;'
        return [cor] * len(linha)
    return df.style.apply(destacar_erros, axis=1)


def obter_status_visual(resposta: str):
    resposta = str(resposta)
    if "❌" in resposta:
        return {
            "classe": "erro",
            "icone": "❌",
            "rotulo": "ERRO",
            "descricao": "Divergência encontrada",
        }
    if "⚠️" in resposta:
        return {
            "classe": "alerta",
            "icone": "⚠️",
            "rotulo": "OK com Dif. Centavos",
            "descricao": "Diferença dentro da tolerância",
        }
    if "✅" in resposta:
        return {
            "classe": "ok",
            "icone": "✅",
            "rotulo": "OK",
            "descricao": "Verificação sem divergência",
        }
    return {
        "classe": "neutro",
        "icone": "❓",
        "rotulo": "Dados Insuficientes",
        "descricao": "Não foi possível concluir a verificação",
    }


def renderizar_chamada_expander(resultado: Dict[str, Any]):
    resposta = resultado["df_resumo"]["Resposta"].iloc[0]
    status = obter_status_visual(resposta)
    id_dimensao = html.escape(str(resultado["id"]))
    titulo = html.escape(str(resultado["titulo"]))
    st.markdown(
        f"""
        <div class="status-expander status-expander--{status['classe']}">
            <div class="status-expander__texto">
                <strong>{status['icone']} {status['rotulo']}</strong>
                <span>{id_dimensao}: {titulo}</span>
            </div>
            <small>{status['descricao']}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def aplicar_estilo_status_expander():
    st.markdown(
        """
        <style>
            .status-expander {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin: 10px 0 4px 0;
                padding: 10px 14px;
                border-radius: 8px;
                border-left: 7px solid;
                color: #FFFFFF;
                font-size: 0.95rem;
            }
            .status-expander__texto {
                display: flex;
                align-items: center;
                gap: 12px;
                min-width: 0;
            }
            .status-expander__texto span {
                overflow-wrap: anywhere;
            }
            .status-expander small {
                font-weight: 700;
                opacity: 0.92;
                white-space: nowrap;
            }
            .status-expander--ok {
                background: rgba(47, 143, 91, 0.85);
                border-left-color: #62D89A;
            }
            .status-expander--erro {
                background: rgba(168, 81, 81, 0.9);
                border-left-color: #FF6B6B;
            }
            .status-expander--alerta {
                background: rgba(194, 162, 97, 0.9);
                border-left-color: #FFD166;
            }
            .status-expander--neutro {
                background: rgba(82, 97, 107, 0.9);
                border-left-color: #AAB7C4;
            }
            @media (max-width: 700px) {
                .status-expander {
                    align-items: flex-start;
                    flex-direction: column;
                }
                .status-expander__texto {
                    align-items: flex-start;
                    flex-direction: column;
                    gap: 4px;
                }
                .status-expander small {
                    white-space: normal;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


###################################################################################################
###################################################################################################
###################################################################################################
# --- 4. Interface do Usuário e Fluxo Principal ---
###################################################################################################
###################################################################################################
###################################################################################################

def main():
    # configurar_pagina() - Comentado pois já foi configurado no app principal
    st.title("Ferramenta de Análise da Consistência no Cruzamento dos Dados - SICONFI")
    # st.markdown("""
    # Esta ferramenta, a partir dos dados extraídos da API do SICONFI, automatiza a análise de consistência no cruzamento de informações 
    # entre os demonstrativos contábeis e fiscais (DCA, RREO e MSC) enviados pelos municípios ao sistema. Seu propósito é apoiar gestores 
    # e contadores públicos dos municípios fluminenses na identificação e correção de divergências de informações entre os demonstrativos que
    # possam comprometer a nota no Ranking da Qualidade da Informação Contábil e Fiscal da STN.
    # """)

    # Seção de Objetivo, usando markdown para negrito e o emoji
    st.markdown(
        """
        **🎯 Nosso principal objetivo é simples:** Ajudá-lo a identificar e corrigir 
        divergências que possam comprometer sua nota no **Ranking da Qualidade da 
        Informação Contábil e Fiscal da STN**.
        """
    )
    # Subtítulo para a lista de funcionalidades
    st.subheader("O que a ferramenta faz?")
    # Lista de funcionalidades usando markdown para tópicos e negrito
    st.markdown(
        """
        - **Extrai** os dados de final de ano dos demonstrativos via API do SICONFI.
        - **Cruza** automaticamente as informações entre **DCA**, **RREO**, **RGF** e **MSC**.
        - **Aponta** de forma clara as inconsistências encontradas para sua análise.
        """
    )


    # --- Inicialização do Estado da Sessão ---
    if 'dados_carregados' not in st.session_state:
        st.session_state.dados_carregados = False
    if 'dataframes_brutos' not in st.session_state:
        st.session_state.dataframes_brutos = {}
    if 'dataframes_tratados' not in st.session_state:
        st.session_state.dataframes_tratados = {}
    if 'extrato_df' not in st.session_state:
        #st.session_state.extrato_df = None
        st.session_state.extrato_df = {}
    if 'show_extrato' not in st.session_state:
        st.session_state.show_extrato = False


    def limpar_estado_dos_dados():
        st.session_state.dados_carregados = False
        st.session_state.dataframes_brutos = {}
        st.session_state.dataframes_tratados = {}
        st.session_state.extrato_df = {}
        st.session_state.show_extrato = False
        buscar_dados_api.clear()
        buscar_dados_msc_paginado.clear()

    ######  SIDEBAR (apenas informações)  ######
    st.sidebar.title("ℹ️ Informações")
    st.sidebar.markdown("> Para informações sobre o [SICONFI](https://siconfi.tesouro.gov.br/siconfi/index.jsf).")
    st.sidebar.markdown("> Para informações sobre o [Ranking SICONFI](https://ranking-municipios.tesouro.gov.br/).")
    st.sidebar.markdown("> Para informações sobre a [API do SICONFI](https://apidatalake.tesouro.gov.br/docs/siconfi/).")
    st.sidebar.divider()
    st.sidebar.markdown("""
                        Desenvolvido por Marcelo Jandussi.
                        📧 **Contato:** mjandussi@gmail.com
                        🌐 **GitHub:** [github.com/mjandussi](https://github.com/mjandussi)
                        """)

    ######  PÁGINA CENTRAL - FILTROS  ######
    st.markdown("### 📋 Selecione o Município e Ano para Análise")

    df_entes = carregar_dados_entes(ARQUIVO_ENTES)
    if df_entes is None: st.stop()

    # Detectar coluna de UF
    uf_col = None
    if 'SG_UF' in df_entes.columns:
        uf_col = 'SG_UF'
    elif 'UF' in df_entes.columns:
        uf_col = 'UF'

    # FILTROS EM COLUNAS NA PÁGINA PRINCIPAL
    col_filtro1, col_filtro2, col_filtro3 = st.columns([1, 2, 1])

    with col_filtro1:
        # Filtro de UF (se disponível)
        if uf_col:
            ufs_disponiveis = sorted(df_entes[uf_col].dropna().unique().tolist())
            uf_selecionada = st.selectbox(
                "🗺️ UF",
                ufs_disponiveis,
                index=ufs_disponiveis.index('RJ') if 'RJ' in ufs_disponiveis else 0,
                on_change=limpar_estado_dos_dados,
                key="uf_select"
            )
            df_entes_filtrado = df_entes[df_entes[uf_col] == uf_selecionada]
        else:
            df_entes_filtrado = df_entes
            uf_selecionada = None

    dicionario_entes = pd.Series(df_entes_filtrado['NOME_ENTE'].values, index=df_entes_filtrado['ID_ENTE']).to_dict()

    with col_filtro2:
        # Campo de busca para facilitar encontrar o município
        busca_municipio = st.text_input(
            "🔍 Buscar Município",
            placeholder="Digite para filtrar...",
            key="busca_municipio"
        )

        # Filtrar municípios pela busca
        if busca_municipio:
            municipios_filtrados = {k: v for k, v in dicionario_entes.items()
                                   if busca_municipio.upper() in v.upper()}
        else:
            municipios_filtrados = dicionario_entes

        if not municipios_filtrados:
            st.warning("Nenhum município encontrado com esse nome.")
            municipios_filtrados = dicionario_entes

        nome_ente_selecionado = st.selectbox(
            "🏛️ Município",
            list(municipios_filtrados.values()),
            on_change=limpar_estado_dos_dados,
            key="select_municipio"
        )

    with col_filtro3:
        ano = st.selectbox(
            "📅 Ano",
            [2022, 2023, 2024],
            index=2,  # 2024 por padrão
            on_change=limpar_estado_dos_dados
        )

    codigo_ente = [k for k, v in dicionario_entes.items() if v == nome_ente_selecionado][0]

    st.divider()

    ######  CABEÇALHO DA ANÁLISE  ######
    st.header(f"📊 Análise: {nome_ente_selecionado} - {uf_selecionada if uf_selecionada else ''} ({ano})")

    url_extrato = f'{URL_BASE_API}/extrato_entregas?id_ente={codigo_ente}&an_referencia={ano}'
    df_extrato_entregas = buscar_dados_api(url_extrato)
    
    tipo_rgf_str, tipo_rreo_str = None, None
    if df_extrato_entregas is not None and not df_extrato_entregas.empty:
        tipo_rgf_str, tipo_rreo_str = obter_tipo_relatorio(df_extrato_entregas)
    else:
        st.warning("Aviso: O extrato de entregas não foi encontrado. A aplicação assumirá o envio de relatórios **'Não Simplificados'**.")
        tipo_rgf_str, tipo_rreo_str = "RGF", "RREO"

    if not tipo_rgf_str: st.stop()

    #st.subheader("Validação Prévia de Entregas")
    tipo_relatorio = "Simplificado" if "Simplificado" in tipo_rgf_str else "Não Simplificado"
    
    # Aqui o Código para caso o Ente não tenho todos os demonstrativos (não irá prosseguir para gerar as análises...)
    if not validar_entregas_obrigatorias(df_extrato_entregas, nome_ente_selecionado, tipo_relatorio):
        st.stop()

    st.session_state.extrato_df = df_extrato_entregas

    st.divider()

    #######################################################################################################################
    # --- Etapa 1: Busca de Dados ---
    # Etapa Inicial de Iniciar a Análise 
    st.subheader("Etapa 1: Buscar e Tratar Dados da API")
    st.markdown("""
    Inicie a Análise de Dados. Clique no botão abaixo para extrair os demonstrativos mais recentes da API do SICONFI e carregar os 
                dados na plataforma.
    """)
    if st.button("Buscar e Preparar Todos os Relatórios", use_container_width=True):
        with st.spinner("Buscando e tratando todos os demonstrativos..."):
            urls_api = construir_urls_api(str(ano), codigo_ente, tipo_rgf_str, tipo_rreo_str)
            dataframes_temporarios = {}
            for chave, url in urls_api.items():
                dataframes_temporarios[chave] = buscar_dados_api(url)
            
            lista_msc_encerramento = []
            msc_pat = buscar_dados_msc_paginado('patrimonial', codigo_ente, str(ano), list(range(1,5)), 'MSCE')
            if msc_pat is not None and not msc_pat.empty: lista_msc_encerramento.append(msc_pat)
            
            msc_orc = buscar_dados_msc_paginado('orcamentaria', codigo_ente, str(ano), [5, 6], 'MSCE')
            if msc_orc is not None and not msc_orc.empty: lista_msc_encerramento.append(msc_orc)
                
            msc_ctr = buscar_dados_msc_paginado('controle', codigo_ente, str(ano), [7, 8], 'MSCE')
            if msc_ctr is not None and not msc_ctr.empty: lista_msc_encerramento.append(msc_ctr)

            if lista_msc_encerramento:
                dataframes_temporarios['msc_encerramento'] = pd.concat(lista_msc_encerramento, ignore_index=True)
            
            dataframes_temporarios['msc_dezembro'] = buscar_dados_msc_paginado('orcamentaria', codigo_ente, str(ano), [6], 'MSCC')
            
            
            dados_tratados = tratar_dados_brutos(dataframes_temporarios)
            st.session_state.dataframes_tratados = dados_tratados
            st.session_state.dataframes_brutos = dataframes_temporarios
            st.session_state.dados_carregados = True
            st.success("Busca e tratamento de dados concluídos!")

    # --- CARREGAR OS Relatórios ---
    # Todo Este "IF" a seguir abaixo está condicionado ao clicar no primeiro botão (dados_carregados)
    if st.session_state.dados_carregados:
        st.subheader("Verificação e Download dos Relatórios (Valores Tratados)")
        st.markdown("""
        Nesta seção, você pode consultar os demonstrativos obtidos diretamente da API do SICONFI. O sistema exibe uma pré-visualização dos 
                    dados na tela (3 primeiras linhas) e oferece a opção para exportar o relatório completo em formato CSV.
        """)
    
        grupos_relatorios = {
            "RREO": [k for k in st.session_state.dataframes_brutos if k.startswith('rreo')],
            "RGF": [k for k in st.session_state.dataframes_brutos if k.startswith('rgf')],
            "DCA": [k for k in st.session_state.dataframes_brutos if k.startswith('dca')],
            "MSC": [k for k in st.session_state.dataframes_brutos if k.startswith('msc')],
        }

        for nome_grupo, chaves_relatorios in grupos_relatorios.items():
            if chaves_relatorios:
                with st.expander(f"Relatórios do Grupo: {nome_grupo}"):
                    for chave in sorted(chaves_relatorios):
                        df = st.session_state.dataframes_brutos.get(chave)
                        
                        if df is not None:
                            status = "✅ Carregado" if not df.empty else "⚠️ Vazio"
                            st.markdown(f"**Relatório:** `{chave}` | **Status:** {status} | **Linhas:** {len(df)}")
                            
                            if not df.empty:
                                st.dataframe(df.head(3))
                                st.download_button(
                                    label=f"Baixar {chave}.csv",
                                    data=converter_df_para_csv(df),
                                    file_name=f"{nome_ente_selecionado}_{ano}_{chave}.csv",
                                    mime='text/csv',
                                    key=f"download_{chave}"
                                )
                                st.markdown("---")
                        else:
                             st.markdown(f"**Relatório:** `{chave}` | **Status:** ❌ Falha no Carregamento")
    

        st.divider()

        st.subheader("Etapa 2: Executar as Análises de Consistência dos Dados")
        st.markdown("""
        Esta é a seção principal do aplicativo, realizando as análises da consistência no cruzamento dos dados entre os demonstrativos contábeis
                    e fiscais carregados no SICONFI.
        As análises realizam o cruzamento automático entre os relatórios DCA, RREO, RGF e MSCs, apontando as inconsistências que precisam de 
                atenção, permitindo correções ágeis e precisas. Os dados das análises de cada dimensão podem ser visualizados na tabela abaixo, 
                    com a opção de expandir o detalhamento das informações avaliadas.
        """)

        st.markdown(
            """
            1. **Analise a tabela de resultados** abaixo, que realiza as verificações por dimensão.
            2. **Expanda as linhas** para investigar os detalhes de cada inconsistência apontada.
            3. **Utilize essas informações** para orientar as correções necessárias nos demonstrativos.
            """
        )
        if st.button("Iniciar Análise Completa", use_container_width=True, disabled=not st.session_state.dados_carregados):
            
            dataframes_tratados = st.session_state.dataframes_tratados
            dados_preparados = preparar_dataframes_analise(dataframes_tratados)
            periodo_rgf = "2" if "Simplificado" in tipo_rgf_str else "3"
            
            # --- CORREÇÃO: Mapeamento completo e chamada de função corrigida ---
            mapeamento_analises = {
                # --- Dimensão II ---
                "D2_00044": (analisar_D2_00044, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_c')]),
                "D2_00046": (analisar_D2_00046, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_c')]),
                "D2_00048": (analisar_D2_00048, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_c')]),
                "D2_00049": (analisar_D2_00049, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_d')]),
                "D2_00050": (analisar_D2_00050, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_d')]),
                "D2_00058": (analisar_D2_00058, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_hi')]),
                "D2_00069": (analisar_D2_00069, [dados_preparados.get('emp_msc_encerramento_com_intra'), dataframes_tratados.get('dca_e')]),
                "D2_00070": (analisar_D2_00070, [dados_preparados.get('emp_msc_encerramento_com_intra'), dataframes_tratados.get('dca_e')]),
                "D2_00071": (analisar_D2_00071, [dados_preparados.get('emp_msc_encerramento_com_intra'), dataframes_tratados.get('dca_e')]),
                "D2_00072": (analisar_D2_00072, [dados_preparados.get('emp_msc_encerramento_com_intra'), dataframes_tratados.get('dca_e')]),
                "D2_00073": (analisar_D2_00073, [dados_preparados.get('emp_msc_encerramento_com_intra'), dataframes_tratados.get('dca_e')]),
                "D2_00074": (analisar_D2_00074, [dataframes_tratados.get('msc_encerramento'), dataframes_tratados.get('dca_f')]),

                # --- Dimensão III ---
                "D3_00001": (analisar_D3_00001, [dataframes_tratados.get('rreo_01')]),
                "D3_00002": (analisar_D3_00002, [dataframes_tratados.get('rreo_01'), dataframes_tratados.get('rreo_02')]),
                "D3_00005": (analisar_D3_00005, [dataframes_tratados.get('rreo_03'), dataframes_tratados.get('rgf_01_exec'), dataframes_tratados.get('rgf_02_exec'), dataframes_tratados.get('rgf_03_exec'), dataframes_tratados.get('rgf_04_exec'), periodo_rgf]),
                "D3_00006": (analisar_D3_00006, [dataframes_tratados.get('rreo_06'), dataframes_tratados.get('rgf_02_exec'), periodo_rgf, ano]),
                "D3_00008": (analisar_D3_00008, [dataframes_tratados.get('rreo_01'), dataframes_tratados.get('rgf_05_exec'), dataframes_tratados.get('rgf_05_leg')]),
                "D3_00009": (analisar_D3_00009, [dataframes_tratados.get('rreo_07'), dataframes_tratados.get('rgf_05_exec'), dataframes_tratados.get('rgf_05_leg')]),
                
                # --- Dimensão IV ---
                "D4_00001": (analisar_D4_00001, [dataframes_tratados.get('rreo_01'), dataframes_tratados.get('dca_c')]),
                "D4_00002": (analisar_D4_00002, [dataframes_tratados.get('rreo_01'), dataframes_tratados.get('dca_d')]),
                "D4_00003": (analisar_D4_00003, [dataframes_tratados.get('rreo_02'), dataframes_tratados.get('dca_e')]),
                "D4_00004": (analisar_D4_00004, [dataframes_tratados.get('rreo_02'), dataframes_tratados.get('dca_e')]),
                "D4_00005": (analisar_D4_00005, [dataframes_tratados.get('rreo_07'), dataframes_tratados.get('dca_f')]),
                "D4_00006": (analisar_D4_00006, [dataframes_tratados.get('rreo_07'), dataframes_tratados.get('dca_g')]),
                "D4_00007": (analisar_D4_00007, [dataframes_tratados.get('rreo_07'), dataframes_tratados.get('dca_g')]),
                "D4_00010": (analisar_D4_00010, [dataframes_tratados.get('rreo_03'), dataframes_tratados.get('dca_c')]),
                "D4_00012": (analisar_D4_00012, [dataframes_tratados.get('rreo_03'), dataframes_tratados.get('dca_c')]),
                "D4_00017": (analisar_D4_00017, [dataframes_tratados.get('rreo_03'), dataframes_tratados.get('dca_c')]),
                "D4_00019": (analisar_D4_00019, [dataframes_tratados.get('rreo_09'), dataframes_tratados.get('dca_d')]),
                "D4_00020": (analisar_D4_00020, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_01')]),
                "D4_00022": (analisar_D4_00022, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_03')]),
                "D4_00024": (analisar_D4_00024, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_03')]),
                "D4_00025": (analisar_D4_00025, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_01')]),
                "D4_00026": (analisar_D4_00026, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_01')]),
                "D4_00029": (analisar_D4_00029, [dados_preparados.get('emp_msc_dezembro'), dataframes_tratados.get('rreo_02')]),
                "D4_00030": (analisar_D4_00030, [dados_preparados.get('emp_msc_dezembro'), dataframes_tratados.get('rreo_02')]),
                "D4_00031": (analisar_D4_00031, [dados_preparados.get('emp_msc_dezembro'), dataframes_tratados.get('rreo_02')]),
                "D4_00032": (analisar_D4_00032, [dados_preparados.get('emp_msc_dezembro'), dataframes_tratados.get('rreo_02')]),
                "D4_00033": (analisar_D4_00033, [dados_preparados.get('emp_msc_dezembro'), dataframes_tratados.get('rreo_02')]),
                "D4_00034": (analisar_D4_00034, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_07')]),
                "D4_00038": (analisar_D4_00038, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_06')]),
                "D4_00040": (analisar_D4_00040, [dataframes_tratados.get('msc_dezembro'), dataframes_tratados.get('rreo_06')]),
            }


            todos_os_resultados = []
            analises_puladas = []
            
            # --- LOOP DE EXECUÇÃO ---
            for id_dim, (funcao, args) in mapeamento_analises.items():
                try:
                    # A chamada agora usa *args para desempacotar a lista de argumentos
                    resultado = funcao(*args)
                    if resultado:
                        todos_os_resultados.append(resultado)
                    else:
                        analises_puladas.append(f"**{id_dim}**: Não executada por falta de um ou mais relatórios obrigatórios.")
                except Exception as e:
                    st.error(f"Erro ao executar a análise {id_dim}: {e}")
                    analises_puladas.append(f"**{id_dim}**: Falhou com um erro inesperado durante a execução: {e}")


            if analises_puladas:
                with st.expander("⚠️ Análises Não Executadas", expanded=True):
                    for aviso in analises_puladas:
                        st.warning(aviso)
            
            if not todos_os_resultados:
                st.warning("Nenhuma análise pôde ser concluída com sucesso.")
                st.stop()

            ############################################################################################################
            # --- SEÇÃO DE ESTATÍSTICAS ---

            # Exibe os resultados que foram gerados com sucesso
            tabela_resumo_completa = pd.concat([res['df_resumo'] for res in todos_os_resultados], ignore_index=True)
            grupos_analise = sorted(tabela_resumo_completa['Grupo'].unique())

            st.subheader("Estatísticas da Análise")
            
            contagens = tabela_resumo_completa['Resposta'].value_counts()
            
            erros = contagens.get("❌ ERRO", 0)
            ok = contagens.get("✅ OK", 0)
            ok_centavos = contagens.get("⚠️ OK (Dif. Centavos)", 0)
            total = len(tabela_resumo_completa)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Quantidade com Erro", f"❌ {erros}")
            col2.metric("Quantidade OK", f"✅ {ok}")
            col3.metric("Quantidade OK (Dif. Centavos)", f"⚠️ {ok_centavos}")
            col4.metric("Total de Dimensões Analisadas", f"📊 {total}")

            st.divider()

            ###########################################################################
            # --- SEÇÃO DE RESULTADOS DAS ANÁLISES DAS DIMENSÕES ---
            for grupo in grupos_analise:
                st.subheader(grupo)
                df_resumo_grupo = tabela_resumo_completa[tabela_resumo_completa['Grupo'] == grupo].drop(columns=['Grupo'])
                df_estilizado = estilizar_tabela_resumo(df_resumo_grupo)
                st.dataframe(df_estilizado, hide_index=True, use_container_width=True,
                    column_config={
                        "Dimensão": st.column_config.TextColumn(width="small"),
                        "Resposta": st.column_config.TextColumn(width="small"),
                        "Descrição da Dimensão": st.column_config.TextColumn(width="large"),
                    })

                detalhes_grupo = [res for res in todos_os_resultados if res['grupo'] == grupo]
                with st.container(border=True):
                    st.write("#### Detalhamento das Análises")
                    aplicar_estilo_status_expander()
                    for resultado in detalhes_grupo:
                        resposta = resultado["df_resumo"]["Resposta"].iloc[0]
                        status = obter_status_visual(resposta)
                        renderizar_chamada_expander(resultado)
                        with st.expander(f"{status['icone']} {status['rotulo']} | **{resultado['id']}**: {resultado['titulo']}"):
                            st.dataframe(resultado['df_detalhes'], hide_index=True, use_container_width=True)

                st.divider()


    st.divider()

    ######################################################################################################################
    # --- SEÇÃO DE ANÁLISE DO EXTRATO DE ENTREGAS ---
    st.subheader("Análise do Extrato de Entregas dos Demonstrativos")

    st.markdown("""
    Nesta seção, é possível analisar o status da entrega dos demonstrativos municipais, a fim de verificar se todos os arquivos, 
                especialmente os de fim de ano, foram corretamente enviados ao SICONFI.
    """)

    #if st.button("Analisar Extrato de Entregas", use_container_width=True, disabled=not st.session_state.dados_carregados):
    if st.button("Analisar Extrato de Entregas dos Demonstrativos", use_container_width=True):
        st.session_state.show_extrato = True

    if st.session_state.get('show_extrato', True):
        df_extrato_entregas = st.session_state.get("extrato_df")
        if df_extrato_entregas is not None and not df_extrato_entregas.empty:
            extrato_filtrado = df_extrato_entregas.copy()

            #st.markdown("---")
            st.markdown(f"##### Extrato apenas dos Demonstrativos do Final do Ano de {ano}")

            # TABELA PARA PODER VER OS EXTRATOS DE FIM DE ANO
            #if st.button("Gerar Tabela de Fim de Ano"):
            df_extrato = st.session_state.get("extrato_df").copy()
            df_extrato['periodo'] = df_extrato['periodo'].astype(str)

            # Determine report names based on the previously detected type
            nome_rgf = "Relatório de Gestão Fiscal Simplificado" if tipo_relatorio == "Simplificado" else "Relatório de Gestão Fiscal"
            nome_rreo = "Relatório Resumido de Execução Orçamentária Simplificado" if tipo_relatorio == "Simplificado" else "Relatório Resumido de Execução Orçamentária"
            periodo_rgf = "2" if tipo_relatorio == "Simplificado" else "3"

            # Build conditions
            cond_msc_e = (df_extrato['entregavel'] == 'MSC Encerramento')
            cond_msc_a = (df_extrato['entregavel'] == 'MSC Agregada') & (df_extrato['periodo'] == '12')
            cond_rreo = (df_extrato['entregavel'] == nome_rreo) & (df_extrato['periodo'] == '6')
            cond_dca = (df_extrato['entregavel'] == 'Balanço Anual (DCA)')
            cond_rgf = (df_extrato['entregavel'] == nome_rgf) & (df_extrato['periodo'] == periodo_rgf)

            # Apply filters
            df_fim_de_ano = df_extrato[cond_msc_e | cond_msc_a | cond_rreo | cond_dca | cond_rgf]

            if not df_fim_de_ano.empty:
                st.dataframe(df_fim_de_ano)
            #     st.download_button(
            #         label="Baixar Tabela de Fim de Ano (.csv)",
            #         data=converter_df_para_csv(df_fim_de_ano),
            #         file_name=f"extrato_fim_de_ano_{nome_ente_selecionado}_{ano}.csv",
            #         mime='text/csv',
            #         key="download_fim_de_ano"
            #     )
            else:
                st.warning("Nenhum demonstrativo de fim de ano encontrado no extrato.")
                    
            
            # TABELA PARA PODER REALIZAR AS ANÁLISES DO EXTRATOS COM OS FILTROS
            st.markdown(f"##### Extrato Completo dos Demonstrativos carregados no SICONFI no ano de {ano}")
            colunas_para_filtrar = ["instituicao", "entregavel"]
            filtros = {}

            for col in colunas_para_filtrar:
                if col in extrato_filtrado.columns:
                    unique_values = ["Todos"] + sorted(list(extrato_filtrado[col].unique()))
                    filtros[col] = st.selectbox(f"Filtrar por {col}", unique_values, key=f"filter_{col}")

            for col, valor_filtro in filtros.items():
                if valor_filtro != "Todos":
                    extrato_filtrado = extrato_filtrado[extrato_filtrado[col] == valor_filtro]
            
            st.dataframe(extrato_filtrado)


            # BOTÃO DE GERAR O DOWNLOAD DO FILTRO REALIZADO
            st.download_button(
                label="Baixar Extrato Filtrado (.csv)",
                data=converter_df_para_csv(extrato_filtrado),
                file_name=f"extrato_entregas_{nome_ente_selecionado}_{ano}.csv",
                mime='text/csv',
                key="download_extrato"
            )

            

        else:
            st.info("O extrato de entregas não foi encontrado ou está vazio para os filtros selecionados.")



# Renomear main() para ser chamada como módulo
def renderizar_artefato_real():
    """
    Renderiza o artefato real de análise SICONFI
    Adaptado para funcionar dentro do app de apresentação
    """
    # Não chamar configurar_pagina() pois já foi configurado no app principal
    # configurar_pagina()

    # Executar a função main original
    main()


if __name__ == "__main__":
    main()
