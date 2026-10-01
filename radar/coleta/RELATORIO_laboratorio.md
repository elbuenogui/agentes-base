# Relatório da coleta — grupo `laboratorio` (sessão 1)

Coletado em 2026-10-01. Provedores: anthropic, openai, google, xai, meta, microsoft. Os seis arquivos
passaram em `radar/validar.py`.

## Limitação geral: proxy de saída da sessão na nuvem

O proxy da sessão bloqueou (EGRESS_BLOCKED) **openrouter.ai, artificialanalysis.ai, lmarena.ai/arena.ai,
x.com, huggingface.co e wikipedia**, além de boa parte dos domínios oficiais dos próprios provedores
(detalhes em cada seção). Consequências que valem para todos os arquivos:

- **Segunda fonte de preço:** o OpenRouter não pôde ser consultado. Onde houve conferência, ela usou o
  JSON de preços do LiteLLM (raw.githubusercontent.com/BerriAI/litellm), que é agregador.
- **Notas e indicadores:** quase todas as notas da Artificial Analysis e do LMArena foram lidas em
  trechos de busca ou em matérias de terceiros, não na página do leaderboard. Cada nota diz isso na sua
  `observacao`. Vale reconferir antes de publicar no painel.
- **Canais do X:** registrados sem leitura do X.

Só platform.claude.com (Anthropic), cloud.google.com (Google) e o GitHub (Microsoft, via fonte da
documentação) foram lidos diretamente como fonte oficial ampla. **OpenAI e Meta não tiveram nenhuma
página oficial lida diretamente**: os preços vieram de trechos de busca e do LiteLLM.


## Anthropic (`anthropic.json`)

Contagens: 19 canais, 10 planos, 20 modelos (4 ativos, 3 restritos Mythos, 8 legados, Sonnet 4.5 com desativação em 2026-11-30, 4 desativados na API própria), 10 capacidades, 5 grátis, 5 programas, 3 indicadores.

- **Notas:** artificialanalysis.ai, lmarena.ai, openrouter.ai e outros bloqueados no proxy. Só aa_index de Opus 5.5 (58) e Sonnet 5.5 (56), max effort, de resultados de busca que citam a AA (marcado como agregador). O índice AA foi recalibrado em set/2026, então notas antigas não entraram. Nenhuma nota LMArena (só agregadores, sem o Opus 5.5).
- **Indicadores:** custo para rodar o índice AA (Opus 5.5 max, Opus 5, Fable 5.1 max) vêm de terceiro — a verificar.
- **Modelos desativados:** lançamento e contexto de Opus 4.1, Opus 4, Sonnet 4 e Haiku 3.5 ficaram null.
- **Mythos:** contexto null nos três; Mythos Preview sem preço nem data de lançamento (depreciado, retirada "a anunciar").
- **AI for Science:** post de 2026-08-27 diz até US$ 50 mil por projeto; central de ajuda ainda diz até US$ 20 mil por 6 meses. Registrado o do post, divergência anotada.
- **Max 20x:** página de preços só mostra "From $100"; US$ 200 vem da central de ajuda oficial.
- **Anual de Team/Enterprise:** null (página só dá valor por assento/mês no anual; descrito em `limites`).
- **Limites diários das routines:** números por dia citados em busca não aparecem na doc atual; só limites por hora registrados.
- **Créditos grátis da API:** oficial diz "uma pequena quantia"; US$ 5 só em agregadores.
- **Claude for Open Source:** status desconhecido (prazo e mudança de critérios vêm de terceiros).
- **Outros tipos:** a Anthropic não tem modelos próprios de imagem, vídeo, voz ou embeddings.

## OpenAI (`openai.json`)

Contagens: 23 canais, 10 planos, 76 modelos, 15 capacidades, 5 grátis, 7 programas, 2 indicadores.

**Atenção: nenhuma página oficial da OpenAI foi lida.** O proxy bloqueou platform.openai.com, developers.openai.com, openai.com, help, community e openai.smapply.org (além de artificialanalysis.ai, openrouter.ai e wikipedia). Reconferir tudo na página oficial antes de importar.

