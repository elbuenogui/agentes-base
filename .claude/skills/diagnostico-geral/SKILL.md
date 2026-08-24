---
name: diagnostico-geral
description: Monta o painel visual de estado do projeto — fases, decisões, questões, lacunas e próximos passos — publicado como artefato. Use quando a pessoa pedir "diagnóstico geral", "panorama", "como está o planejamento", "me mostra o estado do projeto", ou pedir para atualizar o painel depois de decisões novas.
---

# Diagnóstico geral

O usuário lê o estado deste projeto muito melhor em painel do que em prosa — é o formato em que ele
consegue aprovar ou recusar. Quando ele pedir **diagnóstico geral**, a resposta é um painel visual
publicado, **nunca** um texto longo no chat (decisão `D-14` em `spec/DECISOES.md`).

## Regra que não se quebra

O painel é uma **vista**, não uma fonte de verdade. Tudo que ele mostra vem dos arquivos abaixo. Se
uma informação não está num arquivo, ela não entra no painel — ela primeiro vira arquivo.

## O que ler, nesta ordem

| Arquivo | Do que sai no painel |
|---|---|
| `spec/VISAO.md` | as fases e o `estado:` de cada uma |
| `spec/DECISOES.md` | o livro-razão — cada decisão com a razão |
| `spec/QUESTOES_ABERTAS.md` | respondidas e abertas, com o que cada uma trava |
| `spec/LACUNAS.md` | o que falta produzir |
| `spec/BACKLOG.md` | o que está amadurecendo, e para que fase |
| `.claude/metodo/DECISOES_METODO.md` | as decisões de método (`M-nn`) — separadas das de produto |
| `.claude/estado/PLANO.md` | as etapas da fase corrente e o que está em execução |
| `.claude/estado/PROGRESSO.md` | o que o Executor entregou desde a última virada |
| `spec/MAPA.md` | PoCs e rastreabilidade |
| `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` | comportamentos já decididos esperando a fase deles |

Os `estado:` de fase em `VISAO.md` são legíveis por linha: `em-andamento`, `bloqueada:<POC>`,
`condicional`, `nao-iniciada`, `encerrada`, `futuro`. Manter esse formato é o que mantém o painel
barato de gerar.

## Passe de conferência (regra de 2026-08-23, `D-21`)

Você já está lendo os oito arquivos. **No mesmo passe, confira se eles concordam entre si** — e o
que não bater vira uma seção do painel, não um comentário no chat.

O que procurar, em ordem de gravidade:

1. **Contradição de estado.** A mesma etapa, fase, questão ou lacuna com situação diferente em dois
   arquivos (concluída num, na fila noutro). Foi assim que a `VISAO.md` passou dois dias anunciando
   uma etapa "na fila do Executor" que já estava concluída.
2. **Número derivado escrito à mão.** Qualquer contagem em prosa — "14 decisões", "cinco lacunas
   abertas", "seis etapas". Números são do painel; no texto, envelhecem sem avisar. Ao achar um,
   aponte o arquivo e a linha.
3. **Ponteiro quebrado.** Citação a um `D-nn`, `Q-n`, `L-x`, `SPEC-nnn` ou `POC-n` que não existe, ou
   link relativo para arquivo que sumiu.
4. **Data fora de ordem.** Um arquivo que responde uma questão em data anterior à da decisão que a
   substituiu, sem dizer que foi superado. Pela `D-19`, o mais recente vence — então o achado é o
   arquivo mais velho que ainda se apresenta como atual.
5. **Fato sem dono.** A mesma decisão argumentada por extenso em mais de um arquivo. Um argumenta, os
   outros apontam.

**Como reportar**: uma seção do painel chamada **Consistência**, logo antes de "O que eu preciso de
você". Vazia é bom sinal e deve aparecer mesmo assim, dizendo que nada divergiu — silêncio não
distingue "conferi e está certo" de "não conferi".

**O que não fazer**: não corrija nada por conta própria ao gerar o painel. O painel é uma vista, e
essa regra não muda por causa desta seção. Achado vira conversa com o usuário; a correção é do PM,
depois.

## Seções do painel, nesta ordem

1. **Cabeçalho** com a faixa de amplitude (o mesmo desenho que o app traz na tela), a data e uma
   frase dizendo que a página é uma vista do repositório.
2. **Números do topo** — fases abertas, decisões fechadas, questões respondidas de um total, PoCs
   rodadas, histórias escritas. Números que estão em zero e deveriam estar acima disso vão em cor
   de alerta.
3. **As fases**, em cartões com faixa lateral colorida por estado.
4. **Decisões fechadas**, numeradas, **cada uma com a razão junto** — a razão é o conteúdo, não o
   enfeite.
5. **Questões**, em duas colunas: respondidas e abertas, cada aberta dizendo o que trava.
6. **Lacunas e backlog** — o que falta produzir, e o que está amadurecendo para a fase seguinte
   (itens do `BACKLOG.md` com `olhar de novo em:` apontando para ela). Item recusado ou morto não
   entra no painel; ele existe para quem for reabrir, não para ocupar a vista.
7. **Consistência** — o resultado do passe de conferência (ver acima). Vazia, diz que nada
   divergiu; nunca some.
8. **Próximos passos possíveis**, dois ou três, com o recomendado marcado e o custo de cada um em
   sessões e no que exige do usuário.
9. **O que eu preciso de você** — a lista curta de decisões pendentes, numerada.

## Identidade visual — manter estável entre gerações

Um painel que muda de cara a cada geração deixa de ser comparável com o anterior.

- **Fontes** (Google Fonts): `Archivo` para títulos e rótulos, `Source Serif 4` para texto corrido,
  `IBM Plex Mono` para IDs, estados e números. Mono para `F2`, `POC-1`, `D-07`, `SPEC-001` — os IDs
  são dados, não prosa.
- **Cores**, em tokens, com tema claro e escuro: fundo `#F1F4F3` / `#0D1615`; superfície `#FFFFFF` /
  `#15211F`; tinta `#14201F` / `#E7EEEC`; linha `#D5DEDB` / `#26332F`; acento verde-azulado `#0E6E73`
  / `#58B7BB`. Semânticas separadas do acento: pronto `#2F7A4F` / `#6BC08D`; esperando `#96690F` /
  `#D7A94A`; bloqueado `#A33A2E` / `#E0796A`.
- Definir todo o tema claro em `:root`, redefinir só os tokens em
  `@media (prefers-color-scheme: dark)` sob `:root:not([data-theme="light"])` e de novo em
  `:root[data-theme="dark"]`. Nenhuma cor pode existir apenas dentro de um bloco de tema.

## Publicação

Publicar como artefato com o título **Mapa do Assistente** e o ícone 🎙️🗺️.

**Atualizar sempre o mesmo endereço**, para o usuário não acumular painéis velhos:

```
https://claude.ai/code/artifact/cce317cd-d476-4dea-ae46-8d652cec6a3b
```

Numa sessão que não seja esta, passar essa URL no parâmetro `url` ao publicar. Se a ferramenta de
artefato não existir na sessão, escrever o HTML num arquivo e entregar o arquivo, dizendo que o
painel não pôde ser publicado.

## Depois de publicar

Uma resposta curta no chat: o link, e **só** o que mudou desde o painel anterior. O conteúdo está
na página; repetir no chat desperdiça a razão de existir do painel.
