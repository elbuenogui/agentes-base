# Retomada — Assistente de Pesquisa por Áudio (faxina e fechamento)

> Para retomar em um chat novo: com esta pasta conectada, peça ao assistente para ler este arquivo
> (ou cole a "mensagem pronta" ao fim). **Atualizado em 2026-08-21.**
> A frente de usabilidade da interface de gravação **está encerrada** — o arquivo mantém o nome
> antigo de propósito, para não quebrar referências; o plano vivo é o de faxina e fechamento.

## Situar-se (ler nesta ordem — só o relevante, não tudo)

1. `CLAUDE.md` — modo PM/EXEC e a regra de idioma (tudo em português do Brasil).
2. `.claude/PM.md` (se entrar como PM) ou `.claude/EXECUTOR.md` (se entrar como EXEC) — níveis de
   registro no PROGRESSO e arquivamento por virada de plano.
3. `.claude/estado/PLANO.md` — plano vivo: faxina e fechamento, 4 etapas.
4. `.claude/estado/PROXIMA_TAREFA.md` — tarefa do commit (Etapa 3), pronta e **não executada**.
5. `coleta/2026-08-21_interface-enxuta.md` — a frente **viva**: o que o usuário pediu para a
   interface, com as decisões já tomadas. Lista ainda aberta.
6. `coleta/2026-08-21_fechamento-usabilidade.md` — fechamento da usabilidade e da faxina; o **resumo
   consolidado no fim** é a forma útil.
7. `coleta/2026-08-16_mvp-transcricao.md` — frente do MVP, encerrada; o **resumo consolidado no
   fim do arquivo** é a forma útil, o registro bruto acima dele só se precisar expandir algo.

Não há destino final separado para a documentação: a coleta é o registro interno do próprio
projeto, e o comando "aplicar" não é usado aqui.

## Objetivo da thread

Deixar o repositório versionado e arrumado e, em seguida, enxugar a interface — os controles de
configuração para dentro das Configurações, o upload para dentro do menu, e a tela sem o topo.

## Onde estou

O plano de usabilidade **fechou em 2026-08-21** (5 etapas + 3 correções aprovadas), depois de o
usuário usar a interface e aprovar. Arquivado em
`.claude/estado/historico/PLANO_2026-08-21b_usabilidade-encerrado.md`; as 15 entradas do
`PROGRESSO.md` (1.398 linhas) foram para
`.claude/estado/historico/PROGRESSO_usabilidade-gravacao_2026-08-20_a_2026-08-21.md`.

O plano vivo é o de faxina: **Etapa 1 concluída** (arquivamento da virada, feito pelo PM);
**Etapas 2, 3 e 4 em aberto**. Estado detalhado vive no `PLANO.md` — não duplicar aqui.

O app faz hoje: upload (com e sem streaming), gravação por microfone, modo tempo real com corte de
150s e gate de silêncio, consumo e transcrição ligados por id, painel com linha do tempo navegável
(janela móvel de 3min em 24h, navegação por dias) e interface de gravação com botão central de três
estados, faixa espelhada de 80 barras a 60ms com histórico real, cancelar, e copiar e
lixeira/desfazer numa linha abaixo da caixa. Custo acumulado: cerca de US$ 0,10 em API.

**Frente viva: interface enxuta.** O usuário abriu em 2026-08-21 e o primeiro lote já virou tarefa
escrita (guardada em `.claude/tmp/`): os três alternadores do topo viram controles dentro das
Configurações, o upload vira item do menu ⋮ (clicou, escolheu, transcreveu), a parte de cima da
página some com a área de gravação subindo, e o texto do upload passa a somar na mesma caixa das
gravações. Sem plano próprio por enquanto — cabe em uma tarefa. Arrastar e soltar áudio ficou para
depois, no Backlog.

## Decisões já tomadas (ponteiros)

- Modo ao vivo fica com `gpt-live-transcribe`, recusando troca por modelo mais barato → Backlog do
  `PLANO.md`, com a estimativa de economia registrada
- Detecção de turno pela API encerrada sem uso (o modelo recusa `turn_detection`) → Backlog
- Gate de silêncio é "não enviar", não "enviar e não comitar" → plano de usabilidade arquivado
- O cancelar nunca altera a caixa de transcrição, em nenhum modo
- Faxina sem apagar nada: snapshots vão para subpasta, não para o lixo → `PLANO.md`, Etapa 2
- Modo ao vivo fora de foco e um plano vivo por vez → coleta de 2026-08-21, resumo consolidado
- Limpeza de `.claude/tmp/` e `_to_delete/` e higiene do `consumo.jsonl` ficaram fora do plano,
  no Backlog, por decisão do usuário em 2026-08-21

