# Dados analíticos preservados

Esta pasta contém um recorte mínimo e reproduzível dos dados usados no modo
retrospectivo do aplicativo. Ele não é consultado pelo modo de validação
on-line.

## `ranking_rj_2025.csv`

- Exercício: 2025 (Ranking Siconfi 2026, base anual encerrada).
- Universo: 92 municípios do Rio de Janeiro.
- Escopo preservado: cinco verificações de entrega, 72 verificações de
  cruzamento e os campos oficiais de resultado do ICF.
- Base de origem: `municipios_bspn_base_2025.csv`, preservada no repositório da
  dissertação.
- SHA-256 da origem: `4cf62c7cd0ad963969f334c9c76927064c9807e43f5f772427e61a6722c14f29`.
- SHA-256 deste recorte: `e7cbb20e50f20b6adcacefb24deb9f70960341e293fcdd2fba92af6b04a6e097`.

## `metodologia_cruzamentos_2025.csv`

- Metadados das 72 verificações vigentes para municípios em 2025: 17 da D2,
  28 da D3 e 27 da D4.
- Fonte de origem: captura textual da metodologia oficial de 2025, preservada
  como `metodologia_2025.md` no repositório da dissertação.
- SHA-256 da origem: `b4a6d9fec75338908223f59eee2736b667b945e7253a530f30dda9472fd3c021`.
- SHA-256 deste recorte: `29ed2280f10636c50265729fae13cd32e770d7a8d1bc17f227e006a8a422f5a4`.

O conjunto de 72 verificações não equivale à dimensão D4 oficial. Trata-se da
tipologia funcional de “cruzamento e consistência entre demonstrativos” adotada
na dissertação. O subconjunto sem MSC/matriz contém 36 verificações diretamente
conciliáveis entre DCA, RREO e RGF.
