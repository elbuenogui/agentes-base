# Relatório da coleta — grupo `midia` (sessão 3)

Coletado em 2026-10-01. Os sete provedores do grupo têm arquivo em `radar/coleta/` e passaram no
`validar.py`.

| provedor | modelos | planos | notas | programas | canais |
|---|---|---|---|---|---|
| ElevenLabs | 18 | 8 | 0 | 3 | 14 |
| Runway | 9 | 7 | 1 | 6 | 15 |
| Luma AI | 9 | 6 | 2 | 3 | 12 |
| Kling | 22 | 8 | 1 | 3 | 12 |
| Black Forest Labs | 28 | 3 | 6 | 1 | 11 |
| Midjourney | 10 | 4 | 1 | 2 | 8 |
| Suno | 6 | 3 | 3 | 1 | 8 |

Nenhum provedor teve `indicadores` de custo-benefício publicados encontrados.

## Limitação que vale para tudo

A política de rede do ambiente bloqueou o **WebFetch** (EGRESS_BLOCKED) em todos os domínios
testados: sites dos provedores, openrouter.ai, artificialanalysis.ai, docs.bfl.ai e wikipedia.
Toda a coleta foi feita com **WebSearch**, restrito aos domínios oficiais. Nenhum valor foi lido
diretamente na página.

- **Critério para os números:** só entrou número confirmado em duas buscas, ou numa busca restrita ao domínio oficial (marcado na `condicao`/`observacao` quando foi uma só). Divergência virou `null`, com os valores registrados em `observacoes`.
- **Conferência pelo OpenRouter (regra 2):** não foi feita, porque o openrouter.ai estava bloqueado.
- **Benchmarks:** as notas da Artificial Analysis ficaram muito incompletas, porque os resumos de busca davam valores diferentes para o mesmo modelo.
- **Recomendação:** liberar esses domínios no Network access do ambiente e rodar uma conferência com o WebFetch antes de publicar no painel.

## Decisões a confirmar no importador

- **Benchmark de música:** o roteiro não prevê chave para música. Na Suno foram usadas `aa_music_instrumental_elo` e `aa_music_vocals_elo`.
- **Preço por clipe:** a Luma cobra o Ray3.2 por clipe, não por segundo. Foi registrado com unidade `outro`.
- **Sem API pública:** Midjourney e Suno não têm API pública oficial. Os modelos estão registrados sem preço por unidade, e o custo vem dos planos.

## ElevenLabs (`elevenlabs.json`)

- **Preço de TTS por 1K caracteres ficou `null`:** as buscas no domínio oficial divergiram. Uma deu US$ 0,05 (Flash/Turbo) e US$ 0,10 (Multilingual), outras deram US$ 0,04 e US$ 0,08. Parece depender do plano.
- **Notas da Artificial Analysis omitidas por divergência:** o Elo do Eleven v4 apareceu como 1316, 1315 e 1320; o AA-WER do Scribe v2 apareceu como 2,3% e 2,18%.
- **Preços vistos numa busca só e deixados fora:** Voice Changer, Dubbing, add-ons do Scribe e Agents. Os valores estão em `observacoes`.
- **Datas de lançamento:** só v4, v3 e Scribe v2 têm data. Music v2.5 e os demais ficaram `null`.
- **Outros:**
  - O handle do X do CTO não foi encontrado.
  - O preço anual total em USD não foi registrado, só o equivalente mensal.
  - O `valor_usd` dos programas ficou `null`, porque o benefício é dado em créditos ou em meses de plano.
- **Programa de estudantes:** marcado `talvez`, porque o Brasil não aparece na lista de países elegíveis.

## Runway (`runway.json`)

- **Planos:** o total anual de Pro e Max ficou `null`, porque só apareceu o equivalente mensal no anual. O Enterprise não tem preço público.
- **Modelos de terceiros:** a API da Runway revende cerca de 25 modelos de terceiros (Veo, Seedance, Wan, Gemini, GPT Image, ElevenLabs etc.). Não entraram como modelos e estão listados em `observacoes`.
- **Fora da lista atual da API:**
  - O Gen-4 de vídeo não-Turbo e o upscaler próprio não aparecem; não se confirmou se ainda existem no app.
  - GWM Worlds, GWM Robotics e Solaris foram anunciados, mas sem preço nem disponibilidade na API.
