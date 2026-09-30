---
tema: Skills de estado dos projetos e de consolidação macro
data: 2026-09-29
---

# Coleta — skill de estado dos projetos (2026-09-29)

## 1. Pedido e decisões

- [DIRECIONAMENTO] O usuário pediu duas skills: (a) consolidação e planejamento macro dos quatro
  projetos de agente — Mari, assistente, template científico e agentes-base; (b) o estado real de
  cada projeto, porque a página de Planejamento e Execução estava incompleta e defasada (a Mari
  mudou de prioridade e fechou a versão das perguntas operacionais fora do que o plano mostrava).
- [DECISÃO] Estado primeiro, consolidação depois — trade-off: a consolidação espera, mas passa a
  partir de um retrato confirmado de cada projeto, e não do que o PM supunha.
- [DECISÃO] A skill de estado mora no SISTEMA-DE-ORGANIZACAO (fora deste repositório), junto da
  página que consome o resultado. Não entra no PLANO.md da Fase 2 nem no kit exportável.
- [DECISÃO] Plano aprovado em quatro passos: fontes por projeto → skill em varredura completa,
  testada na Mari → modo pontual no encerramento de chat → rodada em todos e página atualizada.
  Registrado como tarefas no `tarefas.yaml` do Sistema e no `DIARIO.md` de lá.

## 2. O que o levantamento à mão da Mari ensinou (vira requisito da skill)

- [DIRECIONAMENTO] Ler primeiro a coleta e a retomada mais recentes e o git log; o PLANO de um
  projeto pode estar mais atrasado que a coleta (é o caso da Mari em 28/09).
- [DIRECIONAMENTO] Um projeto pode ter várias fontes (Mari: API aqui, site em `urbverde-ui`).
- [DIRECIONAMENTO] A skill não depende do agente: Claude e Codex escrevem nos mesmos arquivos.
- [PENDÊNCIA] O documento sobre a nova inserção da Mari na plataforma (UX) não foi achado no
  repositório da Mari; deve estar no repositório do site, que não está conectado.
- [DECISÃO] A Mari fica desatualizada no plano do Sistema até a skill rodar — trade-off: a
  recomendação da página segue errada para a Mari por uns dias, em troca de um teste honesto (a
  skill precisa chegar sozinha ao levantamento feito à mão em 29/09).

## 3. Onde a frente mora daqui em diante

- [DECISÃO] A frente "Estado dos projetos" passa a morar no SISTEMA-DE-ORGANIZACAO: plano no
  `tarefas.yaml`, decisões no `DIARIO.md`, retomada no `RETOMADA.md` de lá, a skill em
  `skills/estado-projetos/`. Não entra no PLANO.md deste repositório — trade-off: o registro sai
  deste repo, em troca de não misturar a Fase 2 do transcritor com um projeto que lê todos os outros.
- [ARTEFATO] Passo 1 concluído: `SISTEMA-DE-ORGANIZACAO/execucao/fontes.yaml`, sete projetos.
- [DIRECIONAMENTO] Próximos chats desta frente abrem com a pasta do Sistema conectada, sem papel
  PM/EXEC, lendo o `RETOMADA.md` de lá. O passo 3 (encerrar chat avisa o Sistema) volta a este
  repositório só como tarefa própria, pelo fluxo PM/EXEC daqui.
