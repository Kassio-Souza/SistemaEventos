from .conexao import conectar

# Inserção de nova pessoa
def inserir_pessoa(pessoa_data):
    conn = conectar()
    if not conn:
        return False, "Erro ao conectar ao banco."

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pessoa (
                cpf, nome, email, telefone, pcd, tipo_pessoa,
                matricula, curso, cargo, area_atuacao, id_departamento, sexo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, pessoa_data)
        conn.commit()
        return True, "Pessoa cadastrada com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao inserir pessoa: {e}"
    finally:
        conn.close()

# Listagem de pessoas para a tela
def listar_pessoas():
    conn = conectar()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT cpf, nome, email, telefone, pcd, tipo_pessoa
            FROM pessoa
            ORDER BY nome DESC
        """)
        return cur.fetchall()
    except Exception as e:
        print(f"Erro ao listar pessoas: {e}")
        return []
    finally:
        conn.close()

# Busca uma pessoa pelo CPF
def buscar_pessoa_por_cpf(cpf):
    conn = conectar()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM pessoa WHERE cpf = %s", (cpf,))
        return cur.fetchone()
    except Exception as e:
        print(f"Erro ao buscar pessoa: {e}")
        return None
    finally:
        conn.close()

# Atualiza uma pessoa já existente
def atualizar_pessoa_dao(cpf, dados):
    conn = conectar()
    if not conn:
        return False, "Erro ao conectar ao banco."

    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE pessoa
            SET email = %s,
                telefone = %s,
                pcd = %s,
                tipo_pessoa = %s,
                matricula = %s,
                curso = %s,
                cargo = %s,
                area_atuacao = %s,
                id_departamento = %s
            WHERE cpf = %s
        """, (
            dados['email'], dados['telefone'], dados['pcd'], dados['tipo'],
            dados['matricula'], dados['curso'], dados['cargo'],
            dados['area'], dados['id_departamento'], cpf
        ))
        conn.commit()
        return True, "Pessoa atualizada com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao atualizar pessoa: {e}"
    finally:
        conn.close()

# Excluir pessoa por CPF
def excluir_pessoa_por_cpf(cpf):
    conn = conectar()
    if not conn:
        return False, "Erro ao conectar ao banco."

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM pessoa WHERE cpf = %s", (cpf,))
        conn.commit()
        return True, "Pessoa excluída com sucesso."
    except Exception as e:
        conn.rollback()
        if "foreign key" in str(e).lower():
            return False, "Não é possível excluir esta pessoa pois há vínculos com inscrições ou eventos."
        return False, f"Erro ao excluir pessoa: {e}"
    finally:
        conn.close()

# Departamentos para dropdown
def obter_departamentos():
    conn = conectar()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_departamento, nome, sigla FROM departamento ORDER BY nome")
        return cur.fetchall()
    except Exception as e:
        print(f"Erro ao carregar departamentos: {e}")
        return []
    finally:
        conn.close()
