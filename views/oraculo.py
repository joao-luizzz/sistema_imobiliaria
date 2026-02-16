import streamlit as st
from core import calculos
from components import ui

def render():
    st.title("🔮 O Oráculo Imobiliário")
    st.markdown("Descubra o **poder de compra** do cliente baseado na renda.")

    # --- 1. PARÂMETROS ---
    with st.container():
        c1, c2, c3 = st.columns(3)
        renda = c1.number_input("Renda Mensal (R$)", min_value=1000.0, value=10000.0, step=500.0, format="%.2f")
        entrada_disponivel = c2.number_input("Entrada Disponível (R$)", min_value=0.0, value=50000.0, step=1000.0, format="%.2f")
        prazo_anos = c3.slider("Prazo Desejado (Anos)", 10, 35, 30)
        
        # Opções avançadas escondidas para não poluir
        with st.expander("⚙️ Ajustes Finos (Taxas e Limites)"):
            ec1, ec2 = st.columns(2)
            taxa_anual = ec1.number_input("Taxa de Juros Anual (%)", 5.0, 15.0, 9.5)
            comprometimento = ec2.slider("Limite de Comprometimento (%)", 20, 35, 30, help="Quanto da renda o banco aceita usar?") / 100

    st.markdown("---")

    # --- 2. CÁLCULO REVERSO ---
    if st.button("🔮 Revelar Poder de Compra", type="primary", use_container_width=True):
        with st.spinner("Consultando os astros financeiros..."):
            # A) Máxima parcela permitida
            max_parcela = renda * comprometimento
            
            # B) Converter taxa anual para mensal
            taxa_mensal = (1 + (taxa_anual / 100))**(1/12) - 1
            meses = prazo_anos * 12
            
            # C) Cálculo Reverso (Valor Presente de uma Anuidade - Fórmula PV)
            # Valor Financiado = Parcela * [ (1 - (1+i)^-n) / i ]
            # (Fórmula simplificada da Tabela Price para estimativa de teto)
            valor_financiado_teto = max_parcela * ((1 - (1 + taxa_mensal)**(-meses)) / taxa_mensal)
            
            # D) Valor do Imóvel = Financiado + Entrada
            potencial_compra = valor_financiado_teto + entrada_disponivel

        # --- 3. RESULTADOS ---
        st.canvas = st.container()
        
        # Destaque Principal
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: rgba(16, 185, 129, 0.1); border-radius: 15px; border: 1px solid #10b981;">
            <p style="color: #cbd5e1; margin-bottom: 5px;">Potencial Máximo de Compra</p>
            <h1 style="color: #10b981; font-size: 3rem; margin: 0;">R$ {potencial_compra:,.2f}</h1>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 10px;">
                Considerando entrada de R$ {entrada_disponivel:,.2f} + Financiamento de R$ {valor_financiado_teto:,.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Espaço

        # Cards de Detalhes
        k1, k2, k3 = st.columns(3)
        k1.markdown(ui.card_html("Parcela Teto", f"R$ {max_parcela:,.2f}", "30% da Renda"), unsafe_allow_html=True)
        k2.markdown(ui.card_html("Renda Mínima", f"R$ {renda:,.2f}", "Utilizada no cálculo"), unsafe_allow_html=True)
        k3.markdown(ui.card_html("Prazo", f"{meses} meses", f"{prazo_anos} anos"), unsafe_allow_html=True)

        st.markdown("### 🏠 O que dá para comprar com isso?")
        
        # Sugestões visuais (Fictícias, mas dão um charme)
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.info(f"🏢 **Apartamento Padrão**\n\nIdeal para unidades de 2 ou 3 quartos em regiões valorizadas. Busque por imóveis na faixa de R$ {potencial_compra * 0.9:,.0f}.")
            
        with col_b:
            st.warning(f"🏘️ **Casa em Condomínio**\n\nPossível em bairros em expansão. Considere reservar R$ {potencial_compra * 0.05:,.0f} para documentação.")
            
        with col_c:
            st.success(f"🏗️ **Imóvel na Planta**\n\nAlto potencial de negociação. Com essa entrada de R$ {entrada_disponivel:,.0f}, você consegue ótimos fluxos de obra.")