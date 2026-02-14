import streamlit as st
from core import database
from components import ui, charts

def render():
    st.title("📊 Painel de Performance")
    st.caption("Visão estratégica da sua operação imobiliária.")
    st.markdown("---")
    
    # 1. Identifica quem está vendo
    usuario_atual = st.session_state.get('username_logado', 'admin')
    
    # 2. Busca os dados no banco
    df = database.buscar_dados_dashboard(usuario_atual)

    # 3. Se não tiver dados, avisa e para
    if df.empty:
        st.info("Ainda não há dados suficientes para gerar os gráficos.")
        st.markdown("👉 Vá na aba **Simulação** e salve alguns atendimentos para testar!")
        return

    # 4. Cálculo dos KPIs (Os números grandes)
    total_vgt = df['valor_imovel'].sum()
    total_sims = len(df)
    
    # Conta quantos aprovados (ignorando maiúsculas/minúsculas)
    aprovados = df[df['status'].str.upper().str.contains('APROVADO', na=False)].shape[0]
    taxa_aprovacao = (aprovados / total_sims) * 100 if total_sims > 0 else 0

    # 5. Exibe os Cards no Topo
    k1, k2, k3 = st.columns(3)
    k1.markdown(ui.card_html("Volume Prospectado (VGT)", f"R$ {total_vgt:,.0f}"), unsafe_allow_html=True)
    k2.markdown(ui.card_html("Total Simulações", f"{total_sims}", "Leads cadastrados"), unsafe_allow_html=True)
    
    # Cor dinâmica: Verde se > 30%, Vermelho se < 30%
    cor_taxa = "#10b981" if taxa_aprovacao > 30 else "#ef4444"
    k3.markdown(ui.card_html("Taxa de Aprovação", f"{taxa_aprovacao:.1f}%", "Qualidade dos Leads", cor_destaque=cor_taxa), unsafe_allow_html=True)

    st.markdown("---")

    # 6. Exibe os Gráficos (Lado a Lado)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📈 Evolução dos Atendimentos")
        # Chama o gráfico de linha do charts.py
        fig_time = charts.grafico_timeline_simulacoes(df)
        st.plotly_chart(fig_time, use_container_width=True)

    with c2:
        st.subheader("🎯 Perfil da Carteira")
        # Chama o gráfico de pizza do charts.py
        fig_status = charts.grafico_pizza_status(df)
        st.plotly_chart(fig_status, use_container_width=True)