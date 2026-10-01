# Relatório da coleta — grupo `inferencia` (sessão 4)

Coleta de 2026-10-01. Provedores: openrouter, groq, cerebras, together, huggingface, cloudflare,
nvidia, github. Os 8 arquivos passam em `radar/validar.py`.

## Limitação que vale para o grupo inteiro

A política de rede do container bloqueou o WebFetch e o curl em todos os domínios consultados
(openrouter.ai, groq.com, cerebras.ai, huggingface.co, artificialanalysis.ai, docs.github.com,
build.nvidia.com etc.). **Toda a coleta veio de trechos do WebSearch**, restrito sempre que possível
ao domínio oficial; o `fonte_url` aponta para a página oficial de onde veio o trecho. Consequências:

- Valores que apareceram numa única busca não tiveram segunda confirmação (cada arquivo diz quais).
- O OpenRouter (`/api/v1/models/<id>/endpoints`) não pôde ser usado como segunda fonte de preço.
- Notas da Artificial Analysis e da LMArena saíram só quando havia valor literal num trecho; na
  maioria dos provedores não há nota, e as poucas que entraram trazem divergências anotadas.
- Os endereços de canais (X, Discord, status) não foram abertos para conferência.

**Recomendação:** antes de importar no Supabase, refazer a conferência dos preços numa sessão com
acesso de rede aos domínios dos provedores (ou liberar esses domínios no ambiente).

## huggingface
- Validador: OK. Canais 12, planos 7, modelos 2 (SmolLM3-3B, SmolVLM2-2.2B, preço null), capacidades 7, grátis 5, programas 2, indicadores 0.
- Sem dado: preço anual de PRO/Team (não apareceu nas buscas); data de lançamento do SmolLM3 e do SmolVLM2 (sem fonte oficial com dia); contexto do SmolLM3 (fonte diz só "128k" via YaRN, sem número exato); tabelas de hardware incompletas (H100 e instâncias Azure/GCP ausentes nos trechos); tabelas por hora vieram de um único trecho de busca.
- A conferir: plano mínimo do HF Jobs (marcado PRO, não literal); contradição entre página de preços (Spaces Gradio/Docker pagos?) e item "Spaces grátis"; desconto de PRO para estudante e programa ZeroGPU para pesquisa não encontrados; @ do X, status, YouTube e Discord não abertos.

## openrouter
- Validador: OK. Canais 9, planos 4 (Free, Standard, Business, Enterprise; taxa de 5,5% / 8% na compra de créditos; BYOK sem taxa até US$ 25.000/mês), modelos 11 (6 rotas próprias + 5 gratuitos `:free`), capacidades 3, grátis 3 (20 req/min; 50 req/dia sem créditos, 1.000/dia após US$ 10), programas 1 (Startup Program, elegível "nao"), indicadores 0.
- Sem dado: catálogo completo não transcrito (fica na API /api/v1/models); notas AA/LMArena não incluídas (roteadores não são avaliados; as notas dos modelos de origem cabem às coletas dos laboratórios); contexto de auto-beta, free, pareto-code e fusion; Owl Alpha (stealth) sem preço nem criador; datas de lançamento de 4 dos 5 modelos `:free`; qwen/qwen3-coder:free não confirmado; nenhum indicador de custo-benefício publicado encontrado.
- A conferir: endereços de status, Discord e GitHub (vieram de busca geral). Divergência registrada: o anúncio de out/2025 dava 1 milhão de requisições BYOK grátis por mês; a regra atual é por custo. OpenRouter anunciou em 2026-08-19 a entrada na Stripe.

## cloudflare
- Validador: OK. Canais 11, planos 2 (Workers Free US$ 0 e Workers Paid US$ 5/mês; 10.000 neurons/dia grátis; US$ 0,011 por mil neurons acima disso; Kimi K2.6, Kimi K2.7 Code e GLM-5.2 exigem Paid desde 2026-07-28), modelos 40 (20 texto/multimodal, 6 embeddings, 1 rerank, 4 STT, 4 TTS, 5 imagem), capacidades 8, grátis 6, programas 3 (todos "nao"), indicadores 1 (preço do neuron).
- Sem dado: catálogo não completo (variantes antigas, classificação e tradução ficaram de fora); EmbeddingGemma 300M sem preço; contexto só do gpt-oss-120b (os outros null; GLM-5.3 anuncia "1M" sem número literal); todas as datas de lançamento null; `pesos_abertos` null nos modelos mais novos (Qwen3.8, Gemma 4, GLM-5.3, Kimi); nenhuma nota de benchmark (AA e LMArena inacessíveis sem WebFetch); valor do código BOOTSTRAPPED (startups) não encontrado.
- A conferir: preços redondos sem segunda busca (GLM-5.3 1,40/4,40; Gemma 4 26B 0,10/0,30); handles do X de Matthew Prince e Rita Kozlov, página de status e Discord.

