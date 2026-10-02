-- radar.painel_json() — versão 2 (2026-10-02)
-- Gera o dados.json que o Painel de Benchmark de IA lê: select radar.painel_json();
-- A versão 1 fica guardada em radar.painel_json_v1() para voltar atrás, se precisar.
--
-- Chaves da versão 1, mantidas: recursos, modelos (os acompanhados), analises, novidades, gasto.
-- Mudança: as ofertas grátis saem de "novidades" e vão para "gratis" (sem o filtro de 60 dias).
-- Chaves novas: versao, contagens, provedores (com canais, planos e capacidades), programas,
-- gratis, biblioteca (todos os modelos, com preços por unidade e notas), indicadores e
-- historico_precos (só modelos com mais de um preço registrado).

create or replace function radar.painel_json()
returns jsonb
language sql
stable
set search_path to ''
as $function$
select jsonb_build_object(
 'versao', 2,
 'gerado_em', now(),
 'contagens', jsonb_build_object(
   'provedores', (select count(*) from radar.provedores),
   'modelos', (select count(*) from radar.modelos where provedor_id is not null),
   'modelos_ativos', (select count(*) from radar.modelos where provedor_id is not null and status = 'ativo'),
   'precos', (select count(*) from radar.precos),
   'precos_unidade', (select count(*) from radar.precos_unidade),
   'notas', (select count(*) from radar.notas),
   'canais', (select count(*) from radar.canais),
   'planos', (select count(*) from radar.planos),
   'capacidades', (select count(*) from radar.capacidades),
   'programas', (select count(*) from radar.programas),
   'gratis', (select count(*) from radar.novidades where tipo = 'gratis'),
   'indicadores', (select count(*) from radar.indicadores)),

 'recursos', (select coalesce(jsonb_agg(to_jsonb(r) - 'atualizado_em' order by r.vence_em nulls last, r.reseta_em nulls last),'[]') from radar.recursos r),

 -- tabela curada (acompanhado = true), no formato da versão 1 e com alguns campos a mais
 'modelos', (select coalesce(jsonb_agg(jsonb_build_object(
     'id',m.id,'provedor',m.provedor,'provedor_id',m.provedor_id,'nome',m.nome,'tipo',m.tipo,'aberto',m.pesos_abertos,
     'lancado',m.lancado_em,'status',m.status,'contexto',m.contexto_tokens,
     'entrada',p.entrada_usd_mtok,'saida',p.saida_usd_mtok,'fonte',p.fonte_url,'preco_desde',p.vigente_desde,
     'notas',(select coalesce(jsonb_object_agg(x.benchmark, jsonb_build_object('v',x.valor,'em',x.medido_em,'fonte',x.fonte_url)),'{}')
              from (select distinct on (benchmark) * from radar.notas n where n.modelo_id=m.id order by benchmark, medido_em desc) x)
   ) order by m.provedor, m.nome),'[]')
   from radar.modelos m
   left join lateral (select * from radar.precos where modelo_id=m.id order by vigente_desde desc limit 1) p on true
   where m.acompanhado),

 'analises', (select coalesce(jsonb_agg(to_jsonb(a) - 'id' order by a.ciclo_em desc),'[]')
   from (select distinct on (modelo_id) * from radar.analises order by modelo_id, ciclo_em desc) a),

 'novidades', (select coalesce(jsonb_agg(to_jsonb(v) - 'id' - 'registrado_em' order by v.publicado_em desc nulls last),'[]') from radar.novidades v
   where v.tipo <> 'gratis' and v.registrado_em > now() - interval '60 days' and (v.valido_ate is null or v.valido_ate >= current_date)),

 'gasto', (select coalesce(jsonb_agg(to_jsonb(g) order by g.mes, g.custo_usd desc),'[]') from radar.gasto_por_modelo g),

 'provedores', (select coalesce(jsonb_agg(jsonb_build_object(
     'id',pv.id,'nome',pv.nome,'grupo',pv.grupo,'site',pv.site,'pais',pv.pais,'resumo',pv.resumo,'coletado_em',pv.coletado_em,
     'n_modelos',(select count(*) from radar.modelos m where m.provedor_id=pv.id),
     'canais',(select coalesce(jsonb_agg(jsonb_build_object('tipo',c.tipo,'nome',c.nome,'url',c.url,'handle',c.handle,'obs',c.observacao) order by c.tipo, c.nome),'[]')
               from radar.canais c where c.provedor_id=pv.id),
     'planos',(select coalesce(jsonb_agg(to_jsonb(pl) - 'id' - 'provedor_id' order by pl.preco_mensal_usd nulls last, pl.nome),'[]')
               from radar.planos pl where pl.provedor_id=pv.id),
     'capacidades',(select coalesce(jsonb_agg(to_jsonb(cp) - 'id' - 'provedor_id' order by cp.capacidade, cp.produto),'[]')
               from radar.capacidades cp where cp.provedor_id=pv.id)
   ) order by pv.grupo, pv.nome),'[]') from radar.provedores pv),

 -- programas: elegíveis primeiro, depois abertos/contínuos
 'programas', (select coalesce(jsonb_agg(to_jsonb(pg) - 'id' order by
     case pg.elegivel when 'sim' then 0 when 'talvez' then 1 else 2 end,
     case pg.status when 'aberto' then 0 when 'em_breve' then 1 when 'continuo' then 2 when 'desconhecido' then 3 else 4 end,
     pg.prazo nulls last, pg.valor_usd desc nulls last),'[]') from radar.programas pg),

 -- ofertas grátis: o provedor está em texto; provedor_id vem do casamento pelo nome
 'gratis', (select coalesce(jsonb_agg(jsonb_build_object(
     'provedor_id',pv.id,'provedor',v.provedor,'titulo',v.titulo,'resumo',v.resumo,'por_que_importa',v.por_que_importa,
     'url',v.url,'publicado_em',v.publicado_em,'valido_ate',v.valido_ate)
   order by v.valido_ate nulls last, v.provedor, v.titulo),'[]')
   from radar.novidades v left join radar.provedores pv on pv.nome = v.provedor
   where v.tipo = 'gratis' and (v.valido_ate is null or v.valido_ate >= current_date)),

 -- biblioteca completa (ignora as 8 linhas antigas sem provedor_id); chaves curtas para o arquivo não crescer
 -- p=provedor_id st=status ab=pesos abertos ctx=contexto lan=lançamento des=desativa_em
 -- e/s=entrada/saída US$/MTok f=fonte do preço ac=acompanhado u=preços por unidade n=notas
 'biblioteca', (select coalesce(jsonb_agg(jsonb_strip_nulls(jsonb_build_object(
     'id',m.id,'p',m.provedor_id,'nome',m.nome,'tipo',m.tipo,'st',m.status,'ab',m.pesos_abertos,'ctx',m.contexto_tokens,
     'lan',m.lancado_em,'des',m.desativa_em,'e',p.entrada_usd_mtok,'s',p.saida_usd_mtok,'f',p.fonte_url,
     'ac',case when m.acompanhado then true end,
     'u',(select jsonb_agg(jsonb_build_object('u',pu.unidade,'v',pu.valor_usd,'c',pu.condicao) order by pu.unidade, pu.valor_usd)
          from (select distinct on (unidade, condicao) * from radar.precos_unidade where modelo_id=m.id order by unidade, condicao, vigente_desde desc) pu),
     'n',(select jsonb_object_agg(x.benchmark, x.valor)
          from (select distinct on (benchmark) * from radar.notas n where n.modelo_id=m.id order by benchmark, medido_em desc) x)
   )) order by m.provedor_id, m.tipo, m.nome),'[]')
   from radar.modelos m
   left join lateral (select * from radar.precos where modelo_id=m.id order by vigente_desde desc limit 1) p on true
   where m.provedor_id is not null),

 'indicadores', (select coalesce(jsonb_agg(to_jsonb(i) - 'id' order by i.medido_em desc, i.nome),'[]') from radar.indicadores i),

 -- histórico: cada preço de modelo que já teve mais de um valor registrado
 'historico_precos', (select coalesce(jsonb_agg(jsonb_build_object('m',h.modelo_id,'d',h.vigente_desde,'e',h.entrada_usd_mtok,'s',h.saida_usd_mtok)
     order by h.modelo_id, h.vigente_desde),'[]')
   from radar.precos h where h.modelo_id in (select modelo_id from radar.precos group by modelo_id having count(*) > 1))
);
$function$;
