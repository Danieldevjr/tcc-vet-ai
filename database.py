import sqlite3
import hashlib
import pandas as pd
from datetime import datetime, timezone, timedelta

NOME_BANCO = "diagnosticos_vet.db"

def conectar_banco():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
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
        sucesso = False 
    finally:
        conn.close()
        
    return sucesso

def autenticar_usuario(email, senate):
    """Verifica credenciais e retorna os dados do utilizador se válidos."""
    conn = conectar_banco()
    cursor = conn.cursor()
    senha_h = hash_senha(senate)
    
    cursor.execute("""
        SELECT id, nome, email, role FROM usuarios
        WHERE email = ? AND senha_hash = ?
    """, (email, senha_h))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "nome": user[1], "email": user[2], "role": user[3]}
    return None

def salvar_diagnostico(nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca):
    """Salva os dados do prontuário com o fuso horário oficial do Brasil (UTC-3)."""
    fuso_br = timezone(timedelta(hours=-3))
    data_registro = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO diagnosticos (data_hora, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data_registro, nome_arquivo, nome_animal, especie, int(idade), nome_tutor, diagnostico, float(confianca)))
    
    conn.commit()
    conn.close()
    
    return data_registro

def carregar_historico():
    """Carrega todos os registros do banco de dados para o Pandas."""
    conn = conectar_banco()
    query = "SELECT id, data_hora, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca FROM diagnosticos ORDER BY id DESC"
    
    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
        
    return df