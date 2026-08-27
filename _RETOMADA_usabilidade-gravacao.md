# Retomada — para o PM, em chat novo

> O nome do arquivo ficou do plano antigo de propósito, para não quebrar referências. O conteúdo é
> sempre o estado **atual**. Última atualização: **2026-08-25**, no encerramento do chat de PM que
> fechou a Fase 1, abriu a Fase 2, escopou a POC-1 e tornou o kit exportável. Atualizado em **2026-08-23**, no fim do chat de PM que fechou a Etapa 2
> e corrigiu o método.

## Leia nesta ordem

1. `CLAUDE.md` — porta de entrada: o papel, e as duas regras que valem em qualquer chat.
2. `.claude/CEREBRO.md` — **o mapa**: onde cada coisa mora e como o método evolui. Novo em 23/08.
3. `.claude/metodo/` — as regras: consistência, higiene, tipos de plano, commit.
4. `.claude/estado/PLANO.md` — a Fase 1: etapas 1, 2 e 6 concluídas, 5 cancelada, **3 é a próxima**.
5. `spec/VISAO.md` e `spec/DECISOES.md` — o produto e as decisões dele (`D-nn`).
6. `spec/specs/SPEC-001…` (fechada) e `spec/contrato/NUCLEO.md` (o contrato medido).
7. `spec/BACKLOG.md` — as ideias que não são etapa, com a fase em que voltam à mesa.

Se quiser o quadro geral antes de tudo: peça **diagnóstico geral** (skill em
`.claude/skills/diagnostico-geral/`; a tabela de comandos está no `CLAUDE.md` e no `CEREBRO.md`). Desde 2026-08-25 o painel é um
**roadmap colapsável** — as fases percorridas com o que cada uma entregou, onde estamos, o que vem, e
o **rastro até o chat** de cada etapa. A skill descreve *como* montar; `.claude/painel.md` diz *quais*
arquivos ler, o vocabulário, o endereço fixo e a identidade visual (`M-08`).

Endereço atual: `https://claude.ai/code/artifact/5727fb8f-851a-4fd9-8a83-024bcbf76d9e`.
A skill também **confere se os arquivos concordam entre si** e reporta numa seção própria — que
aparece mesmo vazia, porque silêncio não distingue "conferi" de "não conferi".

A revisão estrutural que reorganizou tudo isso está em
`https://claude.ai/code/artifact/4e228a5f-85af-41bb-a9c1-e9c6bc31c117`.

## Levar este método para outro projeto

`python3 .claude/kit/exportar.py` gera o kit portátil a partir dos arquivos vivos — zip e pasta em
`.claude/tmp/`. Para levar **uma skill sozinha** (salvar na conta ou usar em outro projeto):
`python3 .claude/kit/exportar.py --skill <nome>`, que empacota a pasta dela num `.skill`. **Nunca copie a mão** (`M-07`): cópia envelhece em paralelo com o original. O script
diz, ao rodar, o que deixou de fora e por quê.

## Duas camadas, e agora elas estão separadas

- **Cérebro** (`.claude/`) — como se trabalha. Genérico, copiável para outro projeto.
- **Produto** (`spec/`, `transcritor/`) — o que se constrói. Deste projeto.

Decisão de método é `M-nn` e mora no cérebro; decisão de produto é `D-nn` e mora em `spec/`. As
quatro decisões de método que estavam no livro-razão do produto (`D-09`, `D-14`, `D-19`, `D-21`)
migraram em 23/08 e deixaram ponteiro no lugar — citação antiga continua resolvendo.

## Onde o projeto está

**A Fase 1 encerrou em 2026-08-24.** O contrato do núcleo está medido, fechado e corrigido: códigos
de erro legíveis por máquina, prazo de espera declarado, teto de tamanho e versão do contrato. O
`transcritor/` está em uso todo dia.

**A Fase 2 abriu**: desktop, ditado universal — atalho, fala, texto no campo em foco. É a fase que o
usuário quer usar todo dia, e ela **encerra com uso em regime, não com o app pronto** (`D-24`).

**Ressalva que não se pode perder**: o critério de conclusão da Fase 1 — *"alguém escreve um cliente
novo lendo só o contrato, sem abrir o `index.html` nem o `main.py`"* — **ainda não foi exercido por
ninguém**. Quem exerce é a POC-1. Se o contrato não bastar, a Fase 1 reabre com evidência de uso
real, e isso é esperado, não fracasso.

## Onde parou

**A Etapa 1 foi entregue em 2026-08-26**: `desktop/app.py`, o primeiro cliente do núcleo fora do app
web — atalho configurável, gate de silêncio por RMS, erros tratados pelo `codigo`, texto no
clipboard. Conferido pelo PM no artefato real.

**O critério da Fase 1 foi respondido**: o contrato **bastou**, com uma lacuna só — não declarava
onde o núcleo escuta. Dois clientes independentes tropeçaram na mesma coisa, o que é a melhor
evidência de que era lacuna real. Fechada no `NUCLEO.md`.

**`D-26`, o achado mais importante e que veio de graça**: a inserção automática de texto (`B-22`) tem
de disparar **de dentro do handler do atalho global** — de um processo desacoplado, o Windows recusa
e a injeção falha **em silêncio**. Descoberto na tentativa parcial da POC-1, antes do corte de
escopo. O app já nasceu na arquitetura certa por acidente.

## O próximo passo — está com o usuário

**Não há tarefa de Executor**, e é proposital. Duas pontas do app não puderam ser testadas porque o
ambiente do Executor não tem microfone nem teclado físico:

- o **atalho global funciona com outra janela em foco**?
- a **captura por microfone real** grava e transcreve?

`python desktop/app.py`, uma vez. São as únicas coisas entre o app e o uso diário — que é o critério
de encerramento da fase (`D-24`).

**Áudio de fala real disponível**: `audio-teste/fala-real.wav`, 32 segundos, entregue pelo usuário
em 2026-08-27 (convertido de `.wma`, que a API não aceita). Até então só havia tom sintético.

**Já na fila para a próxima tarefa**: isolar o `pyperclip.copy()` numa função própria (`D-11`) — hoje
está inline em `_processar_gravacao`, e é exatamente o pedaço que a inserção automática vai trocar.
Desvio encontrado pelo PM no artefato, não relatado pelo Executor.

## O que ficou pendente do usuário

1. **Abrir o chat do Executor com a POC-1**, num momento em que possa acompanhar — a PoC digita de
   verdade nas janelas abertas dele.
2. ~~Teste manual de gravação por microfone~~ — **retirado em 2026-08-25**. A Etapa 3 não encostou
   no caminho de gravação, e o teste por upload exercitou a mesma rota e o mesmo tratamento de erro.
   Era cautela herdada da recomendação do Executor, repassada sem ser pesada.
3. **Commit** do trabalho desta sessão — só o usuário autoriza (`M-05`). O
   `transcritor/BENCHMARK.md` está modificado desde antes e ele decide se entra.
4. **Q4** (Galaxy Watch) segue sem `D-nn`, por escolha: é fato de contexto, não decisão com
   trade-off. Marcada em `QUESTOES_ABERTAS.md` com "dono: este arquivo".

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
