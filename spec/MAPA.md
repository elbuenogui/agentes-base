---
artefato: MAPA
status: vivo
---

# Mapa de rastreabilidade

Índice único do `spec/`. Nenhum outro arquivo lista os outros.

`US-XXX → SPEC-XXX → TASK-XXX → TEST-XXX`

## Fase corrente: F1 — Núcleo de transcrição

| Entrega | Artefato | Status |
|---|---|---|
| E1.1 Contrato da API | [SPEC-001](specs/SPEC-001_contrato-do-nucleo.md) → [contrato/NUCLEO.md](contrato/NUCLEO.md) | **concluída 2026-08-23** — medida, não suposta |
| E1.2 ~~POC-6 tempo real fora do navegador~~ | — | **cancelada**: já respondida por `.claude/tmp/teste_tempo_real.py` (2026-08-20) e sem consumidor, com o ao vivo congelado |
| E1.3 ADR onde roda o núcleo / chave | — | **adiada por decisão**: gatilho é estado compartilhado entre aparelhos (F7/F9) |
| E1.4 Comportamento de erro do núcleo | parte da SPEC-001 | depende do levantamento |
| E1.5 Promover o harness do ao vivo | tarefa de arrumação | decidida pelo PM, não requer usuário |
| ~~E1.6 Parâmetro `idioma`~~ | lacuna L8 | **cancelada 2026-08-23**: a medição refutou o problema (`D-08`) |
| E1.7 Atualizar o `CLAUDE.md` | — | nova (2026-08-21): descreve o repo como "MVP de transcrição" e não cita `spec/` |

## Histórias

Nenhuma promovida ainda. A consolidação proposta na revisão do pré-projeto (US-D02 + US-A02 + US-D03
viram uma capacidade só, *entrega do texto no destino*, com escada de fallback) entra quando a F2
for especificada.

## PoCs

| ID | Fase | Pergunta | Status |
|---|---|---|---|
| POC-1 | F2 | por qual mecanismo inserir texto no campo em foco no Windows, e onde ele falha | não iniciada — **bloqueante da F2**, decide a linguagem do app. Alvos: terminal do Claude Code, VS Code (Electron), aba do WhatsApp |
| POC-2 | F2 | janela flutuante sempre no topo e não-ativável no Windows | não iniciada |
| POC-3 | F3 | overlay + acessibilidade inserindo texto em app de terceiro no S22 | não iniciada — bloqueante da F3 |
| POC-4 | F3/F5 | o que o app do ChatGPT no Android aceita | não iniciada |
| POC-5 | F4 | Wear OS: gravar, enviar, latência, bateria | não iniciada |
| ~~POC-6~~ | F1 | tempo real fora do navegador | **respondida: sim** (2026-08-20) |

## Decisões

[DECISOES.md](DECISOES.md) — livro-razão com 14 decisões fechadas, cada uma com razão e condição de
reabertura. Nenhum ADR promovido ainda: um ADR só nasce quando a decisão precisar de mais espaço do
que uma entrada de livro-razão.

## Lacunas

[LACUNAS.md](LACUNAS.md) — cinco abertas (L-A a L-E), uma fechada. Distinção que importa: questão é
decisão que só o usuário toma; lacuna é trabalho que ainda não foi feito.

## Rascunhos

`_rascunhos/2026-08-21_revisao-pre-projeto.md` — revisão do pré-projeto e as resoluções conversadas.
`_rascunhos/2026-08-21_mapa-de-fases.md` — origem da VISAO.md, mantido como histórico.
`_rascunhos/2026-08-21_inventario-repositorio.md` — o que já existe no repositório, por fase, e as
lacunas I1 a I6 que saíram daí.
`_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` — comportamentos já decididos pelo usuário à espera da
fase deles. **Quem especificar uma fase é obrigado a passar por este arquivo.**
