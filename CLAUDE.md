# CLAUDE.md — Assistente de Pesquisa por Áudio

> Este repositório contém o código do Assistente de Pesquisa por Áudio: MVP de um motor mínimo
> de transcrição (áudio → API OpenAI → transcrição), na pasta `transcritor/`. Não há projeto de
> escrita/relatório separado — a coleta contínua (seção abaixo) é registro interno do próprio
> projeto.

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

## Idioma

Todo o trabalho deste repositório é em **português do Brasil** — a conversa nos dois papéis (PM e
Executor), o `PROGRESSO.md`, o `PLANO.md`, a `PROXIMA_TAREFA.md`, a `coleta/`, o `README.md` do
`transcritor/` e os comentários de código. Nomes de identificadores no código seguem o padrão que
já existe no arquivo. Regra escrita em 2026-08-20, depois de o Executor responder em inglês num
chat de execução.

## Duas camadas, não confundir

- **Progressão** (execução) → `.claude/estado/`. Operacional; canal PM ↔ Executor.
- **Documentação do projeto** (decisões, trade-offs, direcionamentos) → `coleta/`. Curada e
  seletiva. Não há destino final separado: a coleta é registro interno do próprio projeto, sem
  passo de "aplicar". **Dono da coleta é o PM** — o executor só reporta no PROGRESSO.

## Coleta contínua (opcional — mantenha se o projeto precisa reconstruir "por que decidimos assim")

Em todo chat de trabalho, use a skill `coleta-consolidacao`:

- registre por interação em `coleta/AAAA-MM-DD_<tema>.md` (um arquivo por chat), marcando cada
  item com `[DECISÃO]` (com trade-off), `[ARTEFATO]`, `[DIRECIONAMENTO]` ou `[PENDÊNCIA]`; nunca
  reescreva linhas anteriores;
- no comando **"consolidar"** (ou ao encerrar), gere o resumo nas quatro categorias para revisão.

Como não há destino final separado, o comando **"aplicar"** não é usado neste projeto — o
resumo consolidado já é o produto final da coleta. Travas: não inventar; o resumo é proposta
para sua revisão.

*(A skill `coleta-consolidacao` fica em `.claude/skills/coleta-consolidacao/SKILL.md`.)*
