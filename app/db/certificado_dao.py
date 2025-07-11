from datetime import datetime
from .conexao import conectar
from app.utils.pdf_generator import gerar_certificado_pdf
import psycopg2


def processar_certificados_pendentes():
    conn = conectar()
    if not conn:
        return "Erro ao conectar ao banco."
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT cp.id, i.id_inscricao, i.id_pessoa, i.id_evento,
                   p.nome, e.nome, e.carga_horaria
            FROM certificados_pendentes cp
            JOIN inscricao i ON cp.id_inscricao = i.id_inscricao
            JOIN pessoa p ON i.id_pessoa = p.cpf
            JOIN evento e ON i.id_evento = e.id_evento
            WHERE cp.processado = false
        """)
        pendentes = cur.fetchall()
        total = 0
        for row in pendentes:
            id_pendente, id_inscricao, cpf, id_evento, nome_pessoa, nome_evento, carga = row
            data_conclusao = datetime.now()
            autenticacao = f"{id_inscricao}-{int(data_conclusao.timestamp())}"
            pdf = gerar_certificado_pdf(nome_pessoa, nome_evento, carga, data_conclusao, autenticacao)

            cur.execute("""
                INSERT INTO certificado (id_inscricao, carga_horaria, autenticacao, data_de_conclusao, arquivo_pdf)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_inscricao, carga, autenticacao, data_conclusao, psycopg2.Binary(pdf)))

            cur.execute("UPDATE certificados_pendentes SET processado = true WHERE id = %s", (id_pendente,))
            total += 1
        conn.commit()
        return f"{total} certificados gerados com sucesso."
    except Exception as e:
        conn.rollback()
        return f"Erro ao gerar certificados: {e}"
    finally:
        conn.close()


def lista_certificados():
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                c.id_certificado,
                p.nome AS nome_pessoa,
                p.cpf,
                c.carga_horaria,
                c.autenticacao,
                c.data_de_conclusao
            FROM certificado c
            JOIN inscricao i ON c.id_inscricao = i.id_inscricao
            JOIN pessoa p ON i.id_pessoa = p.cpf
        """)
        certificados = cur.fetchall()
        conn.commit()
        return certificados
    except Exception as e:
        conn.rollback()
        return f"Erro ao gerar certificados: {e}"
    finally:
        conn.close()