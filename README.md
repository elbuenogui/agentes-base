# agentes-base

> **Duas coisas moram aqui, e é de propósito.** Este repositório é o **kit** descrito abaixo — e é
> também o **projeto do assistente pessoal multiplataforma**, que é o produto principal. O método
> (como se trabalha) mora em `.claude/`, mapeado em [`.claude/CEREBRO.md`](.claude/CEREBRO.md); o
> produto mora em `spec/` e no `transcritor/`. Este README fala **do kit**: como levá-lo para outro
> projeto. Quem quer entender o produto começa pelo `CLAUDE.md` e pela retomada mais recente.

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
├── GUIA_AGENTES_BASE.md                       explicação didática de todo o sistema
├── CLAUDE.md                                  porta de entrada: roteia o papel (copiar para a raiz do projeto novo)
├── _RETOMADA_TEMPLATE.md                      modelo para criar retomadas de qualquer frente de trabalho
└── .claude/
    ├── CEREBRO.md                             o mapa: onde cada coisa mora e como o método evolui
    ├── PM.md                                  conduta do papel PM
    ├── EXECUTOR.md                            conduta do papel Executor
    ├── metodo/                                as regras, que valem para os dois papéis
    │   ├── CONSISTENCIA.md                    dono único · sem contagem à mão · passe de fechamento
    │   ├── HIGIENE.md                         o que se guarda, o que se joga fora, e com que gatilho
    │   ├── PLANOS.md                          os três tipos de plano: fase, manutenção, acompanhamento
    │   └── COMMIT.md                          quem autoriza commit, e o que se deixa pronto
    ├── estado/
    │   └── README.md                          como funciona a pasta de progressão PM ↔ Executor
    └── skills/
        ├── coleta-consolidacao/               registro contínuo + consolidação      genérica
        ├── revisao-acionada/                  varredura que analisa e não corrige   genérica
        ├── encerrar-chat/                     deixa o projeto retomável             genérica
        └── diagnostico-geral/                 painel de estado                      **identidade visual e endereço são do projeto**

**Não copie** `.claude/metodo/DECISOES_METODO.md` — ele registra o que *esta* instalação decidiu.
Projeto novo herda as regras e começa com ledger vazio.
```

Repare que **não há** `PLANO.md`, `PROXIMA_TAREFA.md`, `PROGRESSO.md` nem arquivos dentro de
`coleta/` neste kit. Isso é proposital: esses arquivos nascem no primeiro uso real do projeto —
criar stubs vazios só gera confusão sobre se algo já foi decidido ou não. O formato exato de cada
um está descrito em `.claude/PM.md` e `.claude/EXECUTOR.md`.

## Como instanciar num projeto novo (a partir de uma branch)

1. Crie a branch/projeto novo normalmente.
2. Copie para a raiz do novo repositório, preservando os caminhos:
   - `CLAUDE.md`
   - `.claude/CEREBRO.md`
   - `.claude/PM.md`
   - `.claude/EXECUTOR.md`
   - `.claude/metodo/` (os quatro arquivos de regra — **sem** o `DECISOES_METODO.md`)
   - `.claude/estado/README.md`
   - `.claude/skills/coleta-consolidacao/`, `revisao-acionada/`, `encerrar-chat/`
     (a `diagnostico-geral` carrega cores, fontes e um endereço fixo do projeto — copie só se for
     reescrever essas três coisas)
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

## A realimentação não é opcional — é o que mantém as duas camadas vivas

A frase acima existe desde a primeira versão deste README e **ficou sete dias sem ser usada**: um
mecanismo genérico foi reinventado dentro da camada do produto, pior do que a versão que já estava
escrita aqui, e as duas camadas passaram esse tempo sem se ler.

Por isso a regra virou passo do método, em [`.claude/CEREBRO.md`](.claude/CEREBRO.md): **mecanismo
que já provou valor numa instalação é candidato a subir para o kit**. Sem esse passo, cada camada
reinventa o que a outra já sabia — e a versão nova costuma ser a pior das duas, porque nasce sem a
razão original junto.
