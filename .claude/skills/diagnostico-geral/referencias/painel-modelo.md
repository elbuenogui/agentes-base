# Configuração do painel — modelo

> Copie para `.claude/painel.md` na raiz do projeto e preencha os `< >`. Este arquivo é **de cada
> projeto**: ele diz *quais* arquivos ler, com que vocabulário, onde publicar e com que cara. A skill
> diz *como* montar.
>
> Preencha **com a pessoa**, uma vez, na primeira chamada do comando. Depois disso é leitura.

## O que ler, e o que cada arquivo rende

| Arquivo | Do que sai no painel |
|---|---|
| `<caminho>` | a espinha do roadmap: as fases e o estado de cada uma |
| `<caminho>` | as etapas da fase corrente, com critério de pronto |
| `<caminho>` | o que foi entregue desde a última virada |
| `<caminho>` | o histórico arquivado, para datar as fases encerradas |
| `<caminho>` | as decisões, com a razão junto |
| `<caminho>` | o que falta produzir |
| `<caminho>` | ideias por estado |
| `<pasta>` | **o rastro**: um arquivo por chat de trabalho |

> Se o projeto não tiver algum desses, **tire a linha** em vez de inventar o arquivo. Painel montado
> sobre arquivo que não existe é chute com cara de autoridade.

## Vocabulário de estado

**Fases**: `<as palavras que este projeto usa>` — por exemplo `em-andamento`, `bloqueada:<X>`,
`nao-iniciada`, `encerrada`, `futuro`.

**Etapas**: `<concluída, cancelada, na fila, depois — ou o que o projeto usar>`.

**Ideias/backlog**: `<os estados>`. **Entram na vista** apenas `<quais>`; o resto existe para quem
for reabrir, não para ocupar espaço.

## Régua de alerta

Número vai em cor de alerta quando:

- `<condição — ex.: "PoCs rodadas em zero enquanto houver PoC bloqueando a fase corrente">`
- `<condição>`

> Declare aqui, não no julgamento de quem gera. Régua que muda entre gerações destrói a comparação,
> que é metade do valor do painel.

## Antes do método

`<O projeto começou em AAAA-MM-DD e ganhou método declarado em AAAA-MM-DD. O que veio antes entra no
roadmap como um bloco só, resumido, com o rastro apontando o histórico arquivado.>`

> Se o projeto nasceu junto com o método, apague esta seção. Se não nasceu, **não a apague**: sem
> ela o painel mente por omissão, fazendo parecer que tudo começou no primeiro plano escrito.

## Publicação

- **Título**: `<nome do painel>` · **ícone**: `<um ou dois emoji>`
- **Endereço fixo**: `<url>` — sempre o mesmo, para não acumular painéis velhos.

## Identidade visual

- **Fontes**: `<uma para títulos, uma para texto corrido, uma monoespaçada para IDs e números>`.
  Identificador é dado, não prosa — vai em mono.
- **Cabeçalho**: `<algum elemento gráfico que amarre o painel ao produto, se houver>`.
- **Cores**, em tokens, claro / escuro:
  - fundo `<hex>` / `<hex>` · superfície `<hex>` / `<hex>` · tinta `<hex>` / `<hex>`
  - linha `<hex>` / `<hex>` · acento `<hex>` / `<hex>`
  - semânticas, **separadas do acento**: pronto `<hex>` / `<hex>` · esperando `<hex>` / `<hex>` ·
    bloqueado `<hex>` / `<hex>`

> Cor semântica separada do acento importa: se "pronto" for a mesma cor do acento, o painel perde a
> capacidade de dizer que alguma coisa está pronta.
