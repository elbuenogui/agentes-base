# PROGRESSO arquivado — 2026-08-19 a 2026-08-20

> Entradas movidas do `PROGRESSO.md` vivo pelo PM em 2026-08-20, na virada de plano,
> conforme a exceção datada de 2026-08-19 registrada no `PM.md`. **Movidas apenas** —
> nenhuma linha foi editada, resumida ou reordenada.
>
> Plano correspondente: Transcrição em tempo real (token efêmero, captura, exibição incremental), consumo e persistência da transcrição, linha do tempo do painel de consumo, e as duas correções aprovadas.

## [2026-08-19] — Plano de tempo real, Etapa 1: Autenticação e conexão com a API ao vivo
Status: concluído

### Decisão (com justificativa baseada em documentação + teste real, não presumida)
**Token efêmero** (não relay). Confirmado empiricamente contra a API real da OpenAI (script
avulso, fora do repositório, com `websockets`+`requests` instalados só no venv local para o
teste — não entraram em `requirements.txt`):
- `POST https://api.openai.com/v1/realtime/client_secrets` (já disponível no SDK instalado,
  `openai==3.1.0`, via `cliente.realtime.client_secrets.create(session=...)`) gera um token
  efêmero (`ek_...`) escopado a uma sessão de transcrição, usando a chave real só no backend.
- O navegador consegue abrir a sessão **direto com a OpenAI**, sem o backend intermediar áudio:
  `new WebSocket("wss://api.openai.com/v1/realtime", ["realtime", "openai-insecure-api-key." +
  token])` — confirmado que a API aceita e devolve `session.created`. (A documentação oficial
  também mostra esse exemplo, mas só apareceu completo depois de eu pedir o snippet de código
  verbatim — uma primeira tentativa sem o subprotocolo `"realtime"` na lista falhou com
  `NegotiationError`, então vale registrar o formato exato aqui.)
- Como a conexão direta funciona e é mais simples (sem lógica de repasse de áudio/eventos nos
  dois sentidos no backend, sem duplicar a latência), não há motivo para relay nesta etapa.

### Feito
- `transcritor/backend/main.py`: novo endpoint `GET /tempo-real/token`. Usa a
  `OPENAI_API_KEY` já carregada de `transcritor/.env` (nunca exposta), chama
  `cliente.realtime.client_secrets.create(session={"type": "transcription", "audio": {"input":
  {"transcription": {"model": "gpt-live-transcribe"}, "turn_detection": None}}})` e devolve
  `{"client_secret", "expira_em", "modelo"}`. `turn_detection: None` é obrigatório para sessões
  de transcrição (a API rejeita VAD nesse tipo de sessão, conforme a doc). Mesmo padrão de
  tratamento de erro dos outros endpoints (chave ausente → 503; autenticação/rede/recusa da API
  → 502), reaproveitando as exceções já importadas (`AuthenticationError`,
  `APIConnectionError`, `APIStatusError`). Nova constante `MODELO_TEMPO_REAL =
  "gpt-live-transcribe"`.
- `transcritor/README.md`: nova seção "Transcrição em tempo real (ponte de autenticação)" com o
  formato da resposta do endpoint e o snippet de `WebSocket` confirmado empiricamente.

### Formato dos eventos (confirmado empiricamente, para as próximas etapas)
- Ao conectar: `session.created`, com a config da sessão (`audio.input.format` = PCM 24kHz,
  `audio.input.transcription.model` = `gpt-live-transcribe`).
- Delta incremental: `conversation.item.input_audio_transcription.delta`, campo `delta` (texto
  novo) — **não** `transcript.text.delta` como no modo streaming em lote da Etapa 7 do plano
  anterior; formato de evento diferente, cuidado ao reaproveitar código na Etapa 2.
- Final: `conversation.item.input_audio_transcription.completed`, campo `transcript` (texto
  completo) — **e inclui `usage`** (mesmo formato usado hoje em `_calcular_custo_usd`: variante
  `type: "tokens"` com `input_tokens`/`output_tokens`/`total_tokens`, ou variante `type:
  "duration"` com `seconds`). Isso é relevante para a Etapa 3 (consumo): dá pra reaproveitar a
  mesma função de cálculo, só trocando/acrescentando o preço por minuto de `gpt-live-transcribe`
  (US$ 0,017/min, já documentado no `PLANO.md`) em vez do preço por token dos modelos em lote.

### Validação (rodado de fato, não simulado)
- Backend local subido (`uvicorn`, porta 8000); `GET /tempo-real/token` → 200, `client_secret`
  com prefixo `ek_` (confirmado que **não** é a chave real, que começa com `sk-`).
- Script avulso (fora do repo) usou esse token pra abrir duas conexões WebSocket reais contra
  `wss://api.openai.com/v1/realtime`: uma com `Authorization: Bearer <token>` (padrão
  servidor-a-servidor) e outra com o subprotocolo exato que um navegador usaria (`["realtime",
  "openai-insecure-api-key." + token]`, já que browsers não podem setar headers customizados em
  WebSocket) — as duas abriram a sessão com sucesso e receberam `session.created` com a config
  esperada (`gpt-live-transcribe`, PCM 24kHz).
- Regressão: `GET /consumo` (endpoint já existente) testado com 200 antes e depois da mudança;
  nenhuma lógica de `/transcrever` foi tocada.
- Servidor de teste e processo de teste encerrados ao final; nenhum arquivo de teste entrou no
  repositório (tudo na pasta de rascunho da sessão, fora de `transcritor/`).

### Critério de pronto
- [x] Decisão registrada (token efêmero), com justificativa baseada em documentação + teste real
- [x] Backend implementa a ponte escolhida, sem expor a chave da API ao navegador em nenhum
      momento (só o token efêmero de curta duração sai do backend)
- [x] Testado isoladamente (fora do frontend) que a ponte abre uma sessão real e recebe eventos
      da API (`session.created` recebido nas duas formas de autenticação testadas)
- [x] `transcritor/README.md` tem uma nota breve sobre a nova rota
- [x] Nenhuma regressão em `/transcrever`, `/consumo` ou no frontend atual (nenhum desses
      arquivos foi alterado nesta tarefa)

### Diagnóstico
- O SDK `openai` já instalado no venv (`3.1.0`) já suporta `client.realtime.client_secrets` e
  todos os tipos de evento da Realtime API — não foi preciso atualizar `requirements.txt`.
- Para o teste avulso fora do repositório, instalei `websockets` e `requests` no mesmo venv do
  projeto (não em `requirements.txt`, já que o app em si não precisa dessas libs: quem vai abrir
  o WebSocket na Etapa 2 é o navegador, em JavaScript, não o backend Python).

### Novas demandas / riscos
- Nenhuma nova relacionada a esta etapa. Segue valendo o item já registrado no Backlog do
  `PLANO.md` sobre CORS aberto (não afetado por esta mudança).

### Ajuste no plano necessário?
Não — Etapa 1 concluída conforme especificado. Pronto para a Etapa 2 (captura em tempo real +
alternador + exibição incremental) quando o PM gerar a próxima `PROXIMA_TAREFA.md` — vale levar
adiante a nota acima sobre o formato de evento ser diferente do streaming em lote existente.

## [2026-08-19] — Plano de tempo real, Etapa 2: Captura em tempo real + alternador + exibição incremental
Status: concluído

### Formato de envio de áudio cliente→servidor (confirmado na documentação oficial, não presumido)
Consultado <https://developers.openai.com/api/docs/guides/realtime-transcription> (2026-08-19)
via WebFetch, antes de implementar:
- **Envio de áudio**: evento `{"type": "input_audio_buffer.append", "audio": "<base64 PCM16>"}`.
- **Fechar um turno**: como a sessão usa `turn_detection: null` (decisão já tomada e implementada
  no backend na Etapa 1, para permitir controle manual), é preciso enviar
  `{"type": "input_audio_buffer.commit"}` explicitamente para a API processar o áudio acumulado e
  disparar a transcrição — a doc **não recomenda** um intervalo específico de commit nem tamanho
  de chunk; calibrado empiricamente (ver "Validação" abaixo).
- Isso era exatamente a lacuna que a Etapa 1 tinha deixado em aberto ("O que esta etapa NÃO
  cobriu ainda") — sem o `commit` explícito, a API nunca dispararia a transcrição, já que
  `turn_detection: null` desativa o corte automático de turno.

### Feito
- `transcritor/frontend/index.html`:
  - novo alternador **"Transcrição em tempo real"** (`#botaoTempoReal`), mesmo estilo visual dos
    alternadores de modelo/streaming, logo abaixo deles; deixa claro na dica que só afeta a
    gravação rápida (upload de arquivo não é tocado); desligado por padrão; não pode ser
    alternado no meio de uma gravação em andamento (normal ou tempo real) — clique é ignorado
    nesse caso;
  - o clique no botão redondo de gravação rápida (`#botaoGravacaoRapida`) agora ramifica no
    início do handler: com o alternador ligado, chama `iniciarGravacaoTempoReal()`/
    `pararGravacaoTempoReal()` (novo fluxo, abaixo); desligado, comportamento idêntico ao que já
    existia (`iniciarGravacaoRapida()`/`pararGravacaoRapida()`, `MediaRecorder` + upload para
    `POST /transcrever`) — nenhuma linha desse caminho antigo foi alterada;
  - **fluxo tempo real** (`iniciarGravacaoTempoReal`): busca o token em `GET /tempo-real/token`
    (mesmo endpoint da Etapa 1, backend em `http://127.0.0.1:8000`); pede o microfone
    (`getUserMedia`, respeitando o dispositivo escolhido no painel de configurações, mesma lógica
    já existente); abre `new WebSocket("wss://api.openai.com/v1/realtime", ["realtime",
    "openai-insecure-api-key." + client_secret])` (formato já confirmado na Etapa 1); captura o
    áudio com `AudioContext` + `ScriptProcessorNode` (não `AudioWorklet` — decisão deliberada para
    manter o frontend em arquivo único, sem módulo externo, seguindo a sugestão da própria tarefa
    de usar o que for mais simples); reamostra manualmente (interpolação linear) da taxa nativa do
    dispositivo para 24kHz, converte para PCM16 mono e envia `input_audio_buffer.append` a cada
    bloco processado (~4096 amostras); um `setInterval` de 3s envia `input_audio_buffer.commit`
    sempre que houver pelo menos ~100ms de áudio acumulado desde o último commit (constante
    `MINIMO_BYTES_PARA_COMMIT_TEMPO_REAL`, baseada no mínimo que a API exige — abaixo disso a
    API rejeita o commit);
  - o `ScriptProcessorNode` é conectado a um `GainNode` com volume zero antes do destino de áudio
    (`audioContext.destination`) — necessário para o `onaudioprocess` disparar em todos os
    navegadores testados, sem tocar o áudio capturado de volta nas caixas de som (eco);
  - **exibição incremental**: evento `conversation.item.input_audio_transcription.delta` (campo
    `delta`) vai sendo somado a um buffer do turno atual e escrito em `#transcriptRapido`
    conforme chega; evento `conversation.item.input_audio_transcription.completed` (campo
    `transcript`) substitui o buffer do turno pelo texto oficial daquele turno (mesma lógica de
    "final substitui a soma dos deltas" já usada no streaming em lote da Etapa 7 anterior) e abre
    espaço para o próximo turno — o texto de turnos já finalizados fica preservado, junto com
    qualquer texto que já estivesse na caixa antes de começar a gravar (comportamento cumulativo
    já existente, preservado);
  - reaproveitado sem alteração: `dispositivoEscolhido` (configurações), `iniciarAnalisadorNivel`/
    `pararAnalisadorNivel` (barras de nível), cronômetro (`inicioGravacaoRapida`,
    `intervaloCronometroRapido`, `atualizarCronometroGravacaoRapida`) — o botão redondo fica
    vermelho pulsando e o cronômetro conta normalmente também no modo tempo real;
  - **tratamento de erro** (`Tratar erro de conexão... sem travar a interface`): falha ao buscar
    o token (backend fora do ar, chave ausente) → mensagem clara antes de pedir o microfone,
    botão permanece clicável; evento `{"type": "error"}` vindo da API (ex.: token inválido) →
    mensagem exibida em `#statusGravacaoRapida` sem interromper a gravação sozinha (a API pode
    mandar um erro recuperável sem fechar a sessão — testado, ver "Validação"); fechamento
    inesperado do WebSocket (`close` sem ter sido um `pararGravacaoTempoReal()` deliberado — flag
    `fechandoTempoRealDeliberadamente` distingue os dois casos) → limpa todos os recursos
    (stream, `AudioContext`, timers), volta a interface ao estado "parado" e mostra mensagem
    orientando a tentar de novo ou desligar o alternador; em nenhum desses casos a página trava
    ou lança exceção;
  - `pararGravacaoTempoReal()` (parada manual): comita o que sobrou no buffer (se atingir o
    mínimo), fecha o WebSocket, libera microfone/`AudioContext`/timers, mostra "Gravação em tempo
    real encerrada.".
- `transcritor/README.md`: seção "Transcrição em tempo real" reescrita — passo a passo do novo
  alternador/fluxo, sub-seções "Ponte de autenticação" (conteúdo da Etapa 1, preservado) e
  "Formato dos eventos" (novo, com a citação da doc oficial e a data da consulta) e "Limitações
  desta etapa" (ScriptProcessorNode em vez de AudioWorklet; sem corte de segurança por tempo nem
  detecção de silêncio no modo tempo real — ver "Novas demandas" abaixo); "Na página" ganhou um
  passo novo citando o alternador, com os passos seguintes renumerados.
