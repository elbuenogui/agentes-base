---
artefato: HISTORIAS
fase: F2
status: vivo
---

# Histórias de usuário — Fase 2, desktop e ditado universal

Fecha a lacuna `L-A`. Escritas em 2026-09-06 pelo PM com o usuário, como manda a `D-13`: histórias
não são pré-requisito da fase, são a primeira entrega dela.

**São spec retroativa, e isso é de propósito.** O app já existe e já é usado; estas histórias
descrevem o que ele faz e por quê, para que exista rastro de `US-XXX` até a spec e o teste. Onde
uma história descreve algo que ainda não existe, isso está dito na própria história.

Os identificadores vêm do pré-projeto (`_rascunhos/2026-08-21_revisao-pre-projeto.md`), preservados
para não quebrar a rastreabilidade de quem já os citou — inclusive o `B-06`.

## US-D01 — Ditar com um atalho, sem tirar a mão do teclado

> Como quem escreve o dia inteiro, quero apertar um atalho, falar e ter o texto pronto, para não
> trocar de janela nem procurar botão no meio do trabalho.

- O acionamento principal é o **atalho global configurável**, não o clique (`D-01`). O clique no
  botão continua existindo como caminho alternativo.
- O mesmo atalho começa e termina a gravação.
- O estado — parado, gravando, processando — é **visível sem ambiguidade** (requisito implícito
  `D3` do pré-projeto).
- Funciona com o app em segundo plano e sem roubar o foco do que está na frente.

Rastreabilidade: `SPEC-002` A, B · `D-01`, `D-11`, `D-27`.

## US-D02 — Entregar o texto no destino

> Como quem dita para escrever em outro lugar, quero o texto pronto para usar no destino, para não
> transcrever de novo nem depender de achar a janela.

**Esta é a consolidação proposta no `B-06`** (US-D02 + US-A02 + US-D03 viram uma capacidade só,
*entrega do texto no destino*, com escada de fallback). A escada tinha três degraus; **hoje tem
dois**, e essa é a mudança que fecha o item:

| Degrau | Situação |
|---|---|
| 1. inserir no campo em foco | **morto** (`D-33`, 2026-09-05) — inserção automática saiu de vez, não é "depois" |
| 2. área de transferência | **é o padrão** — recortar nasce ligado (`D-30`, `SPEC-002` F4) |
| 3. mostrar na janela para copiar à mão | sempre disponível |

- Ao fim da transcrição o texto está na área de transferência **sem clique extra**.
- Colocar o texto **não o consome** (`D-15`): ele continua na janela para ser usado de novo.
- A ação separada "colocar a última transcrição no campo em foco", com atalho próprio e lendo da
  **memória do app** (nunca do clipboard), continua **parqueada e fora do MVP** — decisão do
  usuário em 2026-09-06: colar à mão não é o atrito do uso diário. Desenho preservado em
  `_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`.

Rastreabilidade: `SPEC-002` F · `B-06` (fechado por esta história), `D-15`, `D-30`, `D-33`.

## US-D03 — Ver e corrigir antes de usar

> Como quem dita frases soltas, quero acumular, revisar e desfazer antes de levar o texto embora,
> para não mandar erro adiante.

- A caixa **acumula** transcrições em vez de substituir.
- Apagar tem **desfazer por snapshot** — apagar sem volta é defeito, não simplicidade.
- O texto é editável à mão antes de sair.

Rastreabilidade: `SPEC-002` C, F · desenho de referência: a interface web
(`COMPORTAMENTOS_PARQUEADOS.md`).

## US-D04 — Não atrapalhar a tela

> Como quem usa isto o dia inteiro, quero que o app ocupe quase nada enquanto não estou ditando,
> para não perder espaço nem atenção.

- A janela nasce **compacta** — só o botão de gravar — e expande no hover ou ao entrar em
  gravando/processando; encolhe só com o mouse fora **e** o texto já resolvido (`D-32`).
- **Sempre no topo, sem roubar foco**: passar o mouse revela, só o clique tira foco (`D-15`).
- Arrastável para qualquer canto da tela, inclusive colada nas bordas.
- A área transparente em volta do cartão deixa clicar no que está atrás.

Rastreabilidade: `SPEC-002` J · `D-15`, `D-32` · suíte `desktop/testes_janela_compacta.py`.

## US-D05 — Transcrever um arquivo de áudio que já tenho

> Como quem recebe áudio de outras pessoas, quero jogar o arquivo no app e receber o texto, para
> não ter de tocar e ditar por cima.

- Arrastar e soltar sobre a janela, ou "Enviar arquivo" no menu ⋮.
- É **spec retroativa**: `POST /transcrever` já aceita upload desde a Fase 1.

Rastreabilidade: `SPEC-002` E2 (subiu do `B-01` em 2026-08-27) · contrato `NUCLEO.md`.

## US-D06 — Saber quanto estou gastando

> Como quem paga a API por uso, quero ver o consumo sem sair do app, para não descobrir a conta
> pelo extrato.

- Painel de consumo com as duas escalas da linha do tempo.
- Alarme declarado em **US$ 100/mês** (`D-18`), com condição de reabertura própria — acionada pela
  geração de imagem, que custa ~140× uma transcrição (`D-31`).
- Ver uso é **requisito**, não efeito colateral do backend guardar arquivo (`D-22`): dado errado
  aqui é defeito.

Rastreabilidade: `SPEC-002` H · `D-18`, `D-22`, `D-31`.

## US-D07 — Falhar de forma clara

> Como quem depende disto no meio de uma tarefa, quero saber o que deu errado e o que fazer, para
> não ficar olhando um botão que não responde.

- Sem internet, núcleo fora do ar, permissão de microfone negada, áudio grande demais, silêncio.
- A mensagem vem do **campo `codigo`** da resposta do núcleo, nunca do texto — decisão de
  implementação que virou padrão do app na primeira volta da Etapa 1.
- Cobre o requisito implícito `D2` do pré-projeto, que nenhuma história anterior cobria.

Rastreabilidade: `SPEC-001` (comportamento de erro do núcleo, medido em 2026-08-23) · `D-16`.

## O que estas histórias deliberadamente NÃO cobrem

Está declarado em `../F2_MVP_E_ENTREGAVEIS.md`. Em uma linha: inserção automática e modo ao vivo
(mortos, `D-33`), histórico navegável (`D-22`/`B-11`, adiado pelo usuário em 2026-09-06), seletor
de idioma (`D-08`, refutado por medição) e a ação "colocar a última transcrição" (parqueada).
