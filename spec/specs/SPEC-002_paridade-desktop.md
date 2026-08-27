---
artefato: SPEC-002
titulo: Paridade do app de desktop com a interface web
fase: F2
status: viva
data: 2026-08-27
nasceu_de: reprovação da Etapa 1 no uso real (2026-08-27)
---

# SPEC-002 — Paridade do app de desktop com a interface web

**Régua desta spec, dita pelo usuário em 2026-08-27:** *"eu preferiria que fosse, no mínimo, a mesma
coisa que o HTML. No mínimo. Qualquer coisa mais além disso, a gente implementa aos poucos."*

Ela existe porque a Etapa 1 foi entregue **abaixo dessa régua** e reprovada no uso. O escopo daquela
tarefa — atalho, gravar, transcrever, clipboard — foi escrito por mim (PM) sem passar por
[`_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`](../_rascunhos/COMPORTAMENTOS_PARQUEADOS.md), que desde
2026-08-21 já dizia o contrário: *"A interface web é o desenho de referência do desktop — o código
não se aproveita; o desenho sim"*. Esta spec é aquela frase virada em lista conferível, para o erro
não depender de ninguém lembrar.

## Dono único

O **comportamento observável** desta lista tem um dono: `transcritor/frontend/index.html`. Esta spec
**não** descreve como implementar nada, não fixa widget, layout, cor nem biblioteca. Ela enumera
**o que o usuário consegue fazer** — se o `index.html` mudar, esta lista é que fica desatualizada, e
quem mexer nele é obrigado a passar aqui.

Os números calibrados (limiares, intervalos, limites) estão citados abaixo porque são **decisões de
comportamento** já pagas com medição na interface web. Repeti-los aqui é barato; redescobri-los, não.

## Critério de pronto da paridade

Uma pessoa que usa a interface web hoje abre o app de desktop e **não sente falta de nada** que
fazia antes. Não é "as telas se parecem": é a lista abaixo, item a item, exercida no app rodando.

**E a lista não se entrega em partes** (`D-29`, escrita depois de a paridade ser fatiada em duas e
reprovada de novo no mesmo dia). Enquanto faltar um item, o usuário continua voltando para a
ferramenta antiga — então o valor entregue não é metade, é zero.

---

## A. Fluxo de gravação com estado visível

- **A1 — Um só controle, que alterna.** Um clique inicia a gravação; o clique seguinte para e
  envia. **Não é segurar** (`push-to-talk`). O controle troca de figura conforme o estado: microfone
  (parado) → quadrado (gravando) → girando (processando, desabilitado).
- **A2 — Cancelar é ação separada.** Enquanto grava, existe um segundo controle que **descarta** o
  áudio: nenhuma requisição sai e a caixa de texto não é tocada. Parar e cancelar são coisas
  diferentes e ficam lado a lado.
- **A3 — Cronômetro.** Enquanto grava, tempo decorrido visível no formato `mm:ss`, atualizado a cada
  segundo. Some ao parar.
- **A4 — Faixa de amplitude.** Enquanto grava, uma faixa de 80 barras, amostrada a cada 60 ms — cada
  barra é um instante do passado, o valor novo entra numa ponta e o antigo sai da outra. São ~4,8 s
  de histórico andando. **É isso que responde "o microfone está pegando?" sem ninguém precisar
  adivinhar** — e é a razão de estar na paridade, não decoração.
  **Parado, a faixa some.** O *espaço* dela continua reservado (`J2`), mas **nada é desenhado ali**:
  uma fileira de pontinhos parada no repouso vira ruído permanente na tela — relatado no uso em
  2026-08-27. Reservar o lugar e apagar o conteúdo são coisas diferentes; foi a segunda que faltou.
- **A5 — Corte de segurança.** Aos **5 min** (300 s) a gravação para sozinha e **envia o que gravou
  até ali**, avisando por que parou. **Divergência declarada** (`D-30`, 2026-08-27): a interface web
  corta em 2 min 30 s e continua assim. O desktop é onde se dita de verdade, e 2 min 30 s cortava
  fala no meio. Cinco minutos de áudio a 16 kHz mono dão ~9,6 MB — bem abaixo do limite de 25 MB do
  núcleo.
- **A6 — Gate de silêncio, visível.** Se o **pico** de amplitude da gravação inteira ficar abaixo de
  **0,02** (escala 0–1), nada é enviado e aparece **"Não foi identificado nenhuma fala"** por 3 s. O
  descarte **nunca** é silencioso.
