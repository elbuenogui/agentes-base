# Configuração do painel — deste projeto

> Lido pela skill `diagnostico-geral`, que descreve **como** montar o painel. Este arquivo diz
> **quais** arquivos ler, com que vocabulário, onde publicar e com que cara. Fica no projeto e
> **não vai junto quando o kit for exportado** (`M-07`). Criado em 2026-08-25.

## O que ler, e o que cada arquivo rende

| Arquivo | Do que sai no painel |
|---|---|
| `spec/VISAO.md` | as fases e o `estado:` de cada uma — é a espinha do roadmap |
| `.claude/estado/PLANO.md` | as etapas da fase corrente, com critério de pronto |
| `.claude/estado/PROGRESSO.md` | o que o Executor entregou desde a última virada |
| `.claude/estado/historico/PROGRESSO_*.md` | as entradas das fases encerradas — data, nome e contagem por fase |
| `.claude/estado/historico/PLANO_*.md` | os planos encerrados, para datar as viradas |
| `spec/DECISOES.md` | decisões de produto (`D-nn`), com a razão junto |
| `.claude/metodo/DECISOES_METODO.md` | decisões de método (`M-nn`), separadas das de produto |
| `spec/QUESTOES_ABERTAS.md` | respondidas e abertas, com o que cada uma trava |
| `spec/LACUNAS.md` | o que falta produzir (`L-x`) |
| `spec/BACKLOG.md` | ideias por estado (`B-nn`) — só as vivas entram na vista |
| `spec/MAPA.md` | PoCs e rastreabilidade |
| `coleta/*.md` | **o rastro**: um arquivo por chat de trabalho |
| `spec/_rascunhos/COMPORTAMENTOS_PARQUEADOS.md` | comportamentos decididos esperando a fase deles |

## Vocabulário de estado

**Fases** (`estado:` em `VISAO.md`, legível por linha): `em-andamento` · `bloqueada:<POC>` ·
`condicional` · `nao-iniciada` · `encerrada` · `futuro`.

**Etapas** (no `PLANO.md`): concluída, cancelada, na fila, depois.

**Backlog** (`estado:` em `BACKLOG.md`): `amadurecendo` · `adiada` · `recusada` · `promovida` ·
`morta`. **Entram na vista** as duas primeiras; recusada, promovida e morta ficam de fora.

## Régua de alerta

Número que vai em cor de alerta quando:

- **PoCs rodadas em zero** enquanto existir PoC bloqueando a fase corrente;
- **histórias de usuário em zero** a partir da Fase 2 (antes disso é honesto: o núcleo não tem
  usuário direto);
- **lacunas abertas** que travam a fase corrente;
- **gasto acumulado** encostando no alarme de US$ 100/mês (`D-18`).

## Antes do método

O projeto começou em **16/08/2026** e só ganhou método declarado em **21/08**. Os cinco planos
anteriores — MVP e gravação, robustez/consumo/streaming, tempo real e linha do tempo, usabilidade da
gravação, faxina e interface enxuta — entram no roadmap como **um bloco só, resumido**, com o rastro
apontando os progressos arquivados. Sem ele, o painel dá a impressão falsa de que o projeto começou
no dia em que alguém escreveu o primeiro plano.

## Publicação

- **Título**: `Mapa do Assistente` · **ícone**: 🎙️🗺️
- **Endereço fixo**: `https://claude.ai/code/artifact/5727fb8f-851a-4fd9-8a83-024bcbf76d9e`
- Endereço anterior, mantido só como referência histórica (a rede desta sessão bloqueia a leitura
  dele, então não deve ser sobrescrito no escuro):
  `https://claude.ai/code/artifact/cce317cd-d476-4dea-ae46-8d652cec6a3b`

## Identidade visual

- **Fontes** (Google Fonts): `Archivo` para títulos e rótulos, `Source Serif 4` para texto corrido,
  `IBM Plex Mono` para IDs, datas, estados e números. Mono para `F2`, `POC-1`, `D-07`, `SPEC-001` —
  identificador é dado, não prosa.
- **Cabeçalho**: a faixa de amplitude de áudio, o mesmo desenho que o app traz na tela.
- **Cores**, em tokens, claro / escuro:
  - fundo `#F1F4F3` / `#0D1615` · superfície `#FFFFFF` / `#15211F` · tinta `#14201F` / `#E7EEEC`
  - linha `#D5DEDB` / `#26332F` · linha forte `#B9C6C2` / `#35453F` · apagado `#8B9895` / `#6B7A77`
  - acento verde-azulado `#0E6E73` / `#58B7BB`, fraco `#E2EFEF` / `#122B2C`
  - **método** (roxo, separa `M-nn` de `D-nn`) `#5B4B8A` / `#A99BD4`, fundo `#ECE9F4` / `#1E1B2C`
  - semânticas, separadas do acento: pronto `#2F7A4F` / `#6BC08D` · esperando `#96690F` / `#D7A94A`
    · bloqueado `#A33A2E` / `#E0796A`
