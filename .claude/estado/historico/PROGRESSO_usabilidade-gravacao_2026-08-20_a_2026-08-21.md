# PROGRESSO arquivado — plano "usabilidade da interface de gravação"

> Entradas movidas do `PROGRESSO.md` vivo em 2026-08-21, na virada para o plano de faxina, sem
> edição de uma linha. Cobrem o plano de usabilidade da interface de gravação (5 etapas + 3
> correções aprovadas), de 2026-08-20 a 2026-08-21 — 15 entradas, 1.398 linhas.

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

## [2026-08-20] — Janela de 24 horas na escala "minuto" da linha do tempo, Etapa 2
Status: concluído

### dataviz aplicado
Antes de mexer: reli a skill, seção de interação. Apliquei especificamente: os controles novos
(deslizador + botões "Início"/"Mais recente") ficam numa única linha acima do gráfico, junto do
texto do período — o padrão de `interaction.md` para filtros de intervalo de tempo (uma linha, não
espalhados). Mantive os alvos de clique/hover que já existiam (título nativo no hover, alvo maior
que o círculo desenhado) sem alteração — a tarefa não pedia mexer neles, só na navegação.

### Feito
- `transcritor/frontend/index.html`: escala "minuto" da linha do tempo virou uma janela móvel de
  3 minutos (`LARGURA_JANELA_MINUTO_MS`) a 15px/s (`PX_POR_SEGUNDO_ESCALA_MINUTO`, 50% mais zoom
  que os 10px/s antigos), deslizável dentro das últimas 24h (`JANELA_24H_MS`) ancoradas na
  requisição mais recente (`ancoraFimJanela`, recalculada só ao abrir o painel — `abrirConsumo`).
  Navegação: deslizador `#deslizadorJanelaLinhaTempo` (arrasta livre, `Home`/`End`/setas nativas do
  `<input type="range">`) e botões `#botaoInicioJanela`/`#botaoFimJanela` para pular direto às
  pontas. Estado "ativada" (`linhaTempoAtivada`) liga por clique em `#linhaTempoConsumo` fora de um
  `.ponto-linha-tempo` (checado via `.closest`) e muda o que a roda faz (`deslizarJanela` em vez de
  `trocarEscalaLinhaTempo`) — sinalizado por contorno roxo no container e texto em
  `#estadoRodaLinhaTempo`; desativa com Esc ou clique fora (`document` click/keydown listeners).
  Escala "hora" não foi tocada (mesmo branch de sempre, todo o histórico). Recorte sem requisição
  mostra aviso em vez de retângulo vazio. `transcritor/README.md`: seção "Linha do tempo das
  requisições" reescrita para descrever a janela móvel, os dois estados da roda e a navegação.
- Dois bugs achados e corrigidos durante o teste (abaixo, "Novas demandas / riscos" tem só o que
  ficou sem resolver — estes dois já foram).

### Como testei
Ambiente sem navegador interativo, mas com Python — instalei `playwright` (`pip install
playwright && playwright install chromium`) e escrevi um driver
(`teste_janela.py` no scratchpad da sessão, não versionado) que abre `index.html` via `file://`
contra o backend real já rodando na porta 8000 (mesmo PID de antes desta sessão — `main.py`
modificado às 03:02, processo de 03:04:31, então o código já era o atual; conferido antes de
testar). Rodei contra o `consumo.jsonl` real (13 requisições, 2026-08-18 21:28 a 2026-08-20
16:01 UTC).
- **Largura do SVG, antes e depois** (critério de pronto): o código antigo (10px/s, sem janela)
  aplicado a este histórico real daria **1.776.839px** (calculado à parte, mesma fórmula que o
  código tinha: duração de 153.175s × 1,16 de folga × 10px/s). Medido no navegador **depois**:
  escala "hora" = **624px** (largura do painel, inalterada); escala "minuto" = **2.790px** sempre
  — não depende do histórico (fixo: 3min × 15px/s + 90px de folga nas bordas, ver "bug" abaixo).
- **Duas requisições próximas**: o histórico real tem pares de ~1 a ~13s de diferença em vários
  pontos (ex. `21:02:09.199` → `21:02:10.713`, 1,51s). A 15px/s isso já são ~23px de separação
  entre centros; testei visualmente com um par mais afastado (a captura de tela mostra o ponto mais
  recente da sessão isolado e clicável, com o preço legível acima). Não testei o par de 1,51s
  especificamente pelo script — é o caso mais apertado do histórico e fica **abaixo** do alvo de
  clique de 28px (2×r=14), então dois pontos a ~1,5s um do outro podem ter o alvo de clique
  sobreposto; a poucos segundos (3s+, que é o que o critério pede) já dá 45px+, sem sobreposição.
  Registrado como risco menor abaixo.
- **Deslizar do início ao fim e voltar**: cliquei `#botaoInicioJanela` (deslizador foi a 0, período
  mostrou o início das 24h) e `#botaoFimJanela` (voltou a 86220, o máximo — trecho mais recente).
  Os dois valores batem com `deslocamentoMaximoJanela()` calculado (`24h − 3min` em segundos).
- **Roda nos dois estados**: sem ativar, roda (`deltaY` negativo) trocou "Minuto" → "Hora" — texto
  do botão de zoom mudou. Ativando por clique no container (texto virou "Roda: deslizando a
  janela…"), a mesma roda **não** trocou de escala; moveu o deslizador de 86220 para 86200 (roda
  com `deltaY=-300` → `300 / (15/1000) = 20000ms` → bate com a fórmula de `deslizarJanela`).
- **Clique em ponto não ativa**: com a linha do tempo desativada, disparei o clique num
  `.ponto-linha-tempo` (via `dispatchEvent`, porque o ponto pode ficar fora da área rolada visível
  do container e o Playwright recusa clicar em algo coberto/fora de vista) — o popup abriu com o
  texto real da transcrição, e o estado "ativada" continuou `false` antes e depois.
- **Esc desativa sem fechar o painel**: aqui achei um bug real — o handler de Esc que eu adicionei
  rodava *antes* do handler antigo que fecha o modal de consumo inteiro (`!fundoConsumo.hidden` →
  `fecharConsumo()`), e os dois disparam no mesmo Esc porque estão ambos em `document`. Resultado:
  o primeiro Esc desativava a roda **e** fechava o painel inteiro, tornando a desativação invisível
  na prática. Corrigi com `evento.stopImmediatePropagation()` no meu handler quando ele de fato
  desativa — agora o primeiro Esc só sai do modo de deslizar; um Esc seguinte (já desativado) fecha
  o painel, como antes. Testado depois da correção: painel continuou aberto após o Esc, texto
  voltou a "Roda: trocando de escala".
- **Ponto na borda da janela cortado pelo SVG**: outro bug achado ao olhar a captura de tela — como
  a janela abre encostada no fim das 24h (posição padrão), o ponto mais recente cai exatamente no
  pixel final do SVG, e o `scrollLeft` calculado para deixar 40px de margem excede o máximo
  rolável do container (não há mais conteúdo depois do fim real) e é clampado pelo navegador — o
  ponto (e metade do alvo de clique) ficava colado na borda. Corrigi com uma folga fixa de desenho
  de 3s (`MARGEM_BORDA_JANELA_MS`) em cada ponta do domínio renderizado (não da janela "real" usada
  para decidir quais pontos aparecem, nem do deslizador) — é o que fez a largura ir de 2.700px
  (3min × 15px/s "nominal") para os 2.790px medidos. Confirmado visualmente na captura depois da
  correção: o ponto mais recente aparece com folga da borda direita.
- **Regressão da escala "hora"**: captura de tela mostra todos os 13 pontos do histórico completo,
  rótulo "Zoom: Hora", sem mudança visual do que já existia.
- **Console**: sem mensagens de nenhum tipo (`console` e `pageerror`) em nenhuma das duas rodadas
  completas do script.
- **O que não testei**: gravação de áudio real / dois cliques manuais de verdade a poucos segundos
  de distância (o script não grava áudio, só navega a UI existente) — o histórico real já tinha
  pares próximos o bastante para validar a métrica de pixels, então não forcei uma gravação nova
  só para isso. Também não testei o botão de zoom especificamente com a roda **ativada** (só testei
  os dois handlers de roda separadamente) — o código não faz `linhaTempoAtivada` interferir no
  handler do botão, então é de baixo risco, mas não é evidência direta.

### Critério de pronto
- [x] Largura do SVG da escala "minuto" antes e depois, colada acima — teto novo (2.790px) não
      cresce com o histórico (fixo pelas constantes, não pelos dados)
- [x] Duas requisições a poucos segundos de diferença distinguíveis e clicáveis em separado — vale
      a partir de ~3s (45px); pares abaixo de ~2s (28px) podem ter alvo de clique sobreposto, ver
      risco abaixo
- [x] Dá pra deslizar do trecho mais recente até o começo das 24h e voltar — testado com os botões
      de atalho (deslizador em si não testado por arrasto, só por `value`/evento `input`)
- [x] Roda sem ativar alterna escalas; roda ativada desliza a janela — os dois testados
- [x] Clique num ponto abre popup e não ativa o modo de deslizar
- [x] Estado (ativada ou não) visível na tela (contorno + texto) e dá para desativar (Esc sem
      fechar o painel — corrigido; clique fora, não testado por script mas mesmo mecanismo)
