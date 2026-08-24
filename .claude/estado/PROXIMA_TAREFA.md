# Tarefa: Corrigir as quatro lacunas do contrato
Referente à **Etapa 3** do `PLANO.md` — a última etapa de código da Fase 1

## AVISO ANTES DE COMEÇAR

**Fale com o usuário antes do primeiro comando.** Esta tarefa reinicia o backend várias vezes e
**quebra o `.env` de propósito** (para provocar "sem chave" e "chave inválida"). Ele usa o app ao
vivo — em 2026-08-23 o aviso chegou tarde no meio de uma medição. Faça uma **cópia de segurança do
`.env`** antes e confira, no fim, com `diff` byte a byte mais uma transcrição de verdade.

**Armadilha da porta 8000, 6ª ocorrência possível**: confira se não há backend antigo rodando antes
de medir qualquer coisa. Medir contra o processo errado invalida a medição inteira.

## Contexto

O contrato do núcleo foi medido na Etapa 1 e fechado na SPEC-001. Quatro lacunas viraram requisito
(`R1` a `R4` da spec). Tudo aqui é **aditivo**: o `frontend/index.html` **não é tocado** e precisa
continuar funcionando exatamente igual depois.

## Arquivos envolvidos

- `transcritor/backend/main.py`
- `spec/contrato/NUCLEO.md` (atualizar o contrato com o que passou a valer)

## O que fazer

### R1 — código de erro legível por máquina

Toda resposta de erro passa a trazer um campo `codigo` estável, **ao lado** do `detail`:

    MODELO_INVALIDO · SEM_CHAVE · AUDIO_VAZIO · FALHA_AUTENTICACAO · SEM_CONEXAO
    API_RECUSOU · TEMPO_ESGOTADO · ARQUIVO_MUITO_GRANDE

**Restrição que não pode ser violada**: o `detail` continua sendo **uma string em português**, no
mesmo lugar de hoje. O `index.html` lê `detail` diretamente — se ele virar objeto, a interface
quebra. O corpo passa a ser `{"detail": "<texto>", "codigo": "<CODIGO>"}`. Isso **não** sai de
`HTTPException(detail=...)` sozinho: use um manipulador de exceção próprio ou devolva `JSONResponse`.

No streaming, o evento de erro ganha o mesmo campo:
`{"tipo": "erro", "detail": "<texto>", "codigo": "<CODIGO>"}`.

### R2 — prazo de espera declarado (`D-20`)

O cliente `OpenAI(...)` passa a declarar **timeout próprio: 120s de leitura, 5s de conexão** — hoje
ele herda 600s do SDK. Ao estourar, devolva `TEMPO_ESGOTADO`. Use **`504`** como status HTTP (é
esgotamento de prazo, não falha da API — os outros erros de API continuam `502`); no streaming, vai
como evento `erro` dentro do `200`, como todos os erros que acontecem depois de o stream abrir.

**Meça o tempo real até a falha e registre.** O SDK repete a chamada sozinho em erro de conexão, e
isso multiplica o tempo total. Se der para provocar barato — por exemplo apontando `base_url` para um
socket local que aceita a conexão e nunca responde — provoque de verdade. Se não der, **diga que não
provocou** e registre a constante lida do cliente. Não invente o número.

### R3 — recusar arquivo grande antes do upload

O backend passa a recusar arquivo acima do teto **antes** de mandar para a API, com
`ARQUIVO_MUITO_GRANDE` e mensagem dizendo **o tamanho enviado e o teto** ("arquivo de 64,2 MB; o
limite é 25 MB"). Status `413`.

O teto vira **uma constante nomeada no topo do arquivo**, não um número solto no meio do código.
**Confirme o limite atual na documentação da OpenAI e registre a data da consulta** — é o mesmo
cuidado que o projeto já tem com preços, que mudam sem aviso.

Ganho colateral: hoje um arquivo de 64 MB gasta ~14s subindo para ser recusado no fim, com uma
mensagem que culpa o formato.

### R4 — versão do contrato

Toda resposta de `POST /transcrever` e `GET /consumo` passa a trazer o cabeçalho
**`X-Nucleo-Contrato: 1`** — nas respostas de sucesso **e** nas de erro, nos dois modos. Só nessas
duas rotas: o modo ao vivo está fora do contrato (`D-02`) e não recebe o cabeçalho.

### Atualizar o contrato

`spec/contrato/NUCLEO.md`: a tabela de erros ganha a coluna `codigo`; a seção de versionamento deixa
de dizer "não há versão"; entram o teto de tamanho e o prazo de espera. As lacunas L1, L2, L3 e L5
saem de "confirmada" para "corrigida", com a data.

## Critério de pronto

- [ ] Backend conferido antes de medir (porta 8000 sem processo antigo).
- [ ] **Os oito códigos provocados de verdade** contra o backend rodando, cada um **nos dois modos**,
      com a resposta colada no `PROGRESSO.md`.
- [ ] `detail` continua string em português em todos eles, e o `index.html` não foi tocado.
- [ ] O teto de tamanho **medido** — um arquivo acima recusado localmente (sem chamar a API) e um
      abaixo passando adiante —, e o limite da OpenAI conferido na documentação, com a data.
- [ ] `X-Nucleo-Contrato: 1` presente em sucesso e em erro, nos dois modos, nas duas rotas, e
      ausente nas rotas de tempo real.
- [ ] Prazo de espera declarado no cliente; tempo real até a falha medido **ou** declarado como não
      provocado.
- [ ] `.env` restaurado e conferido: `diff` byte a byte contra a cópia, mais uma transcrição normal
      funcionando.
- [ ] **O app web conferido no navegador depois da mudança** — gravar, transcrever, ver o erro de um
      caso ruim. É a prova de que a mudança foi mesmo aditiva.
- [ ] `spec/contrato/NUCLEO.md` atualizado.
- [ ] Repositório **pronto para commit** conforme `.claude/metodo/COMMIT.md`. **Não commite.**

## Registro no PROGRESSO

`completo` — o critério pede evidência colada dos oito códigos, o que é incompatível com `curto`.

## O que NÃO fazer

- **Não commite.** Só o usuário autoriza.
- **Não toque em `transcritor/frontend/index.html`**, nem "para melhorar junto".
- Não transforme `detail` em objeto.
- Não mexa em `gpt-4o-transcribe-diarize` — o custo zerado e a ausência de `delta` estão fora de
  escopo por `D-17`.
- Não implemente gate de silêncio no backend — é obrigação declarada do cliente (`D-16`).
- Não refatore o `main.py` além do necessário para estas quatro mudanças.
