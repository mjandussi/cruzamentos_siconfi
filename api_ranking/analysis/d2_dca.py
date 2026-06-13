import numpy as np
import pandas as pd


def d2_00044(msc_encerr, df_dca_c):
    rec_total = msc_encerr.query(
        'tipo_valor == "beginning_balance" and (conta_contabil == "621200000" or conta_contabil == "621310100" or '
        'conta_contabil == "621310200" or conta_contabil == "621320000" or conta_contabil == "621390000")'
    )
    rec_total['dimensao'] = 'D2_00044_Rec.Realizada'
    rec_msc = rec_total.groupby('dimensao').agg({'valor': 'sum'})

    rec_dca = df_dca_c.query('cod_conta == "TotalReceitas"')
    rec_dca['dimensao'] = 'D2_00044_Rec.Realizada'
    rec_dca = rec_dca.filter(items=['dimensao', 'valor'])
    rec_dca = rec_dca.set_index("dimensao")
    rec_dca = rec_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00044_t = rec_msc.merge(rec_dca, on='dimensao')
    d2_00044_t['DIF'] = d2_00044_t['valor_x'] - d2_00044_t['valor_y']
    d2_00044_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00044_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00044 = 'ERRO'
        nota_d2_00044 = 0.00
    else:
        resposta_d2_00044 = 'OK'
        nota_d2_00044 = 1.00

    d2_00044 = pd.DataFrame([{
        'Dimensão': 'D2_00044',
        'Resposta': resposta_d2_00044,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas arrecadadas',
        'Nota': nota_d2_00044,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA'
    }])

    return d2_00044, d2_00044_t


def d2_00046(msc_encerr, df_dca_c):
    rec_base = msc_encerr[msc_encerr['tipo_valor'] == 'beginning_balance'].copy()

    conta_str = rec_base['conta_contabil'].astype(str)
    filtro_contas = (
        conta_str.str.startswith('6212') |
        conta_str.str.startswith('6213101') |
        conta_str.str.startswith('6213102') |
        conta_str.str.startswith('62132') |
        conta_str.str.startswith('62139')
    )
    rec_total = rec_base[filtro_contas].copy()

    nat_rec = rec_total['natureza_receita'].astype(str)
    filtro_tributos = (
        nat_rec.str.startswith('111201') |
        nat_rec.str.startswith('111250') |
        nat_rec.str.startswith('111253') |
        nat_rec.str.startswith('111303') |
        nat_rec.str.startswith('111451') |
        nat_rec.str.startswith('111999')
    )
    imposto_msc = rec_total[filtro_tributos].copy()
    imposto_msc['dimensao'] = 'D2_00046_Rec.Impostos'
    imposto_msc = imposto_msc.groupby('dimensao').agg({'valor': 'sum'})

    imposto_dca = df_dca_c.query(
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Receitas Brutas Realizadas") or '
        '(cod_conta == "RO1.1.1.0.00.0.0" and coluna == "Outras Deduções da Receita")'
    ).copy()
    imposto_dca['dimensao'] = 'D2_00046_Rec.Impostos'
    imposto_dca = imposto_dca.filter(items=['dimensao', 'valor'])
    imposto_dca = imposto_dca.set_index("dimensao")
    imposto_dca = imposto_dca.groupby('dimensao').agg({'valor': 'sum'})

    d2_00046_t = imposto_msc.merge(imposto_dca, on='dimensao')
    d2_00046_t['DIF'] = d2_00046_t['valor_x'] - d2_00046_t['valor_y']
    d2_00046_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00046_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00046 = 'ERRO'
        nota_d2_00046 = 0.00
    else:
        resposta_d2_00046 = 'OK'
        nota_d2_00046 = 1.00

    d2_00046 = pd.DataFrame([{
        'Dimensão': 'D2_00046',
        'Resposta': resposta_d2_00046,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas com tributos municipais',
        'Nota': nota_d2_00046,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA'
    }])

    return d2_00046, d2_00046_t


