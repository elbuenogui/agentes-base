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

### B-01 — Arrastar e soltar áudio
`estado: promovida · nasceu: 2026-08-21, frente de interface · virou: SPEC-002 E2, em 2026-08-27`
Soltar o arquivo de áudio para transcrever, sem passar pelo menu.
**Promovida a pedido do usuário**, depois de usar o app de desktop: *"eu gostaria que se arrastasse
um arquivo de áudio até o botão ele transcrevesse"*. O alvo do solte é o **botão de gravar**, e o
caminho é o mesmo do "Enviar arquivo" (`E1`). Detalhe em `spec/specs/SPEC-002_paridade-desktop.md`.

### B-03 — Commit guiado por silêncio (plano B das emendas)
`estado: morta · nasceu: 2026-08-20, modo ao vivo · morta: 2026-09-05 (D-33)`
Os 6s viram **piso** em vez de corte: o turno fecha na primeira pausa depois disso, com um teto para
não segurar o texto indefinidamente.
**Por quê morta:** dependia do modo ao vivo descongelar (`D-02`), e o modo ao vivo saiu de vez
(`D-33`, 2026-09-05) — o gatilho desta ideia nunca vai acontecer. A ideia em si continua boa e
barata, registrada aqui só para quem um dia reconsiderar o modo ao vivo por outro motivo.

### B-04 — Transcrição em blocos com sobreposição
`estado: morta · nasceu: 2026-08-19, contas de custo · morta: 2026-09-05 (D-33)`
Fatiar o áudio em blocos que se sobrepõem, para dar precisão nas bordas sem a API ao vivo.
**Por quê morta:** dependia do modo ao vivo descongelar (`D-02`), que saiu de vez (`D-33`,
2026-09-05) — o cenário que justificava esta ideia (precisão de borda sem a API ao vivo) deixou de
existir junto com o modo ao vivo.

### B-05 — Adiantamento artificial de exibição no streaming
`estado: amadurecendo · nasceu: 2026-08-19 · olhado em 2026-09-06, mantido fora do MVP da F2 (D-34)`
Em áudios curtos o efeito de streaming é imperceptível: o texto chega quase de uma vez.
**Por quê ainda não:** é decisão de sensação de uso, e o único cliente que vai sentir isso é o app
de ditado da F2. **Decisão pendente do usuário** sobre se vale a pena.

### ~~B-06 — Consolidar US-D02 + US-A02 + US-D03 numa capacidade só~~
`estado: fechado em 2026-09-06 · nasceu: 2026-08-21, revisão do pré-projeto`
Virou a **`US-D02`** (`historias/F2_ditado-universal.md`): *entrega do texto no destino*, uma
capacidade só. A escada de fallback ficou com **dois degraus** em vez de três — área de
transferência (padrão) e a janela para copiar à mão; o degrau 1, inserir no campo em foco, morreu
na `D-33`.

### B-07 — Plataforma de chat self-hosted como motor de fase futura
`estado: amadurecendo · nasceu: 2026-08-18 · olhar de novo em: F6`
Open WebUI, LibreChat, AnythingLLM, Dify, LobeHub — avaliar se alguma serve de motor em vez de
construir agente do zero.
**Por quê ainda não:** discutido em 2026-08-18, com decisão de continuar em outro chat; nenhuma ação
tomada neste projeto. A F6 acontece de qualquer forma (`D-12`), então esta avaliação tem destino
certo.

## Adiadas com gatilho

### ~~B-08 — Fechar o CORS do backend~~
`estado: resolvido em 2026-09-30, no plano Núcleo centralizado (D-36) · nasceu: 2026-08-18`
`allow_origins=["*"]` hoje. Confirmado por medição em 2026-08-23 (lacuna L7 do contrato).
**Resolvido:** o núcleo que saiu da máquina — as Edge Functions `transcrever` e `consumo` — **não tem
CORS nenhum** (nenhum `Access-Control-Allow-Origin`; o cliente é o app de desktop). O núcleo local
continua com `*`, porque não saiu da máquina, e a lacuna L7 passou a valer só para ele. Ver
`spec/contrato/NUCLEO.md`, "Autenticação → Sem CORS" e L7.
**Por quê ainda não:** aceitável enquanto tudo roda local. Vira restrição declarada no dia em que
sair da máquina — o mesmo gatilho da `D-05` (servidor próprio).

