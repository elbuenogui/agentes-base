# Sem tarefa de Executor no momento

> Estado em **2026-08-26**. A Etapa 1 (app de desktop mínimo) foi **concluída com duas ressalvas**, e
> uma delas depende do usuário rodar o app. O PM só gera a próxima tarefa depois disso.

**Se você é o Executor e chegou aqui**: não invente tarefa a partir do `PLANO.md`. Avise que não há
tarefa e peça ao PM para gerar uma.

**O que está esperando o usuário** (`python desktop/app.py`, uma vez):

- o **atalho global funciona com outra janela em foco**?
- a **captura por microfone real** grava e transcreve?

O ambiente do Executor não tem microfone nem teclado físico, então essas duas pontas foram revisadas
por leitura e não exercidas. São as únicas coisas entre o app e o uso diário.

**Áudio de fala real disponível** (novo em 2026-08-27): `audio-teste/fala-real.wav` — 32 segundos,
gravação do usuário. Até aqui o núcleo e o app só foram exercitados com **tom sintético**, que prova
que o caminho funciona mas produz texto sem sentido. Este arquivo prova que a cadeia inteira entrega
o que deveria. **Ele não substitui o teste de microfone** — nenhum arquivo exercita a captura.

> O usuário entregou em `.wma`, formato que a API **não aceita**. Convertido para WAV na entrada,
> para o erro genérico de formato não confundir quem for testar. Detalhe em `audio-teste/README.md`.

**Já na fila para a próxima tarefa**, quando ela vier:

1. **Isolar o clipboard numa função própria** (`D-11`) — hoje o `pyperclip.copy(texto)` está inline
   dentro de `_processar_gravacao` em `desktop/app.py`. Pequeno agora, caro depois: é exatamente o
   pedaço que a inserção automática (`B-22`) vai trocar.
2. O que o uso do app apontar.