- `transcritor/backend/main.py` não foi tocado (fora da lista de arquivos desta tarefa; o
  endpoint `GET /tempo-real/token` da Etapa 1 já era suficiente, sem mudança necessária).

### Validação (rodado de fato, com fala real, backend local rodando)
- Sintaxe do JS extraído do `<script>` verificada com `node --check` — sem erros.
- **Fluxo completo com fala real** (Edge headless via `playwright-core`, áudio de ~27s gerado
  pelo sintetizador de voz do Windows a 24kHz mono, injetado como microfone via
  `--use-fake-device-for-media-stream` + `--use-file-for-fake-audio-capture=<wav>`, backend local
  no ar): ligado o alternador, clique no botão redondo → status "Conectando ao modo tempo
  real…" → "Gravando em tempo real…"; amostrando `#transcriptRapido` a cada 500ms durante toda a
  gravação, capturados **60 tamanhos de texto distintos** ao longo de ~34s — progressão visível e
  contínua (não um salto único), confirmando a exibição incremental "conforme os pedaços de áudio
  são capturados", como pedia o critério de pronto; texto final coerente com a fala sintetizada
  (pequenas imprecisões pontuais são variação normal do modelo, não bug); clique de novo → parou,
  status "Gravação em tempo real encerrada.".
- **Intervalo de commit calibrado empiricamente** (já que a doc não recomenda um valor): 3s com
  mínimo de ~100ms de áudio acumulado funcionou sem nenhum erro de "buffer pequeno demais" nem
  perda perceptível de áudio ao longo do teste de 27s (múltiplos turnos, cada um virando uma linha
  de texto no transcript).
- **Modo desligado — regressão** (critério de pronto explícito): com o alternador de tempo real
  no estado padrão (desligado), gravação rápida testada do início ao fim (clique → grava →
  clique → envia para `POST /transcrever`) — comportamento e resultado idênticos aos já validados
  nas etapas anteriores (Etapa 2 do plano anterior), texto do backend aparece no transcript
  normalmente.
- **Erro antes de conectar** (token inválido/indisponível): `GET /tempo-real/token` interceptado
  para devolver HTTP 503 → mensagem clara em `#statusGravacaoRapida`
  ("Não foi possível obter o token do modo tempo real: ..."), botão permanece habilitado e sem a
  classe "gravando" — página não trava.
- **Erro durante a sessão (token com formato válido mas inválido de verdade)**: a API real da
  OpenAI aceitou a conexão e devolveu um evento `{"type": "error", "error": {"message": "Invalid
  realtime token"}}` (não fechou a conexão sozinha) — o frontend mostrou a mensagem
  "Erro no modo tempo real: Invalid realtime token" sem travar; a gravação permaneceu no estado
  "gravando" até o usuário clicar para parar, o que funcionou normalmente (fechou a conexão e
  liberou os recursos sem exceção). Registrado como comportamento real observado, não presumido.
- **Queda de conexão inesperada** (simulada fechando o `WebSocket` diretamente por fora do código
  da aplicação, via instrumentação de teste que intercepta `new WebSocket(...)`, para não
  depender de conseguir derrubar a rede de verdade no ambiente de teste): o listener `close`
  tratou corretamente — mensagem "A conexão com o modo tempo real caiu (token pode ter expirado,
  ou falha de rede). Clique no botão para tentar de novo, ou desligue o alternador..."; classe
  "gravando" removida; botões voltaram a ficar clicáveis; um novo clique iniciou uma nova conexão
  do zero com sucesso ("Gravando em tempo real…" de novo) — confirma que dá pra tentar de novo
  sem recarregar a página.
- Nenhum erro de console/página (`pageerror`) em nenhum dos cenários acima (um único aviso de
  recurso 404 no console, não relacionado — provavelmente `favicon.ico`, não investigado por não
  afetar nenhum critério de pronto).
- Backend de teste (uvicorn) e navegador de teste encerrados ao final; nenhum arquivo de teste
  (`.wav`, scripts Node) entrou no repositório — tudo ficou na pasta de rascunho da sessão, fora
  de `transcritor/`.

### Critério de pronto
- [x] Formato de envio de áudio cliente→servidor confirmado (doc oficial, via WebFetch) e
      registrado acima — não presumido
- [x] Alternador "Tempo real" (mesmo estilo dos outros) presente na gravação rápida
- [x] Com o modo ligado: áudio capturado e enviado continuamente; texto aparece incrementalmente
      conforme os deltas chegam (testado com fala real, 60 tamanhos de texto distintos capturados
      ao longo da gravação)
- [x] Com o modo desligado: comportamento atual sem nenhuma alteração (regressão testada)
- [x] Erro de conexão durante o modo ao vivo tratado sem travar a interface (testado forçando três
      cenários distintos: falha ao buscar token, erro vindo da API durante a sessão, e queda
      inesperada da conexão WebSocket)
- [x] `transcritor/README.md` tem uma nota breve sobre o novo alternador e fluxo — na prática, uma
      seção completa, já que o fluxo tem vários detalhes técnicos (formato PCM, commit manual)
      que pareceram valer a pena documentar
- [x] Nenhuma regressão em `/transcrever` (modo sem tempo real testado), `/consumo` (endpoint não
      tocado), upload de arquivo (não tocado nesta etapa), streaming em lote existente (Etapa 7,
      código não tocado nesta etapa)

### Diagnóstico
- A lacuna que a Etapa 1 tinha deixado em aberto ("formato exato de envio de áudio") tinha duas
  partes, e a doc só respondia uma sozinha de forma explícita: o evento de envio
  (`input_audio_buffer.append`) está bem documentado, mas a necessidade do `commit` manual (por
  causa do `turn_detection: null` já configurado no backend) só fica clara lendo com atenção a
  seção sobre desativar a detecção automática de turno — sem isso, a implementação teria mandado
  áudio sem nunca dar o "trigger" de transcrição.
- `ScriptProcessorNode` está formalmente depreciado a favor de `AudioWorklet`, mas foi escolhido
  deliberadamente (ver nota na tarefa: "ou ScriptProcessorNode, se mais simples") para não
  precisar de um arquivo de módulo separado ou de `Blob URL`, mantendo o frontend em um único
  arquivo `index.html`, no mesmo padrão do resto do projeto. Funcionou sem problemas no
  Chromium/Edge testado.
- O intervalo de commit (3s) e o limiar mínimo (~100ms) foram decisões de implementação, já que a
  documentação não prescreve nenhum dos dois — calibrados testando com fala real; **não** foram
  testados em conexões de rede lenta/instável ou em sessões muito longas (vários minutos), onde um
  intervalo fixo talvez precise de ajuste.

### Novas demandas / riscos
- **Sem corte de segurança por tempo no modo tempo real** (ao contrário da gravação normal, que
  para sozinha em 2min30s): uma gravação em tempo real esquecida ligada continua consumindo a API
  (WebSocket aberto, áudio sendo enviado) até o usuário clicar para parar. Não implementado porque
  não estava no escopo desta tarefa e o registro de consumo/custo do modo ao vivo é a Etapa 3 —
  mas vale o PM considerar um limite semelhante ao da gravação normal numa etapa futura,
  especialmente combinado com a Etapa 3 (custo por minuto mais alto que os modelos em lote).
- Sem detecção de silêncio (a gravação normal evita enviar áudio totalmente mudo); no modo tempo
  real, se o usuário ligar e não falar nada, o WebSocket fica aberto normalmente sem transcrever
  nada (sem custo de transcrição, já que não há turno pra comitar com conteúdo relevante — mas não
  testado esse caso específico).
- Calibração do intervalo de commit (3s) e do limiar mínimo (~100ms) não testada em cenários de
  rede lenta ou sessões de vários minutos — ver "Diagnóstico" acima.
- Aviso de console (recurso 404, provavelmente `favicon.ico`) observado nos testes — não é um bug
  introduzido por esta etapa (a página nunca teve favicon) nem afeta nenhum critério de pronto;
  registrado só por transparência.

### Ajuste no plano necessário?
Não — Etapa 2 concluída conforme especificado. Pronto para a Etapa 3 (consumo no modo ao vivo)
quando o PM gerar a próxima `PROXIMA_TAREFA.md` — vale levar adiante a nota sobre
`gpt-live-transcribe` ser cobrado por minuto (US$ 0,017/min, já documentado no `PLANO.md`), não
por token como os modelos em lote, e a observação sobre não haver corte de segurança/detecção de
silêncio no modo tempo real ainda.

## [2026-08-19] — Entre etapas: usuário perguntou sobre quebra de linha a cada poucos segundos no modo tempo real
Status: explicado ao usuário; pendência registrada para o PM (nenhum código alterado)

### Feito
- Usuário testou o modo tempo real (Etapa 2, concluída acima) e notou que o texto quebra linha a
  cada poucos segundos, sem relação com pausas na fala. Expliquei a causa (não é bug): o alternador
  manda `input_audio_buffer.commit` a cada 3s (intervalo calibrado empiricamente na Etapa 2, já que
  a doc da API não recomenda nenhum valor — ver critério de pronto da Etapa 2 acima); cada commit
  vira um "turno" separado do lado da API (por causa de `turn_detection: null`, decisão da Etapa
  1), e o frontend cola uma quebra de linha entre o texto final de cada turno. Ou seja, a quebra
  é o rastro visível do corte artificial de tempo fixo, não um corte por frase/pausa.
