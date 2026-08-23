# Inventário do repositório — o que já temos e o que falta

> PM, 2026-08-21. Levantamento por leitura do repositório, feito para dimensionar as fases.
> Contagens conferidas na máquina; nenhuma estimativa vira critério de pronto.

## 1. O que já existe e funciona

### Backend — `transcritor/backend/main.py`, 454 linhas

| Capacidade | Situação |
|---|---|
| Transcrição em lote (`POST /transcrever`) | pronta, 3 modelos |
| Transcrição com streaming (mesmo endpoint, `stream=true`) | pronta, NDJSON com `delta`/`final`/`erro` |
| Token efêmero para o modo ao vivo | pronto — **congelado**, sem consumidor novo |
| Cálculo de custo em dólar por requisição | pronto, por token, com fallback por duração |
| Registro de consumo (`consumo.jsonl`) e de transcrições (`transcricoes.jsonl`), ligados por id | pronto |
| Consulta de consumo (`GET /consumo`) | pronta: sessão, por dia e lista de requisições com texto |
| Tratamento de 6 situações de erro | presente, mas **sem código legível por máquina** |

Dependências: `openai`, `fastapi`, `uvicorn`, `python-multipart`, `python-dotenv`. Cinco. Enxuto.

### Interface web — `transcritor/frontend/index.html`, 2.748 linhas, ~90 funções

Gravação rápida com medidor de nível e cronômetro; corte por segurança; upload de arquivo pelo
menu; copiar, recortar, apagar e desfazer com snapshot; configurações (modelo, streaming, tempo
real, microfone); **painel de consumo com linha do tempo navegável** (dia, janela de 24h, zoom,
popup por requisição); e o modo ao vivo com captura PCM, reamostragem e envio por WebSocket.

Isso é bem mais do que "MVP de transcrição". É um produto web completo de uma tela.

### Método e documentação

Kit PM/EXEC com `PM.md`, `EXECUTOR.md` e os três arquivos de estado; 5 arquivos `PROGRESSO_*.md`
arquivados cobrindo ~12 sessões; 3 documentos curados em `coleta/`; `README.md` do transcritor com
**635 linhas** e 20 seções; `BENCHMARK.md` comparando modelos com áudio real.

## 2. O que isso significa por fase

| Fase | O que já temos | O que falta |
|---|---|---|
| **F1 Núcleo** | tudo funcionando | o contrato **escrito e medido**; códigos de erro; idioma na chamada |
| **F2 Desktop** | **nada** | tudo: nenhuma linha de app desktop existe |
| **F3 Android** | nada | tudo |
| **F4/F5 Watch e GPT** | nada | tudo, e o relógio ainda nem foi confirmado como aparelho em mãos |
| **F6–F9** | nada | tudo |

**A conclusão desconfortável e útil**: o repositório tem um **produto web completo e nenhum app**.
A Fase 2 não é "adaptar o que existe" — mas **corrijo aqui uma afirmação que eu tinha feito errado**
(apontada pelo usuário em 2026-08-21): eu disse que a interface web "não se aproveita". O **código**
não se aproveita, porque ela é uma página e o produto é uma janela flutuante sobre outros
aplicativos. O **desenho** se aproveita inteiro, e é o documento de comportamento mais completo que
este projeto tem: o fluxo de gravação, o balão de status, o desfazer por snapshot, o menu de três
pontos, o painel de consumo, a lista de configurações que importam. A spec da Fase 2 deve
transcrever isso, não reinventar. Ver `COMPORTAMENTOS_PARQUEADOS.md`.

Do backend, o que se aproveita de verdade é o aprendizado embutido nele: custo por token,
tratamento de erro, formato de streaming. Por isso o entregável da Fase 1 é o contrato.

## 3. Lacunas descobertas nesta análise

**I1 — A chamada à API não envia o idioma.** `parametros_extra` (`main.py:246`) só carrega
`chunking_strategy`. Com "só português" decidido, passar `language="pt"` tende a melhorar precisão,
reduzir latência e impedir troca de idioma. Barato, e tem efeito direto na régua do Win+H.
→ **Entra como Etapa 3 da Fase 1.**

**I2 — `CLAUDE.md` está desatualizado.** Ele descreve o repositório como "MVP de um motor mínimo de
transcrição" e não menciona `spec/`, o Spec-Driven Development nem a Fase 1. É o **primeiro arquivo
que todo chat novo lê** — desatualizado, ele desalinha o Executor logo na entrada, antes de qualquer
tarefa. → **Entra como etapa da Fase 1.**

**I3 — Não existe teste automatizado nenhum no repositório.** Toda verificação foi manual ou
Playwright ad hoc, jogado fora depois. A cadeia `TASK → TEST` do SDD pressupõe teste que fica.
→ **Questão aberta nova (Q8)**, porque a resposta custa dinheiro: teste que chama a API de verdade
gasta a cada execução.

**I4 — O histórico virou requisito e não tem dono.** Ver [Q7](../QUESTOES_ABERTAS.md).

**I5 — `.claude/tmp/` guarda 594 KB**, dos quais o único arquivo com valor é
`teste_tempo_real.py` (14 KB) — já previsto na Etapa 4 da Fase 1. O resto é um `.wav` de 562 KB,
um log de uvicorn e duas cópias de tarefas já executadas.

**I6 — Pontas soltas menores**: `transcritor/BENCHMARK.md` modificado e não commitado (anterior a
esta sessão); `_to_delete/` com um fóssil de 0 byte; arquivos `.fuse_hidden*` deixados pelo bridge
remoto.

## 4. Efeito no plano da Fase 1

Duas etapas novas, ambas pequenas e ambas dentro do objetivo da fase (fechar o contrato):

- **Enviar `language="pt"` na chamada** — o contrato precisa dizer qual idioma o núcleo assume.
- **Atualizar o `CLAUDE.md`** — o contrato não serve de nada se quem entra no repositório continuar
  lendo que isto é um MVP de transcrição.
