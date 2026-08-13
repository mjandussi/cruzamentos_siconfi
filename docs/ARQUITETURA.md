# Arquitetura

## Visão geral

O Cruzamentos Siconfi é uma aplicação Streamlit executada em um único
processo. Não há banco de dados nem serviço de backend separado: os dados são
obtidos da API ou de arquivos locais, transformados em `DataFrame` do pandas e
mantidos temporariamente no cache ou na sessão do Streamlit.

```text
Navegador
   |
   v
Streamlit: app.py e pages/
   |------------------------------|
   v                              v
Validação on-line                Diagnóstico histórico
   |                              |
   v                              v
API Siconfi                       snapshots em data/
   |                              |
   v                              v
normalização e regras            SHA-256, esquema e estatísticas
   |                              |
   |------------------------------|
                  v
         interface e exportações
```

## Responsabilidades das pastas

| Caminho | Responsabilidade |
| --- | --- |
| `app.py` | Entrada do aplicativo e formulário de login quando habilitado. |
| `pages/` | Orquestração das telas inicial, on-line e histórica. |
| `core/auth.py` | Configuração de autenticação e estado da sessão. |
| `core/methodology.py` | Escopo anual autoritativo e classificação do ICF usada no modo histórico. |
| `core/diagnostics.py` | Vocabulário de estados e resumo de cobertura/conformidade. |
| `core/layout.py` | Configuração compartilhada, navegação e componentes de página. |
| `api_ranking/services/api_loader.py` | Coleta, paginação, repetição de requisições e cache da API. |
| `api_ranking/services/availability.py` | Interpretação do extrato e disponibilidade dos demonstrativos. |
| `api_ranking/services/exports.py` | Transformações puras e geração dos arquivos Excel. |
| `api_ranking/analysis/` | Regras contábeis e fiscais, separadas por dimensão funcional. |
| `api_ranking/renders/result_dashboard.py` | Abas, expanders e evidências dos resultados. |
| `api_ranking/renders/export_panels.py` | Widgets, fragmentos e estado das exportações. |
| `api_ranking/base_ranking/` | Catálogo local usado para localizar municípios; não substitui os dados consultados na API. |
| `data/` | Recortes imutáveis durante a execução do modo histórico. |
| `assets/` | Folha de estilos e marca visual. |
| `tests/` | Testes locais de metodologia, regras, interface e exportação. |

## Fluxo da validação on-line

1. A página oferece somente municípios e um exercício presente em
   `core/methodology.py`.
2. O catálogo local fornece código, nome e UF do município. Quando o exercício
   escolhido ainda não existe nesse catálogo, a lista do ano mais recente é
   usada apenas para a seleção do ente.
3. O extrato de entregas é consultado na API Siconfi. A tela detecta a
   disponibilidade de DCA, RREO, RGF, MSCC e MSCE e, quando aplicável, o tipo
   completo ou simplificado dos relatórios fiscais.
4. `api_ranking/services/api_loader.py` consulta os endpoints necessários e
   devolve `DataFrame`s. As requisições grandes da MSC são paginadas; falhas de
   rede e respostas temporárias da API recebem novas tentativas.
5. A página normaliza sinais e recortes, chama as funções de D2, D3 e D4 e
   mantém no resultado final somente os códigos previstos para o exercício.
6. Cada regra produz um resumo e, quando possível, uma tabela de evidências. O
   resumo consolidado diferencia conformidade, divergência, falta de dados,
   não aplicabilidade e falha técnica.
7. A interface apresenta os resultados em ordem numérica, agrupados em D2, D3
   e D4. As evidências são renderizadas quando o usuário abre a verificação.
8. Os arquivos para download são montados em memória e não são persistidos
   pelo aplicativo.

O endereço-base usado pelo carregador é
`https://apidatalake.tesouro.gov.br/ords/siconfi/tt`. A disponibilidade e o
formato das respostas continuam sob controle do provedor externo.

### Contrato do resultado

O quadro final usa, no mínimo, as seguintes colunas:

| Coluna | Significado |
| --- | --- |
| `Dimensão` | Código da verificação, por exemplo `D4_00001`. |
| `Resposta` | Resposta original da regra, normalmente `OK`, `ERRO` ou `N/A`. |
| `Descrição da Dimensão` | Descrição legível do cruzamento. |
| `Nota` | Valor produzido pela regra quando há conclusão. |
| `OBS` | Contexto, ausências ou ressalvas relevantes. |

