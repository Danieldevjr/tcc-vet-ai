import sqlite3
from datetime import datetime
import pandas as pd

ARQUIVO_DB = 'diagnosticos_vet.db'

def inicializar_banco():
    conn = sqlite3.connect(ARQUIVO_DB)
    cursor = conn.cursor()
    # Adicionadas colunas para o prontuário clínico
    cursor.execute('''CREATE TABLE IF NOT EXISTS historico (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        data_hora TEXT, 
                        nome_arquivo TEXT, 
                        nome_animal TEXT,
                        especie TEXT,
                        idade INTEGER,
                        nome_tutor TEXT,
                        diagnostico TEXT, 
                        confianca REAL)''')
    conn.commit()
    conn.close()

def salvar_diagnostico(nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca):
    conn = sqlite3.connect(ARQUIVO_DB)
    cursor = conn.cursor()
    data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute('''INSERT INTO historico 
                   (data_hora, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (data_hora_atual, nome_arquivo, nome_animal, especie, idade, nome_tutor, diagnostico, confianca))
    conn.commit()
    conn.close()
    return data_hora_atual

def carregar_historico():
    conn = sqlite3.connect(ARQUIVO_DB)
    df = pd.read_sql_query("SELECT * FROM historico ORDER BY id DESC", conn)
    conn.close()
    return df