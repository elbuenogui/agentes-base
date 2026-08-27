"""Cliente mínimo da Parte A — escrito lendo só spec/contrato/NUCLEO.md.

URL base não está no contrato (ver RELATORIO.md) — usei o padrão de porta do
uvicorn (localhost:8000), confirmado por sondagem, não por leitura de código.
"""
import sys
import requests

URL_BASE = "http://localhost:8000"


def transcrever(caminho_audio: str) -> str:
    with open(caminho_audio, "rb") as f:
        resposta = requests.post(
            f"{URL_BASE}/transcrever",
            files={"audio": f},
        )

    corpo = resposta.json()

    if resposta.status_code != 200:
        codigo = corpo.get("codigo")
        if codigo == "SEM_CHAVE":
            raise RuntimeError("Núcleo sem OPENAI_API_KEY configurada — não é possível transcrever.")
        raise RuntimeError(f"Erro do núcleo ({codigo}): {corpo.get('detail')}")

    return corpo["transcricao"]


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "spec/pocs/POC-1/audio-teste.wav"
    texto = transcrever(caminho)
    print(f"Transcrição: {texto}")