- **Datas:** Gen-4 Turbo, Gen-4 Image e Act-Two ficaram sem data oficial de lançamento.
- **Benchmarks:**
  - O `aa_video_elo` do Gen-4.5 não foi encontrado na AA. O Elo 1.247 que a própria Runway divulgou ficou só em `observacoes`.
  - O `lmarena_image_elo` não foi encontrado.
- **Confirmados por uma busca só:** o preço do gen4_image_turbo, o do gwm1_avatars e os tiers da API.
- **Canais a confirmar:** os handles do X do CEO e do CTO, o convite do Discord, a URL do YouTube e o endereço da status page.
- **Outros:**
  - O custo em créditos de cada modelo no app não foi coletado.
  - Não há programa de créditos para pesquisa acadêmica ou startups. O único `elegivel: sim` é o desconto de estudante de 25% via SheerID.
- **Campo `usos_sugeridos`:** o coletor gravou fora do formato e ele foi movido para `observacoes`.

## Luma AI (`luma.json`)

- **Nomes dos planos se contradizem:** a página de preços chama o de US$ 30 de Plus e o de US$ 90 de Pro, e o FAQ do app inverte. Mantive a versão da página de preços.
- **Preço anual:** os valores (US$ 300, 900 e 3.000) apareceram numa busca só, então ficou `null`.
- **Planos antigos do Dream Machine** (Lite, Plus e Unlimited): não registrados, porque parecem substituídos pelo app Luma Agents.
- **Desativação do Ray2 e do Photon:** aparecem como descontinuados na página oficial para assistentes, mas sem data de desativação publicada.
- **Datas de lançamento:** as do Ray2, do Photon e do Ray3 não foram confirmadas.
- **Preço do Ray2 por milhão de pixels:** veio de uma busca só e não entrou.
- **Correspondência de modelos (suposição do coletor):** a API atual expõe `uni-1` e `uni-1-max`, que foram tratados como UNI-1.1. **Conferir.**
- **Ray3.2:** o preço existe só por clipe (5 s / 10 s), não por segundo, então foi registrado com unidade `outro`.
- **Outros números ausentes:** o preço da unidade de Provisioned Throughput e a quantidade de créditos do teste grátis.
- **Benchmarks:** nenhum valor literal de `aa_video_elo` e `aa_image_elo` foi encontrado. Entraram só as notas do LMArena text-to-image para o UNI-1.1.
- **MCP oficial:** só aparece no resumo de uma busca (`a_verificar`).
- **YouTube oficial:** não identificado.
- **Créditos para pesquisa ou startup:** nenhum programa encontrado.

## Kling (`kling.json`)

- **Preços vistos numa só busca (fonte oficial, sem segunda conferência):** 3.0 Omni, Video O1, Image 3.0 Omni em 4K e Image 2.1 imagem→imagem.
- **Sem preço em USD:**
  - Kling 4.0 Flash (`restrito`): só em acesso antecipado para assinantes Ultra anual.
  - Kolors: não achei API própria.
  - Preços em CNY da plataforma chinesa: não coletados.
- **Planos:** o preço de tabela (US$ 10/37/92/180 por mês) está registrado. As buscas citaram também US$ 8,8/32,56/80,96/159,99, ora como renovação com desconto, ora como plano anual. Ficou `preco_anual_usd = null`.
- **Créditos grátis diários:** não confirmados. A página fala em "3 usos/dia" e um tweet de 2024 fala em 66 créditos por login diário (`a_verificar`).
- **Benchmarks:**
  - Entrou só o Kling 3.0 Pro (1095, arena de vídeo com áudio), com a divergência registrada: outros placares da AA mostram 1000 e 1240.
  - As demais notas apareceram uma vez só ou em placares de versões diferentes e foram omitidas.
- **Datas de lançamento:** sem dia exato para Video O1, 3.0 Turbo, Image O1, Image 2.1 e Kolors.
- **X do CEO e de líderes:** não identificados.
- **Virtual Try-On:** foi desativado junto com os modelos antigos em 2026-09-15 e não entrou como modelo. A página de pacotes ainda o cita, o que vale conferir.
- **Programas:** não há crédito para estudante ou pesquisador. O NextGen ficou `talvez`; o Creative Partner e o programa de afiliados ficaram `nao`.

## Black Forest Labs (`bfl.json`)

