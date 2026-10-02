---
tema: Radar / Painel de Benchmark de IA — painel_json() versão 2 e página versão 2
data: 2026-10-02
anterior: coleta/2026-10-01_radar-coleta-e-importacao.md
---

# Coleta — radar: painel_json() v2 e página v2 (2026-10-02)

## 1. Registro por interação

- [DECISÃO] `radar.painel_json()` reescrita (migração `radar_painel_json_v2`). Mantém as chaves da v1 e
  acrescenta `versao`, `contagens`, `provedores` (canais, planos e capacidades aninhados), `programas`
  (ordenados por elegibilidade e situação), `gratis`, `biblioteca`, `indicadores` e `historico_precos`.
  Trade-off: o JSON passa de 85 KB para ~560 KB, em troca de a página mostrar a biblioteca inteira sem
  outra fonte de dados.
- [DECISÃO] As ofertas grátis saem de `novidades` e vão para `gratis`, sem o filtro de 60 dias; o provedor
  é casado pelo nome (101 de 109 casam; as 8 da v1 ficam sem `provedor_id`).
- [DECISÃO] `biblioteca` usa chaves curtas (`p`, `st`, `e`, `s`, `u`, `n`…) e ignora as 8 linhas antigas sem
  `provedor_id`. Trade-off: menos legível, em troca de ~40% a menos de tamanho.
- [DECISÃO] A v1 ficou guardada como `radar.painel_json_v1()` para voltar atrás.
- [ARTEFATO] `radar/banco/painel_json.sql` — fonte da função v2.
- [ARTEFATO] `radar/painel/painel.html` — página v2, mesma identidade visual da v1, com navegação fixa e
  seções novas: programas, grátis, biblioteca de modelos (busca e filtros), provedores, quem faz o quê,
  indicadores e histórico de preços. O gráfico ganhou o modo "todos com nota" (33 modelos com AA).
- [DIRECIONAMENTO] A rede do contêiner da nuvem não alcança o Supabase nem o OpenRouter (proxy recusa).
  O `dados.json` sai pelo `execute_sql`: a saída grande vai para um arquivo em `tool-results/` e um script
  extrai o JSON. Vale lembrar para o script diário de preços: ele não roda nesta nuvem sem liberar a rede.
- [DECISÃO] O Guilherme autorizou o commit e a republicação. Página v2 publicada no mesmo endereço
  (https://claude.ai/artifact/FGk5hSwv1fYD5f1spEtobM, versão 3 do artefato), com o `dados.json` novo.

## 2. Resumo consolidado

**Decisões**
- `painel_json()` v2 com a biblioteca inteira; grátis em chave própria; v1 guardada para rollback.

**Artefatos**
- `radar/banco/painel_json.sql`, `radar/painel/painel.html`; função v2 e `painel_json_v1()` no Supabase.
- Página v2 publicada no endereço da v1.

**Direcionamentos**
- O contêiner da nuvem não alcança Supabase nem OpenRouter; extrair dados pelo arquivo de saída do `execute_sql`.

**Pendências**
- Medição de consumo dos recursos e previsão de esgotamento (próximo passo da retomada).
