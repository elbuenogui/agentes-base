---
artefato: DECISOES
status: vivo
---

# Decisões — livro-razão

Uma decisão por entrada, sempre com **a razão junto**. A razão é o que permite reabrir com
honestidade quando aparecer motivo novo, e o que impede reabrir por esquecimento.

Formato de cada entrada: `### D-nn — título` · `estado:` · a decisão · `Por quê:` · `Reabre se:`

---

### D-01 — O acionamento do desktop é atalho de teclado
`estado: fechada · 2026-08-21 · fase: F2`

O atalho é o acionamento principal e **precisa ser configurável** — o usuário vai mapeá-lo num
botão extra do mouse. O botão flutuante continua existindo, como complemento.

**Por quê:** clicar num botão tira o foco do campo de destino. O Windows resolve assim — o Win+H
manda pôr o cursor no campo *antes* de acionar.
**Reabre se:** a POC-1 mostrar um mecanismo de inserção que não dependa do foco no momento do
acionamento.

### D-02 — O núcleo é lote e streaming; o modo ao vivo fica congelado
`estado: fechada · 2026-08-21 · fase: F1`

Não portar, não reescrever, não apagar.

**Por quê:** o streaming já entrega "o texto aparece enquanto falo", vem do backend e serve
qualquer cliente. O ao vivo custa quase três vezes mais e não tem consumidor.
**Reabre se:** aparecer caso de uso de transcrição contínua (legenda de reunião), que é outro
produto, não o ditado.

**Endurecida em 2026-09-05 (`D-33`):** o usuário confirmou que isto não é mais reabrível por uso futuro — está descartado de vez, não só congelado.

### D-03 — O relógio é cliente magro, sempre
`estado: fechada · 2026-08-21 · fase: F4`

Grava e mostra; nunca processa.

**Por quê:** processar no pulso é bateria gasta fazendo pior o que o telefone faz melhor.
**Reabre se:** nunca, na prática — é decisão de produto, não de implementação.

### D-04 — O telefone é o núcleo do relógio
`estado: fechada · 2026-08-21 · fase: F4`

O relógio fala com o app do telefone pela Wearable Data Layer. **Decorrência: o relógio nunca
precisa da chave da API.**

**Por quê:** confirmado que o Wear OS entrega mensagem com o telefone no bolso e inicia o app se
preciso.
**Reabre se:** a POC-5 mostrar que a bateria não aguenta, ou que a gestão agressiva da Samsung mata
o serviço de forma incontornável.

### D-05 — Servidor próprio adiado, com gatilho declarado
`estado: substituída por D-36 em 2026-09-30 · 2026-08-21 · fase: F7`

O servidor nasce quando houver **estado compartilhado entre aparelhos** — Fase 7, obrigatório na 9.

**Por quê:** o servidor é a fronteira entre "ditado" e "assistente", e o ditado inteiro não precisa
dele. Antecipar custa autenticação para um usuário só, um salto de latência, e um serviço que
quando cai leva junto a ferramenta de todo dia.
**Reabre se:** o registro de consumo fragmentado entre aparelhos virar problema real antes da F7.

### D-06 — A linguagem do app desktop se decide depois da POC-1
`estado: fechada · 2026-08-21 · fase: F2`

**Por quê:** se a inserção exigir o Text Services Framework, empurra para .NET ou C++; se o teclado
sintético bastar, quase qualquer linguagem serve. Escolher antes é escolher a ferramenta antes de
saber o serviço.
**Reabre se:** —

### D-07 — Compartilha-se comportamento, não código
`estado: fechada · 2026-08-21 · fase: todas`

Por isso a Fase 1 entrega um **contrato**, não uma biblioteca.

**Por quê:** o núcleo são umas trezentas linhas; a parte cara é a integração com cada sistema
operacional, que não se compartilha de jeito nenhum.
**Reabre se:** o núcleo crescer a ponto de a duplicação passar a doer mais que a ponte entre
linguagens.

### D-08 — O núcleo não assume idioma, e não precisa de parâmetro
`estado: REVISADA em 2026-08-23 pela medição · fase: F1`

**Revisão:** a medição da Etapa 1 refutou o problema. Mesmo áudio (português com "commit",
"deploy", "pull request", "code review", "branch", "prompt"), com e sem `language="pt"`: **texto
idêntico caractere por caractere, tokens idênticos** (158 entrada / 46 saída nas duas chamadas,
logo custo idêntico). Forçar o idioma não muda nada mensurável.

**Consequências:** a Etapa 5 do plano **cai** — pela condição que ela própria trazia. O contrato
registra que o núcleo não assume idioma e **não expõe parâmetro novo**. O seletor de idioma sai do
parqueamento por falta de justificativa.

**Reabre se:** aparecer um caso real de transcrição saindo no idioma errado. Aí volta com evidência,
não com previsão. *(Ressalva honesta: a medição usou áudio em português; não testou se especificar
ajuda em outro idioma. Como a detecção automática acertou, o valor é baixo até haver falha real.)*

<details><summary>Texto original de 2026-08-21</summary>
`estado: superada · 2026-08-21 · fase: F1 (contrato) e F2 (interface)`

O contrato expõe `idioma` **opcional**; ausente significa detecção automática pela API. **O padrão
é ausente.** A interface da Fase 2 oferece a lista (português, inglês, espanhol, italiano, chinês)
como escolha, não como imposição.

**Por quê:** o usuário não vem tendo erro de idioma na prática, e prevê que forçar "português"
estrague as palavras estrangeiras que se usam em português — no uso real dele, ditando para o
Claude Code e para o VS Code, o vocabulário técnico em inglês é constante.
**Condicionada:** se a medição mostrar **diferença de custo** entre especificar e não especificar, a
decisão volta à mesa.
</details>

### D-09 — A verificação é manual, e isso está declarado
`estado: fechada · migrada para o cérebro em 2026-08-23`

**Decisão de método.** Mudou de casa: mora em
[`.claude/metodo/DECISOES_METODO.md`](../.claude/metodo/DECISOES_METODO.md) como **`M-01`**, com a
razão e a condição de reabertura. O identificador antigo fica aqui como ponteiro para não quebrar as
citações já escritas.

### D-10 — A régua do Win+H está aposentada; a régua passa a ser o app de hoje
`estado: fechada · 2026-08-21 · fase: F2`

O alvo de qualidade do app desktop **não é** empatar com a digitação por voz do Windows: é **não
piorar o que o usuário já usa todo dia**. A única coisa que o Win+H faz e o app de hoje não faz é
escrever direto no campo — e é exatamente isso que a Fase 2 vai construir.

**Por quê:** o usuário reporta que o app atual já é mais rápido, mais preciso e com mais opções que
o Win+H. Uma régua já superada não serve de alvo.
**Reabre se:** —

### D-11 — Windows primeiro, mas a camada de inserção nasce isolada
`estado: fechada · 2026-08-21 · fase: F2`

O desktop **não é só Windows** como ambição. Mas se constrói para Windows primeiro, com a inserção
de texto num módulo próprio, trocável por sistema operacional.

**Por quê:** interface multiplataforma é fácil; **inserir texto no campo de outro aplicativo não
é** — são três implementações distintas (Windows: TSF/SendInput; macOS: API de Acessibilidade com
permissão explícita do usuário; Linux: X11 funciona, e o Wayland bloqueia entrada sintética por
desenho, com solução variando por compositor). Isolar a camada custa pouco agora e evita reescrever
o app inteiro depois.
**Reabre se:** aparecer um segundo computador de uso real — aí a fase de portabilidade ganha data.

### D-12 — A Fase 6 (agente) acontece de qualquer forma
`estado: fechada · 2026-08-21 · fase: F6`

O resultado da fase de integração com GPT define **quando**, não **se**. Se a integração não
funcionar de jeito nenhum, o agente entra imediatamente; se funcionar, é testada por mais tempo e o
agente vem depois.

**Por quê:** decisão de produto do usuário. Isso encerra a Q6 na forma em que ela existia: não
falta mais um critério de "não bastar" para a fase existir — falta só um critério de urgência.
**Reabre se:** —

### D-13 — As lacunas da Fase 2 são a primeira parte da própria Fase 2
`estado: fechada · 2026-08-21 · fase: F2`

Histórias de usuário, lista de entregáveis e definição de MVP não são pré-requisito da Fase 2: são
a **primeira entrega dela**.

**Por quê:** decisão do usuário, e coerente com a regra de teorizar uma fase e fazer. Escrever isso
antes da POC-1 seria escrever sobre suposição.
**Reabre se:** —

