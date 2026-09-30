---
artefato: MAPA
status: vivo
---

# Mapa de rastreabilidade

Índice único do `spec/`. Nenhum outro arquivo lista os outros.

`US-XXX → SPEC-XXX → TASK-XXX → TEST-XXX`

> **Sem número derivado escrito à mão (`D-21`, 2026-08-23).** Este arquivo não diz quantas decisões,
> lacunas ou questões existem — quem conta é o painel do `diagnostico-geral`, que lê os arquivos na
> hora de gerar. Até 23/08 esta página anunciava "14 decisões" e "cinco lacunas abertas"; eram 18 e
> quatro. Contagem escrita à mão envelhece a cada linha nova, sem avisar ninguém.

## Fase encerrada: F1 — Núcleo de transcrição
`encerrada em 2026-08-24`

| Entrega | Artefato | Status |
|---|---|---|
| E1.1 Contrato da API | [SPEC-001](specs/SPEC-001_contrato-do-nucleo.md) → [contrato/NUCLEO.md](contrato/NUCLEO.md) | **concluída 2026-08-23** — medida, não suposta |
| E1.2 ~~POC-6 tempo real fora do navegador~~ | — | **cancelada**: já respondida por `.claude/tmp/teste_tempo_real.py` (2026-08-20) e sem consumidor, com o ao vivo congelado |
| E1.3 ADR onde roda o núcleo / chave | — | **decidida em 2026-09-30** (`D-36`, reabre `D-05`): núcleo remoto no Supabase, com login |
| E1.4 Comportamento de erro do núcleo | parte da SPEC-001 | **medido 2026-08-23**; virou requisito na Etapa 3 do `PLANO.md` (L1, L2, L3, L5) |
| E1.5 Promover o harness do ao vivo | tarefa de arrumação | Etapa 4 do `PLANO.md` — decidida pelo PM, não requer usuário |
| ~~E1.6 Parâmetro `idioma`~~ | lacuna L8 | **cancelada 2026-08-23**: a medição refutou o problema (`D-08` revisada) |
| E1.7 Atualizar o `CLAUDE.md` | — | Etapa 6 do `PLANO.md` — descreve o repo como "MVP de transcrição" e não cita `spec/` |

## F2 — Desktop, ditado universal (concluída em 2026-09-30, por uso em regime)

| Entrega | Artefato | Status |
|---|---|---|
| E2.1 App de desktop — paridade com a interface web | [SPEC-002](specs/SPEC-002_paridade-desktop.md) | **concluída 2026-08-27** — reprovada três vezes e refeita; fechada com a lista A–I inteira, confirmada pelo usuário no app rodando |
| E2.2 POC-1 — mecanismo de inserção no Windows | [pocs/POC-1/](pocs/POC-1/) | **etapa 2** — interrompida por achado, que virou a `D-26`; o resto da investigação foi para `B-22` |
| E2.3 Histórias, entregáveis e MVP | [historias/F2_ditado-universal.md](historias/F2_ditado-universal.md) · [F2_MVP_E_ENTREGAVEIS.md](F2_MVP_E_ENTREGAVEIS.md) | **concluída 2026-09-06** — fecha `L-A`, `L-B` e `L-C` (`D-13`); MVP declarado na `D-34` |
| E2.4 O resto do plano | — | **fechada em 2026-09-30** — não faltaram etapas; a fase encerrou pelo critério de uso em regime |

**Anexos fora do plano da fase** (não são etapa, `.claude/estado/historico/PLANO_2026-09-30_fase2-encerrada.md` tem o
detalhe de cada um): geração de imagem (`D-31`, 2026-08-27, concluída) e botão flutuante compacto (`D-32`,
2026-09-05/06, **concluído** — dez rodadas, fechado com a arquitetura de máscara e confirmado no uso
real).

**Estado da SPEC-002**: viva. É o critério de pronto da Etapa 1 e a régua do que "no mínimo o mesmo
que o HTML" quer dizer, item a item. O dono do comportamento continua sendo
`transcritor/frontend/index.html` — quem mexer nele passa por lá.

**A `D-06` (linguagem do app desktop) está fechada** desde 2026-08-27 pela `D-27`: Python, com a
janela sempre no topo. Não é mais a POC-1 que decide isso.

**Estado da SPEC-001**: fechada em 2026-08-23. O que ela deixou como requisito está na Etapa 3 do
`PLANO.md`; o que ela deixou como comportamento declarado (não como conserto) está na `D-16`
(gate de silêncio é obrigação do cliente) e na `D-17` (diarização fora de escopo).

