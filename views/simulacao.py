import streamlit as st
import urllib.parse
from core import calculos, relatorios
from services import simulacao_service
from components import ui, charts

def render():
    # Cabeçalho limpo
    st.title("🏡 Simulador de Financiamento")
    st.caption("Preencha os dados à esquerda para gerar a proposta instantânea.")
    
    st.divider()

    # Layout: Coluna Esquerda (Inputs) | Coluna Direita (Resultados)
    left_col, right_col = st.columns([1, 1.8], gap="medium")

    # ==========================================
    # 👈 COLUNA DA ESQUERDA: INPUTS
    # ==========================================
    with left_col:
        with st.container(border=True):
            st.markdown("### 👤 Dados & Valores")
            
            cliente = st.text_input("Nome do Cliente", placeholder="Ex: João da Silva")
            
            st.divider()
            
            # --- VALOR DO IMÓVEL ---
            st.markdown("**🏡 Valor do Imóvel**")
            valor_imovel = st.number_input(
                "Valor do Imóvel", min_value=50000.0, value=400000.0, step=5000.0, 
                label_visibility="collapsed", format="%.2f"
            )
            st.markdown(f"<div style='color: #64748b; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;'>💰 {ui.formatar_moeda(valor_imovel)}</div>", unsafe_allow_html=True)

            # --- ENTRADA ---
            st.markdown("**💵 Valor da Entrada**")
            entrada_sugerida = valor_imovel * 0.20 
            entrada = st.number_input(
                "Entrada", min_value=0.0, max_value=valor_imovel, value=entrada_sugerida, step=1000.0,
                label_visibility="collapsed", format="%.2f"
            )
            
            # Feedback Visual da Entrada
            percentual = (entrada / valor_imovel) * 100 if valor_imovel > 0 else 0
            cor_entrada = "#10b981" if percentual >= 20 else "#f59e0b"
            st.markdown(f"<div style='color: {cor_entrada}; font-size: 0.9em; margin-top: -10px; margin-bottom: 5px;'>💳 {ui.formatar_moeda(entrada)} ({percentual:.1f}%)</div>", unsafe_allow_html=True)
            if percentual < 20:
                st.caption("⚠️ Entrada abaixo de 20% restringe bancos.")
            
            # --- 🆕 NOVIDADE: CUSTOS DE DOCUMENTAÇÃO (ITBI) ---
            with st.expander("📝 Custos de Documentação (Estimativa)"):
                st.caption("ITBI, Registro e Escritura costumam ser cerca de 4% a 5% do valor.")
                itbi_percentual = st.number_input("Taxa Documentação (%)", 0.0, 10.0, 4.0, 0.5)
                custo_doc = valor_imovel * (itbi_percentual / 100)
                
                total_necessario = entrada + custo_doc
                st.markdown(f"**Documentação:** {ui.formatar_moeda(custo_doc)}")
                st.markdown(f"<div style='background-color: #fff7ed; padding: 10px; border-radius: 5px; color: #c2410c; font-weight: bold;'>💰 Total na Mão: {ui.formatar_moeda(total_necessario)}</div>", unsafe_allow_html=True)

            st.divider()

            # --- CONDIÇÕES ---
            st.markdown("### ⚙️ Condições")
            taxa_anual = st.slider("Juros Anual (%)", 5.0, 15.0, 9.99, 0.1)
            meses = st.select_slider("Prazo (Anos)", options=[10, 15, 20, 25, 30, 35], value=30) * 12
            escolha = st.radio("Sistema", ["SAC (Decrescente)", "PRICE (Fixa)"], horizontal=True)

    # --- CÁLCULOS (Core) ---
    saldo_devedor = valor_imovel - entrada
    df_sac = calculos.calcular_sac(saldo_devedor, taxa_anual, meses)
    df_price = calculos.calcular_price(saldo_devedor, taxa_anual, meses)
    
    df_atual = df_sac if "SAC" in escolha else df_price
    tipo_tabela = "SAC" if "SAC" in escolha else "PRICE"

    p1 = df_atual.iloc[0]['Parcela']
    ult_p = df_atual.iloc[-1]['Parcela']
    total_pago = df_atual['Parcela'].sum()
    total_juros = df_atual['Juros'].sum()
    renda_minima = p1 / 0.30

    # ==========================================
    # 👉 COLUNA DA DIREITA: RESULTADOS
    # ==========================================
    with right_col:
        
        # 1. DESTAQUE PRINCIPAL
        with st.container(border=True):
            col_destaque_E, col_destaque_D = st.columns([2, 1])
            with col_destaque_E:
                st.caption("Primeira Parcela")
                st.markdown(f"<h1 style='margin: -10px 0 0 0; color: #10b981;'>{ui.formatar_moeda(p1)}</h1>", unsafe_allow_html=True)
                st.caption(f"Última: {ui.formatar_moeda(ult_p)}")
            
            with col_destaque_D:
                st.caption("Renda Mínima")
                st.markdown(f"<h3 style='margin: 0; color: #64748b;'>{ui.formatar_moeda(renda_minima)}</h3>", unsafe_allow_html=True)

        # 2. RESUMO (KPIs)
        c1, c2, c3 = st.columns(3)
        c1.markdown(ui.card_html("Total Pago", ui.formatar_moeda(total_pago), "Imóvel + Juros"), unsafe_allow_html=True)
        c2.markdown(ui.card_html("Só Juros", ui.formatar_moeda(total_juros), f"Custo {tipo_tabela}"), unsafe_allow_html=True)
        c3.markdown(ui.card_html("Financiado", ui.formatar_moeda(saldo_devedor), f"{percentual:.0f}% Entrada"), unsafe_allow_html=True)

        st.write("") 

        # 3. GRÁFICOS E TABELAS
        with st.container(border=True):
            tab_graf, tab_dados = st.tabs(["📊 Análise Visual", "📄 Tabela Detalhada"])
            
            with tab_graf:
                st.plotly_chart(charts.plot_amortizacao(df_atual), use_container_width=True)
                
            with tab_dados:
                st.dataframe(df_atual, height=250, use_container_width=True, hide_index=True)

        # 4. BOTÕES DE AÇÃO
        st.write("")
        with st.container(border=True):
            st.caption("📤 Ações e Exportação")
            b_pdf, b_excel, b_zap, b_save = st.columns(4)
            
            with b_pdf:
                dados_pdf = {
                    "cliente": cliente if cliente else "Visitante",
                    "valor_imovel": valor_imovel, "entrada": entrada,
                    "saldo_devedor": saldo_devedor, "meses": meses, "parcela": p1,
                    "status_texto": f"Renda Min: {ui.formatar_moeda(renda_minima)}"
                }
                arquivo_pdf = relatorios.gerar_proposta_pdf(dados_pdf)
                with open(arquivo_pdf, "rb") as f:
                    st.download_button("📄 PDF", f, file_name=arquivo_pdf, mime="application/pdf", width="stretch")

            with b_excel:
                excel_data = relatorios.gerar_excel_comparativo(df_sac, df_price, {"cliente": cliente, "valor_imovel": valor_imovel, "entrada": entrada, "meses": meses})
                st.download_button("📊 Excel", excel_data, file_name=f"Simulacao_{cliente}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

            with b_zap:
                msg = f"*Simulação {cliente}*\n🏠 Imóvel: {ui.formatar_moeda(valor_imovel)}\n💰 1ª Parcela: {ui.formatar_moeda(p1)}"
                st.link_button("📱 Zap", f"https://wa.me/?text={urllib.parse.quote(msg)}", width="stretch")

            with b_save:
                if st.button("💾 Salvar", type="primary", width="stretch"):
                    if not cliente: st.toast("Digite o nome!", icon="❌")
                    else:
                        autor = st.session_state.get('username_logado', 'admin')
                        # AQUI MUDOU: simulacao_service em vez de database
                        if simulacao_service.salvar_simulacao(cliente, valor_imovel, entrada, p1, "Simulação Web", autor):
                            st.toast("Salvo!", icon="✅")

    # ==========================================
    # 🚀 RODAPÉ: O PODER DA AMORTIZAÇÃO
    # ==========================================
    st.write("")
    with st.expander("🚀 Turbo: Simular Amortização Extra (O Choque de Realidade)", expanded=False):
        c_extra, c_resumo = st.columns([1, 2])
        with c_extra:
            amortizacao_extra = st.number_input("Valor Extra Mensal (R$)", 0.0, step=100.0, format="%.2f")
            if amortizacao_extra > 0: st.caption(f"Visual: **{ui.formatar_moeda(amortizacao_extra)}**")

        with c_resumo:
            if amortizacao_extra > 0:
                amortizacao_media = df_atual['Amortizacao'].mean()
                novo_prazo = int(saldo_devedor / (amortizacao_media + amortizacao_extra))
                meses_eco = meses - novo_prazo
                juros_eco = total_juros * (1 - (novo_prazo / meses))

                st.markdown(f"""
                <div style="background-color: #f0fdf4; padding: 15px; border-radius: 8px; border: 1px solid #10b981;">
                    <h4 style="color: #15803d; margin:0;">⏱️ Cai de {meses} para <b>{novo_prazo} meses</b>!</h4>
                    <p style="margin: 5px 0; color: #166534;">Você economiza <b>{meses_eco/12:.1f} anos</b> de pagamentos.</p>
                    <p style="margin: 0; font-weight: bold; color: #15803d;">💰 Economia de Juros: {ui.formatar_moeda(juros_eco)}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Digite um valor extra (ex: R$ 500) para ver quanto tempo você economiza.")