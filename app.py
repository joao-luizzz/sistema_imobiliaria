import streamlit as st
import pandas as pd
import calculos
import database
import relatorios
import urllib.parse # <--- IMPORTANTE: Necessário para o link do WhatsApp

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Sistema Imobiliário",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILO PROFISSIONAL (CSS) ---
def setup_style():
    # Carrega o CSS base do arquivo
    with open("assets/style.css") as f:
        css = f.read()
    
    st.markdown(f"""
    <style>
        {css}
        
        /* Ajuste de Títulos */
        h1 {{ font-weight: 700; letter-spacing: -1px; font-size: 2.2rem; }}
        h2, h3 {{ font-weight: 600; letter-spacing: -0.5px; }}
        
        /* Sidebar Clean */
        [data-testid="stSidebar"] h1 {{
            font-size: 0.9rem; text-transform: uppercase; color: #64748b; letter-spacing: 1px; margin-top: 20px;
        }}
        
        /* TABELA TRANSPARENTE (Estilo Minimalista) */
        [data-testid="stDataFrame"] {{
            background-color: transparent !important;
        }}
        [data-testid="stDataFrame"] div[class*="stDataFrame"] {{
            background-color: transparent !important;
            border: none !important;
        }}
        /* Remove bordas verticais e deixa só as horizontais */
        div[role="grid"] {{
            border: none !important;
        }}
        
        /* Rodapé Legal */
        .legal-footer {{
            font-size: 0.75rem; color: #94a3b8; text-align: center; margin-top: 50px;
            border-top: 1px solid #334155; padding-top: 20px;
        }}
    </style>
    """, unsafe_allow_html=True)

def main():
    setup_style()
    database.init_db()

    # --- 3. SIDEBAR ---
    with st.sidebar:
        st.markdown("## ⚙️ Configuração") 
        
        st.markdown("### CLIENTE")
        cliente = st.text_input("Nome Completo", "Cliente Modelo")
        renda = st.number_input("Renda Mensal (R$)", 1000.0, step=500.0, value=8500.0)

        st.divider()

        st.markdown("### IMÓVEL")
        valor_imovel = st.number_input("Valor Venda (R$)", 50000.0, value=350000.0, step=1000.0)
        entrada = st.number_input("Entrada (R$)", 0.0, value=50000.0, step=1000.0)
        chaves = st.number_input("Chaves (R$)", 0.0, value=30000.0, step=1000.0)

        st.divider()

        st.markdown("### PAGAMENTO")
        meses = st.slider("Prazo (Meses)", 12, 120, 100)
        c1, c2 = st.columns(2)
        with c1: qtd_intercaladas = st.number_input("Qtd. Anuais", 0, 10, 8)
        with c2: valor_intercalada = st.number_input("Valor Anual", 0.0, value=5000.0, step=500.0)
        
        taxa_correcao = st.number_input("Juros (% a.m.)", 0.0, 2.0, 0.5) / 100
        sistema = st.selectbox("Amortização", ["SAC", "PRICE"])

    # --- 4. CÁLCULOS ---
    saldo_devedor, total_intercaladas = calculos.calcular_saldo_devedor(
        valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada
    )
    
    df_evolucao = calculos.projetar_amortizacao(saldo_devedor, meses, taxa_correcao, sistema)
    parcela_inicial = df_evolucao.iloc[0]['Parcela'] if not df_evolucao.empty else 0.0
    cor_status, texto_status, msg_status, percentual_comp = calculos.analisar_credito(parcela_inicial, renda)

    dados_completos = {
        'cliente': cliente, 'valor_imovel': valor_imovel, 'entrada': entrada,
        'chaves': chaves, 'total_intercaladas': total_intercaladas,
        'saldo_devedor': saldo_devedor, 'meses': meses, 'parcela': parcela_inicial,
        'status_texto': texto_status
    }

    # --- 5. INTERFACE PRINCIPAL ---
    col_logo, col_titulo = st.columns([1, 5])
    with col_titulo:
        st.title("Simulador Financeiro")
        st.caption(f"Proposta Comercial • {cliente}")

    if saldo_devedor < 0:
        st.error("Erro: A entrada supera o valor do imóvel.")
        return

    st.markdown("---")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("1ª Parcela", f"R$ {parcela_inicial:,.2f}", delta=sistema)
    c2.metric("Saldo Financiado", f"R$ {saldo_devedor:,.2f}")
    c3.metric("Renda Comprometida", f"{percentual_comp:.1f}%", delta_color="inverse")
    c4.metric("Total Anuais", f"R$ {total_intercaladas:,.2f}")

    # Status Box
    st.markdown(f"""
        <div style="background-color: {cor_status}15; border: 1px solid {cor_status}40; color: {cor_status}; padding: 12px 20px; border-radius: 8px; margin: 24px 0; font-weight: 500; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">●</span> {texto_status}: {msg_status}
        </div>
    """, unsafe_allow_html=True)

    # ABAS
    tab_analise, tab_docs, tab_hist = st.tabs(["📊 Fluxo Financeiro", "📑 Documentação", "📂 Histórico"])

    with tab_analise:
        st.subheader("Evolução do Saldo")
        st.area_chart(df_evolucao, x="Mês", y=["Parcela"], color="#3b82f6")
        
        st.markdown("#### Detalhamento Mês a Mês")
        # AQUI ESTÁ A MÁGICA DA TABELA
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

    with tab_docs:
        st.subheader("Finalizar Proposta")
        
        # --- LÓGICA DO WHATSAPP ---
        texto_zap = f"""
Olá *{cliente}*! 👋 Segue a proposta para o imóvel na Praia Grande:

💰 *Valor:* R$ {valor_imovel:,.2f}
📉 *Entrada:* R$ {entrada:,.2f}
📅 *Plano:* {meses}x de R$ {parcela_inicial:,.2f} ({sistema})
🔑 *Chaves:* R$ {chaves:,.2f}

_Podemos agendar a visita?_"""
        
        texto_encoded = urllib.parse.quote(texto_zap)
        link_zap = f"https://wa.me/?text={texto_encoded}"

        col_zap, col_pdf, col_save = st.columns([2, 2, 1.5])
        
        with col_zap:
            # Use help para explicar o que o botão faz
            st.link_button("📲 Enviar no WhatsApp", link_zap, type="primary", use_container_width=True, help="Abre o WhatsApp Web com a mensagem pronta")
        
        with col_pdf:
            if st.button("📄 Gerar PDF", use_container_width=True):
                arquivo = relatorios.gerar_proposta_pdf(dados_completos)
                with open(arquivo, "rb") as f:
                    st.download_button("⬇️ Baixar", f, file_name=arquivo, mime="application/pdf", use_container_width=True)
        
        with col_save:
            if st.button("💾 Salvar", use_container_width=True):
                database.salvar_simulacao(cliente, valor_imovel, entrada, parcela_inicial, texto_status)
                st.toast("Salvo no sistema!", icon="✅")

    with tab_hist:
        st.dataframe(database.carregar_historico(), use_container_width=True)

    # Rodapé
    st.markdown("""
        <div class="legal-footer">
            Imobiliária System v2.0 • Praia Grande/SP<br>
            Simulação sem efeito contratual. Valores sujeitos a análise de crédito.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()