## Coleta — MVP transcrição (Etapa 1)

- [DIRECIONAMENTO] Estrutura do projeto fica em subpasta `transcritor/` dentro deste mesmo
  repositório (kit agentes-base), não em repositório separado — código convive com os arquivos
  de PM/EXEC na raiz.
- [DECISÃO] `README.md` da raiz permanece como documentação do kit agentes-base; o projeto tem
  README próprio em `transcritor/README.md` — trade-off: dois READMEs no repositório, mas evita
  perder a documentação do kit e mantém a separação entre "kit" e "projeto".
- [DECISÃO] Placeholders do kit (`CLAUDE.md`, `.claude/PM.md`, `.claude/skills/
  coleta-consolidacao/SKILL.md`) preenchidos assumindo que não há projeto de escrita/relatório
  separado — trade-off: comando "aplicar" removido do fluxo; a coleta deste projeto é registro
  interno, sem promoção a um destino externo.
- [ARTEFATO] `transcritor/` criado com `backend/main.py`, `frontend/index.html`, `.env`
  (placeholder), `requirements.txt` (`openai`) e `README.md` — Etapa 1 do PLANO.md, executada e
  verificada em 2026-08-16.
- [PENDÊNCIA] `transcritor/.env` não está coberto pelo `.gitignore` — risco de vazamento da
  chave da API quando o valor real for preenchido — depende de: decisão do PM sobre ajuste
  rápido vs. nova etapa (registrado no Backlog do PLANO.md).

## Coleta — decisão sobre exceção do PM (2026-08-16)

- [DIRECIONAMENTO] Usuário autorizou, a partir de 2026-08-16, que o PM gere diretamente a tarefa
  de correção quando o Executor reportar um risco de segurança objetivo e de correção pequena —
  sem perguntar antes se vira etapa ou fica no Backlog. Critérios da exceção: risco verificável
  no artefato, correção pequena (não redesenha escopo), plano dentro do limite de 7 etapas.
  Registrado como exceção pontual no PLANO.md, não como regra silenciosa.
- [DECISÃO] Risco do `.env` fora do `.gitignore` promovido de Backlog para Etapa 2 do PLANO.md
  — trade-off: plano chega ao limite de 7 etapas; qualquer novo item de escopo agora exige
  remover algo do plano atual ou abrir um plano separado.
- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md` sobrescrito com a tarefa da Etapa 2 (proteger
  `transcritor/.env`).

## Coleta — Etapa 2 concluída (2026-08-16)

- [ARTEFATO] `.gitignore` da raiz recebeu a regra `transcritor/.env`; `transcritor/.env.example`
  criado com o placeholder `OPENAI_API_KEY=` — Etapa 2 do PLANO.md, executada e verificada em
  2026-08-16 (`git check-ignore -v` confirma a regra ativa).
- [PENDÊNCIA] Achado durante a verificação do PM (fora do escopo da Etapa 2): existe um
  `.git/index.lock` (0 bytes) que o `git status` não conseguiu remover sozinho
  ("Operation not permitted"). Pode travar um próximo `git commit` se não for removido —
  depende de: usuário verificar se não há outro processo git em andamento e, se não houver,
  apagar esse arquivo manualmente antes de commitar.

## Coleta — Etapa 3 concluída (2026-08-16)

- [ARTEFATO] `transcritor/backend/main.py` (FastAPI + Uvicorn): endpoint `POST /transcrever`
  funcional, chave lida só de `transcritor/.env`, erros tratados — Etapa 3 do PLANO.md,
  executada e verificada de ponta a ponta com a API real (transcrição correta de áudio de
  teste).
- [DECISÃO] Framework do backend: FastAPI + Uvicorn (decidido pelo Executor, a tarefa deixou em
  aberto) — trade-off: mais dependências (`fastapi`, `uvicorn`, `python-multipart`,
  `python-dotenv`) do que um servidor mínimo sem framework, mas validação automática de
  requisição e tratamento de erro ficam mais simples.
- [PENDÊNCIA] `transcritor/.venv/` e `transcritor/backend/__pycache__/` fora do `.gitignore` —
  risco pequeno (não vaza segredo, mas polui o repositório se commitado por engano) — dobrado
  para dentro da Etapa 4 em vez de virar etapa própria, porque o plano já estava no limite de 7
  etapas.

## Coleta — Etapa 4 concluída (2026-08-16)

- [ARTEFATO] `.gitignore` recebeu `transcritor/.venv/` e `transcritor/backend/__pycache__/`;
  `transcritor/backend/main.py` agora aceita o campo `modelo` (três valores válidos, padrão
  preservado, erro tratado para valor inválido) — Etapa 4 do PLANO.md, executada e verificada
  no artefato real (três modelos testados com áudio real).
- [DIRECIONAMENTO] A partir de agora, ao gerar `PROXIMA_TAREFA.md` com passo de documentação,
  incluir `transcritor/README.md` explicitamente em "Arquivos envolvidos" — nas Etapas 3 e 4 o
  Executor precisou atualizá-lo mesmo sem estar na lista.

## Coleta — Etapa 5 concluída (2026-08-16)

- [ARTEFATO] `transcritor/frontend/index.html` (HTML/CSS/JS puro): upload de arquivo, seleção
  de modelo, chamada a `POST /transcrever`, estados de carregando/sucesso/erro — Etapa 5 do
  PLANO.md, executada e verificada no artefato real (fluxo completo testado com áudio real e
  com erro proposital).
- [DECISÃO] CORS do backend liberado (`allow_origins=["*"]`) para uso 100% local — trade-off:
  simples para dev local, mas precisaria ser restringido se o backend um dia for exposto fora
  da máquina do usuário. Registrado no Backlog do PLANO.md.

## Coleta — Etapa 6 concluída (2026-08-18)

- [ARTEFATO] `transcritor/frontend/index.html`: seção de gravação pelo microfone (seletor de
  dispositivo de entrada, botão iniciar/parar gravação com indicador visual e cronômetro,
  player de prévia, botão dedicado "Transcrever gravação" reaproveitando modelo e área de
  resultado já existentes do fluxo de upload); `transcritor/README.md` documenta o fluxo — Etapa
  6 do PLANO.md, executada e verificada no artefato real pelo PM (conteúdo bate com o relatado
  no PROGRESSO.md: seletor, indicador, cronômetro, player, botão dedicado, tratamento de erro).
- [DIRECIONAMENTO] Upload de arquivo (Etapa 5) e gravação pelo microfone (Etapa 6) convivem na
  mesma página, como duas formas de entrada alternativas — usuário escolhe uma das duas.
- [DECISÃO] Nome do arquivo de áudio enviado na gravação é inferido a partir do `mimeType` do
  `MediaRecorder` (`gravacao.webm`/`.ogg`/`.mp4`) — trade-off: pequena lógica extra no frontend,
  mas evita alterar o backend, que depende da extensão do nome para reconhecer o formato.
- [ARTEFATO] Bug de CSS encontrado e corrigido durante a própria validação do Executor: regras
  `display` com origem "author" sobrescreviam `[hidden] { display: none }` do user-agent
  (author sempre vence na cascata); corrigido com `[hidden] { display: none !important; }` no
  topo do `<style>`. Testes reexecutados após a correção, todos passaram.
- [PENDÊNCIA] Nenhuma nova além da já registrada (CORS aberto, no Backlog desde a Etapa 5).

## Coleta — Etapa 7 concluída (2026-08-18) — plano de 7 etapas fechado

- [ARTEFATO] `transcritor/benchmark.py` (só biblioteca padrão do Python, sem dependência nova) e
  `transcritor/BENCHMARK.md`: os três modelos processados no mesmo áudio real (~72s), com tempo
  de resposta, custo estimado e transcrição lado a lado; `transcritor/README.md` documenta como
  rodar — Etapa 7 do PLANO.md, executada e verificada no artefato real pelo PM.
- [DECISÃO] Custo estimado calculado por duração do áudio × preço público por minuto documentado
  pela OpenAI (`https://platform.openai.com/docs/pricing`, consultado em 2026-08-18) — trade-off:
  preço pode mudar e não é puxado dinamicamente; fonte e data ficam citadas no resultado para o
  leitor conferir.
- [PENDÊNCIA→DECISÃO] Durante a Etapa 7, `gpt-4o-transcribe-diarize` falhou (HTTP 400 da OpenAI:
  `chunking_strategy is required for diarization models`, repassado pelo backend como 502) — bug
  real e pré-existente em `backend/main.py`, não introduzido pelo benchmark. Afetava também o uso
  normal do frontend (upload e gravação) sempre que esse modelo era selecionado, não só o
  benchmark.
