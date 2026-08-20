# Assistente de Pesquisa por Áudio — MVP de transcrição

Motor mínimo de transcrição: recebe áudio, envia à API da OpenAI e devolve o texto
transcrito (áudio → API → transcrição).

## Como rodar o backend localmente

1. Copie `.env.example` para `.env` e preencha `OPENAI_API_KEY=` com sua chave da OpenAI.
2. Crie o ambiente virtual e instale as dependências (a partir da pasta `transcritor/`):

   ```powershell
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

3. Suba o servidor (porta 8000):

   ```powershell
   .venv\Scripts\uvicorn main:app --app-dir backend --port 8000
   ```

4. Teste o endpoint enviando um áudio (`.m4a`, `.wav` ou `.mp3`):

   ```powershell
   curl.exe -X POST http://127.0.0.1:8000/transcrever -F "audio=@caminho\do\arquivo.m4a"
   ```

   A resposta é um JSON no formato `{"transcricao": "..."}`. Erros (chave ausente/inválida,
   rede, arquivo inválido) voltam como JSON de erro com status 4xx/5xx, sem derrubar o servidor.

5. Opcional — escolha o modelo de transcrição com o campo `modelo` (padrão:
   `gpt-4o-transcribe`; aceitos: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`,
   `gpt-4o-transcribe-diarize`):

   ```powershell
   curl.exe -X POST http://127.0.0.1:8000/transcrever -F "audio=@caminho\do\arquivo.m4a" -F "modelo=gpt-4o-mini-transcribe"
   ```

   Um valor de modelo fora da lista é rejeitado com HTTP 422 antes de chamar a API.

## Como usar o frontend

Com o backend rodando (passo 3 acima), abra **<http://127.0.0.1:8000/>** no navegador — o
próprio backend serve a página, não precisa abrir nenhum arquivo à parte. Essa é a forma
recomendada: como é uma origem HTTP estável, o navegador lembra a permissão de microfone entre
recarregamentos da página.

> Abrir `frontend/index.html` direto (dois cliques, origem `file://`) ainda funciona para
> transcrever, mas o navegador trata cada carregamento como uma origem à parte — por isso ele
> pede a permissão de microfone de novo a cada vez, mesmo que você já tenha autorizado antes.
> Prefira `http://127.0.0.1:8000/` para não repetir essa permissão sempre.

Na página:

1. Escolha o modelo de transcrição no botão "Modelo de transcrição" no topo da página — cada
   clique alterna entre `gpt-4o-transcribe` (padrão) e `gpt-4o-mini-transcribe`; o nome do
   modelo ativo aparece no próprio botão. Esse alternador vale tanto para o upload de arquivo
   quanto para a gravação pelo microfone, abaixo.
2. Logo abaixo, o alternador **"Streaming do transcript"** ("Ligado"/"Desligado", desligado por
   padrão) também vale para os dois fluxos — veja a seção "Streaming do transcript" abaixo.
3. Logo abaixo desse, o alternador **"Transcrição em tempo real"** ("Ligado"/"Desligado",
   desligado por padrão) só vale para a gravação rápida (não afeta o upload de arquivo) — veja a
   seção "Transcrição em tempo real" abaixo.
4. Selecione um arquivo de áudio (`.m4a`, `.wav` ou `.mp3`).
5. Clique em **Transcrever** e aguarde — a transcrição (ou a mensagem de erro) aparece na
   própria página.

> O modelo `gpt-4o-transcribe-diarize` foi desativado desse alternador por decisão do usuário em
> 2026-08-18 (qualidade insatisfatória nos testes). O código continua no `frontend/index.html`,
> comentado, e pode ser reativado incluindo-o de volta na lista `MODELOS_ATIVOS` do script. O
> backend e o `benchmark.py` continuam aceitando os três modelos normalmente.

### Gravação rápida pelo microfone

Em vez de enviar um arquivo existente, também dá para gravar direto na página, no botão redondo
na seção "ou" abaixo do formulário de upload — clique único, usando o microfone padrão do
sistema (ou o escolhido no painel de configurações, veja abaixo):

1. Clique no botão redondo (ícone de microfone) — o navegador vai pedir permissão de acesso ao
   microfone (só na primeira vez) e a gravação começa imediatamente, usando o microfone padrão
   do sistema. O botão fica vermelho e pulsando enquanto grava, e um cronômetro em `mm:ss`
   aparece logo abaixo dele, contando o tempo decorrido a cada segundo. Um visualizador de barras
   também aparece logo abaixo, reagindo em tempo real ao volume captado pelo microfone — serve
   como feedback visual de que o som está sendo captado. As barras somem assim que a gravação
   para (ou se nunca chegou a gravar nada).
