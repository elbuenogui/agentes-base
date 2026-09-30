# ACOMPANHAMENTO — o que se observa, sem Executor

> Tipo de plano descrito em `../metodo/PLANOS.md`. Cada item diz o que se mede, onde se lê, o valor
> de referência e o que fazer quando encostar. Item que termina sai daqui para a `coleta/`.

## A-01 — O núcleo remoto em uso no dia a dia
`aberto em: 2026-09-30 · olhar até: 2026-10-07 · nasceu: critério de conclusão do plano Núcleo centralizado no Supabase (historico/PLANO_2026-09-30_nucleo-remoto-encerrado.md), que virou acompanhamento por decisão do usuário`

- **O que se mede**: (1) linhas novas nos `.jsonl` do núcleo local; (2) ditados com
  `origem = 'nucleo-remoto'` por dia; (3) se a sessão do desktop sobrevive de um dia para o outro
  sem pedir login.
- **Onde se lê**: (1) contagem de linhas de `transcritor/consumo.jsonl` e
  `transcritor/transcricoes.jsonl`; (2) consulta em `assistente.consumo` pelo conector do Supabase
  (só leitura), agrupada pelo dia em `America/Sao_Paulo`; (3) `desktop/app.log` (`sessao: login ok`
  × `sessao: renovada`).
- **Valor de referência** (medido no fechamento, 2026-09-30 16:28): `.jsonl` em **1867** e **1807**
  linhas, última escrita às 14:28; ditados remotos em todo dia em que o usuário usar o app.
- **O que fazer quando encostar**:
  - `.jsonl` cresceu → descobrir quem gravou (interface web, `url_nucleo` apontado para o local) e
    trazer para o banco com `nucleo-remoto/banco/importar_historico.cmd`, que não duplica;
  - o usuário voltou para o núcleo local por falha do remoto → a `D-36` reabre (condição escrita nela);
  - login pedido de novo sem motivo → vira `B-nn`.
- **Termina** em 2026-10-07 se nada disso acontecer: uma semana cobre também a janela em que o
  plano gratuito pausa projeto parado.
