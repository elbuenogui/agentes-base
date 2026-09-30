# PLANO — Núcleo centralizado no Supabase

> Plano de **fase**, aberto em **2026-09-30** e aprovado pelo usuário no mesmo dia. A visão e o mapa
> das fases estão em `spec/VISAO.md`; o método, em `.claude/CEREBRO.md`. Virada de plano: a Fase 2
> encerrou pelo critério de uso em regime (plano em `historico/PLANO_2026-09-30_fase2-encerrada.md`,
> progresso em `historico/PROGRESSO_fase2-desktop_2026-08-25_a_2026-09-21.md`). A decisão que abre
> este plano é a `D-36`, que reabre a `D-05`.

## Objetivo

Um núcleo só, remoto, no Supabase: a chave da OpenAI e o histórico ficam num lugar, e qualquer
cliente novo (Android, relógio) só lê o contrato e chama a API — sem replicar o backend em cada
cliente e sem chave dentro do aparelho.

## Critério de conclusão do plano

**O usuário dita pelo núcleo remoto no dia a dia, e nenhuma transcrição nova vai para os
`.jsonl`.**

## Escopo

- **Dentro**: `POST /transcrever` (lote e streaming) e `GET /consumo` como Edge Functions no projeto
  **RAG-COMPARTILHADO**; um schema próprio no Postgres, com o histórico dos dois `.jsonl`
  importado; **login pelo Supabase Auth** desde já (um usuário, e-mail e senha), com as linhas
  ligadas ao usuário; o consumo da geração de imagem registrado no banco; o app de desktop
  apontando para o remoto; o contrato `NUCLEO.md` em versão nova; o CORS fechado (`B-08`, gatilho
  disparado) e os `.jsonl` trocados por banco (`B-09`).
- **Fora (explícito)**: a geração de imagem remota — **fica no núcleo local**, decisão do usuário
  em 2026-09-30; a interface web; Android e relógio (F3, F4); o modelo `gpt-4o-transcribe-diarize`
  (~43 s para 72 s de áudio medidos na F1 — num áudio de 5 min estoura os 150 s de tempo total da
  Edge Function no plano gratuito); a medição local × remoto — **dispensada pelo usuário**; o modo
  ao vivo, morto (`D-33`).

## Fatos que moldam o plano

Conferidos na documentação do Supabase em 2026-09-30 — conferir de novo antes de decisão que
dependa deles:

- Edge Functions rodam **só TypeScript/Deno**. O `transcritor/backend/main.py` é reescrito, não
  transplantado; a especificação da reescrita é o contrato (`spec/contrato/NUCLEO.md`, `D-07`).
- 150 s de tempo total por requisição (plano gratuito), 256 MB de memória, 2 s de CPU (sem contar
  espera de rede).
- Projeto gratuito pausa depois de 1 semana sem uso. O RAG-COMPARTILHADO é dividido com outro uso —
  cota, segredos e usuários do Auth também são.

## Etapas

1. **[Reconhecer o RAG-COMPARTILHADO]** — critério de pronto: registrado no PROGRESSO, sem alterar
   nada no projeto: plano e região; schemas e funções que já existem; se o Auth já tem usuários e
   provedores configurados (o Auth é por projeto — o usuário deste núcleo vai conviver com os do
   outro uso); e **como as migrações do outro uso são aplicadas** (de qual repositório, por qual
   ferramenta). Esta etapa vem primeiro porque dois repositórios aplicando migração no mesmo projeto
   podem colidir no histórico de migrações — a etapa 2 escolhe o jeito de aplicar a partir daqui.

2. **[Banco, usuário e histórico importado]** — critério de pronto: schema `assistente` criado,
   **não exposto** na API pública de dados; o usuário do núcleo existe no Auth; tabelas de consumo e
   de transcrições com as linhas ligadas a esse usuário e acesso restrito a ele; a contagem de
   linhas e a soma de `custo_usd` no banco batem com `transcritor/consumo.jsonl` e
   `transcritor/transcricoes.jsonl`, conferidas por consulta.

3. **[Transcrever remoto]** — critério de pronto: um áudio real transcrito pela Edge Function nos
   dois modos (lote e streaming), com a resposta na forma do contrato; a linha nova aparece no banco
   ligada ao usuário; requisição sem sessão válida recebe 401; os erros saem com os mesmos `codigo`
   do contrato; a chave da OpenAI mora **só** nos segredos do Supabase.

4. **[Consumo remoto, e a imagem registrando no banco]** — critério de pronto: `GET /consumo`
   remoto devolve o histórico importado mais as linhas novas, na forma do contrato; uma imagem
   gerada pelo núcleo local tem o consumo registrado no banco pela API, e aparece no painel de
   consumo do desktop.

5. **[Desktop no remoto, com login]** — critério de pronto: o usuário faz login uma vez no app de
   desktop, dita no Windows real, e a transcrição cai no banco; a sessão se renova sozinha entre
   usos; nenhuma credencial ou sessão fica versionada no git; `url_nucleo` voltando para
   `http://127.0.0.1:8000` continua funcionando como saída de emergência.

6. **[Contrato novo]** — critério de pronto: `spec/contrato/NUCLEO.md` em versão nova, dizendo onde
   o núcleo escuta, como autenticar (login e renovação da sessão), o limite de 150 s, o CORS
   fechado e o que ficou no núcleo local (geração de imagem). Um cliente novo começa por ele.

## Backlog

O acervo de ideias mora em [`spec/BACKLOG.md`](../../spec/BACKLOG.md). Ao fechar cada etapa, ler os
itens que tocam este plano e perguntar ao usuário quais sobem.

## Nota de processo (deste plano)

- **Tarefa que derrube o núcleo em uso ou mude o `config.json` do desktop avisa o usuário ANTES de
  começar** — ele dita com o app todo dia.
- **Credenciais**: a chave da OpenAI, a senha do usuário e as chaves do projeto Supabase **nunca**
  entram no chat, em log ou no git. Quem digita segredo é o usuário.
- **Commit só com autorização explícita, por commit** (`M-05`). O `.git/index.lock` de 27/08 ainda
  pode travar — o usuário apaga na máquina.
- As regras de método moram em `.claude/metodo/`. Não repita nenhuma aqui.

## Exceção registrada — commit feito pelo PM (2026-09-30)

**Autorizada explicitamente pelo usuário em 2026-09-30** ("pode gerar o commit também, tá na hora").
O `PM.md` e o `metodo/COMMIT.md` dizem que o PM não roda git de escrita; a exceção vale para este
commit, não vira regra. Ficaram fora dele, de propósito: `desktop/app.log` (log de diagnóstico,
cresce a cada uso), `desktop/config.json` (configuração pessoal, com a diferença fantasma de fim de
linha já conhecida) e `desktop/imagens-geradas/` (saída do usuário).
