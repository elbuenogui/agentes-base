# PLANO — Transcrição como serviço para a Mari

> Plano de **fase**, aberto em **2026-09-30** e aprovado pelo usuário no mesmo dia, com ajustes
> ("números perfeitos"). Nasce do `B-27` e da decisão `D-37`. Virada: o plano **Núcleo centralizado
> no Supabase** foi encerrado (`historico/PLANO_2026-09-30_nucleo-remoto-encerrado.md`) e o critério
> de uso dele é observado em `ACOMPANHAMENTO.md` (`A-01`). Não é uma fase da sequência do assistente
> (`spec/VISAO.md`): é o RAG-COMPARTILHADO virando projeto de serviços (`D-36`, nota da Etapa 1).

## Objetivo

A Mari transcreve o áudio de quem usa o site pelo RAG-COMPARTILHADO — recurso de acessibilidade.
A chamada sai do servidor dela com chave própria, o gasto tem teto, e o texto não é guardado.

## Critério de conclusão do plano

**Uma chamada real do servidor da Mari, com um áudio gravado no navegador, volta transcrita, e o
consumo aparece no banco como projeto `mari`, sem texto.**

## Escopo

- **Dentro**: uma Edge Function nova no RAG-COMPARTILHADO, separada da `transcrever` pessoal; uma
  **chave de acesso do serviço por projeto cliente**, que decide o projeto (o corpo não escolhe);
  a chamada à OpenAI feita com a **chave da OpenAI da própria Mari**, para o gasto cair na mesma
  conta que o resto da Mari (usuário, 2026-09-30); uma tabela de consumo por projeto **sem coluna de
  texto**; os limites abaixo; o contrato do serviço; e os **prompts de integração** para o projeto
  do servidor da Mari, escritos pelo PM a partir do contrato.
- **Fora (explícito)**: o código do lado da Mari — gravação no navegador e servidor, que está sendo
  migrado para a UrbVerde — é executado lá, a partir dos prompts; streaming (lote basta para
  devolver o texto); guardar o texto transcrito (`D-37`); login de quem usa o site; `diarize`;
  qualquer mudança na `transcrever` e na `consumo` pessoais e nas funções `buscar`/`ingerir` (e no
  `RAG_CHAVE_ACESSO` delas); observabilidade centralizada dos gastos (`B-28`).

## Limites (aprovados pelo usuário em 2026-09-30)

- Áudio de até **2 min** e **4 MB**. O tamanho é conferido pela função; a duração é obrigação do
  cliente (a gravação para em 2 min).
- Modelo fixo: **`gpt-4o-transcribe`** — o cliente não escolhe.
- Teto de gasto: **US$ 1 por dia por projeto**, no dia de `America/Sao_Paulo`, conferido **antes**
  de chamar a OpenAI.
- Frequência por pessoa: obrigação do servidor da Mari, o único que sabe quem é quem.

## Etapas

1. **[Registro de consumo por projeto]** — **CONCLUÍDA em 2026-09-30**, conferida pelo PM no
   banco: migrações `rag_base, assistente_base, servicos_base`; 11 colunas, três `check`; RLS sem
   política; ACL só `service_role=ar`; `gasto_do_dia` executável só pelo `service_role`; 0 linhas.
   O INFO `rls_enabled_no_policy` do advisor é o desenho, aceito pelo PM. Critério de pronto: schema `servicos` com uma tabela de
   uso da transcrição (projeto, momento, modelo, custo, tokens, bytes, `codigo` do resultado),
   **sem nenhuma coluna de texto livre**; RLS ligado e nenhuma política — `anon` e `authenticated`
   não leem nem gravam; aplicada como migração avulsa com nome prefixado (nunca `db push`, como na
   `D-36`) e SQL versionado em `nucleo-remoto/banco/`; conferido por consulta.

2. **[Função do serviço]** — **CONCLUÍDA em 2026-09-30**: `transcrever-servico` v6 (`ezbr_sha256` `c2b0bda6…`), 5 de 5 no Windows na segunda rodada (a primeira travou em `503`: resposta antecipada sem ler o corpo — Correção 1, drenar o corpo); no banco, 3 linhas `mari` (`413`, sucesso a US$ 0,00162, `429`), nenhuma para os `401`, sem texto; as quatro funções existentes com o mesmo `ezbr_sha256`. Critério de pronto: a função implantada com `verify_jwt: false`,
   autenticando pela chave do serviço; teste real no Windows (a máquina remota não alcança o
   Supabase): sem chave `401`; chave errada `401`; áudio real `200` com a transcrição; arquivo acima
   de 4 MB `413`; teto do dia atingido `429` (provocado com teto rebaixado só para o teste); a linha
   no banco com projeto e custo, sem texto; a `transcrever` pessoal com o mesmo `ezbr_sha256` de
   antes; chaves só nos segredos do Supabase, digitadas pelo usuário.

3. **[Contrato do serviço]** — critério de pronto: `spec/contrato/SERVICO_TRANSCRICAO.md` com
   endereço, autenticação, limites, códigos de erro e as **obrigações do cliente** (chamar só do
   servidor; limitar por pessoa; parar a gravação em 2 min; descartar silêncio antes de enviar,
   porque a API alucina texto em silêncio — L6 do `NUCLEO.md`, `D-16`; não guardar o áudio),
   apontando para o `NUCLEO.md` no que for igual; cada afirmação marcada como medida ou lida no
   código, como no contrato 2.

4. **[Prompts de integração]** — feita pelo **PM**, a pedido do usuário (2026-09-30). Critério de
   pronto: prompts autocontidos para o projeto do servidor da Mari, um por tarefa do lado de lá,
   cada um citando o contrato da Etapa 3 e dizendo o que o agente de lá **não** faz (guardar
   texto, chamar do navegador, guardar a chave no front); entregues ao usuário e guardados em
   `spec/contrato/`.

5. **[Chamada real da Mari]** — critério de pronto: o critério de conclusão do plano, conferido
   pelo PM no banco.

## Backlog

O acervo de ideias mora em [`spec/BACKLOG.md`](../../spec/BACKLOG.md). Ao fechar cada etapa, ler os
itens que tocam este plano e perguntar ao usuário quais sobem.

## Nota de processo (deste plano)

- **Não mexer no ditado de todo dia**: nenhuma tarefa altera a `transcrever`, a `consumo`, o
  schema `assistente` ou o `desktop/`. Se precisar, avisa o usuário antes.
- **Credenciais**: a chave da OpenAI da Mari e a chave do serviço **nunca** entram no chat, em log
  ou no git. Quem digita segredo é o usuário.
- **Commit só com autorização explícita, por commit** (`M-05`).
- As regras de método moram em `.claude/metodo/`. Não repita nenhuma aqui.
