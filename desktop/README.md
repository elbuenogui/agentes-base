# App de desktop — ditado (paridade com a interface web)

Cliente do núcleo de transcrição (`spec/contrato/NUCLEO.md`) que replica o comportamento da
interface web (`transcritor/frontend/index.html`, desenho de referência — `D-27`), com um punhado
de divergências **deliberadas** documentadas em `D-30` (corte de segurança mais longo, balão
flutuante, Consumo em janela própria, recortar por padrão, botões mais leves) — não embute a
página, reescreve o comportamento em Python/Qt, inclusive os ícones (mesmos caminhos SVG,
renderizados com `QtSvg`; o código JS não se aproveita, só o desenho). Lista conferível:
`spec/specs/SPEC-002_paridade-desktop.md`, itens A a J.

## Como rodar

1. Suba o núcleo local (`transcritor/`, ver `transcritor/README.md`) em `http://127.0.0.1:8000` —
   desde a Etapa 5 ele atende só a geração de imagem (`url_nucleo_imagem`); ditado e consumo vão
   para o núcleo remoto, com login (ver "Núcleo remoto e login" abaixo). O atalho do Menu Iniciar
   (`abrir_transcritor.vbs`) já sobe os dois.
2. Nesta pasta:

   ```powershell
   python -m pip install -r requirements.txt
   python app.py
   ```
3. Uma janela pequena abre, sempre por cima das outras, sem roubar o foco, e **de tamanho estável**
   — ela não cresce nem encolhe sozinha, não importa o que aconteça (`J`). Clique no botão redondo
   roxo (ou pressione o atalho global, padrão `Ctrl+Alt+Espaço`) para começar a gravar; clique de
   novo para parar e enviar — **é alternar, não segurar**. O menu **⋮** abre Configurações, Consumo
   (numa janela própria, redimensionável) e Enviar arquivo. Arrastar um `.wav`/`.mp3`/`.m4a` até o
   botão de gravar também transcreve.

## Bibliotecas escolhidas (e por quê, uma linha cada)

- **`PySide6` (Qt)**, incluindo **`QtSvg`** — dá `WindowStaysOnTopHint` + `Tool` +
  `WA_ShowWithoutActivating` juntos (sempre no topo sem roubar o foco), desenha ícones SVG reais,
  interruptores animados e um botão de gravar 100% pintado à mão sem gambiarra. `QtSvg` já vem no
  pacote `PySide6`, não é dependência nova.
- **`keyboard`** — hookeia teclado no nível do sistema no Windows sem driver extra; roda numa
  thread própria, sem travar o loop de eventos do Qt.
- **`sounddevice`** — captura de áudio com wheel pronta para Windows (PortAudio embutido).
- **`numpy`** — mede a amplitude do áudio (barras + gate de silêncio).
- **`requests`** — chama `POST /transcrever` e `GET /consumo` sem escrever o encoding manualmente.

`pyperclip` não é dependência (`D-11`): o clipboard usa `QGuiApplication.clipboard()`, isolado em
`copiar_para_area_de_transferencia` — único ponto que a inserção automática (`B-22`) vai trocar.

## Atalho global — alterna, configurável pela interface (`D-28`)

Um toque começa a gravar, o toque seguinte para e envia. Trocar a tecla é feito nas Configurações,
clicando em "Atalho global" e apertando a combinação desejada (`keyboard.read_hotkey`); vale na
hora, sem reiniciar. Padrão de fábrica: `ctrl+alt+space`.

**Cuidado ao mapear num botão do mouse**: o software do mouse precisa mandar um **atalho de
teclado de verdade** (modo "shortcut"/"keyboard", com as teclas pressionadas *ao mesmo tempo*), não
um **macro/texto** (que manda cada tecla em sequência, apertando e soltando uma por vez). Um combo
de várias teclas soltas sem modificador, vindo de um macro, raramente fica "todo pressionado
junto" — o atalho passa a disparar de forma inconsistente. Prefira `Ctrl+Alt+Espaço` (o padrão) ou
uma tecla única da faixa `F13`–`F24`, se o mouse tiver essa opção — achado no uso real, 2026-08-27.

