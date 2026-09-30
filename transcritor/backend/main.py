# Assistente de Pesquisa por Áudio — backend
# Endpoint de transcrição: recebe um áudio (multipart) e devolve o texto via API da OpenAI.

import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    Timeout,
)
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
#
# Modelos de imagem (Operação 3 — geração de imagem, D-31) têm 3 preços por token em vez de 2: a
# entrada se divide entre texto e imagem (usage.input_tokens_details.{text_tokens,image_tokens}),
# sem "saida"/"entrada" únicos. Confirmado em developers.openai.com/api/docs/pricing, 2026-08-27 —
# **atenção**: gpt-image-1 tem preço diferente de gpt-image-1.5/gpt-image-2 (imagem de entrada
# US$10/US$8/US$8 por milhão, saída US$40/US$32/US$30) — não são intercambiáveis. `dall-e-2`, que
# a tarefa original listava como aceito, **foi removido da API em 2026-05-12** (confirmado por
# busca em 2026-08-27) — por isso não entra na lista de modelos permitidos abaixo.
PRECOS_POR_TOKEN_USD = {
    "gpt-4o-transcribe": {"entrada": 2.50 / 1_000_000, "saida": 10.00 / 1_000_000},
    "gpt-4o-mini-transcribe": {"entrada": 1.25 / 1_000_000, "saida": 5.00 / 1_000_000},
    "gpt-image-2": {"texto_entrada": 5.00 / 1_000_000, "imagem_entrada": 8.00 / 1_000_000, "saida": 30.00 / 1_000_000},
    "gpt-image-1.5": {"texto_entrada": 5.00 / 1_000_000, "imagem_entrada": 8.00 / 1_000_000, "saida": 32.00 / 1_000_000},
    "gpt-image-1": {"texto_entrada": 5.00 / 1_000_000, "imagem_entrada": 10.00 / 1_000_000, "saida": 40.00 / 1_000_000},
    "gpt-image-1-mini": {"texto_entrada": 2.00 / 1_000_000, "imagem_entrada": 2.50 / 1_000_000, "saida": 8.00 / 1_000_000},
}

# Operação 3 — geração de imagem (D-31, fora do plano da Fase 2). gpt-image-1.5 como padrão, por
# pedido explícito da tarefa (gpt-image-2 é o mais novo, mas isso não muda essa decisão).
MODELO_IMAGEM_PADRAO = "gpt-image-1.5"
MODELOS_IMAGEM_PERMITIDOS = ("gpt-image-2", "gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini")
TAMANHOS_IMAGEM_PERMITIDOS = ("auto", "1024x1024", "1536x1024", "1024x1536")
QUALIDADES_IMAGEM_PERMITIDAS = ("low", "medium", "high", "auto")
MAX_IMAGENS_REFERENCIA = 16
# Formatos de imagem comuns aceitos pela API para referência/edição; 50MB por arquivo é o limite
# documentado ("less than 50MB in size") para a rota de edição de imagem.
FORMATOS_IMAGEM_ACEITOS = (".png", ".jpg", ".jpeg", ".webp")
TAMANHO_MAXIMO_IMAGEM_BYTES = 50 * 1024 * 1024
# Gerar imagem demora bem mais que transcrever — timeout de leitura bem mais folgado que o de
# /transcrever (120s).
TIMEOUT_CLIENTE_API_IMAGEM = Timeout(300.0, connect=5.0)
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

# Prazo de espera do cliente da API (R2 / lacuna L3 da SPEC-001): sem isso, o SDK herda o default
# de 5s para conectar e 600s (10min) depois de conectado, mais até 2 tentativas automáticas — um
# app de ditado não pode ficar preso tanto tempo. 120s de leitura é folgado para um áudio de poucos
# minutos, bem abaixo do teto antigo.
TIMEOUT_CLIENTE_API = Timeout(120.0, connect=5.0)

# Teto de tamanho de upload, verificado antes de mandar para a API (R3 / lacuna L2 da SPEC-001).
# 25 MB é o limite documentado pela OpenAI para o campo `file` desta rota: "Files can be up to
# 25 MB." — https://developers.openai.com/api/docs/guides/speech-to-text, consultado em 2026-08-24.
TAMANHO_MAXIMO_AUDIO_BYTES = 25 * 1024 * 1024

