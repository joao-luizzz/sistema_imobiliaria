import streamlit as st
import pandas as pd
import calculos
import database
import relatorios

# Configuração Inicial
st.set_page_config(page_title="Imobiliária PG - MVP", layout="wide", page_icon="🏢")

def main():
    # Garante que o DB existe ao iniciar
    database.init_db()

    # --- 1. SIDEBAR (Inputs vêm PRIMEIRO) ---
    with st.sidebar:
        st.header("Dados do Cliente")
        cliente = st.text_input("Nome", "João Silva")
        renda = st.number_input("Renda Familiar (R$)", min_value=1000.0, step=500.0, value=8500.0)
        
        st.divider()
        st.header("Valores do Imóvel")
        valor_imovel = st.number_input("Valor Total (R$)", min_value=50000.0, value=350000.0, step=1000.0)
        entrada = st.number_input("Entrada (R$)", min_value=0.0, value=50000.0, step=1000.0)
        chaves = st.number_input("Chaves (R$)", min_value=0.0, value=30000.0, step=1000.0)
        
        st.divider()
        st.header("Condições")
        meses = st.slider("Parcelas Mensais", 12, 120, 100)
        qtd_intercaladas = st.number_input("Qtd. Anuais", 0, 10, 8)
        valor_intercalada = st.number_input("Valor Anual (R$)", 0.0, value=5000.0, step=500.0)
        
        # Correção Monetária
        taxa_correcao = st.number_input("Taxa Simulação (% a.m.)", 0.0, 2.0, 0.5) / 100
        
        st.divider()
        # SELETOR NOVO (SAC vs PRICE)
        st.header("Sistema de Amortização")
        sistema = st.radio("Escolha o Sistema", ["SAC", "PRICE"], help="SAC: Parcelas decrescentes. PRICE: Parcelas fixas.")

    # --- 2. PROCESSAMENTO (Cálculos vêm DEPOIS dos inputs) ---
    
    # 2.1 Calcula o Saldo Devedor Inicial
    saldo_devedor, total_intercaladas = calculos.calcular_saldo_devedor(
        valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada
    )
    
    # 2.2 Gera a Tabela Completa (A nova função do calculos.py)
    df_evolucao = calculos.projetar_amortizacao(saldo_devedor, meses, taxa_correcao, sistema)
    
    # 2.3 Extrai a 1ª Parcela para exibir nos KPIs (evita erro se tabela vazia)
    if not df_evolucao.empty:
        parcela_inicial = df_evolucao.iloc[0]['Parcela']
    else:
        parcela_inicial = 0.0

    # 2.4 Analisa Crédito com base na parcela inicial
    cor_status, texto_status, msg_status, percentual_comp = calculos.analisar_credito(parcela_inicial, renda)

    # Preparar dados para o PDF/Banco
    dados_completos = {
        'cliente': cliente,
        'valor_imovel': valor_imovel,
        'entrada': entrada,
        'chaves': chaves,
        'total_intercaladas': total_intercaladas,
        'saldo_devedor': saldo_devedor,
        'meses': meses,
        'parcela': parcela_inicial,
        'status_texto': texto_status
    }

    # --- 3. EXIBIÇÃO (Interface Principal) ---
    
    st.title("🌊 Sistema de Vendas - Praia Grande")
    st.markdown("### Simulador de Financiamento Direto")

    # Validação de Erro
    if saldo_devedor < 0:
        st.error("ERRO: A entrada + chaves + intercaladas supera o valor do imóvel!")
        return

    # Cards (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric(f"1ª Parcela ({sistema})", f"R$ {parcela_inicial:,.2f}")
    col2.metric("Saldo a Financiar", f"R$ {saldo_devedor:,.2f}")
    col3.metric("Comprometimento", f"{percentual_comp:.1f}%")

    # Status Visual (Semáforo)
    st.markdown(f"""
        <div style="background-color:{cor_status}; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom: 20px;">
            <h3>{texto_status}</h3>
            <p>{msg_status}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. ABAS (Onde entra o teu código novo) ---
    tab1, tab2, tab3 = st.tabs(["📈 Projeção Detalhada", "📄 Gerar Proposta", "📂 Histórico"])

    with tab1:
        st.subheader(f"📈 Projeção via Tabela {sistema}")
        
        # Gráfico mostrando Parcela e Juros
        # O novo calculos.py retorna as colunas 'Parcela' e 'Juros', então usamos elas aqui
        st.line_chart(df_evolucao, x="Mês", y=["Parcela", "Juros"])
        
        st.divider()
        st.subheader("📋 Planilha de Evolução Mensal")
        st.dataframe(
            df_evolucao,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Mês": st.column_config.NumberColumn("Mês", format="%d"),
                "Parcela": st.column_config.NumberColumn("Valor Parcela", format="R$ %.2f"),
                "Amortização": st.column_config.NumberColumn("Amortização", format="R$ %.2f"),
                "Juros": st.column_config.NumberColumn("Juros", format="R$ %.2f"),
                "Saldo Devedor": st.column_config.NumberColumn("Saldo Restante", format="R$ %.2f"),
            }
        )

    with tab2:
        st.subheader("🖨️ Exportar Proposta")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Salvar no Banco", use_container_width=True):
                database.salvar_simulacao(cliente, valor_imovel, entrada, parcela_inicial, texto_status)
                st.success(f"Simulação salva!")
        
        with col_btn2:
            if st.button("📄 Baixar PDF", type="primary", use_container_width=True):
                arquivo = relatorios.gerar_proposta_pdf(dados_completos)
                with open(arquivo, "rb") as f:
                    st.download_button("⬇️ Download", f, file_name=arquivo, use_container_width=True)

    with tab3:
        st.subheader("📂 Histórico")
        st.dataframe(database.carregar_historico(), use_container_width=True)

if __name__ == "__main__":
    main()