- [DIRECIONAMENTO] O usuário pediu a correção diretamente ao Executor no chat de execução ("pode
  resolver o bug"), fora do fluxo normal PM → `PROXIMA_TAREFA.md` → Executor. O Executor sinalizou
  esse desvio explicitamente no PROGRESSO.md. Registrado aqui e no PLANO.md para rastreabilidade;
  não é a exceção de segurança já registrada (esse bug era funcional, não de segurança).
- [ARTEFATO] `transcritor/backend/main.py`: adicionado `MODELOS_QUE_EXIGEM_CHUNKING =
  ("gpt-4o-transcribe-diarize",)` e passagem condicional de `chunking_strategy="auto"` só para
  esse modelo. Verificado pelo PM no artefato real: a mudança é mínima e isolada, não toca o
  resto da lógica do endpoint.
- [ARTEFATO] Após a correção, `benchmark.py` foi rerrodado com o mesmo áudio: os três modelos
  retornaram sucesso — `gpt-4o-transcribe` 6,8s, `gpt-4o-mini-transcribe` 2,6s,
  `gpt-4o-transcribe-diarize` 43,3s (bem mais lento — é o modelo que também faz diarização/
  identificação de falantes, processamento mais pesado no lado da OpenAI). Reexecutados os testes
  de upload (Etapa 5) e gravação (Etapa 6) sem regressão; testado também pelo frontend real
  (upload com o modelo de diarização selecionado) → sucesso.
- [DIRECIONAMENTO] Com a Etapa 7 concluída, as 7 etapas do plano (limite do papel PM) estão
  fechadas — MVP validado de ponta a ponta. Qualquer novo item de escopo exige plano novo.

## Coleta — Novo plano aberto: refinamento da captura de voz (2026-08-18)

- [DIRECIONAMENTO] Com o plano do MVP fechado (7/7 etapas), o usuário pediu um refinamento
  novo na experiência de gravação, motivado por querer algo com a dinâmica de apps de voz
  modernos (tipo o modo de voz do ChatGPT). Aberto um `PLANO.md` novo para essa frente (snapshot
  do plano anterior salvo em `.claude/estado/historico/PLANO_2026-08-18c.md`).
- [DECISÃO] Interação do botão de gravação: clique único (clica para começar, clica de novo
  para parar e enviar) — não segurar/soltar. Escolhido pelo usuário entre as duas opções
  levantadas pelo PM.
- [DECISÃO] Modelo `gpt-4o-transcribe-diarize` removido da interface — usuário não gostou da
  qualidade do resultado dele. Fica comentado no código (não apagado), podendo ser reativado no
  futuro. Trade-off: perde a funcionalidade de identificar falantes por enquanto, ganha
  simplicidade na escolha de modelo.
- [DECISÃO] Seletor `<select>` de modelos substituído por um botão simples de alternar entre os
  dois modelos restantes (`gpt-4o-transcribe`, `gpt-4o-mini-transcribe`), compartilhado entre o
  fluxo de upload e o de gravação — sem caixa de seleção.
- [DECISÃO] A soma do transcript ao final (em vez de substituir) vale só para a gravação rápida;
  o upload de arquivo continua substituindo o resultado a cada envio, como hoje.
- [DIRECIONAMENTO] O PM assumiu, com aprovação do usuário, que a nova versão da gravação não vai
  mais ter seleção de dispositivo de microfone (usa o padrão do navegador) — a seção completa de
  gravação da Etapa 6 anterior será substituída pelo botão redondo. Registrado no Backlog do
  novo PLANO.md como possível item futuro se um dia for necessário escolher entre microfones.
- [PENDÊNCIA] Etapas 1 e 2 do novo plano ainda não executadas — `PROXIMA_TAREFA.md` gerada para
  a Etapa 1 (alternador de modelo, sem diarize).
- [DIRECIONAMENTO] Discussão separada (fora deste plano): usuário está avaliando, para uma fase
  futura, adotar uma plataforma self-hosted tipo Claude com agentes/skills (Open WebUI,
  LibreChat, AnythingLLM, Dify, LobeHub) como motor em vez de construir do zero. Decidiu
  continuar essa avaliação em outro chat; nenhuma ação tomada neste projeto por enquanto.

## Coleta — Etapa 1 do plano novo concluída (2026-08-18)

- [ARTEFATO] `transcritor/frontend/index.html`: `<select id="modelo">` removido; botão
  `#botaoModelo` alterna entre `gpt-4o-transcribe` e `gpt-4o-mini-transcribe` (nome do modelo
  ativo aparece no texto do botão); array `MODELOS_ATIVOS` no script com a entrada do diarize
  comentada (não apagada); upload e gravação passaram a ler o modelo de `modeloAtivo()`.
  `transcritor/README.md` atualizado — Etapa 1 do plano novo, executada e verificada no artefato
  real pelo PM (grep confirmou ausência do `<select>` antigo e presença do alternador/array).
- [DECISÃO] O campo `modelo` não está mais dentro do `<form>` (o `<select>` saiu), então o envio
  do upload passou a acrescentar `modelo` manualmente ao `FormData` via `dados.append("modelo",
  modeloAtivo())` — ajuste pontual do Executor para preservar o comportamento do backend sem
  alterá-lo.

## Coleta — Etapa 2 concluída, plano de refinamento fechado (2026-08-18)

- [ARTEFATO] `transcritor/frontend/index.html`: `#botaoGravacaoRapida` (botão redondo, clique
  único) substitui toda a seção antiga da Etapa 6; `#transcriptRapido` (`<textarea>`) acumula o
  texto de cada gravação, editável, preservando edições manuais entre gravações;
  `transcritor/README.md` documenta o novo fluxo — Etapa 2 do plano de refinamento, executada e
  verificada no artefato real pelo PM (grep confirmou ausência dos elementos antigos e presença
  dos novos). Com isso, o plano de refinamento (2/2 etapas) está fechado.
- [DIRECIONAMENTO] Usuário trouxe um pacote de pedidos novos após ver o protótipo funcionando:
  painel de configurações com seletor de microfone, cronômetro, corte de segurança por tempo
  máximo, barras de nível de áudio, correção do navegador pedindo permissão de microfone toda
  vez, painel de consumo (tokens/custo) por sessão e por dia com botão de reset, e alternância
  de streaming da transcrição. Registrado no Backlog do PLANO.md; nenhuma etapa aberta ainda,
  aguardando o usuário priorizar/aprovar.
- [DIRECIONAMENTO] Pesquisa técnica feita pelo PM (fontes oficiais da OpenAI, 2026-08-18) para
  embasar a próxima conversa com o usuário:
  - Permissão de microfone repetida: causa provável é o frontend ser aberto como `file://`
    (sem origem HTTP estável) — navegadores baseados em Chromium não persistem bem permissões
    de mídia para esse tipo de origem entre recarregamentos. Solução provável: servir o
    frontend por um servidor HTTP local (ex.: FastAPI servindo estático, ou um `http.server`
    à parte), dando origem estável para o navegador lembrar da permissão.
  - Custo/tokens: a resposta da API de transcrição pode incluir um campo `usage` — para
    `gpt-4o-transcribe`/`gpt-4o-mini-transcribe`, o tipo retornado tende a ser por duração
    (`type: "duration"`, `seconds`), consistente com a cobrança oficial ser por minuto
    ($0,006/min e $0,003/min, confirmado na página oficial de preços) — não por token, apesar de
    o schema da API também suportar um formato "tokens" (`input_tokens`/`output_tokens`) para
    outros modelos de cobrança. Ou seja, dá para calcular o custo exato por requisição sem
    estimativa (usando a duração real devolvida pela própria API, não só a duração do arquivo
    enviado). Não usa nenhuma chamada extra à API — é campo da própria resposta já feita.
  - Um painel de consumo "diário" exige persistência (algo tem que sobreviver entre reinícios do
    servidor e passar de um dia pro outro) — é a primeira vez que este projeto precisaria de
    algum tipo de armazenamento (ex.: arquivo local JSON/CSV, log por requisição), o que até
    aqui era declarado como "fora de escopo" no MVP original. Sinalizar essa mudança de escopo
    ao usuário antes de aprovar a etapa.
  - Streaming: a API da OpenAI suporta `stream=true` para transcrição de arquivo com
    `gpt-4o-transcribe`/`gpt-4o-mini-transcribe` (não `whisper-1`), devolvendo eventos de texto
    parcial conforme processa — confirmado na documentação oficial. Não há indicação de preço
    diferente por usar streaming (mesma cobrança por minuto/token do modelo, streaming muda só a
    forma de entrega). Requer endpoint novo no backend (repassar o stream da OpenAI para o
    frontend) e lógica no frontend para ir completando o texto aos poucos — maior mudança de
    escopo que as etapas anteriores, que não tocavam o backend.

## Coleta — Novo plano aberto: robustez, consumo e streaming (2026-08-18)

- [DIRECIONAMENTO] Plano de refinamento anterior (2/2 etapas) fechado; novo plano aberto com 7
  etapas (limite do papel PM), arquivado o anterior em
  `.claude/estado/historico/PLANO_2026-08-18f.md`.
- [DECISÃO] Corte automático de segurança na gravação: 2min30s (escolhido pelo usuário entre as
  opções levantadas pelo PM).
- [DECISÃO] Painel de consumo terá persistência em arquivo local (primeira persistência do
  projeto) — decisão explícita do usuário, com plano de trocar por banco de dados de verdade
  depois (registrado no Backlog). Vai ter gráfico de uso por dia e por sessão, não só números.
- [DECISÃO] Correção da permissão de microfone repetida: servir o frontend via servidor HTTP
  local (backend passa a servir o `index.html`), em vez de manter o acesso por `file://`.
  Aprovado pelo usuário mesmo mudando a forma de abrir o app (de "dois cliques" para "abrir
  http://127.0.0.1:8000").
- [DECISÃO] Botão de reset do painel de consumo zera só a visualização da sessão atual; o
  histórico diário salvo em disco não é apagado por esse botão.
- [DECISÃO] Tanto o seletor de microfone quanto o painel de consumo ficam atrás de ícones no
  mesmo estilo "avançado" ao lado do botão redondo (popover/modal), não como painéis fixos na
  tela principal.
- [DIRECIONAMENTO] Pesquisa técnica adicional do PM (fontes oficiais OpenAI, 2026-08-18): a
  cobrança de `gpt-4o-transcribe`/`gpt-4o-mini-transcribe` é na verdade por token (US$ 2,50/US$
  10,00 por milhão de tokens de entrada/saída para o primeiro; US$ 1,25/US$ 5,00 para o mini) —
  o valor "por minuto" usado no benchmark da Etapa 7 anterior é uma conversão aproximada da
  própria OpenAI, não a cobrança literal. A resposta da API já traz um campo `usage` com
  `input_tokens`/`output_tokens`/`total_tokens` automaticamente, sem parâmetro extra na
  chamada e sem custo adicional — não precisa de biblioteca de contagem de tokens. Streaming
  (`stream=true`, suportado pelos dois modelos ativos) não tem indicação de custo diferente do
  não-streaming; a confirmação prática fica para quando a Etapa 7 for implementada.
- [PENDÊNCIA] Etapa 1 (servir frontend via servidor local) tem `PROXIMA_TAREFA.md` gerada;
  demais etapas aguardando.

## Coleta — Etapa 1 concluída; adendo de validação de áudio (2026-08-18)

- [ARTEFATO] `transcritor/backend/main.py`: `StaticFiles` montado em `/` (depois da rota
  `POST /transcrever`, sem colisão); `transcritor/README.md` documenta abrir via
  `http://127.0.0.1:8000/` — Etapa 1 do plano de robustez/consumo, executada e verificada no
  artefato real pelo PM (grep confirmou o mount e a instrução no README).
- [DIRECIONAMENTO] Usuário percebeu que gravações em silêncio (ou clique acidental sem falar)
  ainda eram enviadas para transcrição e a API "alucinava" texto em outro idioma em vez de
  reconhecer que não havia fala. Pediu uma validação: se o áudio captado não tem picos de volume
  relevantes, não enviar.
- [DECISÃO] Essa validação foi incorporada à Etapa 4 (barras de nível de áudio) em vez de virar
  etapa nova — reaproveita o mesmo `AnalyserNode` da Web Audio API que já seria usado para o
  visualizador, mantendo o plano dentro do limite de 7 etapas. Trade-off: a Etapa 4 fica um
  pouco mais carregada (dois critérios de pronto relacionados) em vez de duas etapas menores.

## Coleta — detalhe da Etapa 4 e tarefa da Etapa 2 gerada (2026-08-18)

- [DECISÃO] O aviso de "nenhuma fala detectada" (Etapa 4) será um popup rápido (toast, alguns
  segundos, sem bloquear a tela), não uma mensagem fixa na área de status — registrado no
  PLANO.md para quando essa etapa for executada.
- [PENDÊNCIA] `PROXIMA_TAREFA.md` gerada para a Etapa 2 (painel de configurações com seletor de
  microfone, atrás de um ícone de engrenagem) — próxima na ordem sequencial do plano.

## Coleta — Etapa 2 concluída (2026-08-18)

- [ARTEFATO] `transcritor/frontend/index.html`: ícone `#botaoConfiguracoes` (classe
  `.icone-avancado`, reaproveitável) abre modal com seletor de microfone; escolha guardada em
  `dispositivoEscolhido` e aplicada na gravação seguinte via `deviceId`; sem escolha, mantém o
  padrão — Etapa 2 do plano de robustez/consumo, executada e verificada no artefato real pelo PM.
- [DIRECIONAMENTO] Classe CSS `.icone-avancado` criada de propósito para ser reaproveitada pelo
  ícone de consumo (Etapas 5/6), mantendo a mesma linguagem visual pedida pelo usuário.

## Coleta — Etapa 3 concluída (2026-08-18)

- [ARTEFATO] `transcritor/frontend/index.html`: cronômetro `#cronometroGravacaoRapida` (mm:ss);
  corte automático fixo em 150000ms (2min30s) via `cortarPorSegurancaGravacaoRapida()`,
  reaproveitando o caminho de parada manual; temporizadores cancelados corretamente em qualquer
  parada — Etapa 3 do plano de robustez/consumo, executada e testada pelo Executor de ponta a
  ponta com tempo real (sem acelerar relógio), e verificada no artefato real pelo PM.
- [PENDÊNCIA] Executor sinalizou: a mensagem de corte por segurança reaproveita a classe visual
  `erro` (vermelha), igual a falhas reais — decisão deliberada dele para chamar atenção, mas
  registra que trocar para um estilo de "aviso" dedicado (ex.: amarelo/laranja) é um ajuste
  pequeno se o PM/usuário preferir. Sem ação tomada; aguardando preferência.

## Coleta — Etapa 4 concluída (2026-08-18)

- [ARTEFATO] `transcritor/frontend/index.html`: `#barrasNivel` reage ao RMS do `AnalyserNode`
  (mesmo `MediaStream` da gravação, sem segundo `getUserMedia`); `picoVolumeRapido` acumula o
  maior pico da gravação inteira; `LIMIAR_SILENCIO = 0.02` decide se envia para `/transcrever`
  ou mostra `mostrarToastSemFala()` — Etapa 4 do plano de robustez/consumo, testada pelo
  Executor com áudio real (fake-audio-device do Chrome, `.wav` de silêncio e de tom simulando
  fala) e verificada no artefato real pelo PM.
- [DECISÃO] Se o navegador não suportar Web Audio API, a checagem de silêncio é pulada e a
  gravação sempre envia (comportamento antigo) — evita bloquear todas as gravações num navegador
  sem suporte, em vez de travar a funcionalidade inteira.
- [DIRECIONAMENTO] Técnica de teste registrada pelo Executor para reuso futuro: Chrome com
  `--use-fake-device-for-media-stream` + `--use-file-for-fake-audio-capture=<wav>` alimenta
  `getUserMedia` com áudio real de um arquivo, útil para validar fluxos de captura de áudio sem
  hardware físico disponível no ambiente de teste.

## Coleta — PM retoma thread; Etapa 5 confirmada concluída (2026-08-18)

- [ARTEFATO] PM retomou a thread via `_RETOMADA_robustez-consumo.md` e conferiu a Etapa 5
  diretamente no artefato real (não só no relato do `PROGRESSO.md`): `transcritor/backend/main.py`
  tem `_registrar_consumo`, `_calcular_custo_usd`, o contador em memória `_consumo_sessao` e o
  endpoint `GET /consumo`; `transcritor/consumo.jsonl` existe em disco; `transcritor/README.md`
  documenta o endpoint com exemplo real de resposta — Etapa 5 marcada concluída no `PLANO.md`.
- [DIRECIONAMENTO] Aprovado pelo usuário seguir direto para a Etapa 6 (painel de consumo no
  frontend) — `PROXIMA_TAREFA.md` gerado nesta thread.
- [PENDÊNCIA] `.git/index.lock` (0 bytes, criado em 2026-08-16, mesmo achado da Etapa 2 do MVP)
  ainda presente na raiz do repositório — confirmado pelo PM em 2026-08-18, continua sem solução
  — depende de: usuário remover manualmente antes de qualquer `git add`/`git commit`.

## Coleta — Etapa 6 implementada (2026-08-18) — validação real pendente

- [ARTEFATO] `transcritor/frontend/index.html`: ícone `#botaoConsumo` (`.icone-avancado`) e modal
  `#fundoConsumo` mostrando sessão atual, histórico diário e gráfico de barras (CSS puro) a partir
  de `GET /consumo`; botão "Resetar sessão" zera a exibição via baseline em memória, sem tocar em
  `consumo.jsonl`; `transcritor/README.md` documenta o painel — Etapa 6 do PLANO.md, implementada
  e verificada no artefato real pelo PM, mas **não testada de ponta a ponta com o backend real**
  (ver pendência abaixo).
- [DECISÃO] Gráfico de custo por dia feito só com HTML/CSS (sem Chart.js/dependência nova) —
  trade-off: menos polido visualmente que uma biblioteca dedicada, mas sem dependência de CDN
  externo para um gráfico simples de poucas barras.
- [DECISÃO] Semântica do "Resetar sessão": baseline em memória (sessão exibida = total do backend
  − baseline no momento do reset), em vez de travar a exibição em zero até recarregar a página —
  trade-off: mais útil (sessão volta a crescer com novas transcrições após o reset), mas é uma
  interpretação da tarefa que não estava 100% explícita; PM/usuário deve confirmar se é o
  comportamento desejado.
- [PENDÊNCIA] Etapa 6 não foi testada de ponta a ponta com o backend real rodando na máquina do
  usuário (com `OPENAI_API_KEY` real e transcrições reais) — a implementação aconteceu nesta
  sessão de PM em nuvem, sem acesso ao backend local; validado só com Playwright e resposta
  mockada do `/consumo` (dados equivalentes aos reais da Etapa 5) — depende de: usuário (ou uma
  sessão EXEC local) rodar o backend, fazer 1-2 transcrições reais, abrir o painel e conferir os
  números, e testar o reset com dados reais.

## Coleta — Correção de processo do PM; tarefa da Etapa 7 gerada (2026-08-18)

- [DIRECIONAMENTO] Usuário corrigiu o PM: ao pedir "pode fazer a próxima tarefa", a intenção não
  era autorização geral para o PM virar Executor sempre — o PM deve, por padrão, ficar só no
  papel de planejar/coordenar/gerar `PROXIMA_TAREFA.md`, mesmo dentro do mesmo chat; só executa
  código se pedido de forma explícita e pontual. A Etapa 6 (já implementada por este PM) não foi
  desfeita a pedido do próprio usuário.
- [DIRECIONAMENTO] Usuário pediu para reduzir o volume de testes durante a execução: nada de
  bateria de testes exaustiva a cada iteração pequena — validação básica ao longo do caminho é
  suficiente; a bateria de testes mais completa fica para o final da etapa, quando ela estiver
  pronta. Direcionamento repassado explicitamente na `PROXIMA_TAREFA.md` da Etapa 7 (seção
  "Sobre o ritmo de testes nesta tarefa"), para valer também nas etapas seguintes.
- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md` sobrescrito com a tarefa da Etapa 7 (streaming do
  transcript) — envolve `transcritor/backend/main.py` (parâmetro `stream`, resposta em
  streaming), `transcritor/frontend/index.html` (alternador + exibição incremental) e
  `transcritor/README.md`.

## Coleta — Etapa 7 concluída (2026-08-19) — plano de robustez/consumo/streaming fechado (7/7)

- [ARTEFATO] `transcritor/backend/main.py` (`stream: bool = Form(False)`,
  `_gerar_eventos_transcricao_stream`, `StreamingResponse` em NDJSON),
  `transcritor/frontend/index.html` (`#botaoStreaming`, `consumirStreamTranscricao`,
  compartilhado entre upload e gravação) e `transcritor/README.md` (seção "Streaming do
  transcript") — Etapa 7 do PLANO.md, executada pelo Executor e verificada no artefato real pelo
  PM. De passagem, resolveu também a pendência de validação real da Etapa 6 (painel de consumo
  testado contra o backend de verdade, com dados reais gerados pelos testes desta etapa).
- [DECISÃO] Erro no meio do streaming não pode virar HTTP 4xx/5xx (o `StreamingResponse` já
  enviou status 200 antes de começar a iterar) — vira uma linha `{"tipo":"erro",...}` dentro do
  próprio stream NDJSON — trade-off: cliente precisa checar essa linha em vez de confiar só no
  status HTTP; erros detectáveis antes do stream começar (modelo inválido, chave ausente, arquivo
  vazio) continuam como HTTP normal.
- [PENDÊNCIA→DECISÃO] Usuário reportou "streaming não funciona" após a Etapa 7 — investigado pelo
  Executor: não era bug, é que em áudios curtos (~1s) a API termina rápido demais (791ms, delta
  final em <25ms) para o efeito de texto "aparecendo aos poucos" ser perceptível a olho nu; em
  áudios longos (~25s) o efeito é claramente visível (33 passos ao longo de ~1,4s). Comportamento
  inerente à API, não um bug. Item novo registrado no Backlog do PLANO.md: se o usuário quiser o
  efeito visível mesmo em áudios curtos, precisaria de um adiantamento artificial de exibição —
  decisão pendente do usuário.
- [DIRECIONAMENTO] Plano de robustez/consumo/streaming fechado — 7/7 etapas concluídas e
  verificadas pelo PM no artefato real. `PROXIMA_TAREFA.md` foi sobrescrito com um aviso de
  "nenhuma tarefa ativa" (para não repetir a confusão de duas checagens anteriores do Executor
  achando que a Etapa 7 ainda estava pendente). Próximos passos ficam a critério do usuário: abrir
  um plano novo, ou decidir o item do efeito de streaming em áudio curto.

## Coleta — Novo plano aberto: transcrição em tempo real + linha do tempo de consumo (2026-08-19)

- [DIRECIONAMENTO] Usuário perguntou se dava pra transcrever em tempo real (enquanto ainda fala),
  diferente do streaming da Etapa 7 do plano anterior (que só exibe incrementalmente o texto de
  um áudio já gravado). Pesquisado: a OpenAI separou isso em dois modelos — `gpt-transcribe`
  (lote, sucessor do `gpt-4o-transcribe`, US$ 0,0045/min) e `gpt-live-transcribe` (tempo real,
  US$ 0,017/min, ~3,8x mais caro) — fonte: developers.openai.com/api/docs e cometapi.com
  (comparativo gpt-transcribe vs gpt-live-transcribe).
- [DECISÃO] Avaliada uma alternativa DIY (transcrever em blocos maiores, com sobreposição/
  redundância entre blocos pra manter contexto nas bordas) — nas contas feitas em 2026-08-19,
  mesmo um cenário generoso de sobreposição (bloco de 10s com 5s de overlap, ~83% de áudio extra
  cobrado) sai mais barato que a API ao vivo (≈ US$ 0,011/min vs US$ 0,017/min) — trade-off:
  mais barato por minuto, mas exige construir e testar a lógica de continuidade nas bordas na
  mão, com risco de bug. Decisão do usuário: priorizar a API ao vivo primeiro, por ser mais
  simples de integrar (a API já resolve continuidade sozinha); ideia de blocos com redundância
  vai pro Backlog do PLANO.md pra testar depois.
- [DECISÃO] Persistência de conteúdo: decidido persistir só a **transcrição (texto)** de cada
  requisição, não o áudio em si — trade-off: menos espaço em disco, sem preocupação de retenção/
  limpeza de mídia, mas não permite reprocessar/reouvir o áudio original depois. Armazenamento
  rústico por append num arquivo novo, `transcricoes.jsonl`, separado do `consumo.jsonl` (ligado
  por timestamp/id compartilhado).
- [DIRECIONAMENTO] Painel de consumo ganha uma visualização de linha do tempo: cada requisição
  como um ponto, preço escrito acima do ponto, zoom por hora/minuto, popup ao clicar mostrando o
  texto transcrito — objetivo explícito do usuário é comparar custo entre requisições próximas
  no tempo (ex.: mesmo áudio mandado pra dois modelos diferentes, pra comparar custo/qualidade).
- [ARTEFATO] `.claude/estado/PLANO.md` reescrito com o plano novo (6 etapas); versão anterior
  (robustez/consumo/streaming, 7/7 concluídas) arquivada em
  `.claude/estado/historico/PLANO_2026-08-19b.md`. `.claude/estado/PROXIMA_TAREFA.md`
  sobrescrito com a tarefa da Etapa 1 (autenticação/conexão com a API ao vivo).

## Coleta — Etapa 1 do plano de tempo real concluída (2026-08-19)

- [DECISÃO] Autenticação da sessão em tempo real: **token efêmero** (não relay) — confirmado
  empiricamente contra a API real (`cliente.realtime.client_secrets.create`, SDK `openai==3.1.0`,
  já suportado sem mudar `requirements.txt`) que o navegador abre WebSocket direto com a OpenAI
  (`wss://api.openai.com/v1/realtime`, subprotocolo `["realtime", "openai-insecure-api-key." +
  token]`) sem o backend precisar repassar áudio/eventos — trade-off: mais simples e sem duplicar
  latência, mas a chave real nunca vira relay — a única superfície exposta ao navegador é o token
  de curta duração (`ek_...`).
- [ARTEFATO] `transcritor/backend/main.py`: novo endpoint `GET /tempo-real/token`, constante
  `MODELO_TEMPO_REAL = "gpt-live-transcribe"`, `turn_detection: None` (obrigatório para sessão de
  transcrição), mesmo padrão de erro dos outros endpoints (503 chave ausente, 502 falha da API).
  `transcritor/README.md` ganhou a seção "Transcrição em tempo real (ponte de autenticação)".
- [DIRECIONAMENTO] Formato de evento do modo ao vivo confirmado empiricamente, diferente do
  streaming em lote da Etapa 7 do plano anterior — importante para as Etapas 2 e 3: delta em
  `conversation.item.input_audio_transcription.delta` (campo `delta`); final em
  `conversation.item.input_audio_transcription.completed` (campo `transcript` + `usage`,
  reaproveitável por `_calcular_custo_usd` trocando o preço por minuto de `gpt-live-transcribe`).
- [ARTEFATO] `.claude/estado/PLANO.md`: Etapa 1 marcada concluída pelo PM, verificada contra o
  artefato real (não só o relato do Executor). Snapshot anterior arquivado em
  `.claude/estado/historico/PLANO_2026-08-19c.md`.

## Coleta — Nota de processo: escrita em `.claude/` via bridge remoto (2026-08-19)

- [PENDÊNCIA] Retomada desta thread demorou ~10 minutos — usuário questionou o trade-off de abrir
  chat novo vs. continuar no anterior. Causa raiz identificada: a ferramenta padrão de gravar
  arquivo remoto (bridge do dispositivo, Cowork) recusa qualquer caminho dentro de `.claude/`; a
  alternativa usada na hora (reescrever o arquivo inteiro em base64 e decodificar via shell) foi
  lenta de gerar — não é um custo inerente ao processo de retomada em si.
- [DECISÃO] Daqui pra frente, gravação em `.claude/estado/` (PLANO.md, PROXIMA_TAREFA.md,
  historico/) em sessões via bridge remoto usa `cat > "<arquivo>" <<'EOF' ... EOF` diretamente no
  terminal remoto, em vez da ferramenta de gravar arquivo (bloqueada) ou de reescrita em base64
  (lenta) — trade-off: mais rápido de gerar, mas exige rodar via shell em vez da ferramenta
  padrão de escrita. Registrado como nota técnica permanente em `.claude/PM.md` (seção "Nota
  técnica: como gravar em `.claude/estado/`") para não repetir o mesmo atraso em retomadas
  futuras. Não se aplica a sessões com acesso direto ao sistema de arquivos (ex.: Claude Code
  local) nem a arquivos fora de `.claude/` (`coleta/` continua usando a ferramenta normal).

## Coleta — Etapa 2 do plano de tempo real concluída (2026-08-19)

- [DECISÃO] Formato de envio de áudio cliente→servidor confirmado na documentação oficial (via
  WebFetch, não presumido): evento `input_audio_buffer.append` (áudio PCM16 em base64) para
  enviar pedaços de áudio; como a sessão usa `turn_detection: null` (decisão da Etapa 1), é
  necessário enviar `input_audio_buffer.commit` explicitamente para a API processar o áudio
  acumulado — sem isso a transcrição nunca dispararia.
- [DECISÃO] Captura de áudio via `AudioContext` + `ScriptProcessorNode` (não `AudioWorklet`) —
  trade-off: `ScriptProcessorNode` está formalmente depreciado, mas evita precisar de um módulo
  externo/Blob URL, mantendo o frontend em arquivo único (`index.html`), no mesmo padrão do
  resto do projeto.
- [DECISÃO] Intervalo de commit calibrado empiricamente em 3s (mínimo ~100ms de áudio acumulado),
  já que a documentação da API não recomenda nenhum valor — trade-off: funcionou sem erro nos
  testes feitos, mas não foi testado em rede lenta/instável nem em sessões de vários minutos.
- [ARTEFATO] `transcritor/frontend/index.html`: alternador `#botaoTempoReal`,
  `iniciarGravacaoTempoReal`/`pararGravacaoTempoReal`, exibição incremental via
  `conversation.item.input_audio_transcription.delta`/`.completed`, tratamento de três cenários
  de erro (falha ao obter token, erro da API durante a sessão, queda de conexão). `transcritor/
  README.md`: seção "Transcrição em tempo real" reescrita (ponte de autenticação, formato dos
  eventos, limitações desta etapa).
- [ARTEFATO] `.claude/estado/PLANO.md`: Etapa 2 marcada concluída pelo PM, verificada contra o
  artefato real. Snapshot anterior arquivado em `.claude/estado/historico/PLANO_2026-08-19d.md`.
- [PENDÊNCIA] Usuário reportou quebra de linha a cada ~3s no modo tempo real, sem relação com
  pausas na fala — rastro visível do commit de tempo fixo. Registrado no Backlog do `PLANO.md`
  com três alternativas levantadas pelo Executor — depende de: decisão do usuário sobre qual
  caminho seguir (ou nenhum, se aceitável como está).
- [PENDÊNCIA] Sem corte de segurança por tempo nem detecção de silêncio no modo tempo real
  (diferente da gravação normal) — registrado no Backlog do `PLANO.md` — depende de: decisão do
  usuário/PM sobre se entra em alguma etapa futura, especialmente combinado com o custo por
  minuto da Etapa 4 (renumerada).

## Coleta — Nova etapa aprovada: ajuste de exibição e commit no modo tempo real (2026-08-19)

- [DECISÃO] Sobre a quebra de linha a cada ~3s: usuário escolheu texto contínuo, sem quebra entre
  turnos — trade-off: mais simples de implementar (só frontend), mas não resolve a causa raiz (o
  corte continua sendo por tempo fixo, só deixa de ser visível); as outras duas alternativas
  (ajustar intervalo sozinho, ou trocar para detecção de silêncio da API) ficaram descartadas por
  ora, não removidas como possibilidade futura.
- [DECISÃO] Usuário pediu também dobrar o intervalo de commit de 3s para 6s, exploratório ("pra
  eu ver o que faz") — trade-off: intervalo maior pode significar blocos de transcrição mais
  longos por commit (potencialmente mais precisos) mas também mais delay até o texto do turno
  atual fechar; ainda um valor fixo, não calibrado por nenhum critério além de "dobrar o que já
  tinha".
- [DIRECIONAMENTO] Os dois ajustes acima foram promovidos do Backlog para uma nova **Etapa 3**
  do plano (antes ocupada por "Consumo no modo ao vivo", que virou Etapa 4; demais etapas
  renumeradas — plano fecha em 7/7, no limite do papel PM).
- [ARTEFATO] `.claude/estado/PLANO.md` reescrito com a Etapa 3 nova e renumeração; snapshot
  anterior arquivado em `.claude/estado/historico/PLANO_2026-08-19e.md`.
  `.claude/estado/PROXIMA_TAREFA.md` sobrescrito com a tarefa da nova Etapa 3.

## Coleta — Etapa 3 reaberta: discrepância entre teste e observação ao vivo (2026-08-19)

- [PENDÊNCIA] Executor reportou Etapa 3 concluída no PROGRESSO.md, com commits reais medidos via
  Playwright a 6003ms/5998ms do início da gravação. Usuário, testando ao vivo (cache do navegador
  já descartado com recarregamento forçado), reporta que o primeiro texto aparece antes de
  passarem 6s — contradiz a validação registrada. Usuário levantou a hipótese de que a API pode
  estar fazendo streaming em tempo real independente do intervalo de commit — depende de:
  investigação do Executor com instrumentação de timestamps de delta vs. commit (tarefa gerada).
- [DIRECIONAMENTO] PM não marcou a Etapa 3 como concluída no `PLANO.md` apesar do relato do
  Executor — status alterado para "em verificação", registrando a contradição, até a investigação
  trazer evidência (positiva ou negativa). Segue a regra do papel PM de conferir critério de
  pronto no artefato/comportamento real, não só no relato.
- [ARTEFATO] `.claude/estado/PLANO.md`: Etapa 3 marcada "em verificação"; snapshot anterior
  arquivado em `.claude/estado/historico/PLANO_2026-08-19f.md`. `.claude/estado/PROXIMA_TAREFA.md`
  sobrescrito com tarefa de investigação (captura de timestamps de commit + delta + completed via
  WebSocket, sem alterar comportamento do app).

---

---

## Consolidado (2026-08-19) — resumo nas 4 categorias, para revisão

> Gerado no comando "consolidar". Cobre toda a coleta acima, do início do projeto (MVP) até a
> abertura do plano de transcrição em tempo real + linha do tempo de consumo, em 2026-08-19.
> Substitui o resumo anterior (datado de 2026-08-18, que só cobria até a Etapa 4 do plano de
> robustez/consumo). Proposta para revisão — nada aqui é destino final separado, este resumo já
> é o produto da coleta.

### Decisões
- README da raiz permanece documentação do kit `agentes-base`; o projeto tem README próprio em
  `transcritor/README.md` (dois READMEs, mantém a separação kit/projeto).
- Placeholders do kit preenchidos assumindo que não há projeto de escrita/relatório separado — o
  comando "aplicar" não é usado neste projeto.
- Backend em FastAPI + Uvicorn (decidido pelo Executor, a tarefa original deixou em aberto).
- CORS aberto (`allow_origins=["*"]`) para uso 100% local — revisar se um dia for exposto fora
  da máquina (Backlog).
- Usuário autorizou, a partir de 2026-08-16, que o PM gere diretamente a tarefa de correção
  quando o Executor reportar um risco de segurança objetivo e de correção pequena, sem perguntar
  antes se vira etapa ou fica no Backlog (exceção pontual, não regra silenciosa).
- Interação da gravação rápida: clique único (clica para começar, clica de novo para parar e
  enviar), não segurar/soltar.
- Modelo `gpt-4o-transcribe-diarize` removido da interface (comentado no código, não apagado) —
  qualidade insatisfatória na avaliação do usuário.
- Seletor de 3 modelos substituído por alternador simples entre os 2 modelos restantes,
  compartilhado entre upload e gravação.
- Soma do transcript ao final (em vez de substituir) vale só para a gravação rápida; upload
  continua substituindo a cada envio.
- Corte automático de segurança na gravação: 2min30s.
- Painel de consumo com persistência em arquivo local (primeira persistência do projeto) — trocar
  por banco de dados de verdade fica para depois (Backlog).
- Correção da permissão de microfone repetida: servir o frontend via servidor HTTP local
  (`http://127.0.0.1:8000/`) em vez de abrir por `file://`.
- Cobrança real de `gpt-4o-transcribe`/`gpt-4o-mini-transcribe` é por token — o registro de
  consumo (Etapa 5 do plano de robustez) usa o campo `usage` de tokens da própria resposta da
  API; o valor "por minuto" usado no benchmark é uma conversão aproximada da OpenAI, não a
  cobrança literal desses dois modelos.
- Botão de reset do painel de consumo zera só a sessão atual (baseline em memória: sessão exibida
  = total do backend − baseline no momento do reset); o histórico diário salvo em disco não é
  apagado por ele.
- Seletor de microfone e painel de consumo ficam atrás de ícones "avançados" (popover/modal, classe
  `.icone-avancado` reaproveitada), não fixos na tela principal.
- Validação de "nenhuma fala detectada" incorporada à Etapa 4 do plano de robustez (barras de
  nível), reaproveitando o mesmo `AnalyserNode`, em vez de virar etapa própria; aviso é um popup
  rápido (toast), não mensagem fixa; sem suporte a Web Audio API, a checagem é pulada (grava
  sempre envia) em vez de bloquear a funcionalidade inteira.
- Gráfico de custo por dia do painel de consumo feito só com HTML/CSS (sem Chart.js/dependência
  nova), para não depender de CDN externo.
- Erro no meio do streaming (Etapa 7 do plano de robustez) não pode virar HTTP 4xx/5xx (o
  `StreamingResponse` já enviou status 200) — vira uma linha `{"tipo":"erro",...}` dentro do
  próprio stream NDJSON.
- Efeito de streaming imperceptível em áudios curtos (~1s) é comportamento inerente da API
  (confirmado cronometrado), não um bug — decisão de adiantamento artificial de exibição fica
  pendente do usuário (Backlog).
- Avaliada alternativa de transcrição em blocos com sobreposição/redundância (contexto nas
  bordas) — mesmo com sobreposição generosa (10s de bloco, 5s de overlap), sai mais barata que a
  API ao vivo (≈ US$ 0,011/min vs US$ 0,017/min), mas exige lógica própria de continuidade nas
  bordas; decisão do usuário em 2026-08-19: priorizar a API ao vivo primeiro por simplicidade de
  integração, blocos com redundância ficam no Backlog para testar depois.
- No plano de transcrição em tempo real (aberto em 2026-08-19): persistir só a transcrição
  (texto) de cada requisição, não o áudio — arquivo novo `transcricoes.jsonl`, rústico por
  append, ligado ao `consumo.jsonl` por timestamp/id compartilhado; linha do tempo no painel de
  consumo mostra o preço acima de cada ponto e abre um popup com o texto ao clicar.
- Usuário corrigiu o PM em 2026-08-18: pedir "pode fazer a próxima tarefa" não é autorização
  geral para o PM virar Executor sempre — por padrão o PM só planeja/coordena/gera
  `PROXIMA_TAREFA.md`, mesmo dentro do mesmo chat; só executa código se pedido de forma explícita
  e pontual (a Etapa 6 já implementada por essa exceção não foi desfeita).
- Usuário pediu para reduzir o volume de testes durante a execução: validação básica ao longo do
  caminho é suficiente; bateria de testes mais completa fica reservada para o final de cada
  etapa — direcionamento válido para todas as etapas seguintes, não só a que motivou o pedido.
- Cabeçalhos de seção da coleta seguem o padrão de um único parêntese reservado para a data — sem
  parênteses duplicados (corrigido em 2026-08-19, comparado com os cabeçalhos originais).

### Artefatos
- `transcritor/` (backend, frontend, `.env`, `requirements.txt`, `README.md`) criado, com
  `.gitignore` protegendo `.env`, `.venv/` e `__pycache__/`.
- `backend/main.py`: endpoint `POST /transcrever` (FastAPI) — aceita `modelo` (3 valores,
  `chunking_strategy` condicional para o diarize), CORS liberado (`GET`+`POST`), serve o
  frontend como estático via `StaticFiles` em `/`; registro de consumo por requisição
  (`_registrar_consumo`, `_calcular_custo_usd`, contador `_consumo_sessao`) persistido em
  `transcritor/consumo.jsonl`; endpoint `GET /consumo` (sessão + histórico diário); suporte a
  streaming (`stream`, `_gerar_eventos_transcricao_stream`, `StreamingResponse` em NDJSON).
- `frontend/index.html`: evoluiu de upload simples → alternador de modelo (sem diarize) → botão
  redondo de gravação rápida com transcript cumulativo/editável (`#transcriptRapido`) → ícone de
  configurações com seletor de microfone (`#botaoConfiguracoes`) → cronômetro + corte de
  segurança (2min30s) → barras de nível de áudio + validação de silêncio (popup "Não foi
  identificado nenhuma fala") → ícone/painel de consumo (`#botaoConsumo`, sessão, histórico
  diário, gráfico CSS, botão "Resetar sessão") → alternador de streaming (`#botaoStreaming`,
  `consumirStreamTranscricao`, compartilhado entre upload e gravação).
- `transcritor/benchmark.py` + `BENCHMARK.md`: comparação dos 3 modelos (tempo de resposta, custo
  estimado, transcrição lado a lado).
- `transcritor/README.md` atualizado a cada etapa relevante, documentando cada fluxo novo.
- Bug corrigido: `gpt-4o-transcribe-diarize` exigia `chunking_strategy` (main.py corrigido,
  isolado, sem tocar outros modelos).
- Bug de CSS corrigido: `[hidden] { display: none !important; }` (regra "author" sobrescrevia o
  `[hidden]` padrão do user-agent).
- `.claude/estado/PLANO.md` passou por três planos fechados (MVP, 7/7; refinamento da captura de
  voz, 2/2; robustez/consumo/streaming, 7/7) e um quarto plano aberto agora (transcrição em tempo
  real + linha do tempo de consumo, 6 etapas) — históricos em `.claude/estado/historico/`.

### Direcionamentos
- Projeto vive em `transcritor/`, dentro do mesmo repositório do kit `agentes-base`.
- Ao gerar `PROXIMA_TAREFA.md` com passo de documentação, sempre incluir
  `transcritor/README.md` explicitamente em "Arquivos envolvidos".
- Upload de arquivo e gravação pelo microfone convivem como duas formas de entrada alternativas.
- Discussão paralela, fora do escopo deste projeto/plano: usuário avaliando adotar uma
  plataforma self-hosted tipo Claude com agentes/skills (Open WebUI, LibreChat, AnythingLLM,
  Dify, LobeHub) como motor para uma fase futura — decidiu continuar essa avaliação em outro
  chat; nenhuma ação tomada aqui.
- Pesquisa técnica registrada ao longo do projeto: causa da permissão de microfone repetida
  (`file://` sem origem HTTP estável); cobrança real por token (não por minuto); streaming
  suportado pela API sem indicação de custo adicional; técnica de teste com fake-audio-device do
  Chrome para simular microfone com áudio real em ambiente sem hardware físico; comparativo de
  preço `gpt-transcribe` (lote) vs `gpt-live-transcribe` (tempo real, ~3,8x mais caro).
- Classe CSS `.icone-avancado` criada de propósito para ser reaproveitada entre os ícones
  "avançados" (configurações, consumo).
- PM deve, por padrão, ficar só no papel de planejar/coordenar/gerar tarefa — só executa código
  se pedido de forma explícita e pontual (não é autorização permanente).
- Ritmo de testes: validação básica durante a execução, bateria completa reservada para o final
  de cada etapa.
- Objetivo da linha do tempo do painel de consumo (plano atual): comparar custo entre requisições
  próximas no tempo, ex. o mesmo áudio mandado para dois modelos diferentes.
- Nota de processo registrada no `PLANO.md` atual: ao gerar a tarefa da Etapa 5 (linha do tempo),
  lembrar o Executor de consultar a skill `dataviz` antes de escrever código de visualização.

### Pendências
- `.git/index.lock` (0 bytes, achado em 2026-08-16 na Etapa 2 do MVP, confirmado ainda presente
  em 2026-08-18) — depende de: usuário remover manualmente antes de qualquer `git add`/commit.
- CORS aberto — revisar se o projeto um dia for servido fora da máquina local (Backlog).
- Estilo visual do aviso de corte de segurança reaproveita a cor de "erro" — Executor sugeriu um
  estilo de "aviso" dedicado; decisão pendente do usuário/PM.
- Efeito de streaming imperceptível em áudios curtos — decisão pendente do usuário sobre um
  adiantamento artificial de exibição (Backlog do plano atual).
- Transcrição em blocos com redundância — Backlog do plano atual, para testar depois da API ao
  vivo.
- Exploração de plataforma self-hosted tipo Claude (Open WebUI, LibreChat, AnythingLLM, Dify,
  LobeHub) segue em aberto, para continuar em outro chat.
- Rotação/limpeza automática de transcrições antigas em `transcricoes.jsonl` — sem política de
  retenção definida (Backlog do plano atual).
- Trocar os arquivos locais (`consumo.jsonl`, `transcricoes.jsonl`) por um banco de dados de
  verdade — decisão de adiar (Backlog).
- Plano atual (transcrição em tempo real + linha do tempo de consumo): Etapa 1 tem
  `PROXIMA_TAREFA.md` gerada, ainda não executada; demais 5 etapas aguardando.

## [2026-08-19] Investigação: discrepância "texto aparece antes do primeiro commit" — resolvida

[DECISÃO] Etapa 3 (ajuste de exibição e intervalo de commit no modo tempo real) confirmada como
**concluída**. A discrepância reportada pelo usuário — texto aparecendo na tela antes de passarem
os 6s do intervalo de commit — foi investigada com evidência real (não suposição) e não é um bug:
é o comportamento esperado da Realtime API da OpenAI.

[ARTEFATO] Investigação do Executor (diagnóstico apenas, nenhuma mudança de código): teste com
fala real de mais de 6s, instrumentado via Playwright capturando timestamp exato de cada frame do
WebSocket (`framesent`/`framereceived`). Resultado: primeiro evento `delta` com texto não vazio às
2340ms; primeiro `input_audio_buffer.commit` enviado às 6960ms. Amostragem visual de
`#transcriptRapido` a cada 100-200ms confirmou que a mudança na tela bate exatamente com o
timestamp do evento `delta` de rede — sem outra fonte de texto residual.

[DECISÃO] Correção de registro histórico na Etapa 1 do PLANO.md: o entendimento anterior ("sem o
commit explícito, a API nunca dispararia a transcrição") estava incompleto. Os eventos `delta`
chegam continuamente conforme a fala é reconhecida, independente do `commit` — confirmado na
documentação oficial da Realtime API. O `commit` serve só para fechar um turno e disparar o evento
`completed` (com o `usage`/custo daquele trecho); não é ele que inicia o streaming do texto. O
intervalo de commit (agora 6s) continua controlando apenas de quanto em quanto tempo um trecho é
"fechado" oficialmente — nunca controlou quando o texto aparece na tela.

[DIRECIONAMENTO] Nenhuma mudança de comportamento necessária — a Etapa 3 já atendia ao critério de
pronto (texto contínuo sem quebra de linha; commit a cada ~6s). Próximo passo: Etapa 4 (consumo no
modo ao vivo), pendente de confirmação do usuário para gerar a PROXIMA_TAREFA.md.

---

## Consolidado (2026-08-19, sessão de encerramento) — resumo nas 4 categorias, para revisão

> Gerado no comando "consolidar", a pedido do usuário antes de encerrar esta thread e migrar para
> outra conta. Cobre toda a coleta do projeto do início (MVP) até aqui, incluindo o plano de
> transcrição em tempo real + linha do tempo de consumo (Etapas 1-3 concluídas) e a investigação
> da discrepância de commit/delta. **Substitui o resumo "Consolidado (2026-08-19)" anterior neste
> mesmo arquivo**, que ficou desatualizado (registrava a Etapa 1 do plano de tempo real como "não
> executada", quando já havia sido concluída antes mesmo daquele resumo ser gerado). Proposta para
> revisão — nada aqui é destino final separado, este resumo já é o produto da coleta.

### Decisões
- README da raiz permanece documentação do kit `agentes-base`; o projeto tem README próprio em
  `transcritor/README.md` (dois READMEs, mantém a separação kit/projeto).
- Placeholders do kit preenchidos assumindo que não há projeto de escrita/relatório separado — o
  comando "aplicar" não é usado neste projeto.
- Backend em FastAPI + Uvicorn (decidido pelo Executor, a tarefa original deixou em aberto).
- CORS aberto (`allow_origins=["*"]`) para uso 100% local — revisar se um dia for exposto fora
  da máquina (Backlog).
- Usuário autorizou, a partir de 2026-08-16, que o PM gere diretamente a tarefa de correção
  quando o Executor reportar um risco de segurança objetivo e de correção pequena, sem perguntar
  antes se vira etapa ou fica no Backlog (exceção pontual, não regra silenciosa).
- Interação da gravação rápida: clique único (clica para começar, clica de novo para parar e
  enviar), não segurar/soltar.
- Modelo `gpt-4o-transcribe-diarize` removido da interface (comentado no código, não apagado) —
  qualidade insatisfatória na avaliação do usuário.
- Seletor de 3 modelos substituído por alternador simples entre os 2 modelos restantes,
  compartilhado entre upload e gravação.
- Soma do transcript ao final (em vez de substituir) vale só para a gravação rápida; upload
  continua substituindo a cada envio.
- Corte automático de segurança na gravação normal: 2min30s (o modo tempo real não tem esse corte
  — ver Pendências).
- Painel de consumo com persistência em arquivo local (primeira persistência do projeto) — trocar
  por banco de dados de verdade fica para depois (Backlog).
- Correção da permissão de microfone repetida: servir o frontend via servidor HTTP local
  (`http://127.0.0.1:8000/`) em vez de abrir por `file://`.
- Cobrança real de `gpt-4o-transcribe`/`gpt-4o-mini-transcribe` é por token — o registro de
  consumo usa o campo `usage` de tokens da própria resposta da API; o valor "por minuto" usado no
  benchmark é uma conversão aproximada da OpenAI, não a cobrança literal desses dois modelos.
- Botão de reset do painel de consumo zera só a sessão atual (baseline em memória); o histórico
  diário salvo em disco não é apagado por ele.
- Seletor de microfone e painel de consumo ficam atrás de ícones "avançados" (popover/modal,
  classe `.icone-avancado` reaproveitada), não fixos na tela principal.
- Validação de "nenhuma fala detectada" incorporada à etapa das barras de nível (reaproveitando o
  mesmo `AnalyserNode`), em vez de virar etapa própria; aviso é um popup rápido (toast); sem
  suporte a Web Audio API, a checagem é pulada (grava sempre envia) em vez de bloquear tudo.
- Gráfico de custo por dia do painel de consumo feito só com HTML/CSS (sem Chart.js/dependência
  nova), para não depender de CDN externo.
- Erro no meio do streaming (modo lote) não pode virar HTTP 4xx/5xx (o `StreamingResponse` já
  enviou status 200) — vira uma linha `{"tipo":"erro",...}` dentro do próprio stream NDJSON.
- Efeito de streaming imperceptível em áudios curtos (~1s) é comportamento inerente da API, não
  bug — decisão de adiantamento artificial de exibição fica pendente do usuário (Backlog).
- Avaliada alternativa de transcrição em blocos com sobreposição/redundância — mesmo com
  sobreposição generosa, sai mais barata que a API ao vivo (≈ US$ 0,011/min vs US$ 0,017/min), mas
  exige lógica própria de continuidade nas bordas; decisão do usuário em 2026-08-19: priorizar a
  API ao vivo primeiro por simplicidade de integração, blocos com redundância ficam no Backlog.
- No plano de transcrição em tempo real: persistir só a transcrição (texto) de cada requisição,
  não o áudio — arquivo novo `transcricoes.jsonl`, rústico por append, ligado ao `consumo.jsonl`
  por timestamp/id compartilhado; linha do tempo no painel de consumo mostra o preço acima de cada
  ponto e abre um popup com o texto ao clicar.
- Autenticação da sessão em tempo real: **token efêmero** (não relay) — navegador abre WebSocket
  direto com a OpenAI, backend nunca repassa áudio/eventos; única superfície exposta ao navegador
  é o token de curta duração (`ek_...`).
- Captura de áudio em tempo real via `AudioContext` + `ScriptProcessorNode` (não `AudioWorklet`) —
  mantém o frontend em arquivo único, mesmo padrão do resto do projeto, apesar de depreciado.
- Modo tempo real: texto contínuo sem quebra de linha entre turnos (não reseta a cada commit); e
  intervalo de commit dobrado de 3s para 6s (exploratório, pedido do usuário "pra ver o que faz").
- Correção de registro histórico na Etapa 1 do plano de tempo real: o entendimento original de
  que "sem o commit explícito, a API nunca dispararia a transcrição" estava incompleto — os
  eventos `delta` chegam continuamente conforme a fala é reconhecida, independente do commit
  (confirmado por teste real com timestamps de WebSocket: primeiro delta em 2340ms vs. primeiro
  commit em 6960ms, e pela documentação oficial da Realtime API). O commit só fecha um turno e
  dispara o evento `completed` (com `usage`/custo) — nunca controlou quando o texto aparece na
  tela.
- Gravação em `.claude/estado/` (PLANO.md, PROXIMA_TAREFA.md, historico/) em sessões via bridge
  remoto (Cowork) usa `cat > "<arquivo>" <<'EOF' ... EOF` direto no terminal remoto, porque a
  ferramenta padrão de gravar arquivo remoto recusa qualquer caminho dentro de `.claude/` — causou
  ~10 minutos de atraso numa retomada até ser identificado. Registrado como nota técnica
  permanente em `.claude/PM.md`. Não se aplica a sessões com acesso direto ao sistema de arquivos
  (ex.: Claude Code local, ou o Executor — que roda como extensão local no editor) nem a arquivos
  fora de `.claude/` (`coleta/` continua usando a ferramenta normal de escrita remota).
- Usuário corrigiu o PM em 2026-08-18: pedir "pode fazer a próxima tarefa" não é autorização geral
  para o PM virar Executor sempre — por padrão o PM só planeja/coordena/gera `PROXIMA_TAREFA.md`.
- Ritmo de testes: validação básica durante a execução, bateria completa reservada para o final de
  cada etapa.

### Artefatos
- `transcritor/` (backend, frontend, `.env`, `requirements.txt`, `README.md`), `.gitignore`
  protegendo `.env`, `.venv/` e `__pycache__/`.
- `backend/main.py`: `POST /transcrever` (modo lote, 2 modelos ativos + streaming NDJSON opcional),
  serve o frontend como estático em `/`, registro de consumo (`_registrar_consumo`,
  `_calcular_custo_usd`, `transcritor/consumo.jsonl`, `GET /consumo`), e agora também
  `GET /tempo-real/token` (modo ao vivo, `MODELO_TEMPO_REAL = "gpt-live-transcribe"`,
  `turn_detection: None`, mesmo padrão de erro dos outros endpoints).
- `frontend/index.html`: upload + gravação rápida (clique único, transcript cumulativo/editável),
  ícone de configurações (seletor de microfone), cronômetro + corte de segurança (2min30s), barras
  de nível de áudio + validação de silêncio, ícone/painel de consumo (sessão, histórico diário,
  gráfico CSS, reset), alternador de streaming do modo lote, e agora também `#botaoTempoReal`
  (modo ao vivo: captura contínua via `ScriptProcessorNode`, `input_audio_buffer.append`/`.commit`
  a cada ~6s, texto exibido em fluxo contínuo sem quebra visual entre turnos).
- `transcritor/benchmark.py` + `BENCHMARK.md`: comparação dos 3 modelos de lote.
- `transcritor/README.md` atualizado a cada etapa relevante, incluindo a seção "Transcrição em
  tempo real" (ponte de autenticação, formato dos eventos, limitações).
- `.claude/estado/PLANO.md`: quatro planos ao todo — MVP (7/7 concluído), refinamento da captura
  de voz (2/2 concluído), robustez/consumo/streaming (7/7 concluído), e o atual, transcrição em
  tempo real + linha do tempo de consumo (Etapas 1-3 de 7 concluídas; históricos em
  `.claude/estado/historico/`, até `PLANO_2026-08-19g.md`).
- `.claude/PM.md`: recebeu a nota técnica permanente sobre gravação em `.claude/estado/` via
  bridge remoto.
- Bugs corrigidos ao longo do projeto: `gpt-4o-transcribe-diarize` exigia `chunking_strategy`
  (isolado, sem tocar outros modelos); CSS `[hidden]` sobrescrito por regra "author" (corrigido
  com `!important`).

### Direcionamentos
- Projeto vive em `transcritor/`, dentro do mesmo repositório do kit `agentes-base`.
- Ao gerar `PROXIMA_TAREFA.md` com passo de documentação, sempre incluir `transcritor/README.md`
  explicitamente em "Arquivos envolvidos".
- Upload de arquivo e gravação pelo microfone convivem como duas formas de entrada alternativas.
- PM deve, por padrão, ficar só no papel de planejar/coordenar/gerar tarefa — só executa código se
  pedido de forma explícita e pontual.
- PM confere o critério de pronto no artefato/comportamento real, não só no relato do Executor —
  foi essa disciplina que revelou a discrepância da Etapa 3 do plano de tempo real e levou à
  investigação que a esclareceu (sem bug, sem mudança de código).
- Discussão paralela, fora do escopo deste projeto/plano: usuário avaliando adotar uma plataforma
  self-hosted tipo Claude com agentes/skills (Open WebUI, LibreChat, AnythingLLM, Dify, LobeHub)
  como motor para uma fase futura — decidiu continuar essa avaliação em outro chat.
- Migração de conta discutida nesta sessão (fora do escopo do projeto em si, mas relevante para
  continuidade): não existe transferência direta entre duas contas pessoais da Claude.ai; como
  todo o estado do projeto já vive em arquivos desta pasta (`agentes-base/`, incluindo
  `.claude/estado/`, `coleta/`, e o código em `transcritor/`), mover a pasta para a máquina/conta
  nova é suficiente para retomar — nenhuma memória de chat é necessária, exatamente o propósito
  deste registro de coleta e dos arquivos de estado.
- Próximo passo do plano ativo: Etapa 4 (consumo no modo ao vivo — `_registrar_consumo`/
  `consumo.jsonl` pelo preço por minuto correto do modo tempo real), aguardando o usuário aprovar
  a geração da `PROXIMA_TAREFA.md` correspondente.

### Pendências
- `.git/index.lock` (0 bytes, achado em 2026-08-16, confirmado ainda presente em 2026-08-18) —
  depende de: usuário remover manualmente antes de qualquer `git add`/commit.
- CORS aberto — revisar se o projeto um dia for servido fora da máquina local.
- Estilo visual do aviso de corte de segurança reaproveita a cor de "erro" — Executor sugeriu um
  estilo de "aviso" dedicado; decisão pendente do usuário/PM.
- Efeito de streaming imperceptível em áudios curtos (modo lote) — decisão pendente do usuário
  sobre um adiantamento artificial de exibição (Backlog).
- Transcrição em blocos com redundância — Backlog, para testar depois da API ao vivo.
- Exploração de plataforma self-hosted tipo Claude segue em aberto, para continuar em outro chat.
- Rotação/limpeza automática de transcrições antigas em `transcricoes.jsonl` — sem política de
  retenção definida (Backlog, e o arquivo ainda nem existe — é a Etapa 5 do plano atual).
- Trocar os arquivos locais (`consumo.jsonl`, `transcricoes.jsonl`) por um banco de dados de
  verdade — decisão de adiar (Backlog).
- Sem corte de segurança por tempo nem detecção de silêncio no modo tempo real (diferente da
  gravação normal) — Backlog do plano atual, relevante combinado com o custo por minuto mais alto
  da Etapa 4.
- Plano atual (transcrição em tempo real + linha do tempo de consumo): Etapas 1-3 concluídas e
  verificadas; Etapas 4 (consumo), 5 (persistência da transcrição), 6 (linha do tempo) e 7 (testes
  finais/documentação) aguardando — nenhuma `PROXIMA_TAREFA.md` ativa no momento deste
  consolidado (aguardando aprovação do usuário para seguir).

## [2026-08-19] Retomada em chat novo — abertura da Etapa 4

- [DIRECIONAMENTO] Usuário aprovou seguir para a **Etapa 4 (consumo no modo ao vivo)** como está
  no plano, mantendo os freios de segurança do modo tempo real (corte por tempo e detecção de
  silêncio) no Backlog, sem subir para Etapa. Trade-off aceito conscientemente: enquanto a Etapa 4
  não fecha o ciclo, uma sessão ao vivo esquecida ligada continua consumindo API a ~US$0,017/min
  sem freio automático — a Etapa 4 pelo menos torna esse gasto visível no painel de consumo.
- [DECISÃO] Registrar o consumo do modo ao vivo exige uma **rota nova no backend**
  (`POST /consumo/tempo-real`), não só adaptar `_registrar_consumo`. Motivo: a decisão de Etapa 1
  (token efêmero, navegador↔OpenAI direto, sem relay) faz o `usage` do evento
  `...input_audio_transcription.completed` chegar **no navegador**; o backend nunca vê o áudio nem
  o usage dessa sessão. Trade-off: o frontend passa a ser a fonte do dado de consumo do modo ao
  vivo (um cliente adulterado ou offline registra errado ou não registra) — aceitável para um app
  100% local, e o preço de manter a latência baixa do caminho direto.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 4 gerada, incluindo conferência do preço por minuto na
  página oficial (não presumir os US$0,017/min anotados em 2026-08-19), envio acessório do usage
  pelo frontend (falha não pode travar a sessão), regressão do painel de consumo e atualização do
  `transcritor/README.md`.
- [PENDÊNCIA] Estado do git conferido nesta retomada: **nenhum commit desde o início do produto** —
  `transcritor/`, `coleta/`, `PROGRESSO.md` e `historico/` estão como não rastreados; PLANO.md,
  PROXIMA_TAREFA.md, CLAUDE.md, PM.md, SKILL.md e .gitignore com modificações não commitadas.
  Decisão explícita do usuário em 2026-08-19: **deixar como está**, sem gerar tarefa de commit e
  sem abrir exceção à regra de o EXEC nunca commitar.

## [2026-08-19] Ajuste de método — profundidade do registro e arquivamento

- [DECISÃO] Criada a **regra de profundidade do registro** no `PROGRESSO.md`, em três níveis
  (`recibo` / `curto` / `completo`), declarados pelo PM na `PROXIMA_TAREFA.md` (campo novo
  `## Registro no PROGRESSO`), com `curto` como padrão quando o campo faltar. Motivo, medido:
  o arquivo estava com 134 KB, entrada média de ~6,4 KB (~90 linhas), a maior com 183 linhas, e
  **zero blocos de código colados** — ou seja, o inchaço é prosa narrativa do passo a passo, que
  o PM reverifica no artefato real de qualquer jeito (regra própria do `PM.md`). Trade-off aceito:
  perde-se o relato detalhado do "como fiz", ganha-se um canal PM↔EXEC legível e uma retomada
  barata. O que **não** encolhe, por decisão explícita: como testou (com o dado real que prova),
  o que não foi testado, os riscos e o ajuste de plano — é a parte que só o Executor sabe e que
  se perde se não for escrita.
- [DIRECIONAMENTO] O Executor **pode subir** o nível por conta própria (justificando em uma
  linha) se achar bug fora do escopo ou risco relevante; nunca descer. Mantém-se a fronteira que
  já existia e provou valor: o EXEC **reporta e recomenda, não decide** — os freios de segurança
  do modo tempo real e a correção da nota histórica da Etapa 1 saíram de recomendações dele.
- [DECISÃO] **Arquivamento do `PROGRESSO.md` passa a ter a virada de plano como gatilho, não o
  tamanho.** Medição que motivou: dos 134 KB, ~100 KB são de três planos já encerrados e só
  ~34 KB são do plano vivo. O limite de 40 KB era pequeno demais para as entradas de hoje —
  dispararia no meio de um plano aberto, o pior momento para arquivar. Subiu para **60 KB e
  virou alarme** (sinal de plano se arrastando ou regra de profundidade não seguida), não gatilho.
- [DECISÃO] **Exceção datada de 2026-08-19 ao `PM.md`**: o PM pode mover entradas de planos
  encerrados do `PROGRESSO.md` para `historico/`. Escopo estrito — mover entradas inteiras,
  preservadas palavra por palavra, só de planos fechados, só entre planos. Nunca editar, resumir
  ou reordenar; nunca tocar em entrada de plano vivo. Trade-off: fura a regra de que o PROGRESSO
  é arquivo exclusivo do executor, mas a alternativa (gerar tarefa de EXEC só para recortar e
  colar) queimava um chat inteiro de execução em higiene.
- [ARTEFATO] `.claude/PM.md` e `.claude/EXECUTOR.md` reescritos com as regras acima.
- [DIRECIONAMENTO] Discussão conceitual (2026-08-19) sobre esboçar etapas futuras: decidido que o
  `PLANO.md` (objetivo + critério de pronto) é o nível certo de esboço, e a `PROXIMA_TAREFA.md`
  só faz sentido logo antes de executar, porque é o que mais envelhece. Falta um **nível
  intermediário**: nota de desenho por etapa, com riscos e acoplamentos já antecipáveis. Exemplo
  concreto que motivou: o texto transcrito do modo ao vivo mora no navegador, então a Etapa 5
  (`transcricoes.jsonl`) tem o mesmo acoplamento da Etapa 4 e talvez devesse influenciar o
  desenho da rota que está sendo feita agora. Ainda não escrito.
- [PENDÊNCIA] Arquivamento retroativo dos ~100 KB de planos encerrados no `PROGRESSO.md` — fazer
  na próxima virada de plano (o plano de tempo real ainda está aberto, com as Etapas 4 a 7).
- [PENDÊNCIA] Tarefa da Etapa 4 já estava em execução quando a regra nasceu, sem o campo
  `## Registro no PROGRESSO` — cai no padrão `curto` por default. Decidido não alterar a tarefa no
  meio da execução.

## [2026-08-19] Etapa 4 concluída — consumo no modo ao vivo

- [ARTEFATO] `POST /consumo/tempo-real` no backend (`transcritor/backend/main.py`), com a classe
  Pydantic `UsageTempoReal` validando `type == "duration"` e `seconds >= 0` **antes** de chegar em
  `_registrar_consumo` — não há caminho para gravar lixo em `consumo.jsonl` a partir dessa rota.
  `gpt-live-transcribe` entrou em `PRECO_POR_MINUTO_USD` a US$ 0,017/min, com fonte e data da
  consulta em comentário. No frontend, `reportarConsumoTempoReal` dispara a cada evento
  `...input_audio_transcription.completed`. `transcritor/README.md` documenta o fluxo.
- [DECISÃO] O envio do consumo pelo frontend é **acessório por construção, não só por boa
  prática**: o `fetch` não é aguardado e a falha é engolida em `.catch()` vazio. Trade-off aceito:
  um turno pode não ser contabilizado (backend fora do ar, aba fechada antes do envio) e o número
  do painel fica subestimado, em troca de a sessão de transcrição nunca depender do backend para
  continuar. Validado derrubando o backend no meio de uma gravação real: o texto continuou
  chegando, o encerramento funcionou e não houve nenhum `pageerror`.
- [ARTEFATO] Verificação independente do PM: os cinco registros de `gpt-live-transcribe` em
  `consumo.jsonl` foram reconferidos com a conta `segundos / 60 * 0,017` (12,5s / 7,0s / 6,0s x3)
  — batem na última casa decimal. Painel de consumo agrega por dia, sem distinguir modelo, então
  os registros novos entram sem mudança no JS de renderização.
- [DIRECIONAMENTO] Registrado no `PLANO.md`, junto da Etapa 4, o desenho que vale para as etapas
  seguintes: o registro parte do navegador porque a decisão da Etapa 1 (token efêmero, sem relay)
  faz o `usage` chegar só lá. **A Etapa 5 tem o mesmo acoplamento para o texto transcrito** — o
  texto do modo ao vivo também só existe no navegador.
- [PENDÊNCIA] Havia um backend antigo esquecido ligado na porta 8000 no início da tarefa, servindo
  código sem a rota nova (devolvia 405); o Executor encerrou o processo e subiu o atualizado.
  Armadilha recorrente do projeto, agora com uma ocorrência a mais.
- [PENDÊNCIA] `consumo.jsonl` mistura consumo de uso real com o de sessões de teste do Executor —
  os cinco registros de tempo real são todos de teste. Sem separação prevista até agora.

- [DECISÃO] Desenho da Etapa 5 fechado **antes** de executar (primeiro uso da "nota de desenho",
  o nível intermediário discutido hoje): o texto do modo ao vivo chega ao backend **estendendo a
  rota `POST /consumo/tempo-real`** — texto + `usage` no mesmo POST, backend gravando
  `consumo.jsonl` e `transcricoes.jsonl` na mesma chamada com id compartilhado. Alternativa
  descartada: rota `POST /transcricoes` separada. Trade-off aceito: a rota fica com nome infiel ao
  que faz (talvez renomear) e mexe-se em código recém-validado, em troca de uma chamada por turno
  e do vínculo entre os arquivos sair de graça, sem lógica de correlação. Registrado no `PLANO.md`
  junto da Etapa 5.
- [DIRECIONAMENTO] Usuário optou por **não gerar a `PROXIMA_TAREFA.md` da Etapa 5 agora** —
  execução retomada quando ele decidir. Nenhuma tarefa ativa no momento.

## [2026-08-19] Tarefa da Etapa 5 gerada

- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 5 (persistência da transcrição) gerada, com
  `## Registro no PROGRESSO: curto` — **primeira tarefa a usar o campo de profundidade** criado
  hoje. Desenho conforme a decisão já registrada: id compartilhado gerado por `_registrar_consumo`
  (que passa a devolvê-lo, e devolve `None` quando falha, para não criar linha órfã),
  `_registrar_transcricao` nova, gravação nos dois pontos do modo em lote (fluxo sem streaming em
  `resultado.text` e evento `transcript.text.done` em `evento.text`) e campo de texto **opcional**
  acrescentado ao corpo de `POST /consumo/tempo-real`.
- [DECISÃO] O campo de texto na rota é opcional e o corpo antigo (só `type` + `seconds`) continua
  válido — critério de pronto explícito. Motivo: não quebrar o contrato que acabou de ser validado
  na Etapa 4, e permitir que a rota siga registrando consumo mesmo se o texto não vier.
- [DECISÃO] No modo ao vivo, o frontend manda o texto **do turno** (o `transcript` do evento
  `.completed`), não o transcript acumulado da tela — senão cada linha de `transcricoes.jsonl`
  repetiria tudo o que veio antes.
- [PENDÊNCIA → Backlog] Renomear `POST /consumo/tempo-real`: a partir da Etapa 5 ela grava em dois
  arquivos e o nome deixa de descrever o que faz. Adiado de propósito para não mexer em código
  recém-validado; item acrescentado ao Backlog do `PLANO.md`.

## [2026-08-19] Etapa 5 concluída — persistência da transcrição

- [ARTEFATO] `transcricoes.jsonl` (append, uma linha por requisição: `id_consumo`, `timestamp`,
  `modelo`, `texto`), ligado a `consumo.jsonl` por um `id` `uuid4` que `_registrar_consumo` passou
  a gerar e devolver. Cobre os três caminhos: lote sem streaming, evento `transcript.text.done` do
  streaming, e `POST /consumo/tempo-real` (campo `texto` opcional, contrato antigo preservado).
  `.gitignore` e README atualizados.
- [DECISÃO] Guarda contra linha órfã: `_registrar_consumo` devolve `None` quando falha, e a
  transcrição só é gravada se veio um id válido. Trade-off: numa falha de consumo perde-se também
  o texto daquela requisição, em troca de `transcricoes.jsonl` nunca ter linha sem par.
- [ARTEFATO] Verificação independente do PM sobre os arquivos reais: 16 linhas em
  `transcricoes.jsonl`, **zero órfãs** (todo `id_consumo` existe em `consumo.jsonl`) e zero linhas
  de texto vazio.
- [DIRECIONAMENTO] **A regra de profundidade estreou e funcionou como desenhada**: a tarefa pedia
  nível `curto`, o Executor subiu o nível na seção de testes e **justificou no topo da entrada** —
  o critério de pronto exigia texto salvo x exibido lado a lado nos dois modos, o que não cabia no
  teto de ~15 linhas sem cortar o dado que prova. É exatamente a cláusula de subir justificando.
  Aprendizado para o PM: critério de pronto que pede evidência colada conflita com nível `curto`;
  nesses casos, declarar `completo` já na tarefa.
- [PENDÊNCIA] Apareceu de novo um `uvicorn` órfão de sessão anterior na porta 8000 (PID 19128),
  servindo código sem as mudanças — terceira ocorrência registrada da mesma armadilha.

## [2026-08-19] Defeitos do modo tempo real reportados pelo usuário

- [DIRECIONAMENTO] O usuário usou o modo tempo real de verdade e trouxe **a transcrição como
  evidência** — primeiro retorno de uso real, não de teste. Três defeitos distintos, separados
  pelo PM a partir do código:
  1. **Palavras coladas entre turnos** — `textoFinalizadoTempoReal += dado.transcript` sem
     separador; a Etapa 3 tirou a quebra de linha e não pôs nada no lugar.
  2. **Fim da gravação perdido** — `pararGravacaoTempoReal` fecha o socket na linha seguinte ao
     commit final, sem esperar o `completed`; perde texto, `usage` e linha de transcrição do
     último turno.
  3. **Bordas de turno mal cortadas** — o commit de 6s corta em intervalo fixo, sem olhar
     silêncio, e a palavra partida vira duas ("aparece" / "Parece").
- [DECISÃO] Só os defeitos 1 e 2 sobem para correção, **antes da Etapa 6**. O 3 fica no Backlog:
  não é conserto pontual, é mudança de desenho da sessão ao vivo (commit guiado por silêncio ou
  `turn_detection` da API) e merece decisão própria.
- [DECISÃO] A correção entra como seção **"Correção aprovada"** no `PLANO.md`, **sem consumir
  etapa** — o plano já usa as 7 que o papel PM permite, e ambos são defeitos de entregas das
  Etapas 2 e 3, não escopo novo. Mesmo tratamento dado à investigação de deltas vs. commit.
- [ARTEFATO] `PROXIMA_TAREFA.md` da correção gerada, com nível **`completo`** declarado de
  propósito — aplicação direta do aprendizado da Etapa 5: critério de pronto que exige evidência
  colada é incompatível com o nível `curto`.
- [PENDÊNCIA] O defeito 2 significa que **todo registro de consumo e de transcrição do último
  turno de cada gravação ao vivo foi perdido até agora** — os números de `consumo.jsonl` para
  `gpt-live-transcribe` estão subestimados.

## [2026-08-19] Correção aprovada concluída — fim perdido e palavras coladas

- [ARTEFATO] `transcritor/frontend/index.html`: `concatenarTurnoTempoReal(base, novoTrecho)` insere
  espaço na emenda só quando nenhum dos dois lados já tem, e não põe espaço antes do primeiro
  turno; `pararGravacaoTempoReal` deixou de fechar o socket direto — agora aguarda o `completed`
  do último turno e só então chama `finalizarFechamentoTempoReal`, com
  `TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS = 5000` como rede de segurança e status
  "Encerrando… aguardando a transcrição do último trecho." enquanto espera.
- [DECISÃO] A espera é controlada por um **contador de commits pendentes**
  (`commitsPendentesTempoReal`), não por "aguardar o próximo `completed`" — cobre o caso de o
  commit periódico e o final estarem em voo ao mesmo tempo. Verificado pelo PM que o contador é
  incrementado nos **dois** pontos de commit (timer periódico e final): sem isso a lógica seria
  falsa, e o relato sozinho não provaria.
- [ARTEFATO] Verificação independente do PM: `transcricoes.jsonl` em 24 linhas, **zero órfãs**. O
  Executor testou com fala real de 4 frases (último trecho na tela e gravado nos dois arquivos com
  o mesmo id), forçou o timeout engolindo o `completed` (recuperou em 5029ms, interface não travou
  em "gravando") e conferiu a regressão do modo desligado.
- [PENDÊNCIA → Backlog] Resíduo estreito achado pelo PM na verificação: se o clique em parar cair
  dentro de ~100ms de um commit periódico, `podeComitarFinal` é falso e o fechamento é imediato —
  um `completed` em voo daquele commit ainda se perde. Mesma classe do defeito corrigido, janela
  muito menor. Correção provável: entrar na espera sempre que houver commit pendente, mesmo sem
  commit final.
- [DIRECIONAMENTO] Com isso, Etapas 1 a 5 + correção estão fechadas. Restam a Etapa 6 (linha do
  tempo) e a Etapa 7 (testes finais e documentação).

## [2026-08-19] Tarefa da Etapa 6 gerada — linha do tempo

- [DECISÃO] Para a linha do tempo, `GET /consumo` ganha uma chave **`requisicoes`** (aditiva,
  `sessao` e `por_dia` intocados), com um item por linha de `consumo.jsonl` e o `texto` casado por
  id contra `transcricoes.jsonl`. Mesmo princípio de estender rota existente adotado na Etapa 5.
  Motivo: hoje a rota só devolve agregados por dia e nenhuma rota lê `transcricoes.jsonl` — sem
  dado por requisição não existe ponto para desenhar.
- [DECISÃO] Registros anteriores à Etapa 5 **não têm `id`** e entram na lista com `texto: null`,
  continuando visíveis na linha do tempo. Trade-off: pontos "mudos" no gráfico, em troca de não
  esconder consumo já pago só porque é antigo.
- [DIRECIONAMENTO] Restrição do produto reafirmada na tarefa: frontend é HTML de arquivo único, sem
  build e sem dependências — visualização em SVG à mão, **sem biblioteca de gráfico, nem via CDN**.
  A tarefa exige ler a skill `dataviz` antes da primeira linha de código de gráfico e relatar o que
  foi aplicado.
- [DIRECIONAMENTO] Critério de pronto amarrado ao **objetivo declarado do plano**, não à mecânica:
  mandar o mesmo áudio para dois modelos em sequência e mostrar que dá para ler e comparar o preço
  dos dois pontos. Sem isso, a etapa poderia "passar" com um gráfico bonito que não serve para a
  pergunta que motivou o plano.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 6 gerada, nível **`completo`**.

## [2026-08-19] Etapa 6 concluída — linha do tempo no painel de consumo

- [ARTEFATO] `GET /consumo` ganhou a chave `requisicoes` (aditiva, construída no mesmo loop que já
  agregava `por_dia`), com `textos_por_id` lido de `transcricoes.jsonl` e `texto: None` para
  registro sem `id`. Frontend: `renderizarLinhaTempoConsumo` desenhando SVG à mão, botão de zoom
  hora/minuto (`PX_POR_SEGUNDO_ESCALA_MINUTO = 10`), modal `#fundoPopupRequisicao` com o texto da
  requisição. Nenhuma dependência nova, como exigido.
- [ARTEFATO] Verificação independente do PM: reproduzi o join sobre os arquivos reais — 77
  requisições, 49 antigas sem `id` (texto nulo), 27 com texto, e **as 27 transcrições existentes
  casadas, nenhuma sobrando**.
- [ARTEFATO] **O objetivo do plano foi demonstrado**: mesmo áudio em dois modelos, US$ 0,0006575
  (`gpt-4o-transcribe`) contra US$ 0,00033375 (`gpt-4o-mini-transcribe`) — o mini custou ~metade,
  com os dois pontos a 15,14px de distância na escala minuto e os preços legíveis.
- [DECISÃO] O Executor leu a skill `dataviz` antes de codar e **divergiu conscientemente** de uma
  diretriz dela: a skill desaconselha número em todo ponto, o critério do plano exigia preço acima
  de cada ponto. Ele seguiu o produto e registrou a divergência em vez de escondê-la. Trade-off que
  cobrou seu preço — ver a pendência abaixo.
- [PENDÊNCIA → Backlog] **Rótulos colados na escala "hora"**: com ~77 requisições em 2 dias,
  "cabe o dia inteiro" e "preço em cada ponto" se contradizem e os rótulos se sobrepõem. O volume
  vem de teste de desenvolvimento, não de uso real. Alternativas anotadas: rotular seletivamente
  na escala hora, ou recortar o período.
- [PENDÊNCIA] Gravação por microfone (normal e tempo real) não foi retestada na Etapa 6 — o
  Executor não tocou nesse código e registrou o risco como baixo. Entra na Etapa 7.
- [ARTEFATO] Dois bugs de layout achados e corrigidos pelo próprio Executor durante o
  desenvolvimento: item de grid não encolhendo (`min-width: 0`) com o SVG de ~980.000px da escala
  minuto, e auto-scroll caindo na folga de 8% do eixo em vez do último ponto real.

## [2026-08-19] Etapa 7 gerada — ajustes da linha do tempo + fechamento do plano

- [DECISÃO] Depois de ver a Etapa 6 funcionando, o usuário pediu dois ajustes: **preço só na escala
  "minuto"** (some na escala "hora") e **roda do mouse alternando o zoom**, além do botão. O
  primeiro resolve a colisão de rótulos levantada na Etapa 6 e realinha com a diretriz da skill
  `dataviz` — o item correspondente saiu do Backlog.
- [DECISÃO] Os dois ajustes foram **dobrados dentro da Etapa 7**, em vez de virarem correção
  separada como foi feito com os defeitos do modo tempo real. Motivo: são pequenos e localizados na
  função de render da linha do tempo, e a rodada de testes finais da própria Etapa 7 passa a
  cobri-los. Trade-off: a etapa deixa de ser só validação e mistura mudança de código, em troca de
  economizar um chat EXEC inteiro e mais uma exposição à armadilha recorrente do backend obsoleto.
- [DIRECIONAMENTO] Conflito de desenho travado na tarefa em vez de deixado implícito: na escala
  "minuto" o container **rola horizontalmente com a roda**, que é exatamente o gesto que passará a
  alternar o zoom. A tarefa exige que o Executor escolha um desenho que preserve a navegação
  horizontal e **justifique a escolha no PROGRESSO** — não deixar a linha do tempo sem meio de
  rolar.
- [DECISÃO] Exceção pontual e datada: o Executor está autorizado a editar **apenas a seção Backlog**
  do `PLANO.md` nesta etapa, porque atualizar o Backlog é critério de pronto dela. Exceção limitada
  a esta tarefa, registrada aqui conforme manda o `PM.md`.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 7 gerada, nível `completo` — o registro dela será a base
  do arquivamento do `PROGRESSO.md` (já em 171 KB) na virada de plano.

## [2026-08-19] Etapa 7 concluída + correção do eixo do tempo

- [ARTEFATO] Etapa 7 entregue e verificada: preço só na escala "minuto" (0 de 81 rótulos na escala
  hora, 81 de 81 na de minuto, medido no DOM), roda alternando o zoom, Shift+roda preservando a
  navegação horizontal (`scrollLeft` 0→300), rodada final com fala real cobrindo upload com e sem
  streaming, gravação por microfone e tempo real com 6 turnos (ids conferidos nos dois arquivos).
- [DECISÃO] O Executor mapeou o zoom pelo **sinal do `deltaY`** em vez de alternar a cada evento
  `wheel` — trackpad dispara dezenas de eventos por gesto e alternar por contagem faria a escala
  piscar. Solução idempotente: repetir o mesmo sentido não faz nada depois da primeira troca.
- [PENDÊNCIA → Backlog] 404 de `favicon.ico` no console — pré-existente, cosmético, sem efeito em
  nenhum fluxo.
- [DIRECIONAMENTO] **Defeito reportado pelo usuário usando o painel**: na escala "minuto" o eixo
  parece marcar "minutos desde o primeiro registro". Diagnóstico do PM, três defeitos encadeados:
  rótulo `MM:SS` **sem a hora** (18:02:10 vira "02:10", e a sequência lê como cronômetro); **passo
  fixo de 10s** independente do intervalo (24,2h de histórico = **8.696 marcas** num SVG de
  ~870.000px, para 88 pontos); e **sem indicação de virada de dia**, com o histórico cruzando a
  meia-noite e "21h" aparecendo duas vezes.
- [DECISÃO] Registrado explicitamente no `PLANO.md` que isso é **falha de especificação do PM**,
  não do Executor: nenhum critério de pronto das Etapas 6 e 7 mencionava os rótulos do eixo — as
  etapas cobriam ponto, preço, zoom e popup. Aprendizado: critério de visualização que descreve só
  as marcas de dado deixa o eixo sem dono.
- [DECISÃO] Correção entra como segunda seção "Correção aprovada", **sem consumir etapa** (o plano
  já usa as 7). Etapa 7 fica marcada como concluída **com ressalva registrada**: a rodada final de
  testes rodou antes desta correção, então a tarefa da correção inclui reconferência do painel.

## [2026-08-20] Correção do eixo concluída — plano encerrado

- [ARTEFATO] Eixo do tempo corrigido: `escolherPassoEixo` com escada de passos redondos e alvo de
  espaçamento, marcas alinhadas a fronteiras de tempo **local** (`setSeconds/Minutes/Hours/Date`,
  não múltiplo de epoch), rótulo com precisão dependente do passo e prefixo `dd/mm` só na primeira
  marca de cada dia. Escala "hora" caiu de 35 para 6 marcas no histórico real, com as duas viradas
  de meia-noite marcadas; zero sobreposição medida por `getBBox`.
- [DECISÃO] **Erro de premissa do PM, corrigido pelo Executor com medição.** O critério de pronto
  pedia a contagem da escala "minuto" cair de ~8.700, presumindo régua densa demais. Como
  `largura = duração × PX_POR_SEGUNDO_ESCALA_MINUTO`, o `pxPorMs` é constante (~0,01 px/ms) para
  qualquer duração — o espaçamento por rótulo já era exatamente 100px, acima do alvo de 80px. A
  régua nunca foi densa: é **numerosa**, porque a largura total cresce com o histórico. O Executor
  mediu em vez de forçar o número pedido, e reportou a divergência. Aprendizado para o PM: critério
  numérico derivado de inferência (contagem → densidade) precisa ser checado antes de virar
  critério de pronto.
- [PENDÊNCIA → Backlog] Estratégia de largura da escala "minuto": o SVG cresce sem limite com o
  histórico (1,27 milhão de px, ~12,7 mil marcas para 30,5h). Vira régua impraticável com uso real
  prolongado. Alternativa a avaliar: janela em torno de um ponto escolhido, em vez do histórico
  inteiro.
- [DIRECIONAMENTO] **Regra de idioma escrita** no `CLAUDE.md` e no `EXECUTOR.md` em 2026-08-20:
  todo o trabalho do repositório é em português do Brasil — conversa dos dois papéis, arquivos de
  estado, coleta, README e comentários de código. Motivo: o Executor respondeu em inglês num chat
  de execução, e nenhum dos arquivos de papel dizia o idioma.
- [PENDÊNCIA → Backlog] Botão de copiar o texto da caixa de transcrição da gravação — ideia do
  usuário em 2026-08-20, candidata ao próximo plano.
- [DIRECIONAMENTO] **Plano encerrado**: Etapas 1 a 7 + duas correções aprovadas, todas verificadas
  no artefato real. Próximo passo é a virada de plano — arquivamento do `PROGRESSO.md` (~180 KB,
  incluindo o retroativo de três planos anteriores) e montagem do plano novo a partir do Backlog.

## [2026-08-20] Virada de plano — arquivamento e plano novo

- [ARTEFATO] **Primeira aplicação da regra de arquivamento** criada em 2026-08-19. `PROGRESSO.md`
  foi de **187 KB para 304 bytes**; as 2.565 linhas do corpo foram movidas para três arquivos em
  `historico/`, separados por plano (`PROGRESSO_mvp-e-gravacao_*` 41 KB,
  `PROGRESSO_robustez-consumo-streaming_*` 59 KB, `PROGRESSO_tempo-real-e-linha-do-tempo_*` 88 KB).
  Integridade conferida programaticamente: o conteúdo rejuntado é idêntico ao original, nenhuma
  linha editada, resumida ou reordenada — como a exceção datada exige.
- [DECISÃO] **Plano novo com 4 etapas**, não 6 — o usuário pediu para agrupar o que fosse simples de
  fazer junto, para economizar tempo e token. Dois agrupamentos, ambos com critério explícito:
  (a) freios de custo + resíduo do fechamento + teste dirigido de dois commits viraram uma etapa só,
  porque vivem na mesma região de `frontend/index.html` e **compartilham o aparato de teste** (uma
  sessão ao vivo com fala real exercita os três); (b) botão de copiar + renomear rota + favicon
  viraram a etapa de miudezas, por serem mecânicas e sem decisão de desenho. Trade-off registrado:
  tarefa agrupada tem entrada maior e diagnóstico mais difícil se falhar — mitigado na etapa (b)
  exigindo execução na ordem e relato separado por item, para um bloqueio não segurar os outros.
- [DECISÃO] O plano usa **4 das 7 etapas permitidas, com folga proposital** — o plano anterior
  precisou de duas correções fora da numeração, e deixar espaço evita ter que tratar defeito como
  "correção que não consome etapa" por falta de vaga.
- [DIRECIONAMENTO] **Bordas de turno viraram alternador, não escolha.** O usuário pediu um botão
  para alternar entre o controle de turno próprio (commit a cada 6s, `turn_detection: null`) e o
  da própria API, para poder comparar com a mesma fala. Registrado no plano que o objetivo é
  comparar, não eleger — a decisão de qual vira padrão foi para o Backlog, para ser tomada com dado
  na mão. Acoplamento anotado: no modo da API não existe commit explícito, então a lógica de
  fechamento mexida na Etapa 1 precisa servir aos dois caminhos — por isso a Etapa 1 vem antes.
- [DIRECIONAMENTO] Janela da linha do tempo definida pelo usuário: escala "minuto" mostrando as
  **últimas 24 horas** com mais zoom, em vez do histórico inteiro — resolve o crescimento sem
  limite da largura do SVG. Escala "hora" continua mostrando tudo, e nada some dos agregados.
- [ARTEFATO] `PLANO.md` reescrito; versão anterior arquivada em
  `historico/PLANO_2026-08-20b_tempo-real-encerrado.md`. Notas de processo do plano novo já
  incorporam as lições de ontem: declarar sempre o nível de registro, `completo` quando o critério
  pede evidência colada, e conferir critério numérico derivado de inferência antes de gravá-lo.

## [2026-08-20] Tarefa da Etapa 1 gerada — freios de custo e fechamento

- [DECISÃO] Corte de segurança do modo tempo real fixado em **150s (2min30s)**, o mesmo da gravação
  normal — escolha do usuário entre as opções apresentadas (10min ≈ US$ 0,17 de exposição por
  esquecimento; 30min ≈ US$ 0,51; 150s ≈ US$ 0,04). Trade-off aceito conscientemente: pode
  interromper um uso legítimo longo, em troca de consistência com o resto do app e da menor
  exposição a gravação esquecida. Se incomodar no uso real, revisitar.
- [DIRECIONAMENTO] **Nota de desenho travada na tarefa**: o gate de silêncio da gravação normal
  avalia o pico **uma vez, no fim**, e decide "envio ou não envio o arquivo". No modo ao vivo isso
  não serve — o áudio já foi transmitido e o gasto já aconteceu. A verificação precisa ser contínua.
  O Executor escolhe o mecanismo (não fazer `append` do trecho mudo, ou não fechar `commit` sobre
  ele), mas tem de justificar qual de fato reduz o valor cobrado, já que o `usage` vem por duração
  de áudio — e dizer como evitou cortar frase no meio por causa de pausa curta, que pioraria as
  emendas, problema já conhecido.
- [DIRECIONAMENTO] Critério de pronto do silêncio exige **medição comparada**: custo real da sessão
  muda contra o que teria sido cobrado sem o freio (30s × US$ 0,017/60). Sem isso o critério
  passaria com "não vi cobrança", que não prova nada.
- [DIRECIONAMENTO] Trava explícita: se o gate de silêncio exigir mexer no intervalo de commit de 6s,
  o Executor deve **parar e reportar**, não decidir sozinho — o intervalo interage com a Etapa 2
  (alternador de controle de turno) e é decisão de desenho, não detalhe de implementação.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 1 gerada, nível `completo`, com lembrete da armadilha do
  backend obsoleto (4 ocorrências).

## [2026-08-20] Etapa 1 parcial — freios de custo entregues, validação com navegador pendente

- [ARTEFATO] Corte de segurança de 150s no modo tempo real (`cortarPorSegurancaTempoReal` chamando
  `pararGravacaoTempoReal()`, o mesmo caminho da parada manual); gate de silêncio contínuo no
  `onaudioprocess` com hangover de 2000ms; condição de espera do fechamento trocada para
  `if (commitsPendentesTempoReal > 0)`, fechando o resíduo de ~100ms.
- [DECISÃO] **Gate implementado como "não enviar" (`append`), não "enviar e não comitar"** — e a
  justificativa é o achado técnico da tarefa: com `turn_detection: null`, o áudio appendado e não
  comitado **não desaparece**; fica no buffer do servidor e é absorvido pelo próximo commit, que
  passa a cobrir silêncio + fala e é cobrado pela duração total. "Não comitar" só adiaria e
  esconderia o gasto dentro de um turno legítimo. Medido: 30s de silêncio → 0 bytes enviados → 0
  linhas em `consumo.jsonl` (contra US$ 0,0085 que teriam sido cobrados).
- [DECISÃO] Hangover de 2000ms para o gate não cortar pausa curta no meio de uma frase — pausas de
  até ~2s não interrompem o envio. Trade-off: pausas mais longas que isso cortam, o que é o
  comportamento desejado, mas significa que o parâmetro é o que separa "economia" de "fala picada".
- [PENDÊNCIA] **O ambiente do chat EXEC desta vez não tinha navegador nem microfone** — os
  anteriores tinham (Playwright + Edge + microfone falso na máquina Windows). O Executor contornou
  com um harness em Python que reimplementa o protocolo contra a API real, o que prova o
  comportamento no servidor mas **não** o JavaScript no navegador nem a qualidade com fala humana.
  Ficaram sem validação: texto aparecendo na tela, fala real com pausas, regressão da gravação
  normal, console limpo. Etapa marcada como **parcial** no `PLANO.md`, não concluída.
- [DIRECIONAMENTO] Risco a observar no teste manual, levantado pelo PM na verificação: o bloco de
  ~100ms anterior ao início da fala não é enviado (o hangover só sobe quando o pico passa do
  limiar), então **a primeira palavra pode perder o ataque**. Conferir ouvindo/lendo o começo da
  transcrição.

## [2026-08-20] Etapa 1 concluída pela validação manual + tarefa da Etapa 2

- [ARTEFATO] Etapa 1 fechada. O usuário rodou o roteiro manual e o PM conferiu **nos arquivos**, não
  só no relato: sessão de 150s de parede com **139s de áudio cobrado** (corte no tempo certo, gate
  poupando ~11s de silêncio ≈ US$ 0,0031); **último turno da sessão cortada com texto completo**,
  provando que o corte passa pelo caminho de fechamento com espera; turnos de 4s e 5s dentro de
  janelas de 6s, que é o gate operando; e registros de `gpt-4o-transcribe` logo depois, da
  regressão de gravação normal e upload.
- [DIRECIONAMENTO] **O risco levantado pelo PM não se confirmou**: a primeira palavra não perde o
  ataque ("Isso e um teste da transcricao em tempo real." íntegro em todos os turnos iniciais) — o
  bloco que dispara o hangover é ele próprio enviado. Registrado porque a hipótese estava escrita e
  seria injusto deixá-la no ar.
- [DIRECIONAMENTO] O cenário de silêncio **não deixa rastro por construção** — o acerto é a ausência
  de registro. Limite conhecido da verificação por artefato: nesse caso vale o relato do usuário.
- [ARTEFATO] **Evidência real do problema de bordas**, tirada da fala do usuário e agora citada na
  tarefa da Etapa 2: "Esta e a terceira **fra**" → "**Base** do teste"; "se as **pau**" →
  "**Cousas** entre as frases"; "pausa **bem**" → "**Tem maior** que as outras". A palavra é partida
  na emenda de 6s e cada metade é adivinhada em separado.
- [DIRECIONAMENTO] **Três acoplamentos travados na tarefa da Etapa 2**, achados pelo PM lendo o
  código, para não serem descobertos tarde: (a) o timer de commit periódico não pode continuar
  rodando no modo da API, sob risco de buffer vazio ou turno duplicado; (b) **o gate de silêncio da
  Etapa 1 briga com a detecção da API** — nós paramos de enviar áudio depois de ~2s de silêncio, e é
  justamente esse silêncio que o servidor usa para saber que a fala acabou, então o gate pode
  impedir a API de fechar turno; (c) o fechamento muda, porque não há commit final a aguardar e o
  usuário pode parar no meio de uma frase.
- [DECISÃO] A tarefa proíbe explicitamente **eleger um vencedor**: "turnos por tempo (6s)" continua
  sendo o padrão ao abrir a página. Qual vira padrão é decisão do usuário, depois, com a comparação
  feita — item já no Backlog.
- [DIRECIONAMENTO] Instrução nova na tarefa, aprendida na Etapa 1: se o ambiente do chat EXEC não
  tiver navegador nem microfone, fazer o possível, **marcar o que ficou sem execução e parar** — não
  buscar caminho alternativo para dar critério por atendido.

## [2026-08-20] Etapa 2 bloqueada e reescrita — detecção de turno exige troca de modelo

- [ARTEFATO] Achado do Executor, confirmado pelo PM na documentação oficial e por busca:
  **`gpt-live-transcribe` recusa qualquer `turn_detection` diferente de `null`** — HTTP 400, "Turn
  detection is not supported for this transcription model". Provado por troca de variável única: o
  mesmo payload com `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` e `whisper-1` é aceito. A doc
  oficial da Realtime API usa `turn_detection: null` justamente no exemplo desse modelo.
- [DECISÃO] **Correção de uma análise errada do PM.** Eu havia apresentado "detecção da API" e
  "detector próprio" como se a diferença de custo viesse do controle de turno. Não vem: o custo é
  definido pelo **gate de envio** (Etapa 1) e pelo **preço do modelo**. Mudar o momento do commit
  não muda o custo em nada. A economia de ~3x que aparecia na opção da API vinha de o modelo ser
  outro (US$ 0,017 → US$ 0,006/min), não da detecção.
- [DIRECIONAMENTO] **Ideia do usuário, registrada como plano B no Backlog:** os 6s viram **piso, não
  corte** — passado o piso, o turno fecha na primeira pausa detectada (meio segundo a um segundo),
  com um teto para não segurar o texto indefinidamente. Usa o detector de silêncio que a Etapa 1 já
  instalou, mantém `gpt-live-transcribe`, não muda custo, e resolve as emendas sem depender da API.
- [DECISÃO] Usuário optou por **seguir com a detecção da API**, aceitando a troca de modelo só nesse
  modo (`gpt-4o-transcribe`). Trade-off nomeado antes da decisão: os dois lados da comparação
  deixam de usar o mesmo modelo, então não dá para isolar a causa de uma eventual melhora — mas a
  escolha real do usuário é entre configurações inteiras, não entre variáveis.
- [DIRECIONAMENTO] **Risco central da etapa, escrito na tarefa**: `gpt-4o-transcribe` é modelo de
  lote. Aceita ser criado numa sessão ao vivo, mas não se sabe se entrega texto incremental durante
  a fala ou só ao fechar cada turno. Se não houver exibição incremental, o modo perde o sentido de
  "tempo real" — o Executor deve reportar com os instantes dos eventos e **parar**, sem contornar.
- [PENDÊNCIA → tarefa] Armadilha localizada pelo PM antes de virar erro silencioso:
  `POST /consumo/tempo-real` grava `MODELO_TEMPO_REAL` **fixo**. Com dois modelos em jogo, o custo
  do modo da API seria calculado a US$ 0,017 em vez de US$ 0,006 — o painel mentiria e a comparação
  desta etapa nasceria inválida.
- [DIRECIONAMENTO] Também no Backlog: perseguir a economia de ~3x **trocando só o modelo**, mantendo
  o controle de turno atual — caminho independente, caso a detecção da API não compense.

## [2026-08-20] Detecção de turno pela API encerrada sem uso — decisão do usuário

- [DECISÃO] **Não trocar o modelo do modo ao vivo para baratear.** O usuário avaliou e recusou:
  prefere preservar nuance de fala (pontuação, ênfase) a economizar, tendo recurso disponível. Com
  isso a antiga Etapa 2 (detecção de turno pela API) perde sentido, já que a detecção **só existe**
  em modelos que não são o `gpt-live-transcribe`. Etapa removida do plano, que ficou com 3 etapas.
- [ARTEFATO] Estimativa registrada no Backlog, como o usuário pediu, para o dia em que custo virar
  prioridade: o preço do modelo cai 65%, mas a detecção da API obriga a desligar o gate de silêncio
  da Etapa 1 (passa-se a pagar o tempo todo). Economia real conforme o silêncio da sessão: ~65% sem
  pausas, **~50% numa sessão típica com ~30% de silêncio**, ~29% com metade de silêncio. Em 10
  minutos com 30% de silêncio: US$ 0,119 → US$ 0,060.
- [DIRECIONAMENTO] **Contraponto medido, registrado junto no Backlog para revisão futura.** A
  premissa da recusa é que o modelo mais barato perderia nuance. O `BENCHMARK.md` deste projeto
  aponta o contrário: `gpt-4o-transcribe` **em lote** produziu pontuação e acentuação impecáveis no
  áudio de 72s ("Este é um áudio de teste para o benchmark comparativo..."), enquanto o modo ao vivo
  com `gpt-live-transcribe` produz "Isso e um teste da transcricao" sem acentos e parte palavras nas
  emendas. Indício de que a perda de nuance vem do **tamanho do pedaço enviado** (fatias de 6s), não
  do modelo — quem retomar isto deve testar a hipótese antes de decidir.
- [DECISÃO] **"Deixar mais simples"**: o alternador "Controle de turno" e o caminho `modo_turno=api`
  saem do código, dobrados na etapa de faxina em vez de virarem tarefa própria. Instrução na etapa:
  salvar o trecho removido em `historico/` **antes** de apagar, porque nada deste projeto foi
  commitado e o código só existe no arquivo vivo — sem isso, o trabalho da Etapa 2 desapareceria de
  vez.
- [PENDÊNCIA → Backlog] O commit guiado por silêncio (ideia do usuário: 6s viram piso, turno fecha
  na primeira pausa) continua sendo o caminho de menor custo para resolver as emendas mantendo o
  modelo atual — não aprovado, mas é o candidato natural se o corte de palavras voltar a incomodar.

## [2026-08-20] Tarefa da Etapa 2 (janela móvel) gerada

- [DECISÃO] A conta feita antes de gerar a tarefa mudou o desenho: limitar a escala "minuto" a 24h
  resolve o crescimento sem limite, mas **não** resolve a navegação — a 10px/s, 24h dão 864.000px
  (o histórico atual, de 30h, dá 1,08 milhão), e "mais zoom" piora, porque alarga ainda mais. Não
  dá para ter recorte largo e zoom alto numa escala fixa. O usuário escolheu **janela móvel**:
  recorte de poucos minutos por vez, deslizando dentro das últimas 24h.
- [DIRECIONAMENTO] Trava anotada na tarefa: **ancorar o fim da janela na requisição mais recente,
  não em `Date.now()`** — senão quem abre o painel depois de dois dias sem usar o app vê uma linha
  do tempo vazia e acha que perdeu os dados.
- [DIRECIONAMENTO] Três escolhas de desenho delegadas ao Executor **com obrigação de justificar**:
  largura do recorte, mecanismo de deslizar, e o que fazer com a roda do mouse (hoje ela alterna
  escala; com janela móvel talvez faça mais sentido ela deslizar). A tarefa proíbe mudar o
  comportamento validado sem dizer.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 2 gerada, nível `completo`, com a instrução (nova desde a
  Etapa 1) de parar e reportar se o ambiente não tiver navegador, em vez de buscar contorno.
- [ARTEFATO] Estado do git mudou: o usuário destravou o `index.lock` e **commitou** o projeto. Pela
  primeira vez desde 2026-08-16 o código está versionado — o que reduz o risco da remoção do
  alternador prevista na Etapa 3.

- [DECISÃO] **Roda do mouse na linha do tempo, decidido pelo usuário em 2026-08-20**: sem ativação,
  a roda alterna entre as escalas (comportamento atual); **ativada por clique**, a roda desliza a
  janela no tempo. Resolve o conflito entre os dois gestos sem perder nenhum. Ambiguidade travada
  pelo PM ao escrever a tarefa: clicar num **ponto** continua abrindo o popup do texto — a ativação
  é o clique na área da linha do tempo **fora** dos pontos. Exigido também que o estado seja visível
  (senão a roda vira loteria), reversível, e que o botão de zoom siga funcionando nos dois estados
  como saída garantida.

## [2026-08-20] Bug da rolagem da janela + navegação por dias

- [DIRECIONAMENTO] Usuário usou a janela móvel e reportou que rolar com a linha do tempo ativada
  "vai diretamente pro fim". **Causa localizada pelo PM, e é uma correção antiga brigando com a
  etapa nova**: `linhaTempoConsumo.scrollLeft = xUltimoPonto - larguraVisivel + margemDireita`
  (~linha 1309) roda a **cada renderização**. Veio da Etapa 6 do plano anterior, quando o SVG era o
  histórico inteiro e abrir no ponto mais recente era o certo; com a janela móvel virou hostil,
  porque cada giro da roda redesenha e o redesenho reposiciona o scroll. A janela se move — quem
  volta é a rolagem interna do container.
- [DIRECIONAMENTO] Padrão que vale registrar: **comportamento "conveniente" amarrado ao ciclo de
  render sobrevive à mudança de arquitetura e vira defeito.** Já é a segunda vez neste projeto que
  algo assim aparece (a primeira foi o auto-scroll caindo na folga de 8% do eixo, na própria Etapa
  6). Ao revisar render, perguntar sempre: isto deveria rodar em toda renderização, ou só na
  primeira?
- [DECISÃO] Navegação por dias na escala "hora", a pedido do usuário: um dia por vez, com ida e
  volta, em vez do histórico inteiro comprimido. Dá simetria ao painel — "hora" mostra um dia,
  "minuto" mostra um recorte de minutos dentro de um dia.
- [DIRECIONAMENTO] Ponto mais fácil de errar, travado na tarefa: **as duas escalas precisam
  concordar sobre o período olhado**. Trocar de "hora" (olhando o dia 18) para "minuto" não pode
  jogar o usuário de volta ao trecho mais recente. O Executor tem de propor e justificar como
  amarrou as duas.
- [DECISÃO] Bug e pedido agrupados numa tarefa só, a pedido do usuário — mesma função de render,
  mesmo aparato de teste.

## [2026-08-20] Correção da rolagem concluída + tarefa da Etapa 3 (faxina)

- [ARTEFATO] Correção fechada e verificada no código pelo PM: a flag
  `rolarParaUltimoPontoNaProximaRenderizacao` é ligada em exatamente três pontos (abrir painel,
  trocar escala, botão "Mais recente") e consumida numa única renderização; em qualquer outro
  redesenho o `scrollLeft` fica em 0. É o recorte que anda, não a rolagem interna.
- [ARTEFATO] Sensibilidade da roda medida e registrada em número, como a tarefa exigia: **6,7s por
  giro, 27 giros para atravessar a janela de 3min, ~6,2 giros por tela cheia (624px)** — mantida sem
  ajuste, com o dado justificando a decisão em vez de adjetivo.
- [DECISÃO] Concordância entre as escalas resolvida por **tradução no momento da troca**
  (`sincronizarMinutoComDia`/`sincronizarDiaComMinuto`), não por estado compartilhado — as duas
  guardam o período de formas estruturalmente diferentes. Cuidado que salvou o caso comum: ancorar
  na **última requisição do dia**, não na meia-noite; ancorar na meia-noite faria trocar de escala no
  dia de hoje abrir a janela num horário sem requisição por perto. O Executor relatou ter escrito a
  versão ingênua, visto quebrar e corrigido antes de entregar.
- [DIRECIONAMENTO] **Estado morto achado pelo Executor**: ativar a linha do tempo na escala "hora"
  deixava a roda sem efeito nenhum (não desliza, não troca de escala), prendendo o usuário até Esc.
  Decisão do usuário: ativada na "hora", a roda **navega entre dias**. Fecha a regra do painel numa
  frase só — *ativada, a roda anda no tempo; desativada, alterna as escalas*. Entrou como item (a0)
  da faxina.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 3 gerada (última do plano): cinco itens mecânicos, nível
  `curto` **por item**, com instrução de reportar cada um separadamente e não deixar um bloqueio
  segurar os outros.

## [2026-08-20] Etapa 4 aprovada — faixa de áudio com histórico + botão de cancelar

- [DIRECIONAMENTO] Pedido do usuário a partir da interface de ditado do Claude (captura de tela
  trazida por ele): faixa de barras mostrando o **histórico** do áudio, dando continuidade visual de
  que o áudio está sendo enviado, mais um **botão de cancelar** para quando ele fala algo e quer
  reiniciar.
- [ARTEFATO] Achado do PM ao ler o código: as barras de nível de hoje são **decorativas** —
  `animarBarrasNivel` aplica o mesmo RMS a todas as barras, com uma variação senoidal por índice só
  para parecerem distintas; sobem e descem juntas. Virar histórico é trocar o valor único por um
  buffer de amostras deslocando no tempo: pouco código, mas mudança de conceito.
- [DECISÃO] **O cancelar nunca altera a caixa de texto**, regra dada pelo usuário sem exceção, depois
  de o PM propor três alternativas que mexiam no texto. Na gravação normal ele interrompe antes de
  enviar; no modo tempo real apenas interrompe o envio, e o texto já recebido permanece. Registrado
  porque o PM havia assumido que "reiniciar" implicaria limpar o que apareceu — não implica.
- [PENDÊNCIA] A resolver antes de gerar a tarefa: "só pausa" significa encerrar sem enviar, ou pausar
  de forma retomável (conexão aberta, volta de onde parou)? Muda bastante a implementação no modo
  tempo real.
- [DECISÃO] Entra como **Etapa 4**, depois da faxina — a tarefa da faxina já está escrita e pronta
  para o EXEC, e misturar decisão de desenho numa etapa mecânica desfaria o motivo de tê-la agrupado.

## [2026-08-20] Faxina concluída + tarefa da Etapa 4

- [ARTEFATO] Etapa 3 (faxina) fechada e verificada item a item pelo PM: roda na escala "hora"
  navegando dias com o mesmo sentido de gesto da escala "minuto"; `modo_turno` com **zero**
  ocorrências no frontend e no backend; botão de copiar com confirmação pela área de status
  existente e tratamento de caixa vazia; rota renomeada para `POST /tempo-real/turno-concluido`;
  favicon gerado em memória, sem arquivo novo no repositório. O Executor reportou cada item em
  entrada separada, como pedido — o agrupamento funcionou sem virar entrada única ilegível.
- [DECISÃO] **Desenho do cancelar fechado pelo usuário**: o botão **X cancela, nada será enviado**, e
  **só aparece enquanto grava**; o botão redondo do microfone **vira quadrado durante a gravação**,
  sinalizando parada. Gravando, existem dois controles: quadrado (parar) e X (cancelar).
- [DECISÃO] **Pausa retomável descartada** — manteria o WebSocket aberto e parado, com o token
  efêmero expirando em poucos minutos e a sessão tendo limite próprio; o botão prometeria algo que
  às vezes não cumpriria. Trade-off aceito: para continuar depois de cancelar, aperta gravar de novo.
- [DIRECIONAMENTO] Regra reafirmada na tarefa em três lugares diferentes (o que fazer, critério de
  pronto e o que não fazer): **o cancelar nunca altera a caixa de transcrição**, em nenhum modo. Foi
  a correção que o usuário fez sobre uma suposição errada do PM, e é o tipo de regra que um chat
  futuro reinventaria se estivesse escrita só uma vez.
- [DIRECIONAMENTO] Critério de pronto exige **comprovar o deslocamento das barras** (amostrar
  alturas em dois instantes e mostrar que o padrão andou), não "ficou parecido com a referência" —
  senão o critério passaria com a animação decorativa que já existe hoje.

## [2026-08-20] Etapa 4 concluída + correção de cadência da faixa

- [ARTEFATO] Etapa 4 entregue e verificada no código pelo PM: `amostrasNivel` é um buffer que
  desloca (histórico de verdade, não mais o RMS único replicado com seno cosmético), amostrado por
  `setInterval` em intervalo fixo e zerado a cada gravação nova; `#botaoCancelarGravacaoRapida`
  nasce `hidden` e só aparece gravando; o ícone do botão principal troca de microfone para quadrado
  durante a gravação.
- [DIRECIONAMENTO] Usuário reportou que a movimentação ficou "meio lenta". **Causa localizada pelo
  PM: são os números, não a lógica** — `NUM_BARRAS_NIVEL = 12` com `INTERVALO_AMOSTRA_BARRAS_MS =
  250` dão 4 atualizações por segundo numa faixa de 3,0s; o olho vê degraus, não fluxo. A referência
  (ditado do Claude) tem mais de cem barras finas atualizando rápido.
- [DECISÃO] A correção precisa mexer em **densidade e cadência juntas** — só uma das duas não
  resolve: mais barras no mesmo intervalo continua em degraus; intervalo menor com 12 barras faz a
  faixa cobrir menos de um segundo e piscar. Ponto de partida sugerido: ~60ms com ~80 barras
  (~17 atualizações/s, ~4,8s de histórico), com o Executor livre para ajustar e obrigado a registrar
  os números finais.
- [DIRECIONAMENTO] Tarefa explicita **não refazer a lógica de histórico** — ela está correta e
  verificada. É o tipo de correção em que um executor sem essa trava reescreveria a parte boa junto.

## [2026-08-20] Etapa 5 — reorganização da interface de gravação

- [DIRECIONAMENTO] Pedido do usuário depois de usar a tela: tirar os textos explicativos ("clique
  para gravar", rótulo "Transcrição por voz (editável, soma cada gravação)", mensagem de
  "gravando"); botão de copiar só com ícone, no canto inferior direito da caixa de texto; e os
  controles reorganizados numa faixa em cima, com **gravar fixo no centro**, cancelar à direita só
  durante a gravação, e **três pontos à esquerda** agrupando configurações e consumo num popup.
- [DECISÃO] **Interpretação do PM, sinalizada ao usuário antes de executar**: o campo que mostra
  "Gravando…" é o **mesmo** (`#statusGravacaoRapida`) que mostra "Permissão de microfone negada",
  "Não foi possível conectar ao backend", o aviso do corte de 2min30s e "Texto copiado". Remover o
  campo levaria os erros junto e deixaria o usuário sem diagnóstico. Decidido remover só as
  mensagens redundantes e manter o canal — com critério de pronto exigindo **forçar um erro e provar
  que ele ainda aparece**.
- [DIRECIONAMENTO] Detalhe de acessibilidade travado na tarefa: tirar o `<label>` do transcript
  deixaria a textarea sem nome acessível, e o botão de copiar só com ícone idem — exigido
  `aria-label` nos dois. Remoção de texto visível não pode virar remoção de semântica.
- [DIRECIONAMENTO] Ponto técnico do "centro fixo": `.linha-gravacao-rapida` é hoje um flex com
  `justify-content: center` e `gap`, então qualquer botão que apareça ao lado empurra o do meio. Um
  grid de três colunas com laterais iguais resolve. Critério de pronto **mede**
  `getBoundingClientRect().left` parado e gravando, em vez de aceitar avaliação a olho.
- [DECISÃO] A correção de cadência da faixa foi **dobrada nesta etapa** em vez de virar tarefa
  própria: ainda não tinha ido para execução, mexe na mesma região e no mesmo aparato de teste, e
  reorganizar primeiro obrigaria a testar as barras duas vezes.

- [DECISÃO] **Status vira balão efêmero** (usuário, 2026-08-20), reaproveitando a classe `.toast` já
  existente do aviso de "nenhuma fala" — sem inventar um segundo estilo de notificação. Tempos:
  **confirmação 2s, erro 6s**; o erro ganha mais tempo porque algumas mensagens são longas
  ("Não foi possível conectar ao backend. Confirme que o servidor está rodando na porta 8000...") e
  2s não dariam tempo de ler.
- [DIRECIONAMENTO] **Terceiro tipo de mensagem levantado pelo PM, fora do enquadramento
  confirmação/erro**: "Transcrevendo…" e "Encerrando… aguardando a transcrição do último trecho" são
  **estado em andamento**, não notificação. Se sumissem em 2s, o usuário ficaria diante de uma tela
  parada sem saber se travou — justamente enquanto o app espera a API. Devem durar enquanto a ação
  durar e sumir quando ela termina. Critério de pronto exige testar os três tempos separadamente.
- [DECISÃO] O terceiro tipo de mensagem ("em andamento") foi **resolvido pelo usuário eliminando a
  mensagem**: em vez de texto persistente, o **botão principal vira spinner** enquanto a ação corre.
  O botão passa a ter três estados e conta a história sozinho — **microfone (parado) → quadrado
  (gravando) → spinner (processando)**. Durante o spinner ele fica desabilitado e o X não aparece,
  porque o áudio já foi enviado e não há o que cancelar. Solução melhor que a proposta do PM: mantém
  o sinal de "está trabalhando" sem devolver texto à tela que o usuário quer limpa.
- [DECISÃO] **Lixeira que vira desfazer** (usuário, 2026-08-20): botão só com ícone no canto inferior
  esquerdo da caixa de texto, espelhando o de copiar no direito. Ao apagar e a caixa ficar vazia, o
  **próprio botão troca de função** e vira uma seta curva de desfazer — mesmo lugar, sem botão extra
  nem balão de confirmação. Resolve a perda acidental sem sujar a tela, que era a preocupação do PM
  (apagar destrói texto acumulado de várias gravações e edições manuais, e zerar `value` mata o
  Ctrl+Z nativo).
- [DIRECIONAMENTO] Quatro casos de borda travados na tarefa pelo PM: (1) caixa vazia sem nada a
  restaurar não pode oferecer desfazer falso; (2) **texto novo depois de apagar faz o botão voltar a
  ser lixeira** e descarta o snapshot — senão apertar "desfazer" apagaria o texto novo, o oposto do
  que promete; (3) apertar a lixeira duas vezes não pode perder o snapshot original; (4) o desfazer
  restaura o conteúdo inteiro, incluindo edições manuais, não só a última gravação.
- [DIRECIONAMENTO] **Esclarecimento do usuário sobre a lixeira/desfazer**: o gatilho é o **estado da
  caixa**, não quem a esvaziou. Caixa vazia com conteúdo anterior guardado → botão é desfazer,
  mesmo que o usuário tenha apagado à mão em vez de usar a lixeira.
- [DIRECIONAMENTO] **Armadilha de implementação travada pelo PM**: guardar "o valor anterior" a cada
  evento de digitação quebra no caso mais comum — apagando com backspace segurado, o valor anterior
  ao vazio é **uma única letra**, e o desfazer devolveria "a" em vez do texto. O snapshot precisa ser
  do conteúdo **antes da rajada de edição** (ex.: guardar quando a caixa fica ociosa e não vazia).
  Critério de pronto exige demonstrar justamente esse caso, com o texto antes e depois colado.

## [2026-08-20] Etapa 5 aprovada + acabamento visual da faixa

- [ARTEFATO] Etapa 5 entregue e aprovada pelo usuário ("gostei muito de tudo"). Executor: 80 barras
  a 60ms (4,8s de histórico, ~16,7 atualizações/s), barras em `flex: 1 1 0` para caberem em qualquer
  largura, snapshot do desfazer guardado por **ociosidade de 800ms** — que é justamente o que
  sobrevive à armadilha do backspace segurado levantada pelo PM —, e posição do botão central medida
  antes/depois.
- [DIRECIONAMENTO] Pedido de acabamento: barras mais finas e arredondadas, **espelhadas no centro**,
  placeholder fora, e botões laterais próximos do central. O usuário pediu explicitamente ajuda para
  teorizar o visual.
- [DECISÃO] Teorização do PM, registrada no `PLANO.md`: (1) espelhar é quase de graça — trocar
  `align-items: flex-end` por `center` faz cada barra crescer para os dois lados sozinha; (2)
  silêncio vira fileira de pontos no centro se a altura mínima igualar a largura da barra com
  arredondamento total, que é o "pulso constante" pedido e serve de prova de vida; (3) **a curva de
  amplitude é o que mais muda a sensação** — altura proporcional direta ao RMS espreme a fala normal
  embaixo, e só uma curva compressiva (raiz, dB) põe a conversa na região média e reserva o topo à
  ênfase, que é o "picos crescentes" desejado. Sem ela, espelhar só duplica um traço achatado.
- [DIRECIONAMENTO] Honestidade registrada junto: **a metade de baixo não carrega informação** — é a
  mesma medida refletida. A simetria é escolha estética (legibilidade, "cara de áudio"), não ganho
  de dado. Registrado para que ninguém no futuro ache que está lendo dois canais.
- [DIRECIONAMENTO] Risco do pedido de aproximar os botões: aproximar mexendo nas colunas quebraria o
  **centro fixo** validado na Etapa 5. Tarefa instrui manter as colunas laterais simétricas e
  alinhar o conteúdo para dentro, e o critério de pronto **mede** a posição do botão de novo.
- [DECISÃO] Copiar e lixeira/desfazer saem de **dentro** da caixa de texto para uma linha **abaixo**
  dela (usuário, 2026-08-20), mantendo os lados já escolhidos — lixeira à esquerda, copiar à direita.
  Motivo: sobrepostos ao conteúdo, com a caixa cheia eles ficam flutuando por cima de palavras e o
  texto passa por baixo deles. Critério de pronto acrescentado: texto longo não pode passar sob
  nenhum botão.

---

# Resumo consolidado — encerramento do chat de 2026-08-19/20 (PM)

> Proposta de consolidação, a validar. Cobre o período de 2026-08-19 a 2026-08-20 deste chat de PM:
> o fechamento do plano de tempo real + linha do tempo, a virada de plano, e o plano de usabilidade
> que veio depois. O registro bruto por interação está acima, na ordem em que aconteceu.

## Decisões

- **Modo ao vivo mantido com `gpt-live-transcribe`**, recusando a troca para um modelo ~3x mais
  barato — trade-off: paga-se mais para preservar nuance de fala; a estimativa de economia (~50% numa
  sessão típica) ficou registrada no Backlog para o dia em que custo virar prioridade.
- **Detecção de turno pela API encerrada sem uso** — trade-off: perde-se a chance de corrigir o corte
  de palavras nas emendas, em troca de não trocar de modelo; `gpt-live-transcribe` recusa
  `turn_detection` diferente de `null` (HTTP 400, confirmado na documentação e por teste trocando só
  o modelo).
- **Corte de segurança do modo ao vivo em 150s**, igual à gravação normal — trade-off: pode
  interromper uso legítimo longo, em troca de consistência e de limitar a ~US$ 0,04 o custo de uma
  gravação esquecida.
- **Gate de silêncio implementado como "não enviar"**, não "enviar e não comitar" — trade-off:
  nenhum; foi o achado técnico do período, porque com `turn_detection: null` o áudio não comitado
  fica no buffer do servidor e é cobrado junto no commit seguinte.
- **Registro do PROGRESSO ganhou três níveis** (`recibo`/`curto`/`completo`), declarados pelo PM na
  tarefa — trade-off: perde-se o relato detalhado do "como fiz", ganha-se um canal legível; o que
  nunca encolhe é como testou, com o dado que prova.
- **Arquivamento do PROGRESSO passou a ter a virada de plano como gatilho**, com 60 KB só como
  alarme — trade-off: fura a regra de o PROGRESSO ser exclusivo do executor (exceção datada ao PM),
  em troca de não queimar um chat EXEC em recortar e colar.
- **Botão principal com três estados** (microfone → quadrado → spinner) substituindo as mensagens de
  "em andamento" — trade-off: nenhum; mantém o sinal de "está trabalhando" sem devolver texto à tela.
- **Status virou balão efêmero**: confirmação 2s, erro 6s — trade-off: uniformidade menor, em troca
  de mensagens longas de erro darem tempo de ler.
- **Lixeira que vira desfazer pelo estado da caixa** (não por quem esvaziou) — trade-off: exige
  snapshot por ociosidade em vez do valor anterior, sob pena de o desfazer devolver uma única letra
  quando o usuário apaga com backspace segurado.

## Artefatos

- **Plano de tempo real + linha do tempo encerrado**: 7 etapas + 2 correções, todas verificadas no
  artefato real pelo PM. Arquivado em `historico/PLANO_2026-08-20b_tempo-real-encerrado.md`.
- **`POST /tempo-real/turno-concluido`** (ex-`/consumo/tempo-real`): recebe texto + `usage` do modo
  ao vivo e grava `consumo.jsonl` e `transcricoes.jsonl` com o mesmo id `uuid4`.
- **`transcricoes.jsonl`**: texto de cada requisição ligado ao consumo.
- **Linha do tempo no painel de consumo**: janela móvel de 3min dentro das últimas 24h, navegação
  por dias na escala "hora", eixo com hora de relógio e passo dinâmico, popup com o texto.
- **Freios de custo do modo ao vivo**: corte de 150s e gate de silêncio contínuo com hangover de 2s.
- **Interface de gravação reorganizada**: faixa de barras com histórico real (80 barras a 60ms),
  botão central fixo com três estados, X de cancelar, três pontos agrupando configurações e consumo,
  copiar e lixeira/desfazer.
- **`PROGRESSO.md` arquivado**: de 187 KB para 304 bytes, 2.565 linhas movidas para três arquivos em
  `historico/`, integridade conferida (conteúdo rejuntado idêntico ao original).
- **Regras de método escritas** em `.claude/PM.md`, `.claude/EXECUTOR.md` e `CLAUDE.md` (níveis de
  registro, arquivamento por virada de plano, exceção datada ao PM, idioma português).

## Direcionamentos

- **EXEC reporta e recomenda, não decide.** Confirmado em uso: os freios de custo, a correção da
  nota da Etapa 1, o estado morto da roda na escala "hora" e o bloqueio do `turn_detection` saíram
  todos de recomendações dele.
- **Executor deve parar e reportar quando o ambiente não tiver navegador**, em vez de buscar
  contorno para dar critério por atendido — regra criada depois de uma etapa voltar parcial.
- **Critério de pronto precisa pedir o dado que prova**, não adjetivo. Lições do período: pedir
  contagem presumindo densidade (erro do PM, corrigido pelo Executor com medição); pedir "ficou
  parecido" deixaria passar a animação decorativa que já existia.
- **Comportamento amarrado ao ciclo de render sobrevive à mudança de arquitetura e vira defeito** —
  aconteceu duas vezes com o mesmo `scrollLeft`. Ao revisar render, perguntar se aquilo deve rodar em
  toda renderização ou só na primeira.
- **Remoção de texto visível não pode virar remoção de semântica** — `aria-label` obrigatório onde o
  rótulo saiu.
- **Todo o trabalho do repositório é em português do Brasil** (regra escrita depois de o EXEC
  responder em inglês).

## Pendências

- **Etapa de acabamento visual da faixa** (espelhamento, curva de amplitude, botões fora da caixa,
  laterais próximas do central) — `PROXIMA_TAREFA.md` gerada e **não executada**; depende de: abrir
  um chat EXEC.
- **Bordas de turno cortando palavras** ("frase" → "fra" + "Base") — sem solução aprovada; o
  candidato natural é o commit guiado por silêncio (6s viram piso, turno fecha na primeira pausa),
  ideia do usuário, que não muda custo e mantém o modelo; depende de: o usuário decidir se incomoda.
- **Resíduo do fechamento do WebSocket** (~100ms após commit periódico) — depende de: aprovação.
- **`consumo.jsonl` mistura uso real com testes do Executor** — sem separação prevista.
- **Arquivamento do PROGRESSO na próxima virada** — o vivo voltou a crescer com o plano novo.
- **Backlog maior** (banco de dados no lugar dos `.jsonl`, blocos com sobreposição, rotação de
  transcrições, CORS aberto, plataforma self-hosted) — sem data.
