-- assistente_base.sql — schema `assistente` do núcleo remoto (plano "Núcleo centralizado no Supabase", Etapa 2).
--
-- Projeto Supabase: rag-compartilhado (wqoeoofhuhsdzpkdblbg). Divide o banco com o schema `rag`,
-- que NÃO é tocado aqui. Aplicado pelo conector (apply_migration, nome `assistente_base`), nunca por
-- `supabase db push` — ver PROGRESSO da Etapa 1, resposta 7.
--
-- Idempotente: pode rodar de novo sem erro e sem duplicar nada.
--
-- Cada linha pertence a um usuário do Auth (user_id, preenchido por auth.uid()). O papel
-- `authenticated` só lê e insere as próprias linhas; não há política de update/delete, e `anon`
-- não recebe nada.

create schema if not exists assistente;

-- Consumo: uma linha por chamada paga à API (espelha transcritor/consumo.jsonl).
-- Linhas antigas do .jsonl sem `id` recebem uuid5 determinístico no importador.
create table if not exists assistente.consumo (
    id            uuid primary key,
    user_id       uuid not null default auth.uid() references auth.users (id) on delete cascade,
    "timestamp"   timestamptz not null,
    modelo        text not null,
    custo_usd     numeric not null,
    tipo_usage    text not null,   -- 'tokens' | 'duration' | 'tokens_imagem' no histórico
    input_tokens  integer,         -- nulo quando tipo_usage = 'duration'
    output_tokens integer,
    total_tokens  integer,
    segundos      numeric,         -- só quando tipo_usage = 'duration'
    origem        text             -- 'importado-jsonl' na importação; demais valores nas etapas 3 e 4
);

-- Transcrições: o texto de cada chamada, ligado ao consumo pelo id (espelha transcritor/transcricoes.jsonl).
-- A FK existe porque, na leitura de 2026-09-30, todo id_consumo casava com um id de consumo (0 órfãos).
create table if not exists assistente.transcricoes (
    id          uuid primary key default gen_random_uuid(),
    id_consumo  uuid references assistente.consumo (id) on delete cascade,
    user_id     uuid not null default auth.uid() references auth.users (id) on delete cascade,
    "timestamp" timestamptz not null,
    modelo      text not null,
    texto       text not null
);

-- Índices das colunas usadas pelas políticas e pela FK.
create index if not exists consumo_user_id_idx         on assistente.consumo (user_id);
create index if not exists transcricoes_user_id_idx    on assistente.transcricoes (user_id);
create index if not exists transcricoes_id_consumo_idx on assistente.transcricoes (id_consumo);

-- RLS ligado nas duas tabelas.
alter table assistente.consumo      enable row level security;
alter table assistente.transcricoes enable row level security;

-- Políticas: só o dono lê e insere. `(select auth.uid())` é o mesmo que auth.uid(), avaliado uma vez
-- por consulta em vez de uma vez por linha (recomendação do advisor de desempenho do Supabase).
-- Nenhuma política de update/delete, de propósito.
do $$
begin
    if not exists (select 1 from pg_policies
                   where schemaname = 'assistente' and tablename = 'consumo' and policyname = 'consumo_select_dono') then
        create policy consumo_select_dono on assistente.consumo
            for select to authenticated using ((select auth.uid()) = user_id);
    end if;
    if not exists (select 1 from pg_policies
                   where schemaname = 'assistente' and tablename = 'consumo' and policyname = 'consumo_insert_dono') then
        create policy consumo_insert_dono on assistente.consumo
            for insert to authenticated with check ((select auth.uid()) = user_id);
    end if;
    if not exists (select 1 from pg_policies
                   where schemaname = 'assistente' and tablename = 'transcricoes' and policyname = 'transcricoes_select_dono') then
        create policy transcricoes_select_dono on assistente.transcricoes
            for select to authenticated using ((select auth.uid()) = user_id);
    end if;
    if not exists (select 1 from pg_policies
                   where schemaname = 'assistente' and tablename = 'transcricoes' and policyname = 'transcricoes_insert_dono') then
        create policy transcricoes_insert_dono on assistente.transcricoes
            for insert to authenticated with check ((select auth.uid()) = user_id);
    end if;
end
$$;

-- Permissões: nada para anon/public; authenticated só usa o schema e faz select/insert.
revoke all on schema assistente from public, anon;
revoke all on all tables in schema assistente from public, anon, authenticated;
grant usage on schema assistente to authenticated;
grant select, insert on assistente.consumo, assistente.transcricoes to authenticated;
