import streamlit as st
import pandas as pd
from services import simulacao_service # <--- Mudou aqui
from components import charts, ui

def render():
    st.title("📊 Dashboard Gerencial")
    st.caption("Visão geral da performance do time comercial.")
    
    st.divider()

    # Carrega dados via Service
    usuario = st.session_state.get('username_logado', 'admin')
    df = simulacao_service.obter_dados_dashboard(usuario) # <--- Mudou aqui

    if df.empty:
        st.warning("⚠️ Ainda não há simulações salvas para gerar indicadores.")
        return

    # --- 1. KPIs ---
    total_simulacoes = len(df)
    volume_total = df['valor_imovel'].sum() if 'valor_imovel' in df.columns else 0
    ticket_medio = volume_total / total_simulacoes if total_simulacoes > 0 else 0

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(ui.card_html("Simulações", str(total_simulacoes), "Total acumulado"), unsafe_allow_html=True)
    with kpi2:
        st.markdown(ui.card_html("Volume Potencial", ui.formatar_moeda(volume_total), "Soma dos Imóveis"), unsafe_allow_html=True)
    with kpi3:
        st.markdown(ui.card_html("Ticket Médio", ui.formatar_moeda(ticket_medio), "Valor Médio / Imóvel"), unsafe_allow_html=True)

    st.write("") 

    # --- 2. GRÁFICOS ---
    g1, g2 = st.columns(2)

    with g1:
        with st.container(border=True):
            st.markdown("##### 📅 Evolução Temporal")
            st.plotly_chart(charts.grafico_timeline_simulacoes(df), use_container_width=True)

    with g2:
        with st.container(border=True):
            st.markdown("##### 📝 Status das Propostas")
            # Verifica qual nome da função existe no seu charts.py
            if hasattr(charts, 'grafico_pizza_status'):
                st.plotly_chart(charts.grafico_pizza_status(df), use_container_width=True)
            elif hasattr(charts, 'grafico_status_propostas'):
                st.plotly_chart(charts.grafico_status_propostas(df), use_container_width=True)