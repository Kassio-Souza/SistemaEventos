from app.db.inscricao_dao import (
    fazer_inscricao,
    atualizar_inscricao,
    excluir_inscricao,
    listar_inscricoes,
    buscar_inscricao_por_id
)
from app.db.pessoa_dao import listar_pessoas
from app.db.evento_dao import obter_eventos

def carregar_pessoas():
    """Retorna todas as pessoas cadastradas para uso nos formulários de inscrição."""
    return listar_pessoas()

def carregar_eventos():
    """Retorna todos os eventos disponíveis."""
    return obter_eventos()

def carregar_inscricoes():
    """Retorna todas as inscrições feitas."""
    return listar_inscricoes()

def carregar_por_id(id_inscricao):
    """Retorna uma inscrição específica pelo ID."""
    return buscar_inscricao_por_id(id_inscricao)

def processar_formulario(form):
    """
    Processa o formulário de inscrição:
    - Pode ser uma nova inscrição
    - Uma atualização
    - Ou uma exclusão
    A lógica é determinada pelos campos presentes no formulário.
    """
    # EXCLUSÃO
    if 'excluir_id' in form:
        id_excluir = form.get('excluir_id', '').strip()
        if not id_excluir:
            return False, "ID da inscrição não informado para exclusão."
        return excluir_inscricao(int(id_excluir))

    # ATUALIZAÇÃO
    elif 'atualizar_id' in form:
        id_atualizar = form.get('atualizar_id', '').strip()
        id_pessoa = form.get('pessoa_id', '').strip()
        id_evento = form.get('evento_id', '').strip()
        status = form.get('status_inscricao', '').strip()
        checkin = form.get('status_checkin', '').strip().lower() == 'true'

        if not (id_atualizar and id_pessoa and id_evento and status):
            return False, "Dados incompletos para atualizar inscrição."

        return atualizar_inscricao(
            int(id_atualizar),
            id_pessoa,
            int(id_evento),
            status,
            checkin
        )

    # NOVA INSCRIÇÃO
    else:
        id_pessoa = form.get('pessoa_id', '').strip()
        id_evento = form.get('evento_id', '').strip()

        if not (id_pessoa and id_evento):
            return False, "Pessoa e evento devem ser selecionados."
        
        return fazer_inscricao(id_pessoa, int(id_evento))
