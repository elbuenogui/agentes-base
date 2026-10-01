# Relatório da coleta — laboratório, sessão 2 (2026-10-01)

Provedores: mistral, deepseek, qwen, moonshot, zai, amazon, typesafe. Os 7 arquivos passam em
`radar/validar.py`.

## Limitações que valem para o grupo todo

- **Rede restrita.** A política de rede do ambiente bloqueou WebFetch e curl para todos os domínios
  oficiais testados (mistral.ai, docs.mistral.ai, api-docs.deepseek.com, aws.amazon.com,
  alibabacloud.com, docs.z.ai, docs.typesafe.ai) e também para openrouter.ai, artificialanalysis.ai
  e huggingface.co. **Nenhuma página foi lida diretamente.** Todos os números saíram de trechos do
  WebSearch restrito (`allowed_domains`) aos domínios oficiais. Um número só entrou quando a busca o
  atribuía a uma página oficial, e é essa URL que está em `fonte_url`.
- **Sem segunda fonte no OpenRouter.** A conferência pedida na regra 2 não foi feita em nenhum
  provedor.
- **Cota de buscas esgotada.** A cota de 200 WebSearch da sessão, compartilhada entre os subagentes,
  acabou no meio da coleta de zai, mistral, amazon, moonshot e qwen. Notas de benchmark, indicadores
  e alguns preços ficaram incompletos.
- **Recomendação.** Repetir a conferência dos números num ambiente com WebFetch liberado para os
  domínios oficiais, para o OpenRouter e para a Artificial Analysis, antes de importar no Supabase.

## Por provedor

### typesafe
- Gratuidade: crédito de US$ 5 no cadastro só em blogs/agregadores (a_verificar); teria sido suspenso após pausa de cadastros em 2026-09-22. Contrato oficial só fala em "créditos promocionais" sem valor.
- Promoção grátis no Vercel AI Gateway até 2026-09-25 (já encerrada; comunidade cita 26/09).
- Não confirmado em página oficial se o cadastro direto está aberto ou com lista de espera.
- Programas: nenhum oficial; só joinsecret.com cita US$ 1.000 via OpenRouter para startups (fonte terceira, em observacoes).
- Notas: não se aplicam (modelo de decisão, fora de AA/LMArena). Tipo "texto" por falta de enum melhor.
- Contexto: 64k (TypeSafe/Vercel) vs 32k (Cloudflare) — divergência registrada. País "EUA" de fontes terceiras.
- WebFetch em docs.typesafe.ai bloqueado.
### deepseek
- WebFetch bloqueado em api-docs.deepseek.com: todos os números vêm de trechos do WebSearch restrito a domínios oficiais.
- deepseek-chat / deepseek-reasoner: changelog indicava desativação em 2026-07-24; sem confirmação se ainda respondem. Registrados como desativados.
- V4-Pro: página lista US$ 1,32/3,96 (pico), mas desde 2026-09-14 as chamadas vão ao V4.1-Flash a preço Flash; ressalva em `divergencia`. Sem nota de benchmark.
- Preços antigos (V4-Flash 0,14/0,28; R1 0,55/2,19) tratados como desatualizados (em observacoes).
- Pesos/licença MIT do V4.1-Flash só em páginas de terceiros → a_verificar.
- Data de aposentadoria do V4-Flash = 2026-09-10 (anúncio do V4.1-Flash), aproximação; DeepSeek-OCR sem data exata.
- Sem valor publicado de crédito para novos usuários; sem programas acadêmicos; CEO sem X conhecido.
- Modelos antigos de pesos abertos (R1, V3.x, Janus, Coder) não listados individualmente.
### zai
- Cota de WebSearch da sessão (200) esgotou no meio da coleta; WebFetch bloqueado em docs.z.ai; OpenRouter bloqueado (sem segunda fonte de preço).
- Preço anual do Coding Plan = null: buscas oficiais divergiram (Lite US$ 151,2 vs 172,80/ano).
- Sem preço para GLM-5V-Turbo e para cache de alguns modelos.
- Embedding-3 só no BigModel em yuan (0,5 CNY/1M tokens), não convertido.
- Datas de lançamento só para GLM-5.3 (2026-08-14) e GLM-5 (2026-02-11), ambas de imprensa; demais null.
- Notas AA de modelos anteriores contraditórias → omitidas; LMArena não obtida.
- Indicador US$ 280 (custo do índice AA, GLM-5.3-Flash) de uma única busca.
- Não coletado por falta de cota: TTS/tempo real, página de status, programas acadêmicos, detalhes do Startups Program, limites dos Flash grátis; z.ai/blog não confirmado.
### mistral
- Cota de WebSearch esgotada no meio; WebFetch bloqueado em mistral.ai — nenhuma página lida diretamente.
- Notas: nenhuma do LMArena; Medium 3.5 na AA omitida (buscas deram 14 numa página e 23–30 em outras); MTEB e STT/TTS não buscados. Sem conferência no OpenRouter.
- Sem contexto/data exata: Ministral 3, Codestral, Voxtral Small, Transcribe 2. Sem preço: Leanstral 1.5, Shieldstral.
- Preço anual em US$: só a regra de 20% de desconto. Limites do tier Experiment só no painel. Plano mínimo dos agentes remotos do Vibe Code não confirmado.
- 7 modelos "legado" sem data de retirada confirmada (deprecação anotada na observação de cada modelo).
- Sem programa formal para startups/pesquisa; página de status não registrada; X e GitHub sem conferência; indicadores não buscados.
- Medium 3: preço do anúncio de lançamento, não da página de preços atual.
- Fato novo: Le Chat virou "Vibe" em 2026-08-12 (modos Work/Code/Chat).
### amazon
- WebFetch bloqueado em aws.amazon.com; cota de WebSearch acabou antes das notas de benchmark e da conferência dos @ do X.
- Notas e indicadores: nenhum (buscas na AA/LMArena não rodaram).
- @awscloud e @ajassy sem conferência; @ de líderes técnicos e do Kiro não registrados.
- Sem preço oficial: Nova 2 Pro e Nova 2 Omni (prévia), Nova Multimodal Embeddings fora do vídeo em lote. Nova 2 Sonic e Nova Premier: preço só de terceiros → null, valor em `divergencia`.
- Região dos preços Bedrock: busca citou US East (Ohio), não us-east-1 — não confirmado se iguais.
- EOL incertos: Nova Lite v1 (fontes: 2026-09-30 vs 2026-10-14; registrado 2026-10-14); Nova Pro v1 (2026-09-30 pode ser só algumas regiões); Nova Micro v1 status não confirmado (deixado ativo).
- Sem data de lançamento: Premier, Sonic v1, Multimodal Embeddings, Titan V2. Titan Multimodal Embeddings G1 fora (sem preço/status). Regras do Earth on AWS não conferidas.
### moonshot
- Cota de WebSearch esgotada; WebFetch bloqueado. Fontes extras usadas: platform.kimi.com (docs/preços em chinês) e forum.moonshot.ai.
- Contexto do K3 e do K2.8 Preview = null (fonte só diz "1M").
- preco_anual_usd = null: fonte só publica o mensal equivalente (no texto do plano).
- Planos em yuan da China (Andante ¥49, Moderato ¥99, Allegretto ¥199, Allegro ¥699) não batem com os planos em US$; tiers "Go"/"Plus" do Kimi Code não mapeados.
- Busca web da API: só ¥0,03/chamada, sem valor em US$.
- Sem programas acadêmicos; X do CEO Yang Zhilin não confirmado; sem página de status.
- lmarena do K2.6 e K2.7 Code não confirmada. aa_index do K3: artigo de lançamento da AA = 57, página atual = 44 (registrado 44).
- Datas de lançamento de Kimi-VL e K2.5 não confirmadas. Preços de modelos desativados não registrados (K2.5 US$ 0,60/3,00 só como histórico); Kimi-Audio e Kimi-Linear não verificados.
- Voucher de ¥15 da API exige celular chinês.
### qwen
- WebFetch bloqueado em alibabacloud.com e cota de WebSearch esgotada. Ficaram sem dado: o novo
  líder do Qwen no X, os preços dos VL dedicados (qwen3-vl-*), o preço de rerank, a nota MTEB dos
  embeddings e as notas de STT/TTS da Artificial Analysis.
