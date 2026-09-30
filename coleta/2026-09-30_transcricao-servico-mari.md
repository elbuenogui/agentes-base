---
tema: Fechamento do plano do núcleo remoto e plano da transcrição como serviço para a Mari (B-27)
data: 2026-09-30
anterior: coleta/2026-09-30_nucleo-remoto-supabase.md
---

# Coleta — transcrição como serviço para a Mari (2026-09-30)

## 1. Critério de uso do plano do núcleo remoto

- [DIRECIONAMENTO] Conferência do PM às 16:28 (banco pelo conector, só leitura; `.jsonl` e
  `app.log` na máquina): `.jsonl` parados desde 14:28 (1867 e 1807 linhas; 1867 = `importado-jsonl`
  no banco); 14 linhas `nucleo-remoto` (2 de teste, 12 ditados reais entre 14:30 e 16:25), todas com
  texto e um só dono; 2 imagens `nucleo-local-imagem`. A metade "`.jsonl` parados" se sustenta; a
  metade "no dia a dia" não tinha como — o plano abriu no mesmo dia.
- [DECISÃO] O plano de fase fecha agora e o critério de uso vira `A-01` em
  `.claude/estado/ACOMPANHAMENTO.md` (uma semana, até 2026-10-07). Trade-off: fecha antes de o
  uso em regime estar provado, em troca de liberar o único lugar de plano de fase para a Mari; o
  risco fica coberto pela condição de reabertura da `D-36` e pelo acompanhamento, que não consome
  Executor.
- [ARTEFATO] Virada: `historico/PLANO_2026-09-30_nucleo-remoto-encerrado.md` (com linha de
  fechamento no topo); as 8 entradas do PROGRESSO movidas sem edição para
  `historico/PROGRESSO_nucleo-remoto_2026-09-30.md` (conferido por `diff`); `ACOMPANHAMENTO.md`
  criado no primeiro uso real; `PLANO.md` e `PROXIMA_TAREFA.md` dizendo que não há plano aberto.
  Passe de fechamento: `spec/VISAO.md` (bloco "Núcleo centralizado" `encerrada`) e `spec/MAPA.md`
  ("Plano encerrado").

## 2. Fatos levantados para o `B-27`

- [DIRECIONAMENTO] O servidor da Mari já chama o RAG pelo lado do servidor: 22 buscas com origem
  `mari-api` em `rag.buscas` desde 29/09.
- [DIRECIONAMENTO] O padrão `x-rag-chave` é **uma chave para todos os projetos** (segredo
  `RAG_CHAVE_ACESSO`), com o `projeto` escolhido no corpo — quem tem a chave age como qualquer
  projeto. As funções do RAG usam `verify_jwt: false` e escrevem pelo `SUPABASE_DB_URL`.
- [DIRECIONAMENTO] `rag.buscas` já guarda a pergunta digitada por quem usa a Mari. A questão de
  guardar texto de terceiros já existe hoje, independente da transcrição.
- [DIRECIONAMENTO] `assistente.consumo.user_id` é obrigatório e o RLS é por usuário — o schema é do
  uso pessoal.

## 3. Decisões de escopo do plano da Mari

- [DECISÃO] **Só o serviço** entra neste repositório: função no RAG-COMPARTILHADO, limites,
  registro de consumo por projeto, contrato. A gravação no navegador e a chamada pelo servidor da
  Mari ficam no repositório dela e leem o contrato. Trade-off: o plano fecha dependendo de trabalho
  feito fora daqui (critério: uma chamada real do servidor da Mari transcreve).
- [DECISÃO] **O texto transcrito não é guardado**: o serviço registra só consumo. Trade-off: perde
  material para a pesquisa de IHC; em troca, não depende do comitê de ética. A pergunta enviada à
  Mari continua indo para `rag.buscas`, como já vai.
- [DIRECIONAMENTO] Recomendações do PM, levadas ao rascunho do plano para o usuário vetar: chave
  própria do serviço, com o projeto decidido pela chave e não pelo corpo; função separada da
  `transcrever` pessoal; tabela de consumo à parte do schema `assistente`.
