# Coleta — Retomada de PM: estado do plano e botão flutuante compacto (2026-09-05)

Chat de PM que retomou o projeto depois de uma semana parado (última atividade real: 2026-08-27),
levantou a ideia de mover parte da execução para o Codex CLI, e fechou o desenho do botão flutuante
compacto do app de desktop.

## 1. Registro por interação

- [DIRECIONAMENTO] Retomada em 2026-09-03: nada mudou no repositório desde 27/08. `PROXIMA_TAREFA.md`
  estava desatualizado (ainda descrevia a tarefa de geração de imagem, já concluída no
  `PROGRESSO.md`) — armadilha conhecida deste projeto.
- [PENDÊNCIA] Duas confirmações de uso real seguem em aberto, sem depender desta sessão: a segunda
  correção do crash do Qt na geração de imagem, e o atalho global com outra janela em foco no dia a
  dia.
- [DIRECIONAMENTO] Usuário considerou mover parte da execução (EXEC) para o Codex CLI, para não
  parar de implementar. Registrado em memória de projeto (`projeto_exploracao_codex.md`): o método
  PM/EXEC já é portável (coordenação só por arquivo), e o Codex 2026 suporta `AGENTS.md` + o padrão
  Agent Skills. Ainda não decidido nem testado.
- [DECISÃO] **2026-09-05, o usuário decidiu continuar executando aqui** (créditos Claude), não mover
  para o Codex agora. Trade-off: não aproveita eventual paralelismo de créditos, mas evita o custo de
  adaptar `AGENTS.md`/skills antes de validar se vale a pena.
- [DIRECIONAMENTO] Usuário considera o MVP atual "muito bom" — não pediu para reabrir a Etapa 3
  (histórias/MVP) agora; preferiu propor uma melhoria concreta de UI primeiro.
- [DECISÃO] **`D-32` — botão flutuante compacto por padrão, expande no hover e nos estados
  gravando/processando, encolhe só depois de colocado + mouse fora.** Trade-off: mais uma máquina de
  estados na janela (compacto ⇄ expandido) em troca de a janela deixar de "ficar no caminho" quando
  ociosa. Refina a `D-15` (21/08), que já prometia isto e nunca foi construída. Perguntas de desenho
  respondidas via `AskUserQuestion`: expandir mostra tudo (não uma versão reduzida do menu ⋮); grava/
  processa expande sozinho, independente do mouse.
