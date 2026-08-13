# Como contribuir

Contribuições são bem-vindas, especialmente correções metodológicas,
melhorias de legibilidade, testes e documentação. O princípio central do
projeto é manter o motor simples e rastreável sem alterar silenciosamente o
resultado das regras.

## Antes de começar

1. Leia o [README](README.md), a [arquitetura](docs/ARQUITETURA.md) e a
   [metodologia](docs/METODOLOGIA.md).
2. Para uma mudança relevante, abra uma issue descrevendo problema, escopo e
   resultado esperado. Não publique credenciais ou uma vulnerabilidade ainda
   explorável; nesse caso, siga [`SECURITY.md`](SECURITY.md).
3. Crie uma branch curta a partir da versão atual do projeto.
4. Instale o ambiente conforme o README.

## Princípios de código

- Preserve a separação entre coleta, regra de negócio e apresentação.
- Mantenha os cálculos contábeis em `api_ranking/analysis/`; o renderer não
  deve decidir se um valor está correto.
- Prefira funções pequenas, nomes descritivos e fluxos explícitos a abstrações
  genéricas difíceis de auditar.
- Preserve os `DataFrame`s recebidos. Faça uma cópia antes de normalizar sinais,
  colunas ou tipos quando a mutação puder escapar da função.
- Trate ausência de dados, não aplicabilidade e falha técnica separadamente de
  uma divergência.
- Não aplique a metodologia de um exercício a outro por aproximação.
- Concentre mudanças visuais em `assets/theme.css` sempre que não houver
  necessidade de alterar a estrutura da interface.

### Comentários e docstrings

Comente o **porquê**, não a sintaxe evidente. Um bom comentário registra:

- a origem metodológica de um filtro ou agrupamento;
- o significado contábil de uma conta, coluna, sinal ou período;
- por que uma ausência vira `N/A` em vez de `ERRO`;
- por que uma tolerância ou comparação direcional é necessária;
- uma decisão de compatibilidade que pareceria dispensável sem o contexto.

Evite banners decorativos, repetição do nome da variável e comentários sobre
código antigo que já não existe. Funções públicas ou metodologicamente
relevantes devem ter docstring curta com entradas, saídas e ressalvas.

## Alterações em regras

Uma regra de cruzamento normalmente entrega:

1. um resumo com `Dimensão`, `Resposta`, `Descrição da Dimensão`, `Nota` e
   `OBS`;
2. uma tabela de evidências com os valores que permitem reproduzir a conclusão.

Ao incluir ou corrigir uma regra:

- informe código, exercício de vigência e demonstrativos envolvidos;
- cite a fonte e sua versão ou data; se o documento não for público, registre
  essa limitação;
- explique filtros, sinais, agrupamentos e tolerância;
- forneça casos mínimos conforme, divergente e sem dados;
- atualize `core/methodology.py` apenas quando o escopo anual também mudar;
- confirme que nenhuma regra extra aparece no resultado final;
- atualize `docs/METODOLOGIA.md` quando houver mudança de significado ou
  vigência.

## Dados versionados

Não adicione uma exportação bruta grande como atalho para um teste. Prefira um
fixture pequeno, anônimo e suficiente para reproduzir a situação.

Uma alteração em `data/` deve incluir:

- finalidade e esquema do arquivo;
- fonte, data de obtenção e transformações conhecidas;
- hash SHA-256 do arquivo de origem, quando disponível;
- hash SHA-256 do recorte versionado;
- script ou passos determinísticos de geração; se não existirem, a limitação
  deve permanecer explícita;
- condições de licenciamento ou a marcação `pendente` quando não confirmadas.

Atualize também as constantes de integridade que protegem o modo histórico e
[`data/README.md`](data/README.md). Nunca altere um hash apenas para fazer o teste
passar sem revisar conscientemente o novo conteúdo.

## Testes locais

Execute antes de enviar a contribuição:

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py core api_ranking pages tests
git diff --check
```

Os testes automatizados não devem depender da API ao vivo. Modele as entradas
com `DataFrame`s pequenos ou substitua os carregadores no teste. Uma alteração
na integração deve ser acompanhada também por uma verificação manual do fluxo
on-line, sem registrar os dados baixados no repositório.

## Checklist da contribuição

- [ ] A mudança está restrita ao problema descrito.
- [ ] O comportamento preservado ou alterado está explicado.
- [ ] Regras de negócio possuem fonte e vigência identificadas.
- [ ] Ausência de dados não foi transformada em divergência.
- [ ] Testes novos cobrem a correção ou funcionalidade.
- [ ] Toda a suíte e `git diff --check` passam localmente.
- [ ] Documentação e comentários continuam coerentes com o código.
- [ ] Nenhum segredo, ambiente virtual, cache ou arquivo bruto desnecessário foi
  incluído.
