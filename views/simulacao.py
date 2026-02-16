import streamlit as st
import urllib.parse
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
        taxa = st.number_input("Juros (% a.m.)", 0.0, 2.0, 0.5) / 100
        taxa_adm = st.number_input("Taxas/Seguros (R$)", 0.0, 500.0, 25.0)

    # --- LÓGICA DE CÁLCULO DUPLO ---
    with st.spinner("Comparando cenários..."):
        saldo_devedor, _ = calculos.calcular_saldo_devedor(valor_imovel, entrada, 0, 0, 0)
        
        # Calculamos os dois sistemas para comparar
        df_sac = calculos.projetar_amortizacao(saldo_devedor, meses, taxa, "SAC", taxa_adm)
        df_price = calculos.projetar_amortizacao(saldo_devedor, meses, taxa, "PRICE", taxa_adm)
    
    if not df_sac.empty and not df_price.empty:
        st.title("⚖️ Comparativo SAC vs PRICE")
        
        # Cálculos de Totais
        total_sac = df_sac['Parcela'].sum()
        total_price = df_price['Parcela'].sum()
        economia = total_price - total_sac
        
        # --- CARDS DE IMPACTO ---
        c1, c2, c3 = st.columns(3)
        c1.markdown(ui.card_html("Economia Total (SAC)", f"R$ {economia:,.2f}", "Menos juros acumulados", cor_destaque="#10b981"), unsafe_allow_html=True)
        
        p1_sac = df_sac.iloc[0]['Parcela']
        p1_price = df_price.iloc[0]['Parcela']
        diff_inicial = p1_sac - p1_price
        c2.markdown(ui.card_html("Diferença Inicial", f"R$ {diff_inicial:,.2f}", "SAC começa mais alta"), unsafe_allow_html=True)
        
        c3.markdown(ui.card_html("Custo Total (PRICE)", f"R$ {total_price:,.2f}", "Total pago ao final"), unsafe_allow_html=True)

        st.markdown("---")

        # --- GRÁFICOS LADO A LADO ---
        col_sac, col_price = st.columns(2)
        with col_sac:
            st.subheader("📊 Sistema SAC")
            st.caption("Parcelas decrescentes")
            st.plotly_chart(charts.grafico_evolucao_parcelas(df_sac), use_container_width=True, key="c_sac")
            
        with col_price:
            st.subheader("📈 Sistema PRICE")
            st.caption("Parcelas fixas")
            st.plotly_chart(charts.grafico_evolucao_parcelas(df_price), use_container_width=True, key="c_price")

        # --- SELEÇÃO PARA AÇÃO ---
        st.markdown("### 🎯 Qual plano o cliente prefere?")
        escolha = st.radio("Selecione o sistema para análise final:", ["SAC", "PRICE"], horizontal=True)
        
        # Definimos as variáveis finais baseadas na escolha
        if escolha == "SAC":
            df_final = df_sac
            total_final = total_sac
        else:
            df_final = df_price
            total_final = total_price
            
        p1_final = df_final.iloc[0]['Parcela']
        
        # Analisa o crédito com base na parcela ESCOLHIDA
        cor_st, texto_status, msg_st, comp = calculos.analisar_credito(p1_final, renda)

        # --- 🚨 AQUI ESTÁ A VOLTA DOS AVISOS! ---
        st.markdown("#### 🚦 Análise de Crédito")
        k_status, k_comp = st.columns(2)
        
        # Card de Status (Aprovado/Reprovado)
        k_status.markdown(ui.card_html("Status da Ficha", texto_status, cor_destaque=cor_st), unsafe_allow_html=True)
        
        # Card de Comprometimento de Renda
        cor_comp = "#ef4444" if comp > 30 else "#10b981" # Vermelho se passar de 30%
        k_comp.markdown(ui.card_html("Comprometimento", f"{comp:.1f}%", "Ideal: até 30%", cor_destaque=cor_comp), unsafe_allow_html=True)
        
        # Mensagem Detalhada (Onde aparece o "Risco", "Reprovado por renda", etc)
        if "REPROVADO" in texto_status:
            st.error(f"⚠️ **Motivo:** {msg_st}")
        elif "ATENÇÃO" in texto_status:
            st.warning(f"⚠️ **Alerta:** {msg_st}")
        else:
            st.success(f"✅ **Parecer:** {msg_st}")

            # --- 🚀 NOVO: SIMULADOR DE ANTECIPAÇÃO ---
        st.markdown("---")
        with st.expander("🚀 Acelerar Pagamento (Simular Amortização Extra)", expanded=False):
            st.caption("Mostre ao cliente como quitar o imóvel anos antes do prazo.")
            
            c_input1, c_input2 = st.columns(2)
            valor_extra = c_input1.number_input("Valor Extra (R$)", 0.0, step=100.0, value=500.0)
            freq_extra = c_input2.selectbox("Frequência", ["Mensal", "Anual", "Única (Agora)"])
            
            if valor_extra > 0:
                # Recupera dados do cenário escolhido (SAC ou PRICE)
                prazo_original = meses
                # Juros totais originais (aproximado: Total pago - Saldo Devedor)
                juros_originais = total_final - saldo_devedor 
                
                # Calcula o novo cenário
                novo_prazo, juros_novos = calculos.calcular_antecipacao(
                    saldo_devedor, taxa, escolha, p1_final, valor_extra, freq_extra
                )
                
                # Resultados
                economia_juros = juros_originais - juros_novos
                anos_a_menos = (prazo_original - novo_prazo) / 12
                
                # Exibe visualmente
                k1, k2, k3 = st.columns(3)
                k1.metric("Novo Prazo", f"{novo_prazo} meses", f"- {prazo_original - novo_prazo} meses", delta_color="normal")
                k2.metric("Tempo Economizado", f"{anos_a_menos:.1f} Anos", "de vida ganhos!")
                k3.metric("Juros Economizados", f"R$ {economia_juros:,.2f}", "Dinheiro no bolso")
                
                if novo_prazo < prazo_original:
                    st.success(f"💡 Dica de Venda: Se o cliente pagar **R$ {valor_extra}** {freq_extra.lower()}, ele quita o imóvel **{int(anos_a_menos)} anos antes**!")

     # --- BOTÕES DE AÇÃO (Corrigido para width="stretch") ---
        st.markdown("---")
        b_pdf, b_excel, b_zap, b_save = st.columns(4)
        
        # 1. Botão PDF
        with b_pdf:
            dados_pdf = {
                "cliente": cliente,
                "valor_imovel": valor_imovel,
                "entrada": entrada,
                "saldo_devedor": saldo_devedor,
                "meses": meses,
                "parcela": p1_final,
                "status_texto": f"{texto_status} - {msg_st} (Plano {escolha})"
            }
            arquivo_pdf = relatorios.gerar_proposta_pdf(dados_pdf)
            with open(arquivo_pdf, "rb") as f:
                st.download_button(
                    "📄 PDF", 
                    f, 
                    file_name=arquivo_pdf, 
                    mime="application/pdf", 
                    width="stretch"  # <--- MUDOU AQUI
                )

        # 2. Botão Excel
        with b_excel:
            excel_data = relatorios.gerar_excel_comparativo(
                df_sac, df_price, 
                {"cliente": cliente, "valor_imovel": valor_imovel, "entrada": entrada, "meses": meses}
            )
            st.download_button(
                label="📊 Excel",
                data=excel_data,
                file_name=f"Simulacao_{cliente}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"  # <--- MUDOU AQUI
            )

        # 3. Botão WhatsApp
        with b_zap:
            msg = f"*Proposta {cliente}*\n\n💰 Imóvel: R$ {valor_imovel:,.2f}\n📅 Prazo: {meses} meses\n✅ Plano: {escolha}\n💵 1ª Parcela: R$ {p1_final:,.2f}\n💳 Total: R$ {total_final:,.2f}"
            link = f"https://wa.me/?text={urllib.parse.quote(msg)}"
            st.link_button(
                "📱 Zap", 
                link, 
                width="stretch"  # <--- MUDOU AQUI
            )

        # 4. Botão Salvar
        with b_save:
            if st.button("💾 Salvar", type="primary", width="stretch"): # <--- MUDOU AQUI
                autor = st.session_state.get('username_logado', 'admin')
                if database.salvar_simulacao(cliente, valor_imovel, entrada, p1_final, texto_status, autor):
                    st.toast("Simulação salva!", icon="✅")
                    st.cache_data.clear()