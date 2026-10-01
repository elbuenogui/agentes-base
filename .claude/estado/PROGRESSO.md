# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de **2026-09-30** (encerramento do plano **Núcleo centralizado no
> Supabase**). As entradas dele estão em `historico/PROGRESSO_nucleo-remoto_2026-09-30.md`, e as dos
> planos anteriores nos outros `historico/PROGRESSO_*.md`, todas sem edição.

*(Sem entradas ainda — a primeira nasce quando o Executor concluir a primeira tarefa do próximo plano.)*

## [2026-09-30 16:56] — Serviço de transcrição para a Mari (D-37), Etapa 1: Registro de consumo por projeto
Status: concluído (um item do critério pede leitura do PM — advisors, abaixo)

### Feito
- `nucleo-remoto/banco/servicos_base.sql` (novo): schema `servicos`, tabela `transcricao_uso` com os 3 `check` nomeados, índice `(projeto, "timestamp")`, função `gasto_do_dia` (sql, stable, invoker, `search_path = ''`), RLS sem política, revoke/grant. O revoke da tabela e da função inclui `service_role` antes do grant, para não herdar update/delete de privilégio padrão.
- `nucleo-remoto/README.md`: uma linha na tabela de arquivos, logo abaixo de `assistente_base.sql`.
- Supabase: `apply_migration` `servicos_base` (versão 20260930195434). SHA-256 do `statements` gravado = SHA-256 do arquivo = `918f7818…c847`. `assistente_base` no banco = SHA do arquivo (`27a8144f…f617`); `rag_base` com a mesma versão/nome de antes.
- Conferido por consulta: 11 colunas conforme a tarefa; 3 `check` (`projeto`, `modelo`, `codigo`) + pk. ACL tabela `{postgres=arwdDxtm, service_role=ar}`, função `{postgres=X, service_role=X}`, schema `{postgres=UC, service_role=U}`. `has_table_privilege` select/insert/update/delete: anon e authenticated todos `false`; service_role select/insert `true`, update/delete `false`. `has_function_privilege` execute: anon/authenticated `false`, service_role `true`.
- Teste em bloco `do` que termina em `raise exception` (desfaz tudo), inserts como `set local role service_role`: linha de `now()` com 0.0123 e linha de 5.00 em 23:59:59 de ontem em SP (`inicio_sp` = 2026-09-30 03:00:00+00) → `gasto_do_dia('teste')` = **0.0123**; `'Mari com espaço'` recusado por `transcricao_uso_projeto_check`; como `anon`, insert negado (`permission denied for schema servicos`). Depois: 0 linhas; `gasto_do_dia('teste')` sem linha = 0.
- Idempotência: reexecutei os comandos do arquivo por `execute_sql` (sem registrar migração): sem erro, ACLs e 3 `check` iguais, `schema_migrations` = `rag_base,assistente_base,servicos_base`.
- Não testado: a exposição na API de dados não é legível por SQL (não há `pgrst.db_schemas` no `rolconfig` do `authenticator`); não mexi nela. Mesmo exposto, anon/authenticated não têm `usage` no schema.

### Critério de pronto
- [x] `servicos_base.sql` versionado, idempotente, igual ao que foi aplicado
- [x] migração `servicos_base` aplicada; `rag_base` e `assistente_base` intactas
- [x] tabela sem coluna de texto livre (os três `check` conferidos, e o insert inválido recusado)
- [x] `anon` e `authenticated` sem acesso à tabela e à função; `service_role` com select, insert e execute
- [x] `gasto_do_dia` soma só o dia corrente de São Paulo (teste em transação desfeita)
- [x] tabela vazia no fim; schema não exposto na API — não exposto por mim; a lista de schemas expostos não é consultável pelo conector
- [ ] nenhum aviso novo de segurança sobre `servicos` — nenhum WARN/ERROR novo; surgiu 1 **INFO** `rls_enabled_no_policy` sobre `servicos.transcricao_uso`, consequência direta do "RLS ligado e nenhuma política" pedido (o mesmo INFO que já existe para `rag.buscas` e `rag.trechos`). PM decide se aceita.

### Novas demandas / riscos
- Advisor preexistente, fora do escopo: WARN `auth_leaked_password_protection` (proteção contra senha vazada desligada no Auth).
- `git diff` mostra outros arquivos já modificados antes desta tarefa (`.claude/estado/PLANO.md`, `PROXIMA_TAREFA.md`, `coleta/…`, `spec/*`, `desktop/app.log`); não são desta etapa.

### Ajuste no plano necessário?
Não.

