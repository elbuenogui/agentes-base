# PROGRESSO — log de execução (append-only)

> Vivo desde a virada de plano de 2026-08-21 (plano de faxina e fechamento). As entradas dos
> planos anteriores foram movidas para `.claude/estado/historico/` (arquivos `PROGRESSO_*.md`),
> sem edição — o vivo guarda só o plano em andamento. O plano imediatamente anterior
> (usabilidade da interface de gravação, 2026-08-20 a 2026-08-21) está em
> `.claude/estado/historico/PROGRESSO_usabilidade-gravacao_2026-08-20_a_2026-08-21.md`.

## [2026-08-21] — Enxugar o histórico do método, Etapa 2
Status: concluído

### Feito
Só movimentação de arquivo (`mv`), nenhum conteúdo editado — o `.git/index.lock` já estava
presente (esperado, é o que bloqueia a Etapa 3 até o usuário apagar), então nada aqui passou por
`git` (nem `git mv`), só sistema de arquivos direto.

- Criei `.claude/estado/historico/snapshots/`.
- Descobri por `grep` (não de memória) todo `PLANO_2026-08-*.md` citado por nome fora de
  `historico/` — 8 além dos marcos já listados na tarefa, todos em `coleta/2026-08-16_mvp-transcricao.md`
  (citações de "snapshot arquivado em..." junto de decisões/artefatos, não citações dentro de
  outro snapshot): `PLANO_2026-08-18c.md`, `PLANO_2026-08-18f.md`, `PLANO_2026-08-19b.md`,
  `PLANO_2026-08-19c.md`, `PLANO_2026-08-19d.md`, `PLANO_2026-08-19e.md`, `PLANO_2026-08-19f.md`,
  `PLANO_2026-08-19g.md`. Ficaram na raiz de `historico/` junto dos marcos.
- Movi os outros 48 arquivos (a série de edição sem citação externa) para `snapshots/`.
- Movi `_RETOMADA_robustez-consumo.md` e `_RETOMADA_transcricao-tempo-real.md` da raiz do
  repositório para `.claude/estado/historico/` (raiz, não `snapshots/`).

### Contagens (pedidas explicitamente)
- `historico/` antes: **63 arquivos** (a tarefa estimava "60" — contei de verdade,
  `ls -1 | wc -l`, deu 63).
- `historico/` depois: raiz **17** (7 marcos + 8 citados pelo grep + as 2 retomadas que chegaram)
  + `snapshots/` **48** = **65** no total — bate com 63 (o que já havia) + 2 (retomadas que
  entraram), nada apagado.
- Raiz do repositório: `_RETOMADA_*.md` foi de 4 para 2 (`_RETOMADA_TEMPLATE.md` e
  `_RETOMADA_usabilidade-gravacao.md`, intocados).

### Verificação de referências (repositório inteiro, fora de `.git/` e `.venv/`)
Grep por todo padrão `historico/ARQUIVO.md` e `_RETOMADA_*.md` no repo (265 referências
encontradas) e conferido se o arquivo existe no caminho citado (raiz de `historico/` ou
`snapshots/`, ou raiz do repo para as retomadas vivas): **zero referências quebradas**. As duas
únicas ocorrências que o grep sinalizou como "não resolve" eram o padrão-modelo
`PLANO_AAAA-MM-DD.md` (data literal, não um arquivo real) em `.claude/PM.md` e
`.claude/estado/README.md` — documentação do formato de nome, não uma citação de arquivo.
Nenhuma referência precisou de correção.

Os dois `_RETOMADA_*.md` movidos se auto-citam como "(raiz)" no próprio texto (ex.: linha 81 de
`_RETOMADA_robustez-consumo.md`) — ficou desatualizado depois da mudança de lugar, mas não
mexi: é conteúdo de retomada arquivada, e a tarefa proíbe editar conteúdo de retomada.

