import sqlite3
import hashlib
import pandas as pd
from datetime import datetime, timezone, timedelta

NOME_BANCO = "diagnosticos_vet.db"

def conectar_banco():
    return sqlite3.connect(NOME_BANCO)

def hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 seguro para a senha."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def inicializar_banco():
    """Cria as tabelas do sistema se não existirem."""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela de Diagnósticos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnosticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            nome_arquivo TEXT NOT NULL,
            nome_animal TEXT NOT NULL,
            especie TEXT NOT NULL,
            idade INTEGER NOT NULL,
            nome_tutor TEXT NOT NULL,
            diagnostico TEXT NOT NULL,
            confianca REAL NOT NULL,
            usuario_id INTEGER
        )
    """)
    
    # Tabela de Utilizadores (Alunos e Admins)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'aluno'
        )
    """)
    
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, senha, role="aluno"):
    """Cadastra um novo utilizador. Retorna True se for bem-sucedido."""
    conn = conectar_banco()
    cursor = conn.cursor()
    senha_h = hash_senha(senha)
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, role)
            VALUES (?, ?, ?, ?)
        """, (nome, email, senha_h, role))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False # Email já existente
    finally:
        conn.close()
        
    return sucesso

def autenticar_usuario(email, senha):
    """Verifica credenciais e retorna os dados do utilizador se válidos."""
    conn = conectar_banco()
    cursor = conn.cursor()
    senha_h = hash_senha(senha)
    
    cursor.execute("""
        SELECT id, nome, email, role FROM usuarios
        WHERE email = ? AND senha_hash = ?
    """, (email, senha_h))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "nome": user[1], "email": user[2], "role": user[3]}
    return None
#forçado envio data baseS