- [DIRECIONAMENTO] Reconciliação necessária com `SPEC-002` item J1 ("a janela nunca muda de tamanho
  sozinha"): J1 é sobre conteúdo interno pipocando (cronômetro, faixa, balão), não sobre a troca
  deliberada compacto/expandido. Nota adicionada na própria `SPEC-002`.
- [DIRECIONAMENTO] Divergência para o Android (F3) já estava escrita na própria `D-15` desde 21/08 —
  toque não tem hover; resolve na spec da F3, não aqui. Nenhuma decisão nova necessária agora.
- [ARTEFATO] `spec/DECISOES.md` — `D-32` acrescentado.
- [ARTEFATO] `spec/specs/SPEC-002_paridade-desktop.md` — nota de reconciliação no item J, e a linha
  "os três estados da janela" marcada como **em construção**.
- [ARTEFATO] `.claude/estado/PLANO.md` — anexo fora do plano (`D-32`), no mesmo formato do anexo do
  `D-31`.
- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md` — reescrita: tarefa do botão flutuante compacto,
  substituindo a tarefa de geração de imagem (já entregue), com critério de pronto, riscos comuns
  (flicker no hover, perda do arrastar nativo sem moldura, ancoragem perto da borda da tela) e o que
  não fazer.
- [PENDÊNCIA] Falta decidir se esta sessão (PM) troca de papel para EXEC e implementa agora, ou se
  abre um chat de Executor separado, como o método deste projeto pede — depende de: resposta do
  usuário.

## 2. Consolidado

### Decisões
- Continuar executando via Claude por ora; não mover para Codex nesta sessão.
- `D-32`: botão flutuante compacto, com as regras de expansão/encolhimento acima, refinando `D-15`.

### Artefatos
- `spec/DECISOES.md` (D-32), `spec/specs/SPEC-002_paridade-desktop.md` (nota J1 + linha atualizada),
  `.claude/estado/PLANO.md` (anexo fora do plano), `.claude/estado/PROXIMA_TAREFA.md` (tarefa nova).
- Memória de projeto: `projeto_exploracao_codex.md`, `MEMORY.md` atualizado.

### Direcionamentos
- `PROXIMA_TAREFA.md` costuma ficar desatardado entre sessões — conferir contra `PROGRESSO.md` antes
  de assumir que descreve a tarefa corrente (já era conhecido, reafirmado aqui).
- Melhoria de UI decidida fora da ordem formal do plano (Etapa 3 ainda não escrita) — mesmo padrão
  já aberto pelo `D-31`, não é exceção nova.

### Pendências
- Confirmar em uso real: crash do Qt na geração de imagem (correção 2) e atalho global com outra
  janela em foco — depende de: usuário rodar o app.
- Decidir o papel/chat que executa a tarefa do botão flutuante — depende de: resposta do usuário.
- Etapa 3 (histórias, entregáveis, MVP) segue não iniciada — depende de: sessão de PM dedicada.

## 3. Continuação — execução via subagente (mesma sessão de PM, 2026-09-05)

- [DIRECIONAMENTO] Usuário deu autonomia ao PM para chamar um subagente que executa (papel EXEC),
  em vez de o PM executar ou abrir um chat separado. PM escolheu o modelo (`opus`) pela exigência do
  trabalho (estado de janela, threading Qt, precedente de bugs de transparência já visto no
  projeto).
- [ARTEFATO] `desktop/app.py` alterado pelo subagente: `JanelaDitado._aplicar_modo` (compacto
  110×110 ⇄ janela cheia), vigia de cursor a 100ms (não `enterEvent`/`leaveEvent`, que disparava a
  cada filho), debounce de 250ms para encolher, âncora pelo centro do `BotaoGravar`, arrastar sem
  moldura com limiar de 6px.
- [DECISÃO] Duas leituras que a tarefa não cobria literalmente, resolvidas pelo Executor e aceitas
  pelo PM: não encolhe com resultado pendente na tela (caixa vazia encolhe normal); painel/menu
  aberto trava o encolhimento.
- [PENDÊNCIA] `.git/index.lock` de 27/08 (não desta tarefa) segue impedindo commit — depende de: o
  usuário apagar na máquina (`del ".git\index.lock"`).
- [PENDÊNCIA] Risco de precedente: `WA_TranslucentBackground` no modo compacto pode repetir o bug já
  visto na `CamadaPulso` (transparência ok no `offscreen`, caixa opaca no Windows real) — depende de:
  usuário rodar o app.
- [PENDÊNCIA] Sem moldura, não sobrou forma confirmada de fechar o app (`Alt+F4` não testado, sem
  "Sair" no menu ⋮) — lacuna nova, precisa de tarefa própria antes de considerar isto pronto para uso
  diário.
- [ARTEFATO] `.claude/estado/PLANO.md` — anexo do `D-32` atualizado com o resultado da primeira
  volta e as quatro pendências acima.

## 4. Correção de status desatualizado (mesma sessão, 2026-09-05)

- [DIRECIONAMENTO] Usuário corrigiu o PM: a conversa estava reapresentando como "em aberto" duas
  coisas que ele já tinha descartado de vez — inserção automática no campo em foco (`B-22`/`POC-1`)
  e modo ao vivo (`D-02`). Confirmado por ele: as duas, definitivamente.
- [DECISÃO] **`D-33`** criada: as duas saem de vez, não é "depois". Não confundir com "colocar a
  última transcrição" (atalho próprio), que continua viva.
- [ARTEFATO] `spec/BACKLOG.md`: `B-22`, `B-03`, `B-04` → `morta`, apontando para `D-33`.
- [ARTEFATO] `spec/DECISOES.md`: `D-02` ganhou nota "endurecida em D-33".
- [ARTEFATO] `.claude/estado/PLANO.md`, `spec/specs/SPEC-002_paridade-desktop.md`,
  `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`: menções a "congelado"/"adiada" corrigidas para
  apontar para `D-33`.
- [DECISÃO] Usuário confirmou o conserto do item 3 pendente do `D-32` (fechar o app sem moldura):
  adicionar "Sair" no menu ⋮. Ainda não implementado.
- [PENDÊNCIA] Implementar "Sair" no menu ⋮ — depende de: próxima chamada de subagente Executor.

## 5. Consolidado (atualização)

### Decisões
- `D-33`: inserção automática e modo ao vivo descartados de vez (não "adiados"/"congelados").
- Fechar o app sem moldura: via item "Sair" no menu ⋮.

### Artefatos
- `spec/DECISOES.md` (D-33, nota em D-02), `spec/BACKLOG.md` (B-22/B-03/B-04 → morta), `PLANO.md`,
  `SPEC-002`, `COMPORTAMENTOS_PARQUEADOS.md` (menções corrigidas).
- Memória de projeto: `feedback_status_desatualizado_reapresentado.md`, `projeto_botao_flutuante.md`,
  `MEMORY.md` atualizado (e um arquivo `MEMORY.md` criado por engano na memória pessoal do usuário
  foi apagado na mesma sessão).

### Pendências
- Implementar "Sair" no menu ⋮ — depende de: chamar subagente Executor.
- As três pendências do `D-32` (index.lock, risco de transparência, confirmação real do hover)
  seguem abertas.

## 6. Segunda rodada — achados do usuário rodando de verdade (mesmo dia, 2026-09-05)

- [DIRECIONAMENTO] Usuário rodou a primeira volta do botão flutuante no Windows real e reportou três
  coisas: (1) compacto grande demais — deve abraçar o botão, não 110×110; (2) **bug**: parou de
  encolher depois do primeiro ciclo completo; (3) transição abrupta — pediu animação suave no
  expandir/encolher.
- [DECISÃO] Prioridade: corrigir o bug isolado dos dois ajustes visuais, com teste headless cobrindo
  ao menos dois ciclos completos (a suíte da primeira volta só cobria um, por isso não pegou o bug).
- [ARTEFATO] `spec/DECISOES.md`: `D-32` ganhou nota "refinada em 2026-09-05, segunda rodada".
- [ARTEFATO] `.claude/estado/PLANO.md`: anexo do `D-32` atualizado com a segunda rodada.
- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md`: reescrita — bug do encolhimento, tamanho compacto
  medido contra o botão real, animação de transição. "Sair" no menu ⋮ fica para depois, não entra
  nesta.
- [PENDÊNCIA] Chamar subagente Executor para esta tarefa — depende de: nada, PM já tem autonomia.

## 7. Consolidado (atualização)

### Decisões
- Bug do encolhimento é prioridade sobre os dois ajustes visuais.
- Compacto mede-se contra o `BotaoGravar` real, não um valor arbitrário.
- Transição expandir/encolher precisa ser animada.

### Pendências
- "Sair" no menu ⋮ segue na fila, depois desta rodada.
- As pendências de confirmação real do `D-32` (index.lock, risco de transparência) seguem abertas.

## 8. Segunda rodada entregue (mesmo dia, 2026-09-05)

- [ARTEFATO] `desktop/app.py`: bug corrigido na raiz — `_resultado_pendente` virou função derivada
  (compara caixa com último texto colocado) em vez de booleano manual, eliminando a classe inteira
  de causas (não só apagar pelo botão, também Ctrl+X, edição manual, copiar com caixa vazia).
- [ARTEFATO] Rede de segurança `_corrigir_tamanho_do_modo()` (100ms) para o que não dá para testar
  fora do Windows real.
- [ARTEFATO] Compacto agora 88×88, medido em tempo de execução contra o `BotaoGravar` real (72×72 +
  8px), não mais valor fixo.
- [ARTEFATO] Animação `QPropertyAnimation`/`InOutCubic`/160ms nos dois sentidos; achado e corrigido
  um desvio de âncora de 39px perto do topo da tela (onde o app abre por padrão).
- [ARTEFATO] `desktop/testes_janela_compacta.py` — suíte de regressão nova, versionada (fora da
  lista original da tarefa; PM aceitou, pois é o que teria pego o bug antes do usuário).
- [ARTEFATO] `spec/BACKLOG.md`: `B-24` — achado pequeno (duas transcrições idênticas seguidas
  confundem o detector de pendência), sem urgência.
- [DECISÃO] PM aceitou versionar o arquivo de teste fora da lista original — trade-off: pequeno
  desvio de escopo em troca de rede de regressão real (a suíte anterior só cobria um ciclo).
- [PENDÊNCIA] Tudo que só o Windows real confirma segue igual: suavidade da animação, hover,
  sempre-no-topo, translucidez, microfone, núcleo real.

## 9. Consolidado (atualização final desta sessão)

### Decisões
- Bug do encolhimento: causa raiz eliminada por invariante derivada, não patch pontual.
- Aceito versionar `desktop/testes_janela_compacta.py` fora da lista original da tarefa.

### Artefatos
- `desktop/app.py`, `desktop/testes_janela_compacta.py`, `spec/DECISOES.md` (D-32, segunda rodada),
  `spec/BACKLOG.md` (B-24), `.claude/estado/PLANO.md` (anexo atualizado).

### Pendências
- Confirmar no Windows real: animação, hover, sempre-no-topo, translucidez, microfone, núcleo.
- "Sair" no menu ⋮ segue na fila, ainda não implementado.
- `.git/index.lock` de 27/08 segue impedindo commit.

## 10. Terceira rodada — mais achados reais (mesmo dia, 2026-09-05)

- [DIRECIONAMENTO] Usuário testou a segunda volta de verdade e reportou: (1) a largura do compacto
  não diminuiu, apesar do relatado 88×88; (2) o botão pula de posição/tamanho durante a animação
  (confirmado via pergunta: não é sumir/piscar, é posição/tamanho errado); (3) falta "Sair" no menu
  ⋮, pendência conhecida desde a primeira volta.
- [DIRECIONAMENTO] Achada uma entrada de `PROGRESSO.md` já concluída, entre as duas voltas, corrigindo
  a janela nascendo num vão sem monitor (três monitores do usuário, medido por
  EnumWindows/GetWindowRect). Origem exata não confirmada nesta sessão — não é bloqueio, só contexto
  a preservar na próxima tarefa.
- [DECISÃO] Registro nível `completo` para esta rodada (não `curto`) — duas rodadas anteriores com
  registro curto e suíte headless não pegaram as duas regressões visuais; vale o relato mais extenso.
- [ARTEFATO] `.claude/estado/PROXIMA_TAREFA.md` reescrita com hipóteses de causa para os dois achados
  e instrução de medir quadro a quadro (não só nas pontas) via `grab()` offscreen.
- [PENDÊNCIA] Chamar subagente Executor para esta rodada.

## 11. Consolidado (atualização)

### Decisões
- Nível de registro sobe para `completo` nesta rodada, dado o padrão de regressões escapando do
  headless.
- "Sair" no menu ⋮ entra nesta rodada (não mais adiado).

### Pendências
- Confirmar no Windows real, ainda: translucidez (`D-32`), suavidade/posição da animação (agora com
  medição quadro a quadro), hover, sempre-no-topo, microfone, núcleo real.
- `.git/index.lock` de 27/08 segue impedindo commit.

## 12. Terceira rodada entregue (mesmo dia, 2026-09-05)

- [ARTEFATO] `desktop/app.py`: causa do botão pulando provada por medição de pixel (recorte pelo
  limite da janela durante reflow por quadro); animação reescrita como interpolação da janela
  inteira com layouts congelados; 0px de desvio medido nos dois sentidos e três cantos.
- [ARTEFATO] Bônus achado e corrigido pela mesma mudança: menu ⋮ preso em hover depois de expandir.
- [ARTEFATO] "Sair" adicionado ao menu ⋮ (5º item), testado com laço de evento real.
- [DECISÃO] Largura do compacto **não reproduzida** em headless — registrado honestamente como não
  confirmado, com hipótese específica (mínimo de janela não propagado pelo plugin offscreen) e log
  de diagnóstico novo para a próxima execução real decidir.
- [ARTEFATO] Suíte de teste rodada contra o código da rodada anterior, confirmando que pega os
  mesmos defeitos que o usuário relatou — evidência de que os testes evoluíram, não só o código.
- [PENDÊNCIA] Usuário rodar de novo e conferir: largura real (olhar `app.log`), suavidade da
  animação, hover/arrasto, translucidez, microfone, núcleo.
- [PENDÊNCIA] Decisão do PM/usuário: o percurso de 252–359px do botão perto do canto de abertura
  incomoda? Não é bug, é geometria do ponto de partida.
- [PENDÊNCIA] `desktop/app.log` versionado e crescendo a cada abertura — considerar `.gitignore`.

## 13. Consolidado (atualização final)

### Decisões
- Arquitetura de animação trocada para janela inteira interpolada com layouts congelados.
- Largura do compacto fica como pendência honesta, não fingida como resolvida.

### Pendências
- Confirmar no Windows real (lista de sempre): largura, animação, hover, sempre-no-topo,
  translucidez, microfone, núcleo.
- `desktop/app.log` no `.gitignore`? — decisão pequena, ainda não tomada.
- `.git/index.lock` de 27/08 segue impedindo commit.

## 14. Quarta rodada de feedback — PM parou para juntar evidência antes de despachar de novo

- [DIRECIONAMENTO] Usuário reportou, depois da terceira volta: "a janela ainda abre muito alta e
  larga" (agora os dois eixos, não só a largura) e "o botão ainda apresenta o bug que pisca".
- [DIRECIONAMENTO] PM leu `desktop/app.py` diretamente (sem subagente) antes de decidir o próximo
  passo: `_aplicar_modo(expandido=False, ancorar=False, animar=False)` roda no `__init__`, o
  compacto é calculado contra `botao_gravar.height()` em tempo real, e há log de diagnóstico
  (`_registrar_geometria_compacta`) que ainda não foi lido pelo PM — o usuário não colou o
  conteúdo do `app.log` ainda.
- [PENDÊNCIA] Três rodadas seguidas com achados que o headless não pegou. PM decidiu **não
  despachar uma quarta rodada às cegas** — pedir ao usuário: (a) fechar de vez a instância antiga
  (o "Sair" só existe desde a 3ª volta; instâncias de rodadas anteriores podem seguir abertas e
  sendo confundidas com a versão nova), (b) colar o trecho do `app.log` com "compacto alvo=...", (c)
  descrever melhor o que "pisca" significa.
- [DIRECIONAMENTO] Respostas do usuário (`AskUserQuestion`): (a) confirmou que fechou tudo e abriu
  do zero antes deste último teste — não é instância velha; (b) "pisca" não é a mesma coisa que o
  "pula de posição" já corrigido na 3ª volta — é **o próprio botão tremendo/piscando repetidamente,
  parado, especificamente durante a transição** (o momento em que o resto da janela aparece/some).
- [ARTEFATO] PM leu o corpo completo de `_aplicar_modo`, `_assentar_modo`, `_set_progresso_modo`,
  `_vigiar_ponteiro`, `_atualizar_ponteiro`, `_pode_encolher`, `_resultado_pendente` no `app.py`
  atual. **Hipótese anterior refutada por leitura de código**: `self._expandido` é trocado de
  imediato, ANTES da animação começar (linha 2789) — então o vigia de ponteiro (100ms) não
  reabre `_aplicar_modo` no meio da transição; `_pode_encolher`/`_atualizar_ponteiro` já leem o
  `_expandido` novo e não disparam de novo. Não é corrida de hover.
- [DECISÃO] Nova hipótese, apoiada em código + comportamento conhecido do Qt no Windows: a janela é
  `Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool` **com `WA_TranslucentBackground`**
  (linha 2576-2578) — uma janela "layered" de verdade no Windows (`UpdateLayeredWindow`). A
  animação chama `self.setGeometry(geo)` **redimensionando a janela nativa a cada quadro** (~10
  quadros em 160ms). Redimensionar repetidamente uma janela layered/translúcida sem moldura é
  fonte conhecida de flicker no Windows — e nenhum teste headless (plugin `offscreen`) consegue
  reproduzir isso, porque não há compositor real por trás. Esta é a mesma classe de achado que a
  largura não reproduzida (ambos só aparecem no Windows real, nunca no headless) — plausivelmente
  a MESMA causa raiz: redimensionamento nativo repetido demais, rápido demais, numa janela layered.
- [DECISÃO] Plano da 4ª rodada: parar de redimensionar a janela nativa quadro a quadro. Manter a
  janela do SO num tamanho fixo (o maior entre compacto e expandido) durante toda a transição —
  como já é translúcida, a área "extra" fica invisível — e só encolher de verdade (`setGeometry`
  para o tamanho final pequeno) no fim, já assentado, fora da animação. Deslocar/recortar botão e
  cartão continuam interpolados como hoje, só que dentro dessa janela de tamanho fixo. Isso também
  serve de diagnóstico: se a largura passar a bater certo em repouso (uma única troca de tamanho,
  sem animação no meio), confirma que o problema era o redimensionamento repetido, não um mínimo
  do Windows; se mesmo assim não encolher em repouso, isola o suspeito para o mínimo do SO
  (`SM_CXMINTRACK`).
- [PENDÊNCIA] Continua faltando o conteúdo real do `app.log` — pedido de novo ao usuário, mas o
  PM decidiu não bloquear a 4ª rodada nisso: a mudança de arquitetura acima é correta de qualquer
  jeito (elimina uma classe de risco conhecida) e o log, quando vier, decide o que sobrar.
- [DIRECIONAMENTO] PM despachou a 4ª rodada (subagente `opus`) com essa hipótese e arquitetura.

## 15. Quarta rodada entregue — mudança de arquitetura, não confirmação

- [ARTEFATO] Subagente (`opus`) implementou exatamente o plano: janela nativa parou de ser
  redimensionada a cada quadro (era ~12 vezes por transição); agora só 2 vezes (início: retângulo-
  união dos extremos; fim: tamanho final exato). Cartão e botão continuam interpolados dentro dessa
  janela fixa, que é translúcida (área extra invisível).
- [ARTEFATO] Medido headless: 1 redimensionamento nativo por sentido (não 2, porque a união já é o
  próprio expandido no caso normal), 0px de desvio do botão nos dois sentidos e três cantos, suíte
  estendida (76 verificações, 0 falhas), fumaça de menu/Sair/ditado/gerar-imagem todos passando.
- [PENDÊNCIA] Efeito colateral pequeno aceito por ora: durante os 160ms a janela nativa ocupa o
  retângulo maior e a área transparente extra não é clicável-através (clique ali vira arrasto) —
  já existia comportamento parecido na expandida (borda transparente de 16px), decisão de produto
  se incomodar, não bug.
- [DECISÃO] PM registrou honestamente em `D-32` (novo adendo) e `PLANO.md`: isto **não prova** que
  o tremor ou a largura sumiram — elimina uma causa plausível (redimensionamento nativo repetido
  numa janela translúcida/layered, fonte conhecida de flicker no Windows) comum a ambos os
  sintomas, mas nenhum dos dois é reproduzível headless. Confirmação real e o conteúdo do
  `app.log` (`compacto alvo=... real=...`) continuam pendentes.
- [PENDÊNCIA] Ambiente de teste do subagente precisou de remendo (faltava `libEGL.so.1`) — resolvido
  baixando bibliotecas do Ubuntu para `/tmp`, sem instalar nada permanente; registrado no
  `PROGRESSO.md` para quem rodar a suíte de novo nesta sessão.
- [DIRECIONAMENTO] Próximo passo é do usuário: testar no Windows real e responder duas coisas —
  o tremor sumiu? e o que diz a linha `compacto alvo=... real=...` do `app.log`?

## 16. Consolidado

### Decisões
- Arquitetura de redimensionamento trocada de "a cada quadro" para "só início e fim da transição".
- Continua sem declarar os dois sintomas reais (largura, tremor) como corrigidos — só o usuário
  confirma, e o `app.log` decide o lado da largura/altura.

### Pendências
- Usuário testar de novo no Windows: tremor sumiu? largura/altura do compacto batem?
- Colar a linha `compacto alvo=... real=...` do `app.log`.
- `.git/index.lock` de 27/08 continua impedindo commit.
- `desktop/app.log` no `.gitignore`? — decisão pequena, ainda não tomada.

## 17. Quinta rodada de feedback — novo sintoma mais preciso, PM achou causa por leitura de código

- [DIRECIONAMENTO] Usuário testou a 4ª volta: tremor "melhorou, mas não sumiu" (levemente); sintoma
  mais preciso agora — o botão fica invisível por um instante especificamente no momento em que o
  hover começa ou o mouse sai (não no meio da transição, que já foi resolvido). Tamanho do compacto
  continua ruim.
- [ARTEFATO] PM leu `_aplicar_modo` de novo e achou uma ordem de operações problemática: dois
  blocos (`_configurar_layout_do_modo(expandido)` e um `widget.setVisible(expandido)` sobre os
  widgets só-expandido) rodam **antes** de os layouts serem desabilitados e antes de a janela
  nativa crescer para o tamanho seguro (união) — ou seja, mudam margens/estilo/visibilidade AO VIVO
  na janela ainda do tamanho antigo, com o layout ainda no comando. No caminho que anima, esses
  widgets acabam escondidos de novo duas linhas depois, incondicionalmente — o show é sempre
  desfeito antes do primeiro quadro, mas o efeito colateral ao vivo é a explicação mais provável do
  "invisível por um instante" bem no início/fim da transição.
- [DECISÃO] Achado também que `_assentar_modo` já faz `widget.setVisible(self._expandido)` por
  conta própria — o bloco em `_aplicar_modo` é redundante nos dois caminhos (animado e não-animado).
  Plano da 5ª rodada: apagar esse bloco redundante, adiantar a desabilitação dos layouts e o
  redimensionamento nativo para a união para antes de `_configurar_layout_do_modo` rodar.
- [PENDÊNCIA] `app.log` continua sem ser colado pelo usuário — pedido de novo, explicitamente, no
  fim desta resposta do PM.
- [DIRECIONAMENTO] PM despachou a 5ª rodada (subagente `opus`).

## 18. Quinta rodada entregue — reordenação feita, com dois ajustes por medição

- [ARTEFATO] Subagente (`opus`) reordenou `_aplicar_modo`: layouts desabilitados e conteúdo
  só-expandido escondido antes de `_configurar_layout_do_modo` rodar (medido: 2/2 → 0/2 transições
  com layout ligado durante essa chamada).
- [ARTEFATO] Dois ajustes em relação ao pedido literal, justificados por medição: (1) apagar o
  `setVisible(expandido)` sem mais quebraria a âncora (163px de diferença no centro do botão
  medido com/sem o conteúdo visível) — a garantia foi para dentro de `_centro_local_do_botao`, que
  agora aplica visibilidade correta só durante a própria medição; (2) o redimensionamento nativo
  para a união não pôde vir antes de `_configurar_layout_do_modo` porque a união depende de
  `geo_final`, que depende das margens e do QSS já aplicados (1px de diferença pela borda).
- [DECISÃO] Suíte estendida (91 verificações, 76+15, 0 falhas), sem regressão da 4ª volta (0px de
  desvio, 1 redimensionamento nativo por sentido).
- [PENDÊNCIA] **Honestidade importante, registrada pelo próprio subagente**: a checagem "nada
  visível durante a transição" passa também no código ANTIGO (da 4ª volta) — o show/hide antigo
  era desfeito na mesma chamada Python, sem devolver controle ao laço de eventos, então nenhum
  teste headless a 4ms o enxerga. Ou seja, a suíte prova que a ORDEM mudou (não mexe mais em
  layout habilitado antes de estar seguro), mas não prova que o sintoma relatado (flash visual no
  Windows real) tinha essa causa. Se tinha, deve sumir; se não, não.
- [PENDÊNCIA] `app.log` — terceiro pedido seguido (rodadas 3, 4, 5) sem o usuário colar o conteúdo.
  PM vai pedir de novo, de forma ainda mais direta, na próxima resposta.

## 18. Consolidado

### Decisões
- Reordenação de `_aplicar_modo` feita onde possível; dois desvios do pedido original,
  justificados por medição (163px de âncora, 1px de borda QSS).
- Mantida a honestidade de não declarar nenhum dos sintomas reais (tremor, invisibilidade, largura)
  como corrigido sem confirmação do usuário.

### Pendências
- Usuário testar de novo no Windows: o botão ainda some por um instante no início/fim da
  transição? O tremor mudou mais alguma coisa?
- Colar a linha `compacto alvo=... real=...` do `app.log` — pedido 3 vezes, ainda sem resposta.
- `.git/index.lock` de 27/08 continua impedindo commit.

## 19. Correção de processo — PM devia ler o app.log direto, não pedir para o usuário colar

- [DIRECIONAMENTO] Usuário: "quem vai fazer isso é você entendeu?" — correto. O PM tem acesso ao
  arquivo via `device_bash` (`desktop/app.log`, montado em `$HOME/mnt/agentes-base`) e pediu 3 vezes
  para o usuário colar um trecho que podia ter lido sozinho o tempo todo.
- [ARTEFATO] PM leu `desktop/app.log` diretamente. Achado, na sessão de teste mais recente
  (16:33-16:37, com aberturas reais de microfone intercaladas — é o teste da 4ª volta): **20
  ocorrências seguidas de `compacto alvo=88x88 real=88x88 moldura=88x88 dpr=1.0`** — alvo, real e
  moldura batem exatamente, sem diferença nenhuma, `dpr=1.0` (sem escala aplicada nessa medição).
- [DECISÃO] **Isto refuta, com dado real, as duas hipóteses de causa levantadas nas rodadas 3-4**
  (mínimo de largura imposto pelo Windows / `SM_CXMINTRACK`; discrepância de escala DPI 88↔110). O
  próprio Qt, no Windows real, relata ter alcançado exatamente o tamanho pedido, sem sobra de
  moldura nem de escala. Se o usuário ainda vê o compacto como "péssimo" de tamanho, a causa não é
  nenhuma das duas hipóteses técnicas já registradas — é outra coisa (percepção do que 88×88 parece
  fisicamente, sombra/borda visual dando impressão de maior, monitor diferente do medido, ou algo
  ainda não identificado).
- [ARTEFATO] Achado incidental, de uma medição antiga (13:09, de rodada anterior, não da sessão mais
  recente): uma linha `tamanho_fora_do_modo expandido=True alvo=672x480 real=141x110` — a rede de
  segurança (`_corrigir_tamanho_do_modo`) realmente pegou um caso de janela presa num tamanho errado
  no mundo real, confirmando que o código de correção tem motivo de existir (não é só teórico).
- [PENDÊNCIA] Pergunta em aberto para o usuário, agora fundamentada em dado real: os 88×88 medidos
  batem com o que ele via na tela, ou o "péssimo" é sobre outra coisa (parece maior que 88px na
  prática, é sobre o tamanho expandido, ou é sobre a posição/aparência, não o tamanho em si)?

## 20. Correção de escopo — reclamação era sobre a janela expandida, não o compacto

- [DIRECIONAMENTO] Usuário: "quem vai fazer isso é você entendeu?" sobre o app.log — corrigido
  (seção 19). Depois: "coloquei o botao na tela principal", convite explícito para o PM olhar.
- [ARTEFATO] PM pediu permissão e tirou print da tela real (3 monitores, app estava no monitor
  secundário "936W" originalmente, movido para o principal a pedido do usuário). Com o mouse
  parado longe do botão, o compacto aparece exatamente como desenhado: só o círculo roxo do botão
  de gravar, sem moldura branca, sem caixa ao redor, fundo transparente até os ícones do desktop —
  **confirmado visualmente que o modo compacto está correto**, refutando de vez qualquer teoria de
  "sobra de tamanho" nele.
- [DIRECIONAMENTO] Usuário esclareceu o pedido real: não é sobre o compacto — é que a janela
  **expandida** "está com o mesmo tamanho de quando eu não tinha pedido para mexer nisso ainda"
  (672×480, nunca alterada por nenhuma das 5 rodadas, já que D-32 sempre tratou o expandido como
  "a janela cheia de hoje", intocada por design). Pedido concreto: "diminuir o tamanho do box de
  copiar para um terço do total" — PM interpretou como `self.caixa_texto` (o `QPlainTextEdit` da
  transcrição, único "box" de onde se copia texto), reduzido a ~1/3 da altura total da janela
  (480/3 ≈ 160px), encolhendo `_tamanho_expandido` proporcionalmente. Largura (672px, coluna de
  40rem, `SPEC-002` item I) mantida.
