# O cérebro

> **Como este projeto trabalha.** Aqui mora o método: papéis, regras, comandos e o canal entre
> planejamento e execução. O **produto** mora fora daqui.
>
> Este é o **mapa único** de onde tudo mora (`metodo/CONSISTENCIA.md`, regra 1). Nenhum outro arquivo
> mapeia a estrutura — os outros apontam para cá.

## Onde tudo mora

| Camada | Onde | O que guarda |
|---|---|---|
| **Cérebro** | `.claude/` | como se trabalha — este arquivo, papéis, `metodo/`, `skills/`, `estado/` |
| **Produto** | `spec/` | a visão, as decisões do produto, as specs, o contrato |
| **Código** | a pasta do produto | o que roda |
| **Diário** | `coleta/` | por que se decidiu assim, em ordem cronológica |
| **Kit** | `README.md`, `GUIA_AGENTES_BASE.md` | como levar este método para outro projeto |

## Dentro do cérebro

    .claude/
    ├── CEREBRO.md          este arquivo — o mapa
    ├── painel.md           configuração do painel de roadmap — deste projeto, não vai no kit
    ├── PM.md               conduta do papel PM
    ├── EXECUTOR.md         conduta do papel Executor
    ├── metodo/             as regras, que valem para os dois papéis
    │   ├── CONSISTENCIA.md dono único · sem contagem à mão · passe de fechamento · o mais recente vence
    │   ├── HIGIENE.md      o que se guarda, o que se joga fora, e com que gatilho
    │   ├── PLANOS.md       os três tipos de plano e quando usar cada um
    │   ├── COMMIT.md       quem autoriza, e o que se deixa pronto
    │   └── DECISOES_METODO.md  o que ESTA instalação decidiu (M-nn) — não vai no kit
    ├── kit/                exportar.py — gera o kit portátil a partir destes arquivos (M-07)
    ├── skills/             os comandos (ver tabela abaixo)
    ├── estado/             o canal PM ↔ Executor, vivo
    │   └── historico/      o que já fechou
    └── tmp/                descartável, com validade — nada de valor mora aqui

## Um fato, um dono

| Fato | Dono |
|---|---|
| decisão de **produto**, com razão e condição de reabertura | `spec/DECISOES.md` (`D-nn`) |
| decisão de **método** | `.claude/metodo/DECISOES_METODO.md` (`M-nn`) |
| pergunta que só o usuário responde | `spec/QUESTOES_ABERTAS.md` — a pergunta e o ponteiro |
| trabalho que falta produzir | `spec/LACUNAS.md` |
| ideia que ainda não é trabalho | `spec/BACKLOG.md` (`B-nn`) |
| comportamento observado do produto | o documento de contrato em `spec/contrato/` |
| o porquê e os critérios de aceitação | a `SPEC-nnn` |
| etapas, critérios de pronto, escopo da fase | `.claude/estado/PLANO.md` |
| o que o Executor fez e como testou | `.claude/estado/PROGRESSO.md` |
| **onde tudo mora** | **este arquivo** |
| como o painel de roadmap é montado neste projeto | `.claude/painel.md` |

## Os comandos

| Comando | Faz | Pasta |
|---|---|---|
| **diagnóstico geral** · panorama · roadmap | o painel de roadmap, publicado e colapsável | `skills/diagnostico-geral/` |
| **revisão** · revisa a estrutura | varre e julga achados; **não corrige** | `skills/revisao-acionada/` |
| **coleta:** · consolidar | registra no diário do projeto e consolida | `skills/coleta-consolidacao/` |
| **pode encerrar** · fechar o chat | deixa o projeto retomável em outro chat | `skills/encerrar-chat/` |

Cada uma é um arquivo `SKILL.md`. **Alguns clientes registram skills de projeto automaticamente e
outros não** — quando não registrarem, abra o arquivo pelo caminho acima. É por isso que a tabela
existe: o comando não pode depender de o cliente descobrir sozinho.

## Quem lê o quê

- **Todo chat** lê o `CLAUDE.md` da raiz — ele roteia o papel e aponta para cá. É curto de
  propósito: todo chat paga o custo de lê-lo.
- **Chat de PM** lê `PM.md` e as regras de `metodo/`.
- **Chat de Executor** lê `EXECUTOR.md`, as regras de `metodo/` que couberem, e **só a tarefa
  corrente** em `estado/PROXIMA_TAREFA.md`.
- **Chat sem papel declarado** não tem regra de papel — mas `metodo/COMMIT.md` vale para ele também.

## Como o cérebro evolui

Ele muda quando o trabalho mostra que ele está errado, não por iniciativa de quem passa por aqui.

1. **Regra nova nasce de um problema observado**, não de previsão. O problema vira achado, o achado
   vira decisão `M-nn` com razão escrita, e só então vira regra num arquivo de `metodo/`.
2. **Regra genérica sobe; história fica.** A regra em `metodo/` é escrita sem a história do projeto,
   para poder ser copiada. A história — o que aconteceu, quando, com que evidência — mora na
   `coleta/` e no `M-nn`.
3. **O que se prova aqui volta para o kit.** Mecanismo que já provou valor nesta instalação é
   candidato a subir para o `GUIA_AGENTES_BASE.md`. Sem esse passo, a camada genérica e a camada do
   produto param de conversar, e cada uma reinventa o que a outra já sabia.
   **Levar o kit para outro projeto**: `python3 .claude/kit/exportar.py` gera o pacote a partir
   destes arquivos. Nunca copie a mão — ver `metodo/DECISOES_METODO.md`, `M-07`.
4. **Exceção é datada e registrada.** Exceção pontual às regras vale uma vez, com data e razão no
   `M-nn` correspondente. Exceção não vira regra por repetição silenciosa.
