# Coleta — fechamento da frente de usabilidade e faxina do repositório (2026-08-21)

> Arquivo novo porque `coleta/2026-08-16_mvp-transcricao.md` foi encerrado com o resumo
> consolidado no fim, na virada de 2026-08-20. Append-only.

## Coleta — validação das entregas de 2026-08-21 (PM)

- [ARTEFATO] Acabamento visual da faixa de áudio e proximidade dos controles entregue pelo
  Executor em 2026-08-21 e verificado no artefato real pelo PM em
  `transcritor/frontend/index.html`: faixa espelhada (`align-items: center`), barras finas
  (`max-width: 3px`) com pontas arredondadas (`border-radius: 999px`), curva de amplitude
  compressiva `PISO_BARRAS + sqrt(rms/RMS_TETO_BARRAS) * (1 - PISO_BARRAS)`
  (`RMS_TETO_BARRAS = 0.4`, `PISO_BARRAS = 0.06`), `placeholder` removido da `<textarea>` com o
  `aria-label` intacto, copiar e lixeira/desfazer fora da caixa em `.acoes-campo-transcript`, e
  grid `1fr 4.5rem 1fr` com `justify-self: end/start` aproximando os laterais do centro.
- [DECISÃO] Curva compressiva por raiz quadrada com teto de RMS em 0,4, escolhida pelo Executor
  na calibração — trade-off: 0,15 (primeira tentativa) fazia fala normal saturar igual a fala
  forte, sem diferenciar; 0,4 põe a fala de conversa na região média (p75 38,6%, p90 76,0%) e
  reserva o topo para ênfase, ao custo de fala fraca ficar mais baixa na faixa.
- [DECISÃO] O item opcional da tarefa (barras antigas levemente mais transparentes) foi pulado
  pelo Executor — trade-off: perde-se o reforço visual da direção do tempo, mas a tarefa dizia
  "só se ficar melhor de verdade" e a faixa já lê bem sem isso.
- [ARTEFATO] Correção pontual em 2026-08-21: o botão de copiar pulava para a esquerda quando a
  lixeira/desfazer estava escondida. `hidden` (`display: none`) trocado por `.invisivel`
  (`visibility: hidden`) só no botão de limpar, para ele continuar ocupando o lugar na linha
  `space-between`. Verificado pelo PM no CSS, no HTML inicial e nas três chamadas de
  `atualizarBotaoLimparTranscript`.
- [DIRECIONAMENTO] Usuário aprovou a interface de gravação em 2026-08-21 depois de usar
  ("sim, aprovo") — a frente de usabilidade da interface de gravação está encerrada, com 5
  etapas e 3 correções aprovadas.

## Coleta — decisões da faxina (2026-08-21)

- [DECISÃO] O próximo plano é **só de faxina e fechamento**, sem frente de produto junto —
  trade-off: adia o commit guiado por silêncio (que resolveria o corte de palavras nas emendas),
  mas entra na próxima frente com o repositório versionado e legível, em vez de somar arrumação
  a trabalho novo.
- [DECISÃO] Limpeza de `.claude/tmp/` e de `_to_delete/`, e separação de uso real e de teste no
  `consumo.jsonl`, ficam **fora** do plano de faxina, no Backlog — trade-off: o ruído visual
  permanece (584 KB de rascunho, um fóssil de `index.lock` de 0 byte) e os números de consumo
  seguem misturados, mas o plano fica curto e fecha rápido.
- [DECISÃO] Os snapshots de edição de plano vão para uma subpasta `historico/snapshots/` em vez
  de serem apagados — trade-off: o repositório continua carregando 1,1 MB de história que
  ninguém lê, mas nada se perde e a raiz de `historico/` volta de 60 arquivos para cerca de 7.
- [DIRECIONAMENTO] As retomadas de frentes já encerradas (`_RETOMADA_robustez-consumo.md` e
  `_RETOMADA_transcricao-tempo-real.md`) saem da raiz do repositório para
  `.claude/estado/historico/`; a retomada viva e o `_RETOMADA_TEMPLATE.md` ficam.
- [ARTEFATO] Virada de plano executada pelo PM em 2026-08-21: plano de usabilidade arquivado em
  `.claude/estado/historico/PLANO_2026-08-21b_usabilidade-encerrado.md`; as 15 entradas do
  `PROGRESSO.md` (1.398 linhas, 101 KB) movidas palavra por palavra para
  `.claude/estado/historico/PROGRESSO_usabilidade-gravacao_2026-08-20_a_2026-08-21.md`, com o
  vivo reduzido a 7 linhas de cabeçalho; `PLANO.md` reescrito como plano de faxina (4 etapas);
  `PROXIMA_TAREFA.md` gerada para a Etapa 2.