- [x] Botão de zoom funciona nos dois estados — funciona desativada (testado); ativada, só por
      leitura de código (ver "não testei" acima)
- [x] Janela começa no trecho mais recente ao abrir o painel
- [x] Período exibido visível na interface (texto acima do deslizador)
- [x] Recorte sem requisições mostra aviso — testado (posição "Início" caiu num recorte vazio)
- [x] Escala "hora" inalterada, mostrando todo o histórico
- [x] Números de sessão e por dia inalterados — código não tocado; não testado por não ter mudado
- [x] Preço só na escala "minuto", popup com/sem texto, eixo com hora de relógio — regressão
      exercitada nas capturas de tela
- [x] Nenhum erro novo no console — confirmado (`console` + `pageerror`, duas rodadas)
- [x] `transcritor/README.md` atualizado

### Novas demandas / riscos
- Pares de requisições a **menos de ~2s** de distância (existem alguns no histórico real, inclusive
  um de 0,16s — provavelmente de teste automatizado de sessão anterior, não uso orgânico) têm alvo
  de clique sobreposto na escala "minuto" a 15px/s. O critério da tarefa fala em "poucos segundos",
  que a 15px/s já funciona bem (3s+); não persegui esse caso mais extremo porque exigiria reduzir
  ainda mais o recorte da janela (menos contexto visível) ou aumentar bastante o px/s (recorte mais
  largo) — trade-off que não estava no escopo desta tarefa.
- Ambiente sem navegador interativo — precisei instalar `playwright` + Chromium
  (`pip install playwright && playwright install chromium`) para poder testar de verdade em vez de
  só ler o código; ficou instalado no Python do sistema desta máquina.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Correção aprovada: rolagem da janela + navegação por dias na escala "hora"
Status: concluído

### Regra de auto-scroll adotada (pedida explicitamente na tarefa)
Introduzi uma flag `rolarParaUltimoPontoNaProximaRenderizacao` (`transcritor/frontend/index.html`,
declarada perto do topo junto das outras constantes/estado da linha do tempo). O antigo
`linhaTempoConsumo.scrollLeft = Math.max(0, xUltimoPonto - larguraVisivel + margemDireita)`
(linha ~1309 antes da correção) rodava em toda renderização — a causa já localizada pelo PM. Agora
esse scroll automático só roda quando a flag está ligada, e ela só é ligada em três pontos: (1)
`abrirConsumo()` — abrir o painel; (2) `trocarEscalaLinhaTempo()` — trocar de escala (botão de zoom
ou roda desativada); (3) o clique em "Mais recente" (`botaoFimJanela`). Em qualquer outro redesenho
— roda ativada (`deslizarJanela`) ou arrastar o `deslizadorJanelaLinhaTempo` — o container abre pelo
início do recorte redesenhado (`scrollLeft = 0`), consumindo a flag (ela é desligada assim que usada
uma vez). Justificativa: como a cada giro o recorte inteiro (janela de minutos) se desloca no tempo
por uma quantidade equivalente ao gesto, manter sempre `scrollLeft = 0` produz uma rolagem visual
contínua no mesmo sentido — é o próprio recorte que "anda", não o scroll interno brigando com ele.
"Início (24h atrás)" não precisou de tratamento especial: `scrollLeft = 0` já é exatamente o que esse
botão quer mostrar.

### Como testei (rolagem)
Sem navegador interativo neste ambiente, mas com Python + Playwright já instalados de sessões
anteriores (confirmado: `python -c "import playwright"` OK, Chromium instala e abre). Backend real
já rodando na porta 8000 — conferido antes de testar: processo (PID 38780) iniciado às 03:04:31,
depois da última escrita em `main.py` (03:02:35), então servindo código atual (backend não foi
tocado nesta tarefa de qualquer forma). `index.html` aberto via `file://` (URLs da API são
absolutas, `http://127.0.0.1:8000/...`, então funciona igual a servir por HTTP). Script em
`%TEMP%\...\scratchpad\teste_janela_dia.py` (fora do repo).
- Reproduzido o bug e a correção lado a lado: coloquei a janela numa posição do **meio** do
  intervalo de 24h (não numa ponta, onde o clamp mascara o efeito) e dei 8 giros de roda seguidos
  no mesmo sentido (`deltaY = -100` cada, o valor "clique de roda" normalizado por navegador, não o
  múltiplo sintético de 300 que o Playwright usa por padrão). Medido a cada giro:
  `deslocamentoJanelaMs` e `scrollLeft`. Resultado: `deslocamentoJanelaMs` variou
  43103333 → 43096666 → 43090000 → ... → 43056666 — **-6666,67ms por giro, exatos e constantes**,
  sempre no mesmo sentido (nenhuma inversão); `scrollLeft` ficou em **0 nos 8 giros**, nunca pulou
  para o fim. Antes da correção, o mesmo cenário faria `scrollLeft` saltar para
  `xUltimoPonto - larguraVisivel + margemDireita` a cada giro — perto do fim do recorte — dando a
  sensação de "clicar uma vez e já ir pro fim", que é exatamente a queixa original.
- Fluxo real de usuário (cliques de verdade, não chamadas diretas de função) em
  `teste_fluxo_real.py`: abrir o painel → escala "minuto" → clicar em área vazia do container para
  ativar → 5 giros de roda para trás (`deltaY = -100`) → o texto do período foi de
  "21:12:38 – 21:15:38" para "21:12:04 – 21:15:04" (34,8s de deslocamento em 5 giros, ≈ 6,97s/giro,
  dentro do range de arredondamento dos 6,67s teóricos) — **sempre diminuindo, nunca voltando para o
  fim**. Esc desativou sem fechar o painel (confirmado, ver critério "console" abaixo).

### Sensibilidade da roda (item 2 da tarefa)
Medido com `deltaY = 100` por giro (o "clique de roda" que a doc do PLANO já usava como referência,
não o múltiplo de 300 do Playwright): **6.666,67ms (6,7s) por giro**, valor exato — bate com a conta
já feita no PLANO.md (`100 / (15/1000)`). Automatizei girar a roda repetidamente a partir do início
da janela (`deslocamentoJanelaMs = 0`) até atravessar o recorte inteiro de 3 minutos (180.000ms):
**27 giros**. Contexto de uso real: o container mede **624px de largura visível** (`clientWidth`,
tamanho de painel testado) — a 15px/s isso são ~41,6s de conteúdo visíveis por vez, ou **~6,2 giros
de roda para percorrer uma tela cheia de conteúdo**. Considerei confortável (nem lento — não é
preciso girar dezenas de vezes para mover um pouco — nem rápido demais — não atravessa a tela toda
num giro só) e **não ajustei** `PX_POR_SEGUNDO_ESCALA_MINUTO`; os números acima são o registro pedido
pela tarefa para essa decisão.

### Navegação por dias na escala "hora"
`transcritor/frontend/index.html`: a escala "hora" deixou de comprimir o histórico inteiro
(`Math.min`/`Math.max` sobre todas as `validas`, com folga de 8%) e passou a mostrar **um dia civil
por vez** (meia-noite a meia-noite, hora local) — mesmo bloco `if (escalaLinhaTempo === "hora")`
dentro de `renderizarLinhaTempoConsumo`, agora usando `diaSelecionadoHora` (novo estado, meia-noite
em ms) com a mesma folga de desenho de 3s (`MARGEM_BORDA_DIA_MS`, mesmo valor de
`MARGEM_BORDA_JANELA_MS` da escala "minuto", por analogia — evita o ponto bem em cima da virada de
dia ficar com o alvo de clique colado na borda do SVG). Novo bloco de UI
(`#navegacaoDiaLinhaTempo`, reaproveitando as classes CSS já existentes da navegação da escala
"minuto" — nenhuma CSS nova) com texto "Dia: dd/mm/aaaa" e botões "◀ Dia anterior" / "Dia seguinte
▶", visível só na escala "hora" (`atualizarNavegacaoDia`, chamada ao final do render, espelhando
`atualizarNavegacaoJanela`).
- **Limite navegável**: `limitesDiasComDados()` calcula `[dia da requisição mais antiga, dia da
  requisição mais recente]` (não `[ancoraFimJanela - 24h, ancoraFimJanela]`, que é só o alcance da
  escala "minuto") — `navegarDia()` recusa sair desse intervalo, e os botões ficam `disabled` nas
  pontas (reaproveita o seletor CSS `:not(:disabled)` que já existia para o hover). Testado nos dois
  sentidos com o histórico real (3 dias: 18, 19 e 20/08/2026): dois cliques em "Dia anterior" a
  partir do dia mais recente percorrem os 3 dias reais e desabilitam corretamente no dia 18; chamar
  `navegarDia(-1, ...)` diretamente (contornando o `disabled` da UI) confirma que a própria função
  também recusa, não só o botão.
- **Dia sem requisição**: o histórico real não tem nenhum buraco (todos os 3 dias têm dado), então
  testei sinteticamente — via `evaluate`, renderizei uma lista de 2 requisições fictícias (hoje e
  2 dias atrás, com "ontem" vazio no meio) e chamei `navegarDia(-1, ...)` a partir de hoje. Resultado:
  caiu no dia vazio (confirmei pela data), mostrou o aviso "Nenhuma requisição neste dia." (reusa o
  mesmo parágrafo `.dica` que a escala "minuto" já usava para recorte vazio, agora com texto
  condicional por escala) e o botão "Dia anterior" continuou habilitado (ainda dá pra chegar no dia
  mais antigo, que tem dado) — não veio um retângulo mudo.