### ~~B-09 — Trocar os `.jsonl` por banco de dados~~
`estado: resolvido em 2026-09-30, no plano Núcleo centralizado (D-36) · nasceu: 2026-08-18`
`consumo.jsonl` e `transcricoes.jsonl` viram banco de verdade.
**Resolvido:** o histórico mora em `assistente.consumo` e `assistente.transcricoes` no Supabase (RLS por
usuário, só `select`/`insert`), com o histórico dos `.jsonl` importado e o campo `origem` dizendo quem
gravou cada linha. Os `.jsonl` seguem como registro do núcleo local sem token. Ver
`spec/contrato/NUCLEO.md`, "Registro de consumo". As consequências abertas da `D-22` (retenção,
mistura de uso real com testes) continuam lá.
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
`estado: amadurecendo · nasceu: 2026-08-16 · olhar de novo em: depois da F2 (ver D-22)`
Organizar transcrições por projeto ou entrevista, exportar, guardar metadados.
**Por quê ainda não:** olhado na especificação da F2, em 2026-09-06, e **adiado pelo usuário** — não
entra no MVP da fase (`D-34`). Continua requisito (`D-22`): quando voltar à mesa, dado de histórico
errado é defeito, não ruído.

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

### B-21 — Timeout no streaming cai em `SEM_CONEXAO`, não em `TEMPO_ESGOTADO`
`estado: amadurecendo · nasceu: 2026-08-24, medição da Etapa 3 · olhar de novo em: quando houver um segundo cliente consumindo o núcleo`
Sob a mesma falha de rede (servidor que aceita a conexão e nunca responde), o modo sem streaming
devolve `TEMPO_ESGOTADO`/`504` em **6min01,99s**; o modo streaming devolve `SEM_CONEXAO` dentro de um
`200` em **8min28,92s**. O SDK da OpenAI levanta `APIConnectionError` em vez de `APITimeoutError`
para chamadas `stream=True` nessa condição — o backend usa o mesmo helper de mapeamento nos dois
modos, então não é bug do código do projeto.
**Por quê ainda não:** com um cliente só, e esse cliente sendo o app web que o usuário opera olhando
a tela, um erro de rede genérico resolve. O código errado passa a doer quando um cliente automático
precisar distinguir "a rede caiu" de "demorou demais" para decidir se tenta de novo.
**O que faria virar etapa:** um segundo cliente consumindo o núcleo — que é também o gatilho de
revisão da `M-01` (verificação manual). Aí vale investigar a causa raiz no SDK ou normalizar o
mapeamento no backend.
**Junto com ele**: o `max_retries=2` do SDK não foi alterado, então o tempo real até a falha é
múltiplo dos 120s declarados. Registrado no `NUCLEO.md` para quem for revisar esse número.

### B-22 — Inserção automática no campo em foco (a POC-1 original)
`estado: morta · nasceu: 2026-08-24, escopo da Fase 2 · morta: 2026-09-05 (D-33)`
Investigar por qual mecanismo inserir texto no campo em foco no Windows, e onde ele falha: quatro
alvos (terminal do VS Code, editor do VS Code, WhatsApp no Opera, Bloco de Notas como controle
nativo) × três mecanismos (teclado sintético, API de acessibilidade, área de transferência com
restauração), com escalada para o Text Services Framework se os três falharem.
**Por quê morta:** estava `adiada` desde 2026-08-25 (`D-25`) esperando o copiar-colar manual
incomodar no uso. O usuário confirmou em 2026-09-05 (`D-33`) que isto está descartado de vez, não é
mais "esperando o gatilho" — **não confundir com** a segunda ação "colocar a última transcrição" com
atalho próprio (`COMPORTAMENTOS_PARQUEADOS.md`), que é outra coisa e continua viva.

**Evidência parcial levantada (2026-08-25), preservada como registro técnico** — em
`spec/pocs/POC-1/`:

