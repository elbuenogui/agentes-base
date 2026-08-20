# Assistente de Pesquisa por Áudio — benchmark comparativo entre modelos
# Processa o mesmo áudio pelos três modelos de transcrição suportados pelo backend
# (POST /transcrever, que precisa estar rodando localmente) e grava transcrição, tempo de
# resposta e custo estimado lado a lado em transcritor/BENCHMARK.md.

import argparse
import contextlib
import json
import mimetypes
import time
import urllib.error
import urllib.request
import uuid
import wave
from pathlib import Path

URL_BACKEND = "http://127.0.0.1:8000/transcrever"

MODELOS = ("gpt-4o-transcribe", "gpt-4o-mini-transcribe", "gpt-4o-transcribe-diarize")

# Preço estimado por minuto de áudio, documentado publicamente pela OpenAI em
# https://platform.openai.com/docs/pricing (consultado em 2026-08-18). Os três modelos também
# têm preço por token (entrada/saída), mas o endpoint local não expõe a contagem de tokens da
# resposta — por isso o custo aqui é calculado pela estimativa oficial por minuto de áudio.
PRECO_POR_MINUTO_USD = {
    "gpt-4o-transcribe": 0.006,
    "gpt-4o-mini-transcribe": 0.003,
    "gpt-4o-transcribe-diarize": 0.006,
}
FONTE_PRECO = "https://platform.openai.com/docs/pricing (consultado em 2026-08-18)"


def duracao_em_minutos(caminho_audio: Path, duracao_informada_segundos: float | None) -> float:
    if duracao_informada_segundos is not None:
        return duracao_informada_segundos / 60

    if caminho_audio.suffix.lower() != ".wav":
        raise SystemExit(
            "Não foi possível calcular a duração automaticamente — só arquivos .wav são lidos "
            "diretamente. Informe a duração com --duracao-segundos <n>."
        )

    with contextlib.closing(wave.open(str(caminho_audio), "rb")) as wav:
        quadros = wav.getnframes()
        taxa = wav.getframerate()
    return (quadros / taxa) / 60


def _codificar_multipart(campos: dict, caminho_audio: Path) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    partes = []
    for nome, valor in campos.items():
        partes.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{nome}"\r\n\r\n{valor}\r\n'.encode("utf-8")
        )

    tipo_conteudo = mimetypes.guess_type(caminho_audio.name)[0] or "application/octet-stream"
    cabecalho_arquivo = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="audio"; filename="{caminho_audio.name}"\r\n'
        f"Content-Type: {tipo_conteudo}\r\n\r\n"
    ).encode("utf-8")
    corpo_arquivo = caminho_audio.read_bytes()
    rodape = f"\r\n--{boundary}--\r\n".encode("utf-8")

    corpo = b"".join(partes) + cabecalho_arquivo + corpo_arquivo + rodape
    return corpo, f"multipart/form-data; boundary={boundary}"


def transcrever(caminho_audio: Path, modelo: str) -> dict:
    corpo, content_type = _codificar_multipart({"modelo": modelo}, caminho_audio)
    requisicao = urllib.request.Request(
        URL_BACKEND, data=corpo, method="POST", headers={"Content-Type": content_type}
    )

    inicio = time.monotonic()
    try:
        with urllib.request.urlopen(requisicao, timeout=120) as resposta:
            tempo_segundos = time.monotonic() - inicio
            corpo_resposta = json.loads(resposta.read().decode("utf-8"))
            return {"transcricao": corpo_resposta.get("transcricao", ""), "tempo_segundos": tempo_segundos}
    except urllib.error.HTTPError as erro:
        tempo_segundos = time.monotonic() - inicio
        detalhe = erro.read().decode("utf-8", errors="replace")
        return {"erro": f"HTTP {erro.code} — {detalhe}", "tempo_segundos": tempo_segundos}
    except urllib.error.URLError as erro:
        return {
            "erro": f"Falha de conexão com o backend ({URL_BACKEND}): {erro.reason}. "
            "Confirme que o servidor está rodando (veja o README).",
            "tempo_segundos": time.monotonic() - inicio,
        }


def escrever_markdown(caminho_saida: Path, caminho_audio: Path, minutos: float, resultados: dict) -> None:
    linhas = [
        "# Benchmark entre modelos de transcrição",
        "",
        f"Áudio de teste: `{caminho_audio.name}` (~{minutos * 60:.1f} segundos, fala real).",
        "",
        f"Custo estimado com base no preço público por minuto de áudio documentado pela OpenAI "
        f"em {FONTE_PRECO}. Preços podem mudar — confira a página oficial antes de decisões de "
        "custo.",
        "",
        "| Modelo | Tempo de resposta | Custo estimado (US$) | Transcrição |",
        "|---|---|---|---|",
    ]
    for modelo, resultado in resultados.items():
        if "erro" in resultado:
            linhas.append(f"| `{modelo}` | — | — | **erro:** {resultado['erro']} |")
            continue
        texto = resultado["transcricao"].replace("|", "\\|").replace("\n", " ")
        linhas.append(
            f"| `{modelo}` | {resultado['tempo_segundos']:.1f}s | "
            f"US$ {resultado['custo_estimado_usd']:.5f} | {texto} |"
        )
    caminho_saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Processa um áudio pelos três modelos de transcrição e compara resultado, "
        "tempo e custo estimado. Requer o backend rodando em " + URL_BACKEND.rsplit("/", 1)[0] + "."
    )
    parser.add_argument("audio", type=Path, help="Caminho do arquivo de áudio (fala real, 1 a 5 minutos)")
    parser.add_argument(
        "--duracao-segundos",
        type=float,
        default=None,
        help="Duração do áudio em segundos — necessário se o arquivo não for .wav "
        "(usada só para o cálculo de custo)",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path(__file__).parent / "BENCHMARK.md",
        help="Arquivo Markdown onde o resultado comparativo será gravado",
    )
    args = parser.parse_args()

    if not args.audio.exists():
        raise SystemExit(f"Arquivo de áudio não encontrado: {args.audio}")

    minutos = duracao_em_minutos(args.audio, args.duracao_segundos)
    print(f"Áudio: {args.audio} (~{minutos * 60:.1f}s)")

    resultados = {}
    for modelo in MODELOS:
        print(f"Transcrevendo com {modelo}...")
        resultado = transcrever(args.audio, modelo)
        resultado["custo_estimado_usd"] = minutos * PRECO_POR_MINUTO_USD[modelo]
        resultados[modelo] = resultado
        if "erro" in resultado:
            print(f"  erro: {resultado['erro']}")
        else:
            print(f"  ok ({resultado['tempo_segundos']:.1f}s, ~US$ {resultado['custo_estimado_usd']:.5f})")

    escrever_markdown(args.saida, args.audio, minutos, resultados)
    print(f"Resultado gravado em {args.saida}")


if __name__ == "__main__":
    main()
