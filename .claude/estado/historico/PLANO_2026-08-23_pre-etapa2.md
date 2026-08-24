# PLANO — Fase 1: Núcleo de transcrição

> Plano da **fase corrente** do método Spec-Driven Development. A visão e o mapa das 9 fases estão
> em `spec/VISAO.md`; a especificação desta fase, em `spec/specs/SPEC-001_contrato-do-nucleo.md`;
> a rastreabilidade, em `spec/MAPA.md`. Virada de plano em 2026-08-21 (plano de faxina encerrado e
> arquivado em `historico/PLANO_2026-08-21c_faxina-encerrado.md`).

## Objetivo

Fechar o **contrato do núcleo de transcrição**, para que desktop, Android e Wear consumam a mesma
capacidade sem reimplementá-la, cada um na sua linguagem.

## Critério de conclusão da fase

Alguém consegue escrever um cliente novo lendo só o contrato, **sem abrir o `index.html` nem o
`main.py`**.

## Escopo

- **Dentro**: levantar por medição o comportamento real das rotas do núcleo; escrever o documento
  do contrato em `spec/contrato/NUCLEO.md`; fechar a SPEC-001; corrigir as lacunas que forem
  confirmadas e aprovadas; preservar o harness do modo ao vivo.
- **Fora (explícito)**: qualquer mudança em `transcritor/frontend/index.html`; escolha da linguagem
  do app desktop (depende da POC-1, que é da Fase 2); servidor hospedado (adiado com gatilho
  declarado — ver `spec/VISAO.md`); qualquer trabalho no modo ao vivo além de preservar o harness;
  as PoCs 1 a 5, todas de fases posteriores.

## Etapas

1. **[Levantamento e documento do contrato]** — medir contra o backend rodando o comportamento de
   cada operação e de cada erro previsto na SPEC-001, e escrever `spec/contrato/NUCLEO.md` com o
   que foi **observado**, não com o que foi suposto. Confirmar, refutar ou reclassificar as lacunas
   L1 a L7. Sem mudar código de produto.
   — Critério de pronto: os CA1, CA2 e CA4 da SPEC-001 atendidos; cada linha da tabela de erros com
   evidência de execução real; divergências entre a spec e a máquina listadas e devolvidas ao PM.
   — Status: **concluída (2026-08-23)**. Conferida pelo PM no artefato real. O caminho feliz e as
   seis situações de erro foram provocados de verdade, cada uma nos dois modos; `spec/contrato/
   NUCLEO.md` escrito com exemplos capturados; L1 a L8 fechadas com evidência; nenhum arquivo de
   produto tocado. Três achados que a SPEC-001 não previa: alucinação em silêncio (virou `D-16`),
   custo zerado do modelo de diarização (bug, ver Etapa 3) e ausência de eventos `delta` no
   streaming desse mesmo modelo.

2. **[Fechar a SPEC-001]** — tarefa do PM, não do Executor. Incorporar o levantamento, decidir quais
   lacunas viram requisito, e responder as questões Q1 (idiomas) e Q7 (histórico é requisito?) com
   o usuário. Depende da Etapa 1.

3. **[Corrigir as lacunas aprovadas]** — escopo definido só depois da Etapa 2. Candidatas, agora
   com evidência:
   - **L1 — códigos de erro legíveis por máquina.** É o que permite três clientes reagirem
     diferente a "sem chave" e a "sem rede" sem comparar strings em português.
   - **L2 — erro enganoso em arquivo grande.** Um WAV de 64MB devolve "verifique o formato do
     arquivo de áudio", que aponta para a causa errada.
   - **L5 — versionamento do contrato.** Sem versão, um cliente antigo quebra em silêncio.

   Fora desta etapa por decisão de 2026-08-23 (`D-17`): tudo que depende de
   `gpt-4o-transcribe-diarize` — o custo zerado e a ausência de `delta` em streaming. O modelo está
   desativado da interface desde 2026-08-18; o bug é inalcançável no uso normal.

4. **[Preservar o harness do modo ao vivo]** — promover `.claude/tmp/teste_tempo_real.py` a arquivo
   versionado em `transcritor/`, com um parágrafo dizendo o que ele prova. Decidida pelo PM sem
   consulta ao usuário: é arrumação, e a pasta de origem existe para ser apagada. Pode rodar em
   qualquer ponto da fase.

5. **[Idioma: parâmetro no contrato, não constante no código]** — decisão do usuário em
   2026-08-21, corrigindo o encaminhamento anterior: **não fixar português no código**. O contrato
   ganha um parâmetro `idioma` **opcional**; ausente significa detecção automática pela API. O
   controle de interface (interruptor "fixar idioma" + lista com português, inglês, espanhol,
   italiano e chinês, começando ligado em português) é **Fase 2**, e está parqueado em
   `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`.
   — **Condicionada**: só executa se a medição da Etapa 1 mostrar que fixar o idioma é melhor do
   que deixar a API detectar. Se a medição não mostrar diferença, esta etapa cai e o contrato
   apenas registra que o núcleo não assume idioma.
   — Critério de pronto: o contrato descreve o parâmetro `idioma` com seu comportamento quando
   ausente, e a medição do antes e depois está no `PROGRESSO.md`.

   </details>

