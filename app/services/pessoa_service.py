from app.db.pessoa_dao import inserir_pessoa, listar_pessoas, obter_departamentos, atualizar_pessoa_dao, excluir_pessoa_por_cpf, buscar_pessoa_por_cpf
#from utils.cursos import CURSOS_UNB  # ou manter em settings
from flask import flash
from app.utils.cursos import CURSOS_UNB

TIPOS_PESSOA = ['aluno', 'professor', 'tecnico administrativo', 'convidado']

def processar_cadastro(form):
    cpf = form.get('cpf', '').strip()
    nome = form.get('nome', '').strip()
    email = form.get('email', '').strip()
    telefone = form.get('telefone', '').strip()
    pcd = form.get('pcd', '').lower() == 'true'
    tipo = form.get('tipo', '').lower()
    sexo = form.get('sexo', '').strip()

    matricula = form.get('matricula', '').strip()
    curso = form.get('curso', '').strip()
    cargo = form.get('cargo', '').strip()
    area = form.get('area_atuacao', '').strip()
    id_dep = form.get('id_departamento', '').strip()
    id_departamento = int(id_dep) if id_dep else None

    # Validações básicas
    if not cpf:
        return False, "CPF é obrigatório."
    if not nome:
        return False, "Nome é obrigatório."
    if not email or '@' not in email:
        return False, "Email inválido."
    if tipo not in TIPOS_PESSOA:
        return False, "Tipo de pessoa inválido."

    if tipo in ['aluno', 'professor', 'tecnico administrativo'] and not matricula:
        return False, "Matrícula é obrigatória para esse tipo."
    if tipo == 'aluno' and not curso:
        return False, "Curso é obrigatório para aluno."
    if tipo == 'professor' and not id_departamento:
        return False, "Departamento obrigatório para professor."
    if tipo == 'tecnico administrativo' and (not cargo or not id_departamento):
        return False, "Cargo e departamento são obrigatórios."
    if tipo == 'convidado' and not area:
        return False, "Área de atuação obrigatória para convidado."

    dados = (
        cpf, nome, email, telefone, pcd, tipo, matricula,
        curso, cargo, area, id_departamento, sexo
    )
    return inserir_pessoa(dados)

def carregar_edicao(cpf):
    pessoa = buscar_pessoa_por_cpf(cpf)
    pessoas = listar_pessoas()
    departamentos = obter_departamentos()
    return pessoa, pessoas, departamentos

def atualizar_pessoa(cpf, form):
    dados = {
        'email': form.get('email'),
        'telefone': form.get('telefone'),
        'pcd': str(form.get('pcd', '')).lower() == 'true',
        'tipo': form.get('tipo', '').lower(),
        'matricula': form.get('matricula'),
        'curso': form.get('curso'),
        'cargo': form.get('cargo'),
        'area': form.get('area_atuacao'),
        'id_departamento': int(form.get('id_departamento')) if form.get('id_departamento') else None,
    }
    return atualizar_pessoa_dao(cpf, dados)

def excluir_pessoa(cpf):
    return excluir_pessoa_por_cpf(cpf)
