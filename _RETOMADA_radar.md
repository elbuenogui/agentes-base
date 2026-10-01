# Retomada — Radar / Painel de Benchmark de IA (agentes-base)

> Para retomar em um chat novo: com este repositório conectado (ou numa sessão do Claude Code na
> nuvem neste repositório), peça para ler este arquivo, ou cole a "mensagem pronta" do fim.
> Trabalho normal, sem modo PM/EXEC. **Atualizado em 2026-10-01.**

## Situar-se (ler nesta ordem)

1. `CLAUDE.md`: as duas regras (só o Guilherme autoriza commit; tudo em português).
2. `radar/ROTEIRO_COLETA.md`: regras da coleta e formato dos arquivos.
3. `radar/provedores.json`: os 32 provedores e a sessão de cada um.
4. Doc `claude/painel-benchmark-ia.md` no Project do claude.ai: estado do banco e pendências.

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
- **Coleta pesada:** rodando desde 2026-10-01 em 5 sessões do Claude Code na nuvem, que gravam no
  branch `radar-coleta` (criado a partir de `input-de-audio`, onde está a pasta `radar/`).
  A sessão 2 grava o relatório em `RELATORIO_laboratorio_2.md`, porque divide o grupo com a 1.

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
- A tarefa agendada fica por último, depois de calibrar o ritmo: diário leve, semanal para as notas,
  análises por gatilho e mensal para o gasto.

## Próximos passos

1. ~~Commit e push de `radar/` e deste arquivo.~~ Feito.
2. ~~Abrir as 5 sessões de coleta.~~ Abertas em 2026-10-01; aguardar o push de todas no `radar-coleta`.
3. **Chat com o banco** (Cowork, no Project agentes-base): ler o branch `radar-coleta`, rodar
   `radar/validar.py`, importar no esquema `radar`, atualizar `painel_json()` e publicar a página
   versão 2 no mesmo endereço.
4. Medir o consumo de cada recurso (ccusage, `/status` do Codex, `/usage` do Antigravity, API de
   custos da OpenAI), gravar em `radar.leituras` e montar a previsão de esgotamento.
5. Escrever a skill do radar e só então a tarefa agendada, seguindo a seção "Manutenção" do roteiro.

## Pendências

- Separar a chave da OpenAI por projeto (assistente, Mari, Codex) — depende do Guilherme.
- A medição de consumo precisa rodar no computador do Guilherme: a ponte do Cowork é uma VM que não
  enxerga os CLIs do Windows.
- Programas elegíveis e abertos viram tarefa no Planejamento e Execução (depois).

---

## Mensagem pronta para colar no próximo chat

> Estou retomando o Radar / Painel de Benchmark de IA no agentes-base. Leia `_RETOMADA_radar.md`
> e os itens de "Situar-se". Quero continuar por: <próximo passo>.
