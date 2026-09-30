---
tema: Fechamento do plano do núcleo remoto e plano da transcrição como serviço para a Mari (B-27)
data: 2026-09-30
anterior: coleta/2026-09-30_nucleo-remoto-supabase.md
---

# Coleta — transcrição como serviço para a Mari (2026-09-30)

## 1. Critério de uso do plano do núcleo remoto

- [DIRECIONAMENTO] Conferência do PM às 16:28 (banco pelo conector, só leitura; `.jsonl` e
  `app.log` na máquina): `.jsonl` parados desde 14:28 (1867 e 1807 linhas; 1867 = `importado-jsonl`
  no banco); 14 linhas `nucleo-remoto` (2 de teste, 12 ditados reais entre 14:30 e 16:25), todas com
  texto e um só dono; 2 imagens `nucleo-local-imagem`. A metade "`.jsonl` parados" se sustenta; a
  metade "no dia a dia" não tinha como — o plano abriu no mesmo dia.
- [DECISÃO] O plano de fase fecha agora e o critério de uso vira `A-01` em
  `.claude/estado/ACOMPANHAMENTO.md` (uma semana, até 2026-10-07). Trade-off: fecha antes de o
  uso em regime estar provado, em troca de liberar o único lugar de plano de fase para a Mari; o
  risco fica coberto pela condição de reabertura da `D-36` e pelo acompanhamento, que não consome
  Executor.
- [ARTEFATO] Virada: `historico/PLANO_2026-09-30_nucleo-remoto-encerrado.md` (com linha de
  fechamento no topo); as 8 entradas do PROGRESSO movidas sem edição para
  `historico/PROGRESSO_nucleo-remoto_2026-09-30.md` (conferido por `diff`); `ACOMPANHAMENTO.md`
  criado no primeiro uso real; `PLANO.md` e `PROXIMA_TAREFA.md` dizendo que não há plano aberto.
  Passe de fechamento: `spec/VISAO.md` (bloco "Núcleo centralizado" `encerrada`) e `spec/MAPA.md`
  ("Plano encerrado").

## 2. Fatos levantados para o `B-27`

- [DIRECIONAMENTO] O servidor da Mari já chama o RAG pelo lado do servidor: 22 buscas com origem
  `mari-api` em `rag.buscas` desde 29/09.
- [DIRECIONAMENTO] O padrão `x-rag-chave` é **uma chave para todos os projetos** (segredo
  `RAG_CHAVE_ACESSO`), com o `projeto` escolhido no corpo — quem tem a chave age como qualquer
  projeto. As funções do RAG usam `verify_jwt: false` e escrevem pelo `SUPABASE_DB_URL`.
- [DIRECIONAMENTO] `rag.buscas` já guarda a pergunta digitada por quem usa a Mari. A questão de
  guardar texto de terceiros já existe hoje, independente da transcrição.
- [DIRECIONAMENTO] `assistente.consumo.user_id` é obrigatório e o RLS é por usuário — o schema é do
  uso pessoal.

## 3. Decisões de escopo do plano da Mari

- [DECISÃO] **Só o serviço** entra neste repositório: função no RAG-COMPARTILHADO, limites,
  registro de consumo por projeto, contrato. A gravação no navegador e a chamada pelo servidor da
  Mari ficam no repositório dela e leem o contrato. Trade-off: o plano fecha dependendo de trabalho
  feito fora daqui (critério: uma chamada real do servidor da Mari transcreve).
- [DECISÃO] **O texto transcrito não é guardado**: o serviço registra só consumo. Trade-off: perde
  material para a pesquisa de IHC; em troca, não depende do comitê de ética. A pergunta enviada à
  Mari continua indo para `rag.buscas`, como já vai.
- [DIRECIONAMENTO] Recomendações do PM, levadas ao rascunho do plano para o usuário vetar: chave
  própria do serviço, com o projeto decidido pela chave e não pelo corpo; função separada da
  `transcrever` pessoal; tabela de consumo à parte do schema `assistente`.

## 4. Plano aprovado, com ajustes do usuário

- [DECISÃO] Plano aprovado ("números perfeitos"): áudio até 2 min e 4 MB, `gpt-4o-transcribe`
  fixo, teto de US$ 1/dia por projeto. Vira `D-37`; `B-27` promovido.
- [DECISÃO] A chamada à OpenAI do serviço usa **a mesma chave da OpenAI que a Mari já usa**, "para
  os gastos ficarem bem alinhados". Leitura do PM, declarada ao usuário para vetar: é a chave da
  OpenAI (a conta que paga), não a chave de acesso ao serviço, que continua própria por projeto.
  Trade-off: o gasto da transcrição da Mari sai da conta da Mari, não da do ditado pessoal.
