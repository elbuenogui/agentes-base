---
artefato: LACUNAS
status: vivo
---

# Lacunas — o que falta produzir

Diferente de [QUESTOES_ABERTAS.md](QUESTOES_ABERTAS.md): questão é decisão que só o usuário toma;
lacuna é **trabalho que ainda não foi feito**. Cada uma diz que fase ela trava.

## Abertas

### L-A — Nenhuma história de usuário foi escrita
`trava: F2` · A cadeia de rastreabilidade começa em `US-XXX` e hoje começa vazia — a SPEC-001 não
deriva de história nenhuma. Para um contrato técnico isso é honesto, porque o núcleo não tem
usuário direto. Para a Fase 2, não.
**Encaminhamento (D-13)**: é a primeira entrega da própria Fase 2, não pré-requisito dela.

### L-B — A Fase 2 não tem lista de entregáveis
`trava: F2` · A regra manda escrever a lista antes de especificar.
**Encaminhamento (D-13)**: primeira entrega da Fase 2.

### L-C — Não existe definição declarada de MVP
`trava: F2` · O pré-projeto separa MVP, próxima etapa e futuro como conceito, mas nunca listou o
que é o MVP.
**Encaminhamento (D-13)**: primeira entrega da Fase 2.

### L-D — Nenhuma PoC rodou
`trava: F2 (POC-1), F3 (POC-3), F4 (POC-5)` · A POC-1 é a única coisa capaz de invalidar o desenho
do produto e **não depende da Fase 1 terminar**. Agora tem alvo definido: terminal do Claude Code,
extensão do Claude Code no VS Code, e a aba do WhatsApp no navegador.



## Fechadas

### ~~L-E — Não havia teto de custo mensal~~
`fechada em 2026-08-23` · A medição trouxe o número (US$ 0,53 no projeto inteiro, 343 requisições,
18 a 23 de agosto) e o usuário definiu o alarme: **US$ 100/mês** (`D-18`).

### ~~L-G — A janela do desktop não tinha estados definidos~~
`fechada em 2026-08-21` · Agora tem três — gravando, mostrando o resultado, minimizada — e a regra
de transição entre eles (`D-15`).

### ~~L-F — Não havia livro-razão de decisões~~
`fechada em 2026-08-21` · As decisões viviam espalhadas entre conversa, rascunho e memória.
Agora existe [DECISOES.md](DECISOES.md), com a razão junto de cada uma.
