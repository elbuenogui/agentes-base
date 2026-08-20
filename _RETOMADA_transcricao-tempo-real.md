# Retomada — transcrição em tempo real + linha do tempo de consumo (Assistente de Pesquisa por Áudio)

> Para retomar em um chat novo: com esta pasta/repositório conectado, peça ao assistente para ler
> este arquivo (ou cole a "mensagem pronta" ao fim). Serve para retomar este plano sem repetir o
> que já foi decidido. **Atualizado em 2026-08-19.**

## Situar-se (ler nesta ordem — só o relevante, não tudo)

1. `CLAUDE.md` — modo PM/EXEC e nota sobre coleta contínua.
2. `.claude/PM.md` (se entrar como PM) e `.claude/estado/PLANO.md` — o que já foi decidido e em
   que etapa estamos.
3. `transcritor/backend/main.py`, `transcritor/frontend/index.html`, `transcritor/README.md` —
   código atual do projeto.
4. `coleta/2026-08-16_mvp-transcricao.md`, seção final "Consolidado (2026-08-19)" — resumo
   curado de todas as decisões/artefatos/direcionamentos/pendências até aqui (cobre os quatro
   planos já rodados neste projeto, incluindo este).

> Não há destino final separado para este projeto — a coleta é registro interno, sem passo de
> "aplicar".

## Objetivo da thread

Adicionar transcrição em tempo real (o texto aparece enquanto o usuário ainda fala) usando a
Realtime API da OpenAI (`gpt-live-transcribe`), como modo opcional (alternador liga/desliga).
Junto, persistir a transcrição (texto, não o áudio) de cada requisição com timestamp, e mostrar
isso como uma linha do tempo no painel de consumo (zoom por hora/minuto, preço acima de cada
ponto, popup com o texto ao clicar) — para comparar custo entre requisições próximas no tempo
(ex.: mesmo áudio mandado para dois modelos diferentes).

## Onde estou

Plano de 6 etapas (limite do papel PM), 0 concluídas:
1. Autenticação e conexão com a API ao vivo — `PROXIMA_TAREFA.md` já gerada, aguardando o
   Executor rodar (pode já ter sido executada entre esta thread e a próxima — conferir
   `PROGRESSO.md`).
2. Captura em tempo real + alternador + exibição incremental — não iniciada.
3. Consumo no modo ao vivo — não iniciada.
4. Persistência da transcrição (`transcricoes.jsonl`) — não iniciada.
5. Linha do tempo no painel de consumo — não iniciada.
6. Testes finais e documentação — não iniciada.

## Decisões já tomadas (ponteiros)

- Todas as decisões relevantes → `coleta/2026-08-16_mvp-transcricao.md`, seção "Consolidado
  (2026-08-19)" (categorias Decisões/Artefatos/Direcionamentos/Pendências).
- Comparativo de custo API ao vivo vs. blocos com redundância, e a escolha pela API ao vivo →
  mesma seção "Consolidado", e detalhado na entrada "Novo plano aberto: transcrição em tempo
  real..." da coleta bruta.
- Preços de referência (podem mudar) → nota de processo no fim do `PLANO.md`.

## Plano / próximos passos

1. Verificar em `PROGRESSO.md` se a Etapa 1 já foi executada pelo Executor; se sim, conferir no
   artefato real, marcar concluída no `PLANO.md` e registrar na coleta.
2. Gerar `PROXIMA_TAREFA.md` da Etapa 2 (captura de áudio em tempo real + alternador "Tempo
   real" + exibição incremental do texto).
3. Seguir a ordem das etapas 3 a 6 conforme o `PLANO.md`.

## Pendências e dependências

- `.git/index.lock` ainda presente na raiz do repositório (achado em 2026-08-16, confirmado
  ainda lá em 2026-08-18) — depende de: usuário remover manualmente antes de qualquer commit.
- Estilo visual do aviso de corte de segurança (plano anterior) reaproveita a cor de "erro" —
  decisão de estilo dedicado ainda pendente do usuário/PM.
- Efeito de streaming (plano anterior) imperceptível em áudios curtos — decisão pendente do
  usuário sobre adiantamento artificial de exibição (Backlog).
- Transcrição em blocos com redundância — Backlog deste plano, para testar depois da API ao vivo.
- Rotação/limpeza automática de `transcricoes.jsonl` — sem política de retenção definida
  (Backlog deste plano).

## Onde ficam as coisas

- Código: `transcritor/backend/main.py`, `transcritor/frontend/index.html`,
  `transcritor/README.md`, `transcritor/benchmark.py` + `transcritor/BENCHMARK.md`.
- Dados locais: `transcritor/consumo.jsonl` (consumo por requisição), `transcritor/
  transcricoes.jsonl` (texto transcrito por requisição, criado nesta etapa).
- Estado PM/EXEC: `.claude/estado/PLANO.md`, `PROXIMA_TAREFA.md`, `PROGRESSO.md` (histórico de
  planos anteriores em `.claude/estado/historico/`).
- Coleta: `coleta/2026-08-16_mvp-transcricao.md` (registro bruto + resumo consolidado ao final).

---

## Mensagem pronta para colar no próximo chat

> PM. Estou retomando o Assistente de Pesquisa por Áudio (pasta `transcritor/`, dentro do
> repositório `agentes-base`). A pasta está conectada. Antes de começar, leia
> `_RETOMADA_transcricao-tempo-real.md` e os itens de "Situar-se" ali (`CLAUDE.md`,
> `.claude/PM.md`, `.claude/estado/PLANO.md`, e o resumo consolidado no fim de
> `coleta/2026-08-16_mvp-transcricao.md`). Use a skill `coleta-consolidacao` para ir registrando;
> ao encerrar, "consolidar". Lembre-se: por padrão você fica só no papel de PM (planejar/
> coordenar/gerar tarefa) — só execute código se eu pedir de forma explícita e pontual; e não
> rode bateria de testes exaustiva a cada iteração pequena, só validação básica, deixando os
> testes completos para o final de cada etapa. Quero continuar por: verificar se a Etapa 1
> (autenticação e conexão com a API ao vivo) já foi executada pelo Executor e, se sim, seguir
> para a Etapa 2 (captura em tempo real + alternador + exibição incremental).
