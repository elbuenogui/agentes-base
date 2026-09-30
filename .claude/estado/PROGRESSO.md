# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de **2026-09-30** (encerramento da Fase 2 e abertura do plano
> **Núcleo centralizado no Supabase**). As entradas da Fase 2 estão em
> `historico/PROGRESSO_fase2-desktop_2026-08-25_a_2026-09-21.md`, e as dos planos anteriores nos
> outros `historico/PROGRESSO_*.md`, todas sem edição.

*(Sem entradas ainda — a primeira nasce quando o Executor concluir a primeira tarefa deste plano.)*

## [2026-09-30 03:00 BRT] — Núcleo centralizado no Supabase, Etapa 1: Reconhecer o projeto Supabase RAG-COMPARTILHADO
Status: concluído (com duas perguntas parcialmente não verificáveis — ver 4 e 5)

### Feito

**Caminho de acesso.** Conector Supabase da conta (a CLI não está disponível neste ambiente). Só
chamadas de leitura: `list_projects`, `get_organization`, `get_project`, `list_migrations`,
`list_edge_functions`, `get_edge_function` (buscar), `list_extensions` e 12 `execute_sql`, todos
`SELECT`. Nenhum `supabase link`/`init` rodado; nada gravado em `.claude/tmp/`. Pastas locais lidas
com `cat`/`grep`/`find`/`git log`/`git diff --stat` (só leitura).

**Achado que muda a premissa da tarefa.** A tarefa diz que o RAG-COMPARTILHADO "já é usado pelo
assistente de vendas no WhatsApp". O que a evidência mostra:
- `list_projects` devolve **dois** projetos na mesma organização: `rag-compartilhado`
  (`wqoeoofhuhsdzpkdblbg`) e **`Assistente-vendas-whatsapp`** (`bpqjdrzrqhaxksdcofnj`, sa-east-1,
  criado em 2026-08-28). O assistente de vendas tem projeto Supabase próprio. **Não inspecionei esse
  segundo projeto** — fora do acesso autorizado para esta tarefa.
- O `README.md` do repositório RAG-COMPARTILHADO diz que o banco serve "a Mari (chatbot da
  UrbVerde), depois outros (feiras livres, etc.)". O dono do schema e das migrações do RAG é esse
  repositório, não o do assistente de vendas.
