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
