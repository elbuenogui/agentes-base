# Relatório da coleta — grupo `busca_embeddings` (sessão 5)

Coletado em 2026-10-01. Provedores: `perplexity`, `tavily`, `voyage`, `cohere`. Os quatro arquivos
passaram em `radar/validar.py`.

## Ressalva que vale para o grupo todo

O proxy de saída da sessão na nuvem **bloqueou os sites oficiais dos quatro provedores** (perplexity.ai,
docs.perplexity.ai, tavily.com, docs.tavily.com, voyageai.com, docs.voyageai.com, mongodb.com,
cohere.com, docs.cohere.com) e também openrouter.ai, artificialanalysis.ai, huggingface.co e
web.archive.org. O github.com abriu.

Consequências:

- A maior parte dos números veio do **WebSearch restrito ao domínio oficial**: trechos da página oficial
  resumidos pelo buscador, não a leitura literal da página. O `fonte_url` aponta para a página oficial,
  mas **o valor precisa ser reconferido** quando houver acesso.
- **Cohere** é a exceção parcial: as docs oficiais foram lidas literalmente a partir do repositório-fonte
  (`github.com/cohere-ai/cohere-developer-experience`, commit de 2026-09-30). Isso cobre modelos,
  changelog, deprecações, limites de taxa e preços do Model Vault. A página `cohere.com/pricing`, porém,
  não abriu.
- **Tavily**: parte dos custos em créditos foi conferida no GitHub oficial (`tavily-ai/skills`).
- **Segunda fonte (OpenRouter)**: não houve conferência em nenhum dos quatro. Na Cohere, as divergências
  foram anotadas contra a tabela do LiteLLM.
- **Notas de benchmark e indicadores**: quase todos ficaram de fora, porque o MTEB (Hugging Face) e a
  Artificial Analysis estavam bloqueados.

## Perplexity

- **Mudança de produto**: a API Sonar Chat Completions perdeu o suporte em 2026-09-27 e passou para a
  Agent API.
  - Sonar Pro, Sonar Reasoning Pro e Sonar Deep Research ficaram como `legado`, com os preços antigos.
  - `sonar` segue `ativo` com preço novo. O preço antigo está registrado em `divergencia`.
  - `sonar-reasoning` está `desativado` desde 2025-12-15.
- **Contexto**: `null` em todos os modelos.
  - A doc diz "128K", e o valor não foi arredondado para tokens.
  - Sonar Pro: só agregadores citam o contexto (200K/205K).
  - pplx-embed: só terceiros citam o contexto (32K).
- **Data de lançamento dos Sonar**: não confirmada.
- **Notas**: nenhuma.
  - AA Index do Sonar Pro: os valores divergem (8 vs 9,27) e a fonte primária estava bloqueada.
  - Search Arena: não equivale a `lmarena_elo`.
  - pplx-embed: o valor publicado é nDCG@10, não a média do MTEB.
- **Planos**:
  - Não encontrados os créditos do Computer no plano Pro nem o preço anual do Education Pro.
  - O limite do Free (3 Pro Searches/dia) veio só de resumo de busca.
- **Programas**:
  - Créditos de API para estudantes: não registrados, porque a central de ajuda oficial diz que não há.
  - Perplexity for Startups: veio só de agregador (status `desconhecido`).
- **Modelos de terceiros revendidos na Agent API**: não listados (pertencem aos laboratórios). Os
  openai/gpt-5.x saem da Agent API e da Router API em 2026-10-24 (ver `observacoes`).
- **Canais**: @ do CTO e convite do Discord não conferidos em página oficial.

## Tavily

- **Modelos**: lista vazia de propósito. A Tavily vende APIs de busca cobradas em créditos, não modelos.
  O modo mini/pro da Research API entrou em capacidades.
- **Preço anual**: `null` em todos os planos. Só agregadores citam desconto anual, com nomes de plano
  desatualizados.
- **Plano Project**: um agregador diz que passou de US$ 12,35 para US$ 30 em 2026-09-02. Registrado
  US$ 30, com a divergência anotada como não confirmada.
