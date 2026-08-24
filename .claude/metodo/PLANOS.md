# Tipos de plano

> Camada: **cérebro** (genérico). Dono do formato de cada plano: `../PM.md`.

Um projeto tem mais de um tipo de trabalho, e forçar todos no mesmo formato de plano faz dois
estragos: o trabalho que não entrega produto ocupa o lugar do que entrega, e o trabalho que só se
observa não tem onde ser observado — vira decisão solta que ninguém tem obrigação de reler.

## Plano de fase

**Entrega produto.** Tem objetivo, escopo com "fora" explícito, etapas com critério de pronto
verificável, e um critério de conclusão da fase inteira.

- **Vive em** `.claude/estado/PLANO.md`.
- **Um de cada vez.** É o que ocupa o Executor.
- **Encerra com o entregável em uso**, não com o documento pronto.

## Plano de manutenção

**Não entrega produto**: arruma o método, limpa entulho, reconcilia documentos, paga dívida de
organização. O trabalho é real e precisa de plano, mas medir sucesso por "o que o usuário ganhou"
não funciona aqui.

- **Vive em** `.claude/estado/MANUTENCAO.md`, quando existir.
- **Pode coexistir com um plano de fase**, porque não disputa o mesmo entregável — mas disputa o
  Executor, então uma tarefa por vez continua valendo.
- **Critério de pronto é sempre verificável no arquivo**: "o arquivo X deixou de dizer Y", "a busca
  por Z devolve um resultado só".

> Sem este tipo, trabalho de arrumação se disfarça de plano de fase e ocupa o lugar do produto.

## Acompanhamento

**Não se executa: se observa.** Custo, uso, tamanho de arquivo, alarme que alguém definiu. Não tem
etapas nem critério de pronto — tem **o que se olha, de quanto em quanto tempo, e o que dispara
conversa**.

- **Vive em** `.claude/estado/ACOMPANHAMENTO.md`, quando existir.
- Cada item traz: **o que se mede**, **onde se lê**, **o valor de referência**, e **o que fazer
  quando encostar**.
- Coexiste com qualquer plano; não consome Executor.

> Sem este tipo, um alarme vira decisão porque não há outro lugar — e decisão ninguém releva, então
> o alarme nunca é conferido.

## A regra que separa os três

| | entrega produto | consome Executor | quantos ao mesmo tempo |
|---|---|---|---|
| **Fase** | sim | sim | **um** |
| **Manutenção** | não | sim | um |
| **Acompanhamento** | não | não | quantos precisar |

Na dúvida entre fase e manutenção, pergunte: **se isto ficar pronto, o usuário ganha alguma coisa
que ele consegue usar?** Se a resposta é "o repositório fica mais limpo", é manutenção.

## Backlog não é plano

Ideia que ainda não é trabalho não entra em plano nenhum — ela mora no backlog, com estado e com a
fase em que volta à mesa. **Item de backlog nunca vira etapa por iniciativa do PM**: ao fechar uma
etapa ou fase, o PM lê os itens marcados para a fase seguinte e pergunta ao usuário quais sobem.
