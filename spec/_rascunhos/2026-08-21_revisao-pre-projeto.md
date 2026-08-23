# Revisão do pré-projeto — Assistente Multiplataforma

> Rascunho do PM, 2026-08-21. **Não é spec aprovada.** É o passo que a instrução manda fazer antes
> de qualquer tarefa: achar inconsistência, ambiguidade, história a consolidar, requisito implícito,
> PoC necessária e decisão pendente. Nada aqui tem ID definitivo — ID só nasce aprovado.
> Entradas: `Instrução para o Claude — PM e Arquiteto` + `Pré-Projeto` (ambos de 2026-08-21) e o
> código real em `transcritor/`.

---

## A. Inconsistências

### A1. A ordem das fases 4 e 5 se contradiz dentro do próprio documento
O roadmap da §3 diz **F4 = Smartwatch, F5 = GPT**. A prioridade da §19 diz **4 = GPT, 5 =
smartwatch** — e a instrução do PM (item 9) concorda com a §19. São duas ordens diferentes no
mesmo material.

Recomendação: seguir a §19 (GPT antes do Watch). O Watch é a fase mais cara — hardware novo, Wear
OS, comunicação, bateria — e o resultado da fase GPT muda o que o Watch precisa fazer: se o Watch
só empurra texto, o desenho é um; se precisa exibir resposta do assistente, é outro.

### A2. A numeração das fases 7, 8 e 9 não fecha
O roadmap da §3 tem 8 fases (F7 = contexto + ferramentas + ações, F8 = memória). O corpo tem 9
(§10 F7 contexto, §11 F8 ferramentas, §12 F9 memória). Recomendação: adotar a numeração do corpo e
corrigir o roadmap — contexto e ferramentas são coisas distintas e provavelmente entregas separadas.

### A3. A Fase 1 já está metade pronta e metade impossível como está escrita
Critério de conclusão da F1: "a transcrição deve funcionar de maneira independente da interface
gráfica".

- **Caminho de arquivo: já atende.** `POST /transcrever` (`backend/main.py:221`) recebe áudio e
  devolve texto; `GET /consumo` já dá custo. Qualquer cliente consome isso hoje.
- **Caminho de tempo real: não atende, e não é um detalhe.** O backend só emite token efêmero
  (`GET /tempo-real/token`, `main.py:288`); quem abre o WebSocket com a OpenAI e gerencia a sessão
  é o navegador. Essa lógica mora nas **2.748 linhas** do `frontend/index.html`. Um cliente desktop
  nativo, o Android e o Watch teriam de reimplementá-la cada um.

Ou seja: a Fase 1 não é "consolidar o que existe". A pergunta real da Fase 1 é **o tempo real vira
capacidade do núcleo ou continua sendo responsabilidade de cada cliente?** É a decisão de
arquitetura mais cara do projeto, porque o erro se paga três vezes (desktop, Android, Watch).

### A4. Clicar no botão flutuante briga com inserir no campo em foco
US-D01 diz "clicar no botão para gravar". US-D02 diz "inserir no campo de texto em que estou
trabalhando". Clicar numa janela **tira o foco do campo de destino** — no instante do clique, o
campo ativo do sistema passa a ser o do assistente.

Isso tem solução (janela não-ativável, memorizar o último campo focado, ou acionar por atalho de
teclado), mas o pré-projeto **não menciona atalho de teclado em lugar nenhum** — e para uma
ferramenta de ditado de uso diário isso é provavelmente o acionamento principal, não o secundário.
Requisito implícito, não decidido.

### A5. Hover não existe no Android
Duas interações centrais do desktop dependem de passar o mouse: ver a última transcrição e fazer
aparecer os três pontos. A Fase 3 manda "reproduzir primeiro a experiência do desktop" — mas em
toque não há hover. A reutilização prometida na §2.2 vale para o **núcleo de capacidades**, não
para a interação; o documento trata as duas como a mesma coisa.

---

## B. Ambiguidades (falta definição objetiva)

| # | Ponto | Por que trava |
|---|---|---|
| B1 | "suportar os idiomas relevantes" (§4) | quais? afeta escolha de modelo e custo |
| B2 | "permitir avaliação de latência e de custo" (§4) | RNF sem número não é critério de aceitação. Qual o teto de latência do acionamento ao texto? Qual custo/mês tolerável? |
| B3 | "resultado mais recente" no hover (§5.3) | só o último, ou histórico de N? |
| B4 | plataforma do desktop | "Windows" só aparece de passagem na §2.4. É só Windows? Qual versão? |
| B5 | qual smartwatch | Wear OS é citado; modelo não. E o aparelho já está em mãos? Sem ele a F4 não existe |
| B6 | "copiar; apagar/desfazer" (§5.3) | apagar o resultado da lista e desfazer um texto já inserido no campo alheio são funcionalidades diferentes, com dificuldades diferentes |
| B7 | "caso a integração direta não seja suficiente" (§9) | falta o critério que decide "suficiente" — sem ele a F6 nunca começa nem nunca é descartada |

