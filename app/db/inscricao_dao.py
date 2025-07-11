from .conexao import conectar

def fazer_inscricao(id_pessoa, id_evento):
    """
    Chama a procedure tentar_inscrever_usuario no banco.
    """
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("CALL tentar_inscrever_usuario(%s, %s)", (id_evento, id_pessoa))
            conn.commit()
            return True, "Inscrição realizada com sucesso!"
        except Exception as e:
            mensagem = str(e)
            if 'CONTEXT:' in mensagem:
                mensagem = mensagem.split('CONTEXT:')[0].strip()
            conn.rollback()
            return False, f"Erro ao fazer inscrição: {mensagem}"
        finally:
            conn.close()
    return False, "Erro ao conectar ao banco de dados."

def atualizar_inscricao(id_inscricao, id_pessoa, id_evento, status_inscricao, status_checkin_evento):
    """
    Atualiza os dados de uma inscrição existente.
    """
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE inscricao
                SET id_pessoa = %s,
                    id_evento = %s,
                    status_inscricao = %s,
                    status_checkin_evento = %s
                WHERE id_inscricao = %s
            """, (id_pessoa, id_evento, status_inscricao, status_checkin_evento, id_inscricao))
            conn.commit()
            return True, "Inscrição atualizada com sucesso!"
        except Exception as e:
            conn.rollback()
            return False, f"Erro ao atualizar inscrição: {e}"
        finally:
            conn.close()
    return False, "Erro ao conectar ao banco."

def excluir_inscricao(id_inscricao):
    """
    Exclui uma inscrição, desde que não tenha certificado vinculado.
    """
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM certificado WHERE id_inscricao = %s", (id_inscricao,))
            qtd = cur.fetchone()[0]
            if qtd > 0:
                return False, "Não é possível excluir a inscrição: já existe certificado vinculado."

            cur.execute("DELETE FROM inscricao WHERE id_inscricao = %s", (id_inscricao,))
            conn.commit()
            return True, "Inscrição excluída com sucesso."
        except Exception as e:
            conn.rollback()
            return False, f"Erro ao excluir inscrição: {e}"
        finally:
            conn.close()
    return False, "Erro ao conectar ao banco."

def listar_inscricoes():
    """
    Lista todas as inscrições com nome da pessoa e do evento.
    """
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT i.id_inscricao, p.nome, e.nome, i.status_inscricao, i.status_checkin_evento
                FROM inscricao i
                JOIN pessoa p ON i.id_pessoa = p.cpf
                JOIN evento e ON i.id_evento = e.id_evento
                ORDER BY i.id_inscricao
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erro ao listar inscrições: {e}")
            return []
        finally:
            conn.close()
    return []

def buscar_inscricao_por_id(id_inscricao):
    """
    Retorna os dados de uma inscrição específica.
    """
    conn = conectar()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_inscricao, id_pessoa, id_evento, status_inscricao, status_checkin_evento
                FROM inscricao
                WHERE id_inscricao = %s
            """, (id_inscricao,))
            return cur.fetchone()
        except Exception as e:
            print(f"Erro ao buscar inscrição: {e}")
            return None
        finally:
            conn.close()
    return None
