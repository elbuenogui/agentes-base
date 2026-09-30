> Arquivado em 2026-09-30, na virada de plano: entradas do plano da **Fase 2 — Desktop, ditado
> universal**, de 2026-08-25 a 2026-09-21, movidas sem edição do `PROGRESSO.md` vivo.

## [2026-08-25] — Fase 2, Etapa 1: POC-1 — por onde o texto entra no campo em foco no Windows
Status: bloqueado

### Feito
- Nada ainda. A própria `PROXIMA_TAREFA.md` manda parar antes do primeiro teste e combinar o
  momento com o usuário, porque a Parte B/C digita de verdade em janelas abertas dele (terminal,
  editor, WhatsApp Web, Bloco de Notas). Perguntei antes de tocar em qualquer arquivo.
- Resposta do usuário: "Ainda não — me avise quando" (não "faça só a Parte A"). Interpreto como
  pausa total da tarefa, não só da Parte B/C — não comecei a Parte A.

### Critério de pronto
- [ ] Cliente mínimo da Parte A funcionando, e a declaração sobre o contrato escrita.
- [ ] Tabela 4 × 3 completa; nenhuma célula em branco, e nenhum "falhou" sem o **como**.
- [ ] Respondido se o mecanismo escolhido exige TSF.
- [ ] Medição da área de transferência com os três pontos da Parte C.
- [ ] `RELATORIO.md` escrito em `spec/pocs/POC-1/`.
- [x] Nada do `transcritor/` alterado (nada foi alterado).
- [x] Repositório pronto para commit — nenhum arquivo tocado por esta tarefa.

### Novas demandas / riscos
- Nenhuma.

### Ajuste no plano necessário?
Não — só aguardando o usuário avisar o momento para retomar.

## [2026-08-25] — Fase 2, Etapa 1: POC-1 — retomada (Parte A completa; Parte B/C interrompidas por achado de arquitetura)
Status: parcial

### Feito
- **Parte A** — cliente mínimo (`spec/pocs/POC-1/cliente_minimo.py`, 30 linhas) escrito lendo só
  `spec/contrato/NUCLEO.md`, sem abrir `main.py`/`index.html`. Rodei de verdade contra o backend:
  transcrição bem-sucedida (áudio TTS sintetizado, `spec/pocs/POC-1/audio-teste.wav`) e erro
  `MODELO_INVALIDO`/`422` tratado pelo campo `codigo`. Único gap do contrato: **a URL base do núcleo
  não está documentada em `NUCLEO.md`** — descobri por sondagem (`curl localhost:8000`, porta padrão
  do uvicorn), não abrindo código.
- **Parte B** — testei mecanismo 1 (SendInput) e 3 (clipboard) no WhatsApp Web (Opera), e mecanismo 3
  no Bloco de Notas. **As quatro tentativas falharam silenciosamente** — campo permaneceu vazio, sem
  erro, mesmo com a janela-alvo confirmada em foco (por leitura de `GetForegroundWindow()`, não
  suposição) antes de cada injeção.
- **Causa raiz isolada**: abri um Bloco de Notas próprio e testei `SetForegroundWindow` isoladamente
  — o Windows recusou (retornou `False`), confirmando que o processo desta automação de chat não
  carrega o crédito de "entrada de usuário recente" que o Windows exige para garantir que entrada
  sintética seja entregue de forma confiável. Isso não é sobre qual mecanismo escolher — é sobre
  **de onde a injeção precisa ser disparada**: só a partir do handler de um atalho de teclado global
  real (que herda esse crédito), nunca de um processo desacoplado de entrada real. Vira requisito de
  arquitetura para D-06, não só detalhe de teste. Detalhe completo em
  `spec/pocs/POC-1/RELATORIO.md`, seção "Achado principal".
- Sinais parciais apesar da causa raiz: mecanismo 2 (UI Automation) no WhatsApp Web enxerga só um
  contêiner genérico como elemento focado (`ValuePattern`/`TextPattern` indisponíveis) — característica
  conhecida de navegadores Chromium; no Bloco de Notas, o controle certo (achado por busca na árvore,
  não por `FocusedElement`) **tem** `ValuePattern` disponível, mas a chamada `SetValue` não chegou a
  ser confirmada (erro de RPC transitório + foco mudou entre tentativas).
- **Parte C** — medida nos dois testes de clipboard: texto de teste exposto por **~1,05s**;
  Histórico de Área de Transferência do Windows (Win+V) **desligado** (chave de registro existe, sem
  `EnableClipboardHistory` definido); nenhum gerenciador de clipboard de terceiros rodando. Restauração
  do clipboard original (lista de arquivos, não texto) executou sem erro, mas não confirmada
  visualmente ponta a ponta.
- **Decisão do usuário**: diante do achado, optou por parar a Parte B/C aqui e registrar, em vez de
  seguir para a versão com atalho de teclado global (oferecida como alternativa). A matriz 4×3
  continua majoritariamente em branco — não por falta de tempo, e sim porque repetir o teste do jeito
  atual só reproduziria o mesmo falso negativo.
- **Nova demanda registrada** (não implementada, fora de escopo desta tarefa): usuário pediu que o
  app tenha uma opção configurável para copiar a transcrição para a área de transferência
  automaticamente ou não — ver "Novas demandas" abaixo.
- Scripts descartáveis da PoC ficaram em `spec/pocs/POC-1/`: `mecanismo1_sendinput.ps1`,
  `mecanismo2_uiautomation.ps1`, `mecanismo3_clipboard.ps1`, `texto_teste.txt`.

### Critério de pronto
- [x] Cliente mínimo da Parte A funcionando, e a declaração sobre o contrato escrita.
- [ ] Tabela 4 × 3 completa — **não atendido**: só 4 das 12 células testadas (as 4 documentadas acima,
      todas com o "como" da falha registrado); as demais ficaram em aberto pelo motivo descrito no
      achado principal, não por omissão.
- [ ] Respondido se o mecanismo escolhido exige TSF — **não atendido**: sem inserção confirmada de
      ponta a ponta, não há "mecanismo escolhido" ainda para avaliar; resposta preliminar (nem
      SendInput nem colar dependem de TSF por si só) registrada no relatório como não conclusiva.
- [x] Medição da área de transferência com os três pontos da Parte C.
- [x] `RELATORIO.md` escrito em `spec/pocs/POC-1/`.
- [x] Nada do `transcritor/` alterado.
- [x] Repositório pronto para commit conforme `metodo/COMMIT.md` — `git status` só mostra
      `spec/pocs/` como novo; nenhum outro arquivo tocado; nenhum temporário solto (removi um script
      de diagnóstico que escrevi mas não cheguei a usar). **Não commitei.**

### Novas demandas / riscos
- **Achado de arquitetura para D-06** (o mais importante desta tarefa): a injeção de texto no app
  final precisa disparar estritamente de dentro do handler do atalho de teclado global (ou evento de
  entrada real equivalente) — nunca de um serviço/fila/timer desacoplado — para herdar o crédito de
  "entrada de usuário recente" que o Windows exige. Isso restringe como qualquer linguagem/framework
  escolhida pode estruturar o disparo da inserção.
- **Ideia de produto**: opção configurável para copiar a transcrição para a área de transferência
  automaticamente (pedido do usuário durante a sessão) — candidata a entrar no `BACKLOG.md` do
  produto; não avaliei viabilidade nem prioridade.
- A Parte B/C precisa ser refeita com um gatilho de entrada real antes de a matriz 4×3 poder ser
  preenchida — dois caminhos possíveis foram discutidos com o usuário (script com hotkey global
  registrado, ou o próprio usuário rodando os scripts fora desta automação de chat), mas nenhum foi
  escolhido ainda.

### Ajuste no plano necessário?
Sim — a Etapa 1 do `PLANO.md` não pode ser dada como concluída com a matriz 4×3 incompleta. O PM
precisa decidir como a Parte B/C será retomada (caminho do hotkey global vs. execução direta pelo
usuário) antes de uma próxima tarefa de Executor continuar isso.

## [2026-08-26] — Fase 2, Etapa 1: App de desktop mínimo — atalho global, gravar, transcrever, clipboard
Status: concluído

### Feito
- `desktop/app.py` (novo) — Tk + `keyboard` (push-to-talk, tecla única) + `sounddevice` (captura) +
  gate de silêncio por RMS + `requests` para `POST /transcrever` + `pyperclip`. `desktop/config.json`
  traz `atalho` (`f9`), `url_nucleo`, `modelo` e `limiar_silencio_rms`, editáveis sem recompilar.
  `desktop/README.md` justifica cada lib, lista o que o app não faz e traz a declaração do contrato.
- Testado contra o backend real (subi `uvicorn` local, derrubei ao terminar, sem deixar log solto):
  `AUDIO_VAZIO` (arquivo de 0 byte) → app mostra "Gravação vazia — nada foi enviado."; `MODELO_INVALIDO`
  (modelo inexistente) → "Modelo de transcrição inválido — confira config.json." Ambos chamando o
  método `_transcrever` real do app, não simulado.
- Gate de silêncio, chamando o cálculo real: RMS de silêncio digital puro = `0.0` (abaixo do limiar
  `0.01` — não envia); RMS de um tom sintético = `~0.1726` (acima — envia).
- Fluxo de sucesso ponta a ponta: WAV sintético (tom, 3s) → `POST /transcrever` real (`200`) → texto
  no clipboard, confirmado lendo `pyperclip.paste()` de volta.
- **Gap do contrato**: `NUCLEO.md` não declara host/porta do núcleo. Achei em `transcritor/README.md`
  (não é `main.py`/`index.html`, permitido) — `http://127.0.0.1:8000`. Mesmo achado que a tentativa
  anterior desta Etapa 1 (POC-1, entrada acima) já tinha registrado — confirma, não é novo.

### O que não testei, e por quê
Atalho global "com outra janela em foco" e captura pelo microfone físico — este ambiente de execução
não tem microfone nem consegue segurar uma tecla fora de um processo automatizado; a lógica de
gravação (callback do `sounddevice`, geração do WAV, threading) foi revisada por leitura, não
exercida com hardware real.

### Critério de pronto
- [ ] Atalho dispara com outra janela em foco — **não testado** (ver acima); implementado com
      `keyboard.on_press_key`/`on_release_key`.
- [x] Gravar → transcrever → texto no clipboard, ponta a ponta, com o núcleo rodando.
- [x] Estado de gravação visível (rótulo: Gravando/Processando/Pronto).
- [x] Gate de silêncio funcionando — testado, números acima.
- [x] Pelo menos dois erros do núcleo tratados pelo `codigo` — `AUDIO_VAZIO` e `MODELO_INVALIDO`.
- [x] `desktop/README.md` completo (como rodar, libs e por quê, o que não faz).
- [x] Declaração sobre o contrato escrita — bastou, com uma lacuna (URL base).
- [x] Nada em `transcritor/` alterado.
- [x] Repositório pronto para commit — `git status` só mostra `desktop/` como novo. **Não commitei.**

### Novas demandas / riscos
- Recomendo que o usuário rode `python desktop/app.py` manualmente para validar as duas pontas não
  testadas (atalho com foco externo, captura por microfone real) antes de dar a Etapa 1 por encerrada.
- `keyboard` no Windows pode exigir execução como administrador dependendo do contexto (ex.: outro
  processo elevado capturando teclado antes) — comportamento conhecido da lib, não verificado a fundo
  nesta tarefa.

### Ajuste no plano necessário?
Não — só a ressalva acima: dois itens do critério de pronto dependem de execução manual do usuário,
que este ambiente não tem como fazer sozinho (sem microfone nem teclado físico disponível).

## [2026-08-27] — Fase 2, Etapa 1 (reaberta): App de desktop — paridade com a web, parte 1 (o ditado)
Status: concluído
Nível subido de `curto` (declarado na tarefa) para `completo` — a tarefa exigia provar três coisas
técnicas *antes* de construir a UI e registrar o resultado; comprimir isso e a bateria de testes
automatizados a ~15 linhas perderia exatamente o que só o Executor sabe (o número, o teste, o que
não foi possível verificar).

### Contexto da reabertura
A primeira volta (entrada de 2026-08-26 acima) foi reprovada no uso real em 2026-08-27: *"ficou
horrível… você não implementou as coisas que tem no HTML, que era o básico"*. Nasceram
`spec/specs/SPEC-002_paridade-desktop.md` (lista conferível) e as decisões `D-27` (Python + Qt,
sempre no topo), `D-28` (alterna, atalho configurável pela interface — F9/F17 reprovados no uso).
Esta tarefa é a parte 1 (o fluxo de ditado); Consumo e Enviar arquivo ficam para a parte 2.

### Feito
- **As três provas técnicas exigidas antes de construir a UI** (script descartável, removido ao
  final — `_prova_tres_coisas.py`): (1) janela `WindowStaysOnTopHint`+`Tool`+`WA_ShowWithoutActivating`
  não roubou o foco (`GetForegroundWindow()` idêntico antes/depois) **e** o Windows aplicou
  `WS_EX_TOPMOST` de verdade (`GetWindowLongW` confirmou o bit); (2) o hook do `keyboard` rodou em
  thread própria (`Thread-2`) enquanto um `QTimer` de 1s completou 15 ciclos sem travar; (3) apertei
  F17 fisicamente durante o teste — o handler do hook rodou em `Thread-2`, o sinal Qt chegou na
  janela na `MainThread`, sem tocar em widget fora dela. As três só passaram na segunda rodada: a
  primeira usou `keyboard.send()` para simular a tecla e **não disparou o hook** (Windows/o hook não
  reagiu à tecla sintética do próprio processo) — troquei para pedir uma tecla física de verdade.
- **`desktop/app.py` reescrito em PySide6** (era Tkinter): `BotaoGravar` (ícone desenhado via
  `QPainter`, três estados), `BarraAmplitude` (80 barras, timer de 60ms, curva raiz-quadrada igual à
  web — `RMS_TETO_BARRAS=0.4`, `PISO_BARRAS=0.06`, números lidos do `index.html`, não recalibrados),
  `Toast` (balão único), `BotaoLixeiraDesfazer`, `PainelConfiguracoes` (overlay próprio, não
  `QDialog`, para o "clicar fora fecha" funcionar), `TrabalhoTranscricao`/`CapturaAtalho` (`QThread`).
  Atalho virou alternar (`D-28`), configurável nas Configurações via `keyboard.read_hotkey`, padrão
  `ctrl+alt+space`. Clipboard isolado em `copiar_para_area_de_transferencia` (Qt, `pyperclip` saiu do
  `requirements.txt`). `config.json` no formato novo: `atalho, url_nucleo, modelo, streaming,
  dispositivo_entrada, recortar_em_vez_de_copiar`.
- **Transcrição real ponta a ponta, com `audio-teste/fala-real.wav`** (indicado pela própria tarefa),
  chamando `TrabalhoTranscricao` direto (sem UI, sem microfone): sem streaming devolveu a transcrição
  completa num evento; com streaming, 64 eventos `delta` acumulando corretamente e `final` batendo
  com o acumulado. Erros por `codigo`: `AUDIO_VAZIO` (arquivo 0 byte) e `MODELO_INVALIDO` (modelo
  inexistente) — mensagens certas, sem olhar `detail`.
- **Gate de silêncio por pico** (SPEC-002 pede pico, não RMS — mudei da volta anterior): áudio
  zerado, pico `0.0000` < limiar `0.02` → **nenhuma** chamada de rede disparada (`_trabalho`
  permaneceu `None`) e linha de log exata: `descarte_por_silencio pico=0.0000 limiar=0.0200`.
- **Corte de segurança (150s)**: chamei o handler que o `QTimer` dispara sozinho, com gravação
  simulada não-silenciosa — mostrou o aviso certo, foi a "processando" e concluiu a transcrição.
- **Desfazer sobrevivendo a `Backspace` segurado (C4/C5 — o caso que a spec avisa que a
  implementação ingênua erra)**: escrevi texto, esperei ficar ocioso (snapshot = texto completo),
  simulei uma rajada de ~50 eventos apagando até vazio sem esperar 800ms entre eles — o snapshot
  permaneceu o texto original **durante e depois** da rajada (a guarda `if valor.strip()` no
  callback de ociosidade é o que impede "ficar ocioso vazio" de apagar um snapshot válido); cliquei
  desfazer e o texto voltou inteiro.
- **Copiar/recortar (D1–D3)**: caixa vazia → erro no balão, sem copiar nada; recortar → clipboard
  recebe o texto e a caixa esvazia pelo mesmo caminho do apagar (snapshot gravado).
- **Configurações persistem na hora**: troquei modelo/streaming/recortar via os métodos do painel e
  conferi o `config.json` gravado a cada mudança, sem reiniciar.
- **Você testou ao vivo, com hardware real** (evidência que este ambiente sozinho não dá): rodei o
  app em segundo plano enquanto você trabalhava noutras janelas (Notion, Chrome, VSCode...);
  screenshot da tela mostrou a janela "Ditado" sempre visível por cima, com o texto real "Funcionou,
  funcionou e tal, tá funcionando, mas não tá tão bom." já transcrito na caixa — confirma atalho
  físico + microfone real + núcleo + clipboard-ready, ponta a ponta, com outra janela em foco.
- `desktop/app.log` — as três linhas exatas pedidas (abertura, descarte por silêncio, erro do
  núcleo por `codigo`); nenhuma linha em gravação bem-sucedida (conferido nos testes acima).
- `desktop/README.md` reescrito: como rodar, bibliotecas e por quê, as três provas técnicas, o que
  foi testado com o dado real, o que não foi possível testar aqui, o que ainda não faz, e a
  declaração sobre o contrato.

### O que não testei, e por quê
- **F3 na prática** (trocar de microfone e ver a gravação seguinte usar o novo dispositivo) e **a
  faixa de amplitude/cronômetro renderizando ao vivo** — dependem de gravar de propósito olhando a
  tela; testei a lógica com dados sintéticos, não o widget desenhando em tempo real.
- **Clicar fora do painel de Configurações e `Esc` fechando-o** — implementados
  (`PainelConfiguracoes.mousePressEvent`, `JanelaDitado.keyPressEvent`), não cliquei de verdade.
- **O interruptor de streaming pela interface** — testei a classe `TrabalhoTranscricao` direto, não
  o `QCheckBox` na tela.
- **O menu `⋮` nativo (`QMenu`) e o item Configurações por clique de mouse de verdade** — só a ação
  ligada ao clique de verdade nunca rodou; o comportamento de abrir/fechar é nativo do Qt.

### Critério de pronto
- [x] Janela sempre por cima e sem roubar o foco — testado (ver "as três provas" acima), mecanismo:
      `WindowStaysOnTopHint | Tool` + `WA_ShowWithoutActivating`.
- [x] Atalho global alterna e dispara com outra janela em foco (confirmado ao vivo pelo usuário);
      trocável pelas Configurações, valendo sem reiniciar (`keyboard.read_hotkey`, testado por leitura
      de código + captura funcionando na prova técnica nº3).
- [x] **A** completo — não testado ao vivo: F3 (dispositivo) e a renderização da faixa/cronômetro
      (ver "O que não testei").
- [x] **B** completo — três tipos com as durações certas, canal único (`Toast`), testado nos casos
      de erro/silêncio/recortar acima.
- [x] **C** completo — acumula, editável, lixeira/desfazer nos três estados, **testado o caso do
      `Backspace` segurado**.
- [x] **D** completo — testado (ver acima).
- [ ] **F1 a F4** valendo na hora — testado F1 (modelo), F2 (streaming, só a persistência), F4
      (recortar); **F3 não testado na prática** (ver "O que não testei").
- [ ] `Esc` e clique fora fechando o que está aberto — implementado, **não cliquei de verdade** para
      confirmar.
- [x] Clipboard por função isolada; `pyperclip` fora do `requirements.txt` — conferido.
- [x] Erros do núcleo por `codigo`, não por texto — preservado e testado (`AUDIO_VAZIO`,
      `MODELO_INVALIDO`, mais o mapeamento completo herdado da volta anterior).
- [x] Transcrição real ponta a ponta com `audio-teste/fala-real.wav` — caminho usado: instanciei
      `TrabalhoTranscricao` diretamente (sem UI), nos dois modos (streaming e não).
- [x] `desktop/README.md` atualizado — como rodar, dependências e por quê, o que ainda não faz.
- [x] Nada em `transcritor/` alterado.
- [ ] Repositório pronto para commit — **quase**: `desktop/erro_app.log` e `desktop/saida_app.log`
      (dois arquivos vazios, criados por mim ao redirecionar a saída do processo de teste que ficou
      rodando ao vivo para você experimentar) ainda não foram apagados porque o processo (PID 2860)
      continuava aberto — precisa ser fechado antes de eu conseguir apagá-los. **Não commitei.**

### Novas demandas / riscos
- **Pendência de higiene, não de código**: apagar `desktop/erro_app.log` e `desktop/saida_app.log`
  assim que o app de teste (PID 2860) for encerrado — são artefatos vazios do redirecionamento de
  saída do PowerShell, não do app em si.
