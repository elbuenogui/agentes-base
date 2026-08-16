# Tarefa: Estrutura inicial do projeto e customização do kit
Referente à etapa 1 do PLANO.md

## Contexto
MVP do assistente de pesquisa por áudio: motor mínimo áudio → API OpenAI → transcrição. Este
repositório já tem o kit agentes-base instalado (CLAUDE.md, .claude/PM.md, .claude/EXECUTOR.md
etc.) na branch `input-de-audio`, mas os placeholders `<...>` ainda não foram preenchidos e o
código do projeto em si ainda não existe.

## Arquivos envolvidos
- transcritor/backend/ (pasta nova)
- transcritor/frontend/ (pasta nova)
- transcritor/.env (arquivo novo, com placeholder de chave)
- transcritor/requirements.txt (arquivo novo)
- transcritor/README.md (arquivo novo)
- CLAUDE.md (raiz — preencher placeholders)
- .claude/PM.md (preencher placeholders, se houver)
- .claude/EXECUTOR.md (preencher placeholders, se houver)
- .claude/skills/coleta-consolidacao/SKILL.md (preencher placeholders, se houver)

## O que fazer
1. Criar a subpasta `transcritor/` com as pastas `backend/` e `frontend/` (podem ficar vazias
   ou com um único arquivo inicial mínimo, ex. `main.py`/`app.py` e um `index` inicial — sem
   lógica de negócio ainda, isso é etapa 2 em diante).
2. Criar `transcritor/.env` com um placeholder para a chave da API (ex.
   `OPENAI_API_KEY=`), sem valor real.
3. Criar `transcritor/requirements.txt` com as dependências mínimas já previstas (ex. `openai`
   e o framework web que for escolhido) ou vazio, se preferir decidir o framework na etapa 2.
4. Criar `transcritor/README.md` com o nome do projeto ("Assistente de Pesquisa por Áudio —
   MVP de transcrição") e 1-2 linhas de descrição (motor áudio → API → transcrição).
5. Abrir `CLAUDE.md` (raiz) e substituir os placeholders `<nome do projeto>` e demais `< >`
   pelo contexto real deste projeto (nome: Assistente de Pesquisa por Áudio; não há projeto de
   escrita/relatório separado — ajustar a nota sobre "aplicar" removendo essa etapa, já que a
   coleta é registro interno do próprio projeto).
6. Fazer o mesmo ajuste de placeholders em `.claude/PM.md`, `.claude/EXECUTOR.md` e
   `.claude/skills/coleta-consolidacao/SKILL.md`, se eles tiverem placeholders `< >`
   pendentes.
7. NÃO tocar no `README.md` da raiz do repositório — ele documenta o kit agentes-base e
   permanece como está.

## Critério de pronto
- [ ] `transcritor/backend/` criada
- [ ] `transcritor/frontend/` criada
- [ ] `transcritor/.env` criado com placeholder de chave (sem valor real)
- [ ] `transcritor/requirements.txt` criado
- [ ] `transcritor/README.md` criado com nome + descrição curta do projeto
- [ ] placeholders `<...>` em `CLAUDE.md` preenchidos com o contexto deste projeto
- [ ] placeholders `<...>` em `.claude/PM.md`, `.claude/EXECUTOR.md` e
      `.claude/skills/coleta-consolidacao/SKILL.md` preenchidos, se existiam
- [ ] `README.md` da raiz permanece inalterado
- [ ] nenhum comando de build/teste pré-existente no repositório quebra por causa dessas
      mudanças

## O que NÃO fazer
- Não implementar lógica de backend ou frontend nesta etapa (isso começa na etapa 2)
- Não instalar dependências ainda (só listar em `requirements.txt`)
- Não alterar `README.md` da raiz
- Não commitar nenhuma chave real de API
- Não alterar arquivos fora da lista acima
- Não fazer commit/push — isso fica a critério do usuário depois de revisar