- [DECISÃO] PM despachou a 6ª rodada (subagente `opus`) com esse escopo — primeira rodada desta
  sessão que não é correção de bug, é redesenho de tamanho a pedido direto do usuário.
- [PENDÊNCIA] Confirmação de acesso: PM obteve permissão do usuário (via diálogo do sistema) para
  controlar a tela/mouse na máquina "gbueno" nesta sessão, escopada ao app Python e ao Bloco de
  notas — usado só para diagnóstico visual, nenhuma ação destrutiva.

## 21. Sexta rodada entregue — premissa errada, resultado quase imperceptível

- [ARTEFATO] Subagente mediu antes de mudar: `caixa_texto` já era 171px de 480 (35,6%) — não era o
  maior consumidor de altura como o PM (e o usuário) supunham. O que domina é o fixo: 309px (64%) —
  margens, espaçamentos, linha do botão de gravar, cronômetro, barra de amplitude, linha de
  copiar/lixeira.
- [ARTEFATO] Implementado ao pé da letra do pedido: `caixa_texto` → 160px, `_tamanho_expandido` →
  672×469 (largura mantida). Resultado: janela encolheu **11px (2,3%)** — praticamente imperceptível.
  Compacto confirmado intocado (88×88, testado). Suíte: 107 verificações, 0 falhas (91+16).