- **A7 — Escolha do microfone.** Quando o dispositivo é trocado nas Configurações, vale a partir da
  gravação seguinte; sem escolha, usa o padrão do sistema.

## B. Balão efêmero de status

- **B1 — Três tipos, uma área só.** `confirmação` some em **3 s**; `erro` some em 6 s (mensagens
  longas precisam de tempo de leitura); `andamento` **não mostra texto nenhum** — quem conta essa
  história é o próprio controle de gravação virando spinner.
- **B4 — Onde ele aparece.** **Logo acima do botão de gravar**, sobreposto e **discreto** — texto
  pequeno, fundo suave, sem ocupar a largura toda. **Divergência declarada** (`D-30`, 2026-08-27):
  na web o balão mora no rodapé da tela. Numa janela pequena e sempre no topo, o rodapé fica longe
  de onde o olho está, que é o botão. E **ele flutua sobre o conteúdo**: não é item de layout, não
  empurra nada, não muda o tamanho da janela (ver `J`).
- **B5 — Uma linha só, ancorada.** O balão **não quebra linha**. Ele cresce para os dois lados a
  partir do centro do botão, então a âncora é sempre a mesma e o texto nunca reflui — texto que não
  couber na largura útil da janela é cortado com reticências, com o texto inteiro na dica de foco.
  Quebrar em duas linhas empurra o balão para cima a cada mensagem mais longa: a posição passa a
  depender do tamanho do texto, que é o oposto de discreto.
- **B2 — Nunca empilha.** Uma mensagem nova cancela a anterior e ocupa o lugar dela na hora. Não há
  fila.
- **B3 — Um só canal.** Copiar, recortar, erro de transcrição, corte de segurança e falha de conexão
  usam este mesmo balão. Não se cria um segundo mecanismo de aviso.

## C. Caixa de transcrição

- **C1 — Acumula, não substitui.** Cada gravação nova é **somada** ao que já está na caixa, separada
  por quebra de linha quando falta. Ditar três vezes seguidas produz um texto só.
- **C2 — Editável.** O usuário digita e corrige direto na caixa.
- **C3 — Apagar com desfazer.** Um único botão que troca de função conforme o estado: **lixeira**
  quando há texto, **desfazer** quando a caixa está vazia e há algo guardado, **invisível** quando
  vazia e nada guardado (sem desfazer falso). O lugar dele na linha fica reservado nos três casos.
- **C4 — O desfazer vale não importa como esvaziou** — lixeira, recortar, `Backspace`, `Ctrl+A` +
  `Delete`, ou uma gravação nova por cima.
- **C5 — Como o snapshot é guardado.** Só quando a caixa fica **ociosa por 800 ms** e **não vazia**.
  Nunca a cada tecla. É isso que faz `Backspace` segurado devolver o texto inteiro em vez do último
  caractere: a rajada de eventos reagenda o prazo sem deixá-lo disparar, e o último valor não-vazio
  antes da rajada é o que sobrevive.
- **C6 — Desfazer consome o snapshot.** Esvaziar de novo depois de escrever algo novo gera um
  snapshot novo; não reaproveita o antigo.

## D. Copiar e recortar

- **D1 — Um botão, dois modos.** **Recortar por padrão** — o botão copia **e apaga**. Desligando
  **"Recortar em vez de copiar"** nas Configurações, ele volta a só copiar, trocando ícone e rótulo.
  **Divergência declarada** (`D-30`, 2026-08-27): a web nasce em copiar. No desktop o texto ditado
  vai embora para outro aplicativo e quase nunca volta — deixar o anterior na caixa faz a próxima
  gravação empilhar em cima de lixo. E o desfazer continua cobrindo o arrependimento (`C4`).
- **D2 — Recortar passa pelo mesmo caminho do apagar**, então o desfazer funciona sobre um recorte
  igual a qualquer outra forma de esvaziar.
- **D3 — Caixa vazia** produz erro no balão ("nada para copiar/recortar"), não uma cópia vazia.

## E. Menu de três pontos

Um menu compacto, fora do caminho, com exatamente três itens: **Configurações**, **Consumo**,
**Enviar arquivo**. Fecha ao clicar fora e com `Esc`.

- **E1 — Enviar arquivo.** Escolher um arquivo de áudio do disco e transcrever, preservando **nome e
  extensão reais** no envio. Aceita ao menos `.m4a`, `.wav`, `.mp3`. O resultado entra na caixa pelo
  mesmo caminho da gravação (soma, balão, snapshot).
