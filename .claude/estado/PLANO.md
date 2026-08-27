# PLANO — Fase 2: Desktop, ditado universal

> Plano da **fase corrente**. A visão e o mapa das nove fases estão em `spec/VISAO.md`; o método,
> em `.claude/CEREBRO.md`. Virada de plano em **2026-08-24**: a Fase 1 encerrou com todas as etapas
> concluídas (plano em `historico/PLANO_2026-08-24_fase1-encerrada.md`, progresso em
> `historico/PROGRESSO_fase1-nucleo_2026-08-23_a_2026-08-24.md`).

## Objetivo

Ditar em qualquer lugar do Windows: atalho, fala, e o texto aparece no campo em foco. É a fase que
o usuário quer usar todo dia — e é o que justifica adiar o agente (`D-24`).

## Critério de conclusão da fase

**O usuário usa o ditado deste app no dia a dia, no lugar do que usa hoje.** Não é "está pronto": é
uso em regime. A régua de qualidade é **não piorar o que ele já usa** (`D-10`).

## O que a Fase 1 deixou pendente, e que se prova aqui

A Fase 1 entregou tudo, mas o critério dela — *"alguém escreve um cliente novo lendo só o contrato,
sem abrir o `index.html` nem o `main.py`"* — só se prova com um cliente novo de verdade. **O app de
desktop da Etapa 1 é esse cliente**, e é melhor prova do que a PoC seria: é um cliente que vai ficar
em uso, não um exercício. Se o contrato não bastar, a Fase 1 volta com evidência de uso real.

## Escopo

- **Dentro**: o app de desktop mínimo (`D-25`); as histórias, os entregáveis e a definição de MVP
  (`D-13`); o app desktop para Windows com a camada de inserção **isolada** (`D-11`); atalho
  configurável como acionamento principal (`D-01`); os três estados da janela (`D-15`); e a segunda
  ação, "colocar a última transcrição no campo em foco", com atalho próprio.
- **Fora (explícito)**: Android e smartwatch (F3, F4); agente e integração com LLM (F5 em diante);
  o modo ao vivo, congelado (`D-02`); servidor próprio (`D-05`); a **investigação de mecanismos de
  inserção**, adiada para `B-22` (`D-25`); e o seletor de idioma, desparqueado por medição (`D-08`).

## Etapas

> **Poucas, e é de propósito.** A regra do método é teorizar uma fase e fazer: a lista completa de
> entregáveis desta fase é a **Etapa 3**, e as etapas seguintes se escrevem depois dela. E desde
> 2026-08-25 a **Etapa 1 deixou de ser investigação e virou construção** (`D-25`) — o que o app
> precisa aprender, ele aprende sendo usado.
>
> **Regra que nasceu da reprovação de 2026-08-27:** qualquer tarefa desta fase que **desenhe
> interface** passa antes por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` e por
> `spec/specs/SPEC-002_paridade-desktop.md`. Não é só da Etapa 3.

1. **[App de desktop — paridade com a interface web]** — **reaberta em 2026-08-27.**

   Foi dada por concluída com ressalvas em 26/08 e **reprovada no uso** em 27/08. O usuário rodou o
   app: *"ficou horrível. Eu consegui usar, mas ele não grava direito. Esse F17 ou F9 é uma péssima
   tecla para apertar. Você não implementou as coisas que tem no HTML aqui, que era o básico"*. A
   régua da fase é **não piorar o que ele já usa** (`D-10`) — e o que ele já usa é a interface web.
   Entregar abaixo dela não é etapa concluída com ressalva; é etapa que não cumpriu o critério.

   **Erro é meu, e é de escopo, não de execução.** Escrevi a tarefa como "atalho, gravar,
   transcrever, clipboard" **sem passar por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md`**, que
   desde 21/08 dizia que a interface web é o desenho de referência do desktop e listava o que
   transcrever. O plano manda passar por esse arquivo — mas mandava só na Etapa 3, ao escrever as
   histórias. Passou a valer para **qualquer** tarefa que desenhe interface desta fase.

   **Escopo novo**: [`spec/specs/SPEC-002_paridade-desktop.md`](../../spec/specs/SPEC-002_paridade-desktop.md)
   — a frase "no mínimo o mesmo que o HTML" virada em lista conferível (A a I, aparência
   inclusa), com o que **não** transporta e o que fica para depois. É o critério de pronto desta
   etapa, e **não se entrega em partes** (`D-29`).

   **O que a primeira volta deixou de pé e não se joga fora**: `desktop/app.py` provou o caminho
   ponta a ponta contra o núcleo real, o tratamento de erro pelo campo `codigo` (não pelo texto), e
   a resposta ao critério da Fase 1 — **o contrato bastou**, com uma lacuna só (não declarava onde o
   núcleo escuta), fechada em `spec/contrato/NUCLEO.md` em 26/08. Duas transcrições reais saíram do
   app em 27/08 às 04:25. O caminho funciona; a interface é que ficou abaixo da régua.

   **Estado em 2026-08-27, fim do dia**: a paridade da `SPEC-002` foi entregue e o app está **em uso**.
   A etapa passou de construção para **acabamento**: os pedidos agora nascem do uso, não da lista. As
   duas primeiras divergências deliberadas em relação à interface web estão declaradas na `D-30` —
   corte de segurança de 5 min e recortar como padrão.

   **Dívida a pagar junto** (`D-11`): `pyperclip.copy(texto)` está inline dentro de
   `_processar_gravacao`. Tem de virar função isolada — é exatamente o pedaço que a inserção
   automática (`B-22`) vai trocar.