- [DECISÃO] PM registrou em `D-32`/`PLANO.md`: se o objetivo é a janela expandida visivelmente
  menor, o caminho é mexer nos elementos FIXOS, não na caixa — decisão de produto que só o usuário
  pode autorizar, com números já levantados (espaçamento, margens, linha do topo, cronômetro
  fundido, barra de amplitude → ~354px possível, ~26% menor).
- [PENDÊNCIA] Perguntar ao usuário se autoriza mexer nos elementos fixos para chegar num resultado
  visível, ou se 469px (quase igual a 480) já é aceitável.
- [PENDÊNCIA] Arquivo temporário `desktop/_medicao/medir.py`, criado pelo subagente e não
  rastreado pelo git — pedido de permissão de exclusão foi negado pelo classificador; precisa ser
  apagado manualmente pelo usuário (ou por uma próxima sessão com a permissão concedida).

## 22. Usuário rejeita a 6ª rodada e dá ordem direta — 7ª rodada despachada

- [DIRECIONAMENTO] Usuário, verbatim: "Simplesmente você não conseguiu fazer nada nessa rodada. Você
  não diminuiu horizontalmente a janela, o que eu acho absurdo você não conseguir fazer isso...
  Acabar com essa borda ao redor do botão tão grande? E outra coisa, o botão continua piscando
  quando passa o hover. Bota uma transição maior, ele não sumir, né? Porque ele tá tentando
  desaparecer também o botão vermelho." Quatro ordens diretas, sem pergunta em aberto: (1) reduzir a
  LARGURA da janela expandida (não só a altura); (2) reduzir a "borda" do compacto
  (`MARGEM_JANELA_COMPACTA`, hoje 8px); (3) transição mais longa (`DURACAO_ANIMACAO_MODO_MS`, hoje
  160ms); (4) o piscar do botão vermelho no hover/gravação, que sobreviveu às rodadas 4 e 5.