- **E2 — Arrastar e soltar** *(além da paridade — `B-01`, promovido em 2026-08-27 a pedido do
  usuário)*. Arrastar um arquivo de áudio até o **botão de gravar** e soltar transcreve, pelo mesmo
  caminho do `E1`. Enquanto o arquivo paira sobre a janela, o botão **mostra que vai aceitar**;
  arquivo de formato não aceito é recusado com o balão, não com silêncio.

## F. Configurações

Cinco itens, e só. Cada um vale imediatamente, sem reiniciar:

| item | tipo | efeito |
|---|---|---|
| **F1** Modelo de transcrição | lista | vale para gravação **e** envio de arquivo |
| **F2** Streaming do transcript | interruptor | texto aos poucos conforme a API responde, em vez de esperar a resposta inteira |
| **F3** Dispositivo de entrada | lista | microfone usado a partir da gravação seguinte |
| **F4** Recortar em vez de copiar | interruptor | ver `D1` — **nasce ligado** (`D-30`) |
| **F5** ~~Transcrição em tempo real~~ | — | **não transporta** — modo ao vivo congelado (`D-02`) |

`gpt-4o-transcribe-diarize` continua **fora** da lista de modelos oferecidos (qualidade reprovada em
2026-08-18); o núcleo segue aceitando.

## G. Painel de consumo

> **Esta seção foi reescrita em 2026-08-27, depois de o painel ser reprovado duas vezes.** A versão
> anterior tinha cinco linhas — "linha do tempo com zoom, navegação por dia e janela deslizante" — e
> o resultado saiu do que essas cinco linhas diziam, não do painel que se está copiando. O usuário
> resumiu: *"parece que você não está querendo copiar a versão que estamos copiando"*. **O erro é
> meu**: para todo o resto da paridade eu transcrevi comportamento; para o consumo eu escrevi um
> resumo, e resumo não se implementa — se preenche.
>
> **Fonte obrigatória**: `transcritor/frontend/index.html`, do comentário
> `--- Linha do tempo das requisições ---` até `carregarConsumo()`. São ~800 linhas com números
> calibrados por medição. **Leia antes de escrever qualquer coisa**, e trate cada divergência do que
> está lá como defeito, não como escolha.

> **O Consumo abre em janela própria** — redimensionável, com barra de rolagem, título e fechar
> normais. **Divergência declarada** (`D-30`): na web ele é um modal por cima da página, e a página
> tem a tela inteira. As **Configurações** continuam sobrepostas dentro da janela: são cinco linhas.

### G1 — Sessão

Três linhas, nesta ordem e com estes rótulos: **Requisições**, **Tokens**, **Custo estimado**. Custo
sempre em `US$ 0,0000` com **quatro casas**. Vêm de `sessao` no `GET /consumo`.

**Resetar sessão** guarda os valores atuais como linha de base e passa a mostrar a diferença,
**nunca abaixo de zero**. Não existe endpoint de reset; o histórico do núcleo não é apagado — e isso
fica escrito na tela, com estas palavras: *"O reset zera só esta tela; o histórico salvo no backend
não é apagado."*

### G2 — Histórico diário e gráfico

- Lista de `por_dia`, uma linha por dia: **data à esquerda, `<tokens> tokens — US$ 0,0000` à
  direita**, separadas por um filete. Área com rolagem própria, ~8rem de altura.
- Vazio mostra **"Nenhum consumo registrado ainda."**, não uma área em branco.
- **Gráfico de barras** logo abaixo, mesma ordem dos dias: altura proporcional ao **custo**,
  normalizada pelo maior dia, **mínimo de 4 px** para o dia quase-zero não sumir. Barra de `0.9rem`
  arredondada só em cima, coluna de `1.75rem`, altura total `6rem`, rolagem horizontal. Rótulo do
  dia em **`mm-dd`** por baixo. Dica de foco na barra: `data: US$ 0,0000`.

### G3 — Linha do tempo das requisições

Um ponto por requisição num eixo de tempo. **Duas escalas**, alternadas por um botão que diz a
escala atual:

| | escala **hora** | escala **minuto** |
|---|---|---|
| domínio | **um dia civil por vez**, meia-noite a meia-noite | **janela móvel de 3 min** dentro das últimas 24 h |
| largura | a do painel (mín. 480 px) — o dia inteiro cabe sem rolar | fixa, **15 px/s** → sempre 2.700 px, não importa o tamanho do histórico |
| navegação | **◀ Dia anterior · Dia seguinte ▶**, desabilitados nas pontas | **Início (24h atrás) · deslizador · Mais recente** |
| preço no ponto | **não** — com muitas requisições próximas os rótulos colidem e viram ruído | **sim**, acima de cada ponto, em `$0,0000` |

- **Por que a janela móvel existe**: sem ela, 24 h a 15 px/s dariam 1,3 milhão de pixels de largura.
  O teto fixo é o ponto da decisão — não é detalhe de implementação.
- **Folga de 3 s nas duas bordas** do trecho desenhado (não do trecho que filtra os pontos): sem
  ela, o ponto exatamente na borda fica com metade do alvo de clique cortada.
- **Âncora do fim das 24 h é a requisição mais recente**, não a hora atual — senão quem abre o
  painel depois de dias sem usar vê uma janela vazia.
- **Marcas do eixo**: escada de passos redondos — 10 s, 30 s, 1, 5, 15, 30 min, 1, 3, 6, 12 h, 1 dia
  — escolhendo o **menor passo cujo espaçamento chegue a ~80 px**. As marcas caem em fronteira de
  relógio local (minuto/hora/dia cheios), **nunca** em múltiplo cru de tempo absoluto. A primeira
  marca e toda virada de dia trazem `dd/mm` junto; as demais, só a hora.
- **O ponto**: círculo de raio 4 com anel de 2 px na cor do fundo, para pontos sobrepostos se
  separarem. **Alvo de clique de raio 14** — bem maior que o desenho.
- **A roda do mouse**: com a linha do tempo *ativada* (clique nela), a roda **desliza a janela**; sem
  ativar, a roda rola a janela como qualquer conteúdo. O estado ativado é visível, e sai com `Esc` ou
  clique fora. Sem isso, rolar a janela dentro da linha do tempo vira uma briga.
- **Ao trocar de escala, as duas concordam sobre o período**: quem estava vendo o dia 23 na escala
  hora vê o mesmo trecho ao ir para minuto, e vice-versa.
- **Não pular para o fim ao deslizar.** O salto automático para o ponto mais recente só acontece ao
  **abrir** o painel, ao **trocar de escala** e nos botões de ponta. Reaplicá-lo a cada redesenho é o
  bug clássico: em vez de deslizar, a vista "vai direto pro fim" a cada giro da roda.
- Vazio mostra **"Nenhuma requisição registrada ainda."** e esconde os controles de navegação.

### G4 — Abrir uma requisição

Clique (ou `Enter`/`Espaço`) num ponto abre a **transcrição daquela requisição**, com horário,
modelo e custo. Fecha com `Esc`, com o ✕ e com clique fora. O texto rola se for longo.

### G5 — Carregando e erro

Ao abrir: **"Carregando…"**, com todo o resto escondido — nada de painel meio montado. Erro mostra a
mensagem e **não** deixa sobrar bloco vazio na tela. Núcleo desligado é erro tratado, não travamento.

### G6 — O painel é legível

Não é item da web; é a régua que o desktop reprovou duas vezes. **Todo widget desenhado à mão pinta
o próprio fundo**, todo texto tem cor declarada, e nada vaza da janela — o conteúdo inteiro vive
dentro de uma área com rolagem. Ver a armadilha do QSS na seção I.

## H. Teclado

- **H1 — `Esc` fecha** o que estiver aberto por cima: popup de requisição, painel de consumo,
  configurações, menu de três pontos — nessa ordem de prioridade.
- **H2 — Clicar fora fecha** menu e painéis.

## I. Identidade visual

> **Extrato derivado, conferido em 2026-08-27.** O dono continua sendo o CSS de
> `transcritor/frontend/index.html`. Esta tabela existe porque "o layout não está igual" precisava
> virar número conferível — **se divergir do CSS, o CSS vence**, e esta seção é que está velha.
> `1rem = 16px`.

**Armadilha do Qt que já causou três defeitos visíveis**

Widget estilizado por QSS **perde o desenho nativo das partes que você não declarou**, e a parte
não declarada costuma cair no preto. Foi assim com o fundo do painel de consumo, com os widgets
desenhados à mão sobre o véu do modal e com a lista suspensa das caixas de seleção
(`QComboBox QAbstractItemView`, relatada em 2026-08-27). **Regra: quem estiliza um widget, estiliza
todas as partes dele** — a lista suspensa, a barra de rolagem, a seta, o `viewport`, o estado
desabilitado. E todo widget desenhado à mão pinta o próprio fundo antes de desenhar qualquer coisa.

