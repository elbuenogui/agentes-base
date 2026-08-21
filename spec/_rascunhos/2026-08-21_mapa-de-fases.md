# Mapa de fases — rascunho para aprovação

> PM, 2026-08-21. Contrato de **direção**, não de comportamento. Uma linha de profundidade por
> fase; nenhuma fase futura ganha spec. Aprovado, vira `spec/VISAO.md` + `spec/MAPA.md`.
> Numeração adotada: a do corpo do pré-projeto (9 fases + futura). O roadmap da §3, que tinha 8,
> fica corrigido por esta decisão.

## Decisões já tomadas (2026-08-21)

- **Onde roda o núcleo e onde mora a chave**: não decidido agora. Vira entrega da Fase 1, depois
  da PoC — as opções mudam conforme o tempo real seja ou não portável para fora do navegador.
- **Ordem das fases 4 e 5** (GPT × Watch): decisão adiada para o fim da Fase 3, quando as PoCs de
  Android já tiverem dito o que a plataforma permite. Até lá as duas ficam empatadas no mapa.

---

## F1 — Núcleo de transcrição

- **Objetivo**: fechar o contrato do núcleo, para que desktop, Android e Watch consumam a mesma
  capacidade sem reimplementá-la.
- **Entregável**: contrato de API documentado + decisão de hospedagem/chave tomada.
- **Critério de conclusão**: *alguém consegue escrever um cliente novo lendo só o contrato, sem
  abrir o `index.html`.*
- **PoC**: POC-6 — tempo real fora do navegador.
- **Depende de**: nada. É a fase que destrava todas as outras.
- **Estado**: caminho de arquivo pronto (`POST /transcrever`); tempo real vive no navegador.

## F2 — Desktop, ditado universal

- **Objetivo**: app de uso cotidiano que transforma voz em texto dentro de qualquer aplicação.
- **Entregável**: aplicativo com acionamento persistente, gravação, entrega do texto no destino e
  configurações.
- **Critério de conclusão**: você usa no dia a dia, em vez de digitar.
- **PoCs**: POC-1 inserção no campo em foco (bloqueante) · POC-2 janela flutuante não-ativável.
- **Depende de**: F1 (contrato) e da decisão de onde roda o núcleo.
- **Em aberto**: plataforma (só Windows?) · acionamento por atalho de teclado, ausente do
  pré-projeto e provavelmente o principal.

## F3 — Android, ditado universal

- **Objetivo**: a mesma capacidade no celular, começando pelo S22.
- **Entregável**: app Android com gravação e entrega do texto + **documento do que a plataforma
  permite e do que não permite** (a fase produz conhecimento, não só código).
- **Critério de conclusão**: você usa no celular; e as perguntas de integração estão respondidas
  com evidência, não com suposição.
- **PoCs**: POC-3 overlay + acessibilidade (bloqueante) · POC-4 app do ChatGPT.
- **Depende de**: F1. A hospedagem do núcleo vira bloqueante aqui — o celular não fala com um
  servidor que só existe no seu PC.
- **Nota**: hover não existe em toque. A interação do desktop não se reproduz; o núcleo, sim.

## F4 / F5 — Integração com GPT **e** Smartwatch (ordem em aberto)

**Integração com GPT** — objetivo: descobrir até onde dá para integrar a entrada de voz com uma
LLM já existente sem construir agente próprio. Entregável: definição clara do que é integrável,
automatizável, dependente de interação, proibido, e do que sobra para o sistema fazer.
Critério de conclusão: a pergunta da F6 ("precisamos de agente próprio?") pode ser respondida.

**Smartwatch** — objetivo: validar o relógio como dispositivo de entrada de voz, não como
assistente completo. Entregável: gravar → transcrever → mostrar/encaminhar. PoC: POC-5 (Wear OS,
latência, bateria, caminho de rede). Bloqueio conhecido: o aparelho precisa existir e estar em mãos.

## F6 — Agente open source

- **Objetivo**: reutilizar um agente maduro em vez de escrever um.
- **Gatilho**: só existe se a F5 concluir que a integração direta não basta. **Falta definir o
  critério que decide "não basta"** — sem ele esta fase nunca começa nem é descartada.
- **Entregável**: agente escolhido, justificado e integrado ao núcleo.

## F7 — Contexto

- **Objetivo**: o assistente considera o que você está fazendo ao interpretar o pedido.
- **Escopo**: captura **sob demanda**, no acionamento. Monitoramento contínuo de tela é outra
  coisa e fica fora.
- **Depende de**: F6 (ou da conclusão de que ela não é necessária).

## F8 — Ferramentas e automações

- **Objetivo**: o agente executa ações, não só devolve texto.
- **Depende de**: F7.

## F9 — Memória e contexto persistente

- **Objetivo**: continuidade entre interações e dispositivos.
- **Restrição do produto**: memória e estado **não podem ficar presos a uma LLM** — trocar de
  modelo não pode apagar o assistente.

## Fase futura — Tradução e intérprete

Fora da prioridade inicial. Reaproveita o pipeline pronto. Relevância maior no celular e no
relógio, em viagem.

---

## Fase 1, detalhada — as entregas, nesta ordem

| # | Entrega | Por quê |
|---|---|---|
| E1.1 | **Contrato da API**: endpoints, formatos, erros, limites | hoje existe código, não existe contrato; é o que os três clientes vão ler |
| E1.2 | **POC-6**: tempo real fora do navegador | responde se o tempo real pode ser capacidade do núcleo ou fica exclusivo da web |
| E1.3 | **ADR-001**: onde roda o núcleo e onde mora a chave | escrito **depois** da POC-6, porque o resultado dela muda as opções sobre a mesa |
| E1.4 | **Comportamento de erro** do núcleo | sem internet, API fora, áudio longo, silêncio, permissão negada — todo cliente herda isso |

Nada de E1.1 a E1.4 exige tocar no `index.html`.

---

## Pendências de método antes de abrir a Fase 1

1. `transcritor/frontend/index.html` está **modificado e não commitado** (interface enxuta +
   interruptor "Recortar"). O repositório perde o ponto de restauração conquistado hoje se a Fase 1
   começar por cima disso.
2. O plano de faxina está em 3 de 4 etapas — falta o repasse da Etapa 4. Abrir a Fase 1 é virada de
   plano, e virada de plano é o gatilho de arquivar o `PROGRESSO.md`.
3. Arquivos `.fuse_hidden*` na raiz e em `.claude/estado/` — lixo do bridge remoto, não do projeto.
   Backlog.
