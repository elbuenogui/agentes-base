---
name: encerrar-chat
description: Fecha um chat de PM ou de Executor deixando o projeto retomável em outro chat — consolida a coleta, atualiza o estado e reescreve a retomada. Use quando a pessoa disser "pode encerrar", "vamos fechar o chat", "encerrar por aqui", ou pedir para preparar a retomada para outro chat.
---

# Encerrar chat

O estado deste projeto mora em arquivo, não em conversa — é o que permite trocar de chat sem perder
nada. Encerrar bem é o que mantém essa promessa verdadeira. Um chat que termina sem isso deixa o
próximo tendo de reconstruir contexto por rolagem, que é exatamente o que o método existe para
evitar.

## Os quatro passos, nesta ordem

### 1. Consolidar a coleta
Seguir a skill `coleta-consolidacao`: um arquivo `coleta/AAAA-MM-DD_<tema>.md` por chat, com a
seção 1 de registro por interação (`[DECISÃO]` sempre com trade-off, `[ARTEFATO]` com caminho,
`[DIRECIONAMENTO]`, `[PENDÊNCIA]` sempre com "depende de") e a seção 2 com o resumo nas quatro
categorias. Datas relativas viram absolutas.

### 2. Atualizar o estado
- `.claude/estado/PLANO.md`: marcar etapas concluídas **com o que foi conferido no artefato real**,
  não com "feito". Etapa cancelada não se apaga — riscar e guardar o texto original em `<details>`,
  com o motivo.
- `spec/DECISOES.md`, `QUESTOES_ABERTAS.md`, `LACUNAS.md`: decisões novas, questões respondidas,
  lacunas fechadas. Decisão **revisada por medição** mantém o texto antigo em `<details>` — o
  histórico do porquê é o que impede reabrir por esquecimento.
- `.claude/estado/PROGRESSO.md`: **não se edita**. É canal do Executor, append-only. Se o plano
  virou, arquivar em `historico/` movendo palavra por palavra e conferindo a contagem de linhas.

### 3. Reescrever a retomada
`_RETOMADA_usabilidade-gravacao.md`, na raiz (o nome ficou do plano antigo de propósito, para não
quebrar referências; o conteúdo é sempre o atual). Deve conter, nesta ordem: o que ler e em que
ordem; onde o projeto está; **qual é o próximo passo e de quem ele é**; o que ficou pendente do
usuário; o que não se reabre; e as armadilhas do ambiente.

### 4. Deixar a fila honesta
Se não houver tarefa para o Executor, `PROXIMA_TAREFA.md` **diz isso em voz alta** — não fica com a
tarefa velha. Esse arquivo já envelheceu duas vezes neste projeto apontando para etapa concluída, e
o Executor quase reexecutou.

## Fechar com o painel

Terminar publicando o **diagnóstico geral** (skill `diagnostico-geral`), no endereço fixo. O painel
atualizado é a última coisa que o usuário vê, e é dele que o próximo chat parte.

## Trava

Nada aqui inventa conteúdo. Consolidação e retomada registram o que aconteceu no chat e o que está
nos arquivos. Proposta do assistente entra marcada como proposta, e decisão é sempre de quem conduz
o projeto.
