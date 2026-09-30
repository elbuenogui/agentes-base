# Coleta — Fase 2: Etapa 1 reprovada no uso, reaberta com spec de paridade (2026-08-27)

Chat de PM que recebeu o veredito do usuário sobre o app de desktop, achou a causa do escopo errado,
transformou "no mínimo o mesmo que o HTML" em lista conferível e gerou a tarefa nova.

## 1. Registro por interação

- [VEREDITO] O usuário rodou o app: *"ficou horrível. Eu consegui usar, mas ele não grava direito.
  Esse F17 ou F9 é uma péssima tecla para apertar. Você não implementou as coisas que tem no HTML
  aqui, que era o básico para implementar… eu preferiria que fosse, no mínimo, a mesma coisa que o
  HTML. No mínimo. Qualquer coisa mais além disso, a gente implementa aos poucos."*
- [ERRO DO PM] O escopo da tarefa — "atalho, gravar, transcrever, clipboard" — foi escrito por mim
  sem passar por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`, que desde 21/08 dizia o contrário,
  com as palavras do próprio usuário. **Eu tinha lido esse arquivo na mesma sessão.** Registrado em
  memória como padrão novo (`feedback_escopo_sem_ler_decidido.md`).
- [CAUSA ESTRUTURAL] O `PLANO.md` mandava passar pelo arquivo de comportamentos parqueados — mas só
  na **Etapa 3** (histórias). A tarefa que desenhou interface era a **Etapa 1**. Obrigação amarrada
  a uma etapa não protege as outras. Corrigido no plano: vale para qualquer tarefa da fase que
  desenhe interface.
- [DECISÃO] A Etapa 1 **não foi concluída com ressalva — foi reprovada**. A régua da fase é não
  piorar o que o usuário já usa (`D-10`), e o que ele já usa é a interface web. Etapa reaberta em
  vez de aberta uma nova: renumerar quebraria as citações do PROGRESSO, e o fato honesto é que o
  critério não foi cumprido.
- [ARTEFATO] `spec/specs/SPEC-002_paridade-desktop.md` — a frase virada em lista conferível, itens
  **A a H**, com dono único declarado (`index.html` é dono do comportamento; a spec não descreve
  implementação), os números já calibrados na interface web, o que **não** transporta (hover, modo
  ao vivo) e o que fica para depois (atalho, janela flutuante, inserção no campo em foco). Uma frase
  num rascunho depende de alguém lembrar; uma lista com checkbox, não.
- [BIFURCAÇÃO LEVADA AO USUÁRIO] Embutir a interface web numa janela nativa daria paridade no
  primeiro dia, mas reverteria o que ele disse em 21/08 — não decidi sozinho. **Resposta:
  reescrever em Python, e a janela sempre sobreposta a qualquer outra.** Virou `D-27`, que também
  **fecha a `D-06`** (linguagem do desktop: Python, porque a `D-26` exige disparo de dentro do
  handler do atalho).
- [CONSEQUÊNCIA TÉCNICA REGISTRADA] "Sempre no topo" só serve se a janela **não roubar o foco** ao
  aparecer — é a `D-01` e a `D-15` vistas de novo. Virou requisito bloqueante na tarefa: se as duas
  coisas não derem juntas, o Executor para e a `D-27` reabre.
- [DECISÃO] `D-28` — gravar **alterna** (um toque começa, outro para), e o atalho se configura
  **pela interface**, não editando JSON. Segurar a tecla foi invenção da primeira volta; a interface
  web sempre alternou. E escolher outra tecla por ele seria o mesmo erro em outra tecla.
- [ARTEFATO] `PROXIMA_TAREFA.md` — parte 1 de duas: o fluxo de ditado inteiro (A, B, C, D, F, H +
  menu só com Configurações). Consumo e Enviar arquivo ficam para a parte 2. Inclui a dívida da
  volta anterior: `pyperclip.copy` inline vira função isolada (`D-11`), e `pyperclip` sai — o
  clipboard do Qt basta.

## 2. Trade-offs aceitos

- **Reescrever em vez de embutir**: custa várias voltas de Executor e assume o risco de a interface
  ficar aquém da web por um tempo. Em troca, o desktop não fica acoplado ao `index.html`, e as
  divergências que a fase já tem previstas (janela flutuante, três estados, inserção no campo em
  foco) não viram `if` dentro de um arquivo que tem outro dono.
- **PySide6 em vez de Tk**: dependência pesada, aceita porque a lista de paridade tem modais, ícones,
  faixa animada e balão efêmero — e "pior do que o que ele já usa" é exatamente o que a `D-10` proíbe.
- **Log de diagnóstico em `desktop/app.log`**: três eventos só (abertura, descarte por silêncio com
  o pico medido, `codigo` de erro). Aceito para que "não grava direito" não possa voltar sem
  evidência — e limitado a três para não virar histórico paralelo ao do núcleo.

## 3. O que fica pendente

- O usuário ainda **não disse qual tecla** quer. Padrão de fábrica `ctrl+alt+space` na tarefa, e a
  troca passa a ser dele, pela interface — a decisão sai das minhas mãos de propósito.
- **Parte 2** da paridade (Consumo com linha do tempo, Enviar arquivo) só se escreve quando a parte
  1 estiver em uso.
- Dois arquivos das edições anteriores seguem sem commit: `.claude/metodo/HIGIENE.md` e
  `coleta/2026-08-24_fase2-poc1.md`.

---

## 4. Segunda reprovação no mesmo dia — a lista existia, e eu a parti

- [VEREDITO] O Executor entregou a parte 1 inteira e correta (918 linhas, PySide6, A–D + F + H +
  atalho alternando + clipboard isolado). Mesmo assim: *"não foi implementada a lógica do consumo,
  não foram implementadas as funcionalidades que tinha nos três pontos, o layout também não está
  igual. Então ainda estamos longe do mínimo."*
- [ERRO DO PM, segunda vez] **O erro sobreviveu ao conserto do erro.** A `SPEC-002` nasceu de manhã
  justamente para o escopo não ficar abaixo do piso — e à tarde eu a usei como cardápio, escrevendo
  "parte 1 de duas" e mandando Consumo e Enviar arquivo para depois.
- [O QUE EU TINHA LIDO ERRADO] Ele disse as duas coisas na mesma frase: *"no mínimo a mesma coisa
  que o HTML. No mínimo. Qualquer coisa mais além disso, a gente implementa aos poucos."* Fatiar vale
  para o que vem **além** do piso. Eu li só a segunda metade. Virou `D-29`.
- [ARTEFATO] **Seção I da `SPEC-002` — identidade visual**: paleta, medidas e geometria extraídas do
  CSS do `index.html`, declaradas como **extrato derivado com data** (se divergir do CSS, o CSS
  vence). "O layout não está igual" também precisava virar número conferível.
- [MUDANÇA DE MÉTODO] A conferência de aparência passou a ser **do Executor, não do usuário**:
  renderizar a janela fora da tela (`QT_QPA_PLATFORM=offscreen` + `grab()`) nos três estados,
  capturar as telas equivalentes do `index.html` no Chromium, comparar as duas e **listar no
  PROGRESSO as divergências achadas e corrigidas**. Antes, quem via a divergência era o usuário
  abrindo o app — que é o mais caro dos conferidores possíveis.
- [DÍVIDA DECLARADA] Os ícones viraram exigência. O Executor tinha optado conscientemente por uma
  "cápsula arredondada simples" no lugar do microfone, com a justificativa correta de que a spec não
  pedia fidelidade visual. Agora pede — e os caminhos SVG do `index.html` renderizam com `QtSvg`,
  que já vem no PySide6.
- [PENDÊNCIA HERDADA] `F3` (troca de dispositivo) e `H1/H2` (`Esc` e clique fora) foram entregues
  implementados e não exercidos. Entraram no critério da tarefa nova em vez de virarem pergunta ao
  usuário.

## 5. Trade-off da tarefa nova

Uma tarefa só, grande, em vez de duas — e a linha do tempo do consumo é a parte cara. Aceito com uma
válvula escrita na tarefa: se algum controle da linha do tempo não couber, o Executor **para e avisa
antes**, com o motivo. O que não pode voltar a acontecer é o usuário descobrir a falta abrindo o app.

---

## 6. Paridade entregue, e o primeiro acabamento vindo do uso

- [MARCO] A terceira volta entregou a paridade inteira e o usuário passou a **usar o app**. Os
  pedidos mudaram de natureza: não são mais "falta o que o HTML tem", são ajustes que só aparecem
  quando alguém dita de verdade.
- [DECISÃO] **`D-30` — o desktop pode divergir da web, e toda divergência é declarada na spec.** A
  paridade vira piso, não teto. Sem essa regra, a próxima conferência de aparência acharia as
  diferenças e as trataria como falha de transcrição do desenho — e alguém "consertaria" de volta.
- [DIVERGÊNCIA 1] **Corte de segurança: 2min30 → 5min** no desktop; a web fica em 2min30. É no
  desktop que se dita de verdade, e o corte pegava fala no meio. 5 min a 16 kHz mono são ~9,6 MB,
  longe do limite de 25 MB do núcleo.
- [DIVERGÊNCIA 2] **Recortar vira o padrão** no desktop; a web nasce em copiar. O texto ditado vai
  embora para outro aplicativo e não volta — deixar o anterior na caixa faz a gravação seguinte
  empilhar em cima de lixo. O desfazer (`C4`) continua cobrindo o arrependimento.
- [ACHADO DE APARÊNCIA 1] Os três controles ficaram **espalhados** na barra (dois `addStretch(1)`
  jogando o ⋮ para uma ponta e o cancelar para a outra), quando na web são um **trio encostado no
  meio** com 0,6rem de vão. A seção I falava em "grade de três colunas" e em "o botão não se move" —
  descrevia o mecanismo e não o resultado, e o mecanismo foi cumprido com o resultado errado.
  Reescrita para dizer as duas coisas.
- [ACHADO DE APARÊNCIA 2] *"Os switches não estão bons. Isso não é switch de verdade."* O
  `QCheckBox::indicator` do Qt, estilizado por QSS, dá um retângulo arredondado que **troca de cor**
  — sem a bolinha branca deslizando não existe posição ligado/desligado, só duas cores para decorar.
  Virou parágrafo próprio na seção I, com as medidas e a animação.
- [PADRÃO QUE SE REPETE] Os dois achados são do mesmo tipo: **a spec descreveu o meio e não o fim**.
  "Grade de três colunas" e "trilho e bolinha" eram instruções de implementação; o que faltava era
  dizer o que a pessoa tem de ver. Onde a spec disser como fazer, ela precisa dizer antes o que se
  reconhece na tela.

---

## 7. Segunda rodada de acabamento — e a primeira falha de arquitetura de interface

- [ACHADO, causa única para vários sintomas] *"O botão de áudio tem umas margens quadradas, todos os
  outros também."* Uma regra genérica de QSS — `QPushButton { background-color; border-radius: 6px }`
  — pega **todos** os botões: transforma os círculos de 44 px em quadradinhos e pinta um retângulo
  cinza **atrás** do círculo roxo desenhado à mão. Um sintoma visual, uma linha de causa.
- [ACHADO] O ⋮ vinha com um **chevron para baixo** que ninguém pôs: é o `menu-indicator` que o Qt
  acrescenta sozinho quando se usa `setMenu()`. Não existe no desenho de referência.
- [DIVERGÊNCIA] **Fundo dos botões-ícone mais leve** (`#eef1f5` no lugar de `#e4e7eb`), a pedido.
- [DECISÃO DE DESENHO] O roxo do botão de gravar **fica**. Ele abriu a conversa dizendo que gosta do
  layout antigo — que é o da web, e o roxo é dele. Se era essa a "cor forte", ele corrige em uma
  linha; inverter por conta própria seria trocar o que ele elogiou.