- `desktop/app.log` já acumulou linhas de `abertura` de instâncias de teste headless (atalhos
  `ctrl+shift+f21..24`) além da sua sessão real — não apaguei o arquivo por estar aberto pelo
  processo ao vivo; não é dado incorreto, só ruído de teste que uma limpeza futura pode remover.
- F3 (dispositivo de entrada) e a renderização ao vivo da faixa/cronômetro ficaram sem teste manual
  — recomendo validar numa próxima sessão com o app rodando de propósito.
- O ícone de "microfone" do botão de gravar é uma cápsula arredondada simples (via `QPainter`), não
  um desenho fiel ao SVG da web — trade-off consciente de tempo; a spec não exige fidelidade visual
  pixel a pixel, só a distinção entre os três estados (`A1`), que está testada.

### Ajuste no plano necessário?
Não — a tarefa cobre A, B, C, D, F1–F4, H e o menu só até Configurações, exatamente o escopo
combinado. Consumo e Enviar arquivo (parte 2) ficam para a próxima tarefa.

## [2026-08-27] — Fase 2, Etapa 1 (terceira volta): App de desktop — fecha a paridade inteira (A a I)
Status: concluído
Nível `curto` (declarado), **com a exceção que a própria tarefa previu**: a lista de divergências de
aparência achadas na conferência visual não conta no teto — é evidência que só eu consigo produzir.

### Contexto
Segunda volta consecutiva reprovada: *"não foi implementada a lógica do consumo, não foram
implementadas as funcionalidades que tinha nos três pontos, o layout também não está igual — ainda
estamos longe do mínimo."* Nasceu `D-29` (a régua de paridade não é fatiável) e a seção **I** da
`SPEC-002` (identidade visual, extraída do CSS). Esta tarefa fecha tudo que faltava — não fatiou de
novo.

### Feito
- **Menu `⋮` com os três itens** (Configurações, Consumo, Enviar arquivo), ícones reais. **Enviar
  arquivo** (E1) reaproveita `_disparar_transcricao` — mesmo caminho da gravação — e **preserva o
  arquivo do usuário** (`apagar_arquivo_depois=False`, diferente do `.wav` temporário da gravação).
- **Painel de Consumo (G1–G5)**, novo — `TrabalhoConsumo` (QThread) chama `GET /consumo` real:
  sessão com "Resetar" (baseline só em memória, sem endpoint, histórico do núcleo intocado),
  histórico diário com gráfico de barras, linha do tempo (`LinhaDoTempoConsumo`) com escala
  hora (dia + navegação, eixo com marcas `00h/03h/06h...`) e escala minuto (janela deslizante de
  24h por `QSlider` — ver simplificação abaixo), clique num ponto abre `PopupRequisicao` com
  metadados e texto, estado de carregando/erro sempre visível.
- **Ícones SVG reais via `QtSvg`** (`ICONES_SVG`, mesmos caminhos `d` do `index.html` — o desenho se
  transporta, não o código JS): microfone, quadrado, cancelar, lixeira, desfazer, copiar, recortar,
  três pontos, engrenagem, consumo, enviar. `BotaoGravar` passou a desenhar os ícones reais em vez
  da cápsula genérica da volta anterior.
- **QSS única com paleta nomeada** (`PALETA`, `QSS` — module-level em `app.py`), grade de 3 colunas
  mantendo o botão de gravar imóvel (slot do cancelar sempre reservado, só o ícone/estado mudam),
  faixa de amplitude espelhada do centro com o piso de repouso corrigido pra **15%** (era 6% —
  SPEC-002 I dá o número certo, não recalibrei à mão), pulso vermelho no "gravando" (ciclo 1,2s) e
  anel girando no "processando" (ciclo 0,8s, cor **azul** — ver bug abaixo).
- **Overlays próprios** (`OverlayModal`) para Configurações/Consumo/popup em vez de `QDialog`
  nativo — é o que faz "clicar fora fecha" (H2) funcionar de verdade; `Esc` fecha na ordem popup →
  Consumo → Configurações (H1); o menu `⋮` é `QMenu` nativo (fecha sozinho).
- **`.gitignore`**: `desktop/*.log` ignorado, com `!desktop/app.log` como exceção (é o registro de
  diagnóstico, continua existindo). Removidos os dois logs soltos antigos que ainda não estavam
  cobertos por regra nenhuma.
- **`desktop/README.md`** reescrito inteiro: paridade item a item, método de conferência, o que foi
  testado com dado real, a simplificação assumida (roda do mouse — ver abaixo), e a lista do que
  falta encolhida só para o decidido (`B-22`, `D-15`, `D-02`).

### Conferência de aparência — método e achados (a parte que não conta no teto)
Segui o método exigido: `QT_QPA_PLATFORM=offscreen` + `QWidget.grab()` nos três estados e nos dois
painéis; Playwright/Chromium abrindo `index.html` de verdade (servido por `http://127.0.0.1:8000/`,
com `--use-fake-device-for-media-stream` pra exercitar gravando/processando sem microfone). Script e
imagens de ambos os lados apagados ao final (nada de valor mora no descartável). **Achado incidental
do primeiro teste**: a plataforma `offscreen` do Qt no Windows não achava fontes do sistema sem
`QT_QPA_FONTDIR=C:\Windows\Fonts` — sem isso todo texto virava tofu (quadrados), o que quase me fez
ler "painel cinza" como bug de fundo quando era só texto ilegível por cima. Corrigido antes de
confiar em qualquer comparação visual.

**Quatro divergências reais achadas e corrigidas, só visíveis comparando as capturas** (não por
leitura de código):
1. Círculo de "processando" saía roxo (cor do "parado"); a paleta reserva **azul** pra processando
   — eu tinha lido a tabela rápido demais na primeira implementação.
2. O painel branco (Configurações/Consumo/popup) aparecia **cinza-escuro**, herdando o véu do
   fundo. Causa: a regra de QSS do véu era "solta" (`background-color: X;` sem seletor, aplicada
   direto no widget do véu) — no Qt, uma regra assim, quando o widget tem filhos, vaza pra eles na
   cascata como se fosse `* { ... }`. Troquei pra um seletor por `objectName`
   (`QWidget#veuModal{...}`), que não vaza. **Isto teria afetado a volta anterior também** (o painel
   de Configurações já existia lá) — não percebi porque nunca tinha comparado lado a lado com a
   referência antes desta tarefa.
3. O painel de Consumo (`42rem` no CSS de origem — pensado pra uma página cheia) estourava a
   largura da nossa janela pequena (`40rem`) e cortava o conteúdo por baixo, sem rolagem. Corrigido:
   largura do painel nunca passa da largura da janela menos margem, corpo do painel rola dentro de
   altura fixa (`QScrollArea`).
4. A linha do tempo não tinha marca de hora no eixo (a da web tem `3:00h`, `06h`...). Adicionadas.

### O que não testei, e por quê
- **Atalho físico com outra janela em foco, e microfone real** — sem hardware neste ambiente (mesma
  limitação de sempre).
- **F3 na prática** (troca de dispositivo valendo na gravação seguinte) — só a lógica de resolução.
- **A roda do mouse sobre a linha do tempo** — **não implementada** por decisão consciente de
  escopo (justificativa completa no README): a `SPEC-002` pede "zoom, navegação por dia e janela
  deslizante de 24h" sem exigir o gesto de roda especificamente; implementei os três por
  clique/arraste (`QSlider` + botões) e cortei só o gesto. Sinalizando aqui, como a tarefa pediu,
  em vez de entregar escondido.

### Achado no uso ao vivo, durante esta mesma tarefa (fora do escopo, não consertado)
O usuário tentou mapear o atalho num botão do mouse (Redragon) usando a captura da interface e o
software do mouse enviou uma combinação de **4 teclas soltas, sem modificador** (`=+a+esc+n`). O
`keyboard.add_hotkey` precisa ver todas as teclas de um combo pressionadas **ao mesmo tempo**; um
mouse em modo "macro" manda as teclas em sequência rápida (aperta-solta uma por vez), então o combo
raramente fica "todo pressionado junto" — o atalho passou a disparar de forma inconsistente ("não
limpa quando clica de novo"). Não é bug do app: expliquei ao usuário (trocar o botão do mouse para
modo "atalho de teclado"/"shortcut" em vez de "macro", preferencialmente uma tecla única da faixa
F13–F24) e revertido o `config.json` para `ctrl+alt+space` como paliativo. **Registro como achado de
produto**: a captura de atalho (`CapturaAtalho`/`keyboard.read_hotkey`) aceita qualquer combinação
sem avisar que combos de várias teclas soltas (sem modificador) são frágeis — poderia validar/avisar
na hora da captura. Não implementei (fora do escopo desta tarefa, é uma tarefa de UX própria) —
deixo para o PM decidir se vira demanda.

### Critério de pronto
- [x] `SPEC-002` A a I no app rodando — A a H conferidos (herdados + novos), I conferido pelo método
      de captura de tela (achados acima, corrigidos).
- [x] Menu ⋮ com os três itens; Enviar arquivo pelo mesmo caminho da gravação, nome/extensão reais
      preservados — testado com `audio-teste/fala-real.wav`.
- [x] G1 a G5 contra `GET /consumo` real, com dado de verdade (99 requisições, histórico de dias,
      `US$ 0,20428` na sessão — números batendo entre o app e a mesma consulta feita à mão).
- [x] Painel de consumo com núcleo desligado: testado apontando pra uma porta inexistente (sem
      derrubar o backend real do usuário) — erro visível, app não travou.
- [x] Aparência conferida pelo método das capturas, divergências corrigidas e listadas acima.
      Imagens e scripts apagados ao final.
- [x] QSS única, cores em constantes nomeadas (`PALETA`).
- [x] Janela sempre no topo sem roubar foco; atalho global alterna e é configurável — **mecanismo
      confirmado**, mas a captura em si tem uma fragilidade real de UX com combos sem modificador
      (ver achado acima).
- [x] Erros do núcleo por `codigo`, na transcrição e agora também no consumo.
- [x] `desktop/README.md` atualizado, lista do que falta encolhida ao decidido.
- [x] Logs soltos removidos da regra do git (`.gitignore`); os arquivos em si ainda estão no disco
      porque dois processos de teste (PID 2860 e 50708) seguem abertos com o handle preso — inofensivo
      (já ignorado pelo git), mas só some de verdade quando esses processos forem fechados.
- [x] Nada em `transcritor/` alterado.
- [x] Repositório pronto para commit — `git status` só mostra os arquivos da lista + `app.log` (novo,
      não ignorado de propósito). **Não commitei.**

### Novas demandas / riscos
- **UX da captura de atalho**: considerar validar/avisar quando o combo capturado tem várias teclas
  sem modificador (frágil com mouse em modo macro) — achado no uso ao vivo desta tarefa, não
  implementado (fora de escopo).
- Duas instâncias do app ficaram rodando ao longo da tarefa (uma da volta anterior, uma de teste
  meu) — o usuário sabe e decide quando fechar; não fechei nenhuma sem avisar.
- `JANELA_MINUTOS_LINHA_TEMPO` (10 minutos, escala "minuto" da linha do tempo) é uma constante
  meu, não um número da spec — se o usuário achar a janela grande/pequena demais no uso real, é só
  ajustar essa constante.

### Ajuste no plano necessário?
Não — cobre `SPEC-002` A a I inteira, conforme pedido. A única decisão de escopo tomada (cortar o
gesto de roda da linha do tempo) foi sinalizada, não escondida, como a tarefa instruiu.

## [2026-08-27] — Fase 2, Etapa 1 (quarta volta): App de desktop — acabamento visual, janela estável, Consumo em janela própria, arrastar-soltar
Status: concluído
Nível `curto` (declarado), com a lista de achados da conferência visual fora do teto.

### Contexto
Segunda rodada de acabamento vinda do uso real em 2026-08-27, depois da volta anterior (paridade A
a I). Relatos: botões com "margem quadrada", cor forte e chevron no `⋮`; janela "redimensionando
toda vez que acontece alguma coisa"; e o mais grave — *"a parte de consumo ficou uma bela porcaria.
O fundo ficou preto e não dá pra ver nada que tá escrito. Ficou muito desproporcional... tá até
vazando da tela."* Nasceram `D-30` (divergências do desktop em relação à web, todas declaradas na
spec) e a seção **J** (a janela não se mexe sozinha).

### Feito
- **Botões redondos de verdade** (`estilizar_botao_circular`, estilo direto por widget — não pela
  regra genérica de `QPushButton`, que era a causa raiz das duas queixas: produzia cantos
  arredondados em vez de círculo nos botões de 44/32/28px, e pintava um **retângulo cinza atrás do
  círculo roxo** do botão de gravar). Fundo leve `#eef1f5`/hover `#dde3e9`. `⋮` trocou `setMenu()`
  por `clicked` + `QMenu.popup()` — sem chevron.
- **Trio ⋮·gravar·cancelar encostado e centralizado** (vão de 10px) — a causa raiz também já
  localizada pela tarefa: dois `addStretch` nas pontas empurravam os botões pra fora, e eu confirmei
  isso comparando o centro X do botão de gravar com o cancelar escondido/visível (idêntico depois
  do conserto, ver "Critério de pronto").
