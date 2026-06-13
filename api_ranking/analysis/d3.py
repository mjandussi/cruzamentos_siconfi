import re

import numpy as np
import pandas as pd


def d3_00001(df_rreo_1):
    rec_rreo_1 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Empenhado'
    rec_rreo_1 = rec_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dps_rreo_1 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "TotalDespesas"')
    dps_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Empenhado'
    dps_rreo_1 = dps_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    sup_ou_def_rreo_1 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "Superavit"')
    sup_ou_def_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Empenhado'
    sup_ou_def_rreo_1 = sup_ou_def_rreo_1.groupby('dimensao')['valor'].sum().to_frame()

    d3_00001_e = rec_rreo_1.merge(dps_rreo_1, on='dimensao')
    d3_00001_e['DIF'] = d3_00001_e['valor_x'] - d3_00001_e['valor_y']
    d3_00001_e.columns = ['REC', 'DPS EMP', 'DIF']

    d3_00001_final1 = d3_00001_e.merge(sup_ou_def_rreo_1, on='dimensao')
    d3_00001_final1['DIF Final'] = d3_00001_final1['DIF'] - d3_00001_final1['valor']
    d3_00001_final1.columns = ['REC', 'DPS EMP', 'DIF', 'Superávit ou Défcit', 'DIF Final']

    rec_rreo_1 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Liquidado'
    rec_rreo_1 = rec_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dps_rreo_1 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "TotalDespesas"')
    dps_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Liquidado'
    dps_rreo_1 = dps_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    sup_ou_def_rreo_1 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "Superavit"')
    sup_ou_def_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Liquidado'
    sup_ou_def_rreo_1 = sup_ou_def_rreo_1.groupby('dimensao')['valor'].sum().to_frame()

    d3_00001_l = rec_rreo_1.merge(dps_rreo_1, on='dimensao')
    d3_00001_l['DIF'] = d3_00001_l['valor_x'] - d3_00001_l['valor_y']
    d3_00001_l.columns = ['REC', 'DPS EMP', 'DIF']

    d3_00001_final2 = d3_00001_l.merge(sup_ou_def_rreo_1, on='dimensao')
    d3_00001_final2['DIF Final'] = d3_00001_final2['DIF'] - d3_00001_final2['valor']
    d3_00001_final2.columns = ['REC', 'DPS EMP', 'DIF', 'Superávit ou Défcit', 'DIF Final']

    rec_rreo_1 = df_rreo_1.query('coluna == "Até o Bimestre (c)" & cod_conta == "TotalReceitas"')
    rec_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Pago'
    rec_rreo_1 = rec_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dps_rreo_1 = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "TotalDespesas"')
    dps_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Pago'
    dps_rreo_1 = dps_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    sup_ou_def_rreo_1 = df_rreo_1.query('coluna == "DESPESAS PAGAS ATÉ O BIMESTRE (j)" & cod_conta == "Superavit"')
    sup_ou_def_rreo_1['dimensao'] = 'D3_00001_Superavit ou Defcit_ Pago'
    sup_ou_def_rreo_1 = sup_ou_def_rreo_1.groupby('dimensao')['valor'].sum().to_frame()

    d3_00001_p = rec_rreo_1.merge(dps_rreo_1, on='dimensao')
    d3_00001_p['DIF'] = d3_00001_p['valor_x'] - d3_00001_p['valor_y']
    d3_00001_p.columns = ['REC', 'DPS EMP', 'DIF']

    d3_00001_final3 = d3_00001_p.merge(sup_ou_def_rreo_1, on='dimensao')
    d3_00001_final3['DIF Final'] = d3_00001_final3['DIF'] - d3_00001_final3['valor']
    d3_00001_final3.columns = ['REC', 'DPS EMP', 'DIF', 'Superávit ou Défcit', 'DIF Final']

    d3_00001_t = pd.concat([d3_00001_final1, d3_00001_final2, d3_00001_final3])
    d3_00001_t = d3_00001_t.reset_index()

    limiar = 1e-2
    d3_00001_t['DIF Final'] = d3_00001_t['DIF Final'].apply(lambda x: 0 if abs(x) < limiar else x)

    if (d3_00001_t['DIF Final'] == 0).all():
        resposta_d3_00001 = 'OK'
        nota_d3_00001 = 1.00
    else:
        resposta_d3_00001 = 'ERRO'
        nota_d3_00001 = 0.00

    d3_00001 = pd.DataFrame([{
        'Dimensão': 'D3_00001',
        'Resposta': resposta_d3_00001,
        'Descrição da Dimensão': 'Verifica se o resultado orçamentário foi calculado corretamente no Balanço Orçamentário',
        'Nota': nota_d3_00001,
        'OBS': 'Anexo 01 do RREO 6ºB'
    }])

    return d3_00001, d3_00001_t


