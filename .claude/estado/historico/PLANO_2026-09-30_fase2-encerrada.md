# PLANO — Fase 2: Desktop, ditado universal

> Plano da **fase corrente**. A visão e o mapa das nove fases estão em `spec/VISAO.md`; o método,
> em `.claude/CEREBRO.md`. Virada de plano em **2026-08-24**: a Fase 1 encerrou com todas as etapas
> concluídas (plano em `historico/PLANO_2026-08-24_fase1-encerrada.md`, progresso em
> `historico/PROGRESSO_fase1-nucleo_2026-08-23_a_2026-08-24.md`).

## Objetivo

Ditar em qualquer lugar do Windows: atalho, fala, e o texto aparece no campo em foco. É a fase que
o usuário quer usar todo dia — e é o que justifica adiar o agente (`D-24`).

## Critério de conclusão da fase

**O usuário usa o ditado deste app no dia a dia, no lugar do que usa hoje.** Não é "está pronto": é
uso em regime. A régua de qualidade é **não piorar o que ele já usa** (`D-10`).

## O que a Fase 1 deixou pendente, e que se prova aqui

A Fase 1 entregou tudo, mas o critério dela — *"alguém escreve um cliente novo lendo só o contrato,
sem abrir o `index.html` nem o `main.py`"* — só se prova com um cliente novo de verdade. **O app de
desktop da Etapa 1 é esse cliente**, e é melhor prova do que a PoC seria: é um cliente que vai ficar
em uso, não um exercício. Se o contrato não bastar, a Fase 1 volta com evidência de uso real.

## Escopo

- **Dentro**: o app de desktop mínimo (`D-25`); as histórias, os entregáveis e a definição de MVP
  (`D-13`); o app desktop para Windows com a camada de inserção **isolada** (`D-11`); atalho
  configurável como acionamento principal (`D-01`); os três estados da janela (`D-15`); e a segunda
  ação, "colocar a última transcrição no campo em foco", com atalho próprio.
- **Fora (explícito)**: Android e smartwatch (F3, F4); agente e integração com LLM (F5 em diante);
  o modo ao vivo, morto (`D-02`, `D-33`); servidor próprio (`D-05`); a inserção automática no
  campo em foco, também morta (`B-22`, `D-33`); e o seletor de idioma, desparqueado por medição
  (`D-08`).

## Etapas