- **Preços de API:** do JSON de preços do LiteLLM (raw.githubusercontent.com, agregador), conferidos contra trechos de busca que citam a página oficial; o resultado de cada conferência está em `preco.divergencia`.
- **GPT-5.6 Sol diverge:** LiteLLM US$ 4/20 × buscas que citam a oficial US$ 5/30. Registrado 5/30.
- **Contexto dos GPT-6 e 5.6:** LiteLLM 922.000 tokens de entrada × imprensa 1.050.000 total. Registrado o do LiteLLM.
- **Notas aa_index:** só quatro, de trechos de busca (GPT-6 Astra 53, GPT-6.1 Sol 52, GPT-6 Luna 37, GPT-5.6 Sol 47, variante max). GPT-5.5 fora por valores inconsistentes. Sem Elo LMArena; sem notas de imagem, voz e embeddings.
- **Indicadores:** custo para rodar o índice AA (GPT-6.1 Sol, GPT-6 Astra) via orcarouter.ai — terceiro.
- **Datas de lançamento** null em vários modelos (GPT-5.5, 5.4, 5.2, GPT Image 2/2.5, Realtime 2.x etc.).
- **Planos do ChatGPT:** preços de terceiros; Enterprise e Edu sob consulta. Plus no Brasil ≈ R$ 100/mês (não convertido).
- **Free tier da API:** fontes contraditórias (tokens diários por compartilhamento de dados × crédito de teste de US$ 15 desde 2026-05-13). Todos os itens de `gratis` estão `a_verificar`.
- **Omitidos por já desligados:** os de 2026-07-23 (computer-use-preview, Codex 5.x, deep-research etc.) e 2026-08-10 (chat-latest 5.2/5.3); também os aliases daybreak-* e chat-latest. Sora 2 / 2 Pro entram como desativados (API desligada em 2026-09-24).
- **Status por julgamento, sem confirmação oficial:** `legado` para gpt-4.1, gpt-4o, o3, tts-1; `restrito` para Cyber e Rosalind.
- **Canais x_lider** (@gdb, @kevinweil, @nickaturley, @markchen90, @merettm, @embirico) vieram de memória, sem consulta ao X — conferir.

## Google (`google.json`)

Contagens: 20 canais, 7 planos, 47 modelos, 17 capacidades, 10 grátis, 9 programas, 4 indicadores.

- **Proxy bloqueou a maior parte do Google:** ai.google.dev, gemini.google, blog.google, deepmind.google, docs.cloud.google.com, support.google.com, jules.google, antigravity.google, notebooklm.google, além de artificialanalysis.ai, openrouter.ai e x.com. cloud.google.com e raw.githubusercontent.com abriram.
- **Preços da API:** todos da página oficial do Gemini Enterprise Agent Platform (antigo Vertex AI) em cloud.google.com, endpoint global, camada Standard. Não conferidos contra a Gemini Developer API nem contra o OpenRouter.
- **Gemini 3 Flash Preview:** preço de saída padrão falta na tabela oficial; ficou null (agregadores citam US$ 3,00/MTok).
- **Preços promocionais:** 3.6/3.7/3.8 Flash e TTS 3.8 têm preço introdutório até 2026-12-31, dobrando em 2027-01-01 (anotado em `divergencia`).
- **Planos** (US$ 4,99 / 19,99 / 99,99 / 199,99): de terceiros (gemini.google bloqueado). Preço no Brasil (R$ 24,99 e R$ 96,99) em `observacoes`.
- **Camada gratuita da Gemini API:** sem tabela oficial acessível; números de terceiros como `a_verificar`. Também `a_verificar`: limites grátis de Jules e Antigravity, licença do Gemma 4, Gemini/NotebookLM no Workspace for Education, oferta de estudante.
- **Datas de lançamento** null para 3.1 Pro preview, 3 Flash preview, Nano Banana 2/Pro, Veo 3.1/Fast, Lyria 3 e Omni Flash; as preenchidas vêm de resumos de busca.
- **Contexto** só onde a busca trouxe o número (1.048.576 para 3.5, 3.7 e 3.8 Flash).
- **Notas:** valores AA (aa_index, TTS, vídeo, imagem) lidos em resumos de busca; lmarena_elo do 3.1 Pro de agregador (swfte); sem nota para 3.6/3.7 Flash, Flash-Lite e Veo 3.1. MTEB do gemini-embedding-001 (68,32) do relatório técnico no arXiv.
- **Status:** Imagen 4 e Veo 2/3 desligados na Gemini API mas com preço no Vertex → `legado`; Gemini 2.5 Pro/Flash/Flash-Lite `legado` (data de desligamento anunciada e depois removida); desligamento do 2.5 Flash Image em 2026-10-02 vem de terceiro; Gemini 3.5 Pro anunciado e adiado, não entrou; 3.8 Flash Cyber `restrito`.
- **Ids:** confirmados por busca para 3.8 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3.1 Pro preview e 3.5 Transcribe; os demais são slugs aproximados.
- **Indicadores:** custo por tarefa do índice AA (3.8 Flash, 3.7 Flash) lido na busca; preço por minuto do Gemini 3.5 Transcribe é oficial.
- **Programas:** Google Cloud Research Credits só via orientador; Google.org AI for Science fechado em 2026-04-17.

