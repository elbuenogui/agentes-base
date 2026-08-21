# Tarefa: Commit do trabalho de 2026-08-20 e 2026-08-21
Referente à Etapa 3 do PLANO.md (plano de faxina e fechamento, 2026-08-21)

## Contexto
O repositório não tem nenhum commit desde 2026-08-20: todo o trabalho das duas frentes vive só no
disco. A próxima tarefa depois desta reescreve um pedaço grande do `index.html`, então este commit
é o ponto de restauração dela. A Etapa 2 da faxina (mover snapshots) foi adiada pelo usuário e
**não** faz parte desta tarefa.

## Arquivos envolvidos
Todo o repositório, via git. Nenhum arquivo é editado nesta tarefa — só versionado.

## O que fazer

### 1. Destravar o git, se preciso
Confira se existe `.git/index.lock`. Ele sobrou de sessões que rodaram pelo bridge remoto, onde a
pasta montada não permite apagar arquivo. **Você roda local, então pode apagar** — confirme antes
que não há nenhum processo git rodando. Sem isso, todo commit falha com "Unable to create
'.git/index.lock': File exists".

### 2. Conferir que nada sensível ou local vai junto
Antes de qualquer `git add`, confirme que o `.gitignore` está fazendo o trabalho dele:
- `transcritor/.env` (tem a chave da API), `transcritor/consumo.jsonl`,
  `transcritor/transcricoes.jsonl`, `transcritor/.venv/`, `backend/__pycache__/` e `.claude/tmp/`
  **não podem** aparecer em `git status --short` nem em nenhum commit.
- Use `git check-ignore -v` nesses caminhos para provar, e confira o `git show --stat` de cada
  commit depois de criado.
- Se algum deles aparecer como rastreado ou não ignorado, **pare a tarefa e reporte** — não
  commite e não tente consertar o `.gitignore` por conta própria.

### 3. Commitar agrupado por natureza
Um commit por natureza, não um commit gigante e não um por arquivo. O agrupamento esperado:
1. **Código do produto** — `transcritor/frontend/index.html`, `transcritor/backend/main.py`;
2. **Documentação do produto** — `transcritor/README.md`, `transcritor/BENCHMARK.md`;
3. **Estado do método e histórico** — `.claude/estado/**` (inclusive os arquivos novos em
   `historico/`) e os `_RETOMADA_*.md` da raiz;
4. **Documentação curada** — `coleta/**`.

Se algum arquivo não couber em nenhum desses grupos, decida com bom senso e **diga qual foi e por
quê** no PROGRESSO. Mensagens em português, no imperativo, dizendo o que mudou **e por quê** — não
"atualiza arquivos". O corpo pode ter duas ou três linhas quando o assunto exigir (a frente de
usabilidade, por exemplo, foram 5 etapas e 3 correções).

### 4. Não empurrar
Nada de `git push`. O remoto não faz parte desta tarefa.

## Critério de pronto
- [ ] `.git/index.lock` não existe mais
- [ ] `git status --short` vazio, fora do que o `.gitignore` cobre — **cole a saída**
- [ ] `transcritor/.env`, os dois `.jsonl`, `.venv/`, `__pycache__/` e `.claude/tmp/` **não** estão
      em nenhum commit — **cole a prova** (`git check-ignore -v` e o `--stat` dos commits)
- [ ] Commits agrupados por natureza, com mensagens em português explicando o quê e o porquê —
      **cole o `git log --oneline` dos novos**
- [ ] Nenhum `git push` executado
- [ ] Nenhum arquivo do repositório editado por esta tarefa

## Registro no PROGRESSO
curto

> Nível `curto`, com uma exceção: a **saída do `git status`**, a **prova dos ignorados** e o
> **`git log --oneline`** são obrigatórios — são listas curtas, cabem no teto.

## O que NÃO fazer
- Não faça `git push`
- Não edite nenhum arquivo do projeto, nem o `.gitignore`
- Não mexa em `.claude/estado/historico/` (mover snapshots é a Etapa 2, adiada)
- Não apague nada — nem arquivo do projeto, nem entrada de histórico
- Não use `git add .` sem olhar antes o que entrou