### D-14 — "Diagnóstico geral" é um comando com painel
`estado: fechada · migrada para o cérebro em 2026-08-23`

**Decisão de método.** Mora em [`.claude/metodo/DECISOES_METODO.md`](../.claude/metodo/DECISOES_METODO.md)
como **`M-02`**. O endereço fixo do painel e a identidade visual continuam sendo deste projeto e
moram na skill `diagnostico-geral`.

### D-15 — Colocar o texto não o consome; a janela é que se minimiza
`estado: fechada · 2026-08-21 · fase: F2`

Depois de a transcrição ser colocada num campo, ela **continua disponível** para ser colocada de
novo. O que acontece é que a janela se minimiza sozinha, e volta a aparecer quando o mouse passa
sobre o botão flutuante.

Três estados para a janela do desktop: **gravando**, **mostrando o resultado**, **minimizada**.

**Por quê:** separar *ditar* de *colocar* (ver `COMPORTAMENTOS_PARQUEADOS.md`) só faz sentido se
colocar puder acontecer mais de uma vez. E minimizar em vez de apagar mantém a tela limpa sem
perder o texto.

**Nota técnica que sustenta a decisão:** hover funciona como revelador justamente porque **passar o
mouse não rouba foco** — só o clique rouba. É por isso que o hover pode ser o gatilho de exibição
enquanto o clique não pode ser o gatilho de gravação (`D-01`). As duas decisões são a mesma
observação vista de dois lados.

**Divergência conhecida para a F3:** no Android não existe hover. O estado minimizado vai precisar
de um equivalente por toque, e isso se resolve na especificação da fase Android, não aqui.

**Reabre se:** a POC-2 mostrar que uma janela sempre no topo e não-ativável não recebe eventos de
mouse de forma confiável no Windows.

### D-16 — O gate de silêncio é obrigação declarada do cliente
`estado: fechada · 2026-08-23 · fase: F1 (contrato) e todas as fases de cliente`

**Achado da medição, e o mais importante dela.** Áudio de silêncio puro enviado ao núcleo **não**
devolve texto vazio nem erro: devolve `200` com **alucinação em idioma aleatório** — `"Sélectionnez
la."` em francês sem streaming, `"都没有。"` em chinês com streaming.

Isso nunca apareceu no uso porque **a interface web protege**: `index.html:2195` compara o pico de
amplitude da gravação com `LIMIAR_SILENCIO` e **não envia** o áudio. A proteção mora no cliente, não
no núcleo.

**A decisão:** o contrato passa a declarar, como obrigação do cliente, **medir a amplitude e não
enviar áudio sem fala**. Todo cliente novo — desktop, Android, Wear — tem de reimplementar o gate.

**Por quê:** num app de ditado que escreve no campo em foco, a falha não é um texto errado na tela:
é `"Sélectionnez la."` aparecendo dentro do documento de alguém. E o núcleo recebe áudio já
codificado, enquanto o cliente tem o fluxo cru — o gate é barato lá e caro aqui.

**Nota de método:** isto é exatamente o que o exercício do contrato existe para achar — um
comportamento que parecia do produto e era de um cliente só. Não é requisito inventado pelo PM: é a
formalização do que o app já faz.

**Reabre se:** o núcleo passar a receber áudio cru, ou a API deixar de alucinar em silêncio.

### D-17 — `gpt-4o-transcribe-diarize` está fora de escopo
`estado: fechada · 2026-08-23 · fase: F1 e seguintes`

O modelo de diarização sai do escopo por ora. Os dois achados da medição que dependem dele —
`custo_usd` sempre zerado (`main.py:35-38` não tem entrada de preço para ele) e ausência de eventos
`delta` em streaming — **não viram tarefa**. Ficam registrados no contrato como comportamento
conhecido.

**Por quê:** decisão do usuário. E o fato sustenta: o modelo já estava **desativado da lista da
interface desde 2026-08-18** (`index.html:590` e `697`, comentado a pedido do usuário por
qualidade). Ou seja, o bug de custo é inalcançável no uso normal — corrigi-lo agora seria consertar
o que ninguém aciona.

**Reabre se:** a diarização voltar a ser útil (separar quem fala o quê numa entrevista ou reunião).
Aí o bug de custo volta junto, e vem antes de qualquer uso real — dado de consumo errado é pior que
funcionalidade ausente.

### D-18 — Alarme de custo em US$ 100/mês
`estado: fechada · 2026-08-23 · fase: método`

Alarme, não limite rígido: passar disso é sinal de mudança de padrão de uso, e aí se investiga.

**Por quê:** decisão do usuário. Referência medida: US$ 0,53 no projeto inteiro em 343 requisições,
de 18 a 23 de agosto, em dias de desenvolvimento pesado — o alarme fica cerca de duas ordens de
grandeza acima do observado, o que o torna um sinal de anomalia e não um freio de uso.

**Reabre se:** o padrão de uso mudar de fato — por exemplo, se o modo ao vivo voltar (custa 2,8×
mais por minuto) ou se o assistente passar a chamar LLM a cada acionamento.

> **A condição de reabertura foi acionada em 2026-08-27** pela `D-31` (geração de imagem): uma imagem
> de qualidade média custa ~US$ 0,042, contra ~US$ 0,0003 de uma transcrição de 30 s. O alarme
> continua em US$ 100/mês, mas a referência que o justificava (US$ 0,53 em cinco dias) não vale mais
> como base de comparação. **Reavaliar depois de uma semana de uso do gerador de imagem.**

### D-19 — Entre dois documentos que se contradizem, o mais recente vence
`estado: fechada · migrada para o cérebro em 2026-08-23`

**Decisão de método.** Mora em [`.claude/metodo/DECISOES_METODO.md`](../.claude/metodo/DECISOES_METODO.md)
como **`M-03`**; a regra em si está em `.claude/metodo/CONSISTENCIA.md`.

### D-20 — O núcleo declara prazo de espera de 120 segundos
`estado: fechada · 2026-08-23 · fase: F1`

O backend passa a declarar timeout próprio de **120s de leitura**, mantendo os 5s de conexão, e
devolve `TEMPO_ESGOTADO` ao estourar. Hoje ele não declara nada e herda o default do SDK: 600s.

**Por quê:** o áudio de 12,7s da medição da Etapa 1 voltou em cerca de 2s. 120s cobre com folga uma
gravação longa e ainda assim falha rápido o bastante para o usuário não achar que o app morreu. Num
app de ditado, esperar 10 minutos por uma resposta que não vem é falha de produto, não de contrato.

**Reabre se:** aparecer uso real de áudio longo o suficiente para encostar nos 120s — aí o número
sobe com a medição na mão, não por precaução.

### D-21 — Todo fato tem um dono único, e o painel confere
`estado: fechada · migrada para o cérebro em 2026-08-23`

**Decisão de método.** Mora em [`.claude/metodo/DECISOES_METODO.md`](../.claude/metodo/DECISOES_METODO.md)
como **`M-04`**; as regras em si estão em `.claude/metodo/CONSISTENCIA.md`.

### D-22 — O histórico de transcrições é requisito, não efeito colateral
`estado: fechada · 2026-08-21, promovida ao livro-razão em 2026-08-23 · fase: F2`

Ver uso e histórico **interessa ao usuário** — não é subproduto do backend guardar arquivo. Ainda
incipiente e não mapeado. **Não vira trabalho agora**: o contrato da Fase 1 documenta o histórico
como ele é hoje, e a funcionalidade ganha história de usuário própria na especificação da Fase 2,
porque é lá que alguém vai olhar para ela.

**Por quê:** decisão do usuário em 2026-08-21, respondendo a Q7. Promovida ao livro-razão em
2026-08-23 pela regra de dono único da `D-21` — a resposta morava solta em `QUESTOES_ABERTAS.md`,
que pela regra nova só deve guardar a pergunta e o ponteiro. Chamar de requisito muda o padrão de
qualidade exigido: dado de histórico errado deixa de ser ruído e passa a ser defeito.

**Consequências abertas, que esperam a Fase 2:**

- o histórico existe hoje como efeito colateral: `consumo.jsonl` e `transcricoes.jsonl`, **não
  versionados**, sem política de retenção, presos à máquina onde o backend roda;
- `consumo.jsonl` **mistura uso real com sessões de teste do Executor** — enquanto era ruído, tudo
  bem; sendo requisito, é dado errado. Os números de `gpt-live-transcribe` anteriores a 2026-08-19
  ainda estão subestimados, porque o último turno de cada gravação se perdia antes da correção;