- **Eixo com hora de relógio, preservado**: sem tocar a lógica da escada de passos
  (`ESCADA_PASSOS_EIXO_TEMPO`/`escolherPassoEixo`), o dia de 24h com 624px de largura escolheu
  sozinho o passo de 6h — testado, rótulos exatos: `["20/08 00h", "06h", "12h", "18h", "21/08
  00h"]`. Sem rótulo de preço nos pontos (confirmado: nenhum texto começando com "$" no SVG da
  escala "hora"; a escala "minuto" continua mostrando, confirmado no mesmo teste).

### Concordância entre as duas escalas (item 4, "o ponto mais fácil de errar")
Proposta adotada, com o motivo: as duas escalas guardam o período de formas estruturalmente
diferentes (`diaSelecionadoHora`, um único timestamp de meia-noite; `ancoraFimJanela` +
`deslocamentoJanelaMs`, uma âncora de 24h mais um deslocamento dentro dela) — não dá pra ter uma
única variável compartilhada. A tradução acontece só no momento da troca, dentro de
`trocarEscalaLinhaTempo` (antes de trocar `escalaLinhaTempo`, para as duas funções abaixo ainda
lerem o estado "antigo"):
- **hora → minuto** (`sincronizarMinutoComDia`): reancora a janela de 24h da escala "minuto" na
  **última requisição do dia selecionado** (não em `Date.now()`, nem direto na meia-noite do dia
  seguinte). A cautela de usar a última requisição do dia, e não a meia-noite, foi para não quebrar
  o caso comum: se o dia escolhido é hoje, a última requisição do dia **é** a mais recente de todo o
  histórico — reduz exatamente ao comportamento já validado na Etapa 2 ("abre no trecho mais
  recente"). Só cai na meia-noite do dia seguinte quando o dia não tem nenhuma requisição (não há
  onde ancorar de verdade). Sem essa cautela (minha primeira versão ancorava sempre na meia-noite),
  o caso comum quebraria: trocar pra "minuto" sem nunca ter navegado por dia abriria a janela
  encostada numa meia-noite sem nenhuma requisição por perto — reproduzi esse regressão durante o
  desenvolvimento antes de corrigir (não chegou a ficar no código final).
- **minuto → hora** (`sincronizarDiaComMinuto`): o dia mostrado passa a ser o dia civil do **início**
  do recorte visível (não o fim — evita ambiguidade se o recorte cruzar a meia-noite), com clamp para
  dentro do intervalo de dias com dado (nunca viola o próprio critério da escala "hora").
- Testado nos dois sentidos com o histórico real: fui para o dia 20/08 (hoje, tem dado) na escala
  "hora", troquei pra "minuto" — janela caiu em `17:45:27–17:48:27` (hora local), que bate
  exatamente com o horário da última requisição real de hoje. Fui para o dia 18/08 (2 dias atrás) na
  escala "hora", troquei pra "minuto" — janela caiu dentro do dia 18/08 local (confirmado convertendo
  o horário UTC retornado, `2026-08-19T00:12–00:15Z`, para local -03:00 → 18/08 21:12–21:15). Voltei
  pra "hora" — dia voltado foi 18/08 (sem deriva, mesmo dia de antes da troca). Repeti o ciclo
  completo hora→minuto→hora com cliques de UI reais (não só `evaluate`) em `teste_fluxo_real.py` e
  bateu igual.
- **Cada escala só recalcula do zero (âncora/dia mais recente) quando ainda não tem estado nesta
  abertura do painel** — mesmo padrão de `garantirAncoraJanela` já existente, estendido para
  `garantirDiaSelecionado`. Fechar e reabrir o painel volta as duas para o mais recente (testado:
  após navegar e trocar de escala, fechei com "✕" e reabri — voltou pro dia 20/08).

### Regressões conferidas
- **Roda sem ativar continua trocando de escala** (critério explícito da tarefa): testado — com
  `linhaTempoAtivada = false`, girar a roda sobre a escala "hora" trocou para "minuto".
- **Agregados (sessão e por dia) inalterados**: comparei `ultimoConsumoCarregado.sessao` e `.por_dia`
  antes/depois de navegar de dia e trocar de escala — string idêntica (não são recalculados a partir
  do recorte exibido; vêm direto de `dados.sessao`/`dados.por_dia`, que eu não toquei).
- **Popup com/sem texto, preço só na escala "minuto", clique em ponto não ativa o modo de
  deslizar**: clique num ponto (via `dispatchEvent`, mesma técnica da Etapa 2 — o ponto pode estar
  fora da área rolada visível do container) abriu o popup com o texto real de uma transcrição da
  gravação de teste. Preço: confirmado ausente na escala "hora" e presente na "minuto" (ver acima).
- **Esc desativa sem fechar o painel**: fluxo real (`teste_fluxo_real.py`) — ativei, girei a roda,
  apertei Esc: `linhaTempoAtivada` foi para `false` e o painel continuou aberto.
- **Console**: zero mensagens de qualquer tipo (`console` e `pageerror`) nas duas rodadas completas
  (`teste_janela_dia.py` e `teste_fluxo_real.py`) — nem o 404 do favicon apareceu desta vez (não
  fiz nenhuma chamada que dispare o carregamento do ícone da aba no teste via `file://`).
- `node --check` no `<script>` extraído do HTML confirma sintaxe válida depois de todas as edições.

### `transcritor/README.md`
Seção "Linha do tempo das requisições" atualizada: bullet da escala "hora" reescrito para descrever
a navegação por dias (dia exibido, limites, dia vazio); novo bullet "As duas escalas concordam sobre
o período exibido" explicando a sincronização hora↔minuto e a regra de quando cada uma recalcula do
zero; bullet da roda ativada ganhou os números de sensibilidade (6,7s/giro, 27 giros pra atravessar
a janela, ~6 giros por tela) e a ressalva de que na escala "hora" a roda ativada fica sem efeito (ver
"Novas demandas" abaixo); bullet de "navegação horizontal fina" reescrito explicando a nova regra de
quando o auto-scroll acontece e por quê (a correção do bug relatado).

### Critério de pronto
- [x] Rolar com a linha do tempo ativada desliza continuamente, sem saltar para o fim — testado com
      8 giros seguidos no mesmo sentido a partir do meio da janela: `deslocamentoJanelaMs` moveu
      -6.666,67ms por giro, exato e constante; `scrollLeft` ficou em 0 nos 8 giros (nunca foi para o
      fim). Fluxo real com cliques de UI deu o mesmo padrão (34,8s em 5 giros).
- [x] Rolar sem ativar continua alternando as escalas (regressão da Etapa 2) — testado.
- [x] Sensibilidade confirmada com número: 6,7s por giro (deltaY=100), 27 giros para atravessar a
      janela de 3min, ~6,2 giros para percorrer uma tela cheia (624px) — considerado confortável,
      sem ajuste.
- [x] Escala "hora" mostra um dia por vez, com navegação para o dia anterior e o seguinte — testado.
- [x] O dia exibido está visível na tela — texto "Dia: dd/mm/aaaa" acima do gráfico.
- [x] Não dá para navegar além do intervalo com dados; dia vazio mostra aviso — os dois testados (um
      com histórico real, o outro com dado sintético por não haver buraco no histórico real).
- [x] Trocar de escala preserva o período olhado, nos dois sentidos — testado hora→minuto e
      minuto→hora, com dia recente (reduz ao comportamento antigo) e com dia antigo (2 dias atrás).
- [x] Números de sessão e por dia inalterados — comparação de string antes/depois.
- [x] Popup com texto e sem texto, preço só na escala "minuto", eixo com hora de relógio — tudo
      ainda funcionando. ("Popup sem texto" não testado nesta tarefa especificamente — não achei
      registro sem `texto` no histórico real à mão; o caminho de código não foi tocado, só o dado
      que chega até `abrirPopupRequisicao`, que continua o mesmo de antes.)
- [x] Nenhum erro novo no console — zero mensagens em todas as rodadas (nem o 404 do favicon
      apareceu, por não ter disparado o carregamento do ícone via `file://` desta vez).
- [x] `transcritor/README.md` atualizado.

### Novas demandas / riscos
- **Achado durante o teste, fora do escopo desta tarefa — não mexi**: a "ativação" da linha do tempo
  (clique em área vazia do container, liga `linhaTempoAtivada`) não checa a escala atual — dá pra
  ativar também na escala "hora". Como `deslizarJanela` já tinha (antes desta tarefa) a guarda
  `if (escalaLinhaTempo !== "minuto") return`, o efeito é que a roda fica **sem nenhum efeito** (nem
  desliza, nem troca de escala) enquanto ativado na "hora" — pra sair, precisa Esc, clicar fora, ou o
  botão de zoom. Não é regressão desta tarefa (o guard já existia assim desde a Etapa 2, quando
  "hora" não tinha nada pra deslizar de qualquer forma) e não está nos critérios de pronto, mas ficou
  mais alcançável agora que "hora" também é um container clicável com conteúdo navegável. Documentei
  o comportamento real no README (em vez de descrever um comportamento que não existe) e deixo aqui
  para o PM decidir se vale ativar `trocarEscalaLinhaTempo` a partir da roda também quando ativado na
  "hora" (por simetria) — não implementei por não estar no pedido e para não expandir escopo.
