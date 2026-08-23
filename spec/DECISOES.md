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
`estado: fechada · 2026-08-21 · fase: F7`

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
`estado: fechada · 2026-08-21 · fase: método`

Sem suíte automatizada enquanto o projeto for simples.

**Por quê:** montar suíte custa tempo e chamada de API, e o sistema ainda é pequeno demais para
pagar isso.
**Reabre se:** houver mais de um cliente consumindo o núcleo — aí verificação manual deixa de
cobrir.

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
`estado: fechada · 2026-08-21 · fase: método`

Quando o usuário pedir **diagnóstico geral**, a resposta é um painel visual publicado, montado a
partir dos arquivos deste diretório — nunca um texto longo no chat.

**Por quê:** o usuário lê o estado do projeto muito melhor em painel do que em prosa, e o painel é
o formato em que ele consegue aprovar ou recusar. Vale também como semente do próprio produto: um
assistente que mostra estado visualmente.
**Reabre se:** —

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
