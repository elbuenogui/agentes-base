# Assistente de Pesquisa por Áudio — backend
# Endpoint de transcrição: recebe um áudio (multipart) e devolve o texto via API da OpenAI.

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI
from pydantic import BaseModel, field_validator

# A chave vem exclusivamente de transcritor/.env (nunca hardcoded, nunca logada).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODELO_PADRAO = "gpt-4o-transcribe"
MODELOS_PERMITIDOS = (
    "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe",
    "gpt-4o-transcribe-diarize",
)
# Modelos de diarização exigem esse parâmetro (a API rejeita a requisição sem ele).
MODELOS_QUE_EXIGEM_CHUNKING = ("gpt-4o-transcribe-diarize",)

# Preços oficiais documentados no PLANO.md, em dólares. gpt-4o-transcribe e gpt-4o-mini-transcribe
# são cobrados por token (confirmado empiricamente: usage.type == "tokens" nos dois); o preço por
# minuto abaixo só entra em jogo no fallback por duração (usage.type == "duration", ou usage
# ausente) — mesmos valores já usados em benchmark.py.
PRECOS_POR_TOKEN_USD = {
    "gpt-4o-transcribe": {"entrada": 2.50 / 1_000_000, "saida": 10.00 / 1_000_000},
    "gpt-4o-mini-transcribe": {"entrada": 1.25 / 1_000_000, "saida": 5.00 / 1_000_000},
}
PRECO_POR_MINUTO_USD = {
    "gpt-4o-transcribe": 0.006,
    "gpt-4o-mini-transcribe": 0.003,
    "gpt-4o-transcribe-diarize": 0.006,
    # Modo ao vivo (Realtime API), cobrado por minuto de áudio de entrada — confirmado em
    # https://developers.openai.com/api/docs/pricing (consulta em 2026-08-19).
    "gpt-live-transcribe": 0.017,
}

# Modelo usado nas sessões de transcrição em tempo real (Realtime API). Confirmado empiricamente
# (ver PROGRESSO.md) que o cliente pode se conectar direto na OpenAI via WebSocket usando um
# token efêmero — não é preciso o backend fazer relay de áudio.
MODELO_TEMPO_REAL = "gpt-live-transcribe"

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

# Registro de consumo: um JSON por linha, arquivo local (não versionado — ver .gitignore).
CONSUMO_PATH = Path(__file__).resolve().parent.parent / "consumo.jsonl"

# Registro de transcrições: um JSON por linha, ligado a CONSUMO_PATH pelo campo `id` (mesma
# pasta, mesma política de arquivo local não versionado — ver .gitignore).
TRANSCRICOES_PATH = Path(__file__).resolve().parent.parent / "transcricoes.jsonl"

# Consumo acumulado desde que este processo do backend subiu — reinicia a cada `uvicorn` novo.
_consumo_sessao = {"requisicoes": 0, "tokens": 0, "custo_usd": 0.0}

app = FastAPI(title="Assistente de Pesquisa por Áudio — MVP de transcrição")

# CORS liberado só para desenvolvimento local: o frontend abre como arquivo local (origem
# "null") ou em outra porta. Sem credenciais envolvidas; restringir se sair do ambiente local.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _calcular_custo_usd(modelo: str, usage) -> tuple[float, dict]:
    """Calcula o custo estimado em USD e os campos de consumo a persistir junto do registro."""
    tipo = getattr(usage, "type", None) if usage is not None else None

    if tipo == "tokens":
        precos = PRECOS_POR_TOKEN_USD.get(modelo, {"entrada": 0.0, "saida": 0.0})
        custo = usage.input_tokens * precos["entrada"] + usage.output_tokens * precos["saida"]
        return custo, {
            "tipo_usage": "tokens",
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "segundos": None,
        }

    # usage.type == "duration", ou usage ausente/formato inesperado: fallback por duração.
    segundos = getattr(usage, "seconds", None) if usage is not None else None
    custo = (segundos / 60) * PRECO_POR_MINUTO_USD.get(modelo, 0.0) if segundos is not None else 0.0
    return custo, {
        "tipo_usage": tipo or "ausente",
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "segundos": segundos,
    }


