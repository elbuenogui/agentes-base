---
tema: Atalho no Menu Iniciar para abrir o transcritor com um clique
data: 2026-09-28
---

# Coleta — atalho do transcritor (2026-09-28)

## 1. Pedido e decisão de processo

- [DIRECIONAMENTO] O usuário pediu um atalho para abrir o transcritor: o app fecha, e o chat que
  ele usava para reabrir (subir núcleo + app) tinha batido o limite de uso — ficou sem o recurso.
- [DECISÃO] Chat aberto como PM. Oferecidas duas rotas (exceção pontual do PM ou tarefa para o
  Executor); o usuário escolheu **exceção: PM faz aqui**. Registrada no `PLANO.md` como anexo
  fora do plano. Não vira regra.
- [DECISÃO] Comportamento escolhido: só "fixar no Menu Iniciar". Recusados por omissão: abrir ao
  ligar o PC, reabrir se fechar, ícone na Área de Trabalho.

## 2. O que foi entregue

- [ARTEFATO] `desktop/abrir_transcritor.vbs` — lançador sem janela: testa `GET /consumo` em
  `127.0.0.1:8000`; se não responde, sobe `transcritor\.venv\Scripts\uvicorn.exe` escondido
  (saída em `uvicorn_out.log`/`uvicorn_err.log`, como já se fazia) e espera até 30 s; depois abre
  `python app.py` escondido, a menos que um processo python com `app.py` já exista (aí avisa).
- [ARTEFATO] `desktop/criar_atalho_menu_iniciar.cmd` + `.ps1` — cria `Transcritor.lnk` na pasta
  Programas do Menu Iniciar do usuário, apontando para o `.vbs` via `wscript.exe`.
- [PENDÊNCIA] Não testado no Windows real: o PM não consegue digitar em terminal pelo controle do
  computador. O usuário roda o `.cmd` uma vez e testa pelo Menu Iniciar.
- [PENDÊNCIA] Sem commit — aguarda autorização (`M-05`).
