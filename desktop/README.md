# App de desktop — ditado com atalho global

Cliente mínimo do núcleo de transcrição (`spec/contrato/NUCLEO.md`): segure um atalho global,
fale, solte — o texto aparece na janela e já está no clipboard. Não insere no campo em foco de
outro app; é a Fase 2 seguinte (`B-22`, adiada de propósito).

## Como rodar

1. Suba o núcleo (`transcritor/`, ver `transcritor/README.md`) — precisa estar em
   `http://127.0.0.1:8000` (ou ajuste `url_nucleo` em `config.json`).
2. Nesta pasta:

   ```powershell
   python -m pip install -r requirements.txt
   python app.py
   ```
3. Uma janela pequena abre. Segure a tecla configurada (padrão `F9`) em qualquer lugar — mesmo
   com outra janela em foco — para gravar; solte para transcrever. O texto some no clipboard e
   aparece na janela.

## Bibliotecas escolhidas (e por quê, uma linha cada)

- **`keyboard`** — único pacote comum que hookeia teclado no nível do sistema no Windows sem
  precisar de driver extra; é o que permite o atalho funcionar com outra janela em foco.
- **`sounddevice`** — captura de áudio com wheel pronta para Windows (traz o PortAudio embutido),
  mais leve de instalar que `pyaudio`.
- **`numpy`** — já vem com o Python usado no projeto; usado só para medir a amplitude do áudio
  (gate de silêncio).
- **`pyperclip`** — a forma mais direta de escrever no clipboard do Windows sem depender de COM.
- **`requests`** — chamar o `POST /transcrever` com `multipart/form-data` sem escrever o
  encoding manualmente.
- **`tkinter`** — já vem com o Python; suficiente para uma janela de status + caixa de texto, sem
  dependência nova.

## Atalho configurável

`config.json` — troque `atalho` por qualquer tecla nomeada que a lib `keyboard` reconheça (ex.:
`f9`, `scroll lock`, `pause`). **Limitação conhecida**: o modo é "segurar para gravar"
(push-to-talk), então só suporta uma tecla só — não uma combinação tipo `ctrl+alt+espaço` (isso
exigiria rastrear o estado de várias teclas ao mesmo tempo; fora do escopo desta etapa, "o app faz
uma coisa"). `url_nucleo` e `modelo` também estão em `config.json`.

## Gate de silêncio

Antes de mandar qualquer áudio ao núcleo, o app mede o RMS da gravação inteira; abaixo de
`limiar_silencio_rms` (padrão `0.01`, em `config.json`), nada é enviado — a janela mostra
"Silêncio — nada enviado ao núcleo". Existe porque o núcleo **não filtra isso**: o contrato
(`spec/contrato/NUCLEO.md`, seção L6) documenta que áudio de silêncio puro volta `200` com texto
alucinado em idioma aleatório — sem esse gate, o app colaria lixo no clipboard sem aviso.

Testado de verdade (não só por leitura): RMS de um áudio de silêncio digital puro (zeros) = `0.0`,
abaixo do limiar → não é enviado. RMS de um tom sintético = `~0.17`, acima do limiar → é enviado
normalmente. Resultado registrado no `PROGRESSO.md`.

## Erros do núcleo tratados

O app lê o campo `codigo` da resposta (nunca compara o texto de `detail`) e mostra uma mensagem em
português na janela. Mapeados: `MODELO_INVALIDO`, `SEM_CHAVE`, `AUDIO_VAZIO`,
`ARQUIVO_MUITO_GRANDE`, `FALHA_AUTENTICACAO`, `SEM_CONEXAO`, `API_RECUSOU`, `TEMPO_ESGOTADO` — mais
um cliente de falha de conexão de rede propriamente dita (o núcleo fora do ar). Qualquer `codigo`
fora dessa lista cai no texto de `detail` como retaguarda.

## O que este app NÃO faz

- **Não insere o texto no campo em foco de outro programa.** Só copia para o clipboard; colar em
  outro lugar é ação manual do usuário (`Ctrl+V`). Inserção automática é `B-22`, fora de escopo
  desta etapa por decisão (`D-25`).
- Não tem bandeja do sistema, tema, histórico de transcrições nem tela de configuração — só
  `config.json`.
- Não grava nem transcreve enquanto a tecla não está pressionada (sem modo "toggle").
- Não oferece o modo streaming do contrato — chama sempre `POST /transcrever` sem `stream=true`
  (uma única resposta já é suficiente para colar no clipboard).

## Declaração sobre o contrato

**O contrato bastou para quase tudo** — request/resposta de `POST /transcrever`, os campos
`transcricao` e `codigo`, e a tabela de erros foram implementados só lendo
`spec/contrato/NUCLEO.md`, sem abrir `main.py` nem `index.html`.

**Uma lacuna: o contrato não declara onde o núcleo escuta** (host/porta). Isso não é comportamento
de API — é informação operacional (como subir o servidor), então nem deveria necessariamente estar
no contrato; mas um cliente novo genuinamente não tem como adivinhar `http://127.0.0.1:8000` só
lendo `NUCLEO.md`. Precisei abrir `transcritor/README.md` (não é `main.py` nem `index.html`, então
dentro do permitido) para achar isso — está no passo 3 de "Como rodar o backend localmente". Deixei
`url_nucleo` configurável em `config.json` com esse valor como padrão, para o app não depender de
endereço fixo no código.