### Critério de pronto
- [x] `historico/snapshots/` existe e contém os snapshots de edição (48)
- [x] Raiz de `historico/` com 17 arquivos (7 marcos + 8 citados pelo grep + 2 retomadas) — mais
      que os "~7" estimados na tarefa, porque o grep achou 8 citações reais que a estimativa não
      previa; contagem colada acima
- [x] Nenhum arquivo apagado — conta colada acima (63+2=65 = 17+48)
- [x] As duas retomadas de frentes encerradas saíram da raiz; `_RETOMADA_usabilidade-gravacao.md`
      e `_RETOMADA_TEMPLATE.md` continuam lá, intocados
- [x] Nenhuma referência quebrada — resultado colado acima (265 checadas, 0 quebradas)
- [x] Nenhum arquivo teve o conteúdo alterado — só `mv`, nenhuma correção de referência foi
      necessária

### Novas demandas / riscos
- Nenhum novo.

### Ajuste no plano necessário?
Não.

## [2026-08-21] — Commit do trabalho de 2026-08-20 e 2026-08-21, Etapa 3
Status: concluído

### Feito
- `.git/index.lock` estava presente (sobra de sessão via bridge remoto); confirmei que não havia
  processo `git` rodando (`Get-Process | Where-Object ProcessName -like '*git*'`, vazio) e apaguei.
- Conferi `.gitignore` antes de qualquer `git add` — ver prova abaixo.
- 4 commits, um por natureza, nenhum `git add .`/`-A` (sempre caminhos explícitos por grupo):
  código do produto, documentação do produto, estado do método + histórico, coleta.
- Nenhum `git push`.

### git status --short (depois dos 4 commits)
Vazio.

### Prova de que nada sensível/local entrou
`git check-ignore -v` nos 6 caminhos (`.env`, os dois `.jsonl`, `.venv/`, `__pycache__/`,
`.claude/tmp/`) — os 6 resolvem para regras do `.gitignore`. `git show --stat` dos 4 commits novos,
filtrado por esses mesmos padrões — nenhuma ocorrência em nenhum dos 4.

### git log --oneline (4 novos)
```
c3c2cdb Registra na coleta as decisoes do fechamento do tempo real e da usabilidade da gravacao
7c2e5ab Vira a pagina do metodo: fecha os planos de tempo real e usabilidade, reorganiza o historico
d0dc344 Atualiza o README do transcritor para o fechamento do tempo real e a nova gravacao rapida
5e901ad Fecha o modo tempo real e reformula a gravacao rapida da interface
```
(mensagens completas sem acentuação — escolha deliberada para evitar risco de mojibake permanente
no histórico do git neste ambiente Windows/Git Bash; conteúdo em português íntegro, só sem
diacríticos.)

### Critério de pronto
- [x] `.git/index.lock` não existe mais
- [x] `git status --short` vazio — colado acima
- [x] Nenhum dos 6 caminhos sensíveis/locais em nenhum commit — prova colada acima
- [x] Commits agrupados por natureza, mensagens em português explicando o quê e o porquê — log
      colado acima
- [x] Nenhum `git push` executado
- [x] Nenhum arquivo do repositório editado por esta tarefa (fora deste próprio registro em
      PROGRESSO.md, que por natureza é escrito depois do commit existir)

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não.

## [2026-08-21] — Interface enxuta — configurações, upload no menu e topo da página
Status: concluído

### Feito
- Removidos do topo: `<h1>`, `.subtitulo`, os três `.alternador-modelo`, `<form id="formulario">`
  e o separador "ou". `<section id="gravacao-rapida">` é agora o primeiro bloco do `<main>`. CSS
  órfão removido junto (`.alternador-modelo`, `.rotulo-modelo`, `.dica-modelo`, `.subtitulo`,
  `.separador`, `#botaoModelo/#botaoStreaming/#botaoTempoReal` como botão de texto, `#resultado.*`).