- [DECISÃO] PM revoga, só para esta janela flutuante, o vínculo com `SPEC-002` item I (coluna de
  40rem/672px) — decisão registrada em `D-32` (`spec/DECISOES.md`) e sinalizada na própria
  `SPEC-002` para não confundir sessões futuras. As outras janelas do app (configurações, consumo)
  continuam em 40rem — só a janela do botão passa a ter largura própria e menor.
- [ARTEFATO] PM leu `_definir_estado_botao` (linha ~3166): `botao_gravar.definir_estado(estado)`
  (que muda a cor E inicia o temporizador de pulso de 30ms da `CamadaPulso`) roda ANTES de
  `_aplicar_modo(True)` (a transição de modo, 160ms). Ou seja, ao começar uma gravação a partir do
  compacto, dois sistemas de animação com relógios independentes (30ms do pulso, 160/240ms da
  transição de modo) disputam repintura da mesma região da tela desde o primeiro instante — hipótese
  de causa raiz ainda não confirmada no Windows real, mas nunca antes atacada (rodadas 4-5 mexeram
  em redimensionamento nativo e ordem de layout, não neste ponto).
- [DECISÃO] PM despachou a 7ª rodada (subagente `opus`) com: largura própria menor para a janela
  flutuante; `MARGEM_JANELA_COMPACTA` menor; `DURACAO_ANIMACAO_MODO_MS` maior; adiar o início do
  temporizador de pulso até a transição de modo assentar; e aplicar de verdade os cortes nos
  elementos fixos já medidos na 6ª rodada (~354px de altura, ~26% menor).

