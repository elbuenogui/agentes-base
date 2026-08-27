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

### M-07 — O kit se exporta por script, nunca por cópia
`estado: fechada · 2026-08-25`

Existe um único jeito de levar este método para outro projeto: rodar
`python3 .claude/kit/exportar.py`, que **gera** o kit a partir dos arquivos vivos. **Não existe pasta
`kit/` com cópias dos arquivos**, e não deve passar a existir.

Blocos marcados com `<!-- kit:projeto:inicio -->` … `<!-- kit:projeto:fim -->` saem da cópia
exportada; blocos `<!-- kit:modelo … kit:modelo -->` entram no lugar, com `< >` para quem instalar
preencher. O que fica de fora, e por quê, está declarado no próprio script.

**Por quê:** cópia envelhece em paralelo com o original — é a mesma deriva que a `M-04` existe para
impedir, e seria irônico reproduzi-la justamente no artefato que carrega a regra. Gerado, o kit não
diverge, e exportar de novo daqui a um mês traz junto tudo que tiver melhorado no meio-tempo.

**Detalhe de implementação que é regra, não acidente:** o script **não apaga nada** — o zip é montado
direto da memória e escrito em modo de truncamento. A pasta montada de uma sessão remota recusa
remoção ("Operation not permitted"), e o script precisa rodar tanto local quanto remoto.

**Reabre se:** o kit crescer a ponto de precisar de arquivos que não existem no projeto de origem —
aí ele deixa de ser uma vista do repositório vivo e passa a ter conteúdo próprio.

### M-08 — O painel é roadmap, e a skill é genérica com configuração local
`estado: fechada · 2026-08-25`

O painel de estado passa a ter o **roadmap como espinha**: as fases percorridas com o que cada uma
entregou, onde estamos, o que vem — tudo colapsável, e cada fase apontando o **chat** em que foi
discutida. A skill `diagnostico-geral` descreve **como** montar; `.claude/painel.md` diz **quais**
arquivos ler, com que vocabulário, onde publicar e com que cara.

**Por quê:** o usuário não consegue guardar na cabeça um plano de várias fases com as especificações
e os marcos de cada uma — e quem consegue é quem lê os arquivos. O painel anterior era um retrato do
agora; este responde *onde estamos na sequência*, que é a pergunta que ele realmente faz.

**Por que configuração em arquivo, e não descoberta a cada geração:** painel que muda de forma entre
execuções deixa de ser comparável com o anterior, e comparar é metade do valor. A descoberta acontece
**uma vez**, na instalação, com o usuário junto — e vira arquivo.

**Regras de recorte que nasceram junto** (o livro-razão só cresce; a vista é que recorta): decisão
antiga vira índice de uma linha; item de backlog recusado ou morto não entra; **estimativa de esforço
não entra** — "custa duas sessões" é chute com cara de dado, e vira fato na terceira leitura.

**Reabre se:** o painel deixar de caber numa tela de rolagem confortável mesmo com tudo colapsado —
aí ele vira mais de uma página, e a espinha decide qual.

### M-09 — Skill de conta é outro destino de exportação, não uma segunda fonte
`estado: fechada · 2026-08-25`

Uma skill deste método pode ser salva na conta do usuário, ficando disponível em qualquer chat sem
depender de o repositório estar conectado. **Quando isso acontecer, a cópia de conta é gerada a
partir do arquivo vivo do repositório** — nunca editada à mão lá.

**Por quê:** é a mesma razão da `M-07`. Duas cópias editáveis da mesma regra divergem, e a de conta
é pior de perceber, porque ela some do repositório e ninguém vê que envelheceu. Tratada como destino
de exportação, ela é regenerável e a fonte continua sendo uma só.

**Consequência de desenho:** uma skill candidata a virar skill de conta **tem de aguentar rodar num
projeto que não usa este método**. Por isso a `diagnostico-geral` ganhou um passo 0 que verifica se
existe estado em arquivo e **para, dizendo isso**, em vez de inventar fase e etapa. Painel montado
sobre suposição é pior que painel nenhum: parece autoridade e é chute.

**Reabre se:** aparecer um jeito de a skill de conta apontar para o arquivo do repositório em vez de
copiá-lo — aí não há cópia, e a regra perde o motivo.

### M-10 — Exceção datada: o PM pode commitar quando o usuário autoriza na conversa
`estado: fechada · 2026-08-27`

O `PM.md` proíbe o PM de rodar comando que altere o projeto, e `git commit` está na lista. A `M-05`,
mais nova, diz que **só o usuário autoriza** o commit — *"ou ele autoriza explicitamente, ou ele
mesmo faz"*. As duas juntas deixavam ambíguo o caso em que o usuário autoriza e pede que o PM faça.

**Resolvido**: com autorização explícita do usuário na conversa, **para aquele commit**, o PM
executa. Sem autorização, continua valendo a proibição — e autorização é **por commit**, nunca por
sessão.

**Por quê:** decisão do usuário em 2026-08-27 ("pode commitar"). A regra que importa é *quem decide o
que entra no histórico*, e essa continua sendo dele; quem digita o comando é detalhe. Manter a
proibição literal obrigaria a devolver para ele um trabalho que ele acabou de mandar fazer.

**A parte que não muda**: o PM confere antes o que vai entrar. Nesta primeira aplicação a conferência
já pegou dois resíduos que não deviam ser versionados — `__pycache__` do app novo e dois logs do
`uvicorn` deixados por sessão de teste.

**Reabre se:** um commit sair errado por o PM ter interpretado autorização onde não havia — aí volta
a ser sempre do usuário.
