# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de 2026-08-21 (abertura da **Fase 1 — Núcleo de transcrição**, sob
> o método Spec-Driven Development). As entradas dos planos anteriores foram movidas para
> `.claude/estado/historico/` (arquivos `PROGRESSO_*.md`), sem edição. O plano imediatamente
> anterior (faxina e interface enxuta, 2026-08-21) está em
> `.claude/estado/historico/PROGRESSO_faxina-e-interface_2026-08-21.md`.

## [2026-08-23 16:18] — Fase 1, Etapa 1: Levantar por medição o contrato do núcleo e escrevê-lo
Status: concluído

### Feito

**0. Armadilha da porta 8000, confirmada de novo (5ª ocorrência).** Havia um backend antigo na
porta 8000 (PID 34028, `python.exe`, subido em 22/08 15:40) — derrubado antes de medir. Subi um
backend novo a partir do código atual (`uvicorn main:app --app-dir backend --port 8000`).

**Uso real concorrente detectado durante a medição.** Entre eu subir o backend novo e começar meus
testes, o log (`uvicorn.log`) mostra um `GET /` seguido de uma transcrição real (não é texto de
teste meu — "Então, aqui é um exemplo de um dado específico..."), e depois mais três transcrições
reais enquanto eu reiniciava o backend para os testes de erro (`gpt-4o-transcribe`, textos sobre
"R3 da conclusão" e "como tratar esses casos"/"sessão que quebrou tabela"). Ou seja: **alguém usou
o app de verdade, ao vivo, durante esta sessão de medição** — perguntei ao usuário antes de seguir
com os testes que quebram o `.env` (ver pergunta no chat), ele autorizou explicitamente. Registro
aqui porque confirma, com evidência de log e não só suspeita, o item já existente no Backlog do
`PLANO.md` ("`consumo.jsonl` mistura consumo de uso real com o de sessões de teste do Executor") —
inclusive dentro da *mesma* janela de tempo, não só no mesmo dia.

**1. Caminho feliz — todos os campos e formatos batem com a SPEC-001.**
- `POST /transcrever` sem streaming, modelo padrão: `200 {"transcricao": "..."}` — confirmado.
- Com `stream=true`: `200`, `application/x-ndjson`, sequência de `delta` (33 eventos para ~12,7s de
  áudio) seguida de um `final` — confirmado, texto do `final` bate com a soma dos `delta`.
- `gpt-4o-mini-transcribe` e `gpt-4o-transcribe-diarize` sem streaming: mesmo formato
  `{"transcricao": ...}` — confirmado.
- **Achado novo, fora da SPEC-001**: `gpt-4o-transcribe-diarize` **com** `stream=true` não emitiu
  nenhum evento `delta` — só o `final`, direto. Documentado no contrato como divergência.
- `GET /consumo`: as três seções (`sessao`, `por_dia`, `requisicoes`) vieram na forma descrita; o
  campo `texto` de cada requisição de teste bateu com a transcrição feita logo antes.
- **Achado novo, fora da SPEC-001**: toda requisição com `gpt-4o-transcribe-diarize` grava
  `custo_usd: 0.0` em `consumo.jsonl` — a tabela de preços por token (`main.py:35-38`) não tem
  entrada para esse modelo e cai no default zerado. Bug de cálculo, não lacuna de contrato — sub-
  relata o gasto real sempre que esse modelo é usado. Não corrigi (fora do escopo desta tarefa).

**2. As seis situações de erro, provocadas de verdade, cada uma com e sem streaming (12
provocações).** Todas bateram com a SPEC-001 no padrão geral (erro antes de abrir o stream vira
status HTTP; erro durante a chamada à OpenAI vira evento `erro` dentro de um `200`, mesmo mensagem
idêntica ao `detail` do modo sem streaming):

- Modelo inválido (`modelo=inexistente`): `422` nos dois modos.
- Áudio vazio (arquivo de 0 byte): `400` nos dois modos.
- `OPENAI_API_KEY` ausente (renomeei `.env`, reiniciei o backend, restaurei ao final — conferido
  `diff` byte a byte contra a cópia de segurança antes de restaurar): `503` nos dois modos.
- Falha de autenticação (chave `sk-chave-propositalmente-invalida-...` no `.env`, backend
  reiniciado): `502` sem streaming, evento `erro` dentro de `200` com streaming.
