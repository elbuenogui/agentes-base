# Roteiro da coleta — Biblioteca de IA (radar)

> Lido pelas sessões do Claude Code **na nuvem** que fazem a coleta pesada. Cada sessão cuida de
> **um grupo** de provedores (ver `provedores.json`) e grava **um arquivo JSON por provedor** em
> `radar/coleta/<id>.json`. Depois uma sessão com acesso ao banco importa esses arquivos no esquema
> `radar` do Supabase `rag-compartilhado` e republica o Painel de Benchmark de IA.
>
> Trabalho todo em português do Brasil. Não faça commit em `main`: use o branch `radar-coleta`.
>
> **A coleta completa rodou uma vez (2026-10-01) e não se repete.** Saiu cara: 5 sessões em paralelo,
> um subagente por provedor e o modelo mais caro herdado. Para manter a biblioteca em dia, siga a
> seção [Manutenção](#manutenção) no fim deste arquivo. As regras duras e o formato continuam
> valendo para ela.

## Para quem é

Guilherme: graduando da USP (campus São Carlos, Brasil), com pesquisa vinculada ao projeto UrbVerde
(dados urbanos e ambientais) e orientador docente. Ele tem e-mail institucional da USP. Projetos
que usam IA: um assistente pessoal com transcrição de voz, a Mari (agente de RAG da pesquisa) e uma
base de agentes com papéis PM/EXEC. Já tem: créditos de API da OpenAI, plano Claude Max, Google AI
Pro de estudante (Antigravity CLI), Codex no ChatGPT Free.

Use esse perfil para julgar `elegivel` nos programas e para escrever `usos_sugeridos`.

## Regras duras

1. **Nenhum número sem fonte.** Todo preço, limite, nota e valor de crédito leva `fonte_url` e data.
   Se não achar, use `null` e explique em `observacoes`. Nunca estime, nunca arredonde.
2. **Fonte oficial primeiro.** Preço e plano: página oficial do provedor. Segunda fonte para conferir:
   OpenRouter (`https://openrouter.ai/api/v1/models/<id>/endpoints`). Se divergirem, registre a
   oficial e anote a divergência.
3. **O WebFetch resume a página com um modelo pequeno.** Peça sempre os valores *literais* e
   desconfie de números redondos. Na dúvida, busque o mesmo valor numa segunda página.
4. **Todos os modelos ativos**, não só o topo de linha: inclua os pequenos (ex.: Haiku), os caros
   (ex.: Fable), os de outros tipos (imagem, vídeo, voz, embeddings) e os com desativação anunciada
   (`status` + `desativa_em`).
5. **Indicadores de custo-benefício são encontrados, não inventados.** Ex.: "custo para rodar o
   índice" da Artificial Analysis, preço por ponto de nota publicado por alguém. Cite a fonte.
6. **Canais do X:** registre o @ oficial e o @ do CEO e de líderes técnicos que anunciam
   lançamentos. Não precisa ler os tweets (o X costuma bloquear leitura); só o endereço.
7. Marque `"origem": "a_verificar"` em tudo que veio só de agregador ou blog de terceiros.

## Benchmarks por tipo

| tipo do modelo | `benchmark` (chave) | fonte |
|---|---|---|
| texto | `aa_index`, `lmarena_elo` | artificialanalysis.ai/leaderboards/models; arena.ai/leaderboard/text |
| imagem | `aa_image_elo`, `lmarena_image_elo` | Artificial Analysis Image Arena; LMArena (text-to-image) |
| vídeo | `aa_video_elo` | Artificial Analysis Video Arena |
| voz (fala→texto) | `aa_stt_wer` | Artificial Analysis Speech to Text |
| voz (texto→fala) | `aa_tts_elo` | Artificial Analysis Speech Arena |
| embeddings | `mteb_media` | MTEB leaderboard (Hugging Face) |

Use a variante de maior nota e diga qual em `observacao` da nota.

## Processo, por provedor

1. Leia `provedores.json` e pegue os provedores do seu grupo.
2. Para cada um, colete na ordem: canais → planos → modelos e preços → notas → capacidades →
   grátis → programas → indicadores. Use subagentes em paralelo, um por provedor.
3. Grave `radar/coleta/<id>.json` no formato abaixo.
4. Rode `python radar/validar.py radar/coleta/<id>.json` e corrija até passar.
5. Ao terminar o grupo, faça commit no branch `radar-coleta` com a mensagem
   `radar: coleta <grupo> AAAA-MM-DD` e push. Não abra PR. Outras sessões gravam no mesmo branch
   ao mesmo tempo: antes do push rode `git pull --rebase origin radar-coleta` (se o branch ainda não
   existir no remoto, crie-o a partir de `main`). Cada sessão só mexe nos arquivos dos seus
   provedores, então o rebase não deve dar conflito.
   **Se a sessão cair no meio**, grave e faça push do que já estiver validado; a próxima sessão do
   mesmo grupo pula os provedores que já têm arquivo em `radar/coleta/`.
6. Escreva no fim de `radar/coleta/RELATORIO_<grupo>.md` o que ficou sem dado e por quê.

## Formato do arquivo (`radar/coleta/<id>.json`)

```json
{
  "provedor": {"id": "anthropic", "nome": "Anthropic", "grupo": "laboratorio", "site": "https://www.anthropic.com",
               "pais": "EUA", "resumo": "2 a 3 frases: o que faz e onde se destaca.", "fontes": ["https://..."]},
  "coletado_em": "2026-10-02",
  "canais": [{"tipo": "x_ceo", "nome": "Dario Amodei", "url": "https://x.com/...", "handle": "@...", "observacao": null}],
  "planos": [{"nome": "Max 20x", "publico": "individual", "preco_mensal_usd": 200, "preco_anual_usd": null,
              "inclui": "...", "limites": "...", "fonte_url": "https://...", "conferido_em": "2026-10-02"}],
  "modelos": [{"id": "anthropic/claude-haiku-4.5", "nome": "Claude Haiku 4.5", "tipo": "texto",
               "pesos_abertos": false, "lancado_em": "2025-10-15", "status": "ativo", "desativa_em": null,
               "contexto_tokens": 200000,
               "preco": {"entrada_usd_mtok": 1, "saida_usd_mtok": 5, "fonte_url": "https://...", "divergencia": null},
               "outros_precos": [{"unidade": "mtok_cache", "valor_usd": 0.1, "condicao": "leitura de cache", "fonte_url": "https://..."}],
               "notas": [{"benchmark": "aa_index", "valor": 17, "medido_em": "2026-10-02", "fonte_url": "https://...", "observacao": "variante max"}]}],
  "capacidades": [{"capacidade": "agente_agendado", "produto": "Claude Code routines", "como_acessar": ["nuvem", "cli"],
                   "plano_minimo": "Pro", "gratis": false, "headless": true, "comando": "claude -p ...",
                   "limites": "...", "fonte_url": "https://..."}],
  "gratis": [{"titulo": "...", "resumo": "...", "limites": "...", "chamavel_por_agente": true, "url": "https://...",
              "valido_ate": null, "origem": "verificado"}],
  "programas": [{"nome": "AI for Science", "publico": "pesquisador", "beneficio": "...", "valor_usd": 20000,
                 "requisitos": "...", "elegivel": "talvez", "elegivel_motivo": "...", "como_aplicar": "...",
                 "url": "https://...", "status": "continuo", "prazo": null, "verificado_em": "2026-10-02"}],
  "indicadores": [{"modelo_id": "anthropic/claude-opus-5.5", "nome": "custo para rodar o índice AA", "valor": 5.98,
                   "unidade": "USD", "descricao": "...", "medido_em": "2026-10-02", "fonte_url": "https://..."}],
  "observacoes": "o que não deu para obter e por quê"
}
```

Valores permitidos:

- `grupo`: laboratorio, midia, inferencia, busca_embeddings, outro
- `canais[].tipo`: blog, changelog, docs, precos, status, x_oficial, x_ceo, x_lider, discord, youtube, rss, github, outro
- `planos[].publico`: individual, estudante, equipe, empresa, api, pesquisa
- `modelos[].tipo`: texto, imagem, video, audio_stt, audio_tts, audio, musica, embedding, rerank, multimodal
- `modelos[].status`: ativo, legado, desativacao_anunciada, desativado, restrito
- `outros_precos[].unidade`: mtok_cache, imagem, minuto_audio, hora_audio, segundo_video, mil_caracteres, mil_requisicoes, outro
- `capacidades[].capacidade`: texto, codigo, imagem_gerar, imagem_editar, video_gerar, audio_stt, audio_tts,
  audio_tempo_real, musica, embeddings, rerank, busca_web, pesquisa_profunda, agente_agendado, agente_nuvem,
  computer_use, cli_headless, mcp, notebook
- `capacidades[].como_acessar`: app, web, api, cli, ide, nuvem
- `programas[].publico`: estudante, pesquisador, educador, startup, ong, todos
- `programas[].elegivel`: sim, nao, talvez
- `programas[].status`: aberto, fechado, em_breve, continuo, desconhecido
- `gratis[].origem`: verificado, a_verificar

Datas em `AAAA-MM-DD`. Preços em US$. Se só houver em outra moeda, não converta: deixe o campo `null` e registre o valor
em `observacoes`, com a moeda original.

## Prompts das sessões

Abra uma sessão do Claude Code na nuvem para cada grupo, no repositório agentes-base, e cole:

> Leia `radar/ROTEIRO_COLETA.md` e siga à risca. Seu grupo é **`<grupo>`** (sessão `<n>` em
> `radar/provedores.json`). Colete todos os provedores da sua sessão, valide cada arquivo com
> `radar/validar.py` e faça commit e push no branch `radar-coleta` ao final. Português do Brasil.

Sessões: `1` laboratórios A, `2` laboratórios B, `3` mídia, `4` inferência e agregadores,
`5` busca e embeddings.

## Manutenção

A base completa já existe. Daqui em diante só se atualiza o que mudou, com teto de custo explícito.

| o quê | como | frequência |
|---|---|---|
| preços | script sem IA lendo a API pública de modelos do OpenRouter (`https://openrouter.ai/api/v1/models`); grava a diferença | diário |
| notas e benchmarks | uma sessão, modelo pequeno, lê só os rankings da tabela "Benchmarks por tipo" e grava as diferenças | semanal |
| planos, programas, grátis, capacidades | uma sessão, modelo pequeno, só para provedores cujo changelog ou página de preços mudou desde a última leitura | mensal |
| provedor novo ou lançamento grande | coleta pontual daquele provedor, no formato acima | por gatilho |

Regras da manutenção:

1. **Nunca mais rodar a coleta completa** dos 32 provedores. Se a base parecer velha demais, o
   Guilherme decide e autoriza; não é decisão de sessão.
2. **Nada de sessões em paralelo nem de um subagente por provedor.** Uma sessão por rodada.
3. **Toda sessão declara o modelo explicitamente** (o menor que dê conta), em vez de herdar o da
   sessão que a abriu.
4. Grave só o que mudou, com fonte e data, no mesmo formato de `radar/coleta/<id>.json`.
