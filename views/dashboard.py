import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core import database
from components import ui, charts

def render():
    st.title("📊 Painel de Performance")
    
    # 1. Identifica o utilizador
    usuario_atual = st.session_state.get('username_logado', 'admin')
    
    # 2. Busca os dados (já com o cache que implementamos)
    df = database.buscar_dados_dashboard(usuario_atual)

    if df.empty:
        st.info("Ainda não há dados para filtrar.")
        return

    # --- NOVO: FILTROS DE DATA ---
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📅 Filtros de Período")
        hoje = datetime.now().date()
        
        opcao_data = st.selectbox(
            "Selecionar Período",
            ["Tudo", "Hoje", "Últimos 7 dias", "Este Mês", "Personalizado"]
        )

        if opcao_data == "Hoje":
            df = df[df['data_criacao'].dt.date == hoje]
        elif opcao_data == "Últimos 7 dias":
            inicio = hoje - timedelta(days=7)
            df = df[df['data_criacao'].dt.date >= inicio]
        elif opcao_data == "Este Mês":
            df = df[df['data_criacao'].dt.month == hoje.month]
        elif opcao_data == "Personalizado":
            intervalo = st.date_input("Escolha o intervalo", [hoje - timedelta(days=30), hoje])
            if len(intervalo) == 2:
                df = df[(df['data_criacao'].dt.date >= intervalo[0]) & (df['data_criacao'].dt.date <= intervalo[1])]

    # 3. Lógica de KPIs com o DF Filtrado
    st.markdown(f"**Período:** {opcao_data}")
    
    if df.empty:
        st.warning("Nenhuma simulação encontrada para este período.")
        return

    total_vgt = df['valor_imovel'].sum()
    total_sims = len(df)
    aprovados = df[df['status'].str.upper().str.contains('APROVADO', na=False)].shape[0]
    taxa_aprovacao = (aprovados / total_sims * 100) if total_sims > 0 else 0

    # 4. Cards e Gráficos (O resto do código permanece igual, mas agora usando o DF filtrado)
    k1, k2, k3 = st.columns(3)
    k1.markdown(ui.card_html("Volume (VGT)", f"R$ {total_vgt:,.0f}"), unsafe_allow_html=True)
    k2.markdown(ui.card_html("Simulações", f"{total_sims}"), unsafe_allow_html=True)
    k3.markdown(ui.card_html("Taxa Aprovação", f"{taxa_aprovacao:.1f}%"), unsafe_allow_html=True)

    st.markdown("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(charts.grafico_timeline_simulacoes(df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.grafico_pizza_status(df), use_container_width=True)