# Coleta — Consistência entre documentos e correção do método (2026-08-23)

Chat de PM da retomada. Fechou a Etapa 2 (SPEC-001) e, a pedido do usuário, apurou **de onde vieram**
as inconsistências encontradas na revisão — a pergunta dele foi se o problema é do framework, "porque
se for, vai dar errado sempre".

## 1. Registro por interação

- [DIRECIONAMENTO] O usuário recusou a primeira pergunta do chat ("nem entendi do que você está
  falando"): o PM abriu com escolha técnica entre lacunas antes de contar onde o projeto estava.
  **Contexto vem antes da pergunta**, mesmo com o interlocutor sendo o dono do projeto.
- [DECISÃO] **Escopo da Etapa 3: quatro lacunas** — L1 (código de erro por máquina), L3 (prazo de
  espera), L2 (recusa de arquivo grande antes do upload) e L5 (versão do contrato). Trade-off: uma
  etapa maior do que as três candidatas previstas, em troca de consertar tudo **antes** de existir
  cliente consumindo o núcleo, quando ainda é mudança aditiva e barata.
- [DECISÃO] A L3 entrou por proposta do PM, não estava no plano: o backend herda 600s de timeout do
  SDK, e um app de ditado preso 10 minutos é falha de produto. Virou `D-20`, com **120s** decididos
  pelo usuário.
- [DECISÃO] **`D-19` — entre dois documentos que se contradizem, o mais recente vence**, e o perdedor
  é corrigido na mesma sessão. Trade-off: nenhum relevante; a data já existe em todo artefato. Regra
  de desempate, não de desenho — precisar dela com frequência é sinal de que a `D-21` não está sendo
  seguida.
- [DIRECIONAMENTO] O usuário pediu explicitamente para **mapear a origem** das inconsistências, não
  só corrigi-las: "se for problema da metodologia, significa que vai dar errado sempre". Foi o pedido
  mais valioso do chat — sem ele a Etapa 2 teria fechado com seis remendos e a causa intacta.
- [ARTEFATO] Mapa das seis inconsistências, com causa de cada uma (ver seção 2).
- [DECISÃO] **`D-21` — todo fato tem dono único, e o painel confere**: dono único por fato; nada de
  número derivado escrito à mão; passe de fechamento ao concluir ou cancelar etapa; e o passe de
  conferência dentro da skill `diagnostico-geral`. Trade-off: o painel fica um pouco mais caro de
  gerar e pode acusar achado que o usuário não pediu, em troca de a consistência deixar de depender
  de o PM lembrar.
- [DECISÃO] Não renomear a colisão `L1`–`L8` (lacunas do contrato) × `L-A`–`L-G` (lacunas do
  projeto). Trade-off: convive-se com dois significados separados por um hífen até o fim da Fase 1,
  em troca de não pagar uma varredura para renomear uma família que morre na Etapa 3. Registrado em
  tabela no `MAPA.md` para quem ler no meio.
- [DECISÃO] Exceção pontual e datada: o PM ficou autorizado a editar `.claude/PM.md` e
  `.claude/skills/diagnostico-geral/SKILL.md` **uma vez**, para aplicar a `D-21`. Fora disso, a regra
  de sempre vale. Registrada no `PLANO.md`.
- [ARTEFATO] `SPEC-001` fechada — reescrita para parar de duplicar o contrato: ficou com o *porquê*
  e os critérios de aceitação; o *o quê* mora no `NUCLEO.md`.
- [PENDÊNCIA] Q4 (Galaxy Watch) e Q7 (histórico é requisito) foram respondidas em 21/08 e **nunca
  viraram `D-nn`**. A Q7 é decisão de produto com consequência e provavelmente deveria estar no
  livro-razão. Marcadas em `QUESTOES_ABERTAS.md` com "dono: este arquivo", esperando o usuário.

## 2. As seis inconsistências e de onde vieram

| # | Onde | O que | Causa |
|---|---|---|---|
| 1 | Q1 × `D-08` × SPEC-001 | três respostas para "qual idioma" | fato copiado em 3 arquivos, corrigido em 2 |
| 2 | `MAPA.md` | "14 decisões" (18), "cinco lacunas" (4) | contagem derivada escrita à mão |
| 3 | `L1`–`L8` × `L-A`–`L-G` | dois sentidos para "lacuna" | dois documentos criaram o termo sem se cruzar |
| 4 | Etapa 5 do `PLANO` | etapa cancelada escrita como ativa, `</details>` órfã | edição parcial |
| 5 | Q2 | cabeçalho "parcialmente respondida", corpo "encerrada" | corpo atualizado, cabeçalho não |
| 6 | `VISAO.md` F1 | "a primeira etapa está na fila do Executor" | etapa concluída, arquivo não revisitado |

**Causa raiz**: cinco das seis são o mesmo fato morando em mais de um arquivo sem dono declarado. O
`VISAO.md` tinha a tabela "onde cada informação mora", mas ela mapeia **tipo de artefato**, não
**fato** — então a resposta de uma questão legitimamente aparecia em quatro lugares.

**Sintoma que confirmou o diagnóstico**: o método já tinha detectado essa deriva duas vezes, e nas
duas o conserto foi **um aviso em prosa** — o `PROXIMA_TAREFA.md` carrega até hoje um parágrafo
pedindo ao Executor que não confie nele. Documento que precisa de aviso pedindo desconfiança é
documento sem dono. Virou a regra 5 do `PM.md`: aviso não é conserto.

## 3. Resumo consolidado

### Decisões

`D-19` (o mais recente vence), `D-20` (prazo de espera de 120s), `D-21` (dono único + painel
confere). Mais o escopo da Etapa 3 com quatro lacunas, e a recusa consciente de renomear a colisão
de "lacuna".

### Direcionamentos

Contexto antes da pergunta, ao falar com o usuário. Mapear causa antes de corrigir sintoma. Aviso em
prosa não conserta deriva de documento — ou se ataca a causa, ou se registra a pendência.

### Artefatos

`SPEC-001` fechada e reescrita sem duplicação; `PLANO.md` com Etapas 1 e 2 concluídas, 5 cancelada e
3 detalhada; `QUESTOES_ABERTAS.md`, `MAPA.md` e `VISAO.md` reconciliados; `PM.md` com a seção de
consistência; skill `diagnostico-geral` com o passe de conferência; snapshot em
`historico/PLANO_2026-08-23_pre-etapa2.md`.

### Pendências

Q4 e Q7 sem `D-nn`. A `PROXIMA_TAREFA.md` da Etapa 3 ainda não foi gerada — aguardando o usuário. E
a prova real da `D-21`: o próximo **diagnóstico geral** é que vai dizer se o passe de conferência
acha algo ou se ficou decorativo.

---

## 4. Adendo — o backlog ganha dono (mesma sessão)

- [DIRECIONAMENTO] O usuário propôs, no meio da sessão, que o backlog receba o mesmo tratamento das
  questões abertas: arquivo próprio, ideias ligadas a cada etapa, "porque às vezes uma ideia de uma
  etapa fica interessante só na próxima — ela vai amadurecendo".
- [ARTEFATO] Evidência, na forma que sobreviveu à conferência: o backlog **atravessa fases** e o
  `PLANO.md` morre a cada fase — há item nascido em 16 e 18/08 ainda vivo num plano de uma fase
  aberta em 21/08. E os **60 planos arquivados** em `historico/` congelaram cada um a sua cópia do
  acervo: procurar a razão de uma recusa devolve dezenas de respostas de datas diferentes, e a mais
  recente não é a que aparece primeiro.
- [DIRECIONAMENTO] **Armadilha do número inferido, 3ª e 4ª ocorrências no mesmo argumento** (as duas
  primeiras estão na Nota de processo do `PLANO.md`). Primeiro o PM escreveu "treze versões do
  plano", contando só `historico/PLANO_*.md` e esquecendo a subpasta `snapshots/`. Corrigiu para 60
  — e o usuário perguntou "o plano já tem sessenta versões?", que era a pergunta certa: **não são 60
  planos**. São **4 viradas de plano de verdade** (três encerramentos nomeados e o de hoje), 8
  salvamentos datados e 48 snapshots automáticos, com mediana de **18 linhas** de diferença entre
  consecutivos e vários de 4 a 7. O PM estava contando salvamento automático como se fosse alguém
  recopiando o acervo à mão.
  **O que isso ensina, além de conferir número**: o argumento estava apoiado na métrica errada. A
  justificativa foi reescrita para não depender de contagem de cópias — o que sustenta tirar o
  backlog do plano é ele atravessar fases, que é estrutural e não estatístico. Número frágil não
  sustenta decisão de método; quando o número cai, a decisão cai junto se ela dependia dele.
- [DECISÃO] **`spec/BACKLOG.md` nasce como dono único da ideia-que-não-é-etapa**, e a seção some do
  `PLANO.md`, que fica só com um ponteiro. Trade-off: mais um arquivo na raiz do `spec/`, em troca de
  o acervo parar de morrer (e de ser recopiado) a cada virada de plano.
- [DECISÃO] Cada item tem `nasceu:` (data e origem), `estado:` e **`olhar de novo em:`** (a fase em
  que volta à mesa). O último é o gancho mecânico do amadurecimento: ao fechar uma fase, o passe de
  fechamento da `D-21` lê os itens marcados para a seguinte e pergunta ao usuário quais sobem.
- [DECISÃO] **Item nunca é apagado, só muda de estado** (`amadurecendo`, `adiada`, `recusada`,
  `promovida`, `morta`). É o que faz a mudança de temperatura de uma ideia ficar registrada, em vez
  de ela ser recopiada idêntica ou sumir quando alguém cansa de copiar.
- [DECISÃO] **Ideia recusada com razão mora nos dois lugares, cada um com sua parte** — decisão do
  usuário: a `D-nn` guarda o motivo e a condição de reabertura; o backlog guarda a ideia, viva para
  ser revisitada. Não é duplicação: é divisão de papel, e o item aponta para a decisão em vez de
  reargumentar.
- [ARTEFATO] `D-23` — a recusa de baratear o modo ao vivo trocando o modelo, que estava só no
  backlog, virou decisão. Ela carrega um contraponto que enfraquece a própria recusa: o `BENCHMARK`
  sugere que a perda de nuance vem do **tamanho do pedaço enviado** (fatias de 6s), não do modelo.
  Quem reabrir tem de testar essa hipótese antes de decidir.

### Mais duas inconsistências, achadas ao classificar os vinte itens

| # | O que | Causa |
|---|---|---|
| 7 | "promover o `teste_tempo_real.py`" estava no Backlog **e** como Etapa 4, de 21 a 23/08 | item promovido a etapa não saiu do acervo |
| 8 | "Régua do Win+H — falta aceite explícito" pedia aceite para uma régua **aposentada pela `D-10`** no dia seguinte | backlog não foi revisitado quando a decisão o superou |

Ambas são a mesma família das seis primeiras, e ambas são exatamente o que o `estado:` do novo
backlog resolve: `promovida` aponta para a etapa, `morta` aponta para a decisão que a matou.

---

## 5. Adendo — a revisão estrutural e o componente cérebro

- [DIRECIONAMENTO] O usuário pediu revisão estrutural: o que se produz, onde é a fonte da verdade,
  como evitar acúmulo de lixo, e se o PM tem instrução eficiente. Pediu explicitamente para
  **analisar o propósito original de cada arquivo antes de decidir**, para não cortar sem
  justificativa nem alterar corrompendo o objetivo de criação.
- [ARTEFATO] Painel da revisão, duas passadas:
  `https://claude.ai/code/artifact/4e228a5f-85af-41bb-a9c1-e9c6bc31c117`
- [ARTEFATO] **O achado que reenquadrou tudo**: o `GUIA_AGENTES_BASE.md`, de **16/08**, já continha a
  regra de dono único — *"a retomada é a fonte da verdade sobre onde estamos — nunca duplicar esse
  resumo narrativo... são exatamente esses resumos duplicados que ficam desatualizados primeiro"*. O
  `README.md` já declarava a realimentação (*"traga a melhoria de volta para cá quando fizer sentido
  generalizar"*), nunca usada. **O problema nunca foi falta de regra: foi falta de circulação entre a
  camada genérica e a do produto.**
- [ARTEFATO] Mais duas inconsistências, #9 e #10: o `estado/README.md` dizia 40 KB onde o `PM.md`
  dizia 60; e **eu havia corrompido o `PM.md` no mesmo dia**, escrevendo as regras novas com a
  história deste projeto embutida — o que quebrou a copiabilidade do kit e escondeu do Executor
  regras que valem para ele.
- [DECISÃO] **`D-24` — o assistente é o produto principal, e o agente espera o uso diário.** A
  narrativa do usuário virou decisão. Trade-off: adia a camada de agente, em troca de o projeto
  primeiro se tornar relevante na rotina dele; já existem agentes bons o suficiente para construir
  com eles. **Consequência de método**: a Fase 2 fecha quando ele usar todo dia, não quando estiver
  pronta.
- [DECISÃO] **`M-06` — o cérebro mora em `.claude/`**, declarado em `.claude/CEREBRO.md`. Escolha do
  usuário: é onde as ferramentas já procuram; pasta nova seria melhor para humano e pior para
  máquina.
- [DECISÃO] **`M-05` — só o usuário autoriza commit, e o Executor entrega o repositório pronto.**
  Achado junto: no chat **sem papel declarado** não existia regra nenhuma — era o modo mais
  desprotegido, e ninguém percebia. Por isso a regra é citada nas três portas.
- [DECISÃO] **Livro-razão dividido por camada**: `M-nn` para método (no cérebro), `D-nn` para produto
  (em `spec/`). As quatro decisões de método migraram **mantendo ponteiro no lugar antigo** — a
  precaução que evita quebrar as citações já escritas.
- [DECISÃO] Sobre agentes por ótica na revisão: **a ideia é boa, e o valor está na diversidade e na
  cegueira entre eles, não no número.** Um passe único forma hipótese cedo e lê o resto por dentro
  dela; agentes cegos entre si não compartilham esse contexto. Evidência desta sessão: 6 achados no
  primeiro passe, +2 ao classificar backlog, +1 ao auditar orientação, +1 ao analisar propósitos.
  Cinco agentes com a mesma pergunta, porém, devolvem o mesmo achado cinco vezes.
- [ARTEFATO] Estrutura criada: `.claude/CEREBRO.md` (mapa único) e `.claude/metodo/` com
  `CONSISTENCIA.md`, `HIGIENE.md`, `PLANOS.md`, `COMMIT.md` e `DECISOES_METODO.md`.
- [ARTEFATO] **Três tipos de plano** declarados: fase, manutenção e acompanhamento — os dois últimos
  já tinham acontecido sem ter casa (a faxina de 21/08 disfarçada de plano de fase; o alarme de custo
  virado decisão por falta de lugar).
- [ARTEFATO] Kit desacoplado: `README.md` e `GUIA_AGENTES_BASE.md` atualizados, com o 5º mecanismo
  (regras de método) e a realimentação virando passo do método em vez de sugestão. O
  `DECISOES_METODO.md` fica explicitamente **fora** do que se copia.
- [ARTEFATO] Etapa 6 do plano concluída dentro da revisão: `CLAUDE.md` de 3,2 KB → 2,2 KB, agora
  porta de entrada e não mapa.
- [PENDÊNCIA] A skill **`revisao-acionada`** ficou como esboço no painel — achado com trade-off,
  complexidade e ganho declarados, e lentes independentes. Não foi construída.
- [PENDÊNCIA] Entulho: o lixo do bridge foi movido para `_to_delete/` e entrou no `.gitignore` (a
  pasta montada recusa `rm` com "Operation not permitted"; `mv` funciona). Falta quem rode local
  apagar. O `tmp/` e os 48 snapshots continuam, e dependem de promover o `teste_tempo_real.py`
  primeiro — que é a Etapa 4.

---

## 6. Adendo — a revisão acionada nasce, e o entulho ganha dono

- [DECISÃO] A skill **`revisao-acionada`** foi construída a partir do esboço, por avaliação do
  usuário de que já estava madura para começar. Trade-off: sai antes de ter rodado uma vez de
  verdade, em troca de a próxima revisão já ter forma em vez de ser improvisada de novo.
- [DIRECIONAMENTO] **A trava que o usuário pediu**: a revisão *analisa e não executa*. Escrita como
  seção de abertura da skill, com três razões — achado corrigido no meio da varredura não pode mais
  ser conferido; corrigir muda o terreno que as lentes seguintes ainda vão medir; e quem decide o
  que muda é o usuário. A única escrita permitida é o relatório e, com aprovação, os itens de
  backlog.
- [ARTEFATO] Formato do achado, obrigatório: **o que é · evidência medida · trade-off · complexidade
  · ganho**, mais um veredito (`corrigir agora`, `vira backlog`, `recusar com razão`, `só
  registrar`). Recusar com razão escrita é resultado legítimo — vale mais que um "pendente" que
  ninguém revisita.
- [ARTEFATO] Regra de cobertura: **lente que não rodou é cobertura que não existe**, e o silêncio
  sobre ela se lê como "está tudo certo". A skill obriga a declarar quais rodaram.
- [DECISÃO] **`B-20`** — agentes especialistas por área na revisão, com a correção do usuário
  registrada: **não são vários agentes fazendo a mesma pergunta**; são áreas diferentes (segurança,
  DevOps, dados, custo) fazendo as perguntas delas e buscando as respostas delas. Fica amadurecendo
  até a versão com lentes por texto mostrar onde cega.
- [DECISÃO] **Etapa 4 do plano ampliada** pelo usuário: além de promover o harness, ela passa a
  limpar o `.claude/tmp/`, apagar o `_to_delete/` e aplicar o limiar de snapshot (`B-19`). Ordem
  obrigatória: **promover o harness primeiro** — é o único arquivo com valor dentro da pasta que
  existe para ser apagada. Pode rodar antes da Etapa 3.
- [ARTEFATO] O critério de pronto da Etapa 4 inclui o repositório **pronto para commit** conforme
  `M-05` — é o primeiro teste real da regra nova.

- [ARTEFATO] `PROXIMA_TAREFA.md` gerada para a **Etapa 4** (arrumação), a pedido do usuário, que
  deixou a escolha da ordem com o PM. **Razão da ordem**: a 4 deixa o repositório limpo antes de
  alguém mexer no backend, e o passo 1 dela (promover o harness) é irreversível se a limpeza vier
  antes — o `.claude/tmp/` não é versionado, enquanto os 48 snapshots são (a remoção deles é
  recuperável pelo git; a do rascunho, não).
- [ARTEFATO] Achado ao redigir a tarefa: o docstring do `teste_tempo_real.py` começa com *"Rascunho
  descartável do Executor — NÃO faz parte do produto"*. Promover sem reescrever essa linha deixaria
  no repositório um arquivo versionado dizendo de si mesmo que é descartável. Entrou como passo
  explícito da tarefa.