- **Pay as you go e Enterprise**: `preco_mensal_usd` `null`. O pay as you go é cobrado por uso
  (US$ 0,008/crédito) e o Enterprise é sob consulta.
- **Programas**: `valor_usd` `null`, porque o benefício é em meses e créditos.
  - Estudante: elegível (e-mail USP), mas o texto veio de busca.
  - Startups: não elegível, porque exige VC.
- **Indicador do plano Growth**: US$ 0,005/crédito, só pelo blog da Firecrawl (concorrente), marcado
  como a verificar.
- **Contexto**: a Nebius anunciou a compra da Tavily em fevereiro de 2026, com fechamento previsto para
  o 2º semestre de 2026.

## Voyage AI

- Aquisição pela MongoDB (2025-02-24, US$ 220 mi) confirmada por imprensa.
- **MTEB (`mteb_media`)**: omitido em todos os modelos. O Hugging Face estava bloqueado, e a MongoDB
  só diz que os modelos "lideram o RTEB", sem número.
- **Contexto `null`**:
  - voyage-context-3, voyage-3 e voyage-code-2 (no code-2 a busca deu valor conflitante).
  - voyage-context-4: registrado 32K por chunk; os 120K por documento não foram confirmados.
- **Preços**:
  - rerank-2-lite: `null`.
  - voyage-3-lite e voyage-multilingual-2: fora do arquivo, sem preço achado.
  - voyage-4-nano: uso local, sem preço de API.
- **Datas**: lançamento do voyage-multimodal-3 e do voyage-code-2 sem data.
- **Desativações**: nenhuma com data anunciada. voyage-2 e voyage-large-2 só têm recomendação de migrar.
- **Planos e limites**: não há plano mensal, só pay-as-you-go. Os limites de taxa sem forma de pagamento
  não foram confirmados.
- **Programas**: o "até US$ 5.000" do MongoDB for Startups veio só de busca (`valor_usd` `null`).
- **rerank-2.5**: mantido `ativo`. O rerank-3 saiu em 2026-09-30 e não há anúncio de legado.
- **Indicadores**: nenhum publicado encontrado.

## Cohere

- **Preços oficiais lidos literalmente**: só os de Command R e R+ 08-2024 (changelog). Os demais estão
  marcados `a_verificar`:
  - Command A e Embed 4: busca restrita a cohere.com, conferida com o LiteLLM.
  - Embed 5: só resumo de busca.
  - Command R7B, Aya Expanse, Embed v3 e Rerank: só LiteLLM.
- **Sem preço por token**:
  - Command A+, A Reasoning, A Vision e A Translate (produção via vendas).
  - North Mini Code, North Small Translate, Tiny Aya e Aya Vision 32B.
  - Transcribe e Parse: só o preço por instância-hora do Model Vault.
  - Embed Multilingual Light v3: o LiteLLM traz US$ 100/M, valor claramente errado, por isso não
    registrado.
- **Notas**:
  - `aa_index` só do Command A+ (37, post da AA no X). Há divergência com o valor 13 citado em resumo.
  - `lmarena_elo` e `mteb_media`: fora, sem valor literal.
- **Licenças**: a CC-BY-NC da família Command não foi reconferida no Hugging Face. Os modelos estão
  marcados `pesos_abertos=true`, com nota.
- **Datas**: Tiny Aya, Aya Expanse 32B, Embed v3 e Rerank v3 sem data oficial de lançamento.
- **Programas**:
  - Catalyst Grants: sem valor publicado (`talvez`).
  - Scholars: status `em_breve`, veio de resumo de busca.
  - Startups: parece ter sido retirado (`desconhecido`).
- **Canais**: handle da Joelle Pineau não conferido.
- **Indicadores**: nenhum (Artificial Analysis bloqueada).

## Próximo passo sugerido

Rodar uma reconferência a partir de uma máquina sem o bloqueio do proxy (ou liberar esses domínios na
política de rede do ambiente): abrir as páginas de preço oficiais e o OpenRouter e trocar os valores
"de busca" por leitura literal.