- [DIRECIONAMENTO] O servidor da Mari está sendo migrado inteiro para a UrbVerde.
- [DECISÃO] Terminadas as etapas do serviço, **o PM gera os prompts com o contrato** para o
  projeto do servidor fazer a parte de lá. Entrou como Etapa 4 do plano, feita pelo PM a pedido do
  usuário; a chamada real da Mari é a Etapa 5 e o critério de conclusão.
- [DIRECIONAMENTO] Observabilidade mais robusta e centralizada dos gastos da Mari e dos serviços:
  "depois" — registrada como `B-28`.
- [ARTEFATO] `.claude/estado/PLANO.md` (plano "Transcrição como serviço para a Mari"),
  `spec/DECISOES.md` (`D-37`), `spec/BACKLOG.md` (`B-27` promovido, `B-28`), `spec/VISAO.md` (bloco
  "Transcrição como serviço", fora da sequência), `spec/MAPA.md` (plano corrente),
  `PROXIMA_TAREFA.md` (nenhuma tarefa até o "gera").
- [PENDÊNCIA] Tarefa da Etapa 1 aguardando o "gera" do usuário. Sem commit (`M-05`).

## 5. Tarefa da Etapa 1

- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 1 — schema `servicos`, tabela `transcricao_uso` e função
  `gasto_do_dia`, registro `curto`.
- [DECISÃO] (do PM) "Sem texto" é garantido pela estrutura, não por disciplina: as colunas `text`
  da tabela só aceitam identificadores, por `check`. Trade-off: um campo de observação livre, se um
  dia fizer falta, exige migração. O teto diário vira função SQL já nesta etapa, para a Etapa 2 só
  chamá-la. Só o `service_role` grava e lê; o schema não é exposto na API.

## 6. Etapa 1 concluída

- [ARTEFATO] Schema `servicos` aplicado no RAG-COMPARTILHADO (migração `servicos_base`, Executor por
  subagente); SQL em `nucleo-remoto/banco/servicos_base.sql`, igual ao aplicado (SHA conferido pelo
  Executor). Conferido pelo PM no banco: 11 colunas, três `check` que só aceitam identificador, RLS
  sem política, ACL só `service_role` com select/insert, `gasto_do_dia` só para `service_role`,
  0 linhas. Teste do dia de São Paulo feito em bloco desfeito: soma só a linha de hoje.
- [DECISÃO] (do PM) O INFO `rls_enabled_no_policy` do advisor é aceito: RLS sem política é o
  bloqueio pretendido, mesmo desenho de `rag.buscas` e `rag.trechos`.
- [PENDÊNCIA] `B-29` — WARN `auth_leaked_password_protection`, anterior a este plano.

## 7. Tarefa da Etapa 2

- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 2 — função `transcrever-servico` (Parte A), segredos e
  teste no Windows (Parte B, usuário), conferência no banco (Parte C, PM).
- [DECISÃO] (do PM) Cabeçalho `x-servico-chave`, segredo por projeto (`SERVICO_CHAVE_MARI`), chave
  da OpenAI por projeto (`OPENAI_API_KEY_MARI`); o projeto sai da chave. Trade-off: projeto novo
  exige mudar o código e reimplantar — aceitável com um cliente só (condição de reabertura da `D-37`).
- [DECISÃO] (do PM) Se a consulta do gasto falhar, o serviço **recusa** (`503 LIMITE_INDISPONIVEL`):
  público e pago, falha fechada. Trade-off: banco fora do ar derruba o serviço da Mari junto.
- [DECISÃO] (do PM) Registra toda requisição que passou da autenticação, inclusive recusas por
  tamanho e teto — dá para ver abuso sem guardar texto. As de chave inválida não têm projeto e ficam
  só no log da plataforma.
- [DECISÃO] (do PM) O `429` é provado com o teto rebaixado por segredo (`SERVICO_TETO_DIARIO_USD` = 0)
  durante o teste e apagado no fim — sem inserir linha falsa no registro de gasto.

## 8. Etapa 2, Parte A entregue

- [ARTEFATO] Edge Function `transcrever-servico` implantada (v1, `verify_jwt: false`), igual ao
  versionado em `nucleo-remoto/funcoes/transcrever-servico/index.ts`; teste do Windows em
  `nucleo-remoto/testes/testar_servico.*`. Conferido pelo PM: as quatro funções existentes com o
  mesmo `ezbr_sha256` (todas subiram para a versão 5 sem mudar código — a armadilha já conhecida);
  modelo fixo, 4 MB, teto padrão 1.00, sem CORS, `set local role service_role`; `.cmd` com CRLF.
- [DECISÃO] (do PM, a pedido do Executor) Fica o `idle_timeout: 5`: a conexão fecha enquanto espera
  a OpenAI e reabre para registrar — nunca duas ao mesmo tempo, e não segura vaga do Postgres por
  até 120 s. Lê-se "uma conexão por requisição" como "no máximo uma aberta por vez".