- a troca de arquivo local por banco de dados está no Backlog desde 2026-08-18, adiada pelo usuário.

**Reabre se:** o usuário deixar de consultar uso e histórico na prática — aí volta a ser efeito
colateral e sai do escopo da Fase 2 em vez de ganhar história própria.

### D-23 — Não se troca o modelo do modo ao vivo para economizar
`estado: fechada · 2026-08-20, promovida ao livro-razão em 2026-08-23 · fase: F1`

Trocar `gpt-live-transcribe` (US$ 0,017/min) por `gpt-4o-transcribe` (US$ 0,006/min) no modo ao vivo
foi **avaliado e recusado pelo usuário**. Não será executado. A ideia sobrevive em `B-02`, para o dia
em que custo virar prioridade.

**Por quê:** o usuário prefere preservar nuance de fala — pontuação, ênfase — a economizar, tendo
recurso disponível. E a economia real é bem menor do que o preço de tabela sugere: o modelo mais
barato só fecha turno sozinho usando a detecção de turno da API, o que obriga a **desligar o gate de
silêncio** — passa-se a pagar o tempo todo, não só a fala. O preço do modelo cai 65%, mas a economia
efetiva fica em ~50% numa sessão típica com ~30% de silêncio, e ~29% se metade da sessão é silêncio.
Em dez minutos com 30% de silêncio: US$ 0,119 → US$ 0,060.

**Contraponto medido, que quem reabrir precisa ver junto:** o `BENCHMARK.md` mostra
`gpt-4o-transcribe` em lote produzindo pontuação e acentuação impecáveis num áudio de 72s, enquanto o
modo ao vivo atual produz "Isso e um teste da transcricao" sem acentos e parte palavras nas emendas.
Ou seja, há indício de que a perda de nuance venha do **tamanho do pedaço enviado** (fatias de 6s),
não do modelo — o que enfraquece a própria razão da recusa. **Quem retomar isto deve testar essa
hipótese antes de decidir**, e não reabrir só pelo preço.

**Reabre se:** custo virar prioridade, ou a hipótese do tamanho do pedaço for testada e confirmada —
aí a troca deixa de custar nuance e a razão da recusa cai.

### D-24 — O assistente é o produto principal, e o agente espera o uso diário
`estado: fechada · 2026-08-23 · fase: todas`

O `agentes-base` é a **base para trabalhar** — o núcleo do método e suas atribuições. Dentro dele
nasceu uma ferramenta, a transcrição, que já está em uso todo dia. A partir do botão, ela evolui para
melhorar a eficiência do usuário e **instalar a infraestrutura** que um agente vai exigir depois.

**O núcleo do agente não começa agora.** Já existem agentes disponíveis e bons o suficiente para
construir com eles; aprofundar no agente próprio agora é resolver duas vezes o mesmo problema.

**Por quê:** a régua é de uso, não de funcionalidade. Para o assistente valer mais que os agentes que
o usuário já usa, ele precisa estar **integrado ao cotidiano** — o projeto tem que primeiro se tornar
relevante para si mesmo. É isso, e não sequenciamento técnico, que justifica adiar o agente.

**Consequência de método:** dá à Fase 2 um critério de encerramento mais duro que "está pronto" —
**ela fecha quando o usuário usa todo dia**. Reforça a regra de que uma fase só encerra com o
entregável em uso, e explica por que essa regra é dura aqui em vez de burocracia.

**Reabre se:** o assistente se mostrar incapaz de entrar na rotina sem a camada de agente — aí a
ordem se inverte com evidência de uso, não por previsão.

### D-25 — Começar pelo clipboard com atalho global, e refinar com o uso
`estado: fechada · 2026-08-25 · fase: F2`

A Fase 2 começa construindo o **menor app que já entrega valor** — atalho global, gravar,
transcrever, clipboard — em vez de investigar por qual mecanismo inserir texto no campo em foco. A
POC-1 original (quatro alvos × três mecanismos) **sai do caminho crítico** e vira `B-22`.

**Decorrência: a linguagem do app é Python.** A `D-06` dizia que ela sairia da POC-1; sem a PoC, o
critério passa a ser iterar rápido no que o projeto já usa. Atalho global e clipboard são triviais em
Python, e a camada de inserção nasce isolada (`D-11`) para que trocar de linguagem depois custe só
aquele pedaço.

**Por quê:** decisão do usuário — *"ao invés de ficar explorando e explorando alternativas para poder
começar, vamos já começar"*. E é coerente com a `D-24`: a régua da fase é uso diário, não
funcionalidade. Um app que não existe não entra em rotina nenhuma, por melhor que seja a investigação
que o precede.

**A trava que o PM acrescentou, e que o escopo original não tinha:** clipboard sozinho não entrega
nada que o app web já não faça. **O atalho global é o que torna a primeira versão diferente do que
existe** — ditar sem trocar de janela. Sem ele, a etapa entrega o produto atual sem o navegador.

**Reabre se:** o uso mostrar que copiar e colar à mão é atrito suficiente para atrapalhar — aí a
inserção automática volta do backlog com evidência de uso real, que é melhor base do que a
investigação teria dado.

### D-26 — A inserção de texto tem de disparar de dentro do atalho global
`estado: fechada · 2026-08-26 · fase: F2 e seguintes`

Quando a inserção automática no campo em foco entrar (`B-22`), ela **precisa ser disparada de dentro
do handler do atalho de teclado global** — ou de um evento de entrada real equivalente. **Nunca** de
um serviço, fila, timer ou processo desacoplado da entrada do usuário.

**Por quê:** achado por medição na tentativa parcial da POC-1, em 2026-08-25. Quatro tentativas de
injeção (teclado sintético e clipboard, em dois alvos) **falharam silenciosamente** — campo vazio,
sem erro, com a janela-alvo confirmada em foco por leitura de `GetForegroundWindow()`. A causa foi
isolada: `SetForegroundWindow` devolveu `False`, porque o processo que disparava não carregava o
crédito de *entrada de usuário recente* que o Windows exige para entregar entrada sintética de forma
confiável.

**A consequência é de arquitetura, não de escolha de mecanismo.** Não importa qual dos três
mecanismos se use: se o disparo vier de um processo desacoplado, todos falham do mesmo jeito — e
falham **em silêncio**, que é o pior modo possível, porque parece bug de mecanismo.

**Revisa a `D-06`:** a escolha de linguagem e framework do app passa a ter uma restrição concreta —
tem de conseguir executar a inserção **dentro** do handler do atalho, de forma síncrona.

**Efeito colateral feliz:** o app da Etapa 1 já nasceu com atalho global (`D-25`), então ele já está
na única arquitetura em que a inserção vai funcionar. O corte de escopo do usuário, feito por outra
razão, acertou esta por acidente.

**Reabre se:** aparecer no Windows um caminho de inserção que não dependa desse crédito — a API de
acessibilidade (`UI Automation`) é candidata, porque escreve no controle em vez de sintetizar
entrada, e não chegou a ser confirmada de ponta a ponta.

### D-27 — A interface do desktop é reescrita em Python, e a janela fica sempre no topo
`estado: fechada · 2026-08-27 · fase: F2`

O app de desktop **reescreve** a interface — não embute a interface web numa janela nativa. E a
janela do app **fica sobreposta a qualquer outra janela**, sempre.

**Por quê:** decisão do usuário em 2026-08-27, quando pus a bifurcação para ele. Mantém de pé o que
ele já tinha dito em 21/08 (`COMPORTAMENTOS_PARQUEADOS`): *"o código não se aproveita; o desenho
sim"*. Embutir o `index.html` daria paridade no primeiro dia, mas acoplaria o desktop à interface
web — e toda divergência futura (janela flutuante, inserção no campo em foco, três estados da
janela) passaria a ser um `if` dentro de um arquivo que tem outro dono.

**Sempre no topo tem uma consequência técnica que não é opcional:** a janela precisa aparecer por
cima **sem roubar o foco**. É a mesma observação da `D-01` e da `D-15` vista de novo — quem rouba o
foco destrói o campo de destino. No Qt isso é `WindowStaysOnTopHint` + `Tool` +
`WA_ShowWithoutActivating`; em qualquer outro toolkit, é um requisito a provar antes de seguir.

**Fecha a `D-06`** ("a linguagem do app se decide depois da POC-1"): decidido **Python**, porque a
`D-26` exige que a inserção dispare de dentro do handler do atalho global, e é isso que o app atual
já faz com a biblioteca `keyboard`. A escolha de toolkit vai na tarefa; a linguagem está fechada.

