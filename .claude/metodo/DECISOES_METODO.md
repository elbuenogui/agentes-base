# Decisões de método — livro-razão do cérebro

> **O que é genérico e o que não é**: as regras em `CONSISTENCIA.md`, `HIGIENE.md`, `PLANOS.md` e
> `COMMIT.md` são do kit e vão junto quando ele for copiado. **Este arquivo não vai.** Ele registra
> o que *esta instalação* decidiu, com a razão e a condição de reabertura. Projeto novo começa com
> ledger vazio — herda as regras, não as escolhas.

Formato: `### M-nn — título` · `estado:` · a decisão · **Por quê** · **Reabre se**.

---

### M-01 — A verificação é manual, e isso está declarado
`estado: fechada · 2026-08-21` · *antes `D-09` no livro-razão do produto*

Sem suíte automatizada enquanto o projeto for simples. Critérios de aceitação se cumprem por medição
manual registrada no log de progresso, com evidência colada.

**Por quê:** montar suíte custa tempo e chamada de API paga a cada execução, e o sistema ainda é
pequeno demais para pagar isso.
**Reabre se:** houver mais de um cliente consumindo o núcleo — aí verificação manual deixa de cobrir.

### M-02 — Estado de projeto se lê em painel, não em prosa
`estado: fechada · 2026-08-21` · *antes `D-14`*

Quando o usuário pedir o panorama, a resposta é um **painel visual publicado**, montado a partir dos
arquivos — nunca um texto longo no chat. O painel é **vista**, nunca fonte de verdade: o que não
está em arquivo não entra nele.

**Por quê:** é o formato em que este usuário consegue aprovar ou recusar. Painel também obriga o
estado a existir em arquivo antes de ser mostrado, o que é uma trava útil por si só.
**Reabre se:** —
*(O endereço fixo do painel e a identidade visual são deste projeto e moram na skill, não aqui.)*

### M-03 — Entre dois documentos que se contradizem, o mais recente vence
`estado: fechada · 2026-08-23` · *antes `D-19`*

E o perdedor é corrigido na mesma sessão, não anotado como divergência conhecida. Regra escrita em
`CONSISTENCIA.md`, item 4.

**Por quê:** decisão do usuário, ao ver a mesma pergunta com três respostas diferentes em três
arquivos. Sem regra de desempate, cada leitor julga qual versão vale — que é como uma inconsistência
vira duas. A data já existe em todo artefato, então aplicar não custa nada.
**Reabre se:** —

### M-04 — Todo fato tem dono único, e o passe de conferência confere
`estado: fechada · 2026-08-23` · *antes `D-21`*

As cinco regras de `CONSISTENCIA.md`, mais a conferência automática descrita no fim daquele arquivo.

**Por quê:** numa varredura de 2026-08-23, das nove inconsistências encontradas entre os documentos
do projeto, a maioria era o mesmo fato copiado em vários arquivos e atualizado só em alguns. E o
método já tinha detectado essa deriva duas vezes antes — nas duas, o conserto foi um aviso em prosa,
e a deriva voltou. A regra que sustenta as outras é a última: **transformar disciplina, que falha em
silêncio, numa conferência que roda junto de algo que já se pede.**
**Reabre se:** o passe de conferência ficar caro ou barulhento a ponto de o usuário parar de pedir o
painel. Aí ele vira comando separado, não deixa de existir.

### M-05 — Só o usuário autoriza commit; o Executor entrega pronto
`estado: fechada · 2026-08-23`

Nem o PM nem o Executor commitam por iniciativa própria, e isso vale inclusive no chat sem papel
declarado. O Executor termina a tarefa com o repositório **commitável** — sem lock preso, sem
resíduo do bridge, sem temporário solto, e com o `git status` mostrando só o que pertence à tarefa.
Regra escrita em `COMMIT.md`.

**Por quê:** decisão do usuário. Commit é o ponto em que trabalho vira histórico compartilhado — quem
decide o que entra é quem responde por ele. E o lado prático: o usuário vinha tendo de apagar
arquivo na mão para conseguir commitar, porque a sessão remota não consegue apagar pela pasta
montada e a tarefa não considerava isso parte da entrega.
**Reabre se:** —

### M-06 — O cérebro mora em `.claude/`
`estado: fechada · 2026-08-23`

A camada de método — papéis, regras, skills, estado — mora em `.claude/`, declarada em
`.claude/CEREBRO.md`. O produto mora fora dela.

**Por quê:** decisão do usuário. É onde as ferramentas já procuram e onde metade da camada já morava;
pasta nova seria mais legível para humano e pior para máquina.
**Reabre se:** —
