import re

import numpy as np
import pandas as pd

from api_ranking.analysis.common import fonte_msc_codigo_e_tres_digitos


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

    # RPP e RPNP representam categorias distintas e precisam conferir
    # individualmente. Avaliar apenas o total permitiria que uma divergência
    # positiva em uma categoria anulasse uma divergência negativa na outra.
    diferencas_por_tipo = np.array([abs(dif_rpp), abs(dif_rpnp_tipo)], dtype=float)
    diferencas_sao_zero = np.isclose(
        diferencas_por_tipo,
        0,
        atol=tolerancia_zero,
        rtol=0,
    ).all()

    if diferencas_sao_zero:
        resposta_d3_00009 = 'OK'
        nota_d3_00009 = 1.00
    elif (diferencas_por_tipo <= tolerancia_centavos).all():
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


def _d3_00029_fonte_codigo_4d(series):
    """Mantém a forma de quatro dígitos usada pela regra D3_00026."""
    code_4, _, _ = fonte_msc_codigo_e_tres_digitos(series)
    return code_4


def d3_00017(df_rreo_6, df_rreo_7):
    descricao = (
        'Igualdade entre os Restos a Pagar (Processados e Não-Processados) '
        'Pagos no Exercício'
    )
    colunas_rreo_6 = {'coluna', 'cod_conta', 'valor'}
    colunas_rreo_7 = {'conta', 'cod_conta', 'valor'}
    if (
        not isinstance(df_rreo_6, pd.DataFrame)
        or df_rreo_6.empty
        or not colunas_rreo_6.issubset(df_rreo_6.columns)
        or not isinstance(df_rreo_7, pd.DataFrame)
        or df_rreo_7.empty
        or not colunas_rreo_7.issubset(df_rreo_7.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00017',
            'Resposta': 'N/A',
            'Descrição da Dimensão': descricao,
            'Nota': None,
            'OBS': 'RREO Anexo 6 e/ou Anexo 7 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    rpp_pago_rreo_7 = df_rreo_7.query(
        'cod_conta == "RestosAPagarProcessadosENaoProcessadosLiquidadosPagos" '
        '& conta == "TOTAL (III) = (I + II)"'
    )
    rpp_pago_rreo_7['dimensao'] = 'D3_00017_RPP'
    rpp_pago_rreo_7 = rpp_pago_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpp_pago_rreo_6 = df_rreo_6.query(
        'coluna == "RESTOS A PAGAR PROCESSADOS PAGOS (b)" & ('
        'cod_conta == "DespesasCorrentesExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasCorrentesComFontesRPPS" | '
        'cod_conta == "DespesasDeCapitalExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasDeCapitalComFontesRPPS" | '
        'cod_conta == "RREO6ReservaDeContingencia")'
    )
    rpp_pago_rreo_6['dimensao'] = 'D3_00017_RPP'
    rpp_pago_rreo_6 = rpp_pago_rreo_6.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pago_rreo_7 = df_rreo_7.query(
        'cod_conta == "RestosAPagarNaoProcessadosPagos" & conta == "TOTAL (III) = (I + II)"'
    )
    rpnp_pago_rreo_7['dimensao'] = 'D3_00017_RPNP'
    rpnp_pago_rreo_7 = rpnp_pago_rreo_7.groupby('dimensao').agg({'valor': 'sum'})

    rpnp_pago_rreo_6 = df_rreo_6.query(
        'coluna == "PAGOS (c)" & ('
        'cod_conta == "DespesasCorrentesExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasCorrentesComFontesRPPS" | '
        'cod_conta == "DespesasDeCapitalExcetoFontesRPPS" | '
        'cod_conta == "DespesasPrimariasDeCapitalComFontesRPPS" | '
        'cod_conta == "RREO6ReservaDeContingencia")'
    )
    rpnp_pago_rreo_6['dimensao'] = 'D3_00017_RPNP'
    rpnp_pago_rreo_6 = rpnp_pago_rreo_6.groupby('dimensao').agg({'valor': 'sum'})

    if any(
        quadro.empty
        for quadro in (
            rpp_pago_rreo_7,
            rpp_pago_rreo_6,
            rpnp_pago_rreo_7,
            rpnp_pago_rreo_6,
        )
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00017',
            'Resposta': 'N/A',
            'Descrição da Dimensão': descricao,
            'Nota': None,
            'OBS': 'Linhas de RPP e/ou RPNP pagos ausentes nos Anexos 6 ou 7 do RREO',
        }]), pd.DataFrame()

    rpp_7 = float(rpp_pago_rreo_7['valor'].sum()) if not rpp_pago_rreo_7.empty else 0.0
    rpp_6 = float(rpp_pago_rreo_6['valor'].sum()) if not rpp_pago_rreo_6.empty else 0.0
    rpnp_7 = float(rpnp_pago_rreo_7['valor'].sum()) if not rpnp_pago_rreo_7.empty else 0.0
    rpnp_6 = float(rpnp_pago_rreo_6['valor'].sum()) if not rpnp_pago_rreo_6.empty else 0.0

    dif_rpp = rpp_7 - rpp_6
    dif_rpnp = rpnp_7 - rpnp_6

    d3_00017_t = pd.DataFrame([
        {
            'fonte': 'RREO — Anexo 07',
            'rpp_pagos': rpp_7,
            'rpnp_pagos': rpnp_7,
        },
        {
            'fonte': 'RREO — Anexo 06',
            'rpp_pagos': rpp_6,
            'rpnp_pagos': rpnp_6,
        },
        {
            'fonte': 'Diferença (Anexo 07 − Anexo 06)',
            'rpp_pagos': dif_rpp,
            'rpnp_pagos': dif_rpnp,
        },
    ])

    tolerancia = 0.01
    condicao = [
        not np.isclose(dif_rpp, 0.0, atol=tolerancia, rtol=0.0),
        not np.isclose(dif_rpnp, 0.0, atol=tolerancia, rtol=0.0),
    ]
    if any(condicao):
        resposta_d3_00017 = 'ERRO'
        nota_d3_00017 = 0.00
    else:
        resposta_d3_00017 = 'OK'
        nota_d3_00017 = 1.00

    d3_00017 = pd.DataFrame([{
        'Dimensão': 'D3_00017',
        'Resposta': resposta_d3_00017,
        'Descrição da Dimensão': descricao,
        'Nota': nota_d3_00017,
        'OBS': 'Anexo 6 do RREO e Anexo 7 do RREO'
    }])

    return d3_00017, d3_00017_t