**Reabre se:** o toolkit escolhido não conseguir ficar no topo sem ativar a janela, ou se a
reescrita da paridade (`SPEC-002`) mostrar que o custo de manter duas interfaces com o mesmo
comportamento é maior que o do acoplamento que se evitou aqui.

### D-28 — O acionamento alterna, e o atalho se configura pela interface
`estado: fechada · 2026-08-27 · fase: F2`

Gravar é **alternar**: um toque começa, outro toque para e envia. **Não é segurar** a tecla. E o
atalho global se troca **dentro do app**, nas Configurações — não editando `config.json`.

**Por quê:** relatado no uso real em 2026-08-27 — *"esse F17 ou F9 é uma péssima tecla para
apertar"* e *"ele não grava direito"*. Segurar uma tecla por trinta segundos enquanto se fala é
desconfortável, e transforma qualquer escorregada de dedo em gravação cortada — que é o modo de
falha mais provável por trás do "não grava direito". A interface web sempre alternou (`SPEC-002`,
`A1`); segurar foi invenção da primeira volta da Etapa 1, não estava em lugar nenhum.

E escolher a tecla certa **por mim** era o erro se repetindo em outra tecla: quem sabe qual botão do
mouse ele mapeou é ele. Configurável pela interface fecha a `D-01` do jeito que ela pedia desde
21/08 — *"precisa ser configurável — o usuário vai mapeá-lo num botão extra do mouse"*.

**Reabre se:** o uso mostrar que alternar deixa gravação aberta esquecida com frequência — o corte
de segurança de 2min30s (`SPEC-002`, `A5`) é a rede que existe justamente para esse risco.

### D-29 — Paridade não se entrega em partes
`estado: fechada · 2026-08-27 · fase: F2`

Quando o critério é **paridade com algo que já existe**, a entrega é a lista inteira. Não se fatia
em partes, não se marca etapa como concluída com um pedaço da lista, e não se manda o usuário
"conviver com o que já dá" enquanto o resto vem depois.

**Por quê:** duas voltas seguidas reprovadas em 2026-08-26 e 2026-08-27, pelo mesmo motivo, e as
duas por decisão minha de escopo. A segunda entregou o fluxo de ditado inteiro e correto — e mesmo
assim ouviu *"ainda estamos longe do mínimo"*, porque faltavam o Consumo, os itens do menu e a
aparência. **Paridade é piso, e piso pela metade continua abaixo do piso.** Meio piso não é meio
valor: é zero, porque o usuário continua tendo de voltar para a ferramenta antiga.

A régua da fase (`D-10`) diz "não piorar o que ele já usa". Enquanto faltar um item da lista, o app
é pior do que o que ele já usa, mesmo que cada item entregue esteja perfeito.

**O que isto muda no meu jeito de escopar:** fatiar continua certo para funcionalidade **nova**, que
nasce de nada e cresce por partes — foi o que o usuário pediu quando disse *"qualquer coisa mais
além disso, a gente implementa aos poucos"*. Ele estava separando as duas coisas na mesma frase, e
eu li só a segunda metade.

**Reabre se:** aparecer um item de paridade tão caro que segurar tudo o mais por causa dele saia
pior para o usuário — e nesse caso quem decide segurar ou soltar é ele, com o custo na mesa, não eu
sozinho ao escrever a tarefa.

### D-30 — O desktop pode divergir da web, e toda divergência é declarada na spec
`estado: fechada · 2026-08-27 · fase: F2 e seguintes`

A paridade (`SPEC-002`) é **piso, não teto**. O desktop pode se afastar da interface web quando o uso
real pedir — mas **cada afastamento vira uma linha na própria spec**, dizendo o que a web faz, o que
o desktop faz e por quê. Divergência não declarada é defeito.

Primeiras três, pedidas pelo usuário em 2026-08-27 depois de usar o app:

| ponto | web | desktop | motivo |
|---|---|---|---|
| corte de segurança (`A5`) | 2 min 30 s | **5 min** | é no desktop que se dita de verdade; 2min30 cortava fala no meio |
| padrão de copiar/recortar (`D1`, `F4`) | copiar | **recortar** | o texto vai embora para outro aplicativo e não volta; deixar o anterior na caixa faz a gravação seguinte empilhar em cima de lixo |

Mais três, do mesmo dia, depois de mais uma sessão de uso:

| ponto | web | desktop | motivo |
|---|---|---|---|
| onde o balão aparece (`B4`) | rodapé da tela, 2 s | **acima do botão de gravar**, discreto, 3 s | numa janela pequena e sempre no topo, o rodapé fica longe de onde o olho está |
| painel de consumo (`G`) | modal por cima da página | **janela própria**, redimensionável | a janela do ditado é pequena de propósito; a linha do tempo vazava dela |
| fundo dos botões-ícone (`I`) | `#e4e7eb` | **`#eef1f5`**, mais leve | pedido direto do usuário — "mais claro", "bola nos outros em uma cor mais leve" |

**Nenhuma delas muda a interface web**, que segue como está.

**Por quê a regra, e não só as três mudanças:** sem ela, a próxima conferência de paridade acharia
essas diferenças e as trataria como falha de transcrição do desenho — e alguém "consertaria" de
volta. A spec é que tem de saber a diferença entre um desvio e uma decisão.

**Consequência para quem confere:** ao comparar as telas, divergência encontrada e **não** listada na
spec é achado; listada, é decisão, e não se toca.

**Reabre se:** as divergências crescerem a ponto de a `SPEC-002` virar mais tabela de exceção que
lista de paridade — sinal de que o desktop passou a ter desenho próprio, e aí ele merece uma spec
própria em vez de uma lista de diferenças.

### D-31 — Geração de imagem entra fora do plano, e o núcleo deixa de ser só de transcrição
`estado: fechada · 2026-08-27 · fase: F2, fora do plano da fase`

O app ganha **gerar imagem a partir de imagens de referência e um prompt**, no menu ⋮. E o núcleo
ganha uma segunda operação de IA — deixa de ser **núcleo de transcrição** e passa a ser, de fato,
**a camada que fala com a OpenAI** em nome dos clientes.

**Por quê:** pedido direto do usuário em 2026-08-27, com a razão dita: ele precisa gerar essas
imagens **agora**, e quer a solução mais rápida possível. É uso real batendo à porta, que é
exatamente o que este projeto existe para atender.

**Está fora do plano da Fase 2, e isso fica escrito em vez de disfarçado.** A F2 é "desktop, ditado
universal"; imagem não é ditado. Não vira etapa da fase nem entra no critério de conclusão dela —
entra como **anexo declarado**, com data e motivo, para ninguém acher daqui a um mês que a fase
mudou de objetivo.

**Por que no núcleo, e não no app chamando a OpenAI direto:** a chave da OpenAI mora num lugar só
(`transcritor/.env`), e o registro de consumo mora num lugar só (`consumo.jsonl`). Duplicar a chave
no desktop para ganhar meia hora sairia caro na primeira vez que alguém precisasse trocá-la — e o
custo de imagem, que é **duas ordens de grandeza maior** que o de transcrição, ficaria invisível no
painel de Consumo.

**Guarda-corpo obrigatório, não opcional:** uma imagem de qualidade média a 1024×1024 custa
~**US$ 0,042** — contra ~US$ 0,0003 de uma transcrição de 30 s. São ~140×. O alarme de US$ 100/mês
(`D-18`) foi calibrado sobre um padrão de uso em que o gasto do projeto inteiro em cinco dias foi
US$ 0,53; **este recurso muda o padrão**, que é literalmente a condição de reabertura escrita na
`D-18`. Por isso: preço por token dos modelos de imagem entra na tabela do backend, o custo aparece
no painel de Consumo como qualquer outra requisição, e a estimativa fica visível **antes** de gerar.

**Reabre se:** o recurso pegar e crescer. Aí a pergunta certa não é "como melhorar isto dentro do app
de ditado", é **se ele ainda deve morar num app de ditado** — e a resposta provavelmente é um segundo
cliente do mesmo núcleo, que é o desenho que a `D-07` já previa.

### D-32 — O botão flutuante entra em construção: compacto por padrão, expande no hover e nos estados ativos (refina D-15)
`estado: fechada · 2026-09-05 · fase: F2, além da paridade (já listado na SPEC-002)`

O app passa a nascer **compacto**: só o botão de gravar (o círculo de 72×72 já existente), sem
moldura, sempre no topo, arrastável. A janela cheia de hoje (caixa de transcrição, copiar/recortar,
menu ⋮ com Configurações · Consumo · Enviar arquivo · Gerar imagem) só aparece quando:

- o mouse passa por cima do botão (hover) — mostra **tudo**, como já é hoje, sem versão reduzida;
- o app entra em **gravando** ou **processando** — expande sozinho, independente do mouse estar em
  cima ou não, para o estado ficar visível sem exigir hover.

**Volta a encolher só depois de duas condições juntas**: o texto já ter sido colocado (copiado ou
recortado) **e** o mouse ter saído da área expandida. Encolher com o resultado ainda na tela e sem
ação do usuário perderia o texto de vista sem ele ter decidido isso.

**Por quê:** isto é a `D-15` finalmente construída — três estados da janela e botão flutuante,
decidido em 21/08, listado na `SPEC-002` como "além da paridade... vira etapa própria, aos poucos".
Pedido direto do usuário em 2026-09-05: a janela grande de hoje fica no caminho quando ele não está
ditando.

**Reconciliação com a `SPEC-002`, item J1** (*"a janela nunca muda de tamanho por conta própria"*):
J1 foi escrito contra conteúdo interno aparecendo/sumindo (cronômetro, faixa de amplitude, balão)
fazendo a janela pular de tamanho **sem ninguém ter pedido isso**. A troca compacto ⇄ expandido é
diferente: é deliberada, nomeada, e é o próprio desenho da `D-15` desde 21/08 — não é o que J1 foi
escrito para proibir. Registrar isto explicitamente para a próxima conferência de paridade não tratar
o hover/expansão como achado de J1.

**Sobre o Android (F3):** divergência já conhecida e escrita na própria `D-15` — toque não tem hover.
O equivalente por toque se resolve na especificação da F3, não aqui; esta decisão é só do Windows.

**Reabre se:** o uso real mostrar que expandir durante a gravação distrai mais do que ajuda, ou que
o critério de recolhimento (colocado + mouse fora) deixa o resultado sumindo antes da hora.

### D-33 — Inserção automática e modo ao vivo saem de vez, não é "depois"
`estado: fechada · 2026-09-05 · fase: F1 e F2`

**Confirmado pelo usuário, ao revisar o plano numa retomada:** tanto a **inserção automática no
campo em foco** (`B-22`, a investigação da `POC-1`) quanto o **modo ao vivo / tempo real** (`D-02`)
estão **definitivamente fora** — não é adiamento nem congelamento, é descarte.

**Por quê registrar como decisão nova, em vez de só mudar o estado do backlog:** os dois apareciam
nos arquivos com palavras que sugerem reversibilidade — `B-22` como `adiada`, com um gatilho
declarado; `D-02` como "congelada". Foi exatamente essa leitura que fez o PM reapresentar os dois
como assunto em aberto numa conversa de retomada, quando o usuário já os considerava encerrados. O
erro não foi de memória de conversa — foi de **status desatualizado em arquivo**, e por isso o
conserto é no arquivo, não só no que se fala.

**O que muda, e onde:**
- `spec/BACKLOG.md`: `B-22` vira `morta`; `B-03` e `B-04`, que dependiam do ao vivo descongelar,
  também viram `morta` — o gatilho deles nunca vai acontecer.
- `D-02` e `D-26` **continuam existindo como registro histórico** (o achado técnico da `D-26` segue
  verdadeiro se algo parecido for revisitado por outro motivo), mas `VISAO.md`, `SPEC-002` e
  `COMPORTAMENTOS_PARQUEADOS.md`, que diziam "congelado"/"adiada", passam a apontar para esta
  decisão.
- **O que não muda:** a segunda ação "colocar a última transcrição", com atalho próprio (lida da
  memória do app, nunca do clipboard) — é outra coisa, disparada por gesto explícito do usuário, e
  continua parqueada normalmente em `COMPORTAMENTOS_PARQUEADOS.md`. Não confundir as duas.

**Reabre se:** nunca, na prática — é decisão de produto, não investigação técnica pendente (mesmo
padrão da `D-03`).

**Refinada em 2026-09-05, segunda rodada (achados do usuário rodando no Windows real):**

1. **O compacto está grande demais.** 110×110 foi escolha da primeira volta, não medida do usuário.
   O tamanho compacto deve **abraçar o botão de gravar** — largura e altura pouco maiores que o
   próprio `BotaoGravar`, não um valor redondo arbitrário.
2. **Bug: parou de encolher depois do primeiro ciclo.** Funciona uma vez (grava → coloca → encolhe)
   e nos ciclos seguintes fica preso expandido. Isto é regressão, não refinamento — corrigir antes
   de qualquer outra coisa.
3. **Transição abrupta.** Expandir e encolher devem ser **animados** (suaves), não um resize
   instantâneo — nos dois sentidos.

**Reabre se:** o item 2 (bug) reaparecer depois de corrigido, ou o tamanho/animação escolhidos ainda
incomodarem no próximo uso.

**Segunda rodada entregue em 2026-09-05 (mesmo dia, por outro subagente Executor):**

- **Causa do bug, achada por medição, não suposição**: `_resultado_pendente` era um booleano
  desligado só em dois lugares; qualquer outro caminho que mudasse o texto (apagar pelo teclado,
  Ctrl+X, editar à mão, copiar com a caixa vazia) deixava o sinalizador ligado para sempre, travando
  o encolhimento a partir do segundo ciclo. Corrigido na raiz: virou função **derivada** (compara a
  caixa com o último texto colocado) — não existe mais estado para travar.
- Rede de segurança adicionada: `_corrigir_tamanho_do_modo()` reassenta a janela a cada 100ms se o
  tamanho fugir do modo atual — defesa para o que não dá para testar fora do Windows real.
- Tamanho compacto passou a ser **medido em tempo de execução** contra o `BotaoGravar` real (72×72
  + 8px de margem = 88×88), não mais um valor fixo.
- Animação: `QPropertyAnimation`, `InOutCubic`, 160ms, com a âncora refeita contra o layout real a
  cada quadro (não interpolada) — achou e corrigiu um desvio de 39px perto da borda superior da
  tela, exatamente onde este app abre por padrão.
- Suíte `desktop/testes_janela_compacta.py` criada e versionada (fora da lista original de arquivos
  da tarefa; aceito pelo PM — é o que teria pego o bug antes de chegar ao usuário).

**Pendências que seguem só confirmáveis no Windows real**: suavidade percebida da animação, hover,
sempre-no-topo, translucidez, microfone e núcleo real.

**Terceira rodada entregue em 2026-09-05 (mesmo dia):**

- **Botão pulando na animação — causa provada por medição de pixel**: o reflow de layout por
  quadro (segunda rodada) posicionava o botão nas coordenadas do layout de 672px enquanto a janela
  real ainda tinha 88px — o botão ficava **recortado pelo próprio limite da janela** (círculo de
  21×25px em vez de 65×65px no primeiro quadro). Achou também um bônus: o menu ⋮ ficava preso em
  estado de hover depois de cada expansão, mesma causa.
- **Arquitetura da animação trocada**: em vez de refluir o layout a cada quadro, agora interpola a
  janela inteira (posição + tamanho) entre dois retângulos fixos, com os layouts congelados; o
  conteúdo fica escondido durante os 160ms e volta no assentamento. Desvio medido: **0px**, círculo
  sempre 65×65, nos dois sentidos e nos três cantos testados.
- **Largura do compacto — não reproduzida em headless, hipótese específica registrada**: o plugin
  `offscreen` não propaga tamanho mínimo ao sistema de janelas (`propagateSizeHints()` não
  suportado); no Windows real isso pode fazer o sistema impor um mínimo próprio
  (`SM_CXMINTRACK`, ~112–136px), que é **assimétrico entre largura e altura** — bate exatamente com
  "não diminuiu a lateral". A rodada anterior também zerava o mínimo durante as transições
  (`setMinimumSize(0,0)`); corrigido para declarar sempre 88. Log de diagnóstico acrescentado
  (tamanho alvo vs. real vs. DPI) para a próxima execução real revelar a causa de fato.
- Monitor do usuário roda a 125%: 88px lógicos = 110px físicos — é escala, não bug.
- **"Sair" adicionado ao menu ⋮**, quinto item, `close()` + `QApplication.quit()`, testado com um
  laço de evento real.
- **Prova de regressão**: a suíte nova rodada contra o `app.py` da rodada anterior falhou nos
  mesmos pontos relatados pelo usuário — evidência de que os testes agora pegam o que headless não
  pegava antes.