def _registrar_consumo(modelo: str, usage) -> str | None:
    # Acessório: falha aqui nunca pode derrubar a resposta de /transcrever para o usuário. Devolve
    # o id gerado (ligação com transcricoes.jsonl) ou None quando não conseguiu registrar.
    try:
        id_consumo = uuid4().hex
        custo_usd, campos = _calcular_custo_usd(modelo, usage)
        registro = {
            "id": id_consumo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modelo": modelo,
            "custo_usd": custo_usd,
            **campos,
        }
        with open(CONSUMO_PATH, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

        _consumo_sessao["requisicoes"] += 1
        _consumo_sessao["tokens"] += registro["total_tokens"] or 0
        _consumo_sessao["custo_usd"] += custo_usd
        return id_consumo
    except Exception as erro:
        print(f"[consumo] falha ao registrar consumo (resposta ao usuário segue normalmente): {erro}")
        return None


def _registrar_transcricao(id_consumo: str, modelo: str, texto: str) -> None:
    # Mesma política de _registrar_consumo: falha ao gravar nunca pode derrubar a resposta ao
    # usuário nem interromper o stream — só loga. Sem linha órfã: só é chamada quando
    # _registrar_consumo já devolveu um id válido.
    if not texto or not texto.strip():
        return
    try:
        registro = {
            "id_consumo": id_consumo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modelo": modelo,
            "texto": texto,
        }
        with open(TRANSCRICOES_PATH, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except Exception as erro:
        print(f"[transcricao] falha ao registrar transcrição (resposta ao usuário segue normalmente): {erro}")


def _gerar_eventos_transcricao_stream(cliente, modelo, nome_arquivo, conteudo, parametros_extra):
    # Formato da resposta em stream: NDJSON (um objeto JSON por linha), cada linha com "tipo":
    # "delta" (pedaço de texto, campo "texto"), "final" (texto completo, campo "texto") ou "erro"
    # (campo "detail"). Documentado também no README.
    #
    # Erros da API da OpenAI que ocorrem durante o streaming (autenticação, rede, recusa da API)
    # não podem virar HTTPException com status 4xx/5xx como no fluxo sem streaming: o StreamingResponse
    # já envia o status HTTP 200 e os headers antes de começar a iterar este gerador, então a única
    # forma de reportar o erro ao cliente é como um evento "erro" dentro do próprio stream.
    try:
        eventos = cliente.audio.transcriptions.create(
            model=modelo,
            file=(nome_arquivo, conteudo),
            stream=True,
            **parametros_extra,
        )
        for evento in eventos:
            tipo = getattr(evento, "type", None)
            if tipo == "transcript.text.delta":
                yield json.dumps({"tipo": "delta", "texto": evento.delta}, ensure_ascii=False) + "\n"
            elif tipo == "transcript.text.done":
                usage = getattr(evento, "usage", None)
                if usage is not None:
                    id_consumo = _registrar_consumo(modelo, usage)
                    if id_consumo is not None:
                        _registrar_transcricao(id_consumo, modelo, evento.text)
                else:
                    print(
                        f"[consumo] evento final do streaming sem 'usage' recuperável "
                        f"(modelo {modelo}) — consumo não registrado para esta requisição"
                    )
                yield json.dumps({"tipo": "final", "texto": evento.text}, ensure_ascii=False) + "\n"
    except AuthenticationError:
        yield json.dumps({
            "tipo": "erro",
            "detail": "Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env",
        }, ensure_ascii=False) + "\n"
    except APIConnectionError:
        yield json.dumps({
            "tipo": "erro",
            "detail": "Não foi possível conectar à API da OpenAI — verifique a rede",
        }, ensure_ascii=False) + "\n"
    except APIStatusError as erro:
        yield json.dumps({
            "tipo": "erro",
            "detail": f"A API da OpenAI recusou a requisição (HTTP {erro.status_code}) — "
            "verifique o formato do arquivo de áudio",
        }, ensure_ascii=False) + "\n"


@app.post("/transcrever")
async def transcrever(
    audio: UploadFile = File(...),
    modelo: str = Form(MODELO_PADRAO),
    stream: bool = Form(False),
):
    if modelo not in MODELOS_PERMITIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Modelo inválido: '{modelo}'. Valores aceitos: "
            + ", ".join(MODELOS_PERMITIDOS),
        )

    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY não configurada — preencha transcritor/.env",
        )

    conteudo = await audio.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo de áudio vazio")

    cliente = OpenAI(api_key=chave)
    parametros_extra = {}
    if modelo in MODELOS_QUE_EXIGEM_CHUNKING:
        parametros_extra["chunking_strategy"] = "auto"

    if stream:
        return StreamingResponse(
            _gerar_eventos_transcricao_stream(
                cliente, modelo, audio.filename or "audio", conteudo, parametros_extra
            ),
            media_type="application/x-ndjson",
        )

    try:
        resultado = cliente.audio.transcriptions.create(
            model=modelo,
            file=(audio.filename or "audio", conteudo),
            **parametros_extra,
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=502,
            detail="Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível conectar à API da OpenAI — verifique a rede",
        )
    except APIStatusError as erro:
        raise HTTPException(
            status_code=502,
            detail=f"A API da OpenAI recusou a requisição (HTTP {erro.status_code}) — "
            "verifique o formato do arquivo de áudio",
        )

    id_consumo = _registrar_consumo(modelo, resultado.usage)
    if id_consumo is not None:
        _registrar_transcricao(id_consumo, modelo, resultado.text)

    return {"transcricao": resultado.text}


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

    cliente = OpenAI(api_key=chave)
    try:
        resposta = cliente.realtime.client_secrets.create(
            session={
                "type": "transcription",
                "audio": {
                    "input": {
                        "transcription": {"model": MODELO_TEMPO_REAL},
                        "turn_detection": turn_detection,
                    }
                },
            }
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=502,
            detail="Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível conectar à API da OpenAI — verifique a rede",
        )
    except APIStatusError as erro:
        raise HTTPException(
            status_code=502,
            detail=f"A API da OpenAI recusou a criação da sessão ao vivo (HTTP {erro.status_code})",
        )

    return {
        "client_secret": resposta.value,
        "expira_em": resposta.expires_at,
        "modelo": MODELO_TEMPO_REAL,
        "modo_turno": modo_turno,
    }


