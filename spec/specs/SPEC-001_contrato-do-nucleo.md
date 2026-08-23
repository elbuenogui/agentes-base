---
artefato: SPEC-001
titulo: Contrato do núcleo de transcrição
fase: F1
status: em revisão
data: 2026-08-21
---

# SPEC-001 — Contrato do núcleo de transcrição

## Objetivo

Declarar o que o núcleo faz, o que recebe, o que devolve e como falha — com precisão suficiente
para que um cliente novo (desktop nativo, Android, Wear) seja escrito **sem ler o `index.html`**.

Não é documentação do código: é o contrato que o código passa a ter de cumprir. Onde o código de
hoje diverge, a divergência vira tarefa.

## Escopo

**Dentro**: transcrever áudio (lote e streaming) e consultar consumo.

**Fora, declarado**: o modo ao vivo (`GET /tempo-real/token`,
`POST /tempo-real/turno-concluido`) existe no código e **não faz parte do contrato** — está
congelado por decisão de 2026-08-21. Continua servindo a interface web; nenhum cliente novo deve
consumi-lo. `GET /favicon.ico` é detalhe da interface web, não do núcleo.

## Comportamento observado hoje (a confirmar por medição)

Levantado por leitura de `transcritor/backend/main.py`. **Não medido** — é o que o EXEC vai
verificar antes de esta spec ser congelada.

### Operação 1 — Transcrever áudio

`POST /transcrever`, multipart.

| Campo | Tipo | Obrigatório | Padrão |
|---|---|---|---|
| `audio` | arquivo | sim | — |
| `modelo` | texto | não | `gpt-4o-transcribe` (`main.py:22`) |
| `stream` | booleano | não | `false` |

Modelos aceitos (`main.py:23`): `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`,
`gpt-4o-transcribe-diarize` (este último exige `chunking_strategy=auto`, `main.py:29`).

**Sem streaming** → `200` com `{"transcricao": "<texto>"}` (`main.py:284`).

**Com streaming** → `200`, `application/x-ndjson`, um objeto JSON por linha (`main.py:171`):

```
{"tipo": "delta", "texto": "<pedaço>"}
{"tipo": "final", "texto": "<texto completo>"}
{"tipo": "erro",  "detail": "<mensagem>"}
```

Erros conhecidos:

| Situação | Sem streaming | Com streaming |
|---|---|---|
| modelo inválido | `422` + `detail` | idem (validado antes de abrir o stream) |
| `OPENAI_API_KEY` ausente | `503` + `detail` | idem |
| áudio vazio | `400` + `detail` | idem |
| falha de autenticação na OpenAI | `502` | evento `erro` dentro do stream, com HTTP `200` |
| sem conexão com a OpenAI | `502` | idem |
| OpenAI recusa a requisição | `502` | idem |

O streaming **não pode** usar status HTTP para erro: o `200` e os cabeçalhos já foram enviados
quando o gerador começa a iterar (`main.py:176-180`). Isso é propriedade do contrato, não acidente.

### Operação 2 — Consultar consumo

`GET /consumo` → `200` com `sessao` (acumulado desde que o processo subiu), `por_dia` (agregado) e
`requisicoes` (lista com `id`, `timestamp`, `modelo`, `custo_usd`, `texto`). Arquivo ausente não é
erro: devolve listas vazias (`main.py:400,432`).

## Lacunas do contrato atual

Cada uma vira decisão ou tarefa. São o que impede o critério de conclusão da Fase 1.

**L1 — Erros não têm código legível por máquina.** Só existe `detail` em português. Três clientes
vão precisar reagir diferente a "sem chave" e a "sem rede" — hoje, só comparando strings.
*Proposta*: todo erro passa a trazer `codigo` estável (`SEM_CHAVE`, `AUDIO_VAZIO`, `MODELO_INVALIDO`,
`FALHA_AUTENTICACAO`, `SEM_CONEXAO`, `API_RECUSOU`), com `detail` seguindo como texto humano.