## [2026-09-30 17:14] — Serviço de transcrição para a Mari (D-37), Etapa 2: Função do serviço
Status: parcial — Parte A concluída; Parte B (usuário, Windows) e Parte C (PM) pendentes

### Feito
- `nucleo-remoto/funcoes/transcrever-servico/index.ts` (novo, 378 linhas, só `npm:postgres@3.4.5`): tabela `PROJETOS` com `mari`; chave comparada em tempo constante (SHA-256 dos dois lados, XOR dos 32 bytes, todos os projetos percorridos; segredo < 32 caracteres = desligado); verificações na ordem 1–9 da tarefa; teto = `SERVICO_TETO_DIARIO_USD` (ausente/vazio/inválido/negativo = 1.00; `0` é válido); `X-Servico-Contrato: 1` em toda resposta, sem CORS; linha de uso depois da chave, inclusive nos erros (`atender`); log só com nome e código do erro (`descreverFalha`).
- Banco: um cliente `postgres` por requisição, `max: 1`, `prepare: false`, `connect_timeout: 10`, `idle_timeout: 5` (mesmas opções do `usarBanco` do RAG), fechado no `finally`; cada acesso em `begin` + `set local role service_role`. Conferi no banco real, em transação desfeita: `postgres` é membro de `service_role` e `gasto_do_dia('mari')` = 0 com o papel trocado.
- `nucleo-remoto/testes/testar_servico.py` e `.cmd` (novos): casos 1–5 da tarefa + aviso de apagar o teto; `.cmd` com CRLF (45/45 linhas), só ASCII, mesmo corpo do `testar_transcrever.cmd`. No caso 5, "até 3 vezes" = 1 tentativa + até 3 novas (20 s entre elas).
- `nucleo-remoto/README.md`: 2 linhas na tabela. `.gitignore` sem mudança (`nucleo-remoto/testes/*.log` já cobre).
- `ezbr_sha256` antes = depois: `transcrever` 6f35bb5e…31cf, `consumo` 474bd2d9…2967, `buscar` 536f59b0…16ad, `ingerir` 698685b7…1a7a (todas versão 5). Nova: `transcrever-servico` versão 1, `verify_jwt: false`, `ezbr_sha256` 69c2721b…cb3d.
- Implantado = versionado: o conteúdo devolvido por `get_edge_function`, gravado e comparado byte a byte (`cmp`), tem o mesmo SHA-256 do arquivo: `e16b2c12…dedd` (14185 bytes).
- Teste local na máquina de nuvem (Deno 2.9.6 + Postgres 16 local com `servicos_base.sql` + OpenAI falsa): **18 de 18** — 405; 401 sem chave, com chave errada e com segredo curto; 422 JSON e sem `audio`; 400; 413 com 4 MB+1; 200 com 4 MB exatos; 200 ignorando `modelo`/`stream`/`projeto` (a OpenAI falsa recebeu só `model=gpt-4o-transcribe` e `file`); 429 com teto 0; 200 com teto `abc`; 503 SEM_CHAVE; 503 LIMITE_INDISPONIVEL com banco fora e sem `SUPABASE_DB_URL`; 502 SEM_CONEXAO, FALHA_AUTENTICACAO (detail cita `OPENAI_API_KEY_MARI`) e API_RECUSOU. Banco: 12 linhas (nenhuma para 405/401), custo 0.00045 nos sucessos (100+20 tokens), `codigo` nulo só neles; 0 conexões abertas no fim; log da função sem texto nem chave.
- O `testar_servico.py` (URL trocada para a local) rodou inteiro contra essa função: **5 de 5**, com o caso 5 passando na 3ª tentativa (teto trocado com atraso de propósito, para exercitar as novas tentativas); log sem texto nem chave.
- Não testado: nada contra a função real (a nuvem não alcança o Supabase); `TEMPO_ESGOTADO` (esperaria 120 s); o `.cmd` no Windows.

### Critério de pronto
- [x] função `transcrever-servico` implantada com `verify_jwt: false`, igual ao versionado
- [x] as quatro funções existentes com o mesmo `ezbr_sha256` de antes
- [ ] teste real no Windows: casos 1–5 passam (Parte B) — pendente, com o usuário
- [ ] no banco: linhas do projeto `mari` para os casos 3, 4 e 5 (nenhuma para 1 e 2), a do caso 4 com custo e `codigo` nulo, a do 5 com `LIMITE_DIARIO`; nenhuma coluna com texto (Parte C, PM) — pendente; `servicos.transcricao_uso` tinha 0 linhas antes da implantação
- [ ] `SERVICO_TETO_DIARIO_USD` apagado no fim (confirmado pelo usuário) — pendente
- [x] chaves só nos segredos do Supabase — nada em arquivo, log ou chat (da parte do Executor; o resto depende da Parte B)