- Cabeçalho: `<h1>` continua no DOM, primeiro filho do `<main>`, com classe utilitária
  `.oculto-visualmente` (`position:absolute; width:1px; height:1px; overflow:hidden;
  clip-path:inset(50%)` — não `display:none`). `<title>` da aba intocado.
- Configurações passa a ter, nessa ordem: modelo (`<select id="seletorModelo">`, mesmo conteúdo de
  `MODELOS_ATIVOS`, diarize continua desativado e comentado), streaming
  (`<input type="checkbox" id="botaoStreaming">`) e tempo real
  (`<input type="checkbox" id="botaoTempoReal">`), depois o seletor de microfone que já existia.
  Sem texto de dica na tela; a explicação do tempo real (efeito no custo) foi para o
  `title`/`aria-label` do interruptor. `modeloAtivo()`, `streamingAtivo()` e `tempoRealAtivo()`
  mantidas com a mesma assinatura, só trocando de onde leem o valor (`.value`/`.checked`).
- Confirmado nos ~8 pontos que usam `botaoTempoReal.disabled`: todos ficam dentro de funções
  específicas do modo tempo real (nunca da gravação normal) — trocar de `<button>` para
  `<input type="checkbox">` manteve o `id` e não exigiu tocar em nenhum desses pontos, já que
  `.disabled` funciona igual nos dois tipos de elemento.
- Terceiro item do `#popupMenuAvancado`: "Enviar arquivo" (ícone + rótulo curto), aciona
  `.click()` num `<input type="file" id="inputUploadArquivo" hidden>` (mantendo `accept`) e fecha
  o menu. `input.value` é limpo depois de cada envio, então escolher o mesmo arquivo de novo
  dispara `change` normalmente.
- Upload unificado com a gravação: `enviarGravacaoRapida` ganhou um terceiro parâmetro opcional
  `nomeArquivo` — quando vem do upload, usa o nome real do arquivo (preserva extensão); quando vem
  da gravação, continua com `"gravacao." + extensaoParaMime(...)"` como sempre. `#resultado`, o
  `<form>` e o handler de submit foram removidos por completo; erro do upload usa o balão
  (`mostrarStatusGravacao`), igual à gravação. Spinner no botão central durante a transcrição do
  upload (mesmo estado "processando" da gravação — não há um terceiro indicador).
- Adição além do texto literal da tarefa, justificada: clicar no item "Enviar arquivo" durante uma
  gravação em andamento não abre o seletor (guarda silenciosa) — unificar os dois caminhos no mesmo
  botão/estado (`botaoGravacaoRapida`, `transcriptRapido`) criava uma corrida nova que não existia
  antes (upload disparando no meio de uma gravação/processamento); bloqueei porque o resto da tarefa
  depende de que só um envio esteja em voo por vez.
- `transcritor/README.md`: reescritas as seções que descreviam os três alternadores no topo, o
  formulário de upload com botão "Transcrever" e a área `#resultado` — agora refletem Configurações
  (modelo/streaming/tempo real/microfone) e o item "Enviar arquivo" do menu ⋮, com a mesma caixa
  "Transcrição por voz" para os dois fluxos.
- Verificado por `grep`: zero referências a `formulario`, `resultado`, `mostrar(`, `botaoModelo`,
  `indiceModeloAtivo`, `streamingLigado`, `tempoRealLigado`, `atualizarBotaoModelo`,
  `atualizarBotaoStreaming`, `atualizarBotaoTempoReal`; zero CSS/HTML órfão dos blocos removidos;
  zero `id` duplicado no arquivo. `node -e "new Function(...)"` confirma o JS sem erro de sintaxe.

### Como testei os dois caminhos de envio (upload e gravação) — e o que não testei
Quatro scripts Playwright (Chromium headless, microfone simulado via
`--use-file-for-fake-audio-capture` com `.wav` reais), cobrindo os dois caminhos lado a lado:

1. **Estrutura** (sem custo): título da aba, `<h1>` presente e com ~0px de área visível, topo antigo
   ausente do DOM, campos certos em Configurações (tipos, `title` preenchido, sem texto de dica na
   tela) e os três itens do menu na ordem certa.