def d2_00048(msc_encerr, df_dca_c):
    rec_total = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "621200000"').copy()

    nat_rec = rec_total['natureza_receita'].astype(str)
    filtro_transf = (
        nat_rec.str.startswith('171151') |
        nat_rec.str.startswith('171152') |
        nat_rec.str.startswith('172150') |
        nat_rec.str.startswith('172151') |
        nat_rec.str.startswith('1751') |
        nat_rec.str.startswith('1715')
    )
    transf_msc = rec_total[filtro_transf].copy()
    transf_msc['dimensao'] = 'D2_00048_Transf.Const'
    transf_msc = transf_msc.groupby('dimensao').agg({'valor': 'sum'})

    transf_dca = df_dca_c.query(
        '(cod_conta == "RO1.7.1.1.51.0.0" or cod_conta == "RO1.7.1.1.52.0.0" or '
        'cod_conta == "RO1.7.1.5.00.0.0" or cod_conta == "RO1.7.2.1.50.0.0" or '
        'cod_conta == "RO1.7.2.1.51.0.0" or cod_conta == "RO1.7.5.1.00.0.0") '
        'and coluna == "Receitas Brutas Realizadas"'
    ).copy()
    transf_dca['dimensao'] = 'D2_00048_Transf.Const'
    transf_dca = transf_dca.filter(items=['dimensao', 'valor'])
    transf_dca = transf_dca.set_index("dimensao")
    transf_dca = transf_dca.groupby('dimensao').agg({'valor': 'sum'})

    if not transf_msc.empty and not transf_dca.empty:
        d2_00048_t = transf_msc.merge(transf_dca, on='dimensao')
        d2_00048_t['DIF'] = d2_00048_t['valor_x'] - d2_00048_t['valor_y']
        d2_00048_t.columns = ['MSC ENCERR', 'DCA C', 'DIF']

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00048_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00048 = 'ERRO'
            nota_d2_00048 = 0.00
        else:
            resposta_d2_00048 = 'OK'
            nota_d2_00048 = 1.00
    else:
        d2_00048_t = pd.DataFrame()
        resposta_d2_00048 = 'ERRO'
        nota_d2_00048 = 0.00

    d2_00048 = pd.DataFrame([{
        'Dimensão': 'D2_00048',
        'Resposta': resposta_d2_00048,
        'Descrição da Dimensão': 'Avalia a igualdade das receitas municipais com transferências constitucionais',
        'Nota': nota_d2_00048,
        'OBS': 'MSC de encerramento e no Anexo I-C da DCA (FPM, ICMS e FUNDEB)'
    }])

    return d2_00048, d2_00048_t