- A pasta `PROJETO-SECRETÁRIO-WPP` **não tem código**: só documentos (`DOCUMENTOS/`, `EVIDENCIAS/`,
  `ARTEFATOS/` com subpastas vazias, `.claude/painel.md`). Nenhum `supabase/`, `.sql`, `config.toml`,
  `.env*`, `package.json`, `.ts/.js/.py`; não é repositório git. As menções a Supabase nela são de
  planejamento (`decisoes-tecnicas.md:24`, `requisitos-formais.md:121`: "Supabase no plano gratuito —
  candidato/confirmado por preço").
- Mas o RAG já tem dados de um segundo cliente além da Mari: `rag.trechos` tem o valor de `projeto`
  `assistente-nova-forma` (ver pergunta 2) e `rag.buscas` tem origem `assistente-local`. Não verifiquei
  qual repositório alimenta esse rótulo — nenhuma das duas pastas montadas o contém.

**1. Projeto.**
- `project ref`: `wqoeoofhuhsdzpkdblbg`; nome `rag-compartilhado`; status `ACTIVE_HEALTHY`;
  Postgres 17.6.1.171; criado em 2026-09-29 19:15 UTC. (`get_project`)
- Região: `sa-east-1` (São Paulo). (`get_project`; confere com o README)
- Plano: **gratuito** — organização `SOFIA` (`fflxgmtdwgldionkeovt`), `plan: free`,
  `tier: tier_free`. (`get_organization`)

**2. Banco.**
- Schemas fora de `pg_*`/`information_schema` (consulta em `pg_namespace`): `auth`, `extensions`,
  `graphql`, `graphql_public`, `public`, `realtime`, `storage`, `supabase_migrations`, `vault` (todos
  padrão do Supabase) e **`rag`** (dono `postgres`) — o único não padrão.
- Tabelas do `rag` (contagem exata com `count(*)`):
  - `rag.trechos` — **1391** linhas: `projeto='mari'` 1235 trechos / 189 documentos;
    `projeto='assistente-nova-forma'` 156 trechos / 14 documentos; todos com modelo
    `openai/text-embedding-3-large@1536`.
  - `rag.buscas` — **34** linhas: `mari`/`mari-api` 21, `mari`/`calibracao` 9,
    `assistente-nova-forma`/`assistente-local` 4.
- Funções em `rag`/`public`: só `rag.buscar`. `public`: 0 tabelas, 0 funções.
  `storage.buckets` 0, `storage.objects` 0.
- Extensões instaladas: `vector` 0.8.2 (em `extensions`), `uuid-ossp`, `pgcrypto`,
  `pg_stat_statements`, `supabase_vault`, `plpgsql`. `pg_cron` e `pg_net` **não** instalados.
- **Colisão com `assistente`:** nenhuma. Busca por `ilike '%assistente%'` em schemas, tabelas/visões,
  funções e roles devolveu vazio. Único ponto de atenção é semântico, não técnico: o valor de dado
  `projeto='assistente-nova-forma'` dentro de `rag.trechos` — um schema `assistente` não colide com
  ele, mas o nome pode confundir quem ler o banco.

**3. Edge Functions** (`list_edge_functions`; `supabase/config.toml` do RAG-COMPARTILHADO):
- `buscar` — ACTIVE, versão 2, `verify_jwt: false`.
- `ingerir` — ACTIVE, versão 2, `verify_jwt: false`.
- As duas **dispensam** JWT de propósito (comentário do `config.toml`): autenticação própria pelo
  cabeçalho `x-rag-chave` comparado ao segredo `RAG_CHAVE_ACESSO`, em tempo constante e exigindo
  chave com ≥ 20 caracteres (`_shared/comum.ts`, função `autorizado`).
- Versão implantada × repositório: as duas foram implantadas em 2026-09-29 ~22:10 UTC; os três `.ts`
  locais têm mtime 22:09 UTC e estão **modificados e não commitados** (`git diff --stat`: 4 arquivos,
  +34/−22; HEAD `14ca5d1` é de 18:46 BRT). O código de `buscar` devolvido por `get_edge_function`
  tem o que a cópia de trabalho local tem e o commit não tem (`registrar`, `usarBanco` com `max: 1`).
  Ou seja: o que está no ar é a cópia de trabalho não commitada. O README ainda diz "versão 1".

**4. Auth.**
- `auth.users`: **0**. `auth.identities` agrupado por `provider`: **vazio** (nenhum provedor em uso).
- Signup público aberto/fechado e confirmação de e-mail: **não verificável pelo caminho disponível.**
  O conector não expõe a configuração de Auth do projeto (não há ferramenta de leitura dela), o
  `config.toml` local só tem as seções `[functions.*]` (sem `[auth]`), e nem o README nem as pastas
  do assistente de vendas falam disso. Só o painel (Authentication → Providers/Sign In) ou a
  Management API responde.

**5. Segredos das Edge Functions.**
- **Não verificável pelo conector** (não há ferramenta que liste segredos de Edge Functions).
- Evidência local (nomes, nunca valores): README do RAG-COMPARTILHADO declara `OPENAI_API_KEY` e
  `RAG_CHAVE_ACESSO`, e como opcionais `EMBED_FORNECEDOR`, `EMBED_BASE_URL`, `EMBED_MODELO`,
  `EMBED_API_KEY`. O código implantado (`_shared/comum.ts`) lê exatamente esses e também
  `SUPABASE_DB_URL` (padrão injetado pelo Supabase).
- Chave da OpenAI: pelo README e pelo código, o nome é **`OPENAI_API_KEY`** (com `EMBED_API_KEY`
  tendo precedência se existir). Indício indireto de que está definida: há 1391 trechos ingeridos e 34
  buscas registradas, e as duas funções só funcionam gerando embeddings. Não confirma o nome no
  projeto, só que alguma chave de embedding está lá.
- Vault do banco (`vault.secrets`): 0 segredos.

**6. Migrações.**
- Pasta `supabase/migrations/` só existe no RAG-COMPARTILHADO, com um arquivo:
  `20260929000001_rag_base.sql` (5006 bytes). O assistente de vendas não tem nenhuma.
- `supabase_migrations.schema_migrations` tem **1** registro: versão `20260929200132`, nome
  `rag_base`, 1 statement com 4974 caracteres; o campo `created_by` está preenchido com a conta que
  aplicou (valor omitido aqui).
- **O conteúdo bate, a versão não.** `md5` do SQL gravado no banco = `35e3db95…` = `md5` do arquivo
  local sem a quebra de linha final (conferido com python: 4974 caracteres, mesmo hash). Mas a versão
  no banco (`20260929200132` = 20:01:32 UTC, mesmo minuto do mtime do arquivo) é diferente da do nome
  do arquivo (`20260929000001`). Esse padrão é o de uma migração aplicada pelo `apply_migration` do
  conector/MCP, que carimba a hora da aplicação — inferência, não confirmado.
- Não parece feito à mão pelo painel: há registro na tabela de histórico e o conteúdo é idêntico ao
  arquivo versionado. Mas o histórico **já está dessincronizado** do repositório no número de versão:
  um `supabase db push` rodado do RAG-COMPARTILHADO veria `20260929000001` como pendente e
  `20260929200132` como só-remota, e pediria `migration repair`.

**7. Recomendação.**
Não usar `supabase db push` neste projeto a partir de repositório nenhum: a tabela de histórico é
uma só para todos, e cada repositório veria as migrações do outro como "só-remotas". Aplicar o
schema `assistente` pelo mesmo caminho que o RAG usou (migração avulsa via `apply_migration` ou SQL
idempotente com `create schema if not exists`), com nome de migração prefixado (`assistente_…`) e o
arquivo versionado neste repositório, sem tocar no schema `rag` nem no histórico existente.

### Critério de pronto
- [x] As sete respostas registradas no PROGRESSO, cada uma com a evidência. (4 e 5 com a parte de
      configuração marcada como não verificável, e o porquê.)
- [x] Nenhuma alteração no projeto Supabase (nenhum `create`, `alter`, `deploy`, `db push`,
      `secrets set`, `migration repair`). Só ferramentas de leitura e `SELECT`.
- [x] Nenhum segredo, chave, senha ou dado de usuário escrito no PROGRESSO ou no repositório. (Só
      nomes de segredos; o e-mail do `created_by` foi omitido; nenhum conteúdo de trecho ou pergunta.)
- [x] Nada criado fora de `.claude/tmp/` e do `PROGRESSO.md`. (Nada criado nem em `.claude/tmp/`.
      O `git status` já mostrava, antes desta tarefa, `PROXIMA_TAREFA.md`, `desktop/app.log`,
      `desktop/config.json` modificados e `desktop/imagens-geradas/` não rastreado — não são desta
      tarefa.)

### Novas demandas / riscos
- **Premissa do plano (D-36):** o RAG-COMPARTILHADO não é do assistente de vendas; ele tem projeto
  próprio (`Assistente-vendas-whatsapp`). Quem divide o banco hoje é a Mari e um cliente rotulado
  `assistente-nova-forma`. Vale o PM conferir se o "outro projeto" com que não se pode colidir é o
  certo.
- **Plano gratuito com dois projetos ativos na mesma organização.** O Supabase limita projetos
  gratuitos ativos por conta (pela política que conheço, 2 — não conferido hoje). Criar um terceiro
  para o núcleo não caberia; usar o RAG como casa do núcleo cabe.
- **Pausa por inatividade:** o README do RAG registra como pendente a consulta diária para o projeto
  não pausar após 7 dias sem atividade; `pg_cron` não está instalado.
- **Limite de conexões:** comentário em `_shared/comum.ts` registra que 60 conexões do Postgres do
  plano gratuito se esgotaram numa ingestão em lote em 29/09. Um núcleo novo no mesmo banco disputa
  essas vagas.
- **Código implantado não commitado** no RAG-COMPARTILHADO (versão 2 das duas funções = cópia de
  trabalho, commit ainda na versão 1). Risco para o dono daquele repositório, não para esta tarefa.
- **Configuração de Auth desconhecida** (signup, confirmação de e-mail): a Etapa que criar usuário
  precisa conferir no painel antes. Com signup aberto, qualquer um com a chave `anon` cria usuário.

### Ajuste no plano necessário?
Sim — (1) corrigir a premissa de quem mais usa o RAG-COMPARTILHADO (Mari + `assistente-nova-forma`,
não o assistente de vendas, que tem projeto Supabase próprio); (2) definir o caminho de aplicação do
schema `assistente` sem `db push` (ver resposta 7); (3) prever a leitura da configuração de Auth e dos
segredos pelo painel, que o conector não cobre.

## [2026-09-30 03:20 BRT] — Núcleo centralizado no Supabase, Etapa 2: Banco, usuário e histórico importado (Parte A)
Status: concluído (Parte A). Falta a Parte B, do usuário, e a Parte C, do PM.

### Feito
- **Passo 1 (leitura dos dados, 06:14 UTC).** Os arquivos crescem com o uso: `consumo.jsonl` 1863 linhas
  (1814 com `id`, 49 antigas sem `id`, todas de 18–19/08), `transcricoes.jsonl` 1803 — o PLANO contou
  1861/1801 antes; nenhuma linha vazia no meio nem inválida. Campos do consumo: `timestamp`, `modelo`,
  `custo_usd` (float), `tipo_usage` (`tokens` 1702, `duration` 130, `tokens_imagem` 31), `input/output/total_tokens`
  (int; nulos nas 130 `duration`), `segundos` (float; só nas `duration`), `id`. Transcrições: `id_consumo`,
  `timestamp`, `modelo`, `texto`. **Fuso:** todo `timestamp` é ISO com microssegundos e `+00:00` (UTC).
  **Órfãos de `id_consumo`: 0** (1803 únicos, todos casam) → **FK criada**. 11 consumos com `id` sem
  transcrição. Os ids são uuid4 **sem hífens** (`uuid.hex`); o importador normaliza. Arquivos em CRLF.
- `nucleo-remoto/banco/assistente_base.sql` — schema, `consumo` e `transcricoes`, 3 índices, RLS, 4 políticas
  (select/insert do dono, `authenticated`), grants. Aplicado por `apply_migration` `assistente_base`
  (versão `20260930061625`); `rag` e a migração `rag_base` intactos.
- `nucleo-remoto/banco/importar_historico.py` — login por senha no Auth, upsert `ignore-duplicates` em lotes
  de 500 sequenciais, uuid5 com namespace fixo, `--simular`. Chave publicável `sb_publishable_…` no arquivo.
- `nucleo-remoto/banco/importar_historico.cmd` (CRLF, ASCII) e `nucleo-remoto/README.md`.
- **Testes:** `list_tables` → 2 tabelas, RLS ligado, 0 linhas. Advisors de segurança: nenhum alerta em
  `assistente` (só o INFO antigo de `rag` sem política). Desempenho: 3 "unused index" INFO (tabela vazia).
  `--simular`: **1863 consumos (49 via uuid5), 1803 transcrições, 4+4 lotes, soma `custo_usd` =
  6,88732583333333353127** (igual à soma do passo 1). Servidor HTTP falso local (fora do repositório, já
  apagado): 2 rodadas → 1ª 1863/1803 novas, 2ª 0 novas (idempotente, ids idênticos); cabeçalhos
  `Accept/Content-Profile: assistente`, `Prefer` e lotes 500/500/500/363 conferidos; senha errada sai com
  mensagem. `SELECT` com `json_populate_recordset` confirmou a conversão de `"7.5…e-05"`, `timestamptz` e uuid.
- **Não testado:** login e gravação reais (este ambiente não alcança o Supabase); o `.cmd` no Windows.

### Parte B — o que falta o usuário fazer
1. **Authentication → Users → *Add user*** → *Create new user*: o seu e-mail e uma senha, com
   ***Auto Confirm User*** marcado.
2. **Authentication → *Sign In / Providers***: desligar ***Allow new users to sign up*** e salvar.
3. **Settings → *Data API* → *Exposed schemas***: acrescentar `assistente`, sem tirar os que já estão, e salvar.
4. Dar dois cliques em `nucleo-remoto\banco\importar_historico.cmd` e digitar e-mail e senha (a senha não
   aparece). No fim ele imprime lidas, enviadas, novas e a soma de `custo_usd`; pode rodar de novo sem duplicar.

### Critério de pronto
- [x] Migração aplicada; `list_tables` mostra as duas tabelas com RLS ligado; advisors de segurança
      sem alerta para o schema `assistente`.
- [x] `--simular` imprime 1861 consumos e 1801 transcrições (ou o número real, se o passo 1
      mostrar linha vazia ou inválida — e aí diga qual e por quê) e a soma de `custo_usd`.
      (Real: 1863 e 1803 — não por linha inválida, mas porque o transcritor gravou 2 chamadas depois da contagem do PLANO.)
- [x] Nenhuma senha, chave secreta ou texto de transcrição no repositório, no PROGRESSO ou em log.
      (Os `.jsonl` seguem no `.gitignore`; nenhum `texto` impresso em teste.)
- [x] Os quatro passos da Parte B escritos no PROGRESSO e no `nucleo-remoto/README.md`.

### Novas demandas / riscos
- **Parte C vai ver números maiores** que os daqui se o transcritor for usado até a importação — comparar com
  o que o próprio importador imprimir na hora, não com 1863/1803.
- **`service_role` não tem grant** no schema `assistente` (só `authenticated`). Se a Edge Function da Etapa 3
  usar `service_role` ou conexão direta com outro papel, vai precisar de grant próprio.
- **Linhas de imagem** (`gpt-image-1.5`, 31): `transcricoes.texto` guarda o *prompt*, não transcrição
  (`transcritor/backend/main.py:500`). Vai para o banco igual; quem ler `texto` precisa saber.
- A FK exige que o consumo chegue antes da transcrição; o importador segura as transcrições sem consumo
  lido (contagem "ficam para a próxima"). As etapas 3 e 4 precisam da mesma ordem.
- Políticas usam `(select auth.uid()) = user_id` em vez de `auth.uid() = user_id` (mesmo efeito, forma
  recomendada pelo advisor de desempenho). Não houve segunda migração.

### Ajuste no plano necessário?
Não.

## [2026-09-30 — Correção 1] — Núcleo centralizado no Supabase, Etapa 2: `.cmd` com Python do venv e log do importador
Status: concluído

### Feito
- `importar_historico.cmd` testa com `--version` e usa, nesta ordem, `..\..\transcritor\.venv\Scripts\python.exe`, `py -3`, `python`; diz qual usou e, se nenhum rodar, imprime erro claro antes do `pause` (CRLF, ASCII). `importar_historico.py` grava a saída da tela também em `importar_historico.log` (acréscimo, cabeçalho com data, modo e versão do Python; e-mail mascarado; erro inesperado vira mensagem + traceback no log). `.gitignore`: `nucleo-remoto/banco/*.log`.
- Teste: `--simular` = contagem independente no mesmo instante (1864 consumos, 49 sem id, 1804 transcrições, soma 6,88787583333333353127 — os arquivos cresceram com o uso). Servidor falso local com e-mail e senha de teste, 3 rodadas (ok, erro PGRST106 com e-mail na mensagem, exceção): log com 0 `@`, sem senha, sem token, 0 textos de transcrição. Log de teste apagado. Não testado: o `.cmd` no Windows.

### Critério de pronto
- [x] `.cmd` com a ordem venv → `py -3` → `python` e mensagem se nenhum rodar.
- [x] Log ao lado do script, sem e-mail, senha, token nem texto; erro com código e mensagem.
- [x] `nucleo-remoto/banco/*.log` no `.gitignore`.
- [x] `--simular` com os mesmos totais; log criado e sem `@`, senha de teste nem texto.

### Novas demandas / riscos
- O `pyvenv.cfg` do venv aponta para `C:\Users\Guilherme Bueno\AppData\Local\Programs\Python\Python313`; se esse Python não existir na máquina do usuário, o venv falha no `--version` e o `.cmd` passa para `py -3`.
- A causa real da falha ainda não é conhecida; o log da próxima execução deve mostrá-la.

### Ajuste no plano necessário?
Não.

## [2026-09-30 — Etapa 3] — Núcleo centralizado no Supabase, Etapa 3: Transcrever remoto (Parte A)
Status: concluído (Parte A). Falta a Parte B, do usuário, e a Parte C, do PM.

### Feito
- `nucleo-remoto/funcoes/transcrever/index.ts` — Operação 1 em Deno (`Deno.serve`), cliente Supabase com o JWT de quem chama e `db.schema = 'assistente'` (`SUPABASE_URL` + `SUPABASE_ANON_KEY` injetadas), consumo → transcrição, `origem = 'nucleo-remoto'`, custo igual a `_calcular_custo_usd`. Import `npm:@supabase/supabase-js@2` (o `jsr:` não baixa por trás do proxy daqui, então não daria para checar; os dois funcionam no Supabase).
- Implantada com `deploy_edge_function` `transcrever`, `verify_jwt: true`, **1 vez** (versão 1, ACTIVE). `get_edge_function` devolveu o conteúdo; gravado em arquivo e comparado: **idêntico** ao versionado (md5 `79134a90…`, 13250 bytes). `buscar`/`ingerir` intocadas (versão 2).
- `nucleo-remoto/testes/testar_transcrever.py` e `.cmd` (CRLF, ASCII, mesma escolha de Python do importador); `README.md` com a função e os dois passos; `.gitignore` com `nucleo-remoto/testes/*.log`.
- **`deno check`:** não havia `deno` aqui nem no contêiner; instalei Deno 2.9.6 no rascunho do contêiner (npm) → `deno check` sem erro.
- **Teste local da função (Deno + servidor falso de Auth/banco/OpenAI, prazo trocado para 3 s só na cópia de teste):** 18 casos conferidos — 200 json e NDJSON (3 delta + final), 422 diarize, 400 vazio, 413 com 26 MB, 422 sem `audio`/não multipart, 401 com a chave anônima, 405, 503 SEM_CHAVE nos dois modos, 502 FALHA_AUTENTICACAO e evento `erro` no streaming, 502 API_RECUSOU, 504 TEMPO_ESGOTADO e evento no streaming (3,0 s), falha do banco com resposta 200 mantida; `X-Nucleo-Contrato: 1` e nenhum `Access-Control-Allow-Origin` em todas; custo 0,0035 (1000/100 tokens, 4o) e 0,00175 (mini); consumo sempre antes da transcrição; log da função só com código e mensagem do banco.
- **Teste do script ponta a ponta** (mesma função no Deno + servidor falso): 6/6 casos passaram, contagens +2 em cada; senha errada sai com mensagem; log com 0 `@`, sem senha, token ou texto.
- **Não testado:** gateway real (`verify_jwt`), OpenAI real, RLS real, `.cmd` no Windows — é a Parte B.

### Divergências em relação ao núcleo local
- `gpt-4o-transcribe-diarize` → `422 MODELO_INVALIDO` (lista aceita: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`).
- Prazo: 120 s para a chamada inteira, 1 tentativa, sem prazo separado de conexão (local: 120 s de leitura × 3 tentativas do SDK, até ~6 min; conexão 5 s).
- `detail` de `SEM_CHAVE` e `FALHA_AUTENTICACAO` citam o segredo `OPENAI_API_KEY` das Edge Functions, não `transcritor/.env`.
- Sem CORS (local: `*`).
- Sem token → `401` do gateway do Supabase, no formato dele e **sem** `X-Nucleo-Contrato`.
- Novo `401 NAO_AUTENTICADO` (com cabeçalho): JWT que não é de usuário do Auth (ex.: a chave anônima legada, que passa no `verify_jwt`) — checado com `auth.getUser` antes de gastar chamada paga.
- Novo `422 REQUISICAO_INVALIDA` para corpo não multipart ou sem `audio` (local: 422 do FastAPI, sem `codigo`); novo `405 METODO_NAO_PERMITIDO` e `500 ERRO_INTERNO`, com `codigo`.
- `stream`: `true/1/yes/on` = verdadeiro, qualquer outro valor = falso (local: valor inválido dá 422 do FastAPI).
- Registro no banco em vez dos `.jsonl`: id uuid com hífens, `timestamp` com milissegundos (local: microssegundos), `origem = 'nucleo-remoto'`; sem o acumulado de sessão do processo local.
- `OPENAI_BASE_URL` opcional nos segredos, como o SDK local aceitava (usado só no teste local).

### Parte B — o que falta o usuário fazer
1. No painel do projeto: **Edge Functions → *Secrets***. Se já houver `OPENAI_API_KEY` (o RAG usa), não faça nada. Se não houver, crie com a sua chave da OpenAI. A chave não passa pelo chat.
2. Dois cliques em `nucleo-remoto\testes\testar_transcrever.cmd`, e-mail e senha. O resultado fica em `nucleo-remoto\testes\testar_transcrever.log`.

### Critério de pronto (da etapa, conferido na Parte C)
- [ ] Os seis casos do teste passam contra a função implantada. (Passaram contra a mesma função num servidor falso local; o real é a Parte B.)
- [ ] As linhas novas aparecem no banco ligadas ao usuário, consumo antes de transcrição. (Parte C.)
- [x] A chave da OpenAI mora só nos segredos do Supabase; nenhuma chave secreta no repositório. (Varredura em `nucleo-remoto/`: nenhuma.)
- [x] O código implantado é o mesmo de `nucleo-remoto/funcoes/transcrever/index.ts`. (`get_edge_function` × arquivo: idênticos.)

### Novas demandas / riscos
- **`verify_jwt` e o formato do JWT:** se o projeto assinar os tokens de usuário com as chaves assimétricas novas, o gateway pode recusar um token válido (Supabase recomenda `--no-verify-jwt` com as chaves novas). Sintoma: caso 2 com `401` sem `codigo NAO_AUTENTICADO`. Não verificável daqui.
- Existência de `OPENAI_API_KEY` nos segredos continua não verificável pelo conector (como na Etapa 1).
- O teste da Parte B deixa 2 linhas de teste com `origem = 'nucleo-remoto'` no histórico real do usuário (sem update/delete pela API).
- `npm:@supabase/supabase-js@2` sem versão fixa: cada implantação pega o 2.x mais novo.

### Ajuste no plano necessário?
Não.

## [2026-09-30 — Etapa 4] — Núcleo centralizado no Supabase, Etapa 4: Consumo remoto, e a imagem registrando no banco (Parte A)
Status: concluído (Parte A). Falta a Parte B, do usuário, e a Parte C, do PM.

### Feito
- `nucleo-remoto/funcoes/consumo/index.ts` — Operação 2 lida de `assistente.consumo`/`transcricoes` como o usuário (mesmo cliente e mesma checagem `auth.getUser` da `transcrever`), paginada de 1000 em 1000 ordenada por `id`. Implantada com `deploy_edge_function` `consumo`, `verify_jwt: true`, **1 vez** (versão 1, ACTIVE); `get_edge_function` gravado em arquivo e comparado: **idêntico** (md5 `0fdab967…`, 6492 bytes).
- `transcritor/backend/main.py` — só o registro do `/gerar-imagem`: novos `_token_bearer`, `_resumo_erro_remoto`, `_registrar_imagem_no_banco` e o parâmetro `request`; com `Authorization: Bearer`, grava consumo (`origem = 'nucleo-local-imagem'`, mesmo `_calcular_custo_usd`) e depois a transcrição (prompt) na API de dados, e não nos `.jsonl`; sem o cabeçalho (ou com outro formato), exatamente o caminho antigo. O diff só remove as 3 linhas do registro antigo, que agora ficam no `else`.
- **`httpx` → `httpx2`:** a venv do usuário tem o SDK OpenAI 3.1.0, que traz o `httpx2`, e **não** o `httpx` que a tarefa previa. O import é `httpx2`, com recaída para `httpx`, feito dentro da função de registro (nada muda na subida do núcleo). Sem dependência nova.
- `transcritor/.env.example` — `SUPABASE_URL` e `SUPABASE_CHAVE_PUBLICAVEL` com os valores públicos. O `.env` real não foi tocado.
- `nucleo-remoto/testes/testar_consumo_e_imagem.py` e `.cmd` (CRLF, ASCII, mesma escolha de Python); `README.md`. `nucleo_8001.log` cai no `testes/*.log` que já está no `.gitignore`.
- **Testes do `main.py`** (contêiner, SDK 3.1.0 + `httpx2` como na venv, OpenAI/Supabase falsos, `.jsonl` em cópia isolada): sem cabeçalho, o novo e o **original do HEAD** deram resposta idêntica e linhas `.jsonl` idênticas (fora `id`/`timestamp`), banco sem chamada; `Basic …` e `Bearer ` vazio foram para o `.jsonl`; com Bearer: `.jsonl` intacto, consumo → transcrição com o mesmo id, custo = o da resposta (0,012686); banco recusando (RLS) ou caindo: resposta 200 igual, log só com código/mensagem (ReadTimeout em 10 s); sem `SUPABASE_*` no ambiente: 200 e aviso no log; `/transcrever` com e sem Bearer seguiu no `.jsonl`; 422 de modelo inválido igual ao original. Nenhum prompt ou token nos logs.
- **Não há teste automatizado existente do `main.py`**: os de `.claude/tmp/` e `transcritor/teste_tempo_real.py` são do desktop e do modo ao vivo contra a API real, e não cobrem o `/gerar-imagem`. O comparativo A/B acima faz esse papel.
- **Teste da função** (Deno + PostgREST falso limitado a 1000 linhas, 2500 consumos): 2500/2500 lidos, soma igual, `texto` casado, `por_dia` em São Paulo (linha de 02:30 UTC de 30/09 contou em 29/09), `sessao` = hoje, ordem por `timestamp`; 401 sem token e com a chave anônima, 405 no POST, 502 FALHA_BANCO; `X-Nucleo-Contrato: 1` em todas e nenhum CORS. `deno check` sem erro.
- **Teste do script ponta a ponta** (função no Deno, núcleo novo subindo na 8001, Supabase/OpenAI falsos): 5/5 com o mini aceito, e 5/5 com a OpenAI recusando o mini (pergunta de novo e usa o `gpt-image-1.5`); núcleo que não sobe dá FALHOU no 3, PULADO no 4 e encerra no 5; logs sem `@`, senha, token nem prompt.
- **Não testado:** a função e o núcleo contra o Supabase e a OpenAI reais, e o `.cmd` no Windows — é a Parte B.

### Divergências do `/consumo` remoto em relação ao local
- `sessao` = acumulado do **dia corrente em America/Sao_Paulo** (local: desde que o processo subiu).
- `por_dia` agrupado pela **data em America/Sao_Paulo** (local: os 10 primeiros caracteres do timestamp, ou seja, **UTC**).
- `id` em uuid com hífens (local: `uuid.hex` sem hífens; os 49 antigos sem id eram `null` no local e agora têm o uuid5 da importação).
- `timestamp` no formato do Postgres (`…+00:00`, e milissegundos nas linhas novas da `transcrever`); local: o texto gravado no `.jsonl`.
- Erros novos com `codigo`: `401 NAO_AUTENTICADO`, `405 METODO_NAO_PERMITIDO`, `502 FALHA_BANCO`, `500 ERRO_INTERNO` (local: nunca erra; arquivo ausente dá listas vazias). Sem token → `401` do gateway, sem `X-Nucleo-Contrato`.
- Sem CORS (local: `*`).
- Só as linhas do usuário logado (RLS); o local mostra tudo que está no arquivo.

### Parte B — o que falta o usuário fazer
1. Dois cliques em `nucleo-remoto\testes\testar_consumo_e_imagem.cmd`, e-mail, senha, e Enter quando ele mostrar o custo da imagem (se a OpenAI recusar o `gpt-image-1-mini`, ele pergunta de novo antes de tentar o `gpt-image-1.5`).

### Critério de pronto (da etapa, conferido na Parte C)
- [ ] Os cinco passos do teste passam. (5/5 contra serviços falsos; o real é a Parte B.)
- [ ] `GET /consumo` remoto devolve o histórico importado mais as linhas novas, na forma do contrato. (Parte B/C.)
- [ ] A imagem gerada com token fica no banco (`nucleo-local-imagem`) e não nos `.jsonl`. (Parte B/C.)
- [x] Sem token, `/gerar-imagem` local continua exatamente como antes. (A/B contra o original do HEAD: resposta e `.jsonl` idênticos.)
- [x] Código implantado igual ao versionado; nenhuma chave secreta no repositório.

### Novas demandas / riscos
- **`.env` real sem as duas variáveis:** com o token e sem `SUPABASE_URL`/`SUPABASE_CHAVE_PUBLICAVEL` no `.env`, a imagem **não é registrada em lugar nenhum** (só um aviso no log). O teste injeta as duas no núcleo da 8001; a Etapa 5 (desktop repassando o token) precisa delas no `.env` do usuário antes.
- Com o banco fora do ar, a resposta da imagem atrasa até 10 s (prazo do registro), e o registro se perde (sem recaída para o `.jsonl`, como pede a tarefa).
- `sessao` do `/consumo` local não conta as imagens registradas no banco (o registro remoto não passa por `_consumo_sessao`).
- `gpt-image-1-mini` nunca foi usado neste núcleo; é possível que a OpenAI recuse o `input_fidelity="high"` com ele — o teste cobre isso.
- A Parte B deixa 1 linha `nucleo-local-imagem` de teste no histórico real.

### Ajuste no plano necessário?
Não — mas a Etapa 5 deve prever acrescentar `SUPABASE_URL` e `SUPABASE_CHAVE_PUBLICAVEL` ao `transcritor/.env` do usuário.

## [2026-09-30 — Etapa 5] — Núcleo centralizado no Supabase, Etapa 5: Desktop no remoto, com login (Parte A)
Status: concluído (Parte A). Falta a Parte B, do usuário, e a Parte C, do PM.

### Feito
- `desktop/app.py`:
  - Config: padrões novos `url_nucleo` (remoto), `url_nucleo_imagem`, `supabase_url` e `supabase_chave_publicavel`, mais `migrar_config()` chamada em `carregar_config()`.
  - Sessão: classe `Sessao` (login, renovação e arquivo de sessão), `chamar_com_sessao()` (põe o cabeçalho; num 401, renova uma vez e repete), `TrabalhoLogin` e o sobreposto `PainelLogin`.
  - Janela: "Sair da conta" no menu ⋮, "Conta" em Configurações e a fila `_pendentes_login` para reenvio.
  - A imagem passou a ir para `url_nucleo_imagem`; o timeout do consumo subiu de 10 para 30 s.
  - O login na abertura é pedido em `main()`. Nada da janela mudou (D-32); o painel é um `OverlayModal` como Configurações.
- `desktop/config.json` migrado pela mesma regra: atalho, dispositivo, modelos e pasta foram preservados e `url_nucleo_imagem` ficou com `http://127.0.0.1:8000`. O `app.py` novo abre esse arquivo sem migrar de novo (conferido byte a byte).
- `transcritor/.env`: as duas variáveis faltavam (conferido com `grep -q`). Acrescentei 2 linhas com `>>`; a linha que já existia continua idêntica (conferido por md5 do prefixo) e nenhum conteúdo foi lido nem impresso.
- `desktop/reiniciar_transcritor.cmd` (novo, CRLF, só ASCII): PowerShell em `-EncodedCommand`, com o texto legível no README, conferido idêntico ao embutido. Encerra o dono da porta 8000 e o python rodando `app.py` sem caminho ou `desktop\app.py`, espera a porta liberar por até 15 s e chama o `abrir_transcritor.vbs`.
- `desktop/testes_sessao.py` (novo), `desktop/testes_janela_compacta.py` (só a lista esperada do menu, que ganhou "Sair da conta" — a contagem de verificações não mudou), `desktop/README.md` e `.gitignore` (`sessao.json` como proteção extra).
- **Testes** (contêiner, PySide6 6.11.2 offscreen, sobre os arquivos exatos da máquina, conferidos por md5):
  - **Suíte antiga: 231 verificações passaram, 0 falharam** — a mesma contagem da linha de base rodada antes com o `app.py` antigo.
  - **Suíte nova: 84 verificações passaram, 0 falharam** (~3 s), com Auth, núcleo remoto e núcleo local falsos:
    - migração preservando campos, gravada com `\n` e idempotente;
    - senha nunca no arquivo; sessão relida na abertura seguinte;
    - renovação quando faltam menos de 120 s; renovação por 401 (uma renovação, uma repetição, streaming incluso);
    - renovação recusada pede login sem apagar o áudio nem tocar a caixa, e o áudio é reenviado sozinho depois do login;
    - Consumo recarrega depois do login;
    - cabeçalho presente em transcrever, consumo e gerar-imagem;
    - `url_nucleo` local funciona sem login e sem cabeçalho;
    - log sem token, senha, e-mail nem chave.
  - As duas suítes deixam o `config.json` intacto.
  - A suíte nova acusa 3 mutações do `app.py`: sem cabeçalho (16 falhas), sem repetição após 401 (2) e apagando o áudio na sessão expirada (5).
  - O painel de login foi conferido por captura offscreen, lado a lado com Configurações.
- **Não testado:** Windows real — o login contra o Auth real, o foco do teclado no campo (a janela é `WA_ShowWithoutActivating`; chamo `activateWindow()`, mas o Windows pode negar) e a aparência nativa. O `.cmd` não foi executado. O núcleo e o app não foram reiniciados (é a Parte B).

### Critério de pronto (da etapa)
- [ ] Login uma vez; o ditado real cai no banco; a sessão se renova sozinha entre usos. (Parte B/C; comportamento coberto pelos testes com servidores falsos.)
- [ ] Uma imagem gerada pelo app aparece no painel de consumo (e no banco). (Parte B/C.)
- [x] Nenhuma credencial ou sessão no git; nada sensível no `app.log`. (Sessão em `%APPDATA%`; `sessao.json` no `.gitignore` como proteção; o `.env` segue ignorado; teste S8.)
- [x] `url_nucleo` = `http://127.0.0.1:8000` continua funcionando como saída de emergência. (Teste S5.)
- [x] Suíte headless antiga e nova passando. (231 + 84.)

### Parte B — o que falta o usuário fazer
1. Dois cliques em `desktop\reiniciar_transcritor.cmd`: o núcleo local pega o `main.py` novo e o app abre já no remoto.
2. Entrar com e-mail e senha quando o app pedir.
3. Ditar uma frase qualquer, gerar uma imagem pelo app e abrir o painel de Consumo.
4. Dois cliques em `nucleo-remoto\banco\importar_historico.cmd`, para trazer ao banco o que foi ditado pelo núcleo local depois da importação (não duplica).

### Novas demandas / riscos
- **Uso diário depende do Supabase:** com o Auth ou as funções fora do ar, o ditado falha (a mensagem é a de sem conexão). A saída é pôr `url_nucleo` em `http://127.0.0.1:8000` no `config.json` e reiniciar.
- **Critério de encerramento do `.cmd`:** qualquer python rodando um `app.py` **sem caminho** também é fechado (mesmo critério do `.vbs`).
- **Latência:** o ditado passa a ter a ida ao Supabase (e o arranque a frio da função) além da OpenAI. Não foi medido.
- **Onde o `.jsonl` continua crescendo:** a interface web (`index.html`) e qualquer uso da porta 8000 sem token ainda gravam nos `.jsonl`.
- **Sessão em texto puro:** o JSON em `%APPDATA%` não é cifrado (como a maioria dos apps); um arquivo ilegível só faz pedir login.
- **App antigo ainda aberto:** até o reinício, o app em execução segue com o código antigo. Se ele gravar o `config.json` antes disso, a migração roda de novo na abertura, com o mesmo resultado.

### Ajuste no plano necessário?
Não.

## [2026-09-30 — Etapa 6] — Núcleo centralizado no Supabase, Etapa 6: Contrato novo do núcleo
Status: concluído

### Feito
- `spec/contrato/NUCLEO.md` passou de 419 para 715 linhas; só acrescentei, nada apaguei. O que entrou:
  - no topo, um quadro "Contrato 2" com a legenda das marcas: **[medido]** (serviço real, com a fonte), **[código]**, **[código + teste local]** e **[documentação]**;
  - "Onde o núcleo escuta" com a tabela remoto × local por operação; o texto antigo ficou como "Histórico";
  - a seção nova "Autenticação": entrar, renovar, cabeçalhos exigidos, as duas formas de `401` e a falta de CORS;
  - em "Versionamento", o parágrafo do contrato 2;
  - as seções "Operação 1 no núcleo remoto" e, na Operação 2, "No núcleo remoto" — cada uma com o que é igual ao local, o que foi medido e a tabela de divergências marcada;
  - na Operação 3, "Com o token do usuário";
  - a seção nova "Registro de consumo";
  - notas datadas nas partes que só valem para o local: L5, L7, modo ao vivo e o parágrafo de "tudo medido em 2026-08-23".
- **Passo 3 — subiu para `2` no remoto.** `desktop/app.py` e `transcritor/frontend/index.html` não leem cabeçalho de resposta nenhum (busca por `X-Nucleo`, `headers.get`, `getResponseHeader`). Mudei só a constante `VERSAO_CONTRATO_NUCLEO` nas duas `index.ts`, passei `deno check` e implantei `transcrever` e `consumo` uma vez cada. O `get_edge_function` das duas, gravado em arquivo, é **idêntico** ao versionado: md5 `30ad20ba…` (transcrever) e `44ad7e61…` (consumo). O local fica em `1`.
- `spec/BACKLOG.md`: `B-08` e `B-09` marcados como resolvidos, com ponteiro para `D-36` e para o contrato. Nenhum outro item mudou.
- Nenhuma requisição nova à OpenAI nem ao banco. A evidência medida vem dos `.log` de `nucleo-remoto/testes/` e do `desktop/app.log` (`sessao: login ok` às 14:30 e `sessao: renovada` às 15:39).

### Critério de pronto
- [x] Um cliente novo, lendo só o `NUCLEO.md`, sabe: a URL de cada operação, como fazer login e renovar, os cabeçalhos exigidos, os erros possíveis com seus `codigo`, e onde o consumo fica.
- [x] Cada afirmação sobre o remoto está marcada como medida (com o log) ou lida no código.
- [x] A decisão do passo 3 está registrada; se subiu, o implantado é igual ao versionado.
- [x] Nenhuma chave secreta, e-mail ou texto de transcrição no contrato. (Só a URL e a chave publicável; os exemplos de texto que já existiam são do áudio de teste.)

### Novas demandas / riscos
- **Os dois scripts de teste do remoto conferem `X-Nucleo-Contrato == "1"`:** `testar_transcrever.py` (caso 2) e `testar_consumo_e_imagem.py` (passo 2). Se forem rodados de novo, esses casos vão **falhar** por causa do `2`. Não são clientes e não estavam na lista de arquivos, então não mexi. Ajuste de uma linha em cada, para o PM decidir.
- **O `2` ainda não foi visto numa resposta real:** está no código implantado, conferido com `get_edge_function`, mas os testes reais rodaram antes da troca.
- **As duas funções pularam da versão 1 para a 4:** as versões 2 e 3 foram implantadas por outra sessão entre as etapas. O repositório batia com a versão 1 que eu implantei, então o deploy de agora substituiu o que quer que 2 e 3 tivessem. Se alguém implantou código diferente sem versionar, ele se perdeu. Vale o PM confirmar quem fez.
- **Não medido contra o serviço real** (só código e teste local; o contrato diz isso item a item): `NAO_AUTENTICADO`, o `401` do gateway com JWT expirado, a falta de CORS, `TEMPO_ESGOTADO`, `FALHA_BANCO` e os demais erros das funções.

### Ajuste no plano necessário?
Não.

## [2026-09-30 — Etapa 6, correção] — Núcleo centralizado no Supabase, Etapa 6: testes remotos esperam o contrato 2
Status: concluído

### Feito
- `nucleo-remoto/testes/testar_transcrever.py`: o caso 2 espera `X-Nucleo-Contrato` = `"2"` (a comparação e a linha do caso no docstring). `testar_consumo_e_imagem.py`: o passo 2 (`/consumo` remoto) espera `"2"`; o passo 3 (núcleo local, porta 8001) só imprime o valor, não compara, e ficou como estava. Checagem sem requisição paga: as duas funções v2 no Deno contra serviços falsos deram 6/6 e 5/5; o remoto respondeu `2` e o local `1`.
- Versões 2 e 3 das funções (nota do PM): `buscar` e `ingerir` também saltaram de v2 para v4 com o mesmo `ezbr_sha256` e o mesmo `updated_at` — o número subiu sem mudança de código, provavelmente por mudança de configuração do projeto. Nenhum código de outra sessão se perdeu.

### Critério de pronto
- [x] Os dois scripts esperam `"2"` só nas respostas do remoto.

### Novas demandas / riscos
- Nenhuma.

### Ajuste no plano necessário?
Não.
