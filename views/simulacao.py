import streamlit as st
import os
from core import calculos, database, relatorios
from components import ui, charts

def render():
    # --- PARÂMETROS NA SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🏠 Dados do Imóvel")
        cliente = st.text_input("Nome do Cliente", "Cliente Vip")
        renda = st.number_input("Renda Mensal (R$)", 1000.0, value=8500.0, step=500.0)
        valor_imovel = st.number_input("Valor do Imóvel", 50000.0, value=350000.0, step=10000.0)
        entrada = st.number_input("Entrada", 0.0, value=50000.0, step=5000.0)
        
        st.markdown("---")
        meses = st.slider("Prazo (Meses)", 12, 420, 100)
        sistema = st.selectbox("Sistema", ["SAC", "PRICE"])
        taxa = st.number_input("Juros (% a.m.)", 0.0, 2.0, 0.5) / 100
        taxa_adm = st.number_input("Taxas/Seguros (R$)", 0.0, 500.0, 25.0)

    # --- LÓGICA DE CÁLCULO ---
    # Chaves e intercaladas zeradas por padrão nesta view simplificada
    saldo_devedor, _ = calculos.calcular_saldo_devedor(valor_imovel, entrada, 0, 0, 0)
    df_evolucao = calculos.projetar_amortizacao(saldo_devedor, meses, taxa, sistema, taxa_adm)
    
    if not df_evolucao.empty:
        p1 = df_evolucao.iloc[0]['Parcela']
        cor_st, texto_status, msg_st, comp = calculos.analisar_credito(p1, renda)

        # --- TÍTULO E CARDS ---
        st.title("🏠 Simulador Financeiro")
        k1, k2, k3 = st.columns(3)
        k1.markdown(ui.card_html("1ª Parcela", f"R$ {p1:,.2f}"), unsafe_allow_html=True)
        k2.markdown(ui.card_html("Status", texto_status, cor_destaque=cor_st), unsafe_allow_html=True)
        k3.markdown(ui.card_html("Comprometimento", f"{comp:.1f}%"), unsafe_allow_html=True)

        # --- GRÁFICO E TABELA ---
        st.plotly_chart(charts.grafico_evolucao_parcelas(df_evolucao), use_container_width=True)
        st.markdown(ui.renderizar_tabela_html(df_evolucao), unsafe_allow_html=True)

        st.markdown("---")
        
        # --- BOTÕES DE AÇÃO ---
        col_pdf, col_save = st.columns([1, 1])
        
        # 1. Botão Gerar PDF
        with col_pdf:
            # Prepara os dados para o relatório
            dados_pdf = {
                "cliente": cliente,
                "valor_imovel": valor_imovel,
                "entrada": entrada,
                "saldo_devedor": saldo_devedor,
                "meses": meses,
                "parcela": p1,
                "status_texto": f"{texto_status} - {msg_st}"
            }
            
            # Gera o arquivo
            arquivo_pdf = relatorios.gerar_proposta_pdf(dados_pdf)
            
            # Lê o arquivo em binário para o botão de download
            with open(arquivo_pdf, "rb") as f:
                pdf_bytes = f.read()
            
            st.download_button(
                label="📄 Baixar Proposta (PDF)",
                data=pdf_bytes,
                file_name=arquivo_pdf,
                mime="application/pdf",
                width="stretch"
            )
            
            # Limpeza (opcional): remove o arquivo do servidor após ler
            # os.remove(arquivo_pdf) 

        # 2. Botão Salvar no Banco
        with col_save:
            if st.button("💾 Salvar no Histórico", width="stretch", type="primary"):
                autor_atual = st.session_state.get('username_logado', 'admin')
                sucesso = database.salvar_simulacao(
                    cliente, valor_imovel, entrada, p1, texto_status, autor_atual
                )
                if sucesso:
                    st.toast(f"✅ Simulação salva com sucesso!", icon="🚀")
                else:
                    st.error("Erro ao salvar.")