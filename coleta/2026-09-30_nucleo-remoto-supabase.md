---
tema: Núcleo centralizado no Supabase (reabre D-05)
data: 2026-09-30
---

# Coleta — núcleo remoto no Supabase (2026-09-30)

## 1. A ideia e a decisão

- [DIRECIONAMENTO] O usuário propôs tirar o núcleo da máquina e hospedá-lo no Supabase, com banco
  relacional junto. Motivo, nas palavras dele: não replicar o backend de novo em cada cliente
  ("igual foi replicado aqui a versão web e depois a versão desktop"), não rodar local no Android
  com chave, e liberar o Android e o relógio.
- [DECISÃO] Centralizar o núcleo num backend remoto. Reabre a `D-05` (servidor adiado até a F7) por
  motivo novo, que não é a condição de reabertura escrita nela (consumo fragmentado): clientes
  magros e chave da OpenAI num lugar só. Trade-off aceito: um salto de rede e um serviço externo na
  ferramenta de todo dia. Vira `D-36` quando o plano for aprovado.
- [DECISÃO] Projeto do Supabase: **RAG-COMPARTILHADO**, o mesmo que já existe. Custo: cota e
  segredos divididos com outro uso, então o banco do assistente fica isolado num schema próprio.
- [DECISÃO] Geração de imagem **fica no desktop, no núcleo local**, por enquanto.
- [DECISÃO] **Sem medição local × remoto**: o usuário dispensou.
- [DIRECIONAMENTO] O cliente local passa a falar com a API remota, para que tudo seja salvo no
  banco.
- [DIRECIONAMENTO] Fato técnico que molda o plano, conferido na documentação do Supabase em
  2026-09-30: Edge Functions rodam só TypeScript/Deno (sem Python), com 150 s de tempo total por
  requisição no plano gratuito, 256 MB de memória, e projeto gratuito pausado após 1 semana sem
  uso. O `transcritor/backend/main.py` é reescrito, não transplantado: o contrato
  (`spec/contrato/NUCLEO.md`) é a especificação da reescrita (`D-07`).
- [PENDÊNCIA] Plano em rascunho, esperando aprovação do usuário.

## 2. Plano aprovado

- [DECISÃO] **A Fase 2 encerra pelo critério de uso em regime**, confirmado pelo usuário: ele já
  dita com o app todo dia. A Etapa 4 fecha com a constatação de que não faltaram etapas. Trade-off:
  o método só permite um plano de fase por vez; manter a F2 aberta seguraria o núcleo remoto sem
  ganho.
- [DECISÃO] **Login pelo Supabase Auth já neste plano**, e não token fixo. O PM propôs token fixo
  até o Android; o usuário escolheu deixar o login pronto agora. Custo aceito: mais trabalho no
  desktop (login uma vez, sessão que se renova).
- [DECISÃO] Confirmada a leitura de "o local vai acessar a API para salvar no banco": a imagem
  continua gerada no núcleo local, e o consumo dela é registrado no banco remoto.
- [DECISÃO] `diarize` fora do núcleo remoto: ~43 s para 72 s de áudio (F1) estouraria os 150 s num
  áudio de 5 min.
- [ARTEFATO] `D-36` em `spec/DECISOES.md`; `D-05` marcada como substituída.
- [ARTEFATO] `.claude/estado/PLANO.md` reescrito — plano "Núcleo centralizado no Supabase", seis
  etapas. Snapshot da F2 em `historico/PLANO_2026-09-30_fase2-encerrada.md`; as 22 entradas do
  PROGRESSO da F2 movidas sem edição para
  `historico/PROGRESSO_fase2-desktop_2026-08-25_a_2026-09-21.md`.
- [ARTEFATO] Passe de fechamento: `spec/VISAO.md` (F2 concluída; bloco novo "Núcleo centralizado"
  entre F2 e F3; nota na F7), `spec/MAPA.md` (F2 fechada, plano corrente, E1.3 decidida),
  `spec/BACKLOG.md` (`B-08` e `B-09` subiram).
- [PENDÊNCIA] `PROXIMA_TAREFA.md` da Etapa 1 (reconhecer o RAG-COMPARTILHADO) aguardando o "gera"
  do usuário.
- [PENDÊNCIA] Sem commit — aguarda autorização (`M-05`).

## 3. Tarefa da Etapa 1 e commit