- Nenhum risco novo além dos já registrados no Backlog do `PLANO.md` (mistura de dados de teste em
  `consumo.jsonl` — esta tarefa não gravou nada novo lá, só leu o histórico existente e chamou
  funções de renderização no navegador, sem tocar a API OpenAI nem o backend).
- Ambiente de execução sem navegador "nativo" interativo (mesma limitação de sempre) — reaproveitei
  o Python + Playwright + Chromium já instalados nas sessões da Etapa 1/2 desta máquina; nenhuma
  dependência nova entrou em `transcritor/`. Scripts de teste ficaram em
  `%TEMP%\...\scratchpad\teste_janela_dia.py` e `teste_fluxo_real.py`, fora do repositório.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Faxina (Etapa 3), Item a0: roda na escala "hora" quando a linha do tempo está ativada
Status: concluído

### Feito
- `deslizarJanela` (`frontend/index.html`) não faz mais no-op na escala "hora": chama `navegarDia`
  (mesma função dos botões "Dia anterior/seguinte"), respeitando o limite de dias com dado.
- `atualizarBadgeEstadoRoda` e `trocarEscalaLinhaTempo` ajustados para o texto do badge ("Roda: ...")
  acompanhar a escala atual.

Testado com Playwright + Chromium headless contra `http://127.0.0.1:8000/` (dado real de
`consumo.jsonl`, cobrindo 18–20/08). Ativei a roda na escala "hora" (dia inicial "20/08/2026"):
deltaY<0 → "19/08/2026"; deltaY>0 → voltou a "20/08/2026"; com "Dia seguinte" desabilitado (dia
mais recente), deltaY>0 não passou do limite. Troquei pra "minuto": roda ativada deslizou a janela
(texto do período mudou a cada giro). Desativei (Esc): roda passou a trocar de escala ("Zoom:
Minuto" → "Zoom: Hora"). Zero erros de console nas 3 checagens.

### Critério de pronto
- [x] Ativada na escala "hora", a roda navega entre dias, respeitando os limites de dias com dado;
      ativada na "minuto" continua deslizando a janela; desativada continua alternando as escalas —
      os três testados

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Faxina (Etapa 3), Item a: remoção do alternador de controle de turno
Status: concluído

### Feito
- Frontend: removidos o alternador "Controle de turno" (HTML/CSS) e todo o JS ramificado por
  `modoTurnoApi` (gate de silêncio, timer de commit, fechamento do turno em voo, query string do
  token) em `frontend/index.html`.
- Backend: removidas `MODO_TURNO_TEMPO`/`MODO_TURNO_API`/`MODOS_TURNO_PERMITIDOS`;
  `GET /tempo-real/token` não aceita mais `modo_turno` — sempre abre com `turn_detection: None`.
- Trecho removido salvo em `.claude/estado/historico/CONTROLE_TURNO_REMOVIDO_2026-08-20.md` antes
  da remoção, com cabeçalho explicando origem e motivo.

`grep -r "modo_turno\|MODO_TURNO\|ControleTurno" transcritor/` → zero ocorrências. Sessão real de
navegador (Playwright, microfone falso alimentado por WAV sintetizado via SAPI PT-BR): liguei o
modo tempo real, gravei ~9s — 2 turnos reais contra `gpt-live-transcribe`
(`turn_detection: null`), status final "Gravação em tempo real encerrada." (sucesso), 2 linhas
novas em `consumo.jsonl` (6,0s e 4,0s) com par em `transcricoes.jsonl` pelo mesmo id (ex.:
`e4ac02bf3d1348ebab436165d8fd7561`). Zero erros de console.

Não testei o cenário antigo "turnos pela API" — já estava documentado como bloqueado (recusado
pela API com o modelo atual) antes desta tarefa, não havia comportamento funcional a preservar.

### Critério de pronto
- [x] Alternador some da interface e `modo_turno` some do backend; modo tempo real continua
      funcionando normalmente com `turn_detection: None` — testado com sessão real
- [x] Trecho removido salvo em `.claude/estado/historico/` antes da remoção

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Faxina (Etapa 3), Item b: botão de copiar a transcrição
Status: concluído

### Feito
- Botão "Copiar texto" abaixo da caixa "Transcrição por voz" (`frontend/index.html`), usa
  `navigator.clipboard.writeText` e reaproveita `mostrarStatusGravacao` (mesma área de status da
  gravação) para confirmar a cópia; caixa vazia mostra aviso e não copia.

Sessão real de navegador: preenchi a caixa, cliquei em copiar, li o clipboard via
`navigator.clipboard.readText()` — bateu com o texto digitado; status mostrou "Texto copiado para
a área de transferência.". Com a caixa vazia, cliquei de novo: status mostrou "Nada para copiar —
a caixa de transcrição está vazia." e o clipboard não foi alterado.

### Critério de pronto
- [x] Botão copia o texto e mostra confirmação; caixa vazia tratada

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Faxina (Etapa 3), Item c: renomear POST /consumo/tempo-real
Status: concluído

### Feito
- Backend: `POST /consumo/tempo-real` → `POST /tempo-real/turno-concluido` (nome reflete que grava
  consumo **e** transcrição, não só consumo); função renomeada para `turno_concluido_tempo_real`.
- Frontend: `URL_CONSUMO_TEMPO_REAL` → `URL_TURNO_CONCLUIDO_TEMPO_REAL`, apontando pra rota nova.
- README atualizado nos 2 pontos que citavam a rota antiga.

Mesma sessão real do item (a): a chamada em tempo real bateu na rota nova — confirmado em
`openapi.json` do backend e por `curl -X POST .../tempo-real/turno-concluido` → 200; a rota antiga
`/consumo/tempo-real` responde 404 agora. As 2 linhas novas da sessão real batem 1:1 por id entre
`consumo.jsonl` e `transcricoes.jsonl` (mesmos ids do item a).

### Critério de pronto
- [x] Rota renomeada, frontend e README atualizados; registro de consumo e transcrição continua
      funcionando de ponta a ponta — testado com sessão real, conferindo as duas linhas com o
      mesmo id

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Faxina (Etapa 3), Item d: favicon
Status: concluído

### Feito
- `GET /favicon.ico` (`backend/main.py`) gera em memória um ícone 16x16 sólido (cor #7c3aed) via
  `struct`, sem arquivo de imagem nem dependência nova.

`curl -D- http://127.0.0.1:8000/favicon.ico` → `HTTP/1.1 200 OK`, `content-type: image/x-icon`,
`content-length: 1150`. Sessão real de navegador (Playwright) carregando a página: zero mensagens
de console (antes desta tarefa, o 404 do favicon aparecia sempre — ver entradas anteriores deste
arquivo).

### Critério de pronto
- [x] `GET /favicon.ico` responde, e o 404 some do console

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não.

## [2026-08-20] — Faxina (Etapa 3): critérios gerais (regressão e ambiente)
Status: concluído

### Feito
Checagem de regressão do painel de consumo, além das trocadas por item acima, com Playwright
contra dado real: preço só como rótulo na escala "minuto" (`[]` na "hora", `['$0.0017',
'$0.0011']` na "minuto"), eixo com hora de relógio nas duas escalas (`HH:MM` / `dd/mm HHh`),
popup abre ao clicar num ponto ("gpt-4o-transcribe — US$ 0.0005 — 20/08/2026, 01:23:37"). Zero
erros de console em todas as sessões desta tarefa (7 rodadas de Playwright ao todo).

Backend antigo já estava de pé na porta 8000 (PID de sessão anterior) — encerrado e reiniciado com
o código desta tarefa antes de qualquer teste, conforme aviso da tarefa. Deixei o backend novo
rodando em segundo plano (`.venv\Scripts\uvicorn.exe`, porta 8000) para quem for revisar visualmente.

Custo real de API desta tarefa: 2 turnos de tempo real (6,0s + 4,0s) ≈ US$ 0,0028 — soma ao
Backlog já conhecido de mistura de dados de teste em `consumo.jsonl`/`transcricoes.jsonl`.

Ferramental de teste (scripts Playwright, WAV sintetizado por SAPI) ficou em `%TEMP%\...\scratchpad\`,
fora do repositório — mesma prática das sessões anteriores.

### Critério de pronto
- [x] Nenhuma regressão no painel: janela móvel, navegação por dias, popup, preço só na escala
      "minuto", eixo com hora de relógio
- [x] Nenhum erro novo no console
- [x] `transcritor/README.md` atualizado nos pontos afetados

### Novas demandas / riscos
- Mesma limitação de mistura de dados de teste em `consumo.jsonl` já registrada no Backlog do
  `PLANO.md` — nenhuma ação nova necessária.

### Ajuste no plano necessário?
Não.

## [2026-08-21] — Faixa de áudio com histórico + botão de cancelar, Etapa 4
Status: concluído

### Contexto do achado do PM
Confirmei o diagnóstico: `animarBarrasNivel` (antiga) calculava um único RMS por quadro de
animação (`requestAnimationFrame`, ~60/s) e aplicava esse **mesmo valor** a todas as 12 barras,
diferenciando-as só por `0.7 + 0.3*Math.sin(indice*1.3 + Date.now()/150)` — um seno cosmético sem
memória nenhuma. Reescrevi para um buffer de amostras que anda no tempo, como pedido.

### Feito — `transcritor/frontend/index.html`

**1) Faixa com histórico**
- Novo estado: `amostrasNivel` (array de `NUM_BARRAS_NIVEL`=12 RMS, mais recente na última
  posição) e `INTERVALO_AMOSTRA_BARRAS_MS = 250`. `amostrarNivel()` roda em `setInterval` fixo (não
  mais a cada quadro de animação) — lê o `AnalyserNode`, calcula RMS, `push`/`shift` no buffer e
  redesenha. `iniciarAnalisadorNivel` zera o buffer antes de começar (faixa limpa) e chama
  `renderizarBarrasNivel()` uma vez de imediato, antes da primeira amostra. `pararAnalisadorNivel`
  também zera o buffer e some com a faixa. Vale para os dois modos: `iniciarAnalisadorNivel` é
  chamado tanto por `iniciarGravacaoRapida` quanto pelo handler `"open"` de
  `iniciarGravacaoTempoReal`, sem duplicar código.
- **Segundos de histórico com os valores atuais: 12 barras × 250ms = 3,0 segundos.** Documentado em
  comentário no código (`renderizarBarrasNivel`/declaração de `amostrasNivel`) e no README.
- Achado durante o teste (ver abaixo) e corrigido nesta mesma tarefa: a fórmula original de altura
  era `Math.max(0.15, Math.min(1, rms*6))` — um **clamp**, não uma base. Qualquer RMS abaixo de
  0,025 (o caso comum de silêncio real, nunca zero digital perfeito) caía sempre no mesmo valor
  fixo (15%), fazendo a faixa parecer congelada mesmo com o buffer variando de verdade por trás.
  Troquei para `Math.min(1, 0.15 + rms*6)` — o piso vira uma base **somada**, então a variação
  pequena do ruído de fundo continua visível acima dele. Constatado (não só lido no código): ver
  item de teste "silêncio" abaixo, antes e depois da correção.

**2) Botão quadrado durante a gravação**
- Segundo `<svg id="iconeParar">` (retângulo arredondado) dentro de `#botaoGravacaoRapida`, ao lado
  do `<svg id="iconeMicrofone">` já existente. A troca é só CSS: `.gravando #iconeMicrofone {
  display: none }` / `.gravando #iconeParar { display: block }` — nenhum JS novo, reaproveita as
  quatro chamadas já existentes de `classList.add/remove("gravando")` (gravação normal e tempo
  real). Pulso e troca de `aria-label` inalterados.

**3) Botão ✕ de cancelar**
- Novo `#botaoCancelarGravacaoRapida`, ao lado do botão redondo, `hidden` por padrão. Mostrado só
  no `"open"` do WebSocket (tempo real) e logo após `mediaRecorderRapido.start()` (gravação normal);
  escondido em `pararGravacaoRapida`, no início de `pararGravacaoTempoReal`, em
  `cancelarGravacaoTempoReal` e no handler de `"close"` inesperado do WebSocket.
- **Gravação normal**: `cancelarGravacaoRapida()` liga a flag
  `cancelamentoGravacaoRapidaEmAndamento` e chama o mesmo `pararGravacaoRapida()` de sempre; o
  handler `"stop"` do `MediaRecorder` checa essa flag **antes** da checagem de silêncio e do envio
  — se ligada, descarta `pedacosRapidos`, mostra "Gravação cancelada." e retorna, sem montar o
  `Blob` nem chamar `enviarGravacaoRapida`.
- **Tempo real**: `cancelarGravacaoTempoReal()` é uma função própria (não reaproveita
  `pararGravacaoTempoReal`, porque o comportamento diverge de propósito): chama
  `limparRecursosTempoReal()` (para captura local, timers, analisador — sem mandar o commit final
  de `bytesDesdeUltimoCommitTempoReal`), fecha o WebSocket na hora, zera `commitsPendentesTempoReal`
  sem esperar por eles, e mostra "Gravação cancelada." **Regra sem exceção da caixa de
  transcrição**: o handler `"message"` do WebSocket agora começa com
  `if (cancelamentoTempoRealEmAndamento) return;` — cobre `delta` e `completed` juntos, então nem um
  turno já comitado antes do cancelamento (que pode responder alguns instantes depois, já fora do
  nosso controle) chega a tocar `turnoAtualTempoReal`/`textoFinalizadoTempoReal`/a caixa. Efeito
  colateral aceito conscientemente: se o `completed` de um commit legítimo (do timer de 6s) chegar
  **depois** do clique em cancelar, ele também é descartado — não vira linha em `consumo.jsonl`
  nem `transcricoes.jsonl`, mesmo já cobrado pela OpenAI. A tarefa só exige que a caixa nunca seja
  tocada, não que todo centavo já gasto fique registrado localmente; documentei essa nuance aqui
  para o PM decidir se é aceitável.

### Como testei — Playwright + Chromium headless, backend real na porta 8000
Confirmado antes de testar que o backend já estava de pé servindo o `index.html` atualizado
(`grep -c botaoCancelarGravacaoRapida` no HTML servido → 12 ocorrências); esta tarefa não mexeu no
backend, então não precisou reiniciar. Microfone falso alimentado por dois WAVs sintéticos (fora do
repositório, `%TEMP%\...\scratchpad\`): um com fala real em PT-BR (SAPI, reaproveitado de uma tarefa
anterior) e um novo, de ruído ambiente bem baixo (amplitude máxima 300/32767 ≈ 0,9% do full-scale,
abaixo de `LIMIAR_SILENCIO`, mas não zero — silêncio real nunca é zero digital perfeito).

**Barras andam (fala real)** — alturas de todas as 12 barras em dois instantes (1,2s de intervalo):
```
t1: ['15%','15%','15%','15%','15%','15%','15%','100%','35.2255%','86.2631%','100%','21.6871%']
t2: ['15%','100%','35.2255%','86.2631%','100%','21.6871%','32.7748%','37.7612%','78.9176%','26.8317%','18.5278%','15%']
```
Deslocamento visível a olho: `t1[7..11]` (`100, 35.2255, 86.2631, 100, 21.6871`) reaparece em
`t2[1..5]` — o mesmo trecho de fala "andou" 6 posições na faixa, exatamente o histórico
funcionando (não congelado, não redecorado por seno).

**Silêncio não congela (antes e depois da correção do piso)** — mesmo WAV de ruído ambiente:
- **Antes** da correção (piso como clamp): `t1` e `t2` idênticos, ambos travados em `15%` fixo em
  todas as 12 barras — falha real, não hipotética (rodei o teste, vi travar, só depois corrigi).
- **Depois** (piso somado): `t1: [...15%×8, 18.9087%, 18.4416%, 18.4416%, 18.4166%]`,
  `t2: [...deslocado, 18.5278%, 18.8086%, ...]`, `t3` também diferente de `t2` — todas ≤ 19% (bem
  abaixo do limiar visual de "tem fala"), e mudando a cada instante. Confirmado 2x (rodada isolada e
  dentro da suíte completa).

**Faixa começa limpa**: alturas capturadas no instante exato em que `.gravando` aparece (antes do
primeiro `setInterval` disparar) → `['15%']×12` nas duas rodadas testadas.

**Botão quadrado + ✕ só durante a gravação**: com a gravação ligada, `#iconeParar` visível,
`#iconeMicrofone` escondido, `#botaoCancelarGravacaoRapida` sem o atributo `hidden`. Confirmado nos
dois modos (gravação normal e tempo real).

**Cancelar na gravação normal — antes/depois**:
```
status: "Gravação cancelada."
texto ANTES: 'texto pré-existente antes do teste de cancelamento'
texto DEPOIS: 'texto pré-existente antes do teste de cancelamento'   (idêntico)
consumo.jsonl:      178 -> 178   (não cresceu)
transcricoes.jsonl:  118 -> 118   (não cresceu)
```
Confirmei também: botão sem `.gravando`, `#botaoCancelarGravacaoRapida` escondido de novo,
cronômetro e faixa escondidos, e uma gravação nova inicia normalmente logo em seguida (clique →
`.gravando` aparece sem erro).

**Parar (quadrado) normal, gravação comum — regressão**: gravei 3s de fala real, cliquei em parar
(não cancelar) → texto "Teste da tarefa de faxina." chegou, `consumo.jsonl` 178→179 (+1). Segue
funcionando.

**Cancelar no tempo real — antes/depois (com um turno já comitado antes do cancelamento)**: gravei,
esperei o primeiro turno do timer periódico de 6s chegar de verdade (`wait_for_function` no
conteúdo da caixa, sem timeout fixo arbitrário), **então** cliquei em cancelar:
```
status: "Gravação cancelada."
texto ANTES do cancelamento: ' A tarefa de'   (1º turno já tinha chegado)
texto DEPOIS do cancelamento: ' A tarefa de'  (idêntico — nem esse texto nem nada novo)
consumo.jsonl:      179 -> 179   (não cresceu)
transcricoes.jsonl: 119 -> 119   (não cresceu)
```
Ou seja: o trecho ainda não comitado no momento do clique não virou turno novo, e a caixa não foi
tocada — nem pelo cancelamento em si, nem por nenhum evento em voo depois dele.

**Parar (quadrado) normal no tempo real — regressão, id batendo nos dois arquivos**: nova gravação,
falei ~3s (menos que os 6s do timer, só o commit final deveria rodar), cliquei em parar:
```
texto: "Te da tarefa de faxina. Removendo"
consumo.jsonl: 179 -> 180 (+1)
nova linha consumo.jsonl:      {"id": "63f20b3f3bda4a43b126f0712e1935f7", "modelo": "gpt-live-transcribe", "segundos": 4.0, "custo_usd": 0.0011333...}
última linha transcricoes.jsonl: {"id_consumo": "63f20b3f3bda4a43b126f0712e1935f7", "texto": "Te da tarefa de faxina. Removendo"}
```
Mesmo id nos dois arquivos — confirmado por código (`ids_transcricao.issubset(ids_consumo)` →
`True`), não só por leitura visual.

**Gate de silêncio (regressão)**: gravação normal com o WAV de ruído ambiente, parei (não cancelei)
depois de 2,5s — toast "Não foi identificado nenhuma fala" apareceu, `consumo.jsonl` não cresceu
(181→181). Continua funcionando com o novo `amostrarNivel` (que também alimenta `picoVolumeRapido`,
só que a cada 250ms em vez de a cada quadro de animação).

**Painel de consumo (regressão)**: abriu normalmente, SVG da linha do tempo presente — não mexi
nesse código nesta tarefa, checagem rápida de sanidade.

**Console**: zero erros/avisos em todas as rodadas (7 sessões de navegador, incluindo as duas que
precisaram ser refeitas por causa da correção do piso das barras e de uma falha pontual — ver
abaixo).

**Custo real de API desta tarefa**: ~US$ 0,005–0,006 (2 transcrições curtas via `/transcrever`
[~3s de fala cada] + 2 turnos de tempo real (6s + 4s) numa rodada, mais a repetição da rodada de
tempo real depois de uma falha pontual ao reiniciar a gravação — ver "Novas demandas" abaixo).

### Critério de pronto
- [x] Falando, as barras **andam** — evidência de deslocamento colada acima
- [x] Quantos segundos de histórico: **3,0s** (12 barras × 250ms)
- [x] Em silêncio, a faixa continua andando com barras baixas (não congela) — confirmado após
      corrigir o piso de clamp para base somada (achado durante o próprio teste desta tarefa)
- [x] Gravação nova começa com a faixa limpa — confirmado (`['15%']×12` no instante inicial)
- [x] Durante a gravação o botão mostra um quadrado; fora dela, o microfone — confirmado nos dois
      modos
- [x] X aparece só durante a gravação — confirmado
- [x] Cancelar na gravação normal: nenhuma requisição sai e a caixa fica idêntica — antes/depois
      colado acima
- [x] Cancelar no tempo real: sessão encerra, último trecho não vira turno novo, caixa idêntica —
      antes/depois colado acima
- [x] Depois de cancelar, dá para gravar de novo normalmente — confirmado nos dois modos
- [x] Parar (quadrado) continua funcionando nos dois modos, id batendo nos dois arquivos —
      confirmado (id `63f20b3f3bda4a43b126f0712e1935f7` nos dois)
- [x] Corte de 150s, gate de silêncio e painel de consumo sem regressão — gate de silêncio e painel
      testados com sessão real (acima); corte de 150s **não** foi re-testado com espera real de
      150s (custo de tempo, não de dinheiro) — conferi por leitura de diff que
      `LIMITE_GRAVACAO_MS`/`cortarPorSegurancaGravacaoRapida`/`cortarPorSegurancaTempoReal` não
      foram tocados; o único código novo que os dois caminhos de corte passam a atravessar é
      `botaoCancelarGravacaoRapida.hidden = true` dentro de funções que eles já chamavam
      (`pararGravacaoRapida`/`pararGravacaoTempoReal`), sem branch nova.
- [x] Nenhum erro novo no console — zero em todas as sessões
- [x] `transcritor/README.md` atualizado — seções "Gravação rápida pelo microfone" e "Transcrição
      em tempo real"

### Novas demandas / riscos
- **Efeito colateral aceito conscientemente** (documentado acima, no item 3 do "Feito"): se o
  `completed` de um turno já comitado antes do cancelamento (pelo timer de 6s) chegar depois do
  clique em cancelar, ele é descartado — não vira linha em nenhum dos dois arquivos, embora já
  cobrado pela OpenAI. Não violei a regra da caixa de transcrição (não tocada em hipótese alguma),
  mas o registro local de consumo pode ficar levemente incompleto nesse cenário específico. Fica
  para o PM avaliar se compensa comitar/registrar de outro jeito nessa janela — não implementei
  por conta própria por ser uma escolha de produto, não mecânica.
- Um teste do modo tempo real precisou ser refeito por uma falha pontual ao tentar reiniciar a
  gravação logo após um cancelamento (timeout esperando `.gravando` aparecer) — na segunda
  tentativa, com o mesmo código, funcionou sem problema e sem nenhum erro de console em nenhuma das
  duas rodadas. Não consegui reproduzir de novo; registro aqui por transparência, mas não vejo
  indício de bug no código (mais provável flake de rede/timing do ambiente de teste, já que o
  `fetch` do token e a abertura do WebSocket dependem da rede real até a OpenAI).
- Corte de 150s não testado com espera real (ver critério acima) — risco baixo, código não tocado
  além de uma linha de UI já coberta pelos mesmos caminhos que o corte de segurança usa.
- Ferramental de teste (scripts Playwright, WAV de ruído sintetizado) ficou em
  `%TEMP%\...\scratchpad\`, fora do repositório, mesma prática de tarefas anteriores.

### Ajuste no plano necessário?
Não.

## [2026-08-21] — Reorganização da interface de gravação + cadência da faixa, Etapa 5
Status: concluído

### Feito — `transcritor/frontend/index.html`

**1) Cadência da faixa** — não toquei a lógica de histórico (já correta). Só os números:
`NUM_BARRAS_NIVEL` 12→**80**, `INTERVALO_AMOSTRA_BARRAS_MS` 250→**60** (o ponto de partida
sugerido, ficou bom no teste — sem precisar ajustar). **80 × 60ms = 4,8s de histórico, ~16,7
atualizações/s.** CSS: `#barrasNivel .barra` passou de largura fixa (`0.3rem`) para `flex: 1 1 0`
com `gap: 1px` — com dezenas de barras um valor fixo ou transborda em tela larga ou aperta demais
em tela estreita; com flex a faixa sempre ocupa exatamente a largura do painel.

**2) Textos removidos**: `<p class="dica">Clique para gravar…</p>` e o `<label>` da textarea
(virou `aria-label` na própria `<textarea>`, para não ficar sem nome acessível). Mensagens
redundantes de "Gravando… clique para parar" (gravação normal e tempo real) — removidas as
chamadas, não só escondido o texto. `#statusGravacaoRapida` **não foi removido**, só as
mensagens redundantes, como pedido.

**2b) Status em balão + spinner no botão**: reescrevi `mostrarStatusGravacao(tipo, texto)` —
`tipo` agora é `"confirmacao"` (verde, some em 2000ms), `"erro"` (vermelho, some em 6000ms) ou
`"andamento"` (não mostra balão nenhum — só esconde qualquer balão anterior). Reaproveitei a
classe `.toast` já existente (`#toastSemFala`), sem inventar estilo novo. Toda chamada nova
cancela o `setTimeout` pendente e substitui na hora — decisão: **substitui, não empilha nem
enfileira** (documentado no comentário do código).

