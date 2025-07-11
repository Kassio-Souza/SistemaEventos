
-- ================================================
-- RESET TOTAL DO BANCO - DROP + CREATE
-- ================================================

-- Remover tabelas em ordem reversa de dependência
DROP TABLE IF EXISTS resposta CASCADE;
DROP TABLE IF EXISTS atividades CASCADE;
DROP TABLE IF EXISTS organizadores CASCADE;
DROP TABLE IF EXISTS certificado CASCADE;
DROP TABLE IF EXISTS inscricao CASCADE;
DROP TABLE IF EXISTS evento CASCADE;
DROP TABLE IF EXISTS pessoa CASCADE;
DROP TABLE IF EXISTS local CASCADE;
DROP TABLE IF EXISTS departamento CASCADE;
DROP TABLE IF EXISTS pesquisa_satisfacao CASCADE;

-- Remover ENUMs
DROP TYPE IF EXISTS tipo_pessoa_enum;
DROP TYPE IF EXISTS modalidade_enum;
DROP TYPE IF EXISTS status_evento_enum;

-- Criar ENUMs novamente
CREATE TYPE tipo_pessoa_enum AS ENUM ('aluno', 'professor', 'tecnico administrativo', 'convidado');
CREATE TYPE modalidade_enum AS ENUM ('presencial', 'remoto', 'hibrido');
CREATE TYPE status_evento_enum AS ENUM ('pendente', 'ativo', 'cancelado', 'concluido');


-- Tabela: departamento
CREATE TABLE departamento (
	id_departamento serial NOT NULL,
	nome varchar(45) NOT NULL,
	sigla varchar(10) NOT NULL,
	coordenador varchar(45) NOT NULL,
	email varchar(100) NOT NULL,
	CONSTRAINT departamento_email_key UNIQUE (email),
	CONSTRAINT departamento_pkey PRIMARY KEY (id_departamento)
);

-- Tabela: local
CREATE TABLE "local" (
	id_local serial NOT NULL,
	nome_local varchar(100) NOT NULL,
	especificacao_local varchar(100) NOT NULL,
	logradouro varchar(100) NOT NULL,
	cidade varchar(45) NOT NULL,
	estado varchar(2) NOT NULL,
	cep varchar(9) NOT NULL,
	CONSTRAINT local_pkey PRIMARY KEY (id_local)
);

