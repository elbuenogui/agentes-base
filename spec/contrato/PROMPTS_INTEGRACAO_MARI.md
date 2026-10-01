---
artefato: Prompts de integração do serviço de transcrição — projeto do servidor da Mari
origem: PLANO 2026-09-30, Etapa 4 (escrita pelo PM, a pedido do usuário)
escrito_em: 2026-09-30
contrato: SERVICO_TRANSCRICAO.md (X-Servico-Contrato 1)
executor: Codex, no repositório da Mari
---

# Prompts de integração — Mari

> **Entregue em 2026-09-30, adaptado ao repositório da Mari** — a versão que vale para executar é a de
> lá, não esta. Depois de ler o repositório da Mari, o PM viu que (1) o PM/EXEC de lá roda no Codex e
> pede retomada, não prompt solto; (2) a API é FastAPI em `chatbot-api/`, com `urllib` e `session_id`;
> (3) o chat da Mari mora noutro repositório, o `urbverde-ui-novo`. Então:
> - prompt 1 (rota) virou a especificação do passo 1 de `Mari/_RETOMADA_transcricao-servico-codex.md`;
> - prompt 2 (gravação) virou `Mari/_PROMPT_urbverde-ui-gravacao-voz.md`, para o `urbverde-ui-novo`;
> - prompt 3 (verificação) virou o passo 4 da mesma retomada;
> - o contrato foi copiado para `Mari/chatbot-api/docs/CONTRATO_SERVICO_TRANSCRICAO.md`, com aviso de
>   cópia (a fonte continua sendo `spec/contrato/SERVICO_TRANSCRICAO.md`).
> Este arquivo fica como registro da Etapa 4.

Três prompts, um por tarefa, para colar no **Codex** dentro do repositório da Mari, **nesta ordem** e
um de cada vez: cada um depende do anterior pronto.

| # | tarefa | depende de |
|---|---|---|
| 1 | Rota do servidor que repassa o áudio ao serviço | contrato copiado e chave no ambiente |
| 2 | Gravação no navegador, que preenche a caixa de mensagem | prompt 1 |
| 3 | Verificação ponta a ponta com áudio real | prompts 1 e 2 (é a Etapa 5 do plano) |

Decisões do usuário que os prompts carregam (2026-09-30): a transcrição **preenche a caixa de
mensagem** para a pessoa revisar, nunca envia sozinha; o silêncio é descartado **no navegador**.

## Antes do prompt 1 (o usuário faz)

1. Copiar `spec/contrato/SERVICO_TRANSCRICAO.md` deste repositório para o repositório da Mari, em
   `docs/contratos/SERVICO_TRANSCRICAO.md`. Os prompts apontam para esse caminho. Os links dele para o
   `NUCLEO.md` ficam quebrados lá — o que importa deles já está nos prompts.
2. No ambiente do servidor da Mari (onde ficam as outras variáveis de ambiente dela), criar
   `SERVICO_TRANSCRICAO_CHAVE` com o valor de `SERVICO_CHAVE_MARI` que você guardou. **Não cole a
   chave no Codex.**

## Números que são proposta, não medição

O limite por pessoa e os limiares de silêncio abaixo são **ponto de partida escolhido pelo PM**, não
medidos: ficam em constantes configuráveis e se ajustam na Etapa 5, com uso real.

- Limite por pessoa: **10 transcrições a cada 10 minutos** por sessão (ou, sem sessão, por IP).
- Silêncio: descartar a gravação se o total de trechos com volume acima do limiar somar **menos de
  0,5 s**; limiar inicial de volume em torno de **−45 dBFS** (RMS), a calibrar.

---

## Prompt 1 — Rota do servidor

````text
Tarefa: criar no servidor da Mari uma rota que recebe um áudio gravado no navegador e devolve o texto
transcrito, usando o serviço de transcrição do RAG-COMPARTILHADO.

