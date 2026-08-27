# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de **2026-08-24** (encerramento da Fase 1 e abertura da **Fase 2 —
> Desktop, ditado universal**). As entradas da Fase 1 estão em
> `historico/PROGRESSO_fase1-nucleo_2026-08-23_a_2026-08-24.md`, e as dos planos anteriores nos
> outros `historico/PROGRESSO_*.md`, todas sem edição.

*(Sem entradas ainda — a primeira nasce quando o Executor concluir a primeira tarefa da Fase 2.)*

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
