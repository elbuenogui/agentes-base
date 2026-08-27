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

> **Só três, e é de propósito.** A regra do método é teorizar uma fase e fazer: a lista completa de
> entregáveis desta fase é a **Etapa 2**, e as etapas seguintes se escrevem depois dela. E desde
> 2026-08-25 a **Etapa 1 deixou de ser investigação e virou construção** (`D-25`) — o que o app
> precisa aprender, ele aprende sendo usado.

1. **[App de desktop mínimo — atalho global, gravar, transcrever, clipboard]** —
   **concluída com ressalvas (2026-08-26)**. Conferida pelo PM no artefato real.

   **O que está pronto e conferido**: `desktop/app.py` com atalho configurável em `config.json`, gate
   de silêncio por RMS (testado com números — silêncio `0.0`, tom `~0.17`, limiar `0.01`), erros
   tratados pelo campo `codigo` e não pelo texto, texto no clipboard confirmado lendo de volta, e um
   `README.md` que diz o que o app **não** faz. Nada de `transcritor/` tocado.

   **O critério da Fase 1 foi respondido**: o contrato **bastou**, com uma lacuna só — ele não
   declarava onde o núcleo escuta. Dois clientes independentes tropeçaram na mesma coisa. Lacuna
   fechada em `spec/contrato/NUCLEO.md` em 2026-08-26.

   — **Ressalva 1, depende do usuário**: dois critérios não foram testados porque o ambiente do
   Executor não tem microfone nem teclado físico — **o atalho com outra janela em foco** e **a
   captura por microfone real**. A lógica foi revisada por leitura, não exercida. Rodar
   `python desktop/app.py` uma vez resolve.

   — **Ressalva 2, desvio encontrado pelo PM**: a instrução pedia que o clipboard fosse chamado por
   **uma função própria e isolada** (`D-11`), para a inserção automática entrar depois trocando só
   aquele pedaço. O `pyperclip.copy(texto)` ficou **inline** no meio de `_processar_gravacao`. É
   pequeno de consertar agora e caro de consertar depois — vai como primeiro item da próxima tarefa.

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
são: `B-01` (arrastar e soltar áudio), `B-05` (adiantamento de exibição no streaming), `B-06`
(consolidar as três histórias de entrega do texto) e `B-11` (histórico por projeto).

## Nota de processo (deste projeto)

- **Armadilha da porta 8000: 6 ocorrências.** Confira e derrube backend antigo antes de qualquer
  medição. A última foi em 2026-08-24, o Executor pegou.
- **Tarefa que quebre o `.env` ou o backend avisa o usuário ANTES de começar** — ele usa o app ao
  vivo. Funcionou na Etapa 3 da Fase 1.
- **Falta um teste manual de gravação por microfone** depois das mudanças da Etapa 3 da Fase 1. O
  Executor exercitou o mesmo caminho de código por upload no navegador, mas não é o mesmo teste.
- Preços de referência consultados em 2026-08-19 (conferir antes de decisão de custo):
  `gpt-transcribe` US$ 0,0045/min; `gpt-live-transcribe` US$ 0,017/min. O limite de 25 MB de áudio
  foi conferido na documentação da OpenAI em 2026-08-24.
- As regras de método — consistência, higiene, tipos de plano, commit — moram em `.claude/metodo/`.
  Não repita nenhuma aqui.
