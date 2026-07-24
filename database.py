import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta

NOME_BANCO = "diagnosticos_vet.db"

def conectar_banco():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(NOME_BANCO)

def inicializar_banco():
    """
    Cria a tabela 'diagnosticos' caso ela ainda não exista.
    Estrutura composta por 9 colunas essenciais para o Prontuário Clínico.
    """
    conn = conectar_banco()
    cursor = conn.cursor()
    
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
            confianca REAL NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def salvar_diagnostico(nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca):
    """
    Salva os dados do prontuário e o resultado do diagnóstico no banco de dados.
    Força a captura da data/hora no fuso horário do Brasil (UTC-3).
    Retorna a string da data e hora formatada.
    """
    # Configura o fuso horário oficial do Brasil (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    data_registro = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO diagnosticos (data_hora, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data_registro, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, float(confianca)))
    
    conn.commit()
    conn.close()
    
    return data_registro

def carregar_historico():
    """
    Carrega todos os registros do banco de dados e retorna um DataFrame do Pandas.
    Os dados são ordenados do registro mais recente para o mais antigo.
    """
    conn = conectar_banco()
    query = "SELECT id, data_hora, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca FROM diagnosticos ORDER BY id DESC"
    
    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
        
    return df