def d3_00026(msc_dez, df_rgf_5e):
    """
    CAPAG — Igualdade do saldo de Caixa e Equivalentes de Caixa Bruta por
    grupos de Fontes de Recursos entre a MSC de dezembro (apenas Poder
    Executivo) e o RGF Anexo 5 do Poder Executivo.

    Escopo restrito ao Executivo (Direta + Indireta) em ambos os lados,
    evitando particularidades de layout/preenchimento do RGF Anexo 5 dos
    demais poderes (Legislativo, Judiciário, MP, Defensoria) e
    descasamentos com órgãos que não entregam o anexo (TC, RPPS).

    Filtros aplicados:
    - MSC dezembro (tipo_valor = ending_balance):
        * conta_contabil iniciando em 11111, 11121 ou 11131 (Caixa e
          Equivalentes de Caixa Bruta segundo PCASP);
        * poder_orgao restrito ao Executivo (Direta + Indireta):
            Estados ........ 10111 + 10112
            DF ............. 10121 + 10122
            Municípios ..... 10131 + 10132
        * fonte_recursos agrupada pelos 3 últimos dígitos do código de FR
          conforme mapa STN do RGF Anexo 5.
    - RGF Anexo 5 — apenas Executivo (df_rgf_5e):
        * cod_conta = DisponibilidadeDeCaixaBruta;
        * coluna `conta` em uma das linhas detalhadas (totais I/II/III e
          subtotais hierárquicos — Recursos Vinculados à Educação,
          Recursos Vinculados à Saúde, Demais Vinculações Decorrentes de
          Transferências, Demais Vinculações Legais — ficam fora do mapa
          e por isso não entram no critério).

    Regra: para cada grupo de FR, MSC == RGF (tolerância 0,01). OK quando
    todos os grupos batem; ERRO quando há divergência em algum grupo.
    N/A apenas quando MSC ou RGF Anexo 5 (Executivo) estão indisponíveis.
    """
    desc = (
        'Verifica os valores de Caixa e Equivalentes de Caixa Bruta por grupos '
        'de Fontes de Recursos do RGF Anexo 5 do Executivo contra a MSC de dezembro '
        '(escopo restrito ao Poder Executivo)'
    )
    obs_base = (
        'RGF Anexo 5 (Executivo): cod_conta DisponibilidadeDeCaixaBruta, linhas '
        'detalhadas (sem TOTAL (I)/(II)/(III) e subtotais). MSC dezembro '
        '(ending_balance): conta_contabil 11111/11121/11131; poder_orgao '
        'apenas Executivo (Direta+Indireta) — Estados 10111/10112, DF 10121/10122, '
        'Municípios 10131/10132; fonte_recursos pelos 3 últimos dígitos (mapa STN).'
    )

    msc_need = {'tipo_valor', 'conta_contabil', 'fonte_recursos', 'valor', 'poder_orgao'}
    rgf_need = {'cod_conta', 'conta', 'valor'}

    def _df_ok(df, need):
        return (
            df is not None
            and isinstance(df, pd.DataFrame)
            and not df.empty
            and need.issubset(df.columns)
        )

    if not _df_ok(msc_dez, msc_need):
        return pd.DataFrame([{
            'Dimensão': 'D3_00026',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': (
                'MSC de dezembro indisponível ou sem colunas necessárias '
                '(tipo_valor, conta_contabil, fonte_recursos, poder_orgao, valor)'
            ),
        }]), pd.DataFrame()

    if not _df_ok(df_rgf_5e, rgf_need):
        return pd.DataFrame([{
            'Dimensão': 'D3_00026',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RGF Anexo 5 (Executivo) indisponível ou incompleto (cod_conta, conta, valor)',
        }]), pd.DataFrame()

    # ── MSC: ending_balance + conta_contabil 11111/11121/11131 + PO Executivo
    # Cobre os três tipos de ente (Estado, DF, Município) com Direta+Indireta;
    # demais poderes/órgãos (TC, RPPS, Legislativo, Judiciário, MP, Defensoria)
    # ficam fora desta verificação por decisão metodológica do projeto.
    po_executivo = {
        '10111', '10112',  # Estados — Direta + Indireta
        '10121', '10122',  # DF      — Direta + Indireta
        '10131', '10132',  # Municípios — Direta + Indireta
    }
    msc = msc_dez.loc[msc_dez['tipo_valor'].astype(str).eq('ending_balance')].copy()
    cc = msc['conta_contabil'].astype(str).str.strip()
    msc = msc.loc[
        cc.str.startswith('11111')
        | cc.str.startswith('11121')
        | cc.str.startswith('11131')
    ].copy()
    po_norm = (
        msc['poder_orgao'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    )
    msc = msc.loc[po_norm.isin(po_executivo)].copy()

    # FR (3 últimos dígitos do código de 4 dígitos da fonte na MSC)
    fr4 = _d3_00029_fonte_codigo_4d(msc['fonte_recursos'])
    msc['_fr3'] = fr4.str[-3:]
    msc['_grupo'] = msc['_fr3'].map(_D3_00026_FR_GRUPO)
    msc['_valor'] = pd.to_numeric(msc['valor'], errors='coerce').fillna(0)
    msc['_po'] = (
        msc['poder_orgao'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    )

    msc_por_grupo = (
        msc.loc[msc['_grupo'].notna()]
        .groupby('_grupo', dropna=False)['_valor']
        .sum()
    )

    # Quebra MSC por (grupo, poder_orgao) — usada para diagnóstico de divergências
    msc_por_grupo_po = (
        msc.loc[msc['_grupo'].notna()]
        .groupby(['_grupo', '_po'], dropna=False)['_valor']
        .sum()
    )

    # Saldos em FR não mapeada — só diagnóstico (não compõem o critério)
    msc_nao_mapeada = float(msc.loc[msc['_grupo'].isna(), '_valor'].sum())
    fr_nao_mapeadas = sorted(
        msc.loc[msc['_grupo'].isna() & (msc['_valor'] != 0), '_fr3']
        .dropna().unique().tolist()
    )

    # ── RGF Anexo 5 (Executivo): DisponibilidadeDeCaixaBruta + linhas detalhadas
    rgf = df_rgf_5e.copy()
    cod_norm = rgf['cod_conta'].astype(str).str.strip()
    conta_norm = (
        rgf['conta'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
    )
    rgf = rgf.assign(_cod=cod_norm, _conta=conta_norm)
    rgf = rgf.loc[rgf['_cod'].eq('DisponibilidadeDeCaixaBruta')]
    rgf['_grupo'] = rgf['_conta'].map(_D3_00026_RGF_LABEL_GRUPO)
    rgf['_valor'] = pd.to_numeric(rgf['valor'], errors='coerce').fillna(0)

    rgf_detalhado = rgf.loc[rgf['_grupo'].notna()]
    rgf_por_grupo = rgf_detalhado.groupby('_grupo', dropna=False)['_valor'].sum()

    # Sem nada comparável dos dois lados → N/A
    if rgf_detalhado.empty and msc_por_grupo.empty:
        return pd.DataFrame([{
            'Dimensão': 'D3_00026',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': (
                'Sem linhas comparáveis: RGF Anexo 5 sem cod_conta DisponibilidadeDeCaixaBruta detalhado '
                'e MSC sem saldos em 11111/11121/11131 nas fontes mapeadas'
            ),
        }]), pd.DataFrame()

    # Comparação grupo a grupo (união dos grupos presentes em qualquer dos dois lados)
    grupos = sorted(set(msc_por_grupo.index) | set(rgf_por_grupo.index))
    linhas = []
    erro_grupos = []
    tolerancia = 0.01
    for g in grupos:
        v_msc = float(msc_por_grupo.get(g, 0.0))
        v_rgf = float(rgf_por_grupo.get(g, 0.0))
        dif = round(v_msc - v_rgf, 2)
        linhas.append({
            'Grupo de FR (STN)': g,
            'MSC dez (Caixa Bruta)': v_msc,
            'RGF Anexo 5 (DisponibilidadeDeCaixaBruta)': v_rgf,
            'Diferença (MSC − RGF)': dif,
        })
        # Diagnóstico: para grupos divergentes, abrir a quebra MSC por poder_orgao,
        # facilitando identificar qual PO está sobrando frente ao RGF (ex.: estatal
        # dependente, autarquia ou fundo especial não consolidado no Anexo 5).
        if not np.isclose(v_msc, v_rgf, atol=tolerancia, rtol=0.0):
            erro_grupos.append(g)
            try:
                detalhe_po = msc_por_grupo_po.loc[g].sort_values(ascending=False)
            except (KeyError, ValueError):
                detalhe_po = pd.Series(dtype=float)
            for po, v_po in detalhe_po.items():
                if abs(float(v_po)) < tolerancia:
                    continue
                po_label = _D3_00026_PO_LABEL.get(str(po), 'Outro PO')
                linhas.append({
                    'Grupo de FR (STN)': f'   ↳ MSC PO {po} — {po_label}',
                    'MSC dez (Caixa Bruta)': float(v_po),
                    'RGF Anexo 5 (DisponibilidadeDeCaixaBruta)': None,
                    'Diferença (MSC − RGF)': None,
                })

    if msc_nao_mapeada or fr_nao_mapeadas:
        linhas.append({
            'Grupo de FR (STN)': 'NÃO MAPEADA (apenas diagnóstico — não compõe critério)',
            'MSC dez (Caixa Bruta)': msc_nao_mapeada,
            'RGF Anexo 5 (DisponibilidadeDeCaixaBruta)': 0.0,
            'Diferença (MSC − RGF)': round(msc_nao_mapeada, 2),
        })

    d3_00026_t = pd.DataFrame(linhas)

    if erro_grupos:
        resposta = 'ERRO'
        nota = 0.00
    else:
        resposta = 'OK'
        nota = 1.00

    obs_out = obs_base
    if fr_nao_mapeadas:
        obs_out = (
            obs_out
            + ' Saldo MSC em fonte(s) não mapeada(s): '
            + ', '.join(fr_nao_mapeadas)
            + ' (não compõem o critério OK/ERRO).'
        )

    d3_00026 = pd.DataFrame([{
        'Dimensão': 'D3_00026',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs_out,
    }])
    return d3_00026, d3_00026_t


def d3_00027(df_rreo_1, df_rreo_6):
    """
    Igualdade entre Anexos 1 e 6 do RREO para dotação atualizada, despesas empenhadas e liquidadas.
    Anexo 1: TotalDespesas nas colunas do Balanço Orçamentário; Anexo 6: soma das rubricas indicadas.
    """
    desc = (
        'Verifica a igualdade entre Anexos 1 e 6 do RREO (dotação atualizada, despesas empenhadas e liquidadas)'
    )
    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_6 is None
        or not isinstance(df_rreo_6, pd.DataFrame)
        or df_rreo_6.empty
        or not _RREO_BO_COLS.issubset(df_rreo_6.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00027',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 6 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    pares = (
        ('dotacao_atualizada', 'Dotação atualizada', 'DOTAÇÃO ATUALIZADA (e)', 'DOTAÇÃO ATUALIZADA'),
        ('despesas_empenhadas', 'Despesas empenhadas até o bimestre', 'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)', 'DESPESAS EMPENHADAS'),
        ('despesas_liquidadas', 'Despesas liquidadas até o bimestre', 'DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)', 'DESPESAS LIQUIDADAS'),
    )

    valores_a1 = {}
    valores_a6 = {}
    difs = {}
    for chave, rotulo, col_a1, col_a6 in pares:
        s1 = df_rreo_1.loc[
            (df_rreo_1['coluna'] == col_a1) & (df_rreo_1['cod_conta'] == 'TotalDespesas'),
            'valor',
        ]
        s6 = df_rreo_6.loc[
            (df_rreo_6['coluna'] == col_a6) & (df_rreo_6['cod_conta'].isin(_D3_00027_RREO6_DESP)),
            'valor',
        ]
        if s1.empty or s6.empty:
            return pd.DataFrame([{
                'Dimensão': 'D3_00027',
                'Resposta': 'N/A',
                'Descrição da Dimensão': desc,
                'Nota': None,
                'OBS': f'Linhas ausentes no RREO para: {rotulo}',
            }]), pd.DataFrame()
        valores_a1[chave] = float(s1.sum())
        valores_a6[chave] = float(s6.sum())
        difs[chave] = valores_a6[chave] - valores_a1[chave]

    d3_00027_t = pd.DataFrame([
        {
            'anexo': 'RREO — Anexo 1',
            'dotacao_atualizada': valores_a1['dotacao_atualizada'],
            'despesas_empenhadas': valores_a1['despesas_empenhadas'],
            'despesas_liquidadas': valores_a1['despesas_liquidadas'],
        },
        {
            'anexo': 'RREO — Anexo 6',
            'dotacao_atualizada': valores_a6['dotacao_atualizada'],
            'despesas_empenhadas': valores_a6['despesas_empenhadas'],
            'despesas_liquidadas': valores_a6['despesas_liquidadas'],
        },
        {
            'anexo': 'Diferença (Anexo 6 − Anexo 1)',
            'dotacao_atualizada': difs['dotacao_atualizada'],
            'despesas_empenhadas': difs['despesas_empenhadas'],
            'despesas_liquidadas': difs['despesas_liquidadas'],
        },
    ])

    tolerancia = 0.01
    condicao = [
        not np.isclose(difs['dotacao_atualizada'], 0.0, atol=tolerancia, rtol=0.0),
        not np.isclose(difs['despesas_empenhadas'], 0.0, atol=tolerancia, rtol=0.0),
        not np.isclose(difs['despesas_liquidadas'], 0.0, atol=tolerancia, rtol=0.0),
    ]
    if any(condicao):
        resposta = 'ERRO'
        nota = 0.00
    else:
        resposta = 'OK'
        nota = 1.00

    d3_00027 = pd.DataFrame([{
        'Dimensão': 'D3_00027',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': 'Anexos 1 e 6 do RREO',
    }])
    return d3_00027, d3_00027_t


def d3_00028(df_rreo_1, df_rreo_6):
    """
    Igualdade entre Anexos 1 e 6 do RREO para receitas realizadas e previsão atualizada.
    """
    desc = (
        'Verifica a igualdade entre Anexos 1 e 6 do RREO (receitas realizadas e previsão atualizada)'
    )
    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_6 is None
        or not isinstance(df_rreo_6, pd.DataFrame)
        or df_rreo_6.empty
        or not _RREO_BO_COLS.issubset(df_rreo_6.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00028',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 6 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    pares = (
        ('receita_realizada', 'Receita realizada até o bimestre', 'Até o Bimestre (c)', 'RECEITAS REALIZADAS (a)'),
        ('previsao_atualizada', 'Previsão atualizada', 'PREVISÃO ATUALIZADA (a)', 'PREVISÃO ATUALIZADA'),
    )

    valores_a1 = {}
    valores_a6 = {}
    difs = {}
    for chave, rotulo, col_a1, col_a6 in pares:
        s1 = df_rreo_1.loc[
            (df_rreo_1['coluna'] == col_a1) & (df_rreo_1['cod_conta'] == 'TotalReceitas'),
            'valor',
        ]
        s6 = df_rreo_6.loc[
            (df_rreo_6['coluna'] == col_a6) & (df_rreo_6['cod_conta'].isin(_D3_00028_RREO6_REC)),
            'valor',
        ]
        if s1.empty or s6.empty:
            return pd.DataFrame([{
                'Dimensão': 'D3_00028',
                'Resposta': 'N/A',
                'Descrição da Dimensão': desc,
                'Nota': None,
                'OBS': f'Linhas ausentes no RREO para: {rotulo}',
            }]), pd.DataFrame()
        valores_a1[chave] = float(s1.sum())
        valores_a6[chave] = float(s6.sum())
        difs[chave] = valores_a6[chave] - valores_a1[chave]

    d3_00028_t = pd.DataFrame([
        {
            'anexo': 'RREO — Anexo 1',
            'receita_realizada': valores_a1['receita_realizada'],
            'previsao_atualizada': valores_a1['previsao_atualizada'],
        },
        {
            'anexo': 'RREO — Anexo 6',
            'receita_realizada': valores_a6['receita_realizada'],
            'previsao_atualizada': valores_a6['previsao_atualizada'],
        },
        {
            'anexo': 'Diferença (Anexo 6 − Anexo 1)',
            'receita_realizada': difs['receita_realizada'],
            'previsao_atualizada': difs['previsao_atualizada'],
        },
    ])

    tolerancia = 0.01
    condicao = [
        not np.isclose(difs['receita_realizada'], 0.0, atol=tolerancia, rtol=0.0),
        not np.isclose(difs['previsao_atualizada'], 0.0, atol=tolerancia, rtol=0.0),
    ]
    if any(condicao):
        resposta = 'ERRO'
        nota = 0.00
    else:
        resposta = 'OK'
        nota = 1.00

    d3_00028 = pd.DataFrame([{
        'Dimensão': 'D3_00028',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': 'Anexos 1 e 6 do RREO',
    }])
    return d3_00028, d3_00028_t


def d3_00030(df_rreo_4, df_rreo_6, df_rreo_4_rpps=None):
    """
    Igualdade dos totais de receitas previdenciárias: RREO Anexo 4 × Anexo 6.

    A API entrega o Anexo 4 em dois extratos: o anexo 4 geral e o **RREO Anexo 04 - RPPS**
    (`4_rpps`). Parte das rubricas pode existir só no RPPS;
    por isso soma-se também `df_rreo_4_rpps` quando informado.

    Filtros fixos (API Siconfi):
    - Anexo 4 (+ opcional 4_rpps): cod_conta nos totais RPPS (previdenciário, financeiro,
      administração RPPS, contribuições militares — variantes de grafia na API); coluna PREVISÃO ATUALIZADA (a) e
      RECEITAS REALIZADAS ATÉ O BIMESTRE (b).
    - Anexo 6: cod_conta ReceitasPrimarias*/ReceitasNaoPrimarias* ComFontesRPPS;
      coluna PREVISÃO ATUALIZADA e RECEITAS REALIZADAS (a).
    """
    desc = (
        'Verifica a igualdade entre o total de receitas previdenciárias do RREO Anexo 4 e o Anexo 6'
    )
    obs = (
        'Anexo 4: soma do anexo 4 geral e, quando houver, do extrato Anexo 04 RPPS — '
        'TotalReceitasRPPS*, TotalDasReceitasDaAdministracaoRPPS, contribuições militares (cod_conta com '
        'variantes: Militares / Contribuições / Milirares conforme a API); '
        'Anexo 6: ReceitasPrimariasCorrentesComFontesRPPS e ReceitasNaoPrimariasCorrentesComFontesRPPS.'
    )
    need = {'coluna', 'cod_conta', 'valor'}

    cod_a4 = (
        'TotalReceitasRPPSPrevidenciario',
        'TotalReceitasRPPSFinanceiro',
        'TotalDasReceitasDaAdministracaoRPPS', # OBS: não entra os Militares e nem os com Recursos do Tesouro
    )
    col_prev_a4 = 'PREVISÃO ATUALIZADA (a)'
    col_rec_a4 = 'RECEITAS REALIZADAS ATÉ O BIMESTRE (b)'

    cod_a6 = (
        'ReceitasPrimariasCorrentesComFontesRPPS',
        'ReceitasNaoPrimariasCorrentesComFontesRPPS',
        'ReceitasPrimariasDeCapitalComFontesRPPS',
        'ReceitasNaoPrimariasDeCapitalComFontesRPPS',
    )
    col_prev_a6 = 'PREVISÃO ATUALIZADA'
    col_rec_a6 = 'RECEITAS REALIZADAS (a)'

    def _soma(df, codigos, nome_coluna):
        if df is None or df.empty or nome_coluna is None:
            return 0.0
        m_cc = df['cod_conta'].astype(str).isin(codigos)
        m_col = df['coluna'].astype(str).str.strip() == str(nome_coluna).strip()
        vals = df.loc[m_cc & m_col, 'valor']
        return float(pd.to_numeric(vals, errors='coerce').fillna(0).sum())

    def _df_a4_ok(df):
        return (
            df is not None
            and isinstance(df, pd.DataFrame)
            and not df.empty
            and need.issubset(df.columns)
        )

    if not _df_a4_ok(df_rreo_4) and not _df_a4_ok(df_rreo_4_rpps):
        return pd.DataFrame([{
            'Dimensão': 'D3_00030',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 4 (e Anexo 4 RPPS, se aplicável) indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if (
        df_rreo_6 is None
        or not isinstance(df_rreo_6, pd.DataFrame)
        or df_rreo_6.empty
        or not need.issubset(df_rreo_6.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00030',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 6 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    def _soma_a4(col_nome):
        s = 0.0
        if _df_a4_ok(df_rreo_4):
            s += _soma(df_rreo_4, cod_a4, col_nome)
        if _df_a4_ok(df_rreo_4_rpps):
            s += _soma(df_rreo_4_rpps, cod_a4, col_nome)
        return s

    def _tem_linha(df, codigos, nome_coluna):
        if not _df_a4_ok(df):
            return False
        return bool((
            df['cod_conta'].astype(str).isin(codigos)
            & (df['coluna'].astype(str).str.strip() == nome_coluna)
        ).any())

    a4_disponiveis = (df_rreo_4, df_rreo_4_rpps)
    linhas_presentes = (
        any(_tem_linha(df, cod_a4, col_prev_a4) for df in a4_disponiveis)
        and any(_tem_linha(df, cod_a4, col_rec_a4) for df in a4_disponiveis)
        and _tem_linha(df_rreo_6, cod_a6, col_prev_a6)
        and _tem_linha(df_rreo_6, cod_a6, col_rec_a6)
    )
    if not linhas_presentes:
        return pd.DataFrame([{
            'Dimensão': 'D3_00030',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'Linhas de receitas previdenciárias ausentes nos Anexos 4 e/ou 6 do RREO',
        }]), pd.DataFrame()

    rv4 = _soma_a4(col_rec_a4)
    rv6 = _soma(df_rreo_6, cod_a6, col_rec_a6)
    drv = rv6 - rv4

    pv4 = _soma_a4(col_prev_a4)
    pv6 = _soma(df_rreo_6, cod_a6, col_prev_a6)
    dpv = pv6 - pv4

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(drv, 0.0, atol=tolerancia, rtol=0.0)
        or not np.isclose(dpv, 0.0, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00030_t = pd.DataFrame([
        {
            'detalhe': 'Receitas previdenciárias — Anexo 4 + Anexo 4 RPPS (totais RPPS)',
            'previsao_atualizada': pv4,
            'receitas_realizadas': rv4,
        },
        {
            'detalhe': 'Receitas previdenciárias — Anexo 6 (ComFontesRPPS)',
            'previsao_atualizada': pv6,
            'receitas_realizadas': rv6,
        },
        {
            'detalhe': 'Diferença (Anexo 6 − Anexo 4)',
            'previsao_atualizada': dpv,
            'receitas_realizadas': drv,
        },
    ])

    d3_00030 = pd.DataFrame([{
        'Dimensão': 'D3_00030',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00030, d3_00030_t


def d3_00032(df_rreo_1, df_rreo_4, df_rreo_6):
    """
    Igualdade de Recursos Arrecadados em Exercícios Anteriores (RPPS):
    RREO Anexo 1 × Anexo 4 × Anexo 6.

    Filtros por demonstrativo (API Siconfi):
    - Anexo 1: coluna = 'PREVISÃO ATUALIZADA (a)',
               cod_conta = 'RecursosArrecadadosEmExerciciosAnteriores'
    - Anexo 4: coluna = 'PREVISÃO ORÇAMENTÁRIA',
               cod_conta = 'RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario'
    - Anexo 6: coluna = 'PREVISÃO ORÇAMENTÁRIA',
               cod_conta = 'RREO6SaldoDeExerciciosAnteriores'

    Resultado OK se os três valores forem iguais (tolerância de R$ 0,01).
    """
    desc = (
        'Verifica a igualdade de Recursos Arrecadados em Exercícios Anteriores (RPPS) '
        'entre os Anexos 1, 4 e 6 do RREO'
    )
    obs = (
        'Anexo 1: coluna PREVISÃO ATUALIZADA (a) / cod_conta RecursosArrecadadosEmExerciciosAnteriores; '
        'Anexo 4: coluna PREVISÃO ORÇAMENTÁRIA / cod_conta '
        'RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario; '
        'Anexo 6: coluna PREVISÃO ORÇAMENTÁRIA / cod_conta RecursosArrecadadosEmExerciciosAnteriores.'
    )
    need = {'coluna', 'cod_conta', 'valor'}

    def _df_ok(df):
        return (
            df is not None
            and isinstance(df, pd.DataFrame)
            and not df.empty
            and need.issubset(df.columns)
        )

    def _soma(df, cod_conta, nome_coluna):
        if not _df_ok(df):
            return None
        m_cc = df['cod_conta'].astype(str) == str(cod_conta)
        m_col = df['coluna'].astype(str).str.strip() == str(nome_coluna).strip()
        vals = df.loc[m_cc & m_col, 'valor']
        return float(pd.to_numeric(vals, errors='coerce').fillna(0).sum())

    if not _df_ok(df_rreo_1):
        return pd.DataFrame([{
            'Dimensão': 'D3_00032',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if not _df_ok(df_rreo_4):
        return pd.DataFrame([{
            'Dimensão': 'D3_00032',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 4 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if not _df_ok(df_rreo_6):
        return pd.DataFrame([{
            'Dimensão': 'D3_00032',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 6 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    v1 = _soma(df_rreo_1, 'RecursosArrecadadosEmExerciciosAnteriores', 'PREVISÃO ATUALIZADA (a)')
    v4 = _soma(df_rreo_4, 'RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario', 'PREVISÃO ORÇAMENTÁRIA')
    v6 = _soma(df_rreo_6, 'RecursosArrecadadosEmExerciciosAnteriores', 'PREVISÃO ORÇAMENTÁRIA')

    linhas_presentes = (
        (
            (df_rreo_1['cod_conta'].astype(str) == 'RecursosArrecadadosEmExerciciosAnteriores')
            & (df_rreo_1['coluna'].astype(str).str.strip() == 'PREVISÃO ATUALIZADA (a)')
        ).any()
        and (
            (df_rreo_4['cod_conta'].astype(str) == 'RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario')
            & (df_rreo_4['coluna'].astype(str).str.strip() == 'PREVISÃO ORÇAMENTÁRIA')
        ).any()
        and (
            (df_rreo_6['cod_conta'].astype(str) == 'RecursosArrecadadosEmExerciciosAnteriores')
            & (df_rreo_6['coluna'].astype(str).str.strip() == 'PREVISÃO ORÇAMENTÁRIA')
        ).any()
    )
    if not linhas_presentes:
        return pd.DataFrame([{
            'Dimensão': 'D3_00032',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'Linha de Recursos Arrecadados em Exercícios Anteriores ausente em um ou mais anexos',
        }]), pd.DataFrame()

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(v1, v4, atol=tolerancia, rtol=0.0)
        or not np.isclose(v1, v6, atol=tolerancia, rtol=0.0)
        or not np.isclose(v4, v6, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00032_t = pd.DataFrame([
        {
            'detalhe': 'Anexo 1 — RecursosArrecadadosEmExerciciosAnteriores (PREVISÃO ATUALIZADA (a))',
            'valor': v1,
        },
        {
            'detalhe': 'Anexo 4 — RecursosRPPSArrecadadosEmExerciciosAnterioresPrevidenciario (PREVISÃO ORÇAMENTÁRIA)',
            'valor': v4,
        },
        {
            'detalhe': 'Anexo 6 — RecursosArrecadadosEmExerciciosAnteriores (PREVISÃO ORÇAMENTÁRIA)',
            'valor': v6,
        },
        {
            'detalhe': 'Diferença Anexo 1 − Anexo 4',
            'valor': round(v1 - v4, 2),
        },
        {
            'detalhe': 'Diferença Anexo 1 − Anexo 6',
            'valor': round(v1 - v6, 2),
        },
    ])

    d3_00032 = pd.DataFrame([{
        'Dimensão': 'D3_00032',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00032, d3_00032_t


def d3_00033(df_rreo_1, df_rreo_6):
    """
    Superávit financeiro (previsão): RREO Anexo 1 × Anexo 6.

    Anexo 1: coluna PREVISÃO ATUALIZADA (a), cod_conta SuperavitFinanceiro.
    Anexo 6: coluna PREVISÃO ORÇAMENTÁRIA, cod_conta SuperavitFinanceiro.

    Se a linha não existir nos dois demonstrativos, considera-se OK (coerência na ausência).
    Se existir só em um dos anexos, ERRO (inconsistência).
    """
    desc = (
        'Verifica a igualdade do superávit financeiro (previsão) entre o RREO Anexo 1 e o Anexo 6'
    )
    obs_ok_compare = (
        'Anexo 1: PREVISÃO ATUALIZADA (a) e SuperavitFinanceiro; '
        'Anexo 6: PREVISÃO ORÇAMENTÁRIA e SuperavitFinanceiro.'
    )
    col_a1 = 'PREVISÃO ATUALIZADA (a)'
    col_a6 = 'PREVISÃO ORÇAMENTÁRIA'
    cod = 'SuperavitFinanceiro'

    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_6 is None
        or not isinstance(df_rreo_6, pd.DataFrame)
        or df_rreo_6.empty
        or not _RREO_BO_COLS.issubset(df_rreo_6.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00033',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 6 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    m1 = (
        (df_rreo_1['coluna'].astype(str).str.strip() == col_a1)
        & (df_rreo_1['cod_conta'].astype(str).str.strip() == cod)
    )
    m6 = (
        (df_rreo_6['coluna'].astype(str).str.strip() == col_a6)
        & (df_rreo_6['cod_conta'].astype(str).str.strip() == cod)
    )
    has1 = bool(m1.any())
    has6 = bool(m6.any())

    # Ausente nos dois: coerente → OK (metodologia: não pode faltar só em um)
    if not has1 and not has6:
        obs_both_absent = (
            'Superávit financeiro (previsão, SuperavitFinanceiro) ausente em Anexo 1 e Anexo 6 — '
            'coerente entre os demonstrativos.'
        )
        d3_00033_t = pd.DataFrame([
            {'detalhe': 'Superávit financeiro — RREO Anexo 1', 'valor': 0.0},
            {'detalhe': 'Superávit financeiro — RREO Anexo 6', 'valor': 0.0},
            {'detalhe': 'Diferença (Anexo 6 − Anexo 1)', 'valor': 0.0},
        ])
        d3_00033 = pd.DataFrame([{
            'Dimensão': 'D3_00033',
            'Resposta': 'OK',
            'Descrição da Dimensão': desc,
            'Nota': 1.00,
            'OBS': obs_both_absent,
        }])
        return d3_00033, d3_00033_t

    # Presente em apenas um anexo: inconsistente → ERRO
    if has1 != has6:
        v1 = float(pd.to_numeric(df_rreo_1.loc[m1, 'valor'], errors='coerce').fillna(0).sum()) if has1 else 0.0
        v6 = float(pd.to_numeric(df_rreo_6.loc[m6, 'valor'], errors='coerce').fillna(0).sum()) if has6 else 0.0
        dif = v6 - v1
        obs_mismatch = (
            'Inconsistência: linha SuperavitFinanceiro (previsão) presente em apenas um dos anexos '
            '(Anexo 1 e Anexo 6 devem ambos trazer ou ambos omitir a informação).'
        )
        d3_00033_t = pd.DataFrame([
            {'detalhe': 'Superávit financeiro — RREO Anexo 1', 'valor': v1},
            {'detalhe': 'Superávit financeiro — RREO Anexo 6', 'valor': v6},
            {'detalhe': 'Diferença (Anexo 6 − Anexo 1)', 'valor': dif},
        ])
        d3_00033 = pd.DataFrame([{
            'Dimensão': 'D3_00033',
            'Resposta': 'ERRO',
            'Descrição da Dimensão': desc,
            'Nota': 0.00,
            'OBS': obs_mismatch,
        }])
        return d3_00033, d3_00033_t

    v1 = float(pd.to_numeric(df_rreo_1.loc[m1, 'valor'], errors='coerce').fillna(0).sum())
    v6 = float(pd.to_numeric(df_rreo_6.loc[m6, 'valor'], errors='coerce').fillna(0).sum())
    dif = v6 - v1

    tolerancia = 0.01
    condicao_erro = not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0)
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00033_t = pd.DataFrame([
        {'detalhe': 'Superávit financeiro — RREO Anexo 1', 'valor': v1},
        {'detalhe': 'Superávit financeiro — RREO Anexo 6', 'valor': v6},
        {'detalhe': 'Diferença (Anexo 6 − Anexo 1)', 'valor': dif},
    ])

    d3_00033 = pd.DataFrame([{
        'Dimensão': 'D3_00033',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs_ok_compare,
    }])
    return d3_00033, d3_00033_t


def d3_00034(df_rreo_1, df_rreo_4, df_rreo_6):
    """
    Igualdade da Reserva Orçamentária do RPPS (Previdenciário):
    RREO Anexo 1 × Anexo 4 × Anexo 6.

    Filtros por demonstrativo (API Siconfi):
    - Anexo 1: coluna = 'DOTAÇÃO ATUALIZADA (e)',
               cod_conta = 'ReservaDoRPPS'
    - Anexo 4: coluna = 'PREVISÃO ORÇAMENTÁRIA',
               cod_conta = 'ReservaOrcamentariaDoRPPSPrevidenciario'
    - Anexo 6: coluna = 'PREVISÃO ORÇAMENTÁRIA',
               cod_conta = 'ReservaOrcamentariaDoRPPSPrevidenciario'

    Resultado OK se os três valores forem iguais (tolerância de R$ 0,01).
    """
    desc = (
        'Verifica a igualdade da Reserva Orçamentária do RPPS (Previdenciário) '
        'entre os Anexos 1, 4 e 6 do RREO'
    )
    obs = (
        'Anexo 1: coluna DOTAÇÃO ATUALIZADA (e) / cod_conta ReservaDoRPPS; '
        'Anexo 4: coluna PREVISÃO ORÇAMENTÁRIA / cod_conta ReservaOrcamentariaDoRPPSPrevidenciario; '
        'Anexo 6: coluna PREVISÃO ORÇAMENTÁRIA / cod_conta ReservaOrcamentariaDoRPPSPrevidenciario.'
    )
    need = {'coluna', 'cod_conta', 'valor'}

    def _df_ok(df):
        return (
            df is not None
            and isinstance(df, pd.DataFrame)
            and not df.empty
            and need.issubset(df.columns)
        )

    def _soma(df, cod_conta, nome_coluna):
        if not _df_ok(df):
            return None
        m_cc = df['cod_conta'].astype(str) == str(cod_conta)
        m_col = df['coluna'].astype(str).str.strip() == str(nome_coluna).strip()
        vals = df.loc[m_cc & m_col, 'valor']
        return float(pd.to_numeric(vals, errors='coerce').fillna(0).sum())

    if not _df_ok(df_rreo_1):
        return pd.DataFrame([{
            'Dimensão': 'D3_00034',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if not _df_ok(df_rreo_4):
        return pd.DataFrame([{
            'Dimensão': 'D3_00034',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 4 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if not _df_ok(df_rreo_6):
        return pd.DataFrame([{
            'Dimensão': 'D3_00034',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 6 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    v1 = _soma(df_rreo_1, 'ReservaDoRPPS', 'DOTAÇÃO ATUALIZADA (e)')
    v4 = _soma(df_rreo_4, 'ReservaOrcamentariaDoRPPSPrevidenciario', 'PREVISÃO ORÇAMENTÁRIA')
    v6 = _soma(df_rreo_6, 'ReservaOrcamentariaDoRPPSPrevidenciario', 'PREVISÃO ORÇAMENTÁRIA')

    linhas_presentes = (
        (
            (df_rreo_1['cod_conta'].astype(str) == 'ReservaDoRPPS')
            & (df_rreo_1['coluna'].astype(str).str.strip() == 'DOTAÇÃO ATUALIZADA (e)')
        ).any()
        and (
            (df_rreo_4['cod_conta'].astype(str) == 'ReservaOrcamentariaDoRPPSPrevidenciario')
            & (df_rreo_4['coluna'].astype(str).str.strip() == 'PREVISÃO ORÇAMENTÁRIA')
        ).any()
        and (
            (df_rreo_6['cod_conta'].astype(str) == 'ReservaOrcamentariaDoRPPSPrevidenciario')
            & (df_rreo_6['coluna'].astype(str).str.strip() == 'PREVISÃO ORÇAMENTÁRIA')
        ).any()
    )
    if not linhas_presentes:
        return pd.DataFrame([{
            'Dimensão': 'D3_00034',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'Linha da Reserva Orçamentária do RPPS ausente em um ou mais anexos',
        }]), pd.DataFrame()

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(v1, v4, atol=tolerancia, rtol=0.0)
        or not np.isclose(v1, v6, atol=tolerancia, rtol=0.0)
        or not np.isclose(v4, v6, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00034_t = pd.DataFrame([
        {
            'detalhe': 'Anexo 1 — ReservaDoRPPS (DOTAÇÃO ATUALIZADA (e))',
            'valor': v1,
        },
        {
            'detalhe': 'Anexo 4 — ReservaOrcamentariaDoRPPSPrevidenciario (PREVISÃO ORÇAMENTÁRIA)',
            'valor': v4,
        },
        {
            'detalhe': 'Anexo 6 — ReservaOrcamentariaDoRPPSPrevidenciario (PREVISÃO ORÇAMENTÁRIA)',
            'valor': v6,
        },
        {
            'detalhe': 'Diferença (Anexo 1 − Anexo 4)',
            'valor': round(v1 - v4, 2),
        },
        {
            'detalhe': 'Diferença (Anexo 1 − Anexo 6)',
            'valor': round(v1 - v6, 2),
        },
    ])

    d3_00034 = pd.DataFrame([{
        'Dimensão': 'D3_00034',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00034, d3_00034_t


def d3_00035(df_rreo_1, df_rreo_6):
    """
    Reserva de contingência (dotação atualizada): RREO Anexo 1 × Anexo 6.

    Anexo 1: coluna DOTAÇÃO ATUALIZADA (e), cod_conta ReservaDeContingencia.
    Anexo 6: coluna DOTAÇÃO ATUALIZADA, cod_conta RREO6ReservaDeContingencia.
    """
    desc = (
        'Verifica a igualdade da reserva de contingência (dotação atualizada) entre o RREO Anexo 1 e o Anexo 6'
    )
    obs = (
        'Anexo 1: DOTAÇÃO ATUALIZADA (e) e ReservaDeContingencia; '
        'Anexo 6: DOTAÇÃO ATUALIZADA e RREO6ReservaDeContingencia.'
    )
    col_a1 = 'DOTAÇÃO ATUALIZADA (e)'
    col_a6 = 'DOTAÇÃO ATUALIZADA'
    cod_a1 = 'ReservaDeContingencia'
    cod_a6 = 'RREO6ReservaDeContingencia'

    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_6 is None
        or not isinstance(df_rreo_6, pd.DataFrame)
        or df_rreo_6.empty
        or not _RREO_BO_COLS.issubset(df_rreo_6.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00035',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 6 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    m1 = (
        (df_rreo_1['coluna'].astype(str).str.strip() == col_a1)
        & (df_rreo_1['cod_conta'].astype(str).str.strip() == cod_a1)
    )
    m6 = (
        (df_rreo_6['coluna'].astype(str).str.strip() == col_a6)
        & (df_rreo_6['cod_conta'].astype(str).str.strip() == cod_a6)
    )

    v1 = float(pd.to_numeric(df_rreo_1.loc[m1, 'valor'], errors='coerce').fillna(0).sum())
    v6 = float(pd.to_numeric(df_rreo_6.loc[m6, 'valor'], errors='coerce').fillna(0).sum())
    dif = v6 - v1

    tolerancia = 0.01
    condicao_erro = not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0)
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    ausencias = []
    if not m1.any():
        ausencias.append(f'Anexo 1 sem linha "{col_a1}" + {cod_a1}')
    if not m6.any():
        ausencias.append(f'Anexo 6 sem linha "{col_a6}" + {cod_a6}')
    obs_out = obs
    if ausencias:
        obs_out = obs + ' Ausências parciais tratadas como zero: ' + '; '.join(ausencias) + '.'

    d3_00035_t = pd.DataFrame([
        {'detalhe': 'Reserva de contingência — RREO Anexo 1', 'valor': v1},
        {'detalhe': 'Reserva de contingência — RREO Anexo 6', 'valor': v6},
        {'detalhe': 'Diferença (Anexo 6 − Anexo 1)', 'valor': dif},
    ])

    d3_00035 = pd.DataFrame([{
        'Dimensão': 'D3_00035',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs_out,
    }])
    return d3_00035, d3_00035_t


def d3_00037(df_rreo_1, df_rreo_9):
    """
    Igualdade de investimentos (intra + exceto intra): RREO Anexo 1 × Anexo 9.

    Anexo 1: soma Investimentos + InvestimentosIntra (e variantes); colunas
    DOTAÇÃO ATUALIZADA (e) e DESPESAS EMPENHADAS ATÉ O BIMESTRE (f).
    Anexo 9: apenas cod_conta Investimentos; colunas DOTAÇÃO ATUALIZADA (d) e
    DESPESAS EMPENHADAS (e).
    """
    desc = (
        'Verifica a igualdade de Investimentos (intra + exceto intra) entre o Anexo 1 e o Anexo 9 do RREO'
    )
    obs = (
        'Anexo 1: soma de Investimentos e InvestimentosIntra em DOTAÇÃO ATUALIZADA (e) e '
        'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f); '
        'Anexo 9: apenas Investimentos em DOTAÇÃO ATUALIZADA (d) e DESPESAS EMPENHADAS (e).'
    )

    cods_conta_rreo1 = ('Investimentos', 'InvestimentosIntra')
    cod_a9 = 'Investimentos'
    col_dot_a1 = 'DOTAÇÃO ATUALIZADA (e)'
    col_emp_a1 = 'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)'
    col_dot_a9 = 'DOTAÇÃO ATUALIZADA (d)'
    col_emp_a9 = 'DESPESAS EMPENHADAS (e)'

    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_9 is None
        or not isinstance(df_rreo_9, pd.DataFrame)
        or df_rreo_9.empty
        or not _RREO_BO_COLS.issubset(df_rreo_9.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00037',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 9 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    cc1 = df_rreo_1['cod_conta'].astype(str).str.strip()
    m_cc_a1 = cc1.isin(cods_conta_rreo1) | cc1.str.startswith(
        'InvestimentosIntra', na=False
    )
    m_dot_a1 = m_cc_a1 & (df_rreo_1['coluna'].astype(str).str.strip() == col_dot_a1)
    m_emp_a1 = m_cc_a1 & (df_rreo_1['coluna'].astype(str).str.strip() == col_emp_a1)
    cc9 = df_rreo_9['cod_conta'].astype(str).str.strip()
    m_dot_a9 = (cc9 == cod_a9) & (df_rreo_9['coluna'].astype(str).str.strip() == col_dot_a9)
    m_emp_a9 = (cc9 == cod_a9) & (df_rreo_9['coluna'].astype(str).str.strip() == col_emp_a9)

    if not (m_dot_a1.any() and m_emp_a1.any() and m_dot_a9.any() and m_emp_a9.any()):
        return pd.DataFrame([{
            'Dimensão': 'D3_00037',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': (
                'Linha ausente: A1 exige ao menos um dos cod_conta (soma: Investimentos + InvestimentosIntra) em '
                '"DOTAÇÃO ATUALIZADA (e)" e "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)"; '
                'A9 exige Investimentos em "DOTAÇÃO ATUALIZADA (d)" e "DESPESAS EMPENHADAS (e)"'
            ),
        }]), pd.DataFrame()

    dot_a1 = float(pd.to_numeric(df_rreo_1.loc[m_dot_a1, 'valor'], errors='coerce').fillna(0).sum())
    emp_a1 = float(pd.to_numeric(df_rreo_1.loc[m_emp_a1, 'valor'], errors='coerce').fillna(0).sum())
    dot_a9 = float(pd.to_numeric(df_rreo_9.loc[m_dot_a9, 'valor'], errors='coerce').fillna(0).sum())
    emp_a9 = float(pd.to_numeric(df_rreo_9.loc[m_emp_a9, 'valor'], errors='coerce').fillna(0).sum())

    dif_dot = dot_a9 - dot_a1
    dif_emp = emp_a9 - emp_a1

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(dif_dot, 0.0, atol=tolerancia, rtol=0.0)
        or not np.isclose(dif_emp, 0.0, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00037_t = pd.DataFrame([
        {
            'detalhe': 'Investimentos — RREO Anexo 1',
            'dotacao_atualizada': dot_a1,
            'despesas_empenhadas': emp_a1,
        },
        {
            'detalhe': 'Investimentos — RREO Anexo 9',
            'dotacao_atualizada': dot_a9,
            'despesas_empenhadas': emp_a9,
        },
        {
            'detalhe': 'Diferença (Anexo 9 − Anexo 1)',
            'dotacao_atualizada': dif_dot,
            'despesas_empenhadas': dif_emp,
        },
    ])

    d3_00037 = pd.DataFrame([{
        'Dimensão': 'D3_00037',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00037, d3_00037_t


def d3_00038(df_rreo_1, df_rreo_9):
    """
    Igualdade de inversões financeiras (intra + exceto intra): RREO Anexo 1 × Anexo 9.

    Anexo 1: soma InversoesFinanceiras + InversoesFinanceirasIntra (e variantes); colunas
    DOTAÇÃO ATUALIZADA (e) e DESPESAS EMPENHADAS ATÉ O BIMESTRE (f).
    Anexo 9: apenas cod_conta InversoesFinanceiras; colunas DOTAÇÃO ATUALIZADA (d) e
    DESPESAS EMPENHADAS (e).
    """
    desc = (
        'Verifica a igualdade de Inversões Financeiras (intra + exceto intra) entre o Anexo 1 e o Anexo 9 do RREO'
    )
    obs = (
        'Anexo 1: soma de InversoesFinanceiras e InversoesFinanceirasIntra em DOTAÇÃO ATUALIZADA (e) e '
        'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f); '
        'Anexo 9: apenas InversoesFinanceiras em DOTAÇÃO ATUALIZADA (d) e DESPESAS EMPENHADAS (e).'
    )

    cods_conta_rreo1 = ('InversoesFinanceiras', 'InversoesFinanceirasIntra')
    cod_a9 = 'InversoesFinanceiras'
    col_dot_a1 = 'DOTAÇÃO ATUALIZADA (e)'
    col_emp_a1 = 'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)'
    col_dot_a9 = 'DOTAÇÃO ATUALIZADA (d)'
    col_emp_a9 = 'DESPESAS EMPENHADAS (e)'

    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_9 is None
        or not isinstance(df_rreo_9, pd.DataFrame)
        or df_rreo_9.empty
        or not _RREO_BO_COLS.issubset(df_rreo_9.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00038',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 9 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    cc1 = df_rreo_1['cod_conta'].astype(str).str.strip()
    m_cc_a1 = cc1.isin(cods_conta_rreo1) | cc1.str.startswith(
        'InversoesFinanceirasIntra', na=False
    )
    m_dot_a1 = m_cc_a1 & (df_rreo_1['coluna'].astype(str).str.strip() == col_dot_a1)
    m_emp_a1 = m_cc_a1 & (df_rreo_1['coluna'].astype(str).str.strip() == col_emp_a1)
    cc9 = df_rreo_9['cod_conta'].astype(str).str.strip()
    m_dot_a9 = (cc9 == cod_a9) & (df_rreo_9['coluna'].astype(str).str.strip() == col_dot_a9)
    m_emp_a9 = (cc9 == cod_a9) & (df_rreo_9['coluna'].astype(str).str.strip() == col_emp_a9)

    if not (m_dot_a1.any() and m_emp_a1.any() and m_dot_a9.any() and m_emp_a9.any()):
        return pd.DataFrame([{
            'Dimensão': 'D3_00038',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': (
                'Linha ausente: A1 exige ao menos um dos cod_conta (soma: InversoesFinanceiras + '
                'InversoesFinanceirasIntra) em "DOTAÇÃO ATUALIZADA (e)" e "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)"; '
                'A9 exige InversoesFinanceiras em "DOTAÇÃO ATUALIZADA (d)" e "DESPESAS EMPENHADAS (e)"'
            ),
        }]), pd.DataFrame()

    dot_a1 = float(pd.to_numeric(df_rreo_1.loc[m_dot_a1, 'valor'], errors='coerce').fillna(0).sum())
    emp_a1 = float(pd.to_numeric(df_rreo_1.loc[m_emp_a1, 'valor'], errors='coerce').fillna(0).sum())
    dot_a9 = float(pd.to_numeric(df_rreo_9.loc[m_dot_a9, 'valor'], errors='coerce').fillna(0).sum())
    emp_a9 = float(pd.to_numeric(df_rreo_9.loc[m_emp_a9, 'valor'], errors='coerce').fillna(0).sum())

    dif_dot = dot_a9 - dot_a1
    dif_emp = emp_a9 - emp_a1

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(dif_dot, 0.0, atol=tolerancia, rtol=0.0)
        or not np.isclose(dif_emp, 0.0, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00038_t = pd.DataFrame([
        {
            'detalhe': 'Inversões Financeiras — RREO Anexo 1',
            'dotacao_atualizada': dot_a1,
            'despesas_empenhadas': emp_a1,
        },
        {
            'detalhe': 'Inversões Financeiras — RREO Anexo 9',
            'dotacao_atualizada': dot_a9,
            'despesas_empenhadas': emp_a9,
        },
        {
            'detalhe': 'Diferença (Anexo 9 − Anexo 1)',
            'dotacao_atualizada': dif_dot,
            'despesas_empenhadas': dif_emp,
        },
    ])

    d3_00038 = pd.DataFrame([{
        'Dimensão': 'D3_00038',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00038, d3_00038_t


def d3_00039(df_rreo_1, df_rreo_9):
    """
    Igualdade de amortização da dívida (intra + exceto intra): RREO Anexo 1 × Anexo 9.

    Anexo 1: soma dos cod_conta de amortização (ex.: AmortizacaoDaDivida,
    AmortizacaoRefinanciamentoDaDividaInternaContratual, AmortizacaoDaDividaIntra);
    colunas DOTAÇÃO ATUALIZADA (e) e DESPESAS EMPENHADAS ATÉ O BIMESTRE (f).
    Anexo 9: apenas cod_conta AmortizacaoDaDivida; colunas DOTAÇÃO ATUALIZADA (d) e
    DESPESAS EMPENHADAS (e).
    """
    desc = (
        'Verifica a igualdade de Amortização da Dívida (intra + exceto intra) entre o Anexo 1 e o Anexo 9 do RREO'
    )
    obs = (
        'Anexo 1: soma dos cod_conta de amortização da dívida em DOTAÇÃO ATUALIZADA (e) e '
        'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f); '
        'Anexo 9: apenas AmortizacaoDaDivida em DOTAÇÃO ATUALIZADA (d) e DESPESAS EMPENHADAS (e).'
    )

    # Anexo 1 (estados como RJ): várias linhas de amortização; somar todas.
    # Anexo 9: permanece consolidado em AmortizacaoDaDivida (ex.: Belém).
    cods_conta_rreo1 = (
        'AmortizacaoDaDivida',
        'AmortizacaoRefinanciamentoDaDividaInternaContratual',
        'AmortizacaoDaDividaIntra',
    )
    cod_a9 = 'AmortizacaoDaDivida'
    col_dot_a1 = 'DOTAÇÃO ATUALIZADA (e)'
    col_emp_a1 = 'DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)'
    col_dot_a9 = 'DOTAÇÃO ATUALIZADA (d)'
    col_emp_a9 = 'DESPESAS EMPENHADAS (e)'

    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_9 is None
        or not isinstance(df_rreo_9, pd.DataFrame)
        or df_rreo_9.empty
        or not _RREO_BO_COLS.issubset(df_rreo_9.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00039',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 9 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    cc1 = df_rreo_1['cod_conta'].astype(str).str.strip()
    # Inclui variantes de nome (ex.: RJ) além dos três cod_conta explícitos.
    m_cc_a1 = cc1.isin(cods_conta_rreo1) | cc1.str.startswith(
        'AmortizacaoDaDividaIntra', na=False
    )
    m_dot_a1 = m_cc_a1 & (df_rreo_1['coluna'].astype(str).str.strip() == col_dot_a1)
    m_emp_a1 = m_cc_a1 & (df_rreo_1['coluna'].astype(str).str.strip() == col_emp_a1)
    cc9 = df_rreo_9['cod_conta'].astype(str).str.strip()
    m_dot_a9 = (cc9 == cod_a9) & (df_rreo_9['coluna'].astype(str).str.strip() == col_dot_a9)
    m_emp_a9 = (cc9 == cod_a9) & (df_rreo_9['coluna'].astype(str).str.strip() == col_emp_a9)

    if not (m_dot_a1.any() and m_emp_a1.any() and m_dot_a9.any() and m_emp_a9.any()):
        return pd.DataFrame([{
            'Dimensão': 'D3_00039',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': (
                'Linha ausente: A1 exige ao menos um dos cod_conta de amortização (soma) em '
                '"DOTAÇÃO ATUALIZADA (e)" e "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)"; '
                'A9 exige AmortizacaoDaDivida em "DOTAÇÃO ATUALIZADA (d)" e "DESPESAS EMPENHADAS (e)"'
            ),
        }]), pd.DataFrame()

    dot_a1 = float(pd.to_numeric(df_rreo_1.loc[m_dot_a1, 'valor'], errors='coerce').fillna(0).sum())
    emp_a1 = float(pd.to_numeric(df_rreo_1.loc[m_emp_a1, 'valor'], errors='coerce').fillna(0).sum())
    dot_a9 = float(pd.to_numeric(df_rreo_9.loc[m_dot_a9, 'valor'], errors='coerce').fillna(0).sum())
    emp_a9 = float(pd.to_numeric(df_rreo_9.loc[m_emp_a9, 'valor'], errors='coerce').fillna(0).sum())

    dif_dot = dot_a9 - dot_a1
    dif_emp = emp_a9 - emp_a1

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(dif_dot, 0.0, atol=tolerancia, rtol=0.0)
        or not np.isclose(dif_emp, 0.0, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00039_t = pd.DataFrame([
        {
            'detalhe': 'Amortização da Dívida — RREO Anexo 1',
            'dotacao_atualizada': dot_a1,
            'despesas_empenhadas': emp_a1,
        },
        {
            'detalhe': 'Amortização da Dívida — RREO Anexo 9',
            'dotacao_atualizada': dot_a9,
            'despesas_empenhadas': emp_a9,
        },
        {
            'detalhe': 'Diferença (Anexo 9 − Anexo 1)',
            'dotacao_atualizada': dif_dot,
            'despesas_empenhadas': dif_emp,
        },
    ])

    d3_00039 = pd.DataFrame([{
        'Dimensão': 'D3_00039',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00039, d3_00039_t


def d3_00040(df_rreo_1, df_rreo_9):
    """
    Igualdade de receitas de operações de crédito: RREO Anexo 1 × Anexo 9.

    Anexo 1: cod_conta ReceitasDeOperacoesDeCredito; colunas PREVISÃO ATUALIZADA (a)
    e Até o Bimestre (c).
    Anexo 9: cod_conta RREO9ReceitasDeOperacoesDeCredito; colunas PREVISÃO ATUALIZADA (a)
    e RECEITAS REALIZADAS (b).

    Se **não** existir nenhuma dessas linhas nos **dois** anexos, o ente não tem esse tipo
    de receita a cruzar → **OK**. Só um anexo com linhas e o outro sem → **ERRO**.
    """
    desc = (
        'Verifica a igualdade de Receitas de Operações de Crédito entre o Anexo 1 e o Anexo 9 do RREO'
    )
    obs = (
        'Anexo 1: ReceitasDeOperacoesDeCredito em PREVISÃO ATUALIZADA (a) e Até o Bimestre (c); '
        'Anexo 9: RREO9ReceitasDeOperacoesDeCredito em PREVISÃO ATUALIZADA (a) e RECEITAS REALIZADAS (b).'
    )

    cod_a1 = 'ReceitasDeOperacoesDeCredito'
    cod_a9 = 'RREO9ReceitasDeOperacoesDeCredito'
    col_prev_a1 = 'PREVISÃO ATUALIZADA (a)'
    col_rec_a1 = 'Até o Bimestre (c)'
    col_prev_a9 = 'PREVISÃO ATUALIZADA (a)'
    col_rec_a9 = 'RECEITAS REALIZADAS (b)'

    if (
        df_rreo_1 is None
        or not isinstance(df_rreo_1, pd.DataFrame)
        or df_rreo_1.empty
        or not _RREO_BO_COLS.issubset(df_rreo_1.columns)
        or df_rreo_9 is None
        or not isinstance(df_rreo_9, pd.DataFrame)
        or df_rreo_9.empty
        or not _RREO_BO_COLS.issubset(df_rreo_9.columns)
    ):
        return pd.DataFrame([{
            'Dimensão': 'D3_00040',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 1 e/ou Anexo 9 indisponíveis ou incompletos',
        }]), pd.DataFrame()

    m_prev_a1 = (
        (df_rreo_1['cod_conta'].astype(str).str.strip() == cod_a1)
        & (df_rreo_1['coluna'].astype(str).str.strip() == col_prev_a1)
    )
    m_rec_a1 = (
        (df_rreo_1['cod_conta'].astype(str).str.strip() == cod_a1)
        & (df_rreo_1['coluna'].astype(str).str.strip() == col_rec_a1)
    )
    m_prev_a9 = (
        (df_rreo_9['cod_conta'].astype(str).str.strip() == cod_a9)
        & (df_rreo_9['coluna'].astype(str).str.strip() == col_prev_a9)
    )
    m_rec_a9 = (
        (df_rreo_9['cod_conta'].astype(str).str.strip() == cod_a9)
        & (df_rreo_9['coluna'].astype(str).str.strip() == col_rec_a9)
    )

    tem_a1 = m_prev_a1.any() and m_rec_a1.any()
    tem_a9 = m_prev_a9.any() and m_rec_a9.any()

    # Sem qualquer linha desta natureza nos dois anexos → ente sem operações de crédito a cruzar (OK).
    if not tem_a1 and not tem_a9:
        d3_00040_t = pd.DataFrame([
            {
                'detalhe': 'Sem Receitas de Operações de Crédito nos Anexos 1 e 9 (nada a comparar)',
                'previsao_atualizada': 0.0,
                'receitas_realizadas': 0.0,
            },
        ])
        return pd.DataFrame([{
            'Dimensão': 'D3_00040',
            'Resposta': 'OK',
            'Descrição da Dimensão': desc,
            'Nota': 1.00,
            'OBS': (
                f'{obs} Ente sem registros desta receita nos anexos — verificação dispensada (OK).'
            ),
        }]), d3_00040_t

    if not (tem_a1 and tem_a9):
        return pd.DataFrame([{
            'Dimensão': 'D3_00040',
            'Resposta': 'ERRO',
            'Descrição da Dimensão': desc,
            'Nota': 0.00,
            'OBS': (
                'Cruzamento incompleto: A1 exige ReceitasDeOperacoesDeCredito em "PREVISÃO ATUALIZADA (a)" '
                'e "Até o Bimestre (c)"; A9 exige RREO9ReceitasDeOperacoesDeCredito em '
                '"PREVISÃO ATUALIZADA (a)" e "RECEITAS REALIZADAS (b)". '
                'Um dos anexos tem as linhas e o outro não — revisar demonstrativo.'
            ),
        }]), pd.DataFrame()

    prev_a1 = float(pd.to_numeric(df_rreo_1.loc[m_prev_a1, 'valor'], errors='coerce').fillna(0).sum())
    rec_a1 = float(pd.to_numeric(df_rreo_1.loc[m_rec_a1, 'valor'], errors='coerce').fillna(0).sum())
    prev_a9 = float(pd.to_numeric(df_rreo_9.loc[m_prev_a9, 'valor'], errors='coerce').fillna(0).sum())
    rec_a9 = float(pd.to_numeric(df_rreo_9.loc[m_rec_a9, 'valor'], errors='coerce').fillna(0).sum())

    dif_prev = prev_a9 - prev_a1
    dif_rec = rec_a9 - rec_a1

    tolerancia = 0.01
    condicao_erro = (
        not np.isclose(dif_prev, 0.0, atol=tolerancia, rtol=0.0)
        or not np.isclose(dif_rec, 0.0, atol=tolerancia, rtol=0.0)
    )
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00040_t = pd.DataFrame([
        {
            'detalhe': 'Receitas de Operações de Crédito — RREO Anexo 1',
            'previsao_atualizada': prev_a1,
            'receitas_realizadas': rec_a1,
        },
        {
            'detalhe': 'Receitas de Operações de Crédito — RREO Anexo 9',
            'previsao_atualizada': prev_a9,
            'receitas_realizadas': rec_a9,
        },
        {
            'detalhe': 'Diferença (Anexo 9 − Anexo 1)',
            'previsao_atualizada': dif_prev,
            'receitas_realizadas': dif_rec,
        },
    ])

    d3_00040 = pd.DataFrame([{
        'Dimensão': 'D3_00040',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00040, d3_00040_t


def d3_00044(df_rreo_3, df_rgf_1e):
    """
    CAPAG — Igualdade de Transferências da União relativas à remuneração dos agentes
    comunitários de saúde e de combate às endemias (CF, art. 198, §11 — VII):
    RREO Anexo 3 × RGF Anexo 1 (Executivo).

    Filtros por demonstrativo (API Siconfi):
    - RREO Anexo 3: coluna = 'TOTAL (ÚLTIMOS 12 MESES)',
                    cod_conta = 'RREO3TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude'
    - RGF Anexo 1 (E): coluna = 'Valor',
                       cod_conta = 'TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude'

    Resultado OK se os dois valores forem iguais (tolerância de R$ 0,01).
    """
    desc = (
        'Verifica a igualdade das Transferências da União relativas à remuneração dos '
        'Agentes Comunitários de Saúde e de Combate às Endemias (CF, art. 198, §11 — VII) '
        'entre o RREO Anexo 3 e o RGF Anexo 1 (Executivo)'
    )
    obs = (
        'RREO Anexo 3: coluna TOTAL (ÚLTIMOS 12 MESES) / '
        'cod_conta RREO3TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude; '
        'RGF Anexo 1 (E): coluna Valor / '
        'cod_conta TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude.'
    )
    need = {'coluna', 'cod_conta', 'valor'}

    def _df_ok(df):
        return (
            df is not None
            and isinstance(df, pd.DataFrame)
            and not df.empty
            and need.issubset(df.columns)
        )

    def _soma(df, cod_conta, nome_coluna):
        m_cc = df['cod_conta'].astype(str).str.strip() == str(cod_conta).strip()
        m_col = df['coluna'].astype(str).str.strip() == str(nome_coluna).strip()
        vals = df.loc[m_cc & m_col, 'valor']
        return float(pd.to_numeric(vals, errors='coerce').fillna(0).sum())

    if not _df_ok(df_rreo_3):
        return pd.DataFrame([{
            'Dimensão': 'D3_00044',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 3 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if not _df_ok(df_rgf_1e):
        return pd.DataFrame([{
            'Dimensão': 'D3_00044',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RGF Anexo 1 (Executivo) indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    cod_rreo3 = 'RREO3TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude'
    col_rreo3 = 'TOTAL (ÚLTIMOS 12 MESES)'
    cod_rgf1e = 'TransferenciasDaUniaoRelativasARemuneracaoDosAgentesComunitariosDeSaude'
    col_rgf1e = 'Valor'

    linha_rreo3 = (
        (df_rreo_3['cod_conta'].astype(str).str.strip() == cod_rreo3)
        & (df_rreo_3['coluna'].astype(str).str.strip() == col_rreo3)
    )
    linha_rgf1e = (
        (df_rgf_1e['cod_conta'].astype(str).str.strip() == cod_rgf1e)
        & (df_rgf_1e['coluna'].astype(str).str.strip() == col_rgf1e)
    )
    if not linha_rreo3.any() or not linha_rgf1e.any():
        return pd.DataFrame([{
            'Dimensão': 'D3_00044',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'Linha de transferências para Agentes Comunitários ausente no RREO 3 e/ou RGF 1',
        }]), pd.DataFrame()

    v_rreo3 = _soma(df_rreo_3, cod_rreo3, col_rreo3)
    v_rgf1e = _soma(df_rgf_1e, cod_rgf1e, col_rgf1e)

    tolerancia = 0.01
    condicao_erro = not np.isclose(v_rreo3, v_rgf1e, atol=tolerancia, rtol=0.0)
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00044_t = pd.DataFrame([
        {
            'detalhe': 'RREO Anexo 3 — Transf. da União / Agentes Comunitários (TOTAL ÚLTIMOS 12 MESES)',
            'valor': v_rreo3,
        },
        {
            'detalhe': 'RGF Anexo 1 (E) — Agentes Comunitários com Recursos Vinculados (TOTAL ÚLTIMOS 12 MESES (a))',
            'valor': v_rgf1e,
        },
        {
            'detalhe': 'Diferença (RREO 3 − RGF 1 E)',
            'valor': round(v_rreo3 - v_rgf1e, 2),
        },
    ])

    d3_00044 = pd.DataFrame([{
        'Dimensão': 'D3_00044',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs,
    }])
    return d3_00044, d3_00044_t


def d3_00047(df_rreo_4, df_rreo_6):
    """
    Ranking 2025 oficial — D3_00047.
    Igualdade da Reserva Orçamentária do RPPS (Previdenciário) entre o
    RREO Anexo 4 e o RREO Anexo 6.

    Filtros (API Siconfi), alinhados à D3_00034 para os anexos 4 e 6:
    - Anexo 4 — quadro «RESERVA ORÇAMENTÁRIA DO RPPS»:
        coluna = PREVISÃO ORÇAMENTÁRIA,
        cod_conta = ReservaOrcamentariaDoRPPSPrevidenciario
    - Anexo 6 — quadro «Informações Adicionais» (Reserva Orçamentária do RPPS):
        coluna = PREVISÃO ORÇAMENTÁRIA,
        cod_conta = ReservaOrcamentariaDoRPPSPrevidenciario

    Regra: valor Anexo 4 = valor Anexo 6 (tolerância R$ 0,01).
    """
    desc = (
        'Igualdade da Reserva Orçamentária do RPPS (Previdenciário) '
        'entre o RREO Anexo 4 e o RREO Anexo 6'
    )
    obs = (
        'Anexo 4: coluna PREVISÃO ORÇAMENTÁRIA / cod_conta ReservaOrcamentariaDoRPPSPrevidenciario '
        '(quadro RESERVA ORÇAMENTÁRIA DO RPPS); '
        'Anexo 6: coluna PREVISÃO ORÇAMENTÁRIA / cod_conta ReservaOrcamentariaDoRPPSPrevidenciario '
        '(quadro Informações Adicionais — Reserva Orçamentária do RPPS).'
    )
    need = {'coluna', 'cod_conta', 'valor'}
    cod = 'ReservaOrcamentariaDoRPPSPrevidenciario'
    col = 'PREVISÃO ORÇAMENTÁRIA'

    def _df_ok(df):
        return (
            df is not None
            and isinstance(df, pd.DataFrame)
            and not df.empty
            and need.issubset(df.columns)
        )

    def _soma_e_linhas(df):
        m_cc = df['cod_conta'].astype(str).str.strip() == cod
        m_col = df['coluna'].astype(str).str.strip() == col.strip()
        sub = df.loc[m_cc & m_col]
        v = float(pd.to_numeric(sub['valor'], errors='coerce').fillna(0).sum())
        n = int(len(sub))
        return v, n

    if not _df_ok(df_rreo_4):
        return pd.DataFrame([{
            'Dimensão': 'D3_00047',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 4 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    if not _df_ok(df_rreo_6):
        return pd.DataFrame([{
            'Dimensão': 'D3_00047',
            'Resposta': 'N/A',
            'Descrição da Dimensão': desc,
            'Nota': None,
            'OBS': 'RREO Anexo 6 indisponível ou incompleto (coluna, cod_conta, valor)',
        }]), pd.DataFrame()

    v4, n4 = _soma_e_linhas(df_rreo_4)
    v6, n6 = _soma_e_linhas(df_rreo_6)

    dif = v4 - v6
    tolerancia = 0.01
    condicao_erro = not np.isclose(dif, 0.0, atol=tolerancia, rtol=0.0)
    resposta = 'ERRO' if condicao_erro else 'OK'
    nota = 0.00 if condicao_erro else 1.00

    d3_00047_t = pd.DataFrame([
        {
            'detalhe': 'Anexo 4 — ReservaOrcamentariaDoRPPSPrevidenciario (PREVISÃO ORÇAMENTÁRIA)',
            'valor': v4,
        },
        {
            'detalhe': 'Anexo 6 — ReservaOrcamentariaDoRPPSPrevidenciario (PREVISÃO ORÇAMENTÁRIA)',
            'valor': v6,
        },
        {
            'detalhe': 'Diferença (Anexo 4 − Anexo 6)',
            'valor': round(dif, 2),
        },
    ])

    obs_out = obs
    ausencias = []
    if n4 == 0:
        ausencias.append('Anexo 4 sem linha no filtro (PREVISÃO ORÇAMENTÁRIA + ReservaOrcamentariaDoRPPSPrevidenciario)')
    if n6 == 0:
        ausencias.append('Anexo 6 sem linha no filtro (PREVISÃO ORÇAMENTÁRIA + ReservaOrcamentariaDoRPPSPrevidenciario)')
    if ausencias:
        obs_out = obs + ' Ausências parciais tratadas como zero: ' + '; '.join(ausencias) + '.'

    d3_00047 = pd.DataFrame([{
        'Dimensão': 'D3_00047',
        'Resposta': resposta,
        'Descrição da Dimensão': desc,
        'Nota': nota,
        'OBS': obs_out,
    }])
    return d3_00047, d3_00047_t


##################################################################
##################################################################
##################################################################

# NOVAS DIMENSÕES 2025

##################################################################
##################################################################
##################################################################


_REMOVED_ANALYSES_ARITY = {
    'd3_00011': 2,
    'd3_00012': 2,
    'd3_00013': 2,
    'd3_00021': 2,
    'd3_00029': 2,
    'd3_00045': 2,
    'd3_00046': 2,
    'd3_00048': 2,
    'd3_00049': 2,
    'd3_00050': 2,
    'd3_00051': 2,
    'd3_00052': 2,
    'd3_00054': 2,
    'd3_00055': 2,
    'd3_00056': 2,
}


def _removed_analysis_result(code):
    return pd.DataFrame([{
        "Dimensão": code.upper(),
        "Resposta": "N/A",
        "Descrição da Dimensão": "Verificação sem implementação no motor atual",
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