Leia antes: docs/contratos/SERVICO_TRANSCRICAO.md (o contrato do serviço, versão 1). Ele é a fonte
de verdade; se algo aqui parecer divergir dele, pare e pergunte.

Contexto:
- O serviço é uma Edge Function: POST https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1/transcrever-servico
  multipart/form-data com o arquivo no campo "audio" e a chave no cabeçalho "x-servico-chave".
  Sucesso: 200 {"transcricao": "..."}; erro: {"detail": "...", "codigo": "..."}. Toda resposta da
  própria função traz o cabeçalho X-Servico-Contrato: 1.
- A chave está na variável de ambiente SERVICO_TRANSCRICAO_CHAVE. Ela nunca pode chegar ao navegador.
- É um recurso de acessibilidade: quem não quer ou não consegue digitar grava a pergunta.

Primeiro, descubra a pilha do servidor da Mari (linguagem, framework, onde ficam as rotas, como as
variáveis de ambiente são lidas, como os testes rodam) e siga as convenções que já existem.

Faça:
1. Uma rota POST (por exemplo /api/transcrever, no padrão das rotas existentes) que recebe
   multipart/form-data com o arquivo no campo "audio", vindo do front da Mari.
2. Antes de repassar, confira no servidor: arquivo presente e não vazio; tamanho até 4 194 304
   bytes (4 MB); tipo de áudio (audio/*). Recuse o que falhar sem chamar o serviço.
3. Limite por pessoa: no máximo LIMITE_TRANSCRICOES (padrão 10) a cada JANELA_LIMITE_S (padrão 600 s)
   por sessão; sem sessão, por IP. Guarde só contadores em memória com expiração (nada em disco,
   nada identificável além do necessário para contar). Acima do limite, responda 429 com mensagem
   própria, sem chamar o serviço.
4. Repasse ao serviço com a chave de SERVICO_TRANSCRICAO_CHAVE no cabeçalho x-servico-chave e o
   arquivo no campo "audio", com nome de arquivo cuja extensão corresponda ao formato
   (gravacao.webm, gravacao.mp4, gravacao.wav...). URL em SERVICO_TRANSCRICAO_URL, com o endereço
   acima como padrão. Prazo do cliente: 150 s.
5. Devolva ao front um JSON simples: no sucesso {"texto": "..."}; no erro {"erro": "<mensagem para a
   pessoa, em português>", "pode_tentar_de_novo": true|false}. Mapeie pelo campo "codigo" do
   serviço, nunca pelo "detail":
   - CHAVE_INVALIDA, SEM_CHAVE, FALHA_AUTENTICACAO → "A transcrição está indisponível agora." (false);
     e registre um alerta no log do servidor: é problema de configuração.
   - AUDIO_VAZIO → "Não chegou áudio. Grave de novo." (true)
   - ARQUIVO_MUITO_GRANDE → "A gravação ficou longa demais; grave um trecho menor." (true)
   - LIMITE_DIARIO → "O limite diário de transcrição foi atingido; tente amanhã ou digite a pergunta." (false)
   - LIMITE_INDISPONIVEL, SEM_CONEXAO, API_RECUSOU, ERRO_INTERNO, TEMPO_ESGOTADO →
     "A transcrição está indisponível agora; tente em alguns minutos." (true)
   - REQUISICAO_INVALIDA, METODO_NAO_PERMITIDO → erro de programação: log de erro, e à pessoa
     "A transcrição está indisponível agora." (false)
   - resposta SEM o cabeçalho X-Servico-Contrato (veio da plataforma, não da função): tratar como
     indisponível (true), sem ler "codigo".
   - X-Servico-Contrato diferente de "1": registrar aviso no log (o contrato mudou) e seguir pelo status.
6. Não repita a chamada automaticamente, em nenhum caso: quem decide tentar de novo é a pessoa. Repetir
   um TEMPO_ESGOTADO pode cobrar duas vezes.
7. Log do servidor: só status, codigo, tamanho do áudio em bytes, formato e latência. Nunca o texto
   transcrito, o áudio, a chave, nem dado da pessoa.
8. O áudio fica só em memória durante a requisição: nada em disco, nada em banco, nada em cache. O
   texto só volta ao front; não é guardado no servidor.
9. Documente as variáveis novas (SERVICO_TRANSCRICAO_CHAVE, SERVICO_TRANSCRICAO_URL,
   LIMITE_TRANSCRICOES, JANELA_LIMITE_S) no lugar onde o projeto já documenta as outras (por exemplo
   .env.example), sem valor para a chave.
10. Testes automatizados com o serviço simulado (nunca o real): sucesso; cada grupo de codigo acima;
    resposta sem X-Servico-Contrato; arquivo vazio, acima de 4 MB e não-áudio recusados sem chamar o
    serviço; limite por pessoa; e um teste que garante que a chave não aparece em nenhuma resposta
    nem em nenhum log.

Não faça:
- Não chame o serviço de transcrição a partir do navegador, e não mande a chave ao front de forma
  nenhuma (nem em HTML, nem em variável de build do front).
- Não grave o áudio nem o texto transcrito em disco, banco, log ou analytics.
- Não envie a transcrição como pergunta à Mari: esta rota só devolve o texto.
- Não escolha modelo, streaming ou projeto: o serviço ignora esses campos.
- Não altere outras funcionalidades da Mari além do necessário para registrar a rota.
- Não commite sem autorização.

Pronto quando: a rota existe, os testes passam, e uma chamada manual (curl) à rota do servidor, com um
arquivo de áudio curto de fala, devolve {"texto": ...}. Essa chamada manual custa centavos e só a
pessoa responsável roda.

Ao terminar, responda com: arquivos criados ou alterados; o caminho da rota; como rodar os testes e o
resultado; as variáveis de ambiente novas; e qualquer ponto em que o código da Mari impediu seguir o
contrato.
````

---

## Prompt 2 — Gravação no navegador

````text
Tarefa: no front da Mari, deixar a pessoa gravar a pergunta por voz. A gravação vai para a rota de
transcrição do servidor da Mari (feita na tarefa anterior) e o texto aparece na caixa de mensagem
para a pessoa revisar e enviar. É um recurso de acessibilidade.

Leia antes: docs/contratos/SERVICO_TRANSCRICAO.md, seções 5 (limites) e 9 (obrigações do cliente),
e a rota de transcrição criada no servidor da Mari (o que ela recebe e devolve).

Contexto:
- O front da Mari mora junto com o front do mapa da plataforma; siga os componentes, estilos e o
  padrão de estado que já existem ali.
- A rota do servidor devolve {"texto": "..."} no sucesso, ou {"erro": "...", "pode_tentar_de_novo":
  true|false}.
- Áudio sem fala NÃO volta vazio: o serviço devolve texto inventado (alucinação), e ainda cobra. Por
  isso o silêncio precisa ser descartado aqui, antes de enviar.

Faça:
1. Um botão de microfone junto da caixa de mensagem da Mari. Um toque começa a gravar; outro toque
   para. Durante a gravação, mostre que está gravando e o tempo restante.
2. Grave com MediaRecorder. Formato: o primeiro suportado entre audio/webm;codecs=opus, audio/webm,
   audio/mp4, audio/ogg;codecs=opus (confira com MediaRecorder.isTypeSupported). O nome do arquivo
   enviado tem a extensão do formato real (gravacao.webm, gravacao.mp4, gravacao.ogg).
3. Pare a gravação sozinho em 2 minutos (constante DURACAO_MAXIMA_S = 120), avisando a pessoa.
4. Descarte de silêncio, no navegador: durante a gravação, meça o volume com a Web Audio API
   (AnalyserNode, RMS por quadro). Some o tempo dos quadros acima de LIMIAR_FALA_DBFS (padrão −45).
   Se, ao parar, a soma for menor que FALA_MINIMA_S (padrão 0,5), NÃO envie: mostre "Não ouvi nada.
   Tente gravar de novo." Deixe as três constantes num lugar só, fáceis de ajustar.
5. Antes de enviar, confira o tamanho: acima de 4 194 304 bytes, não envie ("A gravação ficou longa
   demais; grave um trecho menor.").
6. Envie para a rota do servidor da Mari em multipart/form-data, campo "audio". Mostre
   "Transcrevendo..." e impeça outra gravação enquanto isso.
7. No sucesso, ponha o texto na caixa de mensagem (se já houver texto lá, acrescente depois dele, com
   um espaço), coloque o foco na caixa com o cursor no fim, e NÃO envie. A pessoa revisa e envia pelo
   caminho que já existe.
8. No erro, mostre a mensagem que veio em "erro"; se pode_tentar_de_novo for true, ofereça "tentar de
   novo" (que regrava; o áudio anterior já foi descartado).
9. Acessibilidade: o botão tem rótulo acessível que muda entre "Gravar pergunta por voz" e "Parar
   gravação" (e aria-pressed), funciona pelo teclado, e os estados (gravando, transcrevendo, texto
   pronto, erro) são anunciados numa região aria-live. Microfone negado ou ausente: mensagem clara,
   e o resto da Mari segue funcionando.
10. Ao terminar cada tentativa, pare as trilhas do microfone (o indicador de microfone do navegador
    apaga) e descarte o áudio da memória.
11. Testes no padrão do front da Mari para a lógica que não depende de microfone real: escolha do
    formato e da extensão, regra de silêncio, limite de tamanho, inserção do texto na caixa sem
    enviar, tratamento de erro.

Não faça:
- Não chame o serviço do Supabase direto do navegador e não use chave nenhuma no front: o front só
  fala com o servidor da Mari.
- Não envie a transcrição sozinho como pergunta.
- Não guarde áudio nem texto em localStorage, IndexedDB, cookie, analytics ou log.
- Não envie áudio que a regra de silêncio descartou.
- Não mude o comportamento da caixa de mensagem para quem digita.
- Não commite sem autorização.

Pronto quando: numa execução local, gravar uma frase preenche a caixa com o texto sem enviar; gravar
silêncio não chama o servidor; a gravação para sozinha em 2 min; e os testes passam.

Ao terminar, responda com: arquivos criados ou alterados; o formato que o navegador de teste escolheu;
o que foi testado à mão e em quais navegadores; e qualquer ponto em que o front da Mari impediu seguir
estas regras.
````

---

## Prompt 3 — Verificação ponta a ponta (Etapa 5)

````text
Tarefa: verificar, com uma gravação real no navegador, que o caminho inteiro funciona no ambiente
onde a Mari roda (não em teste simulado), e relatar o resultado sem expor texto nem chave.

Leia antes: docs/contratos/SERVICO_TRANSCRICAO.md e as rotas/componentes das duas tarefas anteriores.

Faça, junto com a pessoa responsável (ela grava; você acompanha pelos logs do servidor):
1. Confirme que SERVICO_TRANSCRICAO_CHAVE está definida no ambiente do servidor, sem mostrar o valor
   (só "definida, N caracteres").
2. A pessoa grava uma frase curta pela Mari, no navegador. Confira no log do servidor: status 200,
   formato enviado, tamanho em bytes, latência. O texto aparece na caixa e não é enviado sozinho.
3. A pessoa grava alguns segundos de silêncio: confira que o servidor não recebeu chamada.
4. Anote a hora exata (com fuso) de cada chamada que chegou ao serviço.

Não faça:
- Não copie o texto transcrito para o relatório, o log ou o chat.
- Não mostre a chave nem parte dela.
- Não rode chamadas em laço nem testes de carga contra o serviço real: cada chamada custa.

Ao terminar, responda com, para cada chamada: hora com fuso, formato, bytes, status, codigo (se houve
erro) e latência. Diga também o navegador usado. Esse relatório vai para quem opera o serviço, que
confere o consumo no banco.
````
