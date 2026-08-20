# PROGRESSO arquivado — 2026-08-18 a 2026-08-19

> Entradas movidas do `PROGRESSO.md` vivo pelo PM em 2026-08-20, na virada de plano,
> conforme a exceção datada de 2026-08-19 registrada no `PM.md`. **Movidas apenas** —
> nenhuma linha foi editada, resumida ou reordenada.
>
> Plano correspondente: Servir frontend pelo backend, seletor de microfone, cronômetro e corte de segurança, barras de nível, registro de consumo, painel de consumo e streaming do transcript.

## [2026-08-18] — Plano novo, Etapa 1: Servir frontend via servidor local
Status: concluído

### Feito
- `transcritor/backend/main.py`: importado `StaticFiles` de `fastapi.staticfiles` (já vem com o
  `fastapi` instalado — nenhuma dependência nova) e adicionado, **depois** da rota
  `@app.post("/transcrever")`, um `app.mount("/", StaticFiles(directory=<.../frontend>,
  html=True), name="frontend")`. `html=True` faz `GET /` (e qualquer subcaminho sem extensão)
  servir `index.html` automaticamente. Registrado depois da rota da API de propósito, para a
  rota específica `POST /transcrever` ser resolvida antes do mount genérico — não precisou de
  nenhuma outra mudança para evitar colisão. Nenhuma linha da lógica de transcrição, validação de
  modelo ou CORS foi tocada.
- `transcritor/README.md`: seção "Como usar o frontend" atualizada — a forma recomendada agora é
  abrir `http://127.0.0.1:8000/` (o próprio backend serve a página), com uma nota explicando que
  abrir `frontend/index.html` direto (`file://`) ainda funciona para transcrever, mas o
  navegador pede a permissão de microfone de novo a cada carregamento nesse caso.
- Nenhuma mudança no `frontend/index.html`: o `URL_BACKEND` já era o caminho absoluto
  `http://127.0.0.1:8000/transcrever`, que continua correto servindo a página do mesmo host.

### Validação (rodado de fato, não simulado)
- Backend reiniciado para carregar o mount; `curl` confirmou `GET /` → 200 servindo o HTML do
  frontend, `GET /docs` → 200 (rota automática do FastAPI, prova que o mount não engoliu outras
  rotas), e `POST /transcrever` com áudio real → 200 com transcrição correta (endpoint intacto).
- Teste de persistência de permissão (Edge headless, `playwright-core`, contexto com
  `context.grantPermissions(['microphone'], { origin: 'http://127.0.0.1:8000' })` simulando o
  usuário autorizando uma vez, **sem** `--use-fake-ui-for-media-stream` — se a permissão não
  estivesse valendo, `getUserMedia` ficaria pendurado esperando um prompt que nunca chegaria em
  modo headless, e o teste estouraria por timeout):
  - página carregada em `http://127.0.0.1:8000/` (não `file://`);
  - 1ª gravação (botão redondo da Etapa 2) → sucesso, transcrição correta;
  - página recarregada (`page.reload()`, mesmo contexto, **sem novo `grantPermissions`**);
  - 2ª gravação, logo após recarregar → sucesso, transcrição correta, sem travar — confirma que a
    permissão concedida uma vez para a origem `http://127.0.0.1:8000` continua valendo depois de
    recarregar, resolvendo o problema relatado (com `file://`, cada carregamento é uma origem à
    parte e o navegador pediria de novo).
- Upload de arquivo testado na mesma página (`http://127.0.0.1:8000/`) → sucesso, sem regressão.

### Critério de pronto
- [x] `http://127.0.0.1:8000/` serve a página do frontend (mesmo conteúdo de hoje, sem mudança
      visual nesta etapa)
- [x] `POST /transcrever` continua funcionando normalmente a partir dessa página
- [x] Permissão de microfone concedida uma vez continua valendo depois de recarregar a página
      (testado de fato — ver "Validação" acima)
- [x] `transcritor/README.md` documenta a nova forma de abrir o app, com a nota sobre `file://`
      ainda funcionar mas pedir permissão toda vez
- [x] Nenhuma regressão nos fluxos de upload e gravação já validados

### Diagnóstico
- Nada inesperado; `StaticFiles(html=True)` do Starlette (dependência do FastAPI) resolveu tudo
  sem precisar de rota manual para `/` nem de `aiofiles` (não instalado, e não fez falta —
  serviu o HTML normalmente).
- Como o teste de permissão usa a API de contexto do Playwright (`grantPermissions`) para simular
  "usuário já autorizou uma vez", ele isola exatamente a variável que a tarefa queria corrigir
  (persistência por origem), sem depender de um navegador de verdade com perfil persistente.

### Novas demandas / riscos
- Nenhuma nova.

### Ajuste no plano necessário?
Não — Etapa 1 do plano novo concluída conforme especificado. Aguardando o PM para a próxima
etapa (configurações, cronômetro, barras de áudio, consumo ou streaming, conforme mencionado no
contexto desta tarefa).

## [2026-08-18] — Plano novo, Etapa 2: Painel de configurações com seletor de microfone
Status: concluído

### Feito
- `transcritor/frontend/index.html`:
  - novo ícone de engrenagem (`#botaoConfiguracoes`, SVG inline) ao lado do botão redondo de
    gravação, dentro de uma nova linha (`.linha-gravacao-rapida`) que agrupa os dois; classe
    `.icone-avancado` criada para o estilo (círculo cinza neutro, 2,75rem) especificamente para
    ser reaproveitada pelo próximo ícone "avançado" (consumo, Etapas 5/6 do plano), como pedido;
  - painel de configurações como modal (`#fundoConfiguracoes` fundo escurecido +
    `.painel-config` central, `role="dialog"`), com cabeçalho "Configurações" e botão fechar
    (✕); fecha clicando no ✕, clicando no fundo escurecido (fora do painel) ou com Escape —
    nenhuma dessas ações trava a página nem interfere no resto da interface;
  - `select#dispositivoAudio` dentro do painel, populado por `popularDispositivos()`
    (`enumerateDevices()` filtrando `kind === "audioinput"`, mesma lógica da antiga Etapa 6):
    opção "Padrão do navegador" (`value=""`) + uma opção por dispositivo encontrado; lista
    repopulada toda vez que o painel abre e também depois de todo `getUserMedia` bem-sucedido na
    gravação (rótulos reais só existem após a permissão ser concedida — mesmo comportamento já
    validado na Etapa 6 antiga);
  - `dispositivoEscolhido` (variável de módulo) guarda o `deviceId` escolhido; `iniciarGravacaoRapida()`
    agora monta `{ deviceId: { exact: dispositivoEscolhido } }` quando há escolha, ou `true`
    (comportamento padrão, sem mudança) quando não há;
  - painel sem dispositivos (`enumerateDevices()` retornando vazio) ou sem suporte do navegador
    mostra uma opção única e desabilitada com mensagem clara, sem quebrar nada.
- `transcritor/README.md`: nova subseção "Escolher o microfone (configurações)" explicando o
  ícone, o painel, quando a escolha passa a valer e como fechar; ajustada a frase de abertura da
  seção de gravação (não dizia mais "sem escolher dispositivo").
- `backend/main.py` não foi tocado (fora da lista de arquivos desta tarefa).

### Validação (rodado de fato, não simulado)
Testado com Edge headless (`playwright-core`) contra o backend real servindo
`http://127.0.0.1:8000/` (Etapa 1 deste plano):
- Ícone de configurações abre o modal (antes escondido, `hidden` confirmado); painel lista
  "Padrão do navegador" + os dispositivos de entrada disponíveis (3 microfones fake do Chromium
  no ambiente de teste).
