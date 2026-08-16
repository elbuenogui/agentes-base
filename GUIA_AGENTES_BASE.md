# Guia dos agentes base (PM / Executor / coleta / retomada)

Este documento explica, de forma independente de qualquer projeto específico, como funciona o
conjunto de padrões deste kit. Leia antes de instalar o kit num projeto novo, para decidir o que
faz sentido usar e o que pode simplificar.

## O problema que isso resolve

Trabalhar com um assistente de IA num projeto que dura semanas, com várias sessões de chat, tem
três riscos recorrentes:

1. **Mistura de papéis**: no mesmo fôlego, o assistente planeja e já sai executando — e quando o
   plano muda de ideia no meio do caminho, o código/artefato já foi alterado sem aprovação.
2. **Perda de contexto entre chats**: cada chat novo começa do zero; ou você reexplica tudo, ou o
   assistente assume coisas erradas sobre o que já foi decidido.
3. **Rastro que evapora**: decisões importantes (e os trade-offs por trás delas) só existem na
   rolagem do chat; quando você precisa delas depois (para um relatório, para justificar uma
   escolha, para auditoria), elas se foram.

Os quatro mecanismos abaixo — papéis PM/Executor, canal de progressão, coleta contínua e
retomada — atacam cada um desses riscos separadamente. Você pode adotar só os que fizerem sentido
para o projeto novo; eles não são pacote fechado.

## 1. Papéis PM e Executor

**Resolve**: mistura de planejamento e execução.

É um modo **opt-in**, ligado pela primeira mensagem do chat:

- primeira mensagem **"PM"** → o assistente lê `.claude/PM.md` e assume esse papel: só planeja,
  coordena e registra. Não edita nada do projeto além dos arquivos de estado e da coleta.
- primeira mensagem **"EXEC"** → o assistente lê `.claude/EXECUTOR.md` e assume esse papel: só
  executa a tarefa corrente, exatamente como especificada. Não planeja, não lê o plano inteiro
  para "adiantar", não decide escopo.
- nenhuma das duas → chat normal, sem o modo. Não é preciso perguntar o papel.

Na prática isso costuma rodar em **dois chats diferentes** (ex.: um chat de conversa/planejamento
e outro ligado ao editor de código onde a execução acontece), mas também funciona no mesmo chat
se você alternar as mensagens "PM" e "EXEC" conscientemente.

O ponto central: o PM **não pode** editar código, rodar comando que altere o projeto, nem
executar a tarefa "porque é rápido". O Executor **não pode** decidir o que fazer além do que está
escrito na tarefa corrente — se algo estiver ambíguo, ele para e registra a dúvida em vez de
improvisar. Essa fricção deliberada é o que impede decisões silenciosas de vazarem para dentro do
projeto.

## 2. Canal de progressão (`estado/`)

**Resolve**: como PM e Executor conversam sem estarem no mesmo chat.

Três arquivos, cada um com um dono único:

- `PLANO.md` (dono: PM) — a fonte de verdade do que será feito. Tem Objetivo, Escopo
  (dentro/fora explícito), Etapas (com critério de pronto verificável cada) e Backlog (ideias
  ainda não aprovadas).
- `PROXIMA_TAREFA.md` (dono: PM) — a instrução da etapa **atual**, uma por vez: contexto,
  arquivos envolvidos, o que fazer, critério de pronto, e um "o que NÃO fazer" explícito. É
  sobrescrito a cada nova tarefa — não acumula histórico.
- `PROGRESSO.md` (dono: Executor) — log **append-only** do que foi executado: o que foi feito,
  se o critério de pronto foi atendido, diagnóstico técnico e "novas demandas/riscos" que o
  Executor encontrou mas não consertou (porque estava fora de escopo).

Regras de construção do plano que vale a pena manter em qualquer projeto:

- **Máximo ~7 etapas** por plano — se passar disso, considere dividir em mais de um plano.
- **Todo critério de pronto tem que ser verificável.** Nada de "melhorar performance" sem dizer o
  que "melhor" significa em número ou comportamento observável.
- **Nunca adicionar etapa por iniciativa própria.** Ideia nova no meio do caminho vai para o
  Backlog; só sobe para Etapas se você mandar explicitamente.
- **Antes de gravar o plano, mostrar e perguntar "aprova ou ajusto?"** — o plano não é um
  rascunho que o PM decide sozinho.
- Ao reescrever o plano de forma relevante, guardar a versão anterior em
  `estado/historico/PLANO_<data>.md` antes de sobrescrever.

