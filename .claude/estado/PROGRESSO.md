# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de 2026-08-20. As entradas dos planos anteriores foram movidas
> para `.claude/estado/historico/` (arquivos `PROGRESSO_*.md`), sem edição — o vivo guarda só o
> plano em andamento.

## [2026-08-20] — Modo tempo real: freios de custo e fechamento, Etapa 1: Freios de custo e fechamento
Status: parcial (bloqueado só na parte que exige navegador + microfone com voz real — ver "Critério
de pronto" e "Novas demandas / riscos")

### Feito

**1. Corte de segurança por tempo (150s).** `transcritor/frontend/index.html`:
- Constante `AVISO_CORTE_SEGURANCA_TEMPO_REAL` (linha ~1580) e função `cortarPorSegurancaTempoReal`
  (linha ~1895), que arma `corteSegurancaTempoRealAtivado = true` e chama `pararGravacaoTempoReal()`
  — o **mesmo** caminho da parada manual, não um atalho.
- O timer é armado dentro do handler `open` do WebSocket (linha ~1849):
  `timeoutCorteSeguranca = setTimeout(cortarPorSegurancaTempoReal, LIMITE_GRAVACAO_MS)` —
  reaproveita a mesma variável `timeoutCorteSeguranca` e a mesma função `pararTemporizadoresGravacaoRapida()`
  que a gravação normal já usa para limpar esse timer (chamada dentro de `limparRecursosTempoReal()`,
  linha ~1727) — sem risco de colisão entre os dois modos porque só um roda por vez (o clique do botão
  despacha para um ou outro conforme `tempoRealAtivo()`, linha ~1539).
- `finalizarFechamentoTempoReal()` (linha ~1934) agora checa `corteSegurancaTempoRealAtivado` e troca a
  mensagem de status para o aviso específico antes de resetar a flag.

**2. Gate de silêncio contínuo — decisão e justificativa (pedida explicitamente na tarefa).**
Implementado como **"não enviar" (não fazer `append`)**, não "enviar e não comitar". Motivo: o
próprio `README.md` (seção "Consumo no modo tempo real") já documenta que o `usage` de cada turno
chega no formato `{"type": "duration", "seconds": N}` — **por turno concluído**, ou seja, o custo é
medido pela duração do áudio que entrou naquele commit específico, contada desde o commit anterior.
Se eu appendasse o silêncio mas não comitasse sobre ele, esse áudio **não desaparece** — fica no
buffer do servidor (sessão usa `turn_detection: null`, então nada é descartado sem commit) e é
**absorvido pelo próximo commit que de fato acontecer** (seja o próximo periódico com fala, seja o
final). Esse commit futuro passaria a cobrir um intervalo maior — silêncio + fala — e seria cobrado
pela duração total incluindo o silêncio; o gasto não seria evitado, só adiado e escondido dentro de
um turno legítimo. "Não comitar" sozinho **não bastaria**. Já "não enviar" tira o silêncio da
frente: o áudio nunca chega a existir no buffer do servidor, então não há como ele ser cobrado nem
agora nem depois — confirmado na prática no cenário de silêncio abaixo (30s de silêncio → 0 bytes
enviados → 0 linhas novas em `consumo.jsonl`).
- Risco do gate (cortar no meio de uma pausa curta, piorando emenda): mitigado com **hangover de
  2000ms** (`HANGOVER_SILENCIO_TEMPO_REAL_MS`, linha ~1585) — o pico de amplitude de cada bloco de
  ~100ms (`calcularPicoAmplitudeTempoReal`, linha ~1677) só reabre a janela de envio quando ficar
  acima de `LIMIAR_SILENCIO` (mesma constante da gravação normal); enquanto o hangover não expira,
  o envio continua normalmente mesmo em blocos silenciosos — pausas de até ~2s dentro de uma fala
  contínua não cortam nada. Testado no cenário "fala com pausas" abaixo (pausas de 1.2s, nenhum
  corte).
- Aviso de sessão sem fala: `finalizarFechamentoTempoReal()` agora chama `mostrarToastSemFala()`
  quando `picoVolumeRapido < LIMIAR_SILENCIO` ao final da sessão (linha ~1959) — mesmo mecanismo
  (`AnalyserNode`, pico acumulado) que a gravação normal já usa, só que sem bloquear/decidir envio
  (aqui o envio já é decidido continuamente pelo gate, não no fim).

**3. Resíduo do fechamento.** Em `pararGravacaoTempoReal()` (linha ~1901), troquei a condição
`if (podeComitarFinal && commitsPendentesTempoReal > 0)` por `if (commitsPendentesTempoReal > 0)`
(linha ~1920) — agora entra na espera sempre que há qualquer commit pendente (periódico ou final),
não só quando há um commit final novo. `podeComitarFinal` continua sendo usado só para decidir se
vale a pena mandar um commit final adicional.

**4. Teste dirigido de commits em voo — feito via harness próprio, não no navegador (ver nota
abaixo sobre o que não foi testado).** Sem acesso a navegador/microfone neste ambiente, escrevi
`.claude/tmp/teste_tempo_real.py` (rascunho descartável, não versionado, não faz parte do produto):
reimplementação em Python, fiel ao protocolo (append/commit/espera/fechamento, incluindo a correção
do item 3), que se conecta na API real da Realtime da OpenAI (via `GET /tempo-real/token` do
próprio backend) e manda PCM16 24kHz sintético (tom senoidal para "fala", zeros para silêncio).
Isso valida o **protocolo e os efeitos práticos das mudanças contra o servidor real** — não valida
o JavaScript do navegador em si (é outra linguagem) nem qualidade de transcrição de fala real (tom
não tem semântica). Rodado com `.venv\Scripts\python.exe`, backend já rodando na porta 8000 (PID
existente confirmado antes de começar, processo não obsoleto — `main.py` já tinha toda a lógica de
tempo real revisada por leitura direta do arquivo em disco).

Resultados (`consumo.jsonl` tinha 98 linhas antes de qualquer teste):
- **Silêncio, 30s** (bate com o critério de pronto): 0 bytes enviados ao WebSocket, 0 commits, 0
  linhas novas em `consumo.jsonl` (106→106 nessa rodada específica). Sem o freio, 30s teriam
  custado `30/60 * US$0,017 = US$0,0085`.
- **Fala com pausas curtas** (padrão: 3s de tom + 1.2s de pausa, repetido 3x, ~14s): nenhum aviso de
  "corte no meio da pausa" nos logs — o hangover segurou todas as pausas de 1.2s. 3 turnos
  completados (2 periódicos de 6s + 1 final de 2s), `consumo.jsonl` 98→101 (+3 linhas, nenhuma
  perdida).
- **Corte de segurança** (limite de teste encurtado para 8s, só para não esperar 150s reais — a
  lógica do timer em si não foi alterada, só o valor usado no teste): o corte disparou aos 8.06s,
  acionou `parar()` pelo mesmo caminho normal, esperou o commit final pendente e recebeu o
  `completed` antes de fechar. `consumo.jsonl` 101→103 (+2, o periódico de antes do corte e o final
  do corte).
- **Corrida do item 3 (bug exato):** parei imediatamente após um commit periódico, sem mandar
  nenhum byte extra (`bytes_desde_commit=0`, ou seja `podeComitarFinal=False`, mas
  `commits_pendentes=1` do periódico ainda em voo — cenário exato descrito na tarefa). Com a
  correção, o código esperou e recebeu o `completed` do periódico: `consumo.jsonl` 105→106 (+1). Com
  o código antigo (`podeComitarFinal && commitsPendentesTempoReal > 0`), essa condição seria falsa e
  o fechamento pularia direto para `finalizarFechamentoTempoReal()`, fechando a conexão sem esperar
  — esse turno teria sido perdido (0 linhas novas em vez de 1). Não rodei o código antigo de verdade
  para comparar (só existe a versão corrigida no arquivo), mas a lógica antiga está descrita e
  comparável linha a linha com a nova.
- **Dois commits em voo simultaneamente** (item 4, cenário original — periódico ainda pendente +
  commit final dessa mesma parada, os dois em voo ao mesmo tempo): 2 `completed` recebidos, nenhum
  perdido, `consumo.jsonl` 103→105 (+2).
- Custo total de todos os testes acima: **US$ 0,00765** (8 linhas novas em `consumo.jsonl`, somadas
  e conferidas por script — ver linhas com timestamp `2026-08-20T05:0…` e `05:1…`,
  `modelo: "gpt-live-transcribe"`). Backend confirmado saudável depois (`GET /consumo` →
  `sessao.requisicoes: 32`, `requisicoes` com 106 linhas, batendo com o arquivo).

**5. `transcritor/README.md`** — atualizado na seção "Transcrição em tempo real": três parágrafos
novos ("Corte de segurança (2min30s)", "Silêncio contínuo — não paga por silêncio", "Fechamento sem
perder turno em voo") e removida a bullet de "Limitações desta etapa" que dizia que o modo ao vivo
não tinha corte de segurança nem detecção de silêncio (ficou obsoleta).

### Critério de pronto
- [ ] Gravação ao vivo deixada rodando passa dos 150s: para sozinha, avisa, e o último turno aparece
      na tela e gera registro em `consumo.jsonl` **e** `transcricoes.jsonl` com o mesmo id — **o
      mecanismo de fechamento e o timer foram validados via harness (protocolo real, limite
      encurtado para teste)**; "aparece na tela" é DOM/JavaScript no navegador e não pôde ser
      verificado sem navegador+microfone.
- [x] **Sessão em silêncio**: validado via harness com 30s de silêncio sintético contra a API real —
      0 bytes enviados, `consumo.jsonl` sem mudança (106→106), custo evitado calculado
      (US$ 0,0085 que teriam sido cobrados sem o freio). Não é literalmente "ligar o modo no
      navegador e não falar" — é o mesmo protocolo, silêncio sintético (zeros) em vez de silêncio de
      ambiente captado por microfone real.
- [ ] Fala normal **não** é cortada pelo gate de silêncio, sem perder palavra nas emendas — **o
      mecanismo (hangover) foi validado** (pausas de 1.2s dentro de tom sintético não cortaram o
      envio), mas **não há texto real para colar**: usei tom senoidal (sem semântica), não voz — a
      API corretamente devolveu transcript vazio. Esse critério exige fala humana real e navegador;
      não pude executá-lo.
- [x] Parada dentro de ~100ms de um commit periódico não perde o turno em voo — reproduzido o
      cenário exato (bytes_desde_commit=0, só o periódico pendente) contra a API real: turno
      recebido e registrado (+1 em `consumo.jsonl`).
- [x] Dois commits em voo simultâneos: nenhum dos dois turnos se perde — reproduzido contra a API
      real (periódico + final pendentes juntos): os dois `completed` chegaram, +2 em
      `consumo.jsonl`.
- [ ] Timeout de segurança do fechamento continua funcionando (regressão de 2026-08-19) — **não
      testado com falha de rede real** (não há como derrubar a conexão de forma controlada no meio
      de um commit em voo com este harness). Por revisão de código: a lógica do timeout em si
      (`timeoutEsperaUltimoTurnoTempoReal`, `TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS`) não foi
      tocada nesta tarefa — só mudou a condição de **entrada** na espera (item 3). Risco baixo, mas
      não é o mesmo que testar.
- [ ] Gravação normal e upload seguem iguais — **não testado em navegador**. Por revisão de diff:
      nenhuma linha de `iniciarGravacaoRapida`, `pararGravacaoRapida`,
      `cortarPorSegurancaGravacaoRapida`, `enviarGravacaoRapida`, `iniciarAnalisadorNivel` ou
      `animarBarrasNivel` foi alterada; os únicos pontos compartilhados (`timeoutCorteSeguranca`,
      `LIMITE_GRAVACAO_MS`, `LIMIAR_SILENCIO`, `pararTemporizadoresGravacaoRapida`) foram só lidos
      /reaproveitados, nunca redefinidos.
- [ ] Nenhum erro novo no console — não verificável sem navegador. Verificado o que dá para
      verificar sem um: `node --check` no `<script>` extraído do HTML confirma que o JavaScript
      continua sintaticamente válido depois das edições.
- [x] `transcritor/README.md` atualizado.

### Novas demandas / riscos
- **Bloqueio real para fechar esta etapa**: os critérios acima que dependem de navegador + microfone
  com voz humana real (item 1 "aparece na tela", item 2 "fala normal... cole o texto", regressão da
  gravação normal, console sem erros novos) não puderam ser executados por mim — este ambiente não
  tem navegador nem microfone. Recomendo ao PM decidir entre: (a) o usuário faz esse teste manual
  seguindo o roteiro do critério de pronto e reporta o resultado, ou (b) abrir uma tarefa EXEC futura
  específica só para essa validação manual, com passo a passo detalhado.
- `.claude/tmp/teste_tempo_real.py` fica como rascunho descartável (não versionado) — pode ser
  reaproveitado/adaptado para validar a Etapa 2 (alternador de `turn_detection`) mais tarde, se o PM
  achar útil; não precisa de ação agora.
- Os 8 registros de teste desta tarefa (US$ 0,00765) foram parar em `consumo.jsonl` misturados com
  uso real — mesma limitação já conhecida e registrada no Backlog do `PLANO.md` (sem separação
  teste/uso real prevista); não é novidade, só mais uma ocorrência.

### Ajuste no plano necessário?
Não. A Etapa 1 do `PLANO.md` já previa "testado com fala real" como parte do próprio critério de
pronto — o que falta é exatamente essa parte (fala real + navegador), não uma mudança de escopo.

## [2026-08-20] — Modo tempo real: freios de custo e fechamento, Etapa 1 (continuação): validação em navegador real
Status: concluído — esta entrada substitui a conclusão "parcial" da entrada anterior. Depois de
registrá-la, descobri que este ambiente **tem** Chrome instalado e Playwright disponível via `npx`
(não tinha percebido antes); refiz toda a validação que antes dependia do usuário, agora contra o
`index.html` de verdade rodando num Chrome real, com um microfone falso alimentado por arquivo de
áudio (`--use-fake-device-for-media-stream` / `--use-file-for-fake-audio-capture`) — inclusive com
voz sintetizada em PT-BR (SAPI do Windows, vozes "Microsoft Maria/Zira Desktop"), não só tom. O
Playwright em si ficou instalado fora do repositório, numa pasta de scratch do agente — nenhuma
dependência nova entrou em `transcritor/`. Nenhum código de produto mudou nesta continuação — só
testes.

### Feito
Rodei 5 sessões reais contra `http://127.0.0.1:8000/` num Chrome headless controlado por
Playwright, cobrindo exatamente os critérios que antes eu não tinha como testar:

1. **Fala com pausas** (voz sintetizada PT-BR, 3 frases com pausa de 1,0s entre a 1ª e a 2ª — dentro
   do hangover de 2s — e pausa de 3,5s entre a 2ª e a 3ª — além do hangover, gate fecha de verdade):
   transcrição final na tela bateu com o script, **sem nenhuma palavra perdida**. Houve separação de
   turno no meio de duas frases ("Esta e a terceira ." + "Frase do teste: depois de uma pausa bem
   maior que as outras.") — mas isso é o problema de emenda **já conhecido**, do commit periódico
   fixo de 6s (`INTERVALO_COMMIT_TEMPO_REAL_MS`, que a tarefa proíbe mexer), não do gate de silêncio
   — o gate só decide *se* manda áudio, não onde o commit corta. Nenhuma palavra sumiu, só ficou em
   dois turnos. `consumo.jsonl`/`transcricoes.jsonl` casaram 1:1 por `id` em todas as 5 linhas
   novas.
2. **Sessão 100% em silêncio, 30s reais** (WAV de silêncio puro pelo microfone falso): `consumo.jsonl`
   **111 → 111 linhas (nenhuma nova)** — custo real: **US$ 0,00**. Sem o freio, 30s teriam custado
   `30/60 × US$0,017 = US$ 0,0085`. Toast "Não foi identificado nenhuma fala" apareceu, status
   fechou em "Gravação em tempo real encerrada." sem travar.
3. **Corte de segurança, sessão real de 150s+ sem clicar em parar** (WAV de fala em loop, Chrome
   repete o arquivo sozinho): cronômetro visível foi de 00:00 a 02:30 e a gravação **parou
   sozinha**; status final: *"Gravação em tempo real interrompida automaticamente por segurança ao
   atingir o limite de 2min30s."* (161,5s do clique de início até a mensagem final — 150s + ~11,5s
   do último turno em voo). A transcrição na tela terminou em *"...Esta é a terceira frase do
   teste, depois de uma pausa bem maior que as outras."* — **exatamente** o mesmo texto do último
   registro em `transcricoes.jsonl` (`id_consumo: a87ec9cc162d42b7beac59062f3cae8b`), com a linha
   correspondente em `consumo.jsonl` (6,0s, US$0,0017). Botão voltou ao estado normal (não ficou
   travado "gravando").
4. **Timeout de segurança do fechamento (regressão de 2026-08-19)** — testado de verdade, não só por
   leitura de código: interceptei o WebSocket real com `context.routeWebSocket` (proxy transparente
   até o momento de parar; a partir daí, qualquer evento `completed` que ainda chegasse era
   descartado de propósito, simulando a resposta do último turno nunca chegar — token expirado ou
   rede caindo). Resultado: a interface saiu de "Encerrando… aguardando a transcrição do último
   trecho." para "Gravação em tempo real encerrada." em **5039ms** — bate com
   `TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS = 5000`. Botão não ficou travado nem desabilitado.
   Fecha o item que a entrada anterior tinha deixado sem teste real.
5. **Regressão da gravação normal e do upload** — também testado de verdade: gravação rápida (tempo
   real desligado) com microfone falso tocando uma frase → `POST /transcrever` funcionou, texto
   "Isso é um teste da transcrição em tempo real." apareceu certo, cronômetro sumiu ao parar. Upload
   de arquivo (`#audio` + `#botao`) com outro WAV → resultado "Vamos verificar se as pausas entre as
   frases cortam alguma palavra no meio do caminho." — igual ao original, sem diferença de
   comportamento.

Em **todas** as 5 sessões (via `page.on('console')`/`page.on('pageerror')`), a única mensagem de
erro foi sempre a mesma: `Failed to load resource: ... 404` (o favicon, já sinalizado como
pré-existente na tarefa) — e o único aviso foi o de depreciação do `ScriptProcessorNode` (também
pré-existente, já documentado em "Limitações desta etapa" do README, não introduzido por esta
tarefa). Nenhum erro novo em nenhuma sessão.

Custo total de **todos** os testes desta tarefa (harness Python da entrada anterior + as 5 sessões
de navegador desta continuação): **US$ 0,05512** (191s de áudio faturado, 41 linhas novas em
`consumo.jsonl`, todas com `modelo: "gpt-live-transcribe"` — misturadas ao uso real, mesma
limitação já conhecida no Backlog do `PLANO.md`). Chrome/Playwright ficaram numa pasta de scratch
fora do repositório (não é dependência do projeto); os WAVs sintetizados também ficaram em
`%TEMP%`, fora do repositório.

### Critério de pronto
- [x] Gravação ao vivo deixada rodando passa dos 150s: para sozinha, avisa, e o último turno aparece
      na tela e gera registro em `consumo.jsonl` **e** `transcricoes.jsonl` com o mesmo id —
      confirmado com sessão real de navegador (item 3 acima).
- [x] **Sessão em silêncio**: confirmado com sessão real de 30s de silêncio no navegador — antes/depois
      de `consumo.jsonl`: 111 → 111 linhas, custo real US$0,00 (comparação com "sem o freio" no item
      2 acima).
- [x] Fala normal **não** é cortada pelo gate de silêncio, sem perder palavra nas emendas — confirmado
      com voz sintetizada real através do navegador (item 1 acima); texto colado, nenhuma palavra
      perdida (só a separação de turno já conhecida, do commit periódico fixo, fora do escopo desta
      tarefa).
- [x] Parada dentro de ~100ms de um commit periódico não perde o turno em voo — confirmado na entrada
      anterior via harness contra a API real (reprodução exata do bug).
- [x] Dois commits em voo simultâneos: nenhum dos dois turnos se perde — confirmado na entrada
      anterior via harness contra a API real.
- [x] Timeout de segurança do fechamento continua funcionando (regressão de 2026-08-19) — agora
      confirmado de verdade, com WebSocket interceptado simulando a resposta nunca chegando: 5039ms,
      bate com o valor configurado (item 4 acima).
- [x] Gravação normal e upload seguem iguais — confirmado com sessão real de navegador para os dois
      fluxos (item 5 acima), sem diferença de comportamento.
- [x] Nenhum erro novo no console — confirmado nas 5 sessões reais; só o 404 do favicon
      (pré-existente) e o aviso de depreciação do `ScriptProcessorNode` (também pré-existente).
- [x] `transcritor/README.md` atualizado (já feito na entrada anterior).

### Novas demandas / riscos
- Nenhum risco novo além dos já listados na entrada anterior (mistura de dados de teste em
  `consumo.jsonl`, já no Backlog do `PLANO.md`).
- Ferramental de teste (scripts Playwright, WAVs sintetizados, `.claude/tmp/teste_tempo_real.py`)
  ficou todo fora do controle de versão (scratch do agente + `.claude/tmp/`), reaproveitável para a
  Etapa 2 se o PM achar útil — nenhuma ação necessária agora.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Modo tempo real: alternador entre controle de turno próprio (6s) e o da API, Etapa 2
Status: parcial — bloqueado por limitação do modelo, ver "Novas demandas / riscos"

### Feito

**Formato de `turn_detection` confirmado na doc oficial** (não presumido): guia de VAD da Realtime
API, <https://developers.openai.com/api/docs/guides/realtime-vad>, consulta em 2026-08-20 — tipo
`server_vad` (`threshold`, `prefix_padding_ms`, `silence_duration_ms`, mais `create_response`/
`interrupt_response` que a própria doc marca como "conversas fala-fala, não aplica a transcrição")
e tipo `semantic_vad` (`eagerness`). Nenhum campo numérico do `server_vad` foi fixado no código —
sem confirmação de qual valor seria certo para este projeto, a API aplica os próprios padrões em
vez de eu presumir um número.

**Backend** (`transcritor/backend/main.py`): `GET /tempo-real/token` ganhou o parâmetro de query
`modo_turno` (`tempo`, padrão — igual à Etapa 1; ou `api`) — valor fora da lista rejeitado com HTTP
422. `modo_turno="tempo"` monta `turn_detection: None` (igual antes); `"api"` monta
`turn_detection: {"type": "server_vad"}`. Resposta ganhou o campo `modo_turno` de volta, para
depuração. Escolhi query param (não `session.update` via WebSocket) porque a configuração já nasce
na criação da sessão (`client_secrets.create`), no mesmo lugar que já decidia `turn_detection` na
Etapa 1 — não precisa de uma segunda mensagem depois de conectar.

**Frontend** (`transcritor/frontend/index.html`): novo alternador **"Controle de turno"**
("turnos por tempo (6s)" / "turnos pela API"), no mesmo estilo dos alternadores existentes. Só
aparece (`hidden`) com "Transcrição em tempo real" ligado — o próprio handler de
`botaoTempoReal` alterna o `hidden` da linha; trocar de modo é bloqueado durante gravação em
andamento (mesma guarda usada pelos outros alternadores). Os três acoplamentos do enunciado:

1. **Timer de commit periódico**: só é criado (`setInterval`) quando `!modoTurnoApi`, dentro do
   handler `open` do WebSocket.
2. **Gate de silêncio**: o `if (Date.now() > fimHangoverSilencioTempoReal) return` dentro de
   `onaudioprocess` ganhou a guarda `!modoTurnoApi &&` — no modo "pela API" o áudio é sempre
   enviado (inclusive as pausas), porque a detecção do servidor só consegue perceber que a fala
   parou recebendo o silêncio. Custo: nesse modo a sessão paga pelo tempo todo, não só pela fala —
   perde a otimização desta seção do README; segue limitado pelo corte de 150s e por o usuário
   parar manualmente.
3. **Fechamento**: `pararGravacaoTempoReal` ganhou um ramo só para `modoTurnoApi` — não manda
   commit (não existe "commit final" nesse modo), para a captura local na hora e reaproveita o
   mesmo `TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS` (5s) da Etapa 1 como prazo de tolerância;
   fecha assim que o próximo `completed` chegar, ou ao esgotar o prazo. O handler do evento
   `completed` também ganhou a guarda `modoTurnoApi ||` na condição que decide fechar (não dá pra
   contar `commitsPendentesTempoReal` nesse modo, porque nunca chega a incrementar).

Corte de 150s (`LIMITE_GRAVACAO_MS`, `cortarPorSegurancaTempoReal`), registro de consumo/transcrição
(`reportarConsumoTempoReal`, disparado pelo mesmo evento `completed` nos dois modos) e o painel de
consumo não precisaram de nenhuma mudança — já eram agnósticos a como o turno foi fechado.

`transcritor/README.md`: nova seção "Controle de turno: 'por tempo' ou 'pela API' (Etapa 2)" dentro
de "Transcrição em tempo real", explicando os dois modos, os três acoplamentos e o bloqueio abaixo;
"Formato dos eventos", "Fechamento sem perder turno em voo" e a resposta de exemplo de
`GET /tempo-real/token` também atualizados para refletir o novo parâmetro.

**Achado crítico, testado direto contra a API real (não é bug no código deste projeto):** o modelo
usado no modo ao vivo, `gpt-live-transcribe` (`MODELO_TEMPO_REAL`), **rejeita qualquer
`turn_detection` que não seja `null`** — `cliente.realtime.client_secrets.create(...)` devolve
`HTTP 400`, corpo `{"message": "Turn detection is not supported for this transcription model.",
"type": "invalid_request_error", "param": "session.audio.input.turn_detection", "code":
"invalid_value"}`. Testado com `server_vad` e `semantic_vad` — os dois batem no mesmo erro. Para
descartar erro de formato (e não de modelo), testei o mesmo payload trocando só o modelo:
`gpt-4o-transcribe`, `gpt-4o-mini-transcribe` e `whisper-1` aceitaram `turn_detection: {"type":
"server_vad"}` normalmente (sessão criada, `client_secret` devolvido). Script ad-hoc, direto contra
a API real com a chave de `transcritor/.env`, não commitado (rodado via `python -` inline, não
ficou arquivo). Confirmado também pela rota já modificada do próprio backend:
`curl "http://127.0.0.1:8000/tempo-real/token?modo_turno=api"` → `{"detail":"A API da OpenAI
recusou a criação da sessão ao vivo (HTTP 400)"}`; `modo_turno=tempo` no mesmo teste devolveu um
`client_secret` válido normalmente (regressão da Etapa 1 OK nesse ponto). `modo_turno=xyz` → HTTP
422, como esperado.

**Ambiente sem navegador nem microfone** (mesma limitação já registrada na Etapa 1): não há
Chromium/Playwright nem lib de áudio instalados neste ambiente de execução (`which chromium/chrome/
msedge` vazio, `import sounddevice` falha). Havia um harness Python da Etapa 1 em
`.claude/tmp/teste_tempo_real.py` que reimplementa o protocolo (não o JS) contra a API real sem
navegador — reaproveitável para o modo "por tempo", mas **inútil para o modo "pela API"**: o
bloqueio acima acontece na criação da sessão, antes de qualquer áudio ser enviado, então nenhum
harness de protocolo passa por ele. Não tentei contornar isso trocando `MODELO_TEMPO_REAL` por
conta própria — ver por quê abaixo.

**Processo antigo na porta 8000**: havia um `python.exe` (PID 35288) já escutando, servindo código
antigo — finalizado (`taskkill /F /PID 35288`) e o backend reiniciado com o código novo
(`.venv/Scripts/uvicorn.exe`, mesmo comando do README). Deixei esse processo novo rodando (porta
8000) para o usuário já testar manualmente sem precisar subir nada — se quiser uma sessão de log
limpa, é só derrubar e subir de novo.

### Critério de pronto
- [x] Alternador presente e funcional; "turnos por tempo (6s)" continua sendo o padrão. Não
      testado ao vivo num navegador real (sem navegador neste ambiente — ver acima); confirmado por
      revisão de código que o caminho "por tempo" (`!modoTurnoApi`) é aditivamente idêntico ao da
      Etapa 1 — nenhuma linha do comportamento antigo foi alterada, só envolvida por um `if` que só
      desvia quando `modoTurnoApi === true`. `GET /tempo-real/token?modo_turno=tempo` confirmado
      via curl devolvendo `client_secret` válido, igual a antes.
- [ ] Modo "turnos pela API" transcreve de verdade — **não atende**: bloqueado na criação da sessão
      pela própria API (`gpt-live-transcribe` não aceita `turn_detection` além de `null` — ver
      achado acima). Implementação do lado do cliente/servidor está pronta para o dia em que isso
      for resolvido (troca de modelo, ou a OpenAI passar a suportar), mas não há como demonstrar
      "transcreve de verdade" enquanto essa rejeição persistir.
- [ ] Comparação com os dois textos lado a lado e custo de `consumo.jsonl` — **não atende**,
      consequência direta do item acima (não dá pra gerar o lado "pela API" da comparação) somada à
      falta de navegador/microfone neste ambiente (não dá pra gerar nem o lado "por tempo" com fala
      real aqui).
- [x] Nos dois modos, consumo e transcrição gravados pelo mesmo id — por código: `completed` dispara
      `reportarConsumoTempoReal` igual nos dois modos, sem branch por `modoTurnoApi`; não
      exercitado ao vivo no modo "pela API" pelo motivo acima.
- [x] Corte de 150s funciona nos dois modos — por código: `cortarPorSegurancaTempoReal` e
      `timeoutCorteSeguranca` não têm branch por modo, chamam `pararGravacaoTempoReal` igual;
      não exercitado ao vivo no modo "pela API".
- [x] Parar não trava nem perde o que já foi falado, nos dois modos — modo "por tempo" inalterado
      (ver acima); modo "pela API" implementado com o timeout de 5s reaproveitado (ver "Feito"),
      não exercitado ao vivo pelo motivo acima.
- [x] Formato de `turn_detection` confirmado na doc oficial, com fonte e data — ver "Feito".
- [ ] Nenhum erro novo no console — não verificável sem navegador real neste ambiente.
- [x] `transcritor/README.md` atualizado.

### Novas demandas / riscos
- **Decisão para o PM**: `MODELO_TEMPO_REAL` (`gpt-live-transcribe`) não suporta `turn_detection`
  além de `null` — "turnos pela API" não pode funcionar enquanto esse modelo continuar fixo para o
  modo ao vivo. Não troquei o modelo por conta própria porque afeta os dois modos ao mesmo tempo
  (custo — `gpt-4o-transcribe`/`gpt-4o-mini-transcribe`/`whisper-1` têm preços e comportamento
  diferentes de `gpt-live-transcribe` no README — e comportamento do modo "por tempo" já validado
  na Etapa 1), não só este alternador; não estava nos "Três acoplamentos" levantados na tarefa, e
  "Não fazer" pede para não mudar o padrão nem decisões desse porte sem o PM. Três caminhos que
  vejo, para o PM escolher (ou levantar outro):
  1. Trocar `MODELO_TEMPO_REAL` para um modelo que aceite `server_vad` (`gpt-4o-transcribe`,
     `gpt-4o-mini-transcribe` ou `whisper-1`) nos dois modos — perde a calibração/preço já
     validados de `gpt-live-transcribe` para o modo "por tempo".
  2. Usar `gpt-live-transcribe` só no modo "por tempo" e outro modelo só no modo "pela API" — os
     dois lados da comparação deixam de usar o mesmo modelo, o que complica isolar se a diferença
     de qualidade vem do controle de turno ou do modelo.
  3. Aguardar a OpenAI liberar `turn_detection` para `gpt-live-transcribe` (o erro específico
     sugere que é uma limitação atual do modelo, não do formato da requisição) e revisitar depois.
- Ambiente de execução sem navegador nem microfone (mesmo risco já registrado na Etapa 1, ainda sem
  solução) — nenhum teste desta etapa com fala real de verdade foi possível a partir daqui, nos dois
  modos.
- Backend antigo na porta 8000 (PID 35288, código anterior às Etapas 1 e 2) estava no ar antes desta
  sessão — pode indicar que o usuário (ou outra sessão) deixou um processo esquecido; sinalizando
  para não presumir que a porta 8000 sempre reflete o código atual.

### Ajuste no plano necessário?
Sim — a Etapa 2, como está descrita no `PLANO.md`/`PROXIMA_TAREFA.md`, presume que os dois modos são
comparáveis com o modelo atual; o achado acima mostra que não são, com `gpt-live-transcribe`. Sugiro
o PM decidir entre as três opções listadas em "Novas demandas / riscos" antes de considerar a Etapa
2 encerrada — o código e o README já estão prontos para qualquer uma delas (a mudança seria só o
valor de `MODELO_TEMPO_REAL`, ou movê-lo para depender do modo).