> **Poucas, e é de propósito.** A regra do método é teorizar uma fase e fazer: a lista completa de
> entregáveis desta fase é a **Etapa 3**, e as etapas seguintes se escrevem depois dela. E desde
> 2026-08-25 a **Etapa 1 deixou de ser investigação e virou construção** (`D-25`) — o que o app
> precisa aprender, ele aprende sendo usado.
>
> **Regra que nasceu da reprovação de 2026-08-27:** qualquer tarefa desta fase que **desenhe
> interface** passa antes por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` e por
> `spec/specs/SPEC-002_paridade-desktop.md`. Não é só da Etapa 3.

1. **[App de desktop — paridade com a interface web]** — **CONCLUÍDA em 2026-08-27**, confirmada
   pelo usuário rodando o app: *"tá funcionando como o esperado"*. Reaberta no mesmo dia, depois de
   três reprovações; fechada depois de sete voltas de Executor.

   Foi dada por concluída com ressalvas em 26/08 e **reprovada no uso** em 27/08. O usuário rodou o
   app: *"ficou horrível. Eu consegui usar, mas ele não grava direito. Esse F17 ou F9 é uma péssima
   tecla para apertar. Você não implementou as coisas que tem no HTML aqui, que era o básico"*. A
   régua da fase é **não piorar o que ele já usa** (`D-10`) — e o que ele já usa é a interface web.
   Entregar abaixo dela não é etapa concluída com ressalva; é etapa que não cumpriu o critério.

   **Erro é meu, e é de escopo, não de execução.** Escrevi a tarefa como "atalho, gravar,
   transcrever, clipboard" **sem passar por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`**, que
   desde 21/08 dizia que a interface web é o desenho de referência do desktop e listava o que
   transcrever. O plano manda passar por esse arquivo — mas mandava só na Etapa 3, ao escrever as
   histórias. Passou a valer para **qualquer** tarefa que desenhe interface desta fase.

   **Escopo novo**: [`spec/specs/SPEC-002_paridade-desktop.md`](../../spec/specs/SPEC-002_paridade-desktop.md)
   — a frase "no mínimo o mesmo que o HTML" virada em lista conferível (A a I, aparência
   inclusa), com o que **não** transporta e o que fica para depois. É o critério de pronto desta
   etapa, e **não se entrega em partes** (`D-29`).

   **O que a primeira volta deixou de pé e não se joga fora**: `desktop/app.py` provou o caminho
   ponta a ponta contra o núcleo real, o tratamento de erro pelo campo `codigo` (não pelo texto), e
   a resposta ao critério da Fase 1 — **o contrato bastou**, com uma lacuna só (não declarava onde o
   núcleo escuta), fechada em `spec/contrato/NUCLEO.md` em 26/08. Duas transcrições reais saíram do
   app em 27/08 às 04:25. O caminho funciona; a interface é que ficou abaixo da régua.

   **O que foi entregue**: `desktop/app.py`, 2.323 linhas em PySide6 — janela sempre no topo sem
   roubar foco, atalho global configurável que alterna, gravação com estado visível, caixa que
   acumula com desfazer por snapshot, copiar/recortar, menu ⋮ com Configurações · Consumo · Enviar
   arquivo, painel de consumo com as duas escalas da linha do tempo, arrastar e soltar áudio, e a
   identidade visual conferida contra a interface web. A dívida do `D-11` (clipboard inline) foi
   paga na segunda volta.

   **Cinco divergências deliberadas** em relação à interface web, todas declaradas na `D-30`: corte
   de 5 min, recortar como padrão, balão acima do botão, consumo em janela própria, fundo dos
   botões-ícone mais leve. A web não mudou em nenhuma.

   **Fica pendente, pequeno e conhecido** — não segura a etapa, entra quando incomodar:

   1. o véu escuro dos painéis sobrepostos não pinta — falta `WA_StyledBackground` no
      `OverlayModal`, e o comentário duas linhas abaixo, no mesmo construtor, já explica essa regra;
   2. ativar um ponto da linha do tempo pelo teclado (`SPEC-002` G4) — foco no widget, ←/→ entre
      pontos, contorno de 2 px em `#2563eb`, `Enter`/`Espaço` abrindo a requisição;
   3. `config.json` gera diferença fantasma no git — o app grava CRLF, o versionado é LF, e falta a
      quebra de linha final. Conserto: gravar com `\n`, criar `.gitattributes` com `*.json text
      eol=lf`, e normalizar **preservando** o que o usuário configurou.

   Estavam na `PROXIMA_TAREFA.md` até 2026-08-27, quando ela foi substituída pela `D-31` (gerar
   imagem, pedido urgente do usuário). **Moram aqui até serem chamados** — nenhum se perdeu.

   **O critério da FASE continua aberto**, e é outro: *"o usuário usa o ditado deste app no dia a
   dia, no lugar do que usa hoje"*. Isso é uso em regime, e se mede em dias — não em uma sessão.

2. **[POC-1 — investigação de inserção]** — **interrompida por achado, e o achado vale mais que a
   matriz.** Executada parcialmente em 2026-08-25, antes do corte de escopo. Quatro tentativas de
   injeção falharam **em silêncio**; a causa foi isolada e virou **`D-26`**: a inserção tem de
   disparar de dentro do handler do atalho global, senão o Windows não entrega. A matriz 4×3 ficou
   em branco não por omissão, mas porque repeti-la do jeito antigo só reproduziria o mesmo falso
   negativo. Todo o material está em `spec/pocs/POC-1/` e o que se aprendeu está em `B-22`.

