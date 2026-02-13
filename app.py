import streamlit as st
import pandas as pd
import calculos
import database
import relatorios
import urllib.parse
import os
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema Premium", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

# --- 2. ESTILO ---
def setup_style():
    if os.path.exists("assets/style.css"):
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        /* Tipografia */
        h1 { font-weight: 700; letter-spacing: -1px; font-size: 2rem; color: #f8fafc; }
        h2, h3 { font-weight: 600; color: #e2e8f0; }
        [data-testid="stSidebar"] h1 { font-size: 0.7rem; text-transform: uppercase; color: #64748b; letter-spacing: 1.5px; margin-top: 20px; }
        
        /* Tabela HTML */
        .table-container { max-height: 400px; overflow-y: auto; border: 1px solid #334155; border-radius: 8px; margin-top: 10px; }
        .minimal-table { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #cbd5e1; background: transparent; }
        .minimal-table th { text-align: left; padding: 12px 16px; border-bottom: 2px solid #334155; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; position: sticky; top: 0; background-color: #0f172a; z-index: 10; }
        .minimal-table td { padding: 10px 16px; border-bottom: 1px solid #1e293b; }
        .minimal-table tr:hover { background-color: rgba(59, 130, 246, 0.05); }

        /* Card do Oráculo (Modo Reverso) */
        .oracle-card {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border: 1px solid #3b82f6;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES VISUAIS ---
def renderizar_tabela_html(df):
    df_fmt = df.copy()
    for col in ['Parcela', 'Amortização', 'Juros', 'Seguros/Taxas', 'Saldo Devedor']:
        if col in df_fmt.columns: df_fmt[col] = df_fmt[col].apply(lambda x: f"R$ {x:,.2f}")
    return f'<div class="table-container">{df_fmt.to_html(classes="minimal-table", index=False, border=0)}</div>'

def grafico_high_end(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Mês'], y=df['Parcela'], mode='lines', name='Parcela',
        line=dict(color='#3b82f6', width=3), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)',
        hovertemplate='<b>Mês %{x}</b><br>Total: %{y:,.2f}<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=350,
        hovermode="x unified", xaxis=dict(showgrid=False, color='#64748b'), yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#64748b', tickprefix="R$ ")
    )
    return fig

# --- 4. APP PRINCIPAL ---
def main():
    setup_style()
    database.init_db()

    with st.sidebar:
        # SELETOR DE MODO (O Cérebro do App)
        modo = st.radio("Modo de Operação", ["🏠 Simular Financiamento", "🔮 Poder de Compra (Oráculo)"])
        st.markdown("---")

        st.markdown("## ⚙️ PARÂMETROS")
        st.caption("CLIENTE"); cliente = st.text_input("Nome", "Cliente Vip", label_visibility="collapsed")
        
        # Inputs que mudam conforme o modo
        valor_imovel = 0.0
        entrada = 0.0
        chaves = 0.0
        parcela_alvo = 0.0
        renda = 0.0

        if modo == "🏠 Simular Financiamento":
            renda = st.number_input("Renda Mensal (R$)", 1000.0, step=500.0, value=8500.0)
            st.caption("IMÓVEL"); valor_imovel = st.number_input("Valor Venda", 50000.0, value=350000.0, step=1000.0)
            st.caption("ENTRADA"); entrada = st.number_input("Entrada", 0.0, value=50000.0, step=1000.0)
            st.caption("CHAVES"); chaves = st.number_input("Chaves", 0.0, value=30000.0, step=1000.0)
        else:
            st.info("Descubra qual imóvel cabe no bolso do cliente.")
            st.caption("PARCELA MÁXIMA"); parcela_alvo = st.number_input("Teto da Parcela (R$)", 500.0, value=2500.0, step=100.0)
            st.caption("DINHEIRO DISPONÍVEL"); entrada = st.number_input("Entrada Disponível", 0.0, value=40000.0, step=1000.0)
            chaves = st.number_input("Chaves / FGTS", 0.0, value=10000.0, step=1000.0)

        st.caption("CONDIÇÕES"); meses = st.slider("Prazo (Meses)", 12, 120, 100)
        
        # Intercaladas (Só no modo normal)
        qtd_intercaladas = 0; valor_intercalada = 0.0
        if modo == "🏠 Simular Financiamento":
            c1, c2 = st.columns(2)
            with c1: qtd_intercaladas = st.number_input("Qtd Anuais", 0, 10, 8)
            with c2: valor_intercalada = st.number_input("Vlr Anual", 0.0, value=5000.0, step=500.0)

        st.markdown("<h1>TAXAS & SEGUROS</h1>", unsafe_allow_html=True)
        taxa_correcao = st.number_input("Juros (% a.m.)", 0.0, 2.0, 0.5) / 100
        # NOVO: Taxa Administrativa
        tarifa_adm = st.number_input("Taxa Adm. / Seguro (R$)", 0.0, 500.0, 25.0, step=5.0)
        sistema = st.selectbox("Sistema", ["SAC", "PRICE"])

    # --- LÓGICA 1: SIMULAÇÃO PADRÃO ---
    if modo == "🏠 Simular Financiamento":
        saldo_devedor, total_intercaladas = calculos.calcular_saldo_devedor(valor_imovel, entrada, chaves, qtd_intercaladas, valor_intercalada)
        
        # Calcula com a nova tarifa
        df_evolucao = calculos.projetar_amortizacao(saldo_devedor, meses, taxa_correcao, sistema, tarifa_adm)
        parcela_inicial = df_evolucao.iloc[0]['Parcela'] if not df_evolucao.empty else 0.0
        cor_status, texto_status, msg_status, percentual_comp = calculos.analisar_credito(parcela_inicial, renda)

        dados_export = {'cliente': cliente, 'valor_imovel': valor_imovel, 'entrada': entrada, 'chaves': chaves, 'total_intercaladas': total_intercaladas, 'saldo_devedor': saldo_devedor, 'meses': meses, 'parcela': parcela_inicial, 'status_texto': texto_status}

        # Interface Padrão
        c_h1, c_h2 = st.columns([4, 1])
        with c_h1: st.title("Simulador Financeiro"); st.caption(f"Proposta Comercial • {cliente}")
        if saldo_devedor < 0: st.error("🚨 Entrada maior que o valor!"); return
        st.markdown("---")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("1ª Parcela (c/ Taxa)", f"R$ {parcela_inicial:,.2f}", delta="Mensal")
        k2.metric("Saldo Financiado", f"R$ {saldo_devedor:,.2f}")
        k3.metric("Renda Comprometida", f"{percentual_comp:.1f}%", delta_color="inverse")
        k4.metric("Total Anuais", f"R$ {total_intercaladas:,.2f}")

        st.markdown(f"""<div style="background-color: {cor_status}15; border: 1px solid {cor_status}40; color: {cor_status}; padding: 12px; border-radius: 8px; margin: 20px 0; display: flex; align-items: center; gap: 10px;"><div style="width: 8px; height: 8px; border-radius: 50%; background-color: {cor_status}; box-shadow: 0 0 8px {cor_status};"></div>{texto_status}: {msg_status}</div>""", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 Fluxo", "📑 Proposta", "📂 Histórico"])
        with tab1:
            st.plotly_chart(grafico_high_end(df_evolucao), use_container_width=True, config={'displayModeBar': False})
            st.markdown(renderizar_tabela_html(df_evolucao), unsafe_allow_html=True)
        with tab2:
            msg_zap = f"Olá *{cliente}*! 👋\nProposta: R$ {valor_imovel:,.2f}\nEntrada: R$ {entrada:,.2f}\n{meses}x R$ {parcela_inicial:,.2f}\n_Vamos visitar?_"
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

    # --- LÓGICA 2: MODO ORÁCULO (REVERSO) ---
    else:
        st.title("🔮 Oráculo de Crédito")
        st.caption("Cálculo Reverso: Do bolso do cliente para o imóvel ideal.")
        st.markdown("---")

        # Chama a função nova
        teto_financiamento = calculos.calcular_poder_compra(parcela_alvo, meses, taxa_correcao, sistema, tarifa_adm)
        poder_compra_total = teto_financiamento + entrada + chaves
        
        col_oracle1, col_oracle2 = st.columns([1, 1])
        
        with col_oracle1:
            st.markdown(f"""
            <div class="oracle-card">
                <h3 style="color: #94a3b8; font-size: 0.8rem; letter-spacing: 1px; margin-bottom: 10px;">POTENCIAL DE COMPRA</h3>
                <h1 style="color: #3b82f6; font-size: 3.5rem; margin: 0; text-shadow: 0 0 20px rgba(59,130,246,0.3);">R$ {poder_compra_total:,.2f}</h1>
                <p style="color: #64748b; font-size: 0.9rem; margin-top: 15px;">Considerando {sistema} em {meses} meses</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_oracle2:
            st.subheader("📝 Detalhamento")
            st.write(f"Para pagar uma parcela de **R$ {parcela_alvo:,.2f}**:")
            
            # Barras de Progresso visuais para explicar a composição
            # Adicionei +0.1 para evitar divisão por zero se tudo for zero
            st.caption(f"Entrada em Dinheiro: R$ {entrada:,.2f}")
            st.progress(min(entrada / (poder_compra_total+0.1), 1.0))
            
            st.caption(f"Financiamento Bancário: R$ {teto_financiamento:,.2f}")
            st.progress(min(teto_financiamento / (poder_compra_total+0.1), 1.0))
            
            st.info(f"💡 Nota: Já descontamos a taxa mensal de R$ {tarifa_adm:.2f} do cálculo.")

    # Rodapé e Histórico Global
    if modo == "🏠 Simular Financiamento":
        with tab3: st.dataframe(database.carregar_historico(), use_container_width=True)

    st.markdown("""<div style="font-size: 0.7rem; color: #64748b; text-align: center; margin-top: 60px; border-top: 1px solid #1e293b; padding-top: 20px;">Sistema v3.0 (Oracle) • Praia Grande/SP</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()