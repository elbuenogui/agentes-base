# agentes-base

Kit portátil de arquivos para instalar em qualquer projeto novo onde você (Marcel) quer:

- separar **planejamento** (PM) de **execução** (Executor), em dois chats diferentes;
- manter um **rastro documentado** do que foi decidido, sem depender da memória do chat;
- **retomar** um chat novo sem ter que reexplicar o contexto do zero.

Este kit foi extraído e generalizado do fluxo que já roda no repositório de código da Mari
(chatbot UrbVerde) — lá ele está adaptado à curadoria de um corpus de documentos; aqui ele está
"pelado", sem nenhuma referência a esse domínio, pronto para ser copiado para qualquer repositório
novo.

**Antes de instalar num projeto, leia `GUIA_AGENTES_BASE.md`.** Ele explica o que cada peça faz,
por que existe e quando vale a pena usar (ou não). Não instale isso em piloto automático — é um
processo com custo (disciplina de manter arquivos atualizados); só compensa se o projeto vai ter
mais de um chat de trabalho ao longo do tempo, ou execução em paralelo ao planejamento.

## Conteúdo do kit

```
agentes-base/
├── README.md                                  este arquivo
├── GUIA_AGENTES_BASE.md                        explicação didática de todo o sistema
├── CLAUDE.md                                   ponto de entrada do modo PM/EXEC (copiar para a raiz do projeto novo)
├── _RETOMADA_TEMPLATE.md                       modelo para criar retomadas de qualquer frente de trabalho
└── .claude/
    ├── PM.md                                   regras do papel PM
    ├── EXECUTOR.md                              regras do papel Executor
    ├── estado/
    │   └── README.md                           como funciona a pasta de progressão PM ↔ Executor
    └── skills/
        └── coleta-consolidacao/
            └── SKILL.md                        skill de coleta contínua + consolidação (documentação viva do projeto)
```

Repare que **não há** `PLANO.md`, `PROXIMA_TAREFA.md`, `PROGRESSO.md` nem arquivos dentro de
`coleta/` neste kit. Isso é proposital: esses arquivos nascem no primeiro uso real do projeto —
criar stubs vazios só gera confusão sobre se algo já foi decidido ou não. O formato exato de cada
um está descrito em `.claude/PM.md` e `.claude/EXECUTOR.md`.

## Como instanciar num projeto novo (a partir de uma branch)

1. Crie a branch/projeto novo normalmente.
2. Copie para a raiz do novo repositório, preservando os caminhos:
   - `CLAUDE.md`
   - `.claude/PM.md`
   - `.claude/EXECUTOR.md`
   - `.claude/estado/README.md`
   - `.claude/skills/coleta-consolidacao/SKILL.md`
   - `_RETOMADA_TEMPLATE.md` (fica na raiz; a partir dele você cria `_RETOMADA_<tema>.md` quando
     precisar retomar uma frente específica)
3. Abra cada arquivo copiado e substitua os trechos entre `< >` — nome do projeto, domínio,
   pastas específicas, e se existe ou não um projeto de escrita/relatório separado (ver nota em
   `SKILL.md` sobre o passo "aplicar", que só faz sentido nesse caso).
4. Adicione `.claude/tmp/` e `.claude/estado/*` (exceto `README.md`) ao `.gitignore` **se** você
   não quiser versionar rascunho e progresso — no projeto da Mari eles são versionados
   propositalmente (viram histórico auditável), mas isso é uma escolha, não uma regra fixa.
5. Faça o primeiro commit já com a estrutura instalada — ela é o contrato entre você e os chats
   PM/EXEC daquele projeto.
6. No dia a dia: comece um chat com a palavra **"PM"** para planejar, ou **"EXEC"** para executar
   a tarefa corrente. Sem declarar nada, o chat funciona normal, sem o modo.

## Quando você quiser continuar depois de um tempo parado

Copie `_RETOMADA_TEMPLATE.md` para `_RETOMADA_<tema>.md`, preencha as seções e cole a "mensagem
pronta" do fim do arquivo no chat novo. Detalhes no `GUIA_AGENTES_BASE.md`.

## Relação com o repositório da Mari

Esse kit é a versão genérica do que já roda em `Mari/.claude/` e `Mari/CLAUDE.md`. Se algo aqui
divergir do que está rodando lá, o repositório da Mari é o mais maduro/testado (rodou várias
rodadas reais); traga a melhoria de volta para cá quando fizer sentido generalizar.