- **Preço das licenças comerciais self-hosted** (Builder, Platform, Professional): as buscas trouxeram só o que cada uma inclui, sem valor em USD.
- **Programas:** não há créditos para estudante, pesquisador ou startup. Só existe o Creator Program, marcado `nao` porque exige audiência de criador de conteúdo.
- **Créditos grátis do Playground:** as buscas divergiram (50 contra 200 créditos), então ficou `a_verificar`.
- **Preços vistos numa só busca** (mantidos, com a ressalva no campo `condicao`): o megapixel adicional do FLUX.2 [max]/[pro], o Outpainting [fast] e o Video Upscale.
- **FLUX.2 [dev]:** não tem endpoint hospedado na BFL (só roda local), então não tem preço.
- **Datas:**
  - Ficaram `null` o FLUX.2 [klein] e o Kontext [dev], porque as buscas divergiram.
  - A data da família FLUX.2 (2025-11-25) vem só de terceiros.
  - O FLUX 3 (2026-07-23) aparece descrito como preview/early access.
- **Artificial Analysis:** notas omitidas por divergência entre buscas (ex.: o FLUX.2 [pro] apareceu como 1183,83 e como 1207,58). Também não há nota de vídeo para o FLUX 3.
- **Notas do LMArena:** o max (1162) e o pro (1154) foram confirmados em duas buscas. O flex, o dev e as duas klein vieram de uma busca só.
- **Canais:** Discord, YouTube e página de status não identificados. O X oficial aparece como @bfl_ai, e links antigos usam @bfl_ml.

## Midjourney (`midjourney.json`)

- **Preço por unidade:** nenhum modelo tem preço em USD, porque não existe API pública oficial. Os Termos proíbem automação e apps de terceiros. Em 2025-07-16 abriram só uma pesquisa de interesse por uma Enterprise API. O custo real é tempo de GPU: um lote SD de vídeo leva cerca de 8 min e um lote HD, 26 min.
- **Notas que ficaram de fora:** o V6.1 (1047) e o V6 (1042) no AA apareceram em uma busca só e não entraram. O V8.x não está no AA, a Midjourney não aparece no ranking text-to-image do arena.ai e não achei `aa_video_elo` para o Video V1.
- **V5.2:** sem data exata de lançamento (só "junho de 2023"), então `lancado_em` ficou `null`.
- **Status `legado`:** foi julgamento do coletor para as versões que ainda dá para escolher com `--v`/`--niji`. A lista oficial de versões selecionáveis não foi lida.
- **Edit Model (V8.2):** não entrou como modelo separado, por falta de data e de identificação própria.
- **Vídeo:** não achei modelo de vídeo além do V1.
- **Indicadores de custo-benefício:** nenhum encontrado.
- **Canais:** sem YouTube oficial e sem líderes técnicos além do CEO. O `status.midjourney.com` veio de resumo de busca e precisa ser conferido.
- **Teste grátis:** existe um teste limitado só no app niji·journey, mas os limites não foram informados.

## Suno (`suno.json`)

- **Não há API pública oficial.** Desde 2026-07 existe só um programa de parceiros com acesso antecipado, e essa informação veio da imprensa de terceiros (`a_verificar`).
- **Pacotes de créditos avulsos e downloads extras:** existem, mas o preço só aparece dentro da conta.
- **Preço anual total em USD:** as fontes mostram só o equivalente mensal. Ficou `preco_anual_usd = null` e o valor mensal do anual foi para `limites`.
- **Datas:** não achei nas fontes oficiais a data exata da aposentadoria dos modelos anteriores ao v6 nem a de lançamento do v4.5+.
- **Canais:** sem YouTube oficial, sem página de status e sem @ de líderes técnicos (o CPO foi citado sem @ confirmado).
- **Plano "Basic":** os termos citam "free or basic tier", mas não há plano pago com esse nome. Parece ser o nome antigo do Free.
- **Benchmarks:**
  - O v6-wild não aparece nos placares, e o v6 ainda não estava no placar de vocais.
  - A nota 1169 do v5.5 veio de uma busca só.
  - **Chaves novas:** `aa_music_instrumental_elo` e `aa_music_vocals_elo`, porque o roteiro não prevê benchmark de música. **Decisão a confirmar no importador.**
- **Programa para estudante ou pesquisador:** não existe. Segundo resumo de busca, o antigo Pro estudantil foi descontinuado (`a_verificar`).
- **Termos de uso mudaram em 2026-09-03:** o uso comercial agora vale só para músicas baixadas dentro da cota do plano pago.

