# Tarefa: App de desktop — refazer o painel de consumo transcrevendo o original, e quatro correções visuais
Referente à **etapa 1** do `PLANO.md`

## Contexto

O painel de consumo foi reprovado **duas vezes**. Veredito do usuário: *"o painel de consumo está
muito mal feito, parece que você não está querendo copiar a versão que estamos copiando."*

**A culpa é da spec, e a spec já foi consertada.** A seção `G` tinha cinco linhas de resumo — "linha
do tempo com zoom, navegação por dia e janela deslizante" — e o painel saiu do resumo, não do
original. Para todo o resto da paridade a spec transcreveu comportamento; só para o consumo ela
escreveu um sumário. **Resumo não se implementa, se preenche.**

A seção `G` foi reescrita em `spec/specs/SPEC-002_paridade-desktop.md`: agora são `G1` a `G6`, com as
duas escalas lado a lado, os números calibrados e o **porquê** de cada um.

Esta tarefa tem duas partes independentes: **refazer o consumo** (a grande) e **quatro correções
visuais** que já estavam na fila.

## Arquivos envolvidos

- `desktop/app.py`

## Parte A — O painel de consumo, transcrito do original

### A.1 Leia a fonte antes de escrever qualquer linha

`transcritor/frontend/index.html`, do comentário `--- Linha do tempo das requisições ---` até
`carregarConsumo()`. **São ~800 linhas**, com constantes calibradas por medição e comentários que
explicam por que cada número é aquele. Não é leitura opcional e não dá para fazer esta parte sem ela.

Depois leia `SPEC-002` **G1 a G6**, que é o mesmo conteúdo organizado em critério conferível.

> Isto **não** contradiz a `D-27` ("não copiar código do `index.html` para o Python"). O que se
> transporta é o **comportamento e os números**; a implementação é sua, em Qt. O que a `D-27` proíbe
> é traduzir JavaScript linha a linha — não é ignorar o que o JavaScript faz.

### A.2 O que precisa existir

`G1` sessão com reset por linha de base · `G2` lista diária e gráfico proporcional · `G3` linha do
tempo com **as duas escalas**, navegação por dia, janela móvel, escada de marcas do eixo, ponto com
alvo de clique grande, roda ativada e a regra de não pular para o fim · `G4` popup da requisição ·
`G5` carregando e erro · `G6` legibilidade.

**Onde você tiver de escolher, escolha o que o original faz.** Divergência do original é defeito
nesta parte — exceto a janela própria, que está declarada na `D-30`.

### A.3 Os pontos onde as duas versões anteriores erraram

- **A linha do tempo não é um gráfico de barras nem uma lista.** É um eixo de tempo com pontos.
- **As duas escalas têm domínios diferentes** — um dia civil × janela de 3 minutos. Não é zoom
  contínuo, são dois modos com navegação própria cada um.
- **As marcas do eixo caem em fronteira de relógio**, escolhidas pela escada de passos; não são
  divisões iguais do intervalo.
- **O alvo de clique (raio 14) é maior que o ponto (raio 4)** — de propósito.
- **Nada pode vazar da janela**: conteúdo inteiro dentro de uma área com rolagem.

### A.4 Confira com dado real

O histórico do projeto tem centenas de requisições em vários dias — a linha do tempo tem o que
mostrar nas duas escalas, e o gráfico diário tem mais de uma barra. Suba o núcleo, abra o painel e
**olhe**. Depois abra com o núcleo desligado e confira o `G5`.

## Parte B — Quatro correções visuais (já estavam na fila)

### B.1 A faixa de amplitude some quando não está gravando (`SPEC-002` A4)

`BarraAmplitude` desenha as 80 barras no piso de 15% mesmo parada, e o comentário do código cita o
`J1`/`J2` como justificativa. **Metade certo**: o `J2` manda reservar o *espaço*, não manter o
*conteúdo*. Parada, o `paintEvent` **não desenha nada**; o widget mantém os 40 px de altura.

### B.2 O pulso do botão está sendo cortado num quadrado (`SPEC-002` I)

Conta fechada: botão `setFixedSize(72, 72)`, círculo de raio 34, pulso indo a `34 × 1,35 ≈ 46` —
precisaria de 92 px. O Qt corta no retângulo do widget. O realce do arrastar (`raio + 4`) idem.

**Camada sobreposta, não botão maior**: widget próprio, filho do cartão,
`WA_TransparentForMouseEvents`, centrado sobre o botão no `resizeEvent`, **por baixo dele** no
empilhamento, ~110 px, desenhando só o pulso e o anel de arrastar. O `BotaoGravar` continua 72 × 72 e
**o trio não se mexe** — aumentar o widget consertaria isto e estragaria aquilo.

### B.3 A lista suspensa das caixas de seleção está preta (`SPEC-002` I)

Terceira ocorrência da mesma armadilha: widget estilizado por QSS **perde o desenho nativo das
partes não declaradas**. Declare `QComboBox QAbstractItemView` (fundo branco, texto `#1f2933`, item
selecionado `#2563eb` com texto branco, borda `#bcccdc`), `::drop-down`, `::down-arrow` e o estado
desabilitado. **Varra os outros de uma vez** — barra de rolagem, `viewport` do `QScrollArea`, menu do
⋮ — em vez de esperar a quarta ocorrência.

### B.4 O balão não quebra linha (`SPEC-002` B5)

`setWordWrap(False)`, uma linha sempre, largura livre até a útil da janela menos margem, texto que
não couber **cortado com reticências** (`QFontMetrics.elidedText`) e completo na dica de foco.
Posição recalculada a partir do **centro do botão**, para crescer para os dois lados sem a âncora
sair do lugar. Altura fixa.

## Critério de pronto

- [ ] `G1` a `G6` conferidos **item a item contra o original aberto ao lado**, não contra a memória.
- [ ] As duas escalas funcionando, com a navegação própria de cada uma e concordando sobre o período
      ao trocar.
- [ ] Marcas do eixo em fronteira de relógio, com `dd/mm` na primeira e em cada virada de dia.
- [ ] Roda: desliza a janela com a linha do tempo ativada, rola a janela sem ativar; `Esc` desativa.
- [ ] Deslizar **não** pula para o fim; abrir, trocar de escala e os botões de ponta **pulam**.
- [ ] Clique num ponto abre a transcrição com horário, modelo e custo.
- [ ] Painel legível, nada preto, nada vazando, tudo com rolagem — com dado real e com o núcleo
      desligado.
- [ ] Parte B, os quatro itens.
- [ ] Conferência por captura, **agora incluindo o consumo nas duas escalas**, lado a lado com a
      captura do painel da web no Chromium. Liste no PROGRESSO as divergências que achou e corrigiu.
      Apague as imagens ao terminar.
- [ ] Nada em `transcritor/` alterado.
- [ ] Repositório pronto para commit — **sem commitar** (`M-05`).

## Registro no PROGRESSO
curto — **com a lista de achados da conferência visual fora do teto**. Se a leitura do original
revelar comportamento que a `SPEC-002` ainda não descreve, **escreva isso no PROGRESSO**: é lacuna da
spec, e eu conserto.

## O que NÃO fazer

- **Não** simplificar a linha do tempo "porque em Qt é difícil". Se algum controle não couber,
  **pare e avise antes**, com o motivo — não entregue sem.
- **Não** traduzir o JavaScript linha a linha (`D-27`): transcreva comportamento e números.
- **Não** aumentar o `BotaoGravar` para resolver o `B.2`.
- **Não** mexer em `transcritor/`.
- **Não** commitar.
