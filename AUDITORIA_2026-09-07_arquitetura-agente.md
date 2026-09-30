---
artefato: AUDITORIA
escopo: arquitetura e orquestração de agente no repositório `agentes-base`
data: 2026-09-07
metodo: leitura direta dos arquivos na máquina do usuário (shell), contagens medidas, sem edição de nenhum arquivo do projeto
papel: nenhum — auditoria externa ao ciclo PM/EXEC; nada em `.claude/estado/` foi tocado
---

# Auditoria de arquitetura e orquestração — `agentes-base`

> **Nota de papel.** O `CLAUDE.md` deste repositório manda declarar "PM" ou "EXEC" na primeira
> mensagem, e perguntar quando não for declarado. Esta auditoria não é nem uma coisa nem outra: é
> leitura, e por isso rodou no terceiro modo previsto pelo próprio arquivo ("trabalho normal, sem o
> modo"). **Nada foi editado, movido, apagado ou commitado.** O único arquivo escrito é este
> relatório.

---

## 0. O achado que reordena a leitura de tudo que vem depois

**Não existe agente dentro deste repositório.** Não há orquestrador, roteador, framework, hook,
configuração de permissão, definição de subagente, servidor MCP nem qualquer código que decida
alguma coisa.

**Evidência (medida, não inferida):**

- Busca por `settings*.json`, `.mcp.json`, `hooks*`, pasta `agents/`, pasta `commands/` em todo o
  repositório (exceto `.git/` e `.venv/`): **zero resultados**.
- `.claude/` contém, no primeiro nível: **4 arquivos `.md`, 5 pastas** e um `scheduled_tasks.lock`
  (124 bytes, resíduo de cliente, de 21/08). **Nenhum arquivo de configuração.**
- O único executável de método no repositório é `.claude/kit/exportar.py` — e ele **não orquestra
  nada**: gera um zip a partir dos `.md` vivos.

O que existe é um **protocolo documental de orquestração**: um conjunto de regras em prosa que um
agente externo (Claude Code / Cowork, fora do repositório) lê e escolhe obedecer. O `GUIA` declara
isso explicitamente e com precisão incomum:

> "**agente** | o programa que lê, decide e age com ferramentas | *fora do repositório*"
> "**Papel não é outro agente.** É o *mesmo* agente, com um conjunto de regras que dizem o que ele
> não pode fazer ali."
> "**E nada fica rodando.** Fechou o chat, o papel deixa de existir."
> — `GUIA_AGENTES_BASE.md`, seção 0

**Consequência para esta auditoria:** as perguntas do roteiro (retrieval, seleção de ferramenta,
routing, validação) têm resposta em duas camadas diferentes, e misturá-las produz conclusão errada:

| Camada | Onde está | Quem a executa |
|---|---|---|
| **Política** — o que se deve fazer, ler, escrever e não fazer | `.claude/*.md` (versionado, auditável) | ninguém; é texto |
| **Mecanismo** — o que de fato acontece | cliente de IA + ferramentas dele | opaco a este repositório |

**Segundo achado, do mesmo tipo:** o **produto** (`transcritor/`, `desktop/`) também não é um agente.
`transcritor/backend/main.py` (678 linhas) é um FastAPI com seis rotas que repassam áudio/prompt
para a API da OpenAI; `desktop/app.py` (3.955 linhas) é um cliente PySide6. Não há tool-calling, não
há decisão por LLM, não há loop. Agente é a **Fase 6** do `spec/VISAO.md`, ainda `nao-iniciada`.

> **Documentado:** o repositório se chama `agentes-base` e o `README.md` o descreve como "kit de
> agentes".
> **Implementado:** um kit de **papéis e protocolo de arquivos** para conduzir um agente de
> propósito geral. A palavra "agente" no nome é do domínio de uso, não da arquitetura.

---

# 1. Reconstrução do fluxo real

```text
Mensagem humana no chat  (única entrada; não há API, fila, webhook ou gatilho automático)
  ↓
[CLAUDE.md]  — carregado pelo cliente como instrução de projeto
  ↓
DECISÃO 1: qual papel?   "PM" | "EXEC" | nenhum        (opt-in, declarado pelo humano)
  ↓
[Carga de contexto por papel]  CEREBRO.md (mapa) → PM.md ou EXECUTOR.md → metodo/*.md
  ↓
DECISÃO 2: o que é a tarefa?
   ├── PM   → conversa com o usuário (a tarefa nasce aqui)
   └── EXEC → .claude/estado/PROXIMA_TAREFA.md   (fonte única; PLANO.md é proibido)
  ↓
[Retrieval]  leitura de arquivos apontados pelo mapa / citados pela tarefa
             (sem índice, sem busca semântica, sem ranking — ver §3)
  ↓
DECISÃO 3: alguma skill dispara?   gatilho é uma palavra do usuário, casada por LLM
   diagnostico-geral | revisao-acionada | coleta-consolidacao | encerrar-chat
  ↓
[LLM + ferramentas do cliente]  Read/Edit/Bash/device_bash/Task/Artifact — nenhuma declarada aqui
  ↓
[Execução]
   ├── caminho documentado: outro chat, papel EXEC
   └── caminho real desde 2026-09-05: subagente despachado pelo próprio PM  (ver §7)
  ↓
[Escrita de estado]  PROGRESSO.md (append, dono EXEC) · PLANO/PROXIMA_TAREFA/coleta/DECISOES (PM)
  ↓
[Validação]  humano roda o artefato real   (+ suíte de regressão, só do app desktop)
  ↓
[Resposta]  texto no chat  +  painel publicado como artefato, quando pedido
  ↓
LOOP: usuário aprova → PM escreve a próxima tarefa → ...  (o humano fecha o loop, sempre)
```

## Etapa por etapa

| # | Componente | Entrada | Saída | Decisão tomada | Depende de | Evidência |
|---|---|---|---|---|---|---|
| 1 | `CLAUDE.md` (61 linhas) | 1ª mensagem do chat | papel ativo | qual dos 3 modos | o cliente carregar `CLAUDE.md` | `CLAUDE.md` §"Qual é o seu papel" |
| 2 | `.claude/CEREBRO.md` | papel | mapa de onde tudo mora | o que ler a seguir | disciplina de leitura | `CEREBRO.md` §"Quem lê o quê" |
| 3 | `PM.md` (226 linhas) / `EXECUTOR.md` (101) | papel | lista de permissões e proibições em prosa | o que **não** fazer | nada — não há enforcement | `PM.md` §"O que você NÃO PODE fazer (sem exceção)" |
| 4 | `metodo/*.md` (4 arquivos genéricos + 1 local) | — | regras transversais | consistência, higiene, tipo de plano, commit | leitura voluntária | `.claude/metodo/` |
| 5 | `estado/PROXIMA_TAREFA.md` | — | a tarefa corrente, única | o EXEC não escolhe: recebe | o PM ter atualizado | `EXECUTOR.md` §"Primeira ação, sempre" |
| 6 | skills (`.claude/skills/*/SKILL.md`) | palavra-gatilho do usuário | procedimento carregado | qual procedimento | o cliente registrar skills de projeto **ou** o humano abrir o caminho | `CEREBRO.md` §"Os comandos" ("alguns clientes registram e outros não") |
| 7 | agente externo + ferramentas | tudo acima | edições, comandos, medições | **todas** as decisões operacionais | modelo, cliente, sessão | fora do repositório |
| 8 | `estado/PROGRESSO.md` (1.942 linhas, 154.856 bytes) | resultado da execução | log append-only | nível de detalhe (`recibo`/`curto`/`completo`) | campo declarado na tarefa | `EXECUTOR.md` §"Profundidade do registro" |
| 9 | humano | artefato real | aprovação / reprovação | **a única validação forte** | o humano rodar | `PLANO.md`, Etapa 1: reprovada no uso em 27/08 |
| 10 | `coleta/`, `DECISOES.md`, `painel` | o que aconteceu | rastro curado + vista | o que merece registro | o PM promover | `PM.md` §"Coleta"; `skills/diagnostico-geral` |

**O que não existe neste fluxo, e é preciso dizer em voz alta:** nenhuma etapa é disparada por
código. Entre a etapa 1 e a 10 não há um único `if`. O fluxo inteiro é uma sequência de leituras que
um modelo de linguagem decide (ou não) seguir.

---

# 2. Entrada e interpretação

**Tipos de entrada aceitos:** exclusivamente texto em chat, de um único humano. Não há API, fila,
webhook, agendamento (o `scheduled_tasks.lock` é resíduo de cliente, não configuração), nem entrada
de máquina.

| Mecanismo | Existe? | Classificação | Evidência |
|---|---|---|---|
| Normalização da entrada | não | **inexistente** | nenhum código toca a mensagem |
| Classificação de intenção | sim, mínima | **explícito + baseado em regras** — o humano digita "PM"/"EXEC"; a regra está em prosa | `CLAUDE.md`: "O modo é opt-in, declarado na primeira mensagem" |
| Detecção de contexto | sim | **implícito + baseado em LLM** — o modelo lê `CEREBRO.md` e decide o que abrir | `CEREBRO.md` §"Quem lê o quê" |
| Identificação de tarefa | sim | **explícito, baseado em arquivo** para o EXEC; **conversacional** para o PM | `EXECUTOR.md`: "Leia `PROXIMA_TAREFA.md`. Execute apenas o que está ali" |
| Desambiguação | sim, e é regra dura | **explícito** — dois lados: PM pergunta, EXEC **para** | `PM.md`: "Se algo no meu pedido for ambíguo, pergunte. Não assuma." · `EXECUTOR.md`: "PARE, registre a dúvida em PROGRESSO.md e não improvise" |
| Análise de complexidade | **parcial** | **explícito, mas expresso como profundidade de registro, não como roteamento** | `recibo` / `curto` / `completo` — `PM.md` e `EXECUTOR.md` |
| Decisão do próximo passo | sim | **humano** | `PM.md`: "Pergunte se gero a PROXIMA_TAREFA.md da etapa seguinte" |

**Observação relevante:** a classificação de intenção mais fina do sistema não está na entrada, está
nas **skills**. Cada `SKILL.md` traz um `description` com as palavras que a disparam ("diagnóstico
geral", "revisão", "coleta:", "pode encerrar"). Isso é casamento semântico feito pelo LLM sobre a
descrição — **baseado em LLM**, não em regra. E o `CEREBRO.md` reconhece a fragilidade disso:

> "**Alguns clientes registram skills de projeto automaticamente e outros não** — quando não
> registrarem, abra o arquivo pelo caminho acima."

Nesta sessão as quatro skills apareceram registradas pelo cliente. Isso **não é garantido** e o
projeto sabe disso — daí a tabela de comandos existir em dois lugares (`CLAUDE.md` e `CEREBRO.md`)
como caminho manual. É uma das poucas duplicações deliberadas do repositório, e ela é justificada.

**Ausente por completo:** análise de risco da entrada, verificação de autorização, limite de escopo
por tipo de pedido. Não há nada entre "o usuário pediu" e "o agente faz".

---

# 3. Contexto e retrieval

## Fontes de informação

| Fonte | O que guarda | Como é lida |
|---|---|---|
| `.claude/CEREBRO.md` | **o mapa único** de onde tudo mora | leitura direta, é a raiz do grafo |
| `.claude/estado/` | PLANO (28 KB) · PROXIMA_TAREFA (1,8 KB) · PROGRESSO (154 KB) | leitura direta, por papel |
| `.claude/estado/historico/` | 22 arquivos de planos/progressos encerrados | só sob demanda |
| `spec/` | VISAO, MAPA, DECISOES (62 KB, 34 `D-nn`), BACKLOG (23 itens), LACUNAS, QUESTOES, contrato, 2 SPECs, 7 histórias | apontada pela tarefa |
| `coleta/` | 9 arquivos, 281 KB — o diário por chat | raramente lida; é rastro, não insumo |
| memória de projeto do cliente (`MEMORY.md` + 16 tópicos) | decisões, armadilhas, feedback | **fora do repositório**, ver §6 |
| memória pessoal do usuário | perfil e preferências | fora do repositório e fora do projeto |
| `git log` | 16 commits | leitura permitida aos dois papéis |

## Mecanismos de recuperação

| Mecanismo | Existe? | Como |
|---|---|---|
| Documentos | **sim** — é a única fonte | leitura de arquivo |
| Banco de dados | **não existe** (para o método) | — |
| Memória | sim, em quatro camadas paralelas | §6 |
| Histórico de conversa | **deliberadamente descartado** | "o estado mora em arquivo, não em conversa" (`skills/encerrar-chat`) |
| Vector database / embeddings | **NÃO EXISTE** | `B-13` é backlog de produto, não de método |
| Busca lexical | sim, informal (`grep`, `wc -l` sugeridos no `EXECUTOR.md`) | **baseado em código, sob decisão do LLM** |
| Busca semântica / híbrida | **NÃO EXISTE** | — |
| Filtros / reranking / query expansion | **NÃO EXISTEM** | — |
| Múltiplas buscas / retrieval iterativo | sim, emergente | o agente lê, descobre um ponteiro, lê de novo — não há política escrita |
| Avaliação de suficiência do contexto | **sim, e é o mecanismo mais interessante do projeto** | ver abaixo |
| Tratamento de ausência de informação | **sim, explícito e forte** | ver abaixo |

## A pergunta central: recupera ou decide quanto recuperar?

**Decide — e a decisão é por política escrita, não por medição.** Este é o ponto onde o projeto se
distingue de um RAG ingênuo, e vale citar as três regras que a implementam:

1. **Teto por papel.** O Executor lê `EXECUTOR.md`, as regras que couberem e **só a tarefa
   corrente**; ler o `PLANO.md` é **proibido** — não por segredo, mas para impedir antecipação de
   etapa. É recorte de contexto usado como controle de comportamento.
   > "Não leia o PLANO.md para 'adiantar' etapas futuras." (`EXECUTOR.md`)
2. **Recorte por citação.** "Se a tarefa citar uma spec ou um documento de contrato em `spec/`,
   leia **o que ela citar** — não a pasta inteira" (`EXECUTOR.md`).
3. **Ponteiro em vez de cópia.** `CONSISTENCIA.md` regra 1: cada fato tem um dono; os outros
   arquivos apontam. O efeito de retrieval é direto — **o grafo de leitura tem uma folha por fato**,
   o que reduz tanto o volume quanto o risco de ler a versão errada.

**Suficiência do contexto** é avaliada por um teste de aceitação humano, não por score: o critério de
conclusão da Fase 1 foi *"alguém escreve um cliente novo lendo só o contrato"*. Foi exercido duas
vezes, por dois clientes independentes, e **achou uma lacuna real** (o contrato não dizia onde o
núcleo escuta). Isso é avaliação de suficiência de contexto feita como experimento — evidência
parcial, mas evidência.

**Ausência de informação** tem duas travas escritas, e as duas mandam parar em vez de inventar:

> "**Se não tiver, diga isso e pare.** Um painel montado a partir de suposição é pior que painel
> nenhum: ele parece autoridade e é chute." (`skills/diagnostico-geral`, Passo 0)
> "Se a instrução estiver ambígua ou incompleta: PARE, registre a dúvida em PROGRESSO.md e não
> improvise." (`EXECUTOR.md`)

## Onde o contexto entra na geração

Tudo no **prompt**, por leitura de arquivo no início da sessão e ao longo dela. Não há injeção
programática, não há template de prompt, não há montagem de contexto por código. **Medição do custo
fixo dessa carga** (feita agora, porque o repositório não a mede em lugar nenhum):

| Caminho de leitura | Palavras | Bytes | Ordem de grandeza em tokens |
|---|---|---|---|
| PM (CLAUDE + CEREBRO + PM.md + 4 regras) | 5.350 | 33.783 | ~9 k |
| PM + `PLANO.md` + `DECISOES_METODO.md` | 11.344 | 71.752 | ~19 k |
| EXEC (CLAUDE + EXECUTOR + tarefa + 3 regras) | 3.391 | 21.122 | ~5,5 k |
| `PROGRESSO.md` inteiro, se aberto | — | 154.856 | ~40 k |

---

# 4. Raciocínio e tomada de decisão

| Mecanismo | Existe? | Natureza | Evidência |
|---|---|---|---|
| Regras | **sim, é a espinha** | prosa, ~48 KB no total do método | `.claude/metodo/`, `PM.md`, `EXECUTOR.md` |
| Prompts | sim — os próprios `.md` são os prompts | — | todo o `.claude/` |
| Router | **sim, mas humano** | o usuário digita o papel | `CLAUDE.md` |
| Classificador | não | — | — |
| Planning | **sim, e é humano-no-loop obrigatório** | o PM propõe, o usuário aprova | `PM.md`: "Antes de gravar o plano, mostre e pergunte: 'aprova ou ajusto?'" |
| Decomposição de tarefas | **sim, com limite duro** | máx. 7 etapas; **uma tarefa por vez** | `PM.md`; `metodo/PLANOS.md` |
| Loops | sim, mas **fechados pelo humano** | PM → tarefa → EXEC → progresso → PM confere | `PLANO.md`, dez rodadas da `D-32` |
| Reflexão | sim, ritualizada | `revisao-acionada`, passe de conferência do painel | `skills/revisao-acionada` |
| Validação | sim, humana | §8 |
| Retry | **sim, e é o padrão de operação real** | 10 rodadas na `D-32`, 7 voltas na Etapa 1 | `PLANO.md`, `PROGRESSO.md` |
| Self-correction | **parcial e regrada**: o EXEC pode **subir** o nível de registro, nunca descer; e pode reportar bug fora do escopo mas **não consertar** | explícito | `EXECUTOR.md` |
| Seleção dinâmica de ferramentas | não declarada | é do cliente | — |
| Seleção de modelo | **sim, mas só apareceu na prática** | "PM escolheu o modelo (`opus`) pela exigência do trabalho" | `coleta/2026-09-05`, §3 |

## Workflow fixo × decisão dinâmica — a separação honesta

**É workflow fixo, com dois pontos de decisão dinâmica.**

**Fixo (a maior parte):** a ordem plano → tarefa → execução → progresso → conferência → próxima
tarefa não varia, não se ramifica e não é escolhida pelo agente. A `encerrar-chat` chega a numerar:
"Os quatro passos, **nesta ordem**". Sequência de chamadas ≠ planning: aqui a sequência é
**prescrita em prosa**, e quem escolhe entrar nela é o humano.

**Dinâmico (dois pontos, ambos recentes e ambos não documentados no método):**

1. **Escolha do executor e do modelo.** Em 2026-09-05 o PM passou a decidir, por rodada, se despacha
   um subagente e com qual modelo. Isso é roteamento de verdade — e mora só na `coleta/`.
2. **Formulação de hipótese entre rodadas.** Nas rodadas 4, 5 e 8 da `D-32` o PM **leu o código
   antes de despachar**, refutou a hipótese anterior e formou outra ("refutou a hipótese de corrida
   com o vigia de ponteiro… e formou nova hipótese", `PLANO.md`). Isso é um ciclo de
   hipótese → experimento → refutação executado pelo agente, com o humano como oráculo do resultado.
   **Não está escrito em nenhuma regra**; emergiu do uso.

---

# 5. Ferramentas e execução

## Ferramentas declaradas *pelo projeto*

O repositório declara **uma** ferramenta executável e **quatro** procedimentos.

| Nome | Função | Parâmetros | Quando | Quem decide | Determinístico? | Validação | Retry | Permissão |
|---|---|---|---|---|---|---|---|---|
| `.claude/kit/exportar.py` (161 linhas) | gera o kit portátil (zip + pasta) a partir dos `.md` vivos | `[pasta-de-saida]` ou `--skill <nome>` | ao levar o método para outro projeto | humano | **sim, é código** | falha se faltar arquivo da lista (`SystemExit`) | não | escrita em `.claude/tmp/` |
| skill `diagnostico-geral` | painel de roadmap publicado | — (config em `.claude/painel.md`) | "diagnóstico geral", virada de plano, tarefa conferida | LLM, por gatilho textual | **não** — LLM | passe de conferência interno | não | **não corrige nada** |
| skill `revisao-acionada` | varredura por lentes, achado julgado em 5 campos | lentes escolhidas na hora | "revisão", fechamento de plano | LLM | **não** | conta em vez de estimar | não | **proibido corrigir, mover, apagar, commitar** |
| skill `coleta-consolidacao` | diário append-only + resumo em 4 categorias | `coleta: <nota>`, "consolidar" | todo chat de trabalho | LLM | **não** | travas antialucinação | não | append-only; **só o PM escreve** |
| skill `encerrar-chat` | consolida, atualiza estado, reescreve retomada, publica painel | — | "pode encerrar" | LLM | **não** | — | não | não edita `PROGRESSO.md` |

## Ferramentas *usadas* mas não declaradas aqui

Vêm do cliente e o repositório não as nomeia (com uma exceção): edição de arquivo, shell, leitura,
publicação de artefato, subagente, ponte com a máquina do usuário. A exceção é uma nota operacional
dentro do `PM.md` que **acopla o método a um cliente específico**:

> "A ferramenta padrão de gravar arquivo remoto recusa qualquer caminho dentro de `.claude/`
> ('Writing to .claude is not permitted via remote tools'). … **Faça assim em vez disso**: rode o
> comando diretamente no terminal remoto do dispositivo, gravando o conteúdo com heredoc"
> — `PM.md`, §"Nota técnica"

## O que o agente pode fazer

| Capacidade | Tecnicamente possível | Permitido pelo método |
|---|---|---|
| Executar código | sim | PM: **não** (só leitura) · EXEC: sim |
| Consultar APIs externas | sim | não regulado — acontece (preços da OpenAI conferidos com data) |
| Modificar arquivos | sim | PM: **só** `estado/PLANO`, `estado/PROXIMA_TAREFA`, `coleta/`, `tmp/` · EXEC: só os listados em "Arquivos envolvidos" |
| Modificar banco de dados | n/a | não há banco |
| Chamar outros agentes | sim | **não previsto no método; praticado desde 05/09** |
| Chamar outros modelos | sim | não regulado; praticado (escolha de `opus`) |
| Comandos externos | sim | PM: só leitura (`ls`, `cat`, `git log`, `git diff`) · EXEC: sim |
| Produzir artefatos | sim | sim — código, docs, painel publicado, kit |
| **Commitar** | sim | **NÃO, sem autorização por ação** (`M-05`, com a exceção datada `M-10`) |

---

# 6. Estado e memória

## Estado (o que sustenta a execução corrente)

| Artefato | Dono | Natureza | Tamanho medido |
|---|---|---|---|
| `PLANO.md` | PM | etapas + critérios da fase corrente | 378 linhas / 28 KB |
| `PROXIMA_TAREFA.md` | PM | **uma** tarefa, sobrescrito a cada vez | 36 linhas / 1,8 KB |
| `PROGRESSO.md` | EXEC | log append-only | 1.942 linhas / 154.856 bytes / **21 entradas** |
| `historico/` | PM (só move) | planos e progressos encerrados | 22 arquivos |

Checkpoint existe e tem gatilho declarado: snapshot do plano **em virada** (`HIGIENE.md`), com o
motivo no nome do arquivo. Não há checkpoint de execução dentro de uma tarefa.

## Memória (o que atravessa execuções) — **quatro camadas, duas delas fora do mapa**

| # | Camada | Onde | Declarada no `CEREBRO.md`? |
|---|---|---|---|
| 1 | **Livro-razão de produto** — 34 `D-nn`, cada um com razão e condição de reabertura | `spec/DECISOES.md` (62 KB) | **sim** |
| 2 | **Livro-razão de método** — 10 `M-nn` | `.claude/metodo/DECISOES_METODO.md` | **sim** |
| 3 | **Diário episódico** — 9 arquivos, um por chat, append-only, 281 KB | `coleta/` | **sim** |
| 4 | **Retomada** — o "prompt de boot" do próximo chat | `_RETOMADA_*.md` na raiz | parcialmente (`CLAUDE.md` cita) |
| 5 | **Memória de projeto do cliente** — `MEMORY.md` + 16 arquivos de tópico (`projeto_*`, `feedback_*`) | fora do repositório, na máquina | **NÃO** |
| 6 | **Memória pessoal do usuário** — perfil, preferências | fora do projeto | **NÃO** |

A camada 5 é a mais desconfortável do ponto de vista do próprio método. Ela guarda **o mesmo tipo de
fato** que a `coleta/` e o `DECISOES_METODO.md` (regras de conduta do EXEC, armadilhas do handoff,
feedback recorrente do usuário), com um índice próprio (`MEMORY.md`), e o `CEREBRO.md` se declara
"o **mapa único** de onde tudo mora. Nenhum outro arquivo mapeia a estrutura". **Existem dois
índices.** Pior: a camada 5 já envelheceu — `projeto_kit_agentes.md` diz *"Skill do projeto:
`coleta-consolidacao` (única)"*, e há **quatro** skills desde 24-25/08.

Isto é exatamente a deriva que a `M-04` existe para impedir, acontecendo numa camada que a `M-04`
não enxerga.

**Recuperação da memória:** por leitura de arquivo, sempre. Sem índice invertido, sem embeddings,
sem TTL. O único gancho mecânico de reabertura é o campo `olhar de novo em: <fase>` do `BACKLOG.md`,
lido no passe de fechamento de fase — um mecanismo simples e genuinamente bom.

---

# 7. Agentes e delegação

## Arquitetura de agentes

**Agente único, dois papéis, sem hierarquia declarada — mas com delegação real desde 2026-09-05.**

| Papel | Responsabilidade | Entrada | Saída | Ferramentas | Contexto | Modelo | Como é acionado |
|---|---|---|---|---|---|---|---|
| **PM** | planejar, coordenar, registrar, **conferir** | conversa com o usuário + `PROGRESSO.md` | `PLANO`, `PROXIMA_TAREFA`, `coleta/`, `DECISOES` | leitura ampla; escrita restrita a 4 destinos; git **só leitura** | mapa + regras + plano + spec | não fixado | 1ª mensagem = "PM" |
| **Executor** | executar **uma** tarefa | `PROXIMA_TAREFA.md` | código/artefato + entrada no `PROGRESSO.md` | escrita e execução, restritas aos "Arquivos envolvidos" | tarefa + o que ela citar; **`PLANO.md` proibido** | não fixado | 1ª mensagem = "EXEC" |
| **sem papel** | trabalho normal | — | — | irrestritas | — | — | ausência de declaração |

## Função × delegação — a distinção pedida

- **"Chamar um componente"**: carregar uma skill. O contexto é o mesmo, o agente é o mesmo, o
  procedimento muda. É o que as quatro skills fazem.
- **"Delegar a outro agente"**: passar uma tarefa a uma instância com contexto próprio, que devolve
  um relatório. **Isto acontece de duas formas neste projeto:**
  - **Assíncrona, por arquivo** (documentada): outro chat, papel EXEC, `PROXIMA_TAREFA.md` como
    protocolo de handoff e `PROGRESSO.md` como retorno. É a arquitetura declarada, e é notável: o
    **canal de delegação é o sistema de arquivos**, o que a torna independente de cliente, de
    modelo e de sessão.
  - **Síncrona, por subagente** (não documentada): o PM despacha e recebe de volta na mesma sessão.

> **Documentado:** "Quem executa é o Executor, **em outro chat**" (`PM.md`, cabeçalho).
> **Implementado:** "Usuário deu autonomia ao PM para chamar um **subagente** que executa (papel
> EXEC), em vez de o PM executar ou abrir um chat separado. **PM escolheu o modelo (`opus`)**"
> (`coleta/2026-09-05_botao-flutuante-compacto.md`, §3). O `PLANO.md` registra a entrega "por
> subagente Executor" e a `coleta/` cita subagente **15 vezes**, com quatro despachos nomeados por rodada.

**Nenhum arquivo de `.claude/` foi atualizado para descrever esse modo.** O `PM.md` continua dizendo
que o PM não executa e que o Executor está em outro chat — o que é literalmente verdadeiro e
funcionalmente enganoso: o PM passou a ser um **supervisor** que instancia executores, escolhe
modelo, lê o código entre rodadas e forma hipóteses. É a mudança arquitetural mais significativa dos
últimos 30 dias e vive só no diário.

---

# 8. Validação e controle de qualidade

| Mecanismo | Existe | O que ele **realmente** consegue validar |
|---|---|---|
| **Confirmação do usuário no artefato real** | **sim — é a validação primária** | tudo que se percebe usando: comportamento, ergonomia, regressão visual. Foi ela que reprovou a Etapa 1 em 27/08 e fechou a `D-32` em 06/09. **Não escala, não é reprodutível, depende de o usuário rodar.** |
| Conferência do PM no artefato | sim, é regra | que o critério de pronto foi atendido de fato — "não confie só no relato do executor" (`PM.md`). Valida o **relato**, não o comportamento em produção. |
| Critério de pronto verificável | sim, é regra de construção | que a etapa tem um alvo checável. Não valida nada sozinho; é pré-condição para as outras validações. |
| Suíte de regressão automatizada | **sim, mas só de um componente** | `desktop/testes_janela_compacta.py`, 1.661 linhas, **230 verificações** (cresceu 47 → 91 → 143 → 167 → 230). Valida geometria, âncora, número de resizes nativos. **Não valida** o que só o Windows real mostra — e o projeto diz isso: "nenhum teste headless substitui isso". |
| Verificação manual declarada como método | sim (`M-01`/`D-09`) | reconhece a ausência de suíte e declara o gatilho de revisão: "mais de um cliente consumindo o núcleo" — **gatilho já atingido** (app desktop + `cliente_minimo.py`), sem `M-01` reaberta. |
| Passe de conferência (dentro do painel) | sim | contradição de estado, contagem à mão, ponteiro quebrado, data fora de ordem, fato sem dono. **Só roda quando alguém pede o painel** — e não corrige. |
| `revisao-acionada` | sim | achados julgados em 5 campos, com veredito. **Explicitamente proibida de corrigir** — trava bem argumentada (§"A trava principal"). |
| Schemas / validação estruturada | **NÃO EXISTE** para o método | o formato de `PROXIMA_TAREFA`/`PROGRESSO` é prosa "obrigatória" sem validador. (No **produto** existe: `pydantic`, listas de modelos permitidos, teto de 25 MB.) |
| Segunda chamada ao LLM como crítico | **não como mecanismo automático** | acontece de fato quando o PM confere o trabalho do subagente — mas não é regra escrita |
| Verificação de fontes | sim, cultural e forte | preços e limites da API sempre com **data de consulta**; contrato "medido, não suposto" |
| Retry | sim, humano | 10 rodadas na `D-32`, 7 voltas na Etapa 1 |
| Fallback | **NÃO EXISTE** | não há caminho alternativo quando algo falha; o fluxo para e vira conversa |
| Detecção de erro | parcial | o EXEC deve reportar bug fora de escopo sem consertar |

**O que nenhum mecanismo valida hoje:** que o PM não errou o **escopo**. Foi exatamente essa a falha
de 27/08 — a tarefa foi executada corretamente e reprovada assim mesmo, porque o escopo tinha sido
escrito sem passar por `COMPORTAMENTOS_PARQUEADOS.md`. O conserto foi uma regra nova em prosa
("qualquer tarefa que desenhe interface passa antes por…"), ou seja: **a mesma classe de mecanismo
que falhou**. Não há verificação independente do escopo antes do despacho.

---

# 9. Observabilidade

| O que se observa | Onde | Qualidade |
|---|---|---|
| Decisões e razões | `DECISOES.md` (34), `DECISOES_METODO.md` (10) — cada um com **Por quê** e **Reabre se** | **excelente** — melhor que a maioria dos sistemas de produção |
| Execução | `PROGRESSO.md`, 21 entradas com esqueleto fixo (Feito · Critério · Riscos · Ajuste no plano) | **muito boa** |
| Rastro conversacional | `coleta/`, um arquivo por chat, marcado `[DECISÃO]`/`[ARTEFATO]`/`[DIRECIONAMENTO]`/`[PENDÊNCIA]` | boa; é o que liga uma decisão ao chat em que nasceu |
| Vista consolidada | painel publicado, endereço fixo | boa, mas sob demanda |
| Histórico versionado | 16 commits + 22 arquivos em `historico/` | **fraco no git**: 16 commits para ~22 dias de trabalho intenso, e a árvore está com 16 arquivos modificados não commitados |
| Ferramentas usadas pelo agente | **NÃO EXISTE** | nada registra qual ferramenta foi chamada |
| Contexto recuperado | **NÃO EXISTE** | nada registra que arquivos foram lidos |
| Tokens / custo / latência **do agente** | **NÃO EXISTE** | e é uma ausência marcante, porque o **produto** mede isso com rigor: `consumo.jsonl`, 1.317 linhas, com custo por requisição, e alarme declarado de US$ 100/mês (`D-18`). O projeto mede o custo do que ele constrói e **não mede o custo de se construir**. |
| Chamadas de modelo | não | — |
| Erros | parcial | só o que o humano relata ou o EXEC registra |
| Checkpoints | sim | snapshots de plano em virada |

**É possível reconstruir uma execução depois?** **Parcialmente, e melhor do que o normal.** Dá para
reconstruir *o que foi decidido, por quê, quando, o que foi entregue e como foi testado* — a
`D-32` é reconstruível rodada a rodada, com números. **Não** dá para reconstruir *como* o agente
chegou lá: quais arquivos leu, quantas tentativas fez, quanto custou, quanto demorou. A
observabilidade é **do trabalho**, não **do agente**.

---

# 10. Permissões e limites

## Capacidade técnica × permissão operacional

Esta é a distinção mais importante do repositório, e o `GUIA` a enuncia melhor do que eu conseguiria:

> "**O valor está no limite, não na capacidade.** O PM **consegue** editar código — ele só **não
> pode**, e está escrito que não pode. Essa fricção deliberada é o mecanismo inteiro."

| Ação | Capacidade técnica | Permissão PM | Permissão EXEC | Sem papel | Enforcement |
|---|---|---|---|---|---|
| Ler qualquer arquivo | sim | sim | sim (com recorte) | sim | nenhum |
| Ler `PLANO.md` | sim | sim | **proibido** | sim | **nenhum** |
| Editar `PLANO`/`PROXIMA_TAREFA` | sim | **sim (exclusivo)** | **proibido** | — | nenhum |
| Editar `PROGRESSO.md` | sim | **só mover entradas de plano encerrado** | append no fim | — | nenhum |
| Escrever na `coleta/` | sim | **sim (exclusivo)** | **proibido** | — | nenhum |
| Editar código | sim | **proibido sem exceção datada** | só "Arquivos envolvidos" | livre | nenhum |
| Rodar comando que altere o projeto | sim | **proibido** | sim | livre | nenhum |
| `git status` | sim | **desaconselhado** (deixa `index.lock` pela pasta montada) | sim | — | ambiente |
| **commit / push / reset / rebase** | sim | **só com autorização por ação** | **nunca** | **proibido** | **git + o humano** |
| Apagar arquivo na pasta montada | **não** ("Operation not permitted") | — | — | — | **ambiente** |
| Escrever em `.claude/` por ferramenta remota | **não** | contornado por heredoc no shell | idem | idem | **ambiente** |

**Conclusão dura:** de todas as permissões acima, **três** têm enforcement real, e nenhuma delas foi
projetada pelo método: o git (que exige uma ação humana), a recusa de escrita remota em `.claude/` e
a recusa de remoção na pasta montada. As duas últimas são **acidentes do ambiente que o método
transformou em regra** (`HIGIENE.md` §"Lixo de ferramenta", `PM.md` §"Nota técnica"). Todo o resto é
**conformidade voluntária de um LLM lendo prosa** — e o próprio projeto identificou o furo mais
provável:

> "Vale também para o chat que **não declara papel**. É o modo mais desprotegido justamente porque
> ninguém percebe: sem papel declarado não há regra de papel, e é aí que um commit não autorizado
> escapa." (`metodo/COMMIT.md`)

Não há restrição alguma de acesso a outros projetos, a rede, a segredos além do `.gitignore` (que
protege `transcritor/.env` e os `.jsonl` locais). O único segredo do projeto é a chave da OpenAI, e
o tratamento dela é correto: `.env` ignorado, `.env.example` versionado, comentário no código
dizendo "nunca hardcoded, nunca logada".

---

# 11. Inventário de regras e diretivas, classificado

**Legenda:** A = generalizável · B = dependente do domínio · C = dependente da implementação ·
D = específica do projeto · E = incerta.

## Regras de conduta e papel

| Regra | Onde | Classe | Por quê |
|---|---|---|---|
| Roteamento de papel opt-in na 1ª mensagem | `CLAUDE.md` | **A** | não depende de domínio, cliente ou produto |
| PM planeja e **não executa** | `PM.md` | **A** | a fricção é o mecanismo, não o assunto |
| EXEC executa **só** a tarefa corrente e não lê o plano | `EXECUTOR.md` | **A** | idem |
| Ambiguidade → o EXEC **para** e registra | `EXECUTOR.md` | **A** | trava antialucinação universal |
| Bug fora de escopo → reportar, **não consertar** | `EXECUTOR.md` | **A** | separa achado de mudança |
| Nunca colar código no log; citar `arquivo:linha` | `EXECUTOR.md` | **A** | vale para qualquer projeto com versionamento |
| Três níveis de profundidade de registro, declarados na tarefa | `PM.md`/`EXECUTOR.md` | **A** | controle de custo de log genérico e barato |
| "Pode **subir** o nível, nunca descer" | `EXECUTOR.md` | **A** | assimetria correta |
| Máximo 7 etapas por plano | `PM.md` | **A** (com número arbitrário → **E** quanto ao valor) | o limite é genérico; o "7" não tem evidência registrada |
| Nunca adicionar etapa por iniciativa própria | `PM.md` | **A** | — |
| "Aprova ou ajusto?" antes de gravar o plano | `PM.md` | **A** | ponto de humano-no-loop |
| Idioma do trabalho fixado (pt-BR) | `CLAUDE.md` | **A** quanto ao mecanismo, **D** quanto ao valor | nasceu de um chat que respondeu em inglês |
| Nota de heredoc para escrever em `.claude/` | `PM.md` | **C** | é remendo de um cliente específico |

## Regras de método (`metodo/`)

| Regra | Classe | Por quê |
|---|---|---|
| **Todo fato tem dono único; os outros apontam** | **A** | a regra mais forte do repositório; vale para qualquer sistema documental |
| **Nada de número derivado escrito à mão** | **A** | nasceu de 4 ocorrências medidas do mesmo erro |
| **Passe de fechamento** na mesma sessão | **A** | — |
| **O mais recente vence**, e o perdedor é corrigido na hora | **A** | regra de desempate; o próprio arquivo diz que precisar dela com frequência é sintoma |
| **Aviso não é conserto** | **A** | a mais original das cinco; ataca um antipadrão específico de agentes documentais |
| Higiene com **gatilho declarado** (snapshot em virada; tamanho é alarme, não gatilho) | **A** | — |
| "Se um arquivo do rascunho passou a ter valor, promova na hora" | **A** | — |
| Três tipos de plano (fase / manutenção / acompanhamento) | **A** | resolve um problema real e genérico |
| Backlog atravessa fases; item **nunca é apagado, só muda de estado** | **A** | — |
| **Só o usuário autoriza commit**, por ação | **A** | — |
| "O Executor entrega o repositório **pronto para commit**" | **A** | — |
| Lixo de bridge remoto (`.fuse_hidden*`, `index.lock`, `HEAD.lock`) | **C** | só existe por causa de pasta montada |
| `M-06` — o cérebro mora em `.claude/` | **C** | escolha por conveniência de ferramenta, declarada como tal |
| `M-07` — o kit se exporta por script, nunca por cópia | **A** | é a regra de dono único aplicada ao próprio kit |
| `M-09` — skill de conta é **destino de exportação**, não segunda fonte | **A** | — |
| `M-01`, `M-05`, `M-10` (verificação manual, commit, exceção datada) | **D** quanto ao conteúdo, **A** quanto ao formato do ledger | são escolhas desta instalação, e o arquivo diz isso |

## Regras das skills

| Regra | Classe | Por quê |
|---|---|---|
| "O painel é **vista**, não fonte de verdade" | **A** | — |
| Passo 0: se não há estado em arquivo, **diga e pare** | **A** | trava antialucinação exemplar |
| Configuração local (`painel.md`) separada do procedimento | **A** | separação genérico/específico bem feita |
| "Números do topo calculados na hora, nunca copiados de prosa" | **A** | — |
| **Estimativa de esforço não entra no painel** | **A** | "chute com cara de dado" |
| Menu "o que você pode fazer", consciente de estado | **A** | ataca um problema real: skill esquecida é skill inexistente |
| Revisão **nunca corrige**, com três razões escritas | **A** | a melhor argumentação de trava do repositório |
| Lentes declaradas; "lente que não rodou é cobertura que não existe" | **A** | — |
| Achado julgado em 5 campos + veredito | **A** | — |
| Coleta: 4 marcações, append-only, `[DECISÃO]` sempre com trade-off | **A** | — |
| `[PROPOSTA-ASSISTENTE]` para sugestão do próprio agente | **A** | separa o que o humano disse do que o agente propôs |
| Datas relativas → absolutas no registro | **A** | — |
| Passo "aplicar" removido por não haver destino final | **D** | — |
| Identidade visual, fontes, paleta, endereço fixo do painel | **D** | `painel.md` inteiro |
| Ordem dos 4 passos de encerramento | **A** | — |
| "`PROXIMA_TAREFA.md` diz em voz alta quando não há tarefa" | **A** | nasceu de duas falhas medidas |

## Regras do produto (para contraste)

`spec/DECISOES.md` (34 `D-nn`), `spec/contrato/NUCLEO.md`, `SPEC-001/002`, `COMPORTAMENTOS_PARQUEADOS.md`,
histórias `US-D01..D07` — **todas classe B ou D**. Nada disso pertence a uma base comum de agentes.
O que é generalizável ali é o **formato**: decisão com `Por quê` + `Reabre se`; contrato marcado
`status: observado (não é aspiração)`; spec que declara divergências deliberadas em vez de escondê-las.

---

# 12. Arquitetura conceitual em camadas

```text
Interface .................. chat de texto, um humano.  Painel publicado como saída secundária.
   ↓
Entrada / interpretação .... CLAUDE.md.  Roteamento opt-in por palavra ("PM"/"EXEC").
                             MISTURADA: a "interpretação" é o próprio LLM lendo prosa.
   ↓
Contexto / memória ......... CEREBRO.md (mapa) + estado/ + spec/ + coleta/ + 2 memórias externas.
                             PARCIALMENTE FORA DO MAPA (memória de projeto do cliente).
   ↓
Retrieval .................. leitura de arquivo guiada por mapa e por citação da tarefa.
                             SEM índice, SEM busca semântica, SEM ranking, SEM reranking.
   ↓
Raciocínio / decisão ....... regras em prosa + o modelo.  Sem router, sem classificador.
   ↓
Planning ................... PM propõe → HUMANO aprova → uma tarefa por vez.
                             NÃO É AUTÔNOMO — e isso é deliberado, não lacuna.
   ↓
Tools / Agents ............. 1 script + 4 skills declaradas; as ferramentas reais são do cliente.
                             MISTURADA: delegação a subagente existe e não está declarada aqui.
   ↓
Execution .................. EXEC em outro chat, ou subagente na mesma sessão.
   ↓
Validation ................. HUMANO no artefato real (primária) + 230 verificações de um componente
                             + passe de conferência (só quando o painel roda).
                             NÃO EXISTE validação automática do escopo antes do despacho.
   ↓
Response ................... texto no chat + escrita de estado + painel.
```

**Camadas que NÃO EXISTEM:** roteamento programático, seleção de ferramenta declarada, avaliação
automática, fallback, telemetria, controle de custo do agente, autorização técnica.

**Onde as camadas se misturam:**

1. **Planning e Response no mesmo arquivo.** O `PLANO.md` deveria ser objetivo/escopo/etapas
   (`PM.md` define a estrutura obrigatória em 4 seções). Hoje ele tem **28 KB** e carrega a narrativa
   das dez rodadas da `D-32`, com números, hipóteses e vereditos — conteúdo cujo dono declarado é o
   `PROGRESSO.md` e a `D-32`. É a regra de dono único quebrada no arquivo que a manda seguir.
2. **Retrieval e permissão no mesmo mecanismo.** "O EXEC não lê o `PLANO.md`" é ao mesmo tempo
   política de contexto e controle de comportamento. Elegante, mas significa que mudar o recorte de
   leitura muda a segurança.
3. **Estado e memória na `coleta/`.** Ela é diário (memória) e também é onde pendências operacionais
   vivem ("depende de: chamar subagente Executor") — o que é estado.

---

# 13. Dependências e acoplamentos

## Quem depende de quem

```text
CLAUDE.md ──→ CEREBRO.md ──→ { PM.md, EXECUTOR.md, metodo/*, skills/*, estado/* }
                    │
                    └──→ painel.md ──→ skill diagnostico-geral ──→ { VISAO, PLANO, PROGRESSO,
                                                                     DECISOES, MAPA, coleta/, ... }
PM.md ──→ metodo/{CONSISTENCIA, HIGIENE, PLANOS, COMMIT}      (só ponteiro, sem cópia)
EXECUTOR.md ──→ PROXIMA_TAREFA.md ──(o que ela citar)──→ spec/*
kit/exportar.py ──→ lista fixa de 18 caminhos                  (acoplamento por caminho literal)
```

**Acoplamento forte e saudável:** `metodo/` é citado por ponteiro nos dois papéis e escrito num lugar
só. Trocar uma regra não exige tocar em `PM.md`.

**Substituíveis de forma independente:**

- as quatro skills (o `SKILL.md` é autocontido; a config do painel está fora);
- o produto inteiro (`spec/`, `transcritor/`, `desktop/`) — o método não sabe o que ele constrói;
- o `DECISOES_METODO.md` (o script de exportação o exclui de propósito);
- o `painel.md` (config), separado do procedimento.

**Acoplamentos que preocupam:**

| Acoplamento | Onde | Gravidade |
|---|---|---|
| **Ao cliente/ambiente** | `PM.md` §"Nota técnica" (heredoc para escrever em `.claude/`); `HIGIENE.md` §"Lixo de ferramenta"; `COMMIT.md` (`index.lock` pela pasta montada) | alta — três arquivos de método genérico carregam remendo de um ambiente específico, e um deles (`HIGIENE`) **vai no kit** |
| **`exportar.py` à lista literal de 18 caminhos** | `kit/exportar.py`, `INCLUIR` | média — arquivo novo de método não entra no kit até alguém lembrar; falha barulhenta (`SystemExit`), o que ajuda |
| **`painel.md` ao endereço fixo de um artefato** | `painel.md` §"Publicação" | média — o próprio arquivo registra que a rede da sessão bloqueia a leitura do endereço antigo |
| **Painel a uma ferramenta de publicação** | skill `diagnostico-geral` | baixa — há fallback declarado ("escreva o HTML num arquivo e entregue") |
| **Ao modelo** | nenhum acoplamento declarado; a escolha de `opus` aparece só na `coleta/` | baixa hoje, mas **não regulada** |

**Regras espalhadas / duplicação:** o repositório é notavelmente bom nisso — a duplicação é quase
sempre ponteiro. As exceções reais:

1. **A tabela de comandos existe duas vezes** (`CLAUDE.md` e `CEREBRO.md`). Deliberada e justificada
   (o comando não pode depender de o cliente descobrir a skill).
2. **O passe de conferência está escrito duas vezes por extenso** — os mesmos 6 itens em
   `metodo/CONSISTENCIA.md` §"Como isso se confere" e em `skills/diagnostico-geral` §"Passe de
   conferência". Mesma ordem, mesmas palavras-chave. **Fato sem dono, pela definição do próprio
   projeto.**
3. **As regras de profundidade de registro** aparecem quase inteiras nos dois papéis (`PM.md` e
   `EXECUTOR.md`), com a justificativa reescrita nos dois. Defensável (cada papel lê só o seu), mas
   é conteúdo duplicado, não ponteiro.
4. **A narrativa da `D-32`** existe em `PLANO.md`, `PROGRESSO.md`, `spec/DECISOES.md` e
   `coleta/2026-09-05_*.md`. Quatro versões da mesma história, em quatro níveis de detalhe.

---

# 14. Custos e complexidade

> Formato pedido: mecanismo → custo/complexidade → benefício esperado/observado.

| Mecanismo | Custo introduzido | Benefício |
|---|---|---|
| **Carga de contexto por papel** | ~9 k tokens (PM) / ~5,5 k (EXEC) **por chat, antes de qualquer trabalho**; ~19 k com plano e ledger de método | **observado**: dois chats independentes conseguiram continuar o trabalho sem reexplicação. Nenhuma medição do custo existe no projeto. |
| **`PROGRESSO.md` de 154 KB no arquivo vivo** | ~40 k tokens se aberto inteiro; e o `EXECUTOR.md` manda conferir o fim antes de escrever (mitigação barata: `wc -l`, `grep -n`) | log completo da fase; mas 21 entradas com plano ainda aberto é sintoma, não conquista (§16) |
| **Dois chats (PM/EXEC)** | duplica a carga de contexto; exige handoff por arquivo | **observado**: impediu execução sem aprovação; o `GUIA` diz que é o mecanismo inteiro |
| **Subagente por rodada** | uma sessão de modelo por rodada despachada (4 despachos nomeados na `D-32`); o PM ainda lê o código entre rodadas | **observado**: latência muito menor que abrir chat novo; e o PM manteve continuidade de hipótese entre rodadas, que um chat EXEC novo perderia |
| **Dez rodadas para uma janela flutuante** | dez despachos + dez conferências + dez atualizações de documento | **observado, e o resultado foi bom**: o problema foi resolvido na 9ª por **troca de arquitetura** (máscara no lugar de resize), e o rastro mostra por que as 8 anteriores falharam. O custo é real; o aprendizado também. |
| **Diário `coleta/` (281 KB)** | escrita por interação, em todo chat | **observado**: é a única fonte que explica *por que* o subagente entrou, e o que o usuário disse em cada reprovação |
| **Livro-razão com `Por quê` + `Reabre se`** | mais escrita por decisão | **observado, com evidência forte**: a `D-08` foi reaberta e refutada por medição; a `Q1` teve três respostas em três dias e o rastro está preservado |
| **Passe de conferência dentro do painel** | leitura de ~15 arquivos por geração | **observado**: 9 inconsistências achadas numa varredura (`M-04`); mas só roda quando o painel é pedido |
| **Skills como procedimento em prosa** | cada uma custa 2–8 KB de contexto quando carregada | **parcial**: a `diagnostico-geral` (175 linhas) é a mais cara e a mais usada |
| **Exportação por script (`M-07`)** | manter a lista de 18 caminhos | **observado**: kit gerado em 25/08 sem divergir da fonte |
| **Regra "sem número escrito à mão"** | obriga contar antes de escrever | **observado com número**: 4 ocorrências registradas do erro que ela previne, incluindo uma correção de "13" para "60" e depois a percepção de que os 60 não eram 60 planos |

**Mecanismos sem evidência de benefício registrada:**

- **`metodo/PLANOS.md`** — os três tipos de plano. `MANUTENCAO.md` e `ACOMPANHAMENTO.md` **nunca
  foram criados** (`ls .claude/estado/` confirma). A regra é boa no papel; **não há um único caso de
  uso neste repositório**. Classe A por argumento, não por evidência.
- **O limite de "máximo 7 etapas"** — nenhuma justificativa registrada para o número.
- **A `revisao-acionada`** — não há relatório de revisão versionado no repositório; o único rastro é
  um endereço de artefato citado na retomada, cuja leitura o próprio `painel.md` diz que a rede
  bloqueia. **Não determinado pela auditoria** se ela rodou mais de uma vez.

---

# 15. Evidências de eficácia

| Mecanismo | Evidência | Classificação |
|---|---|---|
| Separação PM/EXEC | a reprovação de 27/08 foi **de escopo do PM**, não de execução; o erro ficou isolado e nomeado ("Erro é meu, e é de escopo, não de execução"). O mecanismo tornou o erro atribuível. | **parcial** |
| Regra de dono único (`M-04`) | 9 inconsistências medidas numa varredura, a maioria do mesmo fato copiado; e a `Q1` com 3 respostas em 3 arquivos | **forte** (para o problema; não para a solução) |
| Sem número escrito à mão | **4 ocorrências** do erro rastreadas, com correção documentada (13 → 60 → "os 60 não são 60 planos") | **forte** |
| Critério "cliente novo lendo só o contrato" | exercido por **2 clientes independentes**, que tropeçaram na **mesma** lacuna | **forte** — é o experimento mais bem desenhado do projeto |
| `D-08` (idioma) | medição: mesmo áudio com e sem `language="pt"` → texto idêntico caractere por caractere | **forte** |
| Suíte de regressão da janela | 47 → 91 → 143 → 167 → **230 verificações**, 0 falhas; pegou uma regressão real de sobreposição na 8ª rodada | **parcial** — pega geometria, não pega o que só o Windows mostra, e o projeto diz isso |
| Retomada / continuidade entre chats | o projeto atravessou ~22 dias e ≥9 chats sem perder o fio | **anedótica** — e ver §16, achado 1 |
| Coleta como rastro | reconstruí toda a entrada do subagente lendo só a `coleta/` | **parcial** |
| Painel de roadmap | nenhum registro de que ele foi consultado e mudou uma decisão | **nenhuma evidência encontrada** |
| Três tipos de plano | nenhum plano de manutenção ou acompanhamento jamais criado | **nenhuma evidência encontrada** |
| `revisao-acionada` | um endereço de artefato citado, ilegível pela sessão | **anedótica** |
| Máximo 7 etapas | — | **nenhuma evidência encontrada** |
| Kit exportável | zip gerado em 25/08 existe (`tmp/kit-agentes-base_2026-08-25.zip`, 45 KB); **não há registro de instalação em outro projeto** | **anedótica** |
| Delegação a subagente | 4 despachos nomeados (15 menções), entregas medidas, mas nunca comparada com o caminho de dois chats | **anedótica** |

---

# 16. Problemas e riscos

> Descrição e evidência primeiro. Sem proposta de solução, conforme a regra fundamental do roteiro.

### P1 — A retomada, que é o mecanismo anticontexto-perdido, está desatualizada
**Classe: metodológica.**
`_RETOMADA_usabilidade-gravacao.md` diz no cabeçalho "Última atualização: **2026-08-25**"; o
`mtime` é **2026-08-27**; e o corpo afirma *"a Fase 1: etapas 1, 2 e 6 concluídas, 5 cancelada, **3 é
a próxima**"* e manda "abrir o chat do Executor com a POC-1". O estado real, em `PLANO.md` e
`PROXIMA_TAREFA.md` de **2026-09-06**: Fase 1 encerrada em 24/08, Fase 2 com a Etapa 3 concluída, e a
POC-1 interrompida com o assunto **morto** pela `D-33`. A skill `encerrar-chat` tem "Reescrever a
retomada" como **passo 3 de 4** e não foi executada nos dois últimos chats (05/09 e 06/09).
**Gravidade:** um chat novo que siga o `CLAUDE.md` ("a retomada mais recente na raiz") recebe um
retrato de 11 dias atrás e é instruído a reabrir trabalho que o usuário matou — que é exatamente a
falha já registrada como padrão recorrente na memória de projeto ("status desatualizado
reapresentado").

### P2 — A delegação a subagente não está no método
**Classe: arquitetural + metodológica.**
A `coleta/2026-09-05` menciona **subagente 15 vezes**, com **quatro despachos nomeados por rodada**
("PM despachou a 4ª/5ª/6ª/7ª rodada (subagente `opus`)") além da execução inicial, e registra a
escolha de modelo pelo PM.
`PM.md` continua abrindo com *"Quem executa é o Executor, em outro chat"* e listando "Executar a
tarefa você mesmo" entre as proibições sem exceção. O `CEREBRO.md` §"Como o cérebro evolui" exige
que mudança de método vire `M-nn`; **não existe `M-11`**. O último `M-nn` é de 27/08.
**Gravidade:** a mudança arquitetural mais recente do projeto é invisível para quem lê só o cérebro
— e para o kit exportado.

### P3 — O `PLANO.md` virou log narrativo
**Classe: arquitetural.**
28 KB, 378 linhas. A estrutura obrigatória do `PM.md` prevê 4 seções; o arquivo tem, além delas,
**13 blocos narrativos** ("Segunda rodada…", "Nona rodada despachada…") com hipóteses, medições e
vereditos. Esse conteúdo tem dono declarado: `PROGRESSO.md` (o que o Executor fez) e `D-32` (a
decisão). É a violação da regra 1 da `CONSISTENCIA.md` **dentro** do arquivo que a impõe.

### P4 — O repositório está há 11 dias em estado não commitável
**Classe: funcional + de manutenção.**
`.git/index.lock` presente desde **2026-08-27** (arquivo de 0 byte, `mtime` 27/08). `git status`
mostra **16 arquivos modificados** e **7 não rastreados**, incluindo `desktop/app.py`, `main.py`,
`DECISOES.md`, `PLANO.md`, `PROGRESSO.md` e duas coletas novas. `COMMIT.md` diz que a tarefa do
Executor "só termina com o repositório **pronto para commitar**" — condição não atendida desde
então, com a causa conhecida e registrada em três arquivos.
**Gravidade:** trabalho de 11 dias fora do histórico versionado, e o único enforcement real de
permissão do sistema (o git) é justamente o que está travado.

### P5 — Permissões são apenas prosa
**Classe: de segurança/permissão.**
Nenhum `settings.json`, nenhum hook, nenhuma allowlist. Todas as proibições do `PM.md` e do
`EXECUTOR.md` dependem de o modelo obedecer. O modo sem papel declarado não tem regra nenhuma além
de `COMMIT.md` — e o próprio `COMMIT.md` o chama de "o modo mais desprotegido".
**Evidência de que a conformidade é imperfeita:** o `EXECUTOR.md` registra "já houve erro de anexar
no meio [do `PROGRESSO.md`]"; a memória de projeto registra que a `PROXIMA_TAREFA.md` apontou ≥2
vezes para etapa já executada. As regras foram criadas **depois** das violações, o que é o desenho
declarado ("Regra nova nasce de um problema observado") — mas confirma que não há prevenção.

### P6 — Quatro camadas de memória, dois índices, um deles fora do mapa
**Classe: arquitetural.**
`CEREBRO.md` se declara "o **mapa único**… Nenhum outro arquivo mapeia a estrutura". Existe um
segundo índice (`MEMORY.md`, memória de projeto do cliente, 16 arquivos de tópico) que guarda o
mesmo tipo de fato e **já divergiu**: `projeto_kit_agentes.md` diz que a skill do projeto é
"`coleta-consolidacao` (única)"; há quatro desde 24-25/08.

### P7 — O passe de conferência tem duas cópias por extenso
**Classe: metodológica.**
Os seis itens, na mesma ordem, em `metodo/CONSISTENCIA.md` e em `skills/diagnostico-geral/SKILL.md`.
Pela regra 1 do primeiro arquivo, um dos dois deveria ser ponteiro.

### P8 — Higiene do rascunho não disparou
**Classe: de manutenção.**
`HIGIENE.md`: "O que ficar sem toque até a virada de plano seguinte sai na limpeza, sem pergunta".
`.claude/tmp/` tem **19 entradas, 268 KB**, com arquivos de 25/08 (o zip do kit e a skill empacotada)
que atravessaram a virada. E a mesma regra diz "Se um arquivo do rascunho passou a ter valor,
promova na hora" — o kit exportado, que é um entregável do `M-07`, mora na pasta que existe para
sumir. `B-10` registra a pendência; ela não foi executada.

### P9 — A profundidade de registro não segurou o `PROGRESSO.md`
**Classe: de custo + metodológica.**
Regra: `curto` é o padrão para código, teto ~15 linhas. Medido: 1.942 linhas / 21 entradas =
**~92 linhas por entrada**, com o plano **ainda aberto**. `HIGIENE.md` prevê exatamente esse caso e
manda **avisar em vez de arquivar** ("é sinal de plano se arrastando ou de regra de profundidade não
seguida"). Não há registro do aviso.

### P10 — O gatilho de reabertura de `M-01` foi atingido e não disparou
**Classe: de avaliação.**
`M-01`/`D-09`: verificação manual, "**Reabre se:** houver mais de um cliente consumindo o núcleo".
Hoje há três consumidores (`transcritor/frontend/index.html`, `desktop/app.py`,
`spec/pocs/POC-1/cliente_minimo.py`). A decisão continua `fechada`. Nenhum mecanismo verifica
condições de reabertura — elas são escritas e ficam esperando alguém lembrar.

### P11 — Nenhuma observabilidade do próprio agente
**Classe: de observabilidade.**
Zero registro de tokens, custo, latência ou ferramentas usadas pelo agente, num projeto que mede o
custo do produto por requisição (`consumo.jsonl`, 1.317 linhas) e definiu um alarme em US$/mês.

### P12 — Escala: o método é de um humano só
**Classe: de escalabilidade.**
Toda validação forte passa pelo usuário rodando o artefato; toda autorização passa por ele; o
roteamento de papel é ele digitando uma palavra. O `GUIA` declara isso como limite conhecido
("Quando NÃO vale a pena usar isso"), o que é honesto — mas significa que a taxa de progresso é
limitada pela disponibilidade de uma pessoa, e o rastro das dez rodadas da `D-32` mostra o custo
disso (três pedidos seguidos do `app.log` sem resposta, registrados no `PLANO.md`).

### P13 — Resíduos menores
**Classe: de manutenção.** `spec/decisoes/` existe e está **vazia** (23/08). `coleta/_TEMPLATE.md` é
citado por duas skills e **não existe** (as duas dizem "se existir", então é hedge, não quebra).
`desktop/app.log` é versionado por exceção explícita no `.gitignore` (`!desktop/app.log`) e está em
122 KB / 1.290 linhas, crescendo com execuções headless de subagente. `.claude/scheduled_tasks.lock`
versionado sem propósito declarado. E o `BACKLOG.md` usa um sexto valor de `estado:` — `fechado`
(linha 86, `B-06`) — que não existe no vocabulário declarado em `.claude/painel.md`
(`amadurecendo` · `adiada` · `recusada` · `promovida` · `morta`), então o painel não sabe o que
fazer com ele.

---

# 17. Elementos potencialmente generalizáveis

| Elemento | Evidência | Generalizável? | Motivo | Confiança |
|---|---|---|---|---|
| **Roteamento de papel opt-in por declaração na 1ª mensagem** | `CLAUDE.md`; três modos, incluindo "sem papel" | **Sim** | função: escolher o conjunto de restrições antes de qualquer ação. Independe de domínio, cliente e modelo | **Alta** |
| **Papel como conjunto de proibições, não de capacidades** | `GUIA` §0: "o valor está no limite, não na capacidade" | **Sim** | é o desenho conceitual que faz o resto funcionar; qualquer agente com ferramentas amplas precisa disso | **Alta** |
| **Canal de coordenação por arquivo (`PLANO` / `PROXIMA_TAREFA` / `PROGRESSO`), com dono único por arquivo** | `.claude/estado/`; 21 entradas; funcionou entre chats e entre sessões | **Sim** | função: handoff entre execuções sem estado compartilhado. Sobrevive a troca de cliente e de modelo | **Alta** |
| **Tarefa corrente única, com "O que NÃO fazer" explícito** | formato obrigatório em `PM.md` | **Sim** | limita escopo de execução por construção | **Alta** |
| **Profundidade de registro declarada na tarefa (3 níveis, sobe mas não desce)** | `PM.md`/`EXECUTOR.md` | **Sim** | controle de custo de log genérico; a assimetria é a parte inteligente | **Alta** (do desenho) / **Média** (da eficácia — ver P9) |
| **"Ambiguidade → pare e registre; não improvise"** | `EXECUTOR.md` | **Sim** | trava antialucinação de custo zero | **Alta** |
| **"Achado fora de escopo: reporte, não conserte"** | `EXECUTOR.md`, `revisao-acionada` | **Sim** | separa observação de mudança; preserva a possibilidade de conferir o achado | **Alta** |
| **Regra de dono único por fato + ponteiro em vez de cópia** | `CONSISTENCIA.md` 1; 9 inconsistências medidas | **Sim** | é a regra que sustenta todas as outras num sistema documental | **Alta** |
| **"Nada de número derivado escrito à mão"** | `CONSISTENCIA.md` 2; 4 ocorrências rastreadas | **Sim** | falha de LLM notoriamente comum, com prevenção barata | **Alta** |
| **"Aviso não é conserto"** | `CONSISTENCIA.md` 5 | **Sim** | antipadrão específico de agentes que documentam o próprio trabalho | **Alta** |
| **"O mais recente vence", declarada como desempate e não como desenho** | `CONSISTENCIA.md` 4 | **Sim** | a autoconsciência ("precisar dela com frequência é sintoma") é o que a torna boa | **Média** |
| **Passe de fechamento ao concluir/cancelar etapa** | `CONSISTENCIA.md` 3 | **Sim** | — | **Alta** |
| **Higiene com gatilho declarado; tamanho é alarme, não gatilho** | `HIGIENE.md` | **Sim** | "higiene que depende de boa vontade não acontece" — mas ver P8: o gatilho não disparou aqui | **Média** |
| **Livro-razão de decisões com `Por quê` + `Reabre se`** | 34 `D-nn` + 10 `M-nn`; `D-08` reaberta e refutada por medição | **Sim** | o campo `Reabre se` é a peça rara: transforma decisão em contrato revisável | **Alta** |
| **Separação decisão de método (`M-nn`) × decisão de produto (`D-nn`)**, com migração de ponteiro | `DECISOES_METODO.md` cabeçalho; 4 decisões migradas com ponteiro deixado | **Sim** | é o que permite exportar o método sem arrastar o domínio | **Alta** |
| **Backlog que atravessa fases, item nunca apagado, com `nasceu:` / `estado:` / `olhar de novo em:`** | `BACKLOG.md`, 23 itens, 5 estados | **Sim** | o campo `olhar de novo em` é um gancho mecânico de reabertura — raro e barato | **Alta** |
| **Diário append-only por chat, com 4 marcações e `[DECISÃO]` sempre com trade-off** | `coleta/`, 9 arquivos | **Sim** | reconstruí a entrada do subagente lendo só isso | **Alta** |
| **`[PROPOSTA-ASSISTENTE]` — marcar o que o agente sugeriu** | `skills/coleta-consolidacao` | **Sim** | separa o que o humano decidiu do que o agente propôs; vale para qualquer agente que registre | **Alta** |
| **Datas relativas → absolutas no registro** | idem | **Sim** | falha clássica de log gerado por LLM | **Alta** |
| **Skill de revisão que analisa e nunca corrige, com três razões escritas** | `revisao-acionada` | **Sim** | as razões (achado corrigido não pode mais ser conferido; corrigir muda o terreno da varredura) são independentes de domínio | **Alta** |
| **Achado julgado em 5 campos + veredito, com "recusar com razão" como resultado legítimo** | idem | **Sim** | "achado sem custo declarado é ruído" | **Alta** |
| **Lentes declaradas: "lente que não rodou é cobertura que não existe"** | idem | **Sim** | ataca o silêncio como falso positivo | **Alta** |
| **Seção que aparece mesmo vazia** ("silêncio não distingue conferi de não conferi") | `diagnostico-geral` | **Sim** | princípio geral de relatório de agente | **Alta** |
| **Passo 0: se não há estado em arquivo, diga e pare** | `diagnostico-geral` | **Sim** | precondição verificada antes de produzir saída com cara de autoridade | **Alta** |
| **Procedimento genérico + configuração local em arquivo separado** (`SKILL.md` × `painel.md`) | `M-08` | **Sim** | é o padrão que permite uma skill ser de conta e ainda assim específica por projeto | **Alta** |
| **"Estimativa de esforço não entra"** | `M-08` | **Sim** | "chute com cara de dado, e vira fato na terceira leitura" | **Média** |
| **Menu de comandos consciente de estado dentro do painel** | `diagnostico-geral` | **Sim** | "ferramenta que ninguém lembra que existe é ferramenta que não existe" — problema real de todo projeto com muitas skills | **Média** |
| **Exportação por script, nunca por cópia (`M-07`) + skill de conta como destino, não fonte (`M-09`)** | `kit/exportar.py`, 161 linhas | **Sim** | resolve a deriva do próprio kit; é a regra de dono único aplicada à distribuição | **Alta** |
| **Marcação `kit:projeto` / `kit:modelo` no texto, para o mesmo arquivo servir de fonte e de modelo** | `CLAUDE.md`, `README.md`, `exportar.py` | **Sim** | mecanismo de templating documental simples e eficaz | **Média** |
| **"Só o humano autoriza commit; autorização por ação, não por sessão"** | `COMMIT.md`, `M-05` | **Sim** | o ponto de controle no lugar certo: onde trabalho vira histórico compartilhado | **Alta** |
| **Checklist de "repositório pronto para commit" como parte da definição de pronto** | `COMMIT.md` | **Sim** — o **conceito** | os itens (`index.lock`, `.fuse_hidden`) são do ambiente; o conceito "a entrega inclui não deixar sujeira" é geral | **Média** |
| **Exceção pontual datada, registrada, que "não vira regra por repetição silenciosa"** | `M-10`, exceção de 06/09 no `PLANO.md` | **Sim** | permite flexibilidade sem erosão da regra | **Alta** |
| **Retomada com "mensagem pronta para colar"** | `_RETOMADA_TEMPLATE.md` | **Sim** — o mecanismo | é o prompt de boot da próxima sessão; mas ver P1: o mecanismo **falhou** nesta instalação | **Média** |
| **Três tipos de plano (fase/manutenção/acompanhamento)** | `PLANOS.md` | **Incerto** | o argumento é bom e genérico; **nunca foi exercido aqui** (nenhum `MANUTENCAO.md` ou `ACOMPANHAMENTO.md` jamais criado) | **Baixa** |
| **Delegação a subagente com escolha de modelo pelo despachante** | `coleta/2026-09-05`, 15 menções / 4 despachos nomeados | **Incerto** | funcionou, mas nunca foi comparado com o caminho de dois chats e não virou regra escrita | **Baixa** |
| **Máximo 7 etapas por plano** | `PM.md` | **Incerto** | o número não tem razão registrada | **Baixa** |

---

# 18. Elementos específicos, que **não** devem ir para uma base comum

| Elemento | Por que é específico | Classe |
|---|---|---|
| Todo o `spec/` — VISAO, 34 `D-nn`, MAPA, contrato do núcleo, SPEC-001/002, histórias, `COMPORTAMENTOS_PARQUEADOS` | é o produto: transcrição, ditado, Windows, OpenAI | **D** |
| `transcritor/`, `desktop/`, `audio-teste/` | código do produto | **D** |
| `.claude/metodo/DECISOES_METODO.md` (10 `M-nn`) | por desenho: "projeto novo começa com ledger vazio — herda as regras, não as escolhas" | **D** (o **formato** é A) |
| `.claude/painel.md` inteiro | fontes, paleta, endereço fixo do artefato, régua de alerta com US$ 100/mês e "PoCs rodadas" | **D** |
| A régua de alerta do painel | "histórias de usuário em zero a partir da Fase 2" só faz sentido com este mapa de fases | **D** |
| Bloco "Antes do método" do painel | data de início e os cinco planos pré-método deste projeto | **D** |
| `_RETOMADA_usabilidade-gravacao.md` | conteúdo do projeto; o **template** é que é genérico | **D** |
| `coleta/*` | diário deste projeto | **D** |
| Nota de heredoc para escrever em `.claude/` (`PM.md`) | remendo de um cliente específico com pasta montada | **C** |
| Itens `.fuse_hidden*`, `.git/index.lock`, `HEAD.lock`, `_to_delete/` (`HIGIENE.md`, `COMMIT.md`) | existem por causa de bridge remoto; **hoje viajam no kit** | **C** |
| `M-06` (o cérebro mora em `.claude/`) | escolha por conveniência de ferramenta, e o próprio `M-06` diz isso | **C** |
| Regra de idioma pt-BR no `CLAUDE.md` | o **mecanismo** (fixar idioma) é A; o **valor** é D | **A/D** |
| Passo "aplicar" removido da `coleta-consolidacao` | consequência de este projeto não ter destino final separado | **D** |
| "Armadilha da porta 8000: 6 ocorrências" (`PLANO.md`) | ambiente deste produto | **D** |
| Lista `INCLUIR` de 18 caminhos em `exportar.py` | o **script** é A; a lista é desta instalação | **A/D** |
| `.gitignore` com `!desktop/app.log`, `transcritor/consumo.jsonl` etc. | deste produto | **D** |

---

# 19. Resumo estrutural

| Dimensão | Implementação atual | Generalizável? | Evidência | Observação |
|---|---|---|---|---|
| **Entrada** | chat de texto; roteamento opt-in por palavra ("PM"/"EXEC"/nada) | **Sim** (o mecanismo) | `CLAUDE.md` | única entrada; sem normalização, sem classificação automática |
| **Contexto** | leitura de arquivo guiada por um mapa único (`CEREBRO.md`) + recorte por papel | **Sim** | `CEREBRO.md` §"Quem lê o quê" | custo fixo medido: ~9 k (PM) / ~5,5 k (EXEC) tokens por chat |
| **Retrieval** | leitura direta; sem índice, sem semântica, sem ranking; teto de contexto por papel e por citação | **Sim** (a política) | `EXECUTOR.md` | a decisão de *quanto* recuperar existe e é por política, não por medição |
| **Raciocínio** | regras em prosa interpretadas pelo LLM | **Sim** (as regras) | `.claude/metodo/` | nenhuma decisão é código |
| **Planning** | PM propõe → humano aprova → 1 tarefa por vez, máx. 7 etapas | **Sim** | `PM.md` | **workflow fixo**, não planning autônomo — e é deliberado |
| **Tools** | 1 script (`exportar.py`) + 4 skills; ferramentas reais são do cliente e não são declaradas | **Sim** (as skills) | `.claude/skills/` | nenhuma seleção de ferramenta é governada pelo repositório |
| **Agents** | 1 agente, 2 papéis, 3º modo sem papel | **Sim** | `GUIA` §0 | "papel não é outro agente" — a distinção está certa e é rara |
| **Delegação** | por arquivo entre chats (documentada) **+ subagente na mesma sessão** (não documentada) | **Sim** (a primeira) / **Incerto** (a segunda) | `PROXIMA_TAREFA.md`; `coleta/2026-09-05` | **Documentado ≠ implementado** — ver P2 |
| **Estado** | 3 arquivos com dono único + histórico com gatilho de virada | **Sim** | `.claude/estado/` | `PROGRESSO.md` em 154 KB com plano aberto (P9) |
| **Memória** | 4 camadas no repo + 2 fora dele; 2 índices concorrentes | **Sim** (as 4 do repo) | `DECISOES`, `coleta/`, `MEMORY.md` | o "mapa único" não é único (P6) |
| **Validação** | humano no artefato real; 230 verificações de 1 componente; passe de conferência sob demanda | **Sim** (o desenho) | `PLANO.md`, `testes_janela_compacta.py` | nada valida o **escopo** antes do despacho — a falha de 27/08 |
| **Observabilidade** | decisões, execução e rastro conversacional excelentes; **zero** telemetria do agente | **Sim** (o que existe) | `PROGRESSO`, `coleta/`, `DECISOES` | mede o custo do produto, não o do processo (P11) |
| **Permissões** | prosa; 3 enforcements reais, todos do ambiente ou do git | **Sim** (o modelo conceitual) | `PM.md`, `COMMIT.md` | "capacidade × permissão" está bem articulado e **tecnicamente desprotegido** (P5) |
| **Output** | texto no chat + escrita de estado + painel publicado em endereço fixo | **Sim** (o padrão vista≠fonte) | `M-02`, `diagnostico-geral` | "o painel é vista, não fonte de verdade" |

---

# 20. Resultado final — as cinco entregas

## Entrega 1 — Arquitetura atual

Ver §1 (diagrama e tabela etapa a etapa) e §12 (camadas). Em uma frase:

> **Um agente de propósito geral, externo ao repositório, conduzido por um protocolo documental de
> dois papéis mutuamente exclusivos, cujo canal de coordenação é o sistema de arquivos, cujas
> permissões são prosa e cuja validação forte é um humano rodando o artefato.**

## Entrega 2 — Inventário

- **Componentes (método):** `CLAUDE.md` (roteador) · `CEREBRO.md` (mapa) · `PM.md` · `EXECUTOR.md` ·
  4 regras genéricas em `metodo/` + 1 ledger local · 4 skills · `estado/` (3 vivos + 22 históricos) ·
  `kit/exportar.py` · `painel.md` (config) · `_RETOMADA_TEMPLATE.md`.
- **Componentes (produto, para contraste):** `transcritor/backend/main.py` (6 rotas) ·
  `transcritor/frontend/index.html` · `desktop/app.py` (3.955 linhas) ·
  `desktop/testes_janela_compacta.py` (230 verificações) · `spec/` (VISAO, MAPA, 34 `D-nn`, 23 `B-nn`,
  LACUNAS, QUESTOES, contrato, 2 SPECs, 7 histórias, POC-1).
- **Regras:** 45 diretivas nomeadas de método e skill (13 de conduta/papel, 16 de `metodo/`, 16 de
  skills), inventariadas e classificadas em §11.
- **Ferramentas:** 1 script + 4 procedimentos; as demais são do cliente e não estão declaradas (§5).
- **Agentes:** 1, com 2 papéis + 1 modo sem papel; delegação por arquivo e por subagente (§7).
- **Retrieval:** leitura de arquivo com mapa e recorte por papel; nenhum mecanismo de busca (§3).
- **Memória:** 6 camadas, 4 no repositório e 2 fora (§6).
- **Estado:** 3 arquivos vivos com dono único + `historico/` (§6).
- **Validação:** 8 mecanismos, 1 automatizado e parcial (§8).

## Entrega 3 — Classificação

- **Generalizável (A):** roteamento de papel opt-in; papel como conjunto de proibições; canal de
  coordenação por arquivo com dono único; tarefa única com "o que NÃO fazer"; profundidade de
  registro declarada; "pare em vez de improvisar"; "reporte, não conserte"; as 5 regras de
  consistência; higiene com gatilho; livro-razão com `Por quê`/`Reabre se`; separação `M-nn`/`D-nn`;
  backlog com `olhar de novo em`; diário append-only com 4 marcações e `[PROPOSTA-ASSISTENTE]`;
  revisão que não corrige; achado em 5 campos; lentes declaradas; seção que aparece vazia; passo 0 de
  precondição; procedimento genérico + config local; autorização de commit por ação; exceção datada;
  exportação por script; `kit:projeto`/`kit:modelo`.
- **Dependente do domínio (B):** praticamente nada no método — o que é de domínio está todo em
  `spec/`, e é o produto.
- **Dependente da implementação (C):** nota de heredoc para `.claude/`; itens de lixo de bridge
  remoto em `HIGIENE.md` e `COMMIT.md`; `M-06`; a dependência de o cliente registrar skills.
- **Específico do projeto (D):** `spec/` inteiro; `transcritor/`; `desktop/`; `painel.md`;
  `DECISOES_METODO.md`; `coleta/`; a retomada preenchida; a régua de US$ 100/mês; a lista `INCLUIR`.
- **Incerto (E):** os três tipos de plano (nunca exercidos); o limite de 7 etapas; a delegação a
  subagente (funciona, não foi comparada, não virou regra); a `revisao-acionada` (não determinado
  quantas vezes rodou).

## Entrega 4 — Problemas

Treze, detalhados em §16 com evidência medida. Os cinco que mudam a leitura do resto:

1. **P1** — a retomada, que é o mecanismo anticontexto-perdido, está 11 dias atrasada e manda
   reabrir trabalho morto (metodológico).
2. **P2** — a delegação a subagente, mudança arquitetural mais recente, não existe em nenhum arquivo
   de método (arquitetural).
3. **P4** — 11 dias de trabalho fora do git, com `index.lock` conhecido e não resolvido (funcional).
4. **P5** — permissões são prosa; os únicos enforcements reais são acidentes do ambiente
   (segurança/permissão).
5. **P3 + P9** — o `PLANO.md` virou log e o `PROGRESSO.md` não obedece à regra de profundidade: as
   duas regras mais citadas do método estão sendo violadas nos arquivos que as carregam
   (arquitetural + custo).

**Duplicações:** o passe de conferência por extenso em dois arquivos (P7); a profundidade de registro
quase inteira nos dois papéis; a narrativa da `D-32` em quatro lugares.
**Acoplamentos:** ao cliente/ambiente (três arquivos genéricos com remendo específico); do
`exportar.py` a uma lista literal; do painel a um endereço fixo.
**Sem evidência de eficácia:** três tipos de plano; limite de 7 etapas; painel como instrumento de
decisão; `revisao-acionada`; instalação do kit em outro projeto.

## Entrega 5 — Candidatos ao Agents Base

Em ordem de confiança, com a **função** que cada um desempenha (que é o critério, não a elegância):

**Núcleo — alta confiança**

1. **Roteamento de papel opt-in** — escolher o conjunto de restrições antes de agir.
2. **Papel = proibições, não capacidades** — o desenho conceitual que faz o resto funcionar.
3. **Canal de coordenação por arquivo, com dono único por arquivo** — handoff sem estado
   compartilhado, sobrevive a troca de chat, de cliente e de modelo.
4. **Tarefa corrente única com "O que NÃO fazer" explícito** — limite de escopo por construção.
5. **"Pare em vez de improvisar"** e **"reporte, não conserte"** — as duas travas antialucinação de
   custo zero.
6. **Regra de dono único por fato + ponteiro em vez de cópia** — a regra que sustenta as outras.
7. **"Nada de número derivado escrito à mão"** — 4 ocorrências medidas do erro que ela previne.
8. **"Aviso não é conserto"** — antipadrão específico de agente que documenta o próprio trabalho.
9. **Livro-razão com `Por quê` + `Reabre se`** — decisão como contrato revisável.
10. **Separação decisão-de-método × decisão-de-produto, com ledger local que não viaja** — é o que
    torna o método exportável.
11. **Autorização de commit por ação, nunca por sessão** — o ponto de controle no lugar certo.
12. **Exceção pontual datada e registrada** — flexibilidade sem erosão da regra.

**Registro e revisão — alta confiança**

13. **Profundidade de registro declarada na tarefa, com "sobe mas não desce"**.
14. **Diário append-only por interação, 4 marcações, `[DECISÃO]` sempre com trade-off**.
15. **`[PROPOSTA-ASSISTENTE]`** — marcar o que o agente sugeriu, para não virar fato do usuário.
16. **Datas relativas → absolutas no registro**.
17. **Revisão que analisa e nunca corrige**, com as três razões escritas.
18. **Achado julgado em cinco campos + veredito**, com "recusar com razão" como resultado legítimo.
19. **Lentes declaradas** — "lente que não rodou é cobertura que não existe".
20. **Seção que aparece mesmo vazia** — silêncio não distingue conferido de não conferido.
21. **Passo 0 de precondição** — se não há do que montar, diga e pare.

**Distribuição e configuração — alta/média confiança**

22. **Procedimento genérico + configuração local em arquivo separado**.
23. **Exportação por script, nunca por cópia; skill de conta é destino, não fonte**.
24. **Marcação `kit:projeto` / `kit:modelo`** para o mesmo arquivo ser fonte e modelo.
25. **Backlog que atravessa fases, com `nasceu:` / `estado:` / `olhar de novo em:`**.
26. **Higiene com gatilho declarado; tamanho é alarme, não gatilho** — desenho bom, cumprimento
    fraco nesta instalação (P8).
27. **Retomada com mensagem pronta para colar** — mecanismo bom, **falhou aqui** (P1); levar sabendo.

**A comparar com os outros dois projetos antes de decidir** *(evidência insuficiente aqui)*

28. Três tipos de plano (fase / manutenção / acompanhamento) — nunca exercido.
29. Delegação a subagente com escolha de modelo pelo despachante — funciona, não comparada.
30. Limite de 7 etapas por plano — sem razão registrada.
31. Menu de comandos consciente de estado — argumento forte, uso não medido.

---

## Anexo — o que esta auditoria **não** determinou

- Quantas vezes a `revisao-acionada` rodou, e o que ela achou (o relatório está num artefato
  publicado que a sessão não consegue ler).
- Se o kit foi instalado em algum outro projeto, e com que resultado (o `README.md` cita o
  repositório da Mari como origem; não há registro do caminho inverso).
- Qualquer número de custo, latência ou consumo de tokens do próprio agente — o projeto não registra
  nada disso.
- O comportamento real do agente sob as regras: só é possível auditar o que ficou escrito, e o que
  ficou escrito é, por desenho, o que alguém decidiu registrar.
