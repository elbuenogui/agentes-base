---
tema: Radar / Painel de Benchmark de IA — coleta completa dos 32 provedores e importação no banco
data: 2026-10-01 a 2026-10-02
anterior: _RETOMADA_radar.md (versão de 2026-10-01)
---

# Coleta — radar: coleta completa e importação (2026-10-01 a 2026-10-02)

## 1. Registro por interação

- [DIRECIONAMENTO] A pasta `radar/` e o `_RETOMADA_radar.md` estavam no branch `input-de-audio`
  (commit c6d36da), não em `main`; o branch `radar-coleta` ainda não existia — a coleta pesada
  nunca tinha rodado.
- [DIRECIONAMENTO] Estado do banco antes: esquema `radar` com 21 modelos, 21 preços, 34 notas,
  7 análises, 43 novidades e 8 recursos; tabelas da biblioteca vazias.
- [DECISÃO] O assistente abriu as 5 sessões de coleta na nuvem (autorizado pelo Guilherme), partindo
  de `input-de-audio` e criando `radar-coleta` a partir dele. Trade-off: rapidez em troca de custo —
  as sessões herdaram o modelo mais caro por não terem modelo declarado.
- [DECISÃO] **A coleta completa não se repete.** Manutenção incremental e barata: preços diários por
  script sem IA (API do OpenRouter), notas semanais e planos/programas mensais só do que mudou, uma
  sessão por vez, modelo pequeno declarado. Trade-off: a biblioteca envelhece nas partes que não
  são relidas, em troca de um custo baixo e previsível. Registrado em `radar/ROTEIRO_COLETA.md`
  (seção "Manutenção") e no `_RETOMADA_radar.md` — commit c7a0b47.
- [DIRECIONAMENTO] Custo medido da coleta completa: US$ 67,92 (sessões 1 a 5: 18,58 · 14,08 · 12,71 ·
  14,36 · 8,18), pago do crédito de nuvem de US$ 171.
- [DIRECIONAMENTO] As sessões pararam antes do commit e se recusaram a commitar por autorização
  repassada pela sessão-mãe: autorização tem de vir do Guilherme na própria sessão. Ele autorizou
  em cada uma.
- [ARTEFATO] `radar-coleta`: 32 `radar/coleta/<id>.json` + 5 relatórios (commits 46b7580 a 6a29a80);
  os 32 passam no `radar/validar.py`.
- [ARTEFATO] `radar/importar.py` (gera SQL de upsert por provedor), no `radar-coleta`.
- [DECISÃO] Identificadores de modelo seguem a coleta (do provedor), não o OpenRouter. 8 modelos
  antigos renomeados levando preços (8), notas (12) e análises (1): `x-ai/grok-4.7`→`xai/grok-4.7`,
  `meta-llama/llama-4-maverick`→`meta/llama-4-maverick`, `mistralai/mistral-medium-3-5`→
  `mistral/mistral-medium-3.5`, `mistralai/mistral-small-2603`→`mistral/mistral-small-4` (único
  casamento inferido, por data), `moonshotai/kimi-k3`→`moonshot/kimi-k3`, `z-ai/glm-5.3`→
  `zai/glm-5.3`, `qwen/qwen3.8-max-0902`→`qwen/qwen3.8-max`, `deepseek/deepseek-v4-pro-0813`→
  `deepseek/deepseek-v4-pro`. Trade-off: rompe a ligação direta com os ids do OpenRouter, em troca
  de uma chave única por modelo daqui em diante.
- [DECISÃO] Modelos novos entram com `acompanhado = false`; os 21 curados continuam `true`.
  Trade-off: a tabela principal do painel fica enxuta, e a biblioteca completa precisa de seção
  própria na versão 2.
- [DECISÃO] Preços entram com `vigente_desde = 2026-10-01`, começando o histórico de preços.
- [DIRECIONAMENTO] Comandos com `delete` expiram em 60 s pela ferramenta do Supabase (pedem
  confirmação que não chega). As 8 linhas antigas ficaram vazias, com `acompanhado = false` e
  `status = 'legado'`, em vez de apagadas.
- [DECISÃO] Extensão `http` ativada no Supabase (autorizada pelo Guilherme) e criadas
  `radar.importar_coleta(jsonb)` e `radar.importar_coleta_url(text)`: o banco baixa o JSON do
  GitHub e faz o upsert sozinho. Trade-off: uma extensão a mais no projeto, em troca de importar
  sem colar 700 KB de SQL (~200 mil tokens) — e a mesma função serve à manutenção.
- [ARTEFATO] Banco depois da importação: 32 provedores, 662 modelos (21 acompanhados), 317 preços,
  696 preços por unidade, 84 notas, 388 canais, 189 planos, 242 capacidades, 93 programas,
  109 ofertas grátis (em `novidades`, tipo `gratis`), 26 indicadores.
- [PENDÊNCIA] Apagar as 8 linhas antigas de `radar.modelos` — depende de: Guilherme rodar o
  `delete` no painel do Supabase (lista no `_RETOMADA_radar.md`).
- [PENDÊNCIA] Atualizar `radar.painel_json()` e publicar a página versão 2 no mesmo endereço —
  depende de: autorização do Guilherme para republicar.
- [PENDÊNCIA] Juntar `radar-coleta` ao `input-de-audio` (ou ao `main`) — depende de: Guilherme
  decidir o branch de destino.

## 2. Resumo consolidado

**Decisões**
- Coleta completa roda uma vez só; manutenção incremental, uma sessão, modelo pequeno declarado.
- Ids de modelo seguem o provedor; 8 modelos antigos renomeados com seus dados.
- Modelos novos fora da tabela curada (`acompanhado = false`); preços datados de 2026-10-01.
- Importação pelo próprio banco (extensão `http` + `radar.importar_coleta_url`).

**Artefatos**
- `radar/coleta/*.json` (32) e relatórios, `radar/importar.py` — branch `radar-coleta`.
- `radar/ROTEIRO_COLETA.md` com a seção "Manutenção" e `_RETOMADA_radar.md` — `input-de-audio`.
- Funções `radar.importar_coleta(jsonb)` e `radar.importar_coleta_url(text)` no Supabase.
- Biblioteca carregada no esquema `radar` (contagens acima).

**Direcionamentos**
- Custo real da coleta completa: US$ 67,92.
- Sessões filhas não aceitam autorização repassada; commit só com o Guilherme na própria sessão.
- `delete` pela ferramenta do Supabase expira; usar o painel para apagar.

**Pendências**
- Apagar as 8 linhas antigas — Guilherme, no painel.
- `painel_json()` + página versão 2 — autorização para republicar.
- Destino do branch `radar-coleta` — Guilherme.
- Medição de consumo, skill do radar e tarefa agendada (passos 4 e 5 da retomada).
