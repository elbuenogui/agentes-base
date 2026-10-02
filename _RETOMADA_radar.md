# Retomada — Radar / Painel de Benchmark de IA (agentes-base)

> Para retomar em um chat novo: com este repositório conectado (ou numa sessão do Claude Code na
> nuvem neste repositório), peça para ler este arquivo, ou cole a "mensagem pronta" do fim.
> Trabalho normal, sem modo PM/EXEC. **Atualizado em 2026-10-02.**

## Situar-se (ler nesta ordem)

1. `CLAUDE.md`: as duas regras (só o Guilherme autoriza commit; tudo em português).
2. `radar/ROTEIRO_COLETA.md`: regras da coleta e formato dos arquivos.
3. `radar/provedores.json`: os 32 provedores e a sessão de cada um.
4. Doc `claude/painel-benchmark-ia.md` no Project do claude.ai: estado do banco e pendências.
5. `coleta/2026-10-01_radar-coleta-e-importacao.md`: o que aconteceu na coleta e na importação.

## Objetivo da thread

Uma biblioteca de IA que se atualiza sozinha e dá insights. Ela reúne modelos e preços, custo ×
desempenho, cada provedor (planos, ferramentas, grátis, programas para estudante e pesquisador,
canais oficiais), os recursos do Guilherme com previsão de esgotamento, e o que usar onde.

## Onde estou

- **Página publicada (versão 1):** Painel de Benchmark de IA, https://claude.ai/artifact/FGk5hSwv1fYD5f1spEtobM.
  Lê o `dados.json`, que é a saída de `select radar.painel_json()`.
- **Banco:** esquema `radar` no Supabase `rag-compartilhado`, já com as tabelas da biblioteca
  (`provedores`, `canais`, `planos`, `capacidades`, `programas`, `indicadores`, `precos_unidade`,
  `leituras`). A primeira carga tem 21 modelos, 7 análises e 43 novidades.
- **Coleta pesada: feita e importada** (2026-10-01/02). Os 32 JSON validados estão no branch
  `radar-coleta` (ainda não juntado a outro branch). O banco tem 32 provedores, 662 modelos
  (21 acompanhados), 317 preços, 696 preços por unidade, 84 notas, 388 canais, 189 planos,
  242 capacidades, 93 programas, 109 ofertas grátis (em `novidades`, tipo `gratis`) e 26 indicadores.
- **Importar de novo** (manutenção): `select radar.importar_coleta_url('https://raw.githubusercontent.com/elbuenogui/agentes-base/radar-coleta/radar/coleta/<id>.json');`
  É upsert: rodar duas vezes não duplica. Usa a extensão `http`, ativada para isso.
- **`painel_json()` ainda é o da versão 1**: só lê `modelos` acompanhados, `precos`, `notas`,
  `analises`, `novidades`, `recursos` e `gasto_por_modelo`. A página publicada não mostra a biblioteca nova.

## Decisões já tomadas

- A coleta pesada roda no Claude Code na nuvem, pago com o crédito de US$ 171 (vence em 05/11).
  Assim não gasta a cota semanal do Max.
- Entram todos os modelos ativos de cada provedor, não só o topo de linha.
- Números só com fonte e data. Indicadores de custo-benefício só quando encontrados numa fonte.
- Extras da versão 2: teste próprio em português e histórico de preços.
- **A coleta completa não se repete** (2026-10-01): saiu cara (5 sessões em paralelo, um subagente
  por provedor, modelo caro herdado). A manutenção é incremental e barata: preços diários por script
  sem IA, notas semanais e planos/programas mensais só do que mudou, sempre numa sessão só e com
  modelo pequeno declarado. Detalhe em `radar/ROTEIRO_COLETA.md`, seção "Manutenção".
- Ids de modelo seguem o provedor (`xai/`, `zai/`, `moonshot/`…), não o OpenRouter; 8 modelos
  antigos foram renomeados com seus preços, notas e análises (lista na coleta de 2026-10-01).
- Modelo novo entra com `acompanhado = false`; a tabela curada continua com os 21. A biblioteca
  completa precisa de seção própria na página.
- Preços datados por `vigente_desde` = dia da coleta: é daí que sai o histórico de preços.
- A tarefa agendada fica por último, depois de calibrar o ritmo: diário leve, semanal para as notas,
  análises por gatilho e mensal para o gasto.

## Próximos passos

1. ~~Coleta completa~~ e ~~importação no banco~~. Feitas em 2026-10-01/02.
2. **Próximo: atualizar `radar.painel_json()`** para incluir provedores, planos, capacidades,
   programas (com `elegivel`), ofertas grátis, preços por unidade e o histórico de preços, e montar
   a **página versão 2** no mesmo endereço (https://claude.ai/artifact/FGk5hSwv1fYD5f1spEtobM).
   Republicar exige autorização do Guilherme.
3. Medir o consumo de cada recurso (ccusage, `/status` do Codex, `/usage` do Antigravity, API de
   custos da OpenAI), gravar em `radar.leituras` e montar a previsão de esgotamento.
4. Escrever a skill do radar e só então a tarefa agendada, seguindo a seção "Manutenção" do roteiro.

## Pendências

- **Apagar 8 linhas antigas de `radar.modelos`** (vazias, `acompanhado = false`). A ferramenta do
  Supabase deixa `delete` expirar; rodar no painel do Supabase:
  `delete from radar.modelos where id in ('x-ai/grok-4.7','meta-llama/llama-4-maverick','mistralai/mistral-medium-3-5','mistralai/mistral-small-2603','moonshotai/kimi-k3','z-ai/glm-5.3','qwen/qwen3.8-max-0902','deepseek/deepseek-v4-pro-0813');`
- **Destino do branch `radar-coleta`** (juntar a `input-de-audio` ou a `main`) — decisão do Guilherme.

- Separar a chave da OpenAI por projeto (assistente, Mari, Codex) — depende do Guilherme.
- A medição de consumo precisa rodar no computador do Guilherme: a ponte do Cowork é uma VM que não
  enxerga os CLIs do Windows.
- Programas elegíveis e abertos viram tarefa no Planejamento e Execução (depois).

---

## Mensagem pronta para colar no próximo chat

> Estou retomando o Radar / Painel de Benchmark de IA no agentes-base. Leia `_RETOMADA_radar.md`
> e os itens de "Situar-se". Quero continuar por: atualizar o `painel_json()` e montar a página versão 2.