2. **Bloqueios** (sem custo): interruptor de tempo real não muda de estado durante gravação normal
   (`preventDefault`) nem durante gravação em tempo real (`disabled=true`, confirmado via
   `botaoTempoReal.disabled`); volta a `disabled=false`/destravado depois de cancelar; item "Enviar
   arquivo" não abre o seletor de arquivo enquanto uma gravação está em andamento.
3. **Nome do arquivo** (sem custo — `page.route` interceptando e abortando antes de chegar à API
   real, só para ler o multipart): upload preserva o nome real (`meu_audio_de_teste.wav`, não vira
   `gravacao.<ext>`); escolher o mesmo arquivo duas vezes seguidas dispara dois envios (prova que o
   `value` é limpo); gravação pelo microfone continua nomeando `gravacao.webm` como sempre — sem
   regressão no caminho antigo.
4. **Ponta a ponta com custo real pequeno** (2 transcrições reais, `.wav` curtos): upload com modelo
   não padrão (`gpt-4o-mini-transcribe`, escolhido no `<select>`) e streaming ligado (interruptor) —
   confirmei via `page.route` (deixando a requisição seguir de verdade) que o multipart enviado
   trazia `modelo=gpt-4o-mini-transcribe` e `stream=true`, ou seja, `modeloAtivo()` e
   `streamingAtivo()` de fato refletem os novos controles, não só a leitura isolada do DOM; o botão
   central mostrou "processando" durante o streaming e o texto chegou na caixa; copiar e
   lixeira/desfazer testados sobre esse texto vindo do upload. Na sequência, tempo real ligado pelas
   Configurações, um turno curto de gravação real: `consumo.jsonl` cresceu exatamente uma linha,
   confirmando `tempoRealAtivo()` de ponta a ponta (não só o `.checked` do interruptor).

**O que não testei** — é onde isso pode falhar sem aparecer:
- Upload de `.m4a`/`.mp3` de verdade (só usei `.wav` nos quatro blocos — o `accept` e o envio tratam
  qualquer formato do mesmo jeito, mas não rodei um arquivo `.mp3` real pela API).
- Navegador diferente de Chromium (Firefox/WebKit) e mobile.
- Troca de dispositivo de microfone (item 4 das Configurações) de verdade com mais de um microfone
  físico — só testei com o dispositivo padrão simulado.
- Duas abas/sessões simultâneas concorrendo pelo mesmo `consumo.jsonl`/`transcricoes.jsonl`.
- Upload de arquivo muito grande ou corrompido (comportamento de erro do backend nesse caso não é
  novo desta tarefa, mas não confirmei que o caminho unificado ainda mostra o balão certo).
- Verificação visual manual em navegador de verdade (só headless automatizado) — não abri a página
  a olho nu para julgar espaçamento/alinhamento do menu ⋮ com o novo item.

### Critério de pronto
- [x] Topo sem título/subtítulo/alternadores/formulário/"ou"; gravação é o primeiro bloco
- [x] `<h1>` oculto visualmente (`clip-path:inset(50%)`, não `display:none`) + `<title>` intocado —
      técnica descrita acima
- [x] Configurações com modelo/streaming/tempo real/microfone, sem dica na tela, explicação no
      `title`/`aria-label`
- [x] `modeloAtivo()`/`streamingAtivo()`/`tempoRealAtivo()` corretas — testadas com envio real de
      cada uma (bloco 4 acima)
- [x] Tempo real bloqueado durante a gravação, liberado depois — confirmado nos pontos que usam
      `.disabled` (todos exclusivos do modo tempo real) e via `preventDefault` na gravação normal