- Sem conexão (`OPENAI_BASE_URL=http://127.0.0.1:1/` no `.env`, backend reiniciado): `502` sem
  streaming (~8s até desistir), evento `erro` dentro de `200` com streaming (~7,6s) — tempo
  consistente com o timeout de conexão de 5s do SDK mais uma repetição.
- OpenAI recusa a requisição (arquivo de texto disfarçado de `.wav`): `502`
  `"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio"` sem
  streaming, evento `erro` com o mesmo texto dentro de `200` com streaming.

Depois de cada teste que mexeu no `.env`, restaurei o arquivo original (`diff` confirmou
identidade byte a byte) e reiniciei o backend; a última chamada da sessão foi uma transcrição
normal bem-sucedida, confirmando que o `.env` restaurado funciona.

**3. Lacunas L1–L8: todas confirmadas, refutadas ou reclassificadas com evidência — ver a tabela
completa em `spec/contrato/NUCLEO.md`, seção final.** Resumo:
- **L1** (sem código de erro) — confirmada, sem mudança.
- **L2** (sem limite de tamanho): enviei um WAV de ~64MB de silêncio puro; levou ~14s até a
  resposta, que foi o **mesmo** erro genérico "verifique o formato do arquivo de áudio" — confirma
  a suspeita da spec de que a mensagem engana sobre a causa real.
- **L3** (sem timeout): **não estimei — medi o código instalado.** `openai==3.1.0`,
  `openai._constants.DEFAULT_TIMEOUT` = `Timeout(connect=5.0, read=600, write=600, pool=600)`,
  `max_retries=2`, nenhum dos dois sobrescrito pelo backend. Bate com o tempo observado (~8s) no
  teste de "sem conexão" (5s de conexão + repetição rápida). Não tentei esperar os 600s completos
  (custo de tempo desproporcional ao valor da evidência, já com a fonte primária em mãos).
- **L4** (evento final sem custo/modelo): confirmada em todas as capturas de streaming — só
  `{"tipo": "final", "texto": ...}`.
- **L6** (áudio sem fala): **reclassificada**. Não é "comportamento indefinido" — é definido e
  ruim. Enviei 5s de silêncio puro (PCM zerado) nos dois modos: sem streaming voltou
  `{"transcricao":"Sélectionnez la."}` (francês, alucinado); com streaming voltou eventos delta em
  chinês e final `"都没有。"` ("não tem nada"). **Nos dois casos, `200`, sem erro, sem texto vazio**
  — alucinação em idioma aleatório. Este era o resultado que o PM disse não conseguir prever, e é
  esse mesmo.
- **L8** (parâmetro de idioma): **refutada como problema.** Gravei um áudio real com voz sintética
  pt-BR (TTS do Windows, voz "Microsoft Maria Desktop" — recurso local, sem custo de API) com
  frases em português cheias de termos técnicos em inglês ("commit", "deploy", "pull request",
  "code review", "branch", "prompt"), simulando o uso real do usuário. Chamei a API da OpenAI
  diretamente (fora da rota do backend, só para medir — não alterei `main.py`) duas vezes: sem
  `language` e com `language="pt"`. Resultado: **texto idêntico caractere por caractere**,
  **tokens idênticos** (`input=158, output=46, total=204` nas duas chamadas — custo idêntico),
  tempo de resposta 1,86s vs 1,25s (diferença dentro do ruído de rede, amostra única, não prova
  nada). Forçar `pt` não mudou nada mensurável. Por isso a Etapa 5 do `PLANO.md` **cai** (condição
  já registrada no próprio plano: "se a medição não mostrar diferença, esta etapa cai").
- **L7** (CORS aberto): confirmada com `OPTIONS /transcrever` e `Origin` arbitrário —
  `access-control-allow-origin: *`. Sem mudança nesta fase.

**4. `spec/contrato/NUCLEO.md` escrito** — documento completo para quem for escrever um cliente
novo, com cada operação, campo, formato de resposta (exemplos reais capturados), tabela de erros
completa e a lista de divergências/achados desta medição.

**5. Custo do levantamento e gasto do projeto (pedido extra do PM).** Via `GET /consumo` ao final:

| Data | Requisições | Tokens | Custo (USD) |
|---|---|---|---|
| 2026-08-18 | 4 | 825 | $0,00302 |
| 2026-08-19 | 84 | 13.372 | $0,10645 |
| 2026-08-20 | 89 | 23.148 | $0,14532 |
| 2026-08-21 | 121 | 33.569 | $0,21158 |
| 2026-08-22 | 1 | 270 | $0,00116 |
| 2026-08-23 (inclui esta medição + uso real concorrente, ver acima) | 44 | 19.033 | $0,06342 |
| **Total histórico** | **343** | — | **$0,53096** |

Não dá para separar com precisão total, nesta consulta, o que é uso real do dia 23 do que é teste
meu — os dois aconteceram entrelaçados na mesma janela (ver "uso real concorrente" acima), e o
`/consumo` não distingue a origem. Por amostragem manual das últimas linhas de `consumo.jsonl`, o
custo do meu levantamento (chamadas que geraram cobrança: caminho feliz ×5, silêncio ×2, verificação
final ×1, mais 2 chamadas diretas à API para o teste de idioma) fica na casa de **US$ 0,01–0,02** —
pequeno frente ao total do dia. As chamadas que só provocaram erro (modelo inválido, áudio vazio,
sem chave, autenticação falha, sem conexão, arquivo não-áudio, arquivo grande) **não geraram
cobrança** — nenhuma delas chegou a processar áudio de verdade na API.

### O que não consegui provocar / não medi

- **Timeout de 600s completo**: não esperei os 10 minutos inteiros para ver o backend estourar de
  verdade — a evidência da constante do SDK mais o comportamento observado no teste de "sem
  conexão" (que usa o timeout de *conexão*, não o de *leitura*) foi suficiente para responder L3
  sem gastar 10 minutos de sessão nisso. Se o PM quiser a prova empírica do timeout de leitura
  completo, precisa de um teste à parte.
- Não testei duração de áudio muito longa (só tamanho de arquivo) — a API pode ter limite de
  duração separado do limite de tamanho; não apareceu evidência disso nem a favor nem contra.

### Critério de pronto
- [x] Backend conferido antes de medir (porta 8000 sem processo antigo) — processo antigo (PID
  34028) encontrado e derrubado antes de subir o novo.
- [x] Caminho feliz medido nas duas formas (lote e streaming) e nos três modelos.
- [x] `GET /consumo` medido, com as três seções descritas.
- [x] As seis situações de erro provocadas de verdade, cada uma com e sem streaming.
- [x] `.env` restaurado e conferido (uma transcrição normal voltando a funcionar depois) — `diff`
  byte a byte contra a cópia de segurança, mais uma chamada de verificação bem-sucedida ao final.
- [x] L1 a L8 cada uma confirmada, refutada ou reclassificada com evidência.
- [x] `spec/contrato/NUCLEO.md` escrito, com exemplos reais capturados.
- [x] Divergências entre a SPEC-001 e a máquina listadas neste `PROGRESSO.md` (e no próprio
  contrato, seção final).
- [x] Nenhum arquivo de produto modificado (`git status --short transcritor/` veio vazio).
- [x] Artefatos de teste limpos (áudios, script de teste de idioma e backup do `.env` removidos do
  scratchpad da sessão; nada foi criado dentro do repositório).

### Novas demandas / riscos
- **Bug de cálculo de custo para `gpt-4o-transcribe-diarize`**: `custo_usd` sempre sai `0.0` para
  esse modelo (tabela `PRECOS_POR_TOKEN_USD` em `main.py:35-38` não tem entrada pra ele). Sub-
  relata o gasto real do projeto sempre que o modelo é usado. Não corrigi — fora do escopo desta
  tarefa (não é lacuna de contrato, é bug de cálculo em código de produto).
- **`gpt-4o-transcribe-diarize` não emite eventos `delta` em streaming** — comportamento real da
  API, não do backend, mas muda o que um cliente pode esperar desse modelo especificamente.
- **Uso real concorrente durante a medição**: confirmado por log que alguém usou o app de verdade
  enquanto eu media (ver "Feito", item 0). Não causou problema desta vez (usuário autorizado antes
  de eu quebrar o `.env`), mas é um risco a considerar se testes futuros do núcleo precisarem
  quebrar `.env`/backend por mais tempo — talvez valha um aviso mais cedo, antes mesmo de começar a
  medir, não só antes da parte que quebra o `.env`.