- **Interruptor desenhado à mão** (`Interruptor`, `QPropertyAnimation` de 0,15s) — trilho azul/cinza
  + bolinha branca deslizando, substituindo o `QCheckBox` estilizado (reprovado: "não é um
  interruptor"). Usado em Streaming e Recortar.
- **`J` — janela de tamanho estável**: removi todo `.hide()/.show()/.setVisible()` de cronômetro,
  faixa de amplitude e botão de cancelar — agora só o **conteúdo** muda (texto vazio, faixa em
  repouso, ícone/enabled do cancelar), nunca a presença no layout. Testado: `janela.size()`
  idêntico antes/depois de iniciar e de parar a gravação.
- **Balão flutuante (`B4`)**: `Toast` deixou de ser um `QLabel` no layout (que alternava
  `setFixedHeight` entre 0 e 32 — uma das causas do redimensionamento) e virou filho do cartão,
  posicionado por `move()` logo acima do botão de gravar, `raise_()` por cima do conteúdo. Confirmação
  agora em **3s** (era 2s).
- **Consumo em janela própria** (`QDialog(janela, Qt.Window)`, 900×600, redimensionável) — não é
  mais um `OverlayModal` dentro da janela pequena. **Duas causas do "fundo preto" achadas e
  corrigidas**: (1) `GraficoBarrasDiario` e `LinhaDoTempoConsumo` são widgets desenhados à mão que
  nunca pintavam o próprio fundo — adicionei `pintor.fillRect(self.rect(), branco)` no início do
  `paintEvent` dos dois; (2) o painel de 42rem realmente não cabia nos 40rem da janela pequena — não
  se aplica mais, a janela de Consumo tem o tamanho dela. `PopupRequisicao` (G4) mudou de dono: agora
  é filho da janela de Consumo, não da janela de ditado — testado (`parentWidget()` confirmado),
  porque abrir o popup na janelinha pequena e distante do clique não faria sentido nenhum.
  `recortar_em_vez_de_copiar` **nasce ligado** (`CONFIG_PADRAO` e já estava assim no `config.json`
  do usuário). Corte de segurança em **300000ms (5min)**, mensagem do balão atualizada pra "5
  minutos".
- **Arrastar e soltar (E2)**: `setAcceptDrops(True)` na janela, `dragEnterEvent`/`dragLeaveEvent`/
  `dropEvent` — realça o botão de gravar com um anel azul enquanto o arquivo paira, recusa formato
  não aceito e mais de um arquivo **pelo balão** (nunca em silêncio), reaproveita
  `_disparar_transcricao` — o mesmo método que o Enviar arquivo (E1) chama, não um caminho novo.
- **Conferência visual de novo** (`QT_QPA_PLATFORM=offscreen` + `grab()`, script e imagens apagados
  ao final): parado, gravando-com-balão, processando, Configurações com o interruptor nas duas
  posições, e a janela de Consumo isolada (`grab()` direto nela, já que agora é uma janela separada
  da principal). Confirmei visualmente: círculos de verdade, sem retângulo atrás do roxo, sem
  chevron, trio junto, balão flutuando sem mexer no layout, interruptor com bolinha nas duas
  posições, Consumo com fundo branco de verdade e sem cortar conteúdo. **Nenhuma divergência nova**
  além do que já estava sendo implementado — o método desta vez serviu pra confirmar que os quatro
  achados da rodada anterior continuavam corrigidos depois da reescrita de layout.

### Critério de pronto
- [x] Nenhum botão com canto quadrado; `BotaoGravar` sem retângulo atrás; ⋮ sem chevron; fundo dos
      secundários em `#eef1f5` — conferido pela captura.
- [x] Janela não muda de tamanho ao gravar/parar/cancelar/balão/painel — **testado
      programaticamente** (`janela.size()` antes/depois), não só por leitura de código.
- [x] Balão acima do botão, discreto, 3s/6s, sem afetar layout — conferido.
- [x] Consumo em janela própria, legível, sem fundo preto, sem vazar, com rolagem — testado com
      `GET /consumo` real (109 requisições) e com o núcleo desligado (porta inexistente, sem tocar
      no backend do usuário).
- [x] Arrastar e soltar: lógica e caminho compartilhado com E1 testados; **o gesto de UI em si
      (arrastar de verdade com o mouse) não foi testado** — ver README.
- [x] Os quatro itens do bloco 6 (trio encostado, corte em 300s, recortar padrão ligado, interruptor
      animado) — todos conferidos, não só "não mexi".
- [x] Conferência por captura feita; achados listados aqui; imagens apagadas ao final.
- [x] `desktop/README.md`: Consumo em janela própria e arrastar-soltar registrados.
- [x] Nada em `transcritor/` alterado.
- [x] Repositório pronto para commit — `git status` só mostra os arquivos da lista + `app.log`
      (novo, não ignorado de propósito). Os quatro `.log` soltos de teste (`erro_app.log`,
      `saida_app.log`, `erro_smoke.log`, `saida_smoke.log`) seguem presos no disco por processos de
      teste antigos ainda abertos, mas já estão fora do `git status` (regra do `.gitignore` da volta
      anterior). **Não commitei.**

### Novas demandas / riscos
- **Achado no uso ao vivo, ainda sem solução** (reportado na volta anterior, continua): captura de
  atalho aceita qualquer combinação sem avisar que combos de várias teclas soltas (sem modificador)
  são frágeis com mouse em modo macro. Não implementado — fora de escopo desta tarefa.
- Duas instâncias antigas do app (de tarefas anteriores) ainda podem estar rodando, prendendo os
  `.log` soltos — inofensivo, só resolve quando o usuário fechar essas janelas.
- Não testei o gesto de arrastar-e-soltar com o mouse de verdade, nem a animação do interruptor em
  movimento — ambos exigem interação humana ou captura de vídeo, fora do alcance deste ambiente.
- Tentei complementar a conferência `offscreen` com um screenshot da tela real (mesmo método que
  confirmou a paridade em tarefas anteriores) e a captura saiu cortada à direita, sem o botão de
  cancelar visível — nas duas tentativas, com `GetWindowRect`/`CopyFromScreen` via PowerShell. Não
  reproduz no teste automatizado (que mede `janela.size()` e a posição X do botão de gravar
  diretamente, sem depender de screenshot) nem no `grab()` offscreen, que mostrou o trio completo e
  corretamente espaçado. Julgo mais provável ser um artefato de DPI da minha ferramenta de captura
  neste monitor (a máquina tem um desktop virtual de ~4650px, sugerindo múltiplos monitores com DPI
  misto) do que um bug do app — mas registro em vez de descartar, porque não consegui confirmar a
  causa. Se a janela real aparecer cortada para o usuário, vale reabrir.

### Ajuste no plano necessário?
Não — os cinco itens (botões, janela estável, balão, Consumo em janela própria, arrastar-soltar) e
o bloco 6 foram cobertos, com o que não deu para testar listado, não escondido.

## [2026-08-27] — Fase 2, Etapa 1 (quinta volta): painel de consumo refeito do original + quatro correções visuais
Status: concluído

### Feito
- `desktop/app.py`: painel de consumo (`G1`-`G6`) reescrito do zero a partir da leitura de
  `transcritor/frontend/index.html` (comentário "Linha do tempo das requisições" até
  `carregarConsumo()`) e da `SPEC-002` G1-G6. `LinhaDoTempoConsumo` virou um widget pintado à mão
  dentro de um `QScrollArea`, com as duas escalas ("hora" = um dia civil, sem rolar; "minuto" =
  janela móvel de 3 min dentro das últimas 24h, largura fixa ~2790px, rola) e navegação própria de
  cada uma (dia anterior/seguinte com limites; deslizador + Início/Mais recente), escada de passos
  do eixo em fronteira de relógio (`_escolher_passo_eixo`/`_primeira_marca_alinhada`, com o carry
  entre unidades verificado em teste unitário), estado "ativada" por clique (roda desliza/navega
  dias quando ativada, troca de escala quando não — replicado do `wheel` listener do JS, não do
  resumo da `SPEC-002`, ver "Novas demandas"), alvo de clique raio 14 sobre ponto raio 4, preço
  acima do ponto só na escala minuto, e a flag de "rolar para o fim" só nos momentos corretos
  (abrir, trocar escala, botão "Mais recente" — nunca ao deslizar). `GraficoBarrasDiario` (G2)
  virou colunas reais (não mais um canvas), com mínimo de 4px, rótulo `mm-dd` e dica de foco.
  `PainelConsumo._construir_lista_diaria` (G2) monta a lista com filete entre dias. Sessão (G1)
  virou três linhas (Requisições/Tokens/Custo estimado). Custo em todo o painel padronizado para
  quatro casas (`formatar_usd`/`formatar_usd_compacto`), como o `toFixed(4)` do JS.
- `BarraAmplitude` (B.1): `paintEvent` não desenha nada quando `self._gravando` é falso; o espaço
  (`setFixedHeight`) continua reservado. `reiniciar()` passou a exigir o argumento `gravando`;
  ajustados os dois pontos que chamavam (`iniciar_gravacao`/`_parar_temporizadores_e_stream`).
- `CamadaPulso` nova (B.2): widget 110px, filho do cartão (não do botão), `WA_TransparentForMouseEvents`,
  reposicionado sobre o centro do `BotaoGravar` (`resizeEvent` + `QTimer.singleShot(0, ...)` para a
  primeira abertura) e `lower()` no empilhamento. `BotaoGravar` só desenha mais o círculo e o
  ícone/spinner; pulso e realce de arrastar saíram do seu `paintEvent`.
- `Toast` (B.4): `setWordWrap(False)`, altura fixa, largura calculada com `QFontMetrics` (texto que
  não cabe é cortado com `elidedText`, texto inteiro no `setToolTip`), reposicionado a partir do
  centro do botão. **Achado e corrigido durante a própria conferência visual**: o cálculo de
  largura máxima usava `self._ancora.window().width()`, mas `self.move()` usa coordenadas do parent
  em comum com a âncora (o cartão, não a janela) — como o cartão tem exatamente a mesma largura que
  a "janela menos margem", o balão longo ficava encostado nos cantos arredondados do cartão em vez
  de ter margem. Troquei para `self.parentWidget().width()`; confirmado por captura antes/depois
  (ver "como testei").
- QSS: `QComboBox QAbstractItemView`/`::drop-down` (B.3 — fundo branco, texto `#1f2933`, selecionado
  `#2563eb`/branco), `QScrollBar` (vertical e horizontal), `QScrollArea`/`QScrollArea > QWidget >
  QWidget` (fundo) e `QMenu`/`QMenu::item:selected`, aplicados de uma vez (pedido explícito da
  tarefa: "varra os outros de uma vez").

### Como testei
Com o **núcleo real já rodando** (porta 8000, `consumo.jsonl` com 780 requisições reais entre
18/08 e 27/08) e `QT_QPA_PLATFORM=offscreen` + `QT_QPA_FONTDIR=C:\Windows\Fonts` (sem a segunda
variável o Qt offscreen não acha fonte nenhuma e todo texto sai como □□□ — não é bug do app, é do
ambiente de teste). Também abri `transcritor/frontend/index.html` com Playwright/Chromium contra o
mesmo núcleo, para comparar as duas capturas lado a lado de verdade (o critério de pronto pede
isso). Sessão (Requisições: 10, Tokens: 2615, Custo: US$ 0.0096), histórico diário e gráfico batem
número a número entre as duas capturas. Escala "minuto": mesma janela (`11:49:34 – 11:52:34`, texto
completo da janela de 24h) e o mesmo ponto com `$0.0007` nas duas capturas. Popup da requisição:
mesmo formato `modelo — US$ 0.0007 — data`. Troquei de escala "hora" → "minuto" e confirmei que a
âncora seguiu o dia que estava selecionado (não voltou para "agora"). Testei também o painel com o
núcleo apontando para uma porta errada (G5): mensagem de erro aparece, nada de painel vazio sobra.
Testei unitariamente `_primeira_marca_alinhada` com os quatro carries (segundo→minuto,
minuto→hora, hora→dia, dia exato) — todos corretos. Não testei: clique/Enter/Espaço em cada ponto
por teclado (só clique do mouse — ver riscos), a animação do pulso/spinner em movimento (só frames
estáticos via captura), e o gesto de roda de verdade (testei as funções que o `wheelEvent` chama,
não o evento do sistema operacional).

### Critério de pronto
- [x] `G1` a `G6` conferidos item a item contra o original aberto ao lado (Playwright + captura
      offscreen, ver "como testei").
- [x] As duas escalas funcionando, com navegação própria e concordando sobre o período ao trocar.
- [x] Marcas do eixo em fronteira de relógio, com `dd/mm` na primeira e em cada virada de dia.
- [x] Roda: desliza a janela/navega dias com a linha do tempo ativada, troca de escala sem ativar
      (ver "Novas demandas" — diverge do texto da `SPEC-002`, segue o JS).
- [x] Deslizar não pula para o fim; abrir, trocar de escala e os botões de ponta pulam.
- [x] Clique num ponto abre a transcrição com horário, modelo e custo.
- [x] Painel legível, nada preto, nada vazando, tudo com rolagem — com dado real e com o núcleo
      desligado.
- [x] Parte B, os quatro itens — conferidos por captura (ver acima).
- [x] Conferência por captura feita, incluindo o consumo nas duas escalas, lado a lado com a web
      via Chromium; achados listados acima e corrigidos (Toast); imagens apagadas ao final.
- [x] Nada em `transcritor/` alterado.
- [x] Repositório pronto para commit — `git status` só mostra `desktop/app.py` (`app.log` ganhou e
      perdeu as mesmas linhas de teste; conferido com `git diff` que voltou a ficar idêntico ao
      commit). **Não commitei.**

### Novas demandas / riscos
- **Lacuna da SPEC-002, achada na leitura do original**: G3 diz "sem ativar, a roda rola a janela
  como qualquer conteúdo" — mas o `wheel` listener real do `index.html` (linha ~1613) faz
  `evento.preventDefault()` e **troca de escala** quando não ativada; só chama scroll nativo com
  Shift pressionado. Implementei o que o JS faz (dono único), não o que a frase resume. Sugiro
  corrigir essa frase na spec.
- **Bug pré-existente, fora do escopo desta tarefa, achado na conferência visual**: o véu escuro do
  `OverlayModal` (usado por `PainelConfiguracoes` e `PopupRequisicao`) não pinta — é um `QWidget`
  puro estilizado por QSS sem `WA_TransparentForMouseEvents`... corrigindo: sem
  `WA_StyledBackground`, então o `background-color` do QSS nunca é aplicado (o comentário do próprio
  código já explica a regra para o `painel` branco, mas não foi aplicada ao véu). Confirmei com
  captura + amostra de pixel (fundo permanece `(255,255,255)` atrás do popup). Não é um dos quatro
  itens da Parte B, então **não mexi** — só registro.
- Não testei ativação por teclado (Enter/Espaço) de um ponto específico da linha do tempo — o
  original faz isso via `tabindex`/foco em cada ponto SVG; o widget pintado à mão só responde a
  clique do mouse. O critério de pronto desta tarefa só pede clique; registrando para o PM avaliar
  se entra como pendência.
- Duas instâncias antigas do app mencionadas na volta anterior — não investiguei de novo, fora do
  escopo desta tarefa.

### Ajuste no plano necessário?
Não — Parte A (consumo) e Parte B (quatro correções) cobertas, com o que não testei e os achados
fora de escopo listados acima, não escondidos.

## [2026-08-27] — Fase 2, Etapa 1 (sexta volta): dois achados do usuário rodando no Windows real
Status: concluído

### Feito
- `desktop/app.py`: `CamadaPulso` ganhou `setStyleSheet("background: transparent;")`. Achado do
  usuário: no Windows real ela aparecia como uma caixa quadrada opaca cobrindo o botão `⋮` vizinho.
  O `grab()` offscreen (ferramenta de conferência desta tarefa) não reproduziu — a plataforma
  offscreen não aplica o mesmo comportamento nativo do Qt de pintar fundo opaco em `QWidget` puro
  assim que qualquer QSS está na cadeia de pais (é a mesma causa do "retângulo cinza atrás do
  círculo" que o `BotaoGravar` já evitava com este mesmo truque, só que eu não tinha copiado o
  truque para a camada nova).
- Menu `⋮`: troquei os três `QMenu.addAction(icone, texto)` por `QWidgetAction` com um `ItemMenuAvancado`
  próprio (ícone + texto num `QHBoxLayout` com `spacing=10`). **Minha primeira tentativa (rodada
  anterior) foi inflar o pixmap com margem transparente à direita — o usuário reportou que só
  encolheu o ícone e a margem continuou ausente.** Causa: a coluna do ícone num `QAction` nativo
  tem largura fixa dada pelo estilo/plataforma, não pelo tamanho do pixmap — o ícone mais largo só
  é reamostrado para caber na mesma coluna, perdendo tamanho sem abrir espaço nenhum. Widget próprio
  contorna o problema por completo (o `QHBoxLayout` é meu, não do estilo).

### Como testei
`QT_QPA_PLATFORM=offscreen` + `QT_QPA_FONTDIR` (mesmo método das voltas anteriores): capturei
`menu_avancado.popup(...)` isolado — os três itens saem com ícone em tamanho cheio (18px) e um vão
visível antes do texto. **Não pude confirmar a `CamadaPulso` pela mesma via**, porque a plataforma
offscreen não reproduz o bug relatado (ver "Feito") — o usuário quem confirma isso rodando de novo.

### Critério de pronto
- [x] Margem entre ícone e texto no menu `⋮` — capturada, com vão visível.
- [ ] Camada do pulso deixou de aparecer como caixa quadrada sobre o botão `⋮` — corrigido pelo
      mesmo padrão já usado no `BotaoGravar`, mas **não confirmável neste ambiente** (ver acima);
      pendente de confirmação do usuário no próximo uso real.

### Novas demandas / riscos
- A ferramenta de conferência visual desta tarefa (`grab()` offscreen) não reproduz bugs de fundo
  opaco que só aparecem com o estilo nativo do Windows — um limite do método, não só desta tarefa.
  Vale lembrar disso da próxima vez que um "widget deveria ser transparente" for alterado.

### Ajuste no plano necessário?
Não — os dois achados do usuário foram corrigidos; o segundo depende de confirmação dele no app
rodando de verdade.

## [2026-08-27] — Fase 2, Etapa 1: três defeitos verificados pelo PM (véu, teclado na linha do tempo, config.json)
Status: concluído

### Feito
- `desktop/app.py` `OverlayModal`: `setAttribute(Qt.WA_StyledBackground, True)` no véu — confirmado
  por amostra de pixel (era `(255,255,255)`, agora `(142,146,156)` atrás do painel).
- `LinhaDoTempoConsumo` (G4): `setFocusPolicy(Qt.StrongFocus)`, `←/→` movem um ponto focado em
  ordem de tempo, `Enter`/`Espaço` abrem a requisição, anel de foco (2px `#2563eb`, 2px de folga)
  só enquanto `hasFocus()`; índice reseta a cada `atualizar()` (escala/dia/janela mudou, o índice
  antigo apontaria pro ponto errado). `area_linha_tempo.setFocusProxy(linha_tempo)` para o `Tab`
  alcançar o widget dentro do `QScrollArea`. Testado por envio de `QKeyEvent` direto (o
  `hasFocus()` real não é confiável em `offscreen`): `→,→,←,Enter` moveu 0→1→0 e ativou o ponto 0.
- `desktop/config.json`: `salvar_config` agora escreve com `newline="\n"` e quebra de linha final.
  Normalizei o arquivo atual com a própria função (preserva os valores do usuário — conferido:
  `atalho: "shift+esc+Ç"`, `recortar_em_vez_de_copiar: true` intactos) e confirmei que escrever de
  novo por cima é **idêntico byte a byte** (round-trip estável, não gera diferença de novo).
- `.gitattributes` (novo, raiz): `*.json text eol=lf`.
- Também nesta janela de trabalho, a pedido direto do usuário (fora dos três itens, achado ao
  rodar): alinhei a borda direita do menu `⋮` com a do botão (ele é o mais à esquerda do trio; o
  menu abria para a direita, por cima do botão de gravar e do cancelar).

### Critério de pronto
- [x] Véu escurecendo de verdade, conferido por amostra de pixel.
- [x] Ponto da linha do tempo alcançável e ativável pelo teclado, com foco visível — a navegação e
      ativação foram testadas via evento sintético; **o anel de foco em si (`hasFocus()`) só é
      confirmável no uso real**, porque a plataforma `offscreen` não ativa janela de verdade.
- [x] `git status` limpo depois de abrir e fechar o app — nenhum handler de `salvar_config` roda
      sem interação do usuário nas Configurações, e o round-trip é idêntico byte a byte quando roda.
- [x] Nada em `transcritor/` alterado.
- [x] Repositório pronto para commit — **sem commitar**. `git status` mostra só `desktop/app.py`,
      `desktop/config.json` (a normalização, deliberada) e `.gitattributes` (novo) como meus;
      `.claude/estado/PLANO.md`, `PROXIMA_TAREFA.md`, `coleta/...`, `spec/MAPA.md` e `SPEC-002`
      aparecem modificados também, mas são do PM, não desta tarefa — não mexi neles.

### Novas demandas / riscos
- O anel de foco pelo teclado (item 2) está implementado e a lógica testada, mas o próprio
  `hasFocus()` — e portanto o anel aparecendo na tela — só é confirmável rodando de verdade
  (mesmo limite do método já registrado na volta anterior).

### Ajuste no plano necessário?
Não — os três itens (véu, teclado na linha do tempo, config.json + `.gitattributes`) foram
cobertos, com o que só o uso real confirma listado, não escondido.

## [2026-08-27] — D-31, fora do plano da Fase 2: Gerar imagem (núcleo + app de desktop)
Status: concluído

### Feito
- `transcritor/backend/main.py`: `POST /gerar-imagem` (Operação 3) — multipart, até 16 imagens de
  referência, chama `images.edit` da OpenAI (`gpt-image-1.5` padrão, `input_fidelity=high`).
  `_calcular_custo_usd` ganhou um branch para o formato de `usage` da geração de imagem
  (`input_tokens_details.{text_tokens,image_tokens}`, sem `type`) na MESMA tabela
  `PRECOS_POR_TOKEN_USD` e chamando a MESMA `_registrar_consumo`/`_registrar_transcricao` das
  transcrições — sem duplicar o caminho de gravação. `_erro_api_para_codigo` ganhou um parâmetro
  para não sugerir "arquivo de áudio" num erro de imagem.
- `spec/contrato/NUCLEO.md`: Operação 3 documentada com captura real (sucesso, tabela de preços,
  cinco erros medidos).
- `desktop/app.py`: `JanelaGeracaoImagem` (menu ⋮, 4º item) — três formas de escolher referência
  (arquivos/pasta/arrastar-soltar) com miniaturas removíveis e contagem `N de 16`, prompt,
  opções com custo estimado, `Gerar` (desabilitado sem prompt/imagem), carregando explícito,
  resultado com preview + custo real + salvamento automático em `pasta_saida_imagens` + Salvar
  como/Abrir pasta. `TrabalhoGeracaoImagem` (QThread, timeout 320s) chama a rota nova.
- `desktop/config.json`/`CONFIG_PADRAO`: `modelo_imagem`, `tamanho_imagem`, `qualidade_imagem`,
  `pasta_saida_imagens`.
- `desktop/README.md`: seção "Gerar imagem" nova.

### Como testei
Com o núcleo reiniciado (avisei e o usuário autorizou antes) e chamadas **reais** à API da OpenAI
(o usuário autorizou o custo real antes de começar): duas imagens de referência (vermelho/azul) +
prompt pedindo um degradê — a API devolveu um PNG 1024×1024 de verdade, decodificado e conferido.
Cinco erros reais provocados contra o núcleo: `PROMPT_VAZIO`, `FORMATO_NAO_ACEITO`,
`IMAGENS_DEMAIS`, `MODELO_INVALIDO` (com `dall-e-2` — ver riscos), `TAMANHO_INVALIDO`. Confirmei
`GET /consumo` trazendo a geração de imagem misturada com as transcrições, custo não-zero. No app:
testei a janela ponta a ponta (adicionar/remover referência, contagem, custo estimado mudando com
a qualidade, `Gerar` habilitando/desabilitando) e o sucesso via uma resposta real da API — a
imagem apareceu, foi salva sozinha em `imagens-geradas/AAAA-MM-DD_HHMMSS.png` (conferido no disco,
PNG válido 1024×1024), e via uma chamada sintética (mesmo formato de resposta) confirmei preview,
custo real formatado, botões de resultado e o botão `Gerar` reabilitando. Fluxo de ditado
reconferido no final: enviei `audio-teste/fala-real.wav` pelo mesmo caminho de sempre — texto real
voltou, `processando` voltou a `False`. `config.json` conferido byte a byte no final (só os 4
campos novos, valores padrão reais — não sobrou nenhum valor de teste).

### Critério de pronto
- [x] Usuário avisado antes de mexer no backend (autorizou por `AskUserQuestion`); núcleo no ar ao
      final (`GET /consumo` respondendo `200`).
- [x] `POST /gerar-imagem` funcionando numa chamada real. Prompt: *"Combine as duas cores de
      referência num degradê diagonal simples, sem texto"*; custo devolvido: `US$ 0,0818`.
- [x] Dois erros exercitados de verdade (na prática, cinco — ver acima).
- [x] Custo aparecendo no painel de Consumo, na linha do tempo, valor não-zero — conferido.
- [x] `NUCLEO.md` com a Operação 3 medida.
- [x] Escolher arquivos, escolher pasta e arrastar-soltar — os três testados (arrastar-soltar só a
      lógica de `dropEvent`/`_adicionar_imagens`, sem simular o gesto do sistema operacional).
- [x] Imagem salva automaticamente, caminho visível na tela.
- [x] Custo estimado visível antes de gerar; custo real visível depois.
- [x] Ditado reconferido ao final, sem quebra.
- [x] Repositório pronto para commit — **sem commitar**. `git status` mostra só os 5 arquivos da
      lista da tarefa como meus (mais `.gitattributes`, da tarefa anterior); os demais modificados
      (`PLANO.md`, `PROXIMA_TAREFA.md`, `coleta/`, `DECISOES.md`, `MAPA.md`) são do PM.

### Novas demandas / riscos
- **A tarefa original citava preços e um modelo errados — corrigido, não só registrado**: o
  rascunho desta tarefa dizia "acrescente os modelos de imagem com os preços... texto de entrada
  US$5/M, imagem de entrada US$10/M, saída US$40/M" — **esses são os preços de `gpt-image-1`, não
  de `gpt-image-1.5`** (o modelo pedido como padrão). Busquei a página oficial antes de fixar
  (`developers.openai.com/api/docs/pricing`, 2026-08-27): `gpt-image-1.5` é US$5/US$8/US$32. Usei
  os preços certos do modelo certo; o valor errado ficaria em silêncio (mesmo bug que o `NUCLEO.md`
  já documentava para `gpt-4o-transcribe-diarize`) se eu tivesse copiado o rascunho sem checar.
- **`dall-e-2`, que a tarefa listava como modelo aceito, foi removido da API da OpenAI em
  2026-05-12** — não entrou na lista de modelos permitidos (confirmado por busca; testado que o
  backend rejeita com `MODELO_INVALIDO` em vez de deixar a chamada falhar do lado da OpenAI).
- **Custo real bem mais alto que a estimativa de saída sozinha** (US$ 0,075–0,082 medido contra
  US$ 0,009–0,034 estimado) porque a estimativa mostrada antes de gerar não conta as imagens de
  referência — isso está dito na tela e no README, mas registro aqui para o PM avaliar se uma
  estimativa melhor (contando o tamanho real das referências escolhidas) vale a pena depois.
- **Gastei mais que uma chamada de teste** — três tentativas de testar o caminho completo
  app→núcleo esbarraram em uma instabilidade do meu próprio ambiente de teste (não do app: threads
  do Qt que terminavam depois do processo de teste morrer, então a chamada completava no núcleo
  mesmo sem eu observar o resultado no cliente) e cada uma já tinha sido enviada de verdade à API
  antes de eu perceber. Gasto total estimado desta tarefa: ~US$ 0,40 (dentro da faixa que o usuário
  autorizou por chamada, só que em mais chamadas do que o estritamente necessário). Nenhuma
  imagem/pasta de teste ficou no repositório — apaguei tudo ao final.
- Não simulei o gesto real de arrastar-e-soltar do sistema operacional (mesmo limite já registrado
  para o E2 da paridade) — testei a lógica que o `dropEvent` chama, não o evento do SO em si.
- **Achado no uso real, depois de entregue**: o usuário rodou o app de verdade e ele **derrubou**
  bem na hora de processar uma geração de imagem real (chamada cobrada, `US$ 0,102746`, confirmada
  em `consumo.jsonl`). Conferido no Visualizador de Eventos do Windows: falha nativa dentro do
  próprio `Qt6Core.dll` (`0xc0000409`, sempre no mesmo endereço interno) — **não é uma exceção
  Python, nenhum `try/except` pega isso**. Achei uma segunda ocorrência idêntica hoje mais cedo
  (04:20, sessão anterior, sem relação com geração de imagem — no meio de uma sequência de trocas
  de atalho global), então parece instabilidade do Qt/PySide6 nesta máquina, não um bug isolado
  desta função — não consegui (nem tentei, foge do escopo de editar Python) corrigir o Qt em si.
  **O que dava para corrigir, corrigi**: `_ao_gerar_sucesso` salvava em disco só depois de montar
  a pré-visualização (`QPixmap`/`scaled`) — exatamente o trecho mais pesado de Qt, e o que rodava
  no momento do crash. Inverti a ordem: agora salva primeiro, monta a pré-visualização depois — se
  crashar nessa segunda parte de novo, a imagem (já paga) sobrevive no disco. Testado com resposta
  sintética: salvamento com sucesso e com falha (pasta inválida) nos dois casos, sem gastar
  chamada real de novo. **Não corrigido**: a causa raiz do crash do Qt em si — fica como risco
  aberto, e o usuário perdeu uma imagem já paga nesta ocorrência (não recuperável; só o registro
  do custo ficou).
- **O app crashou de novo depois da correção acima** (mesmo endereço em `Qt6Core.dll`,
  `0xc0000409`) — e desta vez a inversão de ordem quase ajudou: o arquivo **chegou a ser criado**
  em `imagens-geradas/`, mas ficou com **0 bytes** (o crash interrompeu a escrita, não só a
  pré-visualização). Isso me fez revisar a hipótese: o crash acontece na janela de tempo em que a
  `TrabalhoGeracaoImagem` (uma `QThread`) termina e entrega o resultado à thread da GUI — e a
  primeira ocorrência (04:20, antes desta função existir) também envolvia uma `QThread`
  (`CapturaAtalho`) terminando e emitindo um sinal entre threads. Nos dois casos o sinal carregava
  um payload grande (a imagem inteira em base64, >1MB, no caso da geração). **Mudei
  `TrabalhoGeracaoImagem` para decodificar e salvar o arquivo em disco dentro da própria thread**,
  antes de emitir qualquer sinal — o sinal `sucesso` agora carrega só `(caminho, formato,
  custo_usd)`, não mais a imagem inteira; a GUI relê o arquivo do disco para a pré-visualização.
  Isso tira a persistência do dinheiro já gasto de qualquer dependência da GUI ou do sinal
  sobreviver, e reduz o que atravessa a fila entre threads (testando a hipótese, sem confirmá-la
  com certeza — não tenho como instrumentar um debugger nativo neste ambiente). Testado de novo
  com resposta sintética (sucesso e falha de pasta), sem gastar chamada real.
- **Ainda não confirmado no uso real** se esta segunda mudança evita o crash — só o usuário rodando
  de novo confirma. Se crashar uma terceira vez, o próximo passo seria investigar mais a fundo
  (talvez trocar `QThread` por outra abordagem de concorrência, ou isolar se é o `keyboard` — hook
  de teclado global — brigando com a thread do Qt) — mas isso já é além do que dá para resolver só
  editando os pontos que a tarefa pediu.

### Ajuste no plano necessário?
Não — Parte A (núcleo) e Parte B (interface) cobertas, com os achados de preço/modelo corrigidos
na hora (não só registrados) e o que não deu para testar listado, não escondido. O crash do Qt
achado depois da entrega é risco aberto, não ajuste de plano — corrigi o que dava (mover o
salvamento inteiro para dentro da thread de rede), não o Qt em si.

## [2026-09-05] — D-32, fora do plano da Fase 2: botão flutuante compacto (hover + estado)
Status: concluído

### Feito
- `desktop/app.py`, `JanelaDitado`: dois modos num método só (`_aplicar_modo`) — compacto 110×110
  (só o `BotaoGravar`; `FramelessWindowHint` + `WA_TranslucentBackground`, cartão sem fundo) e a
  janela cheia de hoje, sem nada mudado dentro dela. `_ancorar_pelo_botao` mantém o centro do botão
  de gravar no mesmo ponto da tela nos dois tamanhos e encaixa o resultado na `availableGeometry`.
- Hover: vigia da posição do cursor a cada 100ms (`_vigiar_ponteiro`), **não** `enterEvent`/
  `leaveEvent` — com filhos, o `leaveEvent` dispara a cada entrada num filho (era a fonte do
  flicker). Encolher passa por debounce de 250ms (`_timer_encolher`), cancelado se o mouse voltar.
- `_definir_estado_botao` substituiu as 9 chamadas diretas a `botao_gravar.definir_estado(...)`:
  gravando/processando expandem sozinhos; voltar a `parado` reavalia o encolher na hora.
- `_pode_encolher`: exige mouse fora **e** texto já colocado (`_resultado_pendente`, ligado em
  `_escrever_texto`, desligado em `_clicar_copiar`/`_apagar_com_snapshot`), sem gravação/
  processamento e sem menu ⋮, Configurações, Consumo ou Gerar imagem abertos.
- Arrastar sem moldura: `arraste_iniciar/_mover/_fim` na janela (fundo) + `mousePress/Move/Release`
  no `BotaoGravar` com limiar de 6px, que engole o clique quando o gesto virou arrasto.
- `QSS`: `QWidget#janelaDitado` passou a `background: transparent` (era `fundo_janela`) — sem isso
  o compacto seria um quadrado cinza em volta do círculo.

### Como testei
`QT_QPA_PLATFORM=offscreen` com PySide6 6.11.2 (instalado no meu ambiente; `keyboard` e
`sounddevice` substituídos por stubs, que este shell não tem nem teclado global nem áudio):
47 verificações, 0 falhas. Números reais: nasce `QSize(110, 110)` com caixa de texto, ⋮, copiar,
lixeira, cronômetro e barras escondidos; hover → `QSize(672, 480)`; sair e esperar 250ms → 110;
voltar antes dos 250ms cancela; gravando/processando ficam expandidos 400ms com o ponteiro
marcado fora. Âncora: centro do botão `QPoint(354, 204)` idêntico nos dois tamanhos e na volta.
Borda: nos três cantos de uma tela 800×800 a janela cheia coube inteira (ex.: `QRect(128, 320,
672, 480)`). Arrasto pelo botão no compacto `(300,300)→(340,325)` sem disparar o clique; press+
release parado ainda chama `iniciar_gravacao`; no expandido, arrasto pelo botão e pelo fundo.
Fluxo de ditado ponta a ponta contra um **núcleo falso local** (o núcleo real está fora do ar e o
`127.0.0.1` deste shell não é o da máquina do usuário): subi o `audio-teste/fala-real.wav` de
verdade pelo `_disparar_transcricao` — 1.026.704 bytes multipart recebidos, `RIFF` conferido,
texto entrou na caixa, `processando` voltou a `False`, balão apareceu, não encolheu com o texto na
tela e encolheu depois do recortar. Menu ⋮ com os quatro itens (`Configurações`, `Consumo`,
`Enviar arquivo`, `Gerar imagem`); Configurações, Consumo e a janela de Gerar imagem abrem e
travam o encolher. Regressão visual: comparei pixel a pixel a janela cheia antes/depois com
`grab()` — 44 pixels diferentes dentro do cartão, todos nos quatro cantos arredondados (o fundo
atrás deles virou transparente); o resto idêntico.
**Não testei**: o hover de mouse de verdade, o arrasto real sem moldura, o sempre-no-topo e a
translucidez renderizados no Windows (este shell não dirige GUI); gravação por microfone e
transcrição real contra o núcleo/OpenAI (núcleo fora do ar, inalcançável daqui — e não gastei
chamada paga); geração de imagem real (só a janela abrindo).

### Critério de pronto
- [x] App abre compacto (só o botão de gravar, sem moldura, sem caixa de texto nem menu visíveis).
- [x] Hover expande para a janela cheia de hoje, sem clique. — testado pelo vigia com
      `QCursor.setPos` dentro/fora; o gesto do mouse real fica para o usuário.
- [x] Gravando e processando expandem sozinhos, mesmo sem o mouse em cima — teste com o mouse longe
      da janela durante uma gravação real. — o "sem o mouse em cima" está testado; a gravação **real**
      de microfone não (sem áudio neste ambiente), só o mesmo caminho de código.
- [x] Encolhe só depois de colocar o texto (copiar ou recortar) **e** o mouse ter saído — confirme
      que tirar o mouse com o resultado ainda na tela e nada colocado **não** encolhe.
- [x] Arrastar a janela funciona nos dois tamanhos (compacto e expandido), sem moldura nativa. —
      com eventos de mouse sintéticos; o arrasto de verdade fica para o usuário confirmar.
- [x] Perto da borda da tela, a expansão não empurra a janela para fora da área visível.
- [ ] Nenhum flicker perceptível ao passar o mouse rapidamente sobre a borda do botão. — não dá para
      julgar "perceptível" sem tela real. O que dava para provar está provado (o debounce de 250ms e
      o cancelamento ao voltar); a expansão continua imediata, então uma passada rápida **expande** e
      volta a encolher 250ms depois — se isso incomodar, é caso de um debounce também na entrada.
- [x] Nada do fluxo de ditado, do menu ⋮ (Configurações · Consumo · Enviar arquivo · Gerar imagem)
      nem da geração de imagem quebrado — teste ao menos um de cada depois da mudança. — ditado
      ponta a ponta (núcleo falso, wav real), os quatro itens do menu e a janela de Gerar imagem
      abrindo; **nenhuma chamada paga à OpenAI**.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). — `git status` mostra só
      `desktop/app.py` como meu, mas o `.git/index.lock` de 27/08 **continua lá** (ver riscos).

