import streamlit as st

# --- LISTA DE USUÁRIOS E SENHAS ---
# Atenção: Python diferencia maiúsculas de minúsculas!
USUARIOS = {
    "admin": "1234",          # Usuário: admin | Senha: 1234
    "joao": "vendas2024",     # Usuário: joao  | Senha: vendas2024
    "maria": "imoveis"        # Usuário: maria | Senha: imoveis
}

def verificar_login(usuario, senha):
    """Verifica se usuário e senha batem com a lista."""
    
    # Debug: Mostra no terminal o que está chegando (ajuda a achar erro)
    print(f"Tentativa de Login -> Usuário: '{usuario}' | Senha: '{senha}'")
    
    # Verifica se o usuário existe
    if usuario in USUARIOS:
        # Verifica se a senha está correta
        if USUARIOS[usuario] == senha:
            return True
            
    return False

def realizar_logout():
    """Limpa a sessão e recarrega."""
    st.session_state['logado'] = False
    st.session_state['username_logado'] = None
    st.rerun()