**L2 — Não há limite de tamanho nem de duração.** A API da OpenAI tem limite próprio; hoje um
arquivo grande devolve `502 "verifique o formato do arquivo de áudio"` — mensagem errada para a
causa, que vai confundir quem depurar o cliente.

**L3 — Não há timeout declarado.** Se a OpenAI demorar, o cliente espera indefinidamente. Um app de
ditado precisa de teto e de um erro próprio quando estourar.

**L4 — O evento `final` do streaming não informa custo nem modelo.** O cliente não sabe o que
gastou; só o backend registra. Um cliente nativo que queira mostrar consumo precisa de outra chamada.

**L5 — O contrato não tem versão.** Se o formato mudar, o cliente antigo quebra em silêncio.

**L6 — Áudio sem fala não tem comportamento definido.** Devolve texto vazio? Erro? Não testado.

**L8 — A chamada à API não envia o idioma, e o contrato não tem como dizê-lo.**
`parametros_extra` (`main.py:246`) só carrega `chunking_strategy`.
*Proposta*: o contrato ganha um parâmetro `idioma` **opcional**; ausente significa detecção
automática pela API. Não se fixa português no código — decisão do usuário em 2026-08-21. Fixar ou
não é escolha de quem chama, e o controle de interface que expõe essa escolha é da Fase 2.
**Condicionada à medição**: se a Etapa 1 mostrar que fixar o idioma não melhora nada, o parâmetro
não entra e o contrato apenas registra que o núcleo não assume idioma.

**L7 — CORS aberto** (`allow_origins=["*"]`). Aceitável enquanto tudo é local; vira restrição
declarada no dia em que o núcleo sair da máquina. Já estava no Backlog.

## Critérios de aceitação

- **CA1** — Dado o documento do contrato pronto, quando alguém precisar escrever um cliente novo,
  então todas as operações, campos, formatos de resposta e erros estão nele, e **nenhuma consulta ao
  `index.html` ou ao `main.py` é necessária**.
- **CA2** — Dado cada situação de erro da tabela, quando ela for provocada de verdade contra o
  backend rodando, então a resposta observada bate com a documentada — status, corpo e, no
  streaming, o evento.
- **CA3** — Dado o modo ao vivo, quando alguém ler o contrato, então está escrito que ele existe,
  está congelado e não deve ser consumido por cliente novo.
- **CA4** — Dadas as lacunas L1 a L7, quando o levantamento terminar, então cada uma está
  confirmada, refutada ou reclassificada com evidência — nenhuma fica como suposição do PM.

## Dependências

Nenhuma. É a primeira unidade de trabalho do projeto.

## Riscos

- O PM levantou o comportamento **lendo código, não medindo**. Divergência entre o que está escrito
  aqui e o que a máquina faz é esperada — encontrá-la é o objetivo da primeira tarefa, não um
  fracasso dela.
- Armadilha recorrente do projeto (4 ocorrências): backend antigo esquecido na porta 8000 servindo
  código obsoleto. Medir contra o processo errado invalida o levantamento inteiro.

## Questões respondidas (2026-08-21)

- **Q1 — idiomas**: **português por padrão, mas não fixado no código**. O contrato expõe `idioma`
  como parâmetro opcional (ver L8); a escolha é de quem chama. Lista prevista para a interface da
  Fase 2: português, inglês, espanhol, italiano e chinês, com a opção de não fixar nenhum.
- **Q7 — histórico**: **é requisito**, ainda incipiente e não mapeado. O contrato desta fase
  documenta o histórico como ele é hoje (dois `.jsonl` locais, não versionados, sem retenção); a
  funcionalidade ganha história de usuário própria na especificação da Fase 2, que é quando alguém
  vai olhar para ela.

- **Q8 — como o projeto testa**: **verificação manual, declarada como método**, enquanto o projeto
  for simples. Sem suíte automatizada por ora. Gatilho de revisão: quando houver mais de um cliente
  consumindo o núcleo. Consequência para esta spec: o CA2 é atendido por medição manual registrada
  no `PROGRESSO.md` com evidência colada — é por isso que a tarefa pede nível `completo`.