### Novas demandas / riscos
- **`.git/index.lock` (0 byte, 27/08 16:01, resíduo do último commit feito pela pasta montada)
  bloqueia o próximo `git commit`.** Tentei apagar: `Operation not permitted` (limite conhecido da
  pasta montada, já registrado no `HIGIENE.md`), e o pedido de permissão de exclusão foi negado
  pelo classificador do ambiente. **O usuário precisa apagar na máquina**: na pasta do projeto,
  `del ".git\index.lock"`. Não é resíduo desta tarefa.
- **Sem moldura, a janela perdeu o botão de fechar.** Sobrou o `Alt+F4` (não confirmado no Windows
  real) e não há item "Sair" no menu ⋮. Não consertei — está fora do que a tarefa pediu, e a tarefa
  proibia inventar item de menu. Vale uma tarefa própria.
- **Ambiguidade da regra 4, resolvida no sentido mais defensável — o PM precisa confirmar.** A
  tarefa diz "encolhe só com o texto colocado **e** o mouse fora". Ao pé da letra, um hover à toa com
  a caixa vazia deixaria a janela cheia para sempre (nunca houve texto a colocar). Implementei
  "não encolhe enquanto houver resultado na tela ainda não colocado": caixa vazia + mouse fora
  encolhe; resultado na tela sem copiar/recortar não encolhe, que é o caso que a tarefa descreve.
  Digitação manual do usuário **não** marca pendência (só o texto que veio da transcrição).
- **Trava a mais, não pedida na tarefa**: painel/menu aberto impede o encolher. Sem isso, levar o
  mouse até a janela de Consumo ou Gerar imagem (que são janelas separadas) encolheria a janela
  principal por baixo do painel de Configurações, que é filho dela.
- `desktop/README.md` continua descrevendo o app que "abre na janela cheia". Não toquei — a tarefa
  não trazia lista de "Arquivos envolvidos" e eu me limitei ao `desktop/app.py`. Fica para o PM.
- A margem de 16px em volta do cartão, que era `#f4f6f8`, virou transparente (consequência do
  frameless + translúcido); `PALETA["fundo_janela"]` ficou sem uso. O balão (`Toast`) é escondido
  ao encolher — no compacto ele sairia cortado.
- **Risco não confirmável daqui**: `WA_TranslucentBackground` + `Qt.Tool` + frameless no Windows
  real. Se a composição falhar nessa máquina, o compacto pode aparecer com um quadrado atrás do
  círculo em vez de fundo transparente. Só o usuário rodando confirma.
- A posição inicial continua sendo a que o Qt escolher — agora numa janela de 110px sem moldura,
  pode ser menos óbvia de achar na primeira abertura. Não mexi nisso (não estava na tarefa).
- O crash do `Qt6Core.dll` registrado na entrada anterior (D-31) continua aberto e sem relação com
  esta mudança.
- Sobrou um `.claude/tmp/_teste_escrita.txt` (arquivo vazio de teste de escrita) que este ambiente
  não consegue apagar — está na pasta de rascunho, fora do controle de versão.

### Ajuste no plano necessário?
Não — o comportamento decidido na `D-32` está inteiro no código, com a ambiguidade da regra 4 e as
duas confirmações que dependem de tela real (hover/arrasto de verdade e a translucidez no Windows)
registradas acima em vez de escondidas.

## [2026-09-05] — Achado no uso real: janela nascia num vão sem monitor nenhum
Status: concluído

