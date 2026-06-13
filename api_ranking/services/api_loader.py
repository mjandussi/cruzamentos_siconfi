import asyncio
import time

import httpx
import pandas as pd
import streamlit as st

API_ROOT = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"

MSC_COLUMNS = [
    "exercicio",
    "instituicao",
    "cod_ibge",
    "uf",
    "populacao",
    "an_referencia",
    "me_referencia",
    "mes_referencia",
    "co_tipo_matriz",
    "tipo_matriz",
    "classe_conta",
    "id_tv",
    "tipo_valor",
    "conta_contabil",
    "natureza_conta",
    "natureza_receita",
    "natureza_despesa",
    "funcao",
    "subfuncao",
    "fonte_recursos",
    "valor",
]

#############################################################################
####  Funções Assíncronas  ####
#############################################################################

# Timeout: leitura de payloads grandes (MSC) pode demorar; conexão TLS ocasionalmente estoura com connect curto.
_DEFAULT_TIMEOUT = httpx.Timeout(180.0, connect=60.0)


async def _request_json(
    client,
    url,
    params,
    sem,
    retries=5,
    backoff=0.75,
    timeout=_DEFAULT_TIMEOUT,
):
    """GET JSON com `items`; reintentos em 5xx/429 e em falhas de rede/leitura (ex.: ReadError)."""
    last_status_resp = None
    for attempt in range(retries):
        if sem:
            await sem.acquire()
        try:
            try:
                resp = await client.get(url, params=params, timeout=timeout)
            except httpx.RequestError:
                await asyncio.sleep(backoff * (2 ** attempt))
                if attempt == retries - 1:
                    raise
                continue

            if resp.status_code in (429, 500, 502, 503, 504):
                last_status_resp = resp
                await asyncio.sleep(backoff * (2 ** attempt))
                continue

            resp.raise_for_status()

            try:
                data = resp.json()
            except ValueError:
                await asyncio.sleep(backoff * (2 ** attempt))
                if attempt == retries - 1:
                    raise
                continue

            return data.get("items", [])
        finally:
            if sem:
                sem.release()

    if last_status_resp is not None:
        last_status_resp.raise_for_status()
    raise httpx.ReadError("Esgotadas as tentativas de leitura da API SICONFI.")


async def fetch_paginated(client, path, params, sem=None, page_size=5000, delay=0.0):
    frames, offset = [], 0
    while True:
        q = dict(params)
        q.update({"offset": offset, "limit": page_size})
        items = await _request_json(client, f"{API_ROOT}/{path}", q, sem)
        if not items:
            break
        frames.append(pd.DataFrame(items))
        offset += page_size
        if delay:  # para ser gentil com a API
            await asyncio.sleep(delay)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


async def fetch_once(client, path, params, sem=None):
    items = await _request_json(client, f"{API_ROOT}/{path}", params, sem)
    return pd.DataFrame(items)


async def load_msc_group(client, path, classes, co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay=0.0):
    tasks = []
    for classe in map(str, classes):
        for tipo in tipos_balanco:
            for mes in meses:
                params = {
                    "id_ente": ente,
                    "an_referencia": ano,
                    "me_referencia": mes,
                    "co_tipo_matriz": co_tipo_matriz,
                    "classe_conta": classe,
                    "id_tv": tipo,
                }
                tasks.append(fetch_paginated(client, path, params, sem=sem, delay=delay))
    dfs = await asyncio.gather(*tasks)
    return _ensure_msc_columns(
        pd.concat([df for df in dfs if not df.empty], ignore_index=True) if dfs else pd.DataFrame()
    )


def _ensure_msc_columns(df):
    """Mantém o shape esperado mesmo quando a API não devolve linhas."""
    if df is None or df.empty:
        return pd.DataFrame(columns=MSC_COLUMNS)
    for col in MSC_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df


async def load_msc_all(ente, ano, meses, tipos_balanco, co_tipo_matriz="MSCC", concurrency=6, delay=0.08):
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(http2=True) as client:
        msc_patrimonial = await load_msc_group(client, "msc_patrimonial", [1, 2, 3, 4], co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay)
        msc_orcam = await load_msc_group(client, "msc_orcamentaria", [5, 6], co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay)
        msc_ctr = await load_msc_group(client, "msc_controle", [7, 8], co_tipo_matriz, tipos_balanco, meses, ente, ano, sem, delay)
    return msc_patrimonial, msc_orcam, msc_ctr


