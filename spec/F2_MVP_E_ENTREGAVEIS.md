---
artefato: MVP_E_ENTREGAVEIS
fase: F2
status: vivo
---

# MVP declarado e entregáveis — Fase 2

Fecha as lacunas `L-B` (lista de entregáveis) e `L-C` (definição declarada de MVP). Escrito em
2026-09-06 pelo PM com o usuário (`D-13`), depois de o app estar em uso real.

## MVP declarado (`L-C`)

> **Ditar com um atalho e ter o texto pronto para colar, sem tirar a mão do teclado e sem piorar o
> que eu já uso.**

Nada além disso. A definição saiu de uma pergunta direta ao usuário em 2026-09-06 — *qual passo
manual mais incomoda hoje?* — e a resposta foi **"nada, o fluxo já serve"**. Ou seja: o MVP da
Fase 2 **é o app que já está em uso**, e o que resta da fase não é funcionalidade, é uso em regime.

### Fora do MVP, declarado

Declarar o que fica de fora é metade da definição — sem isso, "MVP" vira nome para "tudo".

| Fora | Por quê | Onde vive |
|---|---|---|
| Inserção automática no campo em foco | morta de vez, não adiada | `D-33`, `B-22`, `POC-1` |
| Modo ao vivo / tempo real | morto de vez | `D-33`, `D-02` |
| Ação "colocar a última transcrição" (atalho próprio) | usuário: colar à mão não é o atrito (2026-09-06) | parqueada em `_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` |
| Histórico navegável por projeto/entrevista | adiado pelo usuário em 2026-09-06 | `D-22`, `B-11` |
| Seletor de idioma | premissa refutada por medição | `D-08` |
| Adiantamento de exibição no streaming | sensação de uso; o fluxo já serve | `B-05` |
| Android, smartwatch, agente | outras fases | `VISAO.md` F3, F4, F5+ |

## Entregáveis da fase (`L-B`)

| # | Entregável | Estado |
|---|---|---|
| 1 | App de desktop para Windows, Python/PySide6, com a camada de inserção isolada (`D-11`, `D-27`) | **entregue** |
| 2 | Paridade com a interface web, item a item | **entregue** — `SPEC-002`, lista A–I, confirmada no app rodando em 2026-08-27 |
| 3 | Atalho global configurável como acionamento principal (`D-01`) | **entregue** |
| 4 | Janela flutuante compacta com os três estados (`D-15`, `D-32`) | **entregue** — confirmada no uso real em 2026-09-06 |
| 5 | Suíte de regressão versionada da janela (`desktop/testes_janela_compacta.py`) | **entregue** — 230 verificações |
| 6 | Histórias, entregáveis e MVP (este documento e `historias/F2_ditado-universal.md`) | **entregue** — 2026-09-06 |
| 7 | **Uso em regime**: o usuário dita neste app no dia a dia, no lugar do que usava | **em curso** — é o critério de conclusão da fase |

**Fora da lista, de propósito**: a geração de imagem (`D-31`) foi entregue e é usada, mas é anexo
fora do plano — F2 é ditado universal, e imagem não é ditado. Ela não conta para o critério da fase,
e a pergunta que ela abriu (se ainda deve morar num app de ditado, ou virar um segundo cliente do
mesmo núcleo, como a `D-07` previa) continua aberta.

## O que o critério de conclusão passa a significar

O critério da fase sempre foi *"o usuário usa o ditado deste app no dia a dia, no lugar do que usa
hoje"*, e com o MVP declarado assim ele fica **sozinho**: não há funcionalidade entre o app de hoje
e o fim da fase. O que pode reabrir escopo é o próprio uso — um incômodo que apareça depois de dias
ditando vale mais que qualquer lista escrita hoje, e é por isso que a Etapa 4 (o resto do plano) só
se escreve com o app rodado por um tempo.
