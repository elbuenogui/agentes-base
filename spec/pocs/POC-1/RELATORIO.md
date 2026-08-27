---
artefato: Relatório da PoC-1 — por onde o texto entra no campo em foco no Windows
referente a: Etapa 1 do PLANO.md (Fase 2)
medido em: 2026-08-25
status: parcial — Parte A concluída; Parte B/C interrompidas por um achado que muda o próprio desenho do teste (ver "Achado principal")
---

# Relatório — PoC-1

## Resumo executivo

A Parte A **funcionou de ponta a ponta** e confirmou que o contrato do núcleo quase basta sozinho —
falta só a URL base. A Parte B parou no meio porque os primeiros testes de digitação real, feitos
através da automação deste chat, **falharam silenciosamente em todos os alvos tentados** — e a causa
raiz encontrada não é sobre qual mecanismo escolher, é sobre **quem está autorizado a digitar**. Esse
achado (seção "Achado principal") precisa ser resolvido antes de a matriz 4×3 poder ser preenchida de
verdade — testar mais células do jeito que foi tentado só repetiria o mesmo falso negativo.

---

## Parte A — o cliente mínimo, escrito só com o contrato

**Resultado: funcionou, lendo só `spec/contrato/NUCLEO.md`.** Não abri `transcritor/backend/main.py`
nem `transcritor/frontend/index.html` em nenhum momento desta parte.

Cliente em [`cliente_minimo.py`](cliente_minimo.py) (30 linhas). Rodado de verdade contra o backend:

- **Transcrição bem-sucedida**: áudio de teste sintetizado por voz (Windows TTS,
  [`audio-teste.wav`](audio-teste.wav)) enviado a `POST /transcrever`, resposta `200` com
  `transcricao` preenchida — texto reconhecível (`"This is a contract test for the transcription
  query, POCONE, parte A."`).
- **Erro tratado pelo `codigo`, não pelo texto**: forcei `modelo=modelo-invalido-teste`, recebi `422`
  com `{"codigo": "MODELO_INVALIDO", "detail": "..."}`, e o cliente ramifica pelo `codigo` — exatamente
  como o contrato documenta.

### Declaração sobre o contrato

**Faltou uma coisa: a URL base do núcleo não está em `NUCLEO.md`.** O documento descreve rotas
(`POST /transcrever`, `GET /consumo`), campos, respostas e erros em detalhe — mas nunca diz onde o
servidor escuta. Descobri por sondagem (`curl` contra `http://localhost:8000/consumo`, a porta padrão
do `uvicorn`), **sem abrir `main.py`**. Isso funcionou porque `8000` é a porta padrão e o backend já
estava rodando — um cliente novo em uma máquina diferente, ou se a porta um dia mudar, não teria como
adivinhar isso só pelo contrato. Recomendo adicionar ao `NUCLEO.md` a URL base (ou como descobri-la,
ex. variável de ambiente) antes de fechar a Fase 1 como "contrato suficiente".

Fora esse ponto, **o contrato bastou** — nenhuma outra dúvida durante a Parte A.

---

## Achado principal — por que a Parte B parou

### O que foi tentado

Alvo: **WhatsApp Web (Opera)**, depois **Bloco de Notas**. Mecanismos testados no WhatsApp: 1
(SendInput/`KEYEVENTF_UNICODE`) e 3 (clipboard). No Bloco de Notas: mecanismo 3.

Em todos os casos, o script confirmava **programaticamente** — não por suposição — que a janela-alvo
já estava em foco (`GetForegroundWindow()` batendo com o título esperado) antes de injetar qualquer
coisa. Mesmo assim, **nada apareceu em nenhuma das quatro tentativas**, sempre do mesmo jeito: sem
erro, sem exceção, campo continuou vazio.

### A causa raiz

Isolei o problema abrindo um Bloco de Notas só meu (processo próprio, não o do usuário) e pedindo ao
Windows para trazê-lo para frente via `SetForegroundWindow`. **A chamada retornou `False` — recusada
— e o foco continuou em outra janela.** Essa é uma proteção do próprio Windows contra roubo de foco
por processos em segundo plano (o mecanismo por trás de `LockSetForegroundWindow`): um processo só
tem crédito para assumir o foco, ou para ter certeza de que sua entrada sintética será entregue ao
alvo certo, se ele estiver associado a uma **entrada de usuário real e recente** (tecla ou clique
físico).

O processo que executa estes scripts — a ferramenta deste chat — nunca carrega esse crédito, porque
ele é acionado por mim (o agente), não por uma tecla que o usuário apertou. Mesmo nos testes em que a
janela-alvo **já estava em foco por uma ação real do usuário antes do script rodar**, o crédito de
"entrada recente" pertence à ação que trouxe aquela janela para frente, não ao processo que roda
depois — e parece não bastar para a entrada sintética (`SendInput`, colar via `Ctrl+V`) ser entregue
de forma confiável.

### Por que isso não invalida a PoC — mas muda como ela precisa ser feita

O app desktop final **não vai ter esse problema do jeito que ele apareceu aqui**: ele vai ser
acionado por um atalho de teclado global de verdade — e um atalho global, ao disparar, **conta como
entrada de usuário legítima** para o Windows, dando ao processo que o escuta o crédito que faltou
aqui. A arquitetura correta para testar isso de verdade é: registrar um hotkey global, e só disparar
a injeção de dentro do handler de `WM_HOTKEY` (ou equivalente) — nunca a partir de um processo
desacoplado de qualquer entrada real, como uma automação de chat ou um serviço em segundo plano sem
gatilho de teclado.

