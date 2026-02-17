import streamlit as st
import time
from services import auth_service

def render():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        with st.container(border=True):
            st.markdown("### 🔐 Acesso ao Sistema")
            st.caption("Digite suas credenciais para continuar.")
            
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            
            st.markdown("---")
            
            if st.button("Entrar", type="primary", use_container_width=True):
                if auth_service.verificar_login(usuario, senha):
                    st.session_state['logado'] = True
                    st.session_state['username_logado'] = usuario
                    st.success("Login realizado com sucesso!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")