## Paridade e as divergências declaradas (`D-30`) — SPEC-002 A a J

- **A** — controle único que alterna, cancelar sempre com o slot reservado (nunca desloca o
  centro), cronômetro, faixa de 80 barras espelhada do centro, **corte de segurança em 5 minutos**
  (`A5`, era 2min30s — a web continua em 2min30s; o desktop é onde se dita de verdade e esse tempo
  cortava fala no meio), gate de silêncio por pico (`0,02`).
- **B** — balão único, confirmação **3s** (era 2s), erro 6s. **`B4`: aparece flutuando por cima,
  logo acima do botão de gravar** (era um rodapé fixo, que empurrava o layout) — discreto, largura
  só do texto, nunca muda o tamanho da janela.
- **C/D** — caixa acumula/edita/desfaz (testado o caso do `Backspace` segurado). **`D1`: "Recortar
  em vez de copiar" nasce ligado** (era desligado) — no desktop o texto ditado vai embora para
  outro app e quase nunca volta; deixar o anterior na caixa fazia a gravação seguinte empilhar em
  cima de lixo.
- **E** — menu `⋮` com Configurações/Consumo/Enviar arquivo/**Gerar imagem** (este último fora da
  paridade, ver seção própria abaixo). **`E2`, novo**: arrastar um arquivo de áudio até o botão de
  gravar e soltar transcreve pelo mesmo caminho do Enviar arquivo — nome e extensão reais
  preservados, botão realça enquanto o arquivo paira, formato não aceito ou mais de um arquivo
  avisam pelo balão (nunca em silêncio).
- **F** — modelo, streaming, dispositivo, recortar — cinco linhas no painel de Configurações
  (continua sobreposto dentro da janela pequena).
- **G — Consumo abre em janela própria** (era um painel sobreposto de 42rem dentro da janela
  pequena de 40rem — "desproporcional, não dá pra ler direito, tá até vazando da tela", relatado no
  uso real). Redimensionável (900×600 na abertura), com rolagem, sessão com resetar (só a tela),
  histórico diário com gráfico, linha do tempo com zoom hora/minuto e navegação por dia, clique
  numa requisição abre a transcrição dela **numa janela própria também** (não na janelinha de
  ditado, que ficaria longe de onde o usuário clicou).
- **H** — `Esc` fecha Configurações; dentro da janela de Consumo, `Esc` fecha primeiro o popup de
  requisição, depois a própria janela de Consumo (prioridade correta mesmo sendo outra janela).
- **I** — **botões-ícone circulares de verdade** (raio = metade do lado — a regra genérica de
  `border-radius` produzia "margem quadrada"; era o retângulo cinza atrás do círculo roxo do botão
  de gravar), fundo leve `#eef1f5`, sem chevron no `⋮`, **interruptor com bolinha branca deslizando**
  (era um `QCheckBox` só trocando de cor — "não é um interruptor"), trio ⋮·gravar·cancelar
  encostado e centralizado (era espalhado nas pontas por dois `addStretch`).
- **J, nova** — a janela não muda de tamanho sozinha: cronômetro, faixa de amplitude e cancelar
  ocupam o espaço deles desde a abertura (vazios, não removidos — o mesmo princípio da lixeira em
  `C3`); balão e painéis flutuam por cima, nunca entram no layout.

## Gerar imagem (`D-31`, fora do plano da Fase 2)

Pedido direto do usuário — *"eu precisava de fazer isso... a solução mais rápida possível"* —, não
é paridade com a web nem etapa da `SPEC-002`. Menu **⋮ → Gerar imagem**, janela própria e
redimensionável (mesma razão do Consumo: precisa de espaço para a pré-visualização).

- **Imagens de referência** — três formas de escolher: **Escolher arquivos…**, **Escolher pasta…**
  (não entra em subpastas) e **arrastar e soltar** na janela. Miniaturas com botão de remover no
  canto, contagem `N de 16` sempre visível; passar de 16 avisa pelo balão e não deixa entrar;
  formato fora de PNG/JPG/WEBP também avisa e não entra.
- **Prompt** — caixa de várias linhas, com foco assim que a janela abre.
- **Opções**: modelo (`gpt-image-1.5` como padrão), tamanho, qualidade — mudar qualquer uma
  atualiza o **custo estimado** ao lado (só a saída, ver aviso abaixo).
- **Gerar** — desabilitado sem prompt ou sem imagem de referência. Durante a chamada, um aviso
  explícito ("pode demorar bem mais que uma transcrição") substitui o botão; erros usam o mesmo
  balão do resto do app, tratados pelo `codigo` do núcleo (`MENSAGENS_ERRO_IMAGEM`).
- **Resultado** — pré-visualização, **custo real** (vem na resposta do núcleo) e dois botões:
  **Salvar como…** e **Abrir a pasta**. A imagem é salva **automaticamente** ao chegar, em
  `pasta_saida_imagens` (padrão: `imagens-geradas/` ao lado do app), com nome
  `AAAA-MM-DD_HHMMSS.png` — o que já foi pago nunca se perde, mesmo que o usuário feche a janela
  sem clicar em nada.

**O custo estimado antes de gerar é aproximado de propósito** — é calculado só a partir dos tokens
de saída típicos por qualidade; o custo real de uma chamada com imagens de referência é dominado
pela **entrada** (as próprias imagens), não pela saída. Medido de verdade: duas referências de
256×256 custaram entre **US$ 0,075 e US$ 0,082** por chamada com `gpt-image-1.5` — a estimativa de
saída sozinha, para as mesmas qualidades, ficava em torno de **US$ 0,009 a US$ 0,034**. A diferença
é esperada e está dita na tela; só a resposta da chamada sabe o valor exato. Ver
`spec/contrato/NUCLEO.md`, Operação 3, para a tabela de preços completa e os erros medidos.

**Config novo**: `modelo_imagem`, `tamanho_imagem`, `qualidade_imagem`, `pasta_saida_imagens` em
`config.json` — os três primeiros valem a partir da próxima geração; o quarto, a partir do próximo
salvamento automático.

**Testado de verdade** (2026-08-27, `gpt-image-1.5`, duas referências, ver `PROGRESSO.md` para os
números completos): chamada real via a janela do app até a imagem aparecer, ser salva sozinha em
`imagens-geradas/` e o botão "Abrir a pasta" funcionar; cinco erros reais provocados contra o
núcleo (`PROMPT_VAZIO`, `FORMATO_NAO_ACEITO`, `IMAGENS_DEMAIS`, `MODELO_INVALIDO`,
`TAMANHO_INVALIDO`); o custo apareceu no painel de Consumo, na linha do tempo, com valor não-zero,
sem nenhuma mudança no painel (o núcleo grava pelo mesmo caminho das transcrições). O fluxo de
ditado foi conferido de novo depois (enviar `audio-teste/fala-real.wav` — texto real voltou,
`processando` voltou a `False`).

## Conferência de aparência (método obrigatório desta tarefa, de novo)

`QT_QPA_PLATFORM=offscreen` + `QWidget.grab()` nos estados parado/gravando-com-balão/processando,
Configurações com o interruptor nas duas posições, e a **janela de Consumo** com dado real (109
requisições, `US$ 0,21722` na sessão). Script e imagens apagados ao final — evidência completa no
`PROGRESSO.md`. Divergências achadas e corrigidas nesta rodada: nenhuma nova além das já descritas
acima como implementação (o método desta vez confirmou que os quatro achados da rodada anterior
continuavam corrigidos, e que os pontos de geometria pedidos — trio encostado, botão de gravar
imóvel, interruptor animado, balão flutuante, Consumo sem fundo preto e sem vazar — bateram com o
pedido, com dado real).

## Núcleo remoto e login (Etapa 5 do plano "Núcleo centralizado no Supabase")

- **Para onde vai cada chamada** (`config.json`): `url_nucleo` =
  `https://wqoeoofhuhsdzpkdblbg.supabase.co/functions/v1` (as funções `transcrever` e `consumo` têm o
  nome das rotas, então nada mudou nas rotas); `url_nucleo_imagem` = `http://127.0.0.1:8000` (só
  `/gerar-imagem`); `supabase_url` e `supabase_chave_publicavel` — públicos por desenho.
- **Migração automática**: um `config.json` antigo (sem `url_nucleo_imagem`) é convertido na
  abertura — o `url_nucleo` antigo vira o da imagem, e tudo o que você configurou (atalho,
  dispositivo, modelo, pasta de imagens…) fica igual. Gravado com `\n` e quebra final.
- **Login uma vez**: sem sessão, o app pede e-mail e senha num painel sobreposto, igual ao de
  Configurações (senha mascarada). Na abertura, se o núcleo configurado for o remoto; e a qualquer
  momento em que a sessão expirar. O que foi ditado sem sessão **não se perde**: o áudio fica
  guardado e é reenviado sozinho depois do login, e a caixa de texto não é tocada.
- **A sessão** (token de acesso, token de renovação, validade e o e-mail) mora em
  `%APPDATA%\agentes-base\sessao.json` — fora do repositório. **A senha nunca é gravada.** O app
  renova o token quando faltam menos de 2 min para expirar e, se uma chamada voltar `401`, renova
  uma vez e repete; se a renovação for recusada, pede login de novo.
- **Cabeçalho**: toda chamada leva `Authorization: Bearer <token>` quando há sessão — inclusive o
  `/gerar-imagem` do núcleo local, que é o que faz o consumo da imagem cair no banco (Etapa 4).
- **"Sair da conta"** no menu ⋮ apaga a sessão; o e-mail logado aparece em Configurações → Conta.
- **Saída de emergência**: voltar `url_nucleo` para `http://127.0.0.1:8000` no `config.json`
  funciona como antes — o núcleo local não exige login e ignora o cabeçalho.
- **`reiniciar_transcritor.cmd`**: encerra só o processo que escuta na porta 8000 e o app de desktop
  (python rodando `app.py`), espera a porta liberar e reabre tudo pelo `abrir_transcritor.vbs`. O
  PowerShell dele vai em base64 dentro do `.cmd`; o texto legível é este:

  ```powershell
  $ErrorActionPreference = 'SilentlyContinue'
  $porta = 8000
  $ids = @(Get-NetTCPConnection -LocalPort $porta -State Listen | Select-Object -ExpandProperty OwningProcess -Unique)
  foreach ($id in $ids) { if ($id -gt 0) { Write-Host "Encerrando o nucleo local (porta $porta, PID $id)"; Stop-Process -Id $id -Force } }
  $apps = @(Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" | Where-Object { $_.CommandLine -match '(^|[\s"])((\S*[\\/])?desktop[\\/])?app\.py("|\s|$)' })
  foreach ($p in $apps) { Write-Host "Encerrando o app de desktop (PID $($p.ProcessId))"; Stop-Process -Id $p.ProcessId -Force }
  for ($i = 0; $i -lt 30; $i++) { if (-not (Get-NetTCPConnection -LocalPort $porta -State Listen)) { break }; Start-Sleep -Milliseconds 500 }
  if (Get-NetTCPConnection -LocalPort $porta -State Listen) { Write-Host "A porta $porta nao liberou em 15 s."; exit 1 }
  exit 0
  ```
- **Testes**: `QT_QPA_PLATFORM=offscreen python desktop/testes_sessao.py` — login, renovação,
  401, reenvio, cabeçalho nas três rotas, saída de emergência e log limpo, contra servidores falsos
  locais (nada toca o `config.json`, o `app.log` nem a sessão reais).

## Registro para diagnóstico (`desktop/app.log`)

Na abertura (dispositivo, taxa de amostragem, atalho); ao descartar por silêncio (pico e limiar);
em erro do núcleo — transcrição **ou** consumo (o `codigo`, ou a mensagem de conexão); e, desde a
Etapa 5, os eventos da sessão (`sessao: login ok`, `renovada`, `renovação recusada http=…`,
`saiu da conta`, `sessao_expirada pendentes=N`) e a migração do config — **nunca** token, senha ou
e-mail. Gravação bem-sucedida não gera linha nenhuma. `desktop/*.log` está no `.gitignore`, com
exceção de `app.log` (esse é o registro de diagnóstico, continua existindo).

## O que foi testado, com o dado real

- **J1 (tamanho estável)**: comparei `janela.size()` antes/depois de iniciar gravação e de parar —
  idêntico nos dois casos.
- **Trio imóvel**: comparei o centro X do botão de gravar com o cancelar escondido e com ele
  ativo — idêntico.
- **G5, núcleo desligado** (janela de Consumo agora própria): apontei uma instância separada para
  uma porta inexistente (sem mexer no backend real, que o usuário usa ao vivo) — erro visível,
  mensagem limpa, app não travou.
- **G4**: o popup de requisição aberto a partir da linha do tempo é filho da janela de Consumo, não
  da janela de ditado — confirmado por `parentWidget()`.
- **E1/E2 pelo mesmo caminho**: chamei `_disparar_transcricao` com `audio-teste/fala-real.wav`
  (caminho que o Enviar arquivo e o soltar-arquivo usam os dois) — transcrição real devolvida, e o
  arquivo do usuário **não foi apagado**.
- **Interruptor**: liga/desliga programaticamente, estado consistente.
- **Regressão completa da volta anterior**: gate de silêncio, desfazer com `Backspace` segurado,
  copiar/recortar (agora testado com o padrão já ligado), corte de segurança (valor novo, 300000ms)
  — todos re-testados depois da reescrita de layout e continuam passando.

## O que **não** foi possível testar aqui, e fica por sua conta

- **Arrastar e soltar de verdade** (arrastar um arquivo do Explorer até o botão) — simulei a lógica
  de extensão/caminho compartilhado, não o gesto de arrastar em si (exige mouse real).
  **Atenção**: o `dragEnterEvent`/`dropEvent` estão implementados e testados na lógica que
  reaproveitam, mas o evento de UI do Qt em si (aceitar o `mimeData`, realçar o botão em tempo
  real) só um teste manual confirma.
- **Atalho físico com outra janela em foco, e microfone real**.
- **F3 na prática** (troca de microfone valendo na gravação seguinte).
- **A animação do interruptor rodando** (0,15s) — testei o estado final nas duas posições, não o
  movimento em si (não há como capturar animação num `grab()` estático).

## O que este app ainda **não** faz (por decisão, não por lacuna)

- **Inserir o texto no campo em foco de outro programa** (`B-22`, `D-26`) — só copia para o
  clipboard.
- **Os três estados de janela / botão flutuante** (`D-15`).
- **Modo ao vivo/tempo real** — congelado (`D-02`).

## Erros do núcleo tratados

Sempre pelo campo `codigo`, nunca pelo texto de `detail`. Mapeados: `MODELO_INVALIDO`, `SEM_CHAVE`,
`AUDIO_VAZIO`, `ARQUIVO_MUITO_GRANDE`, `FALHA_AUTENTICACAO`, `SEM_CONEXAO`, `API_RECUSOU`,
`TEMPO_ESGOTADO` — mais falha de conexão de rede (sem `codigo`), tanto na transcrição quanto no
consumo. Desde a Etapa 5: `NAO_AUTENTICADO` e o `401` do gateway do Supabase viram "Sessão expirada
— entre de novo." (e abrem o login), não erro genérico; `REQUISICAO_INVALIDA` tem mensagem própria. O app abre normalmente com o núcleo desligado.

## Declaração sobre o contrato

Bastou de novo — nenhuma linha de `main.py` foi aberta nesta volta. A única leitura fora do
contrato foi `transcritor/frontend/index.html`, autorizada como desenho de referência (`D-27`). A
lacuna do host/porta do núcleo, registrada nas voltas anteriores, continua a mesma: `url_nucleo` em
`config.json`, padrão `http://127.0.0.1:8000`.
