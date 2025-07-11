from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import inscricao_service

inscricao_bp = Blueprint('inscricao_bp', __name__, template_folder='../templates')

@inscricao_bp.route('/', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'POST':
        sucesso, mensagem = inscricao_service.processar_formulario(request.form)
        flash(mensagem, "success" if sucesso else "danger")
        return redirect(url_for('inscricao_bp.inscricao'))

    return render_template('inscricao.html', 
                           pessoas=inscricao_service.carregar_pessoas(),
                           eventos=inscricao_service.carregar_eventos(),
                           inscricoes=inscricao_service.carregar_inscricoes(),
                           inscricao_para_editar=None)

@inscricao_bp.route('/editar/<int:id_inscricao>', methods=['GET'])
def inscricao_editar(id_inscricao):
    inscricao = inscricao_service.carregar_por_id(id_inscricao)
    if not inscricao:
        flash("Inscrição não encontrada.", "danger")
        return redirect(url_for('inscricao_bp.inscricao'))

    return render_template('inscricao.html',
                           pessoas=inscricao_service.carregar_pessoas(),
                           eventos=inscricao_service.carregar_eventos(),
                           inscricoes=inscricao_service.carregar_inscricoes(),
                           inscricao_para_editar=inscricao)