### Feito
- `desktop/app.py`, `JanelaDitado._montar_ui`: adicionado `self.move(...)` explícito para a tela
  primária logo depois do `resize` inicial. Achado ao vivo com o usuário ("não sei onde foi parar a
  janela", repetido em três aberturas seguidas): o desktop dele tem três monitores num layout com um
  **vão sem cobertura nenhuma** entre o principal e os outros dois (medido via `EnumWindows`/
  `GetWindowRect` do Windows: a janela nascia em retângulos como `(1923,737)-(2201,1256)` e
  `(1370,142)-(1647,660)`, caindo fora de qualquer monitor real). Isso já estava **registrado como
  risco** na entrada anterior (D-32, "a posição inicial continua sendo a que o Qt escolher... não
  mexi nisso") — o risco se confirmou na prática, então corrigi.
- A correção usa `QGuiApplication.primaryScreen().availableGeometry()`, a mesma família de chamada
  que `_ancorar_pelo_botao` (D-32) já usa nas trocas de modo — só que ali ela só roda depois de já
  existir uma posição válida (`ancorar=True`); a abertura inicial passa `ancorar=False` e nunca
  chamava nada equivalente. Não toquei em `_ancorar_pelo_botao` nem no fluxo de expandir/encolher.

### Como testei
Reiniciei o app de verdade (matando o processo antigo e subindo um novo) e conferi a janela por
`EnumWindows`/`GetWindowRect` via PowerShell: antes da correção, `(1923,737)-(2201,1256)` e
`(1370,142)-(1647,660)` (ambos fora de qualquer monitor real, medidos com
`System.Windows.Forms.Screen]::AllScreens`); depois da correção, `(780,127)-(1452,607)` — 672×480
(tamanho esperado, `_tamanho_expandido`), inteira dentro do monitor principal
(`0,0`–`1536,864`).

### Critério de pronto
- [x] Janela nasce dentro de um monitor real, confirmado por medição de tela (não só a olho).
- [x] Nenhum outro arquivo tocado; `_ancorar_pelo_botao`/D-32 intactos.
- [x] Repositório pronto para commit — **sem commitar**. `git status` mostra só `desktop/app.py`
      como meu nesta mudança.

### Novas demandas / riscos
- Não investiguei **por que** o Windows escolhe posições dentro do vão para esta janela específica
  (frameless + `Qt.Tool` + `WA_ShowWithoutActivating` provavelmente pulam a heurística normal de
  cascata do Windows) — só neutralizei o efeito com uma posição inicial explícita. Se o usuário
  reconfigurar os monitores, vale reconferir.
- O crash do `Qt6Core.dll` (D-31, registrado antes) continua aberto e sem relação com este achado.

### Ajuste no plano necessário?
Não — é a confirmação de um risco já registrado por outra volta, corrigido agora que apareceu de
verdade.

## [2026-09-05] — D-32, segunda volta: bug do encolhimento, compacto do tamanho do botão, transição animada
Status: concluído

### Diagnóstico do bug (nível completo — a causa não era nenhuma das três hipóteses da tarefa)
As três hipóteses levantadas na `PROXIMA_TAREFA` foram **descartadas por medição**, não por leitura:
- montei um ambiente headless de verdade (PySide6 6.11.2 + `QT_QPA_PLATFORM=offscreen`; faltava
  `libEGL.so.1`, resolvido com os `.deb` extraídos em `~/.local/qtlibs`, fora do repositório);
- rodei **três ciclos completos** pelo caminho ideal (clique no botão e atalho global, cursor de
  verdade via `QCursor.setPos` com o vigia de 100ms rodando): encolheu nos três;
- rodei uma **matriz de 48 combinações** (iniciar por clique × atalho; ponteiro dentro/fora/entra-e-sai
  durante o processamento; colocar pelo botão × não colocar; transcrição ok × falha; recortar × copiar),
  dois ciclos cada: nenhuma travou;
- rodei um fuzz de sequências aleatórias (entra/sai/gravar/parar/colocar/lixeira/menu/painéis) até o
  orçamento de tempo: nenhuma travou.
Ou seja: `_resultado_pendente` **é** resetado no caminho normal, os dois `QTimer` **são** reiniciados
(`_timer_vigia_ponteiro` é repetitivo, `_timer_encolher` é single-shot e re-armado a cada tique do
vigia) e **não** existe guarda de "já encolheu uma vez".

O que existe, e é uma trava permanente de verdade: `_resultado_pendente` era um **booleano guardado à
mão**, desligado em apenas dois lugares (`_clicar_copiar` no caminho de sucesso e
`_apagar_com_snapshot`). Qualquer outro caminho que mexesse no texto — apagar a caixa pelo teclado
(Ctrl+A/Del), `Ctrl+X` dentro da caixa, editar à mão, ou clicar em copiar com a caixa vazia (que sai
pelo `return` antes do reset) — deixava o sinalizador **ligado para sempre**. Com ele ligado,
`_pode_encolher()` devolve `False` em todos os ciclos seguintes: a janela encolhe da primeira vez e
nunca mais, que é exatamente o sintoma relatado. Num app de ditado, apagar uma transcrição ruim pelo
teclado antes de regravar é o gesto mais banal que existe — é o candidato mais provável ao que o
usuário fez entre o primeiro e o segundo ciclo.
**Honestidade sobre o limite**: não consegui reproduzir a sequência exata do usuário (este shell não
dirige a GUI do Windows). Por isso a correção tem duas camadas: (1) matar a trava na raiz, derivando
o estado em vez de guardá-lo; (2) uma rede de segurança no vigia (`_corrigir_tamanho_do_modo`) que
reassenta a janela no tamanho do modo se ela ficar em qualquer outro — se a causa real for do lado do
sistema de janelas (um `resize` que não pegou), ela se desfaz sozinha no tique seguinte, em 100ms.

### Feito
- `desktop/app.py`, `_resultado_pendente()` virou **função derivada** (`caixa_texto` vs.
  `_texto_colocado`) em vez de booleano; `_escrever_texto`/`_apagar_com_snapshot` não marcam mais
  nada e `_clicar_copiar` grava o texto colocado. Caixa vazia nunca é pendente.
- `desktop/app.py`, `_vigiar_ponteiro` + `_corrigir_tamanho_do_modo`: rede de segurança de 100ms.
- `desktop/app.py`, compacto: `LADO_JANELA_COMPACTA = 110` saiu; entrou `MARGEM_JANELA_COMPACTA = 8`
  e `_lado_compacto()` = `botao_gravar.height() + 2×8` = **88×88** medido contra o botão real de
  72×72 (se o botão mudar, a janela acompanha). O anel de arrastar-soltar (raio 39,5px) ainda cabe.
- `desktop/app.py`, animação: `_aplicar_modo` troca o layout na hora e leva o tamanho por
  `QPropertyAnimation` sobre a propriedade nova `progressoModo` (`InOutCubic`, **160ms** — meio da
  faixa 120–200 pedida: abaixo de ~120 não se lê como movimento, acima de ~200 atrasa o clique).
  A cada quadro: `resize` interpolado → `_reassentar_layout()` → `_ancorar_pelo_botao` **refeito
  contra o layout de verdade** (não interpolado), então o centro do botão fica parado quadro a
  quadro. `_assentar_modo` fecha com `setFixedSize` só no fim; `_layout_externo` passou a
  `SetNoConstraint` (senão o mínimo do layout expandido segurava todos os quadros do encolhimento).
- `desktop/app.py`, `_prender_botao_no_topo()`: mola no fim do layout do cartão, só no compacto.
  Sem ela, nos quadros do encolhimento o cartão ainda é alto e o layout centraliza o botão a ~240px
  do topo — a janela teria de subir ~160px para manter a âncora e, no canto superior da tela (onde
  este app nasce, `move(area+40,+40)`), o encaixe na tela impede: o botão pulava 39px. Achado com o
  teste de âncora quadro a quadro, não a olho.
- **Novo**: `desktop/testes_janela_compacta.py` (promovido do rascunho por ter valor — `HIGIENE.md`),
  suíte headless de 45 verificações, sem rede e sem custo.

### Como testei
`QT_QPA_PLATFORM=offscreen`, PySide6 6.11.2. `python desktop/testes_janela_compacta.py`:
**45 verificações, 0 falhas**, estável em duas execuções seguidas. Números reais: nasce
`QSize(88, 88)` (72 do botão + 2×8); **três ciclos completos** seguidos (gravar → transcrever →
recortar → mouse fora) voltaram a 88×88 nos três; o ciclo com a caixa apagada **pelo teclado** entre
eles também encolheu (é o caso que travava antes) e o ciclo seguinte continuou encolhendo; expandido
`QSize(672, 480)`. Âncora medida a cada 15ms durante as animações: desvio máximo do centro do botão
**0px** nos dois sentidos, e igual ao valor inicial no fim; a expansão e o encolhimento passaram por
pelo menos 2 tamanhos intermediários cada (prova de que não é resize instantâneo). Reversão: sair no
meio da expansão terminou compacto; voltar no meio do encolhimento terminou em 672×480 com a âncora
intacta. Debounce de 250ms sobreviveu (não encolhe na metade dele; voltar cancela). Arrasto no
compacto: pela janela (`+40,+25`) e pelo próprio botão com eventos sintéticos (moveu a janela e
**engoliu** o clique; clique parado ainda grava). Regressão fora do escopo, em script à parte:
janela expandida idêntica (`672×480`, cartão `QRect(16,16,640,448)`, 5 itens no layout do cartão, as
mesmas geometrias dos 8 widgets); ditado ponta a ponta contra um **núcleo falso local** com o
`audio-teste/fala-real.wav` de verdade — **1.026.704 bytes** multipart recebidos, `RIFF` conferido,
texto na caixa, recortar destravou o encolher; menu ⋮ com os 4 itens e Configurações, Consumo e
Gerar imagem abrindo e travando o encolhimento como antes. **Nenhuma chamada paga à OpenAI.**
**Não testei**: nada renderizado no Windows real — a suavidade percebida da animação, o hover de
mouse de verdade, o sempre-no-topo e a translucidez; gravação por microfone e transcrição real
contra o núcleo (fora do ar, inalcançável daqui).

### Critério de pronto
- [x] Bug do encolhimento diagnosticado (causa identificada e descrita no registro) e corrigido. —
      com a ressalva honesta acima: a trava encontrada é real e reproduzível, mas não pude confirmar
      que foi ela que o usuário disparou; daí a rede de segurança.
- [x] Teste headless de **dois ciclos completos** passando (não um só). — três, mais um quarto com a
      caixa apagada por fora dos botões no meio.
- [x] Compacto do tamanho do botão + margem pequena, medido contra o `BotaoGravar` real — não
      110×110. — 88×88 = 72 + 2×8, calculado do botão em tempo de execução.
- [x] Âncora (centro do botão fixo na tela) confirmada nos dois tamanhos, inclusive durante a
      animação. — desvio máximo 0px, amostrado a cada 15ms.
- [x] Expandir e encolher animados, com interrupção/reversão segura se o mouse mudar de lado no meio
      da animação.
- [x] Arrastar a janela ainda funciona no novo tamanho compacto.
- [x] Gravando/processando ainda expande sozinho.
- [x] Nada do fluxo de ditado, do menu ⋮ nem da geração de imagem quebrado.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). — `git status` mostra como meu só
      `desktop/app.py` (modificado) e `desktop/testes_janela_compacta.py` (novo); o
      `.git/index.lock` de 27/08 **continua lá** e não é desta tarefa (ver riscos).

### Novas demandas / riscos
- **`.git/index.lock` (0 byte, 27/08 16:01) continua bloqueando o próximo commit.** Não tentei
  apagar pela pasta montada — é limite conhecido, já documentado no `HIGIENE.md`/`COMMIT.md`. O
  usuário apaga na máquina: `del ".git\index.lock"`.
- **Arquivo novo versionado sem estar em "Arquivos envolvidos"**: `desktop/testes_janela_compacta.py`.
  A tarefa pediu o teste explicitamente e o critério de pronto cobra "teste passando"; deixá-lo em
  `.claude/tmp/` seria jogar fora o entregável na próxima limpeza. Se o PM preferir outro lugar
  (uma pasta `testes/`), é mover.
- **Não reproduzi o bug do usuário.** Se ele voltar a acontecer depois desta volta, o que resta é
  instrumentar: um `log.info` em `_encolher_se_puder` com o motivo da recusa daria a resposta na
  primeira ocorrência. Não fiz agora para não sujar o log de uso.
- **Buraco pequeno no novo `_resultado_pendente()`**: se uma transcrição devolver exatamente o mesmo
  texto que já foi colocado antes, ela é considerada "já colocada" e a janela pode encolher com esse
  texto na tela. É o preço de derivar do conteúdo em vez de marcar; na prática duas transcrições
  idênticas seguidas são raríssimas.
- **Durante a animação de expandir, o conteúdo do cartão fica cortado** pelos poucos quadros em que
  a janela ainda é menor que o layout: o botão fica no lugar (é a âncora) e o resto se revela em
  volta. É consequência de manter a âncora exata quadro a quadro; só o usuário na tela real julga se
  incomoda.
- `desktop/README.md` continua descrevendo o app que "abre na janela cheia" e agora também o
  tamanho antigo do compacto. Não toquei — segue para o PM, como já estava registrado.
- **Rascunho não apagável**: `.claude/tmp/` ficou com os scripts de sonda/fuzz/matriz/patch desta
  volta (`probe*.py`, `fuzz.*`, `matriz.py`, `diag_anc.py`, `verifica_regressao.py`, `patch*.py`) e
  o `_teste_escrita.txt` da volta anterior. `rm` responde `Operation not permitted` pela pasta
  montada. Estão fora do controle de versão (não aparecem no `git status`), então não atrapalham o
  commit; saem na limpeza de virada de plano ou o usuário apaga na máquina.
- O crash do `Qt6Core.dll` (D-31) continua aberto e sem relação com esta volta.

### Ajuste no plano necessário?
Não — os três itens da segunda rodada do `D-32` estão no código. Fica registrado que o bug relatado
não foi reproduzido tal e qual, e que a defesa contra ele é em duas camadas.

## [2026-09-05] — D-32, terceira volta: largura do compacto, botão pulando na animação, "Sair" no menu
Status: concluído (com uma ressalva medida, não escondida: o achado 1 não foi reproduzido aqui)

### Diagnóstico do achado 2 (botão pula / muda de tamanho) — reproduzido e medido
Reproduzi os dois defeitos **em pixels**, não em coordenada, e são dois, não um:

1. **O botão aparecia cortado nos primeiros quadros da expansão.** Capturei a janela com `grab()` a
   cada 8ms e contei os pixels roxos do círculo do `BotaoGravar`. Com o código da 2ª volta, numa
   janela longe de qualquer borda: `prog=0.00` → janela 88x88, botão em `(47,41,72,72)`, recorte
   visível 41x47, **círculo desenhado 21x25px** (82 pixels amostrados) contra os **65x65** (820) do
   círculo inteiro; `prog=0.03` → 33x35; `prog=0.11` → 65x63; só a partir de `prog≈0.26` o círculo
   aparece inteiro. Ou seja: por uns 40ms o botão é um pedaço de círculo encolhido no canto — é
   exatamente o "muda de tamanho" relatado.
   **Causa**: a animação da 2ª volta refluía o layout inteiro a cada quadro (`_reassentar_layout`
   dentro do `_set_progresso_modo`). O layout do modo expandido põe o botão no centro de uma janela
   de 672px (centro local x=336) já no primeiro quadro, quando a janela ainda tem 88px — o botão
   cai **fora do recorte**. A âncora refeita a cada quadro mantinha a *coordenada* certa, e é por
   isso que a suíte de 45 verificações da 2ª volta mediu "desvio 0px" e não viu nada: ela media
   `mapToGlobal(centro)`, que continua correto mesmo quando o widget não é desenhado. Rodei a suíte
   nova contra o código antigo para confirmar que o defeito é pego agora: falha em
   "na expansão o círculo nunca aparece cortado (menor visto: (21, 25), inteiro: (65, 65))".
   **Segunda fonte de recorte**, achada ao consertar a primeira: o cartão (`QFrame`) também recorta
   os filhos. Com a margem externa do modo final (16px) valendo desde o quadro zero, o cartão ficava
   56x56 dentro de uma janela de 88px e cortava o círculo em 55x55. Por isso a margem externa passou
   a ser interpolada junto com o tamanho.

2. **Perto da borda da tela a âncora não cabe, e o botão anda muito.** Com a janela no canto em que
   o app nasce (`move(area+40, +40)`), o centro do botão percorreu, durante a expansão, `x = 83 →
   88 → 102 → 130 → 195 → 335`: **252px**. Nos outros cantos, até 359px. Não é bug de código: é
   geometria — a janela cheia (672x480) não cabe à esquerda do botão, então `_encaixar_na_tela`
   empurra a janela e o botão vai junto. O que dava para melhorar (e melhorou) é que esse
   deslocamento agora é interpolado na mesma curva da animação, e não mais um efeito colateral do
   recálculo de layout quadro a quadro — e o botão nunca aparece cortado no caminho.

**Achado de brinde, não relatado pelo usuário**: o reflow por quadro deixava o botão ⋮ **preso no
estado de hover** depois de cada expansão (`botao_menu.underMouse()` devolvia `True` com o cursor
sobre o botão de gravar, a 100px dali). Comparando pixel a pixel a janela cheia antes/depois desta
volta, as **1568** únicas diferenças estão todas dentro do retângulo 44x44 do ⋮, e são o tom mais
escuro do hover preso. Sumiu junto com o reflow.

### Diagnóstico do achado 1 (largura do compacto) — NÃO reproduzido aqui; o que dá para afirmar
Medido no headless, com o app aberto de verdade: a janela nasce e volta a **88x88 exatos** —
`width()` 88, `frameGeometry().width()` 88, `sizeHint()` 88, `minimumSize()`/`maximumSize()`
88x88, e o `QWindow` por baixo também 88x88. Forcei `resize(40,40)` e reassentei: 88 de novo.
Nenhuma das quatro hipóteses da tarefa aparece como número errado deste lado:
- **filho largo**: com o conteúdo do modo cheio escondido, o mínimo do layout do cartão é 88x88 —
  o único item não vazio é o botão de 72 mais 2x8 de margem. O filho mais largo (`caixa_texto`,
  `sizeHint` 256) não conta: `QWidgetItem` de widget escondido é item vazio para o layout;
- **QSS**: o único `min-width` do QSS inteiro é `QScrollBar::handle:horizontal { min-width: 20px }`,
  que não toca a janela;
- **ordem de resize/activate**: o assentamento faz `setGeometry` → `activate()` dos dois layouts →
  `setFixedSize`, e a rede de segurança do vigia repete isso a cada 100ms se o tamanho fugir;
- **DPI**: este ambiente reporta `devicePixelRatio` 1.0. A máquina do usuário, pela medição da
  entrada anterior (área disponível 1536x864 num monitor de 1920x1080), roda a **125%** — então 88px
  lógicos são **110px físicos** na tela dele, que é exatamente o número do compacto *antigo* em
  pixels lógicos. Se a comparação dele foi a olho contra a versão anterior, "não diminuiu" pode ser
  a leitura de uma janela de 110px físicos. Isso é inferência minha, não medição.

**O que o headless não consegue ver, e é a minha suspeita principal**: o plugin `offscreen` avisa,
em toda execução, `This plugin does not support propagateSizeHints()` — ou seja, **ele nunca informa
mínimo/máximo ao sistema de janelas**. No Windows é justamente por aí (`WM_GETMINMAXINFO`) que o
mínimo de uma janela é definido, e quando o mínimo do `QWindow` é zero vale o mínimo **do sistema**,
cuja *largura* (`SM_CXMINTRACK`, da ordem de 112–136px) é muito maior que a altura. O código da 2ª
volta chamava `setMinimumSize(0, 0)` antes de cada transição e só recolocava o tamanho fixo no fim.
Uma janela presa na largura mínima do sistema, com a altura encolhendo normalmente, tem exatamente o
formato do que o usuário relatou — *"não diminuiu a **lateral**"*, e não "não diminuiu". Mudei:
o mínimo da janela agora é declarado como o lado do compacto (88) o tempo todo, nunca zero.
**Não posso confirmar que era essa a causa** — depende do gerenciador de janelas do Windows, que
este shell não alcança. Por isso a volta também deixa **evidência para a próxima**: uma linha de log
por valor novo (`compacto alvo=88x88 real=88x88 moldura=88x88 dpr=1.0`) e outra, limitada a uma a
cada 5s, quando a rede de segurança precisar reassentar. Se na próxima execução real o log disser
`real=88x88` e a tela mostrar mais largura, a conta deste código está certa e o excesso é do
Windows (aí o caminho é outro: mexer no estilo nativo da janela, não no layout).

### Feito
- `desktop/app.py`, `_aplicar_modo` **reescrito**: a animação passou a interpolar a **janela inteira
  (posição e tamanho)** entre dois retângulos calculados antes de começar, com os **dois layouts
  congelados** (`setEnabled(False)`) durante a transição. Quem posiciona o cartão e o botão a cada
  quadro é a própria classe, por coordenada absoluta. O conteúdo do cartão fica escondido durante a
  transição e volta no assentamento — com o layout congelado ele estaria com a geometria do tamanho
  final dentro de uma janela menor, isto é, cortado e fora do lugar.
- `desktop/app.py`, `_set_progresso_modo`: um `setGeometry` por quadro, mais o cartão e o botão
  posicionados à mão. O centro do botão é interpolado **em coordenadas de tela** e só então
  convertido para dentro da janela já arredondada — assim, quando as duas pontas são o mesmo ponto,
  todo quadro dá exatamente esse ponto (sem o 1px de erro de arredondar janela e botão em separado).
  A margem externa (16 ↔ 0) também é interpolada, senão o cartão recorta o próprio botão.
- `desktop/app.py`, métodos novos: `_configurar_layout_do_modo` (só margens/mola/estilo),
  `_centro_do_botao_na_janela`, `_centro_local_do_botao` (mede onde o layout **vai** pôr o botão num
  tamanho hipotético, rodando o layout do cartão do mesmo jeito que o assentamento final roda),
  `_encaixar_na_tela`, `_geometria_do_modo` (tamanho + posição ancorada + encaixe),
  `_registrar_geometria_compacta`.
- `desktop/app.py`, `_assentar_modo` passou a receber um `QRect` (posição e tamanho de uma vez);
  `_ancorar_pelo_botao` saiu (a âncora agora é calculada em `_geometria_do_modo`, antes de mover).
- `desktop/app.py`, mínimo da janela: `setMinimumSize(lado_compacto)` em vez de `setMinimumSize(0,0)`
  em toda troca de modo — ver o diagnóstico do achado 1.
- `desktop/app.py`, `_corrigir_tamanho_do_modo`: mesma rede de segurança de antes, agora com log
  limitado a uma linha a cada 5s (se o sistema recusar o tamanho, ela dispara 10x por segundo).
- `desktop/app.py`, **"Sair" no menu ⋮** (5º item, depois de Gerar imagem): ícone `sair` novo em
  `ICONES_SVG` e `JanelaDitado._sair`, que faz `close()` (o `closeEvent` solta o atalho global e o
  stream de áudio) e `QApplication.quit()` — sem o `quit()`, as janelas filhas escondidas (Consumo,
  Gerar imagem) segurariam a aplicação viva.
- `desktop/testes_janela_compacta.py`: de 45 para **65 verificações**. Novos: `[3]` largura do
  compacto em `width()`, `frameGeometry()`, mínimo/máximo do widget **e do `QWindow`**, e mínimo
  durante a animação; `[8]` posição inicial dentro da tela (guarda a correção da entrada anterior);
  `[9]` **o botão contado em pixels do `grab()`**, quadro a quadro, nos dois sentidos e no canto da
  tela; `[10]` "Sair" encerrando um laço de eventos de verdade.
- A correção da posição inicial (`self.move(...)` em `_montar_ui`) **não foi tocada**; só o
  comentário que citava o método removido passou a citar `_geometria_do_modo`.

### Como testei
`QT_QPA_PLATFORM=offscreen`, PySide6 6.11.2, `keyboard`/`sounddevice` dublados, nenhuma chamada
paga. `python desktop/testes_janela_compacta.py`: **65 verificações, 0 falhas**, igual em duas
execuções seguidas.
- **Prova de que a suíte pega o defeito**: rodei a suíte nova contra uma cópia do `app.py` de antes
  desta volta — **5 falhas**, exatamente nos pontos relatados: círculo cortado em `(21,25)` na
  expansão e no canto da tela, mínimo `QSize(0,0)` durante a animação, menu sem o 5º item e "Sair"
  estourando a guarda de 3s. Contra o código novo, as mesmas verificações passam.
- **Botão em pixels, depois**: em todos os quadros das duas animações, círculo **65x65** (815–820
  pixels amostrados, contra 82 no pior quadro de antes) e **desvio 0px** do centro em relação à
  âncora, quadro a quadro, medido a cada 8ms. Nos três cantos da tela o círculo também sai inteiro
  em todos os quadros (a janela ali continua andando: é a geometria, ver riscos).
- **Compacto**: `88x88` em `width()`, `frameGeometry()`, `minimumSize()`, `maximumSize()` e no
  `QWindow`; `resize(40,40)` seguido de reassentamento devolve 88x88.
- **Regressão da janela cheia**: geometria de todos os widgets **idêntica** antes/depois
  (`cartao QRect(16,16,640,448)`, botão `(284,25,72,72)`, caixa `(24,203,592,173)`, etc.). No
  `grab()` pixel a pixel sobram 1568 pixels diferentes, todos dentro do ⋮, e são o hover preso do
  código antigo (ver diagnóstico).
- **Fumaça do resto**: menu com os cinco itens; Consumo, Gerar imagem e Configurações abrem e travam
  o encolhimento; `iniciar_gravacao` expande sozinho com o ponteiro longe e volta ao encolher depois
  de cancelar; realce de arrastar-soltar e balão continuam onde deviam; três ciclos completos de
  ditado (com trabalho de transcrição falso) encolhendo nos três.
- **Não testei**: nada renderizado no Windows de verdade — a largura do achado 1 na tela dele, a
  suavidade percebida da animação, o hover de mouse real, o sempre-no-topo e a translucidez;
  gravação por microfone e transcrição real contra o núcleo (fora do ar, inalcançável daqui); o
  clique de mouse de verdade no item "Sair" do menu aberto (disparei o sinal `clicado` do item, que
  é o que o clique dispara); e **não** repeti o teste de upload multipart contra núcleo falso da
  volta anterior — não toquei em nada do caminho de transcrição.

### Critério de pronto
- [x] Largura do compacto medida (`width()` e `frameGeometry().width()`) e explicada — causa
      identificada, não só "ajustei o número". — medida em cinco lugares, todas 88; a causa do que o
      usuário vê **não** ficou provada (não é reproduzível neste ambiente): a suspeita principal, com
      o porquê, está no diagnóstico, a defesa está no código (mínimo nunca zero) e a prova ficou
      preparada em log para a próxima execução real.
- [x] Posição do `BotaoGravar` medida quadro a quadro ao longo de toda a animação (não só nas
      pontas), com desvio documentado. — em coordenada **e em pixels**: desvio 0px e círculo inteiro
      (65x65) em todos os quadros longe da borda; no canto da tela o desvio é de projeto (252–359px,
      número medido) e o círculo continua inteiro.
- [x] "Sair" no menu ⋮, testado (chama o encerramento, não deixa processo pendurado). — laço de
      eventos de verdade encerrado, `aboutToQuit` disparado, janela fechada e atalho global solto,
      com guarda de 3s para o caso de travar.
- [x] A correção da posição inicial (janela num vão sem monitor) continua funcionando. — teste `[8]`
      confere que a janela nasce dentro da área visível e no canto declarado; o `move(...)` de
      `_montar_ui` não foi tocado.
- [x] Nada do fluxo de ditado, menu ⋮, geração de imagem quebrado. — ciclos de ditado, cinco itens
      do menu, três painéis abrindo e travando o encolhimento, regressão da janela cheia idêntica.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). — meu são `desktop/app.py`
      (modificado) e `desktop/testes_janela_compacta.py` (novo, ainda não commitado desde a 2ª
      volta). O `.git/index.lock` de 27/08 **continua lá** (0 byte, 27/08 16:01) e não é desta
      tarefa. Rascunhos desta volta ficaram fora do repositório (ver riscos).

### Novas demandas / riscos
- **`.git/index.lock` (0 byte, 27/08 16:01) segue bloqueando o commit.** Não tentei apagar pela
  pasta montada (limite conhecido). O usuário apaga na máquina: `del ".git\index.lock"`.
- **A causa real do achado 1 continua sem prova.** Se depois desta volta a lateral ainda parecer
  grande, a próxima rodada não precisa adivinhar: o `desktop/app.log` vai ter a linha
  `compacto alvo=... real=... moldura=... dpr=...` da abertura. Se `real` for 88x88, o problema é do
  Windows (mínimo de largura da janela nativa ou escala) e o caminho é outro — mexer no estilo
  nativo da janela (`WS_THICKFRAME`/`WM_GETMINMAXINFO`) ou aceitar a largura mínima e centralizar o
  círculo nela.
