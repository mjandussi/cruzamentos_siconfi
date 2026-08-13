# pyright: reportUndefinedVariable=false
# type: ignore
import streamlit as st

from api_ranking.services.formatting import (
    emoji_por_resposta,
    exibir_status_validacao,
    legenda_capag_na_aba_detalhe,
    mostrar_tabela_formatada,
    titulo_expander_verificacao,
)


def render_tab_d3(tab, ctx):
    globals().update(ctx)
    tab_d3 = tab

    with tab_d3:
        st.markdown("##### D3 - Cruzamento RREO/RGF")
        legenda_capag_na_aba_detalhe()

        # Mostrar aviso se D3 não está disponível
        if not executar_d3:
            st.warning("⚠️ **Dimensão D3 não disponível para este exercício**")
            st.info("""
            Esta dimensão requer o **RREO completo (6º bimestre)** que ainda não foi enviado.

            As verificações D3 analisam a consistência entre RREO e RGF.
            Após o envio do 6º bimestre do RREO, esta dimensão será automaticamente habilitada.
            """)
            st.markdown("---")

        emoji_d3_00001 = emoji_por_resposta(resposta_d3_00001, "D3_00001")
        with st.expander(titulo_expander_verificacao(emoji_d3_00001, "D3_00001", "Resultado Orçamentário (RREO 01)"), expanded=False):
            st.caption("Verifica se o resultado orçamentário foi calculado corretamente no Balanço Orçamentário")
            mostrar_tabela_formatada(d3_00001_t)
            exibir_status_validacao(
                resposta_d3_00001,
                "✅ Resultado orçamentário calculado corretamente",
                "❌ Divergência no cálculo do resultado orçamentário",
                "⏸️ Análise não realizada: a verificação depende do RREO exigido para o exercício."
            )

            st.info("💡 **Explicação:** Compara receitas e despesas (empenhado, liquidado e pago) "
                    "com o superávit/déficit informado no Anexo 01 do RREO.")

        emoji_d3_00002 = emoji_por_resposta(resposta_d3_00002, "D3_00002")
        with st.expander(titulo_expander_verificacao(emoji_d3_00002, "D3_00002", "RREO 01 x RREO 02"), expanded=False):
            st.caption("Verifica a igualdade dos valores de despesa entre RREO Anexo 01 e Anexo 02")
            mostrar_tabela_formatada(d3_00002_t)
            exibir_status_validacao(
                resposta_d3_00002,
                "✅ Valores de despesa consistentes entre os anexos",
                "❌ Diferenças encontradas entre os anexos do RREO",
                "⏸️ Análise não realizada: a verificação depende do RREO exigido para o exercício."
            )

            st.info("💡 **Explicação:** Compara dotações, empenhos, liquidações e RPNP "
                    "entre o Balanço Orçamentário (Anexo 01) e o Demonstrativo da Execução da Despesa "
                    "por Função/Subfunção (Anexo 02).")

        emoji_d3_00005 = emoji_por_resposta(resposta_d3_00005, "D3_00005")
        with st.expander(titulo_expander_verificacao(emoji_d3_00005, "D3_00005", "RCL (RREO 03 x RGF)"), expanded=False):
            st.caption("Verifica a igualdade da Receita Corrente Líquida entre o RREO e o RGF")
            mostrar_tabela_formatada(d3_00005_t)
            exibir_status_validacao(
                resposta_d3_00005,
                "✅ RCL consistente entre RREO e RGF",
                "❌ Diferenças encontradas na RCL entre RREO e RGF",
                "⏸️ Análise não realizada: a verificação depende de RREO e RGF completos."
            )

            st.info("💡 **Explicação:** A Receita Corrente Líquida (RCL) do Anexo 03 do RREO "
                    "deve ser compatível com os anexos 01, 02, 03 e 04 do RGF.")

        emoji_d3_00006 = emoji_por_resposta(resposta_d3_00006, "D3_00006")
        with st.expander(titulo_expander_verificacao(emoji_d3_00006, "D3_00006", "DCL (RREO 06 x RGF 02)"), expanded=False):
            st.caption(
                "Compara a DCL entre **RGF Anexo 02** e **RREO Anexo 06**. "
                "A 3ª linha mostra a **Diferença (RREO − RGF)**."
            )
            mostrar_tabela_formatada(d3_00006_t)
            exibir_status_validacao(
                resposta_d3_00006,
                "✅ DCL consistente entre RREO e RGF",
                "❌ Diferenças encontradas na DCL entre RREO e RGF",
                "⏸️ Análise não realizada: a verificação depende de RREO e RGF completos."
            )

            st.info("💡 **Explicação:** A Dívida Consolidada Líquida do Anexo 06 do RREO "
                    "deve ser compatível com o Anexo 02 do RGF do poder executivo.")

        emoji_d3_00008 = emoji_por_resposta(resposta_d3_00008, "D3_00008")
        with st.expander(titulo_expander_verificacao(emoji_d3_00008, "D3_00008", "RPNP (RREO 01 x RGF 05)"), expanded=False):
            st.caption(
                "Compara o total de RPNP inscrito entre **RGF Anexo 05** e **RREO Anexo 01**. "
                "A 3ª linha mostra a **Diferença (RGF − RREO)**."
            )
            mostrar_tabela_formatada(d3_00008_t)
            exibir_status_validacao(
                resposta_d3_00008,
                "✅ RPNP consistente entre RREO e RGF",
                "❌ Diferenças relevantes nos RPNP entre RREO e RGF",
                "⏸️ Análise não realizada: a verificação depende de RREO e RGF completos.",
                "⚠️ RPNP consistente, com diferença mínima de centavos"
            )

            st.info("💡 **Explicação:** A inscrição de RPNP no RREO Anexo 01 "
                    "deve ser compatível com a soma dos valores do RGF Anexo 05 de todos os poderes.")

        emoji_d3_00009 = emoji_por_resposta(resposta_d3_00009, "D3_00009")
        with st.expander(titulo_expander_verificacao(emoji_d3_00009, "D3_00009", "RPP/RPNP (RREO 07 x RGF 05)"), expanded=False):
            st.caption(
                "Compara os totais entre **RGF Anexo 05** e **RREO Anexo 07** para RPP/RPNP. "
                "A 3ª linha mostra a **Diferença (RGF − RREO)**."
            )
            mostrar_tabela_formatada(d3_00009_t)
            exibir_status_validacao(
                resposta_d3_00009,
                "✅ RPs consistentes entre RREO e RGF",
                "❌ Diferenças relevantes nos RPs entre RREO e RGF",
                "⏸️ Análise não realizada: a verificação depende de RREO e RGF completos.",
                "⚠️ RPs consistentes, com diferença mínima de centavos"
            )

            st.info("💡 **Explicação:** Os valores de RPP e RPNP no RREO Anexo 07 "
                    "devem ser compatíveis com a soma dos valores do RGF Anexo 05 de todos os poderes.")

        emoji_d3_00010 = emoji_por_resposta(resposta_d3_00010, "D3_00010")
        with st.expander(titulo_expander_verificacao(emoji_d3_00010, "D3_00010", "RCL (RGF 01 entre poderes)"), expanded=False):
            st.caption(
                "Mostra o **menor** e o **maior** valor de RCL no RGF Anexo 01 entre os poderes/órgãos "
                "e a 3ª linha com a **Diferença (maior − menor)**."
            )
            mostrar_tabela_formatada(d3_00010_t)
            exibir_status_validacao(
                resposta_d3_00010,
                "✅ RCL consistente entre os poderes/órgãos no RGF 01",
                "❌ Diferenças na RCL entre poderes/órgãos no RGF 01",
                "⏸️ Análise não realizada: a verificação depende do RGF exigido para o exercício."
            )
            st.info("Estados: compara E, L, J, M, D. Municípios: compara E e L.")

        emoji_d3_00011 = emoji_por_resposta(resposta_d3_00011, "D3_00011")
        with st.expander(titulo_expander_verificacao(emoji_d3_00011, "D3_00011", "Dedução Inativos/Pensionistas (RGF 01)"), expanded=False):
            st.caption("Verifica se a dedução de inativos/pensionistas com recursos vinculados é menor ou igual ao valor bruto")
            mostrar_tabela_formatada(d3_00011_t)
            exibir_status_validacao(
                resposta_d3_00011,
                "✅ Dedução de inativos/pensionistas consistente em todos os poderes/órgãos",
                "❌ Dedução de inativos/pensionistas maior que despesa bruta em algum poder/órgão",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info("💡 **Explicação:** A dedução de inativos e pensionistas com recursos vinculados "
                    "não pode ser maior que a despesa bruta com inativos e pensionistas no RGF Anexo 01. "
                    "Estados: E, L, J, M, D. Municípios: E e L.")

        emoji_d3_00012 = emoji_por_resposta(resposta_d3_00012, "D3_00012")
        with st.expander(
            titulo_expander_verificacao(emoji_d3_00012, "D3_00012", "Informação de valores negativos no RREO"),
            expanded=False,
        ):
            st.caption(
                "Verifica se foram informados valores com sinal negativo nos Anexos do **RREO** "
                "(Anexos 01, 02, 03, 04, 04 RPPS, 06, 07 e 09) em campos que não deveriam apresentar "
                "valores negativos. Lista cada linha negativa com **Anexo, cod_conta, conta, coluna e Valor**."
            )
            st.caption(
                "**Iteração inicial:** qualquer valor `< -0,005` em qualquer campo do RREO dispara ERRO. "
                "Conforme forem identificados campos legitimamente negativos (ex.: deduções, retificações), "
                "incluir em `_D3_00012_EXCECOES_NEGATIVO` em `api_ranking/analysis/d3.py` e o ente passa "
                "a marcar OK quando a única ocorrência negativa for permitida."
            )
            mostrar_tabela_formatada(d3_00012_t)
            if resposta_d3_00012 == 'ERRO':
                st.warning(
                    "Há valores negativos no RREO. Confira a tabela acima e, se algum dos campos "
                    "listados puder ser legitimamente negativo, cadastre como exceção em "
                    "`_D3_00012_EXCECOES_NEGATIVO` (chaves opcionais: `anexo`/`anexo_prefixo`/"
                    "`anexo_contem`, `cod_conta`/`cod_conta_prefixo`/`cod_conta_contem`, "
                    "`conta`/`conta_prefixo`/`conta_contem`, `coluna`/`coluna_prefixo`/`coluna_contem`)."
                )
            exibir_status_validacao(
                resposta_d3_00012,
                "✅ Nenhum valor negativo nos Anexos do RREO disponíveis",
                "❌ Há valores negativos no RREO em campos não permitidos",
                "⏸️ Análise não realizada: nenhum Anexo do RREO disponível.",
            )
            st.info(
                "💡 **Explicação:** São varridos os Anexos **01, 02, 03, 04, 04 RPPS, 06, 07 e 09** "
                "do RREO (sempre que disponíveis na API). Para cada Anexo, listamos toda linha com "
                "`valor < -0,005` (tolerância de R$ 0,005). A coluna **OBS** da tabela final inclui "
                "os Anexos efetivamente varridos e a contagem de negativos detectados. Exceções "
                "podem ser cadastradas em `_D3_00012_EXCECOES_NEGATIVO` no módulo de análise."
            )

        emoji_d3_00013 = emoji_por_resposta(resposta_d3_00013, "D3_00013")
        with st.expander(
            titulo_expander_verificacao(emoji_d3_00013, "D3_00013", "Informação de valores negativos no RGF (todos os poderes/órgãos)"),
            expanded=False,
        ):
            st.caption(
                "Verifica se foram informados valores com sinal negativo nos Anexos do **RGF** "
                "**em todos os poderes/órgãos** do ente (Estados/DF: E, L, J, M, D; Municípios: E, L) "
                "em campos que não deveriam apresentar valores negativos. Lista cada linha negativa "
                "com **Anexo, Poder/Órgão, cod_conta, conta, coluna e Valor**."
            )
            st.caption(
                "**Iteração inicial:** qualquer valor `< -0,005` em qualquer combinação Anexo × Poder/Órgão "
                "do RGF dispara ERRO. Conforme forem identificados campos legitimamente negativos "
                "(ex.: deduções, retificações, contas que representam saldo devedor), incluir em "
                "`_D3_00013_EXCECOES_NEGATIVO` em `api_ranking/analysis/d3.py` (com chaves opcionais "
                "`anexo`, `poder`, `cod_conta`, `conta`, `coluna`, `cod_conta_prefixo`, `cod_conta_contem`)."
            )
            mostrar_tabela_formatada(d3_00013_t)
            if resposta_d3_00013 == 'ERRO':
                st.warning(
                    "Há valores negativos no RGF. A coluna **Poder/Órgão** facilita o diagnóstico — "
                    "se o achado se concentrar num poder específico, vale checar primeiro a consistência "
                    "do envio. Campos legitimamente negativos podem ser cadastrados como exceção em "
                    "`_D3_00013_EXCECOES_NEGATIVO`."
                )
            exibir_status_validacao(
                resposta_d3_00013,
                "✅ Nenhum valor negativo nos Anexos do RGF dos poderes/órgãos disponíveis",
                "❌ Há valores negativos no RGF de algum poder/órgão em campos não permitidos",
                "⏸️ Análise não realizada: nenhum Anexo do RGF disponível para os poderes/órgãos do ente.",
            )
            st.info(
                "💡 **Explicação:** São varridos os **Anexos 1 a 5** do RGF em todos os poderes/órgãos "
                "do ente — Estados/DF: **E, L, J, M, D**; Municípios: **E, L**. Para cada combinação "
                "(Anexo × Poder/Órgão), listamos toda linha com `valor < -0,005` (tolerância R$ 0,005). "
                "A coluna **OBS** da tabela final inclui as combinações efetivamente varridas e a "
                "contagem de negativos detectados. Exceções podem ser cadastradas em "
                "`_D3_00013_EXCECOES_NEGATIVO` no módulo de análise."
            )

        emoji_d3_00014 = emoji_por_resposta(resposta_d3_00014, "D3_00014")
        with st.expander(titulo_expander_verificacao(emoji_d3_00014, "D3_00014", "Emendas Individuais (RGF 01-04)"), expanded=False):
            st.caption("Verifica a igualdade do valor das Emendas Individuais entre os anexos 01, 02, 03 e 04 do RGF")
            mostrar_tabela_formatada(d3_00014_t)
            exibir_status_validacao(
                resposta_d3_00014,
                "✅ Emendas Individuais consistentes entre os anexos do RGF",
                "❌ Diferenças encontradas nas Emendas Individuais entre os anexos do RGF",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info("💡 **Explicação:** As Transferências Obrigatórias da União relativas às Emendas Individuais "
                    "devem apresentar valores consistentes entre os anexos 01, 02, 03 e 04 do RGF do poder executivo.")

        emoji_d3_00015 = emoji_por_resposta(resposta_d3_00015, "D3_00015")
        with st.expander(titulo_expander_verificacao(emoji_d3_00015, "D3_00015", "Emendas Individuais (RREO 03 x RGF 01)"), expanded=False):
            st.caption(
                "Compara os totais entre **RGF Anexo 01** e **RREO Anexo 03** para Emendas Individuais. "
                "A 3ª linha mostra a **Diferença (RREO 03 − RGF 01)**."
            )
            mostrar_tabela_formatada(d3_00015_t)
            exibir_status_validacao(
                resposta_d3_00015,
                "✅ Emendas Individuais consistentes entre RREO e RGF",
                "❌ Diferenças encontradas nas Emendas Individuais entre RREO e RGF",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info("💡 **Explicação:** As Transferências Obrigatórias da União relativas às Emendas Individuais "
                    "no Anexo 03 do RREO devem ser compatíveis com os valores do Anexo 01 do RGF do poder executivo.")

        emoji_d3_00016 = emoji_por_resposta(resposta_d3_00016, "D3_00016")
        with st.expander(titulo_expander_verificacao(emoji_d3_00016, "D3_00016", "Emendas de Bancada (RREO 03 x RGF 01)"), expanded=False):
            st.caption(
                "Compara os totais entre **RGF Anexo 01** e **RREO Anexo 03** para Emendas de Bancada. "
                "A 3ª linha mostra a **Diferença (RREO 03 − RGF 01)**."
            )
            mostrar_tabela_formatada(d3_00016_t)
            exibir_status_validacao(
                resposta_d3_00016,
                "✅ Emendas de Bancada consistentes entre RREO e RGF",
                "❌ Diferenças encontradas nas Emendas de Bancada entre RREO e RGF",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info("💡 **Explicação:** As Transferências Obrigatórias da União relativas às Emendas de Bancada "
                    "no Anexo 03 do RREO devem ser compatíveis com os valores do Anexo 01 do RGF do poder executivo.")

        emoji_d3_00017 = emoji_por_resposta(resposta_d3_00017, "D3_00017")
        with st.expander(titulo_expander_verificacao(emoji_d3_00017, "D3_00017", "RP Pagos (RREO 06 x RREO 07)"), expanded=False):
            st.caption(
                "Compara os valores de **RPP pagos** e **RPNP pagos** entre os Anexos 07 e 06 do RREO. "
                "A última linha mostra a diferença (**Anexo 07 − Anexo 06**)."
            )
            mostrar_tabela_formatada(d3_00017_t)
            exibir_status_validacao(
                resposta_d3_00017,
                "✅ RP pagos consistentes entre RREO 06 e RREO 07",
                "❌ Diferenças encontradas nos RP pagos entre RREO 06 e RREO 07",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info("💡 **Explicação:** Os valores de RP processados e não processados pagos no exercício "
                    "devem ser consistentes entre o Anexo 06 e o Anexo 07 do RREO.")

        emoji_d3_00021 = emoji_por_resposta(resposta_d3_00021, "D3_00021")
        with st.expander(titulo_expander_verificacao(emoji_d3_00021, "D3_00021", "Passivo Financeiro >= Restos a Pagar (MSC Dezembro) - CAPAG"), expanded=False):
            st.caption(
                "Verifica se o **Passivo Circulante e Não Circulante Financeiro** (contas iniciadas por **21** e **22** "
                "com `financeiro_permanente = 1`) é **maior ou igual** aos **Restos a Pagar liquidados ou em liquidação** "
                "(contas **6312**, **6313**, **63172**, **6321** e **6327**) — MSC de dezembro, PO Executivo e RPPS."
            )
            mostrar_tabela_formatada(d3_00021_t)
            if resposta_d3_00021 == 'ERRO':
                st.warning(
                    "O Passivo Financeiro (contas 21/22, `financeiro_permanente = 1`) é **menor** que os "
                    "Restos a Pagar liquidados/em liquidação registrados na MSC de dezembro."
                )
            exibir_status_validacao(
                resposta_d3_00021,
                "✅ Passivo Financeiro >= Restos a Pagar liquidados/em liquidação",
                "❌ Passivo Financeiro menor que os Restos a Pagar liquidados/em liquidação",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação (metodologia STN — CAPAG):** O somatório do passivo circulante e não circulante "
                "de natureza **financeira** (contas **21xx** e **22xx**, `financeiro_permanente = 1`) deve ser "
                "**maior ou igual** ao total de restos a pagar liquidados ou em liquidação:\n\n"
                "- **6312** — RP Processados a Liquidar\n"
                "- **6313** — RP Processados a Pagar\n"
                "- **63172** — RP Não-Processados em Liquidação\n"
                "- **6321** — RP Processados em Acompanhamento/Liquidação\n"
                "- **6327** — RP Não-Processados em Acompanhamento\n\n"
                "Filtro de **poder/órgão**: Executivo (`10111`/`10112` para E/DF; `10131`/`10132` para M) "
                "e RPPS (`50511`)."
            )

        emoji_d3_00022 = emoji_por_resposta(resposta_d3_00022, "D3_00022")
        with st.expander(titulo_expander_verificacao(emoji_d3_00022, "D3_00022", "Receitas correntes (MSC x RREO Anexo 1)"), expanded=False):
            st.caption(
                "A tabela mostra os totais por fonte (**MSC** e **RREO Anexo 1**) e uma 3ª linha com a "
                "**Diferença (RREO − MSC)**."
            )
            mostrar_tabela_formatada(d3_00022_t)
            if resposta_d3_00022 == 'ERRO':
                st.warning(
                    "Esta verificação **não aponta qual demonstrativo está incorreto** — só mostra que os **totais não coincidem** "
                    "entre o recorte da MSC e a linha **ReceitasCorrentes** do RREO (Anexo 1). "
                    "Revise escopo (poderes consolidados, refinamentos), período e se o valor do RREO é o do **6º bimestre** alinhado ao seu recorte da MSC."
                )
            exibir_status_validacao(
                resposta_d3_00022,
                "✅ Receitas correntes consistentes entre MSC e RREO",
                "❌ Os totais de receitas correntes divergem entre MSC e RREO (veja valores por fonte na tabela acima).",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info(
                "💡 **Explicação:** Na MSC usa-se `ending_balance` das contas 6212/6213 com natureza iniciando em 1 "
                "(receitas correntes); no RREO, a linha `ReceitasCorrentes` na coluna \"Até o Bimestre (c)\" do Anexo 1."
            )

        emoji_d3_00023 = emoji_por_resposta(resposta_d3_00023, "D3_00023")
        with st.expander(titulo_expander_verificacao(emoji_d3_00023, "D3_00023", "Receitas de capital (MSC x RREO Anexo 1)"), expanded=False):
            st.caption(
                "A tabela mostra os totais por fonte (**MSC** e **RREO Anexo 1**) e uma 3ª linha com a "
                "**Diferença (RREO − MSC)**."
            )
            mostrar_tabela_formatada(d3_00023_t)
            if resposta_d3_00023 == 'ERRO':
                st.warning(
                    "Esta verificação **não aponta qual demonstrativo está incorreto** — só mostra que os **totais não coincidem** "
                    "entre o recorte da MSC e a linha **ReceitasDeCapital** do RREO (Anexo 1). "
                    "Revise escopo, período e alinhamento com o **6º bimestre** do RREO em relação ao recorte da MSC (natureza 2)."
                )
            exibir_status_validacao(
                resposta_d3_00023,
                "✅ Receitas de capital consistentes entre MSC e RREO",
                "❌ Os totais de receitas de capital divergem entre MSC e RREO (veja valores por fonte na tabela acima).",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info(
                "💡 **Explicação:** Na MSC usa-se `ending_balance` das contas 6212/6213 com natureza iniciando em **2** "
                "(receitas de capital); no RREO, a linha `ReceitasDeCapital` na coluna \"Até o Bimestre (c)\" do Anexo 1."
            )

        emoji_d3_00024 = emoji_por_resposta(resposta_d3_00024, "D3_00024")
        with st.expander(titulo_expander_verificacao(emoji_d3_00024, "D3_00024", "Despesas correntes (MSC x RREO Anexo 1)"), expanded=False):
            st.caption(
                "Compara, por bloco, as despesas **empenhadas**, **liquidadas** e **pagas** entre MSC (dezembro) e RREO Anexo 1."
            )
            mostrar_tabela_formatada(d3_00024_t)
            if resposta_d3_00024 == 'ERRO':
                st.warning(
                    "A divergência indica que ao menos um bloco (empenhadas, liquidadas ou pagas) "
                    "não bateu entre MSC e RREO para despesas correntes."
                )
            exibir_status_validacao(
                resposta_d3_00024,
                "✅ Despesas correntes consistentes entre MSC e RREO",
                "❌ Há diferenças nas despesas correntes entre MSC e RREO (veja os blocos na tabela).",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info(
                "💡 **Explicação:** Na MSC (dezembro) somam-se apenas linhas com **tipo_valor = ending_balance** (saldo final), "
                "nas contas 6221301/02/03/04/05/06/07 (empenhada), 6221303/04/07 (liquidada) e 6221304 (paga) — mesmo critério da D4_00025. "
                "No RREO Anexo 1, DespesasCorrentes + DespesasCorrentesIntra nas colunas f/h/j."
            )

        emoji_d3_00025 = emoji_por_resposta(resposta_d3_00025, "D3_00025")
        with st.expander(titulo_expander_verificacao(emoji_d3_00025, "D3_00025", "Despesas de capital (MSC x RREO Anexo 1)"), expanded=False):
            st.caption(
                "Compara, por bloco, as despesas **empenhadas**, **liquidadas** e **pagas** entre MSC (dezembro) e RREO Anexo 1."
            )
            mostrar_tabela_formatada(d3_00025_t)
            if resposta_d3_00025 == 'ERRO':
                st.warning(
                    "A divergência indica que ao menos um bloco (empenhadas, liquidadas ou pagas) "
                    "não bateu entre MSC e RREO para despesas de capital."
                )
            exibir_status_validacao(
                resposta_d3_00025,
                "✅ Despesas de capital consistentes entre MSC e RREO",
                "❌ Há diferenças nas despesas de capital entre MSC e RREO (veja os blocos na tabela).",
                "⏸️ Análise não realizada para este exercício."
            )
            st.info(
                "💡 **Explicação:** Na MSC (dezembro) somam-se apenas linhas com **tipo_valor = ending_balance** (saldo final), "
                "nas contas 6221301/02/03/04/05/06/07 (empenhada), 6221303/04/07 (liquidada) e 6221304 (paga). "
                "No RREO Anexo 1, DespesasDeCapital + DespesasDeCapitalIntra + AmortizacaoRefinanciamentoDaDivida nas colunas f/h/j."
            )

        emoji_d3_00026 = emoji_por_resposta(resposta_d3_00026, "D3_00026")
        with st.expander(titulo_expander_verificacao(emoji_d3_00026, "D3_00026", "Caixa Bruta por grupos de FR (MSC dez x RGF Anexo 5 — Executivo)"), expanded=False):
            st.caption(
                "Compara, por **grupo de Fonte de Recursos** do RGF Anexo 5, o saldo de "
                "**Caixa e Equivalentes de Caixa Bruta**: somatório da MSC de dezembro "
                "(contas iniciadas em 11111/11121/11131, saldo final, **apenas Poder Executivo** — "
                "Direta + Indireta) confrontado com a coluna `DisponibilidadeDeCaixaBruta` do "
                "**RGF Anexo 5 do Executivo**. Demais poderes (Legislativo, Judiciário, MP, Defensoria) "
                "e órgãos como TC e RPPS ficam fora desta verificação."
            )
            st.caption(
                "**Regra:** vigência a partir de **2023** (E/DF/M). OK quando todos os grupos batem (tolerância R$ 0,01); "
                "ERRO quando há divergência em qualquer grupo. Saldos da MSC em fontes não previstas no mapa STN são listados "
                "apenas como diagnóstico — não compõem o critério."
            )
            mostrar_tabela_formatada(d3_00026_t)
            if resposta_d3_00026 == 'ERRO':
                st.warning(
                    "Há divergência entre a soma da MSC (Executivo, por grupo de fonte) e o RGF Anexo 5 do Executivo "
                    "em ao menos um grupo de Fonte de Recursos. A tabela abre, em cada grupo divergente, a quebra MSC "
                    "por `poder_orgao` para identificar a origem da diferença."
                )
            exibir_status_validacao(
                resposta_d3_00026,
                "✅ Caixa e Equivalentes Bruta consistente entre MSC e RGF Anexo 5 (Executivo).",
                "❌ Há diferenças por grupo de fonte entre MSC dez (Executivo) e RGF Anexo 5 (Executivo) — veja a coluna Diferença.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **MSC (dezembro)** — `tipo_valor = ending_balance`, `conta_contabil` em "
                "`11111*`, `11121*` ou `11131*`; `poder_orgao` apenas Executivo (Estados `10111/10112`, "
                "DF `10121/10122`, Municípios `10131/10132`); agrupada pelos **3 últimos dígitos** de "
                "`fonte_recursos` conforme mapa STN. "
                "**RGF Anexo 5 (Executivo)** — `cod_conta = DisponibilidadeDeCaixaBruta`, coluna `conta` em cada linha "
                "detalhada (totais I/II/III e subtotais como *Recursos Vinculados à Educação*, *à Saúde*, "
                "*Demais Vinculações Decorrentes de Transferências* e *Demais Vinculações Legais* ficam de fora)."
            )

        emoji_d3_00027 = emoji_por_resposta(resposta_d3_00027, "D3_00027")
        with st.expander(titulo_expander_verificacao(emoji_d3_00027, "D3_00027", "Despesas: Anexo 1 x Anexo 6 (RREO)"), expanded=False):
            st.caption(
                "Confronta **dotação atualizada**, **despesas empenhadas** e **despesas liquidadas**: "
                "totais do Balanço Orçamentário (Anexo 1) com a soma das rubricas do Anexo 6."
            )
            mostrar_tabela_formatada(d3_00027_t)
            if resposta_d3_00027 == 'ERRO':
                st.warning(
                    "Há diferença entre Anexo 1 e Anexo 6 em ao menos um dos três blocos (dotação, empenhadas ou liquidadas)."
                )
            exibir_status_validacao(
                resposta_d3_00027,
                "✅ Anexos 1 e 6 alinhados para dotação, empenhadas e liquidadas",
                "❌ Divergência entre Anexo 1 e Anexo 6 nas despesas indicadas.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** No Anexo 1 usa-se **TotalDespesas** nas colunas (e), (f) e (h). "
                "No Anexo 6 somam-se as rubricas de despesas correntes/capital (exceto/com RPPS) e reserva de contingência, "
                "nas colunas DOTAÇÃO ATUALIZADA, DESPESAS EMPENHADAS e DESPESAS LIQUIDADAS."
            )

        emoji_d3_00028 = emoji_por_resposta(resposta_d3_00028, "D3_00028")
        with st.expander(titulo_expander_verificacao(emoji_d3_00028, "D3_00028", "Receitas: Anexo 1 x Anexo 6 (RREO)"), expanded=False):
            st.caption(
                "Confronta **receita realizada** e **previsão atualizada**: Anexo 1 (TotalReceitas) x soma das rubricas do Anexo 6."
            )
            mostrar_tabela_formatada(d3_00028_t)
            if resposta_d3_00028 == 'ERRO':
                st.warning(
                    "Há diferença entre Anexo 1 e Anexo 6 em receitas realizadas ou em previsão atualizada."
                )
            exibir_status_validacao(
                resposta_d3_00028,
                "✅ Anexos 1 e 6 alinhados para receitas realizadas e previsão atualizada",
                "❌ Divergência entre Anexo 1 e Anexo 6 nas receitas indicadas.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** No Anexo 1, **TotalReceitas** nas colunas \"Até o Bimestre (c)\" e \"PREVISÃO ATUALIZADA (a)\". "
                "No Anexo 6, soma das rubricas de receitas correntes/capital nas colunas RECEITAS REALIZADAS (a) e PREVISÃO ATUALIZADA."
            )

        emoji_d3_00029 = emoji_por_resposta(resposta_d3_00029, "D3_00029")
        with st.expander(titulo_expander_verificacao(emoji_d3_00029, "D3_00029", "Piso da enfermagem (RGF 1 E × MSC)"), expanded=False):
            st.caption(
                "Compara a **soma das parcelas dedutíveis** no RGF Anexo 1 (Executivo) com **90%** do total MSC "
                "(dezembro, filtros de enfermagem). **OK** se a dedução no RGF não ultrapassa o limite."
            )
            mostrar_tabela_formatada(d3_00029_t)
            if resposta_d3_00029 == 'ERRO':
                st.warning(
                    "A dedução informada no RGF é **maior** que 90% do somatório MSC com os filtros de enfermagem."
                )
            exibir_status_validacao(
                resposta_d3_00029,
                "✅ Dedução do piso da enfermagem dentro do limite (≤ 90% da MSC)",
                "❌ Dedução no RGF acima do limite de 90% em relação à MSC.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** No **RGF 1 (E)** somam-se valores com `cod_conta` começando por **Parcela** na coluna "
                "**TOTAL (ÚLTIMOS 12 MESES) (a)**. Na **MSC** (mês 12, `ending_balance`): contas **6221303–6221307**; "
                "`poder_orgao` **executivo, RPPS e defensoria** (códigos STN, ex.: 10111/10112, 60611 — Estados); "
                "`fonte_recursos` com **últimos 3 dígitos 605** no código de 4 dígitos da fonte (metodologia **605…**); "
                "`natureza_despesa` só com dígitos: **3.1…** (começa em 31), bloco **33xx34xx** ou **33909134 / 33909234**."
            )

        emoji_d3_00030 = emoji_por_resposta(resposta_d3_00030, "D3_00030")
        with st.expander(titulo_expander_verificacao(emoji_d3_00030, "D3_00030", "Receitas previdenciárias (RREO Anexo 4 × Anexo 6)"), expanded=False):
            st.caption(
                "Compara os **totais** de **previsão atualizada** e **receitas realizadas** entre o lado Anexo 4 "
                "(soma do extrato **Anexo 4** e do **Anexo 04 RPPS**, quando existir, com os `cod_conta` de totais RPPS) "
                "e o Anexo 6 (duas rubricas **ComFontesRPPS**), com os nomes de `coluna` fixos da API."
            )
            mostrar_tabela_formatada(d3_00030_t)
            if resposta_d3_00030 == 'ERRO':
                st.warning(
                    "Há diferença entre os totais do Anexo 4 e do Anexo 6 em ao menos uma das duas colunas comparadas."
                )
            exibir_status_validacao(
                resposta_d3_00030,
                "✅ Totais de receitas previdenciárias consistentes entre Anexo 4 e Anexo 6",
                "❌ Divergência nos totais de receitas previdenciárias entre Anexo 4 e Anexo 6.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 4** — soma dos valores com os `cod_conta` de totais RPPS "
                "(incl. contribuições militares) no **Anexo 4** e no **Anexo 04 RPPS** (`4_rpps`), quando houver; "
                "`coluna`: `PREVISÃO ATUALIZADA (a)` e `RECEITAS REALIZADAS ATÉ O BIMESTRE (b)`. "
                "**Anexo 6** — `cod_conta`: `ReceitasPrimariasCorrentesComFontesRPPS`, "
                "`ReceitasNaoPrimariasCorrentesComFontesRPPS`; `coluna`: `PREVISÃO ATUALIZADA` e "
                "`RECEITAS REALIZADAS (a)`."
            )

        emoji_d3_00032 = emoji_por_resposta(resposta_d3_00032, "D3_00032")
        with st.expander(titulo_expander_verificacao(emoji_d3_00032, "D3_00032", "Recursos Arrecadados em Exercícios Anteriores RPPS (RREO Anexos 1, 4 e 6)"), expanded=False):
            st.caption(
                "Compara os **Recursos Arrecadados em Exercícios Anteriores (RPPS)** entre os três anexos do RREO: "
                "Anexo 1 — `PREVISÃO ATUALIZADA (a)` / `RecursosArrecadadosEmExerciciosAnteriores`; "
                "Anexo 4 — `PREVISÃO ORÇAMENTÁRIA` / `RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario`; "
                "Anexo 6 — `PREVISÃO ORÇAMENTÁRIA` / `RREO6SaldoDeExerciciosAnteriores`."
            )
            st.caption(
                "**Regra:** vigência a partir de **2024** (E/DF/M). Os três valores devem ser iguais "
                "(tolerância de R$ 0,01). Qualquer divergência par a par resulta em **ERRO**."
            )
            mostrar_tabela_formatada(d3_00032_t)
            if resposta_d3_00032 == 'ERRO':
                st.warning(
                    "Há divergência nos Recursos Arrecadados em Exercícios Anteriores (RPPS) entre "
                    "ao menos dois dos três anexos do RREO."
                )
            exibir_status_validacao(
                resposta_d3_00032,
                "✅ Recursos Arrecadados em Exercícios Anteriores (RPPS) consistentes entre Anexos 1, 4 e 6",
                "❌ Divergência nos Recursos Arrecadados em Exercícios Anteriores (RPPS) entre os Anexos 1, 4 e 6.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — `cod_conta` **RecursosArrecadadosEmExerciciosAnteriores**, "
                "coluna **PREVISÃO ATUALIZADA (a)**. "
                "**Anexo 4** — `cod_conta` **RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario**, "
                "coluna **PREVISÃO ORÇAMENTÁRIA**. "
                "**Anexo 6** — `cod_conta` **RREO6SaldoDeExerciciosAnteriores**, "
                "coluna **PREVISÃO ORÇAMENTÁRIA**."
            )

        emoji_d3_00033 = emoji_por_resposta(resposta_d3_00033, "D3_00033")
        with st.expander(titulo_expander_verificacao(emoji_d3_00033, "D3_00033", "Superávit financeiro (RREO Anexo 1 × Anexo 6)"), expanded=False):
            st.caption(
                "Compara **SuperavitFinanceiro** na **previsão**: Anexo 1 — `PREVISÃO ATUALIZADA (a)`; "
                "Anexo 6 — `PREVISÃO ORÇAMENTÁRIA`."
            )
            st.caption(
                "**Regra:** vigência a partir de **2024** (E/DF/M). Se **SuperavitFinanceiro** (previsão) não aparecer "
                "em **nenhum** dos dois anexos, o resultado é **OK** (coerência na ausência). "
                "Se aparecer **só em um** dos anexos, é **ERRO**."
            )
            mostrar_tabela_formatada(d3_00033_t)
            if resposta_d3_00033 == 'ERRO':
                st.warning(
                    "Verificação reprovada: valores divergentes entre Anexo 1 e Anexo 6 **ou** "
                    "linha de superávit financeiro (previsão) presente em apenas um dos demonstrativos."
                )
            _obs_33 = None
            if (
                d3_00033 is not None
                and not d3_00033.empty
                and 'OBS' in d3_00033.columns
            ):
                _obs_33 = str(d3_00033['OBS'].iloc[0]).strip() or None
            exibir_status_validacao(
                resposta_d3_00033,
                "✅ Superávit financeiro (previsão) consistente entre Anexo 1 e Anexo 6",
                "❌ Divergência no superávit financeiro (previsão) entre Anexo 1 e Anexo 6.",
                (
                    f"⏸️ {_obs_33}"
                    if _obs_33
                    else (
                        "⏸️ Comparação não realizada: verifique se o RREO Anexo 1 e o Anexo 6 estão completos na extração "
                        "e se existem a linha **SuperavitFinanceiro** com as colunas de previsão indicadas na metodologia."
                    )
                ),
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — `cod_conta` **SuperavitFinanceiro**, coluna **PREVISÃO ATUALIZADA (a)**. "
                "**Anexo 6** — mesmo `cod_conta`, coluna **PREVISÃO ORÇAMENTÁRIA**."
            )

        emoji_d3_00034 = emoji_por_resposta(resposta_d3_00034, "D3_00034")
        with st.expander(titulo_expander_verificacao(emoji_d3_00034, "D3_00034", "Reserva Orçamentária do RPPS Previdenciário (RREO Anexos 1, 4 e 6)"), expanded=False):
            st.caption(
                "Compara a **Reserva Orçamentária do RPPS (Previdenciário)** entre os três anexos do RREO: "
                "Anexo 1 — `DOTAÇÃO ATUALIZADA (e)` / `ReservaDoRPPS`; "
                "Anexo 4 — `PREVISÃO ORÇAMENTÁRIA` / `ReservaOrcamentariaDoRPPSPrevidenciario`; "
                "Anexo 6 — `PREVISÃO ORÇAMENTÁRIA` / `ReservaOrcamentariaDoRPPSPrevidenciario`."
            )
            st.caption(
                "**Regra:** vigência a partir de **2024** (E/DF/M). Os três valores devem ser iguais "
                "(tolerância de R$ 0,01). Qualquer divergência par a par resulta em **ERRO**."
            )
            mostrar_tabela_formatada(d3_00034_t)
            if resposta_d3_00034 == 'ERRO':
                st.warning(
                    "Há divergência na Reserva Orçamentária do RPPS (Previdenciário) entre "
                    "ao menos dois dos três anexos do RREO."
                )
            exibir_status_validacao(
                resposta_d3_00034,
                "✅ Reserva Orçamentária do RPPS (Previdenciário) consistente entre Anexos 1, 4 e 6",
                "❌ Divergência na Reserva Orçamentária do RPPS (Previdenciário) entre os Anexos 1, 4 e 6.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — `cod_conta` **ReservaDoRPPS**, "
                "coluna **DOTAÇÃO ATUALIZADA (e)**. "
                "**Anexo 4** — `cod_conta` **ReservaOrcamentariaDoRPPSPrevidenciario**, "
                "coluna **PREVISÃO ORÇAMENTÁRIA**. "
                "**Anexo 6** — `cod_conta` **ReservaOrcamentariaDoRPPSPrevidenciario**, "
                "coluna **PREVISÃO ORÇAMENTÁRIA**."
            )

        emoji_d3_00035 = emoji_por_resposta(resposta_d3_00035, "D3_00035")
        with st.expander(titulo_expander_verificacao(emoji_d3_00035, "D3_00035", "Reserva de contingência (RREO Anexo 1 × Anexo 6)"), expanded=False):
            st.caption(
                "Compara a **reserva de contingência** na **dotação atualizada**: Anexo 1 — `DOTAÇÃO ATUALIZADA (e)` + "
                "`ReservaDeContingencia`; Anexo 6 — `DOTAÇÃO ATUALIZADA` + `RREO6ReservaDeContingencia`."
            )
            mostrar_tabela_formatada(d3_00035_t)
            if resposta_d3_00035 == 'ERRO':
                st.warning(
                    "Há diferença entre o valor do Anexo 1 e o do Anexo 6 para a reserva de contingência (dotação)."
                )
            exibir_status_validacao(
                resposta_d3_00035,
                "✅ Reserva de contingência (dotação) consistente entre Anexo 1 e Anexo 6",
                "❌ Divergência na reserva de contingência (dotação) entre Anexo 1 e Anexo 6.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — `cod_conta` **ReservaDeContingencia**, coluna **DOTAÇÃO ATUALIZADA (e)**. "
                "**Anexo 6** — `cod_conta` **RREO6ReservaDeContingencia**, coluna **DOTAÇÃO ATUALIZADA**."
            )

        emoji_d3_00037 = emoji_por_resposta(resposta_d3_00037, "D3_00037")
        with st.expander(titulo_expander_verificacao(emoji_d3_00037, "D3_00037", "Investimentos (RREO Anexo 1 × Anexo 9)"), expanded=False):
            st.caption(
                "Compara **Investimentos** (intra + exceto intra) entre o Anexo 1 e o Anexo 9 "
                "nas colunas de dotação atualizada e despesas empenhadas."
            )
            mostrar_tabela_formatada(d3_00037_t)
            if resposta_d3_00037 == 'ERRO':
                st.warning(
                    "Há diferença em investimentos entre os valores do Anexo 1 e do Anexo 9."
                )
            exibir_status_validacao(
                resposta_d3_00037,
                "✅ Investimentos consistentes entre Anexo 1 e Anexo 9",
                "❌ Divergência em investimentos entre Anexo 1 e Anexo 9.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — soma de **Investimentos** + **InvestimentosIntra** "
                "(e contas cujo `cod_conta` comece por `InvestimentosIntra`) nas colunas "
                "**DOTAÇÃO ATUALIZADA (e)** e **DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)**. "
                "**Anexo 9** — apenas **Investimentos** nas colunas "
                "**DOTAÇÃO ATUALIZADA (d)** e **DESPESAS EMPENHADAS (e)**."
            )

        emoji_d3_00038 = emoji_por_resposta(resposta_d3_00038, "D3_00038")
        with st.expander(titulo_expander_verificacao(emoji_d3_00038, "D3_00038", "Inversões Financeiras (RREO Anexo 1 × Anexo 9)"), expanded=False):
            st.caption(
                "Compara **Inversões Financeiras** (intra + exceto intra) entre o Anexo 1 e o Anexo 9 "
                "nas colunas de dotação atualizada e despesas empenhadas."
            )
            mostrar_tabela_formatada(d3_00038_t)
            if resposta_d3_00038 == 'ERRO':
                st.warning(
                    "Há diferença em Inversões Financeiras entre os valores do Anexo 1 e do Anexo 9."
                )
            exibir_status_validacao(
                resposta_d3_00038,
                "✅ Inversões Financeiras consistentes entre Anexo 1 e Anexo 9",
                "❌ Divergência em Inversões Financeiras entre Anexo 1 e Anexo 9.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — soma de **InversoesFinanceiras** + **InversoesFinanceirasIntra** "
                "(e contas cujo `cod_conta` comece por `InversoesFinanceirasIntra`) nas colunas "
                "**DOTAÇÃO ATUALIZADA (e)** e **DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)**. "
                "**Anexo 9** — apenas **InversoesFinanceiras** nas colunas "
                "**DOTAÇÃO ATUALIZADA (d)** e **DESPESAS EMPENHADAS (e)**."
            )

        emoji_d3_00039 = emoji_por_resposta(resposta_d3_00039, "D3_00039")
        with st.expander(titulo_expander_verificacao(emoji_d3_00039, "D3_00039", "Amortização da Dívida (RREO Anexo 1 × Anexo 9)"), expanded=False):
            st.caption(
                "Compara **Amortização da Dívida** (intra + exceto intra) entre o Anexo 1 e o Anexo 9 "
                "nas colunas de dotação atualizada e despesas empenhadas."
            )
            mostrar_tabela_formatada(d3_00039_t)
            if resposta_d3_00039 == 'ERRO':
                st.warning(
                    "Há diferença em Amortização da Dívida entre os valores do Anexo 1 e do Anexo 9."
                )
            exibir_status_validacao(
                resposta_d3_00039,
                "✅ Amortização da Dívida consistente entre Anexo 1 e Anexo 9",
                "❌ Divergência em Amortização da Dívida entre Anexo 1 e Anexo 9.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — soma dos `cod_conta` de amortização da dívida "
                "(ex.: **AmortizacaoDaDivida**, **AmortizacaoRefinanciamentoDaDividaInternaContratual**, "
                "**AmortizacaoDaDividaIntra**) nas colunas **DOTAÇÃO ATUALIZADA (e)** e "
                "**DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)**. "
                "**Anexo 9** — apenas **AmortizacaoDaDivida** nas colunas "
                "**DOTAÇÃO ATUALIZADA (d)** e **DESPESAS EMPENHADAS (e)**."
            )

        emoji_d3_00040 = emoji_por_resposta(resposta_d3_00040, "D3_00040")
        with st.expander(titulo_expander_verificacao(emoji_d3_00040, "D3_00040", "Receitas de Operações de Crédito (RREO Anexo 1 × Anexo 9)"), expanded=False):
            st.caption(
                "Compara **Receitas de Operações de Crédito** entre o Anexo 1 e o Anexo 9. "
                "Se **não** houver linhas desta natureza nos **dois** anexos, o resultado é **OK** "
                "(ente sem esse tipo de receita)."
            )
            mostrar_tabela_formatada(d3_00040_t)
            if resposta_d3_00040 == 'ERRO':
                st.warning(
                    "Há diferença em Receitas de Operações de Crédito entre os valores do Anexo 1 e do Anexo 9."
                )
            exibir_status_validacao(
                resposta_d3_00040,
                "✅ Consistente entre anexos, ou sem receitas de operações de crédito a comparar (OK)",
                "❌ Divergência em Receitas de Operações de Crédito entre Anexo 1 e Anexo 9.",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **Anexo 1** — `cod_conta` **ReceitasDeOperacoesDeCredito** nas colunas "
                "**PREVISÃO ATUALIZADA (a)** e **Até o Bimestre (c)**. "
                "**Anexo 9** — `cod_conta` **RREO9ReceitasDeOperacoesDeCredito** nas colunas "
                "**PREVISÃO ATUALIZADA (a)** e **RECEITAS REALIZADAS (b)**. "
                "Ausência das quatro linhas nos **dois** anexos = **OK**."
            )

        emoji_d3_00044 = emoji_por_resposta(resposta_d3_00044, "D3_00044")
        with st.expander(titulo_expander_verificacao(emoji_d3_00044, "D3_00044", "Transf. União — Agentes Comunitários de Saúde (RREO Anexo 3 × RGF Anexo 1 E)"), expanded=False):
            st.caption(
                "Compara as **Transferências da União relativas à remuneração dos Agentes Comunitários "
                "de Saúde e de Combate às Endemias** (CF, art. 198, §11 — VII) entre o **RREO Anexo 3** "
                "e o **RGF Anexo 1 (Executivo)**. Verificação CAPAG."
            )
            st.caption(
                "**Regra:** vigência a partir de **2024** (E/DF/M). Os dois valores devem ser iguais "
                "(tolerância de R$ 0,01). Qualquer divergência resulta em **ERRO**."
            )
            mostrar_tabela_formatada(d3_00044_t)
            if resposta_d3_00044 == 'ERRO':
                st.warning(
                    "Há divergência nas Transferências da União para Agentes Comunitários de Saúde "
                    "entre o RREO Anexo 3 e o RGF Anexo 1 (Executivo)."
                )
            exibir_status_validacao(
                resposta_d3_00044,
                "✅ Transferências da União para Agentes Comunitários consistentes entre RREO Anexo 3 e RGF Anexo 1 (E)",
                "❌ Divergência nas Transferências da União para Agentes Comunitários entre RREO Anexo 3 e RGF Anexo 1 (E).",
                "⏸️ Análise não realizada para este exercício.",
            )
            st.info(
                "💡 **Explicação:** **RREO Anexo 3** — `cod_conta` "
                "**RREO3TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude**, "
                "coluna **TOTAL (ÚLTIMOS 12 MESES)**. "
                "**RGF Anexo 1 (E)** — `cod_conta` "
                "**TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude**, "
                "coluna **Valor**."
            )

        emoji_d3_00045 = emoji_por_resposta(resposta_d3_00045, "D3_00045")
        with st.expander(titulo_expander_verificacao(emoji_d3_00045, "D3_00045", "Valores negativos em Restos a Pagar (RGF Anexo 5 — Executivo)"), expanded=False):
            st.caption(
                "Verifica se existem **valores negativos** nas colunas de **Restos a Pagar** do "
                "**RGF Anexo 5 (Executivo)**, excluindo as linhas de totais e subtotais (`cod_conta` com 'TOTAL'). "
                "Verificação CAPAG."
            )
            st.caption(
                "**Colunas verificadas** (campo `conta` na API, identificadas pelos sufixos): "
                "**(b)** De Exercícios Anteriores, **(c)** Do Exercício, "
                "**(d)** Restos a Pagar Empenhados e Não Liquidados de Exercícios Anteriores, "
                "**(e)** Demais Obrigações Financeiras. "
                "**Regra:** vigência a partir de **2024** (E/DF/M). "
                "Qualquer valor negativo resulta em **ERRO**."
            )
            mostrar_tabela_formatada(d3_00045_t)
            if resposta_d3_00045 == 'ERRO':
                st.warning(
                    "Há um ou mais valores **negativos** nas colunas de Restos a Pagar do RGF Anexo 5 (Executivo). "
                    "A tabela acima lista todas as linhas com valor negativo identificado."
                )
            exibir_status_validacao(
                resposta_d3_00045,
                "✅ Nenhum valor negativo identificado nas colunas de Restos a Pagar do RGF Anexo 5 (Executivo)",
                "❌ Valor(es) negativo(s) encontrado(s) nas colunas de Restos a Pagar do RGF Anexo 5 (Executivo).",
                "⏸️ RGF Anexo 5 (Executivo) indisponível ou incompleto para este exercício.",
            )
            st.info(
                "💡 **Explicação:** Filtra no **RGF Anexo 5 (Executivo)** as linhas cujo campo `conta` "
                "contém os sufixos **(b)**, **(c)**, **(d)** ou **(e)**, "
                "excluindo `cod_conta` que contenha **TOTAL** (totais e subtotais). "
                "Se qualquer `valor` for **< 0** → **ERRO**. "
                "Se o demonstrativo existe mas nenhuma dessas rubricas está presente, "
                "considera-se que o ente não possui Restos a Pagar nessas colunas → **OK**. "
                "**N/A** ocorre apenas quando o RGF Anexo 5 (Executivo) não está disponível."
            )

        if ano is not None and ano >= 2025:
            st.info(
                "🆕 **Ranking 2025 oficial**\n\n"
                "As verificações homologadas nesta seção são D3_00046 a D3_00055, "
                "conforme metodologia oficial de 2025.",
                icon="ℹ️",
            )

        emoji_d3_00046 = emoji_por_resposta(resposta_d3_00046, "D3_00046")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d3_00046,
                "D3_00046",
                "Despesas de Exercícios Anteriores com pessoal (MSC dez × RGF Anexo 1)"
            ),
            expanded=False
        ):
            st.caption(
                "Verifica a compatibilidade das Despesas de Exercícios Anteriores com gastos com pessoal "
                "registradas na MSC de dezembro com o RGF Anexo 1."
            )
            mostrar_tabela_formatada(d3_00046_t)
            exibir_status_validacao(
                resposta_d3_00046,
                "✅ Despesas de Exercícios Anteriores com pessoal consistentes",
                "❌ Divergência nas Despesas de Exercícios Anteriores com pessoal",
                "⏸️ Pendente de implementação no app conforme metodologia oficial 2025.",
            )
            st.info(
                "💡 **Explicação:** verificação oficial 2025 dependente de regra específica de cruzamento "
                "entre MSC de dezembro e RGF Anexo 1. O app preserva o código oficial e marca N/A "
                "até a implementação do cálculo."
            )

        emoji_d3_00047 = emoji_por_resposta(resposta_d3_00047, "D3_00047")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d3_00047,
                "D3_00047",
                "Reserva Orçamentária do RPPS (RREO Anexo 4 × Anexo 6)"
            ),
            expanded=False
        ):
            st.caption(
                "Verifica a **igualdade** entre o valor da linha **«Valor»** do quadro "
                "**RESERVA ORÇAMENTÁRIA DO RPPS** (Anexo 4) e o valor da linha "
                "**«Reserva Orçamentária do RPPS»** no quadro **Informações Adicionais** (Anexo 6)."
            )
            st.caption(
                "**Regra:** valor do Anexo 4 = valor do Anexo 6 (tolerância de **0,01**). "
                "Diferença → **ERRO**."
            )
            mostrar_tabela_formatada(d3_00047_t)
            if resposta_d3_00047 == 'ERRO':
                st.warning(
                    "Há divergência entre a Reserva Orçamentária do RPPS (Previdenciário) "
                    "informada no Anexo 4 e no Anexo 6 do RREO."
                )
            exibir_status_validacao(
                resposta_d3_00047,
                "✅ Reserva Orçamentária do RPPS consistente entre Anexo 4 e Anexo 6",
                "❌ Diferença entre Anexo 4 e Anexo 6 na Reserva Orçamentária do RPPS",
                "⏸️ RREO Anexo 4 ou Anexo 6 indisponível/incompleto para este ente.",
            )
            st.info(
                "💡 **Explicação:** Em ambos os demonstrativos, filtra `cod_conta` "
                "**ReservaOrcamentariaDoRPPSPrevidenciario** e coluna **PREVISÃO ORÇAMENTÁRIA**. "
                "Ausências parciais (linha ausente em um dos anexos) são tratadas como **zero** "
                "e registradas no campo OBS."
            )

        emoji_d3_00048 = emoji_por_resposta(resposta_d3_00048, "D3_00048")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d3_00048,
                "D3_00048",
                "Inativos indevidos no ASPS (MSC dezembro — CO 1002)"
            ),
            expanded=False
        ):
            st.caption(
                "Verifica se há **naturezas de despesa de inativos/pensionistas** "
                "indevidamente associadas ao **CO 1002 (ASPS)** na MSC de dezembro."
            )
            st.caption(
                "**Regra:** no recorte da execução da despesa (`conta_contabil` iniciando em `62213`, "
                "`tipo_valor` = `ending_balance`, `natureza_despesa` preenchida), "
                "qualquer ocorrência das NDs de inativos/pensionistas com CO 1002 resulta em **ERRO**."
            )
            mostrar_tabela_formatada(d3_00048_t)
            if resposta_d3_00048 == 'ERRO':
                st.warning(
                    "Foram identificadas NDs de inativos/pensionistas no CO 1002 (ASPS) na MSC de dezembro."
                )
            exibir_status_validacao(
                resposta_d3_00048,
                "✅ Não foram encontradas NDs de inativos/pensionistas no CO 1002 (ASPS)",
                "❌ Foram encontradas NDs de inativos/pensionistas no CO 1002 (ASPS)",
                "⏸️ MSC de dezembro indisponível/incompleta para este ente.",
            )
            st.info(
                "💡 **Explicação:** filtra a **MSC de dezembro** com `tipo_valor = ending_balance`, "
                "`conta_contabil` iniciando em `62213`, `complemento_fonte` associado ao **CO 1002** "
                "e `natureza_despesa` preenchida. As NDs de inativos/pensionistas são comparadas sem pontuação."
            )

        emoji_d3_00049 = emoji_por_resposta(resposta_d3_00049, "D3_00049")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d3_00049,
                "D3_00049",
                "Inativos indevidos no MDE (MSC dezembro — CO 1001)"
            ),
            expanded=False
        ):
            st.caption(
                "Verifica se há **naturezas de despesa de inativos/pensionistas** "
                "indevidamente associadas ao **CO 1001 (MDE)** na MSC de dezembro."
            )
            st.caption(
                "**Regra:** no recorte da execução da despesa (`conta_contabil` iniciando em `62213`, "
                "`tipo_valor` = `ending_balance`, `natureza_despesa` preenchida), "
                "qualquer ocorrência das NDs de inativos/pensionistas com CO 1001 resulta em **ERRO**."
            )
            mostrar_tabela_formatada(d3_00049_t)
            if resposta_d3_00049 == 'ERRO':
                st.warning(
                    "Foram identificadas NDs de inativos/pensionistas no CO 1001 (MDE) na MSC de dezembro."
                )
            exibir_status_validacao(
                resposta_d3_00049,
                "✅ Não foram encontradas NDs de inativos/pensionistas no CO 1001 (MDE)",
                "❌ Foram encontradas NDs de inativos/pensionistas no CO 1001 (MDE)",
                "⏸️ MSC de dezembro indisponível/incompleta para este ente.",
            )
            st.info(
                "💡 **Explicação:** filtra a **MSC de dezembro** com `tipo_valor = ending_balance`, "
                "`conta_contabil` iniciando em `62213`, `complemento_fonte` associado ao **CO 1001** "
                "e `natureza_despesa` preenchida. As NDs de inativos/pensionistas são comparadas sem pontuação."
            )

        for codigo, resposta, tabela, titulo in [
            ("D3_00050", resposta_d3_00050, d3_00050_t, "Receitas de impostos (MSC dezembro × SIOPE)"),
            ("D3_00051", resposta_d3_00051, d3_00051_t, "Complementação da União ao Fundeb (MSC dezembro × SIOPE)"),
            ("D3_00052", resposta_d3_00052, d3_00052_t, "Receitas Fundeb decorrentes dos impostos (MSC dezembro × SIOPE)"),
            ("D3_00053", resposta_d3_00053, d3_00053_t, "Transferências de impostos (MSC dezembro × SIOPE)"),
        ]:
            emoji = emoji_por_resposta(resposta, codigo)
            with st.expander(titulo_expander_verificacao(emoji, codigo, titulo), expanded=False):
                st.caption(
                    "Verificação oficial de 2025 que exige cruzamento entre a MSC de dezembro e a base externa SIOPE."
                )
                mostrar_tabela_formatada(tabela)
                exibir_status_validacao(
                    resposta,
                    "✅ Valores consistentes entre MSC e SIOPE",
                    "❌ Divergência entre MSC e SIOPE",
                    "⏸️ Base externa SIOPE não disponível nos endpoints públicos do SICONFI.",
                )
                st.info(
                    "💡 **Explicação:** o código consta na metodologia oficial 2025, mas o cálculo "
                    "depende de dados externos ao SICONFI. O app preserva a verificação como oficial "
                    "e marca N/A até haver integração da fonte externa."
                )

        emoji_d3_00054 = emoji_por_resposta(resposta_d3_00054, "D3_00054")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d3_00054,
                "D3_00054",
                "Qualidade do CO 1002: Função/Fonte (MSC dezembro)"
            ),
            expanded=False
        ):
            st.caption(
                "Verifica se as despesas associadas ao **CO 1002 (ASPS)** estão ligadas "
                "à **Função 10 (Saúde)** ou **Função 28 (Encargos Especiais)** e com "
                "**fontes 500, 502 ou 761** na MSC de dezembro."
            )
            st.caption(
                "**Regra:** no recorte de execução da despesa (`conta_contabil` iniciando em `62213`, "
                "`tipo_valor` = `ending_balance`, `natureza_despesa` preenchida), "
                "qualquer linha com função fora de {10, 28} ou fonte fora de {500, 502, 761} → **ERRO**."
            )
            mostrar_tabela_formatada(d3_00054_t)
            if resposta_d3_00054 == 'ERRO':
                st.warning(
                    "Há inconsistências de função e/ou fonte em despesas com CO 1002 (ASPS) na MSC de dezembro."
                )
            exibir_status_validacao(
                resposta_d3_00054,
                "✅ CO 1002 com função e fonte coerentes na MSC de dezembro",
                "❌ CO 1002 com inconsistência de função e/ou fonte na MSC de dezembro",
                "⏸️ MSC de dezembro indisponível/incompleta para este ente.",
            )
            st.info(
                "💡 **Explicação:** filtra a MSC de dezembro por `complemento_fonte` do **CO 1002** "
                "(normalizado para dígitos), `tipo_valor = ending_balance`, `conta_contabil` iniciando em `62213` "
                "e `natureza_despesa` preenchida. "
                "A função é normalizada para 2 dígitos (`10`/`28`) e a fonte para 3 dígitos "
                "(`500`/`502`/`761`)."
            )

        emoji_d3_00055 = emoji_por_resposta(resposta_d3_00055, "D3_00055")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d3_00055,
                "D3_00055",
                "Qualidade do CO 1001: Função/Fonte (MSC dezembro)"
            ),
            expanded=False
        ):
            st.caption(
                "Verifica se as despesas associadas ao **CO 1001 (MDE)** estão ligadas "
                "à **Função 12 (Educação)** ou **Função 28 (Encargos Especiais)** e com "
                "**fontes 500, 502 ou 761** na MSC de dezembro."
            )
            st.caption(
                "**Regra:** no recorte de execução da despesa (`conta_contabil` iniciando em `62213`, "
                "`tipo_valor` = `ending_balance`, `natureza_despesa` preenchida), "
                "qualquer linha com função fora de {12, 28} ou fonte fora de {500, 502, 761} → **ERRO**."
            )
            mostrar_tabela_formatada(d3_00055_t)
            if resposta_d3_00055 == 'ERRO':
                st.warning(
                    "Há inconsistências de função e/ou fonte em despesas com CO 1001 (MDE) na MSC de dezembro."
                )
            exibir_status_validacao(
                resposta_d3_00055,
                "✅ CO 1001 com função e fonte coerentes na MSC de dezembro",
                "❌ CO 1001 com inconsistência de função e/ou fonte na MSC de dezembro",
                "⏸️ MSC de dezembro indisponível/incompleta para este ente.",
            )
            st.info(
                "💡 **Explicação:** filtra a MSC de dezembro por `complemento_fonte` do **CO 1001** "
                "(normalizado para dígitos), `tipo_valor = ending_balance`, `conta_contabil` iniciando em `62213` "
                "e `natureza_despesa` preenchida. "
                "A função é normalizada para 2 dígitos (`12`/`28`) e a fonte para 3 dígitos "
                "(`500`/`502`/`761`)."
            )