def d2_00049(msc_encerr, df_dca_d):
    """
    Verifica a igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas
    entre MSC de encerramento e DCA Anexo I-D.
    """
    # MSC - Empenhado (62213… com natureza de despesa informada)
    _tb = msc_encerr['tipo_valor'] == 'beginning_balance'
    _cc = msc_encerr['conta_contabil'].astype(str).str.startswith('62213')
    _nd = msc_encerr['natureza_despesa']
    _nd_ok = _nd.notna() & (_nd.astype(str).str.strip() != '')
    emp_msc = msc_encerr.loc[_tb & _cc & _nd_ok].copy()
    emp_msc['dimensao'] = 'D2_00049_Empenhado'
    emp_msc = emp_msc.groupby('dimensao').agg({'valor': 'sum'})

    # MSC - Liquidado (contas 622130300/400/700, com natureza de despesa informada)
    _cc_liq = msc_encerr['conta_contabil'].astype(str).isin(
        ['622130300', '622130400', '622130700']
    )
    liq_msc = msc_encerr.loc[_tb & _cc_liq & _nd_ok].copy()
    liq_msc['dimensao'] = 'D2_00049_Liquidado'
    liq_msc = liq_msc.groupby('dimensao').agg({'valor': 'sum'})

    # MSC - Pago (conta 622130400, com natureza de despesa informada)
    _cc_pago = msc_encerr['conta_contabil'].astype(str) == '622130400'
    pago_msc = msc_encerr.loc[_tb & _cc_pago & _nd_ok].copy()
    pago_msc['dimensao'] = 'D2_00049_Pago'
    pago_msc = pago_msc.groupby('dimensao').agg({'valor': 'sum'})

    # DCA - Empenhado
    emp_dca = df_dca_d.query('coluna == "Despesas Empenhadas" & cod_conta == "TotalDespesas"').copy()
    emp_dca['dimensao'] = 'D2_00049_Empenhado'
    emp_dca = emp_dca.filter(items=['dimensao', 'valor'])
    emp_dca = emp_dca.set_index("dimensao")

    # DCA - Liquidado
    liq_dca = df_dca_d.query('coluna == "Despesas Liquidadas" & cod_conta == "TotalDespesas"').copy()
    liq_dca['dimensao'] = 'D2_00049_Liquidado'
    liq_dca = liq_dca.filter(items=['dimensao', 'valor'])
    liq_dca = liq_dca.set_index("dimensao")

    # DCA - Pago
    pago_dca = df_dca_d.query('coluna == "Despesas Pagas" & cod_conta == "TotalDespesas"').copy()
    pago_dca['dimensao'] = 'D2_00049_Pago'
    pago_dca = pago_dca.filter(items=['dimensao', 'valor'])
    pago_dca = pago_dca.set_index("dimensao")

    # Merge e cálculo de diferenças
    try:
        d2_00049_emp = emp_msc.merge(emp_dca, on='dimensao')
        d2_00049_emp['DIF'] = d2_00049_emp['valor_x'] - d2_00049_emp['valor_y']
        d2_00049_emp.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00049_liq = liq_msc.merge(liq_dca, on='dimensao')
        d2_00049_liq['DIF'] = d2_00049_liq['valor_x'] - d2_00049_liq['valor_y']
        d2_00049_liq.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00049_pago = pago_msc.merge(pago_dca, on='dimensao')
        d2_00049_pago['DIF'] = d2_00049_pago['valor_x'] - d2_00049_pago['valor_y']
        d2_00049_pago.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00049_t = pd.concat([d2_00049_emp, d2_00049_liq, d2_00049_pago])
        d2_00049_t = d2_00049_t.reset_index()

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00049_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00049 = 'ERRO'
            nota_d2_00049 = 0.00
        else:
            resposta_d2_00049 = 'OK'
            nota_d2_00049 = 1.00
    except Exception:
        d2_00049_t = pd.DataFrame()
        resposta_d2_00049 = 'ERRO'
        nota_d2_00049 = 0.00

    d2_00049 = pd.DataFrame([{
        'Dimensão': 'D2_00049',
        'Resposta': resposta_d2_00049,
        'Descrição da Dimensão': 'Verifica a igualdade das Despesas Orçamentárias empenhadas, liquidadas e pagas',
        'Nota': nota_d2_00049,
        'OBS': 'MSC de encerramento e no Anexo I-D da DCA'
    }])

    return d2_00049, d2_00049_t


