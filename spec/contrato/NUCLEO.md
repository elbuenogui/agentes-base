---
artefato: Contrato do núcleo de transcrição
origem: SPEC-001_contrato-do-nucleo.md
medido_em: 2026-08-23
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

O contrato **não tem número de versão** hoje (nem no formato das respostas, nem em nenhum
cabeçalho HTTP). Se o formato mudar no futuro, um cliente antigo quebra sem aviso — isso é uma
lacuna real (L5 da SPEC-001), não uma escolha de desenho. Registrado aqui, sem solução ainda.

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

Todas as seis situações abaixo foram provocadas de verdade contra o backend, cada uma nos dois
modos. Nenhum erro traz um código legível por máquina — só `detail` em texto (L1, confirmada:
ainda é assim; um cliente novo vai precisar comparar strings ou status HTTP até isso mudar).

| Situação | Sem streaming | Com streaming |
|---|---|---|
| Modelo fora da lista aceita | `422` `{"detail":"Modelo inválido: '<valor>'. Valores aceitos: gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize"}` | idêntico — validado antes de abrir o stream |
| `OPENAI_API_KEY` não configurada no backend | `503` `{"detail":"OPENAI_API_KEY não configurada — preencha transcritor/.env"}` | idêntico — validado antes de abrir o stream |
| Arquivo de áudio vazio (0 byte) | `400` `{"detail":"Arquivo de áudio vazio"}` | idêntico |
| Falha de autenticação na API da OpenAI (chave inválida) | `502` `{"detail":"Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env"}` | evento `{"tipo":"erro","detail":"Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env"}`, dentro de um `200` |
| Sem conexão com a OpenAI (rede/host inalcançável) | `502` `{"detail":"Não foi possível conectar à API da OpenAI — verifique a rede"}` | evento `{"tipo":"erro","detail":"Não foi possível conectar à API da OpenAI — verifique a rede"}`, dentro de um `200` |
| A OpenAI recusa a requisição (ex.: arquivo que não é áudio de verdade) | `502` `{"detail":"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio"}` | evento `{"tipo":"erro","detail":"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio"}`, dentro de um `200` |

**O padrão geral, confirmado nos seis casos**: erros que acontecem **antes** de abrir o stream
(modelo inválido, sem chave, áudio vazio) sempre viram status HTTP de erro, em ambos os modos. Erros
que só acontecem **durante** a chamada à API da OpenAI (autenticação, rede, recusa) sempre viram
`200` com evento `erro`, mesmo no modo sem streaming — o corpo é um JSON de erro (não um objeto
`{"tipo": ...}`), mas o status HTTP é sempre `502`. Um cliente precisa checar o status HTTP **e**,
no modo streaming, também checar `tipo` de cada linha — nunca assumir que `200` = sucesso no
streaming.

### L2 — Arquivo grande, sem limite declarado (confirmada)

Enviado um arquivo de ~64 MB (silêncio puro, WAV). Levou ~14s só para o upload chegar ao backend.
Resultado: **o mesmo erro genérico de "OpenAI recusou a requisição"** —
`502` `{"detail":"A API da OpenAI recusou a requisição (HTTP 400) — verifique o formato do arquivo de áudio"}`.
A suspeita da SPEC-001 se confirma: a mensagem fala de "formato do arquivo", mas a causa real é
tamanho. Um cliente que confiar no texto do erro vai investigar a coisa errada. **Não há limite
declarado no contrato hoje** — só o limite implícito da API da OpenAI, que devolve esse erro
disfarçado.

### L3 — Timeout (confirmada, sem estimativa)

Não há timeout configurado no código do backend — o cliente `OpenAI(api_key=chave)` é criado sem
parâmetro `timeout`. Isso não foi estimado: é o valor default lido diretamente do SDK instalado
(`openai==3.1.0`, `openai._constants.DEFAULT_TIMEOUT`):

```
Timeout(connect=5.0, read=600, write=600, pool=600)
```

Ou seja: até **5 segundos** para conectar, e até **600 segundos (10 minutos)** de espera depois de
conectado, antes de desistir — mais até 2 tentativas automáticas (`max_retries=2` do SDK, também
não sobrescrito pelo backend) em caso de erro de conexão. O teste de "sem conexão" (host
inalcançável) bate com isso na prática: a chamada devolveu erro em **~8 segundos**, consistente com
uma tentativa de conexão de 5s mais uma repetição rápida antes de desistir — não os 5s crus.
**Um app de ditado que espera resposta em segundos pode ficar preso até 10 minutos** num backend
que não declara timeout próprio. Isso é lacuna real, não capacidade.

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
| L1 — sem código de erro legível por máquina | **Confirmada** — todos os seis erros provocados só trazem `detail` em texto |
| L2 — sem limite de tamanho declarado | **Confirmada** — arquivo de 64MB devolve o mesmo erro genérico e enganoso |
| L3 — sem timeout declarado | **Confirmada** — herda o default do SDK (5s conexão / 600s leitura), não configurado pelo backend |
| L4 — evento final do streaming sem custo/modelo | **Confirmada** — só tem `texto` |
| L5 — contrato sem versão | **Confirmada** (não estava na tabela original de erros, mas é lacuna real, citada no corpo da SPEC-001) |
| L6 — áudio sem fala sem comportamento definido | **Confirmada, e reclassificada**: não é "indefinido" — é definido e ruim (`200` com alucinação em idioma aleatório, nos dois modos) |
| L7 — CORS aberto | **Confirmada, aceitável por ora** — sem mudança nesta fase |
| L8 — sem parâmetro de idioma | **Refutada como problema** — medição mostrou que forçar `pt` não muda texto, custo nem tempo de forma mensurável; o contrato não ganha o parâmetro `idioma` (Etapa 5 do `PLANO.md` cai) |

Achados novos, fora das lacunas originais da SPEC-001:
- `gpt-4o-transcribe-diarize` com streaming não emite eventos `delta`, só o `final`.
- `gpt-4o-transcribe-diarize` sempre grava `custo_usd: 0.0` em `consumo.jsonl` (bug de tabela de preços).
