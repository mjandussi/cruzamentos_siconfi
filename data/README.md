# Dados analíticos preservados e verificáveis

Esta pasta contém os dois recortes usados exclusivamente no diagnóstico
histórico. O modo de validação on-line não usa esses arquivos para calcular os
cruzamentos.

Os recortes são **verificáveis**: o aplicativo confere seus hashes, esquema e
domínio antes de exibi-los. Eles ainda não são plenamente **reproduzíveis** a
partir da fonte, pois o repositório não contém um script de geração nem todos os
metadados externos necessários.

## Inventário

### `ranking_rj_2025.csv`

| Propriedade | Valor registrado |
| --- | --- |
| Finalidade | Diagnóstico retrospectivo e descritivo. |
| Exercício | 2025. |
| Edição adotada pela tela | Ranking Siconfi 2026. |
| Universo | 92 municípios únicos do Rio de Janeiro. |
| Escopo | Cinco verificações de entrega, 72 cruzamentos e campos preservados do ICF. |
| Formato | CSV com separador `;`, decimal `,` e codificação UTF-8 com BOM. |
| Arquivo de origem registrado | `municipios_bspn_base_2025.csv`, no repositório da dissertação. |
| SHA-256 da origem registrado | `4cf62c7cd0ad963969f334c9c76927064c9807e43f5f772427e61a6722c14f29` |
| SHA-256 deste recorte | `e7cbb20e50f20b6adcacefb24deb9f70960341e293fcdd2fba92af6b04a6e097` |

A página histórica também registra `10/05/2026` como data de corte. A URL da
publicação de origem, a data efetiva de download, o commit do repositório da
dissertação e o procedimento que gerou o recorte são **pendências de
proveniência**. O arquivo original não está neste repositório; por isso, seu hash
registrado não pode ser conferido apenas com este checkout.

Antes do uso, o aplicativo verifica:

- o hash do recorte;
- a presença das colunas de ente, exercício, ICF, cinco entregas e 72
  cruzamentos;
- exatamente 92 códigos municipais únicos;
- somente o exercício 2025;
- somente valores `0` ou `1` nas 72 colunas de cruzamento.

### `metodologia_cruzamentos_2025.csv`

| Propriedade | Valor registrado |
| --- | --- |
| Finalidade | Título e relatórios associados aos cruzamentos do modo histórico. |
| Escopo | 72 códigos municipais: 17 D2, 28 D3 e 27 D4. |
| Formato | CSV com separador `;` e codificação UTF-8 com BOM. |
| Colunas obrigatórias | `codigo`, `titulo` e `relatorio`. |
| Origem registrada | Captura `metodologia_2025.md`, no repositório da dissertação. |
| SHA-256 da origem registrado | `b4a6d9fec75338908223f59eee2736b667b945e7253a530f30dda9472fd3c021` |
| SHA-256 deste recorte | `29ed2280f10636c50265729fae13cd32e770d7a8d1bc17f227e006a8a422f5a4` |

O aplicativo exige 72 códigos únicos e igualdade exata com o escopo de 2025
definido em [`../core/methodology.py`](../core/methodology.py).

A URL, versão, data da captura textual e referência bibliográfica oficial que
fundamentam esse arquivo são **pendências de proveniência**. O arquivo original
`metodologia_2025.md` não acompanha este repositório, portanto o hash da origem
também não pode ser recalculado localmente.

## Como verificar os recortes

No Linux ou macOS:

```bash
sha256sum data/ranking_rj_2025.csv data/metodologia_cruzamentos_2025.csv
```

No Windows PowerShell:

```powershell
Get-FileHash .\data\ranking_rj_2025.csv -Algorithm SHA256
Get-FileHash .\data\metodologia_cruzamentos_2025.csv -Algorithm SHA256
```

Os resultados esperados são:

```text
e7cbb20e50f20b6adcacefb24deb9f70960341e293fcdd2fba92af6b04a6e097  ranking_rj_2025.csv
29ed2280f10636c50265729fae13cd32e770d7a8d1bc17f227e006a8a422f5a4  metodologia_cruzamentos_2025.csv
```

A validação de hash confirma que os bytes são os esperados pelo aplicativo;
ela não certifica a correção material da fonte nem a interpretação das regras.

## Interpretação

O conjunto de 72 verificações integra o grupo **cruzamento** da taxonomia final
da dissertação e preserva códigos D2, D3 e D4 do Ranking; esse grupo não
equivale à dimensão D4 oficial. O subconjunto sem MSC contém 36 conciliações,
sendo 23 D3 e 13 D4.

Uma pontuação zero nesse snapshot é tratada como não pontuação ou falha
equivalente a investigar. Sem os demonstrativos de origem, ela não comprova uma
divergência nem identifica qual informação estaria incorreta.

## Limitações de proveniência e reuso

- Não há script versionado que reconstrua os recortes a partir dos arquivos de
  origem.
- Os arquivos de origem e seus repositórios não estão ligados por URL e commit.
- A data de obtenção e as etapas exatas de seleção, renomeação e redução de
  colunas não foram preservadas.
- A licença ou os termos de reutilização das fontes de dados não estão
  documentados e permanecem **pendentes**. A licença MIT do repositório não
  deve ser interpretada automaticamente como licença dos dados de terceiros.
- O snapshot cobre apenas municípios do RJ e o exercício 2025; ele não sustenta
  generalizações automáticas para outros entes ou períodos.

Para tornar o conjunto plenamente reproduzível, uma contribuição futura deve
adicionar as referências externas, a licença aplicável e um script determinístico
que valide o hash da origem e gere os dois arquivos finais.

## Catálogos usados no modo on-line

O CSV em `api_ranking/base_ranking/` tem outra finalidade: fornece a lista
local de municípios para a interface. Ele não alimenta os valores dos
cruzamentos, que vêm da API Siconfi. A origem, a data de atualização e os termos
de reuso desse catálogo também não estão documentados e são **pendências de
proveniência**.