def d3_00002(df_rreo_1, df_rreo_2):
    dotinic_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO INICIAL" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    dotinic_rreo_2['dimensao'] = 'D3_00002_Dotação_Inicial'
    dotinic_rreo_2 = dotinic_rreo_2.filter(items=['dimensao', 'valor'])

    dotinic_intra_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO INICIAL" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    dotinic_intra_rreo_2['dimensao'] = 'D3_00002_Dotação_Inicial_INTRA'
    dotinic_intra_rreo_2 = dotinic_intra_rreo_2.filter(items=['dimensao', 'valor'])

    dotatualiz_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO ATUALIZADA (a)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    dotatualiz_rreo_2['dimensao'] = 'D3_00002_Dotação_Atualizada'
    dotatualiz_rreo_2 = dotatualiz_rreo_2.filter(items=['dimensao', 'valor'])

    dotatualiz_intra_rreo_2 = df_rreo_2.query('coluna == "DOTAÇÃO ATUALIZADA (a)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    dotatualiz_intra_rreo_2['dimensao'] = 'D3_00002_Dotação_Atualizada_INTRA'
    dotatualiz_intra_rreo_2 = dotatualiz_intra_rreo_2.filter(items=['dimensao', 'valor'])

    emp_rreo_2 = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    emp_rreo_2['dimensao'] = 'D3_00002_Empenhado'
    emp_rreo_2 = emp_rreo_2.filter(items=['dimensao', 'valor'])

    emp_intra_rreo_2 = df_rreo_2.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (b)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    emp_intra_rreo_2['dimensao'] = 'D3_00002_Empenhado_INTRA'
    emp_intra_rreo_2 = emp_intra_rreo_2.filter(items=['dimensao', 'valor'])

    liq_rreo_2 = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    liq_rreo_2['dimensao'] = 'D3_00002_Liquidado'
    liq_rreo_2 = liq_rreo_2.filter(items=['dimensao', 'valor'])

    liq_intra_rreo_2 = df_rreo_2.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    liq_intra_rreo_2['dimensao'] = 'D3_00002_Liquidado_INTRA'
    liq_intra_rreo_2 = liq_intra_rreo_2.filter(items=['dimensao', 'valor'])

    rpnp_rreo_2 = df_rreo_2.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"')
    rpnp_rreo_2['dimensao'] = 'D3_00002_Inscrição RPNP'
    rpnp_rreo_2 = rpnp_rreo_2.filter(items=['dimensao', 'valor'])

    rpnp_intra_rreo_2 = df_rreo_2.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (f)" & cod_conta == "RREO2TotalDespesas" & conta == "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"')
    rpnp_intra_rreo_2['dimensao'] = 'D3_00002_Inscrição RPNP_INTRA'
    rpnp_intra_rreo_2 = rpnp_intra_rreo_2.filter(items=['dimensao', 'valor'])

    dotinic_rreo_1a = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    dotinic_rreo_1b = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    dotinic_rreo_1 = pd.concat([dotinic_rreo_1a, dotinic_rreo_1b])
    dotinic_rreo_1['dimensao'] = 'D3_00002_Dotação_Inicial'
    dotinic_rreo_1 = dotinic_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dotinic_intra_rreo_1 = df_rreo_1.query('coluna == "DOTAÇÃO INICIAL (d)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    dotinic_intra_rreo_1['dimensao'] = 'D3_00002_Dotação_Inicial_INTRA'
    dotinic_intra_rreo_1 = dotinic_intra_rreo_1.filter(items=['dimensao', 'valor'])

    dotatualiz_rreo_1a = df_rreo_1.query('coluna == "DOTAÇÃO ATUALIZADA (e)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    dotatualiz_rreo_1b = df_rreo_1.query('coluna == "DOTAÇÃO ATUALIZADA (e)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    dotatualiz_rreo_1 = pd.concat([dotatualiz_rreo_1a, dotatualiz_rreo_1b])
    dotatualiz_rreo_1['dimensao'] = 'D3_00002_Dotação_Atualizada'
    dotatualiz_rreo_1 = dotatualiz_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    dotatualiz_intra_rreo_1 = df_rreo_1.query('coluna == "DOTAÇÃO ATUALIZADA (e)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    dotatualiz_intra_rreo_1['dimensao'] = 'D3_00002_Dotação_Atualizada_INTRA'
    dotatualiz_intra_rreo_1 = dotatualiz_intra_rreo_1.filter(items=['dimensao', 'valor'])

    emp_rreo_1a = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    emp_rreo_1b = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    emp_rreo_1 = pd.concat([emp_rreo_1a, emp_rreo_1b])
    emp_rreo_1['dimensao'] = 'D3_00002_Empenhado'
    emp_rreo_1 = emp_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    emp_intra_rreo_1 = df_rreo_1.query('coluna == "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    emp_intra_rreo_1['dimensao'] = 'D3_00002_Empenhado_INTRA'
    emp_intra_rreo_1 = emp_intra_rreo_1.filter(items=['dimensao', 'valor'])

    liq_rreo_1a = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    liq_rreo_1b = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    liq_rreo_1 = pd.concat([liq_rreo_1a, liq_rreo_1b])
    liq_rreo_1['dimensao'] = 'D3_00002_Liquidado'
    liq_rreo_1 = liq_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    liq_intra_rreo_1 = df_rreo_1.query('coluna == "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    liq_intra_rreo_1['dimensao'] = 'D3_00002_Liquidado_INTRA'
    liq_intra_rreo_1 = liq_intra_rreo_1.filter(items=['dimensao', 'valor'])

    rpnp_rreo_1a = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "DespesasExcetoIntraOrcamentarias"')
    rpnp_rreo_1b = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "AmortizacaoRefinanciamentoDaDivida"')
    rpnp_rreo_1 = pd.concat([rpnp_rreo_1a, rpnp_rreo_1b])
    rpnp_rreo_1['dimensao'] = 'D3_00002_Inscrição RPNP'
    rpnp_rreo_1 = rpnp_rreo_1.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_intra_rreo_1 = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "DespesasIntraOrcamentariasTotal"')
    rpnp_intra_rreo_1['dimensao'] = 'D3_00002_Inscrição RPNP_INTRA'
    rpnp_intra_rreo_1 = rpnp_intra_rreo_1.filter(items=['dimensao', 'valor'])

    d3_00002_dot_inicial = dotinic_rreo_2.merge(dotinic_rreo_1, on='dimensao')
    d3_00002_dot_inicial['DIF'] = d3_00002_dot_inicial['valor_x'] - d3_00002_dot_inicial['valor_y']
    d3_00002_dot_inicial = d3_00002_dot_inicial[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_inicial.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_dot_inicial_intra = dotinic_intra_rreo_2.merge(dotinic_intra_rreo_1, on='dimensao')
    d3_00002_dot_inicial_intra['DIF'] = d3_00002_dot_inicial_intra['valor_x'] - d3_00002_dot_inicial_intra['valor_y']
    d3_00002_dot_inicial_intra = d3_00002_dot_inicial_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_inicial_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_dot_atualiz = dotatualiz_rreo_2.merge(dotatualiz_rreo_1, on='dimensao')
    d3_00002_dot_atualiz['DIF'] = d3_00002_dot_atualiz['valor_x'] - d3_00002_dot_atualiz['valor_y']
    d3_00002_dot_atualiz = d3_00002_dot_atualiz[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_atualiz.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_dot_atualiz_intra = dotatualiz_intra_rreo_2.merge(dotatualiz_intra_rreo_1, on='dimensao')
    d3_00002_dot_atualiz_intra['DIF'] = d3_00002_dot_atualiz_intra['valor_x'] - d3_00002_dot_atualiz_intra['valor_y']
    d3_00002_dot_atualiz_intra = d3_00002_dot_atualiz_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_dot_atualiz_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_emp = emp_rreo_2.merge(emp_rreo_1, on='dimensao')
    d3_00002_emp['DIF'] = d3_00002_emp['valor_x'] - d3_00002_emp['valor_y']
    d3_00002_emp = d3_00002_emp[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_emp.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_emp_intra = emp_intra_rreo_2.merge(emp_intra_rreo_1, on='dimensao')
    d3_00002_emp_intra['DIF'] = d3_00002_emp_intra['valor_x'] - d3_00002_emp_intra['valor_y']
    d3_00002_emp_intra = d3_00002_emp_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_emp_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_liq = liq_rreo_2.merge(liq_rreo_1, on='dimensao')
    d3_00002_liq['DIF'] = d3_00002_liq['valor_x'] - d3_00002_liq['valor_y']
    d3_00002_liq = d3_00002_liq[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_liq.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_liq_intra = liq_intra_rreo_2.merge(liq_intra_rreo_1, on='dimensao')
    d3_00002_liq_intra['DIF'] = d3_00002_liq_intra['valor_x'] - d3_00002_liq_intra['valor_y']
    d3_00002_liq_intra = d3_00002_liq_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_liq_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_rpnp = rpnp_rreo_2.merge(rpnp_rreo_1, on='dimensao')
    d3_00002_rpnp['DIF'] = d3_00002_rpnp['valor_x'] - d3_00002_rpnp['valor_y']
    d3_00002_rpnp = d3_00002_rpnp[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_rpnp.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    d3_00002_rpnp_intra = rpnp_intra_rreo_2.merge(rpnp_intra_rreo_1, on='dimensao')
    d3_00002_rpnp_intra['DIF'] = d3_00002_rpnp_intra['valor_x'] - d3_00002_rpnp_intra['valor_y']
    d3_00002_rpnp_intra = d3_00002_rpnp_intra[['dimensao', 'valor_x', 'valor_y', 'DIF']]
    d3_00002_rpnp_intra.columns = ['dimensao', 'RREO 2', 'RREO 1', 'DIF']

    final_a = pd.concat([
        d3_00002_dot_inicial,
        d3_00002_dot_inicial_intra,
        d3_00002_dot_atualiz,
        d3_00002_dot_atualiz_intra,
        d3_00002_emp,
        d3_00002_emp_intra,
    ])
    final_b = pd.concat([
        d3_00002_liq,
        d3_00002_liq_intra,
        d3_00002_rpnp,
        d3_00002_rpnp_intra,
    ])

    d3_00002_t = pd.concat([final_a, final_b])

    tolerancia = 1e-2
    if (d3_00002_t['DIF'].abs() <= tolerancia).all():
        resposta_d3_00002 = 'OK'
        nota_d3_00002 = 1.00
    else:
        resposta_d3_00002 = 'ERRO'
        nota_d3_00002 = 0.00

    d3_00002 = pd.DataFrame([{
        'Dimensão': 'D3_00002',
        'Resposta': resposta_d3_00002,
        'Descrição da Dimensão': 'Verifica a igualdade dos valores de despesa entre o Balanço Orçamentário e o Demonstrativo da Execução da Despesa por Função/Subfunção',
        'Nota': nota_d3_00002,
        'OBS': 'Anexo 01 e Anexo 02 do RREO'
    }])

    return d3_00002, d3_00002_t


def d3_00005(df_rreo_3, df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e):
    # Sem demonstrativo no SICONFI, DataFrames vêm sem colunas e .query() quebra (UndefinedVariableError)
    _cols_rreo = {'coluna', 'cod_conta', 'valor'}
    _cols_rgf_quad = {'coluna', 'cod_conta', 'valor'}
    _cols_rgf_cod = {'cod_conta', 'valor'}
    if (
        df_rreo_3 is None or not isinstance(df_rreo_3, pd.DataFrame)
        or not _cols_rreo.issubset(df_rreo_3.columns)
        or df_rgf_1e is None or not isinstance(df_rgf_1e, pd.DataFrame)
        or not _cols_rgf_cod.issubset(df_rgf_1e.columns)
        or df_rgf_2e is None or not isinstance(df_rgf_2e, pd.DataFrame)
        or not _cols_rgf_quad.issubset(df_rgf_2e.columns)
        or df_rgf_3e is None or not isinstance(df_rgf_3e, pd.DataFrame)
        or not _cols_rgf_quad.issubset(df_rgf_3e.columns)
        or df_rgf_4e is None or not isinstance(df_rgf_4e, pd.DataFrame)
        or not _cols_rgf_cod.issubset(df_rgf_4e.columns)
    ):
        d3_00005 = pd.DataFrame([{
            'Dimensão': 'D3_00005',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Verifica a Igualdade da Receita Corrente Líquida (RCL)',
            'Nota': None,
            'OBS': 'RREO Anexo 3 e/ou RGF Anexos 1–4 (Executivo) indisponíveis para o ente/período'
        }])
        return d3_00005, pd.DataFrame()

    rcl_rreo3_df = df_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"').copy()
    rcl_rreo_3 = rcl_rreo3_df.query('cod_conta == "RREO3ReceitaCorrenteLiquida"')
    rcl_rreo_3_divida = rcl_rreo3_df.query('cod_conta == "RREO3ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')
    rcl_rreo_3_pessoal = rcl_rreo3_df.query('cod_conta == "RREO3ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDaDespesaComPessoal"')

    rcl_rgf1 = df_rgf_1e.query('cod_conta == "ReceitaCorrenteLiquidaLimiteLegal"')
    rcl_rgf1_pessoal = df_rgf_1e.query('cod_conta == "ReceitaCorrenteLiquidaAjustada"')

    rcl_rgf2_df = df_rgf_2e.query('coluna == "Até o 3º Quadrimestre"')
    rcl_rgf2 = rcl_rgf2_df.query('cod_conta == "RGF2ReceitaCorrenteLiquida"')
    rcl_rgf2_divida = rcl_rgf2_df.query('cod_conta == "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')

    rcl_rgf3_df = df_rgf_3e.query('coluna == "Até o 3º Quadrimestre"')
    rcl_rgf3 = rcl_rgf3_df.query('cod_conta == "RGF3ReceitaCorrenteLiquida"')
    rcl_rgf3_divida = rcl_rgf3_df.query('cod_conta == "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')

    rcl_rgf4 = df_rgf_4e.query('cod_conta == "RGF4ReceitaCorrenteLiquida"')
    rcl_rgf4_divida = df_rgf_4e.query('cod_conta == "ReceitaCorrenteLiquidaAjustadaParaCalculoDosLimitesDeEndividamento"')

    d3_00005_t1 = pd.concat([rcl_rreo_3, rcl_rgf1, rcl_rgf2, rcl_rgf3, rcl_rgf4]).reset_index()
    d3_00005_t1['DIF'] = d3_00005_t1['valor'].diff()
    d3_00005_t1 = d3_00005_t1[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    d3_00005_t1.loc[0, 'DIF'] = 0

    d3_00005_t2 = pd.concat([rcl_rreo_3_pessoal, rcl_rgf1_pessoal]).reset_index()
    d3_00005_t2['DIF'] = d3_00005_t2['valor'].diff()
    d3_00005_t2 = d3_00005_t2[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    d3_00005_t2.loc[0, 'DIF'] = 0

    d3_00005_t3 = pd.concat([rcl_rreo_3_divida, rcl_rgf2_divida, rcl_rgf3_divida, rcl_rgf4_divida]).reset_index()
    d3_00005_t3['DIF'] = d3_00005_t3['valor'].diff()
    d3_00005_t3 = d3_00005_t3[['instituicao', 'anexo', 'cod_conta', 'valor', 'DIF']]
    d3_00005_t3.loc[0, 'DIF'] = 0

    d3_00005_t = pd.concat([d3_00005_t1, d3_00005_t2, d3_00005_t3]).reset_index(drop=True)

    tolerancia = 0.01
    condicao = ~np.isclose(d3_00005_t['DIF'], 0, atol=tolerancia)

    if condicao.any():
        resposta_d3_00005 = 'ERRO'
        nota_d3_00005 = 0.00
    else:
        resposta_d3_00005 = 'OK'
        nota_d3_00005 = 1.00

    d3_00005 = pd.DataFrame([{
        'Dimensão': 'D3_00005',
        'Resposta': resposta_d3_00005,
        'Descrição da Dimensão': 'Verifica a Igualdade da Receita Corrente Líquida (RCL)',
        'Nota': nota_d3_00005,
        'OBS': 'Anexo 03 do RREO e os Anexos 01, 02, 03 e 04 do RGF do poder executivo'
    }])

    return d3_00005, d3_00005_t


def d3_00006(df_rgf_2e, df_rreo_6, ano):
    _cols_quad = {'coluna', 'cod_conta', 'valor'}
    _cols_rreo6 = {'coluna', 'cod_conta', 'valor'}
    if (
        df_rgf_2e is None or not isinstance(df_rgf_2e, pd.DataFrame)
        or not _cols_quad.issubset(df_rgf_2e.columns)
        or df_rreo_6 is None or not isinstance(df_rreo_6, pd.DataFrame)
        or not _cols_rreo6.issubset(df_rreo_6.columns)
    ):
        d3_00006 = pd.DataFrame([{
            'Dimensão': 'D3_00006',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Verifica a Igualdade da Dívida Consolidada Líquida (DCL)',
            'Nota': None,
            'OBS': 'RREO Anexo 6 e/ou RGF Anexo 2 (Executivo) indisponíveis para o ente/período'
        }])
        return d3_00006, pd.DataFrame()

    dcl_rgf2 = df_rgf_2e.query('cod_conta == "DividaConsolidadaLiquida" and coluna == "Até o 3º Quadrimestre"')
    dcl_rreo6 = df_rreo_6.query(f'cod_conta == "DividaConsolidadaLiquida" and coluna == "Até o Bimestre {ano} (b)"')

    if dcl_rgf2.empty or dcl_rreo6.empty:
        d3_00006 = pd.DataFrame([{
            'Dimensão': 'D3_00006',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Verifica a Igualdade da Dívida Consolidada Líquida (DCL)',
            'Nota': None,
            'OBS': 'Linha DividaConsolidadaLiquida ausente no RGF Anexo 2 e/ou no RREO Anexo 6',
        }])
        return d3_00006, pd.DataFrame()

    valor_rgf = float(pd.to_numeric(dcl_rgf2['valor'], errors='coerce').fillna(0).sum())
    valor_rreo = float(pd.to_numeric(dcl_rreo6['valor'], errors='coerce').fillna(0).sum())
    dif = valor_rreo - valor_rgf

    d3_00006_t = pd.DataFrame([
        {
            'fonte': 'RGF — Anexo 02',
            'cod_conta': 'DividaConsolidadaLiquida',
            'valor': valor_rgf,
        },
        {
            'fonte': 'RREO — Anexo 06',
            'cod_conta': 'DividaConsolidadaLiquida',
            'valor': valor_rreo,
        },
        {
            'fonte': 'Diferença (RREO − RGF)',
            'cod_conta': 'Diferença entre os totais',
            'valor': dif,
        },
    ])

    tolerancia = 0.01
    condicao = not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0)

    if condicao:
        resposta_d3_00006 = 'ERRO'
        nota_d3_00006 = 0.00
    else:
        resposta_d3_00006 = 'OK'
        nota_d3_00006 = 1.00

    d3_00006 = pd.DataFrame([{
        'Dimensão': 'D3_00006',
        'Resposta': resposta_d3_00006,
        'Descrição da Dimensão': 'Verifica a Igualdade da Dívida Consolidada Líquida (DCL)',
        'Nota': nota_d3_00006,
        'OBS': 'Anexo 06 do RREO e o Anexo 02 do RGF do poder executivo'
    }])

    return d3_00006, d3_00006_t


def d3_00008(df_rgf_5e, rgf_o, df_rreo_1, tipo_ente):
    if tipo_ente == "E":
        rpnp_rgf_5e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (IV) = (I + II + III)"'
        )
        rpnp_rgf_5e = rpnp_rgf_5e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf_5_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (III) = (I + II)"'
        )
        rpnp_rgf_5_o = rpnp_rgf_5_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf = pd.concat([rpnp_rgf_5e, rpnp_rgf_5_o])
    else:
        rpnp_rgf_5e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (IV) = (I + II + III)"'
        ) if not df_rgf_5e.empty and 'cod_conta' in df_rgf_5e.columns else pd.DataFrame()
        if not rpnp_rgf_5e.empty:
            rpnp_rgf_5e = rpnp_rgf_5e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf_5_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDoExercicio" & conta == "TOTAL (III) = (I + II)"'
        ) if not rgf_o.empty and 'cod_conta' in rgf_o.columns else pd.DataFrame()
        if not rpnp_rgf_5_o.empty:
            rpnp_rgf_5_o = rpnp_rgf_5_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_rgf = pd.concat([rpnp_rgf_5e, rpnp_rgf_5_o])
    rpnp_rgf['cod'] = "RPNP_Inscrito"

    rpnp_rreo_1 = df_rreo_1.query('coluna == "INSCRITAS EM RESTOS A PAGAR NÃO PROCESSADOS (k)" & cod_conta == "TotalDespesas"')
    rpnp_rreo_1 = rpnp_rreo_1.groupby(['anexo'])['valor'].sum().reset_index()
    rpnp_rreo_1['cod'] = "RPNP_Inscrito"

    d3_pivot = pd.concat([rpnp_rgf, rpnp_rreo_1])
    d3_pivot = d3_pivot.groupby(['cod', 'anexo'])['valor'].sum().reset_index()
    d3_pivot = d3_pivot.pivot(index='cod', columns='anexo', values='valor').fillna(0)

    col_rgf = 'RGF-Anexo 05'
    col_rreo = 'RREO-Anexo 01'
    if d3_pivot.empty:
        d3_00008 = pd.DataFrame([{
            'Dimensão': 'D3_00008',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Verifica a igualdade dos valores dos restos a pagar não processados',
            'Nota': None,
            'OBS': 'Sem dados agregados de RPNP para comparar RGF e RREO',
        }])
        return d3_00008, pd.DataFrame()

    cod_idx = str(d3_pivot.index[0])
    val_rgf = float(d3_pivot.loc[cod_idx, col_rgf]) if col_rgf in d3_pivot.columns else 0.0
    val_rreo = float(d3_pivot.loc[cod_idx, col_rreo]) if col_rreo in d3_pivot.columns else 0.0
    dif = val_rgf - val_rreo

    d3_00008_t = pd.DataFrame([
        {
            'fonte': 'RGF — Anexo 05',
            'cod': cod_idx,
            'valor': val_rgf,
        },
        {
            'fonte': 'RREO — Anexo 01',
            'cod': cod_idx,
            'valor': val_rreo,
        },
        {
            'fonte': 'Diferença (RGF − RREO)',
            'cod': 'Diferença entre os totais',
            'valor': dif,
        },
    ])

    tolerancia_centavos = 0.99999
    tolerancia_zero = 1e-3

    diferenca_encontrada = abs(dif)

    if np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00008 = 'OK'
        nota_d3_00008 = 1.00
    elif diferenca_encontrada <= tolerancia_centavos and not np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00008 = 'OK (com dif centavos)'
        nota_d3_00008 = 1.00
    else:
        resposta_d3_00008 = 'ERRO'
        nota_d3_00008 = 0.00

    d3_00008 = pd.DataFrame([{
        'Dimensão': 'D3_00008',
        'Resposta': resposta_d3_00008,
        'Descrição da Dimensão': 'Verifica a igualdade dos valores dos restos a pagar não processados',
        'Nota': nota_d3_00008,
        'OBS': 'Anexo 01 do RREO e a soma dos valores do Anexo 05 do RGF de todos os poderes/órgãos'
    }])

    return d3_00008, d3_00008_t


def d3_00009(df_rgf_5e, rgf_o, df_rreo_7, tipo_ente):
    if tipo_ente == "E":
        rpnp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        )
        rpnp_a_pagar_rgf_e = rpnp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        )
        rpp_a_pagar_rgf_e = rpp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        )
        rpnp_a_pagar_rgf_o = rpnp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        )
        rpp_a_pagar_rgf_o = rpp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf = pd.concat([rpnp_a_pagar_rgf_e, rpnp_a_pagar_rgf_o])
        rpnp_a_pagar_rgf['cod'] = "RPNP"
        rpp_a_pagar_rgf = pd.concat([rpp_a_pagar_rgf_e, rpp_a_pagar_rgf_o])
        rpp_a_pagar_rgf['cod'] = "RPP"
    else:
        rpnp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        ) if not df_rgf_5e.empty and 'cod_conta' in df_rgf_5e.columns else pd.DataFrame()
        if not rpnp_a_pagar_rgf_e.empty:
            rpnp_a_pagar_rgf_e = rpnp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_e = df_rgf_5e.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (IV) = (I + II + III)"'
        ) if not df_rgf_5e.empty and 'cod_conta' in df_rgf_5e.columns else pd.DataFrame()
        if not rpp_a_pagar_rgf_e.empty:
            rpp_a_pagar_rgf_e = rpp_a_pagar_rgf_e.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarEmpenhadosENaoLiquidadosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        ) if not rgf_o.empty and 'cod_conta' in rgf_o.columns else pd.DataFrame()
        if not rpnp_a_pagar_rgf_o.empty:
            rpnp_a_pagar_rgf_o = rpnp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpp_a_pagar_rgf_o = rgf_o.query(
            'cod_conta == "RestosAPagarLiquidadosENaoPagosDeExerciciosAnteriores" & conta == "TOTAL (III) = (I + II)"'
        ) if not rgf_o.empty and 'cod_conta' in rgf_o.columns else pd.DataFrame()
        if not rpp_a_pagar_rgf_o.empty:
            rpp_a_pagar_rgf_o = rpp_a_pagar_rgf_o.groupby(['anexo'])['valor'].sum().reset_index()

        rpnp_a_pagar_rgf = pd.concat([rpnp_a_pagar_rgf_e, rpnp_a_pagar_rgf_o])
        if not rpnp_a_pagar_rgf.empty:
            rpnp_a_pagar_rgf['cod'] = "RPNP"
        rpp_a_pagar_rgf = pd.concat([rpp_a_pagar_rgf_e, rpp_a_pagar_rgf_o])
        if not rpp_a_pagar_rgf.empty:
            rpp_a_pagar_rgf['cod'] = "RPP"

    rpnp_a_pagar_rreo_7 = df_rreo_7.query('cod_conta == "RestosAPagarNaoProcessadosAPagar" & conta == "TOTAL (III) = (I + II)"')
    rpnp_a_pagar_rreo_7 = rpnp_a_pagar_rreo_7.groupby(['anexo'])['valor'].sum().reset_index()
    rpnp_a_pagar_rreo_7['cod'] = "RPNP"

    rpp_a_pagar_rreo_7 = df_rreo_7.query('cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosAPagar" & conta == "TOTAL (III) = (I + II)"')
    rpp_a_pagar_rreo_7 = rpp_a_pagar_rreo_7.groupby(['anexo'])['valor'].sum().reset_index()
    rpp_a_pagar_rreo_7['cod'] = "RPP"

    total_rpnp_rreo = float(rpnp_a_pagar_rreo_7['valor'].sum()) if not rpnp_a_pagar_rreo_7.empty else 0.0
    total_rpnp_rgf = float(rpnp_a_pagar_rgf['valor'].sum()) if not rpnp_a_pagar_rgf.empty else 0.0
    total_rpp_rreo = float(rpp_a_pagar_rreo_7['valor'].sum()) if not rpp_a_pagar_rreo_7.empty else 0.0
    total_rpp_rgf = float(rpp_a_pagar_rgf['valor'].sum()) if not rpp_a_pagar_rgf.empty else 0.0

    dif_total = (total_rpnp_rgf + total_rpp_rgf) - (total_rpnp_rreo + total_rpp_rreo)
    # manter detalhamento por tipo para inspeção
    dif_rpp = total_rpp_rgf - total_rpp_rreo
    dif_rpnp_tipo = total_rpnp_rgf - total_rpnp_rreo

    d3_00009_t = pd.DataFrame([
        {
            'fonte': 'RGF — Anexo 05',
            'rpp_rpnp_total': total_rpnp_rgf + total_rpp_rgf,
            'dif_rpp': total_rpp_rgf,
            'dif_rpnp': total_rpnp_rgf,
        },
        {
            'fonte': 'RREO — Anexo 07',
            'rpp_rpnp_total': total_rpnp_rreo + total_rpp_rreo,
            'dif_rpp': total_rpp_rreo,
            'dif_rpnp': total_rpnp_rreo,
        },
        {
            'fonte': 'Diferença (RGF − RREO)',
            'rpp_rpnp_total': dif_total,
            'dif_rpp': dif_rpp,
            'dif_rpnp': dif_rpnp_tipo,
        },
    ])

    tolerancia_centavos = 0.99999
    tolerancia_zero = 1e-3

    diferenca_encontrada = abs(dif_total)

    if np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00009 = 'OK'
        nota_d3_00009 = 1.00
    elif diferenca_encontrada <= tolerancia_centavos and not np.isclose(diferenca_encontrada, 0, atol=tolerancia_zero):
        resposta_d3_00009 = 'OK (com dif centavos)'
        nota_d3_00009 = 1.00
    else:
        resposta_d3_00009 = 'ERRO'
        nota_d3_00009 = 0.00

    d3_00009 = pd.DataFrame([{
        'Dimensão': 'D3_00009',
        'Resposta': resposta_d3_00009,
        'Descrição da Dimensão': 'Verifica a igualdade dos valores dos restos a pagar processados e não processados',
        'Nota': nota_d3_00009,
        'OBS': 'Anexo 07 do RREO e os Anexos 05 do RGF de todos os poderes/órgãos'
    }])

    return d3_00009, d3_00009_t


def d3_00010(df_rgf_1e, rgf, tipo_ente):
    if tipo_ente == "E":
        fontes_rgf1 = [
            df_rgf_1e,
            rgf.get("1l", pd.DataFrame()),
            rgf.get("1j", pd.DataFrame()),
            rgf.get("1m", pd.DataFrame()),
            rgf.get("1d", pd.DataFrame()),
        ]
    else:
        fontes_rgf1 = [
            df_rgf_1e,
            rgf.get("1l", pd.DataFrame()),
        ]

    filtrados_rgf1 = []
    for _df in fontes_rgf1:
        if isinstance(_df, pd.DataFrame) and not _df.empty and 'cod_conta' in _df.columns:
            _f = _df.query('cod_conta == "ReceitaCorrenteLiquidaLimiteLegal"')
            if not _f.empty:
                filtrados_rgf1.append(_f)

    if filtrados_rgf1:
        d3_raw = pd.concat(filtrados_rgf1, ignore_index=True)
        d3_raw = d3_raw[['instituicao', 'anexo', 'cod_conta', 'valor']].copy()
        d3_raw['valor'] = pd.to_numeric(d3_raw['valor'], errors='coerce').fillna(0.0)
        idx_min = d3_raw['valor'].idxmin()
        idx_max = d3_raw['valor'].idxmax()
        menor = d3_raw.loc[idx_min]
        maior = d3_raw.loc[idx_max]
        dif = float(maior['valor'] - menor['valor'])

        d3_00010_t = pd.DataFrame([
            {
                'fonte': 'Menor valor de RCL',
                'detalhe': str(menor.get('instituicao', '')),
                'valor': float(menor['valor']),
            },
            {
                'fonte': 'Maior valor de RCL',
                'detalhe': str(maior.get('instituicao', '')),
                'valor': float(maior['valor']),
            },
            {
                'fonte': 'Diferença (maior − menor)',
                'detalhe': 'Comparação entre poderes/órgãos do RGF 01',
                'valor': dif,
            },
        ])
    else:
        d3_00010_t = pd.DataFrame(columns=['fonte', 'detalhe', 'valor'])

    tolerancia = 0.01
    dif_max = float(d3_00010_t.loc[d3_00010_t['fonte'] == 'Diferença (maior − menor)', 'valor'].iloc[0]) if not d3_00010_t.empty else 0.0
    if not np.isclose(dif_max, 0.0, atol=tolerancia):
        resposta_d3_00010 = 'ERRO'
        nota_d3_00010 = 0.00
    else:
        resposta_d3_00010 = 'OK'
        nota_d3_00010 = 1.00

    d3_00010 = pd.DataFrame([{
        'Dimensão': 'D3_00010',
        'Resposta': resposta_d3_00010,
        'Descrição da Dimensão': 'Verifica a Igualdade da Receita Corrente Líquida (RCL) no Anexo 01 do RGF entre os poderes/órgãos',
        'Nota': nota_d3_00010,
        'OBS': 'Estados: E, L, J, M, D. Municípios: E e L.'
    }])

    return d3_00010, d3_00010_t


# ──────────────────────────────────────────────────────────────────────────────
# D3_00012 — Informação de valores negativos no RREO (E/DF/M, vigência 2019+).
#
# Estratégia inicial (segundo orientação do usuário): listar TODA linha do
# RREO com valor agregado < -tolerância e considerar ERRO se ao menos uma
# aparecer. Conforme forem identificados campos legítimos que podem assumir
# valores negativos (ex.: deduções, retificações), incluir aqui em
# `_D3_00012_EXCECOES_NEGATIVO` e o ente passa a marcar OK mesmo se essas
# linhas vierem negativas. A iteração inicial não tem exceções — calibração
# será feita olhando o desempenho do ranking fechado de 2024.
# ──────────────────────────────────────────────────────────────────────────────

# Cada exceção é um dict; uma linha é tratada como permitida negativa quando
# bate em TODAS as chaves do dict (AND). Chaves aceitas (qualquer subconjunto):
#
#   anexo         / anexo_prefixo         / anexo_contem
#   cod_conta     / cod_conta_prefixo     / cod_conta_contem
#   conta         / conta_prefixo         / conta_contem
#   coluna        / coluna_prefixo        / coluna_contem
#
# Comparações são feitas com a string já normalizada (`strip()`).
#
# Exemplos:
#   {'anexo': 'Anexo 01', 'coluna': 'SALDO (a-c)'}              # match exato
#   {'anexo_prefixo': 'Anexo 04', 'coluna_prefixo': 'RESULTADO'}  # AND de prefixos
#   {'cod_conta_prefixo': 'Deducoes'}                            # qualquer anexo
#   {'anexo': 'Anexo 06', 'coluna_contem': 'VARIAÇÃO CAMBIAL'}
_D3_00012_EXCECOES_NEGATIVO: tuple[dict, ...] = (
    # ── RREO Anexo 01 ─────────────────────────────────────────────────────
    # Coluna "SALDO (a-c)" pode aparecer negativa por construção
    # (Receitas Realizadas − Previsão Atualizada).
    {'anexo': 'Anexo 01', 'coluna': 'SALDO (a-c)'},
    # Transferências de capital: "No Bimestre (b)" e "% (b/a)" admitem negativo
    # (retificações / composição do indicador).
    {
        'anexo': 'Anexo 01',
        'cod_conta': 'TransferenciasDeCapitalDaUniaoEDeSuasEntidades',
        'coluna': 'No Bimestre (b)',
    },
    {
        'anexo': 'Anexo 01',
        'cod_conta': 'TransferenciasDeCapitalDaUniaoEDeSuasEntidades',
        'coluna': '% (b/a)',
    },
    {
        'anexo': 'Anexo 01',
        'cod_conta': 'TransferenciasDeCapital',
        'coluna': 'No Bimestre (b)',
    },
    {
        'anexo': 'Anexo 01',
        'cod_conta': 'TransferenciasDeCapital',
        'coluna': '% (b/a)',
    },
    # ── RREO Anexos 01 e 02 ───────────────────────────────────────────────
    # "DESPESAS EMPENHADAS NO BIMESTRE" admite valores negativos
    # (anulações/cancelamentos de empenho registrados no bimestre).
    # Aparece em Anexo 01 (Investimentos, DespesasDeCapital, InversoesFinanceiras,
    # OutrasDespesasCorrentesIntra) e em Anexo 02 (despesas por função).
    # Sem restrição de anexo (caso apareça em outros do RREO).
    {'coluna_contem': 'DESPESAS EMPENHADAS NO BIMESTRE'},
    # "DESPESAS LIQUIDADAS NO BIMESTRE" — mesmo racional (ajustes/anulações no bimestre).
    {'coluna_contem': 'DESPESAS LIQUIDADAS NO BIMESTRE'},
    # ── RREO Anexo 03 ─────────────────────────────────────────────────────
    # Colunas que começam com "<MR-" (mês de referência, ex.: "<MR-12>")
    # podem apresentar valores negativos para deduções/cancelamentos.
    {'anexo': 'Anexo 03', 'coluna_prefixo': '<MR-'},
    # ── RREO Anexo 04 e Anexo 04 RPPS ─────────────────────────────────────
    # Campos de "Resultado" são naturalmente negativos quando há déficit
    # (RREO4ResultadoRPPSFinanceiro, ResultadoAssociadoAInativosEPensionistas*,
    # ResultadoDosBeneficiosMantidosPeloTesouro). Cobre tanto cod_conta com
    # 'Resultado' quanto a descrição (conta) iniciando com 'RESULTADO'.
    {'anexo_prefixo': 'Anexo 04', 'cod_conta_contem': 'Resultado'},
    {'anexo_prefixo': 'Anexo 04', 'conta_prefixo': 'RESULTADO'},
    # ── RREO Anexo 06 ─────────────────────────────────────────────────────
    # Campos de "Resultado" (Resultado Primário/Nominal apurado em déficit,
    # MetaDeResultadoNominalFixada*). Cobre cod_conta com 'Resultado' ou
    # descrição (conta) com 'RESULTADO'.
    {'anexo': 'Anexo 06', 'cod_conta_contem': 'Resultado'},
    {'anexo': 'Anexo 06', 'conta_contem': 'RESULTADO'},
    # Variações: VariacaoCambial, VariacaoSaldoRPP,
    # VariacaoDoSaldoDePrecatoriosIntegrantesDaDC etc. — variações de saldo/
    # cambiais podem ser legitimamente negativas. Match pela descrição (conta)
    # contendo "VARIAÇÃO" (cobre cambial, RPP, precatórios e outras).
    {'anexo': 'Anexo 06', 'conta_contem': 'VARIAÇÃO'},
    # OutrosAjustes (XLIX): ajustes podem ser positivos ou negativos.
    {'anexo': 'Anexo 06', 'cod_conta': 'OutrosAjustes'},
)


# Campos sobre os quais aplicamos os modificadores '_prefixo' e '_contem'
# (todos os helpers de D3_00012 e D3_00013 reaproveitam esta tabela).
_D3_NEG_CAMPOS = ('anexo', 'cod_conta', 'conta', 'coluna')


def _d3_00012_norm_str(s):
    return str(s).strip() if s is not None and not (isinstance(s, float) and pd.isna(s)) else ''


def _d3_neg_match(excecao, valores):
    """Retorna True se o dict de exceção bate em TODAS as chaves declaradas
    sobre o `valores` (dict {'anexo': str, 'cod_conta': str, ...}).
    Suporta sufixos `_prefixo` (startswith) e `_contem` (substring)."""
    for campo in _D3_NEG_CAMPOS:
        v = valores.get(campo, '')
        if campo in excecao and excecao[campo] != v:
            return False
        chave_pref = f'{campo}_prefixo'
        if chave_pref in excecao and not v.startswith(excecao[chave_pref]):
            return False
        chave_cont = f'{campo}_contem'
        if chave_cont in excecao and excecao[chave_cont] not in v:
            return False
    return True


def _d3_00012_e_excecao(anexo, cod_conta, conta, coluna):
    """Retorna True se a tupla bate em pelo menos uma das exceções de
    `_D3_00012_EXCECOES_NEGATIVO`."""
    if not _D3_00012_EXCECOES_NEGATIVO:
        return False
    valores = {
        'anexo': _d3_00012_norm_str(anexo),
        'cod_conta': _d3_00012_norm_str(cod_conta),
        'conta': _d3_00012_norm_str(conta),
        'coluna': _d3_00012_norm_str(coluna),
    }
    for excecao in _D3_00012_EXCECOES_NEGATIVO:
        if _d3_neg_match(excecao, valores):
            return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# D3_00013 — Informação de valores negativos no RGF de TODOS os poderes/órgãos
# (CAPAG, vigência 2019+, E/DF/M).
#
# Mesma lógica da D3_00012, mas varrendo o dict `rgf` por combinação
# (anexo × poder/órgão). Estados/DF varrem E, L, J, M, D; Municípios varrem
# apenas E e L. Linhas legitimamente negativas podem ser cadastradas em
# `_D3_00013_EXCECOES_NEGATIVO`.
# ──────────────────────────────────────────────────────────────────────────────

# Cada exceção é um dict; uma linha é tratada como permitida negativa quando
# bate em TODAS as chaves do dict. Chaves aceitas (qualquer subconjunto):
#
#   anexo         / anexo_prefixo         / anexo_contem
#   poder         (sigla: E, L, J, M, D — sem variantes _prefixo / _contem)
#   cod_conta     / cod_conta_prefixo     / cod_conta_contem
#   conta         / conta_prefixo         / conta_contem
#   coluna        / coluna_prefixo        / coluna_contem
_D3_00013_EXCECOES_NEGATIVO: tuple[dict, ...] = (
    # ── RGF Anexo 1 ───────────────────────────────────────────────────────
    # Coluna "<MR>" (mês de referência) admite valores negativos para
    # deduções/retificações pontuais — ex.: DespesaComPessoalNaoComputada
    # IndenizacaoDemissaoVoluntaria. Aplicado a qualquer poder/órgão (E,L,J,M,D).
    # Equivalente ao "<MR-" do RREO Anexo 03.
    {'anexo_prefixo': 'Anexo 1 (', 'coluna_prefixo': '<MR'},
    # ── RGF Anexo 2 ───────────────────────────────────────────────────────
    # DCL pode ser legitimamente negativa: quando as deduções (depósitos,
    # disponibilidade vinculada etc.) superam a Dívida Consolidada Bruta,
    # a Dívida Líquida fica negativa. Cobre o valor absoluto e o percentual.
    {'anexo_prefixo': 'Anexo 2 (', 'cod_conta': 'DividaConsolidadaLiquida'},
    {'anexo_prefixo': 'Anexo 2 (', 'cod_conta': 'PercentualDaDCLSobreARCL'},
    # ── RGF Anexo 5 ───────────────────────────────────────────────────────
    # Disponibilidade de Caixa Líquida (antes/após inscrição em RP) é
    # naturalmente negativa quando os RP inscritos superam a Disp. Bruta.
    # cod_conta_contem 'DisponibilidadeDeCaixaLiquida' cobre tanto
    # `DisponibilidadeDeCaixaLiquida` quanto `DisponibilidadeDeCaixaLiquidaAposRP`.
    {'anexo_prefixo': 'Anexo 5 (', 'cod_conta_contem': 'DisponibilidadeDeCaixaLiquida'},
    # Disp. bruta (a) pode ficar negativa em RPPS / não vinculados (composição
    # do quadro no Anexo 5) — apenas Executivo conforme casos homologados.
    {
        'anexo_prefixo': 'Anexo 5 (',
        'poder': 'E',
        'cod_conta': 'DisponibilidadeDeCaixaBruta',
        'coluna': 'DISPONIBILIDADE DE CAIXA BRUTA (a)',
    },
)


def _d3_00013_e_excecao(anexo, poder, cod_conta, conta, coluna):
    """Retorna True se a tupla bate em ao menos uma das exceções."""
    if not _D3_00013_EXCECOES_NEGATIVO:
        return False

    valores = {
        'anexo': _d3_00012_norm_str(anexo),
        'cod_conta': _d3_00012_norm_str(cod_conta),
        'conta': _d3_00012_norm_str(conta),
        'coluna': _d3_00012_norm_str(coluna),
    }
    poder_norm = _d3_00012_norm_str(poder)

    for excecao in _D3_00013_EXCECOES_NEGATIVO:
        if 'poder' in excecao and excecao['poder'] != poder_norm:
            continue
        if _d3_neg_match(excecao, valores):
            return True
    return False


# Mapeamento dos poderes/órgãos do RGF. Estados/DF varrem todos; municípios só E/L.
_D3_00013_PODERES_ESTADO = ('E', 'L', 'J', 'M', 'D')
_D3_00013_PODERES_MUNICIPIO = ('E', 'L')
_D3_00013_PODER_LABEL = {
    'E': 'Executivo',
    'L': 'Legislativo',
    'J': 'Judiciário',
    'M': 'Ministério Público',
    'D': 'Defensoria Pública',
}


def d3_00014(df_rgf_1e, df_rgf_2e, df_rgf_3e, df_rgf_4e):
    emenda_indiv_rgf1e = pd.DataFrame()
    if isinstance(df_rgf_1e, pd.DataFrame) and not df_rgf_1e.empty and 'cod_conta' in df_rgf_1e.columns:
        filtro_rgf1e = df_rgf_1e['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf1e = df_rgf_1e[filtro_rgf1e]

    emenda_indiv_rgf2e = pd.DataFrame()
    if isinstance(df_rgf_2e, pd.DataFrame) and not df_rgf_2e.empty and 'coluna' in df_rgf_2e.columns and 'cod_conta' in df_rgf_2e.columns:
        df_rgf_2e_total = df_rgf_2e.query('coluna == "Até o 3º Quadrimestre"')
        filtro_rgf2e = df_rgf_2e_total['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf2e = df_rgf_2e_total[filtro_rgf2e]

    emenda_indiv_rgf3e = pd.DataFrame()
    if isinstance(df_rgf_3e, pd.DataFrame) and not df_rgf_3e.empty and 'coluna' in df_rgf_3e.columns and 'cod_conta' in df_rgf_3e.columns:
        df_rgf_3e_total = df_rgf_3e.query('coluna == "Até o 3º Quadrimestre"')
        filtro_rgf3e = df_rgf_3e_total['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf3e = df_rgf_3e_total[filtro_rgf3e]

    emenda_indiv_rgf4e = pd.DataFrame()
    if isinstance(df_rgf_4e, pd.DataFrame) and not df_rgf_4e.empty and 'cod_conta' in df_rgf_4e.columns:
        filtro_rgf4e = df_rgf_4e['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf4e = df_rgf_4e[filtro_rgf4e]

    if any(not df.empty for df in [emenda_indiv_rgf1e, emenda_indiv_rgf2e, emenda_indiv_rgf3e, emenda_indiv_rgf4e]):
        d3_00014_t = pd.concat([emenda_indiv_rgf1e, emenda_indiv_rgf2e, emenda_indiv_rgf3e, emenda_indiv_rgf4e], ignore_index=True)
    else:
        d3_00014_t = pd.DataFrame()

    if not d3_00014_t.empty and 'valor' in d3_00014_t.columns:
        d3_00014_t = d3_00014_t.reset_index(drop=True)
        d3_00014_t['DIF'] = d3_00014_t['valor'].diff()
        d3_00014_t.loc[d3_00014_t.index[0], 'DIF'] = 0

        tolerancia = 0.01
        condicao = ~np.isclose(d3_00014_t['DIF'], 0, atol=tolerancia)
        if condicao.any():
            resposta_d3_00014 = 'ERRO'
            nota_d3_00014 = 0.00
        else:
            resposta_d3_00014 = 'OK'
            nota_d3_00014 = 1.00

        d3_00014_t = d3_00014_t[['anexo', 'cod_conta', 'valor', 'DIF']].copy()
    else:
        resposta_d3_00014 = 'OK'
        nota_d3_00014 = 1.00
        d3_00014_t = pd.DataFrame(columns=['anexo', 'cod_conta', 'valor', 'DIF'])

    d3_00014 = pd.DataFrame([{
        'Dimensão': 'D3_00014',
        'Resposta': resposta_d3_00014,
        'Descrição da Dimensão': 'Verifica a igualdade do valor das Transferências Obrigatórias da União relativas às Emendas Individuais',
        'Nota': nota_d3_00014,
        'OBS': 'Anexos 1, 2, 3 e 4 do RGF do poder executivo'
    }])

    return d3_00014, d3_00014_t


def d3_00015(df_rgf_1e, df_rreo_3):
    emenda_indiv_rgf1e = pd.DataFrame()
    if isinstance(df_rgf_1e, pd.DataFrame) and not df_rgf_1e.empty and 'cod_conta' in df_rgf_1e.columns:
        filtro_rgf1e = df_rgf_1e['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rgf1e = df_rgf_1e[filtro_rgf1e]

    emenda_indiv_rreo3 = pd.DataFrame()
    if isinstance(df_rreo_3, pd.DataFrame) and not df_rreo_3.empty and 'coluna' in df_rreo_3.columns and 'cod_conta' in df_rreo_3.columns:
        df_rreo_3_total = df_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        filtro_rreo3 = df_rreo_3_total['cod_conta'].astype(str).str.contains('EmendasIndividuais', case=False, na=False)
        emenda_indiv_rreo3 = df_rreo_3_total[filtro_rreo3]

    if (emenda_indiv_rgf1e.empty and emenda_indiv_rreo3.empty) or 'valor' not in emenda_indiv_rgf1e.columns.union(emenda_indiv_rreo3.columns):
        resposta_d3_00015 = 'OK'
        nota_d3_00015 = 1.00
        d3_00015_t = pd.DataFrame(columns=['anexo', 'cod_conta', 'valor'])
    else:
        valor_rgf = float(pd.to_numeric(emenda_indiv_rgf1e.get('valor', pd.Series(dtype=float)), errors='coerce').fillna(0).sum())
        valor_rreo = float(pd.to_numeric(emenda_indiv_rreo3.get('valor', pd.Series(dtype=float)), errors='coerce').fillna(0).sum())
        dif = valor_rreo - valor_rgf

        tolerancia = 0.01
        if not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0):
            resposta_d3_00015 = 'ERRO'
            nota_d3_00015 = 0.00
        else:
            resposta_d3_00015 = 'OK'
            nota_d3_00015 = 1.00

        d3_00015_t = pd.DataFrame([
            {
                'anexo': 'RGF-Anexo 01',
                'cod_conta': 'TransferenciasObrigatoriasDaUniaoRelativasAsEmendasIndividuais',
                'valor': valor_rgf,
            },
            {
                'anexo': 'RREO-Anexo 03',
                'cod_conta': 'RREO3TransferenciasObrigatoriasDaUniaoRelativasAsEmendasIndividuais',
                'valor': valor_rreo,
            },
            {
                'anexo': 'Diferença (RREO 03 − RGF 01)',
                'cod_conta': 'Diferença entre os totais',
                'valor': dif,
            },
        ])

    d3_00015 = pd.DataFrame([{
        'Dimensão': 'D3_00015',
        'Resposta': resposta_d3_00015,
        'Descrição da Dimensão': 'Verifica a igualdade do valor das Transferências Obrigatórias da União relativas às Emendas Individuais',
        'Nota': nota_d3_00015,
        'OBS': 'Anexo 03 do RREO e Anexo 01 do RGF do poder executivo'
    }])

    return d3_00015, d3_00015_t


def d3_00016(df_rgf_1e, df_rreo_3):
    emenda_bancada_rgf1e = pd.DataFrame()
    if isinstance(df_rgf_1e, pd.DataFrame) and not df_rgf_1e.empty and 'cod_conta' in df_rgf_1e.columns:
        filtro_rgf1e = df_rgf_1e['cod_conta'].astype(str).str.contains('Bancada', case=False, na=False)
        emenda_bancada_rgf1e = df_rgf_1e[filtro_rgf1e]

    emenda_bancada_rreo3 = pd.DataFrame()
    if isinstance(df_rreo_3, pd.DataFrame) and not df_rreo_3.empty and 'cod_conta' in df_rreo_3.columns:
        df_rreo_3_base = df_rreo_3
        if 'coluna' in df_rreo_3.columns:
            df_rreo_3_base = df_rreo_3.query('coluna == "TOTAL (ÚLTIMOS 12 MESES)"')
        filtro_rreo3 = df_rreo_3_base['cod_conta'].astype(str).str.contains('Bancada', case=False, na=False)
        emenda_bancada_rreo3 = df_rreo_3_base[filtro_rreo3]

    if (emenda_bancada_rgf1e.empty and emenda_bancada_rreo3.empty) or 'valor' not in emenda_bancada_rgf1e.columns.union(emenda_bancada_rreo3.columns):
        resposta_d3_00016 = 'OK'
        nota_d3_00016 = 1.00
        d3_00016_t = pd.DataFrame(columns=['anexo', 'cod_conta', 'valor'])
    else:
        valor_rgf = float(pd.to_numeric(emenda_bancada_rgf1e.get('valor', pd.Series(dtype=float)), errors='coerce').fillna(0).sum())
        valor_rreo = float(pd.to_numeric(emenda_bancada_rreo3.get('valor', pd.Series(dtype=float)), errors='coerce').fillna(0).sum())
        dif = valor_rreo - valor_rgf

        tolerancia = 0.01
        if not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0):
            resposta_d3_00016 = 'ERRO'
            nota_d3_00016 = 0.00
        else:
            resposta_d3_00016 = 'OK'
            nota_d3_00016 = 1.00

        d3_00016_t = pd.DataFrame([
            {
                'anexo': 'RGF-Anexo 01',
                'cod_conta': 'TransferenciasObrigatoriasDaUniaoRelativasAsEmendasDeBancada',
                'valor': valor_rgf,
            },
            {
                'anexo': 'RREO-Anexo 03',
                'cod_conta': 'RREO3TransferenciasObrigatoriasDaUniaoRelativasAsEmendasDeBancada',
                'valor': valor_rreo,
            },
            {
                'anexo': 'Diferença (RREO 03 − RGF 01)',
                'cod_conta': 'Diferença entre os totais',
                'valor': dif,
            },
        ])

    d3_00016 = pd.DataFrame([{
        'Dimensão': 'D3_00016',
        'Resposta': resposta_d3_00016,
        'Descrição da Dimensão': 'Verifica a igualdade do valor das Transferências Obrigatórias da União relativas às Emendas de Bancada',
        'Nota': nota_d3_00016,
        'OBS': 'Anexo 03 do RREO e Anexo 01 do RGF do poder executivo'
    }])

    return d3_00016, d3_00016_t


def d3_00022(receita_corr, df_rreo_1):
    """
    Compara receitas correntes (MSC — saldo ending e categoria 1 da natureza da receita)
    com as receitas correntes do RREO Anexo 1 (coluna até o bimestre).
    """
    _cols_rreo = {'coluna', 'cod_conta', 'conta', 'valor'}
    if (
        receita_corr is None
        or not isinstance(receita_corr, pd.DataFrame)
        or receita_corr.empty
        or 'valor' not in receita_corr.columns
        or df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or not _cols_rreo.issubset(df_rreo_1.columns)
    ):
        d3_00022 = pd.DataFrame([{
            'Dimensão': 'D3_00022',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Igualdade das receitas correntes (MSC x RREO Anexo 1)',
            'Nota': None,
            'OBS': 'MSC (receitas correntes) e/ou RREO Anexo 1 indisponíveis ou incompletos'
        }])
        return d3_00022, pd.DataFrame()

    # Total MSC (uma linha identificada — evita duas linhas com o mesmo rótulo "RECEITAS CORRENTES")
    valor_msc = float(receita_corr['valor'].sum())

    receita_corr_rreo = df_rreo_1.query(
        'cod_conta == "ReceitasCorrentes" and coluna == "Até o Bimestre (c)"'
    )
    if receita_corr_rreo.empty:
        d3_00022 = pd.DataFrame([{
            'Dimensão': 'D3_00022',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Igualdade das receitas correntes (MSC x RREO Anexo 1)',
            'Nota': None,
            'OBS': 'Linha ReceitasCorrentes não encontrada no RREO Anexo 1'
        }])
        return d3_00022, pd.DataFrame()

    valor_rreo = float(receita_corr_rreo['valor'].sum())
    dif = valor_rreo - valor_msc

    d3_00022_t = pd.DataFrame([
        {
            'fonte': 'MSC',
            'detalhe': 'Receitas correntes (ending_balance, natureza 1)',
            'valor': valor_msc,
        },
        {
            'fonte': 'RREO — Anexo 1 (Balanço Orçamentário)',
            'detalhe': 'RECEITAS CORRENTES',
            'valor': valor_rreo,
        },
        {
            'fonte': 'Diferença (RREO − MSC)',
            'detalhe': 'Diferença entre os totais',
            'valor': dif,
        },
    ])

    tolerancia = 0.01
    condicao = not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0)

    if condicao:
        resposta_d3_00022 = 'ERRO'
        nota_d3_00022 = 0.00
    else:
        resposta_d3_00022 = 'OK'
        nota_d3_00022 = 1.00

    d3_00022 = pd.DataFrame([{
        'Dimensão': 'D3_00022',
        'Resposta': resposta_d3_00022,
        'Descrição da Dimensão': (
            'Verifica a igualdade das receitas correntes orçamentárias e intraorçamentárias '
            '(MSC x RREO Anexo 1)'
        ),
        'Nota': nota_d3_00022,
        'OBS': 'Anexo 1 do RREO e valores da MSC (saldo final — receitas correntes, categoria 1)'
    }])

    return d3_00022, d3_00022_t


def d3_00023(receita_capi, df_rreo_1):
    """
    Compara receitas de capital (MSC — saldo ending, categoria 2 da natureza da receita)
    com as receitas de capital do RREO Anexo 1 (coluna até o bimestre).
    """
    _cols_rreo = {'coluna', 'cod_conta', 'conta', 'valor'}
    if (
        receita_capi is None
        or not isinstance(receita_capi, pd.DataFrame)
        or receita_capi.empty
        or 'valor' not in receita_capi.columns
        or df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or not _cols_rreo.issubset(df_rreo_1.columns)
    ):
        d3_00023 = pd.DataFrame([{
            'Dimensão': 'D3_00023',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Igualdade das receitas de capital (MSC x RREO Anexo 1)',
            'Nota': None,
            'OBS': 'MSC (receitas de capital) e/ou RREO Anexo 1 indisponíveis ou incompletos'
        }])
        return d3_00023, pd.DataFrame()

    valor_msc = float(receita_capi['valor'].sum())

    receita_capi_rreo = df_rreo_1.query(
        'cod_conta == "ReceitasDeCapital" and coluna == "Até o Bimestre (c)"'
    )
    if receita_capi_rreo.empty:
        d3_00023 = pd.DataFrame([{
            'Dimensão': 'D3_00023',
            'Resposta': 'N/A',
            'Descrição da Dimensão': 'Igualdade das receitas de capital (MSC x RREO Anexo 1)',
            'Nota': None,
            'OBS': 'Linha ReceitasDeCapital não encontrada no RREO Anexo 1'
        }])
        return d3_00023, pd.DataFrame()

    valor_rreo = float(receita_capi_rreo['valor'].sum())
    dif = valor_rreo - valor_msc

    d3_00023_t = pd.DataFrame([
        {
            'fonte': 'MSC',
            'detalhe': 'Receitas de capital (ending_balance, natureza 2)',
            'valor': valor_msc,
        },
        {
            'fonte': 'RREO — Anexo 1 (Balanço Orçamentário)',
            'detalhe': 'RECEITAS DE CAPITAL',
            'valor': valor_rreo,
        },
        {
            'fonte': 'Diferença (RREO − MSC)',
            'detalhe': 'Diferença entre os totais',
            'valor': dif,
        },
    ])

    tolerancia = 0.01
    condicao = not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0)

    if condicao:
        resposta_d3_00023 = 'ERRO'
        nota_d3_00023 = 0.00
    else:
        resposta_d3_00023 = 'OK'
        nota_d3_00023 = 1.00

    d3_00023 = pd.DataFrame([{
        'Dimensão': 'D3_00023',
        'Resposta': resposta_d3_00023,
        'Descrição da Dimensão': (
            'Verifica a igualdade das receitas de capital orçamentárias e intraorçamentárias '
            '(MSC x RREO Anexo 1)'
        ),
        'Nota': nota_d3_00023,
        'OBS': 'Anexo 1 do RREO e valores da MSC (saldo final — receitas de capital, categoria 2)'
    }])

    return d3_00023, d3_00023_t


def _comparar_despesas_msc_rreo(
    despesa_base,
    df_rreo_1,
    *,
    codigos_msc_emp,
    codigos_msc_liq,
    codigos_msc_pago,
    codigos_rreo,
    dimensao_codigo,
    descricao_dimensao,
    obs_dimensao,
    detalhe_msc,
):
    cols_msc = {'conta_contabil', 'valor'}
    cols_rreo = {'coluna', 'cod_conta', 'valor'}
    if (
        despesa_base is None
        or not isinstance(despesa_base, pd.DataFrame)
        or despesa_base.empty
        or not cols_msc.issubset(despesa_base.columns)
        or df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or not cols_rreo.issubset(df_rreo_1.columns)
    ):
        d3_na = pd.DataFrame([{
            'Dimensão': dimensao_codigo,
            'Resposta': 'N/A',
            'Descrição da Dimensão': descricao_dimensao,
            'Nota': None,
            'OBS': 'MSC (despesas) e/ou RREO Anexo 1 indisponíveis ou incompletos',
        }])
        return d3_na, pd.DataFrame()

    # Alinhar ao D4 e ao notebook: só saldo final (ending_balance). Sem isso, soma vários
    # tipo_valor (ex.: period_change + ending_balance) e o total MSC fica ~2× o RREO.
    desp_msc = despesa_base.copy()
    if 'tipo_valor' in desp_msc.columns:
        desp_msc = desp_msc[desp_msc['tipo_valor'].eq('ending_balance')]
    if desp_msc.empty:
        d3_na = pd.DataFrame([{
            'Dimensão': dimensao_codigo,
            'Resposta': 'N/A',
            'Descrição da Dimensão': descricao_dimensao,
            'Nota': None,
            'OBS': 'MSC sem linhas ending_balance para o recorte de despesas (dezembro)',
        }])
        return d3_na, pd.DataFrame()

    # Desconsiderar linhas sem natureza da despesa (MSC x RREO exige ND explícita no detalhamento)
    if 'natureza_despesa' in desp_msc.columns:
        _nd = desp_msc['natureza_despesa']
        desp_msc = desp_msc[
            _nd.notna() & (_nd.astype(str).str.strip() != '')
        ].copy()
    if desp_msc.empty:
        d3_na = pd.DataFrame([{
            'Dimensão': dimensao_codigo,
            'Resposta': 'N/A',
            'Descrição da Dimensão': descricao_dimensao,
            'Nota': None,
            'OBS': 'MSC sem linhas com natureza de despesa informada no recorte (ending_balance)',
        }])
        return d3_na, pd.DataFrame()

    def _soma_msc(contas):
        return float(desp_msc[desp_msc['conta_contabil'].isin(contas)]['valor'].sum())

    def _soma_rreo(coluna):
        return float(
            df_rreo_1[
                df_rreo_1['cod_conta'].isin(codigos_rreo)
                & (df_rreo_1['coluna'] == coluna)
            ]['valor'].sum()
        )

    msc_emp = _soma_msc(codigos_msc_emp)
    rreo_emp = _soma_rreo('DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)')
    dif_emp = rreo_emp - msc_emp

    msc_liq = _soma_msc(codigos_msc_liq)
    rreo_liq = _soma_rreo('DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)')
    dif_liq = rreo_liq - msc_liq

    msc_pago = _soma_msc(codigos_msc_pago)
    rreo_pago = _soma_rreo('DESPESAS PAGAS ATÉ O BIMESTRE (j)')
    dif_pago = rreo_pago - msc_pago

    d3_t = pd.DataFrame([
        {
            'fonte': 'MSC',
            'despesas_empenhadas': msc_emp,
            'despesas_liquidadas': msc_liq,
            'despesas_pagas': msc_pago,
        },
        {
            'fonte': 'RREO — Anexo 1',
            'despesas_empenhadas': rreo_emp,
            'despesas_liquidadas': rreo_liq,
            'despesas_pagas': rreo_pago,
        },
        {
            'fonte': 'Diferença (RREO − MSC)',
            'despesas_empenhadas': dif_emp,
            'despesas_liquidadas': dif_liq,
            'despesas_pagas': dif_pago,
        },
    ])

    tolerancia = 0.01
    condicao = [
        not np.isclose(dif_emp, 0.0, atol=tolerancia, rtol=0.0),
        not np.isclose(dif_liq, 0.0, atol=tolerancia, rtol=0.0),
        not np.isclose(dif_pago, 0.0, atol=tolerancia, rtol=0.0),
    ]

    if any(condicao):
        resposta = 'ERRO'
        nota = 0.00
    else:
        resposta = 'OK'
        nota = 1.00

    d3_df = pd.DataFrame([{
        'Dimensão': dimensao_codigo,
        'Resposta': resposta,
        'Descrição da Dimensão': descricao_dimensao,
        'Nota': nota,
        'OBS': obs_dimensao,
    }])

    return d3_df, d3_t


def d3_00024(despesa_corr, df_rreo_1):
    return _comparar_despesas_msc_rreo(
        despesa_corr,
        df_rreo_1,
        codigos_msc_emp=['622130400', '622130500', '622130600', '622130700', '622130300', '622130200', '622130100'],
        codigos_msc_liq=['622130400', '622130700', '622130300'],
        codigos_msc_pago=['622130400'],
        codigos_rreo=['DespesasCorrentes', 'DespesasCorrentesIntra'],
        dimensao_codigo='D3_00024',
        descricao_dimensao='Verifica a igualdade das despesas correntes orçamentárias e intraorçamentárias (MSC x RREO Anexo 1)',
        obs_dimensao='Anexo 1 do RREO e valores da MSC de dezembro (despesas correntes)',
        detalhe_msc='Despesas correntes (MSC dezembro)',
    )


def d3_00025(despesa_capi, df_rreo_1):
    return _comparar_despesas_msc_rreo(
        despesa_capi,
        df_rreo_1,
        codigos_msc_emp=['622130400', '622130500', '622130600', '622130700', '622130300', '622130200', '622130100'],
        codigos_msc_liq=['622130400', '622130700', '622130300'],
        codigos_msc_pago=['622130400'],
        codigos_rreo=['DespesasDeCapital', 'DespesasDeCapitalIntra', 'AmortizacaoRefinanciamentoDaDivida'],
        dimensao_codigo='D3_00025',
        descricao_dimensao='Verifica a igualdade das despesas de capital orçamentárias e intraorçamentárias (MSC x RREO Anexo 1)',
        obs_dimensao='Anexo 1 do RREO e valores da MSC de dezembro (despesas de capital)',
        detalhe_msc='Despesas de capital (MSC dezembro)',
    )


# ──────────────────────────────────────────────────────────────────────────────
# D3_00026 — Caixa e Equivalentes de Caixa Bruta por grupos de Fontes de Recursos
# (MSC dez × RGF Anexo 5 Executivo). CAPAG, oficial desde 2023, escopo E/DF/M.
# ──────────────────────────────────────────────────────────────────────────────

# Mapa STN — fonte de recursos pelos 3 últimos dígitos do código de FR → grupo
# padronizado do RGF Anexo 5. Fonte: quadro de classificação das vinculações
# do RGF (Manual STN, Anexo 5 — DisponibilidadeDeCaixaBruta).
_D3_00026_FR_GRUPO = {
    '500': '1.1 Recursos Não Vinculados de Impostos',
    '501': '1.2 Outros Recursos não Vinculados',
    '502': '1.2 Outros Recursos não Vinculados',
    '503': '1.2 Outros Recursos não Vinculados',
    '540': '2.1.1 Transferências do FUNDEB',
    '541': '2.1.1 Transferências do FUNDEB',
    '542': '2.1.1 Transferências do FUNDEB',
    '543': '2.1.1 Transferências do FUNDEB',
    '546': '2.1.1 Transferências do FUNDEB',
    '544': '2.1.2 Outros Recursos Vinculados à Educação',
    '545': '2.1.2 Outros Recursos Vinculados à Educação',
    '550': '2.1.2 Outros Recursos Vinculados à Educação',
    '551': '2.1.2 Outros Recursos Vinculados à Educação',
    '552': '2.1.2 Outros Recursos Vinculados à Educação',
    '553': '2.1.2 Outros Recursos Vinculados à Educação',
    '569': '2.1.2 Outros Recursos Vinculados à Educação',
    '570': '2.1.2 Outros Recursos Vinculados à Educação',
    '571': '2.1.2 Outros Recursos Vinculados à Educação',
    '572': '2.1.2 Outros Recursos Vinculados à Educação',
    '573': '2.1.2 Outros Recursos Vinculados à Educação',
    '574': '2.1.2 Outros Recursos Vinculados à Educação',
    '575': '2.1.2 Outros Recursos Vinculados à Educação',
    '576': '2.1.2 Outros Recursos Vinculados à Educação',
    '599': '2.1.2 Outros Recursos Vinculados à Educação',
    '600': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '601': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '602': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '603': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '604': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '605': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '621': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '622': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    '631': '2.2.2 Outros Recursos Vinculados à Saúde',
    '632': '2.2.2 Outros Recursos Vinculados à Saúde',
    '633': '2.2.2 Outros Recursos Vinculados à Saúde',
    '634': '2.2.2 Outros Recursos Vinculados à Saúde',
    '635': '2.2.2 Outros Recursos Vinculados à Saúde',
    '636': '2.2.2 Outros Recursos Vinculados à Saúde',
    '659': '2.2.2 Outros Recursos Vinculados à Saúde',
    '660': '2.3 Recursos Vinculados à Assistência Social',
    '661': '2.3 Recursos Vinculados à Assistência Social',
    '662': '2.3 Recursos Vinculados à Assistência Social',
    '665': '2.3 Recursos Vinculados à Assistência Social',
    '669': '2.3 Recursos Vinculados à Assistência Social',
    '803': '2.4 Recursos Vinculados à Previdência Social (Exceto ao RPPS)',
    '804': '2.4 Recursos Vinculados à Previdência Social (Exceto ao RPPS)',
    '700': '2.5.1 Transferências de Convênios e Instrumentos Congêneres (exceto Educação, Saúde e Assistência)',
    '701': '2.5.1 Transferências de Convênios e Instrumentos Congêneres (exceto Educação, Saúde e Assistência)',
    '702': '2.5.1 Transferências de Convênios e Instrumentos Congêneres (exceto Educação, Saúde e Assistência)',
    '703': '2.5.1 Transferências de Convênios e Instrumentos Congêneres (exceto Educação, Saúde e Assistência)',
    '704': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '705': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '706': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '707': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '708': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '709': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '710': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '711': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '712': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '713': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '714': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '715': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '716': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '717': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '718': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '719': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '720': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '721': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '722': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '747': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '748': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '749': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    '754': '2.6.1 Recursos de Operações de Crédito (exceto vinculados à Educação e à Saúde)',
    '755': '2.6.2 Recursos de Alienação de Bens/Ativos',
    '756': '2.6.2 Recursos de Alienação de Bens/Ativos',
    '762': '2.6.2 Recursos de Alienação de Bens/Ativos',
    '759': '2.6.3 Recursos Vinculados a Fundos (exceto Educação, Saúde, Assistência e Previdência)',
    '763': '2.6.3 Recursos Vinculados a Fundos (exceto Educação, Saúde, Assistência e Previdência)',
    '750': '2.6.4 Outras Vinculações Legais',
    '751': '2.6.4 Outras Vinculações Legais',
    '752': '2.6.4 Outras Vinculações Legais',
    '753': '2.6.4 Outras Vinculações Legais',
    '757': '2.6.4 Outras Vinculações Legais',
    '758': '2.6.4 Outras Vinculações Legais',
    '760': '2.6.4 Outras Vinculações Legais',
    '761': '2.6.4 Outras Vinculações Legais',
    '799': '2.6.4 Outras Vinculações Legais',
    '860': '2.7 Recursos Extraorçamentários',
    '861': '2.7 Recursos Extraorçamentários',
    '862': '2.7 Recursos Extraorçamentários',
    '869': '2.7 Recursos Extraorçamentários',
    '880': '2.8 Outras Vinculações',
    '898': '2.8 Outras Vinculações',
    '899': '2.8 Outras Vinculações',
    '800': '3.1 RPPS - Fundo em Capitalização (Plano Previdenciário)',
    '801': '3.2 RPPS - Fundo em Repartição (Plano Financeiro)',
    '802': '3.3 RPPS - Taxa de Administração',
}


# Rótulo na coluna `conta` do RGF Anexo 5 (DisponibilidadeDeCaixaBruta)
# → grupo padronizado. Apenas linhas detalhadas (subtotais e totais I/II/III
# são descartados implicitamente — chaves não presentes neste mapa).
_D3_00026_RGF_LABEL_GRUPO = {
    'Recursos Não Vinculados de Impostos': '1.1 Recursos Não Vinculados de Impostos',
    'Outros Recursos não Vinculados': '1.2 Outros Recursos não Vinculados',
    'Transferências do FUNDEB': '2.1.1 Transferências do FUNDEB',
    'Outros Recursos Vinculados à Educação': '2.1.2 Outros Recursos Vinculados à Educação',
    'Transferências Fundo a Fundo de Recursos do SUS': '2.2.1 Transferências Fundo a Fundo de Recursos do SUS',
    'Outros Recursos Vinculados à Saúde': '2.2.2 Outros Recursos Vinculados à Saúde',
    'Recursos Vinculados à Assistência Social': '2.3 Recursos Vinculados à Assistência Social',
    'Recursos Vinculados à Previdência Social (Exceto ao RPPS)': '2.4 Recursos Vinculados à Previdência Social (Exceto ao RPPS)',
    'Transferências de Convênios e Instrumentos Congêneres (exceto Educação, Saúde e Assistência)': '2.5.1 Transferências de Convênios e Instrumentos Congêneres (exceto Educação, Saúde e Assistência)',
    'Outras Vinculações Decorrentes de Transferências': '2.5.2 Outras Vinculações Decorrentes de Transferências',
    'Recursos de Operações de Crédito (exceto vinculados à Educação e à Saúde)': '2.6.1 Recursos de Operações de Crédito (exceto vinculados à Educação e à Saúde)',
    'Recursos de Alienação de Bens/Ativos': '2.6.2 Recursos de Alienação de Bens/Ativos',
    'Recursos Vinculados a Fundos (exceto Educação, Saúde, Assistência e Previdência)': '2.6.3 Recursos Vinculados a Fundos (exceto Educação, Saúde, Assistência e Previdência)',
    'Outras Vinculações Legais': '2.6.4 Outras Vinculações Legais',
    'Recursos Extraorçamentários': '2.7 Recursos Extraorçamentários',
    'Outras Vinculações': '2.8 Outras Vinculações',
    'Recursos Vinculados ao RPPS - Fundo em Capitalização (Plano Previdenciário)': '3.1 RPPS - Fundo em Capitalização (Plano Previdenciário)',
    'Recursos Vinculados ao RPPS - Fundo em Repartição (Plano Financeiro)': '3.2 RPPS - Fundo em Repartição (Plano Financeiro)',
    'Recursos Vinculados ao RPPS - Taxa de Administração': '3.3 RPPS - Taxa de Administração',
}


# Rótulos dos códigos de poder_orgao mais comuns na MSC (Manual STN — Tabela
# de Poder e Órgão). Usado apenas no diagnóstico da D3_00026 quando há
# divergência grupo a grupo, para o usuário identificar rapidamente qual
# poder/órgão da MSC está sobrando frente ao RGF Anexo 5 consolidado.
_D3_00026_PO_LABEL = {
    '10111': 'Executivo Estadual — Direta',
    '10112': 'Executivo Estadual — Indireta',
    '10131': 'Executivo Municipal — Direta',
    '10132': 'Executivo Municipal — Indireta',
    '10121': 'Legislativo Estadual',
    '10141': 'Legislativo Municipal',
    '20211': 'Tribunal de Contas',
    '30311': 'Judiciário — Direta',
    '30312': 'Judiciário — Indireta',
    '30390': 'Defensoria Pública',
    '40411': 'Ministério Público — Direta',
    '40412': 'Ministério Público — Indireta',
    '50511': 'Tribunal de Contas',
    '60611': 'RPPS',
}


_RREO_BO_COLS = {'coluna', 'cod_conta', 'valor'}

# Rubricas do Anexo 6 somadas para confronto com TotalDespesas do Anexo 1 (D3_00027)
_D3_00027_RREO6_DESP = (
    'DespesasCorrentesExcetoFontesRPPS',
    'DespesasPrimariasCorrentesComFontesRPPS',
    'DespesasNaoPrimariasCorrentesComFontesRPPS',
    'DespesasDeCapitalExcetoFontesRPPS',
    'RREO6ReservaDeContingencia',
    'DespesasPrimariasDeCapitalComFontesRPPS',
    'DespesasNaoPrimariasDeCapitalComFontesRPPS',
)   

# Rubricas do Anexo 6 para receitas realizadas e previsão (D3_00028)
_D3_00028_RREO6_REC = (
    'ReceitasCorrentesExcetoFontesRPPS',
    'ReceitasPrimariasCorrentesComFontesRPPS',
    'ReceitasNaoPrimariasCorrentesComFontesRPPS',
    'ReceitasDeCapitalExcetoFontesRPPS',
    'ReceitasPrimariasDeCapitalComFontesRPPS',
    'ReceitasNaoPrimariasDeCapitalComFontesRPPS',
)


def _d3_00029_norm_cod_id(series):
    return (
        series.astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .str.strip()
    )


def _d3_00029_fonte_codigo_4d(series):
    """
    Código de fonte em 4 dígitos, alinhado ao D1 (`_fonte_msc_codigo_e_tres_digitos`):
    remove sufixo .0 do texto antes de tirar não-dígitos — evita que 1605.0 vire '16050' e falhe o filtro.
    """
    s = series.astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    digitos = s.str.replace(r'\D', '', regex=True)
    curto = digitos.str.len() < 4
    normalizado = digitos.where(~curto, digitos.str.zfill(4))
    return normalizado.str[-4:]


def _d3_00029_po_por_ente(tipo_ente):
    """
    Metodologia STN (D3_00029): PO executivo, RPPS e defensoria pública.
    Códigos alinhados à lista de poder/órgão válida na MSC (D1_00019 / Portaria STN).
    """
    if tipo_ente == "M":
        return {'10131', '10132'}
    return {'10111', '10112', '60611'}


def _d3_00029_nd_mask(nd: pd.Series) -> pd.Series:
    """
    ND didática MCASP → só dígitos na API. Inclui naturezas longas (substring).
    - 3.1.XX.XX.XX → começa por 31 (após remover zeros à esquerda)
    - 3.3.XX.34.XX → bloco 33dd34dd em qualquer posição
    - 3.3.90.91.34 e 3.3.90.92.34 → contém 33909134 ou 33909234
    """
    mask_31 = nd.str.startswith('31', na=False)
    mask_33_34 = nd.str.contains(r'33\d{2}34\d{2}', na=False, regex=True)
    mask_fixos = nd.str.contains('33909134', na=False) | nd.str.contains('33909234', na=False)
    return mask_31 | mask_33_34 | mask_fixos


##################################################################
##################################################################
##################################################################

# NOVAS DIMENSÕES 2025

##################################################################
##################################################################
##################################################################


_REMOVED_ANALYSES_ARITY = {'d3_00011': 2, 'd3_00012': 2, 'd3_00013': 2, 'd3_00017': 2, 'd3_00021': 2, 'd3_00026': 2, 'd3_00027': 2, 'd3_00028': 2, 'd3_00029': 2, 'd3_00030': 2, 'd3_00032': 2, 'd3_00033': 2, 'd3_00034': 2, 'd3_00035': 2, 'd3_00037': 2, 'd3_00038': 2, 'd3_00039': 2, 'd3_00040': 2, 'd3_00044': 2, 'd3_00045': 2, 'd3_00046': 2, 'd3_00048': 2, 'd3_00049': 2, 'd3_00050': 2, 'd3_00051': 2, 'd3_00052': 2, 'd3_00054': 2, 'd3_00055': 2, 'd3_00056': 2}


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