- **`D-26`, o achado que muda tudo**: a injeção tem de disparar de dentro do handler do atalho
  global. Quatro tentativas falharam **em silêncio** por serem disparadas de um processo desacoplado.
  Quando esta investigação voltar, é **daí** que ela parte — a matriz 4×3 em branco não significa
  "não testamos", significa "testamos do jeito errado e sabemos por quê".
- **UI Automation no WhatsApp Web (Opera)**: enxerga só um contêiner genérico como elemento focado,
  sem `ValuePattern` nem `TextPattern` — característica conhecida de Chromium. No Bloco de Notas, o
  controle certo **tem** `ValuePattern`, mas o `SetValue` não chegou a ser confirmado.
- **Clipboard, medido**: texto exposto por **~1,05s**; Histórico de Área de Transferência do Windows
  (Win+V) **desligado** nesta máquina; nenhum gerenciador de terceiros rodando. A restauração
  executou sem erro, mas não foi confirmada visualmente ponta a ponta.

### B-23 — Escolher se a transcrição vai para o clipboard automaticamente
`estado: amadurecendo · nasceu: 2026-08-25, durante a POC-1 · olhar de novo em: depois de alguns dias de uso do app`
Uma opção configurável para o app copiar a transcrição para a área de transferência automaticamente
ou não. Pedido do usuário durante a sessão.
**Por quê ainda não:** o app acabou de nascer copiando sempre, e é justamente o uso que vai dizer se
copiar sempre atrapalha — se você perde o que tinha copiado, com que frequência, e em que situação.
Decidir agora seria decidir sem o dado que chega de graça na primeira semana.
**O que faria virar etapa:** você reclamar de ter perdido algo do clipboard. Aí a opção entra, e já
com a resposta de qual deve ser o padrão.

### B-24 — Duas transcrições idênticas seguidas confundem o detector de "resultado pendente"
`estado: amadurecendo · nasceu: 2026-09-05, correção do bug do encolhimento (D-32) · olhar de novo em: se incomodar no uso`
O detector de pendência da janela compacta (`D-32`, segunda rodada) compara o texto da caixa com o
último texto colocado; se as duas transcrições seguidas saírem **idênticas**, a segunda é lida como
"já colocada" mesmo sem ter sido, e a janela pode encolher antes da hora.
**Por quê ainda não:** achado ao corrigir o bug principal, não reportado pelo usuário. Caso raro
(precisa ditar a mesma frase duas vezes seguidas) e o pior efeito é a janela encolher cedo demais —
incômodo pequeno, não perda de dado.
**O que faria virar etapa:** você notar isso acontecendo de verdade.

### B-25 — Janela compacta deriva de tamanho depois de dias de uso, e o botão some
`estado: amadurecendo · nasceu: 2026-09-21, suporte ao vivo no Windows real (achado do Executor no PROGRESSO) · olhar de novo em: retorno ao planejamento da Etapa 4, a partir de 2026-09-25`
Com o app aberto há dias, a janela nativa sai do tamanho-alvo da `D-32`: medida de fora do processo
(`GetWindowRect`), ficou em **358×293** em vez de **448×366** — exatamente `× 0,8 = 1/1,25`, o `dpr`
que o próprio log registra. O `app.log` capturou o evento (`tamanho_fora_do_modo expandido=True
alvo=448x366 real=358x293`). A máscara continua calculada para 448×366, então o recorte não coincide
mais com onde o botão está desenhado: você vê uma área vazia ("cadê o botão"). Reiniciar o app resolve
na hora (testado duas vezes). Suspeita, não confirmada: troca entre monitores com DPI diferente.
**Por quê ainda não:** achado registrado, não corrigido. A rede de segurança
`_corrigir_tamanho_do_modo` loga o desvio, mas não se sabe se converge sozinha nem em quanto tempo.
**O que faria virar etapa:** já aconteceu uma vez no uso real, e atrapalha o uso em regime, que é o
critério da Fase 2 (`D-24`, `D-34`). Decisão de subir ou não fica para o retorno ao planejamento.
Ponto de partida sugerido pelo Executor: cronometrar se a rede converge; se não, recalcular a
máscara a partir do tamanho **real** em vez de reafirmar o alvo lógico.

