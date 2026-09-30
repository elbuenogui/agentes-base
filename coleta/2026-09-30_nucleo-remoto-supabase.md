---
tema: Núcleo centralizado no Supabase (reabre D-05)
data: 2026-09-30
---

# Coleta — núcleo remoto no Supabase (2026-09-30)

## 1. A ideia e a decisão

- [DIRECIONAMENTO] O usuário propôs tirar o núcleo da máquina e hospedá-lo no Supabase, com banco
  relacional junto. Motivo, nas palavras dele: não replicar o backend de novo em cada cliente
  ("igual foi replicado aqui a versão web e depois a versão desktop"), não rodar local no Android
  com chave, e liberar o Android e o relógio.
- [DECISÃO] Centralizar o núcleo num backend remoto. Reabre a `D-05` (servidor adiado até a F7) por
  motivo novo, que não é a condição de reabertura escrita nela (consumo fragmentado): clientes
  magros e chave da OpenAI num lugar só. Trade-off aceito: um salto de rede e um serviço externo na
  ferramenta de todo dia. Vira `D-36` quando o plano for aprovado.
- [DECISÃO] Projeto do Supabase: **RAG-COMPARTILHADO**, o mesmo que já existe. Custo: cota e
  segredos divididos com outro uso, então o banco do assistente fica isolado num schema próprio.
- [DECISÃO] Geração de imagem **fica no desktop, no núcleo local**, por enquanto.
- [DECISÃO] **Sem medição local × remoto**: o usuário dispensou.
- [DIRECIONAMENTO] O cliente local passa a falar com a API remota, para que tudo seja salvo no
  banco.
- [DIRECIONAMENTO] Fato técnico que molda o plano, conferido na documentação do Supabase em
  2026-09-30: Edge Functions rodam só TypeScript/Deno (sem Python), com 150 s de tempo total por
  requisição no plano gratuito, 256 MB de memória, e projeto gratuito pausado após 1 semana sem
  uso. O `transcritor/backend/main.py` é reescrito, não transplantado: o contrato
  (`spec/contrato/NUCLEO.md`) é a especificação da reescrita (`D-07`).
- [PENDÊNCIA] Plano em rascunho, esperando aprovação do usuário.

## 2. Plano aprovado

- [DECISÃO] **A Fase 2 encerra pelo critério de uso em regime**, confirmado pelo usuário: ele já
  dita com o app todo dia. A Etapa 4 fecha com a constatação de que não faltaram etapas. Trade-off:
  o método só permite um plano de fase por vez; manter a F2 aberta seguraria o núcleo remoto sem
  ganho.
- [DECISÃO] **Login pelo Supabase Auth já neste plano**, e não token fixo. O PM propôs token fixo
  até o Android; o usuário escolheu deixar o login pronto agora. Custo aceito: mais trabalho no
  desktop (login uma vez, sessão que se renova).
- [DECISÃO] Confirmada a leitura de "o local vai acessar a API para salvar no banco": a imagem
  continua gerada no núcleo local, e o consumo dela é registrado no banco remoto.
- [DECISÃO] `diarize` fora do núcleo remoto: ~43 s para 72 s de áudio (F1) estouraria os 150 s num
  áudio de 5 min.
- [ARTEFATO] `D-36` em `spec/DECISOES.md`; `D-05` marcada como substituída.
- [ARTEFATO] `.claude/estado/PLANO.md` reescrito — plano "Núcleo centralizado no Supabase", seis
  etapas. Snapshot da F2 em `historico/PLANO_2026-09-30_fase2-encerrada.md`; as 22 entradas do
  PROGRESSO da F2 movidas sem edição para
  `historico/PROGRESSO_fase2-desktop_2026-08-25_a_2026-09-21.md`.
- [ARTEFATO] Passe de fechamento: `spec/VISAO.md` (F2 concluída; bloco novo "Núcleo centralizado"
  entre F2 e F3; nota na F7), `spec/MAPA.md` (F2 fechada, plano corrente, E1.3 decidida),
  `spec/BACKLOG.md` (`B-08` e `B-09` subiram).
- [PENDÊNCIA] `PROXIMA_TAREFA.md` da Etapa 1 (reconhecer o RAG-COMPARTILHADO) aguardando o "gera"
  do usuário.
- [PENDÊNCIA] Sem commit — aguarda autorização (`M-05`).

## 3. Tarefa da Etapa 1 e commit

- [DIRECIONAMENTO] O usuário autorizou acesso momentâneo ao RAG-COMPARTILHADO para o
  reconhecimento; o login da CLI do Supabase já está feito na máquina.
- [ARTEFATO] `PROXIMA_TAREFA.md` da Etapa 1 — reconhecimento só de leitura, sete perguntas,
  registro `completo`.
- [DECISÃO] Exceção pontual ao `PM.md`/`COMMIT.md`, autorizada pelo usuário em 2026-09-30: o PM
  faz o commit do trabalho acumulado desde `fc461fa`. Fora do commit: `desktop/app.log`,
  `desktop/config.json`, `desktop/imagens-geradas/`. Registrada também no `PLANO.md`.