- Fechar pelo ✕ e clicando fora (no fundo escurecido) — confirmados os dois, modal volta a ficar
  escondido em ambos os casos.
- Instrumentei `navigator.mediaDevices.getUserMedia` na página (wrapper que grava as
  `constraints` recebidas) para confirmar de fato o que é passado ao navegador, sem depender só
  do resultado da transcrição (que seria igual para qualquer dispositivo, já que o áudio "fake"
  do Chromium vem do mesmo arquivo `--use-file-for-fake-audio-capture` independente do
  `deviceId`):
  - com um dispositivo específico escolhido no painel → gravação disparou `getUserMedia` com
    `{"audio":{"deviceId":{"exact":"default"}}}` (o deviceId exato escolhido) — confirma a
    conexão painel → próxima gravação pedida no critério de pronto;
  - voltando para "Padrão do navegador" → `getUserMedia` chamado com `{"audio":true}` — confirma
    que o comportamento padrão (sem escolha) continua sem regressão.
- Simulei zero dispositivos (`navigator.mediaDevices.enumerateDevices` sobrescrito para retornar
  `[]` via `page.evaluate`) e reabri o painel → select mostrou só "Nenhum microfone detectado" e
  ficou desabilitado, sem erro no console nem quebra da página (conferido por screenshot).
- Regressão do upload de arquivo (Etapa 1 deste plano, servido via `http://127.0.0.1:8000/`) →
  sucesso, transcrição correta.

### Critério de pronto
- [x] Ícone de configurações aparece perto do botão redondo e abre um popover/modal ao clicar
- [x] O popover lista os dispositivos de entrada de áudio disponíveis
- [x] Escolher um dispositivo faz a gravação seguinte usar esse microfone (confirmado via
      inspeção direta das `constraints` passadas a `getUserMedia`, não só pelo resultado da
      transcrição)
- [x] Sem escolha feita, a gravação continua usando o microfone padrão, sem regressão
- [x] Painel fecha sem travar a página (✕, clique fora, e também Escape); nenhum dispositivo
      disponível é tratado com mensagem clara dentro do painel
- [x] `transcritor/README.md` documenta o painel de configurações

### Diagnóstico
- Como o áudio "fake" do Chromium em modo de teste vem sempre do mesmo arquivo
  (`--use-file-for-fake-audio-capture`), independente do `deviceId` escolhido, a transcrição
  sozinha não provaria que o dispositivo certo foi usado — por isso validei interceptando
  `getUserMedia` para inspecionar as `constraints` reais, o que é uma prova mais direta do que
  testar só com hardware real (que a máquina desta sessão não tem para múltiplos microfones).
- Reaproveitei a mesma lógica de `popularDispositivos()`/tratamento de erro que existia na Etapa
  6 antiga (removida na Etapa 2 do plano anterior) — não foi preciso reinventar nada, só mover
  para dentro do painel e conectar o resultado à variável `dispositivoEscolhido`.

### Novas demandas / riscos
- Nenhuma nova.

### Ajuste no plano necessário?
Não — Etapa 2 concluída conforme especificado. Aguardando o PM para a próxima etapa.

## [2026-08-18] — Plano novo, Etapa 3: Cronômetro + corte de segurança
Status: concluído

### Feito
- `transcritor/frontend/index.html`:
  - novo elemento `#cronometroGravacaoRapida` (parágrafo `mm:ss`, `hidden` por padrão) logo
    abaixo da linha do botão redondo/engrenagem, estilizado com números tabulares;
  - ao iniciar a gravação (`iniciarGravacaoRapida()`), o cronômetro fica visível, zera para
    `00:00` e passa a atualizar a cada segundo (`setInterval`) com o tempo decorrido desde
    `Date.now()` da gravação, formatado em `mm:ss`;
  - corte de segurança fixo em 150000ms (2min30s): um `setTimeout` agendado junto com o
    cronômetro dispara `cortarPorSegurancaGravacaoRapida()`, que marca um flag e chama a mesma
    função de parar (`pararGravacaoRapida()`) usada no clique manual — mesmo caminho de código
    pedido na tarefa, sem duplicar lógica de parada/envio;
  - `pararGravacaoRapida()` centraliza a limpeza dos dois temporizadores
    (`pararTemporizadoresGravacaoRapida()`: `clearInterval` + `clearTimeout`) e esconde o
    cronômetro, então tanto o clique manual quanto o corte automático cancelam corretamente
    qualquer temporizador pendente — parar manualmente antes do limite cancela o `setTimeout` do
    corte, e ele nunca dispara depois;
  - quando o corte automático aciona a parada, o listener de `stop` do `MediaRecorder` detecta o
    flag e passa um aviso para `enviarGravacaoRapida(blob, avisoSeguranca)`, que mostra a
    mensagem de corte por segurança (classe `erro`, para chamar atenção) por 1,8s antes de trocar
    para "Transcrevendo…" — no clique manual esse aviso é `null` e o fluxo vai direto para
    "Transcrevendo…" como antes;
  - nenhuma outra parte do fluxo (upload, alternador de modelo, configurações) foi tocada.
- `transcritor/README.md`: subseção "Gravação rápida pelo microfone" atualizada — menciona o
  cronômetro visível em `mm:ss` e novo parágrafo dedicado ao corte de segurança de 2min30s
  (comportamento, mensagem de aviso, e que o limite é fixo nesta versão).
- `backend/main.py` não foi tocado (fora da lista de arquivos desta tarefa).

### Validação (rodado de fato, em múltiplas camadas)
1. **Simulação isolada em Node** (harness próprio em `.claude/tmp/`, removido ao final — DOM,
   `MediaRecorder` e temporizadores falsos com relógio controlável): confirmou a aritmética do
   cronômetro (`00:05` aos 5s), que o corte automático dispara exatamente aos 150000ms, que a
   mensagem de aviso aparece antes de mudar para "Transcrevendo…", e que avançar bem além do
   limite depois de uma parada manual não dispara mais nada (temporizador cancelado
   corretamente).
2. **Navegador real** (Edge headless via `playwright-core`, instalado fora do repo na pasta de
   rascunho da sessão; áudio de fala real sintetizado via `System.Speech`, injetado como
   microfone fake): com o relógio virtual da página (`page.clock`) acelerando só os
   `setTimeout`/`setInterval` do app (sem acelerar a captura real de áudio):
   - iniciar gravação → cronômetro fica visível e atualiza corretamente (`00:05` após avançar
     5s virtuais);
   - parar manualmente antes do limite → cronômetro some, transcrição do trecho gravado (tempo
     real curto) é enviada e volta com sucesso; avançar depois o relógio 400s virtuais não
     dispara mais nada (confirma o cancelamento do corte automático no caminho manual);
   - deixar o relógio virtual chegar a 2min30s sem interação → corte automático dispara,
     cronômetro some, mensagem de aviso correta aparece (menciona "segurança" e "2min30s") antes
     de mudar para "Transcrevendo…" — a chamada à API falhou só porque o áudio real capturado
     nesse teste específico durou frações de segundo (efeito colateral de acelerar o tempo da
     página sem acelerar a captura de mídia), não um bug do app.