## Plano / próximos passos

1. **Chat EXEC com a tarefa que está em `.claude/estado/PROXIMA_TAREFA.md`**: o commit de todo o
   trabalho de 20 e 21/08 (Etapa 3 da faxina). A tarefa manda o próprio Executor apagar o
   `.git/index.lock` — ele roda local e consegue; se não conseguir, apague `.git\index.lock` pelo
   Windows.
2. PM confere, marca a Etapa 3 no `PLANO.md` e **promove `.claude/tmp/TAREFA_interface-enxuta.md`
   para `PROXIMA_TAREFA.md`** — a tarefa já está escrita.
3. Chat EXEC com a interface enxuta: alternadores para dentro das Configurações (como
   interruptores), upload como item do menu ⋮, topo da página removido, saída de texto unificada
   na caixa de transcrição.
4. PM confere no artefato real e registra na `coleta/2026-08-21_interface-enxuta.md`. O usuário
   ainda pode ter mais mudanças de interface para pedir — quando o pedido crescer além de uma
   tarefa, aí sim vira plano.
5. Quando sobrar folga: Etapa 2 da faxina (tarefa guardada em `.claude/tmp/TAREFA_etapa2_faxina.md`)
   e o repasse final da Etapa 4. **Modo ao vivo continua fora de foco.**

## Pendências e dependências

- Commit do trabalho de 20 e 21/08 (Etapa 3) — tarefa pronta em `PROXIMA_TAREFA.md`, depende de:
  abrir um chat EXEC
- Interface enxuta — tarefa pronta em `.claude/tmp/TAREFA_interface-enxuta.md`, depende de: o
  commit sair primeiro e o PM promover a tarefa
- Etapa 2 da faxina (mover snapshots) — tarefa guardada em `.claude/tmp/TAREFA_etapa2_faxina.md`,
  adiada pelo usuário
- Mais mudanças de interface — depende de: o usuário passar o resto do que quer
- Resíduo do fechamento do WebSocket (~100ms após commit periódico) — depende de: aprovação
- Bordas de turno cortando palavras — sem data: o usuário tirou o modo ao vivo de foco em 2026-08-21
- `consumo.jsonl` mistura uso real com testes do Executor — Backlog, sem separação prevista
- `.claude/tmp/` guarda hoje **duas tarefas ainda não executadas** além do rascunho descartável —
  não limpar a pasta antes de promovê-las
## Onde ficam as coisas

- Produto: `transcritor/` (`backend/main.py`, `frontend/index.html`, `README.md`, `BENCHMARK.md`)
- Dados locais (não versionados): `transcritor/consumo.jsonl`, `transcritor/transcricoes.jsonl`
- Estado do método: `.claude/estado/` (PLANO, PROXIMA_TAREFA, PROGRESSO)
- Histórico: `.claude/estado/historico/` — marcos na raiz, snapshots de edição em `snapshots/`
  depois da Etapa 2
- Documentação curada: `coleta/2026-08-21_fechamento-usabilidade.md` (viva) e
  `coleta/2026-08-16_mvp-transcricao.md` (encerrada)
- Rascunho descartável: `.claude/tmp/` (fora do controle de versão) — hoje guarda também duas
  tarefas escritas e não executadas: `TAREFA_interface-enxuta.md` e `TAREFA_etapa2_faxina.md`

## Armadilhas conhecidas (não redescobrir)

- **`.git/index.lock` que o bridge não apaga** (2 ocorrências): qualquer `git status` rodado pelo
  bridge remoto deixa o lock para trás ("Operation not permitted") e o commit seguinte falha. Só o
  usuário resolve, apagando pelo Windows.
- **Backend antigo na porta 8000** servindo código obsoleto — 5 ocorrências. Conferir e derrubar
  antes de testar: `netstat -ano | findstr ":8000"`, depois
  `.venv\Scripts\uvicorn main:app --app-dir backend --port 8000`.
- **Cache do navegador**: recarregar com Ctrl+Shift+R depois de mexer no `index.html`.
- Gravar dentro de `.claude/` pelo bridge remoto exige `device_bash` com heredoc — a ferramenta de
  escrita recusa esse caminho.

---

## Mensagem pronta para colar no próximo chat

> PM. Estou retomando o Assistente de Pesquisa por Áudio. A pasta está conectada. Antes de
> começar, leia `_RETOMADA_usabilidade-gravacao.md` e os itens de "Situar-se". Use a skill
> `coleta-consolidacao` para ir registrando; ao fim, "consolidar". A faxina está em andamento (a
> tarefa do commit está em `PROXIMA_TAREFA.md`, ainda não executada, e a da interface enxuta está
> guardada em `.claude/tmp/`).