## 23. Sétima rodada entregue — as quatro ordens implementadas e medidas

- [ARTEFATO] Largura própria da janela expandida: `LARGURA_EXPANDIDA = 448` (era 672, -33%) — piso
  medido da linha do topo = 324px; 448 escolhido medindo legibilidade real da caixa de transcrição
  (~46 caracteres/linha). Não segue mais `SPEC-002` item I (nota já na própria `SPEC-002`).
- [ARTEFATO] Altura: os seis cortes fixos medidos na 6ª rodada, agora aplicados de verdade →
  `ALTURA_EXPANDIDA = 346` (era 469, -26% desde a 6ª; -28% desde os 480 originais). Um corte (linha
  do topo 72→56) não rendeu — `QHBoxLayout` fica na altura do maior filho, e o botão de gravar
  (72px) foi preservado por instrução explícita da tarefa.
- [ARTEFATO] Compacto: `MARGEM_JANELA_COMPACTA = 4` (era 8) → 80×80 (era 88×88).
- [ARTEFATO] Transição: `DURACAO_ANIMACAO_MODO_MS = 240` (era 160).
- [ARTEFATO] Pisca-pisca do botão vermelho: `CamadaPulso` agora adia o início do temporizador de
  pulso (30ms) até a transição de modo assentar, em vez de rodar ao mesmo tempo que ela — inclui um
  sinalizador para o instante "prestes a começar" que o estado da animação sozinho não capturava.
  Cor/ícone do botão continuam mudando na hora. Testado (`[15]`): 0 quadros com o pulso ativo
  durante a transição.
- [ARTEFATO] Suíte: 143 verificações, 0 falhas (era 107, +36) — reconferido pelo PM de forma
  independente, rodando a suíte no dispositivo. Invariantes das rodadas 3-5 (0px de desvio, 1
  redimensionamento nativo por direção, 0 widgets indevidos visíveis) intactos.
- [ARTEFATO] Arquivo temporário da 6ª rodada (`desktop/_medicao/medir.py`) apagado — permissão de
  exclusão concedida desta vez. Nada de temporário ficou no repositório.
- [PENDÊNCIA] Tudo isso — aparência/sensação da janela menor, se o pisca-pisca sumiu de fato, borda
  e transição percebidas como corretas — só o usuário confirma testando no Windows real.

## 24. Usuário testou a 7ª rodada no Windows real — regressão de layout + flicker parcialmente resolvido

- [DIRECIONAMENTO] Usuário, verbatim: "você quebrou o layout e colcou o botao de cortar
  sobrepondo a caixa. a caixa ta num tamanho bom. o botao pisca quando tira o mouse de cima, mas
  consertou o primeira piscada".
