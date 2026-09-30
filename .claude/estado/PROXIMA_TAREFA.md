# Tarefa: Reconhecer o projeto Supabase RAG-COMPARTILHADO
Referente à etapa 1 do PLANO.md

## Contexto
O núcleo vai morar no projeto Supabase **RAG-COMPARTILHADO**, que já é usado por outro projeto (o
assistente de vendas no WhatsApp). Antes de criar qualquer coisa lá, precisamos saber o que já
existe e como o outro projeto aplica mudanças, para não colidir com ele (`D-36`). **Esta tarefa só
lê. Nada é criado, alterado ou implantado no Supabase.**

O usuário já deixou o login da CLI do Supabase feito na máquina e autorizou acesso momentâneo ao
projeto para este reconhecimento.

## Arquivos envolvidos
- `.claude/estado/PROGRESSO.md` — o único arquivo do repositório que esta tarefa escreve.
- `.claude/tmp/` — pasta de trabalho, se alguma ferramenta precisar gravar arquivos locais (ex.:
  `supabase link` cria uma pasta `supabase/` no diretório onde roda — rode de dentro de
  `.claude/tmp/`, nunca da raiz do repositório).
- Só leitura: `C:\Users\Guilherme Bueno\Desktop\ARQUIVO-PESSOAL\02_PROJETOS\PROJETO-SECRETÁRIO-WPP`
  (o repositório do assistente de vendas), para descobrir como ele aplica migrações.

## O que fazer
Responda, com a evidência (comando rodado ou arquivo lido), cada pergunta abaixo:

1. **Projeto**: o `project ref`, a região e o plano (gratuito ou pago) do RAG-COMPARTILHADO.
2. **Banco**: quais schemas existem além dos padrão do Supabase, e quais tabelas há em cada um
   (nomes e contagem de linhas; **não** o conteúdo). Existe algum schema ou tabela com nome que
   colidiria com `assistente`?
3. **Edge Functions**: quais existem, e se alguma exige ou dispensa verificação de JWT.
4. **Auth**: quantos usuários existem e com quais provedores (e-mail/senha, telefone, OAuth...); se
   o cadastro público (signup) está aberto ou fechado; se confirmação de e-mail está ligada. **Não**
   liste e-mails nem dados de usuário — só contagens e configuração.
5. **Segredos**: só os **nomes** dos segredos das Edge Functions. Se já existir um com a chave da
   OpenAI, diga o nome — nunca o valor.
6. **Migrações**: como o assistente de vendas aplica mudanças no banco — há pasta
   `supabase/migrations/` no repositório dele? A tabela `supabase_migrations.schema_migrations` do
   projeto tem registros, e eles batem com os arquivos desse repositório? Ou as mudanças parecem
   feitas à mão pelo painel?
7. **Recomendação** (uma a três linhas): com base em 6, qual é o jeito seguro de este repositório
   aplicar o schema `assistente` sem colidir com o histórico de migrações do outro projeto.

Se algum comando pedir a senha do banco, **peça ao usuário para digitá-la** — ela não aparece no
chat, em log nem em arquivo.

## Critério de pronto
- [ ] As sete respostas registradas no PROGRESSO, cada uma com a evidência.
- [ ] Nenhuma alteração no projeto Supabase (nenhum `create`, `alter`, `deploy`, `db push`,
      `secrets set`, `migration repair`).
- [ ] Nenhum segredo, chave, senha ou dado de usuário escrito no PROGRESSO ou no repositório.
- [ ] Nada criado fora de `.claude/tmp/` e do `PROGRESSO.md`.

## Registro no PROGRESSO
completo — é investigação: o relatório é o entregável.

## O que NÃO fazer
- Não alterar nada no Supabase, nem "só para testar".
- Não alterar o repositório do assistente de vendas — só ler.
- Não rodar `supabase link`/`init` na raiz deste repositório.
- Não alterar arquivos fora da lista acima.
- Não adiantar a Etapa 2 (criar schema, usuário ou tabela).
- Não commitar (`M-05`).
