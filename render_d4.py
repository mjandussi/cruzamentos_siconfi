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


def render_tab_d4(tab, ctx):
    globals().update(ctx)
    tab_d4 = tab

    with tab_d4:
        st.markdown("##### D4 - Cruzamentos RREO, DCA, MSC e RGF")
        legenda_capag_na_aba_detalhe()

        rreo_compl = disponibilidade.get('rreo', {}).get('completo', False)
        dca_disp = disponibilidade.get('dca', {}).get('disponivel', False)

        if not executar_d4:
            st.warning("⚠️ **Dimensão D4 não disponível para este exercício**")
            st.info(
                "Esta dimensão exige **RREO completo (6º bimestre)** com dados na API. "
                "Sem o 6º bimestre, todas as verificações D4 ficam em **N/A**."
            )
        elif rreo_compl and not dca_disp:
            st.info(
                "ℹ️ **Modo parcial (sem DCA):** verificações que cruzam **RREO ou RGF com a DCA** "
                "permanecem em **N/A** até o envio do Balanço Anual; as que usam apenas **MSC×RREO** "
                "ou **RGF×MSC de encerramento** foram calculadas."
            )

        emoji_d4_00001 = emoji_por_resposta(resposta_d4_00001, "D4_00001")
        with st.expander(titulo_expander_verificacao(emoji_d4_00001, "D4_00001", "Receita Realizada (RREO x DCA)"), expanded=False):
            st.caption("Verifica a igualdade da receita realizada entre o RREO Anexo 01 e o Anexo I-C da DCA")
            mostrar_tabela_formatada(d4_00001_t)
            exibir_status_validacao(
                resposta_d4_00001,
                "✅ Receitas realizadas consistentes entre RREO e DCA",
                "❌ Diferença encontrada entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** A receita realizada do Anexo 01 do RREO (6º Bimestre) "
                    "deve ser igual à receita informada no Anexo I-C da DCA.")

        emoji_d4_00002 = emoji_por_resposta(resposta_d4_00002, "D4_00002")
        with st.expander(titulo_expander_verificacao(emoji_d4_00002, "D4_00002", "Execução da Despesa (RREO x DCA)"), expanded=False):
            st.caption("Verifica a igualdade da execução da despesa (Empenhado, Liquidado, Pago e RPNP) entre RREO e DCA")
            mostrar_tabela_formatada(d4_00002_t)
            exibir_status_validacao(
                resposta_d4_00002,
                "✅ Execução da despesa consistente entre RREO e DCA",
                "❌ Diferenças encontradas na execução da despesa entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Os valores de despesas empenhadas, liquidadas, pagas e RPNP "
                    "do Anexo 01 do RREO (6º Bimestre) devem ser iguais aos informados no Anexo I-D da DCA.")

        emoji_d4_00003 = emoji_por_resposta(resposta_d4_00003, "D4_00003")
        with st.expander(titulo_expander_verificacao(emoji_d4_00003, "D4_00003", "Despesa por Função Exceto Intra (RREO 02 x DCA E)"), expanded=False):
            st.caption("Verifica a igualdade da execução da despesa por função (exceto intraorçamentária) entre RREO e DCA")
            mostrar_tabela_formatada(d4_00003_t)
            exibir_status_validacao(
                resposta_d4_00003,
                "✅ Despesas por função (exceto intra) consistentes entre RREO e DCA",
                "❌ Diferenças encontradas nas despesas por função entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Os valores de despesas empenhadas, liquidadas e RPNP (exceto intraorçamentárias) "
                    "do Anexo 02 do RREO (6º Bimestre) devem ser iguais aos informados no Anexo I-E da DCA.")

        emoji_d4_00004 = emoji_por_resposta(resposta_d4_00004, "D4_00004")
        with st.expander(titulo_expander_verificacao(emoji_d4_00004, "D4_00004", "Despesa por Função Intra (RREO 02 x DCA E)"), expanded=False):
            st.caption("Verifica a igualdade da execução da despesa por função (intraorçamentária) entre RREO e DCA")
            # Resetar index para exibição adequada
            d4_00004_t_display = d4_00004_t.reset_index()
            d4_00004_t_display = d4_00004_t_display.rename(columns={'index': 'Dimensão'})
            mostrar_tabela_formatada(d4_00004_t_display)
            exibir_status_validacao(
                resposta_d4_00004,
                "✅ Despesas por função (intra) consistentes entre RREO e DCA",
                "❌ Diferenças encontradas nas despesas intraorçamentárias entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Os valores de despesas empenhadas, liquidadas e RPNP (intraorçamentárias) "
                    "do Anexo 02 do RREO (6º Bimestre) devem ser iguais aos informados no Anexo I-E da DCA.")

        emoji_d4_00005 = emoji_por_resposta(resposta_d4_00005, "D4_00005")
        with st.expander(titulo_expander_verificacao(emoji_d4_00005, "D4_00005", "Restos a Pagar (RREO 07 x DCA F)"), expanded=False):
            st.caption("Verifica a igualdade dos restos a pagar processados e não processados entre RREO Anexo 07 e DCA Anexo I-F")
            mostrar_tabela_formatada(d4_00005_t)
            exibir_status_validacao(
                resposta_d4_00005,
                "✅ Restos a pagar consistentes entre RREO e DCA",
                "❌ Diferenças encontradas nos restos a pagar entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Os valores de restos a pagar processados e não processados (inscritos, pagos, cancelados, etc.) "
                    "do Anexo 07 do RREO devem ser iguais aos informados no Anexo I-F da DCA.")

        emoji_d4_00006 = emoji_por_resposta(resposta_d4_00006, "D4_00006")
        with st.expander(titulo_expander_verificacao(emoji_d4_00006, "D4_00006", "RPNP por Função (RREO 07 x DCA G)"), expanded=False):
            st.caption("Verifica a igualdade dos restos a pagar não processados entre RREO Anexo 07 e DCA Anexo I-G")
            mostrar_tabela_formatada(d4_00006_t)
            exibir_status_validacao(
                resposta_d4_00006,
                "✅ RPNP consistentes entre RREO e DCA",
                "❌ Diferenças encontradas nos RPNP entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Os valores de restos a pagar não processados (inscritos, pagos, cancelados) "
                    "do Anexo 07 do RREO devem ser iguais aos informados no Anexo I-G da DCA.")

        emoji_d4_00007 = emoji_por_resposta(resposta_d4_00007, "D4_00007")
        with st.expander(titulo_expander_verificacao(emoji_d4_00007, "D4_00007", "RPP por Função (RREO 07 x DCA G)"), expanded=False):
            st.caption("Verifica a igualdade dos restos a pagar processados entre RREO Anexo 07 e DCA Anexo I-G")
            mostrar_tabela_formatada(d4_00007_t)
            exibir_status_validacao(
                resposta_d4_00007,
                "✅ RPP consistentes entre RREO e DCA",
                "❌ Diferenças encontradas nos RPP entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Os valores de restos a pagar processados (inscritos, pagos, cancelados) "
                    "do Anexo 07 do RREO devem ser iguais aos informados no Anexo I-G da DCA.")

        # D4_00009 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00009 = emoji_por_resposta(resposta_d4_00009, "D4_00009")
            with st.expander(titulo_expander_verificacao(emoji_d4_00009, "D4_00009", "Receita de Impostos Estaduais (RREO 03 x DCA C)"), expanded=False):
                st.caption("Verifica a igualdade das receitas de impostos estaduais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00009_t)
                exibir_status_validacao(
                    resposta_d4_00009,
                    "✅ Receitas de impostos estaduais consistentes entre RREO e DCA",
                    "❌ Diferenças encontradas nas receitas de impostos estaduais entre RREO e DCA",
                    "⏸️ Análise não realizada: a verificação depende da DCA."
                )

                st.info("💡 **Explicação:** Os valores de receitas de impostos (ICMS, IPVA, ITCD, IRRF) "
                        "do Anexo 03 do RREO (RCL) devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00010 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00010 = emoji_por_resposta(resposta_d4_00010, "D4_00010")
            with st.expander(titulo_expander_verificacao(emoji_d4_00010, "D4_00010", "Receita de Impostos Municipais (RREO 03 x DCA C)"), expanded=False):
                st.caption("Verifica a igualdade das receitas de impostos municipais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00010_t)
                exibir_status_validacao(
                    resposta_d4_00010,
                    "✅ Receitas de impostos municipais consistentes entre RREO e DCA",
                    "❌ Diferenças encontradas nas receitas de impostos municipais entre RREO e DCA",
                    "⏸️ Análise não realizada: a verificação depende da DCA."
                )

                st.info("💡 **Explicação:** Os valores de receitas de impostos (IPTU, ISS, ITBI, IRRF) "
                        "do Anexo 03 do RREO (RCL) devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00011 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00011 = emoji_por_resposta(resposta_d4_00011, "D4_00011")
            with st.expander(titulo_expander_verificacao(emoji_d4_00011, "D4_00011", "Transferências Estaduais (RREO 03 x DCA C)"), expanded=False):
                st.caption("Verifica a igualdade das transferências constitucionais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00011_t)
                exibir_status_validacao(
                    resposta_d4_00011,
                    "✅ Transferências estaduais consistentes entre RREO e DCA",
                    "❌ Diferenças encontradas nas transferências estaduais entre RREO e DCA",
                    "⏸️ Análise não realizada: a verificação depende da DCA."
                )

                st.info("💡 **Explicação:** Os valores de transferências constitucionais (FPE e FUNDEB) "
                        "do Anexo 03 do RREO devem ser iguais aos informados no Anexo I-C da DCA.")

        # D4_00012 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00012 = emoji_por_resposta(resposta_d4_00012, "D4_00012")
            with st.expander(titulo_expander_verificacao(emoji_d4_00012, "D4_00012", "Transferências Municipais (RREO 03 x DCA C)"), expanded=False):
                st.caption("Verifica a igualdade das transferências municipais entre RREO Anexo 03 e DCA Anexo I-C")
                mostrar_tabela_formatada(d4_00012_t)
                exibir_status_validacao(
                    resposta_d4_00012,
                    "✅ Transferências municipais consistentes entre RREO e DCA",
                    "❌ Diferenças encontradas nas transferências municipais entre RREO e DCA",
                    "⏸️ Análise não realizada: a verificação depende da DCA."
                )

                st.info("💡 **Explicação:** Os valores de transferências municipais (FPM, ICMS, IPVA, ITR, FUNDEB) "
                        "do Anexo 03 do RREO devem ser iguais aos informados no Anexo I-C da DCA.")

        
        emoji_d4_00017 = emoji_por_resposta(resposta_d4_00017, "D4_00017")
        with st.expander(titulo_expander_verificacao(emoji_d4_00017, "D4_00017", "Contribuições e Compensações (RREO 03 x DCA C)"), expanded=False):
            st.caption("Igualdade das contribuições dos servidores e compensações financeiras entre RREO e DCA")
            mostrar_tabela_formatada(d4_00017_t)
            exibir_status_validacao(
                resposta_d4_00017,
                "✅ Contribuições e compensações consistentes entre RREO e DCA",
                "❌ Diferenças encontradas entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Compara contribuições dos servidores (RO1.2.1.5.00.0.0) e "
                    "compensações financeiras (RO1.9.9.9.03.0.0) com o RREO 03.")

        emoji_d4_00019 = emoji_por_resposta(resposta_d4_00019, "D4_00019")
        with st.expander(titulo_expander_verificacao(emoji_d4_00019, "D4_00019", "Despesas de Capital (RREO 09 x DCA D)"), expanded=False):
            st.caption("Igualdade do valor das despesas de capital entre RREO 09 e DCA D")
            mostrar_tabela_formatada(d4_00019_t)
            exibir_status_validacao(
                resposta_d4_00019,
                "✅ Despesas de capital consistentes entre RREO e DCA",
                "❌ Diferenças encontradas nas despesas de capital entre RREO e DCA",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** Compara despesas de capital do RREO 09 com DCA D (DO4.0.00.00.00.00).")

        emoji_d4_00020 = emoji_por_resposta(resposta_d4_00020, "D4_00020")
        with st.expander(titulo_expander_verificacao(emoji_d4_00020, "D4_00020", "Receita Arrecadada (MSC Dez x RREO 01)"), expanded=False):
            st.caption("Igualdade nas receitas arrecadadas entre MSC de dezembro e RREO 01")
            mostrar_tabela_formatada(d4_00020_t)

            if resposta_d4_00020 == 'OK':
                st.success("✅ Receitas arrecadadas consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas nas receitas arrecadadas entre MSC e RREO")

            st.info("💡 **Explicação:** Compara MSC dezembro (contas 6212/6213/62139) com RREO 01 (TotalReceitas).")


        # D4_00021 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00021 = emoji_por_resposta(resposta_d4_00021, "D4_00021")
            with st.expander(titulo_expander_verificacao(emoji_d4_00021, "D4_00021", "Tributos Estaduais (MSC Dez x RREO 03)"), expanded=False):
                st.caption("Igualdade nas receitas com tributos estaduais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00021_t)

                if resposta_d4_00021 == 'OK':
                    st.success("✅ Receitas com tributos estaduais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas receitas com tributos estaduais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara ICMS, IPVA, ITCD e IRRF no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro.")

        # D4_00022 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00022 = emoji_por_resposta(resposta_d4_00022, "D4_00022")
            with st.expander(titulo_expander_verificacao(emoji_d4_00022, "D4_00022", "Tributos Municipais (MSC Dez x RREO 03)"), expanded=False):
                st.caption("Igualdade nas receitas com tributos municipais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00022_t)

                if resposta_d4_00022 == 'OK':
                    st.success("✅ Receitas com tributos municipais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas receitas com tributos municipais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara IPTU, ISS, ITBI e IRRF no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro.")

        # D4_00023 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00023 = emoji_por_resposta(resposta_d4_00023, "D4_00023")
            with st.expander(titulo_expander_verificacao(emoji_d4_00023, "D4_00023", "Transferências Constitucionais (MSC Dez x RREO 03)"), expanded=False):
                st.caption("Igualdade nas transferências constitucionais estaduais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00023_t)

                if resposta_d4_00023 == 'OK':
                    st.success("✅ Transferências constitucionais estaduais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas transferências constitucionais estaduais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara FPE e FUNDEB no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro (inclui complemento FUNDEB).")

        # D4_00024 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00024 = emoji_por_resposta(resposta_d4_00024, "D4_00024")
            with st.expander(titulo_expander_verificacao(emoji_d4_00024, "D4_00024", "Transferências Constitucionais (MSC Dez x RREO 03)"), expanded=False):
                st.caption("Igualdade nas transferências constitucionais municipais entre MSC de dezembro e RREO Anexo 03")
                mostrar_tabela_formatada(d4_00024_t)

                if resposta_d4_00024 == 'OK':
                    st.success("✅ Transferências constitucionais municipais consistentes entre MSC e RREO")
                else:
                    st.error("❌ Diferenças encontradas nas transferências constitucionais municipais entre MSC e RREO")

                st.info("💡 **Explicação:** Compara FPM, ICMS, IPVA, ITR e FUNDEB no RREO 03 com as naturezas de receita "
                        "equivalentes no MSC de dezembro.")

        emoji_d4_00025 = emoji_por_resposta(resposta_d4_00025, "D4_00025")
        with st.expander(titulo_expander_verificacao(emoji_d4_00025, "D4_00025", "Despesa Emp/Liq/Pago (MSC Dez x RREO 01)"), expanded=False):
            st.caption("Igualdade das despesas empenhadas, liquidadas e pagas entre MSC de dezembro e RREO 01")
            mostrar_tabela_formatada(d4_00025_t)

            if resposta_d4_00025 == 'OK':
                st.success("✅ Despesas Emp/Liq/Pago consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas nas despesas Emp/Liq/Pago entre MSC e RREO")

            st.info("💡 **Explicação:** Compara despesas empenhadas, liquidadas e pagas do RREO 01 "
                    "com contas 6221305/6221306/6221307/6221304 no MSC de dezembro.")

        emoji_d4_00026 = emoji_por_resposta(resposta_d4_00026, "D4_00026")
        with st.expander(titulo_expander_verificacao(emoji_d4_00026, "D4_00026", "Inscrição RPNP (MSC Dez x RREO 01)"), expanded=False):
            st.caption("Igualdade dos Restos a Pagar Não Processados entre MSC de dezembro e RREO 01")
            mostrar_tabela_formatada(d4_00026_t)

            if resposta_d4_00026 == 'OK':
                st.success("✅ RPNP consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas nos RPNP entre MSC e RREO")

            st.info("💡 **Explicação:** Compara inscrição de RPNP do RREO 01 com contas 6221305/6221306 no MSC de dezembro.")

        emoji_d4_00027 = emoji_por_resposta(resposta_d4_00027, "D4_00027")
        with st.expander(titulo_expander_verificacao(emoji_d4_00027, "D4_00027", "Disponibilidade de Caixa (RGF 2 x DCA AB)"), expanded=False):
            st.caption("Disponibilidade de Caixa Bruta do RGF 2 deve ser menor ou igual a Caixa e Equivalentes (DCA AB)")
            mostrar_tabela_formatada(d4_00027_t)
            exibir_status_validacao(
                resposta_d4_00027,
                "✅ Disponibilidade de Caixa Bruta (RGF 2) <= Caixa e Equivalentes (DCA)",
                "❌ Disponibilidade de Caixa Bruta (RGF 2) maior que Caixa e Equivalentes (DCA)",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF Anexo 2 deve ser "
                    "menor ou igual à Caixa e Equivalentes (1.1.1.0.0.00.00) da DCA AB.")

        emoji_d4_00028 = emoji_por_resposta(resposta_d4_00028, "D4_00028")
        with st.expander(titulo_expander_verificacao(emoji_d4_00028, "D4_00028", "Disponibilidade de Caixa (RGF 5 x DCA AB)"), expanded=False):
            st.caption("Disponibilidade de Caixa Bruta do RGF 5 deve ser menor ou igual a Caixa e Equivalentes (DCA AB)")
            mostrar_tabela_formatada(d4_00028_t)
            exibir_status_validacao(
                resposta_d4_00028,
                "✅ Disponibilidade de Caixa Bruta (RGF 5) <= Caixa e Equivalentes (DCA)",
                "❌ Disponibilidade de Caixa Bruta (RGF 5) maior que Caixa e Equivalentes (DCA)",
                "⏸️ Análise não realizada: a verificação depende da DCA."
            )

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF Anexo 5 deve ser "
                    "menor ou igual à Caixa e Equivalentes (1.1.1.0.0.00.00) da DCA AB.")

        emoji_d4_00029 = emoji_por_resposta(resposta_d4_00029, "D4_00029")
        with st.expander(titulo_expander_verificacao(emoji_d4_00029, "D4_00029", "Previdência Social (RREO 02 x MSC Dez)"), expanded=False):
            st.caption("Igualdade das despesas de Previdência Social entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00029_t)

            if resposta_d4_00029 == 'OK':
                st.success("✅ Previdência Social consistente entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas em Previdência Social entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas da função 09 no RREO 02 com o MSC de dezembro.")

        emoji_d4_00030 = emoji_por_resposta(resposta_d4_00030, "D4_00030")
        with st.expander(titulo_expander_verificacao(emoji_d4_00030, "D4_00030", "Saúde (RREO 02 x MSC Dez)"), expanded=False):
            st.caption("Igualdade das despesas de Saúde entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00030_t)

            if resposta_d4_00030 == 'OK':
                st.success("✅ Saúde consistente entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas em Saúde entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas da função 10 no RREO 02 com o MSC de dezembro.")

        emoji_d4_00031 = emoji_por_resposta(resposta_d4_00031, "D4_00031")
        with st.expander(titulo_expander_verificacao(emoji_d4_00031, "D4_00031", "Educação (RREO 02 x MSC Dez)"), expanded=False):
            st.caption("Igualdade das despesas de Educação entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00031_t)

            if resposta_d4_00031 == 'OK':
                st.success("✅ Educação consistente entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas em Educação entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas da função 12 no RREO 02 com o MSC de dezembro.")

        emoji_d4_00032 = emoji_por_resposta(resposta_d4_00032, "D4_00032")
        with st.expander(titulo_expander_verificacao(emoji_d4_00032, "D4_00032", "Demais Funções (RREO 02 x MSC Dez)"), expanded=False):
            st.caption("Igualdade das despesas das demais funções entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00032_t)

            if resposta_d4_00032 == 'OK':
                st.success("✅ Demais funções consistentes entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas nas demais funções entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas empenhadas das demais funções no RREO 02 com o MSC de dezembro.")

        emoji_d4_00033 = emoji_por_resposta(resposta_d4_00033, "D4_00033")
        with st.expander(titulo_expander_verificacao(emoji_d4_00033, "D4_00033", "Despesas Intra (RREO 02 x MSC Dez)"), expanded=False):
            st.caption("Igualdade das despesas intraorçamentárias entre RREO 02 e MSC de dezembro")
            mostrar_tabela_formatada(d4_00033_t)

            if resposta_d4_00033 == 'OK':
                st.success("✅ Despesas intra consistentes entre RREO e MSC")
            else:
                st.error("❌ Diferenças encontradas nas despesas intra entre RREO e MSC")

            st.info("💡 **Explicação:** Compara despesas intra do RREO 02 com MSC de dezembro (DIGITO_INTRA == 91).")

        emoji_d4_00034 = emoji_por_resposta(resposta_d4_00034, "D4_00034")
        with st.expander(titulo_expander_verificacao(emoji_d4_00034, "D4_00034", "RPP/RPNP Pagos (MSC Dez x RREO 07)"), expanded=False):
            st.caption(
                "Compara os totais de **RPP pagos** e **RPNP pagos** entre **MSC Dezembro** e **RREO Anexo 07**. "
                "A 3ª linha mostra a **Diferença (RREO − MSC)**."
            )
            mostrar_tabela_formatada(d4_00034_t)

            if resposta_d4_00034 == 'OK':
                st.success("✅ RPP/RPNP pagos consistentes entre MSC e RREO")
            else:
                st.error("❌ Diferenças encontradas em RPP/RPNP pagos entre MSC e RREO")

            st.info("💡 **Explicação:** Compara contas 631400000/632200000 (MSC Dez) com RREO 07 (pagos).")

        emoji_d4_00035 = emoji_por_resposta(resposta_d4_00035, "D4_00035")
        with st.expander(titulo_expander_verificacao(emoji_d4_00035, "D4_00035", "Caixa (RGF 5 x MSC Encerr.)"), expanded=False):
            st.caption(
                "Compara **Caixa e Equivalentes (MSC Encerramento)** com **Disponibilidade de Caixa Bruta (RGF Anexo 05)**. "
                "A 3ª linha mostra a **Diferença (RGF − MSC)**."
            )
            mostrar_tabela_formatada(d4_00035_t)

            if resposta_d4_00035 == 'OK':
                st.success("✅ Caixa RGF 5 <= Caixa MSC Encerramento")
            else:
                st.error("❌ Caixa RGF 5 maior que Caixa MSC Encerramento")

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF 5 deve ser "
                    "menor ou igual à Caixa e Equivalentes da MSC de Encerramento.")

        emoji_d4_00036 = emoji_por_resposta(resposta_d4_00036, "D4_00036")
        with st.expander(titulo_expander_verificacao(emoji_d4_00036, "D4_00036", "Caixa (RGF 2 x MSC Encerr.)"), expanded=False):
            st.caption(
                "Compara **Caixa e Equivalentes (MSC Encerramento)** com **Disponibilidade de Caixa Bruta (RGF Anexo 02)**. "
                "A 3ª linha mostra a **Diferença (RGF − MSC)**."
            )
            mostrar_tabela_formatada(d4_00036_t)

            if resposta_d4_00036 == 'OK':
                st.success("✅ Caixa RGF 2 <= Caixa MSC Encerramento")
            else:
                st.error("❌ Caixa RGF 2 maior que Caixa MSC Encerramento")

            st.info("💡 **Explicação:** A Disponibilidade de Caixa Bruta do RGF 2 deve ser "
                    "menor ou igual à Caixa e Equivalentes da MSC de Encerramento.")

        # D4_00037 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00037 = emoji_por_resposta(resposta_d4_00037, "D4_00037")
            with st.expander(titulo_expander_verificacao(emoji_d4_00037, "D4_00037", "Tributos Estaduais (RREO 06 x MSC)"), expanded=False):
                st.caption("Igualdade das receitas com tributos estaduais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00037_t)

                if resposta_d4_00037 == 'OK':
                    st.success("✅ Tributos estaduais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nos tributos estaduais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara ICMS, IPVA, ITCD e IRRF do RREO 06 "
                        "com as naturezas equivalentes no MSC.")

        # D4_00038 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00038 = emoji_por_resposta(resposta_d4_00038, "D4_00038")
            with st.expander(titulo_expander_verificacao(emoji_d4_00038, "D4_00038", "Tributos Municipais (RREO 06 x MSC)"), expanded=False):
                st.caption("Igualdade das receitas com tributos municipais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00038_t)

                if resposta_d4_00038 == 'OK':
                    st.success("✅ Tributos municipais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nos tributos municipais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara IPTU, ISS, ITBI e IRRF do RREO 06 "
                        "com as naturezas equivalentes no MSC.")

        # D4_00039 - Apenas para Estados
        if tipo_ente == "E":
            emoji_d4_00039 = emoji_por_resposta(resposta_d4_00039, "D4_00039")
            with st.expander(titulo_expander_verificacao(emoji_d4_00039, "D4_00039", "Transferências Estaduais (RREO 06 x MSC)"), expanded=False):
                st.caption("Igualdade nas transferências constitucionais estaduais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00039_t)

                if resposta_d4_00039 == 'OK':
                    st.success("✅ Transferências estaduais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nas transferências estaduais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara FPE e FUNDEB do RREO 06 com as naturezas equivalentes no MSC.")

        # D4_00040 - Apenas para Municípios
        if tipo_ente == "M":
            emoji_d4_00040 = emoji_por_resposta(resposta_d4_00040, "D4_00040")
            with st.expander(titulo_expander_verificacao(emoji_d4_00040, "D4_00040", "Transferências Municipais (RREO 06 x MSC)"), expanded=False):
                st.caption("Igualdade nas transferências constitucionais municipais entre RREO 06 e MSC")
                mostrar_tabela_formatada(d4_00040_t)

                if resposta_d4_00040 == 'OK':
                    st.success("✅ Transferências municipais consistentes entre RREO e MSC")
                else:
                    st.error("❌ Diferenças encontradas nas transferências municipais entre RREO e MSC")

                st.info("💡 **Explicação:** Compara FPM, ICMS, IPVA, ITR e FUNDEB do RREO 06 com as naturezas equivalentes no MSC.")

        emoji_d4_00041 = emoji_por_resposta(resposta_d4_00041, "D4_00041")
        with st.expander(titulo_expander_verificacao(emoji_d4_00041, "D4_00041", "Passivo Financeiro (DCA AB x MSC Dez)"), expanded=False):
            st.caption(
                "Verifica se o **PassivoFinanceiro** da DCA AB é **maior ou igual** à soma de "
                "restos a pagar inscritos no exercício e pendentes de pagamento na MSC de dezembro."
            )
            mostrar_tabela_formatada(d4_00041_t)

            if resposta_d4_00041 == 'OK':
                st.success("✅ Passivo Financeiro (DCA AB) cobre os RP inscritos + pendentes (MSC Dez)")
            elif resposta_d4_00041 == 'ERRO':
                st.error("❌ Passivo Financeiro (DCA AB) menor que os RP inscritos + pendentes (MSC Dez)")

            st.info(
                "💡 **Explicação:** **DCA AB** — `cod_conta` **PassivoFinanceiro**. "
                "**MSC Dezembro (ending_balance)** — contas `conta_contabil` iniciando em "
                "`6311`, `6312`, `6313`, `6317`, `6321` e `6327`."
            )

        emoji_d4_00042 = emoji_por_resposta(resposta_d4_00042, "D4_00042")
        with st.expander(
            titulo_expander_verificacao(emoji_d4_00042, "D4_00042", "Demais obrigações financeiras (RGF 5 Exec.) x valores restituíveis (MSC Dez)"),
            expanded=False,
        ):
            st.caption(
                "Verifica se o **TOTAL (IV)** de **Demais obrigações financeiras** no **RGF Anexo 5 (Executivo)** "
                "é **maior ou igual** à soma do **saldo final** na **MSC de dezembro** das contas indicadas, "
                "no **Poder Executivo**, com fontes de recurso **860, 861, 862 e 869**."
            )
            mostrar_tabela_formatada(d4_00042_t)
            exibir_status_validacao(
                resposta_d4_00042,
                "✅ Valor do RGF cobre o montante apurado na MSC (CAPAG), com totais não negativos",
                "❌ RGF menor que o montante MSC **ou** total negativo no RGF ou na MSC (inconsistente com a regra CAPAG)",
                "⏸️ Análise não realizada: faltam dados de RGF 5 (Executivo) ou MSC de dezembro, ou linha não localizada.",
            )
            st.info(
                "💡 **Explicação:** **RGF** — `cod_conta` **DemaisObrigacoesFinanceiras** e `conta` "
                "**TOTAL (IV) = (I + II + III)**. **MSC** — `ending_balance`, `poder_orgao` Executivo, "
                "últimos 3 dígitos da fonte em **860–862** e **869**, contas **2188***, **2288***, "
                "**218910105** e **218910108**. **Regra extra:** se o total do RGF ou o total MSC "
                "apurado for **negativo**, a dimensão fica em **ERRO** (não basta RGF ≥ MSC)."
            )

        emoji_d4_00043 = emoji_por_resposta(resposta_d4_00043, "D4_00043")
        with st.expander(
            titulo_expander_verificacao(emoji_d4_00043, "D4_00043", "Recursos Não Vinculados — Disp. Caixa Bruta + RPs (MSC Dez x RGF 5 Executivo)"),
            expanded=False,
        ):
            st.caption(
                "Compara, em **2 linhas (FR) × 4 colunas (tipos de saldo) = 8 células**, "
                "os Recursos Não Vinculados entre a **MSC de dezembro** (saldo final) e o "
                "**RGF Anexo 5 do Executivo**. Linhas: *Recursos Não Vinculados de Impostos* "
                "(FR 500) e *Outros Recursos não Vinculados* (FR 501, 502, 503). Colunas: "
                "*Disponibilidade de Caixa Bruta*, *RP Liquidados e Não Pagos de Exerc. Anteriores*, "
                "*RP Liquidados e Não Pagos do Exercício* e *RP Empenhados e Não Liq. de Exerc. Anteriores*."
            )
            st.caption(
                "**Regra:** vigência a partir de **2024** (E/DF/M). OK quando todas as 8 células batem (tolerância R$ 0,01); "
                "ERRO quando há divergência em qualquer célula. A tabela abre, em cada célula divergente, a quebra MSC "
                "por `poder_orgao` para identificar a origem da diferença (Direta vs Indireta do Executivo)."
            )
            mostrar_tabela_formatada(d4_00043_t)
            if resposta_d4_00043 == 'ERRO':
                st.warning(
                    "Há diferença entre a MSC (Executivo) e o RGF Anexo 5 do Executivo em ao menos uma das 8 "
                    "células (linha × coluna). Veja a coluna Diferença e, abaixo de cada célula divergente, a "
                    "quebra MSC por `poder_orgao`."
                )
            exibir_status_validacao(
                resposta_d4_00043,
                "✅ MSC e RGF Anexo 5 (Executivo) consistentes em todas as 8 combinações de FR × tipo de saldo.",
                "❌ Há diferenças entre MSC dez (Executivo) e RGF Anexo 5 (Executivo) — veja a coluna Diferença.",
                "⏸️ Análise não realizada: faltam dados de RGF 5 (Executivo) ou MSC de dezembro.",
            )
            st.info(
                "💡 **Explicação:** **MSC (dezembro)** — `tipo_valor = ending_balance`, `poder_orgao` apenas "
                "Executivo (Estados `10111/10112`, DF `10121/10122`, Municípios `10131/10132`). "
                "Combinações por **coluna**: Disponibilidade de Caixa Bruta = `conta_contabil` em "
                "`11111*/11121*/11131*/11133*/11134*/11135*`; RP Liq.NP Exerc. Anteriores = `6321*/6313*`; "
                "RP Liq.NP Exercício = `6327*`; RP Emp.NL Exerc. Anteriores = `6311*/6312*`. "
                "Filtro por **linha** (FR — 3 últimos dígitos): `500` (Recursos Não Vinculados de Impostos) "
                "e `501/502/503` (Outros Recursos não Vinculados). "
                "**RGF Anexo 5 (Executivo)** — `cod_conta` em `DisponibilidadeDeCaixaBruta`, "
                "`RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores`, "
                "`RestosAPagarLiquidadosENaoPagosDoExercicio`, "
                "`RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores`; coluna `conta` em "
                "*Recursos Não Vinculados de Impostos* ou *Outros Recursos não Vinculados*."
            )

        emoji_d4_00045 = emoji_por_resposta(resposta_d4_00045, "D4_00045")
        with st.expander(
            titulo_expander_verificacao(emoji_d4_00045, "D4_00045", "Recursos Extraorçamentários (RGF 5 Exec.) ≥ valores restituíveis MSC Dez"),
            expanded=False,
        ):
            st.caption(
                "Verifica se o valor de **Recursos Extraorçamentários** no **RGF Anexo 5 (Executivo)** "
                "é **maior ou igual** ao saldo final apurado na **MSC de dezembro** das contas "
                "iniciadas em **1113**, associadas às **FRs 860, 861, 862 e 869**, do **Poder Executivo**."
            )
            mostrar_tabela_formatada(d4_00045_t)
            if resposta_d4_00045 == 'ERRO':
                st.warning(
                    "RGF (Recursos Extraorçamentários) menor que o montante apurado na MSC, ou "
                    "algum dos lados está com valor agregado negativo. A tabela traz a quebra "
                    "MSC por `poder_orgao` para apoiar o diagnóstico (Direta vs Indireta do Executivo)."
                )
            exibir_status_validacao(
                resposta_d4_00045,
                "✅ RGF (Recursos Extraorçamentários) cobre o montante apurado na MSC (CAPAG), com totais não negativos",
                "❌ RGF menor que o montante MSC **ou** total negativo no RGF ou na MSC (inconsistente com a regra CAPAG)",
                "⏸️ Análise não realizada: faltam dados de RGF 5 (Executivo) ou MSC de dezembro, ou linha não localizada.",
            )
            st.info(
                "💡 **Explicação:** **RGF Anexo 5 (Executivo)** — `cod_conta` "
                "**DemaisObrigacoesFinanceiras** e `conta` **Recursos Extraorçamentários**. "
                "**MSC dezembro (ending_balance)** — `conta_contabil` iniciando em **1113**, "
                "**fonte_recursos** (3 últimos dígitos) em **860/861/862/869**, `poder_orgao` "
                "Executivo (Direta+Indireta) — Estados `10111/10112`, DF `10121/10122`, "
                "Municípios `10131/10132`. **Regra extra:** se o agregado RGF ou MSC for "
                "**negativo**, a dimensão fica em **ERRO** (não basta RGF ≥ MSC)."
            )

        if ano is not None and ano >= 2025:
            st.info(
                "🆕 **Ranking 2025 oficial**\n\n"
                "As verificações homologadas nesta seção são D4_00046 e D4_00047, "
                "conforme metodologia oficial de 2025.",
                icon="ℹ️",
            )

        emoji_d4_00046 = emoji_por_resposta(resposta_d4_00046, "D4_00046")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d4_00046,
                "D4_00046",
                "Receitas selecionadas (RREO Anexo 3 × DCA Anexo I-C)"
            ),
            expanded=False
        ):
            st.caption(
                "Compara as receitas de **contribuições, patrimonial, agropecuária, industrial e de serviços** "
                "entre o **RREO Anexo 03** e a **DCA Anexo I-C**."
            )
            mostrar_tabela_formatada(d4_00046_t)
            exibir_status_validacao(
                resposta_d4_00046,
                "✅ Totais consistentes entre RREO Anexo 3 e DCA Anexo I-C (líquida de deduções)",
                "❌ Diferença entre o total do RREO Anexo 3 e o total líquido da DCA Anexo I-C",
                "⏸️ Análise não realizada: verificação depende do RREO Anexo 3 e da DCA Anexo I-C.",
            )
            st.info(
                "💡 **Explicação:** **RREO 3** — `coluna` **TOTAL (ÚLTIMOS 12 MESES)** e `cod_conta` "
                "**RREO3ReceitaDeContribuicoes**, **RREO3ReceitaPatrimonial**, **RREO3ReceitaAgropecuaria**, "
                "**RREO3ReceitaIndustrial** e **RREO3ReceitaDeServicos**. **DCA I-C** — mesmas naturezas "
                "nas contas **RO1.2.0.0.00.0.**, **RO1.3.0.0.00.0.**, **RO1.4.0.0.00.0.**, **RO1.5.0.0.00.0.** "
                "e **RO1.6.0.0.00.0.**, calculando **Receitas Brutas Realizadas − Outras Deduções da Receita**."
            )

        emoji_d4_00047 = emoji_por_resposta(resposta_d4_00047, "D4_00047")
        with st.expander(
            titulo_expander_verificacao(
                emoji_d4_00047,
                "D4_00047",
                "Dedução do FUNDEB (RREO Anexo 3 × DCA Anexo I-C)"
            ),
            expanded=False
        ):
            st.caption(
                "Compara a dedução de receita para formação do **FUNDEB** entre o "
                "**RREO Anexo 03** e a **DCA Anexo I-C**."
            )
            mostrar_tabela_formatada(d4_00047_t)
            exibir_status_validacao(
                resposta_d4_00047,
                "✅ Totais consistentes entre RREO Anexo 3 e DCA Anexo I-C para deduções do FUNDEB",
                "❌ Diferença entre o total do RREO Anexo 3 e o total da DCA Anexo I-C para deduções do FUNDEB",
                "⏸️ Análise não realizada: verificação depende do RREO Anexo 3 e da DCA Anexo I-C.",
            )
            st.info(
                "💡 **Explicação:** **RREO 3** — `coluna` **TOTAL (ÚLTIMOS 12 MESES)** e `cod_conta` "
                "**DeducaoDeReceitaParaFormacaoDoFUNDEB**. **DCA I-C** — `coluna` **Deduções - FUNDEB** "
                "e `cod_conta` **TotalReceitas**."
            )
