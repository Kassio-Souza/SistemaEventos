from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import evento_service
from app.db.evento_dao import obter_eventos, obter_evento_por_id, obter_locais, obter_departamentos, listar_possiveis_responsaveis

evento_bp = Blueprint('evento_bp', __name__, template_folder='../templates')



@evento_bp.route('/', methods=['GET', 'POST'])
def evento():
    if request.method == 'POST':
        sucesso, mensagem = evento_service.processar_cadastro(request)
        flash(mensagem, "success" if sucesso else "danger")
        return redirect(url_for('evento_bp.evento'))

    eventos = obter_eventos()
    locais = obter_locais()
    departamentos = obter_departamentos()
    responsaveis = listar_possiveis_responsaveis()
    return render_template('evento.html',
                           eventos=eventos,
                           locais=locais,
                           departamentos=departamentos,
                           modalidades=evento_service.MODALIDADES,
                           evento_para_editar=None,
                           responsaveis=responsaveis)

@evento_bp.route('/editar/<int:id_evento>', methods=['GET', 'POST'])
def evento_editar(id_evento):
    if request.method == 'POST':
        sucesso, mensagem = evento_service.processar_edicao(id_evento, request)
        flash(mensagem, "success" if sucesso else "danger")
        return redirect(url_for('evento_bp.evento'))

    evento = obter_evento_por_id(id_evento)
    eventos = obter_eventos()
    locais = obter_locais()
    departamentos = obter_departamentos()
    responsaveis = listar_possiveis_responsaveis()
    
    return render_template('evento.html',
                           eventos=eventos,
                           locais=locais,
                           departamentos=departamentos,
                           modalidades=evento_service.MODALIDADES,
                           evento_para_editar=evento,
                           responsaveis=responsaveis)

@evento_bp.route('/excluir/<int:id_evento>', methods=['POST'])
def evento_excluir(id_evento):
    forcar = request.form.get('forcar_exclusao') == 'true'
    sucesso, mensagem = evento_service.excluir_evento(id_evento, forcar)
    flash(mensagem, "success" if sucesso else "danger")
    return redirect(url_for('evento_bp.evento'))

@evento_bp.route('/cronograma/view/<int:id_evento>')
def visualizar_cronograma(id_evento):
    return evento_service.visualizar_cronograma(id_evento)

@evento_bp.route('/lista')
def eventos_lista():
    eventos = obter_eventos()
    detalhes = evento_service.carregar_detalhes(eventos)
    return render_template('eventos_lista.html', eventos=eventos, detalhes_eventos=detalhes)
