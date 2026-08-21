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

Em vez de enviar um arquivo existente, também dá para gravar direto na página, na faixa de
controles "ou" abaixo do formulário de upload — clique único, usando o microfone padrão do
sistema (ou o escolhido no painel de configurações, veja abaixo). Essa faixa tem três posições
fixas, da esquerda para a direita, **próximas umas das outras** (coluna central de largura fixa
para o botão de gravar, ladeada por duas colunas simétricas): o botão **⋮ (mais opções)**, o
botão redondo de gravar **no centro** e, só durante a gravação, o botão **✕ de cancelar** logo à
direita dele. O botão de gravar **nunca muda de lugar** — o cancelar aparece/some numa coluna
reservada à parte, de largura fixa, então o centro não é empurrado.

1. Clique no botão redondo (ícone de microfone) — o navegador vai pedir permissão de acesso ao
   microfone (só na primeira vez) e a gravação começa imediatamente, usando o microfone padrão
   do sistema. O botão fica vermelho e pulsando enquanto grava, e o ícone dentro dele troca de
   microfone para um **quadrado**, sinalizando que o clique agora para a gravação (fora da
   gravação, volta ao microfone — veja também "Status da gravação" abaixo para o terceiro estado,
   o spinner). Um cronômetro em `mm:ss` aparece logo abaixo dele, contando o tempo decorrido a
   cada segundo.

   Abaixo do cronômetro aparece uma **faixa de barras com histórico**: cada barra é um instante
   do passado, não o volume "ao vivo" — a cada nova amostra a faixa inteira se desloca, a mais
   nova entra numa ponta e a mais antiga sai da outra, dando a sensação de continuidade de que a
   captação está viva. Com as **80 barras** atuais, amostradas a cada **60ms** (~16,7
   atualizações por segundo), a faixa representa **4,8 segundos** de histórico — rápido o
   bastante para não parecer em degraus.

   As barras são **espelhadas** (crescem do centro pra cima e pra baixo, como uma forma de onda),
   **finas** e com as pontas **totalmente arredondadas** — em repouso (silêncio), cada uma vira um
   pontinho/círculo no meio da faixa, o "pulso constante" que mostra que a captação está viva sem
   som nenhum. A altura usa uma **curva compressiva (raiz quadrada)** sobre o volume captado, em
   vez de proporcional direta: assim a fala de conversa normal usa a região **média/alta** da
   faixa, sem ficar espremida perto do centro, e só fala bem forte chega perto do topo (medido:
   silêncio abaixo de ~19%, fala normal por volta de ~39–76% nos trechos falados, fala forte perto
   de ~49–100% — ver PROGRESSO da tarefa de acabamento para os números completos). Em silêncio as
   barras ficam baixas mas continuam se deslocando — não travam. A largura de cada barra se ajusta
   à largura do painel (não é um valor fixo em pixels, só um teto para ficar fina de verdade),
   então a faixa sempre cabe sem transbordar nem quebrar linha, inclusive em tela estreita. A
   faixa começa limpa a cada gravação nova e some assim que a gravação para (ou se nunca chegou a
   gravar nada).
2. Enquanto grava, aparece também o botão **✕ (cancelar)**, à direita do botão de gravar. Cancelar
   descarta a gravação: no upload direto pelo microfone nenhuma requisição de transcrição sai; no
   modo tempo real (veja abaixo) a sessão encerra sem mandar o trecho ainda não comitado, então
   esse último pedaço falado não vira turno nem custo (o áudio já enviado antes do clique em
   cancelar já foi cobrado — cancelar não desfaz isso, só evita gerar cobrança nova a partir
   dali). **Em nenhum dos dois modos o cancelar toca na caixa "Transcrição por voz"** — nem apaga,
   nem soma nada, mesmo que um trecho já estivesse a caminho antes do clique. Depois de cancelar
   dá para gravar de novo normalmente. O botão some fora da gravação.
3. Clique de novo no botão redondo (agora quadrado) para parar normalmente. Se foi captado algum
   som relevante durante a gravação, ela é enviada automaticamente para transcrição (modelo ativo
   no alternador do topo da página) — não tem botão separado de "enviar". Enquanto a transcrição
   está a caminho, o botão vira um **spinner** (terceiro estado, ver "Status da gravação" abaixo)
   em vez de mostrar um texto de "Transcrevendo…". O cronômetro some assim que a gravação para.
