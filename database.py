import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import json

# --- CONEXÃO COM A NUVEM ---
def get_engine():
    """
    Cria a conexão com o Supabase usando as credenciais do secrets.toml.
    Usa st.cache_resource para não ficar reconectando toda hora.
    """
    try:
        # Pega a URL segura do secrets
        db_url = st.secrets["connections"]["supabase"]["url"]
        
        # O Supabase precisa do driver 'postgresql+psycopg2'
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
            
        return create_engine(db_url)
    except Exception as e:
        st.error(f"Erro ao conectar no banco: {e}")
        return None

# --- INICIALIZAÇÃO DA TABELA ---
def init_db():
    """Cria a tabela no PostgreSQL se ela não existir."""
    engine = get_engine()
    if engine is None: return

    # Comando SQL para criar tabela no Postgres
    create_table_query = """
    CREATE TABLE IF NOT EXISTS simulacoes (
        id SERIAL PRIMARY KEY,
        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cliente VARCHAR(255),
        valor_imovel FLOAT,
        entrada FLOAT,
        parcela FLOAT,
        status VARCHAR(50),
        detalhes JSONB
    );
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()
    except Exception as e:
        st.error(f"Erro ao inicializar banco: {e}")

# --- SALVAR SIMULAÇÃO ---
# ... dentro de database.py ...

def salvar_simulacao(cliente, valor_imovel, entrada, parcela, status):
    engine = get_engine()
    if engine is None: return

    detalhes = json.dumps({
        "origem": "Simulador Web",
        "versao": "v3.0"
    })

    query = text("""
        INSERT INTO simulacoes (cliente, valor_imovel, entrada, parcela, status, detalhes)
        VALUES (:cliente, :valor, :entrada, :parcela, :status, :detalhes)
    """)
    
    try:
        with engine.connect() as conn:
            # AQUI ESTÁ A CORREÇÃO MÁGICA: float(...)
            conn.execute(query, {
                "cliente": cliente,
                "valor": float(valor_imovel),  # Converte np.float64 para float nativo
                "entrada": float(entrada),     # Garante que é float nativo
                "parcela": float(parcela),     # Garante que é float nativo
                "status": status,
                "detalhes": detalhes
            })
            conn.commit()
            return True # Retorna sucesso para o app saber
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# --- CARREGAR HISTÓRICO ---
def carregar_historico():
    engine = get_engine()
    if engine is None: return pd.DataFrame()

    query = "SELECT data_registro, cliente, valor_imovel, parcela, status FROM simulacoes ORDER BY data_registro DESC"
    
    try:
        # Pandas lê direto do SQL (Mágica!)
        df = pd.read_sql(query, engine)
        
        # Formatações visuais para a tabela
        if not df.empty:
            df['data_registro'] = pd.to_datetime(df['data_registro']).dt.strftime('%d/%m/%Y %H:%M')
            df.columns = ["Data", "Cliente", "Valor Imóvel", "Parcela", "Status"]
        return df
    except Exception as e:
        st.error(f"Erro ao ler histórico: {e}")
        return pd.DataFrame()