- [DIRECIONAMENTO] O usuário autorizou acesso momentâneo ao RAG-COMPARTILHADO para o
  reconhecimento; o login da CLI do Supabase já está feito na máquina.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 1 — reconhecimento só de leitura, sete perguntas,
  registro `completo`.
- [DECISÃO] Exceção pontual ao `PM.md`/`COMMIT.md`, autorizada pelo usuário em 2026-09-30: o PM
  faz o commit do trabalho acumulado desde `fc461fa`. Fora do commit: `desktop/app.log`,
  `desktop/config.json`, `desktop/imagens-geradas/`. Registrada também no `PLANO.md`.

## 4. Etapa 1 concluída — o que o reconhecimento mostrou

- [ARTEFATO] Entrada `completo` no `PROGRESSO.md` (Executor por subagente, 2026-09-30). Só leitura
  no Supabase; o PM conferiu a lista de projetos e o histórico de migrações pelo conector.
- [DIRECIONAMENTO] **Correção de premissa do PM**: o RAG-COMPARTILHADO (`wqoeoofhuhsdzpkdblbg`,
  sa-east-1, plano gratuito, criado em 29/09) **não** é dividido com o assistente de vendas — esse
  tem projeto próprio (`Assistente-vendas-whatsapp`). O RAG serve a Mari e um segundo rótulo,
  `assistente-nova-forma`, de origem não identificada. A escolha do projeto continua de pé: a
  organização já tem os 2 projetos ativos que o plano gratuito permite (limite conferido na página
  de preços em 2026-09-30), então um terceiro não cabe sem plano pago.
- [DIRECIONAMENTO] Nada colide com `assistente`. Único schema próprio hoje: `rag`. Auth vazio
  (0 usuários). Edge Functions `buscar` e `ingerir`, com autenticação própria por cabeçalho.
  Segredo `OPENAI_API_KEY` provavelmente já existe (pelo código do RAG, não confirmado no projeto).
- [DECISÃO] (recomendação do Executor, a confirmar na tarefa da Etapa 2) Não usar `supabase db
  push` neste projeto; aplicar o schema `assistente` como migração avulsa, nome prefixado
  `assistente_`, com o SQL versionado neste repositório.
- [PENDÊNCIA] Riscos para as etapas 2–3: o limite de conexões do banco já se esgotou uma vez
  (29/09) — preferir acesso por HTTP a conexão direta; configuração do Auth (cadastro público,
  confirmação de e-mail) só se vê no painel; o RAG tem código implantado sem commit (não é deste
  projeto).
- [PENDÊNCIA] O critério da Etapa 2 diz "schema não exposto na API pública". Com login pelo Auth,
  a alternativa natural é expor com RLS por usuário — pergunta aberta ao usuário.

## 5. Correções do usuário e ajuste da Etapa 2

- [DIRECIONAMENTO] Correção do usuário ao item 4: `assistente-nova-forma` é o RAG do assistente de
  vendas, que ele unificou no RAG-COMPARTILHADO. No futuro, este assistente pode ter acesso a um
  pedaço desse banco.
- [DECISÃO] Ficar no RAG-COMPARTILHADO é **convergência de infraestrutura** (palavras do usuário:
  "fazer a convergência da infraestrutura"), não só falta de vaga. Nota acrescentada à `D-36`.
- [DIRECIONAMENTO] O estouro de conexões de 29/09 foi por muitas requisições simultâneas; o núcleo
  não faz isso. O risco registrado no item 4 cai de peso.
- [DECISÃO] Critério da Etapa 2 ajustado: schema `assistente` **exposto na API com RLS por
  usuário**, em vez de não exposto. Leitura do PM do "fazer certinho" do usuário — declarada como
  suposição na resposta, para ele vetar antes da execução.
- [DIRECIONAMENTO] Achado técnico do PM: a máquina de trabalho remota não alcança o Supabase pela
  rede (teste de 2026-09-30), então a importação dos `.jsonl` roda no Windows do usuário, com a
  senha digitada por ele.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 2.

## 6. Etapa 2, Parte A entregue

- [ARTEFATO] Migração `assistente_base` aplicada no RAG-COMPARTILHADO (schema `assistente`, tabelas
  `consumo` e `transcricoes`, RLS com `select`/`insert` só do dono, nada para `anon`, FK de
  transcrição para consumo). SQL versionado em `nucleo-remoto/banco/assistente_base.sql`. Conferido
  pelo PM: duas tabelas, RLS ligado, 0 linhas; nenhuma chave secreta em `nucleo-remoto/`.
