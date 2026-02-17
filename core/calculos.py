import pandas as pd
import math

def calcular_sac(valor_financiado, taxa_anual, meses):
    """
    Sistema de Amortização Constante (SAC):
    - Amortização fixa
    - Juros decrescentes
    - Parcela decrescente
    """
    # Converter taxa anual para mensal
    i = (taxa_anual / 100) / 12
    
    # No SAC, a amortização é constante
    amortizacao = valor_financiado / meses
    
    dados = []
    saldo_devedor = valor_financiado
    
    for n in range(1, meses + 1):
        juros = saldo_devedor * i
        parcela = amortizacao + juros
        saldo_devedor -= amortizacao
        
        # Correção de arredondamento para não ficar -0.00
        if saldo_devedor < 0:
            saldo_devedor = 0
            
        dados.append([n, parcela, amortizacao, juros, saldo_devedor])
        
    # Cria o DataFrame
    df = pd.DataFrame(dados, columns=['Mes', 'Parcela', 'Amortizacao', 'Juros', 'Saldo Devedor'])
    return df

def calcular_price(valor_financiado, taxa_anual, meses):
    """
    Tabela Price (Sistema Francês):
    - Parcela fixa (PMT)
    - Juros decrescentes
    - Amortização crescente
    """
    i = (taxa_anual / 100) / 12
    
    # Fórmula do PMT (Pagamento Periódico)
    if i == 0:
        parcela_fixa = valor_financiado / meses
    else:
        parcela_fixa = valor_financiado * (i * (1 + i)**meses) / ((1 + i)**meses - 1)
        
    dados = []
    saldo_devedor = valor_financiado
    
    for n in range(1, meses + 1):
        juros = saldo_devedor * i
        amortizacao = parcela_fixa - juros
        saldo_devedor -= amortizacao
        
        if saldo_devedor < 0:
            saldo_devedor = 0
            
        dados.append([n, parcela_fixa, amortizacao, juros, saldo_devedor])
        
    df = pd.DataFrame(dados, columns=['Mes', 'Parcela', 'Amortizacao', 'Juros', 'Saldo Devedor'])
    return df