Terceiro estado do botão de gravar: `definirEstadoBotaoGravacao(estado)` — `"parado"` |
`"gravando"` | `"processando"` — um único ponto que decide classe CSS, `disabled`, visibilidade
do X de cancelar (só aparece em `"gravando"`) e `aria-label`. Troquei todos os pontos que
mexiam nesse estado (gravação normal e tempo real: iniciar, parar, cancelar, corte de segurança,
conexão caída, e os dois pontos de "aguardando resposta") para passar por essa função, em vez de
mexer em `classList`/`disabled`/`hidden` espalhado — eram ~10 lugares diferentes antes.
`#spinnerGravacao` é um `<span>` com `border-top` colorido + `animation: girar` (CSS puro, sem
imagem).

**3) Copiar**: só ícone agora (antes tinha o texto "Copiar texto"), `aria-label` e `title`,
movido para o canto inferior direito da caixa de texto (`position: absolute` sobre a textarea,
que ganhou `padding-bottom` extra pro texto não ficar embaixo do ícone).

**3b) Limpar/desfazer**: botão novo, canto inferior esquerdo (espelhando o de copiar). Lógica:
- `snapshotTranscript` só é gravado quando a caixa fica **ociosa** (`INTERVALO_OCIOSIDADE_
  TRANSCRIPT_MS = 800`, sem mudança) **e não vazia** — nunca a cada tecla. Isso é o que sobrevive
  à armadilha do backspace segurado: uma rajada de eventos `input` mais rápida que 800ms nunca
  deixa o timeout dessa a chance de gravar o vazio como snapshot (a checagem `if
  (valorAtual.trim())` descarta gravar vazio); o último valor não-vazio antes da rajada (o texto
  inteiro) é o que sobra. Testado de verdade (ver abaixo), não só por leitura de código.
