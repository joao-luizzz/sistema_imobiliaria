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
    Retorna: Cor, Status, Mensagem e % de Comprometimento.
    """
    comprometimento = (parcela / renda) * 100 if renda > 0 else 0
    
    if comprometimento < 30:
        # Verde Esmeralda (menos neon)
        return "#059669", "APROVADO", "Comprometimento saudável.", comprometimento
    elif 30 <= comprometimento <= 40:
        # Amarelo Ouro
        return "#d97706", "ATENÇÃO", "Considere aumentar a entrada.", comprometimento
    else:
        # Vermelho Rosado (Rose 600) - Muito mais elegante que o vermelho puro
        return "#e11d48", "REPROVADO", "Risco alto (>40%).", comprometimento

def projetar_amortizacao(saldo_inicial, meses, taxa_mensal, sistema="SAC"):
    """
    Gera a tabela de amortização profissional (SAC ou PRICE).
    """
    dados = []
    saldo_devedor = saldo_inicial
    i = taxa_mensal
    n = meses

    # Definição da Parcela ou Amortização inicial
    if sistema == "PRICE":
        # Fórmula Price: PMT = PV * [i(1+i)^n] / [(1+i)^n - 1]
        if i > 0:
            parcela_fixa = saldo_inicial * (i * (1 + i)**n) / ((1 + i)**n - 1)
        else:
            parcela_fixa = saldo_inicial / n
    else: # SAC
        amortizacao_fixa = saldo_inicial / n

    for mes in range(1, n + 1):
        juros = saldo_devedor * i
        
        if sistema == "PRICE":
            amortizacao = parcela_fixa - juros
            parcela = parcela_fixa
        else: # SAC
            amortizacao = amortizacao_fixa
            parcela = amortizacao + juros
        
        saldo_devedor -= amortizacao
        if saldo_devedor < 0: saldo_devedor = 0

        dados.append({
            "Mês": mes,
            "Parcela": parcela,
            "Amortização": amortizacao,
            "Juros": juros,
            "Saldo Devedor": saldo_devedor
        })

    return pd.DataFrame(dados)