- Usuário pediu para registrar isso como pendência para discutir com o PM, em vez de eu ajustar
  agora. Nenhuma alteração de código foi feita.

### Novas demandas / riscos
- **Pendência de UX para o PM decidir**: o corte de turno a cada 3s (fixo, por tempo) produz
  quebras de linha que não acompanham a fala real — pode incomodar visualmente. Alternativas que
  o PM pode considerar numa etapa futura: (a) não quebrar linha entre turnos, deixando o texto
  fluir contínuo; (b) aumentar/diminuir o intervalo de commit; (c) trocar `turn_detection: null`
  por detecção automática de silêncio do lado da API (`turn_detection` configurado, não `null`),
  deixando a própria OpenAI decidir os cortes por pausa em vez de um timer fixo no cliente — essa
  última opção exigiria mudar o backend (`GET /tempo-real/token` em `main.py`, fora do escopo de
  arquivos desta etapa) e re-testar o formato dos eventos, já que muda o comportamento da sessão.

### Ajuste no plano necessário?
Sim, mas é decisão do PM (não do Executor): decidir qual das alternativas acima (ou outra) aplicar
e gerar uma `PROXIMA_TAREFA.md` para isso, se optar por mudar.

## [2026-08-19] — Etapa 3: Ajuste de exibição e intervalo de commit no modo tempo real
Status: concluído

### Feito
- `transcritor/frontend/index.html`:
  - `INTERVALO_COMMIT_TEMPO_REAL_MS`: `3000` → `6000` (único valor alterado; `MINIMO_BYTES_PARA_COMMIT_TEMPO_REAL`
    não foi tocado — continua fazendo sentido no dobro do intervalo, ver "Diagnóstico").
  - `atualizarTranscriptTempoReal()`: removida a variável `separadorTurno` que inseria `"\n"` entre
    `textoFinalizadoTempoReal` e `turnoAtualTempoReal`; a concatenação agora é direta.
  - Handler de `conversation.item.input_audio_transcription.completed`: removida a inserção de
    `"\n"` entre o texto finalizado anterior e o novo `dado.transcript`; agora é
    `textoFinalizadoTempoReal += dado.transcript` (concatenação direta, sem separador).
  - Nenhuma outra parte do modo tempo real, do backend, ou dos outros fluxos (upload, gravação
    normal, streaming em lote) foi tocada.
- `transcritor/README.md`: seção "Formato dos eventos (cliente↔servidor)" — "intervalo fixo de 3s"
  → "intervalo fixo de 6s" (única menção ao valor antigo encontrada no arquivo).

### Validação (rodado de fato, não simulado)
Testado com Edge headless (`playwright-core`, instalado fora do repo na pasta de rascunho da
sessão) e o backend local já em execução (porta 8000, iniciado antes desta tarefa):
- Áudio de teste gerado com o sintetizador de voz do Windows (`System.Speech`, ~45s de fala
  contínua, texto describing o próprio teste), injetado como microfone via
  `--use-fake-device-for-media-stream` + `--use-file-for-fake-audio-capture=<wav>`.