**Animação que sai do widget é animação cortada**

O pulso do gravando e o realce do arrastar crescem **para fora** do círculo. Num widget de tamanho
fixo igual ao círculo, o Qt corta o que passa da borda — e o anel vira um quadrado de cantos
visíveis, que foi exatamente a "sensação estranha" relatada em 2026-08-27. Quem cresce precisa de
espaço para crescer, **sem** que esse espaço mexa no layout: desenhe em uma camada sobreposta.

**Todos os botões-ícone são círculos, e o fundo deles é leve**

Pedido do usuário em 2026-08-27: *"o botão de áudio tem umas margens quadradas, todos os outros
também… dá pra ficar mais claro e também colocar bola nos outros em uma cor mais leve no fundo"*.

- **Círculo de verdade**, não retângulo com cantos arredondados: raio = **metade** do lado, em todos
  eles (⋮, cancelar, lixeira/desfazer, copiar/recortar, fechar). Uma regra geral de
  `border-radius: 6px` no `QPushButton` transforma os círculos em quadradinhos — e, no botão de
  gravar, pinta um retângulo cinza **atrás** do círculo roxo, que é a "margem quadrada" que ele viu.
  Botão redondo não herda a regra genérica.
- **Fundo leve**: os botões secundários são uma **bola clara** (`#eef1f5`, hover `#dde3e9`) com o
  ícone em `#334155` — mais leve que o cinza da web. O botão de gravar mantém o roxo cheio: é o
  único elemento que precisa se impor.
- **Sem seta de menu.** O ⋮ abre um menu, e o Qt acrescenta sozinho um *chevron* para baixo ao lado
  do ícone (`QPushButton::menu-indicator`). Ele não existe no desenho — tem de sumir.

**Paleta**

| papel | cor |
|---|---|
| fundo da janela | `#f4f6f8` |
| fundo dos cartões e painéis | `#ffffff` |
| borda de cartão e de painel | `#d9e2ec` |
| borda de campo (caixa de texto, lista) | `#bcccdc` |
| texto | `#1f2933` · secundário `#334155` · dica `#52606d` |
| roxo — gravar em repouso, barras de amplitude | `#7c3aed` (hover `#6d28d9`) |
| vermelho — gravando | `#dc2626` (hover `#b91c1c`) · fundo do cancelar `#fee2e2` (hover `#fecaca`), ícone `#b91c1c` |
| azul — processando, interruptor ligado, barra do gráfico | `#2563eb` |
| bola de botão-ícone | `#eef1f5` (hover `#dde3e9`), ícone `#334155` — **mais leve que a web** (`D-30`) |
| balão de confirmação | `#047857` · de erro `#b91c1c` · neutro `#1f2933` |
| véu do modal | `rgba(15,23,42,0.45)` |

**Medidas**

| elemento | medida |
|---|---|
| largura útil da coluna principal | `40rem` (640 px) máx.; painel de consumo `42rem`, configurações `24rem` |
| cartão de gravação | fundo branco, borda 1 px, raio `0.5rem`, respiro interno `1.5rem`, espaçamento `1rem` |
| botão de gravar | círculo de `4.5rem`, ícone `1.75rem` branco |
| botão de cancelar e ⋮ | círculo de `2.75rem`, ícone `1.25rem` |
| botões-ícone da caixa de texto | círculo de `2rem`, ícone `1.05rem` |
| caixa de transcrição | altura mín. `8rem`, raio `0.375rem`, respiro `0.6rem` |
| faixa de amplitude | altura `2.5rem`, barras de `1` a `3` px, `1` px de vão, raio total, altura de repouso `15%`, **espelhada a partir do centro** |
| cronômetro | `1.1rem`, semibold, **dígitos de largura fixa** |
| interruptor | trilho `2.75 × 1.5rem` (44 × 24 px), **bolinha branca de `1.2rem`** (19 px) que desliza `1.25rem`, transição de 0,15 s; trilho `#cbd2d9` desligado e `#2563eb` ligado |
| balão | rodapé, centralizado, `2rem` da borda de baixo, raio `0.375rem`, sombra |
| fonte | Segoe UI (ou a do sistema) |

