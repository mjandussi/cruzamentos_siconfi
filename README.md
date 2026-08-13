# Cruzamentos Siconfi

Aplicativo aberto em Streamlit para apoiar a conferência de consistência entre
demonstrativos contábeis e fiscais publicados no Siconfi. O sistema organiza os
cruzamentos da dissertação nas dimensões funcionais D2, D3 e D4, mostra a memória
de cálculo e permite exportar os dados usados na análise.

> O aplicativo é uma ferramenta de apoio. Seus resultados não constituem nota
> oficial, certificação, auditoria ou decisão do Tesouro Nacional. Uma diferença
> encontrada também não determina, sozinha, qual demonstrativo deve ser corrigido.

## Modos de análise

| Modo | Escopo | Fonte dos dados |
| --- | --- | --- |
| **Validação on-line** | Municípios e exercícios metodológicos de 2023 a 2025 | API pública do Siconfi no momento da consulta |
| **Diagnóstico histórico** | 92 municípios do RJ, exercício 2025 | Recortes locais preservados e verificados por SHA-256 |

A validação on-line consulta o extrato de entregas, identifica a
disponibilidade dos demonstrativos e cruza DCA, RREO, RGF, MSC corrente de
dezembro e MSC de encerramento. Como a API pode ser atualizada, o resultado é
uma fotografia da consulta, e não a reprodução de uma base anual encerrada.

O diagnóstico histórico não consulta a API nem recalcula o Ranking. Ele permite
examinar as 72 verificações de 2025 ou o subconjunto de 36 conciliações sem
dependência da MSC. Consulte a [proveniência dos recortes](data/README.md).

## Escopo metodológico

| Exercício | D2 | D3 | D4 | Total |
| ---: | ---: | ---: | ---: | ---: |
| 2023 | 7 | 17 | 24 | 48 |
| 2024 | 7 | 28 | 26 | 61 |
| 2025 | 17 | 28 | 27 | 72 |

Essas 72 verificações integram o grupo **cruzamento** da taxonomia final da
dissertação e preservam seus códigos operacionais D2, D3 e D4 do Ranking. O
grupo metodológico “cruzamento” não equivale à dimensão D4 oficial do Ranking.
O escopo anual autoritativo do aplicativo está em
[`core/methodology.py`](core/methodology.py). A implementação de 2025 possui
funções concretas para as 72 regras. Disponibilidade de implementação,
aplicabilidade e disponibilidade de dados são conceitos diferentes.

Os períodos, estados de resultado, fontes metodológicas conhecidas e limites
estão detalhados em [Metodologia](docs/METODOLOGIA.md).

## Requisitos

- Python 3.12, versão usada como ambiente de referência;
- acesso à internet para instalar dependências e usar o modo on-line;
- memória compatível com o volume da MSC do município analisado.

O [`requirements.txt`](requirements.txt) fixa as dependências diretas do
ambiente de referência. Ele não é um arquivo de lock completo das dependências
transitivas.

## Instalação e execução

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Linux ou macOS

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

O endereço local normalmente será `http://localhost:8501`. Os comandos usam o
Python do ambiente virtual diretamente, portanto sua ativação é opcional.

## Como usar

Na validação on-line:

1. selecione o exercício, a UF e o município;
2. carregue e valide o extrato de entregas;
3. processe os demonstrativos disponíveis;
4. consulte o resumo e abra as evidências de cada regra em D2, D3 ou D4;
5. exporte os resultados e, depois de uma correção, compare os arquivos
   `antes` e `depois`.

As exportações disponíveis incluem:

- resultados da análise em Excel e comparação entre duas exportações;
- DCA, RREO e RGF reunidos em Excel;
- MSC corrente de dezembro e MSC de encerramento em um Excel separado;
- extrato de entregas em CSV;
- diagnóstico histórico agregado e fila municipal em CSV.

Na exportação da MSC, a matriz corrente permanece como mês 12 e a matriz de
encerramento é apresentada como mês 13 para leitura humana. Na API, ambas são
consultadas com mês de referência 12 e distinguidas pelo tipo de matriz.

## Autenticação opcional

O aplicativo é público por padrão. Para ativar o login, copie
[`.env.example`](.env.example) para `.env`, defina `AUTH_ENABLED=true` e
preencha somente hashes bcrypt nas variáveis de usuário. O arquivo `.env` está
ignorado pelo Git e nunca deve conter senhas em texto puro.

Essa autenticação foi projetada para uma instalação simples e não substitui um
provedor de identidade, HTTPS ou controles de infraestrutura. Leia a
[política de segurança](SECURITY.md) antes de publicar o aplicativo.

## Testes

Com o ambiente instalado:

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py core api_ranking pages tests
```

Os testes são locais e não fazem chamadas à API do Siconfi. Eles cobrem o
escopo metodológico, regras portadas, classificação dos resultados, interface e
exportação da MSC.

## Estrutura

```text
app.py                 entrada e autenticação
pages/                 páginas on-line, inicial e histórica
core/                  autenticação, metodologia, estados e layout compartilhado
api_ranking/           coleta, regras analíticas e apresentação dos resultados
assets/                CSS e marca visual
data/                  recortes históricos preservados
docs/                  arquitetura e metodologia
tests/                 testes unitários e de regressão
```

Veja a [arquitetura e os fluxos](docs/ARQUITETURA.md) e as
[orientações para contribuição](CONTRIBUTING.md).

## Limitações principais

- o modo on-line depende da disponibilidade e do esquema atual da API;
- ausência de dados, não aplicabilidade e falha técnica não significam
  divergência;
- os exercícios fora de 2023 a 2025 não possuem metodologia cadastrada;
- o modo histórico cobre somente municípios do RJ em 2025;
- os testes não validam a integração com a API ao vivo;
- o processamento e os caches ficam na memória do processo Streamlit;
- uma planilha Excel comporta no máximo 1.048.575 linhas de dados além do
  cabeçalho; a exportação da MSC informa erro se ultrapassar esse limite.

## Licença

O código é distribuído sob a [licença MIT](LICENSE). A situação documental
dos dados de terceiros é tratada separadamente em [`data/README.md`](data/README.md).
