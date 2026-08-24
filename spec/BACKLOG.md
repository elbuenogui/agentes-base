---
artefato: BACKLOG
status: vivo
---

# Backlog — ideias que não são etapa

Dono único da **ideia que ainda não é trabalho**. Criado em 2026-08-23, tirando o acervo de dentro do
`.claude/estado/PLANO.md`.

**Por que saiu do plano:** o backlog **atravessa fases**, e o `PLANO.md` morre a cada fase. Há item
nascido em 16 e 18/08 ainda vivo num plano de uma fase aberta em 21/08. E cada plano arquivado
congelou uma cópia do acervo: são **60 arquivos** em `.claude/estado/historico/`, cada um com a sua
versão da mesma recusa — quem procura "por que isso foi recusado" recebe dezenas de respostas de
datas diferentes, e a mais recente não é a que aparece primeiro. Conteúdo que atravessa fases não
mora em arquivo que morre com a fase (`D-21`).

> **Duas correções de número neste arquivo (2026-08-23).** Ele nasceu dizendo "treze versões do
> plano" — contagem feita só sobre `historico/PLANO_*.md`, esquecendo `snapshots/`. Corrigido para
> 60, e aí veio a segunda correção, a que importa: **os 60 não são 60 planos**. São 4 viradas de
> plano de verdade, 8 salvamentos datados e 48 snapshots automáticos, com mediana de 18 linhas de
> diferença entre consecutivos. A justificativa acima foi reescrita para não depender de contagem
> de cópias — o que sustenta este arquivo é o backlog atravessar fases, não quantas vezes alguém
> o recopiou. 3ª e 4ª ocorrências da armadilha do número inferido (Nota de processo do `PLANO.md`).

## Como se lê um item

    ### B-nn — título
    `estado: ... · nasceu: data, onde · olhar de novo em: fase`
    a ideia
    **Por quê ainda não:** ...

- **`estado`** — `amadurecendo` (candidata real, com fase-alvo) · `adiada` (com gatilho declarado) ·
  `recusada` (a razão mora numa decisão, aqui fica a ideia) · `promovida` (virou etapa) · `morta`.
- **`nasceu`** — a ideia carrega a própria origem, para não se julgar fora de contexto.
- **`olhar de novo em`** — o gancho mecânico: quando uma fase fecha, o passe de fechamento (`D-21`)
  lê os itens marcados para a próxima e pergunta ao usuário quais sobem.

**Regra que faz o amadurecimento existir: item nunca é apagado, só muda de estado.** Uma ideia ruim
na Fase 1 e boa na Fase 2 registra essa mudança de temperatura aqui, em vez de ser recopiada idêntica
ou de sumir quando alguém cansa de copiar.

**Recusada com razão mora nos dois lugares, cada um com sua parte** (decisão do usuário, 2026-08-23):
a **decisão** guarda o motivo e a condição de reabertura; o **backlog** guarda a ideia, viva para ser
revisitada. Não é cópia — é divisão de papel.

> **Correção de número, 2026-08-23**: este arquivo nasceu dizendo "treze versões do plano" — contagem
> feita só sobre `historico/PLANO_*.md`, esquecendo a subpasta `snapshots/`. O real é 60. É a 3ª
> ocorrência da armadilha do número inferido registrada na Nota de processo do `PLANO.md`, e desta vez
> o número errado sustentava o argumento para criar este próprio arquivo. Corrigido antes do fim da
> sessão; o argumento ficou mais forte, não mais fraco.

---

## Amadurecendo

### B-01 — Arrastar e soltar áudio na área central
`estado: amadurecendo · nasceu: 2026-08-21, frente de interface · olhar de novo em: F2`
Soltar o arquivo na área central para enviar, sem passar pelo menu.
**Por quê ainda não:** adiado pelo próprio usuário para depois da frente de interface enxuta
("posteriormente vamos voltar com o drag de áudio"). É interação de cliente, e o cliente que importa
agora é o desktop da F2.

### B-03 — Commit guiado por silêncio (plano B das emendas)
`estado: amadurecendo · nasceu: 2026-08-20, modo ao vivo · olhar de novo em: quando o ao vivo descongelar (D-02)`
Os 6s viram **piso** em vez de corte: o turno fecha na primeira pausa depois disso, com um teto para
não segurar o texto indefinidamente.
**Por quê ainda não:** o modo ao vivo está congelado (`D-02`). A ideia é boa e barata — não muda
custo (quem define custo é o gate de envio, não o commit), mantém `gpt-live-transcribe` e resolve o
corte de palavra na emenda sem depender da API. Fica esperando o consumidor aparecer.

