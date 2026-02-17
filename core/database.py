import sqlalchemy as db
from sqlalchemy import create_engine, inspect, text
import streamlit as st

# Configuração da Conexão
# Se quiser mudar para PostgreSQL depois, é só mexer AQUI.
DB_URL = "sqlite:///database.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

def get_engine():
    """Retorna a engine para os Services usarem."""
    return engine

def inicializar_banco():
    """Cria a tabela se não existir (Rodar no início do app)"""
    metadata = db.MetaData()
    
    if not inspect(engine).has_table("simulacoes"):
        tabela = db.Table('simulacoes', metadata,
            db.Column('id', db.Integer, primary_key=True, autoincrement=True),
            db.Column('cliente', db.String),
            db.Column('valor_imovel', db.Float),
            db.Column('entrada', db.Float),
            db.Column('parcela', db.Float),
            db.Column('status', db.String), # Campo texto extra (ex: Parecer)
            db.Column('usuario_criacao', db.String),
            db.Column('data_criacao', db.String) # Vamos salvar como string ISO ou formatada
        )
        metadata.create_all(engine)