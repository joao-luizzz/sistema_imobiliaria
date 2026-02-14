import streamlit as st
import os
from core import calculos, database, relatorios

# Configuração de Página (DEVE ser o primeiro comando Streamlit)
st.set_page_config(page_title="Sistema Premium v3.5", page_icon="💎", layout="wide")

# Importações modulares (Organizadas por pastas)
from core import database, calculos
from components import ui
from views import simulacao, oraculo, historico, dashboard, gestao

# --- 1. INICIALIZAÇÃO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- 2. TELA DE LOGIN ---
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Utilizador").strip()
            pw = st.text_input("Senha", type="password").strip()
            botao = st.form_submit_button("Entrar", width="stretch")
            
            if botao:
                nome = database.login_usuario(user, pw)
                if nome:
                    st.session_state['autenticado'] = True
                    st.session_state['nome_usuario'] = nome
                    st.session_state['username_logado'] = user
                    st.rerun()
                else:
                    st.error("Utilizador ou senha incorretos")

# --- 3. LÓGICA PRINCIPAL ---
if not st.session_state['autenticado']:
    tela_login()
else:
    # Injeta CSS e Inicializa Banco
    ui.inject_custom_css()
    database.init_db()
    
    is_admin = (st.session_state.get('username_logado') == 'admin')

    # --- SIDEBAR GLOBAL ---
    with st.sidebar:
        st.title(f"Olá, {st.session_state['nome_usuario']} 👋")
        
        # O Modo de operação agora é uma variável global que passamos para as views
        modo = st.radio("Navegação Rápida", ["🏠 Simulação", "🔮 Oráculo"])
        st.markdown("---")
        
        if st.button("Sair", width="stretch"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- DEFINIÇÃO DAS ABAS ---
    titulos = ["🏠 Principal", "📂 Histórico", "📊 Analytics"]
    if is_admin:
        titulos.append("⚙️ Gestão")
    
    abas = st.tabs(titulos)

    # --- RENDERIZAÇÃO DAS VIEWS (Onde a mágica acontece) ---
    with abas[0]:
        if modo == "🏠 Simulação":
            simulacao.render()
        else:
            oraculo.render()

    with abas[1]:
        historico.render()

    with abas[2]:
        dashboard.render()

    if is_admin:
        with abas[3]:
            gestao.render()

    # Rodapé fixo
    st.markdown("""<div style="font-size: 0.7rem; color: #64748b; text-align: center; margin-top: 50px;">
    Sistema Imobiliário Profissional • v3.5 (Modular) • 2026</div>""", unsafe_allow_html=True)