def d2_00050(msc_encerr, df_dca_d):
    """
    Verifica a igualdade dos Restos a Pagar processados e não processados
    entre MSC de encerramento e DCA Anexo I-D.
    """
    # MSC - RPP (conta 622130700)
    rpp_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "622130700"'
    ).copy()
    rpp_msc['dimensao'] = 'D2_00050_Inscrição RPP'
    rpp_msc = rpp_msc.groupby('dimensao').agg({'valor': 'sum'})

    # MSC - RPNP (contas 622130500, 622130600)
    rpnp_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and '
        '(conta_contabil == "622130500" or conta_contabil == "622130600")'
    ).copy()
    rpnp_msc['dimensao'] = 'D2_00050_Inscrição RPNP'
    rpnp_msc = rpnp_msc.groupby('dimensao').agg({'valor': 'sum'})

    # DCA - RPP
    rpp_dca = df_dca_d.query(
        'coluna == "Inscrição de Restos a Pagar Processados" & cod_conta == "TotalDespesas"'
    ).copy()
    rpp_dca['dimensao'] = 'D2_00050_Inscrição RPP'
    rpp_dca = rpp_dca.filter(items=['dimensao', 'valor'])
    rpp_dca = rpp_dca.set_index("dimensao")

    # DCA - RPNP
    rpnp_dca = df_dca_d.query(
        'coluna == "Inscrição de Restos a Pagar Não Processados" & cod_conta == "TotalDespesas"'
    ).copy()
    rpnp_dca['dimensao'] = 'D2_00050_Inscrição RPNP'
    rpnp_dca = rpnp_dca.filter(items=['dimensao', 'valor'])
    rpnp_dca = rpnp_dca.set_index("dimensao")

    # Merge e cálculo de diferenças
    try:
        d2_00050_rpp = rpp_msc.merge(rpp_dca, on='dimensao')
        d2_00050_rpp['DIF'] = d2_00050_rpp['valor_x'] - d2_00050_rpp['valor_y']
        d2_00050_rpp.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00050_rpnp = rpnp_msc.merge(rpnp_dca, on='dimensao')
        d2_00050_rpnp['DIF'] = d2_00050_rpnp['valor_x'] - d2_00050_rpnp['valor_y']
        d2_00050_rpnp.columns = ['MSC ENCERR', 'DCA D', 'DIF']

        d2_00050_t = pd.concat([d2_00050_rpp, d2_00050_rpnp])
        d2_00050_t = d2_00050_t.reset_index()

        tolerancia = 0.01
        condicao = ~np.isclose(d2_00050_t['DIF'], 0, atol=tolerancia)

        if condicao.any():
            resposta_d2_00050 = 'ERRO'
            nota_d2_00050 = 0.00
        else:
            resposta_d2_00050 = 'OK'
            nota_d2_00050 = 1.00
    except Exception:
        d2_00050_t = pd.DataFrame()
        resposta_d2_00050 = 'ERRO'
        nota_d2_00050 = 0.00

    d2_00050 = pd.DataFrame([{
        'Dimensão': 'D2_00050',
        'Resposta': resposta_d2_00050,
        'Descrição da Dimensão': 'Verifica a igualdade dos Restos a Pagar processados e não processados',
        'Nota': nota_d2_00050,
        'OBS': 'MSC de encerramento e no Anexo I-D da DCA'
    }])

    return d2_00050, d2_00050_t