- [PENDÊNCIA] `.git/index.lock` existe e o bridge remoto não consegue apagar ("Operation not
  permitted") — trava o commit da Etapa 3 — depende de: o usuário apagar `.git\index.lock` pelo
  Windows.
- [PENDÊNCIA] Etapas 2 e 3 do plano de faxina (enxugar o histórico e commitar o trabalho de 20 e
  21/08) — depende de: abrir um chat EXEC.
- [PENDÊNCIA] Bordas de turno cortando palavras no modo ao vivo — depende de: o usuário decidir
  se incomoda no uso real; se incomodar, o candidato é o commit guiado por silêncio (Backlog).
- [PENDÊNCIA] Resíduo de ~100ms no fechamento do WebSocket após commit periódico — depende de:
  aprovação.
- [PROPOSTA-ASSISTENTE] Promover `.claude/tmp/teste_tempo_real.py` (harness que validou o
  protocolo da API ao vivo sem navegador) a ferramenta versionada em `transcritor/` — hoje é o
  único arquivo com valor dentro de uma pasta descartável, e some na primeira limpeza. Registrado
  no Backlog do `PLANO.md`, não aprovado.

## Coleta — rumo do próximo plano (2026-08-21)

- [DIRECIONAMENTO] O **modo ao vivo sai de foco**: o usuário decidiu em 2026-08-21 não investir
  nele agora. O commit guiado por silêncio (que resolveria o corte de palavras nas emendas) não
  entra no próximo plano e continua no Backlog, sem data.
- [DIRECIONAMENTO] A próxima frente é de **funcionalidade nova**, e o usuário vai trazer qual no
  próximo chat — não foi escolhida aqui.
- [DECISÃO] Não abrir um segundo `PLANO.md` vivo nem enfiar a frente nova como etapa do plano de
  faxina — trade-off: o planejamento da frente nova espera a virada, mas o método continua com um
  plano vivo, uma tarefa por vez e o arquivamento com gatilho na virada, que é o que acabou de ser
  arrumado.
- [DIRECIONAMENTO] A ordem de execução fica: faxina (Etapa 2) → commit (Etapa 3) → frente nova. O
  commit é o ponto de restauração; hoje o trabalho de 20 e 21/08 não tem nenhum commit atrás dele.
- [PROPOSTA-ASSISTENTE] Leitura do PM sobre dependência, para o próximo chat considerar: o app
  grava, transcreve e mostra o texto, mas o material fica em dois `.jsonl` sem dono. Quase todo o
  Backlog de produto (resumo, busca, temas, corpus, RAG) pressupõe o material organizado em uma
  unidade ("esta entrevista", "este projeto"), então **sessões e projetos com exportação** é a
  candidata que destrava as outras. Não aprovado — o usuário escolhe no próximo chat.

# Resumo consolidado — chat de PM de 2026-08-21

## Decisões
- Frente de usabilidade da interface de gravação **encerrada e aprovada** pelo usuário depois de
  uso real (5 etapas + 3 correções).
- Próximo plano é **só de faxina e fechamento** — trade-off: adia produto, mas entra na frente
  seguinte com repositório limpo e versionado.
- Faxina **não apaga nada**: snapshots de plano vão para `historico/snapshots/` — trade-off:
  1,1 MB de história continua no repositório, mas nada se perde e a pasta volta a ser legível.
- Limpeza de `.claude/tmp/` e `_to_delete/` e higiene do `consumo.jsonl` ficam no Backlog.
- **Modo ao vivo fora de foco**; commit guiado por silêncio adiado sem data.
- Um plano vivo por vez: a frente nova só vira `PLANO.md` na virada.
- Curva de amplitude da faixa por raiz quadrada com `RMS_TETO_BARRAS = 0.4` (calibração do
  Executor); `visibility: hidden` no lugar de `hidden` quando o elemento precisa manter o lugar.

## Artefatos
- `transcritor/frontend/index.html`: faixa espelhada, fina e arredondada, com curva compressiva;
  `placeholder` removido; copiar e lixeira/desfazer fora da caixa; controles laterais junto do
  centro; correção do botão de copiar que pulava de lugar.
- `.claude/estado/historico/PLANO_2026-08-21b_usabilidade-encerrado.md` e
  `.claude/estado/historico/PROGRESSO_usabilidade-gravacao_2026-08-20_a_2026-08-21.md` (15
  entradas, 1.398 linhas movidas sem edição).
- `.claude/estado/PLANO.md` novo (faxina, 4 etapas), `PROGRESSO.md` vivo zerado (101 KB → 493 B),
  `PROXIMA_TAREFA.md` da Etapa 2.
- `_RETOMADA_usabilidade-gravacao.md` reescrito; `coleta/2026-08-21_fechamento-usabilidade.md`
  aberto.

## Direcionamentos
- Ordem de execução: faxina → commit → frente nova.
- A frente nova é de funcionalidade e será escolhida pelo usuário no próximo chat.
- Candidata do PM, não aprovada: sessões e projetos com exportação, por destravar o resto do
  Backlog de produto.

## Pendências
- `.git/index.lock` trava o commit — depende de o usuário apagar pelo Windows.
- Etapas 2, 3 e 4 do plano de faxina — depende de abrir um chat EXEC (2 e 3) e de o PM fechar (4).
- Resíduo de ~100ms no fechamento do WebSocket — depende de aprovação.
- `consumo.jsonl` mistura uso real e teste; `.claude/tmp/` acumula 584 KB de rascunho, sendo
  `teste_tempo_real.py` o único com valor — ambos no Backlog.
- Corte de palavras nas emendas do modo ao vivo — sem data, frente fora de foco.

## Coleta — faxina executada e verificada (2026-08-21, depois do resumo acima)

> Registro posterior ao resumo consolidado: as Etapas 2 e 3 rodaram no mesmo dia, num chat EXEC.

- [ARTEFATO] Etapa 2 concluída: `.claude/estado/historico/` reorganizado — raiz com 17 arquivos
  (7 marcos + 8 snapshots citados por nome na coleta do MVP + as 2 retomadas de frentes
  encerradas) e `snapshots/` com 48. Total 65 = os 63 que havia + as 2 retomadas: **nada apagado**.
  265 referências checadas, zero quebradas. Verificado no artefato real pelo PM.
- [DECISÃO] O Executor manteve na raiz 8 snapshots que a estimativa do PM não previa, porque o
  grep os achou citados por nome — trade-off: a raiz ficou com 17 arquivos em vez dos "cerca de 7"
  estimados, mas nenhuma citação da `coleta/` virou link morto. A regra valia mais que o número, e
  ele registrou a diferença em vez de forçar a estimativa.
- [ARTEFATO] Etapa 3 concluída: 4 commits (`5e901ad` código do produto, `d0dc344` documentação do
  produto, `7c2e5ab` estado do método e histórico com 57 arquivos, `c3c2cdb` coleta), 63 arquivos
  ao todo, sem push. `git ls-files` filtrado por `.env`, os dois `.jsonl`, `.venv/`,
  `__pycache__/` e `.claude/tmp/` devolve zero — nada sensível entrou. **O projeto voltou a ter
  ponto de restauração.**
- [DECISÃO] Mensagens de commit sem acentuação, por escolha declarada do Executor — trade-off:
  fica esteticamente pior no `git log`, mas evita risco de mojibake permanente no histórico neste
  ambiente Windows/Git Bash. Conteúdo em português, íntegro.
- [DECISÃO] O `.git/index.lock` é apagado **pelo próprio Executor**, que roda local — a trava de
  "Operation not permitted" só existe pelo bridge remoto. Confirmado na prática em 2026-08-21;
  a nota de processo do `PLANO.md` foi corrigida.
- [PENDÊNCIA] Lição de processo registrada pela 2ª vez: estimativa numérica do PM (o "cerca de 7")
  não pode virar critério de pronto — vai como estimativa declarada.

# Adendo ao resumo consolidado — faxina executada (2026-08-21, fim do dia)

As Etapas 2 e 3 rodaram depois do resumo acima, no mesmo dia, e mudam duas linhas dele:

- **Artefatos**: `historico/` reorganizado (raiz 17, `snapshots/` 48, total 65 = 63 + 2 retomadas,
  nada apagado, 265 referências checadas e zero quebradas) e **4 commits** — `5e901ad` código do
  produto, `d0dc344` documentação do produto, `7c2e5ab` estado do método e histórico (57
  arquivos), `c3c2cdb` coleta. Sem push; `.env`, os dois `.jsonl`, `.venv/`, `__pycache__/` e
  `.claude/tmp/` fora de todos eles.
- **Pendências**: caem a do `.git/index.lock` (o Executor apaga sozinho, ele roda local) e as das
  Etapas 2 e 3. Do plano de faxina sobra só o repasse da Etapa 4, que depende de a frente de
  interface rodar primeiro.