async def load_dca(ente, ano, concurrency=8):
    sem = asyncio.Semaphore(concurrency)
    anexos = {
        "ab": "DCA-Anexo I-AB",
        "c":  "DCA-Anexo I-C",
        "d":  "DCA-Anexo I-D",
        "e":  "DCA-Anexo I-E",
        "f":  "DCA-Anexo I-F",
        "g":  "DCA-Anexo I-G",
        "hi": "DCA-Anexo I-HI",
    }
    async with httpx.AsyncClient(http2=True) as client:
        tasks = {
            k: fetch_once(client, "dca", {"an_exercicio": ano, "no_anexo": v, "id_ente": ente}, sem=sem)
            for k, v in anexos.items()
        }
        results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))


async def load_rreo(ente, ano, tipo_relatorio="Completo", concurrency=8):
    """
    Carrega RREO da API.
    tipo_relatorio: "Completo" ou "Simplificado" (apenas para Municípios)
    """
    sem = asyncio.Semaphore(concurrency)
    anexos = {
        "1": "RREO-Anexo 01",
        "2": "RREO-Anexo 02",
        "3": "RREO-Anexo 03",
        "4": "RREO-Anexo 04",
        "4_rpps": "RREO-Anexo 04 - RPPS",
        "4_rgps": "RREO-Anexo 04 - RGPS",
        "6": "RREO-Anexo 06",
        "7": "RREO-Anexo 07",
        "9": "RREO-Anexo 09",
        "11": "RREO-Anexo 11",
        "14": "RREO-Anexo 14",
    }
    co_tipo_demo = "RREO Simplificado" if tipo_relatorio == "Simplificado" else "RREO"

    base = {"an_exercicio": ano, "nr_periodo": 6, "co_tipo_demonstrativo": co_tipo_demo, "id_ente": ente}
    async with httpx.AsyncClient(http2=True) as client:
        tasks = {k: fetch_once(client, "rreo", base | {"no_anexo": v}, sem=sem) for k, v in anexos.items()}
        results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))


async def load_rgf(ente, ano, tipo_ente="E", tipo_relatorio="Completo", concurrency=8, nr_periodo=None):
    """
    Carrega RGF da API.
    tipo_ente: "E" (Estado) ou "M" (Município)
    tipo_relatorio: "Completo" ou "Simplificado" (apenas para Municípios)

    Diferenças:
    - Estados: Quadrimestral (Q), período 3, todos os poderes (E, L, J, M, D)
    - Municípios Completo: Quadrimestral (Q), período 3, poderes E e L
    - Municípios Simplificado: Semestral (S), período 2, poderes E e L
    """
    sem = asyncio.Semaphore(concurrency)

    if tipo_ente == "E":
        periodicidade = "Q"
        periodo = 3
        co_tipo_demo = "RGF"
        a5_poderes = {"5e": "E", "5l": "L", "5j": "J", "5m": "M", "5d": "D"}
        a1_poderes = {"1e": "E", "1l": "L", "1j": "J", "1m": "M", "1d": "D"}
        outros = {"2e": ("RGF-Anexo 02", "E"), "3e": ("RGF-Anexo 03", "E"), "4e": ("RGF-Anexo 04", "E")}
    else:
        if tipo_relatorio == "Simplificado":
            periodicidade = "S"
            periodo = 2
            co_tipo_demo = "RGF Simplificado"
        else:
            periodicidade = "Q"
            periodo = 3
            co_tipo_demo = "RGF"
        a5_poderes = {"5e": "E", "5l": "L"}
        a1_poderes = {"1e": "E", "1l": "L"}
        outros = {"2e": ("RGF-Anexo 02", "E"), "3e": ("RGF-Anexo 03", "E"), "4e": ("RGF-Anexo 04", "E")}

    # Sobrescreve o período apenas no caso QUADRIMESTRAL (estado ou município Completo),
    # respeitando o quadrimestre escolhido no dashboard RGF. Município Simplificado é
    # sempre SEMESTRAL (período 2) e não deve ser alterado.
    if nr_periodo is not None and periodicidade == "Q":
        periodo = int(nr_periodo)

    async with httpx.AsyncClient(http2=True) as client:
        tasks = {}
        for k, poder in a5_poderes.items():
            tasks[k] = fetch_once(client, "rgf",
                                  {"an_exercicio": ano, "in_periodicidade": periodicidade, "nr_periodo": periodo,
                                   "co_tipo_demonstrativo": co_tipo_demo, "no_anexo": "RGF-Anexo 05",
                                   "co_poder": poder, "id_ente": ente}, sem=sem)
        for k, poder in a1_poderes.items():
            tasks[k] = fetch_once(client, "rgf",
                                  {"an_exercicio": ano, "in_periodicidade": periodicidade, "nr_periodo": periodo,
                                   "co_tipo_demonstrativo": co_tipo_demo, "no_anexo": "RGF-Anexo 01",
                                   "co_poder": poder, "id_ente": ente}, sem=sem)
        for k, (anexo, poder) in outros.items():
            tasks[k] = fetch_once(client, "rgf",
                                  {"an_exercicio": ano, "in_periodicidade": periodicidade, "nr_periodo": periodo,
                                   "co_tipo_demonstrativo": co_tipo_demo, "no_anexo": anexo,
                                   "co_poder": poder, "id_ente": ente}, sem=sem)
        results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))