**O interruptor é um interruptor**

Um retângulo arredondado que muda de cor **não é um interruptor** — é o que o `QCheckBox::indicator`
do Qt entrega de graça, e foi reprovado pelo usuário em 2026-08-27. O que faz alguém reconhecer um
interruptor é a **bolinha branca deslizando de um lado para o outro**: sem ela, não há posição
"ligado" e "desligado", só duas cores que a pessoa precisa decorar. Vale a pena desenhar à mão.

**Geometria que não é decoração**

- **Os três controles são um trio junto, no meio — não uma barra espalhada.** ⋮ à esquerda, gravar
  no meio, cancelar à direita, **encostados**, com `0.6rem` de vão entre eles. O trio inteiro fica
  centralizado no cartão. Na web isso sai de uma grade `1fr · 4.5rem · 1fr` com cada lateral
  alinhada para a borda que **encosta** no centro; o que não se pode fazer é empurrar o ⋮ para a
  ponta esquerda e o cancelar para a ponta direita (foi o que aconteceu na primeira versão do
  desktop, com dois `addStretch` — reportado pelo usuário em 2026-08-27).
- **O botão de gravar não se move.** A coluna do meio tem largura fixa e o vão não muda: aparecer ou
  sumir o cancelar **não** desloca o centro.
- **A faixa de amplitude cresce para os dois lados** a partir do meio, não de baixo.
- **Gravando pulsa**: anel vermelho expandindo, ciclo de 1,2 s.
- **Processando gira**: anel de 1,6 rem, volta a cada 0,8 s.

## J. A janela não se mexe sozinha

Pedido do usuário em 2026-08-27: *"não gosto que a tela fique redimensionando toda vez que acontece
alguma coisa ou surge um novo campo… gostaria que fosse mais estável"*.

- **J1 — Tamanho estável.** A janela **nunca** muda de tamanho por conta própria. Cronômetro, faixa
  de amplitude, botão de cancelar, balão — nada disso pode fazer a janela crescer ou encolher.
- **J2 — O espaço já nasce reservado.** Elementos que vão e voltam ocupam o lugar deles **desde a
  abertura**, vazios ou invisíveis. Some o conteúdo, não a caixa. (É o mesmo princípio que já valia
  para o botão de lixeira/desfazer em `C3`, que fica *invisível* e não *removido* — agora vale para
  todos.)
- **J3 — Quem flutua, flutua mesmo.** O balão (`B4`) e os painéis sobrepostos são desenhados **por
  cima** do conteúdo, não inseridos no layout.
- **J4 — Redimensionar continua sendo do usuário.** Ele arrasta a borda se quiser; a janela só não
  decide isso sozinha.

---

## O que **não** transporta

| item | por quê |
|---|---|
| **Hover como gatilho** | não existe em toque, e no desktop compete com a janela flutuante (`COMPORTAMENTOS_PARQUEADOS`) |
| **Modo ao vivo / tempo real** | congelado (`D-02`), e fora do contrato (`SPEC-001`) |
| **Aviso de "backend na porta 8000"** no texto de erro | o desktop conhece a URL por configuração; a mensagem tem de falar a língua do desktop |

## O que o desktop tem **além** da paridade

Não é paridade, e por isso **não** entra nesta lista como critério — está aqui só para ninguém
confundir escopo com omissão. Cada um vira etapa própria, "aos poucos", como o usuário pediu:

- atalho global de teclado, configurável, como acionamento principal (`D-01`, `D-25`);
- os três estados da janela e o botão flutuante (`D-15`);
- inserir a transcrição no campo em foco (`B-22`, `D-26`) e a segunda ação "colocar a última
  transcrição", que lê da **memória do app**, nunca do clipboard (`COMPORTAMENTOS_PARQUEADOS`);
- arrastar e soltar áudio (`B-01`), cópia automática configurável (`B-23`).

## Defeitos que a Etapa 1 deixou, e que esta spec resolve por construção

| defeito relatado em 2026-08-27 | item que o cobre |
|---|---|
| "ele não grava direito" — sem forma de saber o que falhou | `A4` (faixa), `A3` (cronômetro), `A6` (gate visível), `A7` (dispositivo) |
| "F9/F17 é uma péssima tecla" | `A1` (alternar, não segurar) + atalho configurável **pela interface**, não por JSON |
| descarte silencioso em silêncio ou erro | `A6`, `B1`–`B3` |
