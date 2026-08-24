# Higiene: o que se guarda, o que se joga fora, e quando

> Camada: **cérebro** (genérico). Vale para os dois papéis.

Todo projeto que documenta o próprio processo acumula. O problema não é o peso — é que o acúmulo
**atrapalha quem procura**: uma busca por "por que isso foi recusado" que devolve dezenas de cópias
de vintages diferentes é pior do que não achar nada, porque a mais recente não é a que aparece
primeiro.

Cada regra abaixo tem **gatilho declarado**. Higiene que depende de boa vontade não acontece.

## Snapshot de plano: limiar, não reflexo

Salvar a versão anterior do plano antes de reescrever é certo. Salvar a cada ajuste de uma linha
não é — vira uma pilha de salvamentos quase idênticos que ninguém consegue ler como história.

- **Gatilho**: salva em **virada de plano** (plano fechado ou substituído), ou quando a reescrita
  mudar mais do que umas poucas linhas. Marcar uma etapa como concluída não é reescrita.
- **Nome**: o snapshot de virada leva o motivo no nome (`PLANO_AAAA-MM-DD_<o-que-fechou>.md`), para
  a pasta de histórico se ler como uma sequência de decisões e não como um log.

## Arquivamento do progresso: o gatilho é a virada, não o tamanho

Quando um plano fecha, mova **todas as entradas daquele plano** do log vivo para o histórico,
preservadas palavra por palavra. É o corte natural: entrada de plano encerrado não é mais consultada
para executar, só como história.

**Tamanho é alarme, não gatilho.** Se o arquivo vivo crescer muito com o plano ainda aberto, isso não
significa "arquive" — significa que o plano está se arrastando ou que a regra de profundidade de
registro não está sendo seguida. Avise, não arquive no meio.

## Temporários: nada de valor mora no descartável

A pasta de rascunho (`.claude/tmp/`) existe para ser apagada. A regra que costuma faltar é a inversa
da óbvia:

- **Se um arquivo do rascunho passou a ter valor, promova na hora** para o lugar dele, versionado.
  Descobrir que o único arquivo aproveitável do projeto mora na pasta que existe para sumir é um
  acidente esperando acontecer.
- **O que ficar sem toque até a virada de plano seguinte sai na limpeza**, sem pergunta.

## Diário do projeto: um arquivo por thread, com corte

O registro cronológico (`coleta/`) é append-only por natureza, e append-only sem regra de corte
sempre vira arquivo que ninguém abre. Um tema que dura semanas ganha **um arquivo por thread de
trabalho**, não um arquivo por tema — quando o assunto continua noutra frente, começa arquivo novo
apontando para o anterior.

## Lixo de ferramenta: ignorar antes de acumular

Ambientes que acessam o repositório por pasta montada (bridge remoto) deixam resíduo que **não se
consegue apagar de lá** — o sistema recusa com *"Operation not permitted"*:

- `.fuse_hidden*` — arquivos apagados enquanto estavam abertos;
- `.git/index.lock` — deixado para trás por qualquer comando de git interrompido, e que faz o
  **commit seguinte falhar**.

Duas providências, e as duas são baratas:

1. **No `.gitignore`**, para que nunca sejam commitados por engano: `.fuse_hidden*` e `_to_delete/`.
2. **Quem roda local apaga.** Quem só alcança a pasta montada **move** para `_to_delete/` e avisa o
   que moveu. O `.git/index.lock` é caso especial: ele bloqueia o commit, então apagá-lo é parte de
   deixar o repositório pronto (ver `COMMIT.md`).

## Hierarquia de pastas: só quando há razão

Pasta nova nasce quando **um grupo de arquivos passa a ter leitores diferentes** ou um ciclo de vida
diferente — não para organizar por organizar. Três arquivos soltos não justificam pasta; três
arquivos que só um papel lê, sim.

E quando a estrutura cresce a ponto de alguém não achar um arquivo, o conserto é **um mapa de alto
nível num lugar só** (ver `../CEREBRO.md`), não um README por pasta.
