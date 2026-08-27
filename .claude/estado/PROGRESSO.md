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
