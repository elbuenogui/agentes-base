# Consistência entre documentos

> Camada: **cérebro** (genérico — vale em qualquer projeto que use este kit).
> Vale para os dois papéis, PM e Executor.

Um projeto que dura semanas produz documentos que descrevem uns aos outros. É aí que a deriva
começa: o mesmo fato passa a morar em três arquivos, alguém atualiza um, e os outros dois viram
mentira sem avisar ninguém. As cinco regras abaixo existem para isso, e a última é a que mais custa
lembrar.

## 1. Todo fato tem dono único

Cada fato mora em **um** arquivo. Os outros **apontam**, não repetem.

Antes de escrever qualquer coisa, pergunte: *este fato já tem dono?* Se tem, cite o identificador em
vez de reargumentar. Reargumentar é o que produz três respostas diferentes para a mesma pergunta em
três arquivos — e a versão que você vai encontrar primeiro depois não é necessariamente a certa.

**O que se pode repetir é o ponteiro, nunca o conteúdo.** Uma regra que vale para vários papéis é
citada em cada porta de entrada e escrita num lugar só.

## 2. Nada de número derivado escrito à mão

Quantidade de decisões, de etapas, de pendências, de arquivos. Contagem não é fato que se anota, é
fato que se calcula — anotada, ela envelhece a cada linha nova sem avisar. Quem conta é quem lê os
arquivos na hora (o painel, um comando, um `grep`).

Vale também para número que sustenta argumento: **confira antes de escrever, e cubra as subpastas.**
Um argumento apoiado em número errado morre inteiro quando alguém confere. Prefira sustentar decisão
em algo estrutural, que não dependa de contagem.

## 3. Passe de fechamento

Ao concluir ou cancelar uma etapa, procure o nome e o identificador dela em **todos** os arquivos do
projeto e atualize **toda** citação na mesma sessão.

Etapa cancelada que continua escrita como ativa é indistinguível de etapa viva para quem chega
depois. E o custo de fazer isso na hora é de um minuto; o custo de fazer depois é de uma sessão
inteira de arqueologia.

## 4. Quando dois arquivos se contradizem, o mais recente vence

E o perdedor é **corrigido na mesma sessão**, não anotado como divergência conhecida.

Esta é a regra de **desempate**, não a de desenho. O objetivo da regra 1 é que não exista cópia para
desempatar. Precisar desta regra com frequência é sinal de que a regra 1 não está sendo seguida.

## 5. Aviso não é conserto

Se você se pegar escrevendo *"confira este arquivo contra aquele antes de confiar"*, pare. Isso é um
documento sem dono pedindo desculpa.

O padrão é traiçoeiro porque parece responsabilidade: você detectou a deriva e avisou. Mas aviso
acumula — três ou quatro rodadas e ninguém lê mais nenhum deles, inclusive os que importam. **Ataque
a causa ou registre a pendência**, nunca deixe um bilhete no lugar do conserto.

## Como isso se confere sem depender de memória

Disciplina falha em silêncio. Um passe de conferência que roda junto de algo que já se pede
regularmente (um painel de estado, um comando de encerramento) pega o que a disciplina deixa passar.
O que ele procura, em ordem de gravidade:

1. **Contradição de estado** — a mesma etapa, questão ou item com situação diferente em dois arquivos.
2. **Número derivado escrito à mão** — qualquer contagem em prosa.
3. **Ponteiro quebrado** — citação a um identificador que não existe, ou link para arquivo que sumiu.
4. **Data fora de ordem** — arquivo mais velho que ainda se apresenta como atual depois de ter sido
   superado por outro.
5. **Fato sem dono** — a mesma coisa argumentada por extenso em mais de um lugar.
6. **Arquivo de orientação que não conhece o método corrente** — o mais perigoso, porque é o que
   um chat novo lê primeiro.

O passe **não corrige nada sozinho**: ele é vista, e achado vira conversa. A correção é do PM.
