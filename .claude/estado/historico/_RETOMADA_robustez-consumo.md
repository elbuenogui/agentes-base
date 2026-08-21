# Retomada — robustez, consumo e streaming (Assistente de Pesquisa por Áudio)

> Para retomar em um chat novo: com esta pasta/repositório conectado, peça ao assistente para ler
> este arquivo (ou cole a "mensagem pronta" ao fim). Serve para retomar o plano de robustez/
> consumo sem repetir o que já foi decidido. **Atualizado em 2026-08-18.**

## Situar-se (ler nesta ordem — só o relevante, não tudo)

1. `CLAUDE.md` — modo PM/EXEC e nota sobre coleta contínua.
2. `.claude/PM.md` (se entrar como PM) e `.claude/estado/PLANO.md` — o que já foi decidido e em
   que etapa estamos.
3. `transcritor/backend/main.py`, `transcritor/frontend/index.html`, `transcritor/README.md` —
   código atual do projeto.
4. `coleta/2026-08-16_mvp-transcricao.md`, seção final "Consolidado (2026-08-18)" — resumo
   curado de todas as decisões/artefatos/direcionamentos/pendências até aqui.

> Não há destino final separado para este projeto — a coleta é registro interno, sem passo de
> "aplicar".

## Objetivo da thread

Continuar o plano de robustez e visibilidade de custo da gravação: configurações avançadas
(microfone), proteção contra gravação infinita, feedback visual, correção da permissão de
microfone repetida, painel de consumo (tokens/custo, sessão e histórico diário com gráfico) e a
opção de testar streaming no transcript.

## Onde estou

Plano de 7 etapas (limite do papel PM), 4 concluídas:
1. Servir frontend via servidor local — concluída.
2. Painel de configurações com seletor de microfone — concluída.
3. Cronômetro + corte de segurança (2min30s) — concluída.
4. Barras de nível de áudio + validação de áudio real (popup "Não foi identificado nenhuma
   fala") — concluída.
5. Registro de consumo no backend — `PROXIMA_TAREFA.md` já gerada, aguardando o Executor rodar
   (pode já ter sido executada entre esta thread e a próxima — conferir `PROGRESSO.md`).
6. Painel de consumo no frontend (com gráfico) — não iniciada.
7. Streaming do transcript — não iniciada.

## Decisões já tomadas (ponteiros)

- Todas as decisões relevantes → `coleta/2026-08-16_mvp-transcricao.md`, seção "Consolidado
  (2026-08-18)" (categorias Decisões/Artefatos/Direcionamentos/Pendências).
- Preços de referência da OpenAI (podem mudar) → nota de processo no fim do `PLANO.md`.

## Plano / próximos passos

1. Verificar em `PROGRESSO.md` se a Etapa 5 já foi executada pelo Executor; se sim, conferir no
   artefato real, marcar concluída no `PLANO.md` e registrar na coleta.
2. Gerar `PROXIMA_TAREFA.md` da Etapa 6 (painel de consumo no frontend: ícone estilo
   "avançado" — mesma classe `.icone-avancado` do painel de configurações —, sessão + histórico
   diário + gráfico de custo por dia, botão de reset só da sessão).
3. Etapa 7: streaming do transcript (alternador liga/desliga, mesmo estilo do alternador de
   modelo).

## Pendências e dependências

- `.git/index.lock` encontrado durante a Etapa 2 do MVP (2026-08-16) — conferir se ainda existe
  antes de qualquer commit.
- Estilo visual do aviso de corte de segurança (Etapa 3 deste plano) reaproveita a cor de "erro"
  — Executor sugeriu um estilo de "aviso" dedicado; decisão pendente do usuário/PM.
- CORS aberto (`allow_origins=["*"]`) — Backlog, revisar se um dia for exposto fora da máquina.
- Exploração de plataforma self-hosted tipo Claude com agentes/skills (Open WebUI, LibreChat,
  AnythingLLM, Dify, LobeHub) — discutida, mas decidida para continuar em **outro chat**, sem
  relação direta com este plano.

## Onde ficam as coisas

- Código: `transcritor/backend/main.py`, `transcritor/frontend/index.html`,
  `transcritor/README.md`, `transcritor/benchmark.py` + `transcritor/BENCHMARK.md`.
- Estado PM/EXEC: `.claude/estado/PLANO.md`, `PROXIMA_TAREFA.md`, `PROGRESSO.md` (histórico de
  planos anteriores em `.claude/estado/historico/`).
- Coleta: `coleta/2026-08-16_mvp-transcricao.md` (registro bruto + resumo consolidado ao final).

---

## Mensagem pronta para colar no próximo chat

> PM. Estou retomando o Assistente de Pesquisa por Áudio (pasta `transcritor/`, dentro do
> repositório `agentes-base`). A pasta está conectada. Antes de começar, leia
> `_RETOMADA_robustez-consumo.md` e os itens de "Situar-se" ali (`CLAUDE.md`, `.claude/PM.md`,
> `.claude/estado/PLANO.md`, e o resumo consolidado no fim de
> `coleta/2026-08-16_mvp-transcricao.md`). Use a skill `coleta-consolidacao` para ir registrando;
> ao encerrar, "consolidar". Quero continuar por: verificar se a Etapa 5 (registro de consumo no
> backend) já foi executada pelo Executor e, se sim, seguir para a Etapa 6 (painel de consumo no
> frontend).