## nvidia
- Validador: OK. Canais 13, planos 4 (Developer Program grátis; AI Enterprise US$ 4.500 por GPU/ano; EDU/Inception US$ 1.125 por GPU/ano; nuvem US$ 1 por hora/GPU — os pagos vêm do Licensing Guide, confirmados em duas buscas), modelos 16 (todos com preço null: o build.nvidia.com é teste grátis sem preço por token), capacidades 5, grátis 3, programas 5 (Developer Program "sim"; Academic Grant "nao", só docente e estava fechado; Graduate Fellowship "nao", doutorado; Inception "nao"; DLI Teaching Kit "talvez", via orientador), indicadores 0.
- Notas: aa_index só para Nemotron 3 Ultra (47,7) e Super (36,0), do artigo de lançamento do Ultra na Artificial Analysis; `medido_em` = data desse lançamento.
- Sem dado: limite do teste grátis (~40 RPM e o fim dos 1.000 créditos aparecem só no fórum → `a_verificar`); aa_index divergente nas páginas de modelo da AA (Super e Lightning com 13, Lightning também 24 — provável nova versão do índice), por isso Lightning e Nano ficaram sem nota; nenhum valor literal de MTEB, WER ou Elo de TTS; datas de lançamento de embeddings/rerank, Parakeet, Canary, Magpie Zeroshot/Flow e Cosmos 3; contexto do Ultra e do Omni; `pesos_abertos` do Magpie; OpenRouter não usado como segunda fonte (bloqueado); preços multi-ano e perpétuos do AI Enterprise só em observações (busca única).
- A conferir: @ctnzr, YouTube; convite do Discord não encontrado; Jensen Huang sem conta pessoal ativa conhecida no X.

## groq
- Validador: OK. Canais 10, planos 6 (Free, Developer, Enterprise, Batch com 50% de desconto, Flex, cache com 50%), modelos 16 (4 ativos: gpt-oss-120b, gpt-oss-20b, Whisper v3 US$ 0,111/h, Whisper v3 Turbo US$ 0,04/h; 9 restritos: preview e só Enterprise; 3 desativados: qwen3.6-27b em 2026-09-14, groq/compound e compound-mini em 2026-09-21), capacidades 6, grátis 1 (`a_verificar`), programas 1 (Groq for Startups, "nao"), indicadores 2 (velocidade AA: 471,3 t/s no gpt-oss-120b high; 942,0 t/s no gpt-oss-20b high).
- Mudanças de 2026: Compound desativado (busca web passou à ferramenta browser search dos gpt-oss); Llama saiu do Free/Developer em 2026-08-16 (só Enterprise); CEO atual é Adam Winter (Jonathan Ross foi para a Nvidia em dez/2025), por isso não há `x_ceo`.
- Sem dado: preços sob consulta (Llama Enterprise, MiniMax M2.7); cache do qwen3.8-27b (só "50% de desconto", sem valor literal); preço de browser search e code execution; números exatos dos limites do Free (trechos confusos); datas de lançamento; contexto do Whisper, do Prompt Guard 22M e do Orpheus árabe; aa_index (a AA se contradizia: high 12, low 15). Orpheus em US$ por 1M de caracteres (unidade "outro"), sem conversão.
- A conferir: X do novo CEO, Discord, endereços do X oficial e do GitHub.

## together
- Validador: OK. Canais 10, planos 6 (serverless, Batch com 50% de desconto, endpoints dedicados H100 US$ 5,49/h e B200 US$ 8,99/h, GPU clusters, fine-tuning, Code Interpreter US$ 0,03/sessão), modelos 33 (16 texto/multimodal, 8 imagem, 4 vídeo, 2 STT, 1 TTS, 1 embedding, 1 rerank), capacidades 11, grátis 2 (sem crédito no cadastro; compra mínima US$ 5; Llama 3.3 70B Free `a_verificar`), programas 2 (Startup Accelerator "nao"; Research Credits por convite "talvez"), indicadores 0.
- Sem dado: não é o catálogo completo; vários preços vieram de uma única busca (marcados em `divergencia`/`condicao`); Qwen3.8-2.4T-A95B sem preço (três buscas, três preços diferentes); contexto e data de lançamento null na maioria; H200 dedicado sob consulta; Veo 2.0 sem unidade clara (omitido); embeddings/rerank marcados `restrito` (doc diz só endpoint dedicado, páginas de modelo mostram preço por token); só uma nota (aa_index 50 do DeepSeek V4 Flash 0731, tirada de título de artigo; outra página da AA mostra 34, anotado); Kimi K3 com valores AA inconsistentes (44, 57, 60), não incluído; OpenRouter não usado como segunda fonte.
- A conferir: handle de Ce Zhang (de menção em post oficial); Discord aponta para a página de suporte, sem convite.

## github
- Validador: OK. Canais 7, planos 7 (Free US$ 0; Student US$ 0 com 200 AI Credits/mês; Pro US$ 10; Pro+ US$ 39; Max US$ 100; Business US$ 19/usuário; Enterprise US$ 39/usuário), modelos 33 (`github/*`, preço por MTok da página "Models and pricing"; 11 com desativação anunciada para 2026-10-02 ou 2026-10-19), capacidades 3, grátis 2, programas 3 (Copilot Student "sim" para o Guilherme), indicadores 0.
- Mudanças de 2026 que afetam o roteiro: desde 2026-06-01 o Copilot cobra em GitHub AI Credits (1 crédito = US$ 0,01) por token, e premium requests/multiplicadores viraram legado; o GitHub Models foi fechado a novos clientes em 2026-06-16 e encerrado em 2026-07-30 (valores antigos só como histórico em observações); o Copilot Pro grátis para estudante virou o plano Copilot Student (desde 2026-03-12), e desde 2026-06-24 Free e Student só usam escolha automática de modelo.
- Sem dado: cota de créditos do Free; preço de 8 modelos (GPT-5.4, 5.4 mini, 5.4 nano, 5.3-Codex, 6.1 Sol, Kimi K3, Grok 4.5, Grok 4.6); janela de contexto de todos os modelos; plano mínimo do cloud agent; capacidades MCP e agente agendado (o subagente esgotou o limite de 200 buscas da sessão); notas de benchmark; x_ceo e x_lider (liderança pós-Dohmke não confirmada); preço anual null (planos anuais aposentados, segundo discussões da comunidade — a verificar).
- A conferir: divergência em nomes de modelo (Sonnet 5 × 5.5) e no preço do GPT-6 Astra; vários valores sem segunda confirmação.
