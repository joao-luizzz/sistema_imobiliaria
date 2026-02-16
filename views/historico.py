import streamlit as st
import pandas as pd
from core import database
from components import ui
import io

def render():
    st.title("📂 Histórico de Simulações")
    
    # 1. Identifica Utilizador e Carrega Dados
    usuario = st.session_state.get('username_logado', 'admin')
    
    # Adicionamos um botão de atualização manual
    if st.button("🔄 Atualizar Lista", type="secondary"):
        st.cache_data.clear()
        
    df = database.carregar_historico(usuario)

    if df.empty:
        st.info("Nenhuma simulação registada ainda.")
        return

    # 2. Barra de Ferramentas (Filtros e Ações)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # 🔍 Filtro de Busca
        termo_busca = st.text_input("🔍 Buscar Cliente", placeholder="Digite o nome...").lower()
    
    with c2:
        # 📥 Botão de Exportar Tudo (Excel)
        st.write("") # Espaçamento para alinhar
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Historico Completo")
            
        st.download_button(
            label="📥 Baixar Tudo (.xlsx)",
            data=buffer,
            file_name="historico_geral.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True # width="stretch" se tiver atualizado a library
        )

    # 3. Aplica o Filtro
    if termo_busca:
        df = df[df['cliente'].str.lower().str.contains(termo_busca)]

    # 4. Formatação da Tabela
    st.markdown("---")
    
    # Vamos criar uma coluna 'Excluir' checkbox para permitir seleção em massa (visual)
    # Mas para simplificar e ser robusto, vamos fazer exclusão por ID na sidebar ou botão
    
    # Exibição Profissional
    st.dataframe(
        df,
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "data_criacao": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY HH:mm"),
            "valor_imovel": st.column_config.NumberColumn("Valor Imóvel", format="R$ %.2f"),
            "parcela": st.column_config.NumberColumn("1ª Parcela", format="R$ %.2f"),
            "status": st.column_config.TextColumn("Parecer"),
        },
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # 5. Área de Gestão (Excluir)
    with st.expander("🗑️ Gestão de Registos (Excluir)"):
        st.warning("Cuidado: A exclusão é permanente.")
        
        c_del1, c_del2 = st.columns([3, 1])
        
        # IMPORTANTE: Adicionei step=1 e format="%d" para garantir que visualmente seja inteiro
        id_para_excluir = c_del1.number_input(
            "ID da Simulação para excluir", 
            min_value=0, 
            step=1,             # <--- FORÇA PULAR DE 1 EM 1
            format="%d"         # <--- FORÇA VISUAL INTEIRO
        )
        
        if c_del2.button("Excluir Definitivamente", type="primary", use_container_width=True):
            if id_para_excluir > 0:
                sucesso = database.excluir_simulacao(id_para_excluir)
                
                if sucesso:
                    st.success("✅ Apagado com sucesso!")
                    
                    # --- FAXINA COMPLETA ---
                    st.cache_data.clear() # Limpa o cache de dados
                    
                    import time
                    time.sleep(1) # Espera 1 segundinho pro banco respirar
                    st.rerun()    # Recarrega a página do zero
                else:
                    st.error("❌ Não foi possível apagar via App. Verifique o console.")