- [SEÇÃO NOVA NA SPEC — J] *"Não gosto que a tela fique redimensionando toda vez que surge um campo
  novo."* Virou regra: a janela nunca muda de tamanho sozinha, o espaço do que vai e volta nasce
  reservado, e o que flutua é desenhado por cima em vez de entrar no layout. O balão no rodapé com
  `setFixedHeight` alternando entre 0 e 32 era **causa** disso, não vítima — os dois pedidos eram o
  mesmo problema visto de dois lados.
- [DIVERGÊNCIA] **O balão sobe para cima do botão de gravar**, discreto, 3 s. Na web mora no rodapé
  da tela — mas a janela do desktop é pequena e sempre no topo, e o rodapé fica longe de onde o olho
  está.
- [FALHA DE ARQUITETURA, a mais séria desta rodada] *"A parte de consumo ficou uma bela porcaria. O
  fundo ficou preto… tá até vazando da tela."* Dois problemas somados: um **defeito** (widgets
  desenhados à mão sem pintar fundo próprio, sobre o véu escuro do modal) e um **erro de desenho meu**
  — a `SPEC-002` mandou transcrever um painel de 42rem, que na web vive numa página de tela cheia,
  para dentro de uma janela utilitária pequena. A medida foi transcrita; o contexto, não.
