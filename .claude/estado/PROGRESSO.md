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