## Plano corrente: Núcleo centralizado no Supabase (desde 2026-09-30)

Decisão `D-36` (reabre `D-05`). Seis etapas, critérios em `.claude/estado/PLANO.md`: reconhecer o
projeto RAG-COMPARTILHADO, banco com histórico importado, transcrever remoto, consumo remoto com a
imagem registrando no banco, desktop no remoto com login, contrato novo.

## Duas famílias de "lacuna" — não confundir

| Família | Onde mora | O que é | Situação |
|---|---|---|---|
| `L1`–`L8` | dentro da [SPEC-001](specs/SPEC-001_contrato-do-nucleo.md) | defeitos **do contrato do núcleo** | quatro viram conserto na Etapa 3; as outras viraram decisão. **Morrem no fim da Fase 1** |
| `L-A`–`L-G` | [LACUNAS.md](LACUNAS.md) | **trabalho do projeto** que ainda não foi feito | vivas, cada uma dizendo que fase trava |

Separadas só por um hífen até 2026-08-23, o que já custou releitura. Não foram renomeadas por
decisão consciente: a família `L1`–`L8` está de saída, e renomear o que morre em uma etapa custa
mais que conviver com ela até lá.

## Histórias

[historias/F2_ditado-universal.md](historias/F2_ditado-universal.md) — `US-D01` a `US-D07`, escritas
em 2026-09-06. A consolidação proposta na revisão do pré-projeto (US-D02 + US-A02 + US-D03 viram uma
capacidade só, *entrega do texto no destino*, com escada de fallback) **entrou na `US-D02` e fechou o
`B-06`** — com dois degraus vivos em vez de três: o primeiro, inserir no campo em foco, morreu na
`D-33`.

## PoCs

| ID | Fase | Pergunta | Status |
|---|---|---|---|
| POC-1 | F2 | por qual mecanismo inserir texto no campo em foco no Windows, e onde ele falha | **etapa 1 da fase corrente** — bloqueante da F2, decide a linguagem do app (`D-06`), e é o primeiro cliente a consumir o contrato fora do `index.html`. Alvos: terminal do Claude Code, VS Code (Electron), aba do WhatsApp |
| POC-2 | F2 | janela flutuante sempre no topo e não-ativável no Windows | não iniciada — condição de reabertura da `D-15` |
| POC-3 | F3 | overlay + acessibilidade inserindo texto em app de terceiro no S22 | não iniciada — bloqueante da F3 |
| POC-4 | F3/F5 | o que o app do ChatGPT no Android aceita | não iniciada |
| POC-5 | F4 | Wear OS: gravar, enviar, latência, bateria | não iniciada — condição de reabertura da `D-04` |
| ~~POC-6~~ | F1 | tempo real fora do navegador | **respondida: sim** (2026-08-20) |

## Decisões

[DECISOES.md](DECISOES.md) — livro-razão, cada decisão com a razão e a condição de reabertura.
Nenhum ADR promovido ainda: um ADR só nasce quando a decisão precisar de mais espaço do que uma
entrada de livro-razão.

## Lacunas e questões

[LACUNAS.md](LACUNAS.md) — o que falta produzir, cada uma dizendo que fase trava.
[BACKLOG.md](BACKLOG.md) — ideia que ainda não é trabalho, com origem, estado e a fase em que volta
à mesa. Saiu de dentro do `PLANO.md` em 2026-08-23 (`D-21`).
[QUESTOES_ABERTAS.md](QUESTOES_ABERTAS.md) — a pergunta e o ponteiro para o `D-nn` que a respondeu.

Distinção que importa: **questão** é decisão que só o usuário toma; **lacuna** é trabalho que ainda
não foi feito; **item de backlog** é ideia que ainda não virou nem uma coisa nem outra.

## Rascunhos

`_rascunhos/2026-08-21_revisao-pre-projeto.md` — revisão do pré-projeto e as resoluções conversadas.
`_rascunhos/2026-08-21_mapa-de-fases.md` — origem da VISAO.md, mantido como histórico.
`_rascunhos/2026-08-21_inventario-repositorio.md` — o que já existe no repositório, por fase, e as
lacunas I1 a I6 que saíram daí.
`_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` — comportamentos já decididos à espera da fase deles.
**Quem especificar uma fase é obrigado a passar por este arquivo.**