-- Tabela: pessoa
CREATE TABLE pessoa (
	cpf bpchar(11) NOT NULL,
	nome varchar(45) NOT NULL,
	email varchar(100) NOT NULL,
	telefone varchar(11) NOT NULL,
	pcd bool NOT NULL,
	tipo_pessoa public."tipo_pessoa_enum" NOT NULL,
	matricula varchar(20) NULL,
	curso varchar(30) NULL,
	cargo varchar(45) NULL,
	area_atuacao varchar(50) NULL,
	id_departamento int8 NULL,
	sexo varchar(10) NULL,
	CONSTRAINT pessoa_email_key UNIQUE (email),
	CONSTRAINT pessoa_matricula_key UNIQUE (matricula),
	CONSTRAINT pessoa_pkey PRIMARY KEY (cpf),
	CONSTRAINT fk_pessoa_departamento FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: evento
CREATE TABLE evento (
	id_evento serial NOT NULL,
	nome varchar(100) NOT NULL,
	descricao text NOT NULL,
	status varchar(20) NOT NULL,
	numero_de_vagas int NOT NULL,
	modalidade public."modalidade_enum" NOT NULL,
	carga_horaria int NOT NULL,
	data_hora_inicio timestamp NOT NULL,
	data_hora_fim timestamp NOT NULL,
	cronograma bytea NOT NULL,
	id_local int NOT NULL,
	responsavel_cpf bpchar(11) NOT NULL,
	id_departamento int NOT NULL,
	CONSTRAINT evento_pkey PRIMARY KEY (id_evento),
	CONSTRAINT fk_evento_departamento FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_evento_local FOREIGN KEY (id_local) REFERENCES "local"(id_local) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_evento_responsavel FOREIGN KEY (responsavel_cpf) REFERENCES pessoa(cpf) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: inscricao
CREATE TABLE inscricao (
    id_inscricao SERIAL PRIMARY KEY,
    id_pessoa CHAR(11) NOT NULL,
    id_evento BIGINT NOT NULL,
    status_inscricao VARCHAR(20) NOT NULL,
    status_checkin_evento BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_inscricao_pessoa FOREIGN KEY (id_pessoa)
        REFERENCES pessoa(cpf) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_inscricao_evento FOREIGN KEY (id_evento)
        REFERENCES evento(id_evento) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: certificado
CREATE TABLE inscricao (
	id_inscricao serial NOT NULL,
	id_pessoa bpchar(11) NOT NULL,
	id_evento int NOT NULL,
	status_inscricao varchar(20) NOT NULL,
	status_checkin_evento bool NOT NULL,
	CONSTRAINT inscricao_pkey PRIMARY KEY (id_inscricao),
	CONSTRAINT fk_inscricao_evento FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_inscricao_pessoa FOREIGN KEY (id_pessoa) REFERENCES pessoa(cpf) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: organizadores
CREATE TABLE organizadores (
	id_organizador serial NOT NULL,
	id_evento int NOT NULL,
	nome_pessoa varchar(45) NOT NULL,
	funcao_no_evento varchar(45) NOT NULL,
	telefone varchar(11) NOT NULL,
	email varchar(100) NOT NULL,
	cpf bpchar(11) NOT NULL,
	CONSTRAINT organizadores_email_key UNIQUE (email),
	CONSTRAINT organizadores_pkey PRIMARY KEY (id_organizador),
	CONSTRAINT fk_organizador_evento FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_organizador_pessoa FOREIGN KEY (cpf) REFERENCES pessoa(cpf) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: atividades
CREATE TABLE atividades (
	id_atividade serial NOT NULL,
	id_evento int NOT NULL,
	nome varchar(45) NOT NULL,
	tipo_atividade varchar(45) NOT NULL,
	descricao text NOT NULL,
	numero_vagas int NOT NULL,
	carga_horaria int NOT NULL,
	modalidade public."modalidade_enum" NOT NULL,
	data_hora_inicio timestamp NOT NULL,
	data_hora_fim timestamp NOT NULL,
	espec_local varchar(100) NOT NULL,
	CONSTRAINT atividades_pkey PRIMARY KEY (id_atividade),
	CONSTRAINT fk_atividade_evento FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: pesquisa_satisfacao
CREATE TABLE pesquisa_satisfacao (
	id_pesquisa serial NOT NULL,
	nome_pesquisa varchar(45) NOT NULL,
	CONSTRAINT pesquisa_satisfacao_pkey PRIMARY KEY (id_pesquisa)
);

-- Tabela: resposta
CREATE TABLE resposta (
	id_resposta serial NOT NULL,
	id_evento int NOT NULL,
	id_atividade int NULL,
	id_pesquisa int NOT NULL,
	nota float NOT NULL,
	comentario text NULL,
	CONSTRAINT resposta_pkey PRIMARY KEY (id_resposta),
	CONSTRAINT fk_resposta_atividade FOREIGN KEY (id_atividade) REFERENCES atividades(id_atividade) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_resposta_evento FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_resposta_pesquisa FOREIGN KEY (id_pesquisa) REFERENCES pesquisa_satisfacao(id_pesquisa) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE certificados_pendentes (
	id serial NOT NULL,
	id_inscricao int NOT NULL,
	processado bool DEFAULT false NULL,
	data_registro timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT certificados_pendentes_pkey PRIMARY KEY (id),
	CONSTRAINT fk_certificados_pendentes_inscricao FOREIGN KEY (id_inscricao) REFERENCES inscricao(id_inscricao) ON DELETE CASCADE ON UPDATE CASCADE
);