# nucleo-remoto

O núcleo remoto do assistente: o que mora no Supabase em vez da máquina. O projeto é o
**rag-compartilhado** (`wqoeoofhuhsdzpkdblbg`), no schema **`assistente`** — o schema `rag`, da Mari,
divide o mesmo banco e não é tocado daqui.

| Arquivo | O que é |
|---|---|
| `banco/assistente_base.sql` | A migração do schema `assistente` (tabelas `consumo` e `transcricoes`, RLS, permissões). Idempotente. Aplicada pelo conector do Supabase com o nome `assistente_base` — **nunca** por `supabase db push`. |
| `banco/servicos_base.sql` | A migração do schema `servicos` (tabela `transcricao_uso`: só consumo por projeto cliente, sem texto; função `gasto_do_dia`). Só o `service_role` acessa; o schema não é exposto na API. Idempotente. Aplicada pelo conector com o nome `servicos_base`. |
| `banco/importar_historico.py` | Leva `transcritor/consumo.jsonl` e `transcritor/transcricoes.jsonl` para o banco, logado como você. Só biblioteca padrão do Python. |
| `banco/importar_historico.cmd` | Atalho de duplo clique para o importador no Windows. |
| `funcoes/transcrever/index.ts` | A Edge Function `transcrever` — Operação 1 do contrato (`POST /transcrever`) no Supabase. É exatamente o código implantado (`verify_jwt: true`). Grava consumo e transcrição com o JWT de quem chamou (`origem = 'nucleo-remoto'`). |
| `testes/testar_transcrever.py` e `.cmd` | Teste real da função, no Windows: seis casos, resultado em `testes/testar_transcrever.log`. |
| `funcoes/consumo/index.ts` | A Edge Function `consumo` — Operação 2 do contrato (`GET /consumo`) lida do banco, só com as linhas de quem chamou. É exatamente o código implantado (`verify_jwt: true`). |
| `testes/testar_consumo_e_imagem.py` e `.cmd` | Teste real da Etapa 4, no Windows: `/consumo` remoto e a imagem do núcleo local registrando no banco (sobe um segundo núcleo na porta 8001). Resultado em `testes/testar_consumo_e_imagem.log`. |
| `funcoes/transcrever-servico/index.ts` | A Edge Function `transcrever-servico` — o serviço de transcrição para projetos clientes (D-37), começando pela Mari: chave por projeto no cabeçalho `x-servico-chave`, teto de gasto por dia, e só consumo em `servicos.transcricao_uso` (nunca o texto). É exatamente o código implantado (`verify_jwt: false`). |
| `testes/testar_servico.py` e `.cmd` | Teste real do serviço, no Windows: cinco casos (o quinto pede para criar o segredo do teto e, no fim, apagá-lo). Resultado em `testes/testar_servico.log`. |
| `../spec/contrato/SERVICO_TRANSCRICAO.md` | O contrato do serviço `transcrever-servico`: o que um projeto cliente precisa saber para integrar sem abrir o código (endereço, chave, limites, erros, registro, obrigações do cliente). |

Cada linha do banco pertence a um usuário do Auth; só ele lê e insere as próprias linhas. Não há
update nem delete pela API, e o papel `anon` não enxerga o schema.

## Como importar o histórico (uma vez, no painel do Supabase e no Windows)

1. **Authentication → Users → *Add user*** → *Create new user*: o seu e-mail e uma senha, com
   ***Auto Confirm User*** marcado.
2. **Authentication → *Sign In / Providers***: desligar ***Allow new users to sign up*** e salvar.
   (Com o cadastro aberto, qualquer um com a chave pública criaria usuário.)
3. **Settings → *Data API* → *Exposed schemas***: acrescentar `assistente`, **sem tirar** os que já
   estão, e salvar.
4. Dar dois cliques em `nucleo-remoto\banco\importar_historico.cmd` e digitar e-mail e senha. A senha
   não aparece na tela.

No fim, o importador imprime as linhas lidas, as enviadas, quantas eram novas no banco e a soma de
`custo_usd` calculada dos arquivos.

- **Pode rodar de novo** quantas vezes quiser: cada linha tem id fixo e duplicata é ignorada. Na
  segunda vez, "novas" dá 0 (ou só o que o transcritor gravou desde a última).
- **Só conferir, sem enviar nada:** `importar_historico.cmd --simular` (ou
  `python importar_historico.py --simular`).
- Erro citando `schema` / `PGRST106` → falta o passo 3. Erro de login → passo 1 (usuário confirmado?).

## Edge Function `transcrever`

Endereço: `https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/transcrever`. Mesma forma do contrato
(`spec/contrato/NUCLEO.md`, Operação 1): `POST` `multipart/form-data` com `audio`, `modelo` e `stream`,
cabeçalho `Authorization: Bearer <token do login>`. Diferenças do núcleo local: só
`gpt-4o-transcribe` e `gpt-4o-mini-transcribe` (o `diarize` não cabe nos 150 s da função), prazo de 120 s
sem novas tentativas, sem CORS, e `401 NAO_AUTENTICADO` para quem não é usuário do Auth.

A chave da OpenAI mora só nos segredos do Supabase (`OPENAI_API_KEY`), nunca em arquivo.

### Como testar (no painel do Supabase e no Windows)

1. **Edge Functions → *Secrets***: se já houver `OPENAI_API_KEY` (o RAG usa), não faça nada. Se não
   houver, crie com a sua chave da OpenAI. A chave não passa pelo chat.
2. Dar dois cliques em `nucleo-remoto\testes\testar_transcrever.cmd` e digitar e-mail e senha.

Os casos 2 e 3 transcrevem `audio-teste/fala-real.wav` de verdade (chamadas pagas, centavos). O log
guarda só passou/falhou, status, tempo e o tamanho do texto — nunca o texto, e-mail, senha ou token.

## Edge Function `consumo` e a imagem no banco

`GET https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/consumo`, com `Authorization: Bearer <token do
login>`: mesma forma da Operação 2 (`sessao`, `por_dia`, `requisicoes`), lida de `assistente.consumo` e
`assistente.transcricoes`. Diferenças do núcleo local: `sessao` é o acumulado **do dia de hoje em São
Paulo** (não há processo para "desde que subiu"), `por_dia` agrupa pela data de São Paulo (o local usa a
data UTC), os ids vêm com hífens, e erros novos com `codigo` (`401 NAO_AUTENTICADO`, `405`, `502 FALHA_BANCO`).

A geração de imagem continua no núcleo local (`transcritor/`). Quando o cliente manda
`Authorization: Bearer <token>` em `POST /gerar-imagem`, o núcleo grava o consumo no banco
(`origem = 'nucleo-local-imagem'`, o prompt em `transcricoes.texto`) como esse usuário, e **não** nos
`.jsonl`. Sem o cabeçalho, nada muda. Para isso o `transcritor/.env` precisa de `SUPABASE_URL` e
`SUPABASE_CHAVE_PUBLICAVEL` (valores públicos, estão no `transcritor/.env.example`).

### Como testar (no Windows)

1. Dar dois cliques em `nucleo-remoto\testes\testar_consumo_e_imagem.cmd`, digitar e-mail e senha, e
   apertar Enter quando ele mostrar o custo da imagem (uma imagem pequena, centavos).

O teste sobe um segundo núcleo na porta 8001 e o encerra no fim; o da porta 8000 não é tocado. A saída
desse segundo núcleo fica em `testes/nucleo_8001.log`.
