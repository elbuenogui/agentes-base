---
tema: Etapa 3 da Fase 2 — histórias, entregáveis e MVP
data: 2026-09-06
---

# Coleta — Etapa 3 da Fase 2 (histórias, entregáveis e MVP)

## 1. Abertura da etapa

- [DIRECIONAMENTO] Etapa aberta logo depois de o usuário confirmar no Windows real que a `D-32`
  está funcionando ("tá funcionando como deveria"). Passagem obrigatória por
  `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` feita antes da primeira história, como o
  `PLANO.md` manda desde a reprovação de 27/08.

## 2. As duas perguntas que destravaram a escrita

- [DIRECIONAMENTO] PM perguntou ao usuário qual passo manual mais incomoda hoje, no uso real.
  Resposta: **"nada, o fluxo já serve"**. Ditar, recortar e colar já basta no dia a dia.
- [DECISÃO] Histórico de transcrições (`D-22`, já declarado requisito): **fica para depois**, fora
  do MVP da F2.
- [DIRECIONAMENTO] Consequência das duas respostas juntas: a ação parqueada "colocar a última
  transcrição no campo em foco" **não sobe** — o atrito que ela resolveria não é o atrito que o
  usuário sente.

## 3. O que foi escrito

- [ARTEFATO] `spec/historias/F2_ditado-universal.md` — `US-D01` a `US-D07`, reaproveitando os
  identificadores do pré-projeto para não quebrar rastreabilidade. Spec retroativa de propósito: o
  app já existia quando as histórias foram escritas, o que é consequência direta da `D-13`.
  `US-D07` (falhar de forma clara) cobre o requisito implícito `D2` do pré-projeto, que nenhuma
  história anterior cobria. Fecha `L-A`.
- [ARTEFATO] `spec/F2_MVP_E_ENTREGAVEIS.md` — sete entregáveis (seis entregues; o sétimo é o uso em
  regime, que é o critério da fase) e o MVP declarado com a tabela do que fica **fora** dele. Fecha
  `L-B` e `L-C`.
- [DECISÃO] `D-34` — o MVP da Fase 2 é o app que já está em uso: *"ditar com um atalho e ter o
  texto pronto para colar, sem tirar a mão do teclado e sem piorar o que eu já uso"*.
- [DECISÃO] `B-06` **fechado** dentro da `US-D02`: a escada de entrega do texto ficou com dois
  degraus (área de transferência, padrão; janela para copiar à mão), não três — o primeiro morreu
  na `D-33`. Estava "amadurecendo" desde 21/08.
- [DECISÃO] `B-05` olhado e mantido fora do MVP; `B-11` olhado e adiado. São os três itens marcados
  `olhar de novo em: F2`, agora todos resolvidos.

## 4. Exceção de papel, registrada como a regra manda

- [DECISÃO] Usuário autorizou, em 2026-09-06, que o **PM redigisse ele mesmo** os artefatos de
  `spec/` desta etapa, em vez de passar como tarefa ao Executor. O `PM.md` proíbe o PM de criar
  artefato do projeto e exige que qualquer exceção seja explícita, datada e registrada no
  `PLANO.md` e na coleta — está aqui e lá. **Vale para esta etapa, não vira regra.**

## 5. O que muda no plano

- [DIRECIONAMENTO] Com o MVP declarado assim, **não há funcionalidade entre o app de hoje e o fim
  da Fase 2**. A Etapa 4 deixa de ser "escrever as etapas que faltam" e passa a ser "colher o que o
  uso mostrar" — e pode terminar com a constatação de que não faltam etapas.
- [PENDÊNCIA] Continuam abertos, sem bloquear nada: `.git/index.lock` de 27/08 (usuário apaga na
  máquina), `desktop/app.log` versionado e crescendo, o falso negativo do detector de pendência com
  duas transcrições idênticas seguidas, e a pergunta da `D-31` (se a geração de imagem ainda deve
  morar num app de ditado).