- **Perto da borda da tela o botão anda muito ao expandir (252–359px, medido).** É consequência da
  regra da `D-32` (âncora no centro do botão) somada ao encaixe da janela cheia na área visível: a
  janela cheia não cabe à esquerda de um botão que está a 83px da borda. A janela **nasce** nesse
  canto (`area+40,+40`), então na primeira expansão isso acontece sempre; depois de um ciclo ela
  fica onde a âncora funciona. Se incomodar, a correção natural é a posição inicial já nascer onde a
  janela cheia caberia (ex.: `area.x + 340`), mas isso é mexer na correção da entrada anterior — não
  fiz por conta própria.
- **Durante a transição o conteúdo do cartão fica escondido**, e não mais cortado: a janela cresce
  como um invólucro em volta do botão e o conteúdo aparece no fim dos 160ms. É uma mudança de
  aparência deliberada (o preço de não refluir layout por quadro); só o usuário na tela real julga
  se prefere assim.
- **`desktop/app.log` é versionado** e recebe uma linha a cada abertura. Já estava modificado antes
  desta volta; minhas execuções headless acrescentaram ~220 linhas (uma janela por teste). Vale
  decidir se ele entra no `.gitignore` — não mexi.
- **`desktop/testes_janela_compacta.py` continua novo e não commitado** desde a 2ª volta, e cresceu
  para 587 linhas. Se o PM preferir uma pasta `testes/`, é mover.
- **Rascunhos desta volta ficaram fora do repositório**: usei `$HOME/sondas_d32/` na máquina de
  sessão (some com a sessão) em vez de `.claude/tmp/`, justamente porque os rascunhos das voltas
  anteriores ficaram lá sem poder ser apagados (`Operation not permitted` pela pasta montada). O
  `.claude/tmp/` continua com o que a 2ª volta deixou.
- O crash do `Qt6Core.dll` (D-31) continua aberto e sem relação com esta volta.

### Ajuste no plano necessário?
Não — os três achados da terceira rodada estão no código. Fica registrado que o achado 1 **não foi
reproduzido** neste ambiente, que a defesa contra ele é a declaração do mínimo da janela, e que a
prova de qual lado está o problema ficará no `app.log` na próxima execução real do usuário.

## [2026-09-05] — D-32, quarta volta: parar de redimensionar a janela nativa a cada quadro
Status: concluído (mudança arquitetural feita e medida em headless; os dois sintomas do usuário
seguem **sem confirmação** — só o Windows real decide)

### Feito
- **A animação não chama mais `setGeometry()` na janela do SO quadro a quadro.** `_aplicar_modo`
  leva a janela nativa **uma vez** ao retângulo-união das duas pontas (`_geo_transicao =
  geo_atual.united(geo_final)`) e ela fica parada ali; `_set_progresso_modo` continua interpolando,
  mas agora só posiciona o cartão (deslocado de `-base.topLeft()`) e o botão dentro dessa janela.
  O tamanho final exato volta a ser pedido ao SO só em `_assentar_modo`, como já era. Como a
  interpolação de retângulos é linear e a união é um retângulo, todo quadro do meio (cartão e botão
  inclusive) cabe dentro dela — não há corte novo.
- **Medido, com a suíte headless:** antes, cada transição pedia **11 redimensionamentos nativos**
  (um por quadro distinto da animação de 160ms) **+ 1 no assentamento = 12**. Depois: **1 troca de
  `frameGeometry()` por transição** nos dois sentidos (a união já é o retângulo expandido no caso
  normal, então o `setGeometry` inicial da expansão é o único; no encolhimento a janela já está lá
  e o único é o final). O critério pedia "no máximo 2".
- **Botão continua com 0px de desvio**: nos mesmos casos que a 3ª volta provou (expansão e
  encolhimento longe da borda) e também no teste novo — `desvio 0px` nos dois sentidos. O círculo
  roxo medido em pixels por `grab()` continua inteiro (65x65) em todos os quadros, inclusive no
  canto da tela.
- **Acertos de coerência que a mudança obrigou** (não são reabertura de lógica antiga):
  `_geometria_visivel()` novo — durante a transição `self.geometry()` deixou de ser o que aparece,
  então o vigia de ponteiro, a reversão no meio da animação e os testes passam a perguntar por ele;
  os centros do botão passaram a ser guardados em coordenada de **tela** (`_centro_inicial_global` /
  `_centro_final_global`) em vez de relativos à janela, que era o que amarrava a conta à posição
  nativa; `_corrigir_tamanho_do_modo` ignora a janela enquanto `_geo_transicao` existe (senão a rede
  de segurança "corrigiria" a janela-união); `arraste_mover` desloca os retângulos e centros
  guardados quando se arrasta no meio de uma transição. `_centro_do_botao_na_janela()` ficou sem uso
  e foi removido.
- **Suíte estendida, não substituída**: teste `[11] a janela nativa não é redimensionada quadro a
  quadro` conta as trocas de `frameGeometry()`, confere que os tamanhos nativos ficam dentro da
  união, que o cartão passa por tamanhos intermediários e que o desvio do botão é 0px; e confere que
  `_geo_transicao`/`_geo_visivel` voltam a `None` no fim. Os testes `[4]` e `[9]`, que mediam
  "tamanhos intermediários" por `width()` da janela, passaram a medir `_geometria_visivel().width()`
  — com a mudança, `width()` fica constante em 672 durante a transição inteira (foi essa falha que
  confirmou que a mudança pegou).
- **Suíte inteira: 76 verificações, 0 falhas** (`QT_QPA_PLATFORM=offscreen`). Fumaça do resto:
  menu ⋮ com os cinco itens e abrindo, Gerar imagem e Configurações abrindo, "Sair" encerrando o
  laço de eventos de verdade, três ciclos completos de ditado (trabalho de transcrição falso)
  encolhendo nos três.
- **Não testei**: nada renderizado no Windows de verdade. O flicker e a largura/altura do compacto
  **não são reproduzíveis em headless** (o plugin `offscreen` não tem compositor, e é justamente o
  compositor que a hipótese acusa). Microfone e núcleo real também não.

### Critério de pronto
- [x] Janela nativa muda de tamanho no máximo 2x por transição, medido pela suíte. — **1x** em cada
      sentido (antes: 12x).
- [x] Botão sem desvio de posição — **0px** nos dois sentidos, círculo inteiro (65x65) em todos os
      quadros, inclusive no canto da tela.
- [x] Menu ⋮, "Sair", fluxo de ditado, geração de imagem: nenhum quebrado. — todos exercitados.
- [x] `PROGRESSO.md` registra os números sem inflar e deixa claro o que só o usuário confirma.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py`
      (modificado) e `desktop/testes_janela_compacta.py` (ainda não commitado desde a 2ª volta). O
      `.git/index.lock` de 27/08 continua lá e não é desta tarefa.

### Novas demandas / riscos
- **Honestidade sobre o resultado**: esta volta **não corrigiu** nenhum dos dois sintomas de forma
  provada. Ela eliminou uma causa conhecida (12 redimensionamentos nativos de janela translúcida em
  160ms → 1) que é uma hipótese plausível para os dois. Se o tremor sumir, a hipótese estava certa;
  se continuar, o suspeito seguinte já está isolado (composição/`UpdateLayeredWindow` ou o mínimo do
  Windows, `SM_CXMINTRACK`), e o `app.log` com a linha `compacto alvo=... real=...` continua sendo a
  prova que falta — **ainda não lida**.
- **Efeito colateral novo, pequeno e temporário**: durante os 160ms da transição a janela nativa
  ocupa o retângulo-união (≈672x480 em vez de 88x88). A área extra é transparente, mas **não é
  clicável-através**: um clique nesse retângulo durante a transição cai na janela e vira arrasto.
  São 160ms e a janela expandida já tinha 16px de borda transparente clicável, então não é classe
  nova de problema — mas se incomodar, o caminho é `setMask()` ou `WA_TransparentForMouseEvents` na
  área fora do cartão, e aí é decisão de produto, não conserto.
- **O ambiente de teste precisou de remendo**: o shell Linux desta sessão não tinha `libEGL.so.1`, e
  a suíte nem importava. Resolvi baixando `libegl1`/`libegl-mesa0`/`libgbm1` do arquivo do Ubuntu e
  apontando `LD_LIBRARY_PATH` (nada instalado no sistema, nada no repositório). Quem rodar a suíte
  daqui de novo precisa do mesmo remendo; na máquina Windows do usuário isso não existe.
- Continuam abertos, sem relação com esta volta: `.git/index.lock` de 27/08 bloqueando commit;
  `desktop/app.log` versionado e crescendo (minhas execuções acrescentaram linhas); percurso de
  252–359px do botão perto do canto de abertura (geometria, não bug); crash do `Qt6Core.dll` (D-31).

### Ajuste no plano necessário?
Não. A quarta volta fez o que a tarefa pediu e a suíte prova a parte que dá para provar aqui. O
próximo passo é do usuário: rodar no Windows, dizer se o tremor sumiu e colar a linha
`compacto alvo=... real=...` do `app.log` — é ela que decide se a largura/altura ainda é assunto e,
se for, de que lado (deste código ou do sistema de janelas).

## [2026-09-05] — D-32, quinta volta: a ordem dentro de `_aplicar_modo` (reconfigurar só com o layout congelado)
Status: concluído (reordenação feita e medida em headless; o sintoma "o botão some por um instante"
segue **sem confirmação** — só o Windows real decide)

### Feito
- **Nova ordem em `_aplicar_modo`**: os dois layouts (`_layout_externo`, `_layout_cartao`) são
  desabilitados e o conteúdo só-expandido é escondido **antes** de `_configurar_layout_do_modo`
  rodar. Antes, margens/mola/folha de estilo do cartão e um `setVisible(expandido)` mexiam no
  layout **ainda habilitado**, dentro da janela ainda no tamanho do modo antigo (88px na expansão).
  Medido com espião: `_configurar_layout_do_modo` rodava com layout ligado em **2 de 2** transições;
  agora **0 de 2**.
- **O `setVisible(expandido)` sumiu, mas não do jeito que a tarefa pedia — e o porquê é medido.**
  Apagá-lo puro e simples quebraria a âncora: o layout só conta widget visível, e o centro do botão
  na janela expandida sai em **y=76 com o conteúdo visível e y=239 com ele escondido** (163px, que
  viraria um pulo do botão no assentamento). A garantia foi para dentro de `_centro_local_do_botao`,
  que agora impõe a visibilidade do modo **só durante o `activate()`** da medição e devolve a de
  antes. Resultado: durante a transição inteira o conteúdo fica escondido nos dois sentidos, e a
  medição continua certa.
- **O redimensionamento nativo para a união não pôde ser adiantado para antes de
  `_configurar_layout_do_modo`** — a união depende de `geo_final`, que depende das margens **e da
  folha de estilo** já aplicadas: a borda de 1px do QSS do cartão desloca o centro medido em 1px
  (76 com borda, 75 sem). Adiantar exigiria um redimensionamento nativo a mais por transição (o que
  a 4ª volta eliminou) ou 1px de erro de âncora. Com os layouts congelados, `_configurar_layout_do_modo`
  não reflui nada e não há volta ao laço de eventos entre ele e `_set_progresso_modo(0.0)` — nenhum
  quadro chega a ser pintado no tamanho antigo. Está escrito no docstring.
- **Menos trabalho ao vivo no instante da troca**: `_centro_local_do_botao` (um `activate()` do
  layout cheio) era chamado **2x por transição** com o mesmo argumento; agora **1x** (medido: 4→2
  em duas transições), reaproveitado por `_geometria_do_modo(..., centro_local=...)`.
- **Suíte estendida, não substituída**: teste novo `[12] conteúdo só-expandido nunca aparece durante
  a transição` — amostra a 4ms e confere (a) 0 widget só-expandido visível em **41 quadros** dentro
  de cada transição, (b) `_configurar_layout_do_modo` sempre com os dois layouts congelados, (c) o
  centro do botão medido com o conteúdo escondido == medido com ele visível, (d) desvio **0px** e
  **1 redimensionamento nativo** por sentido (a garantia da 4ª volta, dentro do teste novo). A suíte
  ganhou também filtro por nome (`python testes_janela_compacta.py conteudo_escondido`).
- **Suíte inteira: 91 verificações, 0 falhas** (76 antes + 15 novas), `QT_QPA_PLATFORM=offscreen`.
  Fumaça: menu ⋮ com os cinco itens, Gerar imagem e Configurações abrindo, ciclo de ditado completo
  encolhendo (88x88), "Sair" encerrando o laço de eventos.
- **Prova de regressão**: o teste `[12]` rodado contra o `app.py` da 4ª volta **falha em 2 das 15**
  verificações — exatamente (b) `[(True, True, True), (False, True, True)]` e (c) `y=239 != y=76`.

### Critério de pronto
- [x] Nenhum widget só-expandido visível durante a transição — 0 em 41 quadros amostrados, nos dois
      sentidos.
- [x] `_configurar_layout_do_modo` só roda com os dois layouts desabilitados — 0/2 chamadas com
      layout ligado (antes: 2/2). **Parcial e por medição**: não roda depois do resize nativo, e o
      porquê está acima.
- [x] Suíte inteira passando sem regressão: **91/0**, desvio **0px** e **1** redimensionamento
      nativo por sentido (iguais à 4ª volta).
- [x] Menu ⋮, "Sair", fluxo de ditado, geração de imagem: nenhum quebrado.
- [x] Registro honesto: nada aqui **prova** que o "some por um instante" acabou.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py` e
      `desktop/testes_janela_compacta.py`. O `.git/index.lock` de 27/08 continua lá.

### Novas demandas / riscos
- **Honestidade sobre o resultado**: o sintoma não é reproduzível headless. Pior: a checagem (a) do
  teste novo **passa também no código antigo** — o `setVisible(expandido)` era desfeito dentro da
  mesma chamada, sem voltar ao laço de eventos, então nenhum amostrador de 4ms o enxerga. O que ficou
  provado é que a ordem antiga mexia em layout habilitado (medido) e que a nova não mexe mais; se o
  flash vinha de repolish/relayout ao vivo numa janela layered, sumiu; se vinha de outra coisa, não.
  **Não declarar corrigido** até o usuário testar no Windows.
- **Achado novo, relevante para quem mexer aqui**: a posição do botão medida por
  `_centro_local_do_botao` depende de o conteúdo só-expandido estar visível (163px de diferença) e
  da folha de estilo do cartão (1px, por causa da borda do QSS). Quem reordenar essas chamadas de
  novo precisa das duas condições aplicadas antes de medir.
- **Pendência que continua**: a linha `compacto alvo=... real=...` do `desktop/app.log` nunca foi
  colada pelo usuário — o tamanho do compacto segue sem confirmação, nesta volta também.
- Continuam abertos, sem relação: `.git/index.lock` de 27/08; `desktop/app.log` versionado e
  crescendo (minhas execuções acrescentaram ~linhas); área transparente da janela-união não
  clicável-através durante os 160ms (4ª volta); crash do `Qt6Core.dll` (D-31).
- **Ambiente**: o remendo do `libEGL.so.1` da 4ª volta (`.deb` do Ubuntu em `~/.local/qtlibs`,
  apontado por `LD_LIBRARY_PATH`) continua necessário e já estava no lugar; nada instalado.

### Ajuste no plano necessário?
Não. A 5ª volta fez a reordenação pedida onde ela é possível e mediu o porquê dos dois pontos em que
o pedido literal não cabia (163px da visibilidade, 1px da borda). O próximo passo continua sendo do
usuário: testar no Windows e dizer se o botão ainda some no começo/fim da transição — e colar a
linha `compacto alvo=... real=...` do `app.log`, que segue sendo a prova que falta para o tamanho.

## [2026-09-05] — D-32, sexta volta: janela expandida mais baixa (caixa de transcrição em 160px)
Status: concluído (medido e testado em headless; a aparência no Windows real segue **pendente de
confirmação do usuário**). Escopo diferente das 5 voltas anteriores: não é bug do compacto, é
pedido novo sobre o tamanho da janela **expandida**.

### Feito
- **Medição primeiro** (offscreen, janela expandida em repouso, `_layout_cartao` ativado): dos 480px
  de altura, a caixa de transcrição ocupava **171px** e todo o resto **309px** — 16+16 margem
  externa · 1+1 borda do cartão (QSS) · 24+24 margem do cartão · 4×16 espaçamento · 72 linha do topo
  (⋮ + gravar + cancelar) · 19 cronômetro · 40 barra de amplitude · 32 linha de ações.
