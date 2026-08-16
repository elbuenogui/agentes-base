---
name: coleta-consolidacao
description: Mantém a coleta contínua de decisões, artefatos, direcionamentos e pendências do projeto — registro append-only por interação em coleta/AAAA-MM-DD_tema.md e consolidação em 4 categorias. Use em todo chat de trabalho, nos comandos "coleta:", "consolidar" e, se houver um destino final separado, "aplicar", ou ao encerrar um chat.
---

# Coleta e consolidação (registro vivo do projeto)

Ferramenta de documentação contínua de um projeto de trabalho ao longo de vários chats. Cada
chat deixa um rastro curado de decisões, artefatos, direcionamentos e pendências — para não
depender da memória do chat nem da rolagem para reconstruir "por que decidimos assim".

<Se este projeto alimenta um documento final separado (relatório, projeto de escrita, um
DOCUMENTO_MESTRE.md, etc.), diga aqui qual é e ajuste a seção "Aplicar" abaixo. Se não houver
destino separado, remova a seção "Aplicar" inteira — a coleta fica só como registro interno,
sem o passo de "aplicar" a lugar nenhum.>

## Regras de operação

1. **Um arquivo por chat**: `coleta/AAAA-MM-DD_<tema>.md`, criado a partir de
   `coleta/_TEMPLATE.md` (se existir). Não misturar assuntos de chats diferentes no mesmo
   arquivo.

2. **Registro por interação (seção 1 — append-only)**: ao longo do chat, sempre que algo
   relevante acontecer, acrescente UMA linha por item, marcada com:
   - `[DECISÃO]` — escolha feita, SEMPRE com o trade-off (`— trade-off: ...`);
   - `[ARTEFATO]` — coisa produzida (arquivo, seção, ferramenta), com caminho;
   - `[DIRECIONAMENTO]` — orientação nova ou alterada;
   - `[PENDÊNCIA]` — o que ficou em aberto, com `— depende de: ...`.
   **Nunca reescrever linhas anteriores.** O comando `coleta: <nota>` registra uma nota ditada
   verbatim, com a marcação indicada.

3. **Consolidar (seção 2)**: no comando **"consolidar"** (ou ao encerrar o chat), gere o resumo
   agrupado nas 4 categorias — Decisões, Artefatos, Direcionamentos, Pendências. O resumo é a
   forma útil; o registro bruto da seção 1 só é consultado quando preciso expandir algo.

4. **Aplicar — só se houver um destino final separado.** O comando **"aplicar"** leva o resumo
   consolidado até esse destino, sempre como proposta a validar, nunca automaticamente. Neste
   projeto, se não houver destino separado, não use este comando — o resumo consolidado já é o
   produto final da coleta.

## Travas (antialucinação / human-in-the-loop)

- Não inventar decisões, números, versões ou referências: registrar só o que aconteceu no chat.
- O resumo consolidado é PROPOSTA; nada entra em documento final sem aprovação explícita.
- Decisões são de quem está conduzindo o projeto; o assistente registra e, no máximo, sugere a
  marcação.
- Sugestões próprias do assistente entram marcadas (`[PROPOSTA-ASSISTENTE]`).
- Converter datas relativas em absolutas ao registrar.

## Onde esta skill roda

Pode rodar em mais de um repositório do mesmo projeto, com o mesmo template — a coleta é
portátil; a aplicação a um destino final (se houver) é exclusiva de onde esse destino vive.