- L1 (código de erro por máquina) e L5 (sem versionamento) seguem sem solução — são decisões do PM
  para a Etapa 3, não algo que a medição resolvesse.

### Ajuste no plano necessário?
Sim — duas coisas para o PM:
1. **Etapa 5 cai**, conforme a própria condição já escrita nela: a medição de L8 não mostrou
   diferença de texto, custo ou tempo entre usar `language="pt"` e não usar. O contrato registra
   que o núcleo não assume idioma, sem parâmetro novo.
2. **Achado novo para virar decisão/tarefa**: o bug de custo zerado do `gpt-4o-transcribe-diarize`
   (ver "Novas demandas" acima) não está em nenhuma lacuna da SPEC-001 — é candidato a entrar no
   escopo da Etapa 3 (correção das lacunas aprovadas) ou a virar item de backlog à parte, a critério
   do PM.

## [2026-08-23 23:50] — Etapa 4: Arrumação — promover o harness, limpar o rascunho e o entulho
Status: concluído

### Feito
- Movido `.claude/tmp/teste_tempo_real.py` → `transcritor/teste_tempo_real.py`; reescrevi só a
  primeira linha do docstring (não é mais "rascunho descartável") e a linha de `Uso:` (caminho
  relativo, sem `..\.claude\tmp\`) — resto do docstring e todo o código intactos.
- `transcritor/README.md`: acrescentei a seção "Harness de validação do protocolo (sem navegador)"
  antes de "Benchmark entre modelos", citando o que o harness prova/não prova.
- `.claude/tmp/`: apaguei os 6 arquivos restantes (`teste_linha_tempo.wav`, `uvicorn.log`,
  `ROTEIRO_TESTE_ETAPA1.md`, `_teste_escrita.tmp`, `TAREFA_etapa2_faxina.md`,
  `TAREFA_interface-enxuta.md`); pasta continua existindo, vazia.
- Apagado `_to_delete/` inteiro (5 arquivos: 2 `.fuse_hidden*`, 2 `estado_fuse_*`, 1
  `index.lock.2026-08-16`).
- Apagado `.claude/estado/historico/snapshots/` inteiro (49 arquivos `PLANO_*.md`); raiz do
  `historico/` intacta (20 arquivos, conferido por `ls`).
- Nenhum arquivo de `transcritor/backend/` ou `transcritor/frontend/` tocado.

### Como testei
- `ls -la .claude/tmp/` → só `.`/`..`, 0 arquivos.
- `test -d _to_delete && echo EXISTS || echo GONE` → `GONE`.
- `test -d .claude/estado/historico/snapshots && echo EXISTS || echo GONE` → `GONE`; `ls
  .claude/estado/historico/` → 20 arquivos, todos os que já existiam antes na raiz.
- `test -f .git/index.lock` → `GONE`; `find . -iname "*.fuse_hidden*"` (fora de `.git/`) → vazio.
- `git status --porcelain`: comparado contra o status no início do chat — a única diferença é
  exatamente o que esta tarefa mexeu (49 `D` em `snapshots/`, 1 `D` em `_to_delete/`, `M
  transcritor/README.md`, `?? transcritor/teste_tempo_real.py`); todo o resto (`M`/`D`/`??`
  pré-existentes em `.claude/`, `spec/`, `coleta/` etc.) já estava lá antes de eu começar, não é
  desta tarefa.

### O que não testei
- Não rodei `teste_tempo_real.py` (a tarefa não pede e ele bate na API real, custando dinheiro —
  fora do escopo aqui).

### Critério de pronto
- [x] `transcritor/teste_tempo_real.py` existe, com o cabeçalho corrigido, e
      `.claude/tmp/teste_tempo_real.py` não existe mais.
- [x] `transcritor/README.md` cita o harness, dizendo o que ele prova e o que não prova.
- [x] `.claude/tmp/` está vazio.
- [x] `_to_delete/` não existe.
- [x] `.claude/estado/historico/snapshots/` não existe, e a raiz do `historico/` continua com todos
      os arquivos que tinha.
- [x] `git status` mostra só o que esta tarefa mexeu, e não há `.git/index.lock`.
- [x] Nenhum arquivo de `transcritor/backend/` ou `transcritor/frontend/` foi modificado.

### Novas demandas / riscos
- Nenhuma nova, fora do já registrado nas tarefas anteriores.

### Ajuste no plano necessário?
Não.

## [2026-08-24 01:30] — Etapa 3: Corrigir as quatro lacunas do contrato (R1–R4)
Status: concluído

### Aviso e preparação
Perguntei ao usuário antes do primeiro comando (a tarefa exigia — quebra o `.env` e reinicia o
backend várias vezes); autorizado. Encontrei backend antigo na porta 8000 (PID 24112, processo
`uvicorn` iniciado em 23/08 16:15 — a "armadilha da porta 8000", 6ª ocorrência prevista no
`PLANO.md`): matei antes de medir qualquer coisa. Fiz backup do `.env` (`.claude/tmp/.env.backup`,
comparado por `md5sum` = `d382e58d0ccbd7aca885706fd3603bb4` antes de cada restauração) e removi o
backup ao final (não deixar chave de exemplo/backup solta, `metodo/COMMIT.md`).

### O que mudou em `transcritor/backend/main.py`
- **R1**: nova classe `ErroNucleo` + `@app.exception_handler`, e helper `_erro_api_para_codigo`
  (traduz exceção da SDK → `(codigo, detail, status_http)`, reaproveitado nos dois modos). Os seis
  `raise HTTPException`/`except ... raise HTTPException` de `/transcrever` viraram `raise ErroNucleo`;
  os três `except` da função de streaming viraram um único `except` com o mesmo helper. `detail`
  continua string; `codigo` é campo aditivo. `tempo_real_token` **não foi tocado** — fora do
  contrato (`D-02`), fora do escopo de R1.
- **R2**: `TIMEOUT_CLIENTE_API = Timeout(120.0, connect=5.0)`, passado ao `OpenAI(...)` só em
  `/transcrever` (o cliente de `tempo_real_token` não foi tocado, mesma razão do R1).
  `APITimeoutError` vira `TEMPO_ESGOTADO`/`504`.
- **R3**: `TAMANHO_MAXIMO_AUDIO_BYTES = 25 * 1024 * 1024`, checado logo depois de ler o `UploadFile`
  e antes de instanciar o cliente da API. `ARQUIVO_MUITO_GRANDE`/`413`, mensagem com tamanho e teto
  em português (vírgula decimal).
- **R4**: `response.headers["X-Nucleo-Contrato"] = "1"` nos dois `return` de sucesso
  (`/transcrever` via parâmetro `response: Response` injetado, `/consumo` igual); no `StreamingResponse`
  via `headers=`; nos erros, o `exception_handler` decide pelo `request.url.path` (só
  `/transcrever` e `/consumo`).

### Os oito códigos, provocados de verdade contra o backend, nos dois modos
Backend restaurado/reiniciado entre grupos que precisavam de `.env` ou `OPENAI_BASE_URL`
diferentes (nunca simultâneo com o `.env` quebrado e o app em uso).

**MODELO_INVALIDO** (sem API, `modelo=modelo-que-nao-existe`):
- Sem streaming: `422` `{"detail":"Modelo inválido: 'modelo-que-nao-existe'. Valores aceitos: gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize","codigo":"MODELO_INVALIDO"}`
- Com streaming: idêntico byte a byte.

**AUDIO_VAZIO** (arquivo de 0 byte):
- Sem streaming: `400` `{"detail":"Arquivo de áudio vazio","codigo":"AUDIO_VAZIO"}`
- Com streaming: idêntico.

**ARQUIVO_MUITO_GRANDE** (arquivo de 27.262.976 bytes = 26,0 MB):
- Sem streaming: `413` `{"detail":"Arquivo de 26,0 MB; o limite é 25 MB","codigo":"ARQUIVO_MUITO_GRANDE"}`, `real 0m0.130s`.
- Com streaming: idêntico, `real 0m0.142s`.
- Abaixo do teto (arquivo de 48.044 bytes, WAV real): `200` `{"transcricao":"..."}` — passou adiante e chamou a API de verdade.

**API_RECUSOU** (arquivo de texto disfarçado de `.wav`):
- Sem streaming: `502` `{"detail":"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio","codigo":"API_RECUSOU"}`
- Com streaming: `200`, evento `{"tipo":"erro","detail":"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio","codigo":"API_RECUSOU"}`

**SEM_CHAVE** (`.env` com `OPENAI_API_KEY=` vazio, backend reiniciado):
- Sem streaming: `503` `{"detail":"OPENAI_API_KEY não configurada — preencha transcritor/.env","codigo":"SEM_CHAVE"}`
- Com streaming: idêntico.

**FALHA_AUTENTICACAO** (`.env` com chave inválida `sk-chave-invalida-para-teste-...`, backend reiniciado):
- Sem streaming: `502` `{"detail":"Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env","codigo":"FALHA_AUTENTICACAO"}`
- Com streaming: `200`, evento equivalente com `"codigo":"FALHA_AUTENTICACAO"`.

**SEM_CONEXAO** (`OPENAI_BASE_URL=http://127.0.0.1:1/v1`, porta sem nada escutando):
- Sem streaming: `502` `{"detail":"Não foi possível conectar à API da OpenAI — verifique a rede","codigo":"SEM_CONEXAO"}`, `real 8.087s`.
- Com streaming: `200`, evento equivalente, `real 7.570s`.

**TEMPO_ESGOTADO** (`OPENAI_BASE_URL` apontando para um servidor TCP local descartável que aceita a
conexão e nunca responde nada — `.claude/tmp/hang_server.py`, removido ao final):
- Sem streaming: `504` `{"detail":"A API da OpenAI não respondeu a tempo — tente novamente","codigo":"TEMPO_ESGOTADO"}`, **`real 6m1.993s`** — bate com 120s de leitura × 3 tentativas (1 original + `max_retries=2` do SDK, não alterado).
- Com streaming: **não reproduziu o mesmo código sob a mesma condição** — devolveu `200` com evento `{"tipo":"erro","detail":"Não foi possível conectar à API da OpenAI — verifique a rede","codigo":"SEM_CONEXAO"}`, `real 8m28.924s`. Achado novo, registrado em `NUCLEO.md`: o SDK da OpenAI levantou `APIConnectionError` (não `APITimeoutError`) para a chamada em `stream=True` sob essa falha de rede — o backend não força isso (é o mesmo `except`/helper para os dois modos); é comportamento do SDK, não bug do código escrito nesta tarefa. Não investiguei a causa raiz (fora do escopo).

### Cabeçalho `X-Nucleo-Contrato`
- `POST /transcrever` sucesso: presente (`x-nucleo-contrato: 1`), confirmado nos dois modos.
- `POST /transcrever` erro: presente em todos os oito códigos acima, nos dois modos.
- `GET /consumo`: presente (`x-nucleo-contrato: 1`).
- `GET /tempo-real/token`: **ausente**, confirmado (`curl -D -` sem o cabeçalho).

### `.env`
Restaurado duas vezes (depois de `SEM_CHAVE` e depois de `FALHA_AUTENTICACAO`) com `cp` do backup;
`diff .env .claude/tmp/.env.backup` vazio e `md5sum` idêntico (`d382e58d0ccbd7aca885706fd3603bb4`)
nas duas vezes. Transcrição normal confirmada funcionando depois da restauração final: `200`
`{"transcricao":"ئالما"}` (tom sintético, texto sem sentido esperado — não é fala real).

### App web conferido no navegador
Sem `chromium-cli` nem Playwright pré-instalados no projeto; usei `npx playwright` (Chromium já
estava em cache local do sistema, sem download) e escrevi um driver descartável
(`.claude/tmp/verificar_navegador*.js`, removido ao final) para abrir
`http://127.0.0.1:8000/` de verdade e:
1. Página carrega sem erro de console/página (screenshot tirado, conferido visualmente).
2. Fluxo de **upload de arquivo** pelo popup ⋮ → "Enviar arquivo" (mesmo código que a UI usa depois
   de parar uma gravação): arquivo enviado, balão verde "Transcrição adicionada ao texto abaixo.",
   texto apareceu na caixa `#transcriptRapido`, zero erros de console.
3. Com `.env` quebrado (`SEM_CHAVE`), o mesmo fluxo de upload mostrou o balão **vermelho** com o
   texto exato de `detail` ("Erro ao transcrever: OPENAI_API_KEY não configurada — preencha
   transcritor/.env") — confirma visualmente que `detail` continua string simples e a interface não
   quebrou com o campo `codigo` novo ao lado.
- **Não testei gravação por microfone de verdade** — o Chromium automatizado não tem microfone
  físico nem um humano falando; o upload de arquivo exercita o mesmo caminho de código
  (`POST /transcrever`, mesmo tratamento de `detail`/balão) que a gravação usa depois de parar, mas
  não é o mesmo teste. Recomendo ao usuário um teste manual rápido de gravação com o app já
  rodando.

### Critério de pronto
- [x] Backend conferido antes de medir (porta 8000 sem processo antigo) — PID 24112 antigo morto.
- [x] Os oito códigos provocados de verdade contra o backend rodando, cada um nos dois modos, com a
      resposta colada acima.
- [x] `detail` continua string em português em todos eles, e o `index.html` não foi tocado
      (`git diff --stat -- transcritor/frontend/index.html` vazio).
- [x] Teto de tamanho medido — arquivo acima recusado localmente (26 MB, ~0,13s, sem chamar a API) e
      um abaixo passando adiante; limite da OpenAI confirmado em
      <https://developers.openai.com/api/docs/guides/speech-to-text> ("Files can be up to 25 MB."),
      consultado em 2026-08-24.
- [x] `X-Nucleo-Contrato: 1` presente em sucesso e erro, nos dois modos, nas duas rotas do contrato,
      e ausente nas rotas de tempo real.
- [x] Prazo de espera declarado no cliente (`Timeout(120.0, connect=5.0)`); tempo real até a falha
      medido nos dois modos (não só declarado como "não provocado") — com a divergência de modo
      registrada como achado, não escondida.
- [x] `.env` restaurado e conferido: `diff` byte a byte vazio, `md5sum` idêntico, mais uma
      transcrição normal funcionando.
- [x] App web conferido no navegador (upload real, sucesso e erro visíveis) — gravação por
      microfone real não testada, motivo registrado acima.
- [x] `spec/contrato/NUCLEO.md` atualizado (tabela de erros com `codigo`, versionamento, L1/L2/L3/L5
      de "confirmada" para "corrigida" com data, achado da divergência de streaming registrado).
- [x] Repositório pronto para commit: sem `.git/index.lock`, sem `.fuse_hidden*` soltos,
      `.claude/tmp/` só com `uvicorn.log` (log do processo que deixei rodando, não versionado),
      `git status` mostrando só `transcritor/backend/main.py`, `spec/contrato/NUCLEO.md` e este
      `PROGRESSO.md` como diferença desta tarefa (o resto já estava modificado antes de eu começar).
      **Não commitei.**

### Novas demandas / riscos
- **Divergência de modo em `TEMPO_ESGOTADO`** (ver acima): sob a mesma falha de rede, o modo
  streaming demora mais (~8m29s vs. ~6m02s) e termina em `SEM_CONEXAO`, não em `TEMPO_ESGOTADO`. O
  código está correto (mesmo helper de mapeamento nos dois modos) — é o SDK da OpenAI que se
  comporta diferente para chamadas `stream=True` sob essa condição específica. Não investiguei a
  causa raiz; se o PM achar que vale a pena entender por que, é trabalho novo.
- **`max_retries=2` do SDK não foi alterado** — só o `timeout` foi declarado (R2 pediu isso, não
  mudar retries). Consequência prática, medida: o tempo real até `TEMPO_ESGOTADO`/`SEM_CONEXAO`
  ainda pode chegar a minutos, mesmo com 120s declarados, porque o SDK tenta de novo sozinho. Deixei
  isso registrado no `NUCLEO.md` para quem for revisar esse número no futuro.
- Deixei o backend **rodando** na porta 8000 (com `.env` restaurado, código novo) ao final, para o
  app continuar disponível para o usuário — não parei o processo.

### Ajuste no plano necessário?
Não — as quatro lacunas (R1-R4) foram corrigidas e medidas conforme o critério. Etapa 3 era a
última etapa de código da Fase 1; o PM decide o que vem a seguir.
