from app.db.conexao import conectar
from flask import send_file, abort
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime
import psycopg2

def gerar_certificado_pdf(nome_pessoa, nome_evento, carga_horaria, data_conclusao, autenticacao):
    """
    Gera o conteúdo binário de um certificado em PDF.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "Certificado de Participação")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Certificamos que {nome_pessoa}")
    c.drawString(100, 680, f"participou do evento '{nome_evento}' com carga horária de {carga_horaria} horas.")
    c.drawString(100, 660, f"Data de conclusão: {data_conclusao.strftime('%d/%m/%Y')}")
    c.drawString(100, 640, f"Código de autenticação: {autenticacao}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

def gerar_pendentes():
    """
    Processa todos os certificados pendentes e gera os PDFs correspondentes.
    """
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

def buscar_por_cpf(cpf):
    """
    Retorna todos os certificados emitidos para uma pessoa com o CPF fornecido.
    """
    conn = conectar()
    certificados = []
    mensagem = None
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.id_certificado, e.nome, c.carga_horaria, c.data_de_conclusao, c.autenticacao
                FROM certificado c
                JOIN inscricao i ON c.id_inscricao = i.id_inscricao
                JOIN evento e ON i.id_evento = e.id_evento
                WHERE i.id_pessoa = %s
                ORDER BY c.data_de_conclusao DESC
            """, (cpf,))
            certificados = cur.fetchall()
            if not certificados:
                mensagem = "Nenhum certificado encontrado para este CPF."
        except Exception as e:
            mensagem = f"Erro ao buscar certificados: {e}"
        finally:
            conn.close()
    else:
        mensagem = "Erro de conexão com o banco de dados."

    return certificados, mensagem

def visualizar_certificado(id_certificado):
    """
    Retorna o arquivo PDF de um certificado específico.
    """
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT arquivo_pdf FROM certificado WHERE id_certificado = %s", (id_certificado,))
            resultado = cur.fetchone()
            if resultado and resultado[0]:
                return send_file(
                    BytesIO(resultado[0]),
                    mimetype='application/pdf',
                    as_attachment=False,
                    download_name=f'certificado_{id_certificado}.pdf'
                )
            else:
                abort(404, "Certificado não encontrado ou sem PDF.")
        except Exception as e:
            abort(500, f"Erro ao carregar certificado: {e}")
        finally:
            conn.close()
    else:
        abort(500, "Erro ao conectar ao banco.")
