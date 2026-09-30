-- servicos_base.sql — schema `servicos` do núcleo remoto (plano do serviço de transcrição para a Mari, D-37, Etapa 1).
--
-- Projeto Supabase: rag-compartilhado (wqoeoofhuhsdzpkdblbg). Divide o banco com os schemas `rag` e
-- `assistente`, que NÃO são tocados aqui. Aplicado pelo conector (apply_migration, nome `servicos_base`),
-- nunca por `supabase db push`.
--
-- Idempotente: pode rodar de novo sem erro e sem duplicar nada.
--
-- O serviço de transcrição para projetos clientes registra só consumo, por projeto, sem texto: nenhuma
-- coluna guarda texto livre (as três colunas `text` têm `check`). Quem lê e grava é só o `service_role`
-- (a Edge Function da Etapa 2); `anon` e `authenticated` não recebem nada, e o schema NÃO é exposto na
-- API de dados.

create schema if not exists servicos;

-- Uso: uma linha por chamada ao serviço, paga ou recusada.
create table if not exists servicos.transcricao_uso (
    id            uuid primary key default gen_random_uuid(),
    projeto       text not null,
    "timestamp"   timestamptz not null default now(),
    modelo        text,
    custo_usd     numeric not null default 0,
    input_tokens  integer,
    output_tokens integer,
    total_tokens  integer,
    bytes_audio   integer,
    latencia_ms   integer,
    codigo        text,            -- null = sucesso; senão o `codigo` do erro, inclusive recusa por limite
    -- Nenhum texto livre: as três colunas `text` só aceitam identificadores.
    constraint transcricao_uso_projeto_check check (projeto ~ '^[a-z0-9][a-z0-9_-]{0,62}$'),  -- mesma regra de projetoValido do RAG
    constraint transcricao_uso_modelo_check  check (modelo  ~ '^[a-z0-9.-]{1,64}$'),
    constraint transcricao_uso_codigo_check  check (codigo  ~ '^[A-Z_]{1,40}$')
);

create index if not exists transcricao_uso_projeto_timestamp_idx
    on servicos.transcricao_uso (projeto, "timestamp");

-- Gasto do projeto no dia corrente de São Paulo (0 quando não há linha).
create or replace function servicos.gasto_do_dia(p_projeto text)
returns numeric
language sql
stable
security invoker
set search_path = ''
as $$
    select coalesce(sum(u.custo_usd), 0)
    from servicos.transcricao_uso u
    where u.projeto = p_projeto
      and u."timestamp" >= (date_trunc('day', now() at time zone 'America/Sao_Paulo') at time zone 'America/Sao_Paulo')
      and u."timestamp" <  ((date_trunc('day', now() at time zone 'America/Sao_Paulo') + interval '1 day') at time zone 'America/Sao_Paulo');
$$;

-- RLS ligado e nenhuma política, de propósito: só o `service_role` (que ignora RLS) chega na tabela.
alter table servicos.transcricao_uso enable row level security;

-- Permissões: nada para public/anon/authenticated; `service_role` usa o schema, faz select/insert e
-- executa a função. Ninguém além do dono faz update/delete (o revoke inclui o `service_role` para
-- limpar qualquer privilégio padrão antes do grant).
revoke all on schema servicos from public, anon, authenticated;
revoke all on table servicos.transcricao_uso from public, anon, authenticated, service_role;
revoke all on function servicos.gasto_do_dia(text) from public, anon, authenticated, service_role;
grant usage on schema servicos to service_role;
grant select, insert on table servicos.transcricao_uso to service_role;
grant execute on function servicos.gasto_do_dia(text) to service_role;