- [DIVERGÊNCIA] **Consumo vira janela própria**, redimensionável, com rolagem. Configurações
  continuam sobrepostas — são cinco linhas. A régua que faltava: *painel de leitura rápida cabe
  dentro da janela; dado tabular e gráfico precisam de janela própria.*
- [PROMOÇÃO DE BACKLOG] **`B-01` (arrastar e soltar) subiu** a pedido do usuário e virou o item `E2`
  da spec — solta no **botão de gravar**, reaproveitando o caminho do "Enviar arquivo". Primeira vez
  nesta fase que um item de backlog sobe por pedido direto no uso, e não por revisão de etapa.

## 8. O padrão que estas duas rodadas revelam

As reprovações mudaram de natureza e isso é informação. As três primeiras foram **escopo faltando**
— eu cortava a lista. Estas duas são **transcrição literal demais**: a spec levou a medida (42rem) e
o mecanismo (grade de três colunas, trilho e bolinha) sem levar o **contexto** (uma página de tela
cheia; um trio encostado no meio; uma bolinha que desliza). Transcrever desenho de uma mídia para
outra não é copiar número — é decidir o que o número queria dizer.

---

## 9. Terceira rodada de acabamento — duas armadilhas do Qt ganham nome

- [ACHADO] *"A barra de escuta fica aparecendo mesmo quando não está rodando áudio."* O código estava
  certo pela metade e o comentário dele explicava por quê: mantinha as barras desenhadas em repouso
  **citando o `J1`/`J2`**. Mas o `J2` manda reservar o **espaço**, não manter o **conteúdo**. Uma
  regra minha, aplicada ao pé da letra na direção errada — a spec ganhou a frase que faltava:
  *"reservar o lugar e apagar o conteúdo são coisas diferentes"*.