- Modo tempo real ligado (`#botaoTempoReal`) e gravação iniciada (`#botaoGravacaoRapida`), rodando
  por 24s (cobrindo pelo menos 3 commits):
  - Frames WebSocket capturados via `page.on("websocket")`/`framesent` (sem instrumentação no
    código-fonte): 4 commits enviados, com intervalos reais de **6003ms, 5998ms e 5278ms** entre
    eles (o último menor porque foi o commit manual de encerramento, disparado por
    `pararGravacaoTempoReal()` ao parar a gravação, não pelo timer) — confirma o intervalo de ~6s
    (antes ~3s).
  - Texto final do transcript capturado ao fim do teste: **nenhuma ocorrência de `\n`**
    (`valorFinal.includes("\n") === false`), incluindo nos pontos de transição entre turnos
    finalizados (visível nos snapshots por segundo do `textarea`, ex.: "...seis segundos.Dos de
    Camit Agora continuando..." — turnos concatenados sem quebra visual).
  - A qualidade da transcrição em si (ex.: "Crie um teste" em vez de "Este é um teste") reflete
    limitação da voz sintetizada do Windows / do modelo, não relacionada a este ajuste — fora do
    escopo desta tarefa.
- Regressão do modo desligado (gravação rápida normal, `MediaRecorder` + `POST /transcrever`):
  gravação de 4s com o mesmo áudio, alternador de tempo real desligado (padrão) → status
  `sucesso`, transcrição correta no transcript ("Este é o teste da etapa três do modo...") — sem
  regressão.
- Nenhum arquivo de teste (`.wav`, script node, `node_modules` do `playwright-core`) entrou no
  repositório — tudo ficou na pasta de rascunho da sessão, fora de `transcritor/`. Backend deixado
  no mesmo estado em que já estava (rodando, não iniciado nem encerrado por esta tarefa).

### Critério de pronto
- [x] Texto do modo tempo real não quebra mais linha entre turnos — fica contínuo (testado com
      fala real cobrindo múltiplos turnos, confirmado via captura do `textarea` e do texto final)
- [x] Intervalo de commit dobrado de ~3s para ~6s (confirmado por teste real via frames WebSocket
      capturados pelo Playwright, não só pela leitura do código)
- [x] Nenhuma mudança no backend, no formato dos eventos, ou no comportamento do modo desligado
      (testado)
- [x] `transcritor/README.md` atualizado (única menção ao "3s" encontrada, trocada por "6s")
- [x] Nenhuma regressão nos demais fluxos — modo tempo real ligado testado de ponta a ponta;
      modo desligado (gravação normal) testado sem regressão; upload de arquivo e streaming em
      lote não foram tocados por esta tarefa (nenhuma linha de código compartilhada com eles foi
      alterada), risco de regressão nesses dois considerado desprezível e não testado
      individualmente nesta etapa (evitando bateria exaustiva, conforme instrução da tarefa)

### Diagnóstico
- `MINIMO_BYTES_PARA_COMMIT_TEMPO_REAL` (4800 bytes ≈ 100ms de áudio PCM16 mono 24kHz) é um piso
  mínimo exigido pela API para um commit ser aceito, não relacionado ao tamanho do intervalo do
  timer — com o intervalo dobrado para 6s, o buffer acumulado tende a ser bem maior que esse piso
  (a menos que o usuário fique em silêncio quase todo o intervalo), então o valor continua fazendo
  sentido sem ajuste. Não encontrei motivo para alterá-lo, conforme a ressalva da tarefa.
  Registrando aqui em vez de decidir sozinho sobre esse ponto, como pedido.
  Item já registrado no Backlog do `PLANO.md` (falta de detecção de silêncio) tangencia essa
  mesma questão, mas fora do escopo desta tarefa.
- Captei os timestamps de commit via `page.on("websocket")` do Playwright (frames reais enviados
  pelo navegador), em vez de instrumentar o código-fonte com `console.log` — evita qualquer
  alteração temporária no arquivo da tarefa que precisasse ser desfeita depois.

### Novas demandas / riscos
- Nenhuma nova além das já registradas no Backlog do `PLANO.md` (falta de corte de segurança por
  tempo e de detecção de silêncio no modo tempo real — ambas fora do escopo desta tarefa).

### Ajuste no plano necessário?
Não — Etapa 3 concluída conforme especificado.

## [2026-08-19] — Investigação: discrepância "texto aparece antes do primeiro commit"
Status: concluído (diagnóstico apenas — nenhuma mudança de comportamento no código)

### Feito
- Reproduzido o mesmo ambiente de teste da Etapa 3 (Playwright + Edge headless, `playwright-core`
  fora do repo, mesmo áudio sintetizado de ~45s, backend local já em execução), desta vez logando
  com timestamp preciso (ms desde o clique de "iniciar gravação") TODOS os frames WebSocket
  relevantes — `input_audio_buffer.commit` enviado, `...delta` e `...completed` recebidos (com
  conteúdo) — via `page.on("websocket")`/`framesent`/`framereceived`, mais amostragem do valor
  visual de `#transcriptRapido` a cada 150ms. Transcript foi zerado programaticamente antes do
  teste para descartar texto residual de execução anterior.
- **Resposta com dados**: sim, deltas com texto não vazio chegam antes do primeiro commit.
  - Primeiro `DELTA_RECEBIDO` em **2340ms** (conteúdo `" Cr"`), com a primeira mudança visual no
    `#transcriptRapido` em **2447ms** (aparece já como " Crie").
  - Primeiro `COMMIT_ENVIADO` só em **6960ms** (consistente com o intervalo de ~6s calibrado na
    Etapa 3 — o timer só verifica a cada `INTERVALO_COMMIT_TEMPO_REAL_MS`).
  - Primeiro `COMPLETED_RECEBIDO` em **7624ms**, ~660ms depois do primeiro commit.
  - Ou seja: entre 2340ms e 6960ms, oito eventos `delta` chegaram e já apareceram na tela — mais de
    4,5s antes do primeiro commit. Log completo (cronológico, com todos os timestamps e conteúdo de
    cada delta) registrado no output do teste; principais marcos citados acima.
  - A mudança visual bate exatamente com a chegada de cada delta (ex.: delta em 2340/2350ms →
    textarea muda em 2447ms; delta em 2598ms → textarea muda em 2602ms) — não há nenhuma outra
    fonte de texto aparecendo antes disso; o comportamento observado pelo usuário é real e
    reproduzível, não um artefato de cache ou de outro handler.
- **Causa (não é bug)**: confirmado na documentação oficial da Realtime API
  (`https://developers.openai.com/api/docs/guides/realtime-transcription`, consultada em
  2026-08-19, via WebFetch): os eventos `delta` são transmitidos continuamente conforme a fala
  chega ("returns transcript deltas as speech arrives"), independente de commit já ter sido
  enviado. O `commit` (obrigatório porque a sessão usa `turn_detection: null`, decisão da Etapa 1)
  só sinaliza o fim de um turno e dispara o evento `completed` com o texto final consolidado
  daquele turno — não é um gatilho para a transcrição começar. O entendimento registrado na Etapa 1
  ("sem o commit explícito, a API nunca dispararia a transcrição") estava **incompleto**: o commit
  é necessário para fechar um turno e obter o `completed`, mas a API já transcreve e transmite
  deltas parciais do áudio acumulado no buffer antes disso, em tempo real.
- Nenhuma alteração de comportamento foi feita em `transcritor/frontend/index.html` nem em nenhum
  outro arquivo — só o teste diagnóstico (fora do repo, na pasta de rascunho da sessão).

### Critério de pronto
- [x] Log completo dos frames WebSocket (commit + delta + completed, com timestamp e conteúdo) de
      uma gravação real de mais de 6s, cobrindo três commits (6960ms, 12958ms, 18958ms + o commit
      manual de encerramento em 20122ms)
- [x] Resposta clara registrada: **sim, deltas chegam antes do primeiro commit** — primeiro delta
      em 2340ms vs. primeiro commit em 6960ms (dados exatos acima)
- [x] Comportamento confirmado como esperado pela documentação oficial da API, citada com a fonte
      (não é um bug do frontend)
- [x] Nenhuma alteração de comportamento no código ao final da tarefa

### Diagnóstico
- Não há contradição entre a validação da Etapa 3 (que mediu só o intervalo entre commits, ~6s,
  confirmado de novo aqui: 6960→12958 = 5998ms, 12958→18958 = 6000ms) e o relato do usuário (que
  fala do primeiro **texto aparecendo**, não do primeiro commit) — são dois eventos diferentes que
  a Etapa 3 não tinha motivo para diferenciar, já que seu escopo era só a quebra de linha e o
  intervalo de commit, não a origem do primeiro texto na tela.
- Efeito prático: o usuário vê o texto parcial (deltas) surgindo poucos segundos depois de começar
  a falar (não a cada 6s como um "commit" sugeriria) — isso é o comportamento correto e esperado do
  modo "tempo real" (exibição incremental já era um critério de pronto da Etapa 2: "exibição
  incremental do texto conforme os deltas da API ao vivo chegam"). O intervalo de 6s só afeta
  quando o texto de um turno é "fechado" (`completed`, sem mudança visual perceptível hoje já que
  não há mais separador entre turnos) e quando um novo turno começa a acumular delta do zero.

### Novas demandas / riscos
- Nenhuma — a investigação não encontrou bug; é comportamento esperado da API, já coberto pelo
  critério de pronto original da Etapa 2 (exibição incremental via delta). Nenhuma ação de código
  necessária a partir deste achado.

### Ajuste no plano necessário?
Não — recomendo ao PM apenas atualizar a nota da Etapa 1 no `PLANO.md` ("sem o commit explícito, a
API nunca dispararia a transcrição") para refletir o entendimento completo agora confirmado (deltas
fluem continuamente antes do commit; só o `completed` de cada turno depende dele), já que é uma
correção de registro histórico, não uma mudança de comportamento.

## [2026-08-19] — Etapa 4: Consumo no modo ao vivo
Status: concluído

### Feito
- Preço por minuto de `gpt-live-transcribe` conferido na fonte oficial
  (<https://developers.openai.com/api/docs/pricing>, consultada em 2026-08-19, via WebFetch):
  **US$ 0,017/min**, confirmando o valor já anotado no `PLANO.md`. Adicionado a
  `PRECO_POR_MINUTO_USD` em `backend/main.py`, com comentário citando a fonte e a data.
- `backend/main.py`: nova classe Pydantic `UsageTempoReal` (campos `type`/`seconds`, com
  `field_validator` rejeitando qualquer `type` diferente de `"duration"` e qualquer `seconds`
  negativo — HTTP 422 antes de tocar em `_registrar_consumo`, para não gravar lixo) e nova rota
  `POST /consumo/tempo-real`, que recebe o `usage` de um turno concluído do modo ao vivo como
  corpo JSON e reaproveita `_calcular_custo_usd`/`_registrar_consumo` (mesmas funções do modo sem
  tempo real) — como confirmado na doc oficial da API (API reference dos server events da
  Realtime API, consultada em 2026-08-19) que o `usage` de `gpt-live-transcribe` sempre vem no
  formato `{"type": "duration", "seconds": N}`, o registro cai naturalmente no caminho de
  segundos/preço por minuto de `_calcular_custo_usd`, sem precisar alterar essa função.
- `frontend/index.html`: nova função `reportarConsumoTempoReal(usage)`, chamada a cada evento
  `conversation.item.input_audio_transcription.completed` recebido na sessão de tempo real,
  logo depois de atualizar o transcript na tela. Envia `POST /consumo/tempo-real` com o `usage`
  do turno como corpo JSON. O `fetch` **não é aguardado** (`await`) e qualquer falha é engolida
  em `.catch()` — acessório por construção, não só por boa prática: mesmo que trave, não bloqueia
  o handler de mensagens do WebSocket.
- `transcritor/README.md`: seção "Transcrição em tempo real" ganhou a subseção "Consumo no modo
  tempo real" explicando de onde vem o `usage` (navegador, não backend), o formato
  `{"type": "duration", "seconds": N}`, o fluxo (frontend reporta → backend valida e grava) e a
  natureza acessória do envio. Também ajustada a frase que dizia "não há registro de consumo" no
  modo tempo real (não era mais verdade) e a nota sobre `usage` "não usado ainda" no formato dos
  eventos.

### Validação (rodado de fato, ponta a ponta, com fala real — não simulado)
- **Nota de transparência**: ao subir o backend para testar, a porta 8000 já estava ocupada por um
  processo `python.exe` (PID 31336) rodando desde mais cedo (provavelmente uma sessão de backend
  esquecida ligada de uma interação anterior, servindo o código **antigo**, sem a rota nova — uma
  chamada de teste devolveu 405 "Method Not Allowed" nele). Encerrei esse processo (`Stop-Process
  -Force`) para poder subir o backend com o código atualizado na mesma porta (é o mesmo servidor
  de dev deste projeto, ação local e reversível — não era um processo alheio); registrado aqui
  porque a tarefa não previa essa etapa explicitamente.
- Instalado `playwright-core` na pasta de rascunho da sessão (fora do repo) e usado o Edge do
  Windows já instalado na máquina (`channel: "msedge"`), mesmo padrão das etapas anteriores deste
  projeto. Gerado um áudio de **fala real** de ~47s via `System.Speech.Synthesis` do Windows
  (texto próprio descrevendo o teste) e injetado como microfone via
  `--use-fake-device-for-media-stream` + `--use-file-for-fake-audio-capture=<wav>` (equivalente a
  um microfone real falando, do ponto de vista do navegador).
- **Sessão real de tempo real, mais de um turno**: liguei o alternador "Transcrição em tempo
  real", cliquei para gravar, deixei rodar 25s (folga sobre o intervalo de commit de 6s) e parei.
  A caixa de transcrição acumulou texto correto em múltiplos trechos ("Um teste da etapa de
  consumo... Estou gravando uma fala real... Mais de um turno durante esta sessão... Primeiro
  turno de fala terminando agora..."), confirmando vários turnos concluídos. `consumo.jsonl`
  ganhou **4 linhas novas**, uma por turno, todas com `"modelo": "gpt-live-transcribe"` e
  `"tipo_usage": "duration"`:
  - `seconds: 6.0` → `custo_usd: 0.0017`
  - `seconds: 7.0` → `custo_usd: 0.0019833333333333335`
  - `seconds: 6.0` → `custo_usd: 0.0017`
  - `seconds: 6.0` → `custo_usd: 0.0017`
- **Conta na mão** (conferida contra a duração real de cada trecho, gravada no próprio registro):
  `segundos / 60 * 0,017`. Para 6,0s: `6/60 * 0,017 = 0,0017` — bate com o `custo_usd` gravado.
  Para 7,0s: `7/60 * 0,017 = 0,0019833...` — bate. Os quatro registros conferem exatamente.
- **Painel de consumo do frontend**: abri o painel numa página real (mesmo Edge headless, sem
  precisar de fala) e confirmei via `innerText` renderizado — sessão mostrando "Requisições: 5 |
  Tokens: 0 | Custo estimado: US$ 0.0106" e o dia de hoje agregando `11062 tokens — US$ 0.0512`
  (soma de todos os modelos do dia, incluindo os 4 registros novos do tempo real), sem nenhuma
  mensagem de erro visível — o painel não distingue por modelo, só agrega por dia, então os
  registros novos entram automaticamente sem precisar mudar o JS de renderização.
- **Falha da rota nova não trava a sessão — testado de fato**: outro teste (mesmo tipo de sessão
  real com fala) iniciou a gravação com o backend no ar, e **no meio da gravação** derrubei o
  processo do backend (via `Stop-Process -Force` a partir de outro processo, coordenado por um
  arquivo de sinalização) e deixei a gravação continuar por mais 15s **com o backend fora do ar**.
  Resultado: o status continuou "Gravando em tempo real…" o tempo todo, o transcript continuou
  recebendo texto novo normalmente (a sessão fala direto com a OpenAI via WebSocket, não passa
  pelo backend), o clique de parar funcionou normalmente ("Gravação em tempo real encerrada.") e
  **zero `pageerror`** foi capturado durante todo o teste — nenhuma exceção não tratada, nenhuma
  quebra de página. Backend religado depois.
- **Regressão — modo tempo real desligado / upload normal**: com o backend religado, enviei o
  mesmo áudio de fala real via `POST /transcrever` direto (`gpt-4o-mini-transcribe`, sem streaming,
  sem tempo real) → HTTP 200, transcrição correta, e uma linha nova em `consumo.jsonl` no formato
  de sempre (`"tipo_usage": "tokens"`, com `input_tokens`/`output_tokens`) — confirma que o
  caminho de tokens (usado por `gpt-4o-transcribe`/`gpt-4o-mini-transcribe`) não foi afetado pela
  mudança.
- Validação também de que o corpo é rejeitado antes de gravar qualquer coisa: testei via `curl`
  direto na rota nova com `type: "tokens"` (sem `gpt-live-transcribe` estar nessa lista de preços
  por token) → 422; corpo vazio → 422; `seconds: -1` → 422 — nenhum desses três chegou a gerar
  linha em `consumo.jsonl` (confirmado lendo o arquivo antes/depois).
- Backend deixado rodando (porta 8000, código atualizado) ao final, para o usuário poder usar ou
  testar sem precisar subir de novo. Arquivos de teste (script Node, wav sintetizado, flags de
  coordenação) ficaram todos na pasta de rascunho da sessão, fora do repositório.

### Critério de pronto
- [x] Preço por minuto do `gpt-live-transcribe` conferido na fonte oficial e registrado no código
      com data da consulta (US$ 0,017/min, <https://developers.openai.com/api/docs/pricing>,
      2026-08-19)
- [x] Uma sessão **real** no modo ao vivo (fala de verdade, mais de um turno) grava linha(s) em
      `consumo.jsonl` com `modelo` = `gpt-live-transcribe`, `tipo_usage` por duração e `custo_usd`
      calculado pelo preço por minuto — testado com fala real, 4 turnos, 4 linhas novas
- [x] Custo calculado conferido na mão contra a duração real do trecho — ver conta acima, os
      quatro registros batem exatamente
- [x] Painel de consumo do frontend mostra esses registros ao lado dos demais modelos, sem
      regressão na exibição dos registros antigos — testado no app real
- [x] Falha na rota nova (backend fora do ar) não trava nem interrompe a sessão de tempo real —
      testado de fato, derrubando o backend no meio de uma gravação real
- [x] Modo tempo real desligado segue funcionando igual (regressão de upload e gravação normal) —
      testado com o mesmo áudio via `POST /transcrever` direto
- [x] `transcritor/README.md` atualizado

### Diagnóstico
- A doc pública em linguagem natural (guia de transcrição em tempo real) não documenta o campo
  `usage` do evento `completed`; foi preciso consultar a referência de API dos server events
  (`conversation.item.input_audio_transcription.completed`) para confirmar o formato exato —
  união de dois formatos (`"type": "tokens"` ou `"type": "duration"`), e que `gpt-live-transcribe`
  (ASR cobrado por duração) sempre usa o segundo. Isso bateu exatamente com o que a
  `PROXIMA_TAREFA.md` já antecipava, então não foi preciso desenhar nada diferente do pedido.
- Como a validação do corpo acontece na camada do Pydantic (antes do corpo da rota rodar), uma
  requisição inválida nunca chega a `_registrar_consumo` — não há caminho para gravar lixo em
  `consumo.jsonl` a partir dessa rota.

### Novas demandas / riscos
- Nenhuma nova relacionada ao código. Único ponto de atenção: havia um processo de backend antigo
  esquecido ligado na porta 8000 no início desta tarefa (ver nota de transparência acima) — nada a
  fazer, só um lembrete de que sessões de teste anteriores às vezes deixam o servidor no ar.

### Ajuste no plano necessário?
Não — Etapa 4 concluída conforme especificado.

## [2026-08-19] — Etapa 5: Persistência da transcrição
Status: concluído
(Nível subido de `curto` para além do teto de ~15 linhas na seção "Como testei": o critério de
pronto pediu explicitamente texto salvo x exibido lado a lado nos dois modos em lote, mais uma
sessão ao vivo real multi-turno e o teste de regressão de backend fora do ar — não cabia sem
cortar o dado real que prova cada item.)

### Feito
- `transcritor/backend/main.py`: `_registrar_consumo` agora gera `id` (uuid4 hex), grava no
  registro e devolve o id (ou `None` sem gravar nada se falhar); nova `_registrar_transcricao`
  grava `transcricoes.jsonl` (`id_consumo`, `timestamp`, `modelo`, `texto`), pulando texto
  vazio/só espaço, chamada nos dois pontos do modo em lote (sem streaming e no
  `transcript.text.done`) e em `/consumo/tempo-real`; `UsageTempoReal` ganhou `texto: str | None`.
- `transcritor/frontend/index.html`: `reportarConsumoTempoReal(usage, texto)` agora manda também
  `dado.transcript` do turno no corpo do POST.
- `.gitignore` e `transcritor/README.md`: `transcricoes.jsonl` documentado/ignorado.

### Como testei (backend real, chave real da OpenAI)
- Achei um `uvicorn` órfão de sessão anterior (PID 19128, porta 8000, `python.exe` global, sem meu
  código) — derrubei e subi um novo a partir do `.venv` do projeto para garantir que os testes
  batessem no código editado.
- **Lote sem streaming** (`curl -F audio=@teste.wav`): resposta
  `"Este é um teste de transcricaldiade ou para validar a persistência do texto no backend."`;
  linha salva em `transcricoes.jsonl` com o **mesmo texto**, `id_consumo` = `20dc9faa...` batendo
  com o `id` da linha correspondente em `consumo.jsonl`.
- **Lote com streaming**: evento `final` com o mesmo texto; linha salva idêntica, `id` `01d625a3...`
  batendo, formato NDJSON inalterado.
- **Contrato antigo de `/consumo/tempo-real`** (`{"type":"duration","seconds":5.2}`, sem `texto`):
  200 OK, só gravou consumo (`transcricoes.jsonl` não cresceu). **Contrato novo** (com `texto`):
  gravou as duas linhas ligadas pelo mesmo id.
- **Sessão ao vivo real, múltiplos turnos**: Edge headless via `playwright-core` (instalado fora do
  repo, no scratchpad da sessão) com áudio sintetizado (`System.Speech`, ~40s, 3 "turnos" de fala)
  injetado como microfone (`--use-fake-device-for-media-stream` +
  `--use-file-for-fake-audio-capture`). Resultado: 5 turnos completados, 5 linhas novas em
  `transcricoes.jsonl`, cada `id_consumo` batendo com o `id` da linha de `consumo.jsonl` daquele
  turno (ex.: `244da4a0...` → texto "Turno de teste, falando sobre o registro de transcricao no
  backend."); a concatenação das 5 linhas salvas reproduz o transcript final exibido na tela.
- **Backend fora do ar durante gravação ao vivo** (regressão da Etapa 4): mesmo setup, matei o
  processo do backend (`taskkill /F`) ~8s após iniciar a gravação — a sessão continuou gravando e
  transcrevendo normalmente por mais 20s (WebSocket direto com a OpenAI, só o `fetch` acessório
  falha em silêncio) e encerrou limpo ao clicar em parar (`"Gravação em tempo real encerrada."`).
  Backend religado em seguida a partir do `.venv`, `GET /consumo` voltou a responder normalmente
  com o histórico intacto.
- Não testei: rotação/expiração de `transcricoes.jsonl` (fora do escopo, Backlog); leitura de
  `GET /consumo` para linhas antigas sem `id` — não quebrou (comportamento herdado, `registro.get`),
  mas não é o foco desta etapa.

### Critério de pronto
- [x] Upload sem streaming grava linha em `transcricoes.jsonl` com texto batendo e `id_consumo`
      existente em `consumo.jsonl`
- [x] Upload com streaming idem, sem alterar NDJSON nem comportamento na tela
- [x] Sessão real no modo ao vivo (multi-turno) grava uma linha por turno, ligada ao consumo do
      mesmo turno
- [x] Texto salvo conferido contra o texto exibido, colado acima para os dois modos
- [x] Backend fora do ar durante gravação ao vivo não trava a sessão (regressão testada)
- [x] Corpo antigo da rota `/consumo/tempo-real` continua aceito e grava só consumo
- [x] `.gitignore` e `transcritor/README.md` atualizados

### Novas demandas / riscos
- Nenhuma. Arquivos de teste (`.wav`, projeto `playwright-core`, scripts) ficaram todos fora do
  repositório, no scratchpad da sessão — nada disso entrou em `transcritor/`.

### Ajuste no plano necessário?
Não — Etapa 5 concluída conforme especificado.

## [2026-08-19] — Correção aprovada: fim perdido e palavras coladas no modo tempo real
Status: concluído
(Nível `completo` conforme declarado em `PROXIMA_TAREFA.md` — o critério pede transcript colado
como evidência em três pontos distintos.)

### Feito
- `transcritor/frontend/index.html`:
  - **Defeito 1 (fim perdido)**: `pararGravacaoTempoReal` (linha 1468) reestruturada. Agora, se
    houver áudio suficiente para o commit final, envia o commit, incrementa
    `commitsPendentesTempoReal` (linha 1477), para a captura local imediatamente
    (`limparRecursosTempoReal()` — mic, timers, analisador, sem fechar o WebSocket), mostra
    status "Encerrando… aguardando a transcrição do último trecho.", desabilita o botão de
    gravação, e arma um `setTimeout` de `TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS = 5000`
    (linha 1187) chamando `finalizarFechamentoTempoReal()` (fecha o WS de fato, linha 1501) se o
    tempo esgotar. Se não houver áudio suficiente para comitar, fecha direto, como antes.
  - O handler de `...completed` (linha 1436-1444) decrementa `commitsPendentesTempoReal` e, se
    `aguardandoUltimoTurnoTempoReal` estiver ligado e não houver mais commits pendentes, chama
    `finalizarFechamentoTempoReal()` — o `completed` que chega durante a espera segue o caminho
    normal já existente (entra no transcript, dispara `reportarConsumoTempoReal`) antes de fechar.
    Contagem por pendências (não só "o próximo completed") cobre o caso de haver mais de um
    commit em voo no momento do clique de parar (o commit periódico do timer e o final).
  - **Defeito 2 (palavras coladas)**: nova função `concatenarTurnoTempoReal(base, novoTrecho)`
    (linha 1209) — insere um espaço na emenda só quando nenhum dos dois lados já tem espaço ali;
    não mexe se `base` estiver vazio (sem espaço antes do primeiro turno). Usada no lugar da
    concatenação direta (`textoFinalizadoTempoReal +=`) no handler de `...completed`.
  - Nenhuma outra parte do arquivo foi tocada: intervalo de commit (6s), `turn_detection: null`,
    quebra de linha (continua ausente, decisão da Etapa 3), corte de segurança de 2min30s do modo
    normal — nada disso foi mexido.
- `backend/main.py`, `README.md` e demais arquivos: não tocados (fora da lista da tarefa).

### Como testei (rodado de fato, com fala real e backend real — não simulado)
Sintaxe do `<script>` extraído verificada com `node --check` (sem erros) antes de testar na UI.
Backend local já estava rodando (porta 8000, código do backend não mudou — não precisou reiniciar
para a mudança do frontend pegar, já que é `StaticFiles` servindo o arquivo do disco). Edge
headless via `playwright-core` (instalado fora do repo, na pasta de rascunho da sessão), áudio de
~35s com **4 frases distintas** gerado pelo sintetizador de voz do Windows
(`System.Speech.Synthesis`, PCM 24kHz mono), injetado como microfone via
`--use-fake-device-for-media-stream` + `--use-file-for-fake-audio-capture=<wav>`.

**Cenário 1 — fim da gravação + separador (áudio real, parado a ~35s, perto do fim da fala):**
- Frases ditas (texto exato enviado ao sintetizador):
  `"Primeiro turno de teste da correcao do modo tempo real. Segundo turno falando sobre o erro de
  palavras coladas entre turnos. Terceiro turno verificando se o separador funciona direito sem
  juntar as palavras. Quarto e ultimo turno, esta frase final precisa aparecer completa na tela
  depois de eu clicar para parar a gravacao."`
- Transcript final exibido na tela (colado literalmente, imprecisões de reconhecimento do modelo
  em algumas palavras — "Il" em vez de "Primeiro", "Torno" em vez de "Turno" — são qualidade do
  ASR, fora do escopo desta correção):
  `"Il turno de teste da correcao do modo tempo real. Segundo turno falando sobre o erro de
  palavras coladas entre turnos. s Terceiro turno verificando se o separador funciona. Na
  direito, sem juntar as palavras. Quarto e último. Torno, esta frase final precisa aparecer
  completa na tela. Mas depois de eu clicar para parar a gravação."`
- **Último trecho falado aparece na tela**: "Mas depois de eu clicar para parar a gravação." é o
  final do transcript — esse é exatamente o turno que o bug antigo perdia (commit final enviado,
  socket fechado antes do `completed` chegar). Frames WebSocket capturados confirmam a causa e a
  correção: commit final enviado em `36852ms` (depois do clique em parar, registrado em
  `36825ms`), `completed` correspondente recebido em `37525ms` — 673ms depois, dentro da janela de
  5s do timeout — com o texto exato "Mas depois de eu clicar para parar a gravação." Sem a
  correção, o socket teria fechado em `~36825ms`, antes desse `completed` chegar.
- **Consumo + transcrição ligados pelo mesmo id** (conferido nos arquivos, antes/depois — baseline
  66/16 linhas, depois do teste 74/24): última linha nova de `consumo.jsonl`
  (`id: "83879d7f2c4e4e9b8bb0031dc4a31fdb"`, `modelo: gpt-live-transcribe`, `segundos: 6.0`) bate
  exatamente com a última linha nova de `transcricoes.jsonl`
  (`id_consumo: "83879d7f2c4e4e9b8bb0031dc4a31fdb"`, `texto: "Mas depois de eu clicar para parar a
  gravação."`) — o turno final chegou a gravar em ambos, o que o bug antigo impedia.
- **Nenhuma palavra colada, nenhuma quebra de linha reintroduzida** (transcript de 6 turnos, acima
  — mais de 3 pedido no critério): checagem programática no texto completo —
  `transcript.includes("\n") === false`, `/  /.test(transcript) === false` (sem espaço duplo),
  `transcript.startsWith(" ") === false` (sem espaço no início). As emendas entre turnos ficaram
  com um único espaço (ex.: "...tempo real. Segundo turno...", "...entre turnos. s Terceiro
  turno..." — o "s" solto é imprecisão do modelo de fala, não duplicação/colagem da nossa
  concatenação).

**Cenário 2 — timeout de segurança (`completed` nunca chega, forçado de propósito):** gravação
iniciada, esperados 7s (cobrindo um commit periódico normal, confirmando que o modo funciona antes
de forçar a falha), então liguei uma flag de teste que engole (não repassa ao app) qualquer evento
`...completed` recebido pelo `WebSocket` a partir daquele ponto (instrumentação só do lado do
teste, via `addInitScript` interceptando `addEventListener` — não altera o arquivo da tarefa,
mesmo padrão de teste já usado na Etapa 2 deste plano para simular queda de conexão). Cliquei em
parar: status mudou para "Encerrando… aguardando a transcrição do último trecho.", botão
desabilitado — confirmado logo após o clique. Como o `completed` do commit final nunca chegou (1
evento engolido, confirmado por contador), a interface **não ficou presa em "gravando"**: depois
de exatos **5029ms** (bate com o timeout de 5000ms configurado + overhead de execução), o status
virou "Gravação em tempo real encerrada.", o botão voltou a ficar habilitado e a classe `gravando`
foi removida — recuperação automática via o `setTimeout` de segurança, como pedido no critério.

**Cenário 3 — regressão do modo tempo real desligado:** alternador de tempo real deixado no padrão
(desligado), gravação de 6s com o mesmo tipo de áudio (fluxo `MediaRecorder` + `POST
/transcrever`, não tocado por esta tarefa) → status "Transcrição adicionada ao texto abaixo.",
transcript "Primeiro turno de teste da correção do modo tempo real." — sem regressão.

Não testei: o caso de múltiplos commits pendentes simultâneos no momento do clique de parar (timer
periódico + final, ambos em voo) — a lógica por contador (`commitsPendentesTempoReal`) foi escrita
para cobrir esse caso, mas os testes acima não geraram esse cenário específico na prática (o
commit final saiu isoladamente nos dois cenários testados, sem um periódico ainda pendente no
mesmo instante); ficou coberto por leitura de código, não por teste dirigido.

Backend deixado rodando (porta 8000) ao final, no mesmo estado em que já estava (não reiniciado
por esta tarefa, já que só o frontend mudou). Arquivos de teste (`.wav`, script Node,
`playwright-core`) ficaram todos na pasta de rascunho da sessão, fora de `transcritor/`.

### Critério de pronto
- [x] Gravação real de mais de um turno, encerrada por clique: o último trecho falado aparece na
      tela — testado e colado acima (Cenário 1)
- [x] Esse mesmo último turno gera registro em `consumo.jsonl` **e** em `transcricoes.jsonl`,
      ligados pelo mesmo id — conferido nos arquivos, antes/depois (acima)
- [x] Nenhuma palavra colada na emenda entre turnos, nenhuma quebra de linha reintroduzida —
      transcript de 6 turnos colado acima como evidência (mais que os 3+ pedidos)
- [x] Sem espaço duplicado, sem espaço sobrando no início — checagem programática, ambos `false`
- [x] Timeout de segurança testado: `completed` forçado a nunca chegar (Cenário 2) — interface
      não ficou presa em "gravando", recuperou em 5029ms
- [x] Regressão: modo tempo real desligado segue igual — testado (Cenário 3)

### Novas demandas / riscos
- Nenhuma nova relacionada ao código. Ponto de atenção só de teste (não de produto): não cobri por
  teste dirigido o caso de dois commits pendentes simultâneos no clique de parar (ver "Não
  testei" acima) — a lógica do contador foi desenhada para esse caso, mas vale o PM saber que não
  foi validado na prática, caso queira uma tarefa futura dedicada a isso.

### Ajuste no plano necessário?
Não — correção concluída conforme especificado.

## [2026-08-19] — Etapa 6: Linha do tempo no painel de consumo
Status: concluído

### Antes de codificar — skill dataviz
Li `SKILL.md`, `references/marks-and-anatomy.md`, `references/palette.md` e
`references/interaction.md` antes de escrever qualquer código de visualização.

- **Forma**: um ponto por requisição num eixo de tempo (não um "chart" com categoria a codificar
  por cor) — série única, então **sem legenda** (marks-and-anatomy.md: "a single series needs no
  legend box").
- **Marca**: círculo `r=4` (diâmetro 8px, dentro do mínimo `≥8px`) com **anel de 2px na cor da
  superfície** (`stroke="#fff" stroke-width="2"`), técnica descrita em marks-and-anatomy.md para
  separar pontos que se sobrepõem, sem desenhar borda extra.
- **Alvo de clique/hover**: círculo transparente `r=14` (~28px) por cima de cada marca — acima do
  mínimo de 24px pedido em `interaction.md` ("give each point a transparent hit area of at least
  24px").
- **Rótulo de preço em cada ponto**: a diretriz geral da skill é rotular seletivamente ("never a
  number on every point"), mas a tarefa pede explicitamente o preço acima de **cada** ponto — é o
  requisito do produto (comparar custo entre pontos), então prevalece sobre a diretriz geral;
  registrado como decisão consciente, não como desvio não percebido.
- **Cor**: reaproveitei o azul já usado no resto da interface (`#2563eb`, o mesmo do botão
  "Transcrever" e das barras do gráfico diário) em vez de importar a paleta de referência da
  skill — este frontend é inteiramente light-mode, sem tokens de tema, então manter a mesma cor
  de acento já em uso é mais consistente do que introduzir um novo hex.
- **Hover**: como o requisito explícito da tarefa é o **clique** abrindo um popup com o texto
  (não um tooltip customizado), usei um `<title>` nativo do SVG em cada ponto como hover mínimo
  (resumo: modelo, preço, horário) — dentro do orçamento de "sem biblioteca, HTML de arquivo
  único" da tarefa, sem construir uma camada de tooltip própria.

### Feito
- `transcritor/backend/main.py`: `GET /consumo` ganhou a chave `requisicoes` (aditiva — `sessao`
  e `por_dia` com o mesmo código/formato de antes). Implementação: um dicionário
  `id_consumo → texto` é montado lendo `transcricoes.jsonl` uma vez; depois, no mesmo loop que já
  agregava `por_dia`, cada linha de `consumo.jsonl` vira um item de `requisicoes` (`id`,
  `timestamp`, `modelo`, `custo_usd`, `texto`), casando pelo `id`. Registro sem `id` (anterior à
  Etapa 5) entra com `texto: null`. Lista ordenada por `timestamp` no fim. Mesma tolerância a
  lixo já existente (linha inválida pulada, arquivo ausente não derruba a rota).
- `transcritor/frontend/index.html`:
  - Painel de consumo alargado (`min(95vw, 42rem)`, era `min(90vw, 24rem)`) para caber a linha do
    tempo.
  - Novo bloco `#blocoLinhaTempoConsumo` com botão de zoom (`#botaoZoomLinhaTempo`) e o container
    `#linhaTempoConsumo`, onde `renderizarLinhaTempoConsumo()` desenha um `<svg>` à mão (sem
    biblioteca) a cada carregamento do painel.
  - Escala "hora": largura do SVG = largura do container (`clientWidth`), então tudo que existe
    em `requisicoes` sempre cabe sem rolar. Escala "minuto": pixels por segundo fixos
    (`PX_POR_SEGUNDO_ESCALA_MINUTO = 10`), então a largura cresce com o intervalo real dos dados —
    rola horizontalmente, abrindo já rolado até o último ponto real (não até `scrollWidth` bruto,
    que ficaria em espaço vazio — ver bug corrigido abaixo).
  - Clique (ou Enter/Espaço, o ponto é focável) abre `#fundoPopupRequisicao`, um modal novo no
    mesmo padrão dos existentes (fundo escurecido, `✕`, clique fora, Esc), com o texto ou o aviso
    de ausência de transcrição.
  - `carregarConsumo()` passou a desocultar os containers **antes** de chamar
    `renderizarConsumo()` (era depois) — a escala "hora" mede `clientWidth`, que é 0 num elemento
    `[hidden]`.
- `transcritor/README.md`: documentada a chave `requisicoes` da rota (com exemplo) e a seção
  "Linha do tempo das requisições" (zoom, popup, alvo de clique, decisão de mostrar tudo sem
  filtrar por dia).

### Dois bugs achados e corrigidos durante o teste (não óbvios pela leitura do código)
1. **Item de grid não encolhe com conteúdo grande**: `.painel-config` é `display: grid`; um filho
   de grid não encolhe abaixo do tamanho intrínseco do conteúdo por padrão. Com o SVG da escala
   "minuto" chegando a ~980.000px de largura (ver por quê, abaixo), o container inteiro — e o
   modal com ele — esticava para acompanhar, e `overflow-x: auto` nunca entrava em ação (não
   havia overflow a esconder, o pai tinha crescido junto). Corrigido com `min-width: 0` em
   `#blocoLinhaTempoConsumo` e `.linha-tempo-consumo`. Confirmado via Playwright
   (`clientWidth`/`scrollWidth` do container antes/depois — abaixo).
2. **Auto-scroll caía em espaço vazio**: o domínio do eixo tem uma folga de 8% para cada lado
   (para os pontos extremos não colarem na borda). Rolar para `scrollWidth` (o fim bruto do SVG)
   caía nessa folga, não no último ponto real. Corrigido calculando a posição do último ponto
   desenhado (`xUltimoPonto`) e rolando para `xUltimoPonto - larguraDisponível + margem`.

### Como testei
Sem Playwright disponível no ambiente por padrão — instalei via `npx playwright install
chromium` (script descartável em `.claude/tmp`/scratchpad, fora do repositório) para dirigir um
Chromium real contra o backend rodando de verdade.

- **Áudio de teste**: sintetizado com `System.Speech` do Windows (TTS nativo, sem depender de
  gravação manual), ~562KB, frase mencionando "comparando o custo entre dois modelos diferentes".
- **Servidor**: havia um backend antigo (PID 31920, python.exe, iniciado 16:39:54) já ocupando a
  porta 8000 rodando o código **anterior** a esta tarefa — parei esse processo (dev local, sem
  dado em risco — nada persiste nele além dos `.jsonl` já em disco) e subi um novo `uvicorn` com
  o código atualizado antes de testar.
- **Critério "GET /consumo devolve requisicoes com texto casado por id"**: `curl
  http://127.0.0.1:8000/consumo` colado (truncado aqui pelo tamanho real — 76 requisições; ver
  chamada completa na sessão) —
  registro antigo (sem id): `{"id": null, "timestamp": "2026-08-18T21:28:47.125831+00:00",
  "modelo": "gpt-4o-transcribe", "custo_usd": 0.00069, "texto": null}`;
  registro recente (com texto): `{"id": "20dc9faa163f4cb38d83cbc5f391d083", "timestamp":
  "2026-08-19T19:36:19.547257+00:00", "modelo": "gpt-4o-transcribe", "custo_usd": 0.000405,
  "texto": "Este é um teste de transcricaldiade ou para validar a persistência do texto no
  backend."}`. `sessao`/`por_dia` no mesmo formato de sempre, valores batendo com os já
  conferidos em etapas anteriores.
- **Critério "comparação funciona na prática"**: enviei o mesmo áudio de teste para
  `gpt-4o-transcribe` e, 1,5s depois, para `gpt-4o-mini-transcribe`, via `POST /transcrever` real
  (dois `curl`, backend real, sem mock). Os dois registros em `consumo.jsonl`:
  `gpt-4o-transcribe` → `custo_usd: 0.0006575` (21:02:09 UTC); `gpt-4o-mini-transcribe` →
  `custo_usd: 0.00033375` (21:02:10 UTC, ~1,5s depois) — mini custou quase metade, consistente
  com a tabela de preços do PLANO.md. No painel (Playwright), os dois pontos aparecem lado a lado
  na escala "minuto", 15,14px de distância (a 10px/segundo, bate com ~1,5s), com os preços
  legíveis acima de cada um — clique no ponto mais recente abriu o popup com
  `"gpt-4o-mini-transcribe — US$ 0.0003 — 19/08/2026, 18:02:10"` e o texto transcrito batendo
  exatamente com o que a API devolveu.
- **Zoom**: medido via `getAttribute("width")` do `<svg>` e `clientWidth` do container — escala
  "hora": `624 === 624` (largura do SVG igual à do container, sem rolagem, as 76 requisições
  cabem). Escala "minuto": `983.721px` de largura (span real do histórico, ~2 dias, a 10px/s —
  ver nota de UX abaixo) — distância entre os dois pontos mais próximos (o par de teste acima)
  medida em 15,14px, visualmente distintos e clicáveis em separado (confirmado por clique
  individual no último ponto).
- **Popup com texto / sem texto**: clique no ponto mais recente (com texto) abriu o popup com o
  texto correto (colado acima). Clique num ponto antigo (sem `id`, via `dispatchEvent` de
  `click` — o clique geométrico do Playwright não conseguia isolar um ponto específico entre
  vários quase sobrepostos na escala "hora" densa, então despachei o evento direto no elemento
  para testar a lógica de clique em si) abriu o popup com `"gpt-4o-transcribe — US$ 0.0007 —
  18/08/2026, 18:28:47"` e o texto **"Não há transcrição guardada para esta requisição."** —
  sem erro no console.
- **Console do navegador**: três execuções separadas do Playwright (abrir painel + zoom + dois
  popups; upload real pela UI) — `CONSOLE_MSGS: []` nas três, incluindo `pageerror`.
- **Regressão — sessão/dia**: após as duas chamadas de comparação, o painel mostrou "Requisições:
  2, Tokens: 323, Custo estimado: US$ 0.0010" — bate com 161+162 tokens e
  0,0006575+0,00033375 ≈ 0,00099125 arredondado para 4 casas.
- **Regressão — upload pela UI real** (não só `curl`): Playwright preencheu `#audio` com o mesmo
  arquivo de teste, clicou "Transcrever", `#resultado.sucesso` apareceu com o texto correto, e o
  ponto novo apareceu na linha do tempo (76 → 77 pontos) na reabertura do painel — sem erro no
  console.
- **Não testei**: gravação pelo microfone (normal e tempo real) via browser — não alterei nenhum
  código desses fluxos nesta tarefa (só `GET /consumo`, que é aditivo, e o painel de consumo), e
  as Etapas 2–5 e a correção aprovada já cobriram esses caminhos com teste real; risco de
  regressão nesta tarefa específica é baixo por não ter tocado nesse código.

### Nota de UX (não é bug, registro para o PM avaliar)
Com ~76 requisições acumuladas em ~2 dias de teste de desenvolvimento (não filtradas — decisão
explícita do plano: "a linha do tempo mostra tudo que existe"), a escala **"hora"** fica com
rótulos de preço colados/ilegíveis onde há muitos pontos próximos — é o único jeito de cumprir ao
mesmo tempo "cabe o dia inteiro" e "preço acima de cada ponto" com esse volume de dados de teste
acumulado. Em uso real (uma sessão de pesquisa, não dois dias de teste de dev), a densidade tende
a ser bem menor. Não mexi nisso por não ser uma opção aprovada (filtrar/paginar está no Backlog
como não aprovado). Screenshots fora do repositório, em
`C:\Users\GUILHE~1\AppData\Local\Temp\claude\c--Users-Guilherme-Bueno-Desktop-projetinhos-agentes-base\53392e1a-cfa9-448c-a8a1-7a9985af70c0\scratchpad\`:
`consumo_hora.png` (densidade descrita acima), `consumo_minuto.png`, `popup_com_texto.png`,
`popup_sem_texto.png` — pasta de sessão, pode não sobreviver ao encerramento do ambiente.

### Critério de pronto
- [x] `GET /consumo` devolve `requisicoes` com texto casado por id, e `sessao`/`por_dia`
      inalterados — trecho real colado acima (registro antigo com `texto: null` e recente com
      texto)
- [x] Painel mostra um ponto por requisição, posicionado pelo horário, com o preço acima do ponto
- [x] Comparação funciona na prática — dois preços do mesmo áudio em modelos diferentes, colados
      acima (0,0006575 vs 0,00033375), pontos próximos e legíveis na escala minuto
- [x] Zoom por minuto separa visualmente pontos a poucos segundos de distância (15,14px medidos);
      zoom por hora cabe o painel inteiro sem rolar (624px = 624px, com 76 pontos)
- [x] Clique num ponto abre o popup com o texto, conferido contra `transcricoes.jsonl` (bateu
      exatamente)
- [x] Ponto sem transcrição abre popup com aviso, sem erro no console
- [x] Nenhuma regressão: números de sessão/dia corretos; upload testado pela UI real; gravação
      normal/tempo real não tocadas nesta tarefa (não testadas de novo — ver "Não testei")
- [x] Nenhum erro no console do navegador durante todo o uso testado (três execuções, `[]`)
- [x] `transcritor/README.md` atualizado

### Novas demandas / riscos
- Densidade de rótulos na escala "hora" com muitos pontos próximos (ver "Nota de UX" acima) —
  não é regressão desta tarefa, é uma tensão inerente ao volume de dados de teste acumulado com a
  decisão já tomada de não filtrar/paginar a linha do tempo.
- Dois bugs de CSS/JS encontrados e corrigidos durante o próprio desenvolvimento desta etapa (grid
  não encolhendo, auto-scroll caindo em espaço vazio) — já corrigidos e testados, registrados aqui
  só para rastreabilidade, não são pendência.
- Gravação pelo microfone (normal e tempo real) não foi retestada nesta tarefa — risco baixo
  (nenhum código desses fluxos foi tocado), mas fica registrado para o PM decidir se quer uma
  rodada de teste manual antes de considerar o plano inteiro (Etapa 7) encerrado.

### Ajuste no plano necessário?
Não — critério de pronto da Etapa 6 atendido conforme especificado.

## [2026-08-19] — Etapa 7: Ajustes da linha do tempo + testes finais e documentação
Status: concluído

### Feito
- `transcritor/frontend/index.html` — Parte 1, ajuste 1 (preço só na escala "minuto"):
  - o bloco que desenha o `<text>` de preço acima de cada ponto (dentro do `forEach` de
    `renderizarLinhaTempoConsumo`) agora só executa `if (escalaLinhaTempo === "minuto")`;
  - o `aria-label` do `<svg>` também passou a citar o preço condicionalmente (só quando a escala é
    "minuto"), para não afirmar algo que não está mais no desenho na escala "hora";
  - comentário de cabeçalho da seção (que documentava a decisão original de rotular todo ponto,
    referenciando a skill `dataviz`) atualizado para explicar a mudança e por que ela ainda não
    esconde a informação (`title` do hover e popup de clique continuam mostrando o preço nas duas
    escalas).
- `transcritor/frontend/index.html` — Parte 1, ajuste 2 (roda alterna o zoom, com navegação
  horizontal preservada):
  - `trocarEscalaLinhaTempo(novaEscala)` extraída do handler de clique do botão (mesma lógica,
    agora reutilizável) e chamada também pelo novo listener `wheel` em `#linhaTempoConsumo`;
  - **desenho escolhido para a restrição da tarefa** (roda pura vira zoom, mas a escala "minuto"
    precisa continuar navegável horizontalmente): o listener ignora o evento quando
    `evento.shiftKey` é verdadeiro — nesse caso **não** chama `preventDefault()`, deixando o
    navegador rolar horizontalmente sozinho (Shift+roda é o gesto nativo do Chromium/Edge para
    isso, funciona mesmo o container tendo `overflow-x: auto` sem nenhum código adicional). Sem
    Shift, o evento é interceptado (`preventDefault`) e o sentido do `deltaY` decide a escala alvo
    (`> 0` → "minuto", `< 0` → "hora") em vez de alternar por contagem de evento — trackpads
    disparam dezenas de eventos `wheel` por gesto, e alternar a cada evento faria a escala
    piscar/voltar; mapear pelo sinal é idempotente (repetir o mesmo sentido não faz nada depois da
    primeira troca);
  - o listener está no próprio `#linhaTempoConsumo` (não em `#fundoConsumo` nem em um ancestral
    maior), então só captura a roda quando o cursor está sobre a linha do tempo — rolar o resto do
    painel (histórico diário, gráfico de barras) continua propagando normalmente para a página.
- `transcritor/README.md` — seção "Linha do tempo das requisições" reescrita para documentar os
  dois ajustes acima (preço só em "minuto"; zoom por roda com os dois estados; navegação horizontal
  por Shift+roda ou pela barra de rolagem) e removida a frase antiga que afirmava o preço aparecer
  acima de todo ponto nas duas escalas.
- `.claude/estado/PLANO.md` — **Backlog**: conferido; os dois itens exigidos pela etapa já
  constavam (blocos com sobreposição/redundância — linha do "transcrição em blocos com
  sobreposição..."; limpeza de transcrições antigas — linha "rotação/limpeza automática de
  transcrições antigas..."). Nenhuma edição foi necessária.
- Nenhuma mudança em `backend/main.py` nem no comportamento do modo tempo real (intervalo de
  commit, `turn_detection`, corte de bordas) — fora do escopo desta etapa, conforme instruído.

### Validação (rodado de fato, com fala real, ponta a ponta)
Suite automatizada em Node + `playwright-core` (Edge headless real, mesmo padrão das etapas
anteriores), script em `test.mjs` na pasta de rascunho da sessão (fora do repo). Três instâncias
separadas de navegador (o `--use-file-for-fake-audio-capture` é fixado no lançamento do processo),
cada uma com um `.wav` de fala real gerado pelo sintetizador de voz do Windows
(`System.Speech.Synthesis`, 16kHz/16-bit/mono), backend local já no ar com `OPENAI_API_KEY` real:

- **Upload sem streaming**: HTTP 200, texto "Teste de upload do assistente de pesquisa por áudio.
  Etapa 7, rodada final de testes." reconhecido corretamente.
- **Upload com streaming**: alternador ligado, HTTP 200 em stream, texto final equivalente
  reconhecido corretamente ("Etapa 7: Rodada final de testes" — variação de pontuação do modelo,
  não erro de transporte).
- **Painel de consumo / linha do tempo** (medido no DOM/SVG real via `page.$$eval`, não a olho):
  - escala "hora": 81 pontos, **0** elementos `<text>` com conteúdo iniciando em "$" (nenhum rótulo
    de preço) — confirma o ajuste 1;
  - escala "minuto" (alternada rolando a roda sem Shift sobre `#linhaTempoConsumo`): 81 pontos,
    **81** rótulos de preço — um por ponto, como antes;
  - `#botaoZoomLinhaTempo` mostrou "Zoom: Minuto" e depois "Zoom: Hora" acompanhando a troca feita
    pela roda, nas duas direções;
  - `scrollLeft` do container forçado a `0` na escala "minuto", depois Shift+roda (`deltaY: 300`)
    → `scrollLeft` foi para `300` (rolou), confirmando a navegação horizontal preservada; a escala
    continuou "Zoom: Minuto" (Shift+roda não mexeu no zoom);
  - roda disparada sobre `#consumoDiarioLista` (fora da linha do tempo) → escala continuou "Zoom:
    Hora", sem alternar — confirma que só a linha do tempo captura a roda;
  - botão de zoom clicado depois de tudo isso → ainda alterna corretamente ("Zoom: Minuto"),
    confirma que o botão não quebrou com a mudança;
  - popup num ponto com `aria-label` "...com transcrição" → mostrou o texto real salvo em
    `transcricoes.jsonl` (conferido: começa com "Este é um teste de transcri..."), meta com modelo
    e preço;
  - popup num ponto com `aria-label` "...sem transcrição" (registro antigo, sem `id`) → mostrou
    "Não há transcrição guardada para esta requisição.", sem quebrar;
  - sessão e histórico diário exibidos batem com `GET /consumo` consultado por `curl` antes do
    teste (7 requisições/949 tokens/US$ 0,0035 na sessão ao final; dois dias agregados).
- **Gravação normal pelo microfone** (fala real via fake device, `microfone.wav`): clique inicia
  (`.gravando` aplicada), ~4s de fala, clique para parar → status "Transcrição adicionada ao texto
  abaixo.", `#transcriptRapido` foi de `""` para "Teste de gravação normal pelo microfone." — texto
  reconhecido bate com a fala.
- **Modo tempo real, múltiplos turnos** (fala real via fake device, `tempo_real.wav`, ~33s cobrindo
  vários commits de 6s): alternador ligado, gravação de ~34s, texto incremental confirmado ainda
  gravando (trecho parcial capturado no meio: "...Terdisparado pelo temporizador perió"), parado →
  status "Gravação em tempo real encerrada.", **último trecho de fala presente na tela**
  ("...O fechamento da conexão. Primeiro turno da" — a cauda "Primeiro turno da" é o fake-audio
  reiniciando o `.wav` porque a gravação, incluindo a espera pelo `completed` final, passou dos
  ~33s de áudio disponível; não é bug do app). Conferido nos arquivos reais depois do teste:
  6 linhas novas de `gpt-live-transcribe` em `consumo.jsonl` (custos entre US$ 0,0014 e US$ 0,0020,
  batendo com `segundos/60*0,017`) e as mesmas 6 linhas em `transcricoes.jsonl`, **cada uma com o
  mesmo `id`/`id_consumo`** (ex.: `80b1ffdd3e274266bae8af5d3329653e` no último turno, texto
  "O fechamento da conexão. Primeiro turno da" nos dois arquivos) — critério "mesmo id" confirmado
  no artefato real, não só na tela.
- **Console do navegador**: `page.on("console"/"pageerror")` capturado nas três fases. Único erro:
  `Failed to load resource: the server responded with a status of 404 (Not Found)` — confirmado com
  `curl http://127.0.0.1:8000/favicon.ico` → 404. É o pedido automático de favicon do navegador;
  o backend nunca serviu um (`StaticFiles(html=True)` não tem fallback para caminhos com extensão
  fora do índice), pré-existente a esta etapa e a nenhum dos fluxos testados — não é erro dos
  fluxos de transcrição/consumo, é uma lacuna cosmética não coberta pelo escopo desta tarefa.
  Nenhum outro `console.error` nem `pageerror` em nenhuma das três fases.
- Regressão: os três fluxos principais (upload, gravação normal, tempo real) e o painel de consumo
  inteiro foram exercitados nesta mesma rodada — nenhuma quebra encontrada em nenhum deles.

### O que não testei
- Não testei em navegador diferente de Chromium/Edge (mesma limitação já registrada em etapas
  anteriores) — o app roda em contexto único de navegador local do usuário, sem CI multi-browser.
- Não forcei o corte de segurança de 2min30s da gravação normal nem o timeout de 5s de fechamento
  do modo tempo real nesta rodada — já validados em etapas anteriores (Etapa 2/correção aprovada),
  fora do escopo desta etapa (que não mexeu nessa lógica).
- Não limpei manualmente `consumo.jsonl`/`transcricoes.jsonl` antes do teste — a suite rodou sobre
  o histórico acumulado de etapas anteriores (79→81 pontos na linha do tempo ao longo da sessão),
  o que é o cenário real de uso (decisão do projeto de não filtrar/paginar), não um ambiente limpo.

### Critério de pronto
- [x] Escala "hora" sem rótulo de preço; escala "minuto" com o preço acima de cada ponto —
      conferido no DOM/SVG (0 de 81 vs. 81 de 81)
- [x] Roda do mouse alterna as escalas, e o rótulo do botão acompanha
- [x] Navegação horizontal na escala "minuto" continua possível — Shift+roda, testado
      (`scrollLeft` 0→300); documentado no README
- [x] Rolar fora da linha do tempo (resto do painel) não alterna zoom — testado sobre
      `#consumoDiarioLista`
- [x] Upload com e sem streaming: transcrição correta, consumo e transcrição gravados (painel
      mostrou os pontos novos com texto depois do upload)
- [x] Gravação normal pelo microfone: transcrição correta na tela
- [x] Modo tempo real, mais de um turno: último trecho aparece na tela e gera registro em
      `consumo.jsonl` **e** `transcricoes.jsonl` com o mesmo id (6 turnos, ids conferidos)
- [x] Painel: sessão e por dia corretos, as duas escalas, os dois tipos de popup
- [x] Nenhum erro no console do navegador em nenhum dos fluxos — **com uma ressalva**: o 404 de
      `favicon.ico` aparece nas três fases; é pré-existente (backend nunca serviu favicon) e não
      relacionado a nenhum fluxo de transcrição/consumo desta ou de etapas anteriores — ver "Novas
      demandas" abaixo
- [x] `transcritor/README.md` conferido e atualizado
- [x] Backlog do `PLANO.md` com os dois itens exigidos pela etapa (já constavam, nenhuma edição
      necessária)

### Novas demandas / riscos
- **`favicon.ico` 404** (achado nesta etapa, fora do escopo): o backend não serve nenhum favicon,
  gerando um `console.error` de 404 a cada carregamento da página, em qualquer fluxo — cosmético,
  não afeta nenhuma funcionalidade, mas tecnicamente é "um erro no console" se o critério for lido
  ao pé da letra. Sugestão de tarefa pequena para o PM: servir um favicon estático (ou uma resposta
  vazia 204) em `GET /favicon.ico`.
- Backend local (porta 8000) **deixado rodando** ao final desta etapa, com o `.env` e a chave real
  já carregados — mesma prática das etapas anteriores, para o usuário poder abrir
  `http://127.0.0.1:8000/` e usar o app imediatamente sem precisar subir o servidor de novo.
- Script de teste (`test.mjs`) e os três `.wav` de fala sintetizada ficaram só na pasta de
  rascunho da sessão, fora do repositório — nada disso entrou em `transcritor/` nem em
  `.claude/estado/`.
- **Plano concluído**: esta era a Etapa 7/7 (última) do plano vigente
  (`.claude/estado/PLANO.md`) — todas as etapas e a correção aprovada estão marcadas concluídas.
  Fica a critério do PM decidir sobre arquivamento do `PLANO.md`/`PROGRESSO.md` (o próprio
  `EXECUTOR.md` cita este registro "completo" como base para a virada de plano).

### Ajuste no plano necessário?
Não — critério de pronto da Etapa 7 atendido conforme especificado (com a ressalva cosmética do
favicon, registrada acima para o PM avaliar como item novo, não como pendência desta etapa).

## [2026-08-20] — Correção aprovada (segunda), eixo do tempo da linha do tempo
Status: concluído

### Feito
- `transcritor/frontend/index.html`: laço de marcas do eixo (`renderizarLinhaTempoConsumo`)
  reescrito — passo dinâmico (`escolherPassoEixo`, escada 10s a 1 dia, alvo ≥80px via `pxPorMs`),
  alinhado a fronteiras locais (`primeiraMarcaAlinhada`/`proximaMarcaEixo`, via
  `setSeconds/Minutes/Hours/Date`, não epoch cru), rótulo com precisão dependente do passo
  (`HH:MM:SS` <1min, `HH:MM` em minuto, `HHh` em hora+, evitando texto repetido) e prefixo de data
  (`dd/mm`) só na primeira marca de cada dia.
- `transcritor/README.md`: item 3 novo na seção "Linha do tempo das requisições" descrevendo o
  eixo (hora de relógio, passo dinâmico, virada de dia).
- Testado com o histórico real (`consumo.jsonl`, 89 requisições, 30,5h, cruzando meia-noite duas
  vezes) via Playwright contra o backend local: medi contagem/overlap por `getBBox` antes e depois
  da mudança, e simulei um segundo cenário (burst de 3min em 480px) para confirmar que o passo
  também sobe da escada quando o intervalo é curto (não fica sempre em 10s).
- Não testei em navegador fora de Chromium (mesma limitação já registrada em etapas anteriores).

### Critério de pronto
- [x] Escala "minuto": rótulo "18:28:50" bate com o timestamp real da requisição mais próxima
      ("18/08/2026, 18:28:47" — 3s de distância, dentro do passo de 10s; 28,75px no SVG)
- [x] Escala "hora": ticks "18/08 18h" → "19/08 00h" → "06h" → "12h" → "18h" → "20/08 00h" — as
      duas viradas de meia-noite do histórico real marcadas, sem repetir data fora delas
- [~] Contagem: hora 35→**6** (dataset real, 30,5h); minuto 12.737→**12.756** (praticamente
      igual) — ver "Novas demandas" abaixo, não é regressão nem bug introduzido
- [x] Zero overlap nas duas escalas, medido por `getBBox` (x0/x1 de cada rótulo), não a olho
- [x] Reconferência: zoom por botão e roda (Minuto↔Hora), Shift+roda (`scrollLeft` 0→1000),
      popup com texto e sem texto — todos ok
- [x] Zero erro novo de console/`pageerror` (só o 404 de favicon, pré-existente)
- [x] `transcritor/README.md` atualizado

### Novas demandas / riscos
- **Achado sobre o critério de contagem da escala "minuto"**: o passo dinâmico, calculado
  honestamente, resolve para 10s neste dataset — igual ao valor fixo anterior — porque
  `PX_POR_SEGUNDO_ESCALA_MINUTO = 10` (fora do escopo desta correção, que ficou restrita ao "laço
  que começa em `const passoMs`") faz a largura do SVG escalar linearmente com a duração exibida,
  deixando `pxPorMs` constante (~0,01px/ms) **independente da duração**; 10s × 0,01 = 100px já é o
  menor degrau da escada que bate o alvo de 80px. Medido (não estimado): o espaçamento por rótulo
  já era exatamente 100px **antes** da correção — a régua não era fisicamente densa, só numerosa
  (12,7 mil nós, porque a largura total é de ~1,27 milhão de px para 30,5h de histórico). Reduzir
  a contagem de fato exigiria mexer na largura/escala de pixels-por-segundo da escala "minuto", o
  que ficaria fora do escopo apontado no contexto da tarefa — não mexi nisso.

### Ajuste no plano necessário?
Sim — o critério "queda de ~8.700 para algo compatível com 80–120px" pressupunha que a densidade
antiga fosse visualmente menor que 80px; medido, já era exatamente 100px (ver achado acima). A
régua "minuto" segue com contagem alta (12,7 mil) por design (largura ∝ duração), não por bug de
passo. Decisão do PM: aceitar como está (o espaçamento por rótulo já bate o alvo, só que numeroso
no total), ou abrir tarefa nova para revisitar `PX_POR_SEGUNDO_ESCALA_MINUTO`/a estratégia de
largura da escala "minuto".
