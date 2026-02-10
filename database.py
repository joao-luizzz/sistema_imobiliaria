import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = 'imoveis.db'

def init_db():
    """Cria a tabela se não existir."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS simulacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            data TEXT,
            valor_imovel REAL,
            entrada REAL,
            parcela REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_simulacao(cliente, valor_imovel, entrada, parcela, status):
    """Insere uma nova simulação."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO simulacoes (cliente, data, valor_imovel, entrada, parcela, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (cliente, data_atual, valor_imovel, entrada, parcela, status))
    conn.commit()
    conn.close()

def carregar_historico():
    """Lê todas as simulações."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM simulacoes ORDER BY id DESC", conn)
    conn.close()
    return df