# Rotas cobertas pelo contrato do núcleo (R4) — só essas recebem o cabeçalho de versão. O modo ao
# vivo (`/tempo-real/*`) está fora do contrato por decisão de 2026-08-21 (ver spec/contrato/NUCLEO.md).
ROTAS_DO_CONTRATO = {"/transcrever", "/consumo", "/gerar-imagem"}
VERSAO_CONTRATO_NUCLEO = "1"

# Núcleo no Supabase (Etapa 4): quando o cliente repassa `Authorization: Bearer <token do usuário>`,
# o consumo de /gerar-imagem vai para o banco (schema `assistente`), gravado como esse usuário pela API
# de dados — e não para os .jsonl. Sem o cabeçalho, nada muda. URL e chave publicável vêm de
# SUPABASE_URL e SUPABASE_CHAVE_PUBLICAVEL em transcritor/.env (públicas por desenho).
ORIGEM_IMAGEM_REMOTA = "nucleo-local-imagem"
TIMEOUT_REGISTRO_REMOTO_S = 10.0

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


class ErroNucleo(Exception):
    """Erro do núcleo com código legível por máquina (R1 / lacuna L1 da SPEC-001). `detail`
    continua sendo uma string em português no mesmo lugar de sempre — o `index.html` lê esse campo
    direto e quebra se ele virar objeto; `codigo` é um campo aditivo ao lado dele."""

    def __init__(self, status_code: int, codigo: str, detail: str):
        self.status_code = status_code
        self.codigo = codigo
        self.detail = detail


@app.exception_handler(ErroNucleo)
async def _manipulador_erro_nucleo(request: Request, exc: ErroNucleo) -> JSONResponse:
    headers = (
        {"X-Nucleo-Contrato": VERSAO_CONTRATO_NUCLEO}
        if request.url.path in ROTAS_DO_CONTRATO
        else {}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "codigo": exc.codigo},
        headers=headers,
    )


def _erro_api_para_codigo(erro: Exception, o_que_verificar: str = "o formato do arquivo de áudio") -> tuple[str, str, int]:
    """Traduz uma exceção da SDK da OpenAI em (codigo, detail, status_http) — usado tanto no modo
    sem streaming (vira ErroNucleo) quanto no modo streaming (vira evento "erro"). A ordem dos
    `isinstance` importa: APITimeoutError é subclasse de APIConnectionError, e AuthenticationError
    é subclasse de APIStatusError — a checagem mais específica precisa vir primeiro.

    `o_que_verificar` só troca a mensagem do caso genérico (API_RECUSOU) — os outros três já são
    independentes de operação; usado por /gerar-imagem para não sugerir "arquivo de áudio" num
    erro de geração de imagem."""
    if isinstance(erro, APITimeoutError):
        return "TEMPO_ESGOTADO", "A API da OpenAI não respondeu a tempo — tente novamente", 504
    if isinstance(erro, AuthenticationError):
        return (
            "FALHA_AUTENTICACAO",
            "Falha de autenticação na API da OpenAI — verifique a chave em transcritor/.env",
            502,
        )
    if isinstance(erro, APIConnectionError):
        return "SEM_CONEXAO", "Não foi possível conectar à API da OpenAI — verifique a rede", 502
    return (
        "API_RECUSOU",
        f"A API da OpenAI recusou a requisição (HTTP {erro.status_code}) — verifique {o_que_verificar}",
        502,
    )