**Quarta rodada entregue em 2026-09-05 (mesmo dia) — mudança de arquitetura, não confirmação:**

- **Nova hipótese, do PM, apoiada em leitura de código**: a janela é `Qt.FramelessWindowHint |
  Qt.WindowStaysOnTopHint | Qt.Tool` com `WA_TranslucentBackground` — uma janela "layered" de
  verdade no Windows. A animação da terceira volta ainda chamava `setGeometry()` na janela
  **nativa** a cada quadro (~11 vezes em 160ms). Redimensionar repetidamente uma janela
  layered/translúcida sem moldura é fonte conhecida de flicker no Windows, e nada disso aparece em
  teste headless — mesma classe de achado que a largura não reproduzida (ambos só no Windows real).
  A hipótese de corrida com o vigia do ponteiro (100ms) foi **checada e refutada** por leitura de
  código antes desta rodada: `self._expandido` já troca antes da animação começar, então não há
  novo disparo de `_aplicar_modo` no meio da transição.
- **Mudança feita**: a janela nativa agora só muda de tamanho **2 vezes por transição** (antes: 12)
  — uma vez no início, para o retângulo-união dos dois extremos (`_geo_transicao`), e uma vez no
  fim, para o tamanho final exato. Durante os 160ms, cartão e botão continuam interpolados como
  antes, só que dentro dessa janela já fixa (a área extra é transparente, logo invisível).
  Redimensionamentos nativos medidos: **1x** em cada sentido. Desvio do botão: **0px**, círculo
  inteiro nos dois sentidos e nos três cantos — a suíte (`desktop/testes_janela_compacta.py`,
  estendida com um teste novo) prova as duas coisas; 76 verificações, 0 falhas.
- **Efeito colateral pequeno e aceito por ora**: durante os 160ms a janela nativa ocupa o
  retângulo-união (maior que o compacto) e a área transparente fora do cartão não é clicável-através
  — um clique ali durante a transição vira arrasto. Já existia um comportamento parecido na janela
  expandida (16px de borda transparente clicável); se incomodar, o conserto (`setMask()` ou
  `WA_TransparentForMouseEvents`) é decisão de produto, não bug.
- **Honestidade explícita, registrada no `PROGRESSO.md`**: esta volta não prova que o tremor ou a
  largura sumiram — elimina uma causa plausível para os dois, comum ao fato de nenhuma rodada ter
  conseguido reproduzir nenhum dos dois sintomas fora do Windows real. O `app.log` com a linha
  `compacto alvo=... real=...` continua sendo a prova que falta, ainda não lida pelo PM.

**Quinta rodada entregue em 2026-09-05 (mesmo dia) — sintoma mais preciso, causa mais provável, sem confirmação:**

- **Usuário testou a 4ª volta**: tremor "melhorou, mas não sumiu"; sintoma mais preciso — o botão
  fica **invisível por um instante** especificamente no início/fim da transição (hover entrando ou
  saindo), não no meio (já corrigido).
- **Causa achada por leitura de código, não suposição**: em `_aplicar_modo`, `_configurar_layout_do_modo`
  (muda margens/estilo do cartão) e um `widget.setVisible(expandido)` sobre o conteúdo só-expandido
  rodavam **antes** de os dois layouts serem desabilitados e antes de a janela nativa crescer para a
  união (mudança da 4ª volta) — ou seja, ao vivo, com o layout ainda no comando, na janela ainda do
  tamanho antigo. Medido: `_configurar_layout_do_modo` rodava com layout ligado em 2 de 2 transições;
  corrigido para 0 de 2.
- **Ajuste em relação ao pedido original, por medição**: apagar o `setVisible(expandido)` sem mais
  quebraria a âncora — o layout só conta widget visível, e o centro do botão na janela expandida
  muda 163px conforme o conteúdo esteja visível ou escondido. A garantia foi para dentro de
  `_centro_local_do_botao`, que agora aplica a visibilidade certa só durante a própria medição e
  devolve a de antes. O redimensionamento nativo para a união também não pôde vir antes de
  `_configurar_layout_do_modo`: a união depende de `geo_final`, que depende das margens e da folha
  de estilo já aplicadas (1px de diferença por causa da borda do QSS) — adiantar exigiria um
  redimensionamento nativo a mais, o que a 4ª volta eliminou.
- **Honestidade explícita, medida**: a checagem "nenhum widget visível durante a transição" passa
  também no código da 4ª volta — o show antigo era desfeito na mesma chamada, sem voltar ao laço de
  eventos, e nenhum teste headless a 4ms o enxerga. O que ficou provado é que a ordem mudou (layout
  não é mais mexido ao vivo antes de estar seguro); se o flash relatado vinha disso, deve sumir; se
  vinha de outra causa, não. Suíte: 91 verificações, 0 falhas (76 antes + 15 novas); 0px de desvio e
  1 redimensionamento nativo por sentido mantidos (sem regressão da 4ª volta).

**Correção de processo, mesmo dia**: o PM pediu 3 vezes que o usuário colasse trechos do
`app.log`, quando já tinha acesso direto ao arquivo pela ponte com a máquina do usuário — o usuário
corrigiu isto diretamente ("quem vai fazer isso é você"). PM leu o arquivo e achou, na sessão de
teste mais recente (a da 4ª volta): **20 ocorrências seguidas de
`compacto alvo=88x88 real=88x88 moldura=88x88 dpr=1.0`** — alvo, real e moldura idênticos, sem
escala aplicada. **Isto refuta, com dado real, as duas hipóteses de causa da largura levantadas nas
rodadas 3 e 4** (mínimo de largura do Windows / `SM_CXMINTRACK`; discrepância de escala DPI
88↔110): o próprio Qt relata ter alcançado exatamente o tamanho pedido. Se o usuário ainda vê o
compacto como errado, não é nenhuma das duas causas técnicas já descartadas — resta perguntar o que
exatamente ele está vendo (parece maior que 88px na prática, é sobre o expandido, é aparência e não
tamanho). Achado incidental de uma medição antiga (13:09, rodada anterior): uma linha
`tamanho_fora_do_modo expandido=True alvo=672x480 real=141x110` prova que a rede de segurança
(`_corrigir_tamanho_do_modo`, 2ª volta) já pegou um caso real de janela presa no tamanho errado.

**Ainda pendente de confirmação real**: se o "invisível por um instante" sumiu; o que exatamente o
usuário via quando disse "tamanho ainda péssimo", já que os números do `app.log` não sustentam
nenhuma das hipóteses técnicas registradas até aqui; suavidade percebida, hover/arrasto reais,
translucidez, microfone, núcleo.

**Achado sem ação, para decisão do PM**: perto do canto onde a janela nasce, o centro do botão
percorre 252–359px durante a animação (a janela cheia não cabe à esquerda do ponto de abertura) —
é geometria do ponto de partida, não bug; mexer nisso tocaria a correção de posição inicial de uma
entrada anterior, e o Executor preferiu não mexer sem pedido explícito.

**Sexta rodada, mesmo dia — escopo novo (não é mais bug do compacto):** o PM tirou print da tela
real do usuário (com permissão, controle remoto) e **confirmou visualmente que o modo compacto está
correto** — só o círculo do botão, sem moldura, fundo transparente. O usuário esclareceu que sua
reclamação era sobre a janela **expandida** ("está com o mesmo tamanho de quando eu não tinha pedido
para mexer nisso ainda"), pedindo para reduzir "o box de copiar" (a caixa de transcrição,
`caixa_texto`) a um terço do total, para a janela expandida ficar "um retângulo bem menor". Medido
antes de mudar: dos 480px de altura de hoje, `caixa_texto` já ocupava **171px (35,6%)** — já estava
perto de 1/3; quem domina a altura é o que é **fixo** (309px, 64%: margens, espaçamentos, a linha do
botão de gravar, o cronômetro, a barra de amplitude, a linha de copiar/lixeira). Implementado ao pé
da letra (`caixa_texto` → 160px, `_tamanho_expandido` → 672×469, largura mantida, `SPEC-002` I):
a janela só encolheu **11px (2,3%)** — **é provável que o usuário não perceba diferença**. Compacto
confirmado intocado (88×88, testado). Suíte: 107 verificações, 0 falhas (91+16).