def d2_00058(msc_encerr, df_dca_hi):
    """
    Verifica a igualdade entre os valores informados de VPA do FUNDEB (União e Estados)
    na DCA e na MSC de Encerramento.
    """
    vpa_fundeb_msc = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "452240000"'
    ).copy()
    vpa_fundeb_msc['dimensao'] = 'D2_00058_MSC_Transferências do FUNDEB - Inter OFSS - Estado'
    vpa_fundeb_msc = vpa_fundeb_msc.groupby('dimensao').agg({'valor': 'sum'})

    vpa_fundeb_dcahi = df_dca_hi.query('cod_conta == "P4.5.2.2.4.00.00"').copy()
    vpa_fundeb_dcahi['dimensao'] = 'D2_00058_DCA_Transferências do FUNDEB - Inter OFSS - Estado'
    vpa_fundeb_dcahi = vpa_fundeb_dcahi.groupby('dimensao').agg({'valor': 'sum'})

    vpa_fundeb_msc_u = msc_encerr.query(
        'tipo_valor == "beginning_balance" and conta_contabil == "452230000"'
    ).copy()
    vpa_fundeb_msc_u['dimensao'] = 'D2_00058_MSC_Transferências do FUNDEB - Inter OFSS - União'
    vpa_fundeb_msc_u = vpa_fundeb_msc_u.groupby('dimensao').agg({'valor': 'sum'})

    vpa_fundeb_dcahi_u = df_dca_hi.query('cod_conta == "P4.5.2.2.3.00.00"').copy()
    vpa_fundeb_dcahi_u['dimensao'] = 'D2_00058_DCA_Transferências do FUNDEB - Inter OFSS - União'
    vpa_fundeb_dcahi_u = vpa_fundeb_dcahi_u.groupby('dimensao').agg({'valor': 'sum'})

    d2_00058_t = pd.concat([
        vpa_fundeb_msc,
        vpa_fundeb_dcahi,
        vpa_fundeb_msc_u,
        vpa_fundeb_dcahi_u
    ])

    d2_00058_t['diff_valor'] = d2_00058_t['valor'].diff()
    d2_00058_ta = d2_00058_t.reset_index()

    indices_desejados = range(0, len(d2_00058_ta), 2)
    indices_existentes = [indice for indice in indices_desejados if indice in d2_00058_ta.index]
    d2_00058_ta.loc[indices_existentes, 'diff_valor'] = 0.0

    tolerancia = 0.01
    condicao = ~np.isclose(d2_00058_ta['diff_valor'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00058 = 'ERRO'
        nota_d2_00058 = 0.00
    else:
        resposta_d2_00058 = 'OK'
        nota_d2_00058 = 1.00

    d2_00058 = pd.DataFrame([{
        'Dimensão': 'D2_00058',
        'Resposta': resposta_d2_00058,
        'Descrição da Dimensão': 'Avalia se os valores de VPA e VPD com Fundeb estão iguais',
        'Nota': nota_d2_00058,
        'OBS': 'MSC de encerramento e no Anexo I-HI da DCA'
    }])

    return d2_00058, d2_00058_ta


def d2_00069(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra na função 09 (Previdência Social)
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    previ_msc = emp_msc_encerr.query('funcao == "09" & DIGITO_INTRA != "91"').copy()
    val_msc = pd.to_numeric(previ_msc['valor'], errors='coerce').fillna(0).sum()

    previ_dca = df_dca_e.query('coluna == "Despesas Empenhadas" and conta == "09 - Previdência Social"').copy()
    val_dca = pd.to_numeric(previ_dca['valor'], errors='coerce').fillna(0).sum()

    dif = val_msc - val_dca
    d2_00069_t = pd.DataFrame({
        'Dimensão': ['D2_00069_Previdência Social'],
        'MSC': [val_msc],
        'DCA E': [val_dca],
        'DIF': [dif],
    })

    tolerancia = 0.01
    if not np.isclose(dif, 0, atol=tolerancia):
        resposta_d2_00069 = 'ERRO'
        nota_d2_00069 = 0.00
    else:
        resposta_d2_00069 = 'OK'
        nota_d2_00069 = 1.00

    d2_00069 = pd.DataFrame([{
        'Dimensão': 'D2_00069',
        'Resposta': resposta_d2_00069,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 09 (Prev. Social)',
        'Nota': nota_d2_00069,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00069, d2_00069_t


def d2_00070(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra na função 10 (Saúde)
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    saude_msc = emp_msc_encerr.query('funcao == "10" & DIGITO_INTRA != "91"').copy()
    val_msc = pd.to_numeric(saude_msc['valor'], errors='coerce').fillna(0).sum()

    saude_dca = df_dca_e.query('coluna == "Despesas Empenhadas" and conta == "10 - Saúde"').copy()
    val_dca = pd.to_numeric(saude_dca['valor'], errors='coerce').fillna(0).sum()

    dif = val_msc - val_dca
    d2_00070_t = pd.DataFrame({
        'Dimensão': ['D2_00070_Saúde'],
        'MSC': [val_msc],
        'DCA E': [val_dca],
        'DIF': [dif],
    })

    tolerancia = 0.01
    if not np.isclose(dif, 0, atol=tolerancia):
        resposta_d2_00070 = 'ERRO'
        nota_d2_00070 = 0.00
    else:
        resposta_d2_00070 = 'OK'
        nota_d2_00070 = 1.00

    d2_00070 = pd.DataFrame([{
        'Dimensão': 'D2_00070',
        'Resposta': resposta_d2_00070,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 10 (Saúde)',
        'Nota': nota_d2_00070,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00070, d2_00070_t


def d2_00071(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra na função 12 (Educação)
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    edu_msc = emp_msc_encerr.query('funcao == "12" & DIGITO_INTRA != "91"').copy()
    val_msc = pd.to_numeric(edu_msc['valor'], errors='coerce').fillna(0).sum()

    edu_dca = df_dca_e.query('coluna == "Despesas Empenhadas" and conta == "12 - Educação"').copy()
    val_dca = pd.to_numeric(edu_dca['valor'], errors='coerce').fillna(0).sum()

    dif = val_msc - val_dca
    d2_00071_t = pd.DataFrame({
        'Dimensão': ['D2_00071_Educação'],
        'MSC': [val_msc],
        'DCA E': [val_dca],
        'DIF': [dif],
    })

    tolerancia = 0.01
    if not np.isclose(dif, 0, atol=tolerancia):
        resposta_d2_00071 = 'ERRO'
        nota_d2_00071 = 0.00
    else:
        resposta_d2_00071 = 'OK'
        nota_d2_00071 = 1.00

    d2_00071 = pd.DataFrame([{
        'Dimensão': 'D2_00071',
        'Resposta': resposta_d2_00071,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na função 12 (Educação)',
        'Nota': nota_d2_00071,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00071, d2_00071_t


def d2_00072(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas exceto-intra nas Demais Funções
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    demais_msc = emp_msc_encerr.query('(funcao != "09" & funcao != "10" & funcao != "12") & DIGITO_INTRA != "91"').copy()
    val_msc = pd.to_numeric(demais_msc['valor'], errors='coerce').fillna(0).sum()

    demais_dca = df_dca_e.query(
        'coluna == "Despesas Empenhadas" & '
        'conta not in ["09 - Previdência Social", "10 - Saúde", "12 - Educação", '
        '"Despesas Exceto Intraorçamentárias", "Despesas Intraorçamentárias"]'
    ).copy()
    demais_dca = demais_dca[demais_dca['conta'].str.match(r"^\d{2} - ")]
    val_dca = pd.to_numeric(demais_dca['valor'], errors='coerce').fillna(0).sum()

    dif = val_msc - val_dca
    d2_00072_t = pd.DataFrame({
        'Dimensão': ['D2_00072_Demais Funções'],
        'MSC': [val_msc],
        'DCA E': [val_dca],
        'DIF': [dif],
    })

    tolerancia = 0.01
    if not np.isclose(dif, 0, atol=tolerancia):
        resposta_d2_00072 = 'ERRO'
        nota_d2_00072 = 0.00
    else:
        resposta_d2_00072 = 'OK'
        nota_d2_00072 = 1.00

    d2_00072 = pd.DataFrame([{
        'Dimensão': 'D2_00072',
        'Resposta': resposta_d2_00072,
        'Descrição da Dimensão': 'Avalia se o valor de despesas exceto-intra na Demais Funções',
        'Nota': nota_d2_00072,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00072, d2_00072_t


def d2_00073(emp_msc_encerr, df_dca_e):
    """
    Avalia se o valor de despesas com Funções Intraorçamentárias
    é consistente entre MSC de encerramento e Anexo E da DCA.
    """
    intra_msc = emp_msc_encerr.query('DIGITO_INTRA == "91"').copy()
    val_msc = pd.to_numeric(intra_msc['valor'], errors='coerce').fillna(0).sum()

    intra_dca = df_dca_e.query('coluna == "Despesas Empenhadas" & conta == "Despesas Intraorçamentárias"').copy()
    val_dca = pd.to_numeric(intra_dca['valor'], errors='coerce').fillna(0).sum()

    dif = val_msc - val_dca
    d2_00073_t = pd.DataFrame({
        'Dimensão': ['D2_00073_Funções Intraorçamentárias'],
        'MSC': [val_msc],
        'DCA E': [val_dca],
        'DIF': [dif],
    })

    tolerancia = 0.01
    if not np.isclose(dif, 0, atol=tolerancia):
        resposta_d2_00073 = 'ERRO'
        nota_d2_00073 = 0.00
    else:
        resposta_d2_00073 = 'OK'
        nota_d2_00073 = 1.00

    d2_00073 = pd.DataFrame([{
        'Dimensão': 'D2_00073',
        'Resposta': resposta_d2_00073,
        'Descrição da Dimensão': 'Avalia se o valor de despesas com Funções Intraorçamentárias',
        'Nota': nota_d2_00073,
        'OBS': 'MSC de Encerramento e o Anexo E da DCA'
    }])

    return d2_00073, d2_00073_t


def d2_00074(msc_encerr, df_dca_f):
    """
    Compara o saldo final de RPPP e RPNPP Pagos
    entre MSC de Encerramento e Anexo F da DCA.
    """
    rpp_pago_dca = df_dca_f.query(
        'cod_conta == "TotalDespesas" and '
        '(coluna == "Restos a Pagar Processados Pagos" or coluna == "Restos a Pagar Não Processados Pagos")'
    ).copy()

    def _sum_dca_col(df, nome_coluna):
        sub = df[df['coluna'] == nome_coluna]
        return pd.to_numeric(sub['valor'], errors='coerce').fillna(0).sum() if not sub.empty else 0.0

    dca_rpnp_pago = _sum_dca_col(rpp_pago_dca, 'Restos a Pagar Não Processados Pagos')
    dca_rpp_pago = _sum_dca_col(rpp_pago_dca, 'Restos a Pagar Processados Pagos')

    rpnp_pago_msc = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "631400000"').copy()
    msc_rpnp_pago = pd.to_numeric(rpnp_pago_msc['valor'], errors='coerce').fillna(0).sum() if not rpnp_pago_msc.empty else 0.0

    rpp_pago_msc = msc_encerr.query('tipo_valor == "beginning_balance" and conta_contabil == "632200000"').copy()
    msc_rpp_pago = pd.to_numeric(rpp_pago_msc['valor'], errors='coerce').fillna(0).sum() if not rpp_pago_msc.empty else 0.0

    dif_rpnp = msc_rpnp_pago - dca_rpnp_pago
    dif_rpp = msc_rpp_pago - dca_rpp_pago

    d2_00074_t = pd.DataFrame({
        'Dimensão': [
            'D2_00074_RPNP Pagos',
            'D2_00074_RPP Pagos',
        ],
        'MSC': [msc_rpnp_pago, msc_rpp_pago],
        'DCA F': [dca_rpnp_pago, dca_rpp_pago],
        'DIF': [dif_rpnp, dif_rpp],
    })

    tolerancia = 0.01
    condicao = ~np.isclose(np.array([dif_rpnp, dif_rpp]), 0, atol=tolerancia)

    if condicao.any():
        resposta_d2_00074 = 'ERRO'
        nota_d2_00074 = 0.00
    else:
        resposta_d2_00074 = 'OK'
        nota_d2_00074 = 1.00

    d2_00074 = pd.DataFrame([{
        'Dimensão': 'D2_00074',
        'Resposta': resposta_d2_00074,
        'Descrição da Dimensão': 'Compara o saldo final de RPPP e RPNPP Pagos',
        'Nota': nota_d2_00074,
        'OBS': 'MSC de Encerramento e o Anexo F da DCA'
    }])

    return d2_00074, d2_00074_t


# A partir daqui resolvi usar a MSC PATRIMONIAL
######################################################################################################################
######################################################################################################################
######################################################################################################################

# Novas Verificações 2025

######################################################################################################################
######################################################################################################################
######################################################################################################################


def _comparar_rp_dca_g_msc_encerr(
    df_dca_g,
    rp_encerramento,
    codigo_dimensao,
    descricao_dimensao,
    conta_dca,
    filtro_msc,
    filtro_dca=None,
):
    """
    Compara RP do Anexo I-G da DCA com a MSC de encerramento (beginning_balance).
    """

    colunas_rp = [
        'Restos a Pagar Não Processados Liquidados',
        'Restos a Pagar Não Processados Pagos',
        'Restos a Pagar Não Processados Cancelados',
        'Restos a Pagar Processados Pagos',
        'Restos a Pagar Processados Cancelados',
    ]
    mapa_contas_msc = {
        'Restos a Pagar Não Processados Liquidados': ['6313', '6314'],
        'Restos a Pagar Não Processados Pagos': ['6314'],
        'Restos a Pagar Não Processados Cancelados': ['6319'],
        'Restos a Pagar Processados Pagos': ['6322'],
        'Restos a Pagar Processados Cancelados': ['6329'],
    }

    dca_base = df_dca_g.copy()
    if 'cod_conta' in dca_base.columns:
        dca_base = dca_base[dca_base['cod_conta'] == 'TotalDespesas']
    if filtro_dca is None:
        dca_filtrado = dca_base[
            (dca_base['conta'] == conta_dca) &
            (dca_base['coluna'].isin(colunas_rp))
        ].copy()
    else:
        dca_filtrado = filtro_dca(dca_base, colunas_rp).copy()
    dca_agrupado = dca_filtrado.groupby('coluna', as_index=False)['valor'].sum()
    mapa_dca = dict(zip(dca_agrupado['coluna'], dca_agrupado['valor']))

    msc_base = rp_encerramento.copy()
    msc_recorte = filtro_msc(msc_base)

    linhas = []
    for coluna in colunas_rp:
        prefixos = mapa_contas_msc[coluna]
        valor_dca = float(pd.to_numeric(mapa_dca.get(coluna, 0), errors='coerce'))
        serie_conta = msc_recorte['conta_contabil'].astype(str)
        mascara_contas = False
        for prefixo in prefixos:
            mascara_contas = mascara_contas | serie_conta.str.startswith(prefixo)
        valor_msc = float(
            pd.to_numeric(
                msc_recorte.loc[
                    mascara_contas,
                    'valor',
                ],
                errors='coerce',
            ).fillna(0).sum()
        )
        linhas.append({
            'item_rp': coluna,
            'conta_msc': ' + '.join([f'{p}*' for p in prefixos]),
            'valor_dca': valor_dca,
            'valor_msc': valor_msc,
            'dif': valor_dca - valor_msc,
        })

    d2_t = pd.DataFrame(linhas)
    tolerancia = 0.01
    condicao_erro = (~np.isclose(d2_t['dif'], 0, atol=tolerancia)).any()

    if condicao_erro:
        resposta = 'ERRO'
        nota = 0.00
    else:
        resposta = 'OK'
        nota = 1.00

    d2 = pd.DataFrame([{
        'Dimensão': codigo_dimensao,
        'Resposta': resposta,
        'Descrição da Dimensão': descricao_dimensao,
        'Nota': nota,
        'OBS': 'MSC de encerramento (beginning_balance) x DCA Anexo I-G',
    }])

    return d2, d2_t


_REMOVED_ANALYSES_ARITY = {'d2_00002': 2, 'd2_00003': 2, 'd2_00004': 2, 'd2_00005': 2, 'd2_00006': 2, 'd2_00007': 2, 'd2_00008': 2, 'd2_00010': 2, 'd2_00011': 2, 'd2_00012': 3, 'd2_00013': 5, 'd2_00014': 3, 'd2_00015': 2, 'd2_00016': 2, 'd2_00017': 2, 'd2_00018': 2, 'd2_00019': 2, 'd2_00020': 2, 'd2_00021': 2, 'd2_00023': 2, 'd2_00024': 2, 'd2_00028': 5, 'd2_00029': 4, 'd2_00030': 2, 'd2_00031': 2, 'd2_00032': 2, 'd2_00033': 2, 'd2_00034': 2, 'd2_00035': 2, 'd2_00036': 2, 'd2_00037': 2, 'd2_00038': 2, 'd2_00039': 2, 'd2_00040': 2, 'd2_00045': 2, 'd2_00047': 2, 'd2_00051': 2, 'd2_00052': 2, 'd2_00053': 2, 'd2_00054': 2, 'd2_00055': 2, 'd2_00059': 2, 'd2_00060': 2, 'd2_00061': 2, 'd2_00066': 2, 'd2_00067': 2, 'd2_00068': 2, 'd2_00076': 2, 'd2_00077': 2, 'd2_00079': 2, 'd2_00080': 2, 'd2_00081': 2, 'd2_00082': 2, 'd2_00083': 2, 'd2_00084': 2, 'd2_00085': 2, 'd2_00086': 2, 'd2_00087': 2, 'd2_00088': 2, 'd2_00089': 2, 'd2_00093': 2, 'd2_00094': 2, 'd2_00095': 2, 'd2_00099': 2, 'd2_00100': 2, 'd2_00101': 2, 'd2_00102': 2, 'd2_00103': 2, 'd2_00104': 2, 'd2_00105': 2}


def _removed_analysis_result(code):
    return pd.DataFrame([{
        "Dimensão": code.upper(),
        "Resposta": "N/A",
        "Descrição da Dimensão": "Verificação fora do escopo da Tabela 12 - Cruzamentos",
        "Nota": None,
        "OBS": "Análise removida do aplicativo CRUZAMENTOS SICONFI.",
    }])


def _removed_analysis_stub(name):
    def _stub(*_args, **_kwargs):
        result = _removed_analysis_result(name)
        detail = pd.DataFrame()
        arity = _REMOVED_ANALYSES_ARITY.get(name, 2)
        values = [result, detail]
        while len(values) < arity:
            values.append(pd.DataFrame())
        return tuple(values[:arity]) if arity != 1 else result
    return _stub


def __getattr__(name):
    if name in _REMOVED_ANALYSES_ARITY:
        return _removed_analysis_stub(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