## xAI (`xai.json`)

Contagens: 11 canais, 9 planos, 24 modelos (5 desativados em 2026-05-15; Imagine Image Quality com desativação em 2026-11-02), 12 capacidades, 4 grátis, 0 programas, 1 indicador.

- **Bloqueios no proxy:** docs.x.ai, x.ai, artificialanalysis.ai, x.com, openrouter.ai, pricepertoken, models.dev, aipricing.guru. Preços oficiais vieram de trechos de busca restritos a docs.x.ai/x.ai, conferidos com o JSON do LiteLLM (raw.githubusercontent.com) no lugar do OpenRouter. Notas AA/LMArena vieram de trechos de busca ou matérias de terceiros (dito na `observacao`).
- **Preços só do LiteLLM (a verificar):** Grok 4.6, 4.5, Grok Build 0.1; Imagine Image Pro; Video 1.5 Preview; imagem de entrada do Video 1.5; Transcribe 1.0; faixa >200k do 4.3 e 4.20; desconto de batch.
- **Divergências oficial × LiteLLM:** imagine-image-quality (0,07 em 2K × 0,05); imagine-image-2.0 (0,04–0,08 × 0,06).
- **Planos de agregador:** SuperGrok Lite, SuperGrok Business, X Premium+; anuais do SuperGrok não confirmados.
- **Datas de lançamento:** só as com anúncio oficial (4.5, 4.6, 4.7); 4.3 ficou null.
- **Notas faltando:** Grok Build 0.1 (duas notas AA conflitantes, 27 e 41 — nenhuma registrada); Elo LMArena do Grok 4.7; Elo de TTS/STT.
- **Id do TTS não confirmado** (`xai/grok-tts`, com aviso).
- **Sem embeddings** na API (só Collections/file_search).
- **Programas:** nenhum programa público para estudante/pesquisador/startup.
- **Créditos grátis (a_verificar):** US$ 25 no cadastro; até US$ 150/mês por compartilhamento de dados; até 20% do gasto na API do X de volta.
- **x_lider:** nenhum registrado (sem ler o X não deu para confirmar).
- **Marca:** em 2026 aparece como "SpaceXAI"; o @xai pode ter virado @SpaceXAI.

## Meta (`meta.json`)

Contagens: 14 canais, 9 planos, 14 modelos, 10 capacidades, 6 grátis, 4 programas, 2 indicadores.

**Quase nenhuma página foi lida diretamente:** o proxy bloqueou ai.meta.com, llama.com, llama.developer.meta.com, dev.meta.ai, developer.meta.com, about.fb.com, meta.com, huggingface.co, artificialanalysis.ai e wikipedia. Os valores vieram de trechos do WebSearch filtrado por domínio oficial; `fonte_url` aponta para a página oficial citada no trecho.

