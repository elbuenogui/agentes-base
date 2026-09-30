# Retomada — para o PM, em chat novo

> O nome do arquivo ficou do plano antigo de propósito, para não quebrar referências. O conteúdo é
> sempre o estado **atual**. **Atualizado em 2026-09-30**, no encerramento do chat de PM que fechou
> a Fase 2, abriu e executou o plano "Núcleo centralizado no Supabase" e registrou a ideia da
> transcrição como serviço para a Mari.

## Leia nesta ordem

1. `CLAUDE.md` — o papel e as duas regras que valem em qualquer chat.
2. `.claude/CEREBRO.md` — o mapa de onde tudo mora.
3. `.claude/PM.md` e as regras de `.claude/metodo/`.
4. `.claude/estado/PLANO.md` — plano "Núcleo centralizado no Supabase": seis etapas concluídas;
   falta só o critério de uso. A seção final "Estado em 2026-09-30" resume.
5. `spec/DECISOES.md` → `D-36` (e a nota dela) — por que o núcleo saiu da máquina.
6. `spec/contrato/NUCLEO.md` — **contrato 2**: onde o núcleo escuta (remoto × local),
   autenticação, divergências marcadas como medidas ou lidas no código.
7. `spec/BACKLOG.md` → `B-27` (Mari) e `B-26` (imagem).
8. `coleta/2026-09-30_nucleo-remoto-supabase.md` — o diário deste plano, com a consolidação no fim.

## Onde o projeto está

- **Fase 2 encerrada** em 2026-09-30, pelo critério de uso em regime (snapshot em
  `.claude/estado/historico/PLANO_2026-09-30_fase2-encerrada.md`).
- **Núcleo remoto em uso**: projeto Supabase **rag-compartilhado** (`wqoeoofhuhsdzpkdblbg`,
  sa-east-1, plano gratuito), funções `transcrever` e `consumo` (`verify_jwt: true`, contrato 2),
  schema `assistente` com RLS por usuário, histórico importado (1867 linhas) e ditados reais
  entrando (`origem = 'nucleo-remoto'`).
- **Desktop** logado no Supabase (sessão em `%APPDATA%\agentes-base\sessao.json`, renova sozinha),
  ditando no remoto; **geração de imagem continua no núcleo local** (porta 8000) e registra no banco
  com o token (`nucleo-local-imagem`).
- O RAG-COMPARTILHADO também guarda o RAG da Mari e o do assistente de vendas (schema `rag`) — é
  **convergência de infraestrutura**, um projeto de serviços.

## O próximo passo — é do PM, com o usuário

1. Conferir o critério de uso do plano (ditados `nucleo-remoto` crescendo, `.jsonl` parados) e,
   se se sustentar, **fechar o plano**: arquivar `PLANO.md` e `PROGRESSO.md` em `historico/`.
2. Escrever com o usuário o **plano da transcrição como serviço para a Mari** (`B-27`): o usuário
   pediu para retomar por aqui. Pontos já levantados: chamada sai do servidor da Mari com chave de
   serviço (padrão `x-rag-chave` das funções do RAG), nunca do navegador; consumo por projeto, não
   por usuário (mexe no schema: `user_id` é obrigatório hoje); limites de tamanho, frequência e
   gasto; decidir se o texto de terceiros é guardado (pesquisa com pessoas, comitê de ética). O
   contrato 2 é o documento que a integração lê.

## Pendente do usuário

- `B-26` — geração de imagem pelo app às vezes falha com `API_RECUSOU` (já acontecia em 23/09).
  Ele mandou deixar para depois.
- Painel de diagnóstico geral não foi republicado neste chat.

## O que não se reabre

- Servidor adiado (`D-05`) — substituída pela `D-36`.
- Modo ao vivo e inserção automática (`D-33`) — mortos.
- Tamanho e animação da janela flutuante (`D-32`) — aprovados e fechados.

## Armadilhas do ambiente (desta sessão)

- **A máquina de trabalho remota (e o contêiner do PM) não alcançam o Supabase pela rede.**
  Teste real roda no Windows do usuário, por script com `.cmd` e log ao lado; o PM confere pelo
  conector do Supabase (só leitura) e pelo log.
- A venv do transcritor tem `httpx2` (SDK OpenAI 3.1.0), não `httpx`.
- O número de versão das Edge Functions sobe com mudança de configuração do projeto, sem mudar
  código — conferir `ezbr_sha256` antes de achar que alguém sobrescreveu função.
- Gravar em `.claude/` pelo bridge: só por heredoc no terminal remoto (ver `PM.md`).
- Executor por subagente funcionou bem neste chat: tarefa em `PROXIMA_TAREFA.md`, Parte A do
  Executor, Parte B do usuário no Windows, Parte C de conferência do PM.

---

## Mensagem pronta para colar no próximo chat

> PM. Estou retomando o `agentes-base`. A pasta está conectada. Leia
> `_RETOMADA_usabilidade-gravacao.md` e os itens de "Leia nesta ordem". Quero conferir o critério
> de uso do plano do núcleo remoto e, em seguida, planejar a transcrição como serviço para a Mari
> (`B-27`).