### B-04 — Transcrição em blocos com sobreposição
`estado: amadurecendo · nasceu: 2026-08-19, contas de custo · olhar de novo em: quando o ao vivo descongelar (D-02)`
Fatiar o áudio em blocos que se sobrepõem, para dar precisão nas bordas sem a API ao vivo.
**Por quê ainda não:** o usuário decidiu em 2026-08-19 testar a API ao vivo primeiro, por ser mais
simples de integrar. Sai mais barato por minuto que a API ao vivo mesmo com sobreposição generosa,
mas exige lógica própria de continuidade nas bordas.

### B-05 — Adiantamento artificial de exibição no streaming
`estado: amadurecendo · nasceu: 2026-08-19 · olhar de novo em: F2`
Em áudios curtos o efeito de streaming é imperceptível: o texto chega quase de uma vez.
**Por quê ainda não:** é decisão de sensação de uso, e o único cliente que vai sentir isso é o app
de ditado da F2. **Decisão pendente do usuário** sobre se vale a pena.

### B-06 — Consolidar US-D02 + US-A02 + US-D03 numa capacidade só
`estado: amadurecendo · nasceu: 2026-08-21, revisão do pré-projeto · olhar de novo em: F2`
As três histórias viram *entrega do texto no destino*, com escada de fallback: campo em foco →
área de transferência → janela.
**Por quê ainda não:** histórias são a primeira entrega da própria F2 (`D-13`), e escrever isso antes
da POC-1 seria escrever sobre suposição.

### B-07 — Plataforma de chat self-hosted como motor de fase futura
`estado: amadurecendo · nasceu: 2026-08-18 · olhar de novo em: F6`
Open WebUI, LibreChat, AnythingLLM, Dify, LobeHub — avaliar se alguma serve de motor em vez de
construir agente do zero.
**Por quê ainda não:** discutido em 2026-08-18, com decisão de continuar em outro chat; nenhuma ação
tomada neste projeto. A F6 acontece de qualquer forma (`D-12`), então esta avaliação tem destino
certo.

## Adiadas com gatilho

### B-08 — Fechar o CORS do backend
`estado: adiada · nasceu: 2026-08-18 · gatilho: o núcleo ser servido fora da máquina do usuário`
`allow_origins=["*"]` hoje. Confirmado por medição em 2026-08-23 (lacuna L7 do contrato).
**Por quê ainda não:** aceitável enquanto tudo roda local. Vira restrição declarada no dia em que
sair da máquina — o mesmo gatilho da `D-05` (servidor próprio).

### B-09 — Trocar os `.jsonl` por banco de dados
`estado: adiada · nasceu: 2026-08-18 · gatilho: ver D-22`
`consumo.jsonl` e `transcricoes.jsonl` viram banco de verdade.
**Por quê ainda não:** decisão explícita do usuário em 2026-08-18 de adiar. **O motivo e as
consequências abertas moram na `D-22`** (histórico é requisito) — inclusive a retenção de
transcrições antigas e o fato de `consumo.jsonl` misturar uso real com sessões de teste do Executor.
Aqui fica só a ideia.

### B-10 — Limpeza de `.claude/tmp/` e de `_to_delete/`
`estado: adiada · nasceu: 2026-08-21, faxina · gatilho: nenhum — quando incomodar`
584 KB de rascunho em `tmp/` (`teste_linha_tempo.wav`, `uvicorn.log`, roteiros de teste, cópias de
tarefas já executadas) e o fóssil `index.lock.2026-08-16` de 0 byte em `_to_delete/`.
**Por quê ainda não:** deixado fora do plano por decisão do usuário na faxina de 2026-08-21. Nada
disso é versionado — é ruído visual, não risco.

## Longo prazo, sem fase atribuída

### B-11 — Histórico por projeto/entrevista, exportação, metadados
`estado: amadurecendo · nasceu: 2026-08-16 · olhar de novo em: F2 (ver D-22)`
Organizar transcrições por projeto ou entrevista, exportar, guardar metadados.
**Por quê ainda não:** o histórico virou requisito (`D-22`) mas ganha história de usuário própria só
quando a F2 for especificada.

### B-12 — Pipeline de limpeza → segmentação → classificação → resumo
`estado: amadurecendo · nasceu: 2026-08-16 · olhar de novo em: F5/F6`
Modelos especializados encadeados depois da transcrição.

### B-13 — Busca semântica, embeddings, RAG, corpus de entrevistas
`estado: amadurecendo · nasceu: 2026-08-16 · olhar de novo em: F9`
Depende de `B-09` e é a cara da fase de memória.

### B-14 — Camada de agente que escolhe modelo e informação
`estado: amadurecendo · nasceu: 2026-08-16 · olhar de novo em: F6`
Coberta pela `D-12`: a F6 acontece de qualquer forma.

### B-15 — Suporte a celular e smartwatch
`estado: promovida · nasceu: 2026-08-16 · virou: F3 e F4 na VISAO.md`
Deixou de ser ideia de backlog quando o mapa de fases foi escrito em 2026-08-21.

## Recusadas — a ideia fica, o motivo mora na decisão

