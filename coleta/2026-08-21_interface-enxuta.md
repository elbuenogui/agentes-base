# Coleta — frente nova: interface enxuta (a partir de 2026-08-21)

> Frente de funcionalidade escolhida pelo usuário em 2026-08-21, depois de a de usabilidade
> encerrar. Ainda em levantamento: o usuário disse que passaria as mudanças aos poucos, então
> este arquivo é a lista viva até o plano ser montado. Append-only.

## Coleta — primeiro lote de mudanças (2026-08-21)

- [DIRECIONAMENTO] A tela principal deve ficar enxuta: os três alternadores do topo (**Modelo de
  transcrição**, **Streaming do transcript**, **Transcrição em tempo real**) saem da página e
  passam a viver dentro da janela de **Configurações**, que hoje só tem o seletor de microfone.
- [DIRECIONAMENTO] O **upload de áudio vira um item do menu de três pontos**, ao lado de
  Configurações e Consumo, aberto por ícone. Sem o rótulo "Arquivo de áudio (.m4a, .wav, .mp3)" e
  sem botão "Transcrever": escolheu o arquivo, já transcreve. Pedido literal do usuário: "não
  precisa colocar esse tanto de descrição... eu quero mais clean".
- [DECISÃO] O texto do áudio enviado por upload passa a **somar na mesma caixa de transcrição**
  das gravações — trade-off: exige unificar dois caminhos de saída que hoje são separados
  (`#resultado` para o upload e `#transcriptRapido` para a gravação), mas a tela passa a ter um
  lugar só de texto, com copiar e lixeira/desfazer valendo para tudo.
- [DECISÃO] **A parte de cima da página some inteira** — título, subtítulo, os três alternadores,
  o formulário de upload e o separador "ou" — e a área de gravação sobe para o topo. Sem título
  na tela. Trade-off: a página perde o `<h1>`, então o nome do app precisa continuar existindo em
  algum lugar acessível (título da aba e/ou cabeçalho visualmente oculto), senão a tela fica sem
  identificação para leitor de tela.
- [DECISÃO] Dentro das Configurações, streaming e tempo real viram **interruptores liga/desliga**
  e o modelo vira **lista de seleção**, sem o "(clique para alternar)" — trade-off: dá mais
  trabalho de CSS/JS do que só mover os botões atuais para dentro da janela, e traz risco de
  regressão nos três controles, mas tira o jeitão de MVP de dentro das configurações.
- [DIRECIONAMENTO] **Arrastar e soltar áudio** na área central volta **depois**, em outra frente —
  o usuário disse "posteriormente vamos voltar com o drag de áudio". Registrado no Backlog do
  `PLANO.md`.
- [PENDÊNCIA] A lista de mudanças desta frente **não está fechada** — o usuário ainda vai passar
  outros itens — depende de: o usuário terminar de passar as mudanças para o PM montar o plano.

## Coleta — formato e ordem de execução (2026-08-21)

- [DIRECIONAMENTO] O usuário decidiu que este primeiro lote **cabe em uma tarefa só** e não precisa
  de plano — a frente segue sem `PLANO.md` próprio por enquanto.
- [DECISÃO] Ordem de execução: **commit primeiro** (Etapa 3 da faxina), depois a tarefa da
  interface — trade-off: adia a interface em uma sessão de EXEC, mas a tarefa reescreve um pedaço
  grande do `index.html` e hoje não existe nenhum commit atrás dela para servir de restauração.
  A Etapa 2 da faxina (mover snapshots) foi adiada pelo usuário para depois disso.
- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md` agora tem a tarefa do commit (Etapa 3), com
  checagem explícita de que `.env`, os dois `.jsonl`, `.venv/` e `__pycache__/` não entram em
  commit nenhum.
- [ARTEFATO] `.claude/tmp/TAREFA_interface-enxuta.md` — tarefa da interface escrita e guardada,
  pronta para virar `PROXIMA_TAREFA.md` assim que o commit sair.
  `.claude/tmp/TAREFA_etapa2_faxina.md` — a tarefa da Etapa 2, guardada antes de o arquivo vivo ser
  sobrescrito.
- [DECISÃO] Mesmo o usuário tendo pedido "sem título", a página mantém um **cabeçalho visualmente
  oculto** e o `<title>` da aba — trade-off: some da tela como ele quer, mas a página não fica
  anônima para leitor de tela. Decidido pelo PM e avisado ao usuário, sem objeção.
- [PENDÊNCIA] `.claude/tmp/` passou a guardar tarefas que ainda não foram executadas — depende de:
  não limpar a pasta antes de promovê-las (aviso registrado no Backlog do `PLANO.md`).

## Coleta — tarefa promovida (2026-08-21)

- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md` passou a ser a tarefa da interface enxuta, depois
  de o commit da Etapa 3 sair. A tarefa entra **fora do `PLANO.md`** (a frente não tem plano
  próprio, por decisão do usuário), então o registro dela no `PROGRESSO.md` vai cair junto com o
  do plano de faxina — quem arquivar na próxima virada precisa saber disso.

# Resumo consolidado — levantamento da frente de interface enxuta (2026-08-21)

> Frente **em aberto**: a tarefa do primeiro lote está escrita e ainda não foi executada, e o
> usuário pode ter mais mudanças a pedir. Este resumo cobre o que foi decidido até aqui.

## Decisões
- O texto do upload passa a **somar na mesma caixa** das gravações — trade-off: exige unificar
  dois caminhos de saída hoje separados (`#resultado` e `#transcriptRapido`), mas a tela passa a
  ter um lugar só de texto, com copiar e lixeira/desfazer valendo para tudo.
- **A parte de cima da página some inteira** (título, subtítulo, alternadores, formulário e o
  "ou") e a área de gravação sobe — trade-off: a página perde o `<h1>`, então o nome do app fica
  num cabeçalho visualmente oculto e no `<title>` da aba, para a tela não ficar anônima para
  leitor de tela. Decisão do PM, avisada ao usuário, sem objeção.
- Dentro das Configurações: modelo vira **lista de seleção**, streaming e tempo real viram
  **interruptores**, sem texto de dica na tela (a explicação vai para `title`/`aria-label`) —
  trade-off: mais trabalho de CSS/JS e risco de regressão nos três controles do que só mover os
  botões, mas tira o jeitão de MVP de dentro da janela.
- O primeiro lote **cabe em uma tarefa** e a frente segue **sem `PLANO.md` próprio** — trade-off:
  o registro dela no `PROGRESSO.md` cai junto com o do plano de faxina, e a próxima virada vai
  precisar separar; em troca, não se abre um segundo plano vivo por três mudanças de interface.
- **Commit primeiro, interface depois** — trade-off: adiou a interface em uma sessão de EXEC, mas
  a tarefa reescreve um pedaço grande do `index.html` e não havia ponto de restauração. Executado
  em 2026-08-21: os 4 commits saíram antes.

## Artefatos
- `.claude/estado/PROXIMA_TAREFA.md` — tarefa da interface enxuta, escrita, promovida e **não
  executada**. Além do pedido do usuário, ela carrega três armadilhas mapeadas pelo PM na leitura
  do código: reaproveitar `enviarGravacaoRapida` preservando nome e extensão reais do arquivo (ela
  hoje renomeia tudo para `gravacao.<ext>`), atualizar os ~8 pontos que fazem
  `botaoTempoReal.disabled` ao trocar o controle de tempo real, e limpar o `value` do input de
  arquivo para o mesmo arquivo poder ser escolhido duas vezes seguidas.
- Cópia da tarefa em `.claude/tmp/TAREFA_interface-enxuta.md` (já promovida, pode ir na limpeza).

## Direcionamentos
- Upload sem descrição de formatos e sem botão "Transcrever": escolheu o arquivo, transcreve.
- Enquanto o pedido couber em uma tarefa, segue sem plano; quando crescer, aí vira `PLANO.md` — e
  essa é a virada em que o `PROGRESSO.md` deve ser arquivado de novo.
- **Modo ao vivo fora de foco**: nada de commit guiado por silêncio nesta frente.

## Pendências
- Executar a tarefa da interface — depende de: abrir um chat EXEC.
- Mais mudanças de interface — depende de: o usuário passar o resto do que quer.
- Repasse final da retomada (Etapa 4 da faxina) — depende de: a interface rodar primeiro.
- Arrastar e soltar áudio na área central — adiado pelo usuário, no Backlog do `PLANO.md`.