### Parte B — passo a passo para o usuário
1. **Antes de tudo**, no painel do Supabase, projeto **rag-compartilhado** → **Edge Functions → Secrets**: confira que **não existe** o segredo `SERVICO_TETO_DIARIO_USD`. Se existir, apague. (Com ele valendo 0, o caso 4 volta `429` em vez de `200`.)
2. **Gerar a chave do serviço.** Abra o PowerShell e cole esta linha inteira; ela gera uma chave aleatória de 43 caracteres e copia para a área de transferência (nada aparece na tela):
   `$b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_') | Set-Clipboard`
3. Em **Edge Functions → Secrets**, crie `SERVICO_CHAVE_MARI` e cole a chave como valor (Ctrl+V), sem espaço nem quebra de linha. Salve.
4. **Guarde essa mesma chave num lugar seguro** (gerenciador de senhas), agora, antes de copiar outra coisa: ela vai para o servidor da Mari na Etapa 5. Não cole no chat nem em arquivo do repositório.
5. Ainda em **Secrets**, crie `OPENAI_API_KEY_MARI` com a **mesma chave da OpenAI que a Mari usa**. Salve.
6. Copie de novo a `SERVICO_CHAVE_MARI` do lugar seguro e dê dois cliques em `nucleo-remoto\testes\testar_servico.cmd`. Quando ele pedir a chave, cole com **clique direito** na janela (o Ctrl+V pode não funcionar nesse campo) e tecle Enter. Nada aparece na tela; a linha seguinte deve dizer `Chave recebida (43 caracteres).`
7. Os casos 1 a 4 rodam sozinhos (o 4 é uma chamada paga de centavos).
8. **Caso 5:** quando ele pausar, vá em **Secrets**, crie `SERVICO_TETO_DIARIO_USD` com o valor `0`, salve, volte à janela e tecle Enter. Se a função ainda estiver com o valor velho, ele espera 20 s e tenta de novo (até 3 vezes) — pode levar pouco mais de um minuto.
9. **No fim, apague `SERVICO_TETO_DIARIO_USD`** em **Secrets** (o script pede em destaque). Enquanto ele existir com 0, toda transcrição da Mari é recusada.
10. Avise o PM com a última linha (`Resultado: X de 5 casos passaram.`) e confirme que apagou o `SERVICO_TETO_DIARIO_USD`. O registro fica em `nucleo-remoto\testes\testar_servico.log` (sem texto e sem chave).
- Se falhar: `401` nos casos 3–5 → a chave colada não é a do segredo, ou o segredo tem menos de 32 caracteres; `503 SEM_CHAVE` → `OPENAI_API_KEY_MARI` ausente ou com outro nome; `502 FALHA_AUTENTICACAO` → a chave da OpenAI está errada; `429` no caso 4 → o passo 1 não foi feito; `503 LIMITE_INDISPONIVEL` → a função não alcançou o banco (avise o PM).

### Novas demandas / riscos
- Parte C: cada tentativa do caso 5 que voltar `200` é paga e deixa **mais uma linha de sucesso** (custo, `codigo` nulo) antes da `LIMITE_DIARIO`. O log do teste diz quantas foram.
- Conexão: com `idle_timeout: 5` (como no RAG), numa chamada paga a conexão do cliente fecha durante a espera da OpenAI e reabre para o registro — nunca mais de uma ao mesmo tempo, mas pode haver duas em sequência na mesma requisição. Escolhi para não segurar uma vaga do Postgres por até 120 s. Se o PM quiser a leitura literal ("uma conexão só"), basta tirar o `idle_timeout`.
- Teto não é atômico: requisições simultâneas passam juntas pela conferência; o estouro fica limitado a (chamadas simultâneas × custo de um áudio de até 4 MB).
- `TEMPO_ESGOTADO` registra custo 0, mas a OpenAI pode ter cobrado; o gasto do dia subestima nesse caso.
- A função respeita um segredo `OPENAI_BASE_URL`, se existir (trecho copiado da `transcrever`, usado no teste local); hoje afeta as duas funções igualmente.
- Higiene: o `py_compile` do teste deixou um `__pycache__`, que a pasta montada não deixa apagar; movido para `_to_delete/pycache_testar_servico_2026-09-30/` (ignorado pelo git). Pode apagar na mão.
- `git diff` mostra arquivos já modificados antes desta tarefa (`PLANO.md`, `PROXIMA_TAREFA.md`, `PROGRESSO.md` da Etapa 1, `coleta/…`, `spec/*`, `desktop/app.log`, `servicos_base.sql` não rastreado); não são desta etapa.

