from datetime import datetime
from flask import send_file, abort
from io import BytesIO
from app.db.evento_dao import (
    cadastrar_evento,
    obter_eventos,
    obter_evento_por_id,
    obter_locais,
    obter_departamentos,
    atualizar_evento,
    excluir_evento_dao,
    obter_detalhes_evento
)

# Enum de modalidades válidas para seleção no formulário
MODALIDADES = ['presencial', 'remoto', 'hibrido']

def validar_dados_evento(form):
    """Valida os campos do formulário de evento."""
    erros = []
    nome = form.get('nome', '').strip()
    descricao = form.get('descricao', '').strip()
    status = form.get('status', '').strip()
    vagas = form.get('vagas', '').strip()
    modalidade = form.get('modalidade', '').strip()
    carga = form.get('carga_horaria', '').strip()
    inicio = form.get('inicio', '').replace('T', ' ').strip()
    fim = form.get('fim', '').replace('T', ' ').strip()
    id_local = form.get('id_local', '').strip()
    cpf_resp = form.get('resp_cpf', '').strip()
    id_departamento = form.get('id_departamento', '').strip()

    # Validações
    if not nome:
        erros.append("Nome do evento é obrigatório.")
    if not vagas.isdigit() or int(vagas) <= 0:
        erros.append("Número de vagas inválido.")
    if not carga.isdigit() or int(carga) <= 0:
        erros.append("Carga horária inválida.")
    try:
        dt_inicio = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
        dt_fim = datetime.strptime(fim, "%Y-%m-%d %H:%M:%S")
        if dt_inicio >= dt_fim:
            erros.append("Início deve ser antes do fim.")
    except:
        erros.append("Datas inválidas.")
    if not id_local:
        erros.append("Local é obrigatório.")
    if not cpf_resp:
        erros.append("CPF do responsável é obrigatório.")
    if not id_departamento:
        erros.append("Departamento responsável é obrigatório.")

    return erros

def processar_cadastro(request):
    """Processa o cadastro de um novo evento."""
    form = request.form
    cronograma_file = request.files.get('cronograma')
    cronograma = cronograma_file.read() if cronograma_file and cronograma_file.filename else None

    erros = validar_dados_evento(form)
    if erros:
        return False, " ".join(erros)

    return cadastrar_evento(
        form['nome'].strip(),
        form['descricao'].strip(),
        form['status'].strip(),
        form['vagas'].strip(),
        form['modalidade'].strip(),
        form['carga_horaria'].strip(),
        form['inicio'].replace('T', ' ').strip(),
        form['fim'].replace('T', ' ').strip(),
        cronograma,
        form['id_local'].strip(),
        form['resp_cpf'].strip(),
        form['id_departamento'].strip()
    )

def processar_edicao(id_evento, request):
    """Processa a edição de um evento existente."""
    form = request.form
    cronograma_file = request.files.get('cronograma')

    if cronograma_file and cronograma_file.filename:
        cronograma = cronograma_file.read()
    else:
        # Busca o cronograma atual do banco
        evento_atual = obter_evento_por_id(id_evento)
        cronograma = evento_atual[9]  # ou ['cronograma'] se for dicionário

    erros = validar_dados_evento(form)
    if erros:
        return False, " ".join(erros)

    return atualizar_evento(
        id_evento,
        form['nome'].strip(),
        form['descricao'].strip(),
        form['status'].strip(),
        form['vagas'].strip(),
        form['modalidade'].strip(),
        form['carga_horaria'].strip(),
        form['inicio'].replace('T', ' ').strip(),
        form['fim'].replace('T', ' ').strip(),
        cronograma,
        form['id_local'].strip(),
        form['resp_cpf'].strip()
    )
def carregar_detalhes(lista_eventos):
    """Carrega todos os detalhes para cada evento da listagem pública."""
    detalhes = {}
    for evento in lista_eventos:
        detalhes[evento[0]] = obter_detalhes_evento(evento[0])
    return detalhes

def excluir_evento(id_evento, forcar_exclusao=False):
    """Exclui evento, tratando regras de inscrição e certificado."""
    return excluir_evento_dao(id_evento, forcar_exclusao)

def visualizar_cronograma(id_evento):
    """Retorna o arquivo binário do cronograma armazenado."""
    conn = None
    try:
        from app.db.conexao import conectar
        conn = conectar()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT cronograma FROM evento WHERE id_evento = %s", (id_evento,))
            resultado = cur.fetchone()
            if resultado and resultado[0]:
                return send_file(BytesIO(resultado[0]), mimetype='application/pdf')
            else:
                abort(404, "Arquivo não encontrado.")
    finally:
        if conn:
            conn.close()
    abort(500, "Erro ao acessar cronograma.")


