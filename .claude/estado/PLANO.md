# PLANO — Fase 1: Núcleo de transcrição

> Plano da **fase corrente** do método Spec-Driven Development. A visão e o mapa das 9 fases estão
> em `spec/VISAO.md`; a especificação desta fase, em `spec/specs/SPEC-001_contrato-do-nucleo.md`;
> a rastreabilidade, em `spec/MAPA.md`. Virada de plano em 2026-08-21 (plano de faxina encerrado e
> arquivado em `historico/PLANO_2026-08-21c_faxina-encerrado.md`). Etapas 1 e 2 concluídas em
> 2026-08-23; versão anterior deste arquivo em `historico/PLANO_2026-08-23_pre-etapa2.md`.

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

## Exceção registrada (2026-08-23)

Por decisão explícita e datada do usuário nesta data, o PM ficou autorizado, **uma vez**, a editar
`.claude/PM.md` e `.claude/skills/diagnostico-geral/SKILL.md` para aplicar as correções de método da
`D-21`. Fora dessa aplicação, a regra de sempre vale: o PM não edita arquivo de método por conta
própria. Registrado também na `coleta/2026-08-23_metodo-consistencia.md`.

## Etapas

1. **[Levantamento e documento do contrato]** — medir contra o backend rodando o comportamento de
   cada operação e de cada erro previsto na SPEC-001, e escrever `spec/contrato/NUCLEO.md` com o
   que foi **observado**, não com o que foi suposto.
   — Status: **concluída (2026-08-23)**. Conferida pelo PM no artefato real. O caminho feliz e as
   seis situações de erro foram provocados de verdade, cada uma nos dois modos; `spec/contrato/
   NUCLEO.md` escrito com exemplos capturados; L1 a L8 fechadas com evidência; nenhum arquivo de
   produto tocado. Três achados que a SPEC-001 não previa: alucinação em silêncio (virou `D-16`),
   custo zerado do modelo de diarização (`D-17`) e ausência de eventos `delta` no streaming desse
   mesmo modelo (`D-17`).

2. **[Fechar a SPEC-001]** — trabalho de PM, não de Executor.
   — Status: **concluída (2026-08-23)**, em chat de PM. A SPEC-001 passou a `status: fechada`, com
   o medido incorporado e as lacunas convertidas em requisito ou em comportamento declarado. As
   questões Q1 e Q7 já estavam respondidas desde 21/08 — a Etapa 2 só precisou reconciliá-las. O
   escopo da Etapa 3 foi definido com o usuário (quatro lacunas, abaixo). Fora do previsto: a
   revisão encontrou **seis inconsistências entre documentos**, todas mapeadas, corrigidas e com a
   causa raiz atacada em `D-19` e `D-21`.

3. **[Corrigir as quatro lacunas aprovadas]** — escopo aprovado pelo usuário em 2026-08-23.
   Mudanças **aditivas** em `transcritor/backend/main.py`; `transcritor/frontend/index.html` não é
   tocado e precisa continuar funcionando igual.

   - **L1 — código de erro legível por máquina.** Toda resposta de erro ganha `codigo` estável, com
     `detail` em português seguindo como texto humano. Oito códigos: `MODELO_INVALIDO`, `SEM_CHAVE`,
     `AUDIO_VAZIO`, `FALHA_AUTENTICACAO`, `SEM_CONEXAO`, `API_RECUSOU`, `TEMPO_ESGOTADO`,
     `ARQUIVO_MUITO_GRANDE`. Vale nos dois modos — no streaming, dentro do evento `{"tipo":"erro"}`.
   - **L3 — prazo de espera declarado.** Hoje o backend herda o default do SDK (5s de conexão,
     600s de leitura). Passa a declarar **120s de leitura**, mantendo os 5s de conexão, e devolve
     `TEMPO_ESGOTADO` ao estourar. Número decidido pelo usuário em 2026-08-23 — ver `D-20`.
   - **L2 — recusa de arquivo grande antes do upload.** O backend passa a recusar acima do limite
     da API da OpenAI, **antes** de subir o arquivo, com `ARQUIVO_MUITO_GRANDE` e mensagem que diz
     o tamanho enviado e o teto. O limite exato é **a medir pelo Executor**, não a supor — ver
     "Nota de processo" sobre critério numérico derivado de inferência.
   - **L5 — versão do contrato.** Cabeçalho `X-Nucleo-Contrato: 1` em toda resposta do núcleo, e a
     versão declarada no `spec/contrato/NUCLEO.md`. Cabeçalho e não campo no corpo, porque serve
     igual para o JSON e para o NDJSON do streaming.

   — Critério de pronto: os oito códigos provocados de verdade contra o backend rodando, com a
   resposta colada no `PROGRESSO.md`; o limite de tamanho **medido** (um arquivo abaixo e um acima
   do teto), não estimado; `X-Nucleo-Contrato` presente nas respostas de sucesso e de erro, nos
   dois modos; `spec/contrato/NUCLEO.md` atualizado com códigos, teto, prazo e versão; o app web
   conferido funcionando depois da mudança.
   — Fora desta etapa (`D-17`): tudo que depende de `gpt-4o-transcribe-diarize` — o custo zerado e
   a ausência de `delta` em streaming.
   — Fora desta etapa (`D-16`): o gate de silêncio, que é obrigação declarada do cliente, não do
   núcleo.

