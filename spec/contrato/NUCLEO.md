---
artefato: Contrato do núcleo de transcrição
origem: SPEC-001_contrato-do-nucleo.md
medido_em: 2026-08-23
atualizado_em: 2026-08-24 (Etapa 3 — R1 a R4, ver PROGRESSO.md)
status: observado (não é aspiração — é o que a máquina faz hoje)
---

# Contrato do núcleo de transcrição

Este documento descreve tudo que um cliente novo (app desktop, Android, Wear, ou qualquer outro)
precisa saber para consumir o núcleo de transcrição — **sem abrir `index.html` nem `main.py`**.
Todo comportamento aqui foi **medido contra o backend rodando** em 2026-08-23 (não é leitura de
código): cada exemplo de resposta é uma captura real, e cada linha da tabela de erros foi
provocada de verdade. Onde a medição divergiu da SPEC-001 original (que tinha sido levantada só
por leitura de código), o que está escrito aqui é **o observado** — a divergência em si está
listada no `PROGRESSO.md` da tarefa, para o PM decidir o que fazer com ela.

## Fora do contrato: o modo ao vivo

`GET /tempo-real/token` e `POST /tempo-real/turno-concluido` existem no backend e continuam
servindo a interface web atual, mas **não fazem parte deste contrato** — estão congelados por
decisão de 2026-08-21. **Nenhum cliente novo deve consumi-los.** `GET /favicon.ico` é detalhe da
interface web, também fora do contrato.

## Versionamento

**Corrigida em 2026-08-24 (R4).** Toda resposta de `POST /transcrever` e `GET /consumo` — sucesso
**e** erro, nos dois modos — carrega o cabeçalho `X-Nucleo-Contrato: 1`. Confirmado por medição
real: presente nas duas rotas em todos os casos testados, **ausente** em `GET /tempo-real/token`
(fora do contrato, ver acima). Se o formato mudar no futuro, o número muda junto — um cliente pode
checar o cabeçalho antes de assumir o formato.

---

## Operação 1 — Transcrever áudio

`POST /transcrever`, `multipart/form-data`.

| Campo | Tipo | Obrigatório | Padrão | Observação |
|---|---|---|---|---|
| `audio` | arquivo | sim | — | qualquer formato que a API da OpenAI aceite (`.wav`, `.m4a`, `.mp3`, ...) |
| `modelo` | texto | não | `gpt-4o-transcribe` | ver lista abaixo |
| `stream` | booleano (`"true"`/`"false"` como string do form) | não | `false` | |

Não existe parâmetro de idioma nesta rota (ver "Idioma" mais abaixo — a ausência é intencional,
confirmada por medição, não uma lacuna a preencher).

### Modelos aceitos

| Modelo | Observação |
|---|---|
| `gpt-4o-transcribe` | padrão |
| `gpt-4o-mini-transcribe` | mais barato, mesma forma de resposta |
| `gpt-4o-transcribe-diarize` | o backend acrescenta `chunking_strategy=auto` automaticamente antes de chamar a API — **o cliente não precisa (nem pode) mandar esse parâmetro**; ver divergências abaixo, esse é o modelo com mais comportamento diferente |

Qualquer outro valor é rejeitado com `422` antes de qualquer chamada à API (não gera custo).

### Resposta sem streaming

`200`, `Content-Type: application/json`:

```json
{"transcricao": "Este é um teste de transcrical para a linha do tempo do painel de consumo. Estou comparando o custo entre dois modelos diferentes usando o mesmo áudio."}
```

Único campo: `transcricao` (string). Capturado de verdade contra os três modelos — o formato é
idêntico nos três.

### Resposta com streaming (`stream=true`)

`200`, `Content-Type: application/x-ndjson` — um objeto JSON por linha. Formato confirmado contra
`gpt-4o-transcribe` e `gpt-4o-mini-transcribe` (captura real, 33 eventos para um áudio de ~12,7s):

```
{"tipo": "delta", "texto": "Este"}
{"tipo": "delta", "texto": " é"}
{"tipo": "delta", "texto": " um"}
{"tipo": "delta", "texto": " teste"}
...
{"tipo": "delta", "texto": "."}
{"tipo": "final", "texto": "Este é um teste de transcrical para a linha do tempo do painel de consumo. Estou comparando o custo entre dois modelos diferentes usando o mesmo áudio."}
```