6. **[Atualizar o `CLAUDE.md`]** — hoje ele descreve o repositório como "MVP de um motor mínimo de
   transcrição" e não menciona `spec/`, o método Spec-Driven Development nem a Fase 1. É o primeiro
   arquivo que todo chat novo lê: desatualizado, desalinha o Executor antes de qualquer tarefa.
   — Critério de pronto: quem abre um chat novo entende, só pelo `CLAUDE.md`, que o transcritor é a
   Fase 1 de um produto maior, onde mora a especificação e qual é a fase corrente.

## Backlog (não aprovado)
- **Arrastar e soltar áudio na área central** para enviar sem passar pelo menu — pedido do
  usuário em 2026-08-21, adiado por ele mesmo para depois da frente de interface enxuta
  ("posteriormente vamos voltar com o drag de áudio");
- **Baratear o modo ao vivo trocando o modelo** (`gpt-live-transcribe` US$ 0,017/min →
  `gpt-4o-transcribe` US$ 0,006/min) — **avaliado e recusado pelo usuário em 2026-08-20**, não será
  executado. Fica registrado com a estimativa para o dia em que custo virar prioridade.
  **Quanto economizaria**: o preço do modelo cai 65%, mas usar a detecção de turno da API (única
  forma de o modelo mais barato fechar turnos sozinho) obriga a desligar o gate de silêncio da
  Etapa 1 — passa-se a pagar o tempo todo, não só a fala. Economia real conforme a proporção de
  silêncio da sessão: ~65% se você fala sem parar, **~50% numa sessão típica com ~30% de silêncio**,
  ~29% se metade da sessão é silêncio. Numa sessão de 10 minutos com 30% de silêncio: US$ 0,119 →
  US$ 0,060. **Motivo da recusa**: o usuário prefere preservar nuance de fala (pontuação, ênfase) a
  economizar, tendo recurso disponível. **Contraponto medido, registrado para revisão futura**: o
  `BENCHMARK.md` mostra `gpt-4o-transcribe` em lote produzindo pontuação e acentuação impecáveis no
  áudio de 72s, enquanto o modo ao vivo atual (com `gpt-live-transcribe`) produz "Isso e um teste da
  transcricao" sem acentos e parte palavras nas emendas — indício de que a perda de nuance vem do
  **tamanho do pedaço enviado** (fatias de 6s), não do modelo. Quem quiser retomar isto deve testar
  a hipótese antes de decidir;
- **Alternador de controle de turno e detecção pela API** — construído e depois **encerrado sem
  uso** em 2026-08-20, porque `gpt-live-transcribe` recusa `turn_detection` diferente de `null` e a
  alternativa exigia trocar de modelo (item acima, recusado). O código sai da interface na Etapa 3;
  o registro do que foi aprendido fica no `PROGRESSO.md` e na `coleta/`;
- **Commit guiado por silêncio (plano B das emendas)** — 6s viram piso em vez de corte; o turno
  fecha na primeira pausa depois disso, com um teto para não segurar o texto indefinidamente. Ideia
  do usuário em 2026-08-20. Não muda custo (quem define o custo é o gate de envio da Etapa 1, não o
  commit), mantém `gpt-live-transcribe` e resolve o corte de palavra na emenda sem depender da API;
- CORS do backend está aberto (`allow_origins=["*"]`), aceitável para uso 100% local — revisar
  se um dia o projeto for servido fora da máquina do usuário;
- trocar os arquivos locais de consumo e transcrição (`consumo.jsonl`, `transcricoes.jsonl`) por
  um banco de dados de verdade — decisão explícita do usuário em 2026-08-18 de adiar essa troca;
- rotação/limpeza automática de transcrições antigas em `transcricoes.jsonl` — sem política de
  retenção definida ainda;
- `consumo.jsonl` mistura consumo de uso real com o de sessões de teste do Executor — sem separação
  prevista; os números de `gpt-live-transcribe` anteriores a 2026-08-19 estão subestimados, porque
  o último turno de cada gravação era perdido antes da correção;
- histórico, armazenamento por projeto/entrevista, exportação, metadados;
- pipeline de limpeza → segmentação → classificação → resumo com modelos especializados;
- banco de dados, busca semântica, embeddings, RAG, corpus de entrevistas;
- camada de agente que decide qual modelo/informação usar;
- suporte a celular e smartwatch;
- transcrição em blocos com sobreposição (redundância) para precisão nas bordas — mais barata
  por minuto que a API ao vivo (mesmo com sobreposição generosa, nas contas feitas em 2026-08-19),
  mas exige lógica própria de continuidade nas bordas; decisão do usuário em 2026-08-19 de testar
  a API ao vivo primeiro, por ser mais simples de integrar;
