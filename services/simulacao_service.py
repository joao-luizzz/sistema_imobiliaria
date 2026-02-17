import pandas as pd
from sqlalchemy import text
from datetime import datetime
from core.database import get_engine

def salvar_simulacao(cliente, valor_imovel, entrada, parcela, status, usuario):
    engine = get_engine()
    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query = text("""
    INSERT INTO simulacoes (cliente, valor_imovel, entrada, parcela, status, usuario_criacao, data_criacao)
    VALUES (:cli, :val, :ent, :par, :st, :usu, :dt)
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "cli": cliente, "val": valor_imovel, "ent": entrada,
                "par": parcela, "st": status, "usu": usuario, "dt": data_hoje
            })
            conn.commit()
        return True
    except Exception as e:
        # AQUI ESTÁ O SEGREDO: Mostra o erro vermelho na tela
        st.error(f"❌ Erro ao salvar no Banco de Dados: {e}")
        print(f"ERRO DETALHADO: {e}") # Mostra no terminal também
        return False
def carregar_historico(usuario):
    """Carrega lista de simulações (Admin vê tudo, corretor vê as dele)."""
    engine = get_engine()
    
    if usuario == 'admin':
        query = "SELECT * FROM simulacoes ORDER BY id DESC"
    else:
        query = f"SELECT * FROM simulacoes WHERE usuario_criacao = '{usuario}' ORDER BY id DESC"
        
    try:
        df = pd.read_sql(query, engine)
        return df
    except:
        return pd.DataFrame()

def excluir_simulacao(id_simulacao):
    """Deleta um registro pelo ID."""
    engine = get_engine()
    query = text("DELETE FROM simulacoes WHERE id = :id")
    
    try:
        with engine.connect() as conn:
            conn.execute(query, {"id": id_simulacao})
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao excluir: {e}")
        return False

def obter_dados_dashboard(usuario):
    """Mesma lógica do histórico, mas usado pelo dashboard."""
    return carregar_historico(usuario)