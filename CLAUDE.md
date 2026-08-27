# CLAUDE.md — porta de entrada

<!-- kit:projeto:inicio -->
> **Este repositório é o `agentes-base`**: a base de método para trabalhar, e dentro dela o
> **assistente pessoal multiplataforma**, que é o produto principal. O `transcritor/` é a Fase 1 dele
> — o núcleo de transcrição, já em uso todo dia.
>
> **O mapa de onde tudo mora está em [`.claude/CEREBRO.md`](.claude/CEREBRO.md).** Este arquivo não
> repete o mapa: ele roteia o papel e fixa as duas regras que valem em qualquer chat. É curto de
> propósito — todo chat paga o custo de lê-lo.
<!-- kit:projeto:fim -->
<!-- kit:modelo
> **Este repositório é o `<NOME DO PROJETO>`**: <uma frase dizendo o que ele é>. O produto vive em
> `<PASTA DO PRODUTO>`.
>
> **O mapa de onde tudo mora está em [`.claude/CEREBRO.md`](.claude/CEREBRO.md).** Este arquivo não
> repete o mapa: ele roteia o papel e fixa as duas regras que valem em qualquer chat. É curto de
> propósito — todo chat paga o custo de lê-lo.
kit:modelo -->

## Qual é o seu papel

O modo é **opt-in**, declarado na primeira mensagem do chat:

- **"PM"** → leia `.claude/PM.md`. Você planeja, coordena e registra. **Não executa.**
- **"EXEC"** → leia `.claude/EXECUTOR.md`. Você executa a tarefa corrente. **Não planeja.**
- **Nenhum dos dois** → trabalho normal, sem o modo. Não é preciso perguntar o papel.

## As duas regras que valem nos três modos

**1. Só o usuário autoriza commit.** Ou ele autoriza explicitamente, ou ele mesmo faz. Vale também
para `push`, `reset --hard`, `rebase` e qualquer coisa que reescreva histórico. Autorização é por
ação, não por sessão. Detalhes e a lista do que deixar pronto: [`.claude/metodo/COMMIT.md`](.claude/metodo/COMMIT.md).

**2. Todo o trabalho é em português do Brasil** — a conversa nos dois papéis, os arquivos de estado,
a coleta, os READMEs e os comentários de código. Nomes de identificadores no código seguem o padrão
que já existe no arquivo. *(Regra escrita depois de um chat de execução responder em inglês: sem ela
declarada, o idioma oscila entre sessões.)*

## Comandos

Procedimentos escritos que qualquer chat pode carregar. **Se o seu cliente não registrar skills de
projeto automaticamente, abra o arquivo — o caminho está aqui de propósito.**

| Você pede | O que acontece | Onde está escrito |
|---|---|---|
| **"diagnóstico geral"**, "panorama", "roadmap" | painel de roadmap publicado, colapsável, com o rastro até o chat de cada etapa | `.claude/skills/diagnostico-geral/` + `.claude/painel.md` |
| **"revisão"**, "revisa a estrutura" | varredura que **analisa e não corrige**, com cada achado julgado | `.claude/skills/revisao-acionada/` |
| **"coleta:"**, "consolidar" | registro do diário do projeto e o resumo em quatro categorias | `.claude/skills/coleta-consolidacao/` |
| **"pode encerrar"**, "vamos fechar o chat" | consolida, atualiza o estado e reescreve a retomada | `.claude/skills/encerrar-chat/` |

## Onde o produto e o método se separam

- **Método** (como se trabalha) → `.claude/` — papéis, regras em `metodo/`, skills, estado.
- **Produto** (o que se constrói) → `spec/` — visão, decisões, specs, contrato.
- **Diário** (por que se decidiu assim) → `coleta/`, um arquivo por thread de trabalho, append-only.
  **Dono é o PM**; o Executor reporta no `PROGRESSO.md` e o PM promove o que vale registrar.

Se um chat novo precisar se situar antes de agir, o caminho é
[`.claude/CEREBRO.md`](.claude/CEREBRO.md) e depois a retomada mais recente na raiz
(`_RETOMADA_*.md`).