2. **[POC-1 — investigação de inserção]** — **interrompida por achado, e o achado vale mais que a
   matriz.** Executada parcialmente em 2026-08-25, antes do corte de escopo. Quatro tentativas de
   injeção falharam **em silêncio**; a causa foi isolada e virou **`D-26`**: a inserção tem de
   disparar de dentro do handler do atalho global, senão o Windows não entrega. A matriz 4×3 ficou
   em branco não por omissão, mas porque repeti-la do jeito antigo só reproduziria o mesmo falso
   negativo. Todo o material está em `spec/pocs/POC-1/` e o que se aprendeu está em `B-22`.

3. **[Histórias, entregáveis e MVP]** — PM com o usuário, não Executor (`D-13`). Escrever as
   histórias de usuário, a lista de entregáveis da fase e a definição declarada de MVP. Fecha as
   lacunas `L-A`, `L-B` e `L-C`.
   — **Obrigatório**: passar por `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` antes de escrever a
   primeira história. Ele já traz três coisas decididas para esta fase — a interface web como
   desenho de referência (transcrever, não reinventar), a ação "colocar a última transcrição" com
   atalho próprio e inserção a partir da memória do app (nunca da área de transferência), e o que
   **não** se transporta: hover como gatilho, e o modo ao vivo.
   — Pode começar em paralelo à Etapa 1, mas **a parte que depende do mecanismo de inserção só
   fecha depois dela**.

4. **[Escrever o resto do plano]** — PM. Com o app mínimo **em uso** e o MVP definido, as etapas
   seguintes se escrevem com base no que o uso mostrou — inclusive se a inserção automática (`B-22`)
   volta do backlog.
   — Critério de pronto: um plano de fase com etapas verificáveis, aprovado pelo usuário.

## Backlog

O acervo de ideias mora em [`spec/BACKLOG.md`](../../spec/BACKLOG.md). **Ao fechar cada etapa desta
fase**, ler os itens marcados com `olhar de novo em: F2` e perguntar ao usuário quais sobem. Hoje
são: `B-05` (adiantamento de exibição no streaming), `B-06` (consolidar as três histórias de entrega
do texto) e `B-11` (histórico por projeto). `B-01` (arrastar e soltar) **subiu em 2026-08-27**, a
pedido do usuário, e virou o item `E2` da `SPEC-002`.

## Nota de processo (deste projeto)

- **Armadilha da porta 8000: 6 ocorrências.** Confira e derrube backend antigo antes de qualquer
  medição. A última foi em 2026-08-24, o Executor pegou.
- **Tarefa que quebre o `.env` ou o backend avisa o usuário ANTES de começar** — ele usa o app ao
  vivo. Funcionou na Etapa 3 da Fase 1.
- **Microfone real já foi exercitado** em 2026-08-27: duas transcrições de fala saíram do app de
  desktop às 04:25 (US$ 0,0003 no total). A cadeia inteira — microfone, envio, transcrição, texto de
  volta — funciona. O que reprovou foi a interface, não o caminho.
- Preços de referência consultados em 2026-08-19 (conferir antes de decisão de custo):
  `gpt-transcribe` US$ 0,0045/min; `gpt-live-transcribe` US$ 0,017/min. O limite de 25 MB de áudio
  foi conferido na documentação da OpenAI em 2026-08-24.
- As regras de método — consistência, higiene, tipos de plano, commit — moram em `.claude/metodo/`.
  Não repita nenhuma aqui.