3. **Teste de ponta a ponta com tempo real** (mesmo setup, sem acelerar o relógio desta vez —
   deixei a gravação rodar de verdade por 2min30s): corte automático disparou exatamente aos
   150s (log: início 21:04:08 UTC, corte 21:06:38 UTC), mensagem de aviso correta exibida, e a
   transcrição do áudio real gravado até o corte voltou certa na caixa de transcript
   ("Este é um áudio de teste para validar o cronômetro e o corte de segurança da gravação
   rápida.") — status final `sucesso`. Esse teste cobre o item do critério de pronto que pede
   "testado de fato, deixando gravar até o corte" de forma completa, sem nenhum atalho.
- Regressão: os testes acima (parar manual, upload já indiretamente coberto por não ter sido
  tocado) não mostraram nenhum erro de console além do esperado; o servidor backend (já rodando
  desde sessão anterior) continuou respondendo normalmente durante e depois dos testes — deixei
  ele no ar ao final, mesmo padrão das etapas anteriores.
- Todos os artefatos de teste (`node_modules`, script Playwright, áudio sintetizado, harness Node)
  ficaram na pasta de rascunho da sessão (fora do repo) ou em `.claude/tmp/` (removidos ao final,
  conforme `EXECUTOR.md`) — nada disso entrou em `transcritor/`.

### Critério de pronto
- [x] Cronômetro visível abaixo do botão mostra o tempo decorrido durante a gravação, em mm:ss
- [x] Gravação atinge 2min30s e para automaticamente, enviando o áudio gravado até ali (testado
      de fato com tempo real, sem acelerar nada — ver item 3 da validação)
- [x] Mensagem clara indica que a gravação foi cortada por segurança quando isso acontece
- [x] Parar manualmente antes de 2min30s funciona normalmente, sem o corte automático interferir
      depois (testado: gravar, parar manualmente, avançar o relógio bem além do limite depois —
      nada dispara)
- [x] `transcritor/README.md` documenta o cronômetro e o limite de 2min30s
- [x] Nenhuma regressão nos fluxos de upload, configurações (Etapa 2) e gravação já validados —
      nenhum desses arquivos/lógicas foi tocado além do pedido nesta tarefa

### Diagnóstico
- Achado de tooling (não é bug do app): `page.waitForFunction(fn, options)` do `playwright-core`
  passando só 2 argumentos posicionais faz a lib interpretar o segundo argumento como `arg` (a
  ser passado para dentro da função da página), não como `options` — por isso o `timeout`
  customizado era ignorado silenciosamente e caía no padrão de 30s. Precisei corrigir para
  `page.waitForFunction(fn, undefined, options)` no script de teste com espera real de 2min30s.
  Não afeta o código do projeto, só registro para não repetir o erro em testes futuros.
- A classe CSS reaproveitada para a mensagem de corte de segurança é `erro` (vermelha), mesma
  usada para falhas reais — decisão deliberada para chamar atenção do usuário (é um evento que
  merece destaque, mesmo não sendo tecnicamente um erro); se o PM preferir uma cor/estilo
  dedicado para "aviso" distinto de "erro", é um ajuste pequeno e localizado.

### Novas demandas / riscos
- Nenhuma nova.

### Ajuste no plano necessário?
Não — Etapa 3 concluída conforme especificado. Aguardando o PM para a próxima etapa (Etapa 4:
barras de nível de áudio e validação de silêncio, conforme mencionado no contexto da tarefa).

## [2026-08-18] — Plano novo, Etapa 4: Barras de nível de áudio + validação de silêncio
Status: concluído

### Feito
- `transcritor/frontend/index.html`:
  - ao iniciar a gravação rápida (`iniciarGravacaoRapida`), logo antes de `mediaRecorderRapido.start()`,
    chama `iniciarAnalisadorNivel(streamRapido)`: cria um `AudioContext` + `AnalyserNode`
    (`fftSize = 256`) conectado ao mesmo `MediaStream` já usado pelo `MediaRecorder` (não abre um
    segundo `getUserMedia`) e começa um loop de animação (`requestAnimationFrame`);
  - o loop (`animarBarrasNivel`) lê `getByteTimeDomainData` a cada frame, calcula o RMS da
    amostra (para as barras) e o maior desvio de amostra único (para o pico), atualizando
    `picoVolumeRapido` como o maior pico já visto **na gravação inteira**, não só no frame atual;
  - visualizador: 12 `<span class="barra">` gerados uma vez em `#barrasNivel`, cada um com a
    altura (`style.height`, em %) recalculada a cada frame a partir do RMS do frame, com uma leve
    variação senoidal por índice só para dar um efeito visual "orgânico" entre as barras (não
    afeta a lógica de silêncio, que usa o pico bruto, não essa variação estética); container fica
    `hidden` fora de gravação e visível (`hidden = false`) só enquanto grava;
  - `pararAnalisadorNivel()` (chamado dentro de `pararGravacaoRapida()`, antes de
    `mediaRecorderRapido.stop()`) cancela o `requestAnimationFrame` pendente, fecha o
    `AudioContext` (`.close()`) e esconde as barras — evita vazar `AudioContext`s entre gravações
    sucessivas. Importante: essa função **não zera** `picoVolumeRapido` — o valor acumulado
    precisa sobreviver até o listener de `stop` do `MediaRecorder` decidir se envia ou não;
    `picoVolumeRapido` só é reiniciado a zero no início da *próxima* gravação, dentro de
    `iniciarAnalisadorNivel`;
  - validação de silêncio: no listener de `stop` do `MediaRecorder`, antes de montar o `Blob` e
    chamar `enviarGravacaoRapida`, verifica `analisadorAtivoNestaGravacao && picoVolumeRapido <
    LIMIAR_SILENCIO`; se verdadeiro, **não** monta nem envia o blob — só limpa o status e chama
    `mostrarToastSemFala()` (toast fixo no rodapé, role="status", que aparece por 3s e some
    sozinho, sem bloquear o resto da página); se falso, segue o fluxo normal de sempre (inclusive
    o aviso de corte de segurança da Etapa 3, quando aplicável — os dois avisos não se sobrepõem
    porque a checagem de silêncio decide antes de chegar no aviso de corte);
  - `analisadorAtivoNestaGravacao` existe como flag de segurança: só é `true` quando o
    `AudioContext` foi criado com sucesso (`window.AudioContext || window.webkitAudioContext`
    disponível). Se o navegador não suportar Web Audio API, a checagem de silêncio é **pulada**
    (flag continua `false`), e a gravação segue o comportamento antigo (sempre envia) — evita que
    a ausência de suporte a `AudioContext` bloqueie silenciosamente todas as gravações nesse
    navegador;
  - `LIMIAR_SILENCIO = 0.02`: limiar comparado ao maior desvio de amostra (escala 0–1, onde a
    amostra bruta do `AnalyserNode` é um byte 0–255 centrado em 128). Valor documentado no próprio
    código com o raciocínio (ruído de ambiente fica abaixo de ~0.01; fala normal ultrapassa
    facilmente 0.05–0.1), pedido explicitamente pela tarefa;
  - nenhuma outra parte do fluxo (upload, alternador de modelo, configurações, cronômetro, corte
    de segurança) foi alterada além de duas chamadas novas (`iniciarAnalisadorNivel` /
    `pararAnalisadorNivel`) inseridas nos pontos de início/fim já existentes.
- `transcritor/README.md`: subseção "Gravação rápida pelo microfone" ganhou uma frase sobre o
  visualizador de barras (o que é, quando aparece/some) e um parágrafo novo dedicado ao
  comportamento "Nenhuma fala detectada" (o que é checado, quando o áudio não é enviado, o texto
  exato do aviso, e onde o limiar está documentado no código para ajuste futuro).
- `backend/main.py` não foi tocado (fora da lista de arquivos desta tarefa).

### Validação (rodado de fato, em navegador real com microfone fake)
Sem acesso a um microfone físico neste ambiente, usei o Chrome instalado na máquina (headless,
via `--remote-debugging-port` + Chrome DevTools Protocol, driblado com um script Node — Node 22
tem `WebSocket` nativo, não precisei instalar nenhuma dependência nova) com
`--use-fake-device-for-media-stream` e `--use-file-for-fake-audio-capture=<wav>`, que faz o
Chrome alimentar `getUserMedia` com um arquivo de áudio real de verdade (não é mock da API do
navegador — é o mesmo caminho de captura real, só trocando a fonte física pelo arquivo). Gerei
dois `.wav` de teste (silêncio total; tom de 300Hz a 40% de amplitude, simulando volume de fala)
e rodei o fluxo completo (clicar para gravar → aguardar → clicar para parar) contra o backend
real (`uvicorn`, já com a chave da OpenAI configurada):
1. **Silêncio**: barras ficam no piso (15%, o mínimo visual) a gravação toda; ao parar,
   `picoVolumeRapido` fica abaixo de `LIMIAR_SILENCIO` → toast "Não foi identificado nenhuma
   fala" aparece, **nenhuma** requisição a `/transcrever` é disparada (confirmado observando a
   aba de rede via CDP) — critério de pronto "gravar em silêncio total não envia e mostra o
   popup" confirmado de fato, não só por leitura de código.