- [ARTEFATO] Positivo: o tamanho da caixa de transcrição (`caixa_texto`, 160px) está bom — não
  mexer nele. O fix do pisca-pisca do botão vermelho ao começar a gravar (adiar o temporizador de
  pulso) parece ter funcionado ("consertou a primeira piscada").
- [ARTEFATO] Regressão real, confirmada por medição direta do PM (script headless instanciando
  `JanelaDitado`, sem alterar `app.py`): `ALTURA_EXPANDIDA = 346` ficou pequena demais para o
  próprio conteúdo do cartão. `cartao.minimumSizeHint()` mede 346px de altura sozinho (sem contar
  os 2×8px de `MARGEM_EXTERNA_EXPANDIDA` por fora) — a 7ª rodada esqueceu de somar essa margem
  externa ao definir `ALTURA_EXPANDIDA`. Resultado: a janela fica ~16-30px mais baixa do que o
  cartão precisa; como o layout externo usa `SetNoConstraint` (necessário para a animação), o Qt
  não recusa o tamanho pequeno demais — ele espreme o conteúdo, e a caixa de texto (que tem fator
  de esticar) fica mais baixa que seus 160px declarados, sobrepondo a linha de baixo
  (`linha_acoes`: lixeira à esquerda, botão de copiar/cortar à direita). Medido: caixa termina em
  y=288, botão de cortar/copiar começa em y=281 — 7px de sobreposição.
- [DIRECIONAMENTO] "Botão de cortar" = `self.botao_copiar`, que mostra o ícone de recortar por
  padrão (`recortar_em_vez_de_copiar` nasce ligado, `SPEC-002` F4/`D-30`) — não é um botão
  diferente, é o mesmo botão de copiar com outro rótulo/ícone.
- [PENDÊNCIA] Flicker no hover-out (mouse saindo, expandido→compacto) ainda não resolvido — é uma
  classe diferente do flicker do botão vermelho (que não tem `CamadaPulso` pulsando fora do estado
  "gravando"); é o mesmo tipo de flicker que as rodadas 4-5 atacaram (janela translúcida/nativa
  redimensionada), ainda não eliminado de vez no sentido de encolher.
- [DECISÃO] PM despachou a 8ª rodada: (1) corrigir `ALTURA_EXPANDIDA` para incluir a margem
  externa que faltou, com um teste novo que checa sobreposição de posição real entre widgets (não
  só a soma das alturas — é exatamente o tipo de teste que teria pego este bug antes de chegar ao
  usuário); (2) nova tentativa, mais cirúrgica, para o flicker no encolhimento (`setUpdatesEnabled`
  em volta do redimensionamento nativo de assentamento, para evitar um quadro intermediário sem
  repintura durante o resize da janela translúcida).

## 25. Oitava rodada entregue — sobreposição corrigida, tentativa adicional no flicker

- [ARTEFATO] `ALTURA_FIXA_EXPANDIDA` 186→202 (a conta certa soma os 16px de margem externa que a
  7ª rodada esqueceu) + `FOLGA_ALTURA_EXPANDIDA = 4` (nova constante, folga de segurança) →
  `ALTURA_EXPANDIDA = 366` (era 346). `ALTURA_CAIXA_TEXTO` (160) e `LARGURA_EXPANDIDA` (448)
  inalterados. Reconferido pelo PM: `caixa_texto` termina em y=300, linha de ações começa em y=309
  — 9px de vão, sem sobreposição.
- [ARTEFATO] Teste novo `[16]`: geometria real de todos os widgets do cartão, checagem de
  sobreposição par a par — a classe de teste que teria pego o bug da 7ª rodada. Teste `[13]`
  reescrito para exigir `altura >= mínimo do layout`, não travar um número solto.
- [ARTEFATO] Tentativa adicional no flicker de encolhimento: `setUpdatesEnabled(False)` → reflow →
  `setUpdatesEnabled(True)` → `repaint()` síncrono em volta dos dois `setGeometry` nativos
  existentes (união e assentamento). Arquitetura das rodadas 4-5 intocada. **Não confirmado no
  Windows real** — só o teste do usuário decide.
- [ARTEFATO] Suíte: 167 verificações, 0 falhas (era 143, +24) — reconferida pelo PM de forma
  independente, incluindo medição direta da geometria (sem sobreposição, 9px de vão).
- [PENDÊNCIA] Usuário testar no Windows real: sobreposição sumiu? Flicker no hover-out melhorou ou
  não? Tamanho final (448×366 expandido, 80×80 compacto) está bom?

## 26. Usuário testou a 8ª rodada no Windows real — duas frentes fechadas, o flicker não

- [DIRECIONAMENTO] Veredito do usuário sobre a 8ª rodada, rodada no Windows real (o `app.log`
  registra a abertura às 16:50 com `dpr=1.25`, `compacto alvo=80x80 real=80x80 moldura=80x80` —
  o compacto bate no alvo na máquina dele, sem mínimo assimétrico imposto pelo sistema):
  (1) **a sobreposição do botão de copiar/cortar sobre a caixa sumiu** — a correção de altura
  (`ALTURA_EXPANDIDA` 346→366) resolveu; (2) **o tamanho final está bom** — 448×366 expandido,
  80×80 compacto, transição de 240ms ficam como estão, assunto encerrado; (3) **o flicker do
  hover-out melhorou, mas continua**.
- [DECISÃO] Tamanho da janela flutuante: **fechado**. Não se reabre sem pedido novo.
- [PENDÊNCIA] Flicker no encolhimento (expandido→compacto, mouse saindo) resiste a três tentativas
  seguidas: 4ª rodada (um redimensionamento nativo por sentido, em vez de um por quadro), 5ª
  rodada (reordenação — layouts congelados antes de qualquer reconfiguração), 8ª rodada
  (`setUpdatesEnabled` + `repaint()` síncrono em volta dos redimensionamentos nativos). Cada uma
  melhorou; nenhuma eliminou.
- [DIRECIONAMENTO] Leitura do PM sobre a assimetria, feita no código antes de propor qualquer
  coisa: o único redimensionamento nativo do sentido *encolher* acontece no **fim** da transição
  (`_assentar_modo`), porque o retângulo-união do encolhimento é o próprio retângulo expandido —
  o `setGeometry` do começo é no-op. No sentido *expandir* é o contrário: o resize nativo cai no
  **começo** e o do fim é no-op. Isso casa exatamente com o sintoma relatado (pisca ao sair, não
  ao entrar) e diz onde o problema mora: **o resize nativo da janela translúcida/layered,
  isoladamente**, não o número de resizes nem a ordem das operações — que é o que as três
  tentativas anteriores atacaram.

## 27. Decisão de arquitetura — a janela para de mudar de tamanho (9ª rodada despachada)

