# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de 2026-08-21 (plano de faxina e fechamento). As entradas dos
> planos anteriores foram movidas para `.claude/estado/historico/` (arquivos `PROGRESSO_*.md`),
> sem edição — o vivo guarda só o plano em andamento. O plano imediatamente anterior
> (usabilidade da interface de gravação, 2026-08-20 a 2026-08-21) está em
> `.claude/estado/historico/PROGRESSO_usabilidade-gravacao_2026-08-20_a_2026-08-21.md`.

## [2026-08-21] — Enxugar o histórico do método, Etapa 2
Status: concluído

### Feito
Só movimentação de arquivo (`mv`), nenhum conteúdo editado — o `.git/index.lock` já estava
presente (esperado, é o que bloqueia a Etapa 3 até o usuário apagar), então nada aqui passou por
`git` (nem `git mv`), só sistema de arquivos direto.

- Criei `.claude/estado/historico/snapshots/`.
- Descobri por `grep` (não de memória) todo `PLANO_2026-08-*.md` citado por nome fora de
  `historico/` — 8 além dos marcos já listados na tarefa, todos em `coleta/2026-08-16_mvp-transcricao.md`
  (citações de "snapshot arquivado em..." junto de decisões/artefatos, não citações dentro de
  outro snapshot): `PLANO_2026-08-18c.md`, `PLANO_2026-08-18f.md`, `PLANO_2026-08-19b.md`,
  `PLANO_2026-08-19c.md`, `PLANO_2026-08-19d.md`, `PLANO_2026-08-19e.md`, `PLANO_2026-08-19f.md`,
  `PLANO_2026-08-19g.md`. Ficaram na raiz de `historico/` junto dos marcos.
- Movi os outros 48 arquivos (a série de edição sem citação externa) para `snapshots/`.
- Movi `_RETOMADA_robustez-consumo.md` e `_RETOMADA_transcricao-tempo-real.md` da raiz do
  repositório para `.claude/estado/historico/` (raiz, não `snapshots/`).

### Contagens (pedidas explicitamente)
- `historico/` antes: **63 arquivos** (a tarefa estimava "60" — contei de verdade,
  `ls -1 | wc -l`, deu 63).
- `historico/` depois: raiz **17** (7 marcos + 8 citados pelo grep + as 2 retomadas que chegaram)
  + `snapshots/` **48** = **65** no total — bate com 63 (o que já havia) + 2 (retomadas que
  entraram), nada apagado.
- Raiz do repositório: `_RETOMADA_*.md` foi de 4 para 2 (`_RETOMADA_TEMPLATE.md` e
  `_RETOMADA_usabilidade-gravacao.md`, intocados).

### Verificação de referências (repositório inteiro, fora de `.git/` e `.venv/`)
Grep por todo padrão `historico/ARQUIVO.md` e `_RETOMADA_*.md` no repo (265 referências
encontradas) e conferido se o arquivo existe no caminho citado (raiz de `historico/` ou
`snapshots/`, ou raiz do repo para as retomadas vivas): **zero referências quebradas**. As duas
únicas ocorrências que o grep sinalizou como "não resolve" eram o padrão-modelo
`PLANO_AAAA-MM-DD.md` (data literal, não um arquivo real) em `.claude/PM.md` e
`.claude/estado/README.md` — documentação do formato de nome, não uma citação de arquivo.
Nenhuma referência precisou de correção.

Os dois `_RETOMADA_*.md` movidos se auto-citam como "(raiz)" no próprio texto (ex.: linha 81 de
`_RETOMADA_robustez-consumo.md`) — ficou desatualizado depois da mudança de lugar, mas não
mexi: é conteúdo de retomada arquivada, e a tarefa proíbe editar conteúdo de retomada.

### Critério de pronto
- [x] `historico/snapshots/` existe e contém os snapshots de edição (48)
- [x] Raiz de `historico/` com 17 arquivos (7 marcos + 8 citados pelo grep + 2 retomadas) — mais
      que os "~7" estimados na tarefa, porque o grep achou 8 citações reais que a estimativa não
      previa; contagem colada acima
- [x] Nenhum arquivo apagado — conta colada acima (63+2=65 = 17+48)
- [x] As duas retomadas de frentes encerradas saíram da raiz; `_RETOMADA_usabilidade-gravacao.md`
      e `_RETOMADA_TEMPLATE.md` continuam lá, intocados
- [x] Nenhuma referência quebrada — resultado colado acima (265 checadas, 0 quebradas)
- [x] Nenhum arquivo teve o conteúdo alterado — só `mv`, nenhuma correção de referência foi
      necessária

### Novas demandas / riscos
- Nenhum novo.

### Ajuste no plano necessário?
Não.
