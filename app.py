import streamlit as st
import pandas as pd
import calculos
import database
import relatorios

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Imobiliária PG - Sistema Premium",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUNÇÃO DE ESTILO (Agora lê do arquivo separado) ---
def setup_style():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    setup_style() # Aplica o CSS do arquivo assets/style.css
    database.init_db()

    # --- 3. SIDEBAR (Inputs) ---
    with st.sidebar:
        st.markdown("### ⚙️ Parâmetros")
        
        with st.expander("👤 Cliente", expanded=True):
            cliente = st.text_input("Nome", "Cliente Modelo")
            renda = st.number_input("Renda Mensal (R$)", min_value=1000.0, step=500.0, value=8500.0)

        with st.expander("🏠 Imóvel", expanded=True):
            valor_imovel = st.number_input("Valor Total (R$)", min_value=50000.0, value=350000.0, step=1000.0)
            entrada = st.number_input("Entrada (R$)", min_value=0.0, value=50000.0, step=1000.0)
            chaves = st.number_input("Chaves (R$)", min_value=0.0, value=30000.0, step=1000.0)

        with st.expander("💰 Condições", expanded=True):
            meses = st.slider("Prazo (Meses)", 12, 120, 100)
            qtd_intercaladas = st.number_input("Qtd. Anuais", 0, 10, 8)
            valor_intercalada = st.number_input("Valor Anual (R$)", 0.0, value=5000.0, step=500.0)
            taxa_correcao = st.number_input("Correção Mensal (%)", 0.0, 2.0, 0.5) / 100
            
            st.divider()
            sistema = st.radio("Amortização", ["SAC", "PRICE"], horizontal=True)

    # --- 4. CÁLCULOS ---
    saldo_devedor, total_intercaladas = calculos.calcular_saldo_devedor(
        valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada
    )
    
    df_evolucao = calculos.projetar_amortizacao(saldo_devedor, meses, taxa_correcao, sistema)
    parcela_inicial = df_evolucao.iloc[0]['Parcela'] if not df_evolucao.empty else 0.0
    cor_status, texto_status, msg_status, percentual_comp = calculos.analisar_credito(parcela_inicial, renda)

    # Dados para PDF/DB
    dados_completos = {
        'cliente': cliente, 'valor_imovel': valor_imovel, 'entrada': entrada,
        'chaves': chaves, 'total_intercaladas': total_intercaladas,
        'saldo_devedor': saldo_devedor, 'meses': meses, 'parcela': parcela_inicial,
        'status_texto': texto_status
    }

    # --- 5. INTERFACE PRINCIPAL ---
    st.title("🌊 Vendas Praia Grande")
    st.caption("Sistema de Simulação de Financiamento Direto")

    if saldo_devedor < 0:
        st.error("⚠️ Atenção: O valor da entrada supera o valor do imóvel.")
        return

    # Cards de Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("1ª Parcela", f"R$ {parcela_inicial:,.2f}", delta=sistema)
    with col2: st.metric("Saldo Financiado", f"R$ {saldo_devedor:,.2f}")
    with col3: st.metric("Renda Comprometida", f"{percentual_comp:.1f}%", delta_color="inverse")
    with col4: st.metric("Total Intercaladas", f"R$ {total_intercaladas:,.2f}")

    # Status Visual
    st.markdown(f"""
        <div style="background-color: {cor_status}; color: white; padding: 16px; border-radius: 12px; text-align: center; margin: 20px 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); font-weight: 600;">
            {texto_status} — {msg_status}
        </div>
    """, unsafe_allow_html=True)

    # Abas
    tab1, tab2, tab3 = st.tabs(["📊 Gráficos & Tabela", "📄 Documentação", "📂 Histórico"])

    with tab1:
        st.subheader("Evolução Financeira")
        st.area_chart(df_evolucao, x="Mês", y=["Parcela"], color="#3b82f6")
        st.markdown("#### Detalhamento Mensal")
        st.dataframe(df_evolucao, use_container_width=True, hide_index=True,
            column_config={
                "Mês": st.column_config.NumberColumn(format="%d"),
                "Parcela": st.column_config.NumberColumn(format="R$ %.2f"),
                "Amortização": st.column_config.NumberColumn(format="R$ %.2f"),
                "Juros": st.column_config.NumberColumn(format="R$ %.2f"),
                "Saldo Devedor": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )

    with tab2:
        st.info("Gere a proposta oficial em PDF.")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Salvar Simulação", use_container_width=True):
                database.salvar_simulacao(cliente, valor_imovel, entrada, parcela_inicial, texto_status)
                st.toast("Simulação salva!", icon="✅")
        with col_b2:
            if st.button("📄 Baixar PDF", type="primary", use_container_width=True):
                arquivo = relatorios.gerar_proposta_pdf(dados_completos)
                with open(arquivo, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=arquivo, mime="application/pdf", use_container_width=True)

    with tab3:
        st.subheader("Histórico")
        st.dataframe(database.carregar_historico(), use_container_width=True)

if __name__ == "__main__":
    main()