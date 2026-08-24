---
name: revisao-acionada
description: Varre o projeto procurando inconsistências, entulho, acoplamento indevido e oportunidades de melhoria, e devolve cada achado julgado — com evidência medida, trade-off, complexidade e ganho. Use quando a pessoa pedir "revisão", "revisa a estrutura", "o que está errado aqui", ou ao fechar um plano. Analisa e reporta; nunca corrige.
---

# Revisão acionada

Uma revisão feita sob comando, no lugar de esperar alguém desconfiar de alguma coisa.

## A trava principal: isto é análise, não execução

**A revisão não corrige nada.** Não edita, não apaga, não move, não renomeia, não commita — nem
quando o conserto é óbvio, nem quando "é rápido", nem quando o próprio achado diz o que fazer.

Por quê, e não é formalidade:

- **Achado corrigido no meio da varredura não pode mais ser conferido.** Quem lê o relatório depois
  não sabe se o problema era real ou se a correção criou outro.
- **Corrigir muda o terreno que ainda está sendo varrido.** As lentes seguintes passam a medir um
  repositório diferente do que as primeiras mediram, e os achados param de ser comparáveis.
- **Quem decide o que muda é o usuário.** A revisão entrega achado julgado; virar tarefa é decisão
  dele, e execução é do Executor.

A única escrita permitida é o **relatório** e, se o usuário aprovar na conversa, os **itens de
backlog** que saírem dele. Nada mais.

## Passo 1 — escolher as lentes

Uma lente é **uma pergunta concreta e um lugar para olhar**. O valor está na diversidade entre elas,
não na quantidade: lentes que fazem a mesma pergunta devolvem o mesmo achado várias vezes e custam
várias vezes mais.

Lentes que costumam render numa revisão de método e documentação:

| Lente | A pergunta dela |
|---|---|
| **Consistência** | dois arquivos dizem coisas diferentes sobre o mesmo fato? |
| **Higiene** | o que está se acumulando, e qual regra deixou de ter gatilho? |
| **Propósito** | para que este arquivo foi criado, e ele ainda cumpre isso? |
| **Acoplamento** | o que é genérico está preso dentro do que é específico? |
| **Ergonomia** | quem chega novo consegue se orientar, e pelo arquivo que ele lê primeiro? |

Declare quais lentes rodaram. **Lente que não rodou é cobertura que não existe** — e silêncio sobre
ela lê-se como "está tudo certo".

## Passo 2 — varrer medindo

- **Conte, não estime.** Cubra as subpastas, não só o primeiro nível.
- **Número que sustenta argumento se confere antes de escrever.** Um argumento apoiado em número
  errado morre inteiro quando alguém confere.
- **Pergunte o que a unidade contada significa.** Sessenta arquivos não são sessenta decisões.
- Quando não der para medir, escreva "estimativa" na frente do número.

## Passo 3 — julgar cada achado

Achado sem custo declarado é ruído. Cinco campos, obrigatórios:

    **O que é** — uma frase.
    **Evidência** — o que foi medido ou lido, com caminho de arquivo.
    **Trade-off** — o que se perde consertando, e o que se perde não consertando.
    **Complexidade** — baixa / média / alta, com a razão em meia linha.
    **Ganho** — o que melhora de concreto, para quem.

E um **veredito**: `corrigir agora` · `vira item de backlog` · `recusar com razão` · `só registrar`.

Recusar é resultado legítimo. Um achado recusado com a razão escrita vale mais que um achado
"pendente" que ninguém vai revisitar.

## Passo 4 — consolidar

Lentes independentes acham a mesma coisa por caminhos diferentes sem saber. A consolidação junta os
duplicados **preservando os dois caminhos** — um problema achado por duas lentes distintas é mais
sólido, e vale dizer isso no relatório.

## Passo 5 — entregar

- **Painel**, seguindo a decisão de método de que estado se lê em painel e não em prosa. Vista,
  nunca fonte de verdade.
- **Itens de backlog** para o que não é agora, cada um com origem e a fase em que volta à mesa.
- **Lista curta do que precisa de decisão do usuário**, numerada, no fim.

## O que nunca fazer

- Corrigir, apagar, mover ou commitar durante a revisão.
- Inventar achado sem evidência de arquivo.
- Escrever achado sem trade-off e sem ganho.
- Contar sem conferir, ou apresentar estimativa como medição.
- Omitir que uma lente não rodou.
- Transformar achado em etapa de plano por conta própria — isso é decisão do usuário.