**Isso vira um requisito de arquitetura para a próxima etapa, não só um detalhe de teste**: qualquer
linguagem/framework escolhida em D-06 precisa iniciar a injeção estritamente de dentro do callback do
atalho global (ou evento de teclado/mouse real equivalente) — nunca de uma fila, timer ou serviço
desacoplado — ou vai esbarrar na mesma proteção do Windows em produção.

### O que ficou provado apesar da causa raiz (sinais parciais, não conclusivos)

- **Mecanismo 2 no WhatsApp Web (Opera)**: independente do problema de crédito de entrada (isso é
  leitura de estado, não injeção — não é bloqueado pela mesma proteção), o UI Automation não enxerga
  o campo de mensagem como elemento focado. `AutomationElement.FocusedElement` devolve um contêiner
  genérico (`ControlType.Group`, classe `SplitWebViewContainer`), sem `ValuePattern` nem `TextPattern`
  disponíveis. Isso é uma característica conhecida de navegadores baseados em Chromium — a árvore de
  acessibilidade completa só é ativada sob demanda (quando o Chromium detecta um leitor de tela ativo),
  então a árvore exposta ao UI Automation pode ficar rasa por padrão. Uma implementação real
  precisaria forçar essa ativação ou navegar a árvore por outro caminho — não é garantido que
  funcione.
- **Mecanismo 2 no Bloco de Notas**: ao localizar o controle certo por `TreeWalker`/`FindFirst` (não
  pelo atalho de `FocusedElement`), encontrei um `ControlType.Document` com **`ValuePattern`
  disponível** (`True`) e consegui ler seu conteúdo (vazio, batendo com o estado real da janela). Isso
  é sinal de que controles nativos do Win32 expõem `ValuePattern` de forma confiável — a chamada de
  `SetValue` em si não chegou a ser confirmada por causa de um erro de RPC transitório
  (`RPC_E_SERVERFAULT`) combinado com o foco tendo mudado de janela entre uma tentativa e a repetição.

---

## Parte C — medição da área de transferência

Feita nos dois testes de mecanismo 3 (WhatsApp e Bloco de Notas), com
[`mecanismo3_clipboard.ps1`](mecanismo3_clipboard.ps1):

- **Tempo de exposição**: o texto de teste ficou no clipboard por **~1,05s** em ambos os testes
  (medido do `SetText` até a restauração do conteúdo original, incluindo os ~300ms de espera antes do
  `Ctrl+V` e ~700ms depois). Esse tempo é meu, não do mecanismo em si — dá para encurtar bastante numa
  implementação real (o delay foi só para dar tempo do `Ctrl+V` ser processado antes de restaurar).
- **Confiabilidade da restauração**: o conteúdo original capturado nos dois testes era uma lista de
  arquivos (`FileDrop`, de algo copiado antes no Explorer) — não texto simples. O script salvou os
  caminhos via `Clipboard.GetFileDropList()` e restaurou via `SetFileDropList()` sem lançar erro, mas
  **não confirmei visualmente que os arquivos ainda colavam certo depois** — o teste de colagem em si
  não produziu resultado visível (ver achado principal), o que também impede confirmar a restauração
  de ponta a ponta com certeza total.
- **Histórico de área de transferência do Windows (Win+V)**: **desligado**. A chave de registro
  `HKCU:\Software\Microsoft\Clipboard` existe mas não tem o valor `EnableClipboardHistory` definido —
  o padrão do Windows quando o recurso nunca foi ativado manualmente nas Configurações é desligado.
- **Gerenciador de clipboard de terceiros**: nenhum processo conhecido rodando (`Ditto`, `CopyQ`,
  `ClipboardFusion`, `ClipX`, `ClipMate` — nenhum encontrado na lista de processos).

---

## Resposta pendente: o mecanismo escolhido exige TSF?

**Não dá para responder com confiança ainda** — nenhum mecanismo teve uma inserção de texto
confirmada de ponta a ponta nesta sessão, então não há "mecanismo escolhido" para avaliar. O que dá
para adiantar: nem `SendInput`/`KEYEVENTF_UNICODE` nem colar via clipboard dependem do Text Services
Framework por si só (TSF entra em cena para recursos como candidatos de IME ou correção de texto
assistida, não para inserção bruta de caracteres Unicode ou colagem) — mas essa resposta só fica
sólida depois que a matriz 4×3 for refeita com um gatilho de entrada real (ver "Achado principal").

---

## O que falta para fechar a Parte B/C

A matriz 4×3 continua com a maior parte das células em branco — não por falta de tempo, mas porque
testar mais combinações do jeito que foi feito até aqui só reproduziria o mesmo falso negativo.
Refazer exige um dos dois caminhos discutidos com o usuário nesta sessão: (a) um script que registra
um atalho de teclado global e só injeta a partir do handler desse atalho (herdando o crédito de
entrada real de quando o usuário aperta a tecla), ou (b) o próprio usuário rodando os scripts
diretamente (não através desta automação de chat), para que a ação de disparar o script já carregue
entrada real recente.

## Nada do `transcritor/` foi alterado nesta tarefa.