- `tipo: "delta"` — um pedaço de texto novo, campo `texto`. Pode chegar em vários eventos seguidos.
- `tipo: "final"` — texto completo da transcrição, campo `texto`. **Só traz o texto** — nenhum
  campo de custo, modelo ou id (ver L4 abaixo; confirmado por medição, não é lacuna de captura).
- `tipo: "erro"` — ver seção de erros.

**Divergência confirmada por medição — `gpt-4o-transcribe-diarize` com streaming não emite nenhum
evento `delta`.** A API só devolve um único evento final:

```
{"tipo": "final", "texto": "Eis aí um teste de transcrical para a linha do tempo do painel de consumo. Estou comparando o custo entre dois modelos diferentes usando o mesmo audio."}
```

Um cliente que espera atualização incremental de texto com esse modelo **não vai ver nada até o
fim** — na prática, para esse modelo, streaming se comporta como não-streaming, só que com o
cabeçalho e o formato de envelope do modo streaming. Isso não está na SPEC-001 original (que
supôs o mesmo formato delta+final para os três modelos) — é achado novo desta medição.

### Idioma

A chamada à API **não envia parâmetro de idioma** hoje, e este contrato **não expõe um parâmetro
`idioma`** em `POST /transcrever`. Isso foi testado, não só herdado da leitura de código: um áudio
real em português com termos técnicos em inglês no meio ("commit", "deploy", "pull request",
"code review", "branch", "prompt") foi transcrito duas vezes chamando a API diretamente — uma vez
sem especificar idioma, outra com `language="pt"` forçado. Resultado:

- **Texto**: idêntico nas duas chamadas, caractere por caractere.
- **Tokens/custo**: idênticos (`input_tokens=158, output_tokens=46, total_tokens=204` nas duas).
- **Tempo de resposta**: 1,86s sem idioma vs. 1,25s com `pt` — dentro do ruído normal de latência
  de rede, não é diferença sistemática (uma única amostra de cada lado não prova nada sobre
  velocidade).

**Conclusão: forçar `pt` não mudou nada mensurável.** A hipótese que motivava a Etapa 5 do
`PLANO.md` (parâmetro `idioma` opcional no contrato) não se sustentou nesta medição — a etapa cai,
conforme a condição já registrada no plano. O núcleo simplesmente **não assume idioma nenhum**; a
API detecta sozinha, e não há evidência de que fixar `pt` ajude ou atrapalhe.

---

## Erros de `POST /transcrever`

**Corrigida em 2026-08-24 (R1).** Todo erro carrega um campo `codigo` estável, ao lado de `detail`
(que continua sendo string em português, no mesmo lugar de sempre). As oito situações abaixo foram
provocadas de verdade contra o backend, cada uma nos dois modos — as seis originais mais as duas
novas que R2 e R3 introduziram (`TEMPO_ESGOTADO`, `ARQUIVO_MUITO_GRANDE`).