---

## C. Histórias a consolidar

**US-D02 (inserir no campo, desktop) e US-A02 (usar em apps externos, Android) são a mesma
capacidade em plataformas diferentes.** Proposta: uma capacidade única — *entrega do texto no
destino* — com uma escada de fallback comum:

```
1. inserir no campo em foco   (ideal, depende da plataforma)
2. colar via área de transferência  (quase sempre possível)
3. mostrar no popup para o usuário copiar  (sempre possível)
```

Consequências:

- **US-D03 deixa de ser história independente** — vira o degrau 3 dessa escada.
- Cada plataforma implementa a mesma escada com mecanismos próprios; o comportamento observável e
  os critérios de aceitação são compartilhados.
- **US-D05 (arquivo de áudio) já existe no código** (`POST /transcrever` aceita upload). É spec
  retroativa, não desenvolvimento novo.
- **US-G01 (GPT como destino)** é caso particular dessa escada **até** o ponto em que passa a
  exigir resposta de volta — aí vira outra capacidade e merece história própria.

---

## D. Requisitos implícitos (estão pressupostos, não escritos)

- **D1 — Onde roda o núcleo e onde mora a chave da API.** Hoje: backend local, chave no servidor,
  cliente pede token efêmero. Android e Watch **não podem** depender de um servidor rodando no PC
  do usuário. Ou existe um backend hospedado, ou cada cliente carrega a chave (com o risco que
  isso traz). Trava as fases 3 e 4, e é melhor decidir na 1.
- **D2 — Comportamento de erro.** Sem internet, API fora do ar, áudio longo demais, silêncio,
  permissão de microfone negada. Nenhuma história cobre.
- **D3 — Sinal de gravação.** Um app que fica com acesso ao microfone precisa de indicação
  inequívoca de quando está gravando. Aparece só como "identificar visualmente" dentro da US-D01.
- **D4 — Atalho global de teclado** (ver A4).
- **D5 — Persistência.** O backend hoje grava `transcricoes.jsonl` e `consumo.jsonl`. Isso é
  requisito do produto ou efeito colateral do MVP? Vira questão de privacidade quando o app for de
  uso diário.
- **D6 — Iniciar com o sistema.** "Botão persistente sempre disponível" pressupõe isso.

---

## E. PoCs necessárias antes de virar spec

| ID | Fase | Pergunta | Se falhar |
|---|---|---|---|
| POC-1 | 2 (bloqueante) | Dá para inserir texto no campo em foco no Windows, em navegador, e-mail, editor e mensageiro, sem perder o foco? | MVP desktop cai para clipboard + popup — muda a promessa do produto |
| POC-2 | 2 | Janela flutuante sempre no topo e **não-ativável** no Windows | acionamento passa a ser só por atalho |
| POC-3 | 3 (bloqueante) | Overlay + serviço de acessibilidade no Android do S22 inserindo texto em app de terceiro | Android vira "compartilhar/colar", não "ditado universal" |
| POC-4 | 3/5 | O que o app do ChatGPT no Android aceita: intent de compartilhar? teclado? nada? | integração com GPT muda de destino |
| POC-5 | 4 | Wear OS: gravar, enviar (Bluetooth ao telefone ou Wi-Fi ao backend), latência e bateria | Watch vira acionador remoto, não captador |
| POC-6 | 1 | O tempo real funciona fora do navegador? (WebSocket + token efêmero a partir de cliente nativo) | tempo real fica exclusivo da web, ou vira serviço do núcleo |

Risco de calendário à parte, não técnico: serviço de acessibilidade no Android tem política
própria de publicação na Play Store. Se em algum momento a distribuição sair do "instalo no meu
aparelho", isso volta como restrição.

---

## F. Decisões pendentes do usuário

1. Ordem das fases 4 e 5 (A1).
2. Onde roda o núcleo e onde mora a chave (D1) — decisão de arquitetura, não de gosto.
3. Desktop é só Windows? (B4)
4. Qual smartwatch, e já está em mãos? (B5)
5. Idiomas, teto de latência, teto de custo (B1, B2).
6. A tarefa de **interface enxuta**, pronta e não executada em `PROXIMA_TAREFA.md`, ainda vale?
   Se a Fase 2 cria um cliente desktop nativo, polir o `index.html` pode ser trabalho descartável.
   Contra-argumento: a §4 do pré-projeto diz explicitamente que a interface HTML continua sendo o
   cliente de teste do núcleo. Recomendação do PM: **executar** — é pequena e o cliente de teste é
   declarado — mas sabendo que não é investimento no produto final.

