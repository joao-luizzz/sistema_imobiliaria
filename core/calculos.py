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

# --- ADICIONE NO FINAL DE core/calculos.py ---

def calcular_antecipacao(saldo_inicial, taxa_mensal, sistema, parcela_atual, valor_extra, periodicidade="Mensal"):
    """
    Simula o impacto de pagar um valor extra recorrente.
    Retorna: Novo Prazo (meses), Juros Totais Pagos, Economia Gerada
    """
    saldo = saldo_inicial
    meses_percorridos = 0
    total_juros_com_extra = 0
    
    # Loop de simulação mês a mês
    while saldo > 0 and meses_percorridos < 420: # Limite de segurança
        meses_percorridos += 1
        
        # 1. Calcula Juros do mês
        juros = saldo * taxa_mensal
        total_juros_com_extra += juros
        
        # 2. Define amortização normal
        if sistema == "SAC":
            amortizacao = parcela_atual - juros # Simplificação baseada na parcela média/inicial
            # Nota: No SAC a parcela cai, mas para antecipação vamos assumir o esforço financeiro constante
        else: # PRICE
            amortizacao = parcela_atual - juros
            
        # 3. Aplica o Extra
        amortizacao_extra = 0
        if periodicidade == "Mensal":
            amortizacao_extra = valor_extra
        elif periodicidade == "Anual" and meses_percorridos % 12 == 0:
            amortizacao_extra = valor_extra
        elif periodicidade == "Única (Agora)" and meses_percorridos == 1:
            amortizacao_extra = valor_extra

        # 4. Abate do saldo
        saldo -= (amortizacao + amortizacao_extra)
        
        # Se pagou tudo, para
        if saldo < 0:
            saldo = 0
            
    return meses_percorridos, total_juros_com_extra