2. Clique de novo no mesmo botão para parar. Se foi captado algum som relevante durante a
   gravação, ela é enviada automaticamente para transcrição (modelo ativo no alternador do topo
   da página) — não tem botão separado de "enviar". Um texto de status abaixo do botão mostra
   "Transcrevendo…" e depois o resultado. O cronômetro some assim que a gravação para.
3. O texto transcrito é **somado ao final** da caixa "Transcrição por voz" logo abaixo, sem
   apagar o que já estava lá — inclusive edições manuais. Grave quantas vezes quiser; cada
   gravação nova soma um parágrafo. A caixa de texto é editável a qualquer momento.

**Corte de segurança (2min30s):** se a gravação continuar até atingir 2 minutos e 30 segundos
sem o usuário parar manualmente, ela é interrompida automaticamente — o mesmo caminho do clique
manual de parar — e, havendo som relevante captado, o áudio gravado até ali é enviado para
transcrição normalmente, sem precisar de nenhuma ação. Quando isso acontece, a área de status
mostra por alguns instantes um aviso explicando que a gravação foi cortada por segurança ao
atingir o limite, antes de mudar para "Transcrevendo…". Esse limite é fixo (não configurável)
nesta versão.

**Nenhuma fala detectada:** ao longo de toda a gravação, o volume captado pelo microfone é
acompanhado (mesma peça técnica das barras acima, o `AnalyserNode` da Web Audio API) e o maior
pico de volume observado é guardado. Se, ao parar (manualmente ou pelo corte de segurança), esse
pico ficou abaixo de um limiar mínimo de silêncio — ou seja, a gravação inteira ficou em silêncio
(ex.: clique sem querer, sem falar nada) — o áudio **não é enviado** para transcrição, e aparece
um aviso rápido (alguns segundos, sem bloquear a tela) dizendo "Não foi identificado nenhuma
fala". Isso evita mandar silêncio para a API, que às vezes "alucina" um texto em outro idioma em
vez de reconhecer que não havia fala. O limiar não filtra idioma, qualidade da fala ou ruído — só
distingue "teve som relevante" de "silêncio total"; está documentado (e ajustável, se necessário)
no código-fonte, na constante `LIMIAR_SILENCIO` do `frontend/index.html`.

Se a permissão de microfone for negada ou o navegador não suportar gravação, uma mensagem de
erro clara aparece perto do botão, sem apagar o texto já transcrito e sem quebrar o restante da
página (o upload de arquivo continua funcionando normalmente). O texto do transcript não é salvo
entre sessões — fechar ou recarregar a página apaga o que estiver ali.

### Escolher o microfone (configurações)

Ao lado do botão redondo de gravação tem um ícone de engrenagem — clique nele para abrir o
painel de configurações:

1. O painel lista os dispositivos de entrada de áudio disponíveis (inclui a opção "Padrão do
   navegador"). Os nomes reais dos microfones só aparecem depois que a permissão de microfone
   for concedida pela primeira vez — antes disso, ou se nenhum microfone for detectado, o painel
   mostra uma mensagem clara no lugar da lista.
2. Escolher um dispositivo na lista vale a partir da **próxima gravação** (não afeta uma
   gravação já em andamento). Sem escolha feita, ou voltando para "Padrão do navegador", a
   gravação usa o microfone padrão do sistema — comportamento de sempre.
3. Feche o painel clicando no **✕** ou clicando fora dele (na área escurecida) — fechar não
   cancela nada nem interrompe o resto da página.

## Streaming do transcript

Por padrão, o backend só devolve a transcrição depois que a API da OpenAI termina de processar o
áudio inteiro (resposta JSON única, como descrito acima). Ligando o alternador **"Streaming do
transcript"** no topo da página, o texto passa a aparecer **aos poucos**, conforme a API vai
gerando cada pedaço — tanto no upload de arquivo (área `#resultado`) quanto na gravação rápida
pelo microfone (caixa "Transcrição por voz"). O alternador é compartilhado entre os dois fluxos,
no mesmo padrão do alternador de modelo, e começa **desligado**.

### Formato da resposta em stream (backend)

Com o campo de formulário `stream=true` em `POST /transcrever`, o backend chama a API da OpenAI
com `stream=True` (confirmado empiricamente contra a API real, para `gpt-4o-transcribe` e
`gpt-4o-mini-transcribe`: a API emite vários eventos `transcript.text.delta` — cada um com um
pedaço de texto novo no campo `delta` — seguidos de um único evento final `transcript.text.done`,
com o texto completo no campo `text` e o `usage` no mesmo formato usado na resposta sem
streaming) e repassa isso ao cliente como uma resposta HTTP em streaming
(`StreamingResponse`, `Content-Type: application/x-ndjson`): **uma linha com um objeto JSON por
evento** (NDJSON), no formato:

```
{"tipo": "delta", "texto": "pedaço de texto"}
{"tipo": "delta", "texto": " mais um pedaço"}
{"tipo": "final", "texto": "texto completo da transcrição"}
```

Se a chamada à API da OpenAI falhar **durante** o streaming (autenticação, rede, ou a API
recusando o áudio), o backend não pode mais trocar o código de status HTTP (o `200` e os headers
já foram enviados assim que o streaming começou) — o erro aparece como mais uma linha do stream,
no formato `{"tipo": "erro", "detail": "mensagem legível"}`. Erros que acontecem **antes** de
começar o streaming (modelo inválido, chave ausente, arquivo vazio) continuam voltando como
resposta JSON de erro normal, com o status HTTP correto (422/503/400), igual ao fluxo sem
streaming.

### Comportamento no frontend

Com o alternador ligado, o JavaScript lê a resposta aos poucos (`response.body.getReader()`),
interpreta cada linha NDJSON e vai atualizando a área de transcrição a cada evento `delta`
recebido; ao chegar o evento `final`, o texto final substitui o acumulado (proteção contra
qualquer divergência entre a soma dos pedaços e o texto oficial da API) e o estado muda para
sucesso. Um evento `erro` mostra a mensagem na área de erro correspondente
(`#resultado` no upload, `#statusGravacaoRapida` na gravação), sem travar a interface em
"carregando"; se a conexão cair no meio sem nenhum evento `final` nem `erro` chegar, o frontend
mostra uma mensagem genérica de conexão interrompida pelo mesmo motivo. Na gravação rápida, o
texto que vai chegando é somado (aos poucos) ao final do que já estava na caixa antes dessa
gravação — mesmo comportamento cumulativo do modo sem streaming, só que visível em tempo real.

### Consumo no modo streaming

O registro de consumo (tokens/custo, ver seção abaixo) funciona igual nos dois modos: o backend
usa o `usage` do evento final (`transcript.text.done`) para calcular e persistir o custo, do
mesmo jeito que usa o `usage` da resposta única no modo sem streaming. Se, por algum motivo, o
evento final não trouxer `usage` recuperável, o backend registra essa limitação no log do
servidor e não grava um valor inventado — a transcrição em si não é afetada.

## Registro de consumo

Cada transcrição bem-sucedida (`POST /transcrever`) registra automaticamente uma linha em
`transcritor/consumo.jsonl` (um JSON por linha — timestamp, modelo, tokens de entrada/saída e
custo estimado em USD, calculado com os preços oficiais por token da OpenAI para
`gpt-4o-transcribe` e `gpt-4o-mini-transcribe`). Esse arquivo é local — está no `.gitignore`,
mesmo tratamento do `.env`, e não é versionado. Se o registro falhar por qualquer motivo, o erro
só é logado no console do servidor; a resposta da transcrição para o usuário não é afetada.

Para consultar o consumo agregado:

```powershell
curl.exe http://127.0.0.1:8000/consumo
```

A resposta traz três blocos:

- `sessao`: total acumulado desde que o backend foi ligado (contador em memória, reinicia a cada
  `uvicorn` novo);
- `por_dia`: total agregado por dia (`AAAA-MM-DD`), lido de `consumo.jsonl`, cobrindo todo o
  histórico salvo;
- `requisicoes`: uma linha por requisição registrada em `consumo.jsonl`, ordenada por
  `timestamp`, com `id`, `timestamp`, `modelo`, `custo_usd` e `texto` — usada pela linha do tempo
  do painel (seção abaixo). `texto` vem de `transcricoes.jsonl`, casado pelo campo `id_consumo`
  com o `id` de cada requisição; quando não há correspondência (registro anterior à existência do
  `id`, ou transcrição que falhou ao gravar), `texto` vem `null` — a requisição continua na
  lista, só sem texto.

```json
{"sessao": {"requisicoes": 3, "tokens": 491, "custo_usd": 0.00169},
 "por_dia": [{"data": "2026-08-18", "requisicoes": 3, "tokens": 491, "custo_usd": 0.00169}],
 "requisicoes": [
   {"id": null, "timestamp": "2026-08-17T10:00:00+00:00", "modelo": "gpt-4o-transcribe", "custo_usd": 0.0007, "texto": null},
   {"id": "a1b2c3...", "timestamp": "2026-08-18T21:28:47+00:00", "modelo": "gpt-4o-transcribe", "custo_usd": 0.00069, "texto": "..."}
 ]}
```

### Painel de consumo no frontend

Ao lado do ícone de configurações (engrenagem) tem um segundo ícone, de gráfico de barras —
clique nele para abrir o painel de consumo:

1. Ao abrir, o painel busca `GET /consumo` na hora e mostra o consumo da **sessão atual**
   (requisições, tokens e custo estimado em USD), o **histórico diário** (lista com data, tokens
   e custo de cada dia salvo em `consumo.jsonl`) e um **gráfico simples de barras** com o custo
   por dia. Os dados não ficam em cache nem são atualizados sozinhos — cada vez que o painel é
   aberto, ele busca de novo.
2. O botão **"Resetar sessão"** zera só a exibição da sessão atual nesta tela do navegador — ele
   não chama nenhum endpoint novo nem apaga ou altera `consumo.jsonl` no backend. Depois do
   reset, a sessão exibida volta a crescer a partir de zero conforme novas transcrições forem
   feitas; o histórico diário não é afetado pelo reset. O reset em si também não fica salvo em
   lugar nenhum — se a página for recarregada, a sessão volta a mostrar o total real do backend.
3. Se o backend estiver fora do ar ou a busca falhar, o painel mostra uma mensagem de erro no
   lugar dos dados, sem quebrar o resto da página.
4. Feche o painel clicando no **✕** ou clicando fora dele, igual ao painel de configurações.

### Linha do tempo das requisições

Abaixo do gráfico de barras, o painel de consumo desenha uma **linha do tempo**, em SVG puro
(sem biblioteca de gráfico) — um ponto por requisição de `requisicoes` (ver seção acima),
posicionado pelo horário no eixo. É a visualização pensada para o objetivo do projeto: comparar o
custo entre requisições próximas no tempo (por exemplo, o mesmo áudio mandado para dois modelos
diferentes, um logo após o outro) — por isso o **preço de cada requisição aparece escrito acima
do ponto na escala "minuto"** (onde os pontos ficam espaçados o bastante para o rótulo caber sem
colidir). Na escala "hora", com requisições muito mais próximas entre si, o rótulo some (evita
colisão/ruído visual); o preço continua acessível ali via o `title` do hover e pelo popup de
clique (ambos abaixo).

1. **Zoom hora/minuto**: alterna a escala do eixo, tanto pelo botão quanto pela roda do mouse.
   - **Hora**: a linha do tempo inteira (tudo que está em `requisicoes`) é comprimida na largura
     do painel — cabe sem precisar rolar, mas requisições muito próximas podem se sobrepor; sem
     rótulo de preço acima dos pontos (ver acima).
   - **Minuto**: escala fixa de pixels por segundo, então duas requisições feitas com poucos
     segundos de diferença aparecem como pontos distintos e clicáveis separadamente, cada um com
     o preço escrito acima. Como o painel mostra **tudo que existe** em `consumo.jsonl` (sem
     separar teste de uso real, nem filtrar por dia — decisão do projeto), essa escala pode ficar
     bem mais larga que o painel; ela abre com a rolagem já no fim (as requisições mais recentes),
     que é o caso de uso principal.
   - **Botão "Zoom: Hora / Zoom: Minuto"**: alterna entre as duas escalas a cada clique; o texto
     do botão sempre reflete a escala atual, seja qual for a origem da troca (botão ou roda).
   - **Roda do mouse sobre a linha do tempo**: também alterna a escala (dois estados — rolar para
     um lado vai para "minuto", para o outro volta para "hora"). Só funciona com o cursor sobre a
     linha do tempo; rolar o resto do painel de consumo (histórico diário, gráfico de barras)
     continua rolando a página normalmente, sem mexer no zoom.
   - **Navegação horizontal na escala "minuto"**: como a roda pura ficou reservada para o zoom,
     role horizontalmente segurando **Shift** enquanto usa a roda (gesto nativo do navegador para
     rolagem horizontal) — ou arraste a barra de rolagem do container.
2. **Clique num ponto** abre um popup com o modelo, o preço, o horário e o texto transcrito
   daquela requisição (lido de `transcricoes.jsonl` via o campo `texto` de `requisicoes`). Quando
   `texto` é `null` (registro anterior ao campo `id`, ou transcrição que falhou ao gravar), o
   popup mostra um aviso — "Não há transcrição guardada para esta requisição" — no lugar do
   texto, sem quebrar. Feche o popup pelo **✕**, clicando fora, ou Esc.
3. **Eixo do tempo**: os rótulos são sempre hora de relógio local (nunca "tempo decorrido desde o
   primeiro registro") e o passo entre marcas se ajusta ao intervalo exibido e à largura em
   pixels, mirando um rótulo a cada ~80–120px — uma escada de passos "redondos" (10s, 30s, 1min,
   5min, 15min, 30min, 1h, 3h, 6h, 12h, 1 dia), alinhados a fronteiras de tempo local legíveis
   (minuto/hora cheios), não a múltiplos crus de epoch. A precisão do rótulo acompanha o passo
   escolhido — `HH:MM:SS` quando o passo é menor que um minuto, `HH:MM` no nível de minuto, `HHh`
   no nível de hora ou mais grosso — para nunca repetir o mesmo texto em ticks vizinhos. Quando o
   intervalo exibido cruza a meia-noite, a **primeira marca de cada dia** traz a data junto
   (`dd/mm`, ex.: "19/08 00h"); fora dessas viradas a data não aparece, para não poluir o eixo
   quando tudo cabe num único dia.
3. Cada ponto tem um alvo de clique maior que o círculo desenhado (mais fácil de acertar) e um
   `title` nativo do SVG com um resumo (modelo, preço e horário), para o hover do mouse — vale nas
   duas escalas, inclusive na "hora" sem o rótulo de preço visível.

## Registro de transcrição

Além do consumo, cada transcrição bem-sucedida também grava o **texto** em
`transcritor/transcricoes.jsonl` (um JSON por linha), nos dois modos (upload em lote — com ou sem
streaming — e ao vivo). Cada linha tem, no mínimo:

```json
{"id_consumo": "a1b2c3...", "timestamp": "2026-08-19T12:00:00+00:00", "modelo": "gpt-4o-transcribe", "texto": "..."}
```

`id_consumo` liga essa linha ao registro correspondente em `consumo.jsonl` (mesmo campo `id` lá).
Esse arquivo é local — está no `.gitignore`, mesmo tratamento de `consumo.jsonl` e `.env`, e não é
versionado. Só o texto é persistido; o áudio nunca é guardado. Texto vazio (ou só espaço) não gera
linha. Mesma política de falha do registro de consumo: se a gravação falhar por qualquer motivo, o
erro só é logado no console do servidor — a resposta ao usuário (ou o stream, no modo streaming)
não é afetada. No modo em lote, a transcrição só é gravada quando o registro de consumo daquela
mesma requisição deu certo (evita linha órfã sem `id_consumo` correspondente).

## Transcrição em tempo real

Ligando o alternador **"Transcrição em tempo real"** no topo da página (desligado por padrão,
vale só para a gravação rápida — o upload de arquivo não é afetado), o botão redondo passa a
gravar e transcrever ao mesmo tempo: o texto vai aparecendo na caixa "Transcrição por voz"
**enquanto você ainda está falando**, em vez de esperar a gravação terminar. Funciona assim:

1. Primeiro clique no botão redondo: o frontend busca um token de acesso em
   `GET /tempo-real/token` (ponte de autenticação — ver abaixo), pede o microfone
   (`getUserMedia`, mesmo dispositivo escolhido no painel de configurações) e abre uma conexão
   WebSocket **direto com a OpenAI** (não passa pelo backend). O áudio capturado é convertido
   para PCM16 mono 24kHz e enviado continuamente à API, a cada pedaço capturado.
2. O botão fica vermelho e pulsando (mesmo indicador visual da gravação normal), o cronômetro e
   as barras de nível aparecem normalmente.
3. O texto vai sendo somado à caixa "Transcrição por voz" conforme os pedaços chegam da API —
   sem esperar o fim da gravação.
4. Segundo clique: para a captura, fecha a conexão e mostra "Gravação em tempo real encerrada."
   Não há upload nem chamada a `POST /transcrever` nesse modo — a transcrição inteira acontece
   via WebSocket.
5. Se a conexão cair (token expirado, rede instável, erro da API) durante a gravação, uma
   mensagem de erro aparece no lugar do status, a interface volta ao estado "parado" (sem
   travar), e o usuário pode clicar de novo para tentar reconectar ou desligar o alternador.

A transcrição de cada turno também é persistida em `transcricoes.jsonl` (ver seção "Registro de
transcrição" acima), junto do consumo (ver "Consumo no modo tempo real" abaixo).

### Controle de turno: "por tempo" ou "pela API" (Etapa 2)

Com o modo tempo real ligado, aparece um segundo alternador, **"Controle de turno"**, que decide
**quem fecha cada turno** — objetivo desta etapa é poder comparar os dois, não eleger um vencedor
(a escolha de padrão fica para depois, com dado na mão). Some da tela junto com o alternador de
tempo real (não faz sentido sem ele) e não pode ser trocado no meio de uma gravação em andamento.

- **"turnos por tempo (6s)"** (padrão, comportamento da Etapa 1, sem mudança): a sessão é aberta
  com `turn_detection: null` e o navegador manda `input_audio_buffer.commit` a cada 6s (calibrado
  testando com fala real) — é esse controle que corta palavra na emenda entre turnos, o problema
  que motivou esta etapa (ver exemplos no `PROXIMA_TAREFA.md`/`PROGRESSO.md` da Etapa 2).
- **"turnos pela API"**: a sessão é aberta com
  `turn_detection: {"type": "server_vad"}` — formato confirmado no guia de VAD da Realtime API
  (<https://developers.openai.com/api/docs/guides/realtime-vad>, consulta em 2026-08-20) — e é a
  própria API que detecta o fim da fala e fecha o turno; o navegador nunca manda
  `input_audio_buffer.commit` nesse modo.

  > **Bloqueio conhecido, confirmado contra a API real em 2026-08-20:** o modelo usado por este
  > projeto no modo ao vivo, `gpt-live-transcribe` (constante `MODELO_TEMPO_REAL` no backend), **não
  > aceita nenhum valor de `turn_detection` além de `null`** — a API recusa a criação da sessão com
  > `HTTP 400` e a mensagem `"Turn detection is not supported for this transcription model."`. Isso
  > foi confirmado testando `server_vad` e `semantic_vad` diretamente contra a API (script ad-hoc,
  > não commitado); os mesmos payloads funcionam normalmente com `gpt-4o-transcribe`,
  > `gpt-4o-mini-transcribe` e `whisper-1`. Ou seja: **"turnos pela API" está implementado (backend
  > e frontend) mas não funciona de verdade enquanto `MODELO_TEMPO_REAL` continuar sendo
  > `gpt-live-transcribe`** — clicar em gravar nesse modo mostra o erro "Não foi possível obter o
  > token do modo tempo real" ao tentar abrir a sessão. Trocar o modelo do modo ao vivo é uma
  > decisão maior que esta etapa não cobria (afeta custo e comportamento dos dois modos, não só
  > deste alternador) — fica para o PM decidir. Ver `PROGRESSO.md` da Etapa 2 para o log completo do
  > teste e as opções levantadas.

Os dois acoplamentos abaixo (gate de silêncio e fechamento) já levam em conta os dois modos, para
o dia em que esse bloqueio for resolvido:

- **Timer de commit periódico**: só roda no modo "por tempo". No modo "pela API" ele fica
  desligado — mandar commit por cima do `server_vad` tende a dar erro de buffer vazio ou turno
  duplicado.
- **Gate de silêncio contínuo** (ver "Silêncio contínuo" abaixo): só se aplica no modo "por tempo".
  No modo "pela API" o gate fica desligado — a detecção de fala do servidor precisa **receber** o
  silêncio para saber que a fala acabou; se o navegador parasse de mandar áudio depois do hangover,
  a API podia nunca fechar o turno. Efeito sobre o custo: nesse modo o áudio é enviado o tempo
  todo, inclusive as pausas — perde a otimização de custo desta seção (só silêncio sustentado deixa
  de ser enviado no modo "por tempo"), limitado apenas pelo corte de 150s e por o usuário parar
  manualmente.
- **Fechamento**: no modo "pela API" não há commit final para aguardar (quem fecha o turno é o
  servidor). Ao parar, o navegador para a captura local na hora e reaproveita o mesmo timeout de
  segurança de 5s do modo "por tempo" como prazo de tolerância — fecha assim que o `completed` do
  turno em andamento chegar, ou ao esgotar o prazo, o que vier primeiro. Sem isso a interface
  travaria esperando um evento que pode nunca chegar (por exemplo, se a sessão já estava em
  silêncio havia tempo quando o usuário clicou em parar).

**Corte de segurança (2min30s):** mesmo limite e mesmo espírito da gravação normal (ver acima) —
se a gravação ao vivo continuar até os 2min30s sem o usuário parar manualmente, ela para sozinha,
pelo **mesmo caminho** do clique manual de parar (não um atalho): o último turno em voo é aguardado
e registrado normalmente antes de fechar a conexão. A área de status mostra um aviso específico do
modo ao vivo por alguns instantes antes de voltar a "Gravação em tempo real encerrada."

**Silêncio contínuo — não paga por silêncio:** diferente da gravação normal, onde o silêncio só é
avaliado **uma vez, no fim** (decide se o arquivo inteiro é enviado ou não), no modo ao vivo o
áudio é transmitido continuamente enquanto a gravação está ligada — uma checagem só no fim não
evitaria gasto nenhum, porque o custo já teria acontecido antes de chegar lá. A checagem aqui é
**contínua**: a cada bloco de áudio capturado (~100ms), o volume é comparado ao mesmo
`LIMIAR_SILENCIO` da gravação normal; enquanto não houver som acima do limiar por mais de 2
segundos seguidos (hangover), o bloco simplesmente **não é enviado** à API — sem envio, não há
turno, não há `usage`, não há custo para aquele trecho. O hangover de 2s existe para não cortar
pausas curtas naturais entre frases (o problema de emenda que o modo ao vivo já tem); só silêncio
realmente sustentado deixa de ser enviado, e a fala normal (com pausas dentro do limite do
hangover) segue inteira, sem perder palavra. Se a sessão inteira transcorrer sem fala, o mesmo
aviso "Não foi identificado nenhuma fala" da gravação normal aparece ao parar.

**Fechamento sem perder turno em voo:** no modo "por tempo", ao parar (manual, corte de segurança,
ou depois de um commit periódico disparado bem perto da hora de parar), a interface só fecha a
conexão com a OpenAI depois de aguardar — ou desistir, com um timeout de segurança de 5s —
**qualquer** commit ainda pendente, não só o commit final. Isso evita perder o texto e o custo do
último trecho quando a parada cai a poucos milissegundos de um commit periódico que ainda não
recebeu o `completed`. No modo "pela API" o fechamento é diferente — ver "Controle de turno" acima.

### Ponte de autenticação

`GET /tempo-real/token` gera e devolve um **token efêmero** (`client_secret`, formato `ek_...`,
válido por poucos minutos) que autoriza abrir uma sessão de transcrição ao vivo
(`gpt-live-transcribe`) direto entre o navegador e a OpenAI, via WebSocket — a chave real da API
nunca sai do backend. Aceita o parâmetro de query opcional `modo_turno` (Etapa 2, ver "Controle de
turno" acima) — `tempo` (padrão) ou `api`; qualquer outro valor é rejeitado com HTTP 422. Resposta:

```json
{"client_secret": "ek_...", "expira_em": 1234567890, "modelo": "gpt-live-transcribe", "modo_turno": "tempo"}
```

O navegador usa esse token para abrir a conexão (confirmado empiricamente contra a API real):

```javascript
const ws = new WebSocket("wss://api.openai.com/v1/realtime", [
  "realtime",
  "openai-insecure-api-key." + clientSecret,
]);
```

### Formato dos eventos (cliente↔servidor)

Confirmado na documentação oficial da Realtime API
(<https://developers.openai.com/api/docs/guides/realtime-transcription>, consultada em
2026-08-19):

- **Envio de áudio**: evento `input_audio_buffer.append`, campo `audio` com um pedaço de PCM16
  mono 24kHz codificado em base64.
- **Fechar um turno**: depende do "Controle de turno" (Etapa 2, ver seção acima). No modo "por
  tempo" a sessão usa `turn_detection: null` e o cliente precisa enviar `input_audio_buffer.commit`
  explicitamente para a API processar o áudio acumulado e disparar a transcrição — a doc não
  recomenda um intervalo específico de commit; o frontend usa um intervalo fixo de 6s (só comita se
  já houver pelo menos ~100ms de áudio no buffer, mínimo exigido pela API), calibrado testando com
  fala real. No modo "pela API" a sessão usa `turn_detection: {"type": "server_vad"}` (formato
  confirmado no guia de VAD da Realtime API,
  <https://developers.openai.com/api/docs/guides/realtime-vad>, consulta em 2026-08-20) e é a
  própria API que fecha o turno — o cliente nunca manda `input_audio_buffer.commit` nesse modo
  (bloqueio conhecido com o modelo atual, ver seção "Controle de turno" acima).
- **Texto incremental**: `conversation.item.input_audio_transcription.delta`, campo `delta` —
  formato diferente do `transcript.text.delta` usado no streaming em lote (seção acima).
- **Texto final de cada turno**: `conversation.item.input_audio_transcription.completed`, campo
  `transcript` (mais o `usage` do turno, usado para registrar consumo — ver seção seguinte).

### Consumo no modo tempo real

Diferente do modo sem tempo real, aqui o navegador fala **direto** com a OpenAI (token efêmero) —
o backend nunca vê o áudio nem o resultado. Isso muda de onde vem o dado de consumo: o campo
`usage` de cada turno concluído chega no evento
`conversation.item.input_audio_transcription.completed`, **no navegador**, não no backend.
Confirmado na documentação oficial (API reference dos server events da Realtime API, consultada em
2026-08-19) que, para `gpt-live-transcribe` — modelo de ASR cobrado por duração —, esse `usage`
sempre vem no formato `{"type": "duration", "seconds": N}`.

Para registrar isso em `consumo.jsonl` (mesmo arquivo dos demais modelos), o frontend reporta esse
`usage` ao backend a cada turno concluído:

1. A cada evento `conversation.item.input_audio_transcription.completed`, o JavaScript envia
   `POST /consumo/tempo-real` com o `usage` daquele turno **e o `transcript` daquele mesmo
   turno** (não o transcript acumulado da tela) como corpo JSON, no campo opcional `texto` (por
   exemplo, `{"type": "duration", "seconds": 12.5, "texto": "o que foi dito neste turno"}`).
2. O backend valida o corpo (rejeita com HTTP 422 qualquer coisa que não seja `type: "duration"`
   com `seconds` não negativo, para não gravar lixo) e reaproveita `_calcular_custo_usd` /
   `_registrar_consumo` — as mesmas funções do modo sem tempo real — calculando o custo pelo preço
   por minuto de `gpt-live-transcribe` (US$ 0,017/min, conferido em
   <https://developers.openai.com/api/docs/pricing> em 2026-08-19) e gravando uma linha em
   `consumo.jsonl` com `modelo: "gpt-live-transcribe"` e `tipo_usage: "duration"`. Quando o corpo
   traz `texto`, o backend grava também uma linha em `transcricoes.jsonl` (ver "Registro de
   transcrição" acima), ligada pelo mesmo `id`. O campo `texto` é opcional — corpo sem ele continua
   válido e grava só o consumo, mantendo o contrato antigo da rota; a rota continua se chamando
   `/consumo/tempo-real` apesar de agora também persistir texto.
3. O envio é acessório: o `fetch` não é aguardado e qualquer falha é engolida em silêncio — se o
   backend estiver fora do ar, a transcrição na tela e a sessão de tempo real seguem normalmente,
   só aquele turno não é registrado (nem o consumo, nem o texto).

Esses registros aparecem no painel de consumo do frontend (seção "Painel de consumo no frontend"
abaixo) somados ao total do dia, junto dos demais modelos — o painel agrega por dia sem distinguir
modelo.

### Limitações desta etapa

- `AudioContext`/`ScriptProcessorNode` (não `AudioWorklet`) — escolha deliberada para manter o
  frontend em um único arquivo, sem módulo externo; funciona nos navegadores testados.

## Benchmark entre modelos

`transcritor/benchmark.py` processa o mesmo arquivo de áudio pelos três modelos suportados
(`gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize`), reaproveitando o
endpoint `POST /transcrever` do backend, e grava o comparativo (transcrição, tempo de resposta e
custo estimado) em `transcritor/BENCHMARK.md`.

1. Com o backend rodando (passo 3 em "Como rodar o backend localmente"), rode:

   ```powershell
   .venv\Scripts\python.exe benchmark.py caminho\do\audio.wav
   ```

   Use um áudio com fala real de 1 a 5 minutos. Arquivos `.wav` têm a duração calculada
   automaticamente; para outros formatos (`.m4a`, `.mp3`), informe a duração manualmente com
   `--duracao-segundos <n>`.

2. Veja o resultado comparativo em `transcritor/BENCHMARK.md` (sobrescrito a cada execução; use
   `--saida <arquivo>` para gravar em outro lugar).

O custo é estimado com base na duração do áudio e no preço público por minuto documentado pela
OpenAI em <https://platform.openai.com/docs/pricing> (preços podem mudar — a fonte e a data da
consulta ficam registradas no próprio `BENCHMARK.md`).
