# Trecho removido: alternador "Controle de turno" (Etapa 2, encerrada sem uso)

> Removido de `transcritor/frontend/index.html` e `transcritor/backend/main.py` em 2026-08-20,
> porque `gpt-live-transcribe` recusa `turn_detection` diferente de `null` (bloqueio documentado
> no README antes desta remoção) e a alternativa de trocar de modelo foi recusada pelo usuário.
> Este arquivo é conveniência de consulta — o histórico completo está no git.

## Backend (`transcritor/backend/main.py`)

Constantes e comentário (antes de `CONSUMO_PATH`):

```python
# Alternador de controle de turno do modo tempo real (Etapa 2): "tempo" mantém o comportamento da
# Etapa 1 (turn_detection: None, cliente comita a cada 6s); "api" delega ao server_vad da própria
# Realtime API. Formato de `turn_detection` confirmado na doc oficial — guia de VAD da Realtime API
# (https://developers.openai.com/api/docs/guides/realtime-vad, consulta em 2026-08-20): tipo
# "server_vad" aceita threshold/prefix_padding_ms/silence_duration_ms (create_response e
# interrupt_response só valem para conversas fala-fala, não para sessão de transcrição). Nenhum
# desses campos numéricos é fixado aqui — sem confirmação de qual seria o valor certo para este
# projeto, deixa a API aplicar seus próprios padrões em vez de presumir um número.
MODO_TURNO_TEMPO = "tempo"
MODO_TURNO_API = "api"
MODOS_TURNO_PERMITIDOS = (MODO_TURNO_TEMPO, MODO_TURNO_API)
```

Parâmetro, validação e `turn_detection` condicional em `GET /tempo-real/token`:

```python
@app.get("/tempo-real/token")
async def tempo_real_token(modo_turno: str = MODO_TURNO_TEMPO):
    """Gera um token efêmero (client secret) para o navegador abrir uma sessão de transcrição ao
    vivo direto com a OpenAI (WebSocket), sem que a chave real da API passe pelo navegador em
    nenhum momento. O token dura poucos minutos e só serve para abrir sessões de transcrição
    (não dá acesso geral à API). `modo_turno` escolhe quem fecha cada turno: "tempo" (padrão,
    cliente comita a cada 6s) ou "api" (server_vad da Realtime API decide). Ver
    transcritor/README.md para o formato de uso no frontend."""
    if modo_turno not in MODOS_TURNO_PERMITIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"modo_turno inválido: '{modo_turno}'. Valores aceitos: "
            + ", ".join(MODOS_TURNO_PERMITIDOS),
        )

    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY não configurada — preencha transcritor/.env",
        )

    turn_detection = None if modo_turno == MODO_TURNO_TEMPO else {"type": "server_vad"}
    ...
    return {
        "client_secret": resposta.value,
        "expira_em": resposta.expires_at,
        "modelo": MODELO_TEMPO_REAL,
        "modo_turno": modo_turno,
    }
```

## Frontend (`transcritor/frontend/index.html`)

CSS (seletores dentro dos blocos compartilhados com os outros botões-alternador):

```css
#botaoModelo, #botaoStreaming, #botaoTempoReal, #botaoControleTurno { ... }
#botaoModelo:hover:not(:disabled), #botaoStreaming:hover:not(:disabled), #botaoTempoReal:hover:not(:disabled), #botaoControleTurno:hover:not(:disabled) { background: #dbeafe; }
```

HTML:

```html
<div class="alternador-modelo" id="linhaControleTurno" hidden>
  <span class="rotulo-modelo">Controle de turno:</span>
  <button type="button" id="botaoControleTurno"></button>
  <span class="dica-modelo">(só aparece com a transcrição em tempo real ligada — decide quem fecha cada turno: um timer de 6s no navegador, ou a detecção de fala da própria API)</span>
</div>
```

JS — bloco do alternador em si:

```js
// --- Controle de turno (só vale com o tempo real ligado, ver alternador acima) ---
// "tempo" (padrão): timer no navegador comita a cada 6s, igual à Etapa 1. "api": a própria
// Realtime API decide o fim de cada turno (server_vad) — ver justificativa e fonte da doc
// oficial no README, seção "Transcrição em tempo real".

const botaoControleTurno = document.getElementById("botaoControleTurno");
const linhaControleTurno = document.getElementById("linhaControleTurno");
let modoTurnoApi = false;

function atualizarBotaoControleTurno() {
  botaoControleTurno.textContent = modoTurnoApi ? "turnos pela API" : "turnos por tempo (6s)";
}

botaoControleTurno.addEventListener("click", () => {
  const gravandoNormal = mediaRecorderRapido && mediaRecorderRapido.state === "recording";
  if (gravandoTempoRealEmAndamento || gravandoNormal) return;
  modoTurnoApi = !modoTurnoApi;
  atualizarBotaoControleTurno();
});

atualizarBotaoControleTurno();
```

JS — linha removida do handler do alternador de tempo real (mostrava/escondia `linhaControleTurno`):

```js
// O controle de turno só faz sentido com o tempo real ligado — some da tela junto com ele,
// em vez de ficar visível e sem efeito nenhum.
linhaControleTurno.hidden = !tempoRealLigado;
```

JS — todos os pontos em que `modoTurnoApi` ramificava o comportamento do modo tempo real
(gate de silêncio, timer de commit, fechamento do turno em voo, query string do token):

```js
// query string do token:
const respostaToken = await fetch(URL_TOKEN_TEMPO_REAL + "?modo_turno=" + (modoTurnoApi ? "api" : "tempo"));

// gate de silêncio contínuo (dentro de onaudioprocess):
if (!modoTurnoApi && Date.now() > fimHangoverSilencioTempoReal) return;

// timer de commit periódico (dentro do handler "open" do WebSocket):
if (!modoTurnoApi) {
  intervaloCommitTempoReal = setInterval(() => { ... }, INTERVALO_COMMIT_TEMPO_REAL_MS);
}

// fechamento do turno em voo (dentro do handler "message", evento "completed"):
if (aguardandoUltimoTurnoTempoReal && (modoTurnoApi || commitsPendentesTempoReal === 0)) {
  finalizarFechamentoTempoReal();
}

// pararGravacaoTempoReal — ramo inteiro do modo "pela API" (fechamento sem commit manual,
// aguardando o "completed" do turno em andamento ou o timeout de 5s):
if (modoTurnoApi) {
  limparRecursosTempoReal();
  aguardandoUltimoTurnoTempoReal = true;
  botaoGravacaoRapida.disabled = true;
  mostrarStatusGravacao("carregando", "Encerrando… aguardando a transcrição do último trecho.");
  timeoutEsperaUltimoTurnoTempoReal = setTimeout(() => {
    timeoutEsperaUltimoTurnoTempoReal = null;
    finalizarFechamentoTempoReal();
  }, TIMEOUT_ESPERA_ULTIMO_TURNO_TEMPO_REAL_MS);
  return;
}
```