| Situação | `codigo` | Sem streaming | Com streaming |
|---|---|---|---|
| Modelo fora da lista aceita | `MODELO_INVALIDO` | `422` `{"detail":"Modelo inválido: '<valor>'. Valores aceitos: gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize","codigo":"MODELO_INVALIDO"}` | idêntico — validado antes de abrir o stream |
| `OPENAI_API_KEY` não configurada no backend | `SEM_CHAVE` | `503` `{"detail":"OPENAI_API_KEY não configurada — preencha transcritor/.env","codigo":"SEM_CHAVE"}` | idêntico — validado antes de abrir o stream |
| Arquivo de áudio vazio (0 byte) | `AUDIO_VAZIO` | `400` `{"detail":"Arquivo de áudio vazio","codigo":"AUDIO_VAZIO"}` | idêntico |
| Arquivo acima do teto de tamanho (ver R3 abaixo) | `ARQUIVO_MUITO_GRANDE` | `413` `{"detail":"Arquivo de 26,0 MB; o limite é 25 MB","codigo":"ARQUIVO_MUITO_GRANDE"}` (medido com um arquivo de 26 MB) | idêntico — recusado antes de abrir o stream, em ~0,13s nos dois modos |
| Falha de autenticação na API da OpenAI (chave inválida) | `FALHA_AUTENTICACAO` | `502` `{"detail":"Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env","codigo":"FALHA_AUTENTICACAO"}` | evento `{"tipo":"erro","detail":"Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env","codigo":"FALHA_AUTENTICACAO"}`, dentro de um `200` |
| Sem conexão com a OpenAI (rede/host inalcançável) | `SEM_CONEXAO` | `502` `{"detail":"Não foi possível conectar à API da OpenAI — verifique a rede","codigo":"SEM_CONEXAO"}` (medido: ~8,1s) | evento equivalente, dentro de um `200` (medido: ~7,6s) |
| A OpenAI recusa a requisição (ex.: arquivo que não é áudio de verdade) | `API_RECUSOU` | `502` `{"detail":"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio","codigo":"API_RECUSOU"}` | evento equivalente, dentro de um `200` |
| A API não responde dentro do prazo declarado (ver R2 abaixo) | `TEMPO_ESGOTADO` | `504` `{"detail":"A API da OpenAI não respondeu a tempo — tente novamente","codigo":"TEMPO_ESGOTADO"}` (medido: **6min01,99s**, host que aceita a conexão e nunca responde) | **divergência medida** — ver nota abaixo da tabela |

**O padrão geral, confirmado nos oito casos**: erros que acontecem **antes** de abrir o stream
(modelo inválido, sem chave, áudio vazio, arquivo grande) sempre viram status HTTP de erro, em
ambos os modos. Erros que só acontecem **durante** a chamada à API da OpenAI (autenticação, rede,
recusa, tempo esgotado) sempre viram `200` com evento `erro` no modo streaming — o corpo é um JSON
de erro (não um objeto `{"tipo": ...}`) no modo sem streaming, mas o status HTTP reflete a falha
real (`502` ou `504`, nunca `200`). Um cliente precisa checar o status HTTP **e**, no modo
streaming, também checar `tipo` de cada linha — nunca assumir que `200` = sucesso no streaming.

**Achado novo da medição — o modo streaming não reproduziu `TEMPO_ESGOTADO` na mesma condição.**
Apontando o cliente para um host que aceita a conexão TCP e nunca responde nada (mesmo cenário dos
dois testes), o modo sem streaming devolveu `TEMPO_ESGOTADO`/`504` em 6min01,99s, consistente com
120s de leitura × 3 tentativas (1 original + 2 retries automáticos do SDK). O modo streaming, sob a
**mesma condição**, devolveu `SEM_CONEXAO`/evento `erro` em **8min28,92s** — mais tempo, e um código
diferente. O backend não força esse resultado (o mapeamento de exceção → código é o mesmo código
para os dois modos, em `_erro_api_para_codigo`); é o SDK da OpenAI que levantou uma exceção
diferente (`APIConnectionError`, não `APITimeoutError`) para a chamada em modo `stream=True` sob
essa mesma falha de rede. Não investigado a fundo (fora do escopo desta tarefa); registrado aqui
como comportamento observado, não como bug do backend — o código `TEMPO_ESGOTADO` existe e está
coberto no modo streaming pelo mesmo `except`, só não foi essa exceção específica que o SDK
levantou neste teste.

### L2 — Arquivo grande, sem limite declarado (corrigida em 2026-08-24, R3)

O backend agora recusa arquivo acima de **25 MB** (`TAMANHO_MAXIMO_AUDIO_BYTES` em `main.py`) antes
de mandar para a API — ver tabela acima (`ARQUIVO_MUITO_GRANDE`, `413`). O limite foi confirmado na
documentação oficial: *"Files can be up to 25 MB."* —
<https://developers.openai.com/api/docs/guides/speech-to-text>, consultada em 2026-08-24. Medido: um
arquivo de 26 MB é recusado em **~0,13s** (contra os ~14s de antes, subindo o arquivo inteiro para
só então ser recusado pela API com uma mensagem que apontava para a causa errada). Um arquivo abaixo
do teto passa adiante normalmente (medido com o mesmo arquivo de teste usado nos outros casos,
`200`, transcrição real devolvida).