**Decisão pendente, para antes de uma 7ª rodada**: se o objetivo é uma janela expandida
visivelmente menor, a "caixa de copiar" não é o lugar — é preciso mexer nos elementos fixos, hoje
fora do escopo autorizado. Candidatos já medidos pelo Executor: espaçamento 16→8 (−32px), margem do
cartão 24→16 (−16px), margem externa 16→8 (−16px), barra de amplitude 40→24 (−16px), linha do topo
72→56 com botões 44→32 (−16px), cronômetro fundido na linha do topo (−35px). Tudo junto, com a caixa
em 160: **~354px** de altura (~26% menor que os 480 originais) — decisão de produto do usuário, não
falta de execução.

**Ainda pendente de confirmação real**: aparência da janela expandida menor (mesmo os 11px);
"invisível por um instante" do botão (5ª volta); o que exatamente o usuário via ao dizer "tamanho
ainda péssimo" do compacto (refutado por print, mas a causa do relato original nunca foi explicada);
suavidade percebida, hover/arrasto reais, translucidez, microfone, núcleo.

**Sétima rodada, mesmo dia — usuário rejeita o resultado da 6ª e dá ordem direta, sem mais perguntas:**
"Simplesmente você não conseguiu fazer nada nessa rodada. Você não diminuiu horizontalmente a
janela... Não consegue colocar a janela padrão num formato menor? Acabar com essa borda ao redor do
botão tão grande? E outra coisa, o botão continua piscando quando passa o hover. Bota uma transição
maior, ele não sumir, né? Porque ele tá tentando desaparecer também o botão vermelho." Quatro
ordens diretas, sem espaço para nova pergunta de esclarecimento:

1. **Reduzir a LARGURA da janela expandida** — revoga, para esta janela flutuante especificamente,
   o vínculo com `SPEC-002` item I ("largura útil da coluna principal: 40rem/640px"). Este vínculo
   nunca foi uma exigência de paridade visual com o resto do app — foi uma escolha de reaproveitar
   uma medida já existente; o usuário agora pede explicitamente que a janela flutuante seja mais
   estreita que o resto do app. `SPEC-002` item I continua valendo para as outras janelas (painel
   de configurações, consumo, etc.) — só a janela flutuante do botão (`D-15`/`D-32`) passa a ter
   largura própria, menor, documentada aqui e não naquela tabela compartilhada.
2. **Reduzir `MARGEM_JANELA_COMPACTA`** (hoje 8px por lado, compacto 88×88) — o usuário chama isso
   de "borda ao redor do botão tão grande".
