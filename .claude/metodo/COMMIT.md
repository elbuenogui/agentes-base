# Commit: quem autoriza, e o que se deixa pronto

> Camada: **cérebro** (genérico). Vale nos **três modos** — PM, Executor e chat sem papel declarado.
> Citada em `../../CLAUDE.md`, `../PM.md` e `../EXECUTOR.md`; escrita só aqui.

## Só o usuário autoriza o commit

Ou ele autoriza explicitamente, ou ele mesmo faz. **Nem o PM nem o Executor commitam por iniciativa
própria**, e isso não muda porque a tarefa "claramente terminou" ou porque o commit "é óbvio".

Vale também para o chat que **não declara papel**. É o modo mais desprotegido justamente porque
ninguém percebe: sem papel declarado não há regra de papel, e é aí que um commit não autorizado
escapa. Por isso esta regra é citada nas três portas de entrada.

O mesmo vale para qualquer coisa que publique ou desfaça trabalho: `push`, `reset --hard`, `rebase`,
apagar branch, reescrever histórico. Autorização é **por ação**, não por sessão: um "pode commitar"
não vale para o commit seguinte.

## O Executor entrega o repositório pronto para commit

Terminar a tarefa inclui deixá-la commitável. Se o usuário precisa apagar arquivo na mão para
conseguir commitar, **a tarefa não terminou** — isso é falha de entrega, não detalhe de ambiente.

Antes de reportar "concluído", confira:

- [ ] **`.git/index.lock` não existe.** Ele é deixado para trás por comando de git interrompido — e
      qualquer sessão que só alcance o repositório por pasta montada **não consegue apagá-lo**. Quem
      roda local consegue: apague.
- [ ] **Nenhum `.fuse_hidden*` solto.** Resíduo de arquivo apagado enquanto estava aberto pela pasta
      montada. Estão no `.gitignore`, mas continuam ocupando espaço e confundindo busca.
- [ ] **Nenhum temporário fora da pasta de rascunho** — nada de `.bak`, `.tmp` ou arquivo de teste
      espalhado pelo repositório.
- [ ] **`git status` só mostra o que pertence à tarefa.** Arquivo modificado que a tarefa não pedia
      é ou engano, ou algo que precisa ser reportado antes — nunca "vai junto".
- [ ] **Artefato de teste removido**: áudio, dump, log, chave de exemplo, backup de configuração.

Se algum item não puder ser resolvido, **diga qual e por quê** no registro de progresso, em vez de
deixar para o usuário descobrir na hora de commitar.

## O que o PM faz

Nada de git além de leitura. Comandos de leitura (`git log`, `git diff`) são permitidos; qualquer um
que altere o repositório, não.

**Cuidado específico do PM em sessão remota**: rodar `git status` pela pasta montada deixa o
`index.lock` para trás e **quebra o commit seguinte**, sem aviso. Prefira `git log` e `git diff`, que
não escrevem o lock.
