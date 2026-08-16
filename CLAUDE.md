# CLAUDE.md — <nome do projeto>

> <1-2 linhas descrevendo o projeto e, se houver, a relação com um projeto de escrita/relatório
> separado. Ex.: "Este repositório contém o código de <produto>. Além do trabalho de código,
> todo chat de trabalho pode manter uma coleta contínua para documentar decisões — ver seção
> abaixo — se o projeto tiver essa necessidade."

## Modo PM/EXEC (opt-in — ligue quando quiser)

Este repo pode operar num fluxo de **PM (planeja) + Executor (executa)**, em dois chats
separados (ex.: um chat de conversa/planejamento = PM; a extensão do assistente no editor de
código = Executor). O modo é **opcional** e ligado pela primeira mensagem do chat:

- Primeira mensagem **"PM"** → leia `.claude/PM.md` e siga aquelas regras. Você **não executa**.
- Primeira mensagem **"EXEC"** → leia `.claude/EXECUTOR.md` e siga aquelas regras. Você **não
  planeja**.
- **Nenhum dos dois declarado** → trabalho normal do repo, sem modo PM/EXEC. Não é preciso
  perguntar o papel.

Estado do modo (só os três arquivos vivos ficam na raiz de `.claude/estado/`; higiene e
histórico em `.claude/estado/README.md`):

- `.claude/estado/PLANO.md` .............. fonte de verdade do que será feito (PM)
- `.claude/estado/PROXIMA_TAREFA.md` ..... instrução única da tarefa atual (PM)
- `.claude/estado/PROGRESSO.md` .......... log append-only do que foi executado (Executor)

Se `.claude/estado/` não existir, crie-a antes de escrever. Nenhum desses três arquivos deve
existir como stub vazio — nascem no primeiro uso real.

## Duas camadas, não confundir

- **Progressão** (execução) → `.claude/estado/`. Operacional; canal PM ↔ Executor.
- **Documentação do projeto** (decisões, trade-offs, direcionamentos) → `coleta/`. Curada e
  seletiva. <Se houver um projeto de escrita/relatório separado, diga o nome dele aqui e ajuste a
  seção abaixo. Se não houver, remova a menção a "aplicar" e trate a coleta como registro interno
  do próprio projeto.> **Dono da coleta é o PM** — o executor só reporta no PROGRESSO.

## Coleta contínua (opcional — mantenha se o projeto precisa reconstruir "por que decidimos assim")

Em todo chat de trabalho, use a skill `coleta-consolidacao`:

- registre por interação em `coleta/AAAA-MM-DD_<tema>.md` (um arquivo por chat), marcando cada
  item com `[DECISÃO]` (com trade-off), `[ARTEFATO]`, `[DIRECIONAMENTO]` ou `[PENDÊNCIA]`; nunca
  reescreva linhas anteriores;
- no comando **"consolidar"** (ou ao encerrar), gere o resumo nas quatro categorias para revisão.

<Se existir um projeto de escrita/relatório separado:> **Não aplique ao mestre aqui** — leve o
**resumo** para <nome do projeto de escrita> e lá use **"aplicar"**. Travas: não inventar; o
resumo é proposta; nada entra no relatório sem sua aprovação.

*(A skill `coleta-consolidacao` fica em `.claude/skills/coleta-consolidacao/SKILL.md`.)*