- O Qwen Code CLI não tem mais cota grátis. O login grátis via Qwen OAuth acabou em 2026-04-15
  (issue QwenLM/qwen-code#3203), e por isso o item não entrou em `gratis`. O modo headless
  `qwen -p` está marcado "a confirmar".
- Sem x_ceo nem x_lider: Junyang Lin (@JustinLin610) saiu do Qwen em 2026-03-03.
- Preço ficou null em:
  - qwen3.8-max-prime: só achei o preço China/EUA, US$ 3,301/9,902;
  - qwen3.8-27b;
  - qwen3.8-2.4t-a95b;
  - qwen3.7-flash;
  - a faixa 0–32K do qwen3-max;
  - qwen3.8-omni-flash e qwen-audio-3.1-*: os valores encontrados não eram confiáveis.
- Qwen3.7-Plus: US$ 0,4/1,6 pode ser o preço cheio ou o promocional de −20%. A promoção venceu em
  2026-08-31; ver o campo `divergencia`.
- Qwen3.8-Max: Singapura US$ 2/6 (gravado), China/EUA US$ 1,65/4,951, Arena US$ 1,69/5,07.
- O preço do Wan3.0 vem do blog oficial da Alibaba Cloud, não da página de preços.
- As datas de lançamento do Qwen3.8-Flash e do Qwen-Audio-3.1 não foram confirmadas.
- Nenhum indicador de custo-benefício encontrado.
- Qwen3-Coder (pesos abertos) e Qwen3-Embedding entraram sem preço e sem data. O Qwen3-Coder
  aberto está marcado "a verificar".
- O Token Plan está gravado com o preço cheio; a promoção está em `limites`.
