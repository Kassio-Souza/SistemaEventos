from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.services import certificado_service
from app.db.certificado_dao import lista_certificados

certificados_bp = Blueprint('certificados_bp', __name__, template_folder='../templates')

@certificados_bp.route('/', methods=['GET', 'POST'])
def certificados():
    cpf = None
    certificados = []
    mensagem = None

    if request.method == 'POST':
        cpf = request.form.get('cpf', '').strip()
        if not cpf:
            mensagem = "Por favor, digite um CPF válido."
        else:
            certificado_service.gerar_pendentes()
            certificados, mensagem = certificado_service.buscar_por_cpf(cpf)

    return render_template('certificados.html',
                           certificados=certificados,
                           cpf=cpf,
                           mensagem=mensagem)

@certificados_bp.route('/visualizar/<int:id_certificado>')
def visualizar_certificado(id_certificado):
    return certificado_service.visualizar_certificado(id_certificado)


@certificados_bp.route('/lista', methods=['GET'])
def listar_todos_certificados():
    certificados = lista_certificados()
    return jsonify(certificados)