# Comportamentos parqueados

> Comportamentos que o usuário já definiu, mas cuja fase ainda não foi especificada. Ficam aqui
> para não se perderem entre a conversa e a spec. **Nada aqui é tarefa** — cada item vira história
> ou spec quando a fase dele chegar. Quem especificar a fase é obrigado a passar por este arquivo.

## ~~Seleção de idioma nas Configurações~~ — **DESPARQUEADO em 2026-08-23**

> A medição refutou a premissa: forçar `pt` produziu texto e custo idênticos a não forçar nada
> (`D-08`). O seletor perde a justificativa e sai da fila. Volta se aparecer transcrição saindo no
> idioma errado — com evidência, não com previsão. O desenho abaixo fica registrado para esse dia.

### Desenho original (2026-08-21)

Definido pelo usuário em 2026-08-21. **Condicionado ao resultado da medição da Etapa 1 da Fase 1**:
só existe se fixar o idioma se mostrar melhor que deixar a API detectar.

- Um **interruptor** "fixar idioma", que pode ser desligado — desligado significa **nenhum idioma
  fixado**, e a API detecta sozinha.
- Uma **lista** com português, inglês, espanhol, italiano e chinês.
- Estado inicial: interruptor **ligado**, idioma **português**.

Consequência para a Fase 1: o contrato do núcleo ganha um parâmetro `idioma` **opcional** — ausente
significa detecção automática. É isso que torna a caixinha possível em qualquer cliente, hoje na
interface web e amanhã no app desktop. O controle é interface; o parâmetro é contrato.

## A interface web é o desenho de referência do desktop — *fase: F2*

Correção de uma afirmação minha, feita pelo usuário em 2026-08-21. Eu havia escrito que a interface
web "não se aproveita". **O código não se aproveita; o desenho sim** — e é o documento de
comportamento mais completo que este projeto tem.

O que ela já define, e a spec da Fase 2 deve transcrever em vez de reinventar: o fluxo de gravação
com estado visível, o balão efêmero de status, apagar com desfazer por snapshot, copiar e recortar,
o menu de três pontos com Configurações / Consumo / Enviar arquivo, o painel de consumo com linha
do tempo, e a lista de configurações que importam.

O que **não** se transporta: hover como gatilho (não existe em toque, e no desktop compete com a
janela flutuante) e o modo ao vivo, congelado.

## "Colocar a última transcrição aqui" como ação própria — *fase: F2*

Ideia do usuário em 2026-08-21: depois de recortar o texto, poder ir a outro aplicativo e **só
clicar** para o texto entrar ali.

O que **não** dá: o aplicativo não consegue remapear o botão do mouse. Quem faz isso é o software
do próprio mouse, e o remapeamento momentâneo por outro programa não é confiável.

O que dá, e é melhor: **uma segunda ação com atalho próprio** — "colocar a última transcrição no
campo em foco". O usuário mapeia um botão do mouse para gravar e outro para colocar. Nenhum
remapeamento acontece; são dois atalhos independentes, e o mouse continua fazendo o que sempre fez.

Por que isso vale mesmo se a inserção automática funcionar (POC-1 bem-sucedida):

- separa **ditar** de **colocar** — dá para falar agora e escolher o destino depois;
- permite colocar o mesmo texto em vários campos, sem reditar;
- é o degrau de resgate quando a inserção automática falhar num aplicativo específico. O produto
  degrada com elegância em vez de quebrar.

**Detalhe de desenho que importa**: a ação deve inserir a partir da **memória do próprio
aplicativo**, não da área de transferência. Se depender do clipboard, qualquer coisa que o usuário
copiar entre o ditado e o destino destrói o texto — e o app passa a brigar pela área de
transferência com o resto do sistema.

**Respondido em 2026-08-21 (`D-15`)**: colocar **não consome** o texto — ele continua disponível
para ser colocado de novo. A janela é que se minimiza, e volta com o hover sobre o botão flutuante.
É o que torna esta ação útil mais de uma vez seguida.

## Painel de estado como capacidade do próprio assistente — *fase: F8 ou F9*

Observação do usuário em 2026-08-21, ao ver o primeiro painel de diagnóstico: aquilo não é só
ferramenta de planejamento, é **semente do produto**. Um assistente que responde "como está X?" com
um painel visual, montado a partir do estado real, em vez de um parágrafo.

O que já está provado pelo caminho do planejamento e vale como desenho: o painel é **vista**, nunca
fonte de verdade; ele lê arquivos de formato estável; e a informação que não está num arquivo não
entra no painel — vira arquivo primeiro.

Ligações: `D-14` (o comando "diagnóstico geral") e a skill `.claude/skills/diagnostico-geral/`, que
é o protótipo funcionando dessa capacidade.
