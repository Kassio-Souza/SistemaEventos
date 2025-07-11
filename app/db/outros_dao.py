from .conexao import conectar
from psycopg2 import Error
from datetime import datetime
from flask import flash

def validar_data_hora_formato(dt_str):
    if 'T' in dt_str:
        dt_str = dt_str.replace('T', ' ')
    try:
        datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

tipos_pessoa_enum = ['aluno', 'professor', 'tecnico administrativo', 'Convidado']
modalidades_enum = ['presencial', 'remoto']

def _obter_locais():
    conn = conectar()
    locais = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_local, nome_local FROM local ORDER BY nome_local")
            locais = cur.fetchall()
        except Error as e:
            flash(f"Erro ao carregar locais: {e}", "danger")
        finally:
            conn.close()
    return locais

def obter_departamentos():
    conn = conectar()  # sua função de conexão
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_departamento, nome, sigla FROM departamento ORDER BY nome")
            resultados = cur.fetchall()
            return resultados  # lista de tuplas: (id, nome, sigla)
        finally:
            conn.close()
    return []