O renderer não deve recalcular a regra. Ele apenas classifica e apresenta o
resumo e a memória de cálculo recebidos.

## Fluxo do diagnóstico histórico

1. A página lê `data/ranking_rj_2025.csv` e
   `data/metodologia_cruzamentos_2025.csv`.
2. Antes da análise, valida o SHA-256, as colunas obrigatórias, os 92 municípios,
   o exercício e o domínio das pontuações.
3. O usuário escolhe o escopo completo de 72 cruzamentos ou o recorte de 36
   conciliações sem MSC.
4. A tela calcula estatísticas descritivas e uma fila de conferência por
   município. O cenário de ganho é contrafactual e não altera nem reproduz uma
   apuração oficial.
5. As tabelas agregadas e municipais podem ser baixadas em CSV.

Esse modo não usa os demonstrativos atuais nem faz chamadas externas. A origem
e as limitações dos arquivos estão em [`../data/README.md`](../data/README.md).

## Cache e estado

| Conteúdo | Mecanismo | Expiração configurada |
| --- | --- | ---: |
| Catálogo local de entes | `st.cache_data` | 24 horas |
| Extrato de entregas | `st.cache_data` | 1 hora |
| DCA, RREO, RGF e MSC | `st.cache_data` | 12 horas |
| Snapshots históricos validados | `st.cache_data` | Sem TTL explícito |
| Contexto e bytes de exportação | `st.session_state` | Sessão atual ou troca de ente/exercício |

O cache melhora a reexecução, mas consome memória do processo. Em uma
instalação com muitos usuários ou municípios grandes, o operador deve monitorar
o consumo e reiniciar ou limitar o processo conforme a infraestrutura. O
projeto não fornece persistência distribuída nem coordena cache entre réplicas.

## Exportações

- O Excel de demonstrativos contém DCA, RREO e RGF em abas separadas.
- O Excel da MSC contém somente MSCC/dezembro e MSCE/encerramento. A MSCE,
  consultada na API com mês 12, recebe o valor semântico 13 apenas na cópia
  exportada; o `DataFrame` usado pelas regras não é alterado.
- O Excel de resultados inclui situação diagnóstica e identificação das regras
  relacionadas à CAPAG. Duas exportações podem ser comparadas por resposta e
  nota.
- O extrato de entregas e as saídas históricas usam CSV.

A planilha da MSC aceita até 1.048.575 linhas de dados, reservando uma linha
para o cabeçalho do Excel. Acima disso, a exportação é interrompida com uma
mensagem explícita.

## Configuração

`.streamlit/config.toml` define o tema escuro, a execução headless e desativa a
telemetria do navegador. `.env.example` documenta as variáveis opcionais de
autenticação. O arquivo `.env` local tem precedência quando é carregado pelo
aplicativo.

| Variável | Padrão | Uso |
| --- | --- | --- |
| `AUTH_ENABLED` | `false` | Exige login quando recebe `true`, `1`, `yes` ou `sim`. |
| `SESSION_TIMEOUT_MINUTES` | `60` | Expira a sessão por inatividade. |
| `MAX_LOGIN_ATTEMPTS` | `10` | Limite de falhas registrado na sessão atual. |
| `LOGIN_LOCKOUT_MINUTES` | `60` | Duração do bloqueio local à sessão. |
| `USER_MJANDUSSI` | vazio | Hash bcrypt do perfil correspondente. |
| `USER_BELEM` | vazio | Hash bcrypt do perfil correspondente. |
| `USER_SUBCONT` | vazio | Hash bcrypt do perfil correspondente. |

As três configurações numéricas devem conter inteiros válidos. Os nomes de
perfil aceitos e eventuais restrições de ente ainda são definidos no código, e
não por um cadastro externo.

Os detalhes e limites de segurança estão em [`../SECURITY.md`](../SECURITY.md).

## Limites de teste

A suíte usa dados sintéticos e componentes locais. Ela protege regras e
contratos conhecidos sem depender da rede, mas não detecta antecipadamente uma
mudança de esquema ou indisponibilidade da API ao vivo. Uma verificação manual
do fluxo on-line continua necessária antes de uma publicação.
