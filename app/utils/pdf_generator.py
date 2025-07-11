from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime

def gerar_certificado_pdf(nome_pessoa, nome_evento, carga_horaria, data_conclusao, autenticacao):
    """
    Gera o conteúdo binário de um certificado em PDF com as informações fornecidas.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Cabeçalho do certificado
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "Certificado de Participação")

    # Corpo do certificado
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Certificamos que {nome_pessoa}")
    c.drawString(100, 680, f"participou do evento '{nome_evento}' com carga horária de {carga_horaria} horas.")
    c.drawString(100, 660, f"Data de conclusão: {data_conclusao.strftime('%d/%m/%Y')}")
    c.drawString(100, 640, f"Código de autenticação: {autenticacao}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
