import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import json
import hashlib

# --- FUNÇÕES DE SEGURANÇA ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- CONEXÃO COM A NUVEM ---
def get_engine():
    try:
        db_url = st.secrets["connections"]["supabase"]["url"]
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
        return create_engine(db_url)
    except Exception as e:
        st.error(f"Erro de Conexão: Verifique o arquivo secrets.toml. Detalhe: {e}")
        return None

# --- INICIALIZAÇÃO DA TABELA ---
def init_db():
    engine = get_engine()
    if engine is None: return

    # CORREÇÃO: Padronizei para data_criacao e adicionei a coluna autor
    create_table_query = """
    CREATE TABLE IF NOT EXISTS simulacoes (
        id SERIAL PRIMARY KEY,
        data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        cliente VARCHAR(255),
        valor_imovel FLOAT,
        entrada FLOAT,
        parcela FLOAT,
        status VARCHAR(50),
        autor VARCHAR(255),
        detalhes JSONB
    );
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()
    except Exception as e:
        st.error(f"Erro ao inicializar banco: {e}")

# --- LOGIN ---
def login_usuario(username, password):
    engine = get_engine()
    if engine is None: return None
    
    user_clean = username.strip()
    pw_clean = password.strip()
    
    query = text("SELECT password_hash, nome FROM usuarios WHERE username = :user")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"user": user_clean}).fetchone()
            if result:
                db_password = result[0]
                nome = result[1]
                if check_hashes(pw_clean, db_password):
                    return nome
            return None
    except Exception as e:
        return None

# --- SALVAR SIMULAÇÃO ---
def salvar_simulacao(cliente, valor_imovel, entrada, parcela, status, autor):
    engine = get_engine()
    if engine is None: return False

    detalhes = json.dumps({"origem": "Simulador Web", "versao": "3.5"})
    
    # CORREÇÃO: A query agora bate com as colunas corretas
    query = text("""
        INSERT INTO simulacoes (cliente, valor_imovel, entrada, parcela, status, detalhes, autor, data_criacao)
        VALUES (:cliente, :valor, :entrada, :parcela, :status, :detalhes, :autor, NOW())
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "cliente": cliente,
                "valor": float(valor_imovel),
                "entrada": float(entrada),
                "parcela": float(parcela),
                "status": status,
                "detalhes": detalhes,
                "autor": autor
            })
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")
        return False

# --- CARREGAR HISTÓRICO ---
def carregar_historico(usuario_atual):
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    
    try:
        with engine.connect() as conn:
            # CORREÇÃO: Padronizado para data_criacao
            cols = "id, data_criacao, cliente, valor_imovel, parcela, status, autor"
            
            if usuario_atual == 'admin':
                query = text(f"SELECT {cols} FROM simulacoes ORDER BY data_criacao DESC")
                result = conn.execute(query)
            else:
                query = text(f"SELECT {cols} FROM simulacoes WHERE autor = :u ORDER BY data_criacao DESC")
                result = conn.execute(query, {"u": usuario_atual})
            
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        return pd.DataFrame()

# --- GESTÃO DE UTILIZADORES ---
def listar_usuarios():
    engine = get_engine()
    if engine is None: return []
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT username, nome FROM usuarios")).fetchall()
    except: return []

def criar_usuario(username, password, nome):
    engine = get_engine()
    if engine is None: return False
    pw_hash = make_hashes(password)
    try:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO usuarios (username, password_hash, nome) VALUES (:u, :p, :n)"), 
                         {"u": username, "p": pw_hash, "n": nome})
            conn.commit()
            return True
    except: return False

def excluir_usuario(username):
    engine = get_engine()
    if engine is None: return False
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM usuarios WHERE username = :u AND username != 'admin'"), {"u": username})
            conn.commit()
            return True
    except: return False

def buscar_dados_dashboard(usuario_atual):
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    
    try:
        with engine.connect() as conn:
            # Selecionamos apenas o necessário para os gráficos
            cols = "data_criacao, valor_imovel, status, autor"
            
            if usuario_atual == 'admin':
                query = text(f"SELECT {cols} FROM simulacoes")
                result = conn.execute(query)
            else:
                query = text(f"SELECT {cols} FROM simulacoes WHERE autor = :u")
                result = conn.execute(query, {"u": usuario_atual})
            
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            # Garante que a coluna de data seja datetime (para o gráfico de linha funcionar)
            if not df.empty and 'data_criacao' in df.columns:
                df['data_criacao'] = pd.to_datetime(df['data_criacao'])
                
            return df
    except Exception as e:
        st.error(f"Erro no dashboard: {e}")
        return pd.DataFrame()