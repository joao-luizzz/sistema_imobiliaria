import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import hashlib
from datetime import datetime

# --- 1. CONEXÃO E CONFIGURAÇÃO ---
def get_engine():
    """
    Cria a conexão com o Banco de Dados de forma robusta.
    Tenta ler de [database] url ou SUPABASE_URL.
    """
    db_url = None
    
    try:
        # Tenta pegar dos secrets (formato padrão Streamlit)
        if "database" in st.secrets and "url" in st.secrets["database"]:
            db_url = st.secrets["database"]["url"]
        # Tenta pegar direto (formato simples)
        elif "url" in st.secrets:
            db_url = st.secrets["url"]
        # Tenta pegar formato Supabase
        elif "SUPABASE_URL" in st.secrets:
            db_url = st.secrets["SUPABASE_URL"]
            
        if db_url is None:
            st.error("❌ Erro: URL do banco não encontrada no secrets.toml")
            return None

        # Corrige o driver para SQLAlchemy (postgres:// -> postgresql+psycopg2://)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
            
        return create_engine(db_url)
        
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def init_db():
    """Cria as tabelas necessárias se não existirem"""
    engine = get_engine()
    if engine is None: return
    
    # Tabela de Usuários
    create_users = """
    CREATE TABLE IF NOT EXISTS usuarios (
        username VARCHAR(50) PRIMARY KEY,
        password_hash VARCHAR(64) NOT NULL,
        nome VARCHAR(100) NOT NULL
    );
    """
    
    # Tabela de Simulações
    create_sims = """
    CREATE TABLE IF NOT EXISTS simulacoes (
        id SERIAL PRIMARY KEY,
        cliente VARCHAR(100),
        valor_imovel FLOAT,
        entrada FLOAT,
        parcela FLOAT,
        status VARCHAR(50),
        data_criacao TIMESTAMP DEFAULT NOW(),
        autor VARCHAR(50)
    );
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(create_users))
            conn.execute(text(create_sims))
            conn.commit()
    except Exception as e:
        print(f"Erro no init_db: {e}")

# --- 2. SEGURANÇA E LOGIN ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hash(password) == hashed_text

def criar_usuario(username, password, nome):
    engine = get_engine()
    if engine is None: return False
    try:
        with engine.connect() as conn:
            query = text("INSERT INTO usuarios (username, password_hash, nome) VALUES (:u, :p, :n)")
            conn.execute(query, {"u": username, "p": make_hash(password), "n": nome})
            conn.commit()
            st.cache_data.clear()
            return True
    except Exception as e:
        st.error(f"Erro ao criar usuário: {e}")
        return False

def listar_usuarios():
    """Lista usuários para a tela de Gestão"""
    engine = get_engine()
    if engine is None: return []
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT username, nome FROM usuarios"))
            return result.fetchall()
    except: return []

# Cache de Login
@st.cache_data(ttl=600, show_spinner=False)
def buscar_credenciais_cache():
    engine = get_engine()
    if engine is None: return {}
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT username, password_hash, nome FROM usuarios")).fetchall()
            return {row[0]: {'hash': row[1], 'nome': row[2]} for row in result}
    except: return {}

def login_usuario(username, password):
    cache = buscar_credenciais_cache()
    if username in cache:
        if check_hashes(password, cache[username]['hash']):
            return cache[username]['nome']
    return None

# --- 3. SIMULAÇÕES E DADOS ---
def salvar_simulacao(cliente, valor_imovel, entrada, parcela, status, autor):
    engine = get_engine()
    if engine is None: return False
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO simulacoes (cliente, valor_imovel, entrada, parcela, status, autor, data_criacao)
                VALUES (:c, :v, :e, :p, :s, :a, NOW())
            """)
            conn.execute(query, {"c": cliente, "v": valor_imovel, "e": entrada, "p": parcela, "s": status, "a": autor})
            conn.commit()
            st.cache_data.clear()
            return True
    except: return False

@st.cache_data(ttl=60)
def excluir_simulacao(id_simulacao):
    """Remove uma simulação do banco pelo ID com COMMIT MANUAL E EXPLÍCITO"""
    engine = get_engine()
    if engine is None: return False
    
    # Garantia: Converte para inteiro aqui também
    id_safe = int(id_simulacao)
    
    try:
        # Abre a conexão
        with engine.connect() as conn:
            # 1. Cria o comando SQL com parametro seguro
            query = text("DELETE FROM simulacoes WHERE id = :id_val")
            
            # 2. Executa o comando
            result = conn.execute(query, {"id_val": id_safe})
            
            # 3. O PULO DO GATO: Obriga o Commit (Salvar)
            conn.commit()
            
            # Verifica se alguma linha foi afetada
            if result.rowcount > 0:
                return True
            else:
                print(f"⚠️ Aviso: O comando rodou, mas nenhum ID {id_safe} foi encontrado para apagar.")
                return False
                
    except Exception as e:
        st.error(f"❌ Erro Python ao excluir: {e}")
        return False

@st.cache_data(ttl=60)
def carregar_historico(usuario_atual):
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    try:
        with engine.connect() as conn:
            # Se for admin, vê tudo. Se não, vê só o dele.
            q = "SELECT id, data_criacao, cliente, valor_imovel, parcela, status FROM simulacoes"
            if usuario_atual != 'admin':
                q += f" WHERE autor = '{usuario_atual}'"
            q += " ORDER BY data_criacao DESC LIMIT 500"
            
            result = conn.execute(text(q))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(e)
        return pd.DataFrame()

@st.cache_data(ttl=60)
def buscar_dados_dashboard(usuario_atual):
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    try:
        with engine.connect() as conn:
            q = "SELECT data_criacao, valor_imovel, status, autor FROM simulacoes"
            if usuario_atual != 'admin':
                q += f" WHERE autor = '{usuario_atual}'"
            
            result = conn.execute(text(q))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            if not df.empty:
                df['data_criacao'] = pd.to_datetime(df['data_criacao'])
            return df
    except: return pd.DataFrame()