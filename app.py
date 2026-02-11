import streamlit as st
import pandas as pd
import calculos
import database
import relatorios
import urllib.parse
import os
import plotly.graph_objects as go # <--- A ARMA SECRETA PARA GRÁFICOS BONITOS

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema Premium", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

# --- 2. ESTILO ---
def setup_style():
    if os.path.exists("assets/style.css"):
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        /* Ajustes de Tipografia */
        h1 { font-weight: 700; letter-spacing: -1px; font-size: 2rem; color: #f8fafc; }
        h2, h3 { font-weight: 600; color: #e2e8f0; }
        
        /* Sidebar Clean */
        [data-testid="stSidebar"] h1 { font-size: 0.7rem; text-transform: uppercase; color: #64748b; letter-spacing: 1.5px; margin-top: 20px; }
        
        /* Container Tabela */
        .table-container { max-height: 400px; overflow-y: auto; border: 1px solid #334155; border-radius: 8px; margin-top: 10px; }
        
        /* Tabela HTML Custom */
        .minimal-table { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #cbd5e1; background: transparent; }
        .minimal-table th { text-align: left; padding: 12px 16px; border-bottom: 2px solid #334155; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; position: sticky; top: 0; background-color: #0f172a; z-index: 10; }
        .minimal-table td { padding: 10px 16px; border-bottom: 1px solid #1e293b; }
        .minimal-table tr:hover { background-color: rgba(59, 130, 246, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. COMPONENTES VISUAIS PREMIUM ---

def renderizar_tabela_html(df):
    """Gera tabela HTML sem bordas verticais"""
    df_fmt = df.copy()
    for col in ['Parcela', 'Amortização', 'Juros', 'Saldo Devedor']:
        if col in df_fmt.columns: df_fmt[col] = df_fmt[col].apply(lambda x: f"R$ {x:,.2f}")
    return f'<div class="table-container">{df_fmt.to_html(classes="minimal-table", index=False, border=0)}</div>'

def grafico_high_end(df):
    """Gera um gráfico Plotly estilo Fintech com degradê"""
    fig = go.Figure()
    
    # Adiciona a linha com preenchimento degradê
    fig.add_trace(go.Scatter(
        x=df['Mês'], 
        y=df['Parcela'],
        mode='lines',
        name='Parcela',
        line=dict(color='#3b82f6', width=3), # Linha Azul Neon
        fill='tozeroy', # Preenche até o eixo zero
        fillcolor='rgba(59, 130, 246, 0.1)', # 10% Opacidade (Muito sutil e elegante)
        hovertemplate='<b>Mês %{x}</b><br>Parcela: R$ %{y:,.2f}<extra></extra>' # Tooltip limpo
    ))

    # Layout Minimalista (Remove fundo branco e grades feias)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Transparente
        margin=dict(l=0, r=0, t=10, b=0), # Sem margens inúteis
        height=350,
        hovermode="x unified", # Linha vertical ao passar o mouse
        xaxis=dict(
            showgrid=False, 
            color='#64748b', 
            showline=True, linecolor='#334155'
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#1e293b', # Grade horizontal muito sutil
            color='#64748b', 
            tickprefix="R$ ", 
            zeroline=False
        ),
        dragmode=False # Desativa zoom chato
    )
    return fig

# --- 4. APP PRINCIPAL ---
def main():
    setup_style()
    database.init_db()

    with st.sidebar:
        st.markdown("## ⚙️ CONTROLES")
        st.caption("CLIENTE"); cliente = st.text_input("Nome", "Cliente Vip", label_visibility="collapsed"); renda = st.number_input("Renda", 1000.0, step=500.0, value=8500.0)
        st.caption("IMÓVEL"); valor_imovel = st.number_input("Valor", 50000.0, value=350000.0, step=1000.0); entrada = st.number_input("Entrada", 0.0, value=50000.0, step=1000.0); chaves = st.number_input("Chaves", 0.0, value=30000.0, step=1000.0)
        st.caption("CONDIÇÕES"); meses = st.slider("Prazo", 12, 120, 100); c1, c2 = st.columns(2); 
        with c1: qtd_intercaladas = st.number_input("Qtd Anuais", 0, 10, 8)
        with c2: valor_intercalada = st.number_input("Vlr Anual", 0.0, value=5000.0, step=500.0)
        taxa_correcao = st.number_input("Juros (% a.m.)", 0.0, 2.0, 0.5) / 100; sistema = st.selectbox("Sistema", ["SAC", "PRICE"])

    saldo_devedor, total_intercaladas = calculos.calcular_saldo_devedor(valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada)
    df_evolucao = calculos.projetar_amortizacao(saldo_devedor, meses, taxa_correcao, sistema)
    parcela_inicial = df_evolucao.iloc[0]['Parcela'] if not df_evolucao.empty else 0.0
    cor_status, texto_status, msg_status, percentual_comp = calculos.analisar_credito(parcela_inicial, renda)

    dados_export = {'cliente': cliente, 'valor_imovel': valor_imovel, 'entrada': entrada, 'chaves': chaves, 'total_intercaladas': total_intercaladas, 'saldo_devedor': saldo_devedor, 'meses': meses, 'parcela': parcela_inicial, 'status_texto': texto_status}

    # HEADER
    c_h1, c_h2 = st.columns([4, 1])
    with c_h1: st.title("Simulador Financeiro"); st.caption(f"Proposta Comercial • {cliente}")
    
    if saldo_devedor < 0: st.error("🚨 Entrada maior que o valor do imóvel!"); return
    st.markdown("---")

    # CARDS
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("1ª Parcela", f"R$ {parcela_inicial:,.2f}", delta="Mensal")
    k2.metric("Saldo Financiado", f"R$ {saldo_devedor:,.2f}")
    k3.metric("Renda Comprometida", f"{percentual_comp:.1f}%", delta_color="inverse")
    k4.metric("Total Anuais", f"R$ {total_intercaladas:,.2f}")

    st.markdown(f"""<div style="background-color: {cor_status}15; border: 1px solid {cor_status}40; color: {cor_status}; padding: 12px 20px; border-radius: 8px; margin: 24px 0; font-weight: 500; display: flex; align-items: center; gap: 12px;"><div style="width: 8px; height: 8px; border-radius: 50%; background-color: {cor_status}; box-shadow: 0 0 8px {cor_status};"></div>{texto_status}: {msg_status}</div>""", unsafe_allow_html=True)

    # ABAS
    tab_fluxo, tab_docs, tab_hist = st.tabs(["📊 Fluxo Financeiro", "📑 Proposta & Zap", "📂 Histórico"])

    with tab_fluxo:
        st.subheader("Projeção de Pagamentos")
        
        # --- AQUI ESTÁ O GRÁFICO NOVO (Substituindo o area_chart) ---
        figura = grafico_high_end(df_evolucao)
        st.plotly_chart(figura, use_container_width=True, config={'displayModeBar': False}) # Remove botoes de zoom chatos
        
        st.markdown("#### Tabela Detalhada")
        st.markdown(renderizar_tabela_html(df_evolucao), unsafe_allow_html=True)

    with tab_docs:
        st.subheader("Atendimento")
        msg_zap = f"Olá *{cliente}*! 👋\nProposta Imóvel:\n💰 Valor: R$ {valor_imovel:,.2f}\n📉 Entrada: R$ {entrada:,.2f}\n📅 Plano: {meses}x de R$ {parcela_inicial:,.2f} ({sistema})\n_Agendamos visita?_"
        link_zap = f"https://wa.me/?text={urllib.parse.quote(msg_zap)}"
        
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1: st.link_button("📲 WhatsApp", link_zap, type="primary", use_container_width=True)
        with c2: 
            if st.button("📄 PDF", use_container_width=True):
                pdf = relatorios.gerar_proposta_pdf(dados_export)
                with open(pdf, "rb") as f: st.download_button("⬇️ Baixar", f, file_name=pdf, mime="application/pdf", use_container_width=True)
        with c3:
            if st.button("💾 Salvar", use_container_width=True):
                database.salvar_simulacao(cliente, valor_imovel, entrada, parcela_inicial, texto_status); st.toast("Salvo!", icon="✅")

    with tab_hist: st.dataframe(database.carregar_historico(), use_container_width=True)

    st.markdown("""<div style="font-size: 0.7rem; color: #64748b; text-align: center; margin-top: 60px; border-top: 1px solid #1e293b; padding-top: 20px;">Sistema v2.5 (Fintech) • Praia Grande/SP</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()