####################################################################################################3

#############################################################################
####  Funções com Cache  ####
#############################################################################
#
#   CACHE — LOCAL vs PRODUÇÃO (alinhado à página de validações)
#   -------------------------------------------------------------
#   Por defeito: TTL nos decorators; sem max_entries → vários entes/anos
#   podem ficar em cache (rápido para testes locais; mais RAM no processo).
#
#   Em VPS com 8 GB e vários estados grandes no mesmo container, podes:
#   • em get_extratos:     @st.cache_data(..., max_entries=16)
#   • em load_all_data_cached: @st.cache_data(..., max_entries=3)
#   (LRU expulsa entradas antigas; reduz pico, pode forçar novo download.)
#
#   Na página de validações existe bloco comentado: st.cache_data.clear()
#   ao mudar ente/ano — combina bem com max_entries em cenários apertados.
#
#############################################################################

# LER A BASE DO RANKING (RESULTADOS)
@st.cache_data(ttl=86400, show_spinner=False)  # Cache por 24 horas (bases mudam raramente)
def load_base_ranking(tipo_ente, caminho_base_estados, caminho_base_municipios):
    """
    Carrega a base de ranking (estados ou municípios) com cache.
    TTL = 86400 segundos (24 horas / 1 dia)
    """
    try:
        if tipo_ente == "E":
            df = pd.read_csv(
                caminho_base_estados,
                encoding='utf-8',
                sep=';',
                on_bad_lines='skip',
                low_memory=False
            )
            return df, "COD_IBGE", "NO_ESTADO"
        df = pd.read_csv(
            caminho_base_municipios,
            encoding='utf-8',
            sep=';',
            on_bad_lines='skip',
            low_memory=False
        )
        return df, "ID_ENTE", "NOME_ENTE"
    except Exception as e:
        raise e

