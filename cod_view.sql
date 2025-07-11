-- public.resumo_eventos_com_organizadores fonte

CREATE OR REPLACE VIEW public.resumo_eventos_com_organizadores
AS SELECT e.id_evento,
    e.nome AS nome_evento,
    e.status,
    e.modalidade,
    e.data_hora_inicio,
    e.data_hora_fim,
    d.nome AS departamento_responsavel,
    string_agg(((o.nome_pessoa::text || ' ('::text) || o.funcao_no_evento::text) || ')'::text, ', '::text) AS organizadores,
    count(DISTINCT i.id_inscricao) FILTER (WHERE i.status_inscricao::text = 'confirmado'::text) AS total_inscritos_confirmados,
    e.numero_de_vagas,
    e.numero_de_vagas - count(DISTINCT i.id_inscricao) FILTER (WHERE i.status_inscricao::text = 'confirmado'::text) AS vagas_restantes,
    count(DISTINCT a.id_atividade) AS total_atividades
   FROM evento e
     JOIN departamento d ON e.id_departamento = d.id_departamento
     LEFT JOIN organizadores o ON o.id_evento = e.id_evento
     LEFT JOIN inscricao i ON i.id_evento = e.id_evento
     LEFT JOIN atividades a ON a.id_evento = e.id_evento
  GROUP BY e.id_evento, e.nome, e.status, e.modalidade, e.data_hora_inicio, e.data_hora_fim, d.nome;