import streamlit as st
import pandas as pd
import calculos
import database
import relatorios

# --- 1. CONFIGURAÇÃO E ESTILO (O SEGREDO DO DESIGN) ---
st.set_page_config(
    page_title="Imobiliária PG - Sistema Premium",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def setup_style():
    # Cores inspiradas no Tailwind: Slate, Emerald, Sky Blue
    st.markdown("""
    <style>
        /* Importando fonte moderna (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #f8fafc; /* Slate-50 */
            border-right: 1px solid #e2e8f0;
        }

        /* --- METRICS CARDS (Estilo Tailwind shadow-md rounded-xl) --- */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0; /* Slate-200 */
            border-radius: 0.75rem; /* rounded-xl */
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }

        /* --- INPUTS & SLIDERS --- */
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            border-radius: 0.5rem; /* rounded-lg */
            border: 1px solid #cbd5e1; /* Slate-300 */
        }
        
        .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
            border-color: #3b82f6; /* Blue-500 */
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
        }

        /* --- BOTÕES (Estilo Moderno) --- */
        .stButton > button {
            border-radius: 0.5rem;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
        }
        
        /* Botão Primário (Simulado) */
        div[data-testid="stVerticalBlock"] > div > div > div > div > .stButton > button {
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }

        /* --- ABAS (Tabs) --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 4px;
            color: #64748b; /* Slate-500 */
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(59, 130, 246, 0.1);
            color: #2563eb; /* Blue-600 */
        }

        /* --- CABEÇALHO --- */
        h1 {
            color: #0f172a; /* Slate-900 */
            letter-spacing: -0.025em;
        }
        h2, h3 {
            color: #334155; /* Slate-700 */
        }
        
        /* Remove padding extra do topo */
        .block-container {
            padding-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    setup_style() # Injeta o CSS moderno
    database.init_db()

    # --- 2. SIDEBAR (Inputs) ---
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

    # --- 3. PROCESSAMENTO ---
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

    # --- 4. INTERFACE PRINCIPAL ---
    st.title("🌊 Vendas Praia Grande")
    st.caption("Sistema de Simulação de Financiamento Direto")

    if saldo_devedor < 0:
        st.error("⚠️ Atenção: O valor da entrada supera o valor do imóvel.")
        return

    # 4.1 Cards de Métricas (Estilizados pelo CSS)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("1ª Parcela", f"R$ {parcela_inicial:,.2f}", delta=sistema)
    with col2: st.metric("Saldo Financiado", f"R$ {saldo_devedor:,.2f}")
    with col3: st.metric("Renda Comprometida", f"{percentual_comp:.1f}%", delta_color="inverse")
    with col4: st.metric("Total Intercaladas", f"R$ {total_intercaladas:,.2f}")

    # 4.2 Status Visual Moderno
    st.markdown(f"""
        <div style="
            background-color: {cor_status}; 
            color: white; 
            padding: 16px; 
            border-radius: 12px; 
            text-align: center; 
            margin: 20px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            font-weight: 600;
        ">
            {texto_status} — {msg_status}
        </div>
    """, unsafe_allow_html=True)

    # 4.3 Abas
    tab1, tab2, tab3 = st.tabs(["📊 Gráficos & Tabela", "📄 Documentação", "📂 Histórico"])

    with tab1:
        st.subheader("Evolução Financeira")
        # Gráfico de Área com cor moderna
        st.area_chart(df_evolucao, x="Mês", y=["Parcela"], color="#3b82f6")
        
        st.markdown("#### Detalhamento Mensal")
        st.dataframe(
            df_evolucao, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Mês": st.column_config.NumberColumn(format="%d"),
                "Parcela": st.column_config.NumberColumn(format="R$ %.2f"),
                "Amortização": st.column_config.NumberColumn(format="R$ %.2f"),
                "Juros": st.column_config.NumberColumn(format="R$ %.2f"),
                "Saldo Devedor": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )

    with tab2:
        st.info("Gere a proposta oficial em PDF para envio imediato.")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 Salvar Simulação", use_container_width=True):
                database.salvar_simulacao(cliente, valor_imovel, entrada, parcela_inicial, texto_status)
                st.toast("Simulação salva com sucesso!", icon="✅")
        with col_b2:
            if st.button("📄 Gerar PDF Oficial", type="primary", use_container_width=True):
                arquivo = relatorios.gerar_proposta_pdf(dados_completos)
                with open(arquivo, "rb") as f:
                    st.download_button("⬇️ Baixar PDF", f, file_name=arquivo, mime="application/pdf", use_container_width=True)

    with tab3:
        st.subheader("Últimas Simulações")
        st.dataframe(database.carregar_historico(), use_container_width=True)

if __name__ == "__main__":
    main()