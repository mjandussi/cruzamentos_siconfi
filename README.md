# Cruzamentos Siconfi

Aplicativo Streamlit para apoiar a análise de consistência entre informações
contábeis e fiscais publicadas no Siconfi. O projeto organiza verificações das
dimensões D2, D3 e D4 e apresenta os resultados com contexto, cobertura e
rastreabilidade.

> **Importante:** o aplicativo produz um diagnóstico técnico de apoio. Seus
> resultados não constituem nota oficial, certificação, auditoria ou decisão do
> Tesouro Nacional. A classificação oficial deve ser consultada nos canais do
> próprio Tesouro.

## Modos de análise

### Validação on-line

Consulta a API pública do Siconfi durante a execução e cruza dados da MSC, DCA,
RREO e RGF disponíveis para o ente e o período selecionados. O resultado é uma
fotografia da disponibilidade da API naquele momento: ausência de dados, falha
técnica e não aplicabilidade devem ser interpretadas separadamente de uma
divergência efetivamente reproduzida.

Esse modo requer conexão com a internet. Como as fontes podem ser atualizadas,
o resultado on-line não deve ser tratado como reprodução automática de uma base
anual encerrada.

### Diagnóstico histórico

Usa os recortes locais e imutáveis em [`data/`](data/) para explorar o exercício
de 2025 dos 92 municípios do Rio de Janeiro. A tela permite analisar:

- o escopo completo de 72 verificações de cruzamento (17 D2, 28 D3 e 27 D4); e
- o subconjunto de 36 verificações diretamente conciliáveis entre DCA, RREO e
  RGF, sem dependência da MSC.

O modo histórico é retrospectivo e descritivo. Uma não pontuação na base
encerrada sinaliza uma ocorrência a investigar; isoladamente, ela não prova qual
fonte está incorreta. A proveniência, os hashes e as limitações dos recortes
estão descritos em [`data/README.md`](data/README.md).

## Estado da implementação

O escopo de 2025 possui **72 de 72 regras concretas no motor**: 17 D2, 28 D3 e
27 D4. As 23 lacunas identificadas na comparação inicial com a dissertação foram
portadas dos arquivos de regras originais:

- D2: `D2_00100` a `D2_00104`;
- D3: `D3_00017`, `D3_00026`, `D3_00027`, `D3_00028`, `D3_00030`,
  `D3_00032`, `D3_00033`, `D3_00034`, `D3_00035`, `D3_00037`, `D3_00038`,
  `D3_00039`, `D3_00040`, `D3_00044` e `D3_00047`;
- D4: `D4_00043`, `D4_00046` e `D4_00047`.

A tela on-line calcula essa cobertura diretamente das listas metodológicas e
das funções existentes em `d2_dca.py`, `d3.py` e `d4.py`. Não há catálogo de
regras paralelo para manter. "Regra concreta" indica presença da implementação;
a execução para cada ente ainda depende da disponibilidade dos demonstrativos.

## Requisitos

- Python 3.12 (recomendado);
- acesso à internet para instalar as dependências e usar a validação on-line.

As versões de execução estão fixadas em [`requirements.txt`](requirements.txt)
para tornar a instalação reproduzível.

## Instalação e execução

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O Streamlit exibirá o endereço local do aplicativo, normalmente
`http://localhost:8501`.

## Autenticação opcional

Por padrão, o aplicativo inicia sem exigir login. Para habilitar autenticação,
copie [`.env.example`](.env.example) para `.env`, altere `AUTH_ENABLED` para
`true` e informe hashes bcrypt nas variáveis de usuário. Nunca registre o
arquivo `.env` nem senhas em texto puro no Git.

## Testes

Com o ambiente virtual ativado e as dependências instaladas:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem as listas metodológicas, as 72 funções concretas de 2025, os
estados do diagnóstico e regressões analíticas das regras portadas. Eles não
fazem chamadas à API do Siconfi.

Uma verificação rápida de sintaxe também pode ser executada com:

```bash
python -m compileall -q app.py core api_ranking pages tests
```

## Estrutura principal

```text
app.py                 entrada e autenticação
pages/                 telas on-line e retrospectiva
core/                  metodologia, diagnóstico, layout e utilitários
api_ranking/           coleta, regras analíticas e renderização dos resultados
data/                   recortes históricos reproduzíveis
tests/                  testes unitários e de regressão
assets/                 identidade visual
```

## Licença

Consulte [`LICENSE`](LICENSE).
