---
artefato: SPEC-001
titulo: Contrato do núcleo de transcrição
fase: F1
status: fechada
data: 2026-08-23
substitui: versão de 2026-08-21 (levantada por leitura de código, no git)
---

# SPEC-001 — Contrato do núcleo de transcrição

**Fechada em 2026-08-23.** A versão de 21/08 descrevia o comportamento do núcleo *lido no código* e
dizia, em cada tabela, "a confirmar por medição". A medição aconteceu (Etapa 1 do `PLANO.md`) e
mudou coisa. Esta versão incorpora o resultado.

> **Dono único (`D-21`).** O comportamento observado do núcleo mora em
> [`contrato/NUCLEO.md`](../contrato/NUCLEO.md) — **um lugar só**. Esta spec não repete tabela de
> campo, de resposta nem de erro: ela diz o que o núcleo **tem de passar a cumprir** e por quê. A
> versão anterior mantinha as duas coisas em paralelo, e foi assim que a spec e a máquina
> divergiram.

## Objetivo

Declarar o que o núcleo faz, o que recebe, o que devolve e como falha — com precisão suficiente para
que um cliente novo (desktop nativo, Android, Wear) seja escrito **sem ler o `index.html` nem o
`main.py`**.

## Escopo

**Dentro**: transcrever áudio (lote e streaming) e consultar consumo.

**Fora, declarado**: o modo ao vivo (`GET /tempo-real/token`, `POST /tempo-real/turno-concluido`)
existe no código e **não faz parte do contrato** — congelado pela `D-02`. Continua servindo a
interface web; nenhum cliente novo deve consumi-lo. `GET /favicon.ico` é detalhe da interface web.

## Comportamento observado

Em [`contrato/NUCLEO.md`](../contrato/NUCLEO.md), medido contra o backend rodando em 2026-08-23:
caminho feliz nos três modelos e nos dois modos, as seis situações de erro provocadas de verdade,
`GET /consumo` capturado. Cada exemplo lá é captura real, não exemplo redigido.

## Requisitos derivados da medição

O que o núcleo **passa a ter de cumprir**. Escopo aprovado pelo usuário em 2026-08-23; a execução é
a Etapa 3 do `PLANO.md`.

- **R1 (de L1) — todo erro carrega `codigo` estável**, com `detail` em português seguindo como texto
  humano. Oito códigos: `MODELO_INVALIDO`, `SEM_CHAVE`, `AUDIO_VAZIO`, `FALHA_AUTENTICACAO`,
  `SEM_CONEXAO`, `API_RECUSOU`, `TEMPO_ESGOTADO`, `ARQUIVO_MUITO_GRANDE`. Vale nos dois modos.
  *Por quê*: três clientes vão reagir diferente a "sem chave" e a "sem rede". Hoje só dá para
  distinguir comparando strings em português — e qualquer ajuste de redação quebra os três de uma
  vez.
- **R2 (de L3) — o núcleo declara prazo de espera próprio**: 120s de leitura, 5s de conexão,
  `TEMPO_ESGOTADO` ao estourar (`D-20`). *Por quê*: hoje herda 600s do SDK. Num app de ditado, ficar
  presos 10 minutos é falha de produto.
- **R3 (de L2) — o núcleo recusa arquivo acima do limite antes de subir**, com
  `ARQUIVO_MUITO_GRANDE` dizendo o tamanho enviado e o teto. *Por quê*: medido — um WAV de 64 MB
  devolve "verifique o formato do arquivo de áudio", que aponta para a causa errada, depois de
  gastar ~14s subindo o arquivo. O teto exato é **a medir**, não a supor.
- **R4 (de L5) — toda resposta do núcleo carrega `X-Nucleo-Contrato: 1`**, e o `NUCLEO.md` declara a
  versão. *Por quê*: sem versão, um cliente antigo quebra em silêncio no dia em que o formato mudar.
  Cabeçalho e não campo no corpo, porque serve igual para o JSON e para o NDJSON.

## O que a medição resolveu sem virar conserto

- **L4 — o evento `final` do streaming não traz custo nem modelo.** Confirmada e **aceita**: quem
  quiser consumo chama `GET /consumo`. Não vira requisito nesta fase.
- **L6 — áudio sem fala.** Reclassificada: não é indefinido, é definido e ruim — `200` com
  alucinação em idioma aleatório, nos dois modos. Virou a **`D-16`**: medir amplitude e não enviar
  áudio sem fala é **obrigação declarada do cliente**, não do núcleo. É o achado mais importante da
  Etapa 1 — a proteção existia no `index.html` e parecia ser do produto.
- **L7 — CORS aberto.** Confirmada e aceita enquanto tudo é local. Vira restrição declarada no dia
  em que o núcleo sair da máquina.
- **L8 — sem parâmetro de idioma.** **Refutada como problema** pela medição: mesmo áudio com e sem
  `language="pt"` deu texto idêntico caractere por caractere e tokens idênticos (`D-08` revisada).
  O núcleo não assume idioma e não ganha parâmetro.
- **Os dois achados de `gpt-4o-transcribe-diarize`** (custo sempre zerado; streaming sem eventos
  `delta`): **fora de escopo** pela `D-17` — o modelo está desativado da interface desde 18/08, o
  bug é inalcançável no uso normal. Ficam registrados no `NUCLEO.md` como comportamento conhecido.

## Critérios de aceitação — situação no fechamento

- **CA1** — cliente novo escrito só com o contrato, sem abrir `index.html` nem `main.py`.
  **Atendido em forma, a validar em uso**: só a POC-1 da Fase 2 prova de verdade, escrevendo um
  cliente. É a mesma régua do critério de conclusão da fase.
- **CA2** — cada situação de erro provocada de verdade, com a resposta observada batendo com a
  documentada. **Atendido**: seis situações, cada uma nos dois modos, evidência colada no
  `PROGRESSO.md`.
- **CA3** — está escrito que o modo ao vivo existe, está congelado e não deve ser consumido.
  **Atendido**: seção própria no `NUCLEO.md`.
- **CA4** — cada lacuna confirmada, refutada ou reclassificada com evidência, nenhuma como
  suposição do PM. **Atendido, com correção de redação**: o critério dizia "L1 a L7" e a spec listava
  oito. São **L1 a L8**, todas fechadas com evidência.

## Dependências

Nenhuma. Foi a primeira unidade de trabalho do projeto.

## O que esta spec ensinou sobre o método

O risco declarado em 21/08 era "o PM levantou o comportamento lendo código, não medindo; divergência
é esperada — achá-la é o objetivo". O risco se realizou e o mecanismo funcionou: a medição achou
três comportamentos que a spec não previa, um deles (`D-16`) com consequência direta em todo cliente
futuro.

O que **não** funcionou foi manter a spec e o contrato descrevendo a mesma coisa em paralelo: a spec
envelheceu em pontos que ninguém releu. Daí a regra de dono único da `D-21`, e a forma desta versão
— a spec ficou com o *porquê* e as respostas de aceitação; o *o quê* mora no contrato.
