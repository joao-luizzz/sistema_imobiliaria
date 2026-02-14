import streamlit as st
from core import calculos, database, relatorios


def render():
    st.header("👥 Gestão de Acessos")
    st.caption("Controle quem pode acessar o sistema e os leads")

    col_add, col_list = st.columns([1, 1])

    with col_add:
        st.subheader("🆕 Novo Corretor")
        with st.form("cadastro_usuario_form"):
            new_user = st.text_input("Username (Login)").lower().strip()
            new_nome = st.text_input("Nome do Corretor")
            new_pw = st.text_input("Senha Inicial", type="password")
            
            submit = st.form_submit_button("Cadastrar Corretor", width="stretch")
            
            if submit:
                if new_user and new_pw and new_nome:
                    if database.criar_usuario(new_user, new_pw, new_nome):
                        st.success(f"Corretor {new_nome} cadastrado!")
                        st.rerun()
                else:
                    st.error("Preencha todos os campos corretamente.")

    with col_list:
        st.subheader("📋 Utilizadores Ativos")
        usuarios = database.listar_usuarios()
        
        for u in usuarios:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{u[1]}**\n\n`@{u[0]}`")
                
                # Impede o admin de se auto-excluir por acidente
                if u[0] != 'admin':
                    if c2.button("❌", key=f"del_{u[0]}"):
                        database.excluir_usuario(u[0])
                        st.rerun()
                else:
                    c2.disabled = True