- [ACHADO, com a conta fechada] *"A expansão do botão de gravar ainda tá sendo limitada por
  quadrado."* Confirmado por aritmética: botão de 72 px, círculo de raio 34, pulso indo a
  `34 × 1,35 ≈ 46` — precisaria de 92 px. O Qt corta no retângulo do widget e o anel aparece
  ceifado. O realce do arrastar (raio + 4) sofria do mesmo. Virou armadilha nomeada na seção I:
  **animação que sai do widget é animação cortada**.
- [DECISÃO DE IMPLEMENTAÇÃO] Resolver com **camada sobreposta** e não aumentando o botão: aumentar o
  widget consertaria o corte e estragaria o trio, que acabou de ser ajustado. Um conserto que
  desfaz outro é meio conserto.
- [ACHADO] *"O fundo das caixas de seleção está preto."* Terceira ocorrência do **mesmo** defeito
  (painel de consumo, widgets desenhados à mão, agora a lista suspensa do `QComboBox`). Virou a
  segunda armadilha nomeada: **widget estilizado por QSS perde o desenho nativo das partes não
  declaradas, e a parte não declarada cai no preto**. A tarefa manda varrer os outros de uma vez, em
  vez de esperar a quarta ocorrência.
- [ACHADO] *"A notificação não quebre linha, mas continue centralizada."* O balão tem
  `setWordWrap(True)` e largura máxima de 260 px, e é ancorado pelo **topo** do botão — então texto
  comprido vira duas linhas e **empurra a âncora para cima**. A posição passava a depender do
  tamanho da mensagem. Vira uma linha só, cortada com reticências, crescendo a partir do centro.