- [ARTEFATO] Importador `nucleo-remoto/banco/importar_historico.py` + `.cmd`, idempotente (ids
  fixos, `uuid5` para as 49 linhas antigas sem id). Simulação: 1863 consumos, 1803 transcrições,
  soma `custo_usd` ≈ US$ 6,8873; 0 órfãos, timestamps em UTC.
- [PENDÊNCIA] Parte B com o usuário (criar usuário, fechar cadastro, expor schema, rodar o
  importador); Parte C é a conferência do PM.
- [PENDÊNCIA] Para as etapas 3–4: `service_role` não tem grant em `assistente` (a Edge Function deve
  gravar como o usuário, não como administrador); a ordem de gravação é consumo antes de
  transcrição; as 31 linhas de imagem guardam o prompt em `texto`.

## 7. Etapa 2 concluída

- [ARTEFATO] Histórico importado pelo usuário no Windows: 1864 consumos e 1804 transcrições,
  conferidos pelo PM no banco; soma de `custo_usd` idêntica à dos arquivos (6,88787583…); um só
  dono. As 60 linhas de consumo sem transcrição = 49 antigas sem id + 11 que nunca tiveram texto.
- [DIRECIONAMENTO] A primeira falha não era o Python (suspeita do PM, desmentida pelo log): foram
  duas tentativas com credencial errada antes do login dar certo. A Correção 1 fica mesmo assim —
  o log é o que permitiu saber.
- [PENDÊNCIA] Não verificável pelo banco: cadastro público fechado (passo 2) — conferir no painel.

## 8. Etapa 3, Parte A entregue

- [ARTEFATO] Edge Function `transcrever` implantada (v1, `verify_jwt: true`; conferida pelo PM na
  lista de funções — `buscar` e `ingerir` intactas na v2). Código em
  `nucleo-remoto/funcoes/transcrever/index.ts`, igual ao implantado (md5 conferido pelo Executor).
  Teste do Windows em `nucleo-remoto/testes/`.
- [DECISÃO] (do Executor, aceita pelo PM) Códigos novos no contrato: `401 NAO_AUTENTICADO` (a
  função confere se o token é de um usuário do Auth antes de gastar a chamada paga — a chave anônima
  também passaria pelo gateway), `422 REQUISICAO_INVALIDA`, `405`, `500 ERRO_INTERNO`. Prazo de
  120 s numa tentativa só. Divergências completas no PROGRESSO; entram no contrato na Etapa 6.
- [PENDÊNCIA] Risco declarado: se o projeto assina tokens com as chaves JWT novas, o gateway pode
  recusar o token do usuário (`401` sem `NAO_AUTENTICADO`); conserto seria reimplantar com
  `verify_jwt: false`, já que a função confere o usuário sozinha — decisão do PM, se acontecer.
- [PENDÊNCIA] O teste real deixa 2 linhas com `origem = 'nucleo-remoto'` no histórico (a API não
  apaga, por desenho).

## 9. Etapa 3 concluída

- [ARTEFATO] Teste real no Windows contra a função implantada: 6 de 6 (sem token 401; lote 200 em
  4,0 s; streaming 200 em 2,7 s com 81 deltas e 1 final; diarize 422; áudio vazio 400; +2 linhas
  em cada tabela). Conferido pelo PM no banco: 2 consumos e 2 transcrições com
  `origem = 'nucleo-remoto'`, mesmo dono, US$ 0,00316 no total.
- [DIRECIONAMENTO] O risco das chaves JWT novas não se materializou: o gateway aceitou o token do
  usuário com `verify_jwt: true`.

## 10. Tarefa da Etapa 4

- [DECISÃO] Quem registra a imagem no banco é o núcleo local, com o token que o cliente repassar no
  `Authorization`; sem token, segue nos `.jsonl` (o desktop atual não quebra). O teste sobe um
  segundo núcleo na porta 8001 para não derrubar o de uso diário.
- [DECISÃO] Ajuste de critério no PLANO: "aparece no painel de consumo do desktop" saiu da Etapa 4
  e foi para a 5 — o painel só lê o remoto, e o desktop só tem sessão, depois do login.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 4.

## 11. Etapa 4, Parte A entregue