# PEGAR A BASE DE EXTRATO DE ENTREGAS (política de cache: ver quadro acima)
@st.cache_data(show_spinner=False, ttl=3600)
def get_extratos(ente: str, ano: int, page_size: int = 5000) -> pd.DataFrame:
    """
    Busca todos os registros de extrato na API SICONFI usando paginação.
    O resultado é cacheado por (ente, ano, page_size).
    TTL = 3600 segundos (1 hora)
    """
    url = f"{API_ROOT}/extrato_entregas"
    frames = []
    offset = 0
    while True:
        params = {"id_ente": ente, "an_referencia": ano, "limit": page_size, "offset": offset}
        r = None
        for attempt in range(5):
            try:
                r = httpx.get(url, params=params, timeout=_DEFAULT_TIMEOUT)
                r.raise_for_status()
                break
            except httpx.RequestError:
                if attempt == 4:
                    raise
                time.sleep(0.75 * (2 ** attempt))
        items = r.json().get("items", [])
        if not items:
            break
        frames.append(pd.DataFrame(items))
        if len(items) < page_size:
            break
        offset += page_size
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# PEGAR TODOS OS DEMONSTRATIVOS (política de cache: ver quadro acima)
@st.cache_data(ttl=43200, show_spinner=False)
def load_all_data_cached(ente, ano, meses, tipos_balanco, tipo_ente="E", tipo_relatorio="Completo",
                         carregar_msce=True, carregar_dca=True, carregar_rreo=True, carregar_rgf=True):
    """
    Carrega todos os dados da API com cache.
    TTL = 43200 segundos (12 horas)

    Parâmetros:
    - ente: código do ente
    - ano: ano de exercício
    - meses: lista de meses disponíveis (baseado no extrato)
    - tipos_balanco: tipos de balanço
    - tipo_ente: "E" (Estado) ou "M" (Município)
    - tipo_relatorio: "Completo" ou "Simplificado" (apenas para Municípios)
    - carregar_msce: se True, carrega MSC de Encerramento
    - carregar_dca: se True, carrega DCA
    - carregar_rreo: se True, carrega RREO
    - carregar_rgf: se True, carrega RGF
    """
    async def _load_all():
        if meses:
            msc_patrimonial, msc_orcam, msc_ctr = await load_msc_all(
                ente, ano, meses, tipos_balanco, co_tipo_matriz="MSCC", concurrency=6, delay=0.08
            )
        else:
            msc_patrimonial, msc_orcam, msc_ctr = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        if carregar_msce:
            msc_patrimonial_encerr, msc_orcam_encerr, msc_ctr_encerr = await load_msc_all(
                ente, ano, [12], tipos_balanco, co_tipo_matriz="MSCE", concurrency=6, delay=0.08
            )
        else:
            msc_patrimonial_encerr, msc_orcam_encerr, msc_ctr_encerr = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        if carregar_dca:
            dca = await load_dca(ente, ano)
        else:
            dca = {k: pd.DataFrame() for k in ['ab', 'c', 'd', 'e', 'f', 'g', 'hi']}

        if carregar_rreo:
            rreo = await load_rreo(ente, ano, tipo_relatorio=tipo_relatorio)
        else:
            rreo = {k: pd.DataFrame() for k in ['1', '2', '3', '4', '4_rpps', '4_rgps', '6', '7', '9', '11', '14']}

        if carregar_rgf:
            rgf = await load_rgf(ente, ano, tipo_ente=tipo_ente, tipo_relatorio=tipo_relatorio)
        else:
            if tipo_ente == "E":
                rgf = {k: pd.DataFrame() for k in ['5e', '5l', '5j', '5m', '5d', '1e', '1l', '1j', '1m', '1d', '2e', '3e', '4e']}
            else:
                rgf = {k: pd.DataFrame() for k in ['5e', '5l', '1e', '1l', '2e', '3e', '4e']}

        return {
            'msc_patrimonial': msc_patrimonial,
            'msc_orcam': msc_orcam,
            'msc_ctr': msc_ctr,
            'msc_patrimonial_encerr': msc_patrimonial_encerr,
            'msc_orcam_encerr': msc_orcam_encerr,
            'msc_ctr_encerr': msc_ctr_encerr,
            'dca': dca,
            'rreo': rreo,
            'rgf': rgf
        }

    return asyncio.run(_load_all())


# PEGAR APENAS O RGF (usado pelo Dashboard RGF) — cache de 12h
@st.cache_data(ttl=43200, show_spinner=False)
def load_rgf_cached(ente, ano, tipo_ente="E", tipo_relatorio="Completo", nr_periodo=None):
    """
    Carrega os anexos do RGF da API com cache (dict de DataFrames por chave: 1e, 2e, 3e, 5e, ...).
    TTL = 43200 segundos (12 horas).

    - tipo_ente: "E" (Estado) ou "M" (Município)
    - tipo_relatorio: "Completo" ou "Simplificado" (apenas para Municípios)
    - nr_periodo: quadrimestre/semestre da API (sobrescreve o período padrão quando informado)
    """
    return asyncio.run(
        load_rgf(ente, ano, tipo_ente=tipo_ente, tipo_relatorio=tipo_relatorio, nr_periodo=nr_periodo)
    )