4. O texto transcrito é **somado ao final** da caixa "Transcrição por voz" logo abaixo, sem
   apagar o que já estava lá — inclusive edições manuais. Grave quantas vezes quiser; cada
   gravação nova soma um parágrafo. A caixa de texto é editável a qualquer momento (sem rótulo
   visível acima dela — tem `aria-label` para leitor de tela).

Numa linha logo **abaixo** da caixa de texto (fora dela — não cobre o conteúdo, nem quando a
caixa está cheia) ficam dois botões só de ícone: à **esquerda**, o de apagar/desfazer (veja
"Apagar e desfazer" logo abaixo) e à **direita**, o de **"Copiar texto"** (`aria-label` e
`title` com esse nome), que copia o conteúdo atual da caixa para a área de transferência e
confirma com um balão (ver "Status da gravação" abaixo). Com a caixa vazia, o botão de copiar
não copia nada e mostra um aviso em vez de fingir que copiou.

### Status da gravação: balão efêmero + spinner no botão

As mensagens de status da gravação (erro, confirmação, "transcrevendo…") não ocupam mais espaço
fixo na página — aparecem como um **balão flutuante efêmero**, no mesmo estilo (`.toast`) já
usado pelo aviso "Não foi identificado nenhuma fala". Três tipos, com tempos diferentes:

- **Confirmação** (sucesso — "Transcrição adicionada ao texto abaixo.", "Texto copiado para a
  área de transferência.", "Gravação cancelada.", "Gravação em tempo real encerrada."): balão
  verde, some sozinho em **~2 segundos**.
- **Erro** (permissão negada, backend fora do ar, erro do modo tempo real, aviso do corte de
  2min30s, "nada para copiar"): balão vermelho, some em **~6 segundos** — mais tempo porque
  algumas dessas mensagens são longas.
- **Em andamento** (transcrevendo, ou aguardando o último turno do tempo real ao encerrar): **não
  vira balão** — em vez de texto, o **botão de gravar vira um spinner**, ficando desabilitado
  (sem o X de cancelar, já que o áudio já foi enviado e não há mais o que cancelar) até a ação
  terminar. É por isso que o botão tem três estados visuais: **microfone** (parado) → **quadrado**
  (gravando) → **spinner** (processando).

Uma mensagem nova sempre substitui a anterior na hora (nunca empilha nem entra em fila). O balão
usa `aria-live`, então continua sendo anunciado por leitor de tela mesmo desaparecendo sozinho.

### Apagar e desfazer

O botão à esquerda, na linha abaixo da caixa de texto, troca de ícone e de função conforme o
estado da caixa, não conforme quem a esvaziou:

- **Caixa com texto** → ícone de **lixeira**; clicar apaga tudo.
- **Caixa vazia, com algo apagado recentemente** → ícone de **desfazer** (seta curva); clicar
  devolve o texto inteiro, inclusive edições manuais feitas por cima do que veio de uma gravação.
- **Caixa vazia sem nada guardado ainda** (página recém-aberta): o botão fica **escondido** — sem
  fingir que há algo pra desfazer.

O desfazer funciona **não importa como a caixa esvaziou** — pela lixeira, apagando à mão,
segurando backspace, ou selecionando tudo (Ctrl+A) e apertando Delete. O "snapshot" usado pelo
desfazer só é gravado quando a caixa fica **ociosa** (sem mudança por ~0,8s) com texto — nunca a
cada tecla — para não perder o texto quando o usuário apaga tudo rápido demais (apagar com
backspace segurado dispara dezenas de eventos de mudança em sequência, mais rápido que o
intervalo de ociosidade; se o snapshot fosse gravado a cada tecla, o desfazer devolveria só o
último caractere antes do vazio). Escrever algo novo depois de esvaziar (digitando ou gravando de
novo) faz o botão voltar a ser lixeira; esvaziar de novo a partir daí desfaz para esse conteúdo
mais recente, não para o texto antigo.

**Corte de segurança (2min30s):** se a gravação continuar até atingir 2 minutos e 30 segundos
sem o usuário parar manualmente, ela é interrompida automaticamente — o mesmo caminho do clique
manual de parar — e, havendo som relevante captado, o áudio gravado até ali é enviado para
transcrição normalmente, sem precisar de nenhuma ação. Quando isso acontece, aparece um balão de
erro (~6s) explicando que a gravação foi cortada por segurança ao atingir o limite, e o botão
passa pelo estado de spinner enquanto a transcrição está a caminho. Esse limite é fixo (não
configurável) nesta versão.

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

Clique no botão **⋮** (mais opções), à esquerda do botão redondo de gravação, para abrir um
popup com dois itens — **Configurações** e **Consumo** (ver seção abaixo) — que agrupa os dois
ícones avançados que antes ficavam soltos na faixa de controles. O popup fecha clicando fora dele
ou com **Esc**, e cada item abre seu próprio painel (fechando o popup junto). Clique em
**Configurações**:

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
sucesso. Um evento `erro` mostra a mensagem no lugar correspondente (área `#resultado` no
upload; balão de erro em `#statusGravacaoRapida` na gravação — ver "Status da gravação" acima),
sem travar a interface em "carregando"; se a conexão cair no meio sem nenhum evento `final` nem
`erro` chegar, o frontend
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

No mesmo popup **⋮** (mais opções) descrito acima, clique em **Consumo** para abrir o painel:

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

1. **Zoom hora/minuto**: alterna a escala do eixo, tanto pelo botão quanto pela roda do mouse. As
     duas escalas mostram um recorte por vez (nunca o histórico inteiro de uma vez) — **hora** um
     dia, **minuto** uma janela de minutos — e trocar de escala preserva o período que você estava
     olhando (ver "As duas escalas concordam sobre o período" mais abaixo).
   - **Hora — um dia por vez** (correção aprovada em 2026-08-20; antes comprimia o histórico
     inteiro na largura do painel, que ficava ilegível com muitas requisições próximas). Mostra as
     24h de um único dia civil (meia-noite a meia-noite, hora local), com navegação para o **dia
     anterior/seguinte** logo acima do gráfico — mesmo padrão visual da navegação da escala
     "minuto" (um texto com o dia exibido + dois botões). Só é possível navegar dentro do
     **intervalo de dias que têm alguma requisição**: o botão da ponta correspondente fica
     desabilitado no primeiro/último dia com dado. Um dia sem nenhuma requisição (mas dentro desse
     intervalo, por exemplo um dia sem uso entre dois dias de uso) ainda é navegável — o painel
     mostra o aviso "Nenhuma requisição neste dia." em vez de um retângulo vazio sem explicação. O
     painel sempre abre no dia da requisição mais recente. Sem rótulo de preço acima dos pontos
     (ver acima).
   - **Minuto — janela móvel nas últimas 24h**: em vez de desenhar o histórico inteiro numa régua
     só (o que cresce sem limite — 30h de histórico a 10px/s já passavam de 1 milhão de pixels de
     largura), a escala "minuto" mostra um **recorte fixo de 3 minutos**, a 15px/s — duas
     requisições a poucos segundos de distância já ficam a dezenas de pixels uma da outra,
     distintas e clicáveis em separado. A largura do SVG é sempre a mesma (não depende de quanto
     `consumo.jsonl` já acumulou); o usuário desliza esse recorte dentro das **últimas 24 horas**,
     contadas a partir de uma âncora que normalmente é a requisição mais recente (não o relógio do
     computador — abrir o painel depois de dias sem uso não deixa a linha do tempo vazia; ver
     abaixo o que muda quando a âncora vem de uma troca de escala). Requisições fora dessas 24h não
     somem do painel: continuam na escala "hora" e nos números agregados (sessão e histórico
     diário) acima.
     - O painel sempre abre com a janela no **trecho mais recente**. Para deslizar: o **deslizador**
       abaixo do cabeçalho (arrasta livremente, ou `Home`/`End`/setas com o foco nele — jeito mais
       direto de pular para as pontas), ou os botões **"Início (24h atrás)"** / **"Mais recente"**
       (pulo direto para cada ponta, sem precisar acertar o arrasto). O texto acima do deslizador
       mostra o período exibido (janela atual e as 24h em volta).
     - Quando o recorte visível não tem nenhuma requisição, o painel avisa em texto ("Nenhuma
       requisição neste recorte…") em vez de mostrar um retângulo vazio sem explicação.
   - **As duas escalas concordam sobre o período exibido** (correção aprovada em 2026-08-20):
     trocar de escala não reinicia a navegação. Ao ir de "hora" (olhando o dia X) para "minuto", a
     janela de minutos reancora nas últimas 24h **terminando na última requisição do dia X** (ou na
     meia-noite seguinte, se esse dia não tiver nenhuma), então o recorte cai dentro do dia X — no
     caso comum de X ser hoje, isso reduz exatamente ao comportamento de sempre (âncora = a
     requisição mais recente de todo o histórico). Ao voltar de "minuto" para "hora", o dia
     exibido passa a ser o dia civil do **início** do recorte que estava visível. Cada escala só
     recalcula o próprio período do zero (âncora/dia mais recente) quando o painel é reaberto, ou
     na primeíssima vez que aquela escala é usada numa sessão do painel — a partir daí, tanto
     navegar dentro de uma escala quanto alternar entre elas preserva o que você escolheu.
   - **Botão "Zoom: Hora / Zoom: Minuto"**: alterna entre as duas escalas a cada clique; o texto
     do botão sempre reflete a escala atual, seja qual for a origem da troca (botão ou roda).
     Funciona em qualquer estado da linha do tempo (ver "ativação" abaixo) — é a saída garantida
     se a roda confundir.
   - **Roda do mouse sobre a linha do tempo — dois estados, sinalizados ao lado do botão de
     zoom**:
     - **Desativada** (estado inicial, ao abrir o painel): a roda **alterna a escala** hora/minuto
       (dois estados — rolar para um lado vai para "minuto", para o outro volta para "hora"), como
       sempre.
     - **Ativada** (só tem efeito na escala "minuto" — na "hora" o modo pode ser ativado do mesmo
       jeito, mas a roda fica sem efeito nenhum enquanto ativado, já que não há janela para
       deslizar dentro de um dia inteiro fixo; para trocar de escala nesse estado, use o botão de
       zoom ou desative primeiro com Esc/clique fora):
       a roda **desliza a janela móvel** dentro das 24h, em vez de trocar de escala — útil para
       ajuste fino sem tirar a mão do mouse (para pular direto às pontas, use o deslizador ou os
       botões, bem mais rápidos que girar a roda até o fim). Sensibilidade: cada "clique" de roda
       (deltaY = 100, o padrão normalizado por navegador) desliza a janela em **~6,7 segundos**;
       são **~27 cliques de roda** para atravessar o recorte de 3 minutos inteiro, e **~6** para
       percorrer uma tela cheia do painel (624px visíveis por vez, no tamanho de painel testado) —
       medido e considerado confortável, sem necessidade de ajuste (nem lento nem rápido demais na
       prática). Ativa com um clique em **qualquer lugar do container da linha do tempo** que não
       seja um ponto — área vazia, acima/abaixo do eixo, margens, o SVG inteiro; **pontos
       continuam abrindo o popup de transcrição** (ver abaixo), não ativam nem desativam nada. O
       estado ativado tem um contorno roxo no container e o texto ao lado do botão de zoom muda
       para "Roda: deslizando a janela". Desativa com **Esc** (sem fechar o painel de consumo — um
       segundo Esc, já desativado, é que fecha o painel, como antes) ou **clicando fora** da linha
       do tempo.
     Em ambos os estados, rolar o resto do painel de consumo (histórico diário, gráfico de barras)
     continua rolando a página normalmente, sem mexer na linha do tempo.
   - **Navegação horizontal fina dentro do recorte da escala "minuto"**: como a roda pura fica
     reservada para o zoom/deslizar (ver acima), role horizontalmente segurando **Shift** enquanto
     usa a roda (gesto nativo do navegador para rolagem horizontal) — ou arraste a barra de
     rolagem do container. **O recorte só abre já rolado até a requisição mais recente visível
     nele em alguns momentos específicos** (abrir o painel, trocar de escala, clicar em "Mais
     recente") — nos demais redesenhos, causados pelo próprio ato de deslizar (roda ativada ou
     arrastar o deslizador), o container abre pelo **início** do recorte novo (correção aprovada em
     2026-08-20: antes, esse scroll automático rodava em toda renderização, inclusive as
     disparadas por deslizar — cada giro da roda redesenhava e imediatamente puxava a rolagem de
     volta para o fim, dando a impressão de que rolar "pulava direto pro fim" em vez de deslizar).
     Como o recorte em si se desloca de forma equivalente ao gesto, o efeito visual passa a ser uma
     rolagem contínua no mesmo sentido a cada giro, nunca um salto.
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

1. Primeiro clique no botão redondo: o botão já vira **spinner** nesse instante (conectar também
   conta como "em andamento" — ver "Status da gravação" acima) enquanto o frontend busca um token
   de acesso em `GET /tempo-real/token` (ponte de autenticação — ver abaixo), pede o microfone
   (`getUserMedia`, mesmo dispositivo escolhido no painel de configurações) e abre uma conexão
   WebSocket **direto com a OpenAI** (não passa pelo backend). O áudio capturado é convertido
   para PCM16 mono 24kHz e enviado continuamente à API, a cada pedaço capturado.
2. Assim que a sessão abre, o botão fica vermelho e pulsando com o ícone de quadrado (mesmo
   indicador visual da gravação normal), o cronômetro, a faixa de barras com histórico e o botão
   ✕ de cancelar aparecem normalmente (ver seção "Gravação rápida pelo microfone" acima para o
   que cada um faz).
3. O texto vai sendo somado à caixa "Transcrição por voz" conforme os pedaços chegam da API —
   sem esperar o fim da gravação.
4. Segundo clique no botão redondo (parar, não cancelar): o botão vira spinner de novo enquanto
   comita o trecho que ainda não virou turno e aguarda a transcrição dele chegar; ao terminar,
   fecha a conexão, volta ao ícone de microfone e mostra o balão de confirmação "Gravação em
   tempo real encerrada." Não há upload nem chamada a `POST /transcrever` nesse modo — a
   transcrição inteira acontece via WebSocket.
5. Clicar em **✕ (cancelar)** em vez de parar: fecha a sessão na hora, **sem** mandar esse commit
   final — o trecho ainda não comitado não vira turno nem custo, e a caixa de transcrição não é
   tocada. Áudio de trechos anteriores já comitados (pelo timer periódico de 6s, ver abaixo) já
   foi cobrado pela API antes do cancelamento e continua cobrado — cancelar não desfaz o passado.
6. Se a conexão cair (token expirado, rede instável, erro da API) durante a gravação, um balão de
   erro aparece, a interface volta ao estado "parado" (ícone de microfone, sem travar), e o
   usuário pode clicar de novo para tentar reconectar ou desligar o alternador.

A transcrição de cada turno também é persistida em `transcricoes.jsonl` (ver seção "Registro de
transcrição" acima), junto do consumo (ver "Consumo no modo tempo real" abaixo).

**Corte de segurança (2min30s):** mesmo limite e mesmo espírito da gravação normal (ver acima) —
se a gravação ao vivo continuar até os 2min30s sem o usuário parar manualmente, ela para sozinha,
pelo **mesmo caminho** do clique manual de parar (não um atalho): o último turno em voo é aguardado
(botão em spinner) e registrado normalmente antes de fechar a conexão. Um balão de erro específico
do modo ao vivo aparece por ~6s antes do balão de confirmação "Gravação em tempo real encerrada."

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

**Fechamento sem perder turno em voo:** ao parar (manual, corte de segurança, ou depois de um
commit periódico disparado bem perto da hora de parar), a interface só fecha a conexão com a
OpenAI depois de aguardar — ou desistir, com um timeout de segurança de 5s — **qualquer** commit
ainda pendente, não só o commit final. Isso evita perder o texto e o custo do último trecho quando
a parada cai a poucos milissegundos de um commit periódico que ainda não recebeu o `completed`.

### Ponte de autenticação

`GET /tempo-real/token` gera e devolve um **token efêmero** (`client_secret`, formato `ek_...`,
válido por poucos minutos) que autoriza abrir uma sessão de transcrição ao vivo
(`gpt-live-transcribe`) direto entre o navegador e a OpenAI, via WebSocket — a chave real da API
nunca sai do backend. Resposta:

```json
{"client_secret": "ek_...", "expira_em": 1234567890, "modelo": "gpt-live-transcribe"}
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
- **Fechar um turno**: a sessão usa `turn_detection: null`, então o cliente precisa enviar
  `input_audio_buffer.commit` explicitamente para a API processar o áudio acumulado e disparar a
  transcrição — a doc não recomenda um intervalo específico de commit; o frontend usa um intervalo
  fixo de 6s (só comita se já houver pelo menos ~100ms de áudio no buffer, mínimo exigido pela
  API), calibrado testando com fala real.
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
   `POST /tempo-real/turno-concluido` com o `usage` daquele turno **e o `transcript` daquele mesmo
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
   válido e grava só o consumo, mantendo o contrato antigo do corpo da requisição (o nome da rota
   já reflete que ela registra o turno inteiro — consumo e texto — não só o consumo).
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