- Botão troca de ícone (`.modo-desfazer` no `<button>`, dois `<svg>` sempre no DOM) conforme
  `atualizarBotaoLimparTranscript()`: texto → lixeira; vazia com snapshot → desfazer; vazia sem
  nada → escondido.
- `escreverTranscript(valor)` é o ponto único que toda escrita programática (upload normal,
  streaming, tempo real) usa em vez de `transcriptRapido.value = ...` direto — centraliza
  reagendar o snapshot e atualizar o botão pra qualquer origem do texto, não só digitação manual.

**4) Reorganização dos controles**: `.controles-gravacao-rapida` virou um grid de 3 colunas —
`grid-template-columns: 2.75rem 1fr 2.75rem` — esquerda (menu ⋮) e direita (cancelar) com
**largura fixa** (não `auto`), centro (`justify-self: center`) só com o botão de gravar. Como as
colunas das pontas têm largura fixa, elas não colapsam quando o cancelar vira `hidden`
(`display:none` não afeta o tamanho da coluna do grid) — é isso que mantém o botão de gravar
sempre no mesmo lugar. Medido, não só arquitetado (ver "Como testei").

Menu **⋮**: `#botaoConfiguracoes` e `#botaoConsumo` (que antes ficavam soltos na linha) foram
movidos pra dentro de `#popupMenuAvancado`, um popover `position: absolute` ancorado no wrapper do
botão ⋮. `abrirConfiguracoes()`/`abrirConsumo()` chamam `fecharMenuAvancado()` no início, então o
popup sempre fecha ao abrir um dos dois modais. Fecha também com clique fora (listener em
`document`, checando `.contains`) e Esc — mesmo padrão dos outros modais do projeto.

