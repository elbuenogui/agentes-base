# diagnóstico geral — o painel de roadmap

Uma skill que lê os arquivos de estado de um projeto e devolve **uma página navegável**: as fases
percorridas com o que cada uma entregou, onde estamos, o que vem, e o rastro até o chat em que cada
coisa foi decidida.

## Para que ela existe

Quem toca um projeto de várias fases não consegue guardar na cabeça o plano inteiro, com as
especificações e os marcos de cada etapa. **Quem consegue é quem lê os arquivos.** A skill devolve
isso em forma navegável, em vez de um parágrafo no chat.

E devolve **estado**, não opinião: tudo que aparece vem de arquivo. O que não está em arquivo não
entra — vira arquivo primeiro.

## Quando ela dispara

Você pede: **"diagnóstico geral"**, "panorama", "roadmap", "como está o projeto". Ou automaticamente,
se o projeto adotar os gatilhos: **ao fechar uma tarefa conferida** e **na virada de plano** — os
dois momentos em que alguma coisa mudou de verdade.

## O que ela precisa do projeto

**Estado guardado em arquivo.** Um plano com etapas, um registro do que já foi feito, decisões
escritas. Se o projeto não tiver isso, a skill **diz que não tem e para** — ela não inventa fase nem
etapa. Painel montado sobre suposição é pior que painel nenhum: parece autoridade e é chute.

## Como instalar

**Na conta** — vale em qualquer chat, sem depender do repositório: salve o `SKILL.md`. É o caminho
para quem toca vários projetos.

**No projeto** — copie esta pasta para `.claude/skills/diagnostico-geral/`. É o caminho para quem
quer a skill versionada junto com o projeto, viajando no git com ele.

Os dois convivem. Se o seu cliente não registrar skills de projeto automaticamente, aponte o caminho
do arquivo — vale a pena deixar isso escrito no arquivo de entrada do projeto, para o comando não
depender de o cliente descobrir sozinho.

## A configuração fica no projeto

A skill descreve **como** montar o painel. **Quais** arquivos ler, com que vocabulário, onde publicar
e com que cara é de cada projeto, e mora em **`.claude/painel.md`**.

Na primeira chamada, se esse arquivo não existir, a skill **não adivinha**: ela monta a configuração
com você, uma vez, a partir do modelo em `referencias/painel-modelo.md`. Depois disso é leitura.

> **Por que não descobrir a cada geração:** painel que muda de forma entre execuções deixa de ser
> comparável com o anterior — e comparar é metade do valor.

## Ela também lembra o projeto do que ele sabe fazer

Uma seção do painel lista **o que você pode fazer** — cada comando com o que se digita, o que
acontece e o fluxo em uma linha. Montada a partir do que o projeto realmente tem, e **consciente do
estado**: um comando cujo insumo já existe aparece em destaque dizendo isso; um que não se aplica
agora fica apagado, mas continua na lista.

**Por quê:** ferramenta que ninguém lembra que existe é ferramenta que não existe. Um projeto acumula
skills e comandos, e eles somem da cabeça de quem os criou em poucas semanas.

## O que a mantém enxuta

Um painel que cresce sem regra vira um paredão que ninguém lê. Não entram: decisão antiga por
extenso (vira índice de uma linha), item de backlog recusado ou morto, **estimativa de esforço**
("custa duas sessões" é chute com cara de dado), e qualquer número copiado de dentro de um arquivo —
se está em prosa, provavelmente está velho.

## Ela também confere

No mesmo passe em que lê, a skill checa se os arquivos concordam entre si: contradição de estado,
contagem escrita à mão, ponteiro quebrado, data fora de ordem, fato sem dono, e arquivo de orientação
que não conhece o método corrente. O resultado sai numa seção do painel — **que aparece mesmo
vazia**, porque silêncio não distingue "conferi e está certo" de "não conferi".

**Ela não corrige nada.** Achado vira conversa; a correção é de quem cuida do plano, depois.

## Se você alterar esta skill

Ela nasceu num repositório onde o arquivo vivo é a fonte. Cópias — na conta, em outro projeto — são
**destinos de exportação**, não segundas fontes. Se melhorar alguma regra, melhore na origem e
reexporte: cópia editada à mão diverge, e a de conta é a pior de perceber, porque some do repositório
e ninguém vê que envelheceu.

## Conteúdo

    SKILL.md                          o procedimento — é o que a skill executa
    README.md                         este arquivo
    referencias/painel-modelo.md      modelo do .claude/painel.md, com os < > para preencher