### Ajuste no plano necessário?
Não.

## [2026-09-30 17:44] — Serviço de transcrição para a Mari (D-37), Etapa 2: Função do serviço — Correção 1
Status: parcial — correção implantada; falta repetir a Parte B (usuário) e a Parte C (PM)

### Feito
- `nucleo-remoto/funcoes/transcrever-servico/index.ts` (378 → 395 linhas): nova `drenarCorpo(req)`, que lê `req.body` com `getReader()` e descarta cada pedaço, sem acumular, dentro de `try/catch` que ignora falha. É chamada logo antes do `return` do `405` e do `401` em `atender`. Nenhum `arrayBuffer()`/`formData()` nesses caminhos, e nada mais mudou (diff: +15 linhas da função, +1 linha em cada saída).
- Reprodução do travamento **antes** da correção: **não consegui reproduzir.** Com o código da versão 1 (idêntico ao implantado antes), 401/405 voltaram em ≤ 0,4 s em todas as tentativas: 1 MB e 20 MB, com `Content-Length` e em `chunked`, direto e por um intermediário TCP que só repassa o corpo à medida que o destino aceita (buffers de 4 KB e envio bloqueante, `proxy_lento.py` no rascunho da nuvem). O Deno local lê e descarta sozinho o corpo que ficou sem ler, então o comportamento do runtime/gateway do Supabase não aparece aqui. Não há prova local de que esta correção resolva o caso real: a confirmação é a nova rodada da Parte B.
- Testes locais depois da correção: os mesmos 18 casos da primeira entrada, **18 de 18** (12 linhas no banco, 3 com `codigo` nulo, 0 conexões abertas no fim, log sem texto nem chave); os cenários de reprodução acima também voltam 401/405 em ≤ 0,6 s; `testar_servico.py` contra a função local, **5 de 5**.
- Implantação: a primeira chamada ao `deploy_edge_function` falhou com `InternalServerErrorException` e não mudou nada (conferido: continuava versão 5, `69c2721b…`). A segunda deu certo: `transcrever-servico` versão 6, `verify_jwt: false`, `ezbr_sha256` `c2b0bda6…df83`. O conteúdo devolvido por `get_edge_function` é igual byte a byte ao arquivo: SHA-256 `ba4325aa…3cf5`, 14842 bytes.
- As outras quatro com o mesmo `ezbr_sha256` antes e depois: `transcrever` 6f35bb5e…31cf, `consumo` 474bd2d9…2967, `buscar` 536f59b0…16ad, `ingerir` 698685b7…1a7a. Observação: o campo `version` das cinco subiu +4 entre a primeira implantação e esta (5→9; `transcrever-servico` 1→5) sem mudar `updated_at` nem `ezbr_sha256`. Provavelmente por causa da troca de segredos na Parte B, mas não confirmei.

### Critério de pronto
- [x] `drenarCorpo` antes do `405` e do `401`, sem `arrayBuffer()`/`formData()`; nada mais muda na função
- [x] testes locais de novo: lógica igual (18 de 18, e 5 de 5 com o script)
- [ ] travamento reproduzido localmente antes da correção — não reproduzido (acima), sem prova inventada
- [x] `transcrever-servico` reimplantada com `verify_jwt: false`, igual ao versionado
- [x] as outras quatro com o mesmo `ezbr_sha256`

### Novas demandas / riscos
- Sem reprodução local, só a nova rodada do `testar_servico.cmd` mostra se a causa era essa. Se o caso 1 ainda travar, a causa está em outro ponto do caminho (gateway), não na leitura do corpo.
- `drenarCorpo` lê o corpo inteiro de quem não tem chave: um cliente sem chave pode fazer a função receber o corpo todo até o limite da plataforma. Não há teto de bytes na drenagem porque a tarefa não pediu.
- Repetir a Parte B como está na primeira entrada. Antes de rodar, conferir de novo que `SERVICO_TETO_DIARIO_USD` não existe.

### Ajuste no plano necessário?
Não.

## 2026-09-30 — "Abrir planejamento" (D-35) testado no Windows real

- O usuário abriu o menu ⋮ e clicou: a página de Planejamento e Execução abre. Fecha o que ficou
  em aberto na entrada de 2026-09-25 (hoje em `historico/PROGRESSO_fase2-desktop_2026-08-25_a_2026-09-21.md`).

