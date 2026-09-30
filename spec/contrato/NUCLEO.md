---
artefato: Contrato do núcleo de transcrição
origem: SPEC-001_contrato-do-nucleo.md
medido_em: 2026-08-23
atualizado_em: 2026-09-30 (contrato 2 — núcleo remoto no Supabase, com login, D-36; antes: 2026-08-27, Operação 3, D-31)
status: observado (não é aspiração) — cada afirmação sobre o núcleo remoto diz se foi medida ou lida no código
---

# Contrato do núcleo de transcrição

> **Contrato 2 — 2026-09-30 (`D-36`).** O núcleo passou a morar em **dois lugares**: o **remoto**
> (Edge Functions no Supabase, com login obrigatório — Operações 1 e 2) e o **local** (a máquina do
> usuário — Operação 3, e as Operações 1 e 2 como saída de emergência). Um cliente novo começa por
> [Onde o núcleo escuta](#onde-o-núcleo-escuta) e [Autenticação](#autenticação-só-no-núcleo-remoto).
> O que valia só para o núcleo local continua neste documento, marcado como tal; o que mudou ganhou
> a data e o ponteiro para `D-36`. O histórico de consumo saiu dos `.jsonl` para o banco
> ([Registro de consumo](#registro-de-consumo-2026-09-30-d-36)).
>
> **Como ler as marcas das seções do remoto** — não há mais um "tudo medido" geral:
> - **[medido]** — observado contra o serviço real, com a fonte citada. As fontes são os testes de
>   `nucleo-remoto/testes/` rodados no Windows do usuário em 2026-09-30 — `testar_transcrever.log`
>   (04:10) e `testar_consumo_e_imagem.log` (13:02); os `.log` são locais e não versionados, e o
>   resumo de cada um está no `PROGRESSO.md` das Etapas 3 e 4 — e o uso real do app de desktop na
>   Etapa 5 (`desktop/app.log` e a conferência do PM no banco).
> - **[código]** — lido no código (`nucleo-remoto/funcoes/*/index.ts`, `transcritor/backend/main.py`,
>   `desktop/app.py`, `nucleo-remoto/banco/assistente_base.sql`). Onde diz **[código + teste local]**,
>   também foi exercitado contra servidores falsos locais, não contra o serviço real.
> - **[documentação]** — comportamento do próprio Supabase, não medido aqui.

**Acrescentado em 2026-08-27**: o núcleo ganhou uma operação que **não é de transcrição** —
`POST /gerar-imagem` (Operação 3, abaixo). É uma entrada fora do plano da Fase 2 (`D-31`), pedida
direto pelo usuário; o nome deste documento continua "contrato do núcleo de transcrição" por
inércia histórica, não porque o núcleo só transcreva mais.

Este documento descreve tudo que um cliente novo (app desktop, Android, Wear, ou qualquer outro)
precisa saber para consumir o núcleo de transcrição — **sem abrir `index.html` nem `main.py`**.
Todo comportamento aqui foi **medido contra o backend rodando** em 2026-08-23 (não é leitura de
código): cada exemplo de resposta é uma captura real, e cada linha da tabela de erros foi
provocada de verdade. Onde a medição divergiu da SPEC-001 original (que tinha sido levantada só
por leitura de código), o que está escrito aqui é **o observado** — a divergência em si está
listada no `PROGRESSO.md` da tarefa, para o PM decidir o que fazer com ela. *(2026-09-30: este
parágrafo vale para o que descreve o núcleo local. O núcleo remoto usa as marcas **[medido]** /
**[código]** do quadro acima.)*

## Onde o núcleo escuta

**Desde 2026-09-30 (`D-36`), em dois lugares — escolha pela operação:**

| | **Núcleo remoto** | **Núcleo local** |
|---|---|---|
| endereço base | `https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1` | `http://127.0.0.1:8000` |
| Operação 1 — `POST /transcrever` | **sim — use este** | sim, **só como saída de emergência** |
| Operação 2 — `GET /consumo` | **sim — use este** | sim, **só como saída de emergência** (e lê os `.jsonl`, não o banco) |
| Operação 3 — `POST /gerar-imagem` | **não existe** | **sim — o único lugar** |
| login | **obrigatório** (ver [Autenticação](#autenticação-só-no-núcleo-remoto)) | não exige; aceita o token e, na Operação 3, usa-o |
| versão (`X-Nucleo-Contrato`) | `2` | `1` |
| onde o consumo fica | banco (`assistente.*`) | banco, se veio com token (só Operação 3); `.jsonl`, sem token |

- **As rotas têm o mesmo nome nos dois**: a função remota `transcrever` responde em
  `…/functions/v1/transcrever`, e a `consumo` em `…/functions/v1/consumo`. Um cliente monta
  `endereço base + "/transcrever"` e troca só a base **[medido: os dois `.log`; o desktop faz isso,
  `desktop/app.py`]**.
- **Saída de emergência**: apontar as Operações 1 e 2 de volta para `http://127.0.0.1:8000` funciona
  como antes da Etapa 5 — o núcleo local não exige login e ignora o cabeçalho `Authorization` em
  `/transcrever` e `/consumo` **[código + teste local: `main.py` não lê cabeçalho nessas rotas, e o
  `/transcrever` do `main.py` real com e sem `Bearer` gravou igual no teste A/B da Etapa 4; o desktop
  apontado para um núcleo local falso funciona sem login — `desktop/testes_sessao.py`, S5]**. O preço: o que for ditado ali vai para os `.jsonl`, não para o
  banco (e depois pode ser levado ao banco por `nucleo-remoto/banco/importar_historico.cmd`, que
  não duplica).
- **Limites do remoto que o local não tem**: cada requisição a uma Edge Function tem teto de 150 s
  no plano gratuito (`D-36`) — é por isso que `gpt-4o-transcribe-diarize` saiu do remoto e que a
  chamada à OpenAI tem prazo de 120 s **[código]**. O projeto é o **rag-compartilhado**, dividido com
  o RAG unificado da Mari e do assistente de vendas (`D-36`, nota da Etapa 1).
- **Um cliente não deve fixar nenhum dos dois endereços no código** — mesma regra de antes (abaixo):
  deixe os dois configuráveis, com estes valores como padrão. O desktop guarda os dois em
  `desktop/config.json` (`url_nucleo` e `url_nucleo_imagem`).

**Histórico — como era até 2026-09-29 (contrato 1, só o núcleo local):**

`http://127.0.0.1:8000` por padrão — o núcleo é um servidor local, subido com `uvicorn` a partir de
`transcritor/` (ver `transcritor/README.md` para o passo a passo).

**Acrescentado em 2026-08-26**, e vale registrar como foi descoberto: era a **única lacuna** que dois
clientes independentes encontraram ao serem escritos lendo só este documento. Nenhum dos dois
conseguiu adivinhar o endereço, e os dois tiveram de abrir outro arquivo para achá-lo. Não é
comportamento de API — é informação operacional —, mas sem ela o contrato não basta, que era
justamente o critério de conclusão da Fase 1.

**Um cliente não deve fixar este endereço no código**: deixe configurável, com este valor como
padrão.

## Autenticação (só no núcleo remoto)

**Nova em 2026-09-30 (`D-36`).** O núcleo remoto só atende um **usuário do Supabase Auth** do
projeto. Não há cadastro aberto: o usuário é criado no painel do Supabase (Authentication → Users),
e o cadastro público foi desligado na Etapa 2 (passo feito pelo usuário no painel; este documento não
o conferiu) **[documentação do plano, `PROGRESSO.md` da Etapa 2]**. O núcleo local não tem login.

Valores públicos por desenho (podem ir em qualquer cliente): a URL do projeto
`https://wqoeoofhuhsdzpkdblbg.supabase.co` e a chave publicável
`sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w`. **Nenhuma chave secreta (`service_role`) é usada
por cliente algum**, nem pelas funções: elas gravam e leem o banco com o token do próprio usuário
**[código]**.

### Entrar (uma vez)

```
POST https://wqoeoofhuhsdzpkdblbg.supabase.co/auth/v1/token?grant_type=password
apikey: sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w
Content-Type: application/json

{"email": "<e-mail>", "password": "<senha>"}
```

- `200` devolve, entre outros, `access_token` (o token que vai nas chamadas), `refresh_token`,
  `expires_in` (segundos), `expires_at` (epoch) e `user` **[medido: "Login ok" nos dois `.log` e no
  uso real; campos: código — `desktop/app.py`, `Sessao._aplicar` — e documentação]**.
- Credencial errada: `400` com `error_code: "invalid_credentials"` **[documentação; código + teste
  local — `desktop/testes_sessao.py`, S2]**. O cliente não deve gravar a senha: guarde só o que a API
  devolve.
- O `apikey` é exigido **pelo Auth** **[documentação]** — todo cliente deste projeto o manda nessa
  chamada.

### Renovar

```
POST https://wqoeoofhuhsdzpkdblbg.supabase.co/auth/v1/token?grant_type=refresh_token
apikey: sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w
Content-Type: application/json

{"refresh_token": "<o último refresh_token recebido>"}
```

- **O token de renovação muda a cada uso**: a resposta traz um `refresh_token` novo, e é ele que vale
  na próxima renovação. Guarde sempre o último **[documentação; o desktop grava o novo a cada
  renovação — código + teste local, S3]**. Duas renovações simultâneas com o mesmo token podem
  derrubar a sessão; o desktop serializa as renovações com um lock **[código]**.
- O token de acesso vale ~1 h (padrão do projeto) **[documentação]**. Medido no uso real:
  `sessao: login ok` às 14:30 e `sessao: renovada` às 15:39 de 2026-09-30, no `desktop/app.log`
  **[medido]**.
- Como o desktop faz (sugestão para qualquer cliente) **[código + teste local, S3/S4]**: renova
  **antes** de chamar, quando faltam menos de 2 min para `expires_at`; se uma chamada voltar `401`,
  renova **uma vez** e repete; se a renovação for recusada (`400`/`401`/`403`), descarta a sessão e
  pede login de novo — sem perder o que estava sendo enviado.

### Cabeçalhos que as funções exigem

| cabeçalho | exigido? | evidência |
|---|---|---|
| `Authorization: Bearer <access_token>` | **sim**, nas duas funções | **[medido]**: sem ele, `401` do gateway (caso 1 de `testar_transcrever.log`, passo 1 de `testar_consumo_e_imagem.log`) |
| `apikey` | **não** — nas funções | **[medido no uso real + código]**: o desktop manda só `Authorization` às funções (`desktop/app.py`, `_cabecalho_autorizacao`) e os ditados reais da Etapa 5 caíram no banco (conferido pelo PM). Os testes mandam os dois, o que também funciona **[medido]** |
| `Content-Type: multipart/form-data` | na Operação 1 | como no contrato 1 |

O token precisa ser de **usuário**: o gateway (`verify_jwt`) aceita qualquer JWT válido do projeto,
inclusive a chave anônima legada **[documentação]**, e é a função que confere, com o Auth, se há um
usuário por trás antes de gastar uma chamada paga **[código + teste local]**.

### As duas formas de `401`

| quem responde | quando | corpo | `X-Nucleo-Contrato` | evidência |
|---|---|---|---|---|
| **o gateway do Supabase** (a função nem roda) | sem `Authorization`, ou JWT inválido/expirado | JSON do gateway, **sem `codigo`**: sem cabeçalho veio `{"code": "UNAUTHORIZED_NO_AUTH_HEADER", "message": "Missing authorization header"}` | **ausente** | corpo e status **[medido]**, nas duas funções; JWT expirado não foi provocado; a ausência do cabeçalho é **[código]** (o gateway responde antes da função) |
| **a função** | JWT válido que não é de usuário (ex.: a chave anônima) ou que o Auth recusa | `{"detail": "Sessão inválida ou expirada — faça login de novo", "codigo": "NAO_AUTENTICADO"}` (ou "Sessão ausente…") | `2` | **[código + teste local]** |

**Regra para o cliente**: trate **qualquer** `401` do núcleo remoto como "sessão expirada" — renove
uma vez e repita; se não der, peça login. Não dependa de `codigo` no `401`, porque o do gateway não
tem. O desktop mostra "Sessão expirada — entre de novo." nos dois casos **[código + teste local]**.

### Sem CORS

As funções remotas **não** mandam `Access-Control-Allow-Origin` — o cliente é o app de desktop, não
uma página web (`B-08`, resolvido) **[código + teste local; não medido contra o serviço real]**. Uma
página web que queira chamar o núcleo remoto direto do navegador **não vai conseguir** hoje.

## Fora do contrato: o modo ao vivo

`GET /tempo-real/token` e `POST /tempo-real/turno-concluido` existem no backend e continuam
servindo a interface web atual, mas **não fazem parte deste contrato** — estão congelados por
decisão de 2026-08-21. **Nenhum cliente novo deve consumi-los.** `GET /favicon.ico` é detalhe da
interface web, também fora do contrato. (2026-09-30: existem só no núcleo local; o remoto não os tem,
e o modo ao vivo está morto — `D-33`.)

## Versionamento

**Corrigida em 2026-08-24 (R4).** Toda resposta de `POST /transcrever` e `GET /consumo` — sucesso
**e** erro, nos dois modos — carrega o cabeçalho `X-Nucleo-Contrato: 1`. Confirmado por medição
real: presente nas duas rotas em todos os casos testados, **ausente** em `GET /tempo-real/token`
(fora do contrato, ver acima). Se o formato mudar no futuro, o número muda junto — um cliente pode
checar o cabeçalho antes de assumir o formato.

**`POST /gerar-imagem` (Operação 3, 2026-08-27) entrou na mesma lista** — carrega o mesmo cabeçalho,
confirmado por medição (ver abaixo).

**2026-09-30 (`D-36`) — o núcleo remoto fala o contrato `2`; o local continua no `1`.** Autenticação
obrigatória é mudança de contrato (a mesma requisição que funcionava passa a voltar `401`), então o
número sobe no remoto. O **formato** das respostas de sucesso das Operações 1 e 2 é o mesmo do `1`;
o que muda está listado em cada operação, em "No núcleo remoto". Toda resposta **das funções** —
sucesso e erro — leva `X-Nucleo-Contrato: 2` **[código: `VERSAO_CONTRATO_NUCLEO = "2"` nas duas
funções, conferido no código implantado com `get_edge_function` em 2026-09-30 (versão 4 das duas)]**;
o `401` do gateway não leva cabeçalho nenhum do núcleo (ver [Autenticação](#as-duas-formas-de-401)).
Os testes reais da Etapa 3/4 foram rodados **antes** da troca e mediram `1` — o valor `2` em si ainda
não foi medido numa resposta real. Antes de subir, conferiu-se que nenhum cliente compara o valor do
cabeçalho (`desktop/app.py` e `transcritor/frontend/index.html` não leem cabeçalho de resposta
nenhum) **[código]**.

---

## Operação 1 — Transcrever áudio

`POST /transcrever`, `multipart/form-data`.

> **2026-09-30:** o texto abaixo descreve a operação como o núcleo **local** a faz (contrato 1). No
> remoto ela é igual, com as divergências listadas em
> [Operação 1 no núcleo remoto](#operação-1-no-núcleo-remoto-contrato-2-2026-09-30-d-36).

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

**2026-09-30 (`D-36`)**: o núcleo saiu da máquina — e o remoto **não** tem CORS nenhum (`B-08`,
resolvido). Esta lacuna continua valendo só para o núcleo **local**.

## Operação 1 no núcleo remoto (contrato 2, 2026-09-30, `D-36`)

`POST https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/transcrever`, com
`Authorization: Bearer <access_token>`.

**Igual ao local:** os campos do formulário (`audio`, `modelo`, `stream`), a resposta sem streaming
(`{"transcricao": ...}`), o streaming NDJSON com `delta` e `final` (e `erro` dentro do `200`), os
`codigo` e status da tabela de erros acima, o teto de 25 MB, a ordem das validações (modelo, chave,
vazio, tamanho — todas antes de abrir o stream) e o cálculo de custo registrado **[código]**.
Medido contra o serviço real **[medido: `testar_transcrever.log`, 2026-09-30 04:10]**:
- sem streaming: `200`, `transcricao` de 287 caracteres para `audio-teste/fala-real.wav` (~32 s),
  em 4,0 s;
- com `stream=true`: `200`, `Content-Type: application/x-ndjson`, 81 eventos `delta` e 1 `final`,
  em 2,7 s;
- `modelo=gpt-4o-transcribe-diarize` → `422 MODELO_INVALIDO`, detalhe
  `Modelo inválido: 'gpt-4o-transcribe-diarize'. Valores aceitos: gpt-4o-transcribe, gpt-4o-mini-transcribe`;
- áudio de 0 byte → `400 AUDIO_VAZIO` (`Arquivo de áudio vazio`);
- as duas chamadas de sucesso deixaram +2 linhas em `assistente.consumo` com
  `origem = 'nucleo-remoto'` e +2 em `assistente.transcricoes` ligadas a elas;
- no uso real do desktop (Etapa 5), 2 ditados caíram no banco com `origem = 'nucleo-remoto'`
  (conferido pelo PM) **[medido]**.

**Divergências em relação ao local:**

| o quê | remoto | local | marca |
|---|---|---|---|
| `gpt-4o-transcribe-diarize` | recusado com `422 MODELO_INVALIDO` (só `gpt-4o-transcribe` e `gpt-4o-mini-transcribe`) | aceito | **[medido]** |
| prazo da chamada à OpenAI | 120 s para a chamada inteira, **uma** tentativa, sem prazo separado de conexão → `504 TEMPO_ESGOTADO` (ou evento `erro`) | 120 s de leitura por tentativa, 3 tentativas do SDK (até ~6 min) | **[código + teste local]** |
| login | obrigatório; `401` do gateway ou `401 NAO_AUTENTICADO` | não há | **[medido]** (gateway) / **[código + teste local]** (função) |
| `detail` de `SEM_CHAVE` | `OPENAI_API_KEY não configurada — crie o segredo nas Edge Functions do Supabase` | cita `transcritor/.env` | **[código + teste local]** |
| `detail` de `FALHA_AUTENTICACAO` | `… verifique o segredo OPENAI_API_KEY nas Edge Functions do Supabase` | cita `transcritor/.env` | **[código + teste local]** |
| corpo não multipart, ou sem `audio` | `422 REQUISICAO_INVALIDA`, com `codigo` | `422` do FastAPI, sem `codigo` | **[código + teste local]** |
| método que não é `POST` | `405 METODO_NAO_PERMITIDO`, com `codigo` | `405` do FastAPI | **[código + teste local]** |
| erro inesperado da função | `500 ERRO_INTERNO`, com `codigo` | — | **[código]** |
| `stream` com valor que não é `true`/`false` | `true`, `1`, `yes`, `on` valem verdadeiro; qualquer outro vale falso | `422` do FastAPI | **[código]** |
| CORS | nenhum `Access-Control-Allow-Origin` | `*` (L7) | **[código + teste local]** |
| onde registra | banco, com o token do usuário; falha ao registrar não quebra a resposta (só vai para o log da função, sem texto) | `.jsonl` | **[medido]** (registro) / **[código + teste local]** (falha) |
| `X-Nucleo-Contrato` | `2` | `1` | **[código]** — ver Versionamento |

Não provocados contra o serviço real (cobertos só por código e teste local): `TEMPO_ESGOTADO`,
`SEM_CONEXAO`, `API_RECUSOU`, `FALHA_AUTENTICACAO`, `SEM_CHAVE`, `ARQUIVO_MUITO_GRANDE`,
`REQUISICAO_INVALIDA`, `METODO_NAO_PERMITIDO`, `NAO_AUTENTICADO`. As lacunas L4 (evento `final` só com
`texto`) e L6 (áudio sem fala alucina) valem igual no remoto — a função repassa o que a API devolve
**[código]**.

---

## Operação 2 — Consultar consumo

> **2026-09-30:** o texto abaixo descreve o núcleo **local** (contrato 1), que lê os `.jsonl`. O
> remoto lê o banco e tem as divergências listadas em "No núcleo remoto", no fim desta operação.

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

### No núcleo remoto (contrato 2, 2026-09-30, `D-36`)

`GET https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/consumo`, com
`Authorization: Bearer <access_token>`. Lê `assistente.consumo` e `assistente.transcricoes` **como o
usuário** — o RLS só devolve as linhas dele **[código]**.

**Igual ao local:** a forma inteira — `sessao` (`requisicoes`, `tokens`, `custo_usd`), `por_dia`
(`data`, `requisicoes`, `tokens`, `custo_usd`), `requisicoes` (`id`, `timestamp`, `modelo`,
`custo_usd`, `texto`, com `texto` casado pelo `id_consumo` e `null` quando não há). Medido contra o
serviço real **[medido: `testar_consumo_e_imagem.log`, 2026-09-30 13:02]**: `200`, forma do contrato,
1866 requisições — o mesmo total que a API de dados conta em `assistente.consumo` para o usuário —,
35 dias em `por_dia`, soma de `custo_usd` da função igual à da API (6,8910358333), 1806 requisições
com texto, em 2,9 s. O painel de Consumo do desktop abriu contra ele no uso real da Etapa 5
**[medido, uso real — relato do usuário, "deu tudo certo"]**.

**Divergências em relação ao local:**

| o quê | remoto | local | marca |
|---|---|---|---|
| `sessao` | acumulado **do dia corrente em São Paulo** (`America/Sao_Paulo`) — não há processo remoto para "desde que subiu" | acumulado desde que o processo subiu | **[código + teste local]**; o valor em si apareceu no teste real (48 requisições, US$ 0,117623), a regra do fuso não foi medida |
| `por_dia` | agrupado pela **data em São Paulo** | pelos 10 primeiros caracteres do `timestamp`, ou seja, **UTC** | **[código + teste local]** — uma requisição de 02:30 UTC cai no dia anterior |
| `id` | uuid **com hífens** | `uuid.hex`, sem hífens; `null` nas 49 linhas antigas sem `id` (que no banco ganharam uuid5 na importação) | **[código]** |
| `timestamp` | formato do Postgres (`…+00:00`), com milissegundos nas linhas gravadas pela função | o texto gravado no `.jsonl` (microssegundos) | **[código]** |
| quais linhas | **só as do usuário logado** (RLS) | tudo o que está no arquivo | **[código]**; o total bateu com a contagem da API, que também passa pelo RLS **[medido]** |
| erros | `401` (gateway ou `NAO_AUTENTICADO`), `405 METODO_NAO_PERMITIDO`, `502 FALHA_BANCO` (leitura do banco falhou), `500 ERRO_INTERNO` — todos com `codigo`, menos o do gateway | nunca erra; arquivo ausente dá listas vazias | `401` do gateway **[medido]**; o resto **[código + teste local]** |
| limite de linhas | lê o banco em páginas de 1000 (o teto da API de dados) até o fim | lê o arquivo inteiro | **[código + teste local, 2500 linhas]**; 1866 no real **[medido]** |
| CORS | nenhum | `*` | **[código + teste local]** |
| `X-Nucleo-Contrato` | `2` | `1` | **[código]** |

O achado antigo desta operação (`gpt-4o-transcribe-diarize` com `custo_usd` zero) não se aplica ao
remoto, que não aceita esse modelo; as linhas antigas importadas dos `.jsonl` continuam com o custo
que tinham.

---

## Operação 3 — Gerar imagem

**Acrescentada em 2026-08-27, fora do plano da Fase 2 (`D-31`)** — pedido direto do usuário, não é
transcrição. > **2026-09-30:** só existe no núcleo **local**. Com `Authorization: Bearer <token>`, o consumo vai
> para o banco em vez dos `.jsonl` — ver "Com o token do usuário", mais abaixo.

`POST /gerar-imagem`, `multipart/form-data`. Quem fala com a API da OpenAI é sempre o
núcleo; nenhum cliente tem (nem precisa) da chave.

| Campo | Tipo | Obrigatório | Padrão | Observação |
|---|---|---|---|---|
| `imagens` | arquivo, repetido | sim | — | uma ou mais, até 16; `.png`, `.jpg`/`.jpeg` ou `.webp`, até 50 MB cada |
| `prompt` | texto | sim | — | vazio (ou só espaço) é erro |
| `modelo` | texto | não | `gpt-image-1.5` | ver lista abaixo |
| `tamanho` | texto | não | `auto` | `auto`, `1024x1024`, `1536x1024`, `1024x1536` |
| `qualidade` | texto | não | `medium` | `low`, `medium`, `high`, `auto` |

### Modelos aceitos

| Modelo | Observação |
|---|---|
| `gpt-image-2` | o mais novo (flagship atual) |
| `gpt-image-1.5` | **padrão desta rota** — decisão explícita da tarefa que criou esta operação, não do modelo mais novo estar disponível |
| `gpt-image-1` | a OpenAI já avisa remoção futura (23/10/2026, confirmado por busca em 2026-08-27) |
| `gpt-image-1-mini` | mais barato dos quatro |

**`dall-e-2` não está na lista** — a tarefa original que criou esta operação o citava como aceito,
mas uma busca em 2026-08-27 confirmou que **a OpenAI removeu `dall-e-2`/`dall-e-3` da API em
2026-05-12**. Chamá-lo hoje devolveria erro da própria API; por isso o backend rejeita antes, com
`MODELO_INVALIDO` (confirmado por medição — ver tabela de erros abaixo).

### Resposta de sucesso

`200`, `Content-Type: application/json`. Captura real (chamada com duas imagens de referência —
um quadrado vermelho e um azul — e o prompt *"Combine as duas cores de referência num degradê
diagonal simples, sem texto"*, `gpt-image-1.5`, `tamanho=1024x1024`, `qualidade=low`):

```json
{
  "imagem_b64": "iVBORw0KGgoAAAANSUhEUgAABAA...",
  "formato": "png",
  "custo_usd": 0.08183800000000001,
  "revised_prompt": null
}
```

- `imagem_b64` — a imagem inteira em base64 (`b64_json` da API, repassado direto). A chamada real
  devolveu um PNG 1024×1024 válido (decodificado e conferido nesta medição).
- `formato` — vem de `output_format` da resposta; `png` nesta captura (o backend não força nenhum).
- `custo_usd` — calculado pelo backend a partir de `usage` (ver "O custo, medido de verdade"
  abaixo), **sempre presente**, mesmo que o registro em `consumo.jsonl` falhe (acessório).
- `revised_prompt` — só existe para `dall-e-3` segundo a documentação da OpenAI; **veio `null`
  nesta medição com `gpt-image-1.5`**, consistente com isso.

### O custo, medido de verdade — bem mais caro que transcrever (`D-31`, `D-18`)

Confirmado por medição em 2026-08-27, `gpt-image-1.5`, duas imagens de referência de 256×256:

| tamanho | qualidade | `input_tokens` | `output_tokens` | `custo_usd` |
|---|---|---|---|---|
| `1024x1024` | `low` | 8.762 | 372 | **US$ 0,0818** |
| `auto` | `medium` (padrão) | 4.378 | 1.254 | **US$ 0,0751** |

Para comparar: uma transcrição de ~13s custa em torno de **US$ 0,0007** — a geração de imagem
custou entre **~115× e ~120×** mais nestas duas medições. A maior parte do custo real vem da
**entrada** (as imagens de referência), não só da saída — a estimativa que um cliente mostra
**antes** de gerar (baseada só em tokens de saída típicos por qualidade) fica bem abaixo do custo
real quando há imagens de referência grandes; só a resposta da API sabe o valor exato.

`usage` desta operação não tem campo `type` (diferente da Operação 1) — tem
`input_tokens_details.{text_tokens, image_tokens}` em vez de um `input_tokens` só. O backend
detecta esse formato (por `input_tokens_details` estar presente) e aplica os três preços por
token (texto de entrada, imagem de entrada, saída) da tabela `PRECOS_POR_TOKEN_USD`, confirmados
em <https://developers.openai.com/api/docs/pricing> (consulta em 2026-08-27):

| modelo | texto de entrada | imagem de entrada | saída |
|---|---|---|---|
| `gpt-image-2` | US$ 5,00 / milhão | US$ 8,00 / milhão | US$ 30,00 / milhão |
| `gpt-image-1.5` | US$ 5,00 / milhão | US$ 8,00 / milhão | US$ 32,00 / milhão |
| `gpt-image-1` | US$ 5,00 / milhão | US$ 10,00 / milhão | US$ 40,00 / milhão |
| `gpt-image-1-mini` | US$ 2,00 / milhão | US$ 2,50 / milhão | US$ 8,00 / milhão |

**Atenção para quem for reusar a Etapa anterior desta tarefa**: o rascunho original citava
US$ 5/US$ 10/US$ 40 como se fossem os preços de `gpt-image-1.5` — são os preços de `gpt-image-1`.
`gpt-image-1.5` (o padrão desta rota) é **US$ 5/US$ 8/US$ 32** — mais barato na entrada de imagem e
mais caro na saída. Confira sempre contra a página oficial antes de fixar um número.

### O registro reaproveita o caminho de `/transcrever`, sem mudar o cliente

Confirmado por medição: a requisição aparece em `consumo.jsonl` com o mesmo formato de campos
(`id`, `timestamp`, `modelo`, `custo_usd`, `total_tokens`), e em `transcricoes.jsonl` com o
**prompt no lugar do texto transcrito** — então `GET /consumo` devolve a geração de imagem
misturada com as transcrições, sem nenhuma mudança no cliente que já lê essa rota:

```json
{"id": "ba16ae0c...", "timestamp": "2026-08-27T21:47:54...", "modelo": "gpt-image-1.5", "custo_usd": 0.08183800000000001, "texto": "Combine as duas cores de referência num degradê diagonal simples, sem texto"}
```

### Com o token do usuário (2026-09-30, `D-36`)

A Operação 3 **só existe no núcleo local** (`http://127.0.0.1:8000/gerar-imagem`). O cabeçalho
`Authorization: Bearer <access_token>` é **opcional**, e muda **só onde o consumo é registrado** — a
requisição, a resposta e os erros são os mesmos **[código + teste local — A/B contra o `main.py`
anterior]**:

| | sem `Authorization` (ou em outro formato que não `Bearer <token>`) | com `Authorization: Bearer <token>` |
|---|---|---|
| onde registra | `consumo.jsonl` e `transcricoes.jsonl`, como antes | banco, **como o usuário do token**: uma linha em `assistente.consumo` com `origem = 'nucleo-local-imagem'` (mesmos campos e custo), depois uma em `assistente.transcricoes` com o **prompt** no `texto` — e **nada** nos `.jsonl` |
| evidência | **[código + teste local]** | **[medido: `testar_consumo_e_imagem.log`, passos 3–4]**: `200`, `custo_usd` 0,047231, `X-Nucleo-Contrato: 1`, +1 `nucleo-local-imagem` e +1 transcrição no banco, 0 linhas novas de imagem nos `.jsonl`; e 1 imagem gerada pelo app no uso real da Etapa 5 **[medido, conferido pelo PM]** |

- **Falha ao registrar nunca quebra a resposta**: se o banco recusar ou estiver fora, a imagem volta
  normalmente e o núcleo só escreve uma linha no seu log (código e mensagem do banco, sem prompt nem
  token); o registro dessa imagem se perde — não há recaída para os `.jsonl` **[código + teste local]**.
  Com o banco fora do ar, a resposta atrasa até 10 s (prazo do registro) **[código + teste local]**.
- **O núcleo local precisa de `SUPABASE_URL` e `SUPABASE_CHAVE_PUBLICAVEL` no `transcritor/.env`**
  (valores públicos, estão no `.env.example`). Sem eles, com token, a imagem **não é registrada em
  lugar nenhum** — só um aviso no log **[código + teste local]**.
- O núcleo local continua no contrato `1` e sem CORS fechado (L7) — ele não saiu da máquina.
- **Achado de 2026-09-30**: `gpt-image-1-mini` foi recusado pela OpenAI (`502 API_RECUSOU`, "HTTP
  400") no teste real; `gpt-image-1.5` passou **[medido: `testar_consumo_e_imagem.log`, passo 3]**. A
  causa não foi investigada (o núcleo pede `input_fidelity="high"`; é hipótese, não fato).

### Erros de `POST /gerar-imagem`

Cinco situações provocadas de verdade contra o backend (2026-08-27), todas com `codigo` estável ao
lado de `detail`, mesmo padrão da Operação 1:

| Situação | `codigo` | Resposta medida |
|---|---|---|
| Prompt vazio ou só espaço | `PROMPT_VAZIO` | `400` `{"detail":"O prompt não pode ficar vazio","codigo":"PROMPT_VAZIO"}` |
| Arquivo que não é imagem aceita (`.txt` testado) | `FORMATO_NAO_ACEITO` | `415` `{"detail":"Formato não aceito em 'arquivo.txt'. Use PNG, JPG ou WEBP","codigo":"FORMATO_NAO_ACEITO"}` |
| Mais de 16 imagens de referência (17 testadas) | `IMAGENS_DEMAIS` | `413` `{"detail":"No máximo 16 imagens de referência; recebi 17","codigo":"IMAGENS_DEMAIS"}` |
| Modelo fora da lista aceita (`dall-e-2` testado — ver acima por quê) | `MODELO_INVALIDO` | `422` `{"detail":"Modelo inválido: 'dall-e-2'. Valores aceitos: gpt-image-2, gpt-image-1.5, gpt-image-1, gpt-image-1-mini","codigo":"MODELO_INVALIDO"}` |
| Tamanho fora da lista aceita | `TAMANHO_INVALIDO` | `422` `{"detail":"Tamanho inválido: '9999x9999'. Valores aceitos: auto, 1024x1024, 1536x1024, 1024x1536","codigo":"TAMANHO_INVALIDO"}` |

Não provocados nesta medição (implementados pelo mesmo padrão da Operação 1, reaproveitando
`_erro_api_para_codigo`, mas sem uma condição real de rede/chave à mão para testar): `SEM_CHAVE`,
`FALHA_AUTENTICACAO`, `SEM_CONEXAO`, `TEMPO_ESGOTADO`, `API_RECUSOU`, `QUALIDADE_INVALIDA`,
`IMAGEM_AUSENTE`, `IMAGEM_VAZIA`, `ARQUIVO_MUITO_GRANDE` (50 MB por imagem, mesmo limite —
`"Files can be up to 50MB in size."` para a rota de edição de imagem).

Todas as validações de campo (`PROMPT_VAZIO`, `MODELO_INVALIDO`, `TAMANHO_INVALIDO`,
`QUALIDADE_INVALIDA`, `IMAGENS_DEMAIS`, `FORMATO_NAO_ACEITO`, `IMAGEM_AUSENTE`, `IMAGEM_VAZIA`)
acontecem **antes** de qualquer chamada à API — não geram custo, mesmo padrão da Operação 1.

---

## Registro de consumo (2026-09-30, `D-36`)

O histórico de consumo mora no banco do projeto Supabase, schema **`assistente`** **[código:
`nucleo-remoto/banco/assistente_base.sql`]**:

- **`assistente.consumo`** — uma linha por chamada paga: `id` (uuid), `user_id` (o usuário do Auth),
  `timestamp`, `modelo`, `custo_usd`, `tipo_usage`, `input_tokens`, `output_tokens`, `total_tokens`,
  `segundos`, **`origem`**.
- **`assistente.transcricoes`** — o texto de cada chamada (a transcrição, ou o **prompt** na
  geração de imagem): `id`, `id_consumo` (chave estrangeira para `consumo.id` — a linha de consumo é
  sempre gravada antes), `user_id`, `timestamp`, `modelo`, `texto`.
- **RLS por usuário**: o papel `authenticated` só faz `select` e `insert` das **próprias** linhas; não
  há `update` nem `delete` pela API, e o papel anônimo não enxerga o schema.
- **`origem`** tem três valores:

  | `origem` | quem grava |
  |---|---|
  | `importado-jsonl` | o importador (`nucleo-remoto/banco/importar_historico.py`), a partir dos `.jsonl` do núcleo local — idempotente, pode rodar de novo |
  | `nucleo-remoto` | a função `transcrever` (Operação 1 no remoto) |
  | `nucleo-local-imagem` | o núcleo local, na Operação 3 **com** token |

- **Os `.jsonl` (`transcritor/consumo.jsonl` e `transcricoes.jsonl`) continuam existindo**, e são o
  registro do **núcleo local sem token**: a saída de emergência das Operações 1 e 2, a interface web
  (`index.html`) e a Operação 3 sem token. O `GET /consumo` do núcleo local lê só eles; o do remoto
  lê só o banco. O desktop, desde a Etapa 5, não escreve mais nos `.jsonl` (conferido pelo PM: pararam
  de crescer depois do reinício) **[medido]**.
- Um cliente pode ler o próprio histórico direto pela API de dados
  (`https://wqoeoofhuhsdzpkdblbg.supabase.co/rest/v1/consumo`, com `apikey`, `Authorization` e
  `Accept-Profile: assistente`) — é o que os testes fazem para contar linhas **[medido]** —, mas o
  caminho do contrato é o `GET /consumo`.

## Resumo das lacunas L1–L8 da SPEC-001

| Lacuna | Status após medição |
|---|---|
| L1 — sem código de erro legível por máquina | **Corrigida em 2026-08-24** — todo erro traz `codigo` estável ao lado de `detail`, oito situações provocadas de verdade nos dois modos |
| L2 — sem limite de tamanho declarado | **Corrigida em 2026-08-24** — teto de 25 MB (documentado pela OpenAI), recusa em ~0,13s com `ARQUIVO_MUITO_GRANDE`/`413` |
| L3 — sem timeout declarado | **Corrigida em 2026-08-24** — cliente declara 120s de leitura / 5s de conexão, `TEMPO_ESGOTADO`/`504` ao estourar; tempo real até a falha medido (6min01,99s sem streaming — ver divergência no modo streaming na seção de erros) |
| L4 — evento final do streaming sem custo/modelo | **Confirmada** — só tem `texto` |
| L5 — contrato sem versão | **Corrigida em 2026-08-24** — `X-Nucleo-Contrato: 1` em sucesso e erro, nas duas rotas do contrato, ausente no modo ao vivo · **2026-09-30**: o núcleo remoto fala o `2` (autenticação obrigatória); o local segue no `1` — ver Versionamento |
| L6 — áudio sem fala sem comportamento definido | **Confirmada, e reclassificada**: não é "indefinido" — é definido e ruim (`200` com alucinação em idioma aleatório, nos dois modos) |
| L7 — CORS aberto | **Confirmada, aceitável por ora** — sem mudança nesta fase · **2026-09-30**: o núcleo remoto não tem CORS (`B-08`, resolvido); o local continua com `*`, porque não saiu da máquina |
| L8 — sem parâmetro de idioma | **Refutada como problema** — medição mostrou que forçar `pt` não muda texto, custo nem tempo de forma mensurável; o contrato não ganha o parâmetro `idioma` (Etapa 5 do `PLANO.md` cai) |

Achados novos, fora das lacunas originais da SPEC-001:
- `gpt-4o-transcribe-diarize` com streaming não emite eventos `delta`, só o `final`.
- `gpt-4o-transcribe-diarize` sempre grava `custo_usd: 0.0` em `consumo.jsonl` (bug de tabela de preços).
- Sob a mesma condição de rede que produz `TEMPO_ESGOTADO` no modo sem streaming, o modo streaming
  produziu `SEM_CONEXAO` (mais tempo até falhar, código diferente) — ver seção "Erros de `POST
  /transcrever`" acima.
