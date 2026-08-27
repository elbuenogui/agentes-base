---
artefato: VISAO
status: aprovada
data: 2026-08-21
---

# Visão — Assistente pessoal multiplataforma

> **O usuário não deve precisar sair do ambiente em que está para acessar o assistente.**

O produto evolui de uma ferramenta de transcrição para um assistente que recebe voz, transcreve,
entrega o texto no contexto atual, entende o contexto, usa uma LLM, executa ações e mantém memória —
em desktop, Android e smartwatch. O botão é o ponto de entrada, não o produto.

O `transcritor/` deste repositório é a **Fase 1** já implementada, não um projeto separado.

## Onde cada informação mora

**O mapa único está em [`.claude/CEREBRO.md`](../.claude/CEREBRO.md).** Este arquivo não repete o
mapa — até 2026-08-23 quatro arquivos diferentes mapeavam a estrutura, e quatro mapas parciais é o
mesmo que nenhum.

Do que este arquivo é dono: **a visão do produto e o mapa das fases**, abaixo. As decisões de produto
moram em `DECISOES.md`; as de método, no cérebro.

## Como este plano se organiza

Dois níveis, e só dois: o **mapa de fases** (abaixo), com uma linha de profundidade por fase, e a
**fase corrente**, funda. Não se escreve spec de fase futura; antes de especificar a fase N escreve-se
a lista de entregáveis dela; e uma fase só encerra com o entregável **em uso**, não com o documento
pronto.

## Mapa de fases

Numeração: a do corpo do pré-projeto (9 fases + futura). O roadmap da §3, que tinha 8, fica
corrigido por esta decisão.

### F1 — Núcleo de transcrição
`estado: encerrada`
Fechou o contrato do núcleo, medido contra a máquina e não suposto. Encerrada em **2026-08-24** com
todas as etapas concluídas: contrato levantado por medição, SPEC-001 fechada, as quatro lacunas
aprovadas corrigidas (códigos de erro, prazo de espera, teto de tamanho e versão do contrato) e a
arrumação feita. A Etapa 5 (parâmetro de idioma) caiu por medição (`D-08`).

**Critério de conclusão, exercido e respondido em 2026-08-26**: dois clientes novos foram escritos
lendo só o contrato, sem abrir o código. **Ele bastou**, com uma lacuna única — não declarava onde o
núcleo escuta. Os dois tropeçaram na mesma coisa, de forma independente, o que é a melhor evidência
possível de que era lacuna real e não distração de um deles. Fechada no contrato na mesma data. **A
Fase 1 fecha de verdade.**

### F2 — Desktop, ditado universal
`estado: em-andamento`
Atalho, fala, texto no campo em foco. **É a fase que o usuário quer usar todo dia**, e é o que
justifica adiar o agente (`D-24`). Régua: **não piorar o que ele já usa** (`D-10`). Windows primeiro,
com a camada de inserção isolada (`D-11`).

Três etapas no `PLANO.md`, e só três de propósito: a **POC-1** (a única coisa capaz de invalidar o
desenho do produto, e que decide a linguagem do app), as **histórias, entregáveis e MVP** (`D-13`), e
só então o resto do plano. **Encerra com uso em regime, não com o app pronto.**

### F3 — Android, ditado universal
`estado: bloqueada:POC-3`
A mesma capacidade no S22. Entrega duas coisas: o app e o documento do que a plataforma permite e
do que não permite. Hover não existe em toque — a interação do desktop não se reproduz; o núcleo,
sim.

### F4 — Smartwatch
`estado: nao-iniciada`
Validar o relógio como entrada de voz, não como assistente. **Aparelho em mãos: Galaxy Watch 5.**
PoC-5: Wear OS, latência, bateria, e a gestão agressiva de bateria da Samsung. O relógio é cliente
magro e o telefone é o núcleo dele (`D-03`, `D-04`).

### F5 — Integração com GPT
`estado: nao-iniciada`
Até onde dá para integrar a entrada de voz com uma LLM existente sem construir agente próprio.
Ordem entre F4 e F5 ainda em aberto — decisão adiada para o fim da F3.

### F6 — Agente open source
`estado: nao-iniciada`
**Acontece de qualquer forma** (`D-12`). O resultado da F5 define quando: se a integração direta
não funcionar, entra imediatamente; se funcionar, é testada por mais tempo e o agente vem depois.

### F7 — Contexto
`estado: nao-iniciada`
Captura sob demanda, no acionamento. Monitoramento contínuo de tela fica fora. É aqui que o
servidor próprio deixa de ser opcional (`D-05`).

### F8 — Ferramentas e automações
`estado: nao-iniciada`
O agente executa ações, não só devolve texto.

### F9 — Memória e contexto persistente
`estado: nao-iniciada`
Continuidade entre interações e aparelhos. Restrição de produto: **memória e estado não podem ficar
presos a uma LLM** — trocar de modelo não apaga o assistente.

### FF — Tradução e intérprete
`estado: futuro`
Fora da prioridade inicial. Reaproveita o pipeline pronto.