- [ARTEFATO] Edge Function `consumo` implantada (v1, `verify_jwt: true`), igual ao versionado
  (`nucleo-remoto/funcoes/consumo/index.ts`). `main.py` registra a imagem no banco quando recebe o
  token (+108 linhas, só no caminho do `/gerar-imagem`; sem token, idêntico ao original, testado
  contra o HEAD). Teste do Windows em `nucleo-remoto/testes/testar_consumo_e_imagem.*`.
- [DIRECIONAMENTO] Premissa errada do PM corrigida pelo Executor: a venv tem `httpx2` (SDK OpenAI
  3.1.0), não `httpx`; o registro importa um ou outro, sem dependência nova.
- [DECISÃO] (divergência aceita) `/consumo` remoto agrupa `por_dia` e `sessao` pelo dia de
  `America/Sao_Paulo`; o local agrupava em UTC e `sessao` era "desde que o processo subiu".
- [PENDÊNCIA] Para a Etapa 5: o `transcritor/.env` real precisa ganhar `SUPABASE_URL` e
  `SUPABASE_CHAVE_PUBLICAVEL` antes de o desktop repassar o token; e o núcleo da porta 8000 precisa
  ser reiniciado para pegar o `main.py` novo. Banco fora do ar = registro de imagem perdido (sem
  recaída para os `.jsonl`), aceito.

## 12. Etapa 4 concluída

- [ARTEFATO] Teste real no Windows, 5 de 5: `/consumo` remoto sem token 401; com token 200, 1866
  requisições e soma de `custo_usd` idêntica à da API (6,8910358333), 35 dias; imagem gerada pelo
  núcleo na porta 8001 com token, registrada no banco (`nucleo-local-imagem`, US$ 0,047) e nenhuma
  linha nova de imagem nos `.jsonl`; núcleo 8001 encerrado. Conferido pelo PM no banco.
- [DIRECIONAMENTO] A OpenAI recusou `gpt-image-1-mini` nesta rota (HTTP 400, provavelmente pelo
  `input_fidelity="high"`); o teste caiu no `gpt-image-1.5` com confirmação do usuário.
- [PENDÊNCIA] Para a Etapa 5: o `consumo.jsonl` já tem 1 linha a mais que o banco (ditado pela
  porta 8000 depois da importação) — rodar o importador de novo (idempotente) no momento da virada,
  depois de o desktop passar a usar o remoto.

## 13. Tarefa da Etapa 5

- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 5 — login e sessão no desktop (sessão em `%APPDATA%`, fora
  do repositório), `url_nucleo` para as funções remotas, `url_nucleo_imagem` para o local, migração
  automática do `config.json`, `reiniciar_transcritor.cmd`, e a reimportação idempotente na virada.