- **`self.caixa_texto.setMinimumHeight(128)` → `ALTURA_CAIXA_TEXTO = 160`** (480/3 = 160, o "um
  terço do total" pedido). Com o fator de esticar 1 e a janela na altura nova, a caixa fica em
  **exatamente 160px** (medido, não estimado) — o mínimo passou a ser o que ela ocupa, não um piso
  solto.
- **`self._tamanho_expandido` = `QSize(672, ALTURA_EXPANDIDA)` = `672x469`**, com
  `ALTURA_EXPANDIDA = ALTURA_FIXA_EXPANDIDA (309) + ALTURA_CAIXA_TEXTO (160)`. Conta: 309 fixos
  (inalterados) + 160 da caixa = 469. **Largura intocada** (672 = 40rem + respiro, `SPEC-002` I).
  As três constantes ficaram no topo do `app.py`, com a medição escrita no comentário.
- **Usabilidade da caixa menor, medida**: viewport de 138px = **9 linhas** visíveis sem rolar (antes
  eram 10); uma frase de transcrição normal não gera rolagem. Entre encolher mais e menos, ficou o
  maior, como a tarefa pediu.
- **Suíte estendida**: `[13] altura da janela expandida e da caixa de transcrição` (mede o layout
  real e trava os 309px fixos, a largura de 672, os 160px da caixa e as linhas visíveis) e
  `[14] a nova altura do expandido não toca no compacto` (troca `_tamanho_expandido` para 480/700/
  200 e confere que `_lado_compacto()`/`_tamanho_do_modo(False)` continuam 88×88, mais um ciclo real
  expandir→encolher terminando em 88×88).
- **Suíte inteira: 107 verificações, 0 falhas** (91 antes + 16 novas), rodada em 4 blocos por causa
  do limite de tempo do shell. Nenhum teste antigo precisou de ajuste: eles já liam
  `j._tamanho_expandido` em vez do `480` literal.
- **Fumaça**: menu ⋮ com os cinco itens, Configurações/Consumo/Gerar imagem abrindo, copiar e
  lixeira funcionando, janela terminando em 672×469.

### Critério de pronto
- [x] `caixa_texto` em 160px — ~1/3 dos 480px de antes, medido no layout, não estimado.
- [x] `_tamanho_expandido` = 672×469 (largura mantida, `SPEC-002` I).
- [x] Janela compacta sem nenhuma mudança — 88×88, provado pelo teste `[14]` e pelo `[3]` antigo.
- [x] Suíte inteira passando: 107/0.
- [x] Menu ⋮, "Sair", copiar/lixeira, geração de imagem: nenhum quebrado.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py` e
      `desktop/testes_janela_compacta.py`.

### Novas demandas / riscos
- **A premissa da tarefa não se confirmou na medição, e isso muda o resultado prático.** A caixa de
  transcrição **não** era "o maior consumidor de altura": ela já era 171px de 480 (**35,6%**, ou
  seja, já estava em ~1/3). Quem domina a altura é o que está fixo — **309px, 64%** da janela.
  Consequência: reduzir a caixa a 160px encolheu a janela em **11px** (480 → 469, 2,3%). O pedido
  foi cumprido ao pé da letra, mas é provável que o usuário não perceba diferença e volte a dizer
  que "está do mesmo tamanho". **Decidir com ele antes de uma 7ª volta**: para a janela expandida
  ficar visivelmente menor é preciso mexer no que a tarefa mandou não mexer. Os candidatos, com o
  quanto cada um vale: espaçamento 16→8 (**−32px**), margem do cartão 24→16 (**−16px**), margem
  externa 16→8 (**−16px**), barra de amplitude 40→24 (**−16px**), linha do topo 72→56 (botões 44→32,
  **−16px**), cronômetro fundido na linha do topo (**−35px** com o espaçamento). Tudo junto, com a
  caixa em 160: **~354px de altura** (contra 469 agora e 480 antes) — ~26% menor.
- **Confirmação visual pendente**: a aparência da janela expandida menor só o usuário valida no
  Windows real (mesma pendência de sempre; headless não decide isso).
- **Sujeira que não consegui limpar**: escrevi um script de medição em `desktop/_medicao/medir.py` e
  o sistema **bloqueou a exclusão de arquivos** nesta sessão (`Operation not permitted`, e o pedido
  de permissão foi negado). O arquivo está **fora do git** (não rastreado) e ganhou um cabeçalho
  dizendo que é temporário e pode ser apagado — **apagar `desktop/_medicao/` à mão**. A medição de
  verdade virou o teste `[13]`; nada depende dessa pasta.
- **Ambiente**: o remendo do `libEGL.so.1` (`.deb` em `~/.local/qtlibs` + `LD_LIBRARY_PATH`) das
  voltas anteriores continua necessário e já estava no lugar; nada instalado.
- Continuam abertos, sem relação com esta volta: `.git/index.lock` de 27/08; `desktop/app.log`
  versionado e crescendo; área transparente não clicável-através durante os 160ms; crash do
  `Qt6Core.dll` (`D-31`).

### Ajuste no plano necessário?
Sim, provavelmente — não no plano das etapas, mas no escopo desta linha de trabalho: a medição
mostra que "encolher a janela expandida" e "encolher a caixa de transcrição" **não são a mesma
coisa** (a caixa é 1/3 da altura, o resto é 2/3). Se o objetivo do usuário for a janela menor de
fato, a próxima volta precisa autorizar mexer nos elementos fixos — com os números acima já
levantados, é uma volta curta.

## [2026-09-05] — D-32, sétima volta: largura própria, cortes nos fixos, borda menor, transição mais longa e o pulso adiado

Contexto: o usuário rejeitou a 6ª volta ("simplesmente você não conseguiu fazer nada nessa rodada")
e deu quatro ordens diretas. Esta volta executa as quatro, mais a aplicação real dos cortes nos
elementos fixos que a 6ª volta só tinha medido. Tudo medido no layout de verdade (offscreen), não
somado à mão.

### Feito
1. **Largura própria** (`LARGURA_EXPANDIDA = 448`, era `int(40*16)+32 = 672`): a janela flutuante
   deixou de seguir o item I da `SPEC-002`. Piso medido no layout real: linha do topo
   `49 (cronômetro) + 10 + ⋮ 32 + 10 + gravar 72 + 10 + cancelar 32 + 10 + espelho 49 = 274`;
   `+ 2×16` margem do cartão `= 306`; `+ 2×1` borda do QSS `= 308`; `+ 2×8` margem externa
   `= 324`. Em 324 as duas molas ficam em 0px (cabe, mas sem respiro). A escolha entre 324 e 672
   foi por **leitura da caixa de transcrição, medida com a fonte real**: 324 → 30 caracteres por
   linha · 384 → 38 · 432 → 44 · **448 → 46** · 672 → 74. 448 é o menor valor medido que mantém a
   caixa na faixa legível de ~45+ caracteres, e ainda sobram 62px em cada mola. **−224px (−33%)**.
2. **Os seis cortes nos fixos, aplicados**: espaçamento do cartão 16→8; margem do cartão 24→16;
   margem externa 16→8; `BarraAmplitude` 40→24; ⋮ e cancelar 44→32; `rotulo_cronometro` fundido na
   `linha_topo` (o cartão passou de 5 para 4 linhas). Altura **medida depois de aplicar**:
   `ALTURA_FIXA_EXPANDIDA` 309 → **186**, logo `ALTURA_EXPANDIDA` 469 → **346** (`186 + 160`).
   **−123px (−26%)** contra os 469 da 6ª volta, **−28%** contra os 480 originais.
   Janela expandida: **672×469 → 448×346** (área: −54%).
3. **Borda do compacto**: `MARGEM_JANELA_COMPACTA` 8 → **4** — compacto de **88×88 → 80×80**
   (`72` do botão `+ 2×4`), testado nos testes `[3]` e `[14]`.
4. **Transição mais longa**: `DURACAO_ANIMACAO_MODO_MS` 160 → **240**. A faixa de 120–200ms da 2ª
   volta foi revogada: veio de suposição minha, não de pedido do usuário, e o pedido dele agora é
   o oposto ("bota uma transição maior, ele não sumir").
5. **Pulso adiado até a transição assentar** (o ataque ao pisca-pisca do botão vermelho): o
   temporizador de 30ms da `CamadaPulso` nascia no mesmo instante que a transição de modo, quando
   a gravação começa a partir do compacto — dois sistemas de animação com relógios próprios
   repintando a mesma região. Agora `CamadaPulso.definir_estado("gravando")` pergunta à janela
   (`esta_em_transicao_de_modo()`) e, se houver transição, marca `_pulso_adiado` em vez de ligar o
   temporizador; `_assentar_modo` (o fim de **toda** transição, animada ou não) chama
   `liberar_pulso_adiado()`. A cor/ícone do botão **não** foram adiados — mudam na hora, como antes.
   Como `_definir_estado_botao` troca o estado do botão *antes* de chamar `_aplicar_modo`, a
   animação ainda não está rodando no instante da pergunta: por isso existe o sinalizador
   `_transicao_de_modo_pendente`, o "vai começar agora" que `_anim_modo.state()` sozinho não
   enxerga. A ordem das chamadas da 4ª/5ª volta **não** foi mexida.

### Como testei
- Suíte inteira: **143 verificações, 0 falhas** (eram 107 na 6ª volta; +36 novas). Invariantes das
  voltas 4 e 5 mantidos, sem regressão: **1 redimensionamento nativo por sentido**, **0px** de
  desvio do centro do botão, **0 widget** só-expandido visível durante a transição, e o centro
  local do botão agora bate exatamente com e sem conteúdo visível (223,60 nos dois casos).
- Teste `[13]` reescrito: passou a medir também a largura (própria, ≥25% menor que 672, ≥ piso do
  layout), as duas molas da linha do topo iguais e não-nulas, o botão de gravar centralizado no
  cartão (±1px), o cartão com 4 linhas e cada um dos seis cortes onde ele de fato acontece.
- Teste `[15]`, novo, para a Parte 5: prova que a cor/ícone mudam na hora, que o temporizador de
  pulso **não** está ativo em nenhum quadro amostrado da transição (10 amostras), que ele começa —
  com o intervalo certo — só depois de a janela assentar, que sem transição nenhuma ele começa na
  hora (nada é adiado à toa), e que parar de gravar no meio da transição cancela a pendência em vez
  de ressuscitar um pulso no fim.
- **Fumaça**: menu ⋮ com os cinco itens; Configurações, Consumo e Gerar imagem abrindo; copiar/
  recortar, lixeira e desfazer funcionando. O painel de Configurações é um *overlay* dentro da
  janela do ditado — medido: 384×244 dentro dos 448×346 novos, com 32px de folga lateral e 51px em
  cima, não encolheu nem foi cortado. O `Toast` já se limita à largura do pai; nada a ajustar.
- **Conferência visual** (render offscreen dos dois modos, apagado depois): cronômetro à esquerda
  na mesma linha dos botões, botão de gravar centralizado, barra de amplitude, caixa e linha de
  ações no lugar; compacto = só o círculo, 80×80.

### Critério de pronto
- [x] Largura reduzida, com nome próprio (`LARGURA_EXPANDIDA`), medida e documentada com a conta.
- [x] Os seis cortes aplicados de verdade; `ALTURA_EXPANDIDA` = 346, **medida** depois de aplicar.
- [x] `MARGEM_JANELA_COMPACTA` = 4 (compacto 80×80), testado.
- [x] `DURACAO_ANIMACAO_MODO_MS` = 240.
- [x] Início de `_timer_pulso` adiado até a transição terminar, com teste que prova isso (`[15]`).
- [x] Suíte inteira passando: **143/0**.
- [x] Menu ⋮, "Sair", copiar/recortar/lixeira, geração de imagem: nenhum quebrado.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py` e
      `desktop/testes_janela_compacta.py`.

### Novas demandas / riscos
- **Honestidade sobre a Parte 5**: isto é uma correção **de código para uma causa plausível e bem
  fundamentada**, não uma confirmação de que o pisca-pisca acabou. Não existe compositor num
  ambiente headless Linux — o teste `[15]` prova que os dois sistemas de animação **deixaram de
  rodar ao mesmo tempo**, que era a hipótese; não prova que era isso que o usuário via. **Só o
  usuário confirma no Windows real**, como em todas as voltas anteriores.
- **Desvio da tarefa, medido e justificado**: a 6ª volta previa a linha do topo em 56px
  (⋮/cancelar 44→32, −16px). Isso **não é alcançável**: a altura de uma `QHBoxLayout` é a do widget
  mais alto dela, e o `BotaoGravar` continua 72px por ordem explícita da própria tarefa. Os outros
  cinco cortes vieram inteiros; este vale 0px em vez de −16px. Por isso a altura final é 346 e não
  os ~330 que a soma da 6ª volta sugeriria.
- **Desvio pequeno na fusão do cronômetro**: para o botão de gravar continuar centralizado no
  cartão com o cronômetro à esquerda, entrou um `espelho_cronometro` (widget vazio de 49px) do
  outro lado. É um **widget**, não um `addSpacing`, de propósito: entra em `_widgets_so_expandido`
  e some no modo compacto — um espaçador de layout não some, e os 49px dele empurrariam o botão
  para fora da janela de 80px (a mesma classe de defeito que a 3ª volta corrigiu).
- **Confirmação visual pendente, como sempre**: 448×346 e 80×80 são o que o usuário vai julgar. Se
  ainda achar largo, o piso medido é 324 — dá mais 124px, ao custo de 30 caracteres por linha na
  caixa de transcrição.
- **Ambiente**: o remendo do `libEGL.so.1` (`.deb` em `~/.local/qtlibs` + `LD_LIBRARY_PATH`) já
  estava no lugar; nada instalado.
- **Limpeza**: `desktop/_medicao/medir.py` (sujeira da 6ª volta) foi **apagado** — a permissão de
  exclusão, negada na volta passada, foi concedida nesta. Meus scripts de medição ficaram fora do
  repositório (`~/medicao_d32/`, no bridge); nada temporário sobrou dentro do projeto.
- Continuam abertos, sem relação com esta volta: `.git/index.lock` de 27/08; `desktop/app.log`
  versionado e crescendo; área transparente não clicável-através durante a transição (agora 240ms);
  crash do `Qt6Core.dll` (`D-31`).

### Ajuste no plano necessário?
Não. As quatro ordens do usuário e os cortes pendentes da 6ª volta saíram inteiros nesta volta; o
que resta é confirmação no Windows real, não trabalho de plano.

## [2026-09-05] — D-32, oitava volta: a conta da altura que esqueceu a margem externa, e mais uma tentativa no flicker do encolhimento

Curto, como pedido. Duas coisas: consertar a regressão que chegou ao usuário ("você quebrou o
layout e colocou o botão de cortar sobrepondo a caixa") e uma tentativa a mais no flicker do
hover-out. `ALTURA_CAIXA_TEXTO` (160) e `LARGURA_EXPANDIDA` (448) **não** foram tocados.

### O que mudei
- **Altura, medida no layout real** (não somada à mão): `j._layout_externo.minimumSize().height()`
  = **362px** é o mínimo da JANELA (cartão 346 + 2×8 de `MARGEM_EXTERNA_EXPANDIDA`, já com a borda
  de 1px do QSS). Tirando a caixa: `ALTURA_FIXA_EXPANDIDA` **186 → 202** — os 186 da 7ª volta eram
  a mesma lista de componentes **sem** as duas margens externas. Mais `FOLGA_ALTURA_EXPANDIDA = 4`
  (constante nova, folga contra variação de métrica de fonte entre máquinas):
  **`ALTURA_EXPANDIDA` = 202 + 160 + 4 = 366** (era 346). A janela segue 448 de largura e ~24%
  mais baixa que os 480 originais — os "-28%" da 7ª volta só existiam porque a janela estava menor
  que o próprio conteúdo.
- **Efeito medido**: antes, caixa terminando em y=288 e `botao_copiar` começando em y=281 (7px de
  sobreposição, o que o usuário viu). Agora caixa até y=292, ações a partir de y=301 — **8px de
  espaçamento**, exatamente o `ESPACAMENTO_CARTAO`. A caixa fica em **164px** (o piso de 160 mais
  os 4 de folga, que ela absorve por ser a única com fator de esticar); `ALTURA_CAIXA_TEXTO`
  continua sendo o piso declarado, intocado.
- **Flicker do encolhimento (tentativa, não solução)**: os dois `setGeometry` nativos que já
  existiam — o do retângulo-união em `_aplicar_modo` e o do assentamento em `_assentar_modo` —
  passaram a rodar entre `setUpdatesEnabled(False)` e `setUpdatesEnabled(True)`, com `repaint()`
  **síncrono** logo depois de religar. O reflow (`_reassentar_layout`, `setFixedSize`, quadro zero)
  entrou junto, dentro do bloco, para não sobrar quadro com janela do tamanho novo e conteúdo do
  tamanho velho. **Nada** da arquitetura das 4ª/5ª voltas mudou: continua 1 redimensionamento
  nativo por sentido.

### Como testei
- **Suíte inteira: 167 verificações, 0 falhas** (eram 143; +24), rodada duas vezes seguidas com o
  mesmo resultado. Invariantes das voltas 4-5 intactos: 1 redimensionamento nativo por sentido,
  **0px** de desvio do centro do botão, **0 widget** só-expandido visível durante a transição.
- **`[16]` (novo) — sobreposição de geometria real**, que é o teste que faltava: compara pixels
  (`mapTo(janela)`) do fundo da `caixa_texto` contra o topo de `botao_lixeira`/`botao_copiar`, e
  cruza **todos os pares** de widgets do cartão procurando interseção. E, para não ser um teste que
  só passa: ele **repõe a altura errada da 7ª volta (346)** e confere que o próprio critério acusa
  a sobreposição — depois volta para 366 e confere que limpa. Era exatamente isso que faltava; o
  teste da 7ª volta travava o número `346` e ficou verde com a tela quebrada.
- **`[17]` (novo)** — tranca a tentativa do flicker: nos dois sentidos, todo `setGeometry` nativo
  roda com `updatesEnabled=False`, há `repaint()` depois de religar (nunca antes), e a janela nunca
  fica com as atualizações desligadas no fim.
- **`[13]` ajustado**: em vez do número solto, passou a exigir `j.height() >= layout_externo.
  minimumSize().height()` com exatamente a folga declarada, e que `ALTURA_FIXA_EXPANDIDA +
  ALTURA_CAIXA_TEXTO` bata com esse mínimo — quem esquecer uma margem de novo quebra aqui.
- **Corrida latente da suíte, achada de raspão**: os testes deixavam o cursor em (79,79) e a janela
  seguinte nasce em (40,40) com 80×80, ou seja, **embaixo do cursor** — se o vigia de 100ms
  tiqueasse antes da primeira medição, a janela expandia sozinha e `[14]` media errado. Aparecia e
  sumia conforme o tempo total da suíte. `nova_janela()` agora começa com `mouse_longe()`.
- **Fumaça**: menu ⋮ com os cinco itens, Configurações/Consumo/Gerar imagem abrindo, recortar
  (clipboard + caixa esvaziada), lixeira e desfazer. Painel de Configurações medido: 384×244 dentro
  dos 448×366, sem corte.

### Critério de pronto
- [x] Sem sobreposição no expandido assentado, provado por geometria real (`[16]`), não por soma.
- [x] `ALTURA_CAIXA_TEXTO` (160) e `LARGURA_EXPANDIDA` (448) inalterados.
- [x] `setUpdatesEnabled`/`repaint()` em volta dos redimensionamentos nativos, sem regressão.
- [x] Suíte inteira passando: **167/0**.
- [x] Menu ⋮, "Sair", copiar/recortar/lixeira, geração de imagem: nenhum quebrado.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py`,
      `desktop/testes_janela_compacta.py` e este `PROGRESSO.md`.

### Novas demandas / riscos
- **Honestidade sobre a Parte 2**: isto é uma tentativa, **não uma confirmação**. Não existe
  compositor num Linux headless — o `UpdateLayeredWindow` do Windows, que é onde o quadro
  intermediário apareceria, simplesmente não roda aqui. O que ficou provado é o mecanismo (resize
  sem pintura parcial + repaint síncrono) e a ausência de regressão. Se o flicker do hover-out
  vinha daí, deve sumir; se vinha de outra coisa, não. **Só o usuário, no Windows real, decide.**
- A caixa ficando em 164px em vez de 160 é consequência da folga; se o usuário achar que cresceu
  demais, o ajuste é `FOLGA_ALTURA_EXPANDIDA` (2px ou 0), não `ALTURA_CAIXA_TEXTO`.
- **Ambiente**: o remendo do `libEGL.so.1` (`.deb` em `~/.local/qtlibs` + `LD_LIBRARY_PATH`) já
  estava no lugar; nada instalado.
- **Limpeza**: meus scripts de medição ficaram em `~/medicao_d32_r8/` (fora da pasta montada) e
  foram apagados no fim; nada temporário sobrou dentro do repositório.
- Continuam abertos, sem relação com esta volta: `.git/index.lock` de 27/08; `desktop/app.log`
  versionado e crescendo; área transparente não clicável-através durante a transição; crash do
  `Qt6Core.dll` (`D-31`).

### Ajuste no plano necessário?
Não. A regressão era de conta de altura e está corrigida com teste que a pega; o flicker do
encolhimento continua sendo confirmação de uso real, não trabalho de plano.

## [2026-09-05] — D-32, nona volta: a janela para de mudar de tamanho (máscara no lugar de resize)
Status: concluído (mudança de arquitetura feita e medida em headless; **o flicker segue sem
confirmação** — e desta vez nem a máscara é observável aqui, ver "Novas demandas / riscos")

Nível `completo`, não `curto`: é troca de arquitetura, três decisões tiveram de ser tomadas por
mim porque a tarefa não as cobria, e uma delas muda comportamento visível para o usuário.

### O que mudei
- **A janela nativa tem um tamanho só, para sempre**: `setFixedSize(448x366)` em `_montar_ui`
  (era `resize`). Sumiram o `setFixedSize` do assentamento compacto e os `setMinimumSize`/
  `setMaximumSize` por modo de `_aplicar_modo` e `_assentar_modo`.
- **Zero `setGeometry`/`move` nativo em transição, nos dois sentidos.** `_aplicar_modo` não leva
  mais a janela ao retângulo-união: `_geo_transicao` passou a ser `QRect(self.pos(), self.size())`,
  que já é onde a janela está. `_assentar_modo` não pede geometria ao SO — recebe o retângulo do
  **modo** (em coordenada de tela) e o guarda como `_offset_visivel` + `_tamanho_visivel`.
- **Quem cresce e encolhe é a máscara**: `_retangulo_mascara`, `_aplicar_mascara` e
  `_limpar_mascara` (novos), com `FOLGA_MASCARA_PX = 2` (constante nova). Retangular, como o PM
  decidiu. `_limpar_mascara` no começo da transição, `_aplicar_mascara` no assentamento — um
  `setMask` por transição. `_aplicar_mascara` só chama o sistema quando a região mudou.
- **`_geometria_visivel()` virou o eixo**, fora da transição também: devolve o retângulo do modo
  no offset em que ele mora dentro da janela. `_vigiar_ponteiro`, `_atualizar_ponteiro`, a reversão
  no meio da animação e o arrasto continuaram funcionando sem reescrita, como o PM previu.
- **`_geometria_do_modo` não encaixa mais na tela** e, no expandido, devolve a própria janela — é o
  que garante que a expansão não precise mover nada. `_encaixar_na_tela` sobrou com um uso só: a
  posição de abertura, que agora nasce grande e por isso passou a precisar dele.
- **`_corrigir_tamanho_do_modo` confere a máscara** (item 7 da tarefa), em dois braços: se o
  sistema mexeu no tamanho fixo, reassenta o modo inteiro; se só a região divergiu (um sobreposto
  abriu ou fechou), repõe a máscara, que é barato. Sem isso ela dispararia 10x/s para sempre.
- **`_registrar_geometria_compacta`** passou a registrar a região: uma linha por valor novo,
  `compacto alvo=80x80 mascara=84x84+182+19 janela=448x366 dpr=1.0` (linha real do `app.log`).
- **`_offset_do_retangulo`** (novo) prende o cartão compacto aos limites da janela e loga se
  precisar prender.
- Suíte: `[17]` reescrito para o contrato novo (e renomeado para `testar_transicao_sem_resize_nativo`),
  `[18]` e `[19]` novos, e todo teste que perguntava `j.size()` para saber o modo passou a
  perguntar ao helper novo `tam_visivel()` — `j.size()` é 448x366 nos dois modos agora.
- **Nenhum tamanho aprovado mudou**: 448, 366, 160, 80x80, 240ms conferidos pelos testes de sempre.

### Como testei
- **`[17]` (novo contrato), espionando as chamadas reais**: em cada sentido, **0 `setGeometry`,
  0 `resize`, 0 `move`** nativos; **1 `clearMask` + 1 `setMask`**, nessa ordem, as duas com
  `updatesEnabled=False`, e `repaint()` síncrono depois de religar (o envelope da 8ª volta,
  mantido). Antes desta volta era 1 redimensionamento nativo por sentido.
- **`[11]` (4ª volta) confirma pelo outro lado**: `frameGeometry()` muda **0 vezes** na transição
  inteira, nos dois sentidos (era 1). **`[12]` (5ª volta)**: 61 quadros por sentido, **0 widget**
  só-expandido visível, **desvio 0px** do centro do botão, 0 redimensionamento nativo.
- **Medição própria, fora do repositório**: 124 amostras na expansão e 193 no encolhimento, a 4ms —
  janela sempre `448x366 @ (40,40)`, desvio máximo do centro do botão **0px**, 48 a 52 quadros com
  o retângulo visível em tamanho intermediário (a animação continua viva, não virou pulo).
- **Máscara medida**: compacto `84x84+182+19` (o cartão de 80x80 mais 2px de folga por lado);
  expandido `436x354+6+6` (o cartão de 432x350 mais a folga). `QWidget.mask()` guarda a mesma
  região — é o estado que o Qt levaria ao sistema de janelas, e o teste `[18]` confere nele, não só
  na variável deste código.
- **Hover (`[18]`, o risco nº 1 da mudança)**: o ponto a 200px do botão está **dentro** da janela
  nativa e **fora** do cartão visível; com o cursor lá e o vigia rodando, a janela **não** expande;
  com o cursor no botão, expande. É o teste que teria pegado a quebra mais provável.
- **Sobrepostos**: `painel_configuracoes` é filho e ocupa a janela inteira (`resizeEvent`) — a
  máscara cresce para cobri-lo e volta ao cartão quando ele fecha. Menu ⋮, Consumo e Gerar imagem
  são janelas próprias (`isWindow()=True`), logo não são recortados. Conferido também que o anel
  que a `CamadaPulso` desenha (raio ~46px) cabe dentro da máscara do expandido.
- **Arrasto (`[19]`, novo)**: nos dois modos a janela, o cartão visível e o centro do botão andam
  exatamente o que o gesto pediu; no meio de uma transição o arrasto move a janela e o assentamento
  **não** devolve a janela para o lugar de antes.
- **Suíte inteira: 195 verificações, 0 falhas** (eram 167; +28), rodada três vezes seguidas com o
  mesmo resultado. Fumaça à parte: menu ⋮ com cinco itens, "Sair" encerrando o laço de eventos,
  Configurações/Consumo/Gerar imagem, copiar/recortar e lixeira.
- **O que NÃO testei, e não dá para testar aqui**: qualquer coisa que dependa de compositor. Ver
  abaixo — nesta volta a limitação é maior do que nas anteriores.

### Critério de pronto
- [x] Em uma transição inteira, nos dois sentidos: 0 redimensionamento nativo e 0 movimento nativo,
      provado por teste que conta chamadas (`[17]`) e confirmado por `[11]`/`[12]`.
- [x] Exatamente um `setMask` por transição, no assentamento (`[17]`).
- [x] 0px de desvio do centro do `BotaoGravar` durante a transição (`[11]`, `[12]`, e medição
      própria com 124/193 amostras).
- [x] Hover entra e sai pelo cartão visível: cursor a 200px do botão **não** expande (`[18]`).
- [x] Clique fora da máscara — provado **só no que headless entrega**: a região que o `QWidget`
      guarda exclui os cantos e tudo o que está fora do cartão (`[18]`). **Confirmação no Windows
      real: pendente** (ver riscos).
- [x] Arrastar continua funcionando nos dois modos e no meio de uma transição (`[19]`, `[7]`).
- [x] Sem sobreposição no expandido assentado (`[16]` verde), suíte inteira passando (195/0), testes
      novos dentro de `desktop/testes_janela_compacta.py`.
- [x] Menu ⋮ com "Sair", Configurações, Consumo, Gerar imagem, copiar/recortar/lixeira/desfazer:
      nenhum quebrado; sobrepostos continuam dentro da máscara.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py`,
      `desktop/testes_janela_compacta.py`, este `PROGRESSO.md` e `desktop/app.log` (minhas execuções
      acrescentaram linhas). O `.git/index.lock` de 27/08 **continua lá** e eu não tenho permissão
      de apagar arquivo nesta máquina — o usuário precisa rodar `del ".git\index.lock"` na raiz.

### Novas demandas / riscos
- **Honestidade sobre o que headless prova, e nesta volta é menos que nunca.** Não existe
  compositor no `offscreen`, e o plugin **nem aplica máscara**: cada `setMask` imprime
  `This plugin does not support setting window masks` no stderr. Ou seja, o efeito **visual e de
  clique** da máscara é **zero** aqui. O que ficou provado é o mecanismo (a janela não é mais
  redimensionada nem movida; a região certa é calculada e entregue ao Qt uma vez por transição) e a
  ausência de regressão em tudo o que a suíte já cobria. Se o flicker vinha do resize nativo da
  janela layered, ele deve sumir; se vinha de outra coisa, não. **Só o Windows real decide** — e o
  precedente da `CamadaPulso` (27/08) mostra que `WA_TranslucentBackground` já se comportou
  diferente nos dois ambientes.
- **Como vai parecer se a máscara não pegar no Windows** (para o usuário saber o que olhar): o modo
  compacto vai aparecer como um retângulo grande de 448x366 em vez do círculo — falha barulhenta, e
  a linha `compacto alvo=80x80 mascara=... janela=448x366` do `app.log` diz de que lado está.
- **DECISÃO QUE TOMEI SOZINHA, e é a que mais precisa de aval: o expandido pode ficar cortado pela
  borda da tela.** Como a janela não se move mais em transição, `_geometria_do_modo` deixou de
  encaixar o retângulo na tela. Medido: o cartão compacto mora a **184px** das bordas laterais da
  janela, **21px** do topo e **265px** da base. Consequência: se o usuário arrastar o botão para
  menos de 184px da lateral da tela (ou menos de 21px do topo), a janela de 448x366 fica
  parcialmente fora da tela e **o cartão expandido aparece cortado nessa borda**. Antes desta volta
  o encaixe empurrava a janela e o botão deslizava. Três saídas, e a escolha é de produto:
  (a) aceitar o corte; (b) limitar o arrasto à área em que a janela cabe — mas aí o botão não chega
  a menos de 184px das bordas laterais, o que é pior; (c) permitir **um `move()` nativo** (não
  resize) no assentamento, só quando a janela estiver fora da tela — 0 movimento no caso normal,
  que é o que os testes medem. Não implementei nenhuma: o contrato desta rodada diz 0 movimento
  nativo, e mudar isso por conta própria seria decidir no lugar do PM.
- **Outras decisões minhas, menores**: (1) `_geometria_visivel()` devolve o retângulo do **modo** —
  no expandido isso inclui os 8px de margem externa transparente, então o hover continua exatamente
  como era; a máscara é que para no cartão + 2px. (2) A `CamadaPulso` ficou **fora** da união da
  máscara: ela é um widget de 110x110 em volta de um botão de 72 e inflaria o compacto de 84 para
  96 — o anel que ela desenha cabe no cartão, e há teste para isso. (3) A abertura passou a ancorar
  (`ancorar=True`) e a ativar os dois layouts antes: sem isso o botão ainda está em (0,0) quando a
  âncora o mede e ele **saltava 184x21px na primeira expansão** (medido). (4) `_tamanho_visivel`
  existe porque `_aplicar_modo` troca `self._expandido` antes de perguntar o retângulo de partida —
  sem ele a expansão só animava os últimos 16px (medido).
- **Ganho colateral, como o PM previsto**: a área transparente do expandido (8px em volta do
  cartão) passou a ser clicável-através. Sobram os quatro cantinhos do retângulo da máscara, custo
  aceito na tarefa.
- **Atraso de até 100ms na máscara quando um sobreposto abre**: quem repõe é o vigia. Na prática é
  a borda de 6px do painel de Configurações por um décimo de segundo; se incomodar, o conserto é
  chamar `_aplicar_mascara()` ao mostrar/esconder o painel.
- **Ambiente**: o `$HOME` da ponte é **por sessão**, então o remendo da 8ª volta não existia mais —
  tive de reinstalar `PySide6-Essentials 6.9.0` (`pip --user`) e refazer o `libEGL.so.1`
  (`.deb` do Ubuntu extraído em `~/.local/qtlibs` + `LD_LIBRARY_PATH`). Nada instalado no sistema,
  nada dentro do repositório. Quem retomar daqui precisa refazer os dois.
- **Limpeza**: meus scripts de medição ficaram em `~/medicao_d32_r9/` (fora da pasta montada) e
  foram apagados no fim. Nada temporário sobrou no repositório.
- Continuam abertos, sem relação com esta volta: `.git/index.lock` de 27/08; `desktop/app.log`
  versionado e crescendo; crash do `Qt6Core.dll` (`D-31`).

### Ajuste no plano necessário?
Não para o plano; **sim para a `D-32`**, se o usuário confirmar. A rodada entrega a arquitetura que
o PM desenhou, inteira e medida. O que sobra é (1) o veredito do Windows real sobre o flicker e
sobre a máscara funcionar, e (2) a decisão de produto sobre o corte na borda da tela, descrita
acima com os três caminhos — essa é a única coisa que a tarefa não cobria e que muda o que o
usuário vê.

## [2026-09-06] — D-32, décima volta: a janela volta a caber na tela, ao preço de um `move()` (nunca de um resize)
Status: concluído (o encaixe é medido e testado; o flicker continua **sem confirmação** — headless
não tem compositor, e a máscara segue sem efeito visual aqui)

Nível `curto`. A rodada é a pendência que eu tinha deixado para o PM na 9ª volta, com o aval dele:
zero redimensionamento nativo continua absoluto, um movimento nativo passa a ser permitido.

### O que mudei
- **`_geometria_do_modo` volta a encaixar na tela — só no modo expandido.** É lá que o retângulo do
  modo é a janela inteira (448x366) e, portanto, onde a borda da tela pode cortar. O compacto
  continua ancorado no botão, sem encaixe: encaixá-lo empurraria o botão do lugar em que o usuário
  o deixou.
- **Um `move()` nativo por transição, e só quando é preciso** (`_aplicar_modo`): `destino_janela`
  é `geo_final.topLeft()` na expansão e `self.pos()` no encolhimento; o `move` roda dentro do mesmo
  bloco de `setUpdatesEnabled(False)` que já limpava a máscara, **antes** do quadro zero.
- **A ordem que o PM mandou conferir**: `_geo_transicao` passou a ser `QRect(destino_janela, ...)`
  — a janela **já movida**. Como `_set_progresso_modo` posiciona o cartão por coordenada de tela
  descontando `base.topLeft()`, é isso que segura o cartão parado no instante do deslocamento: o
  `move` arrasta o cartão junto (ele é filho), e o quadro zero o devolve ao ponto de tela de antes.
  Com a base na posição velha, o botão saltaria o deslocamento inteiro num quadro.
- **`_assentar_modo` também encaixa**, para os caminhos sem animação (abertura, reversão
  instantânea, rede de segurança): se `geo.topLeft() != self.pos()` no expandido, move ali. Na
  transição animada esse move nunca dispara — `_aplicar_modo` já pôs a janela no lugar.
- Nada mais mudou: tamanhos, animação do cartão, máscara (uma por transição), `_offset_visivel`/
  `_tamanho_visivel` e `_geometria_visivel()` intactos.

### Como testei
- **`[20]` (novo), com espião nas chamadas nativas**, com o botão colado a 10px de cada uma das
  quatro bordas da área útil: **1 `move` e 0 `resize`** na expansão em todas elas, e o retângulo
  visível **inteiro dentro da área útil** nas quatro. **Longe das bordas: 0 `move`, 0 `resize`,
  desvio 0px** — o caso comum não regrediu. E o **encolhimento não move nada em nenhum dos cinco
  casos** (a janela já está encaixada).
- **Deslizamento, não salto** (mesmo teste, quadro a quadro a 4ms): o centro do botão anda num
  sentido só nos dois eixos, e nenhum quadro carrega o deslocamento inteiro. Medido: esquerda
  213px de deslocamento com passo máximo de 40px; direita 214/38; topo 50/10; base 295/55 — o pico
  é o meio da curva `InOutCubic`, não o instante do `move`.
- **`[21]` (novo), o gesto que motivou a rodada**: arrastar o botão até 12px do canto inferior
  esquerdo, soltar (o botão fica onde o gesto o deixou, ±1px, e **não pula de volta**), passar o
  mouse — o cartão expandido cabe inteiro na área útil e o cartão branco não é cortado por borda
  nenhuma.
- **Suíte inteira: 230 verificações, 0 falhas** (eram 195; +35), rodada duas vezes seguidas. Os
  invariantes das voltas 4-9 seguem: **0 troca de `frameGeometry()`** por transição nos dois
  sentidos, 0px de desvio longe das bordas, 0 widget só-expandido visível, 61 quadros por sentido,
  sem sobreposição no expandido (`[16]`).
- **Não testei**: nada com compositor. Ver riscos.

### Critério de pronto
- [x] Janela colada em cada uma das quatro bordas, expandindo: retângulo visível inteiro dentro da
      área útil e **exatamente 1** `move()` nativo (`[20]`).
- [x] Longe das bordas, expandindo e encolhendo: **0** `move()` (`[20]`).
- [x] **0 redimensionamento nativo** em toda transição, nos dois sentidos (`[20]`, `[17]`, `[11]`,
      `[12]`).
- [x] Desvio 0px longe das bordas; perto da borda, deslizamento monótono sem salto, medido quadro a
      quadro (`[20]`).
- [x] Arrastar até a borda e expandir: sem corte, sem pulo ao soltar (`[21]`).
- [x] Suíte inteira passando (230/0), testes novos dentro do arquivo versionado.
- [x] Nenhum tamanho aprovado mudou (`[3]`, `[13]`, `[14]` verdes).
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`). Meus arquivos: `desktop/app.py`,
      `desktop/testes_janela_compacta.py`, este `PROGRESSO.md` e `desktop/app.log`. O
      `.git/index.lock` de 27/08 continua lá e eu não tenho permissão de apagá-lo: o usuário
      precisa rodar `del ".git\index.lock"` na raiz.

### Novas demandas / riscos
- **Resposta à pergunta do PM sobre a `CamadaPulso`: não há o que resolver.** Medido: gravar sempre
  expande antes (o pulso só liga em `_assentar_modo`, 7ª volta), e no expandido a máscara é
  436x354 enquanto o anel desenhado é 94x94 — cabe com folga. No compacto o temporizador está
  parado (`estado='parado'`), então não existe anel para cortar. O único desenho que a camada faz
  no compacto é o **realce de arrastar arquivo**, e ele é menor: raio do botão + 4 = 38, ou seja
  ~79px com o traço de 3px, dentro dos 84px da máscara compacta. O que fica de fora da máscara é só
  a área transparente do widget de 110x110 — nada visível.
- **Honestidade, de novo e sem encolher**: esta volta não prova nada sobre o flicker. O plugin
  `offscreen` continua imprimindo `This plugin does not support setting window masks` a cada
  `setMask`, ou seja, a máscara não tem efeito visual nem de clique aqui. O que a rodada prova é o
  contrário do que motivou o risco: que o encaixe na tela voltou **sem** trazer de volta um único
  redimensionamento nativo.
- **Risco novo, pequeno e declarado**: perto da borda, a expansão agora tem um `move()` nativo. Se
  no Windows real o deslocamento de uma janela layered também piscar (a hipótese do PM, apoiada na
  assimetria do sintoma, diz que o culpado é o resize, não o move), o flicker vai continuar
  **apenas nesse caso** — perto das bordas, expandindo. É um sintoma bem mais estreito que o de
  hoje e distinguível: se o usuário relatar pisca só num canto da tela, é este `move`.
- **Ambiente**: `PySide6-Essentials 6.9.0` (`pip --user`) e o remendo do `libEGL.so.1` em
  `~/.local/qtlibs` continuam sendo necessários e são **por sessão** — quem retomar refaz os dois.
- **Limpeza**: scripts de medição em `~/medicao_d32_r10/` (fora da pasta montada), apagados no fim.
  Nada temporário no repositório.

### Ajuste no plano necessário?
Não. A pendência que eu tinha deixado para o PM na 9ª volta está fechada com a decisão dele e
medida. O que resta é o veredito do Windows real: se o flicker do hover-out sumiu, se a máscara
pega, e se o `move` perto da borda é ou não visível.

## [2026-09-21] — Veredito do Windows real (D-32): a máscara pega, mas o tamanho da janela deriva do alvo durante o uso
Status: achado registrado, **não corrigido** — a volta anterior (10ª) rodou inteira em Linux/
`offscreen` e disse explicitamente que não podia confirmar isto; esta é a confirmação pendente.

### Contexto
Sem tarefa aberta — suporte ao vivo com o usuário rodando o app de verdade (ele perguntou "cade o
botão"). Não é o meu código (D-32 é de outra sessão); registrando o achado em vez de mexer na
state machine de 10 voltas sem ter lido as anteriores por inteiro.

### O que vi
- **A máscara funciona no Windows real** — a dúvida que a 10ª volta deixou em aberto
  ("`offscreen` não tem compositor... a máscara não tem efeito visual nem de clique aqui") está
  respondida: numa abertura limpa, `GetWindowRect` (via `EnumWindows`/P-Invoke, medido de fora do
  processo) mostra a janela em `(40,40)-(488,406)` — **exatamente** 448×366, batendo com o log
  (`compacto alvo=80x80 mascara=84x84+182+19 janela=448x366 dpr=1.25`). O recorte aparece no lugar
  certo.
- **Depois de um tempo de uso, a janela nativa sai do tamanho-alvo** — encontrado com o app já
  rodando há dias (não numa abertura fresca): `GetWindowRect` mediu `(1602,564)-(1960,857)`, ou
  seja **358×293**, exatamente `448×366 × 0,8` (= `1/1,25`, o `dpr` que o próprio log registra
  minutos antes). O `app.log` já tinha capturado o mesmo evento sozinho: `tamanho_fora_do_modo
  expandido=True alvo=448x366 real=358x293`. A máscara (`84x84+182+19`) continua calculada para o
  canvas de 448×366 — dentro de uma janela real de 358×293 ela ainda cabe geometricamente, mas o
  recorte já não coincide com onde o botão está desenhado, e o resultado que o usuário vê é uma
  área vazia (**"cadê o botão"**).
- **A rede de segurança (`_corrigir_tamanho_do_modo`, 10x/s) existe e loga o desvio, mas não
  resolve na hora** — o desvio ficou visível para o usuário até eu reiniciar o processo; não
  cronometrei quanto tempo a rede levaria para corrigir sozinha (se é que corrige — o código chama
  `setFixedSize` + `_assentar_modo` de novo, mas não vi uma segunda linha de log confirmando que
  o tamanho voltou ao alvo depois disso).
- **Reiniciar o processo resolve na hora** — testado duas vezes: matar e subir de novo sempre
  produziu `448x366` exato na primeira medição.

### Como testei
Medição de fora do processo via P/Invoke (`EnumWindows` + `GetWindowRect`/`GetWindowText`), não
`self.geometry()` de dentro do app — mede o que o Windows realmente desenhou, não o que o Qt acha
que pediu. Comparado com as linhas do próprio `app.log` (`compacto ...` e `tamanho_fora_do_modo
...`) para os mesmos instantes.

### Novas demandas / riscos
- **Bug real, não corrigido**: a janela nativa deriva do tamanho-alvo depois de algum tempo de uso
  (suspeito: troca de monitor com DPI diferente, dado que o `dpr` varia entre `1.25` e `1.0` nas
  linhas do log — o usuário tem três monitores com DPIs diferentes, já registrado como causa de
  outro bug nesta mesma máquina). Quando deriva, o botão fica praticamente inacessível até reiniciar
  o app — e o usuário não tem como saber que é isso, só vê "sumiu".
  **Sugestão para quem pegar isto**: cronometrar se `_corrigir_tamanho_do_modo` de fato converge
  sozinho (e em quanto tempo), e — se não convergir — considerar recalcular a máscara a partir do
  tamanho **real** (`self.width()/self.height()`) em vez de reafirmar o alvo lógico; hoje
  `_corrigir_tamanho_do_modo` tenta forçar a janela de volta ao alvo, mas o log mostra o desvio
  sendo registrado sem uma segunda linha confirmando que ele de fato voltou.
- Não fiz nada além de reiniciar o processo do usuário — nenhuma linha de `app.py` tocada nesta
  entrada.

### Ajuste no plano necessário?
Não é meu plano para ajustar — é o achado que a 10ª volta pediu ("o veredito do Windows real"),
com metade boa notícia (a máscara pega) e metade risco novo e confirmado (a deriva de tamanho).

## 2026-09-25 — "Abrir planejamento" no menu ⋮ (pedido direto, fora do plano — D-35)

### O que foi feito
- `desktop/app.py`: constante `URL_PLANEJAMENTO`, ícone `planejamento`, item "Abrir planejamento"
  como primeiro do menu ⋮ e o método `_abrir_planejamento` (`QDesktopServices.openUrl`, com uma
  linha no log).
- `desktop/testes_janela_compacta.py` [10]: seis itens na ordem, e o primeiro abre o link certo.
- Suíte headless: 231 verificações passaram, 0 falharam.

### O que não foi feito
- Não testado no Windows real: falta o usuário abrir o menu e clicar. Nenhum commit.

### Ajuste no plano necessário?
Não. Não muda o critério da Fase 2.