- [x] Item de upload no menu ⋮, abre o seletor e fecha o menu
- [x] Mesmo arquivo duas vezes seguidas transcreve as duas
- [x] Texto do upload soma na caixa com separador correto; copiar e lixeira/desfazer funcionam
- [x] Nome/extensão reais preservados no upload; gravação sem regressão — os dois caminhos testados
- [x] Spinner no botão central durante upload; erro no balão
- [x] Sem regressão: gravação normal, tempo real (ligado pelas Configurações), cancelar, cronômetro,
      faixa de barras, menu ⋮ (Configurações e Consumo) — todos exercitados nos 4 blocos de teste
- [x] Nenhuma regra CSS órfã — grep confirmou
- [x] Nenhum erro novo no console — os únicos erros vistos durante os testes foram
      `net::ERR_CONNECTION_REFUSED` deliberados (bloco 3, requisição abortada de propósito para não
      gerar custo); filtrados explicitamente, não são erro do produto
- [x] `transcritor/README.md` atualizado

### Novas demandas / riscos
- Guard contra upload durante gravação (ver "Feito" acima) — não pedido letra por letra na tarefa,
  mas necessário para não introduzir uma corrida nova ao unificar os dois caminhos.
- Lacunas de teste listadas acima (`.mp3`/`.m4a` reais, outro navegador, troca de microfone física,
  concorrência entre abas) — nenhuma delas é evidência de bug, só não foram exercitadas.

### Ajuste no plano necessário?
Não.

## [2026-08-21] — Interruptor "Recortar em vez de copiar"
Status: concluído

Pedido direto do usuário no chat (fora do fluxo PROXIMA_TAREFA.md), mesmo padrão dos outros
pedidos ad hoc desta sessão. Sem campo de nível declarado — nível `curto` por padrão.

### Feito
- `transcritor/frontend/index.html`: novo interruptor **"Recortar em vez de copiar"** nas
  Configurações (desligado por padrão, explicação no `title`), como último item do painel. Ligado,
  o botão "Copiar texto" da caixa "Transcrição por voz" vira "Recortar texto": troca de ícone
  (copiar → tesoura, mesmo padrão de troca de ícone por classe CSS já usado no botão
  lixeira/desfazer), copia o texto E apaga a caixa em seguida. A apagada reaproveita o mesmo
  caminho com snapshot da lixeira — extraí a função `apagarTranscriptComSnapshot()` (antes só
  inline no handler da lixeira) para os dois usarem o mesmo código; o desfazer recupera um texto
  recortado normalmente. Caixa vazia + recortar ligado mostra "Nada para recortar…" em vez de
  "Nada para copiar…".
- `transcritor/README.md`: documentado o novo interruptor na seção de Configurações e na descrição
  do botão de copiar/recortar; balão de confirmação/erro atualizados para citar "recortar".

### Como testei
Playwright (Chromium headless, sem custo de API — só interação de DOM/clipboard):
interruptor existe e começa desligado; ligar troca `aria-label`/`title`/classe do botão e o ícone
visível (`getComputedStyle(...).display`, confirmado `iconeCopiar`↔`iconeRecortar`); com texto na
caixa, clicar recorta (clipboard recebeu o texto exato E a caixa esvaziou) e o botão
lixeira/desfazer entra em `modo-desfazer`, com o desfazer recuperando o texto; caixa vazia com
recortar ligado mostra o aviso "Nada para recortar…"; desligar o interruptor volta o botão para
"Copiar texto". Zero erros de console. Não testei em navegador de verdade (só headless) nem em
outro navegador além do Chromium.

### Critério de pronto
- [x] Configuração nova nas Configurações, desligada por padrão
- [x] Ícone do botão muda junto com o rótulo
- [x] Recortar copia e depois apaga, com desfazer funcionando sobre o texto recortado
- [x] Caixa vazia não quebra (aviso próprio)
- [x] `transcritor/README.md` atualizado
- [x] Nenhum erro novo no console

### Novas demandas / riscos
- Nenhum.

### Ajuste no plano necessário?
Não — pedido fora do PLANO.md (ad hoc), não altera a frente em andamento.
