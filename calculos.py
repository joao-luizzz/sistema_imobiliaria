import pandas as pd

def calcular_saldo_devedor(valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada):
    """Calcula o saldo devedor subtraindo todas as entradas."""
    total_intercaladas = qtd_intercaladas * valor_intercalada
    total_deducoes = entrada + chaves + total_intercaladas
    saldo_devedor = valor_imovel - total_deducoes
    return saldo_devedor, total_intercaladas

def analisar_credito(parcela, renda):
    """
    O 'Sinal de Trânsito' financeiro.
    Retorna: Cor Hex, Status, Mensagem e % de Comprometimento.
    """
    comprometimento = (parcela / renda) * 100 if renda > 0 else 0
    
    if comprometimento < 30:
        return "#059669", "APROVADO", "Comprometimento saudável (abaixo de 30%).", comprometimento
    elif 30 <= comprometimento <= 40:
        return "#d97706", "ATENÇÃO", "Limite de alerta! Considere aumentar a entrada.", comprometimento
    else:
        return "#e11d48", "REPROVADO", "Risco alto! Comprometimento acima de 40%.", comprometimento

def projetar_amortizacao(saldo_inicial, meses, taxa_mensal, sistema="SAC", tarifa=0.0):
    """
    Gera a tabela de amortização (SAC ou PRICE) incluindo Tarifas/Seguros.
    """
    dados = []
    saldo_devedor = saldo_inicial
    i = taxa_mensal
    n = meses

    # Definição da Parcela Base (Sem tarifa)
    if sistema == "PRICE":
        # Fórmula Price: PMT = PV * [i(1+i)^n] / [(1+i)^n - 1]
        if i > 0:
            parcela_base_fixa = saldo_inicial * (i * (1 + i)**n) / ((1 + i)**n - 1)
        else:
            parcela_base_fixa = saldo_inicial / n
    else: # SAC
        amortizacao_fixa = saldo_inicial / n

    for mes in range(1, n + 1):
        juros = saldo_devedor * i
        
        if sistema == "PRICE":
            amortizacao = parcela_base_fixa - juros
            parcela_base = parcela_base_fixa
        else: # SAC
            amortizacao = amortizacao_fixa
            parcela_base = amortizacao + juros
        
        # AQUI ESTÁ O REALISMO: Somamos a taxa na parcela final
        parcela_final = parcela_base + tarifa
        
        saldo_devedor -= amortizacao
        if saldo_devedor < 0: saldo_devedor = 0

        dados.append({
            "Mês": mes,
            "Parcela": parcela_final, # Usamos 'Parcela' como nome padrão para facilitar os gráficos
            "Amortização": amortizacao,
            "Juros": juros,
            "Seguros/Taxas": tarifa,
            "Saldo Devedor": saldo_devedor
        })

    return pd.DataFrame(dados)

def calcular_poder_compra(parcela_maxima, meses, taxa_mensal, sistema="SAC", tarifa=0.0):
    """
    ORÁCULO: Calcula quanto o banco financia dado um teto de parcela.
    """
    # 1. Tira a taxa do caminho (ela come margem)
    parcela_liquida = parcela_maxima - tarifa
    
    if parcela_liquida <= 0:
        return 0.0

    if sistema == "SAC":
        # No SAC, a primeira parcela é a maior. Usamos ela como teto.
        fator_divisao = (1 / meses) + taxa_mensal
        if fator_divisao == 0: return 0.0
        valor_financiado = parcela_liquida / fator_divisao
        
    else: # PRICE
        # Valor Presente de uma Anuidade (PV)
        if taxa_mensal > 0:
            fator_vp = (1 - (1 + taxa_mensal) ** (-meses)) / taxa_mensal
            valor_financiado = parcela_liquida * fator_vp
        else:
            valor_financiado = parcela_liquida * meses

    return valor_financiado