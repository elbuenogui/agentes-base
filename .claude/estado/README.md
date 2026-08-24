# .claude/estado/ — canal de progressão PM ↔ Executor

Esta pasta é o **único canal** entre o PM e o Executor. Camada de *progressão* (operacional),
separada da `coleta/`, que é o diário do projeto.

O mapa completo de onde tudo mora está em [`../CEREBRO.md`](../CEREBRO.md).

## Arquivos vivos

- `PLANO.md` .............. as etapas da fase corrente, com critério de pronto (dono: PM)
- `PROXIMA_TAREFA.md` ..... instrução única da tarefa atual (dono: PM)
- `PROGRESSO.md` .......... log append-only do que foi executado (dono: Executor)

Podem existir também, quando fizerem falta, um `MANUTENCAO.md` e um `ACOMPANHAMENTO.md` — os outros
dois tipos de plano, descritos em [`../metodo/PLANOS.md`](../metodo/PLANOS.md).

São criados no primeiro uso real; não há stubs vazios aqui, de propósito.

## Higiene

`historico/` guarda o que já fechou: snapshots de plano em virada, e as entradas de progresso dos
planos encerrados. Rascunho descartável vai em `../tmp/`, e nada de valor mora lá.

**Os limiares — quando salvar snapshot, quando arquivar, quando limpar — moram em
[`../metodo/HIGIENE.md`](../metodo/HIGIENE.md).** Este arquivo não repete número: foi assim que ele
passou dias dizendo um limiar diferente do que valia.
