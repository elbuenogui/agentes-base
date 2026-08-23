# Retomada — para o PM, em chat novo

> O nome do arquivo ficou do plano antigo de propósito, para não quebrar referências. O conteúdo é
> sempre o estado **atual**. Atualizado em **2026-08-23**, no encerramento do chat de PM que abriu
> o método Spec-Driven Development.

## Leia nesta ordem

1. `spec/VISAO.md` — a visão e as nove fases, com o `estado:` de cada uma.
2. `spec/DECISOES.md` — 16 decisões fechadas, cada uma com **Por quê** e **Reabre se**.
3. `.claude/estado/PLANO.md` — a Fase 1, seis etapas, uma concluída e uma cancelada.
4. `spec/contrato/NUCLEO.md` — o contrato do núcleo, medido contra a máquina.
5. `spec/QUESTOES_ABERTAS.md` e `spec/LACUNAS.md` — o que ainda falta.

Se quiser o quadro geral antes de tudo: peça **diagnóstico geral** — a skill
`.claude/skills/diagnostico-geral/` monta o painel a partir desses mesmos arquivos, e republica no
endereço fixo `https://claude.ai/code/artifact/cce317cd-d476-4dea-ae46-8d652cec6a3b`.

## Onde o projeto está

O `transcritor/` é a **Fase 1** de um assistente pessoal multiplataforma. A Fase 1 fecha o contrato
do núcleo; a Fase 2 (desktop, ditado universal) é a que o usuário quer usar todo dia.

**Concluído em 2026-08-23**: a Etapa 1 da Fase 1 — o contrato foi **medido**, não suposto. Caminho
feliz nos três modelos e nos dois modos; as seis situações de erro provocadas de verdade; as oito
lacunas fechadas com evidência.

**Cancelado**: a Etapa 5 (parâmetro de idioma), pela condição escrita nela mesma — a medição não
achou diferença de texto, tokens ou custo.

## O próximo passo, e é seu

**Etapa 2 — fechar a SPEC-001.** É trabalho de PM, não de Executor: incorporar o que foi medido,
decidir quais lacunas viram requisito e escrever o escopo da Etapa 3.

As candidatas da Etapa 3 já estão listadas no `PLANO.md` com evidência: códigos de erro legíveis
por máquina (L1), o erro enganoso em arquivo grande (L2) e o versionamento do contrato (L5).
**Fora de escopo (`D-17`)**: tudo que depende de `gpt-4o-transcribe-diarize`.

`PROXIMA_TAREFA.md` está declarando explicitamente que **não há tarefa de Executor**. Isso é
proposital: em duas ocasiões anteriores o arquivo ficou desatualizado apontando para etapa já feita,
e o Executor quase reexecutou.

## O que ficou pendente do usuário

**Nada.** As oito questões estão respondidas ou dissolvidas. O alarme de custo ficou em
**US$ 100/mês** (`D-18`), contra um gasto medido de US$ 0,53 em 343 requisições de 18 a 23 de
agosto.

## O que não se reabre sem motivo novo

Está tudo em `spec/DECISOES.md` com a condição de reabertura escrita. Os que mais tentam voltar:
modo ao vivo (congelado), servidor próprio (adiado com gatilho em estado compartilhado entre
aparelhos), processamento no relógio (nunca), idioma fixado em código (refutado por medição) e
qualquer trabalho em `gpt-4o-transcribe-diarize` (fora de escopo).

## Armadilhas do ambiente

- **Backend antigo na porta 8000** — 5 ocorrências. Conferir e derrubar antes de qualquer medição.
- **`.git/index.lock`** deixado pelo bridge remoto; o Executor apaga sozinho porque roda local.
- **Tarefa que quebra o `.env` ou o backend precisa avisar o usuário antes de começar** — ele usa o
  app ao vivo, e isso já aconteceu no meio de uma medição.
- **`PROXIMA_TAREFA.md` costuma envelhecer.** Conferir contra o `PROGRESSO.md` antes de confiar.
