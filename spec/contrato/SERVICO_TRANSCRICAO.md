---
artefato: Contrato do serviço de transcrição para projetos clientes
origem: PLANO 2026-09-30, Etapa 3
medido_em: 2026-09-30 (teste do Windows das 17:53 e conferência do PM no banco)
status: observado (não é aspiração) — cada afirmação diz se foi medida, lida no código ou tirada da documentação
---

# Contrato do serviço de transcrição (`transcrever-servico`)

> Para quem integra o serviço num projeto cliente (hoje, o servidor da Mari) **sem abrir o código**.
> A decisão que criou o serviço é a `D-37`; o código é
> `nucleo-remoto/funcoes/transcrever-servico/index.ts` (versão implantada 6).
>
> **Como ler as marcas** (mesma legenda do [`NUCLEO.md`](NUCLEO.md)):
> - **[medido]** — observado contra o serviço real. Fontes: o `testar_servico.log` da execução de
>   **2026-09-30 17:53** (local, não versionado; resumo no `PROGRESSO.md` da Etapa 2) e a conferência
>   do PM em `servicos.transcricao_uso` depois dela.
> - **[código]** — lido em `transcrever-servico/index.ts` ou em `nucleo-remoto/banco/servicos_base.sql`.
>   **[código + teste local]** — também exercitado contra Postgres e OpenAI falsos locais, não contra o
>   serviço real.
> - **[documentação]** — comportamento do Supabase, da OpenAI ou do navegador, não medido aqui.
>
> Os tempos medidos (0,8 a 2,7 s por chamada) são **uma rodada**, não garantia.

## 1. Para que serve e para quem

Transcreve um áudio curto e devolve o texto, para **projetos clientes que chamam do próprio
servidor**. Não é para navegador nem para app de pessoa final. Recurso de acessibilidade da Mari:
a pessoa grava, o servidor da Mari manda o áudio, recebe o texto e o devolve à pessoa (`D-37`).

- Projeto cliente hoje: **só `mari`**, numa tabela fixa no código. Projeto novo exige mudar o código e
  reimplantar **[código]**.
- A chamada à OpenAI usa a chave da OpenAI **do próprio projeto cliente** (`OPENAI_API_KEY_MARI`), então
  o gasto cai na conta dele **[código]**.

## 2. Endereço e método

```
POST https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/transcrever-servico
Content-Type: multipart/form-data; boundary=...
x-servico-chave: <chave do projeto>

campo "audio": o arquivo de áudio
```

- A URL e o método: **[medido]**.
- O corpo precisa ter `Content-Type` começando por `multipart/form-data`, e o campo `audio` precisa ser
  um **arquivo** (um campo de texto chamado `audio` não serve) **[código + teste local]**.
- **Qualquer outro campo é ignorado**: `modelo`, `stream`, `projeto` ou o que vier **[código + teste
  local]**. Nada no corpo escolhe projeto, modelo ou streaming.
- A função não confere o formato do áudio: repassa à OpenAI o arquivo com o nome que veio (ou `audio`,
  se veio sem nome) **[código]**. Formato que a OpenAI não aceita volta como `502 API_RECUSOU`
  **[código]**. **Só WAV foi medido** (`fala-real.wav`, 1 026 318 bytes) **[medido]**. Um formato de
  gravação de navegador (WebM/Opus, por exemplo) não foi testado contra o serviço real.
- Mande o nome do arquivo com a extensão do formato (`gravacao.webm`, `gravacao.wav`). A API da OpenAI
  usa o nome para reconhecer o formato **[documentação — não verificado aqui]**.

Exemplo, do servidor, com a chave lida de uma variável de ambiente e nunca escrita no código:

```
curl -sS -X POST "https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/transcrever-servico" \
  -H "x-servico-chave: $SERVICO_CHAVE" \
  -F "audio=@gravacao.webm"
```

## 3. Autenticação

- Cabeçalho **`x-servico-chave`**. **Sem JWT**: a função está implantada com `verify_jwt: false`, e
  `Authorization`/`apikey` não são usados **[código]**.
- **O projeto sai da chave**: a função compara a chave recebida com a de cada projeto da tabela, em
  tempo constante (SHA-256 dos dois lados, todos os projetos percorridos), e o projeto é o da chave que
  casou **[código]**.
- Sem cabeçalho, ou com chave que não casa → `401 CHAVE_INVALIDA` **[medido]**.
- A chave mora num **segredo por projeto** nas Edge Functions do Supabase: **`SERVICO_CHAVE_MARI`**
  para a Mari **[código]**. Segredo ausente ou com **menos de 32 caracteres** desliga o projeto: toda
  chamada dele volta `401` **[código + teste local]**. A chave da Etapa 2 tem 43 caracteres **[medido]**.
