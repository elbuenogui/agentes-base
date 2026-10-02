# Retomada — Radar / Painel de Benchmark de IA (agentes-base)

> Para retomar em um chat novo: com este repositório conectado (ou numa sessão do Claude Code na
> nuvem neste repositório), peça para ler este arquivo, ou cole a "mensagem pronta" do fim.
> Trabalho normal, sem modo PM/EXEC. **Atualizado em 2026-10-02 (chat do painel v2, encerrado).**

## Situar-se (ler nesta ordem)

1. `CLAUDE.md`: as duas regras (só o Guilherme autoriza commit; tudo em português).
2. `radar/ROTEIRO_COLETA.md`: regras da coleta e formato dos arquivos.
3. `radar/provedores.json`: os 32 provedores e a sessão de cada um.
4. Doc `claude/painel-benchmark-ia.md` no Project do claude.ai: estado do banco e pendências.
5. `coleta/2026-10-01_radar-coleta-e-importacao.md`: o que aconteceu na coleta e na importação.
6. `coleta/2026-10-02_radar-painel-v2.md`: a função `painel_json()` v2 e a página v2.
7. `radar/banco/painel_json.sql` e `radar/painel/painel.html`: a fonte do que está no ar.

## Objetivo da thread

Uma biblioteca de IA que se atualiza sozinha e dá insights. Ela reúne modelos e preços, custo ×
desempenho, cada provedor (planos, ferramentas, grátis, programas para estudante e pesquisador,
canais oficiais), os recursos do Guilherme com previsão de esgotamento, e o que usar onde.

## Onde estou

- **Página publicada (versão 2, desde 2026-10-02):** Painel de Benchmark de IA, https://claude.ai/artifact/FGk5hSwv1fYD5f1spEtobM.
  Lê o `dados.json`, que é a saída de `select radar.painel_json()`. Fonte da página: `radar/painel/painel.html`.
- **Banco:** esquema `radar` no Supabase `rag-compartilhado`, já com as tabelas da biblioteca
  (`provedores`, `canais`, `planos`, `capacidades`, `programas`, `indicadores`, `precos_unidade`,
  `leituras`). A primeira carga tem 21 modelos, 7 análises e 43 novidades.
- **Coleta pesada: feita e importada** (2026-10-01/02). Os 32 JSON validados estão no branch
  `radar-coleta` (ainda não juntado a outro branch). O banco tem 32 provedores, 662 modelos
  (21 acompanhados), 317 preços, 696 preços por unidade, 84 notas, 388 canais, 189 planos,
  242 capacidades, 93 programas, 109 ofertas grátis (em `novidades`, tipo `gratis`) e 26 indicadores.
- **Importar de novo** (manutenção): `select radar.importar_coleta_url('https://raw.githubusercontent.com/elbuenogui/agentes-base/radar-coleta/radar/coleta/<id>.json');`
  É upsert: rodar duas vezes não duplica. Usa a extensão `http`, ativada para isso.
- **`painel_json()` já é a versão 2** (2026-10-02), aplicada no banco. Fonte em `radar/banco/painel_json.sql`.
  Mantém as chaves da v1 e acrescenta `versao`, `contagens`, `provedores` (com canais, planos e
  capacidades), `programas`, `gratis` (saiu de `novidades`), `biblioteca` (654 modelos, com preços por
  unidade e notas), `indicadores` e `historico_precos`. Sai com ~560 KB. A v1 ficou guardada em
  `radar.painel_json_v1()` para voltar atrás.
- **Página versão 2 publicada** (versão 3 do artefato): `radar/painel/painel.html` (lê `dados.json`, a saída de
  `select radar.painel_json();`). Seções novas: programas para você, grátis, biblioteca de modelos com
  filtros, provedores, quem faz o quê, indicadores e histórico de preços; o gráfico ganhou "todos com nota".
- **Como tirar o `dados.json` do banco nesta nuvem**: a rede do contêiner não alcança o Supabase. O
  `execute_sql` com `select radar.painel_json();` estoura o limite de saída e o Claude Code grava o
  resultado num arquivo em `tool-results/`; dali um script extrai o JSON. Não colar o JSON na conversa.

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
2. ~~`radar.painel_json()` versão 2 e página versão 2~~. Feitas e publicadas em 2026-10-02.
   Para atualizar os dados: gerar o `dados.json` de novo e republicar no mesmo endereço (exige
   autorização do Guilherme).
3. **Próximo (do assistente, com o Guilherme no computador dele):** medir o consumo de cada recurso (ccusage, `/status` do Codex, `/usage` do Antigravity, API de
   custos da OpenAI), gravar em `radar.leituras` e montar a previsão de esgotamento.
4. Escrever a skill do radar e só então a tarefa agendada, seguindo a seção "Manutenção" do roteiro.

## Armadilhas do ambiente

- **A nuvem do Claude Code não alcança o Supabase nem o OpenRouter** (o proxy recusa a conexão). Para
  tirar o `dados.json`: rodar `select radar.painel_json();` pelo `execute_sql`; a saída estoura o limite,
  vai para um arquivo em `~/.claude/projects/.../tool-results/` e um script extrai o JSON de dentro do
  bloco `<untrusted-data-…>`. Nunca colar o JSON na conversa (são ~200 mil tokens).
- O script diário de preços (OpenRouter) não roda nesta nuvem sem liberar a rede do ambiente.
- `delete` pela ferramenta do Supabase expira; apagar pelo painel do Supabase.
- Ao testar a página localmente, o arquivo não tem `<meta charset>` (o artefato põe na publicação):
  envolver com um cabeçalho de teste, senão os acentos e as expressões regulares quebram.
- Republicar: `Artifact` com o `url` da página, `file_path` no `painel.html` e `files: {"dados.json": …}`.
  Autorização do Guilherme a cada vez.

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
> e os itens de "Situar-se". Quero continuar por: medir o consumo dos recursos e montar a previsão de esgotamento.