---

## G. Como o plano se organiza (regra do "teoriza uma, faz uma")

Dois níveis, e só dois:

- **Mapa de fases** — uma página, as 9 fases, cada uma com objetivo, entregável, critério de
  conclusão, PoCs conhecidas e dependências. É contrato de direção, não de comportamento. Não
  detalha nada.
- **Fase corrente** — uma por vez: lista de entregáveis → US → SPEC → PoC → TASK → TEST.

Regras que impedem a teorização de se descolar do concreto:

- **Não se escreve spec de fase futura.** Fase futura tem uma linha no mapa e nada mais.
- Antes de especificar a fase N, escrever primeiro a **lista de entregáveis da fase** ("são estas
  4 entregas, nesta ordem") e só então especificar a primeira delas.
- Uma fase só é declarada encerrada com o entregável **em uso**, não com o documento pronto.

### Por onde começar

Recomendação: **Fase 1 curta**, escopo "fechar o contrato do núcleo", três entregas:

1. documentar a API atual como contrato (é o que os três clientes vão consumir);
2. decidir onde roda o núcleo e onde mora a chave (D1);
3. POC-6 — tempo real fora do navegador.

Sem isso a Fase 2 começa cega, e o custo do erro se paga três vezes.

---

# Resoluções (conversa com o usuário, 2026-08-21)

## A4 — RESOLVIDA: dá para inserir no campo em foco, e o Windows mostra como

O usuário apontou que o próprio Windows faz isso como recurso de acessibilidade. Correto — a
digitação por voz do Windows (Win+H) e o Voice Access inserem texto no campo em foco de aplicativos
de terceiros. A objeção original não era "é impossível"; era "clicar num botão tira o foco". E a
prova de existência **confirma a solução em vez de derrubar a objeção**:

- A Microsoft aciona por **atalho de teclado**, não por clique. A instrução oficial é literalmente
  *"put your cursor in a text box"* e então pressionar Win+H — o campo é escolhido **antes**, e o
  acionamento nunca pede um clique.

**Decisões que decorrem disso:**

1. **O acionamento principal do desktop é atalho de teclado.** O botão flutuante continua existindo
   (é o que dá presença e mostra a última transcrição), mas um app cujo único gatilho é o clique
   sempre terá o problema de foco. Isso preenche o requisito implícito D4, que não estava no
   pré-projeto.
2. **POC-1 muda de pergunta.** Não é mais "dá para inserir?" — está respondido que dá. É
   **"por qual mecanismo, e onde ele falha?"**

### O que a POC-1 tem de responder agora

Três mecanismos possíveis no Windows, com limites diferentes:

| Mecanismo | Limite conhecido |
|---|---|
| **UIA `TextPattern`** | **não serve** — a documentação da Microsoft diz explicitamente que "the TextPattern classes do not provide a means to insert or modify text". É read-only, feito para leitor de tela |
| **UIA `ValuePattern`** | funciona só em parte dos controles e normalmente **substitui o valor inteiro** — inaceitável para inserir no meio de um e-mail já escrito |
| **Teclado sintético (SendInput)** | quase universal, mas lento para texto longo e sensível a layout de teclado e IME |
| **Text Services Framework (TSF)** | é o que a própria Microsoft recomenda para entrada de texto, e quase certamente o que o Win+H usa. Mais trabalho, melhor resultado |

A PoC não é um experimento único: é uma **matriz de compatibilidade** por aplicativo-alvo. Os
casos que costumam quebrar mecanismos diferentes: apps Electron (Slack, VS Code, Discord),
terminais, apps Java, jogos e sessões de área de trabalho remota.

A escada de fallback (campo em foco → clipboard → popup) **continua valendo** — mas deixa de ser
aposta sobre viabilidade e passa a ser escolha em tempo de execução, por aplicativo.

### Proposta de RNF (marcada como proposta, não requisito)

O Win+H existe, é gratuito e já está no sistema. Isso dá uma régua honesta para o produto:

> **O ditado do desktop precisa ser pelo menos tão rápido e tão preciso quanto o Win+H.**
> Abaixo disso, o app não tem razão de existir no desktop.

Se aceito, resolve a ambiguidade B2 (latência sem número) com um alvo mensurável em vez de um
palpite. O que justifica o produto acima dessa régua: escolha de modelo, histórico, custo visível,
mesma capacidade nas três plataformas e o caminho para assistente — nada disso o Win+H faz.

## A3 — RESOLVIDA: o núcleo é lote + streaming; o ao vivo fica congelado

### Correções ao diagnóstico original (erros meus, medidos depois)

1. **"A lógica do tempo real mora nas 2.748 linhas do `index.html`" está errado.** São ~400 linhas,
   entre 2407 e 2790, em funções delimitadas (`iniciarCapturaPcmTempoReal`,
   `iniciarGravacaoTempoReal`, `pararGravacaoTempoReal`, `limparRecursosTempoReal`…).
2. **São três caminhos, não dois** — eu tinha empacotado streaming junto com ao vivo:

   | Caminho | Como funciona | Reutilizável hoje |
   |---|---|---|
   | Lote | `POST /transcrever` → texto | sim |
   | **Streaming** | mesmo endpoint com `stream=true`, NDJSON com deltas | **sim — o backend faz tudo** |
   | Ao vivo | backend só emite token efêmero; cliente captura PCM e fala WebSocket com a OpenAI | não |

   O streaming já entrega "o texto aparece enquanto falo" sem WebSocket, sem PCM e sem token
   efêmero. Qualquer cliente ganha de graça.
3. **A POC-6 já tinha sido respondida.** `.claude/tmp/teste_tempo_real.py` validou o protocolo do
   ao vivo sem navegador (registrado na coleta de 2026-08-21). Não falta PoC; faltava eu ter lido.

### Decisão (usuário, 2026-08-21)

**Núcleo = lote + streaming. O modo ao vivo está congelado** — não se porta, não se reescreve, não
se apaga. Reafirmação da decisão de 2026-08-21 de tirá-lo de foco. Não reabrir sem motivo novo.

Decorrências: **POC-6 sai da Fase 1** (já respondida e sem consumidor). O harness vira tarefa de
arrumação da Fase 1, decidida pelo PM, sem consulta — preserva a evidência agora que o modo fica
parado.

## Arquitetura — decisões de 2026-08-21 (conversa PM ↔ usuário)

### Fechadas

- **O relógio é cliente magro, sempre.** Grava áudio e mostra texto; não processa nada. Decisão de
  produto do usuário. Motivo: processamento no pulso é bateria gasta fazendo pior o que o telefone
  faz melhor.
- **O telefone é o núcleo do relógio.** Confirmado que o Wear OS permite: a Wearable Data Layer
  (`MessageClient` + `WearableListenerService`) entrega mensagens do relógio ao app do telefone e
  **o inicia se ele não estiver rodando** — funciona com o telefone no bolso. Ressalvas anotadas
  para a PoC da Fase 4: a própria documentação avisa do custo de bateria de um
  `WearableListenerService`; a Data Layer não funciona se o relógio estiver pareado com iPhone
  (irrelevante aqui); e a gestão agressiva de bateria da Samsung é risco conhecido a testar no
  aparelho real.
- **Decorrência**: o relógio **nunca precisa da chave da API**. Mata um galho inteiro de
  complicação na Fase 4.
- **A linguagem do app desktop é decidida depois da POC-1**, não agora. Se a inserção de texto
  exigir Text Services Framework, empurra para .NET/C++; se `SendInput` bastar, quase qualquer
  linguagem serve. Escolher antes é escolher a ferramenta antes de saber o serviço.
- **O que se compartilha entre plataformas é o comportamento, não o código.** O núcleo são ~300
  linhas (chamar a API, ler resposta, calcular custo, registrar); a parte cara é a integração com
  cada sistema operacional, que não se compartilha de jeito nenhum. Por isso o entregável da Fase 1
  é o **contrato**, e não uma biblioteca única.

### Servidor próprio: adiado, com critério de disparo

**O servidor é a fronteira entre "ditado" e "assistente".** As fases 1 a 5 não precisam de um:
desktop chama a API; telefone chama a API; relógio chama o telefone. A partir da Fase 7 (contexto)
e obrigatoriamente na Fase 9 (memória e contexto persistente entre aparelhos) ele deixa de ser
opcional — memória compartilhada entre dispositivos não existe sem um lugar comum.

**Gatilho declarado**: o servidor nasce quando o produto precisar de estado compartilhado entre
aparelhos. Antes disso, não.

Custo de adiar (aceito): registro de consumo fragmentado, um arquivo por aparelho, sem visão do
total; e a chave da API em cada aparelho (revogar = trocar em N lugares). Uso pessoal, risco do
próprio usuário.

Custo de antecipar (evitado): autenticação para um usuário só; um salto de rede a mais no caminho
do áudio, contra a régua do Win+H; e um serviço que, quando cai, leva junto a ferramenta que você
usa todo dia.