### Como testei — Playwright + Chromium headless, backend real na porta 8000 (sem mudança nele
### nesta tarefa — só confirmei que estava servindo o HTML atualizado antes de testar)

Usei os mesmos dois WAVs sintéticos de tarefas anteriores (fala real em PT-BR via SAPI, e ruído
ambiente bem baixo) — fora do repositório, `%TEMP%\...\scratchpad\`.

**Números da faixa + movimento contínuo**: em 889ms de janela, amostrando as 80 alturas a cada
~20ms (25 checagens), **15 mudanças de estado** detectadas — bate com ~60ms/amostra configurado
(889/15 ≈ 59ms). Exemplo de deslocamento capturado (fala real, 1,5s de intervalo):
```
t1[7..11]  = [100%, 35.2255%, 86.2631%, 100%, 21.6871%]
t2[1..5]   = [100%, 35.2255%, 86.2631%, 100%, 21.6871%]   ← o mesmo trecho "andou" 6 posições
```

**Faixa cabe sem transbordar, em várias larguras** (`barrasNivel.scrollWidth` vs `clientWidth`,
gravação real ligada em cada uma):
```
320px:  scrollWidth 238 == clientWidth 238
375px:  scrollWidth 293 == clientWidth 293
640px:  scrollWidth 558 == clientWidth 558
1024px: scrollWidth 590 == clientWidth 590
```
Nenhuma quebrou linha (`document.documentElement.scrollWidth` também bateu com `clientWidth` nas
4 larguras).

**Botão de gravar não se move**: `getBoundingClientRect().left`
```
parado:            604
gravando (X visível): 604
```
Idêntico — colado ao pixel.

**Menu ⋮**: popup abre, `#botaoConfiguracoes` abre o modal de configurações **e** fecha o popup
junto (confirmado pelos dois atributos `hidden` no mesmo instante); mesma checagem pra
`#botaoConsumo`. Popup fecha com clique fora (`page.mouse.click(5,5)`) e com Esc — os dois
testados separadamente.

**Balões — tempos medidos de verdade** (não estimados): confirmação **1946–2003ms** (3 medições);
erro **6000–6044ms** (2 medições). Mensagens em sequência: nunca mais de 1 balão
(`.toast:not([hidden])`) visível ao mesmo tempo.

**Erro forçado sem gastar API**: interceptei `**/transcrever` com Playwright (`route.abort`,
atraso proposital de propósito pra dar tempo de observar o estado "processando" no meio —
detalhe do teste, não do produto) — durante o envio: `classe` continha `"processando"`,
`disabledProp: true`, `xHidden: true`, `spinnerDisplay: "block"` (leitura única via
`page.evaluate`, sem race entre chamadas separadas). Ao falhar: balão de erro "Não foi possível
conectar ao backend…" apareceu, botão voltou a `"parado"`. Console acusou
`net::ERR_CONNECTION_REFUSED` — **esperado**, é o próprio abort do teste, não uma falha real.

**Três estados do botão — regressão em tempo real**: `"processando"` logo ao clicar (conectando,
antes mesmo do WebSocket abrir) → `"gravando"` (ícone quadrado, `iconeMicrofone` com
`display:none`) → clicar em parar de verdade → `"processando"` de novo → balão de confirmação
"Gravação em tempo real encerrada." Nova linha em `consumo.jsonl` (`segundos: 3.0`,
`id: a101719f...`) com a mesma id em `transcricoes.jsonl` (`id_consumo: a101719f...`,
`texto: "Na tarefa de faxina."`) — confirmado por código (`issubset`), não só lido.

**Copiar/limpar/desfazer — 8 casos, todos passando** (script isolado, sem custo de API):
1. Caixa com texto → lixeira; clicar apaga, vira desfazer.
2. Desfazer restaura o texto, volta a ser lixeira.
3. **Armadilha do backspace segurado** (a que o PM travou): digitei um texto, esperei ficar
   ocioso (1s), apaguei tudo com ~70 `Backspace` em sequência rápida (`delay=5`,
   bem mais rápido que os 800ms de ociosidade) — colado no teste:
   ```
   ANTES:  'Este e um texto razoavelmente longo para testar o backspace segurado.'
   DEPOIS: 'Este e um texto razoavelmente longo para testar o backspace segurado.'
   ```
   Texto **inteiro**, não a última letra.
3b. Mesma armadilha com Ctrl+A + Delete — mesmo resultado, texto inteiro restaurado.
4. Texto novo digitado depois de esvaziar → botão volta a lixeira.
5. Esvaziar de novo → desfazer restaura o conteúdo **mais recente** ("novo texto digitado"), não
   o texto2 de antes.
6. Lixeira duas vezes seguidas (a segunda já em modo "desfazer") não perde o texto original —
   porque o botão já trocou de modo no primeiro clique, então o segundo clique desfaz, não apaga
   de novo.
7. Página recém-aberta, nada escrito ainda: botão escondido (sem `hidden` → **presente**, checado
   o atributo).
8. Escrevi "texto de gravação simulado", esperei ficar ocioso, **editei por cima** (" + edição
   manual do usuário"), esperei ficar ocioso de novo, apaguei e desfiz — restaurou a string
   completa com a edição manual incluída, não só a parte "de gravação".

Zero erros de console em nenhum dos 8 casos.

**Regressões**: gate de silêncio (WAV de ruído ambiente, parei sem cancelar → toast "sem fala",
`consumo.jsonl` não cresceu), cancelar na gravação normal (texto idêntico antes/depois, arquivo
não cresceu), painel de consumo (abre normalmente, SVG da linha do tempo presente) — todos
confirmados com sessão real, script isolado, zero erros de console.

### O que NÃO consegui testar (e por quê)
- **Corte de 150s**: não testei com espera real (150s por teste é caro em tempo, não em
  dinheiro). Tentei acelerar com `page.clock.install()` +
  `page.clock.run_for(151000)` — **travou** (processo Python ficou preso, CPU quase zero,
  matei depois de ~5min sem progresso). Abandonei essa abordagem — meu palpite é que o relógio
  simulado do Playwright não convive bem com o `AudioContext`/captura de áudio real que continua
  rodando em tempo real de verdade por trás. Não reproduzi o risco de outra forma. Confiança de
  que não regrediu vem só de leitura de código: `LIMITE_GRAVACAO_MS`,
  `cortarPorSegurancaGravacaoRapida` e `cortarPorSegurancaTempoReal` não foram tocados — a única
  mudança que os atravessa é chamar `definirEstadoBotaoGravacao("processando")` antes de
  `pararGravacaoRapida()`/`pararGravacaoTempoReal()`, o mesmo caminho já testado com sessão real
  no "parar" comum.

### Novas demandas / riscos
- **Achado durante o teste, fora do escopo desta tarefa — não mexi (a tarefa proíbe mexer no
  cancelar/tempo real)**: existe uma condição de corrida **pré-existente** (de antes desta
  tarefa, na implementação do cancelar de tempo real) entre cancelar uma sessão de tempo real e
  iniciar uma nova **quase imediatamente** depois. `wsTempoReal`, `fechandoTempoRealDeliberadamente`
  e outras variáveis de estado do modo tempo real são compartilhadas entre sessões (não
  reiniciadas por sessão) — o evento `"close"` do WebSocket **cancelado** é assíncrono (round-trip
  de rede de verdade para fechar com a OpenAI) e pode chegar **depois** que a sessão nova já abriu.
  Se isso acontecer enquanto a flag `fechandoTempoRealDeliberadamente` da sessão nova ainda estiver
  `false` (ela só vira `true` de novo quando a sessão nova é parada/cancelada), o handler de
  `"close"` da sessão **velha** roda a limpeza inteira em cima do estado da sessão **nova**:
  zera `wsTempoReal`, chama `limparRecursosTempoReal()` (para os timers e o analisador da sessão
  nova que está gravando!) e mostra o balão de erro "A conexão com o modo tempo real caiu…" —
  travando a sessão nova num estado inconsistente (fica pendurada em "gravando" sem
  `wsTempoReal`, comandos futuros de parar/cancelar não fecham nada de verdade). **Reproduzido de
  verdade**: cancelar, aguardar menos de ~1s, e começar a gravar de novo — na minha reprodução, a
  sessão nova entrou em "gravando" normalmente, mas ao clicar em "parar" ficou presa em
  "processando" para sempre (nunca resolveu, nem pelo timeout de 5s de
  `TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS`, porque o handler de fechamento que deveria rodar
  foi "roubado" pelo evento da sessão velha). **Com ~3s de espera entre cancelar e a próxima
  gravação, não reproduz** — é uma janela de corrida estreita, não algo que acontece sempre. Não
  consertei por estar fora do escopo desta tarefa ("Não mexer... no cancelar nem no modo tempo
  real") — registro aqui pro PM decidir se abre uma tarefa nova. Um caminho possível (não
  implementado): dar a cada sessão um identificador próprio e o handler de `"close"` checar se
  ainda é o dono do estado atual antes de limpar algo.
- Corte de 150s não testado com espera real (ver acima).
- Ferramental de teste (scripts Playwright, WAVs) ficou em `%TEMP%\...\scratchpad\`, fora do
  repositório.

### Ajuste no plano necessário?
Não — mas ver o achado de corrida no tempo real acima, pra decisão do PM sobre abrir tarefa nova.

## [2026-08-21] — Acabamento visual da faixa + proximidade dos controles
Status: concluído

### Feito — `transcritor/frontend/index.html` (só CSS/HTML/a curva das barras; lógica de
histórico, snapshot do desfazer, spinner e balão intocados)
- Faixa: `#barrasNivel { align-items: center }` (espelha), `.barra` com `max-width: 3px` (fina de
  verdade, o flex continua garantindo que cabe) e `border-radius: 999px` (arredondamento total).
