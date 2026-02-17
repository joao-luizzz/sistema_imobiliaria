import streamlit as st
from components import ui

def render():
    st.title("🔮 O Oráculo do Crédito")
    st.caption("Descubra quanto o cliente pode financiar baseado na renda dele.")
    
    st.divider()

    left_col, right_col = st.columns([1, 1.5], gap="large")

    # --- INPUTS (ESQUERDA) ---
    with left_col:
        with st.container(border=True):
            st.markdown("### 💰 Renda & Perfil")
            
            # Renda
            st.markdown("vals **Renda Mensal Bruta**")
            renda = st.number_input("Renda", min_value=1000.0, value=10000.0, step=500.0, format="%.2f", label_visibility="collapsed")
            st.markdown(f"<div style='color: #10b981; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;'>💰 {ui.formatar_moeda(renda)}</div>", unsafe_allow_html=True)

            # Entrada Disponível
            st.markdown("vals **Entrada Disponível**")
            entrada_disponivel = st.number_input("Entrada", min_value=0.0, value=50000.0, step=1000.0, format="%.2f", label_visibility="collapsed")
            st.caption(f"Visual: {ui.formatar_moeda(entrada_disponivel)}")
            
            st.divider()
            
            # Condições
            st.markdown("### ⚙️ Condições do Banco")
            prazo_anos = st.slider("Prazo (Anos)", 10, 35, 30)
            taxa_anual = st.slider("Taxa de Juros (%)", 6.0, 15.0, 9.99, 0.1)
            comprometimento = st.slider("Limite de Parcela (Renda)", 20, 35, 30, help="Geralmente os bancos travam em 30%")

    # --- CÁLCULOS ---
    margem_parcela = renda * (comprometimento / 100)
    taxa_mensal = (taxa_anual / 100) / 12
    meses = prazo_anos * 12
    
    # Cálculo Reverso (PMT -> Valor Presente) - Aproximação Tabela Price
    # PV = PMT * [ (1 - (1+i)^-n) / i ]
    valor_financiavel = margem_parcela * ((1 - (1 + taxa_mensal) ** (-meses)) / taxa_mensal)
    
    poder_compra = valor_financiavel + entrada_disponivel

    # --- RESULTADOS (DIREITA) ---
    with right_col:
        with st.container(border=True):
            st.subheader("🎯 Resultado da Análise")
            
            # Destaque Principal
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background-color: #f8fafc; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin:0; color: #64748b; font-size: 1rem;">Poder de Compra (Imóvel Máximo)</p>
                <h1 style="margin:0; color: #3b82f6; font-size: 3rem;">{ui.formatar_moeda(poder_compra)}</h1>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            c1.markdown(ui.card_html("Financiamento Teto", ui.formatar_moeda(valor_financiavel), "Limite do Banco"), unsafe_allow_html=True)
            c2.markdown(ui.card_html("Parcela Máxima", ui.formatar_moeda(margem_parcela), f"{comprometimento}% da Renda"), unsafe_allow_html=True)

        st.write("")
        st.info(f"ℹ️ **Interpretação:** Com renda de **{ui.formatar_moeda(renda)}**, o banco libera uma parcela de até **{ui.formatar_moeda(margem_parcela)}**. Isso paga um financiamento de **{ui.formatar_moeda(valor_financiavel)}** em {prazo_anos} anos.")