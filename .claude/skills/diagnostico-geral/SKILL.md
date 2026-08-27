---
name: diagnostico-geral
description: Monta o painel de roadmap do projeto — as fases percorridas com o que cada uma entregou, onde estamos, o que vem, e o rastro até o chat de cada etapa. Publicado como página, colapsável. Use quando a pessoa pedir "diagnóstico geral", "panorama", "roadmap", "como está o projeto", ou ao fechar uma tarefa ou uma fase.
---

# Diagnóstico geral — o painel de roadmap

Quem toca um projeto de várias fases não consegue guardar na cabeça o plano inteiro, com as
especificações e os marcos de cada etapa. **Quem consegue é quem lê os arquivos.** Este painel existe
para devolver isso em forma navegável: o caminho percorrido, onde estamos, e o que vem.

## Regra que não se quebra

O painel é uma **vista**, não uma fonte de verdade. Tudo que ele mostra vem de arquivo. Se uma
informação não está num arquivo, **ela não entra no painel** — ela primeiro vira arquivo.

E o painel **não corrige nada**. Achado vira conversa; a correção é de quem cuida do plano, depois.

## Passo 0 — o projeto guarda estado em arquivo?

Esta skill monta o painel **a partir de arquivos**. Antes de qualquer coisa, veja se o projeto tem o
que ler: um plano com etapas, um registro do que já foi feito, decisões escritas.

**Se não tiver, diga isso e pare.** Um painel montado a partir de suposição é pior que painel
nenhum: ele parece autoridade e é chute. Ofereça o caminho honesto — começar a registrar o estado em
arquivo, e o painel passa a existir junto — mas não invente fase, etapa nem decisão que não está
escrita em lugar nenhum.

**Se tiver estado em arquivo mas com outra organização** (nomes diferentes, outra estrutura de
pastas), a skill continua servindo: o que muda é a configuração do passo seguinte, não o desenho do
painel.

## Passo 1 — a configuração do projeto

Esta skill descreve **como** se monta o painel. **Quais** arquivos ler, com que vocabulário e onde
publicar é de cada projeto, e mora em **`.claude/painel.md`**.

**Se esse arquivo não existir**, não adivinhe a cada geração: painel que muda de forma entre
execuções deixa de ser comparável, e comparar é o ponto. Em vez disso, **monte a configuração uma vez,
com a pessoa**:

**Use `referencias/painel-modelo.md` como base** — ele tem a estrutura e os `< >` para preencher.

1. Percorra o repositório e proponha a lista de arquivos-fonte e o que cada um rende no painel.
2. Levante o vocabulário de estado que o projeto já usa (as palavras que marcam fase e etapa).
3. Pergunte onde publicar — endereço fixo, para não acumular painéis velhos.
4. Combine a identidade visual: duas ou três fontes e uma paleta com tema claro e escuro.
5. **Escreva tudo em `.claude/painel.md`** e siga de lá em diante.

A descoberta acontece **uma vez**, na primeira chamada. Depois disso é leitura.

## A espinha é o roadmap

A seção mais importante é uma **linha do tempo vertical de fases**, e ela começa **antes** da fase
corrente. Cada fase é um bloco que abre (`<details>`/`<summary>`, sem JavaScript):

- **fase corrente**: aberta, com as etapas, o que está na fila e o que está esperando;
- **fases encerradas**: fechadas, com uma linha de resumo na capa e, ao abrir, as etapas com data,
  o que a fase entregou e o achado mais importante dela;
- **fases futuras**: fechadas, com o essencial e o que as bloqueia;
- **o que veio antes do método**, se houver: projeto quase nunca começa com processo declarado, e o
  trabalho anterior existiu. Ele entra como um bloco só, resumido — sem ele, o painel dá a impressão
  falsa de que o projeto começou no dia em que alguém escreveu o primeiro plano.

## Rastreabilidade: cada fase aponta o chat

Todo bloco fechado termina com um **rastro**: os arquivos do diário (um por chat de trabalho) e o log
de execução arquivado daquela fase. É o que permite voltar à conversa em que uma coisa foi decidida,
meses depois. Sem isso, o painel diz *o que* aconteceu e perde *onde foi discutido*.

## As outras seções, nesta ordem

1. **Números do topo** — calculados na hora, nunca copiados de prosa. Fases, decisões, questões
   respondidas de um total, PoCs rodadas, lacunas abertas, tarefas registradas. Número que está em
   zero e deveria estar acima vai em cor de alerta — **e o que "deveria" significa está declarado no
   `painel.md`**, não no julgamento de quem gera.
2. **A espinha** (acima).
3. **Onde estamos** — a tarefa corrente, por que ela importa e o que ela decide. Uma caixa só, em
   destaque. É a seção que a pessoa lê primeiro quando volta depois de dias.
4. **O que você pode fazer** — o menu de comandos disponíveis. Ver abaixo: é a seção que impede o
   projeto de esquecer as próprias ferramentas.
5. **Decisões** — as mais recentes por extenso, **cada uma com a razão junto**; o resto vira índice
   de uma linha, colapsado. A razão é o conteúdo, não o enfeite: é o que permite reabrir com
   honestidade e o que impede reabrir por esquecimento.