## 10. O que muda no meu jeito de escrever a spec

Três das cinco últimas correções vieram de a spec ter sido **cumprida ao pé da letra e errada no
resultado** — barras em repouso citando o `J2`, medida de 42rem transcrita para uma janela pequena,
grade de três colunas cumprida com os botões nas pontas. O padrão é sempre o mesmo: escrevi o
mecanismo, e o Executor implementou o mecanismo. **Regra nova para mim: toda regra da spec diz
primeiro o que a pessoa vê, e só depois como se faz.** As duas armadilhas nomeadas nesta rodada
seguem esse formato — sintoma primeiro, mecanismo depois.

---

## 11. O painel de consumo reprovado duas vezes — e a spec como causa

- [VEREDITO] *"O painel de consumo está muito mal feito. Parece que você não está querendo copiar a
  versão que estamos copiando."* Segunda reprovação do mesmo painel.
- [CAUSA, e é minha] A seção `G` da `SPEC-002` tinha **cinco linhas de resumo** — "linha do tempo
  com zoom, navegação por dia e janela deslizante de 24h" — para descrever **~800 linhas** de
  JavaScript com constantes calibradas por medição. Para todo o resto da paridade eu transcrevi
  comportamento; só para o consumo escrevi um sumário. **O painel saiu do resumo, não do original**,
  e saiu exatamente do tamanho do resumo.
- [PADRÃO] **Resumo não se implementa, se preenche.** Onde a spec resume, o Executor inventa o
  resto — e inventa pouco, porque não sabe o que não sabe.
- [ARTEFATO] `G` reescrita: `G1` a `G6`, com as duas escalas em tabela comparativa (dia civil ×
  janela móvel de 3 min), a escada de passos do eixo, a folga de 3 s nas bordas, a âncora no ponto
  mais recente e não no relógio, o alvo de clique de raio 14 sobre um ponto de raio 4, o estado
  "ativada" da roda e a regra de **não pular para o fim ao deslizar**. Cada número com o porquê.
- [MUDANÇA NA TAREFA] A leitura do original virou **passo obrigatório e explícito**, com o intervalo
  de linhas nomeado — e com a ressalva de que isso não fere a `D-27`: transportar comportamento e
  números não é traduzir JavaScript linha a linha.
- [VÁLVULA] Se a leitura do original revelar comportamento que a spec ainda não descreve, o Executor
  escreve isso no PROGRESSO como **lacuna da spec**. É o caminho de volta que faltava — até aqui, o
  que a spec não dizia simplesmente não existia.

---

## 12. O consumo transcrito — e a válvula funcionando pela primeira vez

- [ENTREGA] Painel de consumo refeito a partir do original: as duas escalas com domínios diferentes,
  escada de marcas do eixo, janela móvel, alvo de clique grande, roda ativada, popup da requisição.
  `desktop/app.py` foi de 918 para **2.323 linhas**. Conferido por mim no artefato real.
- [A VÁLVULA PEGOU UM ERRO MEU] O Executor leu o `index.html` e achou que a `G3` estava **errada**:
  eu escrevi que "sem ativar, a roda rola a janela como qualquer conteúdo", e o `wheel` real faz
  `preventDefault()` e **troca de escala**; o scroll nativo só acontece com `Shift`. Ele implementou
  o que o código faz — dono único — e registrou a divergência em vez de me obedecer. **Conferi na
  fonte: ele está certo.** Spec corrigida. Foi a primeira vez que o caminho de volta funcionou: até
  aqui, o que a spec não dizia simplesmente não existia.