4. **[Arrumação: harness, rascunho e entulho]** — **concluída (2026-08-23)**. Conferida pelo PM no
   artefato real: harness em `transcritor/teste_tempo_real.py` com o cabeçalho reescrito (não se
   declara mais descartável) e citado no `README.md` com o que prova e o que não prova; `.claude/tmp/`
   vazio; `_to_delete/` e `historico/snapshots/` apagados, com a raiz do `historico/` intacta em 20
   arquivos; sem `index.lock`, sem `.fuse_hidden`, nada de `backend/` ou `frontend/` tocado. Ordem
   respeitada: promoção antes de qualquer remoção.
   — Nota: o registro diz 49 snapshots apagados; o git conta 48. Divergência de uma unidade, sem
   efeito no resultado — a pasta não existe mais. Fica anotada porque número em registro é evidência.
   — *(Escopo original abaixo, ampliado pelo usuário em 2026-08-23 na revisão estrutural.)*
   - **Promover o harness**: `.claude/tmp/teste_tempo_real.py` vira arquivo versionado em
     `transcritor/`, com um parágrafo dizendo o que ele prova. **Isto vem primeiro** — é o único
     arquivo com valor dentro de uma pasta que existe para ser apagada.
   - **Limpar o `.claude/tmp/`** depois da promoção: o WAV de teste, o `uvicorn.log`, o
     `_teste_escrita.tmp` e as cópias de tarefas já executadas.
   - **Apagar o `_to_delete/`** inteiro. Ele guarda o lixo do bridge (`.fuse_hidden*`) e um fóssil de
     0 byte. A sessão remota não consegue apagar pela pasta montada — recusa com "Operation not
     permitted"; o Executor roda local e consegue.
   - **Aplicar o limiar de snapshot** (`B-19`): hoje são 48 snapshots automáticos em
     `historico/snapshots/`, com mediana de 18 linhas de diferença entre consecutivos. Manter os que
     são virada de plano, descartar os demais — a regra está em `.claude/metodo/HIGIENE.md`.
   — Critério de pronto: `.claude/tmp/` e `_to_delete/` vazios ou inexistentes; o harness versionado
   e citado no `transcritor/README.md`; `historico/snapshots/` só com viradas de plano; e o
   repositório **pronto para commit** conforme `.claude/metodo/COMMIT.md` — que é o primeiro teste
   real dessa regra.

5. **[~~Idioma: parâmetro no contrato~~]** — **CANCELADA em 2026-08-23**, pela condição que a
   própria etapa trazia. A medição da Etapa 1 comparou o mesmo áudio com e sem `language="pt"`:
   texto idêntico caractere por caractere e tokens idênticos, logo custo idêntico. O contrato
   registra que o núcleo não assume idioma e não ganha parâmetro novo. Ver `D-08` (revisada).

6. **[Atualizar o `CLAUDE.md`]** — **concluída (2026-08-23)**, dentro da revisão estrutural, não
   como tarefa de Executor. A revisão mostrou que o problema era maior do que a etapa previa: cinco
   documentos de orientação não conheciam o método, não um. Todos reconciliados na mesma sessão, e o
   `CLAUDE.md` encolheu de 3,2 KB para 2,2 KB — ele voltou a ser porta de entrada e deixou de
   disputar o papel de mapa, que agora é do `.claude/CEREBRO.md`.

## Backlog

**Mudou de casa em 2026-08-23**: o acervo de ideias mora agora em
[`spec/BACKLOG.md`](../../spec/BACKLOG.md), com ID `B-nn`, estado, origem e a fase em que cada uma
volta à mesa.

**Por quê**: o backlog **atravessa fases** e este arquivo morre a cada fase — há item nascido em 16 e
18/08 ainda vivo num plano de uma fase aberta em 21/08. E os 60 planos arquivados em `historico/`
congelaram cada um a sua cópia do acervo, então procurar a razão de uma recusa devolve dezenas de
respostas de datas diferentes, e a mais recente não é a que aparece primeiro. Conteúdo que atravessa
fases não mora em arquivo que morre com a fase (`D-21`).

**Ao fechar uma etapa ou uma fase**: ler os itens do `BACKLOG.md` marcados com
`olhar de novo em:` para a fase seguinte e perguntar ao usuário quais sobem para Etapas. Item de
backlog nunca vira etapa por iniciativa do PM.

## Nota de processo (lembrete para o PM)
- **As regras de método não são repetidas aqui.** Passe de fechamento, número derivado à mão, o
  mais recente vence, higiene e commit moram em `.claude/metodo/` — leia de lá. Esta nota guarda só
  o que é **deste projeto**.
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
