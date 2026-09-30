---
tema: Retomada do PM em 2026-09-25 — o que aconteceu desde a Etapa 3
data: 2026-09-25
---

# Coleta — retomada do PM (2026-09-25)

## 1. O que o PROGRESSO trouxe desde 2026-09-06

- [PENDÊNCIA] **Deriva de tamanho da janela compacta (`D-32`)**, achada em 2026-09-21 por um
  Executor em suporte ao vivo, com o usuário perguntando "cadê o botão". Metade boa notícia: a
  máscara funciona no Windows real (448×366 exato numa abertura limpa, a dúvida que a 10ª volta tinha
  deixado). Metade risco confirmado: depois de dias de uso a janela nativa cai para 358×293
  (`× 1/1,25`), a máscara deixa de coincidir com o botão e ele some até reiniciar. Não corrigido.
  Registrado como `B-25`; a decisão de subir ou não fica para o planejamento da Etapa 4.
- [ARTEFATO] **"Abrir planejamento" no menu ⋮** (`D-35`, 2026-09-25, pedido direto, fora do plano):
  primeiro item do menu, abre a página de Planejamento e Execução no navegador (`URL_PLANEJAMENTO`
  em `desktop/app.py`). Teste [10] exige os seis itens na ordem; 231 verificações, 0 falhas,
  headless. Verificado pelo PM no artefato real: o `app.log` do Windows registra
  `menu: abrir planejamento` às 15:49 e 17:25 de 2026-09-25, ou seja, o item funciona no uso real,
  que era o que o Executor deixou como não testado.
- [DIRECIONAMENTO] Mesmo caso da `D-31`: funcionalidade fora da paridade (`D-27`) e fora do MVP
  (`D-34`), sem mudar o critério da fase.

## 2. Estado do registro encontrado na retomada

- [PENDÊNCIA] A retomada na raiz (`_RETOMADA_usabilidade-gravacao.md`) parou em 2026-08-25, antes da
  Fase 2 andar; esta retomada foi feita lendo o estado direto dos arquivos. Reescrever no
  encerramento deste chat.
- [PENDÊNCIA] `.git/index.lock` de 2026-08-27 continua lá, e há trabalho sem commit desde 2026-09-06
  (entre eles `spec/historias/`, `spec/F2_MVP_E_ENTREGAVEIS.md`, `AUDITORIA_2026-09-07_*`). O
  usuário apaga o lock na máquina; commit só com autorização (`M-05`).

## 3. Próximo passo combinado

- [DIRECIONAMENTO] Usuário pediu registrar `B-25` e esta coleta, e depois voltar ao planejamento
  (Etapa 4).