### B-02 — Baratear o modo ao vivo trocando o modelo
`estado: recusada · nasceu: 2026-08-20 · motivo: D-23 · olhar de novo em: se custo virar prioridade`
Trocar `gpt-live-transcribe` (US$ 0,017/min) por `gpt-4o-transcribe` (US$ 0,006/min).
**Por quê ainda não:** o usuário prefere nuance de fala a economia, tendo recurso disponível. Os
números da economia real, o contraponto medido do `BENCHMARK.md` e a condição de reabertura estão na
**`D-23`** — quem retomar isto lê a decisão antes, porque ela contém um indício que enfraquece a
própria recusa.

### B-16 — Alternador de controle de turno e detecção pela API
`estado: morta · nasceu: 2026-08-20 · morreu: 2026-08-20`
Deixar o usuário escolher entre controle de turno próprio e detecção da API.
**Por quê morta:** construída e encerrada sem uso no mesmo dia — `gpt-live-transcribe` recusa
`turn_detection` diferente de `null`, e a alternativa exigia trocar de modelo (`B-02`, recusada). O
que se aprendeu está em `.claude/estado/historico/CONTROLE_TURNO_REMOVIDO_2026-08-20.md`. Não é
adiamento: o caminho está fechado enquanto o modelo for esse.

### B-17 — Régua do Win+H como critério de aceitação
`estado: morta · nasceu: 2026-08-21 · morreu: 2026-08-21, pela D-10`
A proposta do PM de que o ditado precisa ser pelo menos tão rápido e preciso quanto a digitação por
voz nativa do Windows.
**Por quê morta:** a `D-10` aposentou a régua no dia seguinte — o usuário reporta que o app de hoje
já é mais rápido, mais preciso e com mais opções que o Win+H. Régua já superada não serve de alvo; a
régua passou a ser **não piorar o que ele já usa**. Este item pedia "aceite explícito do usuário" até
2026-08-23, para uma régua que já não existia.

## Promovidas a etapa

### B-18 — Promover o harness do modo ao vivo a arquivo versionado
`estado: promovida · nasceu: 2026-08-20 · virou: Etapa 4 do PLANO.md`
`.claude/tmp/teste_tempo_real.py`, o harness em Python que validou o protocolo da API ao vivo sem
navegador — o único arquivo com valor dentro de uma pasta descartável.
**Nota**: esteve no Backlog **e** como Etapa 4 do plano ao mesmo tempo, de 21 a 23 de agosto. É o
tipo de duplicação que este arquivo existe para acabar: item promovido muda de estado e aponta para a
etapa, não vive nos dois lugares.

---

## Achados desta sessão que viraram item

### B-19 — Regra de snapshot do PLANO sem limiar nem limpeza
`estado: amadurecendo · nasceu: 2026-08-23, ao conferir o número de versões do plano · olhar de novo em: próxima faxina`
O `PM.md` manda salvar a versão anterior do `PLANO.md` "ao reescrever de forma relevante". O
"relevante" nunca foi aplicado: são **48 snapshots** em `historico/snapshots/` (772 KB), com mediana
de **18 linhas** de diferença entre consecutivos e vários de 4 a 7 — em 20/08 foram 20 num dia. O
`historico/` inteiro pesa 1,3 MB.
**Por quê ainda não:** é ruído, não risco — nada disso é lido para executar. Mas atrapalha de um jeito
concreto: foi essa pilha que fez o PM contar "60 versões do plano" como se fossem 60 decisões, e
qualquer busca por texto no `historico/` devolve dezenas de cópias do mesmo trecho.
**O que faria virar etapa:** um limiar declarado (só salva se mudou mais que N linhas ou se é virada
de plano) mais uma limpeza dos snapshots que não são virada. Combina com a limpeza do `B-10`.

### B-20 — Revisão com agentes especialistas por área
`estado: amadurecendo · nasceu: 2026-08-23, ao desenhar a revisão acionada · olhar de novo em: quando a revisão acionada tiver rodado algumas vezes`
Rodar a revisão com **agentes especialistas**, cada um trazendo as perguntas da própria área —
segurança, DevOps, dados, custo, acessibilidade — em vez de lentes genéricas descritas por texto.
Cada um varre sem ver o que os outros acharam, e a consolidação vem depois.
**Por quê ainda não:** a versão com lentes por texto já está na skill e precisa rodar algumas vezes
para mostrar onde ela cega. Correção do usuário, que vale registrar: **não são vários agentes fazendo
a mesma pergunta** — são áreas diferentes fazendo as perguntas delas e buscando as respostas delas.
Cinco agentes com a mesma pergunta custam cinco vezes mais e acham o mesmo.
**O que faria virar etapa:** uma revisão acionada em que um achado importante só aparecesse se
alguém soubesse perguntar como um especialista da área — aí a lente por texto provou o limite dela.
