---
artefato: QUESTOES_ABERTAS
status: vivo
---

# Questões abertas

Cada uma bloqueia uma fase específica. Nenhuma bloqueia a Fase 1 — por isso a Fase 1 pode começar.

## ~~Q1 — Quais idiomas o produto suporta?~~ **RESPONDIDA (2026-08-21)**
**Só português, por enquanto.**
Decorrência encontrada na análise do repositório: a chamada à API **não envia o idioma hoje**
(`main.py:246`, `parametros_extra` só carrega `chunking_strategy`). Com o idioma fixado, passar
`language="pt"` tende a melhorar precisão, reduzir latência e impedir o modelo de trocar de idioma
sozinho. Virou candidata da Etapa 3 da Fase 1. **"Por enquanto" fica registrado**: o dia em que
entrar um segundo idioma, esse parâmetro deixa de ser constante e vira configuração.

## ~~Q2 — Qual o teto de latência e de custo?~~ **PARCIALMENTE RESPONDIDA (2026-08-21)**
**Latência: régua trocada.** O Win+H foi descartado como alvo — o usuário reporta que o app de hoje
já é mais rápido, mais preciso e com mais opções. A régua passa a ser **não piorar o que ele já usa
todo dia** (`D-10`).
**Custo: RESPONDIDO em 2026-08-23, com número medido.** O gasto histórico do projeto inteiro, de
18 a 23 de agosto, foi **US$ 0,53 em 343 requisições**; o dia mais caro foi 21/08, com US$ 0,21.
São dias de desenvolvimento pesado, não de uso em regime.
**Definido pelo usuário em 2026-08-23: alarme em US$ 100/mês**, não limite rígido (`D-18`).
Encostar nele é sinal de mudança de padrão de uso, não de excesso. **Questão encerrada.**

## ~~Q3 — O desktop é só Windows?~~ **RESPONDIDA (2026-08-21)**
**Não como ambição; sim como ponto de partida.** Windows primeiro, com a camada de inserção de
texto isolada num módulo trocável por sistema operacional (`D-11`). A parte difícil não é a
interface multiplataforma — é que inserir texto no campo de outro aplicativo são três
implementações diferentes, e no Linux com Wayland há bloqueio por desenho.

## ~~Q4 — Qual smartwatch, e já está em mãos?~~ **RESPONDIDA (2026-08-21)**
**Galaxy Watch 5, já em mãos.** A F4 deixa de ter bloqueio de hardware. Fica valendo o risco
conhecido da gestão agressiva de bateria da Samsung, a ser medido na POC-5.

## ~~Q5 — "Copiar / apagar / desfazer" — o que cada um faz?~~ **RESPONDIDA (2026-08-21)**
**O comportamento do texto não muda depois de colocado.** A transcrição continua viva e disponível
para ser colocada de novo — colocar não consome. O que muda é a **janela**: ela se minimiza, e
volta a aparecer no **hover** sobre o botão flutuante.

Decorrência de desenho: a janela do desktop tem três estados — *gravando*, *mostrando o resultado*
e *minimizada* — e a transição para minimizada é automática depois de colocar o texto em algum
lugar. Ver `D-15`.

## ~~Q6 — Qual critério decide que "a integração direta com GPT não basta"?~~ **DISSOLVIDA (2026-08-21)**
A pergunta não se aplica mais: **a Fase 6 acontece de qualquer forma** (`D-12`). O resultado da F5
define só a urgência — se a integração não funcionar, o agente entra imediatamente; se funcionar,
é testada por mais tempo e o agente vem depois.

## ~~Q7 — O histórico de transcrições é requisito ou efeito colateral?~~ **RESPONDIDA (2026-08-21)**
**É requisito** — ver uso e histórico interessa ao usuário. Ainda incipiente e não mapeado.
Decorrências abertas, que agora precisam de dono:
- o histórico existe hoje como efeito colateral: dois arquivos `.jsonl` **não versionados**, sem
  política de retenção, presos à máquina onde o backend roda;
- `consumo.jsonl` **mistura uso real com sessões de teste do Executor** — enquanto era ruído,
  tudo bem; sendo requisito, é dado errado;
- a troca de arquivo local por banco de dados está no Backlog desde 2026-08-18, adiada pelo usuário.

**Encaminhamento do PM**: o contrato da Fase 1 documenta o histórico como ele é hoje; a
funcionalidade ganha história de usuário própria quando a Fase 2 for especificada, porque é lá que
alguém vai olhar para ela. Não vira trabalho agora.

## ~~Q8 — Como este projeto testa?~~ **RESPONDIDA (2026-08-21)**
**Verificação manual, declarada como método**, enquanto o projeto for simples. Sem teste
automatizado por ora: montar suíte custa tempo e chamada de API, e o usuário decidiu que isso
espera um sistema mais robusto e maior. **Gatilho de revisão**: quando houver mais de um cliente
consumindo o núcleo, verificação manual deixa de cobrir — é aí que a decisão volta.

Contexto original:
Não existe nenhum teste automatizado no repositório. Toda verificação foi manual ou Playwright ad
hoc, descartado depois. A cadeia `TASK → TEST` do método pressupõe teste que **fica**.
Por que é decisão sua e não minha: teste que chama a API de verdade **gasta dinheiro a cada
execução**. As opções são teste com gravação de resposta (não gasta, mas não pega mudança da API),
teste com chamada real limitado a um áudio de 2 segundos (gasta centavos, pega tudo), ou nenhum
teste automatizado e verificação manual declarada como método.