### L3 — Timeout (corrigida em 2026-08-24, R2)

O cliente `OpenAI(...)` usado em `POST /transcrever` agora declara `timeout=Timeout(120.0,
connect=5.0)` — 120s de leitura, 5s de conexão — em vez de herdar o default do SDK
(`Timeout(connect=5.0, read=600, write=600, pool=600)`, com `max_retries=2` também herdado, não
alterado por esta correção). Ao estourar, o erro vira `TEMPO_ESGOTADO`/`504` (ver tabela acima).

**Medido de verdade, não estimado**: apontando o cliente (via `OPENAI_BASE_URL`) para um servidor
TCP local que aceita a conexão e nunca responde nada, o modo sem streaming levou **6min01,99s** até
falhar — consistente com 120s de leitura vezes 3 tentativas (a original mais as 2 automáticas do
SDK, `max_retries=2` não alterado). O modo streaming, sob a mesma condição, levou **8min28,92s** e
terminou em `SEM_CONEXAO`, não em `TEMPO_ESGOTADO` — ver o achado logo acima da tabela de erros.
**Uma consequência prática desta medição**: mesmo com o timeout declarado, o tempo real até a falha
ainda é multiplicado pelas tentativas automáticas do SDK — 120s declarados não significam "falha em
até 120s" quando a causa é uma conexão que trava (o `max_retries=2` do SDK não foi alterado por não
estar no escopo de R2). Registrado aqui para quem for revisar esse número no futuro.

### L4 — Evento final do streaming não traz custo nem modelo (confirmada)

Confirmado em todas as capturas de streaming: o evento `final` só tem `{"tipo": "final", "texto":
"..."}`. Nenhum campo de custo, tokens ou modelo. Um cliente que queira mostrar consumo em tempo
real precisa de uma chamada separada a `GET /consumo` depois.

### L6 — Áudio sem fala (confirmada — resultado imprevisível, não é erro nem vazio)

Enviado um WAV de 5s de silêncio puro (PCM zerado). **Nos dois modos, a resposta foi `200` com
texto alucinado, não vazio e não relacionado ao conteúdo (que não tinha nenhum):

- Sem streaming: `{"transcricao":"Sélectionnez la."}` (francês, sem sentido nenhum com o áudio)
- Com streaming: eventos delta em chinês (`"都"`, `"没有"`, `"。"`), final `{"tipo":"final","texto":"都没有。"}` ("não tem nada", em chinês)

**Nenhuma das duas execuções produziu erro nem texto vazio.** Um cliente que trata "sem resposta de
erro" como "transcrição válida" vai mostrar lixo alucinado ao usuário, em idioma aleatório, sem
aviso. Isso é o comportamento real da API da OpenAI para silêncio com este modelo — o backend não
filtra nem detecta isso hoje. Qualquer proteção (ex.: descartar áudio abaixo de um limiar de
volume, como já faz o frontend atual) precisa acontecer **antes** de mandar o áudio, porque a API
não vai avisar.

### L7 — CORS aberto (confirmada, sem mudança)

`OPTIONS /transcrever` com `Origin` arbitrário devolve `access-control-allow-origin: *`. Confirmado
que qualquer origem é aceita — aceitável enquanto o núcleo só roda localmente, vira restrição
quando (e se) ele for servido fora da máquina do usuário. Sem mudança nesta fase.

---

## Operação 2 — Consultar consumo

`GET /consumo` → `200`, sem parâmetros. Resposta real capturada (truncada para exemplo):

```json
{
  "sessao": {"requisicoes": 1, "tokens": 161, "custo_usd": 0.0006575},
  "por_dia": [
    {"data": "2026-08-18", "requisicoes": 4, "tokens": 825, "custo_usd": 0.00302},
    {"data": "2026-08-23", "requisicoes": 44, "tokens": 19033, "custo_usd": 0.06342}
  ],
  "requisicoes": [
    {"id": "6ee3246f...", "timestamp": "2026-08-23T19:06:45.440686+00:00", "modelo": "gpt-4o-transcribe", "custo_usd": 0.0006575, "texto": "Este é um teste de transcrical..."}
  ]
}
```