- **Troca de chave:** sobrescrever o valor de `SERVICO_CHAVE_MARI` no painel. A função relê o segredo a
  cada requisição **[código]**. A chave antiga para de valer quando as instâncias em execução recebem o
  valor novo **[documentação — não medido]**. Em seguida, pôr a chave nova no servidor da Mari.
- Quem guarda o valor: só o segredo do Supabase e o servidor do projeto cliente. **Nunca** no front,
  no repositório, em log ou em chat.

## 4. Resposta de sucesso

```
HTTP/1.1 200
Content-Type: application/json
X-Servico-Contrato: 1

{"transcricao": "<texto>"}
```

- `200` com `transcricao` não vazia e `X-Servico-Contrato: 1` **[medido]** (293 caracteres para
  `fala-real.wav`, em 2,7 s, numa rodada).
- Se a OpenAI não devolver texto, `transcricao` vem `""` com `200` **[código]**. Áudio sem fala **não**
  vem vazio: vem texto alucinado (ver [obrigações](#9-obrigações-do-cliente)).
- **`X-Servico-Contrato`** vai em **toda** resposta que a própria função monta, de sucesso ou de erro
  **[código]**. É a versão deste contrato. Para o cliente:
  - valor `1`: este documento vale;
  - resposta **sem** o cabeçalho não veio da função, mas da plataforma (prazo esgotado, falha do
    gateway): trate pelo status, sem ler `codigo` **[código]**;
  - valor diferente de `1`: o contrato mudou; registre no log do servidor e avise quem mantém a
    integração.
- **O que muda a versão** (mesmo critério da seção [Versionamento do `NUCLEO.md`](NUCLEO.md#versionamento)): qualquer mudança que quebre um cliente escrito sobre este
  documento. Por exemplo, a forma do corpo de sucesso ou de erro, o nome ou o significado de um
  `codigo`, o cabeçalho de autenticação, o nome do campo `audio`, ou um limite que passe a recusar o que
  hoje é aceito. Não muda a versão: mensagem de `detail`, preço, valor do teto, projeto novo.

## 5. Limites

| limite | valor | quem confere | marca |
|---|---|---|---|
| tamanho do áudio | **4 MB = 4 194 304 bytes**, medido no arquivo `audio` (não no corpo inteiro); exatamente 4 194 304 passa, 4 194 305 volta `413` | a função | 4 194 305 → `413`: **[medido]**; 4 194 304 → `200`: **[código + teste local]** |
| duração | **2 min** | **o cliente** — a função não confere duração | **[código]** |
| modelo | fixo, **`gpt-4o-transcribe`**, sem streaming | a função | **[código]**; o modelo registrado no sucesso: **[medido]** |
| teto de gasto por dia | **US$ 1,00** por projeto, por padrão | a função, antes de chamar a OpenAI | **[código]** |
| prazo da chamada à OpenAI | **120 s**, uma tentativa só | a função → `504 TEMPO_ESGOTADO` | **[código]** |

Os quatro primeiros valores são escolha da `D-37`, não medição. O 4 MB não garante os 2 min: quanto
cabe depende do formato e da taxa de amostragem da gravação, que o cliente escolhe **[código]**.

**Teto diário, em detalhe:**
- O gasto do dia é a soma de `custo_usd` das linhas do projeto em `servicos.transcricao_uso` **[código]**.
- "Dia" é o **dia civil de São Paulo** (`America/Sao_Paulo`), de 00:00 a 00:00 **[código]**.
- A conferência é `gasto do dia ≥ teto` → recusa, **antes** da chamada paga. Uma chamada que começa
  abaixo do teto passa, mesmo que termine acima dele **[código]**.
- O segredo **`SERVICO_TETO_DIARIO_USD`** muda o teto. É **um valor só para todos os projetos**; o gasto
  é que é contado por projeto **[código]**. Ausente, vazio, não numérico ou negativo → US$ 1,00; `0` é
  válido e recusa tudo **[código + teste local]**. Com `0`, a recusa veio na primeira tentativa depois de
  criado o segredo **[medido]** (uma rodada; o tempo até valer não é garantido).

## 6. Erros

Todo erro da função tem corpo `{"detail": "<português>", "codigo": "<CODIGO>"}` e o cabeçalho
`X-Servico-Contrato: 1` **[código]**. Decida pelo **`codigo`**: o `detail` é para log e pode mudar.
Na ordem em que a função confere:

| # | status | `codigo` | quando | registra linha? | custa? | o que o cliente faz | marca |
|---|---|---|---|---|---|---|---|
| 1 | `405` | `METODO_NAO_PERMITIDO` | método que não é `POST` (inclusive `OPTIONS`) | não | não | não repetir: é erro de programação | **[código + teste local]** |
| 2 | `401` | `CHAVE_INVALIDA` | sem `x-servico-chave`, chave que não casa, ou projeto desligado | **não** | não | não repetir; alertar quem opera o servidor (chave errada ou trocada). À pessoa: "A transcrição está indisponível agora." | **[medido]** (sem chave e chave errada, nenhuma linha); projeto desligado: **[código + teste local]** |
| 3 | `422` | `REQUISICAO_INVALIDA` | corpo que não é multipart, ilegível, ou sem o arquivo `audio` | sim, sem modelo | não | não repetir: é erro de programação | **[código + teste local]** |
| 4 | `400` | `AUDIO_VAZIO` | arquivo de 0 byte | sim (`bytes_audio = 0`) | não | não repetir. À pessoa: "Não chegou áudio. Grave de novo." | **[código + teste local]** |
| 5 | `413` | `ARQUIVO_MUITO_GRANDE` | arquivo acima de 4 194 304 bytes | **sim**, `modelo` nulo, `custo_usd = 0`, com `bytes_audio` | **não** | não repetir o mesmo arquivo. À pessoa: "A gravação ficou longa demais; grave um trecho menor." | **[medido]** |
| 6 | `429` | `LIMITE_DIARIO` | gasto do dia do projeto ≥ teto | **sim**, `modelo` nulo, `custo_usd = 0` | **não** | não repetir hoje. À pessoa: "O limite diário de transcrição foi atingido; tente amanhã ou digite a pergunta." | **[medido]** |
| 6 | `503` | `LIMITE_INDISPONIVEL` | a consulta do gasto do dia falhou (banco fora, por exemplo) | tenta; com o banco fora, não consegue | não | pode repetir **uma vez**, depois de alguns segundos. À pessoa: "A transcrição está indisponível agora; tente em alguns minutos." | **[código + teste local]** |
| 7 | `503` | `SEM_CHAVE` | segredo `OPENAI_API_KEY_MARI` ausente | sim, sem modelo | não | não repetir; alertar quem opera. À pessoa: "indisponível agora." | **[código + teste local]** |
| 8 | `502` | `FALHA_AUTENTICACAO` | a OpenAI recusou a chave dela (HTTP 401) | sim, `modelo` preenchido, `custo_usd = 0` | não | não repetir; alertar quem opera | **[código + teste local]** |
| 8 | `502` | `API_RECUSOU` | a OpenAI respondeu outro erro HTTP (formato de áudio, limite ou falha da OpenAI) | sim, `custo_usd = 0` | não registrado | no máximo **uma** nova tentativa; se repetir, o formato do áudio é o suspeito | **[código + teste local]** |
| 8 | `502` | `SEM_CONEXAO` | a função não chegou à OpenAI, ou a resposta não era JSON | sim, `custo_usd = 0` | não registrado | pode repetir **uma vez** | **[código + teste local]** |
| 8 | `504` | `TEMPO_ESGOTADO` | a OpenAI não respondeu em 120 s | sim, `custo_usd = 0` | **pode ter custado** (ver [riscos](#10-riscos-aceitos)) | não repetir sozinho; oferecer à pessoa "tentar de novo" | **[código]** |
| 9 | `500` | `ERRO_INTERNO` | erro inesperado na função | sim, se passou da chave | não | pode repetir **uma vez**; se repetir, alertar quem opera | **[código]** |

A coluna "registra linha?" segue a regra de [o que é registrado](#8-o-que-é-registrado-e-o-que-nunca-é):
tudo que passa da chave deixa uma linha; `405` e `401`, não.

Respostas que **não** vêm da função, porque não trazem `X-Servico-Contrato`, como prazo estourado da
plataforma: trate como indisponível e não repita em laço **[código]** (a função sempre põe o cabeçalho).

## 7. Sem CORS

A função não devolve `Access-Control-Allow-Origin` em resposta nenhuma **[código]**. No sucesso real,
o cabeçalho veio ausente **[medido]**. Por causa do cabeçalho `x-servico-chave`, o navegador manda
antes uma pré-requisição `OPTIONS` **[documentação]**. Ela cai no `405` **[código]**, e o navegador
bloqueia a chamada **[documentação]**.

**Por quê:** o cliente é um servidor. Um navegador que chamasse direto precisaria ter a chave, e quem
tem a chave gasta a conta da OpenAI do projeto até o teto. Sem CORS, o erro de quem tentar isso aparece
no primeiro teste, e não depois de a chave vazar.

## 8. O que é registrado e o que nunca é

Uma linha em **`servicos.transcricao_uso`** por requisição que **passou da chave**, inclusive as
recusadas depois dela **[código + teste local]**. As colunas **[código]**:

| coluna | conteúdo |
|---|---|
| `id`, `timestamp` | gerados pelo banco |
| `projeto` | o da chave (`mari`) |
| `modelo` | `gpt-4o-transcribe` quando a chamada à OpenAI começou; nulo antes disso |
| `custo_usd` | calculado dos tokens (US$ 2,50 por milhão de entrada, US$ 10,00 por milhão de saída), ou por minuto (US$ 0,006) se a OpenAI informar duração em vez de tokens; 0 quando não houve chamada paga |
| `input_tokens`, `output_tokens`, `total_tokens` | os que a OpenAI informou |
| `bytes_audio` | tamanho do arquivo `audio` |
| `latencia_ms` | duração da chamada à OpenAI; nulo sem chamada |
| `codigo` | nulo no sucesso; senão, o `codigo` do erro |

Medido **[medido]**, nas três linhas da execução de 17:53:
- `413`: `modelo` nulo, `custo_usd = 0`, `bytes_audio = 4 194 305`;
- sucesso: `gpt-4o-transcribe`, US$ 0,00162, 320/82 tokens, 2182 ms, `codigo` nulo;
- `429`: `modelo` nulo, `custo_usd = 0`, `codigo = LIMITE_DIARIO`;
- nenhuma linha para os dois `401`.

O `custo_usd` do sucesso ficou gravado como `0.0016200000000000001`: resíduo de ponto flutuante,
desprezível na soma **[medido]**.

- **Nunca registrado:** o texto transcrito, o áudio, a chave. Também não há quem é a pessoa nem o
  endereço de origem **[código]**. As três colunas de texto (`projeto`, `modelo`, `codigo`) só aceitam
  identificadores, por `check` no banco **[código]**. O log da função guarda só o nome e o código do
  erro, sem texto, chave ou áudio **[código + teste local]**.
- Falha ao registrar **não** quebra a resposta: vai só para o log da função **[código + teste local]**.
- **Quem lê:** só o papel `service_role` (a própria função) e o dono do banco. `anon` e `authenticated`
  não têm acesso, e o schema `servicos` não é exposto na API de dados **[código]**. O projeto cliente
  **não** consulta o próprio consumo pelo serviço: pede a quem opera o Supabase.

## 9. Obrigações do cliente

São exigências deste contrato. A marca vai no fato que motiva cada uma.

1. **Chamar só do servidor, e nunca pôr a chave no front.** Quem tem a chave gasta a conta da OpenAI
   do projeto até o teto, e o serviço não distingue quem chamou **[código]**. Sem CORS, o navegador
   nem consegue **[código]**.
2. **Limitar por pessoa.** O teto é do projeto inteiro **[código]**. Sem limite por pessoa, uma só
   pessoa esgota o dia de todas, e o serviço não sabe quem é a pessoa **[código]**.
3. **Parar a gravação em 2 min.** A função não confere duração, só os 4 MB **[código]**. Os 2 min são
   o limite da `D-37`, e é o cliente que o garante.
4. **Descartar silêncio antes de enviar.** Áudio sem fala volta `200` com texto alucinado, não vazio
   nem erro. Está medido no núcleo pessoal ([`NUCLEO.md`, L6](NUCLEO.md#l6--áudio-sem-fala-confirmada--resultado-imprevisível-não-é-erro-nem-vazio))
   e vira obrigação do cliente pela `D-16`. Este serviço repassa o que a OpenAI devolve, sem filtro
   **[código]**. Além do lixo, o silêncio enviado **custa**.
5. **Não guardar o áudio.** O serviço não guarda **[código]**, e guardar fala de terceiros depende do
   comitê de ética (`D-37`).
6. **Não guardar o texto além do necessário para devolvê-lo à pessoa.** Mesmo motivo (`D-37`). O que a
   pessoa decidir enviar à Mari segue o caminho que já existia (`D-37`).
7. **Tratar `429`, `503` e prazo esgotado.** Siga a coluna "o que o cliente faz" da [tabela de
   erros](#6-erros). Ponha um prazo de cliente acima do da função: 120 s de OpenAI mais o resto
   **[código]**. O teste usa 170 s **[código]**, e a Edge Function tem teto de tempo próprio
   **[documentação — não medido]**. Nunca repita em laço: `429` só passa no dia seguinte, e repetir
   `504` pode cobrar duas vezes.

## 10. Riscos aceitos

- **Teto não atômico.** Chamadas simultâneas conferem o gasto ao mesmo tempo e passam juntas
  **[código]**. Na prática, o teto pode ser ultrapassado em até (chamadas simultâneas × custo de um áudio
  de até 4 MB). Com um limite por pessoa (obrigação 2), o estouro fica pequeno.
- **`TEMPO_ESGOTADO` registra custo 0, embora a OpenAI possa ter cobrado** **[código]**. Na prática, o
  gasto do dia fica subestimado nesse caso, e o teto é conferido contra um valor menor que o real.
- **Requisição sem chave faz a função ler o corpo inteiro** (Correção 1 da Etapa 2) **[código + teste
  local]**. Antes da correção, o `401` com ~1 MB de corpo travou no Supabase até a plataforma derrubar a
  requisição. Depois dela, voltou em 0,8 a 1,2 s **[medido]**. A causa não foi reproduzida localmente;
  o histórico está no `PROGRESSO.md`. Na prática, quem manda lixo sem chave ocupa a função pelo tempo
  de enviar o corpo, até o limite da plataforma. Não gera linha nem custo **[medido]** (os `401`).
- **Banco fora do ar derruba o serviço.** A consulta do gasto falha, e a função recusa com
  `503 LIMITE_INDISPONIVEL` em vez de transcrever sem saber o gasto **[código + teste local]**. Na
  prática, nenhuma transcrição até o banco voltar; é a falha fechada de um serviço público e pago.

## 11. Igual ao núcleo pessoal, e diferente

O núcleo pessoal é a Operação 1 do [`NUCLEO.md`](NUCLEO.md#operação-1-no-núcleo-remoto-contrato-2-2026-09-30-d-36).

**Igual:**
- a tradução das falhas da OpenAI em `FALHA_AUTENTICACAO`, `API_RECUSOU`, `SEM_CONEXAO` e
  `TEMPO_ESGOTADO`, com os mesmos status e o mesmo prazo de 120 s numa tentativa **[código]**. Muda só
  o segredo citado no `detail` (`OPENAI_API_KEY_MARI`);
- `405 METODO_NAO_PERMITIDO`, `422 REQUISICAO_INVALIDA`, `400 AUDIO_VAZIO`, `413 ARQUIVO_MUITO_GRANDE`,
  `500 ERRO_INTERNO` e o corpo `{"detail", "codigo"}` **[código]**;
- a alucinação em silêncio (L6) **[código]**: as duas funções repassam o que a API devolve;
- o cálculo de custo por tokens e a ausência de CORS **[código]**.

**Diferente:**

| | serviço | núcleo pessoal |
|---|---|---|
| autenticação | `x-servico-chave`, chave por projeto; `401 CHAVE_INVALIDA` | login (`Authorization: Bearer`); `401 NAO_AUTENTICADO` |
| modelo | fixo; `modelo` é ignorado | escolhível; modelo fora da lista → `422 MODELO_INVALIDO` |
| streaming | não há; `stream` é ignorado | `stream=true` devolve NDJSON |
| texto | **nunca guardado** | guardado em `assistente.transcricoes` |
| tamanho | 4 MB | 25 MB |
| teto diário | sim: `429 LIMITE_DIARIO`, `503 LIMITE_INDISPONIVEL` | não há |
| versão | `X-Servico-Contrato: 1` | `X-Nucleo-Contrato: 2` |

Coluna do serviço: **[código]**; coluna do núcleo pessoal: conforme o `NUCLEO.md`.

## 12. Como verificar

`nucleo-remoto/testes/testar_servico.cmd` (duplo clique no Windows). Ele pede a chave sem mostrá-la e
grava `testar_servico.log` ao lado, sem texto nem chave. Contra o serviço real, prova **[medido]**:
1. sem chave → `401 CHAVE_INVALIDA`;
2. chave errada → `401 CHAVE_INVALIDA`;
3. 4 MB + 1 byte → `413 ARQUIVO_MUITO_GRANDE`, sem custo;
4. `fala-real.wav` → `200`, `transcricao` não vazia, `X-Servico-Contrato: 1`, sem CORS (uma chamada
   paga, centavos);
5. teto `0` (o script pausa para criar `SERVICO_TETO_DIARIO_USD` e, no fim, pede para apagá-lo) →
   `429 LIMITE_DIARIO`.

As linhas no banco são conferidas à parte, por quem opera o Supabase. O teste **não** provoca contra o
serviço real `405`, `422`, `400`, os dois `503`, os `502`, o `504` nem o `500`. Esses só foram
exercitados localmente (entradas da Etapa 2 no `PROGRESSO.md`).
