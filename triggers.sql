create trigger trg_gerar_certificados_evento after
update
    on
    public.evento for each row
    when (((old.status)::text is distinct
from
    (new.status)::text)) execute function gerar_certificados_para_evento_concluido()



create trigger trg_checkin_certificado after
update
    on
    public.inscricao for each row
    when ((old.status_checkin_evento is distinct
from
    new.status_checkin_evento)) execute function registrar_certificado_pendente()


CREATE OR REPLACE FUNCTION public.gerar_certificados_para_evento_concluido()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Verifica se o status mudou para 'concluido'
    IF NEW.status = 'concluido' AND OLD.status IS DISTINCT FROM 'concluido' THEN
        -- Insere certificados pendentes para todas as inscrições confirmadas com check-in
        INSERT INTO certificados_pendentes (id_inscricao)
        SELECT i.id_inscricao
        FROM inscricao i
        WHERE i.id_evento = NEW.id_evento
          AND i.status_inscricao = 'confirmado'
          AND i.status_checkin_evento = TRUE
          AND NOT EXISTS (
              SELECT 1 FROM certificados_pendentes cp
              WHERE cp.id_inscricao = i.id_inscricao AND cp.processado = FALSE
          );
    END IF;

    RETURN NEW;
END;
$function$
;

-- DROP FUNCTION public.registrar_certificado_pendente();

CREATE OR REPLACE FUNCTION public.registrar_certificado_pendente()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    evento_status TEXT;
BEGIN
    -- Verifica se o check-in foi atualizado para TRUE e o status da inscrição é 'confirmado'
    IF NEW.status_checkin_evento = TRUE 
       AND OLD.status_checkin_evento IS DISTINCT FROM TRUE 
       AND NEW.status_inscricao = 'confirmado' THEN

        -- Buscar o status do evento relacionado
        SELECT status INTO evento_status
        FROM evento
        WHERE id_evento = NEW.id_evento;

        -- Verifica se o evento está concluído
        IF evento_status = 'concluido' THEN
            -- Verifica se já está pendente
            IF NOT EXISTS (
                SELECT 1 FROM certificados_pendentes
                WHERE id_inscricao = NEW.id_inscricao AND processado = FALSE
            ) THEN
                INSERT INTO certificados_pendentes (id_inscricao) VALUES (NEW.id_inscricao);
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$function$
;
