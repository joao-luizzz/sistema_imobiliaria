import pandas as pd

def calcular_saldo_devedor(valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada):
    total_intercaladas = qtd_intercaladas * valor_intercalada
    total_deducoes = entrada + chaves + total_intercaladas
    saldo_devedor = valor_imovel - total_deducoes
    return saldo_devedor, total_intercaladas

def calcular_parcela(saldo_devedor, meses):
    if saldo_devedor <= 0: return 0.0
    return saldo_devedor / meses if meses > 0 else 0.0

def analisar_credito(parcela, renda):
    comprometimento = (parcela / renda) * 100 if renda > 0 else 0
    if comprometimento < 30:
        return "green", "APROVADO", "Comprometimento saudável (<30%).", comprometimento
    elif 30 <= comprometimento <= 40:
        return "orange", "ATENÇÃO", "Entre 30% e 40%.", comprometimento
    else:
        return "red", "REPROVADO", "Risco alto (>40%).", comprometimento

def projetar_evolucao(saldo, parcela, meses, taxa):
    dados = []
    for i in range(1, meses + 1):
        dados.append({"Mês": i, "Valor Parcela": parcela * ((1 + taxa) ** i)})
    return pd.DataFrame(dados)
