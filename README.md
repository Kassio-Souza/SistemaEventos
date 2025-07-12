# Sistema de Gerenciamento de Eventos Universitários - UnB

## Informações importantes estão presentes neste arquivo. Vale a pena lê-lo.

Este sistema foi desenvolvido por **Ana Paula Gomes de Matos**, **Kassio Gândara de Souza**,**Kaillany Perreira Santos**, como parte da disciplina de Banco de Dados, com o objetivo de gerenciar eventos acadêmicos da Universidade de Brasília (UnB). 
A aplicação permite o cadastro e a visualização de eventos, pessoas e inscrições, com foco em integridade de dados, escalabilidade e possibilidade de análise de métricas futuras.

---

## Nosso Objetivo:

Criar um sistema completo e funcional que:

- Gerencie eventos, participantes, responsáveis e atividades.
- Garanta **consistência e integridade referencial** no banco de dados.
- Permita análise futura por meio de **views analíticas**, **triggers automáticas** e **procedures reutilizáveis**.
- Suporte documentos em PDF, como **cronogramas**.
- Seja conectado a um banco **PostgreSQL online**, permitindo verificação prática via pgAdmin, DBeaver, ou similar.

---

## Modelagem do Banco:

O banco foi projetado com **restrições `ON DELETE RESTRICT`** para garantir:

- Segurança e integridade dos dados relacionados.
- Impedir exclusão acidental de registros que possuem dependências.
- Exigir ação explícita do sistema antes de excluir registros importantes (ex: eventos com inscrições).

Essa modelagem favorece **análises confiáveis** no futuro, como:

- Número médio de inscritos por evento.
- Distribuição de eventos por tipo de pessoa (professor, aluno etc.).
- Eventos com mais certificados gerados.

---

## CRUD: Pessoa, Evento e Inscrição:

### Pessoa (`/pessoa`)

- Criação, edição e exclusão de registros.
- Campos dinâmicos de acordo com o tipo de pessoa: `aluno`, `professor`, `técnico administrativo`, `convidado`.
- Restrições:
  - O CPF é **chave primária**.
  - E-mails e matrículas são **únicos**.
  - `id_departamento` só é obrigatório para professores e técnicos.

 Exclusão:
- Se a pessoa tiver inscrição, evento ou organização vinculados, a exclusão será **bloqueada** (`RESTRICT`).

---

###  Evento (`/evento`)

- Criação com cronograma (PDF), dados de local, responsável e departamento.
- Edição e exclusão com confirmação.
- Suporte a várias **atividades**.
- Responsável deve estar cadastrado como pessoa válida.

 PDF:
- O cronograma é enviado via formulário HTML com `enctype="multipart/form-data"`:
  ```python
  cronograma_file = request.files.get('cronograma')
  v_cronograma = cronograma_file.read()
  ```
- Armazenado como `BYTEA` no banco.
- Acesso via rota Flask:
  ```python
  @app.route('/evento/cronograma/<int:id_evento>')
  def visualizar_cronograma(id_evento):
      ...
      return send_file(BytesIO(blob), ...)
  ```

Exclusão:
- Eventos com inscrições, atividades ou organizadores **não podem ser excluídos diretamente**.
- A aplicação avisa e exige confirmação manual, em conformidade com o `ON DELETE RESTRICT`.

---

### Inscrição (`/inscricao`)

- Permite inscrever pessoas em eventos ativos.
- Valida duplicidade e disponibilidade de vagas.
- Suporte a alteração de status (pendente, confirmado, cancelado) e check-in.

 Exclusão:
- Inscrições não podem ser removidas se vinculadas a certificados pendentes (por trigger).
- `certificados_pendentes` usa `ON DELETE CASCADE`, removendo automaticamente os pendentes se a inscrição for apagada.

---

## Procedure: `tentar_inscrever_usuario(p_id_evento, p_cpf)`

 Criada diretamente no **banco de dados**, por ser:

- Mais eficiente e rápida para execução em lote.
- Mais segura, pois roda diretamente no contexto transacional do banco.
- Fácil de testar e auditar fora da aplicação.

 Valida:

- Pessoa existe.
- Evento está ativo.
- Vaga disponível.
- Pessoa não inscrita.

**Exemplos de uso (casos de teste)**:
```sql
Exexute na sequencia:
-- Evento cheio (erro esperado)
CALL tentar_inscrever_usuario(13, '00100020033');

-- Evento evento concluido (erro esperado)
CALL tentar_inscrever_usuario(6, '00100020033');

-- Evento ativo, com vagas
CALL tentar_inscrever_usuario(12, '00100020033');

-- Pessoa já inscrita (erro esperado)
CALL tentar_inscrever_usuario(12, '00100020033');

```

---

## View: `resumo_eventos_com_organizadores`

 Criada no banco para:

- Agregar dados complexos em tempo de execução.
- Reduzir a lógica no backend.
- Permitir análise rápida com ferramentas externas (BI, Excel, etc.).

Dados exibidos:

- Nome e status do evento.
- Modalidade.
- Datas de início/fim.
- Departamento.
- Organizadores (via `string_agg`).
- Total de inscritos confirmados.
- Vagas restantes.
- Total de atividades.

Referência técnica usada:  
https://neon.com/postgresql/postgresql-aggregate-functions/postgresql-string_agg-function

---

##  Triggers Criadas (extra)

###  `trg_gerar_certificados_evento`
Cria certificados pendentes automaticamente quando o status do evento muda para `concluido`.

```sql
CREATE TRIGGER trg_gerar_certificados_evento
AFTER UPDATE ON evento
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION gerar_certificados_para_evento_concluido();
```

###  `trg_checkin_certificado`
Gera pendência de certificado quando o participante faz check-in em evento já concluído.

```sql
CREATE TRIGGER trg_checkin_certificado
AFTER UPDATE ON inscricao
FOR EACH ROW
WHEN (OLD.status_checkin_evento IS DISTINCT FROM NEW.status_checkin_evento)
EXECUTE FUNCTION registrar_certificado_pendente();
```

 Referência técnica:  
https://www.postgresql.org/docs/current/plpgsql-trigger.html

---

## Acesso ao Banco de Dados

As credenciais para conexão estão disponíveis no arquivo:

```
app/config.py
```

 *"Para caso seja difícil de encontrar deixarei ela nesse arquivo, as credenciais."*
```python
DB_NAME = 'postgres'
DB_USER = 'postgres.rxsowfuvofotbifooljx'
DB_PASSWORD = 'SistemaDB2025'
DB_HOST = 'aws-0-sa-east-1.pooler.supabase.com'
DB_PORT = '5432'

Essas credenciais podem ser usadas em **pgAdmin, DBeaver ou similar** para comprovar:

- Conexão ativa com o banco PostgreSQL remoto.
- Visualização das tabelas, procedures, views e triggers.
- Armazenamento de arquivos PDF no campo `cronograma` (tipo BYTEA).

---

##  Link do Sistema

Através do seguinte link, é possível **comprovar visualmente** o funcionamento completo do sistema:

- Exclusões protegidas por dependências
- Leitura e visualização de dados relacionados
- Atualização de registros com verificação de integridade
- Conexão com banco remoto
- Armazenamento e exibição de cronograma (PDF)

 [https://sistemaeventos.onrender.com/] como o serviço é gratuito pode demorar 50 segundos para compilar.

---

##  Referências Utilizadas

- [PostgreSQL CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html)
- [PL/pgSQL Triggers](https://www.postgresql.org/docs/current/plpgsql-trigger.html)
- [String Aggregation PostgreSQL](https://neon.com/postgresql/postgresql-aggregate-functions/postgresql-string_agg-function)

---