3. **[Histórias, entregáveis e MVP]** — PM com o usuário, não Executor (`D-13`). Escrever as
   histórias de usuário, a lista de entregáveis da fase e a definição declarada de MVP. Fecha as
   lacunas `L-A`, `L-B` e `L-C`.
   — **Obrigatório**: passar por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` antes de escrever a
   primeira história. Ele já traz três coisas decididas para esta fase — a interface web como
   desenho de referência (transcrever, não reinventar), a ação "colocar a última transcrição" com
   atalho próprio e inserção a partir da memória do app (nunca da área de transferência), e o que
   **não** se transporta: hover como gatilho, o modo ao vivo e a inserção automática no campo em
   foco — os dois últimos saíram de vez, não é mais "adiado" (`D-33`, 2026-09-05).
   — Pode começar em paralelo à Etapa 1, mas **a parte que depende do mecanismo de inserção só
   fecha depois dela**.

4. **[Escrever o resto do plano]** — PM. Com o app mínimo **em uso** e o MVP definido, as etapas
   seguintes se escrevem com base no que o uso mostrou — inclusive se a inserção automática (`B-22`)
   volta do backlog.
   — Critério de pronto: um plano de fase com etapas verificáveis, aprovado pelo usuário.

## Anexo fora do plano — geração de imagem (`D-31`)

Entrou em **2026-08-27**, a pedido direto do usuário, que precisava gerar imagens naquele momento.
**Não é etapa desta fase e não entra no critério de conclusão dela**: a F2 é ditado universal, e
imagem não é ditado. Está aqui para ficar visível, não para ser confundido com o plano.

O que muda de fato: o núcleo ganha `POST /gerar-imagem` e **deixa de ser só de transcrição**; o custo
por chamada é ~140× o de uma transcrição, o que aciona a condição de reabertura do alarme da `D-18`.
Se o recurso pegar, a pergunta seguinte é se ele ainda deve morar num app de ditado — provavelmente
vira um segundo cliente do mesmo núcleo, que é o desenho que a `D-07` já previa.

## Anexo fora do plano — botão flutuante compacto (`D-32`)

Entrou em **2026-09-05**, a pedido direto do usuário. **Não é etapa desta fase e não entra no
critério de conclusão dela** (mesma lógica da `D-31`) — mas ao contrário da geração de imagem, isto
**já estava listado** na `SPEC-002` como "além da paridade... vira etapa própria, aos poucos": é a
`D-15` (três estados da janela, decidida em 21/08) finalmente construída.

O app passa a nascer compacto — só o botão de gravar — e expande para a janela cheia no hover ou ao
entrar em gravando/processando; encolhe de volta só depois de o texto ter sido colocado **e** o
mouse ter saído. Detalhe completo em `D-32`, que também reconcilia isto com o item J1 da `SPEC-002`
("a janela nunca muda de tamanho sozinha") — são coisas diferentes, e a `SPEC-002` já foi atualizada
com a nota.

**Consequência de escopo, quando a Etapa 3 escrever a lista de entregáveis da fase:** este item já
não é mais só uma linha de backlog — está em construção. Ele passa a fazer parte do que o MVP da F2
inclui, mesmo que a etapa formal ainda não tenha sido escrita.

**Primeira volta entregue em 2026-09-05, por subagente Executor — não confirmada no uso real.**
Implementado em `desktop/app.py` (`JanelaDitado._aplicar_modo`, vigia de cursor a 100ms em vez de
`enterEvent`/`leaveEvent`, debounce de 250ms, âncora pelo centro do `BotaoGravar`). 47 verificações
headless (`QT_QPA_PLATFORM=offscreen`) passaram, incluindo o fluxo de ditado ponta a ponta contra um
núcleo falso local. **Nada disso substitui rodar no Windows de verdade** — nenhuma chamada real ao
microfone nem à OpenAI foi feita.

Pendências abertas, na ordem em que importam:

1. **`.git/index.lock` (resíduo de 27/08) segue impedindo commit** — não é desta tarefa, mas trava
   qualquer commit futuro. O usuário precisa apagar na máquina: `del ".git\index.lock"` na raiz do
   repositório.
2. **Risco de precedente conhecido**: o modo compacto depende de `WA_TranslucentBackground` — a
   mesma classe de bug já vista neste projeto (`CamadaPulso`, 27/08: transparência que funciona no
   `offscreen` e aparece como caixa opaca no Windows real). É o primeiro teste que vale fazer.
3. **Sumiu a forma de fechar o app.** Sem moldura, foi embora o botão nativo de fechar; só sobra
   `Alt+F4` (não confirmado), e o menu ⋮ não tem "Sair". Não é regressão desta tarefa ter deixado de
   cobrir — é lacuna nova que a mudança abriu. Precisa de tarefa própria antes de considerar isto
   pronto para uso diário.
4. Duas leituras que o Executor teve de decidir sozinho, pendentes de aval do PM: (a) "encolhe" só
   quando não há resultado pendente ainda não colocado — janela vazia encolhe normalmente; (b) painel
   ou menu aberto (Configurações/Consumo/Gerar imagem) trava o encolhimento, para não fechar por
   baixo do usuário. Ambas aceitas nesta sessão de PM.

Detalhe completo do que foi testado e como está em `.claude/estado/PROGRESSO.md`, entrada de
2026-09-05.

**Segunda rodada, mesmo dia, depois de rodar no Windows de verdade**: usuário reportou o compacto
grande demais (deve abraçar o botão, não 110×110), um **bug** — parou de encolher depois do primeiro
ciclo — e pediu transição animada em vez de resize instantâneo. Detalhe em `D-32` (nota "refinada em
2026-09-05, segunda rodada"). Nova tarefa em `PROXIMA_TAREFA.md`, prioridade no bug.

**Segunda rodada entregue no mesmo dia**: bug corrigido na raiz (o sinalizador de "resultado
pendente" virou função derivada, não booleano manual — classe inteira de causas eliminada, não só o
caminho relatado). Compacto agora mede 88×88 contra o `BotaoGravar` real, em vez de valor fixo.
Transição animada (160ms, `InOutCubic`), com correção de um desvio de âncora de 39px perto do topo
da tela. Suíte de regressão nova, versionada, em `desktop/testes_janela_compacta.py`.

**Ainda só confirmável no Windows real**: suavidade percebida da animação, hover, sempre-no-topo,
translucidez, microfone e núcleo real — nenhum teste headless substitui isso.

**Achado pequeno, sem urgência**: duas transcrições idênticas seguidas seriam lidas como "já
colocada" (falso negativo do detector de pendência) — vira item de backlog, não bloqueia nada.

**Terceira rodada, mesmo dia**: o botão pulando na animação tinha causa provada (recorte pelo
próprio limite da janela durante o reflow por quadro) — corrigido trocando a arquitetura da
animação (janela inteira interpolada, layouts congelados, 0px de desvio medido). "Sair" adicionado
ao menu ⋮. **A largura do compacto não foi reproduzida em headless** — hipótese forte registrada em
`D-32` (mínimo de janela não propagado pelo plugin offscreen; no Windows o sistema pode impor um
mínimo assimétrico), com log de diagnóstico novo para a próxima execução real confirmar. Pendente:
usuário rodar de novo e olhar `app.log`; decidir se o percurso de 252–359px do botão perto do canto
onde a janela nasce incomoda (é geometria do ponto de abertura, não bug).

**Quarta rodada, mesmo dia**: usuário relatou de novo (depois da 3ª volta): compacto ainda abre alto
e largo demais (agora nos dois eixos), e o botão "pisca" — tremor parado durante a transição, sintoma
diferente do "pula de posição" já corrigido. PM leu o código antes de despachar: refutou a hipótese
de corrida com o vigia de ponteiro (o `_expandido` já troca antes da animação começar) e formou nova
hipótese — a janela é translúcida/layered no Windows (`WA_TranslucentBackground` +
`FramelessWindowHint`), e a animação ainda redimensionava a janela **nativa** a cada quadro (~11
vezes em 160ms), fonte conhecida de flicker nesse tipo de janela no Windows, invisível ao headless.
Corrigido: a janela nativa agora só muda de tamanho 2 vezes por transição (união dos extremos no
início, tamanho final no fim); cartão e botão continuam interpolados dentro dela. Medido: 1
redimensionamento nativo por sentido (era 12), 0px de desvio do botão. **Não é confirmação — é
mudança de causa suspeita**: só o Windows real decide se o tremor sumiu; o `app.log` continua sendo
a prova que falta para a largura/altura.

**Quinta rodada, mesmo dia**: usuário testou a 4ª volta — tremor "melhorou, mas não sumiu"; achou
sintoma mais preciso, o botão fica invisível por um instante bem no início/fim da transição (hover
entrando ou saindo), não no meio. PM achou causa por leitura de código: dois blocos em
`_aplicar_modo` (mudar margens/estilo do cartão, mostrar/esconder conteúdo só-expandido) rodavam
antes de os layouts serem desabilitados e antes do redimensionamento nativo para a união da 4ª
volta — ao vivo, na janela ainda do tamanho antigo. Corrigido: reordenado para os layouts serem
desabilitados e a janela crescer para a união primeiro. Um ajuste em relação ao pedido original, por
medição: apagar puro e simples o show/hide quebraria a âncora (163px de diferença conforme
visibilidade do conteúdo) — a garantia foi para dentro do método de medição do centro do botão.
Suíte: 91 verificações (76+15), 0 falhas, sem regressão da 4ª volta. **Honestidade registrada**: a
checagem "nada visível durante a transição" passa também no código antigo (headless não enxerga o
instante) — só o Windows real confirma se o "some por um instante" acabou. `app.log` continua sem
ser colado pelo usuário, em 3 pedidos seguidos.

## Backlog

O acervo de ideias mora em [`spec/BACKLOG.md`](../../spec/BACKLOG.md). **Ao fechar cada etapa desta
fase**, ler os itens marcados com `olhar de novo em: F2` e perguntar ao usuário quais sobem. Hoje
são: `B-05` (adiantamento de exibição no streaming), `B-06` (consolidar as três histórias de entrega
do texto) e `B-11` (histórico por projeto). `B-01` (arrastar e soltar) **subiu em 2026-08-27**, a
pedido do usuário, e virou o item `E2` da `SPEC-002`.

## Nota de processo (deste projeto)

- **Armadilha da porta 8000: 6 ocorrências.** Confira e derrube backend antigo antes de qualquer
  medição. A última foi em 2026-08-24, o Executor pegou.
- **Tarefa que quebre o `.env` ou o backend avisa o usuário ANTES de começar** — ele usa o app ao
  vivo. Funcionou na Etapa 3 da Fase 1.
- **Microfone real já foi exercitado** em 2026-08-27: duas transcrições de fala saíram do app de
  desktop às 04:25 (US$ 0,0003 no total). A cadeia inteira — microfone, envio, transcrição, texto de
  volta — funciona. O que reprovou foi a interface, não o caminho.
- Preços de referência consultados em 2026-08-19 (conferir antes de decisão de custo):
  `gpt-transcribe` US$ 0,0045/min; `gpt-live-transcribe` US$ 0,017/min. O limite de 25 MB de áudio
  foi conferido na documentação da OpenAI em 2026-08-24.
- As regras de método — consistência, higiene, tipos de plano, commit — moram em `.claude/metodo/`.
  Não repita nenhuma aqui.

**Sexta rodada, mesmo dia — escopo novo**: PM confirmou por print real que o compacto está correto;
usuário esclareceu que a reclamação era sobre a janela EXPANDIDA (672×480, nunca tocada pelas 5
rodadas anteriores), pedindo para reduzir a caixa de transcrição a 1/3 do total. Medido antes de
mudar: a caixa já era 35,6% da altura (171 de 480px) — não era o maior consumidor, o fixo (margens,
espaçamentos, linha do botão, cronômetro, barra de amplitude, linha de copiar) é 64%. Implementado
ao pé da letra: janela só encolheu 11px (480→469, 2,3%) — pendência registrada em `D-32`: decisão do
usuário se quer autorizar mexer nos elementos fixos para um resultado visível (~354px possível,
~26% menor, números já levantados pelo Executor).

**Sétima rodada, mesmo dia — usuário rejeita a 6ª e dá ordem direta**: "não conseguiu fazer nada
nessa rodada... diminuir horizontalmente a janela... acabar com essa borda ao redor do botão...
botão continua piscando no hover... bota uma transição maior". PM revoga, só para esta janela
flutuante, o vínculo com `SPEC-002` item I (40rem/672px) — as outras janelas do app continuam com
40rem. Despachada a 7ª rodada: largura menor (própria desta janela), `MARGEM_JANELA_COMPACTA`
menor, `DURACAO_ANIMACAO_MODO_MS` maior, aplicação real dos cortes nos elementos fixos já medidos na
6ª (~354px de altura), e uma tentativa de causa raiz para o pisca-pisca do botão vermelho: em
`_definir_estado_botao`, o estado/cor do botão (e o temporizador de pulso de 30ms da `CamadaPulso`)
começa ANTES da transição de modo (`_aplicar_modo`) — dois relógios de animação não sincronizados
disputando repintura da mesma região ao mesmo tempo, nunca atacado nas rodadas 4-5. Ver `D-32`
(`spec/DECISOES.md`) para o texto completo.

**Sétima rodada entregue, mesmo dia**: as quatro ordens do usuário implementadas e medidas — janela
expandida 672×469 → 448×346 (largura própria, não segue mais `SPEC-002` item I; altura com os seis
cortes fixos da 6ª rodada agora realmente aplicados); compacto 88×88 → 80×80
(`MARGEM_JANELA_COMPACTA` 8→4); transição 160→240ms; e uma correção de causa raiz para o pisca-pisca
do botão vermelho (temporizador de pulso da `CamadaPulso` adiado até a transição de modo assentar,
em vez de rodar concorrente com ela). Suíte: 143 verificações, 0 falhas (reconferido pelo PM). Nada
disso está confirmado no Windows real ainda — ver `D-32` (`spec/DECISOES.md`) para os números
completos e o que ainda depende do usuário testar.

**Oitava rodada, mesmo dia**: usuário testou a 7ª no Windows real — achou uma regressão real (botão
de copiar/cortar sobrepondo a caixa de transcrição, causada por `ALTURA_EXPANDIDA` ter esquecido de
somar a margem externa da janela) e reportou melhora parcial no pisca-pisca do botão vermelho
(sumiu ao começar a gravar, mas continua ao tirar o mouse de cima/encolher). Despachada a 8ª rodada:
correção da altura com teste de sobreposição de geometria real, e tentativa adicional
(`setUpdatesEnabled`/`repaint()`) para o flicker do encolhimento. Ver `D-32` (`spec/DECISOES.md`).

**Oitava rodada entregue, mesmo dia**: regressão da 7ª corrigida — `ALTURA_EXPANDIDA` 346→366
(faltavam os 16px de margem externa + 4px de folga), sem tocar `ALTURA_CAIXA_TEXTO`/`LARGURA_EXPANDIDA`;
sobreposição confirmada eliminada (9px de vão, reconferido pelo PM). Teste novo de geometria real
(não só soma de números) para pegar esta classe de bug no futuro. Tentativa adicional para o
flicker de encolhimento (`setUpdatesEnabled`/`repaint()` em volta dos resizes nativos existentes,
sem mudar a arquitetura das rodadas 4-5) — não confirmada no Windows real. Suíte: 167 verificações,
0 falhas. Ver `D-32` (`spec/DECISOES.md`) para os números completos.

**Veredito do usuário sobre a 8ª rodada, no Windows real (2026-09-05)**: a sobreposição do botão de
copiar/cortar sobre a caixa **sumiu**; o tamanho final (448×366 expandido, 80×80 compacto, transição
de 240ms) **está aprovado e fechado** — não se reabre sem pedido novo; o flicker do hover-out
**melhorou, mas continua**. O `app.log` confirma a execução real às 16:50 (`dpr=1.25`, compacto
80×80 exato). Sobra uma frente só nesta iteração da `D-32`, e é a que resiste a três tentativas
(rodadas 4, 5 e 8). Leitura nova do PM, feita no código: no sentido *encolher* o único
redimensionamento nativo cai no **fim** da transição (a união é o próprio retângulo expandido); no
sentido *expandir*, no **começo**. Isso casa com o sintoma (pisca ao sair, não ao entrar) e aponta o
resize nativo da janela translúcida **em si** como causa — não o número deles nem a ordem das
operações em volta, que foi o que as três tentativas atacaram. Decisão de caminho pendente com o
usuário: mais uma tentativa cirúrgica, mudar a arquitetura (máscara no lugar de redimensionar, que
também resolveria a área transparente não clicável-através), ou mandar o flicker para o backlog e
voltar ao plano da fase (Etapa 3).

**Nona rodada despachada, mesmo dia — troca de arquitetura**: escolhida pelo usuário entre três
caminhos. A janela nativa passa a ter um tamanho só (o expandido, 448×366) e quem cresce e encolhe
na tela vira a máscara (`setMask`, retangular, aplicada uma vez por transição) — zero
redimensionamento e zero movimento nativo em transição, que é a única jogada que muda de classe
depois de três tentativas de disfarçar o resize. Ganho colateral aceito: a área transparente passa
a ser clicável-através, pendência antiga. Tarefa completa em `PROXIMA_TAREFA.md`.

**Nona e décima rodadas entregues, 2026-09-05/06 — a janela parou de mudar de tamanho**: a janela
nativa virou `setFixedSize(448×366)` e quem cresce e encolhe na tela é a máscara (`clearMask` no
começo da transição, `setMask` no assentamento; retângulo do cartão + `FOLGA_MASCARA_PX = 2`).
`_geometria_visivel()` virou o eixo — hover, âncora, arrasto e a rede de segurança passaram a
perguntar a ele. Medido e reconferido pelo PM: **0 redimensionamento nativo** por transição (era 1
por sentido), 0px de desvio do centro do botão, suíte 167 → 230 verificações, 0 falhas.

A 9ª rodada deixou um efeito colateral que o PM mediu e **recusou**: sem encaixe na tela, o botão
precisaria ficar a 223px das laterais e 305px da base para o expandido não sair da tela — que é
justamente onde um botão flutuante mora. Daí a 10ª: o contrato "0 movimento nativo" foi **revogado
pelo PM** (o que realoca a superfície da janela layered é o *resize*, não o *move*), e o encaixe
voltou com **um `move()` por transição, só quando necessário** — 0 longe das bordas, 1 colado em
qualquer das quatro. Perto da borda o botão desliza, comportamento antigo e já aceito.

**Risco novo, declarado**: se no Windows o deslocamento de janela layered também piscar, o sintoma
sobrevive **só** ao expandir num canto da tela — e é distinguível justamente por isso.

**Confirmado no Windows real em 2026-09-06** — usuário, depois de testar as rodadas 9 e 10: *"tá
funcionando como deveria"*. **A iteração da `D-32` fecha aqui**: a janela flutuante compacta está
em uso, com a arquitetura de máscara (0 redimensionamento nativo) e o encaixe na tela por `move()`
condicional. O que sobrou não é desta frente: `.git/index.lock` de 27/08 travando commits,
`desktop/app.log` versionado e crescendo, e o achado pequeno das duas transcrições idênticas
seguidas (falso negativo do detector de pendência) — todos itens de backlog, nenhum bloqueia nada.

**Etapa 3 aberta na sequência** (histórias, entregáveis e MVP — PM com o usuário, `D-13`).

## Etapa 3 — CONCLUÍDA em 2026-09-06

Histórias, entregáveis e MVP escritos pelo PM com o usuário (`D-13`), depois de passar por
`spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`, como este plano obriga.

- **`spec/historias/F2_ditado-universal.md`** — `US-D01` a `US-D07`, reaproveitando os
  identificadores do pré-projeto. Fecha `L-A`.
- **`spec/F2_MVP_E_ENTREGAVEIS.md`** — sete entregáveis (seis entregues, o sétimo é o uso em regime)
  e o MVP declarado, com a lista do que fica **fora** dele. Fecha `L-B` e `L-C`.
- **`D-34`** — o MVP da F2 é o app que já está em uso. Saiu de pergunta direta ao usuário sobre o
  atrito do uso real: *"nada, o fluxo já serve"*. A mesma conversa adiou o histórico (`B-11`).
- **`B-06` fechado** dentro da `US-D02`: a escada de entrega do texto ficou com dois degraus, não
  três — o primeiro morreu na `D-33`.

> **Exceção pontual ao papel de PM, autorizada pelo usuário em 2026-09-06** (regra do `PM.md`:
> exceção precisa ser explícita, datada e registrada no plano e na coleta): o PM redigiu ele mesmo
> os artefatos em `spec/` desta etapa — histórias, entregáveis e MVP — em vez de passar como tarefa
> ao Executor. Vale para esta etapa, não vira regra.

**Consequência de escopo, e é grande**: com o MVP declarado assim, **não há funcionalidade entre o
app de hoje e o fim da Fase 2**. O critério de conclusão fica sozinho — uso em regime — e a Etapa 4
deixa de ser "escrever as etapas que faltam" para ser "colher o que o uso mostrar".

## Etapa 4 — aberta, e depende de dias de uso, não de trabalho

Critério de pronto (inalterado): um plano de fase com etapas verificáveis, aprovado pelo usuário —
**ou** a constatação registrada de que não faltam etapas, e a fase encerra pelo critério de uso.

O que alimenta esta etapa: incômodos que aparecerem ditando (que é o que a `D-34` diz esperar), os
itens de backlog marcados para depois, e a pergunta aberta da `D-31` (se a geração de imagem ainda
deve morar num app de ditado).

## Anexo fora do plano — atalho no Menu Iniciar para abrir o transcritor (2026-09-28)

**Exceção de PM, autorizada explicitamente pelo usuário em 2026-09-28** (escolheu "Exceção: PM faz
aqui" em vez de passar a tarefa ao Executor). Motivo: o app fecha e, sem o chat que costumava
abri-lo (limite de uso atingido), o usuário ficou sem o transcritor. Vale para este atalho, não vira
regra.

Entregue em `desktop/`: `abrir_transcritor.vbs` (sobe o núcleo na porta 8000 se não estiver no ar,
espera até 30 s, e abre `app.py` se ainda não estiver aberto — tudo sem janela de terminal) e
`criar_atalho_menu_iniciar.cmd` + `.ps1` (cria o atalho "Transcritor" no Menu Iniciar; roda uma
vez). Não muda o critério da fase nem o MVP (`D-34`). Opções oferecidas e **não** escolhidas:
abrir ao ligar o PC, reabrir sozinho se fechar, ícone na Área de Trabalho.
