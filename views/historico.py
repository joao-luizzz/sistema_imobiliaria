import streamlit as st
from services import simulacao_service # <--- Mudou aqui
import time

def render():
    st.title("📂 Histórico de Simulações")
    st.caption("Gerencie e consulte propostas salvas anteriormente.")
    
    st.divider()

    # Pega usuário e carrega via Service
    usuario = st.session_state.get('username_logado', 'admin')
    df = simulacao_service.carregar_historico(usuario) # <--- Mudou aqui

    if df.empty:
        st.info("📭 Nenhuma simulação encontrada no histórico.")
        return

    # --- TABELA ---
    with st.container(border=True):
        st.markdown(f"### 📋 Registros Encontrados ({len(df)})")
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "data_criacao": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY HH:mm"),
                "valor_imovel": st.column_config.NumberColumn("Valor Imóvel", format="R$ %.2f"),
                "parcela": st.column_config.NumberColumn("Parcela Inicial", format="R$ %.2f"),
            }
        )

    st.write("") 

    # --- EXCLUSÃO ---
    with st.expander("🗑️ Gestão de Registros (Excluir)"):
        st.markdown("""
        <div style="background-color: #fef2f2; padding: 15px; border-radius: 8px; border: 1px solid #ef4444; margin-bottom: 15px;">
            <strong style="color: #b91c1c;">⚠️ Zona de Perigo:</strong> A exclusão é permanente.
        </div>
        """, unsafe_allow_html=True)
        
        c_input, c_btn = st.columns([3, 1])
        
        with c_input:
            id_para_excluir = st.number_input("ID da Simulação", min_value=0, step=1, format="%d")
        
        with c_btn:
            st.write("")
            st.write("")
            if st.button("Excluir Agora", type="primary", use_container_width=True):
                if id_para_excluir > 0:
                    id_safe = int(id_para_excluir)
                    # Chama o Service para excluir
                    if simulacao_service.excluir_simulacao(id_safe): # <--- Mudou aqui
                        st.success(f"✅ ID {id_safe} apagado!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erro ao apagar. ID não encontrado.")
                else:
                    st.warning("Digite um ID válido.")