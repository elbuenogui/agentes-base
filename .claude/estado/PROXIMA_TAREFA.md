# Tarefa: Contrato do serviço
Referente à etapa 3 do PLANO.md

## Contexto
A função `transcrever-servico` está no ar e passou 5 de 5 no Windows (Etapa 2). Agora falta o
documento que um agente do projeto do servidor da Mari lê para integrar **sem abrir o código**. Ele
é a base dos prompts de integração que o PM escreve na Etapa 4. O modelo de escrita é o contrato 2
(`spec/contrato/NUCLEO.md`): cada afirmação marcada como medida ou lida no código.

## Arquivos envolvidos
- `spec/contrato/SERVICO_TRANSCRICAO.md` (novo)
- `nucleo-remoto/README.md` (uma linha apontando o contrato novo, junto das linhas da Etapa 2)

## Fontes (ler antes de escrever)
- `nucleo-remoto/funcoes/transcrever-servico/index.ts` — o código implantado (v6)
- `nucleo-remoto/banco/servicos_base.sql` — o registro e o `gasto_do_dia`
- `nucleo-remoto/testes/testar_servico.log` — a **segunda** execução, de 2026-09-30T17:53 (a
  primeira, de 17:34, é a que travou antes da Correção 1)
- `.claude/estado/PROGRESSO.md` — as entradas da Etapa 2 e da Correção 1
- `spec/contrato/NUCLEO.md` — **só** o cabeçalho (como marcar medido/código), a seção "L6 — Áudio
  sem fala" e a "Operação 1 no núcleo remoto", para apontar em vez de repetir
- `spec/DECISOES.md` — só a `D-16` e a `D-37`

## O que fazer

1. Escrever `spec/contrato/SERVICO_TRANSCRICAO.md` com o mesmo tipo de cabeçalho YAML do
   `NUCLEO.md` (`artefato`, `origem: PLANO 2026-09-30, Etapa 3`, `medido_em`, `status`) e a mesma
   legenda de marcas: **[medido]**, **[código]**, **[código + teste local]**, **[documentação]**.
   Ele deve responder, nesta ordem:
   1. **Para que serve e para quem**: projetos clientes que chamam do **servidor**; hoje só `mari`.
   2. **Endereço e método**: URL completa, `POST`, `multipart/form-data`, campo `audio`; outros
      campos ignorados.
   3. **Autenticação**: cabeçalho `x-servico-chave`; o projeto sai da chave; sem JWT
      (`verify_jwt: false`); a chave mora num segredo por projeto e é trocada **sobrescrevendo o
      segredo** (a chave antiga para de valer). O nome do segredo pode aparecer; valor, nunca.
   4. **Resposta de sucesso**: `200 {"transcricao": ...}`, o cabeçalho `X-Servico-Contrato: 1` e o
      que ele significa para o cliente (versão do contrato; o que muda a versão).
   5. **Limites**: 4 MB (conferido pela função), 2 min (obrigação do cliente, não conferido), modelo
      fixo, teto diário por projeto (padrão, segredo que o muda, o que é "dia"), prazo de 120 s da
      chamada à OpenAI.
   6. **Tabela de erros**: status, `codigo`, quando acontece, se registra linha, se custa, e o que
      o cliente deve fazer (repetir ou não, avisar a pessoa com que mensagem). Todos os códigos da
      função, na ordem em que são conferidos.
   7. **Sem CORS**, e por quê.
   8. **O que é registrado** (colunas de `servicos.transcricao_uso`) e **o que nunca é** (texto,
      áudio, chave); quem pode ler o registro.
   9. **Obrigações do cliente**, uma por item, cada uma com o motivo: chamar só do servidor e nunca
      pôr a chave no front; limitar por pessoa; parar a gravação em 2 min; **descartar silêncio**
      antes de enviar (apontar para a L6 do `NUCLEO.md` e para a `D-16`, sem copiá-las); não
      guardar o áudio; não guardar o texto além do necessário para devolvê-lo à pessoa; tratar
      `429`, `503` e prazo esgotado.
   10. **Riscos aceitos**, cada um com o que significa na prática: teto não atômico (chamadas
       simultâneas passam juntas pela conferência); `TEMPO_ESGOTADO` registra custo 0 embora a
       OpenAI possa ter cobrado; requisição sem chave faz a função ler o corpo inteiro (Correção 1);
       banco fora do ar derruba o serviço (`503 LIMITE_INDISPONIVEL`, falha fechada).
   11. **O que é igual ao núcleo pessoal e o que não é**: apontar para o `NUCLEO.md` onde valer
       igual (tradução de erros da OpenAI, alucinação em silêncio); dizer onde difere (chave em vez
       de login, sem escolha de modelo, sem streaming, sem texto guardado).
   12. **Como verificar**: o `testar_servico.cmd` e o que ele prova.
2. Marcar **cada afirmação**: **[medido]** só o que o log de 17:53 ou a conferência do PM no banco
   mostram (as 3 linhas: `413` sem custo e modelo nulo; sucesso com `gpt-4o-transcribe`,
   US$ 0,00162, 320/82 tokens, 2182 ms; `429` sem custo; nenhuma linha para os `401`). O resto é
   **[código]** ou **[código + teste local]**. Os tempos medidos (0,8 a 2,7 s) entram como
   observação de uma rodada, não como garantia.
3. Não repetir o que já mora noutro documento — apontar (`metodo/CONSISTENCIA.md`).
4. Acrescentar a linha do contrato ao `nucleo-remoto/README.md`.

## Critério de pronto
- [ ] `spec/contrato/SERVICO_TRANSCRICAO.md` cobre os 12 pontos, com cada afirmação marcada
- [ ] nada no documento contradiz o `index.ts` v6 (o Executor confere código × documento item a
      item, e lista no PROGRESSO os pontos em que o documento diz algo que o código não faz)
- [ ] nenhum valor de segredo, nenhum texto transcrito
- [ ] o `NUCLEO.md` não foi tocado

## Registro no PROGRESSO
curto

## O que NÃO fazer
- Não alterar a função, os testes, o banco, o `NUCLEO.md` nem nenhum outro arquivo fora da lista
- Não implantar nada, não chamar a função real
- Não escrever os prompts de integração (Etapa 4, do PM)
- Não commitar (`M-05`)