def _gerar_favicon_ico() -> bytes:
    """Gera em memória um favicon.ico mínimo (quadrado sólido 16x16, cor da marca #7c3aed) — sem
    depender de nenhum arquivo de imagem nem biblioteca externa. Formato: cabeçalho ICO + uma
    imagem BITMAPINFOHEADER de 32bpp (canal alfa cobre a transparência, máscara AND zerada)."""
    largura = altura = 16
    pixel_bgra = bytes((237, 58, 124, 255))  # cor #7c3aed opaca, em ordem BGRA
    dados_xor = pixel_bgra * (largura * altura)
    dados_and = b"\x00" * (((largura + 31) // 32) * 4 * altura)

    cabecalho_dib = struct.pack(
        "<IiiHHIIiiII",
        40, largura, altura * 2, 1, 32, 0, len(dados_xor) + len(dados_and), 0, 0, 0, 0,
    )
    imagem = cabecalho_dib + dados_xor + dados_and

    cabecalho_ico = struct.pack("<HHH", 0, 1, 1)
    entrada_ico = struct.pack(
        "<BBBBHHII", largura, altura, 0, 0, 1, 32, len(imagem), len(cabecalho_ico) + 16,
    )
    return cabecalho_ico + entrada_ico + imagem


FAVICON_ICO = _gerar_favicon_ico()


def _calcular_custo_usd(modelo: str, usage) -> tuple[float, dict]:
    """Calcula o custo estimado em USD e os campos de consumo a persistir junto do registro."""
    tipo = getattr(usage, "type", None) if usage is not None else None

    # Operação 3 (geração de imagem): usage não tem "type" — tem input_tokens_details com a
    # entrada já dividida em texto/imagem. Checar isso primeiro identifica o formato sem precisar
    # de um parâmetro extra nesta função (mantém /transcrever e /gerar-imagem chamando a mesma
    # _registrar_consumo, sem duplicar o código que grava o arquivo e atualiza a sessão).
    detalhes_entrada = getattr(usage, "input_tokens_details", None) if usage is not None else None
    if detalhes_entrada is not None:
        precos = PRECOS_POR_TOKEN_USD.get(
            modelo, {"texto_entrada": 0.0, "imagem_entrada": 0.0, "saida": 0.0}
        )
        texto_tokens = getattr(detalhes_entrada, "text_tokens", 0) or 0
        imagem_tokens = getattr(detalhes_entrada, "image_tokens", 0) or 0
        saida_tokens = getattr(usage, "output_tokens", 0) or 0
        custo = (
            texto_tokens * precos.get("texto_entrada", 0.0)
            + imagem_tokens * precos.get("imagem_entrada", 0.0)
            + saida_tokens * precos.get("saida", 0.0)
        )
        return custo, {
            "tipo_usage": "tokens_imagem",
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": saida_tokens,
            "total_tokens": getattr(usage, "total_tokens", None),
            "segundos": None,
        }

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


def _token_bearer(request: Request) -> str | None:
    """Token do cabeçalho `Authorization: Bearer <token>`, ou None sem cabeçalho (ou em outro formato)."""
    valor = request.headers.get("authorization") or ""
    if not valor[:7].lower() == "bearer ":
        return None
    return valor[7:].strip() or None


def _resumo_erro_remoto(resposta) -> str:
    # Só código e mensagem curta da API de dados — nunca o `details`, que pode repetir a linha (o prompt).
    try:
        corpo = resposta.json()
    except Exception:
        return ""
    if not isinstance(corpo, dict):
        return ""
    return f"{corpo.get('code') or ''} {str(corpo.get('message') or '')[:200]}".strip()


def _registrar_imagem_no_banco(token: str, modelo: str, usage, prompt: str) -> None:
    """Grava o consumo de /gerar-imagem no banco, como o usuário do token: primeiro a linha de
    `assistente.consumo` (mesmos campos e custo de _registrar_consumo, origem nucleo-local-imagem),
    depois a de `assistente.transcricoes` com o prompt no texto (como transcricoes.jsonl faz).

    Mesma política dos registros locais: falha aqui nunca derruba a resposta — só vai para o log,
    sem prompt nem token. O cliente HTTP é o que o SDK da OpenAI já traz (httpx2 no SDK 3.x, httpx nos
    anteriores), importado aqui dentro para que nenhum problema com ele afete a subida do núcleo."""
    try:
        try:
            import httpx2 as cliente_http
        except ImportError:
            import httpx as cliente_http

        url = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
        chave_publicavel = (os.getenv("SUPABASE_CHAVE_PUBLICAVEL") or "").strip()
        if not url or not chave_publicavel:
            print(
                "[consumo-remoto] SUPABASE_URL ou SUPABASE_CHAVE_PUBLICAVEL ausente em transcritor/.env "
                "— consumo da imagem não registrado"
            )
            return
        cabecalhos = {
            "apikey": chave_publicavel,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Content-Profile": "assistente",
            "Prefer": "return=minimal",
        }

        custo_usd, campos = _calcular_custo_usd(modelo, usage)
        id_consumo = str(uuid4())
        consumo = {
            "id": id_consumo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modelo": modelo,
            "custo_usd": custo_usd,
            **campos,
            "origem": ORIGEM_IMAGEM_REMOTA,
        }
        resposta = cliente_http.post(
            f"{url}/rest/v1/consumo", json=consumo, headers=cabecalhos, timeout=TIMEOUT_REGISTRO_REMOTO_S
        )
        if resposta.status_code >= 300:
            print(
                f"[consumo-remoto] falha ao registrar o consumo da imagem (resposta segue normalmente): "
                f"HTTP {resposta.status_code} {_resumo_erro_remoto(resposta)}"
            )
            return

        if not prompt or not prompt.strip():
            return
        transcricao = {
            "id_consumo": id_consumo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modelo": modelo,
            "texto": prompt,
        }
        resposta = cliente_http.post(
            f"{url}/rest/v1/transcricoes", json=transcricao, headers=cabecalhos, timeout=TIMEOUT_REGISTRO_REMOTO_S
        )
        if resposta.status_code >= 300:
            print(
                f"[consumo-remoto] falha ao registrar o prompt da imagem (resposta segue normalmente): "
                f"HTTP {resposta.status_code} {_resumo_erro_remoto(resposta)}"
            )
    except Exception as erro:
        print(f"[consumo-remoto] falha ao registrar a imagem no banco (resposta segue normalmente): {type(erro).__name__}")


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
    except (APITimeoutError, AuthenticationError, APIConnectionError, APIStatusError) as erro:
        codigo, detail, _status_http = _erro_api_para_codigo(erro)
        yield json.dumps(
            {"tipo": "erro", "detail": detail, "codigo": codigo}, ensure_ascii=False
        ) + "\n"


@app.post("/transcrever")
async def transcrever(
    response: Response,
    audio: UploadFile = File(...),
    modelo: str = Form(MODELO_PADRAO),
    stream: bool = Form(False),
):
    if modelo not in MODELOS_PERMITIDOS:
        raise ErroNucleo(
            status_code=422,
            codigo="MODELO_INVALIDO",
            detail=f"Modelo inválido: '{modelo}'. Valores aceitos: "
            + ", ".join(MODELOS_PERMITIDOS),
        )

    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        raise ErroNucleo(
            status_code=503,
            codigo="SEM_CHAVE",
            detail="OPENAI_API_KEY não configurada — preencha transcritor/.env",
        )

    conteudo = await audio.read()
    if not conteudo:
        raise ErroNucleo(status_code=400, codigo="AUDIO_VAZIO", detail="Arquivo de áudio vazio")

    if len(conteudo) > TAMANHO_MAXIMO_AUDIO_BYTES:
        tamanho_mb = f"{len(conteudo) / (1024 * 1024):.1f}".replace(".", ",")
        limite_mb = TAMANHO_MAXIMO_AUDIO_BYTES // (1024 * 1024)
        raise ErroNucleo(
            status_code=413,
            codigo="ARQUIVO_MUITO_GRANDE",
            detail=f"Arquivo de {tamanho_mb} MB; o limite é {limite_mb} MB",
        )

    cliente = OpenAI(api_key=chave, timeout=TIMEOUT_CLIENTE_API)
    parametros_extra = {}
    if modelo in MODELOS_QUE_EXIGEM_CHUNKING:
        parametros_extra["chunking_strategy"] = "auto"

    if stream:
        return StreamingResponse(
            _gerar_eventos_transcricao_stream(
                cliente, modelo, audio.filename or "audio", conteudo, parametros_extra
            ),
            media_type="application/x-ndjson",
            headers={"X-Nucleo-Contrato": VERSAO_CONTRATO_NUCLEO},
        )

    try:
        resultado = cliente.audio.transcriptions.create(
            model=modelo,
            file=(audio.filename or "audio", conteudo),
            **parametros_extra,
        )
    except (APITimeoutError, AuthenticationError, APIConnectionError, APIStatusError) as erro:
        codigo, detail, status_http = _erro_api_para_codigo(erro)
        raise ErroNucleo(status_code=status_http, codigo=codigo, detail=detail)

    id_consumo = _registrar_consumo(modelo, resultado.usage)
    if id_consumo is not None:
        _registrar_transcricao(id_consumo, modelo, resultado.text)

    response.headers["X-Nucleo-Contrato"] = VERSAO_CONTRATO_NUCLEO
    return {"transcricao": resultado.text}


@app.post("/gerar-imagem")
async def gerar_imagem(
    request: Request,
    response: Response,
    imagens: list[UploadFile] = File(...),
    prompt: str = Form(...),
    modelo: str = Form(MODELO_IMAGEM_PADRAO),
    tamanho: str = Form("auto"),
    qualidade: str = Form("medium"),
):
    """Operação 3 (D-31, fora do plano da Fase 2): gera uma imagem nova a partir de uma ou mais
    imagens de referência e um prompt, via POST https://api.openai.com/v1/images/edits. Quem fala
    com a OpenAI é sempre o núcleo — nenhum cliente tem (nem precisa) da chave."""
    if not prompt or not prompt.strip():
        raise ErroNucleo(status_code=400, codigo="PROMPT_VAZIO", detail="O prompt não pode ficar vazio")

    if modelo not in MODELOS_IMAGEM_PERMITIDOS:
        raise ErroNucleo(
            status_code=422,
            codigo="MODELO_INVALIDO",
            detail=f"Modelo inválido: '{modelo}'. Valores aceitos: " + ", ".join(MODELOS_IMAGEM_PERMITIDOS),
        )
    if tamanho not in TAMANHOS_IMAGEM_PERMITIDOS:
        raise ErroNucleo(
            status_code=422,
            codigo="TAMANHO_INVALIDO",
            detail=f"Tamanho inválido: '{tamanho}'. Valores aceitos: " + ", ".join(TAMANHOS_IMAGEM_PERMITIDOS),
        )
    if qualidade not in QUALIDADES_IMAGEM_PERMITIDAS:
        raise ErroNucleo(
            status_code=422,
            codigo="QUALIDADE_INVALIDA",
            detail=f"Qualidade inválida: '{qualidade}'. Valores aceitos: " + ", ".join(QUALIDADES_IMAGEM_PERMITIDAS),
        )

    if not imagens:
        raise ErroNucleo(status_code=400, codigo="IMAGEM_AUSENTE", detail="Envie ao menos uma imagem de referência")
    if len(imagens) > MAX_IMAGENS_REFERENCIA:
        raise ErroNucleo(
            status_code=413,
            codigo="IMAGENS_DEMAIS",
            detail=f"No máximo {MAX_IMAGENS_REFERENCIA} imagens de referência; recebi {len(imagens)}",
        )

    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        raise ErroNucleo(
            status_code=503,
            codigo="SEM_CHAVE",
            detail="OPENAI_API_KEY não configurada — preencha transcritor/.env",
        )

    arquivos_para_api = []
    for arquivo in imagens:
        extensao = Path(arquivo.filename or "").suffix.lower()
        if extensao not in FORMATOS_IMAGEM_ACEITOS:
            raise ErroNucleo(
                status_code=415,
                codigo="FORMATO_NAO_ACEITO",
                detail=f"Formato não aceito em '{arquivo.filename}'. Use PNG, JPG ou WEBP",
            )
        conteudo = await arquivo.read()
        if not conteudo:
            raise ErroNucleo(status_code=400, codigo="IMAGEM_VAZIA", detail=f"Arquivo vazio: '{arquivo.filename}'")
        if len(conteudo) > TAMANHO_MAXIMO_IMAGEM_BYTES:
            limite_mb = TAMANHO_MAXIMO_IMAGEM_BYTES // (1024 * 1024)
            raise ErroNucleo(
                status_code=413,
                codigo="ARQUIVO_MUITO_GRANDE",
                detail=f"'{arquivo.filename}' passa de {limite_mb} MB",
            )
        arquivos_para_api.append((arquivo.filename or "imagem.png", conteudo))

    cliente = OpenAI(api_key=chave, timeout=TIMEOUT_CLIENTE_API_IMAGEM)
    try:
        resultado = cliente.images.edit(
            model=modelo,
            image=arquivos_para_api,
            prompt=prompt,
            size=tamanho,
            quality=qualidade,
            input_fidelity="high",  # são imagens de referência — a fidelidade ao que foi enviado é o ponto
            n=1,
        )
    except (APITimeoutError, AuthenticationError, APIConnectionError, APIStatusError) as erro:
        codigo, detail, status_http = _erro_api_para_codigo(erro, "o prompt e as imagens de referência enviadas")
        raise ErroNucleo(status_code=status_http, codigo=codigo, detail=detail)

    dados = resultado.data[0] if resultado.data else None
    if dados is None or not dados.b64_json:
        raise ErroNucleo(status_code=502, codigo="API_RECUSOU", detail="A API não devolveu nenhuma imagem")

    # Custo calculado uma vez, sempre — a resposta ao usuário reporta o que foi cobrado de
    # verdade, mesmo que o registro em consumo.jsonl falhe (acessório, ver _registrar_consumo).
    custo_usd, _campos = _calcular_custo_usd(modelo, resultado.usage)
    token = _token_bearer(request)
    if token:
        # Com o token do usuário: registra no banco (Etapa 4 do núcleo no Supabase), não nos .jsonl.
        _registrar_imagem_no_banco(token, modelo, resultado.usage, prompt)
    else:
        id_consumo = _registrar_consumo(modelo, resultado.usage)
        if id_consumo is not None:
            _registrar_transcricao(id_consumo, modelo, prompt)  # transcricoes.jsonl guarda o prompt no lugar do texto

    response.headers["X-Nucleo-Contrato"] = VERSAO_CONTRATO_NUCLEO
    return {
        "imagem_b64": dados.b64_json,
        "formato": resultado.output_format or "png",
        "custo_usd": custo_usd,
        "revised_prompt": dados.revised_prompt,
    }


@app.get("/tempo-real/token")
async def tempo_real_token():
    """Gera um token efêmero (client secret) para o navegador abrir uma sessão de transcrição ao
    vivo direto com a OpenAI (WebSocket), sem que a chave real da API passe pelo navegador em
    nenhum momento. O token dura poucos minutos e só serve para abrir sessões de transcrição
    (não dá acesso geral à API). Ver transcritor/README.md para o formato de uso no frontend."""
    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY não configurada — preencha transcritor/.env",
        )

    cliente = OpenAI(api_key=chave)
    try:
        resposta = cliente.realtime.client_secrets.create(
            session={
                "type": "transcription",
                "audio": {
                    "input": {
                        "transcription": {"model": MODELO_TEMPO_REAL},
                        "turn_detection": None,
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
    }


class UsageTempoReal(BaseModel):
    """Corpo esperado em POST /tempo-real/turno-concluido: o campo `usage` do evento
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


@app.post("/tempo-real/turno-concluido")
async def turno_concluido_tempo_real(usage: UsageTempoReal):
    """Registra o consumo e a transcrição de um turno concluído do modo ao vivo. O frontend chama
    isso porque, nesse modo, o navegador fala direto com a OpenAI (token efêmero) e o `usage`
    chega só lá — o backend não tem outro jeito de saber quanto foi gasto. Quando o corpo traz
    `texto`, grava também a transcrição daquele turno, ligada ao mesmo id do registro de
    consumo."""
    id_consumo = _registrar_consumo(MODELO_TEMPO_REAL, usage)
    if id_consumo is not None and usage.texto is not None:
        _registrar_transcricao(id_consumo, MODELO_TEMPO_REAL, usage.texto)
    return {"registrado": True}


@app.get("/consumo")
async def consumo(response: Response):
    response.headers["X-Nucleo-Contrato"] = VERSAO_CONTRATO_NUCLEO
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


@app.get("/favicon.ico")
async def favicon():
    return Response(content=FAVICON_ICO, media_type="image/x-icon")


# Serve o frontend como arquivo estático em http://127.0.0.1:8000/ — dá ao navegador uma origem
# HTTP estável (em vez de file://), então a permissão de microfone concedida uma vez continua
# valendo entre recarregamentos. Registrado depois de /transcrever para não conflitar com a rota
# da API.
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / "frontend", html=True),
    name="frontend",
)
