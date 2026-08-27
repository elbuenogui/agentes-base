# Áudio de teste

Fala real, em português, para exercitar o núcleo de transcrição e os clientes dele de ponta a ponta.

## `fala-real.wav`

- **32 segundos**, PCM 16 bits, mono, 16 kHz — o formato mais previsível para a API.
- **Origem**: gravação do usuário (`Gravando 5.wma`), entregue em 2026-08-27 e convertida na entrada.

**Por que não está no formato original**: o arquivo veio em `.wma`, e a API da OpenAI **não aceita
`.wma`** — os formatos aceitos são `flac`, `m4a`, `mp3`, `mp4`, `mpeg`, `mpga`, `oga`, `ogg`, `wav` e
`webm`. Mandar o `.wma` direto devolveria `API_RECUSOU` com a mensagem genérica de formato, e quem
estivesse testando acharia que era bug do cliente. Convertido na entrada para o problema não se
repetir a cada uso.

## Para que serve

Até agora o núcleo e o app de desktop foram testados com **tom sintético**, que prova que o caminho
funciona mas produz texto sem sentido. Este arquivo é **fala real**: é o que prova que a cadeia
inteira — áudio, envio, transcrição, texto de volta — entrega o que deveria entregar.

Serve também como referência estável: mesmo áudio, sempre, para comparar resultado entre modelos ou
depois de uma mudança no núcleo.

## O que ele **não** substitui

**Não testa a captura por microfone.** O app de desktop grava do microfone físico, e nenhum arquivo
exercita esse caminho — isso continua dependendo de alguém rodar o app com um microfone de verdade.

## Custo

Transcrever 32 segundos com `gpt-4o-transcribe` custa alguns centavos de dólar. Não é grátis, mas
está bem longe do alarme de US$ 100/mês (`D-18`) — use à vontade para testar.