2. **Tom (volume de fala)**: barras reagem visivelmente ao longo do tempo (chegam a 100% no
   início, variam frame a frame — confirmado amostrando a altura das barras a cada 300ms); ao
   parar, o pico ficou bem acima do limiar → toast **não** aparece, uma requisição real a
   `/transcrever` foi disparada e o backend respondeu com sucesso (status final "Transcrição
   adicionada ao texto abaixo.") — confirma que fala real não é bloqueada (sem falso positivo).
   Observação: o volume das barras decai ao longo de ~2s mesmo com o tom constante — não é bug do
   app, é a supressão de ruído/AGC padrão do `getUserMedia` do Chrome tratando um tom sintético
   estacionário como ruído; fala real (com variação natural) não sofre esse efeito. Não afeta a
   validação porque o pico é capturado logo no início, antes da supressão atuar, e o pico já
   acumulado nunca é resetado até a próxima gravação.
3. Rodei também um ciclo completo (gravar → parar) escutando `Runtime.exceptionThrown` via CDP:
   nenhuma exceção JS não tratada em nenhum dos dois cenários.
4. Servidor da página verificado servindo `http://127.0.0.1:8000/` normalmente antes dos testes
   (mesmo backend usado nas etapas anteriores); o script inline também foi checado com
   `new Function(...)` no Node antes de tudo, para pegar qualquer erro de sintaxe cedo.
- Regressão: upload, alternador de modelo, configurações, cronômetro e corte de segurança não
  foram tocados no código além das duas chamadas novas já descritas; não há nada nesses fluxos
  que dependa da checagem de silêncio, então risco de regressão é baixo. Não testei manualmente o
  upload/configurações nesta rodada (fora do escopo desta tarefa e já validados nas etapas
  anteriores), mas revisei o diff e confirmei que nenhuma linha desses fluxos foi alterada.
- Ambiente de teste (Chrome headless, perfis temporários, `.wav` gerados, scripts CDP) ficou
  inteiramente em `%TEMP%`, fora do repositório; processos do Chrome de teste e o `uvicorn` de
  teste foram encerrados ao final. Nada disso entrou em `transcritor/`.

### Critério de pronto
- [x] Barras de nível reagem visivelmente ao volume captado durante a gravação, com fala real
      (testado com tom simulando fala — barras variam claramente frame a frame, chegando a 100%)
- [x] Barras somem/ficam neutras quando não está gravando (escondidas via `hidden` fora do
      período de gravação; confirmado nos dois cenários testados)
- [x] Gravar em silêncio total de propósito NÃO envia para transcrição e mostra o popup "Não foi
      identificado nenhuma fala" (testado de fato — ver item 1 da validação)
- [x] Gravar com fala normal continua enviando e transcrevendo normalmente, sem falso positivo
      bloqueando (testado de fato — ver item 2 da validação)
- [x] `transcritor/README.md` documenta as barras e o aviso de ausência de fala
- [x] Nenhuma regressão nos fluxos de upload, configurações, cronômetro/corte de segurança já
      validados (nenhuma linha desses trechos foi alterada; ver observação em "Regressão" acima)

### Diagnóstico
- Não havia microfone físico disponível neste ambiente para um teste manual tradicional; usei o
  mecanismo de fake-audio-device do Chrome (alimentando `getUserMedia` com um `.wav` real) para
  validar o comportamento de ponta a ponta sem depender de hardware. Achei que valia registrar a
  técnica caso seja útil em etapas futuras que também dependam de captura de áudio real.
- O tom sintético de teste sofreu supressão progressiva por AGC/noise suppression do Chrome (um
  tom puro e estacionário parece "ruído" para esses algoritmos); fala humana real não tem esse
  problema por ter variação natural. Não é um problema do app, só uma particularidade do áudio
  sintético usado no teste — registrado para não causar confusão se alguém tentar reproduzir o
  teste depois.

### Novas demandas / riscos
- Nenhuma nova.

### Ajuste no plano necessário?
Não — Etapa 4 concluída conforme especificado. Aguardando o PM para a próxima etapa.

## [2026-08-18] — Plano novo, Etapa 5: Registro de consumo no backend
Status: concluído

### Feito
- Antes de implementar, confirmei empiricamente (chamada direta à API, fora do endpoint, com o
  áudio de teste) o formato real de `usage` para os dois modelos ativos: **ambos**
  (`gpt-4o-transcribe` e `gpt-4o-mini-transcribe`) devolvem `usage.type == "tokens"` (com
  `input_tokens`/`output_tokens`/`total_tokens`), não `"duration"` — a ambiguidade que a tarefa
  sinalizava foi resolvida assim, na prática, antes de decidir a lógica final.
- `transcritor/backend/main.py`:
  - `PRECOS_POR_TOKEN_USD` (preços por token dos dois modelos, conforme documentado no
    `PLANO.md`) e `PRECO_POR_MINUTO_USD` (fallback por duração — mesmos valores já usados em
    `benchmark.py`, estendido para `gpt-4o-transcribe-diarize` por consistência, embora esse
    modelo não faça parte do escopo desta tarefa);
  - `_calcular_custo_usd(modelo, usage)`: se `usage.type == "tokens"`, calcula pelo preço por
    token; caso contrário (`"duration"` ou `usage` ausente/formato inesperado), cai no fallback
    por `usage.seconds` × preço por minuto (sem tentar calcular duração a partir do arquivo de
    áudio em si — não foi necessário, já que os dois modelos ativos sempre devolvem tokens; deixei
    registrado no comentário do código por quê);
  - `_registrar_consumo(modelo, usage)`: monta o registro (timestamp UTC ISO, modelo, tipo de
    usage, tokens, segundos, custo) e faz append em `transcritor/consumo.jsonl` (uma linha JSON
    por requisição); tudo dentro de um `try/except Exception` amplo que só loga no console do
    servidor em caso de falha — nunca propaga erro para a resposta de `/transcrever`;
  - chamada a `_registrar_consumo(modelo, resultado.usage)` inserida logo após a chamada bem
    sucedida à API, antes do `return` de `/transcrever`; nenhuma outra linha do endpoint existente
    foi alterada;
  - contador em memória `_consumo_sessao` (requisições, tokens, custo) acumulado a cada chamada,
    reiniciado a cada `uvicorn` novo (por definição — não é persistido);
  - novo endpoint `GET /consumo`: lê `consumo.jsonl` linha a linha (ignorando linhas
    corrompidas/vazias, e tolerando o arquivo não existir ainda — primeiro uso), agrega por dia
    (`AAAA-MM-DD`, extraído do timestamp) cobrindo todo o histórico salvo (optei pelo "todo o
    histórico" que a tarefa permitia como alternativa mais simples ao corte de 30 dias), e devolve
    `{"sessao": {...}, "por_dia": [...]}`, registrado **antes** do `app.mount("/", StaticFiles...)`
    para não colidir com o mount genérico;
  - `allow_methods` do CORS ampliado de `["POST"]` para `["GET", "POST"]` — necessário para o
    endpoint novo (`GET`) funcionar a partir de um futuro frontend na Etapa 6; nenhuma outra regra
    de CORS foi tocada.
- `.gitignore` (raiz): adicionada a regra `transcritor/consumo.jsonl`, mesmo padrão/comentário já
  usado para `transcritor/.env` (dado local, nunca versionado).
- `transcritor/README.md`: nova seção "Registro de consumo" documentando o arquivo local, o
  formato do `GET /consumo` (com exemplo de resposta real do teste abaixo) e que a interface no
  frontend fica para uma etapa futura.

### Validação (rodado de fato, não simulado)
- Encontrei o backend já rodando neste ambiente a partir de uma sessão anterior, servindo a versão
  **antiga** do código (sem `/consumo`) — o sintoma foi `POST /transcrever` funcionando
  normalmente mas `GET /consumo` devolvendo 404 e nenhum `consumo.jsonl` sendo criado. Encerrei
  esse processo (`Stop-Process`, porta 8000 livre) e subi um novo `uvicorn` a partir do código
  atualizado antes de continuar — sem isso o teste real ficaria mascarado.
- Gerado um `.wav` de teste com fala real via sintetizador de voz do Windows (mesma técnica de
  etapas anteriores), usado só para os testes, apagado ao final (não entrou no repositório).
- Três transcrições reais enviadas ao backend (`gpt-4o-transcribe`, `gpt-4o-mini-transcribe`,
  `gpt-4o-transcribe` de novo) — todas HTTP 200. Após as três:
  - `transcritor/consumo.jsonl` tinha exatamente 3 linhas, cada uma com `tipo_usage: "tokens"` e
    os `input_tokens`/`output_tokens`/`total_tokens` batendo exatamente com o `usage` devolvido
    pela API em cada chamada;
  - conferi o cálculo manualmente para as três linhas (ex.: 128 tokens de entrada × US$
    2,50/1M + 37 de saída × US$ 10,00/1M = US$ 0,00069) — bateu exatamente com o `custo_usd`
    persistido nas três;
  - `GET /consumo` devolveu `{"sessao": {"requisicoes": 3, "tokens": 491, "custo_usd": 0.00169},
    "por_dia": [{"data": "2026-08-18", "requisicoes": 3, "tokens": 491, "custo_usd": 0.00169}]}`
    — soma de sessão e agregado diário batendo com as três linhas persistidas.
- Falha ao registrar consumo: não forcei um erro real (ex.: arquivo sem permissão de escrita) —
  validado por inspeção do código, já que o `try/except Exception` amplo envolve toda a escrita e
  o `return` da transcrição já acontece independentemente do resultado de `_registrar_consumo`.
- Arquivo de teste (`teste_audio.wav`) e log do servidor de teste apagados ao final; backend de
  teste deixado rodando na porta 8000 (mesma prática das etapas anteriores, para facilitar teste
  do usuário) — agora já com a versão atualizada do código.

### Critério de pronto
- [x] Cada transcrição bem-sucedida registra um evento de consumo no arquivo local
- [x] `GET /consumo` devolve consumo da sessão atual e consumo agregado por dia
- [x] Testado com três transcrições reais (dois modelos), números batendo com o `usage` da API
- [x] `consumo.jsonl` está no `.gitignore` (`git check-ignore -v` confirmou)
- [x] Falha ao registrar consumo não quebra a resposta de `/transcrever` (por construção do
      código; não forçada uma falha real — ver "Validação" acima)
- [x] `transcritor/README.md` documenta o novo endpoint e o arquivo local
- [x] Nenhuma regressão em `/transcrever` (testado três vezes com sucesso) — fluxos do frontend
      não foram re-testados nesta tarefa (nenhum arquivo de frontend foi tocado; a única mudança
      que poderia afetá-lo, o CORS `allow_methods`, só adiciona `GET`, não remove nada)

### Diagnóstico
- O formato de `usage` para os dois modelos ativos é sempre `"tokens"` na prática (confirmado
  empiricamente) — o fallback por duração existe no código (`usage.type == "duration"` ou usage
  ausente) mas não foi exercitado por um caso real nesta validação; ele cobre principalmente o
  modelo `gpt-4o-transcribe-diarize` (fora do alternador do frontend, mas ainda aceito pelo
  backend) e qualquer mudança futura de comportamento da API.
- Havia um backend obsoleto já rodando neste ambiente antes desta tarefa começar (provavelmente
  deixado no ar de uma sessão anterior) — reiniciar servidores de teste sem primeiro checar se já
  existe um no ar pode mascarar silenciosamente testes de mudanças no backend; vale a pena checar
  `netstat`/processo antes de assumir que `curl` bateu no código atual.

### Novas demandas / riscos
- Nenhuma nova além do já sinalizado no `PLANO.md` (interface de consumo no frontend fica para a
  Etapa 6).

### Ajuste no plano necessário?
Não — Etapa 5 concluída conforme especificado. Aguardando o PM para a Etapa 6 (painel de consumo
no frontend).

## [2026-08-18] — Checagem: PROXIMA_TAREFA.md ainda pede a Etapa 5 (já concluída)
Status: nenhuma ação necessária

### Feito
- Chamado como EXEC para "iniciar a próxima tarefa"; `PROXIMA_TAREFA.md` ainda contém a
  instrução da Etapa 5 (registro de consumo no backend). Conferi o critério de pronto item a
  item contra o código atual (`transcritor/backend/main.py`, `transcritor/README.md`,
  `.gitignore`) — tudo já implementado e bate exatamente com o registro de conclusão da Etapa 5
  logo acima neste arquivo (mesma data, teste real com três transcrições). Não reexecutei nada
  nem alterei código.

### Diagnóstico
- `_RETOMADA_robustez-consumo.md` (raiz) já sinalizava essa possibilidade: "Etapa 5... pode já
  ter sido executada entre esta thread e a próxima — conferir PROGRESSO.md". `PLANO.md` ainda
  não tem a Etapa 5 marcada como concluída (só 1–4 têm) e `PROXIMA_TAREFA.md` não foi
  regenerado para a Etapa 6 — isso é ação do PM, fora do escopo do Executor.

### Novas demandas / riscos
- Nenhuma nova.

### Ajuste no plano necessário?
Sim, mas é ação do PM (não do Executor): marcar a Etapa 5 como concluída em `PLANO.md` e gerar
`PROXIMA_TAREFA.md` para a Etapa 6 (painel de consumo no frontend), conforme o próprio
`_RETOMADA_robustez-consumo.md` já indicava como próximo passo.

## [2026-08-18] — Plano novo, Etapa 6: Painel de consumo no frontend

### Contexto de execução (leia antes do resto)
Esta etapa foi executada dentro do mesmo chat de PM (sessão em nuvem, sem acesso direto ao seu
computador além da ponte de arquivos), a pedido explícito do usuário ("pode fazer a próxima
tarefa"), não pelo Executor local de costume. Registro isso aqui porque muda o que foi possível
validar de fato — ver "Validação" abaixo.

### Feito
- `transcritor/frontend/index.html`:
  - novo botão `#botaoConsumo` (classe `.icone-avancado`, mesmo estilo do `#botaoConfiguracoes`),
    com ícone de gráfico de barras, ao lado do botão de configurações;
  - novo modal `#fundoConsumo` (reaproveita a classe `.painel-config` do modal de configurações
    para manter a mesma linguagem visual), com cabeçalho "Consumo" e botão de fechar
    `#botaoFecharConsumo` — a regra CSS de `#botaoFecharConfiguracoes` foi estendida para incluir
    também `#botaoFecharConsumo` (mesmo seletor combinado), em vez de duplicar a regra;
  - ao abrir o modal, busca `GET /consumo` na hora (sem cache/polling) e renderiza: sessão atual
    (requisições, tokens, custo em USD), histórico diário (lista com data/tokens/custo por dia) e
    um gráfico de barras de custo por dia feito só em HTML/CSS (sem adicionar dependência nova —
    optei por essa alternativa em vez de Chart.js via CDN, já que a tarefa permitia e evita
    depender de rede externa para um gráfico simples de poucas barras);
  - botão "Resetar sessão": guarda os totais de sessão do backend no momento do clique como uma
    baseline em memória (`sessaoBaseReset`); a partir daí, a sessão exibida é sempre
    `(total atual do backend − baseline)`, então volta a zero na hora e cresce de novo com as
    próximas transcrições, sem chamar nenhum endpoint novo e sem tocar em `consumo.jsonl`. A
    baseline não é persistida (variável JS em memória) — reinicia ao recarregar a página, igual
    ao contador de sessão do próprio backend;
  - erro ao buscar `GET /consumo` (backend fora do ar, rede) mostra mensagem dentro do próprio
    painel (`#consumoErro`), sem lançar exceção nem afetar o resto da página.
- `transcritor/README.md`: nova seção "Painel de consumo no frontend" (dentro de "Registro de
  consumo"), documentando o ícone, o que o painel mostra, o comportamento exato do reset (zera
  só a tela, não persiste, não mexe no backend) e o tratamento de erro.

### Validação (parcial — ver limitação abaixo)
- Sintaxe do JS extraído do `<script>` verificada com `node --check` — sem erros.
- Testado com Playwright (Chromium headless, `/mnt/user-data/uploads` local, sem o backend real)
  interceptando `GET /consumo` com uma resposta mockada (a mesma resposta real registrada na
  Etapa 5: `{"sessao": {"requisicoes": 3, "tokens": 491, "custo_usd": 0.00169}, "por_dia": [...]}`):
  - painel abre e mostra "Requisições: 3", "Tokens: 491", "Custo estimado: US$ 0.0017" e as duas
    linhas do histórico diário corretamente;
  - gráfico renderiza 2 barras (uma por dia do mock);
  - clique em "Resetar sessão" zera a exibição (0 requisições/tokens/custo); fechar e reabrir o
    painel com o mesmo mock (simulando nenhuma transcrição nova) mantém a sessão em zero —
    confirma que a baseline do reset funciona como esperado;
  - simulando falha de rede (`route.abort()`), o painel mostra a mensagem de erro e o resto da
    página continua funcional (testado alternando o modelo depois do erro);
  - nenhum erro de console/página (`pageerror`) em nenhum dos cenários;
  - regressão: painel de configurações (`#botaoConfiguracoes`) testado lado a lado, continua
    abrindo e fechando normalmente, com o visual inalterado (capturas de tela comparadas).
- **Não validado nesta etapa** (limitação do ambiente, não pulado por escolha): teste de ponta a
  ponta com o backend real rodando na máquina do usuário, com `OPENAI_API_KEY` de verdade e
  transcrições reais, como o Executor fez nas etapas anteriores. A sessão que executou esta etapa
  não tem acesso ao backend local do usuário além da ponte de arquivos — só foi possível simular
  a resposta do `GET /consumo`, não gerar consumo real. Fica pendente uma verificação rápida do
  usuário (ou de uma sessão EXEC local): rodar o backend, fazer 1-2 transcrições reais, abrir o
  painel e conferir que os números batem com o `GET /consumo` puro, e testar o reset com dados
  reais.

### Critério de pronto
- [x] Ícone de consumo, mesmo estilo visual do de configurações, abre o popover/modal com sessão
      atual e histórico diário
- [x] Gráfico de custo por dia visível dentro do popover
- [x] Botão de reset zera só a exibição da sessão no frontend, sem endpoint novo nem alteração no
      backend/`consumo.jsonl` (por construção do código — baseline em memória, ver "Feito")
- [ ] Testado abrindo o painel depois de uma transcrição real — **não feito nesta etapa**, ver
      "Validação"; testado com dados mockados equivalentes aos reais da Etapa 5
- [x] Erro ao buscar `GET /consumo` não quebra o resto da página (testado com falha de rede
      simulada)
- [x] `transcritor/README.md` documenta o novo painel
- [x] Nenhuma regressão nos fluxos já validados — testado configurações (visual e abertura/
      fechamento) e alternador de modelo; upload e gravação não foram exercitados nesta etapa
      porque nenhum arquivo relacionado a eles foi tocado (só CSS/HTML/JS novos, sem alterar
      código existente de upload/gravação)

### Diagnóstico
- Reaproveitar a classe `.painel-config` para o modal de consumo (em vez de criar uma classe
  nova) manteve a tarefa simples e o visual idêntico, ao custo de o nome da classe não descrever
  mais só "configurações" — se um dia o projeto crescer, vale renomear para algo genérico tipo
  `.painel-popover`.
- A semântica do reset (baseline em memória, sessão exibida = atual − baseline) foi uma decisão
  de implementação não detalhada na tarefa: a alternativa mais simples seria mostrar sempre zero
  até a página recarregar, mas isso tornaria o reset pouco útil (qualquer transcrição nova depois
  do reset sumiria da visualização). Optei pela baseline por ser o comportamento mais parecido
  com um "reset de cronômetro", mas é uma interpretação — sinalizando para o PM/usuário validar
  se é isso mesmo que fazia sentido.

### Novas demandas / riscos
- Validação de ponta a ponta com backend real e transcrições reais ainda pendente (ver
  "Validação") — recomendo rodar antes de considerar a etapa fechada de vez.

### Ajuste no plano necessário?
Não — Etapa 6 implementada conforme especificado, com a ressalva de validação real pendente
registrada acima. Etapa 7 (streaming do transcript) segue não iniciada.

## [2026-08-19] — Plano novo, Etapa 7: Streaming do transcript
Status: concluído

### Feito
- **Passo 1 (formato real dos eventos, confirmado empiricamente antes de implementar)**: script
  avulso (fora do repo) chamando `cliente.audio.transcriptions.create(..., stream=True)`
  diretamente contra a API real, para os dois modelos ativos (`gpt-4o-transcribe`,
  `gpt-4o-mini-transcribe`). Formato encontrado: uma sequência de eventos
  `TranscriptionTextDeltaEvent` (`type="transcript.text.delta"`, campo `delta` com um pedaço de
  texto novo) seguida de **um único** evento final `TranscriptionTextDoneEvent`
  (`type="transcript.text.done"`, campo `text` com o texto completo e campo `usage` no **mesmo
  formato** já usado no fluxo sem streaming — `usage.type == "tokens"`, `input_tokens`,
  `output_tokens`, `total_tokens`). Nenhum evento de erro dedicado veio da API nos testes; erros
  de rede/autenticação continuam levantando as mesmas exceções da SDK (`AuthenticationError`,
  `APIConnectionError`, `APIStatusError`) do fluxo sem streaming, só que agora podem acontecer no
  meio da iteração do stream em vez de numa chamada síncrona única.
- **Backend (`transcritor/backend/main.py`)**: `POST /transcrever` ganhou o campo de formulário
  `stream: bool = Form(False)`. Com `stream=true`, a validação de modelo/chave/arquivo vazio
  continua idêntica e síncrona (ainda dá pra devolver 422/503/400 normalmente, porque acontece
  antes de qualquer resposta ser iniciada); depois disso, em vez da chamada única, o endpoint
  devolve um `StreamingResponse` (`Content-Type: application/x-ndjson`) gerado por
  `_gerar_eventos_transcricao_stream`, que itera os eventos da API e emite uma linha JSON por
  evento: `{"tipo":"delta","texto":"..."}` para cada pedaço, `{"tipo":"final","texto":"..."}` no
  evento final (chamando `_registrar_consumo` com o `usage` desse evento — mesma função já usada
  no modo sem streaming, nenhuma lógica de custo nova) e `{"tipo":"erro","detail":"..."}` se a
  chamada à API falhar durante a iteração. Essa última parte é uma decisão de design registrada em
  "Diagnóstico" abaixo: como o `StreamingResponse` já envia status 200 e headers antes de começar a
  iterar o gerador, um erro no meio do stream não pode mais virar um HTTPException com status
  4xx/5xx — vira mais uma linha do próprio stream. Se o evento final não trouxer `usage`
  recuperável, um aviso é só logado no console do servidor (nenhum valor inventado é persistido),
  igual ao padrão já usado no `_registrar_consumo` existente. Modo `stream=false`/ausente: nenhuma
  linha de código do caminho antigo foi alterada.
- **Frontend (`transcritor/frontend/index.html`)**: novo alternador `#botaoStreaming` ("Ligado"/
  "Desligado", começa desligado), mesmo estilo visual do `#botaoModelo` (CSS combinado nos dois
  seletores), compartilhado entre upload e gravação rápida, logo abaixo do alternador de modelo.
  Nova função `consumirStreamTranscricao(resposta, callbacks)` compartilhada: lê a resposta via
  `response.body.getReader()`, faz o parsing incremental do NDJSON linha a linha (tolera uma linha
  incompleta ficando no buffer até a próxima leitura) e chama `aoDelta`/`aoFinal`/`aoErro`
  conforme os eventos chegam; devolve `{ ok, teveErro }` ao final para o chamador decidir se
  precisa mostrar um erro genérico de conexão interrompida (quando a conexão cai sem nenhum evento
  `final` nem `erro` ter chegado). No upload (`#formulario` submit), com streaming ligado, cada
  delta atualiza `#resultado` (classe "carregando", texto crescendo) e o evento final troca para
  classe "sucesso" com o texto oficial da API (não a soma manual dos deltas, por segurança). Na
  gravação rápida (`enviarGravacaoRapida`), mesma lógica, mas escrevendo em `#transcriptRapido` a
  partir do texto já existente na caixa antes dessa gravação (preserva o comportamento cumulativo
  já existente, só que visível em tempo real). Em ambos os fluxos, com streaming desligado, o
  código antigo (fetch único, resposta JSON) não foi tocado.
- **`transcritor/README.md`**: nova seção "Streaming do transcript" documentando o alternador, o
  formato NDJSON da resposta em stream (com exemplo), a diferença de tratamento de erro (erro
  antes do stream começar = HTTP normal; erro durante o stream = linha `"tipo":"erro"` dentro do
  próprio stream, já que o status HTTP não pode mais mudar nesse ponto), o comportamento do
  frontend e a paridade do registro de consumo entre os dois modos. "Como usar o frontend"
  ganhou um passo citando o novo alternador.

### Validação (rodado de fato, com fala real, ao final da implementação — conforme direcionamento
do usuário de reservar os testes completos para o fim)
- **Formato dos eventos**: confirmado contra a API real antes de implementar (ver "Feito", passo
  1) — não presumido.
- **Backend isolado**: `curl -N` contra `POST /transcrever` com `stream=true` mostrou as linhas
  NDJSON chegando (dezenas de eventos `delta` seguidos de um `final`), com acentuação/UTF-8
  corretos; `stream=false` no mesmo áudio continuou devolvendo o JSON único de sempre, sem
  diferença de comportamento.
- **Consumo equivalente entre os dois modos**: mesmo áudio, mesmo modelo (`gpt-4o-transcribe`),
  uma vez com `stream=false` e outra com `stream=true` — `consumo.jsonl` registrou
  `input_tokens=185` nos dois casos (idêntico, é o tamanho do áudio) e `output_tokens` de 47 vs 49
  (variação natural do texto transcrito entre as duas chamadas à API, não um bug); custo estimado
  praticamente idêntico (US$ 0,0009325 vs US$ 0,0009525). Confirma que o registro de consumo do
  modo streaming é equivalente ao modo sem streaming para o mesmo áudio, como pedia o critério de
  pronto.
- **Erro durante o streaming, sem travar**: dois testes distintos —
  (a) chamado `_gerar_eventos_transcricao_stream` diretamente com uma chave da API inválida:
  o gerador emitiu a linha `{"tipo":"erro","detail":"Falha de autenticação..."}` e terminou
  normalmente, sem travar nem propagar exceção;
  (b) teste isolado do parser do frontend (Node, simulando um `ReadableStream` fake) cobrindo três
  cenários — deltas seguidos de um evento de erro sem final (conexão recusada pela API no meio),
  deltas seguidos de final normal, e deltas sem nenhum evento final/erro (conexão caindo de
  verdade) — os três se comportaram como esperado (`ok`/`teveErro` corretos, nenhuma promise
  pendurada).
- **Erro de conexão de verdade, na interface real**: Edge headless (`playwright-core`) abrindo
  `http://127.0.0.1:8000/`, com a rota de `/transcrever` interceptada para simular o backend fora
  do ar (`route.abort`) e streaming ligado — mensagem de erro clara apareceu em `#resultado`
  (classe "erro"), botão "Transcrever" voltou a ficar habilitado com o texto original (não ficou
  travado em "Transcrevendo…").
- **Exibição incremental de verdade, com fala real**: mesmo Edge headless, áudio de ~25s gerado
  por sintetizador de voz do Windows, streaming ligado, amostrando `#resultado` a cada 40ms durante
  o upload — capturados 33 tamanhos de texto distintos ao longo de ~1,4s (progressão visível,
  não um salto único do início pro fim), terminando com o texto completo em classe "sucesso".
  Repetido na gravação rápida (gravação de ~19s via microfone fake com o mesmo áudio real
  injetado) — texto de `#transcriptRapido` também cresceu em múltiplos passos visíveis durante a
  gravação/envio, terminando em status "sucesso".
- **Regressão — upload sem streaming**: mesmo áudio, alternador desligado — resposta idêntica ao
  comportamento de sempre (JSON único, sem passos intermediários).
- **Regressão — configurações, consumo, alternador de modelo**: painel de configurações abre/
  fecha normalmente; painel de consumo abre, busca `GET /consumo` e mostra os dados (inclusive os
  registros gerados pelos testes desta etapa); alternador de modelo continua alternando
  normalmente — nenhum dos três foi afetado pelas mudanças de CSS/HTML compartilhadas com o novo
  alternador de streaming.
- Backend de teste reiniciado uma vez no início (para carregar o código novo) e deixado rodando ao
  final (porta 8000), no mesmo padrão das etapas anteriores deste plano. Nenhum arquivo de teste
  (`.wav`, scripts Node/Python) entrou no repositório — tudo ficou na pasta de rascunho da sessão,
  fora de `transcritor/`.

### Critério de pronto
- [x] Alternador de streaming, mesmo estilo do alternador de modelo, liga/desliga o modo em
      upload e gravação (testado nos dois fluxos)
- [x] Com streaming ligado, o texto aparece incrementalmente na área de transcript conforme a API
      devolve (testado com fala real, os dois modelos ativos — formato confirmado empiricamente
      antes de implementar, e a progressão incremental capturada com timestamps no teste real)
- [x] Com streaming desligado, o comportamento atual (resposta completa de uma vez) continua
      idêntico — sem regressão (testado)
- [x] Consumo (Etapa 5) registrado corretamente também no modo streaming — tokens/custo batendo
      com o que a API reportou, valor equivalente entre streaming ligado e desligado para o mesmo
      áudio (testado com comparação direta no `consumo.jsonl`)
- [x] Erro de conexão durante o streaming tratado sem travar a interface (testado tanto o caminho
      do backend — erro de autenticação no meio do stream — quanto a interface real — backend
      inacessível durante upload com streaming ligado)
- [x] `transcritor/README.md` documenta o alternador e o formato da resposta em stream
- [x] Nenhuma regressão nos fluxos já validados (upload, gravação, configurações, painel de
      consumo, `/transcrever` sem streaming, `/consumo`) — todos testados nesta etapa

### Diagnóstico
- **Decisão de design não detalhada na tarefa, registrada aqui**: como o `StreamingResponse` do
  FastAPI/Starlette envia o status HTTP e os headers assim que a resposta começa a ser processada
  — antes de qualquer conteúdo do gerador ser produzido — não existe como, uma vez iniciado o
  streaming, devolver um código de erro HTTP diferente de 200 se a chamada à API da OpenAI falhar
  no meio da iteração (autenticação, rede, recusa do áudio). A solução adotada foi representar
  esse erro como mais um evento dentro do próprio stream NDJSON (`{"tipo":"erro",...}`), documentada
  no README. Erros que dá pra detectar **antes** de iniciar o stream (modelo inválido, chave
  ausente, arquivo vazio) continuam preservando o comportamento HTTP normal (422/503/400), porque
  acontecem antes de qualquer resposta ser aberta.
- O evento final da API (`transcript.text.done`) já trouxe o `usage` no mesmo formato usado pelo
  fluxo sem streaming nos testes reais — não foi preciso nenhum código de conversão extra além de
  reaproveitar `_registrar_consumo`/`_calcular_custo_usd` já existentes.
- Pequena diferença de transcrição observada entre chamadas (ex.: "transcrição" numa chamada e
  "transcrical" em outra, para a mesma frase) é variação normal do modelo de fala-pra-texto entre
  execuções, não um efeito do streaming — confirmado comparando o mesmo áudio nos dois modos mais
  de uma vez.

### Novas demandas / riscos
- Nenhuma nova. A pendência de validação real do painel de consumo (registrada na Etapa 6) foi
  coberta de passagem nesta etapa: o painel foi aberto contra o backend real, com dados reais
  gerados pelos próprios testes desta tarefa (ver "Regressão — configurações, consumo, alternador
  de modelo" acima).

### Ajuste no plano necessário?
Não — Etapa 7 concluída conforme especificado. Era a última etapa planejada neste plano; próximos
passos ficam a critério do PM/usuário. Nenhum commit/push foi feito, conforme instrução da tarefa.

## [2026-08-19] — Entre etapas: usuário reportou "streaming não funciona" (texto só aparece no final)
Status: resolvido (não era bug de código — comportamento esperado para áudio curto)

### Feito
- Diagnosticado com um teste real e controlado: gravei um áudio de fala bem curto ("Teste
  curto.", ~1s de fala) e repeti o mesmo teste automatizado de captura de progressão (Edge
  headless, amostrando a área de resultado a cada 20ms) já usado para validar a Etapa 7.
  Resultado: a chamada inteira (conectar → primeiro delta → evento final) terminou em **791ms**,
  com a transição de "carregando" pro texto final acontecendo em menos de 25ms — tempo curto
  demais para o olho humano perceber como "aparecendo aos poucos". Com áudio mais longo (~25s,
  testado na validação original da Etapa 7), a mesma mecânica mostrou claramente 33 passos de
  texto crescendo ao longo de ~1,4s.
- Confirmado também por `curl -N` direto no backend (sem passar pelo navegador) que os eventos
  `delta` continuam chegando um por um, normalmente — não é um bug de streaming quebrado, é
  a API da OpenAI processando um áudio muito curto rápido demais para o efeito visual aparecer.
- Nenhuma alteração de código feita — não era um bug; expliquei o diagnóstico ao usuário e pedi
  para testar com uma gravação mais longa (10-20s+) para conseguir perceber o efeito.

### Diagnóstico
- O streaming em si funciona corretamente em todos os áudios (curtos ou longos) — a diferença é
  só de percepção: quanto mais curto o áudio, menos pedaços de texto chegam e mais rápido a API
  termina de gerá-los, então o efeito incremental fica imperceptível a olho nu. Isso é inerente ao
  comportamento da API da OpenAI (não presumido — confirmado pelo teste cronometrado acima), não
  uma falha da implementação desta etapa.

### Novas demandas / riscos
- Nenhuma de código. Registro apenas para o PM/usuário: se a expectativa é que o efeito visual
  seja perceptível mesmo em gravações curtas, isso exigiria um adiantamento artificial de exibição
  (ex.: revelar o texto letra a letra num ritmo mínimo, independente de quando o pedaço realmente
  chegou da API) — mudança de escopo deliberada, não implementada aqui porque a Etapa 7 pedia
  mostrar o texto "conforme a API devolve", e um atraso artificial contradiria isso. Fica como
  decisão para o PM se quiser abrir como item novo.

### Ajuste no plano necessário?
Não é claro ainda — depende de o usuário confirmar se o comportamento (efeito visível só em
áudios mais longos) é aceitável ou se quer um efeito de exibição artificialmente pausado mesmo em
áudios curtos.

## [2026-08-19] — Checagem: PROXIMA_TAREFA.md ainda pede a Etapa 7 (já concluída)
Status: nenhuma ação necessária

### Feito
- Chamado como EXEC para "iniciar a próxima tarefa"; `PROXIMA_TAREFA.md` ainda contém a
  instrução da Etapa 7 (streaming do transcript). Conferi o critério de pronto item a item contra
  o código atual:
  - `transcritor/backend/main.py`: campo `stream: bool = Form(False)`,
    `_gerar_eventos_transcricao_stream`, `StreamingResponse` (`application/x-ndjson`) — presentes.
  - `transcritor/frontend/index.html`: alternador `#botaoStreaming`, função
    `consumirStreamTranscricao`, uso em ambos os fluxos (upload e gravação rápida) — presentes
    (confirmado via grep, linhas 259–542 e 1058–1084).
  - `transcritor/README.md`: seção "Streaming do transcript" documentando alternador, formato
    NDJSON e comportamento de consumo — presente.
  Tudo bate exatamente com o registro de conclusão da Etapa 7 acima neste arquivo (mesma data,
  testes completos com fala real, os dois modelos, erro de conexão, consumo equivalente). Não
  reexecutei nada nem alterei código.

### Diagnóstico
- Mesma situação já registrada em 2026-08-18 para a Etapa 5: `PLANO.md`/`PROXIMA_TAREFA.md` não
  foram regenerados pelo PM depois da conclusão da Etapa 7 (e do incidente pós-etapa sobre áudio
  curto, também já resolvido e registrado acima).

### Novas demandas / riscos
- Nenhuma nova.

### Ajuste no plano necessário?
Sim, mas é ação do PM (não do Executor): marcar a Etapa 7 como concluída em `PLANO.md` e gerar
`PROXIMA_TAREFA.md` para a próxima etapa (ou registrar que era a última etapa planejada e decidir
os próximos passos, inclusive a questão em aberto sobre o efeito visual em áudios curtos,
sinalizada no incidente pós-etapa acima).