- `sessao` — acumulado em memória **desde que o processo do backend subiu**. Reinicia a zero a
  cada `uvicorn` novo (confirmado: reiniciei o backend várias vezes durante esta medição e o
  contador voltou a zero cada vez).
- `por_dia` — agregado por data (`AAAA-MM-DD`), lido do histórico completo em `consumo.jsonl`.
  Confirmado que arquivo ausente (ou histórico vazio) devolve lista vazia, não erro.
- `requisicoes` — uma linha por requisição já registrada, com `texto` vindo de
  `transcricoes.jsonl` casado pelo `id`. Confirmado batendo: o `texto` de cada requisição de teste
  feita nesta medição apareceu correto e completo na consulta seguinte a `/consumo`.

### Divergência confirmada por medição — custo de `gpt-4o-transcribe-diarize` sempre zero

Achado novo, fora da SPEC-001 original: toda requisição usando `gpt-4o-transcribe-diarize` grava
`custo_usd: 0.0` em `consumo.jsonl`, mesmo consumindo tokens de verdade (`total_tokens` não-zero).
Causa: a tabela de preços por token no backend (`main.py:35-38`, `PRECOS_POR_TOKEN_USD`) só tem
entradas para `gpt-4o-transcribe` e `gpt-4o-mini-transcribe` — para qualquer outro modelo (incluindo
o diarize), o cálculo cai no default `{"entrada": 0.0, "saida": 0.0}` e o custo sai zerado sempre.
**Isso significa que todo uso de `gpt-4o-transcribe-diarize` fica invisível no `/consumo` e no
histórico de gasto** — sub-relatando o custo real do projeto sempre que esse modelo é usado. Não é
uma lacuna do contrato (a *forma* da resposta está certa), é um bug de cálculo — reportado aqui
como achado, não corrigido (fora do escopo desta tarefa).

---

## Resumo das lacunas L1–L8 da SPEC-001

| Lacuna | Status após medição |
|---|---|
| L1 — sem código de erro legível por máquina | **Corrigida em 2026-08-24** — todo erro traz `codigo` estável ao lado de `detail`, oito situações provocadas de verdade nos dois modos |
| L2 — sem limite de tamanho declarado | **Corrigida em 2026-08-24** — teto de 25 MB (documentado pela OpenAI), recusa em ~0,13s com `ARQUIVO_MUITO_GRANDE`/`413` |
| L3 — sem timeout declarado | **Corrigida em 2026-08-24** — cliente declara 120s de leitura / 5s de conexão, `TEMPO_ESGOTADO`/`504` ao estourar; tempo real até a falha medido (6min01,99s sem streaming — ver divergência no modo streaming na seção de erros) |
| L4 — evento final do streaming sem custo/modelo | **Confirmada** — só tem `texto` |
| L5 — contrato sem versão | **Corrigida em 2026-08-24** — `X-Nucleo-Contrato: 1` em sucesso e erro, nas duas rotas do contrato, ausente no modo ao vivo |
| L6 — áudio sem fala sem comportamento definido | **Confirmada, e reclassificada**: não é "indefinido" — é definido e ruim (`200` com alucinação em idioma aleatório, nos dois modos) |
| L7 — CORS aberto | **Confirmada, aceitável por ora** — sem mudança nesta fase |
| L8 — sem parâmetro de idioma | **Refutada como problema** — medição mostrou que forçar `pt` não muda texto, custo nem tempo de forma mensurável; o contrato não ganha o parâmetro `idioma` (Etapa 5 do `PLANO.md` cai) |

Achados novos, fora das lacunas originais da SPEC-001:
- `gpt-4o-transcribe-diarize` com streaming não emite eventos `delta`, só o `final`.
- `gpt-4o-transcribe-diarize` sempre grava `custo_usd: 0.0` em `consumo.jsonl` (bug de tabela de preços).
- Sob a mesma condição de rede que produz `TEMPO_ESGOTADO` no modo sem streaming, o modo streaming
  produziu `SEM_CONEXAO` (mais tempo até falhar, código diferente) — ver seção "Erros de `POST
  /transcrever`" acima.