- [ACHADO DE MÉTODO, o mais importante desta volta] **A conferência por captura tem ponto cego.** O
  `grab()` offscreen não reproduz o estilo nativo da plataforma: uma camada que devia ser
  transparente saiu transparente na captura e **opaca no Windows real**, tapando o botão vizinho. A
  captura limpa não é prova quando o achado é sobre fundo, transparência ou desenho nativo. Virou
  parágrafo próprio na seção I, com a consequência escrita: nesses casos a conferência **termina no
  uso real**, e a tarefa diz isso em vez de marcar o item como confirmado.
- [ARMADILHA DO ÍCONE NO MENU] Tentativa 1 do Executor foi inflar o pixmap com margem transparente —
  só encolheu o ícone. A coluna de ícone de um `QAction` nativo tem largura fixa dada pelo estilo, e
  o pixmap maior é reamostrado para caber nela. Resolvido com `QWidgetAction` e layout próprio.
- [DEFEITO CONFIRMADO PELO PM] `OverlayModal` é `QWidget` puro com fundo no QSS e **sem
  `WA_StyledBackground`** — o véu escuro nunca pinta, e Configurações e o popup aparecem sem
  escurecer o fundo. O detalhe que dói: **o comentário duas linhas abaixo, no mesmo `__init__`,
  explica exatamente essa regra** — para justificar por que o painel branco é `QFrame`. A regra
  estava escrita e não foi aplicada ao vizinho.
- [PENDÊNCIA VS. SPEC] `G4` pede clique **ou `Enter`/`Espaço`** no ponto da linha do tempo; o
  critério que eu escrevi na tarefa só pedia clique. O Executor entregou clique e registrou a
  diferença. Erro meu de critério, não dele — o critério tem de cobrir o item da spec inteiro.
- [HIGIENE] `desktop/config.json` gera diferença fantasma em todo `git status`: o app grava CRLF, o
  versionado é LF, e o arquivo não termina com quebra de linha. Vai junto na próxima volta, com
  `.gitattributes`.
- [OBSERVAÇÃO] O usuário commitou duas vezes por conta própria nesta sequência (`35ceff9`,
  `fc461fa`) e configurou o atalho como `shift+esc+Ç` — a `D-28` (atalho escolhido por ele, pela
  interface) está sendo exercida na prática.

---

## 13. Etapa 1 fechada

- [MARCO] *"Tá funcionando como o esperado."* A Etapa 1 fecha em 2026-08-27, depois de **três
  reprovações e sete voltas de Executor**, com a `SPEC-002` cumprida de A a I e confirmada pelo
  usuário no app rodando. `desktop/app.py`: 2.323 linhas.
- [CONFIRMAÇÃO PENDENTE RESOLVIDA] A correção da `CamadaPulso` — a única que a captura offscreen não
  conseguia provar — está confirmada pelo uso real, que era exatamente onde a spec dizia que essa
  classe de conserto termina.
- [ESTADO DA SPEC-002] Fechada **como critério**, viva **como registro de divergências**. São cinco
  (`D-30`), e a interface web não mudou em nenhuma. Enquanto o desktop divergir, é nela que se
  escreve.
- [PENDÊNCIAS PEQUENAS, NÃO SEGURAM A ETAPA] Véu sem `WA_StyledBackground`, teclado no ponto da linha
  do tempo (`G4`), CRLF × LF do `config.json`. Descritas na `PROXIMA_TAREFA.md`, prontas para
  disparar quando incomodarem.
- [O CRITÉRIO DA FASE CONTINUA ABERTO] *"O usuário usa o ditado deste app no dia a dia, no lugar do
  que usa hoje."* Isso é uso em regime e se mede em dias. A etapa entregou a condição; o regime é o
  que falta.

## 14. O saldo do dia, em uma linha

