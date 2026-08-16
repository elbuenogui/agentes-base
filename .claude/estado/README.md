# .claude/estado/ — canal de progressão PM ↔ Executor

Esta pasta é o **único canal** entre o PM e o Executor. Camada de *progressão*
(operacional), separada da `coleta/`, que é a camada de *documentação do
projeto* (decisões, trade-offs, direcionamentos).

## Arquivos vivos (só estes três ficam na raiz da pasta)

- `PLANO.md` .............. fonte de verdade do que será feito (dono: PM)
- `PROXIMA_TAREFA.md` ..... instrução única da tarefa atual (dono: PM)
- `PROGRESSO.md` .......... log append-only do que foi executado (dono: Executor)

São criados no primeiro uso real (não há stubs falsos aqui de propósito).

## Higiene (para não virar entulho)

- `historico/` — snapshots datados de plano e trechos rotacionados de progresso.
  Ao reescrever o PLANO, o PM salva a versão anterior como
  `historico/PLANO_AAAA-MM-DD.md`. Quando o PROGRESSO.md cresce muito (~40 KB)
  ou uma fase fecha, arquiva-se o concluído em `historico/PROGRESSO_<fase>.md`.
- `../tmp/` (`.claude/tmp/`) — rascunho descartável. Recomenda-se deixar fora
  do controle de versão.
- Nada de `.bak` solto nesta pasta.