- Curva de amplitude: troquei `altura = piso + rms*6` (linear) por `altura = piso +
  sqrt(rms/RMS_TETO_BARRAS)*(1-piso)` — raiz quadrada, côncava, estica os valores baixos.
  `RMS_TETO_BARRAS = 0.4`, `PISO_BARRAS = 0.06` (piso menor que antes, pro repouso virar
  pontinho). Calibrado testando com fala real — números abaixo.
- Placeholder removido da `<textarea>`; `aria-label` intocado.
- Copiar e limpar/desfazer saíram de dentro da caixa (`position:absolute`) para uma
  `<div class="acoes-campo-transcript">` (flex, `justify-content: space-between`) logo abaixo —
  removi o `padding-bottom` extra da textarea que reservava espaço pra eles.
- Grid dos controles: `grid-template-columns: 2.75rem 1fr 2.75rem` → `1fr 4.5rem 1fr` +
  `column-gap: 0.6rem` — coluna central agora do tamanho exato do botão (fixo, não muda),
  laterais simétricas e flexíveis. `.wrapper-menu-avancado` e `#botaoCancelarGravacaoRapida`
  trocaram `justify-self` de `start`/`end` (bordas externas) para `end`/`start` (bordas internas,
  encostando no centro) — é isso que aproxima sem tirar a garantia de imobilidade (nem a largura
  da coluna central nem o gap mudam com o cancelar aparecendo/sumindo).

### Como testei — Playwright + Chromium, backend real (sem mudança nele, só confirmei que
estava servindo o HTML atualizado)

**Alturas medidas em 3 situações** (WAV de ruído ambiente = silêncio; WAV de fala real SAPI =
normal; mesmo WAV amplificado 3x = forte — 480 amostras por situação, ~1,8s de gravação):
```
silêncio: max=19,1%  p90=17,8%  p75=17,3%  média=11,3%
normal:   max=97,3%  p90=76,0%  p75=38,6%  média=24,7%
forte:    max=100%   p90=88,0%  p75=48,9%  média=28,9%
```
Fala normal usando a região média/alta nos trechos falados (p75/p90), sem saturar sempre — só
forte bate no teto com frequência. Calibrei `RMS_TETO_BARRAS` de 0,15 (primeira tentativa, onde
"normal" já saturava igual a "forte", sem diferenciar) para 0,4 (valores acima).

**Botão central imóvel** (`getBoundingClientRect().left`):
```
parado:              604
gravando (X visível): 604
```
Idêntico.

**Proximidade**: gap medido entre o botão de gravar e os vizinhos — `9,59px` dos dois lados
(menu à esquerda, cancelar à direita).

**Faixa continua cabendo sem transbordar** (regressão, mesmas 4 larguras da tarefa anterior):
320/375/640/1024px — `scrollWidth == clientWidth` nas 4, sem quebra de linha.

**Botões fora da caixa, sem cobrir texto**: preenchi a caixa com 5 linhas de texto — topo da
linha de botões (`614,9px`) ficou abaixo do fundo da caixa (`604,5px`); copiar à direita de
limpar, confirmado por coordenada.

**Regressão**: copiar (balão de confirmação), lixeira→desfazer (restaura o texto), menu ⋮ abrindo
configurações e consumo (com o painel de consumo carregando o SVG da linha do tempo) — todos
testados de novo depois das mudanças de layout, tudo funcionando. CSS dos 3 estados do botão
(microfone/quadrado/spinner) conferido via `classList`/`getComputedStyle` — não refiz uma sessão
real de envio porque a lógica de estado (`definirEstadoBotaoGravacao`) não foi tocada nesta
tarefa, só o CSS ao redor. Não testei tempos de balão (2s/6s) de novo por não ter mexido em
`mostrarStatusGravacao`. Zero erros de console em todas as sessões.

### O que não fiz
- Opção de barras mais antigas ficarem levemente mais transparentes — pulei por decisão própria
  (a tarefa deixava opcional, "só se ficar melhor de verdade"); não me pareceu necessário depois
  de ver a faixa fina/arredondada/espelhada funcionando bem sozinha.

### Critério de pronto
- [x] Faixa espelhada — `align-items: center`, confirmado via `getComputedStyle`
- [x] Barras finas (3px medido) com pontas arredondadas (`border-radius: 999px`); em silêncio vira
      fileira de pontos (max 19,1% de uma faixa de 2,5rem = poucos pixels, arredondado total)
- [x] Curva de amplitude registrada com alturas em silêncio/normal/forte — coladas acima
- [x] Faixa cabe sem transbordar, tela larga e estreita — regressão confirmada nas 4 larguras
- [x] Placeholder removido; `aria-label` intacto
- [x] Copiar e lixeira/desfazer fora da caixa, numa linha abaixo — lixeira à esquerda, copiar à
      direita
- [x] Texto longo não passa por baixo de botão nenhum — coordenadas conferidas
- [x] Os dois botões continuam só ícone, com `aria-label`/`title`, troca lixeira↔desfazer OK
- [x] Cancelar e três pontos visivelmente próximos do centro — gap de 9,59px medido
- [x] Botão central imóvel — 604px parado, 604px gravando
- [x] Sem regressão: spinner (CSS conferido), balão (classe/comportamento conferido, tempo não
      re-medido — código não tocado), copiar, lixeira/desfazer, cancelar, três pontos
- [x] Nenhum erro novo no console
- [x] `transcritor/README.md` conferido — parágrafos da faixa, dos botões e da introdução da
      seção de gravação atualizados

### Novas demandas / riscos
- Nenhum novo. O achado de corrida no modo tempo real (cancelar + reiniciar rápido demais)
  continua registrado na entrada anterior — esta tarefa não mexeu nesse código.

### Ajuste no plano necessário?
Não.

## [2026-08-21] — Correção pontual: botão de copiar pulava de lugar com a caixa vazia
Status: concluído

### Feito
Achado do usuário, direto no chat (fora do fluxo PROXIMA_TAREFA.md, mas claro e pequeno o
bastante pra executar na hora): com a caixa de texto vazia no início (lixeira/desfazer ainda sem
nada pra mostrar), o botão de limpar usava o atributo `hidden` (`display:none`) — tirando-o do
layout da linha `.acoes-campo-transcript` (`justify-content: space-between`), então o botão de
copiar, sozinho, caía na ponta esquerda em vez de ficar à direita.

Troquei `hidden` por uma classe `.invisivel` (`visibility: hidden`) só para o botão de limpar: o
elemento continua invisível e não-interativo, mas continua **ocupando o lugar dele** na linha, e o
de copiar não se move mais. `transcritor/frontend/index.html`: CSS (`#botaoLimparTranscript.invisivel`),
HTML (estado inicial já com a classe + `disabled`, sem `hidden`) e JS
(`atualizarBotaoLimparTranscript` — as três chamadas de `.hidden = ...` viraram
`.classList.add/remove("invisivel")`).

### Como testei
Sessão real de navegador (Playwright): posição (`getBoundingClientRect().left`) do botão de
copiar em três momentos — caixa vazia recém-aberta, com texto (lixeira aparece), depois de apagar
(desfazer aparece) — **903px nos três**, nunca mudou. Confirmei também que a lixeira some de novo
(fica em `visibility:hidden`) sem alterar a posição do copiar. Reexecutei a suíte completa de
lixeira/desfazer da tarefa anterior (8 casos, incluindo a armadilha do backspace segurado) — todos
continuam passando, só precisei atualizar a checagem do próprio script de teste (que olhava o
atributo `hidden`, que não existe mais) para olhar a classe `invisivel`. Zero erros de console.

### Critério de pronto
- [x] Botão de copiar não pula de lugar quando a lixeira/desfazer está escondida
- [x] Lixeira/desfazer continua funcionando igual (8 casos re-testados)
- [x] Nenhum erro novo no console

### Ajuste no plano necessário?
Não.
