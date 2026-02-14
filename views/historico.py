import streamlit as st
from core import database
import pandas as pd

def render():
    st.title("📂 Histórico de Atendimentos")
    st.caption("Visualize e gerencie as simulações realizadas no sistema.")
    st.markdown("---")
    
    # 1. Obtém o usuário logado
    autor_atual = st.session_state.get('username_logado', 'admin')
    
    # 2. Busca os dados (A lógica de quem vê o quê está no core/database.py)
    df_hist = database.carregar_historico(autor_atual)

    # 3. Verifica se o DataFrame está vazio
    if df_hist is None or df_hist.empty:
        st.info("Nenhuma simulação encontrada. Que tal realizar a primeira agora?")
        if st.button("🔄 Verificar novamente"):
            st.rerun()
    else:
        # 4. Layout da Tabela
        # Dica: O admin vê a coluna 'autor', o corretor talvez não precise
        colunas_visiveis = ["data_criacao", "cliente", "valor_imovel", "parcela", "status"]
        if autor_atual == 'admin':
            colunas_visiveis.append("autor")

        # Exibição profissional com st.dataframe
        st.dataframe(
            df_hist[colunas_visiveis], 
            use_container_width=True,
            hide_index=True,
            column_config={
                "data_criacao": st.column_config.DatetimeColumn(
                    "Data e Hora", 
                    format="DD/MM/YYYY HH:mm"
                ),
                "cliente": "Nome do Cliente",
                "valor_imovel": st.column_config.NumberColumn(
                    "Valor Imóvel", 
                    format="R$ %.2f"
                ),
                "parcela": st.column_config.NumberColumn(
                    "1ª Parcela", 
                    format="R$ %.2f"
                ),
                "status": st.column_config.TextColumn(
                    "Status de Crédito"
                ),
                "autor": "Responsável"
            }
        )
        
        # 5. Ações Extras
        st.markdown("---")
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.download_button(
                label="📥 Baixar Histórico (CSV)",
                data=df_hist.to_csv(index=False).encode('utf-8'),
                file_name=f'historico_{autor_atual}.csv',
                mime='text/csv',
                width="stretch"
            )
        
        with c2:
            if st.button("🔄 Atualizar Lista", width="stretch"):
                st.rerun()