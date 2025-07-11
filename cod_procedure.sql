-- DROP PROCEDURE public.tentar_inscrever_usuario(int4, text);

CREATE OR REPLACE PROCEDURE public.tentar_inscrever_usuario(IN p_id_evento integer, IN p_cpf text)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    vagas_total INTEGER;
    vagas_ocupadas INTEGER;
    status_evento TEXT;
BEGIN
    -- Verificar se a pessoa com esse CPF existe
    IF NOT EXISTS (
        SELECT 1 FROM pessoa WHERE cpf = p_cpf
    ) THEN
        RAISE EXCEPTION 'Pessoa com CPF % não encontrada.', p_cpf;
    END IF;

    -- Verificar se já está inscrita no evento (e ainda não cancelou)
    IF EXISTS (
        SELECT 1 FROM inscricao
        WHERE id_evento = p_id_evento
          AND id_pessoa = p_cpf
          AND status_inscricao != 'cancelado'
    ) THEN
        RAISE EXCEPTION 'Pessoa já está inscrita neste evento.';
    END IF;

    -- Buscar número de vagas e status do evento
    SELECT numero_de_vagas, status
    INTO vagas_total, status_evento
    FROM evento
    WHERE id_evento = p_id_evento;

    IF vagas_total IS NULL THEN
        RAISE EXCEPTION 'Evento não encontrado ou sem número de vagas definido.';
    END IF;

    -- Verificar se o evento está com status 'ativo'
    IF LOWER(status_evento) != 'ativo' THEN
        RAISE EXCEPTION 'Inscrições só são permitidas em eventos com status ATIVO. Status atual: %', status_evento;
    END IF;

    -- Contar número de vagas ocupadas com inscrição confirmada
    SELECT COUNT(*) INTO vagas_ocupadas
    FROM inscricao
    WHERE id_evento = p_id_evento
      AND status_inscricao = 'confirmado';

    IF vagas_ocupadas >= vagas_total THEN
        RAISE EXCEPTION 'Não há mais vagas disponíveis para este evento.';
    END IF;

    -- Inserir nova inscrição como confirmada
    INSERT INTO inscricao (
        id_evento,
        id_pessoa,
        status_inscricao,
        status_checkin_evento
    )
    VALUES (
        p_id_evento,
        p_cpf,
        'confirmado',
        FALSE
    );
END;
$procedure$
;
