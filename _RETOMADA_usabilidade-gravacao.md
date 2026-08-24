# Retomada — para o PM, em chat novo

> O nome do arquivo ficou do plano antigo de propósito, para não quebrar referências. O conteúdo é
> sempre o estado **atual**. Atualizado em **2026-08-23**, no fim do chat de PM que fechou a Etapa 2
> e corrigiu o método.

## Leia nesta ordem

1. `CLAUDE.md` — porta de entrada: o papel, e as duas regras que valem em qualquer chat.
2. `.claude/CEREBRO.md` — **o mapa**: onde cada coisa mora e como o método evolui. Novo em 23/08.
3. `.claude/metodo/` — as regras: consistência, higiene, tipos de plano, commit.
4. `.claude/estado/PLANO.md` — a Fase 1: etapas 1, 2 e 6 concluídas, 5 cancelada, **3 é a próxima**.
5. `spec/VISAO.md` e `spec/DECISOES.md` — o produto e as decisões dele (`D-nn`).
6. `spec/specs/SPEC-001…` (fechada) e `spec/contrato/NUCLEO.md` (o contrato medido).
7. `spec/BACKLOG.md` — as ideias que não são etapa, com a fase em que voltam à mesa.

Se quiser o quadro geral antes de tudo: peça **diagnóstico geral** — a skill
`.claude/skills/diagnostico-geral/` monta o painel a partir desses arquivos e republica no endereço
fixo `https://claude.ai/code/artifact/cce317cd-d476-4dea-ae46-8d652cec6a3b`. **Desde 2026-08-23 ela
também confere se os arquivos concordam entre si**, e reporta o que divergir numa seção própria.

A revisão estrutural que reorganizou tudo isso está em
`https://claude.ai/code/artifact/4e228a5f-85af-41bb-a9c1-e9c6bc31c117`.

## Duas camadas, e agora elas estão separadas

- **Cérebro** (`.claude/`) — como se trabalha. Genérico, copiável para outro projeto.
- **Produto** (`spec/`, `transcritor/`) — o que se constrói. Deste projeto.

Decisão de método é `M-nn` e mora no cérebro; decisão de produto é `D-nn` e mora em `spec/`. As
quatro decisões de método que estavam no livro-razão do produto (`D-09`, `D-14`, `D-19`, `D-21`)
migraram em 23/08 e deixaram ponteiro no lugar — citação antiga continua resolvendo.

## Onde o projeto está

O `transcritor/` é a **Fase 1** de um assistente pessoal multiplataforma. A Fase 1 fecha o contrato
do núcleo; a Fase 2 (desktop, ditado universal) é a que o usuário quer usar todo dia.

**Concluído em 2026-08-23**: a Etapa 1 (contrato **medido**, não suposto) e a Etapa 2 (SPEC-001
fechada, escopo da Etapa 3 definido, método corrigido).

**Cancelada**: a Etapa 5 (parâmetro de idioma), pela condição escrita nela mesma — a medição não
achou diferença de texto, tokens ou custo (`D-08` revisada).

## O próximo passo — Etapa 3, a última de código da Fase 1

**A `PROXIMA_TAREFA.md` está gerada e é a Etapa 3.** O Executor pode abrir e executar — mas
**precisa falar com o usuário antes do primeiro comando**: a tarefa quebra o `.env` de propósito e
reinicia o backend várias vezes, e ele usa o app ao vivo.

As quatro lacunas, em `transcritor/backend/main.py`, tudo aditivo e sem tocar no `index.html`:

- **L1** — campo `codigo` estável em todo erro, oito códigos, nos dois modos. **O `detail` continua
  string em português**: o `index.html` lê ele direto, e transformá-lo em objeto quebra a interface.
- **L3** — prazo de espera de 120s de leitura e `TEMPO_ESGOTADO` com status `504` (`D-20`).
- **L2** — recusar arquivo acima do teto **antes** do upload, com `413` e mensagem dizendo o tamanho
  e o teto. O limite é **a medir e a conferir na documentação**, com data.
- **L5** — `X-Nucleo-Contrato: 1` em toda resposta de `/transcrever` e `/consumo`, sucesso e erro.

Depois dela, a Fase 1 fecha — e o critério de conclusão é duro: **alguém escreve um cliente novo
lendo só o contrato**, sem abrir o `index.html` nem o `main.py`. Quem prova isso de verdade é a
POC-1, já na Fase 2.

**Etapa 4 concluída em 2026-08-23**: harness promovido para `transcritor/teste_tempo_real.py`,
`tmp/` vazio, `_to_delete/` e `historico/snapshots/` apagados. Foi a estreia da regra `M-05` e ela
passou — repositório entregue pronto para commit, sem commit.

## O que ficou pendente do usuário

- **Q4 não tem `D-nn`**, e por escolha: "Galaxy Watch 5, em mãos" é fato de contexto, não decisão
  com trade-off. Marcada em `QUESTOES_ABERTAS.md` com "dono: este arquivo". (A Q7 estava no mesmo
  caso e foi promovida à `D-22` em 2026-08-23.)
- Nada mais. O alarme de custo ficou em US$ 100/mês (`D-18`), contra US$ 0,53 medidos em 343
  requisições de 18 a 23 de agosto.

## O que não se reabre sem motivo novo

Está tudo em `spec/DECISOES.md` com a condição de reabertura escrita. Os que mais tentam voltar:
modo ao vivo (congelado), servidor próprio (adiado com gatilho em estado compartilhado entre
aparelhos), processamento no relógio (nunca), idioma fixado em código (refutado por medição) e
qualquer trabalho em `gpt-4o-transcribe-diarize` (fora de escopo, `D-17`).

## Armadilhas do ambiente

- **Backend antigo na porta 8000** — 5 ocorrências. Conferir e derrubar antes de qualquer medição.
- **`.git/index.lock`** deixado pelo bridge remoto; o Executor apaga sozinho porque roda local.
- **Tarefa que quebra o `.env` ou o backend precisa avisar o usuário antes de começar** — ele usa o
  app ao vivo, e isso já aconteceu no meio de uma medição.

## Armadilha do próprio método (corrigida em 2026-08-23, verificar se pegou)

A Etapa 2 encontrou **seis inconsistências** entre `spec/` e `.claude/estado/` — cinco delas o mesmo
fato copiado em vários arquivos e atualizado só em alguns. Isso virou `D-19` (o mais recente vence) e
`D-21` (dono único por fato, nada de contagem à mão, passe de fechamento, e o painel confere).

Na mesma sessão, o **backlog saiu de dentro do `PLANO.md`** e virou `spec/BACKLOG.md`: ele atravessa
fases e o plano morre a cada fase, e os 60 planos arquivados congelaram cada um a sua cópia do
acervo. Cada item agora tem `nasceu:`, `estado:` e `olhar de novo em:`, e **nunca é
apagado, só muda de estado**. Ao fechar uma etapa ou fase, leia os itens marcados para a fase
seguinte e pergunte ao usuário quais sobem.

**Antes o conserto dessa deriva era sempre um aviso em prosa** — inclusive o que este arquivo
carregava, pedindo para conferir a `PROXIMA_TAREFA.md` contra o `PROGRESSO.md`. A regra 5 do `PM.md`
proíbe isso agora: aviso não é conserto. Se você notar deriva nova, corrija ou registre pendência.