- efeito de streaming imperceptível em áudios curtos — decisão pendente do usuário sobre se vale a
  pena um adiantamento artificial de exibição;
- explorar plataforma de chat self-hosted tipo Claude com agentes/skills (Open WebUI, LibreChat,
  AnythingLLM, Dify, LobeHub) como possível motor para uma fase futura — discutido em 2026-08-18,
  decisão de continuar em outro chat, nenhuma ação tomada neste projeto ainda.

- **Limpeza de `.claude/tmp/` e de `_to_delete/`** — levantado na faxina de 2026-08-21 e deixado
  fora do plano por decisão do usuário. `.claude/tmp/` guarda 584 KB de rascunho
  (`teste_linha_tempo.wav` com 562 KB, `uvicorn.log`, `ROTEIRO_TESTE_ETAPA1.md`,
  `_teste_escrita.tmp`); `_to_delete/` guarda só o fóssil `index.lock.2026-08-16`, de 0 byte. Nada
  disso é versionado — é ruído visual, não risco. Desde 2026-08-21 a pasta guarda também cópias das
  tarefas `TAREFA_etapa2_faxina.md` e `TAREFA_interface-enxuta.md`, ambas já executadas ou
  promovidas — podem ir junto na limpeza;
- **Promover `.claude/tmp/teste_tempo_real.py` a ferramenta versionada em `transcritor/`** — é o
  harness em Python que validou o protocolo da API ao vivo sem navegador (2026-08-20), o único
  arquivo com valor dentro de uma pasta descartável: some junto com o resto na primeira limpeza;

## Nota de processo (lembrete para o PM)
- **Tarefa que quebra o backend ou o `.env` precisa avisar o usuário ANTES de começar**, não só
  antes da parte destrutiva — em 2026-08-23 o Executor descobriu, por log, que o usuário estava
  usando o app ao vivo no meio da medição. Não deu problema (ele autorizou), mas o aviso chegou
  tarde. Recomendação do próprio Executor, acatada.
- **Armadilha da porta 8000: 5ª ocorrência** (backend antigo servindo código obsoleto, PID 34028 de
  22/08). Continua valendo o lembrete em toda tarefa que meça o backend.
- Ao gerar `PROXIMA_TAREFA.md` com passo de documentação, incluir `transcritor/README.md`
  explicitamente em "Arquivos envolvidos".
- Ao gerar tarefa que mexa em visualização/gráfico (Etapa 3), lembrar o Executor de consultar a
  skill `dataviz` antes de escrever o código.
- Declarar sempre o campo `## Registro no PROGRESSO`. Critério de pronto que pede evidência colada
  (transcript, resposta de rota) é incompatível com o nível `curto` — nesses casos, `completo`.
- Critério numérico derivado de inferência precisa ser conferido antes de virar critério de pronto
  (lição de 2026-08-20: pedi queda na contagem de marcas presumindo densidade, e a densidade já
  estava correta). **2ª ocorrência em 2026-08-21**: estimei "cerca de 7 arquivos" na raiz do
  `historico/` e o grep achou 8 citações reais que eu não tinha previsto — o resultado foi 17.
  Estimativa vai como estimativa declarada, nunca como critério de pronto.
- Preços de referência consultados em 2026-08-19 (podem mudar — conferir
  https://developers.openai.com/api/docs/pricing antes de decisões de custo): `gpt-transcribe`
  (lote) US$ 0,0045/min; `gpt-live-transcribe` (tempo real) US$ 0,017/min — cerca de 3,8x mais caro.
- Armadilha recorrente (4 ocorrências): backend antigo esquecido na porta 8000 servindo código
  obsoleto. Lembrar o Executor de conferir e derrubar antes de testar.
- Armadilha do `.git/index.lock` (2 ocorrências: 2026-08-16 e 2026-08-21): qualquer `git status`
  rodado pelo bridge remoto deixa o lock para trás, porque a pasta montada não permite apagar
  arquivo ("Operation not permitted"), e o commit seguinte falha. Antes de qualquer etapa que
  commite, avise o Executor de que ele mesmo deve apagar o lock (ele roda local e consegue —
  confirmado em 2026-08-21); só peça ao usuário se o Executor não conseguir.
- Arquivar o `PROGRESSO.md` **na hora** em que o plano fecha, não no chat seguinte: na virada de
  2026-08-21 o arquivo já estava em 101 KB e 1.404 linhas, acima do alarme de 60 KB.

- **Consolidar as histórias US-D02 + US-A02 + US-D03** numa capacidade só (*entrega do texto no
  destino*, com escada campo em foco → clipboard → popup) — proposta da revisão do pré-projeto,
  entra quando a Fase 2 for especificada, não agora.
- **Régua do Win+H** — a proposta do PM de que o ditado precisa ser pelo menos tão rápido e preciso
  quanto a digitação por voz nativa do Windows está aceita tacitamente, **falta aceite explícito**
  do usuário para virar critério de aceitação (Q2).