### B-26 — Geração de imagem pelo app falha com `API_RECUSOU` antes de funcionar
`estado: amadurecendo · nasceu: 2026-09-30, Parte B da Etapa 5 do plano Núcleo centralizado · olhar de novo em: quando o usuário pedir ("corrigir depois", 2026-09-30)`
No teste real da Etapa 5, a primeira geração de imagem pelo app deu `API_RECUSOU` (HTTP 400 da
OpenAI; `app.log` 2026-09-30 14:32) e a seguinte entrou no banco (`nucleo-local-imagem`, 14:33). O
mesmo código aparece sete vezes em 2026-09-23, antes de qualquer mudança deste plano — não é
regressão do núcleo remoto. Suspeita do usuário: "tem a ver com as chamadas dos modelos". Pista já
registrada na Etapa 4: a OpenAI recusou `gpt-image-1-mini` nesta rota (provavelmente pelo
`input_fidelity="high"`), e o `config.json` do desktop usa `gpt-image-2`.
**Por quê ainda não:** o usuário mandou deixar para depois.
**O que faria virar etapa:** pedido do usuário. Ponto de partida: logar o `message` da recusa da
OpenAI (hoje só o código chega ao `app.log`) e conferir quais parâmetros cada modelo aceita.

### B-27 — Transcrição como serviço para a Mari (recurso de acessibilidade)
`estado: promovida em 2026-09-30 — plano "Transcrição como serviço para a Mari" (`D-37`) · nasceu: 2026-09-30, ideia do usuário`
O RAG-COMPARTILHADO vira um projeto de **serviços** (RAG + transcrição). A Mari grava o áudio no
navegador de quem usa o site, manda para a transcrição e devolve o texto para a pessoa enviar —
recurso de acessibilidade. Diferença para o desktop: quem usa a Mari é público, sem login no Auth.
Caminho avaliado pelo PM: a chamada sai do **servidor** da Mari com uma chave de serviço (mesmo
padrão do cabeçalho `x-rag-chave` das funções `buscar`/`ingerir`), nunca do navegador; consumo
registrado por projeto (`mari`), não por usuário; limites de tamanho, frequência e gasto; e decidir
se o texto de terceiros é guardado (pesquisa com pessoas, comitê de ética).
**Por quê ainda não:** o plano corrente não fechou; a Etapa 6 (contrato novo) é o documento que essa
integração vai ler.

### B-28 — Observabilidade centralizada dos gastos da Mari e dos serviços
`estado: amadurecendo · nasceu: 2026-09-30, pedido do usuário no planejamento do B-27 · olhar de novo em: ao fechar o plano "Transcrição como serviço para a Mari"`
Uma vista única do gasto da Mari (conversa, RAG, transcrição) e dos outros serviços do
RAG-COMPARTILHADO, mais robusta que olhar tabela por tabela. Hoje o gasto está espalhado: consumo
pessoal em `assistente.consumo`, buscas em `rag.buscas` (sem custo), e a transcrição da Mari vai
para a tabela de uso do schema `servicos`.
**Por quê ainda não:** o usuário disse "depois"; o serviço de transcrição precisa existir antes.
**O que faria virar etapa:** pedido do usuário, com o serviço em uso.

### B-29 — Proteção contra senha vazada desligada no Auth do RAG-COMPARTILHADO
`estado: amadurecendo · nasceu: 2026-09-30, advisor de segurança lido na Etapa 1 do plano da Mari (anterior a ela) · olhar de novo em: quando o usuário pedir`
O advisor do Supabase avisa (WARN `auth_leaked_password_protection`) que o Auth não confere senhas
contra a base de senhas vazadas. Hoje o Auth tem um usuário só, o do ditado pessoal, com cadastro
público fechado. Não se conferiu se a opção está disponível no plano gratuito.
**Por quê ainda não:** fora do plano corrente, e o risco é baixo com cadastro fechado.
**O que faria virar etapa:** pedido do usuário, ou o Auth ganhar mais usuários.
