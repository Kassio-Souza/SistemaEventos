from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import pessoa_service
from app.db.pessoa_dao import listar_pessoas
from app.db.pessoa_dao import obter_departamentos
from app.utils.cursos import CURSOS_UNB # opcional: criar um arquivo de cursos

pessoa_bp = Blueprint('pessoa_bp', __name__, template_folder='../templates')

@pessoa_bp.route('/', methods=['GET', 'POST'])
def pessoa():
    if request.method == 'POST':
        dados = request.form
        sucesso, mensagem = pessoa_service.processar_cadastro(dados)
        flash(mensagem, "success" if sucesso else "danger")
        return redirect(url_for('pessoa_bp.pessoa'))

    pessoas = listar_pessoas()
    departamentos = obter_departamentos()
    return render_template('pessoa.html',
                           tipos_pessoa=pessoa_service.TIPOS_PESSOA,
                           pessoas=pessoas,
                           pessoa_para_editar=None,
                           departamentos=departamentos,
                           cursos=CURSOS_UNB)

@pessoa_bp.route('/editar/<cpf>', methods=['GET', 'POST'])
def pessoa_editar(cpf):
    if request.method == 'POST':
        dados = request.form
        sucesso, mensagem = pessoa_service.atualizar_pessoa(cpf, dados)
        flash(mensagem, "success" if sucesso else "danger")
        return redirect(url_for('pessoa_bp.pessoa'))

    pessoa, pessoas, departamentos = pessoa_service.carregar_edicao(cpf)
    return render_template('pessoa.html',
                           tipos_pessoa=pessoa_service.TIPOS_PESSOA,
                           pessoas=pessoas,
                           pessoa_para_editar=pessoa,
                           departamentos=departamentos,
                           cursos=CURSOS_UNB)

@pessoa_bp.route('/excluir/<cpf>', methods=['POST'])
def pessoa_excluir(cpf):
    sucesso, mensagem = pessoa_service.excluir_pessoa(cpf)
    flash(mensagem, "success" if sucesso else "danger")
    return redirect(url_for('pessoa_bp.pessoa'))
