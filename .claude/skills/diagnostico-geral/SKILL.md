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
| `.claude/estado/PLANO.md` | as etapas da fase corrente e o que está em execução |
| `.claude/estado/PROGRESSO.md` | o que o Executor entregou desde a última virada |
| `spec/MAPA.md` | PoCs e rastreabilidade |
| `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` | comportamentos já decididos esperando a fase deles |

Os `estado:` de fase em `VISAO.md` são legíveis por linha: `em-andamento`, `bloqueada:<POC>`,
`condicional`, `nao-iniciada`, `encerrada`, `futuro`. Manter esse formato é o que mantém o painel
barato de gerar.

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
6. **Lacunas**, o que falta produzir.
7. **Próximos passos possíveis**, dois ou três, com o recomendado marcado e o custo de cada um em
   sessões e no que exige do usuário.
8. **O que eu preciso de você** — a lista curta de decisões pendentes, numerada.

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
