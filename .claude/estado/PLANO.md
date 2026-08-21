## Objetivo
Fechar a frente de usabilidade da interface de gravação e deixar o repositório arrumado e
versionado antes de abrir a próxima frente de produto. Nenhuma mudança de comportamento do app
neste plano.

## Escopo
- Dentro: arquivamento da virada (PLANO e PROGRESSO), enxugamento de
  `.claude/estado/historico/` e das retomadas de frentes encerradas, commit de todo o trabalho de
  2026-08-20 e 2026-08-21, atualização da retomada viva e abertura da coleta da frente nova.
- Fora (explícito): limpeza de `.claude/tmp/` e de `_to_delete/` (decisão do usuário em
  2026-08-21 de deixar fora deste plano — foi para o Backlog); separação de uso real e de teste no
  `consumo.jsonl` (Backlog); qualquer mudança em `transcritor/frontend/index.html` ou
  `transcritor/backend/main.py`; a escolha da próxima frente de produto.

## Etapas
1. [Arquivamento da virada] — critério de pronto: as 15 entradas do `PROGRESSO.md` movidas palavra
   por palavra para `historico/PROGRESSO_usabilidade-gravacao_2026-08-20_a_2026-08-21.md`, com
   cabeçalho dizendo de qual plano e de que período é; `PROGRESSO.md` vivo só com o cabeçalho,
   apontando para o arquivo; contagem de linhas fechando (1.398 movidas + 7 no vivo, contra as
   1.404 originais); plano encerrado salvo em
   `historico/PLANO_2026-08-21b_usabilidade-encerrado.md`.
   — Status: **concluída (2026-08-21)**, feita pelo PM neste chat, pela exceção datada de
   2026-08-19 (arquivamento do PROGRESSO na virada). Contagem conferida: arquivo arquivado com
   1.404 linhas (6 de cabeçalho novo + 1.398 movidas), vivo com 7, 15 entradas `## [` no arquivado.

2. [Enxugar o histórico do método] — critério de pronto: os snapshots de edição de plano movidos
   para `.claude/estado/historico/snapshots/`, deixando na raiz de `historico/` só os marcos
   citados por nome em outros arquivos (as viradas de plano e os arquivos `PROGRESSO_*.md`); os
   dois `_RETOMADA_*.md` de frentes encerradas (`_RETOMADA_robustez-consumo.md` e
   `_RETOMADA_transcricao-tempo-real.md`) movidos da raiz do repositório para
   `.claude/estado/historico/`; **nenhum arquivo apagado**, só movido; e um `grep` no repositório
   inteiro confirmando que nenhuma referência por caminho quebrou. Alvo: a raiz de `historico/`
   sai de 60 arquivos para cerca de 7.

3. [Commit do trabalho de 2026-08-20 e 2026-08-21] — critério de pronto: `git status --short`
   vazio fora do que o `.gitignore` cobre; o trabalho em commits separados por natureza (código do
   produto, documentação do produto, estado do método e histórico), com mensagens em português
   dizendo o que mudou e por quê; `git log --oneline` mostrando os novos commits; **sem push**.
   > **Depende do usuário**: `.git/index.lock` existe e o bridge remoto não consegue apagar. Tem
   > de ser apagado no Windows antes desta etapa, ou o commit falha.

4. [Retomada e coleta da frente nova] — critério de pronto: `_RETOMADA_usabilidade-gravacao.md`
   refletindo o estado real (frente encerrada, o que ficou em aberto, ponteiros certos) e
   `coleta/2026-08-21_fechamento-usabilidade.md` criado com as entregas de 2026-08-21, as decisões
   deste chat e o resumo consolidado nas quatro categorias.
   — Status: **parcial (2026-08-21)** — feita antecipadamente, a pedido do usuário, para o chat
   poder fechar antes das Etapas 2 e 3. A retomada e a coleta já refletem o estado real e o rumo
   (modo ao vivo fora de foco; frente nova de funcionalidade, a ser escolhida pelo usuário no
   próximo chat). **Falta o repasse final** depois que as Etapas 2 e 3 rodarem: confirmar na
   retomada que os snapshots e as retomadas encerradas mudaram de lugar e que o commit saiu.

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
  disso é versionado — é ruído visual, não risco. **Atenção**: desde 2026-08-21 a pasta guarda
  também `TAREFA_etapa2_faxina.md` e `TAREFA_interface-enxuta.md`, tarefas escritas esperando a
  vez — não limpar antes de promovê-las para `PROXIMA_TAREFA.md`;
- **Promover `.claude/tmp/teste_tempo_real.py` a ferramenta versionada em `transcritor/`** — é o
  harness em Python que validou o protocolo da API ao vivo sem navegador (2026-08-20), o único
  arquivo com valor dentro de uma pasta descartável: some junto com o resto na primeira limpeza;

## Nota de processo (lembrete para o PM)
- Ao gerar `PROXIMA_TAREFA.md` com passo de documentação, incluir `transcritor/README.md`
  explicitamente em "Arquivos envolvidos".
- Ao gerar tarefa que mexa em visualização/gráfico (Etapa 3), lembrar o Executor de consultar a
  skill `dataviz` antes de escrever o código.
- Declarar sempre o campo `## Registro no PROGRESSO`. Critério de pronto que pede evidência colada
  (transcript, resposta de rota) é incompatível com o nível `curto` — nesses casos, `completo`.
- Critério numérico derivado de inferência precisa ser conferido antes de virar critério de pronto
  (lição de 2026-08-20: pedi queda na contagem de marcas presumindo densidade, e a densidade já
  estava correta).
- Preços de referência consultados em 2026-08-19 (podem mudar — conferir
  https://developers.openai.com/api/docs/pricing antes de decisões de custo): `gpt-transcribe`
  (lote) US$ 0,0045/min; `gpt-live-transcribe` (tempo real) US$ 0,017/min — cerca de 3,8x mais caro.
- Armadilha recorrente (4 ocorrências): backend antigo esquecido na porta 8000 servindo código
  obsoleto. Lembrar o Executor de conferir e derrubar antes de testar.
- Armadilha do `.git/index.lock` (2 ocorrências: 2026-08-16 e 2026-08-21): qualquer `git status`
  rodado pelo bridge remoto deixa o lock para trás, porque a pasta montada não permite apagar
  arquivo ("Operation not permitted"), e o commit seguinte falha. Antes de qualquer etapa que
  commite, peça ao usuário para apagar `.git\index.lock` pelo Windows.
- Arquivar o `PROGRESSO.md` **na hora** em que o plano fecha, não no chat seguinte: na virada de
  2026-08-21 o arquivo já estava em 101 KB e 1.404 linhas, acima do alarme de 60 KB.
