# Coleta — Fase 1: contrato do núcleo (2026-08-21 a 2026-08-23)

Chat de PM que abriu o método Spec-Driven Development, planejou o produto inteiro e acompanhou a
primeira tarefa executada sob ele.

## 1. Registro por interação

- [DIRECIONAMENTO] O `transcritor/` deixa de ser o projeto e vira a **Fase 1** de um assistente
  pessoal multiplataforma, planejado por Spec-Driven Development (2026-08-21).
- [DECISÃO] `spec/` nasce dentro de `agentes-base`, com o transcritor como núcleo já implementado
  — trade-off: herda o histórico e o acoplamento do repo, em troca de não duplicar o núcleo nem o
  método num projeto novo.
- [DECISÃO] A SPEC entra como camada intermediária entre `PLANO.md` e `PROXIMA_TAREFA.md` —
  trade-off: mais um nível de documento, em troca de preencher a lacuna de método aberta em
  2026-08-19.
- [DECISÃO] ADR por promoção: decisão técnica nasce dentro da spec e só vira arquivo próprio quando
  vale para mais de uma — trade-off: decisão transversal fica escondida até ser promovida, em troca
  de não criar trinta arquivos de uma linha.
- [ARTEFATO] `spec/_rascunhos/2026-08-21_revisao-pre-projeto.md` — revisão do pré-projeto: 5
  inconsistências, 7 ambiguidades, consolidação de histórias, 6 requisitos implícitos, 6 PoCs.
- [DECISÃO] Acionamento do desktop é atalho de teclado configurável, botão flutuante como
  complemento — trade-off: um controle a mais para configurar, em troca de não perder o foco do
  campo de destino no momento de acionar.
- [DECISÃO] Núcleo = lote + streaming; modo ao vivo congelado — trade-off: quem quiser transcrição
  contínua não tem, em troca de não portar ~400 linhas de captura PCM para três plataformas.
- [DECISÃO] Relógio é cliente magro e o telefone é o núcleo dele — trade-off: o relógio não funciona
  sem o telefone por perto, em troca de nunca precisar da chave da API nem de processar no pulso.
- [DECISÃO] Servidor próprio adiado, com gatilho em "estado compartilhado entre aparelhos" —
  trade-off: consumo fragmentado por aparelho e chave em cada um, em troca de não manter um serviço
  no ar para um usuário só.
- [DECISÃO] Compartilha-se comportamento, não código; a Fase 1 entrega um contrato — trade-off:
  ~300 linhas reimplementadas por plataforma, em troca de cada uma usar a ferramenta que lhe cabe.
- [DECISÃO] Windows primeiro, com a camada de inserção isolada por sistema operacional —
  trade-off: um módulo a mais de indireção, em troca de não reescrever o app quando aparecer um
  segundo computador.
- [DECISÃO] Verificação manual declarada como método, sem suíte automatizada — trade-off: nenhuma
  rede de segurança contra regressão, em troca de não gastar tempo e chamadas de API num sistema
  ainda pequeno. Gatilho de revisão: mais de um cliente consumindo o núcleo.
- [DECISÃO] A régua do Win+H foi aposentada; a régua passa a ser o app de hoje — trade-off: perde-se
  um alvo externo e objetivo, em troca de um alvo verdadeiro (o app já superou o Win+H).
- [DECISÃO] A Fase 6 acontece de qualquer forma; o resultado da fase GPT define só a urgência —
  trade-off: compromete tempo futuro sem saber ainda se será necessário.
- [DECISÃO] As lacunas da Fase 2 são a primeira entrega da própria Fase 2 — trade-off: a fase abre
  sem histórias escritas, em troca de não escrever spec sobre suposição antes da POC-1.
- [DECISÃO] "Diagnóstico geral" é comando com painel visual publicado, em endereço fixo —
  trade-off: manter formato estável dá trabalho, em troca de duas leituras do projeto serem
  comparáveis entre si.
- [ARTEFATO] `spec/VISAO.md`, `spec/DECISOES.md`, `spec/QUESTOES_ABERTAS.md`, `spec/LACUNAS.md`,
  `spec/MAPA.md` — reestruturação: cada tipo de informação com uma casa só.
