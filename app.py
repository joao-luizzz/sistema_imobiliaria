import streamlit as st
import os # <--- Importante para verificar se o arquivo existe
from views import login, dashboard, simulacao, oraculo, historico
from core import database
from services import auth_service

# Configuração da Página
st.set_page_config(
    page_title="Sistema Imobiliário",
    page_icon="🏡",
    layout="wide"
)

# Inicializa o Banco de Dados
database.inicializar_banco()

# CSS Personalizado
st.markdown("""
    <style>
        .stButton>button { height: 3em; }
    </style>
""", unsafe_allow_html=True)

# Lógica de Sessão
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

# Tela de Login ou Sistema
if not st.session_state['logado']:
    login.render()

else:
    # --- SIDEBAR (MENU LATERAL) ---
    with st.sidebar:
        # CORREÇÃO AQUI: Verifica se a imagem existe antes de tentar mostrar
        if os.path.exists("assets/img/logo.png"):
            st.image("assets/img/logo.png", width=150)
        else:
            st.markdown("## 🏠 Imobiliária") # Mostra texto se não tiver logo
            
        st.markdown(f"👤 Olá, **{st.session_state['username_logado']}**")
        
        menu = st.radio(
            "Navegação", 
            ["Simulação", "Oráculo", "Dashboard", "Histórico"]
        )
        
        st.markdown("---")
        if st.button("Sair (Logout)"):
            auth_service.realizar_logout()

    # --- ROTEAMENTO DE PÁGINAS ---
    if menu == "Simulação":
        simulacao.render()
    elif menu == "Oráculo":
        oraculo.render()
    elif menu == "Dashboard":
        dashboard.render()
    elif menu == "Histórico":
        historico.render()