- [DECISÃO] Usuário escolheu, entre três caminhos oferecidos pelo PM (tentativa cirúrgica nº 4,
  troca de arquitetura, ou parar e mandar para o backlog), **trocar a arquitetura**: a janela
  nativa passa a ter um tamanho só — o expandido, 448×366 — e quem cresce e encolhe na tela é uma
  **máscara** (`setMask`). Zero redimensionamento nativo e zero movimento nativo em transição.
- [DIRECIONAMENTO] Por que isto e não mais uma tentativa cirúrgica: as três anteriores atacaram
  quantos resizes existem, em que ordem as operações rodam e como o resize é publicado. A
  assimetria do sintoma (pisca ao sair, não ao entrar) aponta o resize nativo da janela
  translúcida **em si** — então a única jogada que muda de classe é não ter resize nenhum.
- [DECISÃO] Máscara **retangular** (retângulo delimitador do cartão + 1–2px de folga), não
  arredondada: `setMask` é 1 bit e serrilharia os cantos; dentro da máscara o alfa por pixel
  continua valendo, então o cartão arredondado continua suave. Custo aceito: os quatro cantinhos
  externos seguem não-clicáveis-através.
- [DECISÃO] Máscara aplicada **uma vez por transição**, no assentamento — nunca quadro a quadro
  (`SetWindowRgn` por quadro seria o mesmo erro da 3ª/4ª rodada com outro nome).
- [ARTEFATO] Eixo da mudança: `_geometria_visivel()` passa a devolver o retângulo do cartão visível
  em coordenada de tela também fora da transição — com isso hover, âncora, arrasto e a rede de
  segurança `_corrigir_tamanho_do_modo` continuam funcionando sem reescrita.
- [DECISÃO] Ganho colateral aceito de propósito: a área transparente da janela passa a ser
  clicável-através, resolvendo uma pendência antiga de produto.
- [DECISÃO] Tamanho da janela: **congelado**. Nenhum dos números aprovados muda nesta rodada; se
  mudar, é regressão.
- [PENDÊNCIA] `.git/index.lock` de 27/08 continua travando commits — as nove rodadas de hoje estão
  fora de controle de versão, e uma mudança de arquitetura sem ponto de retorno é risco novo, não
  o mesmo de antes. Usuário precisa rodar `del ".git\index.lock"` na raiz.

## 28. Nona e décima rodadas entregues — máscara no lugar de resize, e o encaixe na tela de volta

- [ARTEFATO] 9ª rodada: janela nativa `setFixedSize(448×366)`; `FOLGA_MASCARA_PX = 2` e os métodos
  `_retangulo_mascara`, `_aplicar_mascara`, `_limpar_mascara`, `_offset_do_retangulo`;
  `_geo_transicao` virou a própria janela; `_assentar_modo` guarda `_offset_visivel`/
  `_tamanho_visivel` em vez de pedir geometria ao SO; `_geometria_visivel()` passou a valer fora da
  transição também. Medido: **0 resize e 0 move nativos** por transição (era 1 resize por sentido),
  1 `clearMask` + 1 `setMask`, 0px de desvio do botão. Suíte 167 → 195.
- [DIRECIONAMENTO] O `offscreen` **nem aplica máscara** (`This plugin does not support setting
  window masks`). O efeito visual e de clique da máscara é zero em headless — a suíte prova que a
  região certa é calculada e entregue ao Qt uma vez por transição, e nada além disso. Flicker segue
  sendo confirmação de Windows real.
- [DECISÃO] PM **recusou** o efeito colateral da 9ª: sem `_encaixar_na_tela`, o botão precisaria
  ficar a 223px das laterais e 305px da base para o cartão expandido não sair da tela — que é onde
  um botão flutuante de ditado mora. Limitar o arrasto (tirar o canto da tela do usuário) foi
  descartado como pior que o problema.
- [DECISÃO] PM **revogou o próprio contrato** de "0 movimento nativo", com medição na mão: o que
  realoca a superfície da janela layered é o **redimensionamento**, não o deslocamento. Fica: 0
  resize sempre (invariante absoluto), 1 `move()` por transição **só quando o encaixe na tela
  pedir**.
- [ARTEFATO] 10ª rodada: `_geometria_do_modo` volta a encaixar, só no expandido; `_aplicar_modo`
  ganhou `destino_janela` e um `move()` condicional dentro do mesmo bloco de `setUpdatesEnabled`
  que limpa a máscara; `_geo_transicao` passa a ser medido com a janela **já movida** (com a base
  antiga o botão saltaria o deslocamento inteiro num quadro). Medido: 1 move e 0 resize colado em
  cada uma das quatro bordas, 0 move e 0 resize longe delas, deslizamento monótono. Suíte 195 →
  **230 verificações, 0 falhas** — reconferida pelo PM de forma independente.
- [DIRECIONAMENTO] `CamadaPulso` conferida a pedido do PM: não há corte no compacto. Gravar sempre
  expande antes (o pulso só liga no assentamento) e o único desenho da camada no compacto é o
  realce de arrastar arquivo (~79px dentro dos 84px da máscara).
- [PENDÊNCIA] Risco novo declarado: se o deslocamento de janela layered também piscar no Windows, o
  sintoma sobrevive **só ao expandir num canto da tela** — e é distinguível por isso.
- [PENDÊNCIA] Usuário testar no Windows real: o flicker do hover-out acabou? Hover, translucidez e
  clique-através (a área em volta do cartão agora deve deixar clicar no que está atrás)? Expandir
  colado num canto: cabe inteiro e sem salto?

## 29. Confirmado no uso real — a iteração da `D-32` fecha

- [DECISÃO] Usuário testou as rodadas 9 e 10 no Windows real em 2026-09-06: *"tá funcionando como
  deveria"*. A troca de arquitetura (máscara no lugar de resize) **resolveu o flicker** que três
  tentativas anteriores só tinham atenuado — e resolveu porque atacou a causa (o redimensionamento
  da janela layered existir), não o sintoma.
- [DIRECIONAMENTO] Lição de método, que vale além desta feature: três rodadas seguidas tentaram
  disfarçar um mecanismo (contar menos resizes, reordenar as operações, silenciar a pintura em
  volta) e cada uma melhorou sem resolver. O que fechou foi **eliminar o mecanismo**. Quando duas
  tentativas seguidas melhoram sem fechar, a pergunta certa deixa de ser "como disfarçar melhor" e
  passa a ser "dá para não ter isso".
- [DECISÃO] `D-32` encerrada como iteração. O que sobra são itens de backlog sem bloqueio:
  `.git/index.lock` de 27/08, `desktop/app.log` versionado, e o falso negativo do detector de
  pendência com duas transcrições idênticas seguidas.
- [DIRECIONAMENTO] Próximo passo do plano: **Etapa 3 da Fase 2** — histórias, entregáveis e
  definição de MVP, PM com o usuário (`D-13`), passando obrigatoriamente por
  `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` antes da primeira história.