Cinco reprovações, todas com a mesma raiz e nenhuma repetida: **escopo cortado abaixo do piso**
(`D-29`), **spec descrevendo o meio e não o fim** (grade de três colunas, trilho e bolinha, `J2`
aplicado ao contrário) e **resumo no lugar de transcrição** (a `G` de cinco linhas para 800 de
código). Todas viraram regra escrita. A última volta foi a primeira em que o Executor **me
corrigiu** — leu o original, viu que a `G3` estava errada e registrou em vez de obedecer.

## 15. Decisão de rumo, com a Etapa 1 fechada

Quatro caminhos na mesa: limpar as pendências e deixar assentar · atacar a inserção no campo em foco
(`B-22`) · escrever as histórias e o MVP (Etapa 3) · encerrar o chat.

**Escolha do usuário: limpar as três pendências e deixar assentar.** É o que a `D-25` já dizia — *o
que o app precisa aprender, ele aprende sendo usado* — e é o único caminho que responde ao critério
da fase, que é uso em regime e se mede em dias. A `B-22` continua sendo o maior salto de valor e o
maior risco (quatro tentativas já falharam em silêncio uma vez); esperar o app assentar antes de
mexer na camada de inserção é ordem, não adiamento.

---

## 16. Geração de imagem — entrada fora do plano, declarada

- [PEDIDO] *"Eu quero a solução mais rápida possível, porque eu precisava de fazer isso."* Escolher
  imagens (ou uma pasta), escrever um prompt, e a OpenAI devolve uma imagem nova. Interface no ⋮.
- [DECISÃO — `D-31`] Aceito, e **declarado como anexo fora do plano da F2**. A fase é ditado
  universal; imagem não é ditado. Não vira etapa nem entra no critério de conclusão. Fica escrito
  com data e motivo em vez de disfarçado de escopo — para ninguém achar, daqui a um mês, que a fase
  mudou de objetivo.
- [DECISÃO DE ARQUITETURA] Vai no **núcleo**, não no app chamando a OpenAI direto. A chave mora num
  lugar só e o registro de consumo mora num lugar só. Duplicar a chave no desktop ganharia meia hora
  e custaria caro na primeira troca de chave — e deixaria invisível justamente o custo que mais
  importa. Consequência assumida: **o núcleo deixa de ser "de transcrição"** e passa a ser a camada
  que fala com a OpenAI.
- [CUSTO, e o guarda-corpo] Imagem de qualidade média a 1024×1024: **~US$ 0,042**. Transcrição de
  30 s: ~US$ 0,0003. **~140×.** Isso aciona literalmente a condição de reabertura escrita na `D-18`
  ("o padrão de uso mudar de fato") — anotado lá, com prazo de reavaliação de uma semana. Por isso a
  tarefa exige: preço dos modelos de imagem na tabela do backend, custo registrado em
  `consumo.jsonl` pelo mesmo caminho das transcrições, estimativa visível **antes** de gerar e custo
  real depois. Sem isso o painel de Consumo passaria a mentir.
- [ARMADILHA APROVEITADA] O bug conhecido do `diarize` — modelo fora da tabela de preços grava
  `custo_usd: 0.0` em silêncio — vira aviso explícito na tarefa. Já documentado no `NUCLEO.md` desde
  24/08, agora finalmente serve para prevenir em vez de só explicar.
- [API CONFIRMADA NA DOC, 2026-08-27] `POST /v1/images/edits`, multipart com `image[]` repetido (até
  16), `prompt` até 32k caracteres, modelos `gpt-image-2` / `gpt-image-1.5` / `gpt-image-1` /
  `gpt-image-1-mini`, `input_fidelity: high` (é o que importa quando a entrada são referências), e
  `usage` com tokens na resposta — o que permite calcular custo pelo mesmo caminho já existente.
- [INVERSÃO DECLARADA] Única tarefa deste projeto em que "funcionar hoje" vem antes de "ficar bom" —
  e está escrito na tarefa que a inversão é porque **o usuário pediu**, não porque acabou o tempo.
- [PENDÊNCIAS PRESERVADAS] As três de limpeza saíram da `PROXIMA_TAREFA.md` e foram para o `PLANO.md`
  com o conserto de cada uma escrito. Substituir a tarefa não pode apagar o que estava nela.