- [PENDÊNCIA] Riscos aceitos, a entrar no contrato (Etapa 3): o teto não é atômico (chamadas
  simultâneas passam juntas pela conferência, estouro limitado a elas); `TEMPO_ESGOTADO` registra
  custo 0 embora a OpenAI possa ter cobrado.
- [PENDÊNCIA] `_to_delete/pycache_testar_servico_2026-09-30/` — resíduo que a pasta montada não deixa
  apagar; o usuário apaga na máquina.

## 9. Primeira execução da Parte B — caso 1 travou

- [ACHADO] Caso 1 (sem chave, ~1 MB no corpo): em vez de `401` imediato, `503` da plataforma depois
  de 160,6 s. A chave digitada chegou certa (43 caracteres). Nenhuma linha em
  `servicos.transcricao_uso`, nada cobrado. Usuário orientado a interromper (Ctrl+C) durante o caso 2, que travaria igual.
- [ACHADO] Causa provável: resposta antecipada (`401`) sem ler o corpo — no Supabase o upload trava
  atrás dos intermediários, o cliente nunca lê a resposta. Os testes locais não pegaram porque, na
  mesma máquina, 1 MB cabe nos buffers. Lição: teste local de servidor HTTP não prova comportamento
  de upload atrás de proxy.
- [DECISÃO] (do PM) Correção: drenar o corpo, descartando os pedaços, antes do `405`/`401`. Ler
  com `arrayBuffer()` seria abrir a memória para quem nem tem chave.

## 10. Correção 1 implantada; a primeira rodada seguiu até o caso 4 na versão velha

- [ARTEFATO] `transcrever-servico` v6 (`ezbr_sha256` `c2b0bda6…`), com o corpo drenado antes do
  `405`/`401`. O Executor não reproduziu o travamento localmente (o Deno local descarta o corpo não
  lido sozinho) — a prova só vem da rodada no Windows.
- [ACHADO] A primeira rodada não foi interrompida: casos 1 a 4 deram `503` em ~160 s, todos servidos
  pela versão antiga (a v6 subiu às 20:43 UTC, depois do início do caso 4). Logs da plataforma:
  cada chamada termina em `WallClockTime` com ~12 ms de CPU — a função nunca respondeu. Nenhuma
  linha no registro, nada cobrado.
- [ACHADO] Casos 3 e 4 (com a chave digitada) também travaram e não deixaram linha: com 12 ms de CPU
  não houve leitura de 1–4 MB de formulário, o que indica que a chave digitada **não casou** com o
  segredo e esses casos também caíram no `401`. Não dá para ver o segredo daqui; o usuário suspeitou
  da chave por conta própria.
- [DECISÃO] (do usuário, aceita pelo PM) Gerar uma chave nova e sobrescrever `SERVICO_CHAVE_MARI`
  antes da nova rodada — ela ainda não foi entregue ao servidor da Mari, então trocar não custa nada.

## 11. Etapa 2 — Partes B e C concluídas

- [ACHADO] Segunda rodada no Windows (17:53 local), com `transcrever-servico` v6 e chave nova:
  **5 de 5**. Caso 1 `401` em 1,2 s; caso 2 `401` em 0,8 s; caso 3 `413` em 0,9 s; caso 4 `200` em
  2,7 s (293 caracteres, `X-Servico-Contrato=1`, sem `Access-Control-Allow-Origin`); caso 5 `429`
  na primeira tentativa. A drenagem do corpo resolveu o travamento — confirmado só no Supabase real,
  como previsto.
- [ACHADO] Parte C (PM, no banco): 3 linhas em `servicos.transcricao_uso`, todas `mari` — `413`
  (`ARQUIVO_MUITO_GRANDE`, custo 0, modelo nulo), sucesso (`gpt-4o-transcribe`, US$ 0,00162,
  320/82 tokens, 2182 ms, `codigo` nulo) e `429` (`LIMITE_DIARIO`, custo 0). Nenhuma para os casos
  1 e 2; nenhuma coluna com texto. Custo total do teste: US$ 0,00162.
- [PENDÊNCIA] Confirmação do usuário de que `SERVICO_TETO_DIARIO_USD` foi apagado — o PM não lê
  segredos.

## 12. Etapa 2 fechada; Etapa 3 aberta

- [DECISÃO] (do usuário) Etapa 2 aceita; seguir para a Etapa 3. Commit autorizado pelo usuário — pela
  regra do PM (só leitura de git), o PM prepara o comando e o usuário roda no Git Bash dele; fica de
  fora o `desktop/app.log`, que é uso do app, não trabalho do plano.
- [DECISÃO] (do PM) `SERVICO_TETO_DIARIO_USD`: apagar, não fixar valor — o padrão do código já é o
  US$ 1 aprovado nos Limites. Fixar 1 no segredo daria dois lugares para o mesmo número.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 3 — contrato do serviço, 12 pontos, com os riscos aceitos
  da Etapa 2 (teto não atômico, custo 0 no prazo esgotado, drenagem do corpo, falha fechada).