E ao receber o retorno do Executor, o PM confere o critério de pronto **no próprio artefato**
(código, documento), não só no relato — e só então marca a etapa como concluída.

Quando o `PROGRESSO.md` cresce demais (na ordem de dezenas de KB) ou uma fase fecha, o conteúdo
já concluído vai para `estado/historico/PROGRESSO_<fase>.md`, deixando no arquivo vivo só o
recente. Rascunho descartável (de qualquer papel) vai em `.claude/tmp/`, que fica fora do
histórico e normalmente fora do controle de versão.

## 3. Coleta contínua e consolidação

**Resolve**: decisões e trade-offs que evaporam junto com a rolagem do chat.

Separada da camada de progressão de propósito: `estado/` é operacional (o que fazer agora);
`coleta/` é **documentação do projeto** — o material que algum dia vira relatório, retrospectiva,
justificativa de decisão, ou simplesmente "por que fizemos assim". Só faz sentido manter essa
camada se você antecipa precisar reconstruir esse histórico depois — em projetos curtos e de um
chat só, ela é peso morto.

Mecânica:

- **Um arquivo por chat/tema**: `coleta/AAAA-MM-DD_<tema>.md`.
- **Registro por interação**, uma linha por item, sempre marcada com uma das quatro tags:
  - `[DECISÃO]` — sempre acompanhada do trade-off (`— trade-off: ...`);
  - `[ARTEFATO]` — algo produzido, com caminho;
  - `[DIRECIONAMENTO]` — orientação nova ou alterada;
  - `[PENDÊNCIA]` — o que ficou em aberto, com `— depende de: ...`.
- **Nunca reescrever linha anterior** — é log, não rascunho. Se algo mudou, registra-se uma nova
  linha, não se edita a antiga.
- Comando **"consolidar"** (ou ao encerrar o chat): o assistente agrupa tudo em um resumo nas
  quatro categorias, pronto para ser revisado por você.
- Comando **"aplicar"** (opcional — só se existir um projeto de escrita/relatório separado, ou
  uma seção equivalente dentro do próprio projeto): leva o resumo consolidado para esse destino,
  sempre como proposta a validar, nunca direto.

Travas anti-alucinação que valem a pena manter: nunca inventar decisão, número ou versão — só
registrar o que de fato aconteceu no chat; o resumo consolidado é proposta, nada entra em
documento final sem sua aprovação; datas relativas ("ontem", "semana passada") viram datas
absolutas no momento do registro.

## 4. Retomada

**Resolve**: reabrir um chat depois de um tempo sem perder o fio.

Um arquivo `_RETOMADA_<tema>.md` por frente de trabalho ativa, com uma ordem de leitura
recomendada ("Situar-se" — só o relevante, não tudo), o estado atual em poucas linhas, o próximo
passo, pendências com "depende de: quem/o quê", onde as coisas ficam no projeto, e — a parte mais
usada na prática — uma **mensagem pronta para colar** no chat novo, que já inclui a palavra "PM"
ou "EXEC" se for o caso.

A regra que evita divergência: a retomada (mais o `PLANO.md`/matriz do projeto, se houver) é a
**fonte da verdade** sobre "onde estamos" — nunca duplicar esse resumo narrativo dentro de
`PROXIMA_TAREFA.md` ou de outro arquivo operacional, porque são exatamente esses resumos
duplicados que ficam desatualizados primeiro.

## Quando NÃO vale a pena usar isso

- Projeto pequeno, que você espera fechar num chat só ou em poucos dias.
- Você mesmo é quem planeja e executa, sem alternar contexto nem se afastar por dias — o overhead
  de manter PLANO/PROGRESSO/coleta sincronizados supera o benefício.
- Não há necessidade de reconstruir "por que decidimos assim" depois (nesse caso, pule a coleta e
  fique só com PM/EXEC + retomada, ou nem isso).

## Adaptando para um projeto novo

1. Decida quais dos quatro mecanismos você quer (nem sempre são os quatro).
2. Copie os arquivos correspondentes deste kit (ver `README.md`) para o projeto novo.
3. Substitua os placeholders `< >` pelo contexto real do projeto.
4. Se o projeto não tem uma frente de documentação/relatório separada, simplifique a skill de
   coleta removendo o passo "aplicar" (fica só registro + consolidar).
5. No primeiro chat "PM" do projeto novo, peça para o assistente montar o `PLANO.md` inicial —
   ele vai seguir a estrutura descrita em `.claude/PM.md`.