- [ARTEFATO] `.claude/skills/diagnostico-geral/SKILL.md` — a skill que monta o painel.
- [ARTEFATO] Painel publicado em `https://claude.ai/code/artifact/cce317cd-d476-4dea-ae46-8d652cec6a3b`.
- [ARTEFATO] `spec/specs/SPEC-001_contrato-do-nucleo.md` — a especificação da primeira unidade.
- [DECISÃO] Colocar o texto num campo **não o consome**; a janela é que se minimiza e volta com o
  hover — trade-off: a janela some da vista sem o texto sumir, exigindo um estado a mais.
- [ARTEFATO] `spec/contrato/NUCLEO.md` — o contrato do núcleo, **medido** contra a máquina pelo
  Executor em 2026-08-23.
- [DECISÃO] A Etapa 5 (parâmetro de idioma) **cai** — a medição mostrou texto e tokens idênticos com
  e sem `language="pt"`. Trade-off: nenhum; a etapa existia condicionada a esse resultado.
- [DECISÃO] O gate de silêncio vira obrigação declarada do cliente no contrato — trade-off: todo
  cliente novo tem de reimplementá-lo, em troca de não fazer análise de amplitude sobre áudio já
  codificado no núcleo.
- [PENDÊNCIA] Bug: `gpt-4o-transcribe-diarize` grava `custo_usd: 0.0` — depende de: o PM decidir se
  entra na Etapa 3 ou vira backlog.
- [PENDÊNCIA] L1 (códigos de erro por máquina) e L5 (versionamento do contrato) — depende de:
  decisão do PM na Etapa 2.
- [PENDÊNCIA] Teto de custo de US$ 10/mês como alarme — depende de: aceite explícito do usuário.
- [DIRECIONAMENTO] O uso real concorrente durante a medição pode ser ignorado como risco — o
  usuário estava de fato usando o app e não considera o dado útil (2026-08-23).

- [DECISÃO] `gpt-4o-transcribe-diarize` fica **fora de escopo**; os dois achados que dependem dele
  não viram tarefa — trade-off: o bug de custo zerado permanece no código, em troca de não consertar
  o que ninguém aciona (o modelo está desativado da interface desde 2026-08-18). (2026-08-23)
- [DECISÃO] Alarme de custo em **US$ 100/mês**, não limite rígido — trade-off: fica cerca de duas
  ordens de grandeza acima do gasto observado, o que o torna sinal de anomalia e não freio de uso.
  (2026-08-23)

## 2. Resumo consolidado

### Decisões

Dezesseis, todas em `spec/DECISOES.md` com razão e condição de reabertura (`D-01` a `D-16`). As
estruturantes: atalho de teclado como acionamento; núcleo de lote e streaming com o ao vivo
congelado; relógio magro com o telefone como núcleo; servidor adiado com gatilho; contrato em vez
de biblioteca compartilhada; Windows primeiro com inserção isolada; verificação manual declarada;
Fase 6 certa; lacunas da F2 dentro da F2; diagnóstico em painel; colocar não consome; gate de
silêncio como obrigação do cliente.

### Artefatos

`spec/` inteira (visão, decisões, questões, lacunas, mapa, SPEC-001, contrato medido, rascunhos e
comportamentos parqueados); a skill `diagnostico-geral` e o painel publicado; o `PLANO.md` da Fase
1 com seis etapas; a virada de plano arquivada em `historico/`.

### Direcionamentos

Teorizar uma fase e fazer, nunca teorizar todas. Mapa raso e fase corrente funda. Quem especificar
uma fase é obrigado a ler `COMPORTAMENTOS_PARQUEADOS.md`. O painel é vista, nunca fonte de verdade
— informação que não está em arquivo não entra nele. O que se compartilha entre plataformas é
comportamento, não código.

### Pendências

L1 (códigos de erro por máquina), L2 (erro enganoso em arquivo grande) e L5 (versionamento do
contrato), esperando a decisão da Etapa 2. E as PoCs, nenhuma rodada — a POC-1 continua sendo o
maior risco do projeto.

Encerradas no fim do chat: o teto de custo (US$ 100/mês de alarme) e o bug do modelo de diarização,
que saiu de escopo junto com o modelo.
