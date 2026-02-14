import streamlit as st
from core import calculos, database, relatorios
from components import ui

def render():
    st.title("🔮 Oráculo de Crédito")
    st.caption("Cálculo Reverso: Do bolso do cliente para o imóvel ideal")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Premissas")
        parcela_alvo = st.number_input("Teto da Parcela (R$)", 500.0, value=2500.0, step=100.0)
        entrada = st.number_input("Entrada Disponível (R$)", 0.0, value=40000.0, step=1000.0)
        chaves = st.number_input("Chaves / FGTS (R$)", 0.0, value=10000.0, step=1000.0)
        
        st.markdown("---")
        meses = st.slider("Prazo Desejado (Meses)", 12, 420, 100, key="slider_oraculo")
        sistema = st.selectbox("Sistema de Amortização", ["SAC", "PRICE"], key="select_oraculo")

    # Realiza o cálculo usando o motor no core/calculos.py
    # Assumindo juros padrão de 0.5% e taxa adm de 25.0
    teto_financiamento = calculos.calcular_poder_compra(parcela_alvo, meses, 0.005, sistema, 25.0)
    poder_compra_total = teto_financiamento + entrada + chaves

    with col2:
        st.markdown(f"""
        <div class="oracle-card">
            <h3 style="color: #94a3b8; font-size: 0.8rem; letter-spacing: 1px; margin-bottom: 10px;">POTENCIAL DE COMPRA</h3>
            <h1 style="color: #3b82f6; font-size: 3.5rem; margin: 0; text-shadow: 0 0 20px rgba(59,130,246,0.3);">
                R$ {poder_compra_total:,.2f}
            </h1>
            <p style="color: #64748b; font-size: 0.9rem; margin-top: 15px;">Baseado em uma parcela de R$ {parcela_alvo:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"O cliente consegue financiar até **R$ {teto_financiamento:,.2f}** com estas condições.")