class UsageTempoReal(BaseModel):
    """Corpo esperado em POST /consumo/tempo-real: o campo `usage` do evento
    `conversation.item.input_audio_transcription.completed`, como o navegador recebe da OpenAI.
    Confirmado na doc oficial (consulta em 2026-08-19) que, para `gpt-live-transcribe` (modelo de
    ASR cobrado por duração), esse `usage` sempre vem no formato {"type": "duration", "seconds": N}
    — por isso só esse formato é aceito aqui; qualquer outro é lixo e é rejeitado com 422.

    `texto` é opcional: quando presente, é o texto transcrito daquele turno (persistido em
    transcricoes.jsonl, ligado ao registro de consumo pelo mesmo id). Corpo sem `texto` continua
    válido e grava só o consumo — mantém o contrato antigo da rota."""

    type: str
    seconds: float
    texto: str | None = None

    @field_validator("type")
    @classmethod
    def _tipo_deve_ser_duration(cls, valor: str) -> str:
        if valor != "duration":
            raise ValueError("esperado usage.type == 'duration' para o modo tempo real")
        return valor

    @field_validator("seconds")
    @classmethod
    def _segundos_nao_negativos(cls, valor: float) -> float:
        if valor < 0:
            raise ValueError("usage.seconds não pode ser negativo")
        return valor


@app.post("/consumo/tempo-real")
async def consumo_tempo_real(usage: UsageTempoReal):
    """Registra o consumo de um turno concluído do modo ao vivo. O frontend chama isso porque,
    nesse modo, o navegador fala direto com a OpenAI (token efêmero) e o `usage` chega só lá — o
    backend não tem outro jeito de saber quanto foi gasto. Quando o corpo traz `texto`, grava
    também a transcrição daquele turno, ligada ao mesmo id do registro de consumo."""
    id_consumo = _registrar_consumo(MODELO_TEMPO_REAL, usage)
    if id_consumo is not None and usage.texto is not None:
        _registrar_transcricao(id_consumo, MODELO_TEMPO_REAL, usage.texto)
    return {"registrado": True}


@app.get("/consumo")
async def consumo():
    # Texto por id_consumo, lido de transcricoes.jsonl, para casar com cada linha de
    # consumo.jsonl abaixo. Registro antigo (sem `id`) ou sem transcrição correspondente fica
    # sem entrada aqui — o requisição correspondente entra na lista com texto None.
    textos_por_id: dict[str, str] = {}
    try:
        with open(TRANSCRICOES_PATH, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    registro = json.loads(linha)
                except json.JSONDecodeError:
                    continue
                id_consumo = registro.get("id_consumo")
                texto = registro.get("texto")
                if id_consumo and texto:
                    textos_por_id[id_consumo] = texto
    except FileNotFoundError:
        pass

    por_dia: dict[str, dict] = {}
    requisicoes: list[dict] = []
    try:
        with open(CONSUMO_PATH, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    registro = json.loads(linha)
                except json.JSONDecodeError:
                    continue
                data = registro.get("timestamp", "")[:10]
                agregado = por_dia.setdefault(
                    data, {"data": data, "requisicoes": 0, "tokens": 0, "custo_usd": 0.0}
                )
                agregado["requisicoes"] += 1
                agregado["tokens"] += registro.get("total_tokens") or 0
                agregado["custo_usd"] += registro.get("custo_usd") or 0.0

                id_registro = registro.get("id")
                requisicoes.append({
                    "id": id_registro,
                    "timestamp": registro.get("timestamp"),
                    "modelo": registro.get("modelo"),
                    "custo_usd": registro.get("custo_usd") or 0.0,
                    "texto": textos_por_id.get(id_registro) if id_registro else None,
                })
    except FileNotFoundError:
        pass

    return {
        "sessao": dict(_consumo_sessao),
        "por_dia": sorted(por_dia.values(), key=lambda item: item["data"]),
        "requisicoes": sorted(requisicoes, key=lambda item: item["timestamp"] or ""),
    }


# Serve o frontend como arquivo estático em http://127.0.0.1:8000/ — dá ao navegador uma origem
# HTTP estável (em vez de file://), então a permissão de microfone concedida uma vez continua
# valendo entre recarregamentos. Registrado depois de /transcrever para não conflitar com a rota
# da API.
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / "frontend", html=True),
    name="frontend",
)