- [DECISÃO] (do PM) Sessão guardada em arquivo em `%APPDATA%\agentes-base\`, não no gerenciador de
  credenciais do Windows, para não trazer dependência nova; a senha nunca é gravada.

## 14. Etapa 5, Parte A entregue

- [ARTEFATO] `desktop/app.py` (+638 linhas): login pelo Supabase Auth num sobreposto no estilo de
  Configurações, sessão em `%APPDATA%\agentes-base\sessao.json` (senha nunca gravada), renovação
  antes de expirar e por `401`, áudio guardado e reenviado se a sessão cair, "Sair da conta" no
  menu ⋮, conta visível em Configurações, token repassado ao núcleo local na imagem. Janela
  intocada (`D-32`). `config.json` migrado (conferido pelo PM: `url_nucleo` remoto,
  `url_nucleo_imagem` local, atalho preservado). `transcritor/.env` ganhou só as 2 linhas públicas.
  `desktop/reiniciar_transcritor.cmd` novo. Suítes headless: 231/231 (antiga) e 84/84 (nova, que
  pega três mutações deliberadas).
- [PENDÊNCIA] Riscos declarados: o ditado passa a depender do Supabase (saída de emergência é o
  `url_nucleo` local); foco do teclado no campo de e-mail pode precisar de clique no Windows;
  latência da primeira chamada não medida; a interface web continua gravando nos `.jsonl`.

## 15. Etapa 5 concluída, e a ideia da transcrição para a Mari

- [ARTEFATO] Uso real confirmado pelo usuário e conferido pelo PM: login ok, 2 ditados reais pelo
  núcleo remoto, 1 imagem do app registrada no banco, `.jsonl` parados desde o reinício. Faltou o
  passo 4 (reimportar): 3 linhas do `.jsonl` de antes da virada ainda não estão no banco.
- [PENDÊNCIA] `B-26` — `API_RECUSOU` na geração de imagem, já presente em 23/09; usuário mandou
  deixar para depois.
- [DIRECIONAMENTO] Ideia do usuário: o RAG-COMPARTILHADO como **projeto de serviços** (RAG +
  transcrição), e a transcrição como ferramenta de acessibilidade da Mari (grava no navegador,
  transcreve, devolve o texto). Registrada como `B-27`, com o caminho avaliado pelo PM.

## 16. Tarefa da Etapa 6

- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 6 — contrato novo com os dois lugares do núcleo,
  autenticação, divergências marcadas como medidas ou lidas no código, e `B-08`/`B-09` fechados.
- [DECISÃO] (do PM) O número de versão do contrato sobe para `2` no remoto **só se** nenhum cliente
  compara o valor do cabeçalho; se algum compara, o Executor não sobe e o PM decide.

## 17. Etapa 6 concluída — todas as etapas do plano fechadas

- [ARTEFATO] `spec/contrato/NUCLEO.md` em contrato 2 (419 → 715 linhas, só acréscimos): onde o
  núcleo escuta (remoto × local), autenticação, divergências marcadas `[medido]` com a fonte ou
  `[código]`, registro de consumo no banco. `X-Nucleo-Contrato` subiu para `2` no remoto (nenhum
  cliente compara o valor); local segue em `1`. Testes remotos ajustados para `2`. `B-08` e `B-09`
  resolvidos.
- [DIRECIONAMENTO] As versões 2 e 3 das funções não eram código de outra sessão: `buscar` e
  `ingerir` também saltaram de versão sem mudar o `ezbr_sha256` — o número sobe com mudança de
  configuração do projeto. Conferido pelo PM.
- [PENDÊNCIA] Resta o critério de conclusão do plano, que é de uso: ditar pelo remoto no dia a dia
  sem nada novo nos `.jsonl`. E a reimportação das 3 linhas de antes da virada.

## 18. Encerramento do chat

- [ARTEFATO] Reimportação feita pelo usuário: +3 consumos e +3 transcrições; banco com 1867
  `importado-jsonl`, 12 `nucleo-remoto` e 2 `nucleo-local-imagem` (conferido pelo PM).
- [DIRECIONAMENTO] Usuário pediu para encerrar e retomar num chat novo com o plano da Mari (`B-27`).
- [DECISÃO] Commit autorizado pelo usuário ("pode commitar"); imagens geradas ficam locais, fora do
  git, por enquanto.

---

# Consolidação (2026-09-30)

## Decisões
- `D-36`: núcleo centralizado no Supabase (RAG-COMPARTILHADO), com banco e login — reabre a `D-05`
  por motivo novo (clientes magros, chave num lugar só). Trade-off: serviço externo na ferramenta
  diária; saída de emergência é o núcleo local.
- Fase 2 encerrada pelo critério de uso em regime.
- Login pelo Supabase Auth desde já (não token fixo); schema `assistente` exposto com RLS por
  usuário; migração avulsa, nunca `db push`.
- Geração de imagem fica local e registra no banco com o token; `diarize` fora do remoto.
- Contrato 2 no remoto (`X-Nucleo-Contrato: 2`); local segue em 1.
- Ficar no RAG-COMPARTILHADO é convergência de infraestrutura (projeto de serviços).

## Artefatos
- `nucleo-remoto/` (migração, importador, funções `transcrever` e `consumo`, testes do Windows).
- `transcritor/backend/main.py` (registro da imagem no banco com token).
- `desktop/app.py` (login, sessão, remoto), `desktop/testes_sessao.py`, `reiniciar_transcritor.cmd`.
- `spec/contrato/NUCLEO.md` contrato 2; `spec/DECISOES.md` `D-36`; `B-26`, `B-27` no backlog.

## Direcionamentos
- O RAG-COMPARTILHADO vira projeto de serviços: RAG + transcrição.
- A transcrição pode virar recurso de acessibilidade da Mari (`B-27`).

## Pendências
- Critério do plano (uso em regime pelo remoto, `.jsonl` parados) — depende de dias de uso.
- `B-26` (imagem com `API_RECUSOU`) — depende de o usuário pedir.
- Plano da Mari (`B-27`) — depende do próximo chat de PM.
- Painel de diagnóstico geral não republicado neste chat.