## [2026-09-30 18:07] — Serviço de transcrição para a Mari (D-37), Etapa 3: Contrato do serviço
Status: concluído (um ponto pede decisão do PM: a regra de versão, abaixo)

### Feito
- `spec/contrato/SERVICO_TRANSCRICAO.md` (novo, 288 linhas): cabeçalho YAML como o do `NUCLEO.md`, legenda de marcas e as 12 seções na ordem da tarefa. A tabela de erros (seção 6) tem status, `codigo`, quando, se registra, se custa, o que o cliente faz e a marca de cada linha. L6, `D-16` e `D-37` só apontadas.
- `nucleo-remoto/README.md`: uma linha na tabela, logo abaixo das linhas da Etapa 2.
- Fontes de [medido]: o log de 17:53 e as 3 linhas de `servicos.transcricao_uso`, relidas por `execute_sql` só de leitura (20:53:19Z `413`, 20:53:22Z sucesso 320/82 tokens 2182 ms, 20:57:05Z `429`). O custo do sucesso está gravado como `0.0016200000000000001` (ponto flutuante do JS no `numeric`); o documento registra isso como resíduo desprezível.
- Conferência código × documento: comparei cada afirmação [código] com o `index.ts` v6 e o `servicos_base.sql`. Três pontos que eu mesmo tinha escrito errado foram corrigidos antes de fechar: o custo por minuto (fallback de `calcularCusto`) faltava na coluna `custo_usd`; o `OPTIONS → 405` estava como [código + teste local], mas só o `GET` foi testado localmente (virou [código]); e a Correção 1 estava escrita como causa provada (virou "antes travou, depois voltou em 0,8–1,2 s [medido]; a causa não foi reproduzida"). **Nenhum ponto restante em que o documento afirme algo que o código não faz.**
- Não testado: nada novo. Não chamei a função real e não implantei nada. O `NUCLEO.md` não foi tocado (`git diff` vazio nele).

### Critério de pronto
- [x] `spec/contrato/SERVICO_TRANSCRICAO.md` cobre os 12 pontos, com cada afirmação marcada — com uma marca a mais na legenda, **[proposta]**, usada uma vez (ver abaixo)
- [x] nada no documento contradiz o `index.ts` v6 (o Executor confere código × documento item a item, e lista no PROGRESSO os pontos em que o documento diz algo que o código não faz) — nenhum restante; os três corrigidos estão acima
- [x] nenhum valor de segredo, nenhum texto transcrito (só nomes de segredos; `grep` por `sk-`/`Bearer ey` vazio)
- [x] o `NUCLEO.md` não foi tocado

### Novas demandas / riscos
- **Pede decisão do PM — "o que muda a versão" (seção 4):** nenhuma fonte lida define isso para o `X-Servico-Contrato` (a seção Versionamento do `NUCLEO.md` estava fora da lista de fontes). Escrevi uma regra e marquei **[proposta]**: muda a versão o que quebra cliente (forma dos corpos, nome ou significado de `codigo`, autenticação, campo `audio`, limite que passe a recusar o que hoje passa); não muda `detail`, preço, valor do teto ou projeto novo. O PM confirma ou troca, e aí a marca sai.
- **Achado de código, sem mudança:** `SERVICO_TETO_DIARIO_USD` é **um valor só para todos os projetos**; o gasto é que é contado por projeto. Hoje só há `mari`, mas um segundo projeto herdaria o mesmo teto. O documento diz isso (seção 5).
- **Não respondido por falta de medição:** (a) se formato de navegador (WebM/Opus) funciona — só WAV foi medido; (b) quanto tempo a troca de um segredo leva para valer (o teto `0` valeu na 1ª tentativa, numa rodada só); (c) o teto de tempo da Edge Function, citado como [documentação]. Os três estão no documento como tal.
- Marca **[documentação]** usada sem ler a documentação: o `OPTIONS` de pré-requisição do navegador, o nome de arquivo como pista de formato para a OpenAI, a propagação de segredo e o teto de tempo da Edge Function. Todos escritos como "não verificado aqui".

### Ajuste no plano necessário?
Não.
- Ajuste [18:15]: o PM confirmou a regra de versão. Em `SERVICO_TRANSCRICAO.md`, **[proposta]** virou o ponteiro para a seção Versionamento do `NUCLEO.md` (`NUCLEO.md#versionamento`), com o texto da regra igual; saíram da legenda a linha da marca e o "mais uma" do título dela.