3. **Aumentar `DURACAO_ANIMACAO_MODO_MS`** (hoje 160ms) — pedido explícito do usuário ("bota uma
   transição maior"), para a transição parecer mais suave e não como um sumiço abrupto.
4. **Piscar do botão vermelho ao gravar, ainda não resolvido pelas rodadas 4 e 5**: o PM leu
   `_definir_estado_botao` (linha ~3166) e confirmou uma causa plausível ainda não tratada:
   `self.botao_gravar.definir_estado(estado)` roda **antes** de `self._aplicar_modo(True)` — ou
   seja, ao iniciar uma gravação a partir do compacto, o botão fica vermelho e o temporizador
   independente de 30ms da `CamadaPulso` (`_timer_pulso`, linha 870) começa a disparar **no mesmo
   instante** em que a transição de modo (160ms, depois 240ms) começa — dois sistemas de animação
   com relógios próprios e não sincronizados, repintando a mesma região da tela ao mesmo tempo. É a
   explicação mais concreta encontrada por leitura de código para "o botão vermelho tentando
   desaparecer" durante a transição — ainda não confirmada no Windows real, mas nunca antes
   atacada (rodadas 4 e 5 mexeram em redimensionamento nativo e ordem de layout, não neste ponto
   específico).

PM despachou a 7ª rodada (subagente `opus`) com as quatro mudanças acima, mais a aplicação real
(ainda pendente desde a 6ª) dos cortes nos elementos fixos já medidos (espaçamento, margens, barra
de amplitude, linha do topo, cronômetro fundido) para a janela expandida ficar visivelmente menor
em altura também (~354px, ~26% menor que os 480 originais) — o usuário não teve chance de reagir a
essa opção antes de já rejeitar a 6ª rodada como um todo, mas seu pedido geral ("formato menor") a
cobre.

**Sétima rodada entregue, mesmo dia:** as quatro ordens do usuário foram implementadas e medidas,
não estimadas.
- **Largura própria da janela expandida**: `LARGURA_EXPANDIDA = 448` (era 672, `-224px`/`-33%`) —
  não segue mais `SPEC-002` item I (nota já registrada lá). Piso medido da linha do topo (três
  botões + cronômetro + espelho, margens e borda): 324px; 448 escolhido medindo caracteres por
  linha na caixa de transcrição com a fonte real (448 → ~46 caracteres, banda legível), bem abaixo
  dos 672 originais.
- **Altura**: os seis cortes de elementos fixos, medidos na 6ª rodada e só agora aplicados de
  verdade, deram `ALTURA_FIXA_EXPANDIDA = 186` (era 309) + `ALTURA_CAIXA_TEXTO = 160` (inalterado) =
  `ALTURA_EXPANDIDA = 346` (era 469 depois da 6ª, 480 original — **-28%** desde o início). Um dos
  seis cortes (linha do topo 72→56) não rendeu o esperado: `QHBoxLayout` fica na altura do maior
  filho, e o botão de gravar (72px) foi explicitamente preservado — a redução real veio dos outros
  cinco cortes.
- **Janela compacta**: `MARGEM_JANELA_COMPACTA = 4` (era 8) → 80×80 (era 88×88), testado sem
  regressão.
- **Transição**: `DURACAO_ANIMACAO_MODO_MS = 240` (era 160), a pedido direto do usuário.
- **Pisca-pisca do botão vermelho**: hipótese do PM confirmada como mecanismo plausível e corrigida
  no código — `CamadaPulso` agora pergunta à janela se há uma transição de modo em andamento
  (`esta_em_transicao_de_modo()`, incluindo o instante "prestes a começar" que `_definir_estado_botao`
  sinaliza antes de chamar `_aplicar_modo`) e adia o início do temporizador de 30ms até
  `_assentar_modo` liberar; cor/ícone do botão continuam mudando na hora. Testado (`[15]`): 0
  quadros com o temporizador ativo durante os 10 quadros amostrados da transição. **Não é
  confirmação real** — só o Windows real confirma que o "botão vermelho tentando desaparecer"
  sumiu.
- Suíte: **143 verificações, 0 falhas** (107→143, +36), reconferido pelo PM de forma independente.
  Invariantes das rodadas 3-5 intactos (0px de desvio do botão, 1 redimensionamento nativo por
  direção, 0 widgets só-expandido visíveis durante a transição). Menu ⋮, Sair, configurações,
  consumo, geração de imagem, copiar/recortar/lixeira: conferidos, nenhum quebrado; painel de
  configurações (384×244) cabe dentro da nova janela de 448×346 sem cortar.
- Arquivo temporário da 6ª rodada (`desktop/_medicao/medir.py`) **apagado** (permissão de exclusão
  concedida desta vez). Nada de temporário ficou no repositório.

**Ainda pendente de confirmação real**: aparência e sensação da janela expandida menor (448×346);
se o pisca-pisca do botão vermelho de fato sumiu; borda do compacto (80×80) e transição de 240ms
percebidas como corretas. Tudo isso só o usuário confirma testando no Windows.

**Oitava rodada, mesmo dia — usuário testou a 7ª no Windows real, achou uma regressão:**
"você quebrou o layout e colcou o botao de cortar sobrepondo a caixa. a caixa ta num tamanho bom.
o botao pisca quando tira o mouse de cima, mas consertou o primeira piscada." Dois pontos:

1. **Regressão real, diagnosticada pelo PM por medição direta** (script headless instanciando
   `JanelaDitado`, sem alterar `app.py`): `ALTURA_EXPANDIDA = 346` (7ª rodada) esqueceu de somar os
   `2 * MARGEM_EXTERNA_EXPANDIDA` (16px) que ficam por fora do cartão — o cartão sozinho já precisa
   de 346px (`minimumSizeHint`), mas só recebe `346 - 16 = 330`. Como `layout_externo` usa
   `SetNoConstraint` (necessário para a animação), o Qt espreme o conteúdo em vez de recusar: a
   `caixa_texto` fica mais baixa que os 160px declarados e sobrepõe a `linha_acoes`
   (`botao_lixeira`/`botao_copiar`) — medido 7px de sobreposição. O tamanho da `caixa_texto` em si
   (160px) e a largura (`LARGURA_EXPANDIDA`, 448px) foram confirmados como bons pelo usuário — só a
   conta da altura total que esqueceu a margem externa.
2. **Pisca-pisca do botão vermelho ao começar a gravar melhorou** ("consertou o primeira
   piscada") — o fix da 7ª rodada (adiar o temporizador de pulso da `CamadaPulso`) parece ter
   funcionado. **Mas o flicker ao tirar o mouse de cima (hover-out, expandido→compacto) continua**
   — classe diferente, a mesma que as rodadas 4-5 atacaram (redimensionamento nativo de janela
   translúcida), ainda não eliminada de vez nesse sentido.

PM despachou a 8ª rodada: (1) corrigir a conta de `ALTURA_EXPANDIDA` incluindo a margem externa,
com um teste novo de sobreposição de geometria real (não só soma de números — é o tipo de teste
que teria pego este bug antes de chegar ao usuário); (2) tentativa adicional para o flicker de
encolhimento, envolvendo os `setGeometry` nativos existentes com `setUpdatesEnabled`/`repaint()`
síncrono, sem inventar nova hipótese de causa nem mudar a arquitetura de redimensionamento das
rodadas 4-5.

**Oitava rodada entregue, mesmo dia:** a regressão corrigida e medida (não estimada) — o PM
reconferiu de forma independente.
- **Altura corrigida**: `ALTURA_FIXA_EXPANDIDA` 186→202 (a conta certa desta vez inclui os
  `2×8=16px` de `MARGEM_EXTERNA_EXPANDIDA` que a 7ª rodada esqueceu) + nova constante
  `FOLGA_ALTURA_EXPANDIDA = 4` (margem de segurança contra variação de fonte entre máquinas) →
  `ALTURA_EXPANDIDA = 202 + 160 + 4 = 366` (era 346). Reconferido pelo PM: `caixa_texto` termina em
  y=300, a linha de ações (lixeira/copiar) começa em y=309 — 9px de vão, sem sobreposição.
  `caixa_texto` renderiza a 164px (o piso de 160 + os 4px de folga, absorvidos por ela por ser a
  única com fator de esticar). `ALTURA_CAIXA_TEXTO` (160) e `LARGURA_EXPANDIDA` (448) inalterados,
  como pedido. Redução real desde os 480px originais: ~24% (não os ~28% que a 7ª rodada tinha
  calculado sobre uma altura que na verdade não cabia o conteúdo).
- **Teste novo `[16]`**: mede a geometria real de todos os widgets do cartão (via `mapTo`) e checa
  ausência de sobreposição par a par, não só a soma de números — a classe de teste que teria
  pegado o bug da 7ª rodada antes de chegar ao usuário. Reconferido pelo PM instanciando a janela
  diretamente: sem sobreposição confirmada.
- **Tentativa adicional no flicker de encolhimento**: os dois `setGeometry` nativos existentes
  (união em `_aplicar_modo`, assentamento em `_assentar_modo`) agora rodam com
  `setUpdatesEnabled(False)` → reflow/`setFixedSize` → `setUpdatesEnabled(True)` → `repaint()`
  síncrono, para evitar o compositor do Windows capturar um quadro intermediário sem repintura
  completa. Arquitetura de redimensionamento das rodadas 4-5 intocada (1 redimensionamento nativo
  por sentido, 0px de desvio, 0 widgets indevidos visíveis — reconferido). **Não é confirmação
  real** — só o Windows real confirma se o flicker no hover-out sumiu.
- Suíte: **167 verificações, 0 falhas** (143→167, +24), reconferida pelo PM de forma independente.
  Achado incidental (não é bug de produto): um teste antigo deixava o cursor perto de onde a
  próxima janela nasce, e o vigia de ponteiro (100ms) podia expandir a janela antes da primeira
  medição — corrigido afastando o mouse no início de cada teste.
- Nenhum arquivo temporário deixado no repositório (`git status` conferido pelo PM).

**Ainda pendente de confirmação real**: se o flicker no hover-out (encolher) de fato sumiu ou
melhorou; aparência final da janela expandida (448×366) e compacta (80×80); tudo o que só o
Windows real confirma.

### D-34 — O MVP da Fase 2 é o app que já está em uso

`estado: fechada · 2026-09-06 · fase: F2`

**Ditar com um atalho e ter o texto pronto para colar, sem tirar a mão do teclado e sem piorar o que
eu já uso.** É a definição declarada de MVP da F2 (`L-C`), e ela não descreve trabalho futuro:
descreve o app de hoje.

Fica **fora** do MVP, declarado: a ação "colocar a última transcrição no campo em foco" (segue
parqueada), o histórico navegável (`D-22`/`B-11`), o seletor de idioma (`D-08`), o adiantamento de
exibição no streaming (`B-05`), e o que já estava morto (`D-33`).

**Por quê:** pergunta direta ao usuário em 2026-09-06 — *qual passo manual mais incomoda hoje, no
uso real?* — e a resposta foi **"nada, o fluxo já serve"**. A mesma conversa adiou o histórico. Uma
definição de MVP escrita contra o uso real vale mais que uma escrita contra a lista de desejos: o
que sobrar de incômodo aparece ditando, não planejando.

**Consequência para a fase:** não há funcionalidade entre o app de hoje e o fim da F2. O critério de
conclusão — *usar o ditado deste app no dia a dia, no lugar do que usava* — fica sozinho, e a Etapa
4 (o resto do plano) só se escreve com dias de uso acumulados. Também fecha o `B-06` dentro da
`US-D02`.

**Reabre se:** o uso em regime revelar um atrito que o usuário não previu hoje — que é exatamente o
que a Etapa 4 espera colher.

### D-35 — "Abrir planejamento" entra no menu ⋮, fora do plano

`estado: fechada · 2026-09-25 · fase: F2`

O menu ⋮ do app de desktop ganha, como **primeiro item**, "Abrir planejamento": abre no navegador
padrão a página de Planejamento e Execução do Sistema de Organização
(`ARQUIVO-PESSOAL/02_PROJETOS/SISTEMA-DE-ORGANIZACAO`), cujo endereço é fixo (`URL_PLANEJAMENTO` em
`desktop/app.py`). Ícone próprio, `planejamento` (barras escalonadas, como uma linha do tempo).

**Por quê:** pedido direto do usuário em 2026-09-25 — o app já fica aberto o dia todo, e o plano
precisa estar a um clique. Mesmo caso da `D-31`: fora da paridade (`D-27`) e fora do MVP (`D-34`),
sem mudar o critério da fase.

**Verificação:** `desktop/testes_janela_compacta.py` [10] passa a exigir os seis itens na ordem e
que o primeiro abra exatamente `URL_PLANEJAMENTO` (sem abrir navegador no teste). 231 verificações,
0 falhas, rodadas headless.

### D-36 — O núcleo sai da máquina: centralizado no Supabase, com login (reabre D-05)

`estado: fechada · 2026-09-30 · fase: Núcleo centralizado`

O núcleo de transcrição passa a ser **remoto**, em Edge Functions no projeto Supabase
**RAG-COMPARTILHADO**, com banco Postgres (schema próprio) no lugar dos `.jsonl` e **login pelo
Supabase Auth** desde já. O app de desktop vira cliente do núcleo remoto. A **geração de imagem fica
no núcleo local**, mas o consumo dela é registrado no mesmo banco.

**Por quê:** motivo novo, trazido pelo usuário — não é a condição de reabertura escrita na `D-05`
(consumo fragmentado). O backend já foi replicado uma vez (interface web, depois desktop); o Android
e o relógio seriam a terceira e a quarta, ou exigiriam a chave da OpenAI dentro do aparelho. Com um
núcleo central, todo cliente novo é magro, lê o contrato e chama a API; a chave mora num lugar só.
É a `D-07` (compartilha-se comportamento, não código) pagando: o contrato medido vira a
especificação da reescrita.

**Trade-offs aceitos:** um salto de rede a mais e um serviço externo na ferramenta de todo dia (os
dois riscos que a `D-05` apontava); reescrita em TypeScript/Deno, porque Edge Functions não rodam
Python; limite de 150 s por requisição no plano gratuito (tira o `diarize` do núcleo remoto);
projeto dividido com outro uso (cota, segredos e usuários do Auth). Mitigação: `url_nucleo` de volta
para o local continua sendo saída de emergência. A medição local × remoto foi **dispensada pelo
usuário**. O login entra agora, e não com o Android, por escolha do usuário: deixar pronto.

**Reabre se:** o núcleo remoto falhar no uso diário a ponto de o usuário voltar para o local, ou o
plano gratuito (pausa por inatividade, limites) virar obstáculo real.