6. **O que falta** — lacunas, questões abertas e o backlog que amadurece para a fase seguinte.
7. **Consistência** — o resultado do passe de conferência (abaixo).
8. **O que eu preciso de você** — a lista curta e numerada do que depende de decisão da pessoa.

## O menu: "o que você pode fazer"

**Ferramenta que ninguém lembra que existe é ferramenta que não existe.** Um projeto acumula skills,
papéis e comandos, e eles somem da cabeça de quem os criou em poucas semanas. O painel é o lugar onde
a pessoa efetivamente olha — então é ali que o menu tem de morar.

Monte a lista **lendo o que o projeto tem**: as pastas em `.claude/skills/`, os papéis, a tabela de
comandos do arquivo de entrada, e os scripts do método. Não invente comando que não existe, e não
omita um que existe só porque não foi usado ainda.

Cada item traz três coisas:

- **o que se digita** — a palavra exata, em mono, porque é dado e não prosa;
- **o que acontece**, em uma ou duas frases, com a trava que mais importa daquele comando;
- **o fluxo**, numa linha de passos curtos — é o que responde "e depois o quê?" sem obrigar a abrir
  a skill.

**E o menu é consciente do estado, não uma lista fixa.** Um comando cujo insumo já existe aparece em
destaque, dizendo isso — *"tem tarefa esperando desde 25/08"*. Um que não se aplica agora fica
apagado, mas **continua na lista**: sumir é como o projeto esquece que a ferramenta existe.

## O que mantém o painel enxuto

Um painel que cresce sem regra vira um paredão que ninguém lê. O que **não** entra:

- **decisão antiga por extenso** — o livro-razão só cresce, por desenho; a vista é que recorta;
- **item de backlog recusado ou morto** — existe para quem for reabrir, não para ocupar espaço;
- **estimativa de esforço** — "custa duas sessões" é chute com cara de dado, e vira fato na terceira
  vez que alguém lê;
- **qualquer número copiado de dentro de um arquivo** — se está em prosa, provavelmente está velho.

## Passe de conferência

Você já está lendo os arquivos todos. **No mesmo passe, confira se eles concordam entre si.** Em
ordem de gravidade:

1. **Contradição de estado** — a mesma etapa, fase ou questão com situação diferente em dois arquivos.
2. **Número derivado escrito à mão** — qualquer contagem em prosa. Aponte arquivo e linha.
3. **Ponteiro quebrado** — citação a um identificador que não existe, ou link para arquivo que sumiu.
4. **Data fora de ordem** — arquivo mais velho que ainda se apresenta como atual depois de superado.
5. **Fato sem dono** — a mesma coisa argumentada por extenso em mais de um lugar.
6. **Arquivo de orientação que não conhece o método corrente** — o mais perigoso, porque é o que um
   chat novo lê primeiro.

**A seção aparece mesmo vazia**, dizendo que nada divergiu. Silêncio não distingue "conferi e está
certo" de "não conferi".

## Quando gerar

| Gatilho | Por quê |
|---|---|
| **tarefa conferida** — o executor entregou e quem planeja conferiu | é a unidade real de progresso: alguma coisa mudou de verdade |
| **virada de plano** — uma fase encerra e outra abre | é a mudança grande; o roadmap ganha uma fase inteira |
| **encerramento de chat** | nada mudou, mas é quando a pessoa vai olhar |
| **a pessoa pedir** | qualquer hora |

Gerar a cada mensagem é ruído; gerar só quando pedem deixa o painel velho. Os dois primeiros
gatilhos são o equilíbrio.

## Identidade visual — estável entre gerações

**Painel que muda de cara a cada geração deixa de ser comparável com o anterior**, e comparar é
metade do valor. As fontes, a paleta e a estrutura das seções ficam declaradas no `painel.md` e não
mudam sem motivo.

Duas regras técnicas que não dependem do projeto:

- **Tema claro e escuro por token.** Defina a paleta clara em `:root`, redefina só os tokens em
  `@media (prefers-color-scheme: dark)` sob `:root:not([data-theme="light"])` e de novo em
  `:root[data-theme="dark"]`. **Nenhuma cor pode existir apenas dentro de um bloco de tema** — é o
  jeito clássico de a página sair ilegível para metade das pessoas.
- **Colapso sem JavaScript**, com `<details>` e `<summary>`: funciona em qualquer lugar, é acessível
  pelo teclado e não quebra quando o script não carrega.

## Publicação

Publique no **endereço fixo declarado no `painel.md`**, para a pessoa não acumular painéis velhos.
Se a ferramenta de publicação não existir na sessão, escreva o HTML num arquivo e entregue o arquivo,
dizendo que o painel não pôde ser publicado.

**Se você não conseguir ler a versão publicada** — rede bloqueada, permissão ausente —, **não
sobrescreva no escuro**: publique num endereço novo, avise, e deixe a pessoa comparar.

## Depois de publicar

Uma resposta curta no chat: o link, e **só o que mudou** desde o painel anterior. O conteúdo está na
página; repetir no chat desperdiça a razão de o painel existir.
