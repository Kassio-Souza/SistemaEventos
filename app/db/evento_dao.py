from .conexao import conectar
from datetime import datetime

def cadastrar_evento(nome, descricao, status, vagas, modalidade, carga_horaria, inicio, fim, cronograma, id_local, resp_cpf, id_departamento):
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            dt_inicio = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
            dt_fim = datetime.strptime(fim, "%Y-%m-%d %H:%M:%S")

            cur.execute("""
                INSERT INTO evento (
                    nome, descricao, status, numero_de_vagas,
                    modalidade, carga_horaria, data_hora_inicio,
                    data_hora_fim, cronograma, id_local,
                    responsavel_cpf, id_departamento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, descricao, status, int(vagas), modalidade, int(carga_horaria),
                  dt_inicio, dt_fim, cronograma, int(id_local), resp_cpf, int(id_departamento)))

            conn.commit()
            return True, "Evento cadastrado com sucesso!"
        except Exception as e:
            conn.rollback()
            return False, f"Erro ao cadastrar evento: {e}"
        finally:
            conn.close()
    return False, "Erro ao conectar ao banco de dados."

def obter_eventos():
    conn = conectar()
    eventos = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT e.id_evento, e.nome, e.descricao, e.status,
                       e.numero_de_vagas, e.modalidade, e.carga_horaria,
                       e.data_hora_inicio, e.data_hora_fim, e.cronograma,
                       l.nome_local, p.nome
                FROM evento e
                JOIN local l ON e.id_local = l.id_local
                JOIN pessoa p ON e.responsavel_cpf = p.cpf
                ORDER BY e.nome
            """)
            eventos = cur.fetchall()
        except Exception as e:
            eventos = []
            print(f"Erro ao obter eventos: {e}")
        finally:
            conn.close()
    return eventos

def obter_evento_por_id(id_evento):
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_evento, nome, descricao, status,
                       numero_de_vagas, modalidade, carga_horaria,
                       data_hora_inicio, data_hora_fim, cronograma,
                       id_local, responsavel_cpf
                FROM evento
                WHERE id_evento = %s
            """, (id_evento,))
            return cur.fetchone()
        except Exception as e:
            print(f"Erro ao buscar evento: {e}")
        finally:
            conn.close()
    return None

def atualizar_evento(id_evento, nome, descricao, status, vagas, modalidade, carga_horaria, inicio, fim, cronograma, id_local, resp_cpf):
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            dt_inicio = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
            dt_fim = datetime.strptime(fim, "%Y-%m-%d %H:%M:%S")

            cur.execute("""
                UPDATE evento
                SET nome=%s, descricao=%s, status=%s,
                    numero_de_vagas=%s, modalidade=%s, carga_horaria=%s,
                    data_hora_inicio=%s, data_hora_fim=%s, cronograma=%s,
                    id_local=%s, responsavel_cpf=%s
                WHERE id_evento = %s
            """, (nome, descricao, status, int(vagas), modalidade, int(carga_horaria),
                  dt_inicio, dt_fim, cronograma, int(id_local), resp_cpf, id_evento))

            conn.commit()
            return True, "Evento atualizado com sucesso!"
        except Exception as e:
            conn.rollback()
            return False, f"Erro ao atualizar evento: {e}"
        finally:
            conn.close()
    return False, "Erro ao conectar ao banco."

def excluir_evento_dao(id_evento, forcar_exclusao=False):
    conn = conectar()
    if not conn:
        return False, "Erro de conexão com o banco."

    try:
        cur = conn.cursor()

        # Verificar certificados
        cur.execute("""
            SELECT COUNT(*) FROM certificado c
            JOIN inscricao i ON c.id_inscricao = i.id_inscricao
            WHERE i.id_evento = %s
        """, (id_evento,))
        qtd_certificados = cur.fetchone()[0]
        if qtd_certificados > 0:
            return False, "Não é possível excluir o evento, pois há certificados gerados."

        # Verificar inscrições
        cur.execute("SELECT COUNT(*) FROM inscricao WHERE id_evento = %s", (id_evento,))
        qtd_inscricoes = cur.fetchone()[0]
        if qtd_inscricoes > 0 and not forcar_exclusao:
            return False, "Existem inscrições associadas. Deseja forçar a exclusão?"

        # Executar exclusão em cascata controlada
        cur.execute("DELETE FROM resposta WHERE id_evento = %s", (id_evento,))
        cur.execute("DELETE FROM inscricao WHERE id_evento = %s", (id_evento,))
        cur.execute("DELETE FROM organizadores WHERE id_evento = %s", (id_evento,))
        cur.execute("DELETE FROM atividades WHERE id_evento = %s", (id_evento,))
        cur.execute("DELETE FROM evento WHERE id_evento = %s", (id_evento,))

        conn.commit()
        return True, "Evento excluído com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao excluir evento: {e}"
    finally:
        conn.close()

def obter_locais():
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_local, nome_local FROM local ORDER BY nome_local")
            return cur.fetchall()
        except Exception as e:
            print(f"Erro ao carregar locais: {e}")
            return []
        finally:
            conn.close()
    return []

def obter_departamentos():
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_departamento, nome, sigla FROM departamento ORDER BY nome")
            return cur.fetchall()
        finally:
            conn.close()
    return []

def obter_detalhes_evento(id_evento):
    conn = conectar()
    detalhes = {}
    if conn:
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT e.id_evento, e.nome, e.descricao, e.status, e.numero_de_vagas,
                       e.modalidade, e.carga_horaria, e.data_hora_inicio, e.data_hora_fim,
                       e.cronograma, l.nome_local, l.especificacao_local,
                       p.nome AS nome_responsavel, d.nome AS nome_departamento
                FROM evento e
                JOIN local l ON e.id_local = l.id_local
                JOIN pessoa p ON e.responsavel_cpf = p.cpf
                JOIN departamento d ON e.id_departamento = d.id_departamento
                WHERE e.id_evento = %s
            """, (id_evento,))
            detalhes["evento"] = cur.fetchone()

            cur.execute("""
                SELECT nome, tipo_atividade, descricao, data_hora_inicio, data_hora_fim, espec_local
                FROM atividades
                WHERE id_evento = %s
                ORDER BY data_hora_inicio
            """, (id_evento,))
            detalhes["atividades"] = cur.fetchall()

            cur.execute("""
                SELECT p.nome, p.tipo_pessoa, i.status_inscricao
                FROM inscricao i
                JOIN pessoa p ON i.id_pessoa = p.cpf
                WHERE i.id_evento = %s
                ORDER BY i.status_inscricao DESC, p.nome
            """, (id_evento,))
            detalhes["inscritos"] = cur.fetchall()

        except Exception as e:
            print(f"Erro ao obter detalhes do evento: {e}")
        finally:
            conn.close()
    return detalhes

def listar_possiveis_responsaveis():
    conn = conectar()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT cpf, nome
                FROM pessoa
                WHERE tipo_pessoa IN ('professor', 'tecnico administrativo')
                ORDER BY nome
            """)
            resultados = cur.fetchall()
        return resultados
    finally:
        conn.close()
