# Metodologia

## Finalidade

O aplicativo reproduz cruzamentos selecionados na dissertação para apoiar a
conferência de consistência entre demonstrativos. Ele não tenta executar todas
as verificações do Ranking e não calcula uma nota oficial.

A taxonomia final da dissertação possui cinco grupos: entrega/homologação/
retificação, estrutura/preenchimento, adequação MCASP/PCASP, cruzamento e
demais. Este aplicativo implementa o grupo **cruzamento**. Os rótulos D2, D3 e
D4 preservam os códigos operacionais das verificações do Ranking; o conjunto
de 72 itens de 2025 não deve ser confundido com a dimensão D4 oficial.

## Fontes internas de verdade

O projeto separa três responsabilidades:

1. [`../core/methodology.py`](../core/methodology.py) define quais códigos
   pertencem a cada exercício e dimensão;
2. `api_ranking/analysis/d2_dca.py`, `d3.py` e `d4.py` implementam os cálculos;
3. [`../data/metodologia_cruzamentos_2025.csv`](../data/metodologia_cruzamentos_2025.csv)
   fornece título e relatórios para o snapshot histórico de 2025.

O arquivo CSV não substitui a lista anual do módulo Python. O modo histórico
valida que seus 72 códigos coincidem exatamente com o escopo de 2025.

O enquadramento conceitual decorre da seção 3.4 e do Quadro 2 da dissertação.
As listas operacionais anuais foram registradas no código a partir do recorte
municipal usado nas simulações do repositório da dissertação. A URL pública, o
commit exato dessa origem e a referência bibliográfica definitiva ainda não
estão registrados neste repositório e são **pendências de proveniência**.

## Escopo por exercício

| Exercício | D2 | D3 | D4 | Total |
| ---: | ---: | ---: | ---: | ---: |
| 2023 | 7 | 17 | 24 | 48 |
| 2024 | 7 | 28 | 26 | 61 |
| 2025 | 17 | 28 | 27 | 72 |

O motor de 2025 possui uma função concreta para cada item do escopo. Em 2024,
`D3_00029` e `D4_00045` pertencem à lista metodológica, mas não possuem uma
implementação concreta no motor atual; sua resposta deve permanecer
inconclusiva, nunca ser interpretada como divergência.

O recorte histórico oferece ainda 36 verificações diretamente conciliáveis sem
MSC: 23 da D3 e 13 da D4. Esse subconjunto está documentado somente para 2025;
o código rejeita sua aplicação silenciosa a outro exercício.

### Complementação do escopo de 2025

Durante a evolução do artefato, 23 regras ausentes foram incorporadas ao motor:

- D2: `D2_00100` a `D2_00104`;
- D3: `D3_00017`, `D3_00026`, `D3_00027`, `D3_00028`, `D3_00030`,
  `D3_00032`, `D3_00033`, `D3_00034`, `D3_00035`, `D3_00037`, `D3_00038`,
  `D3_00039`, `D3_00040`, `D3_00044` e `D3_00047`;
- D4: `D4_00043`, `D4_00046` e `D4_00047`.

Os testes verificam a existência e a chamada das 72 funções de 2025. Isso
comprova cobertura de implementação, mas não valida os dados retornados pela API
nem substitui a conferência metodológica por um especialista.

## Demonstrativos e períodos

| Fonte | Recorte usado no carregamento on-line |
| --- | --- |
| DCA | Anexos anuais necessários às regras. |
| RREO | 6º bimestre e anexos exigidos pelo cruzamento. |
| RGF completo municipal | 3º quadrimestre. |
| RGF simplificado municipal | 2º semestre. |
| MSCC | Matriz corrente de dezembro, `co_tipo_matriz=MSCC`, mês 12. |
| MSCE | Matriz de encerramento, `co_tipo_matriz=MSCE`, mês 12 na API. |

Nem toda regra depende de todas as fontes. A D2 do escopo cruza principalmente
DCA e MSC de encerramento; a D3 combina verificações internas de RREO/RGF e
cruzamentos com a MSC de dezembro; a D4 combina informação contábil e fiscal.

Na exportação em Excel, a MSCE recebe o mês semântico 13 para distinguir o
encerramento da MSCC de dezembro. Essa alteração ocorre em uma cópia destinada
ao arquivo e não modifica os dados usados pelas regras.

## Resultado de uma regra

As regras normalmente retornam:

- um `DataFrame` de uma linha com código, resposta, descrição, nota e observação;
- um `DataFrame` com os valores, filtros ou diferenças usados como evidência.

A resposta original é resumida pelo aplicativo nos seguintes estados:

| Estado | Interpretação |
| --- | --- |
| Conforme | A regra retornou uma conclusão compatível com `OK`. |
| Divergência | A regra retornou `ERRO` ou indicou diferença conclusiva. |
| Dados insuficientes | Demonstrativo, linha ou informação necessária não estava disponível. |
| Não aplicável | A regra não se aplica ao contexto analisado. |
| Falha técnica | A execução falhou ou devolveu uma resposta não reconhecida. |

Somente resultados conformes ou divergentes são conclusivos. Assim:

```text
cobertura conclusiva = (conformes + divergências) / regras esperadas
conformidade observada = conformes / resultados conclusivos
```

Uma cobertura baixa não é uma taxa alta de erros. Da mesma forma, `N/A`, falta
de dados e falha técnica não podem ser convertidos automaticamente em nota zero.

## Igualdade e tolerância

As regras trabalham com valores monetários agregados e, em muitos casos,
adotam tolerância de centavos. Não existe uma tolerância global que possa ser
alterada sem revisar o método: algumas regras possuem condições direcionais ou
tratamentos próprios. A função da regra e seu teste de regressão são a referência
executável para esse detalhe.

## Diagnóstico histórico e cenário contrafactual

O modo histórico usa pontuações preservadas da base anual, não os
demonstrativos que lhes deram origem. Uma não pontuação indica um item a
investigar, mas não comprova a causa.

Para municípios com as cinco entregas essenciais, a tela calcula um limite
máximo de ganho supondo, de forma contrafactual, que todas as não pontuações do
escopo escolhido fossem recuperadas e que as demais regras permanecessem
constantes:

```text
ganho máximo (p.p.) = não pontuações selecionadas / 195 * 100
percentual simulado = min(100, percentual preservado + ganho máximo)
```

O aplicativo adota o denominador 195 e as faixas A ≥ 95%, B ≥ 85%, C ≥ 75%,
D ≥ 65% e E abaixo de 65%. A referência externa exata que fundamenta esses
parâmetros ainda deve ser acrescentada à documentação; aqui eles são descritos
como comportamento verificável do artefato.

O cenário não considera interações entre regras, aceitação de retificação nem
efeito automático na CAPAG.

## Como atualizar uma regra ou um exercício

Uma alteração metodológica deve ser explícita e rastreável:

1. registre o documento, versão, data e trecho que fundamentam a mudança;
2. atualize a lista do exercício em `core/methodology.py`, sem reutilizar
   silenciosamente a lista de outro ano;
3. implemente ou ajuste a função analítica correspondente;
4. preserve o contrato do resumo e da tabela de evidências;
5. crie testes com caso conforme, divergente e sem dados;
6. se houver novo snapshot histórico, atualize metadados, hashes e
   [`../data/README.md`](../data/README.md);
7. execute toda a suíte antes de publicar.

Não se deve inferir vigência futura a partir de um exercício anterior. Um ano
sem referencial cadastrado deve continuar gerando erro explícito.
