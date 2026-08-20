# Nenhuma tarefa ativa

A antiga Etapa 2 (detecção de turno pela API) foi **encerrada sem uso** por decisão do usuário em
2026-08-20: `gpt-live-transcribe` recusa `turn_detection` diferente de `null`, e a alternativa
exigiria trocar para um modelo mais barato — recusado, porque o usuário prefere preservar nuance de
fala a economizar. A economia estimada e o contraponto medido ficaram registrados no Backlog do
`PLANO.md`, para o dia em que custo virar prioridade.

O plano ficou com **3 etapas**: a 1 (freios de custo, concluída), a 2 (janela de 24h na linha do
tempo) e a 3 (faxina — que agora inclui **remover o alternador de controle de turno**, código que
ficou sem uso).

Próximo passo: gerar a tarefa da **Etapa 2 (janela de 24 horas na escala "minuto")**. Ao gerar,
lembrar o Executor de consultar a skill `dataviz` antes de escrever código de visualização.

Não gerar automaticamente — aguardar o pedido explícito do usuário.
