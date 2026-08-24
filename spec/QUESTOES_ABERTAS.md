---
artefato: QUESTOES_ABERTAS
status: vivo
---

# Questões abertas

Decisões que **só o usuário toma**. Diferente de [LACUNAS.md](LACUNAS.md), que é trabalho que ainda
não foi feito.

> **Regra de dono único (`D-21`, 2026-08-23).** Este arquivo guarda a **pergunta** e o **ponteiro**
> para onde a resposta mora. Quando existe um `D-nn` em [DECISOES.md](DECISOES.md), a razão da
> resposta mora lá e **não é repetida aqui** — foi a repetição que produziu três respostas
> diferentes para a Q1 entre 21 e 23 de agosto. Onde não existe `D-nn`, está escrito que o dono é
> este arquivo.

**Nenhuma questão aberta bloqueia a Fase 1.** Todas as oito estão respondidas ou dissolvidas.

## ~~Q1 — Quais idiomas o produto suporta?~~ **RESPONDIDA** · dono: [`D-08`](DECISOES.md)

**O núcleo não assume idioma e não expõe parâmetro de idioma.** A API detecta sozinha.

Respondida três vezes, e por isso vale registrar o rastro — foi esta questão que revelou o problema
de método corrigido pela `D-21`:

| Quando | O que se disse | Situação |
|---|---|---|
| 21/08, manhã | "só português, fixado no código" | **superada no mesmo dia** |
| 21/08, tarde | "parâmetro `idioma` opcional, padrão ausente" | **superada pela medição** |
| 23/08 | "nenhum parâmetro; a API detecta" | **vale esta** (`D-19`: o mais recente vence) |

O que decidiu foi medição, não opinião: mesmo áudio com e sem `language="pt"` deu texto idêntico
caractere por caractere e tokens idênticos. A razão completa e a condição de reabertura estão na
`D-08`. A lista de idiomas para a interface saiu do parqueamento por falta de justificativa.

## ~~Q2 — Qual o teto de latência e de custo?~~ **RESPONDIDA** · dono: [`D-10`](DECISOES.md) e [`D-18`](DECISOES.md)

- **Latência**: a régua é **não piorar o que o usuário já usa hoje** (`D-10`). O Win+H foi
  descartado como alvo — o app atual já é mais rápido e mais preciso que ele.
- **Custo**: **alarme em US$ 100/mês, não limite rígido** (`D-18`). Referência medida: US$ 0,53 no
  projeto inteiro, 343 requisições, de 18 a 23 de agosto.

**Questão encerrada** — o cabeçalho dizia "parcialmente respondida" até 2026-08-23, quando o corpo
já a dava por encerrada. Corrigido pelo passe de fechamento da `D-21`.

## ~~Q3 — O desktop é só Windows?~~ **RESPONDIDA** · dono: [`D-11`](DECISOES.md)

**Não como ambição; sim como ponto de partida.** Windows primeiro, com a camada de inserção de
texto isolada num módulo trocável por sistema operacional.

## ~~Q4 — Qual smartwatch, e já está em mãos?~~ **RESPONDIDA** · dono: este arquivo

**Galaxy Watch 5, já em mãos** (2026-08-21). A F4 deixa de ter bloqueio de hardware. Fica valendo o
risco conhecido da gestão agressiva de bateria da Samsung, a ser medido na POC-5.

> Sem `D-nn` próprio: é fato de contexto, não decisão com trade-off. Se virar escolha entre
> aparelhos, aí nasce a decisão.

## ~~Q5 — "Copiar / apagar / desfazer" — o que cada um faz?~~ **RESPONDIDA** · dono: [`D-15`](DECISOES.md)

**O texto não é consumido ao ser colocado** — quem se minimiza é a janela, que volta no hover sobre
o botão flutuante. Daí saem os três estados da janela do desktop.

## ~~Q6 — Qual critério decide que "a integração direta com GPT não basta"?~~ **DISSOLVIDA** · dono: [`D-12`](DECISOES.md)

A pergunta não se aplica: a Fase 6 acontece de qualquer forma. O resultado da F5 define a urgência,
não a existência.

## ~~Q7 — O histórico de transcrições é requisito ou efeito colateral?~~ **RESPONDIDA** · dono: [`D-22`](DECISOES.md)

**É requisito** (2026-08-21), ainda incipiente e não mapeado. **Não vira trabalho agora**: o contrato
da Fase 1 documenta o histórico como ele é hoje, e a funcionalidade ganha história de usuário própria
na especificação da Fase 2.

As três consequências abertas — arquivos `.jsonl` não versionados e sem retenção, `consumo.jsonl`
misturando uso real com teste, e a troca por banco de dados adiada — moram na `D-22`, não aqui.

> Promovida ao livro-razão em 2026-08-23: a resposta morava solta neste arquivo, e "histórico é
> requisito" é decisão de produto com consequência. Foi a primeira aplicação da `D-21` a um caso que
> já existia.

## ~~Q8 — Como este projeto testa?~~ **RESPONDIDA** · dono: [`D-09`](DECISOES.md)

**Verificação manual, declarada como método**, enquanto o projeto for simples. Gatilho de revisão:
quando houver mais de um cliente consumindo o núcleo.

Consequência para a SPEC-001: o CA2 é atendido por medição manual registrada no `PROGRESSO.md` com
evidência colada — é por isso que a tarefa da Etapa 1 pediu nível `completo`.