- **Mudança de contexto:** a Llama API foi desativada em 2026-07-06; a Meta passou a vender a família Muse (fechada) pela Meta Model API, lançada em 2026-07-09.
- **Llama sem preço:** a Meta não hospeda mais Llama; preço null (preços de terceiros citados em `observacoes`). Llama 4 Maverick/Scout, 3.3, 3.2, 3.2 Vision e 3.1 marcados como legado.
- **OpenRouter:** conferência impossível (bloqueado).
- **Notas AA divergentes:** trechos misturam versões do índice (Muse Spark 1.3 max: 62 no lançamento × 48 hoje). Registrado só o 48. Custo por tarefa também diverge (US$ 1,37 na página × US$ 0,55 no post do X).
- **LMArena:** notas de agregador (HelloGitHub), não da arena.ai. Sem notas de imagem, voz e vídeo.
- **Créditos de US$ 20 da Meta Model API:** só confirmados por terceiros (`a_verificar`).
- **Brasil na Meta Model API:** não confirmado ("expanded global access" sem lista de países).
- **Datas faltando:** chegada de Muse Image e SAM 3.1 à API.
- **Muse Video:** só preview, sem API e sem preço (restrito). Pesos do Muse Spark 1.2 prometidos, ainda não saíram. Muse Spark original (abr/2026) só no app, não entrou.
- **Programas:** nenhuma bolsa acadêmica/estudante ativa. Llama Impact Grants e Llama Startup Program fechados. Único elegível: Meta Global AI Developer Hackathon (inscrições ainda por abrir).
- **Meta One:** sem preço anual; plano de US$ 7,99 aparece como "Plus" (teste) e "Core" (lançamento) — registrado "Core".
- **Cargo do Nat Friedman** não reconferido.
- **Modelos abertos de mídia sem API** (Seamless, Audiobox, DINOv3, V-JEPA 2, SAM Audio, Omnilingual ASR) não viraram modelos; SAM 3 e Omnilingual ASR estão em `gratis`, os demais em `observacoes`. Movie Gen nunca teve pesos abertos.

## Microsoft (`microsoft.json`)

Contagens: 17 canais, 11 planos, 23 modelos (MAI + Phi), 13 capacidades, 6 grátis, 5 programas, 1 indicador.

- **Bloqueados no proxy:** azure.microsoft.com, learn.microsoft.com, techcommunity.microsoft.com, microsoft.ai, prices.azure.com, huggingface.co, openrouter.ai, artificialanalysis.ai. Lista de modelos, contexto, status e datas de desativação lidos direto na fonte da documentação no GitHub (MicrosoftDocs/azure-ai-docs, commit de 2026-10-01), citando a URL canônica do learn.microsoft.com.
- **Preços dos MAI:** de trechos de busca das páginas oficiais (blogs da Microsoft), não da página de preços — conferir quando o domínio abrir.
- **Sem preço oficial:** MAI-Voice-2.1 e 2.1-Flash (preços achados são do Voice-2/2-Flash, marcados como legado sem confirmar status), MAI-Transcribe-2-Streaming, Phi-4-reasoning, Phi-4-mini-reasoning, Phi-4-reasoning-vision-15B.
- **Preços dos Phi:** do anúncio oficial de mar/2025, podem estar desatualizados; agregadores divergem (anotado em `divergencia`).
- **Notas:** sem aa_index nem lmarena_elo do MAI-Thinking-1. As três notas incluídas são de terceiros: lmarena_image_elo 1331 do MAI-Image-2.6 (Neowin), aa_stt_wer 2,0 do MAI-Transcribe-2 (post da AA no X), aa_tts_elo 1187 do MAI-Voice-2 (página do OpenRouter via busca).
- **Datas de lançamento de terceiros:** MAI-Transcribe-2, MAI-Voice-2-Flash, Phi-4-reasoning-vision-15B.
- **Outros sem dado:** preços padrão do Azure Speech (STT/TTS não-MAI); promoção de US$ 18 do Copilot Business só em terceiros; nenhum valor de crédito publicado para AFMR nem AARI.
- **Nota prática:** MAI-Thinking-1 vem com cota padrão de 0 TPM (pedir aumento); MAI Playground só nos EUA; não confirmado se a camada F0 cobre os MAI. MAI-Image-2.5 / 2.5-Flash / 2.5-Pro têm desativação marcada para 2026-10-01.
