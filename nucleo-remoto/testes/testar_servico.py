"""Teste real da Edge Function `transcrever-servico` (serviço para projetos clientes, D-37), no Windows.

Pede a chave do serviço (`SERVICO_CHAVE_MARI`, sem eco na tela) e roda cinco casos contra a função
implantada, nesta ordem:
  1. sem `x-servico-chave`                       -> 401 CHAVE_INVALIDA
  2. chave errada                                -> 401 CHAVE_INVALIDA
  3. arquivo de 4 MB + 1 byte, gerado em memória -> 413 ARQUIVO_MUITO_GRANDE (sem custo)
  4. audio-teste/fala-real.wav                   -> 200, `transcricao` não vazia, X-Servico-Contrato: 1
     (chamada paga, centavos)
  5. teto: pausa para você criar o segredo SERVICO_TETO_DIARIO_USD = 0 no painel; manda o mesmo
     áudio e espera 429 LIMITE_DIARIO. Se vier 200 (instância ainda com o valor velho), espera 20 s
     e tenta de novo, até 3 vezes, registrando cada tentativa.
No fim pede, em destaque, que você APAGUE o segredo SERVICO_TETO_DIARIO_USD, e mostra o resumo.

Imprime e grava em `testar_servico.log` (ao lado deste arquivo, acrescentado a cada execução): caso,
passou/falhou, status, tempo e o TAMANHO do texto — nunca o texto nem a chave.

Só biblioteca padrão.
"""

import getpass
import json
import secrets
import sys
import time
import traceback
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

# Público por desenho (URL do projeto). Nenhuma chave neste arquivo.
SUPABASE_URL = "https://wqoeoofhuhsdzpkdblbg.supabase.co"
URL_FUNCAO = f"{SUPABASE_URL}/functions/v1/transcrever-servico"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
AUDIO = RAIZ / "audio-teste" / "fala-real.wav"
ARQ_LOG = AQUI / "testar_servico.log"
PRAZO_S = 170  # a função tem 150 s de teto; folga para rede
LIMITE_BYTES = 4 * 1024 * 1024
ESPERA_TETO_S = 20
NOVAS_TENTATIVAS_TETO = 3

_log = None


def saida(*partes):
    linha = " ".join(str(p) for p in partes)
    print(linha, flush=True)
    if _log:
        _log.write(linha + "\n")
        _log.flush()


def multipart(arquivo_nome, arquivo_bytes):
    fronteira = uuid.uuid4().hex
    corpo = (
        (f'--{fronteira}\r\nContent-Disposition: form-data; name="audio"; filename="{arquivo_nome}"\r\n'
         "Content-Type: audio/wav\r\n\r\n").encode()
        + arquivo_bytes
        + f"\r\n--{fronteira}--\r\n".encode()
    )
    return corpo, f"multipart/form-data; boundary={fronteira}"


def requisitar(corpo, cabecalhos):
    """Devolve (status, cabeçalhos, corpo_bytes, segundos). Erro HTTP também volta como resposta."""
    req = urllib.request.Request(URL_FUNCAO, data=corpo, method="POST", headers=cabecalhos)
    inicio = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=PRAZO_S) as resp:
            return resp.status, resp.headers, resp.read(), time.monotonic() - inicio
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read(), time.monotonic() - inicio


def codigo_de(corpo):
    try:
        d = json.loads(corpo or b"{}")
    except ValueError:
        return None
    return d.get("codigo") if isinstance(d, dict) else None


def resumo_erro(corpo):
    """Só código e mensagem curta do corpo de erro (nunca há texto transcrito num erro)."""
    try:
        d = json.loads(corpo or b"{}")
    except ValueError:
        return f"(corpo não-JSON, {len(corpo or b'')} bytes)"
    if not isinstance(d, dict):
        return "(corpo inesperado)"
    cod = d.get("codigo") or d.get("code") or ""
    msg = d.get("detail") or d.get("message") or d.get("msg") or ""
    return f"{cod} {str(msg)[:160]}".strip()


def tamanho_transcricao(corpo):
    try:
        d = json.loads(corpo)
    except ValueError:
        return 0
    return len(d.get("transcricao") or "") if isinstance(d, dict) else 0


RESULTADOS = []


def registrar_caso(numero, nome, passou, status, segundos, extra=""):
    RESULTADOS.append((numero, passou))
    saida(f"caso {numero} — {nome}: {'PASSOU' if passou else 'FALHOU'} | status {status} | "
          f"{segundos:.1f} s{' | ' + extra if extra else ''}")


def main():
    if not AUDIO.is_file():
        saida(f"Áudio de teste não encontrado: {AUDIO.name} (esperado em audio-teste/)")
        return 2
    audio = AUDIO.read_bytes()
    saida(f"Função: {URL_FUNCAO}")
    saida(f"Áudio: {AUDIO.name}, {len(audio)} bytes")

    chave = getpass.getpass("Chave do serviço (SERVICO_CHAVE_MARI; não aparece na tela): ").strip()
    if not chave:
        saida("Nenhuma chave digitada — teste cancelado.")
        return 2
    saida(f"Chave recebida ({len(chave)} caracteres).")

    corpo_audio, tipo_audio = multipart("fala-real.wav", audio)

    # 1. sem chave
    st, cab, resp, seg = requisitar(corpo_audio, {"Content-Type": tipo_audio})
    registrar_caso(1, "sem x-servico-chave -> 401 CHAVE_INVALIDA",
                   st == 401 and codigo_de(resp) == "CHAVE_INVALIDA", st, seg, resumo_erro(resp))

    # 2. chave errada (aleatória, do mesmo tamanho de uma chave de verdade)
    errada = secrets.token_urlsafe(32)
    while errada == chave:
        errada = secrets.token_urlsafe(32)
    st, cab, resp, seg = requisitar(corpo_audio, {"Content-Type": tipo_audio, "x-servico-chave": errada})
    registrar_caso(2, "chave errada -> 401 CHAVE_INVALIDA",
                   st == 401 and codigo_de(resp) == "CHAVE_INVALIDA", st, seg, resumo_erro(resp))

    autenticado = {"Content-Type": tipo_audio, "x-servico-chave": chave}

    # 3. 4 MB + 1 byte, gerado em memória
    corpo_grande, tipo_grande = multipart("grande.wav", b"\0" * (LIMITE_BYTES + 1))
    st, cab, resp, seg = requisitar(corpo_grande, {"Content-Type": tipo_grande, "x-servico-chave": chave})
    registrar_caso(3, "4 MB + 1 byte -> 413 ARQUIVO_MUITO_GRANDE",
                   st == 413 and codigo_de(resp) == "ARQUIVO_MUITO_GRANDE", st, seg, resumo_erro(resp))

    # 4. fala-real.wav (chamada paga)
    st, cab, resp, seg = requisitar(corpo_audio, autenticado)
    if st == 200:
        tamanho = tamanho_transcricao(resp)
        contrato = cab.get("X-Servico-Contrato")
        cors = cab.get("Access-Control-Allow-Origin")
        ok = tamanho > 0 and contrato == "1"
        extra = (f"transcricao com {tamanho} caracteres | X-Servico-Contrato={contrato} | "
                 f"Access-Control-Allow-Origin={cors}")
    else:
        ok = False
        extra = resumo_erro(resp)
    registrar_caso(4, "fala-real.wav -> 200", ok, st, seg, extra)

    # 5. teto do dia
    saida("")
    saida("=" * 72)
    saida("CASO 5 — agora, no painel do Supabase (Edge Functions -> Secrets), CRIE o segredo")
    saida("    SERVICO_TETO_DIARIO_USD   com o valor   0")
    saida("e salve. Depois volte aqui e tecle Enter.")
    saida("=" * 72)
    input("Enter quando o segredo estiver criado... ")
    inicio_caso = time.monotonic()
    ok5, st5, extra5 = False, "-", ""
    for tentativa in range(1, NOVAS_TENTATIVAS_TETO + 2):
        st, cab, resp, seg = requisitar(corpo_audio, autenticado)
        if st == 200:
            saida(f"    tentativa {tentativa}: status 200 em {seg:.1f} s "
                  f"(transcricao com {tamanho_transcricao(resp)} caracteres) — instância ainda sem o teto novo")
        else:
            saida(f"    tentativa {tentativa}: status {st} em {seg:.1f} s | {resumo_erro(resp)}")
        st5 = st
        if st == 429 and codigo_de(resp) == "LIMITE_DIARIO":
            ok5, extra5 = True, f"{resumo_erro(resp)} | na tentativa {tentativa}"
            break
        if st != 200:
            extra5 = f"{resumo_erro(resp)} | na tentativa {tentativa}"
            break
        if tentativa <= NOVAS_TENTATIVAS_TETO:
            saida(f"    esperando {ESPERA_TETO_S} s para tentar de novo...")
            time.sleep(ESPERA_TETO_S)
        else:
            extra5 = f"ainda 200 depois de {tentativa} tentativas"
    registrar_caso(5, "teto 0 -> 429 LIMITE_DIARIO", ok5, st5, time.monotonic() - inicio_caso, extra5)

    # 6. apagar o segredo do teto, e o resumo
    saida("")
    saida("#" * 72)
    saida("#  IMPORTANTE: no painel do Supabase (Edge Functions -> Secrets), APAGUE")
    saida("#  o segredo SERVICO_TETO_DIARIO_USD agora.")
    saida("#  Enquanto ele existir com 0, o serviço recusa toda transcrição da Mari.")
    saida("#  Sem ele, o teto volta ao padrão de US$ 1,00 por dia.")
    saida("#" * 72)

    passou = sum(1 for _, ok in RESULTADOS if ok)
    falhos = [str(n) for n, ok in RESULTADOS if not ok]
    saida(f"\nResultado: {passou} de {len(RESULTADOS)} casos passaram."
          + (f" Falharam: {', '.join(falhos)}." if falhos else ""))
    return 0 if passou == len(RESULTADOS) else 1


def executar():
    global _log
    try:
        _log = open(ARQ_LOG, "a", encoding="utf-8")
        _log.write(f"\n===== {datetime.now().isoformat(timespec='seconds')} — Python {sys.version.split()[0]} =====\n")
    except OSError as e:
        print(f"(aviso: não consegui abrir {ARQ_LOG.name}: {e}; seguindo sem log)")
    try:
        codigo = main()
    except KeyboardInterrupt:
        saida("Interrompido pelo usuário.")
        saida("Se você já criou o segredo SERVICO_TETO_DIARIO_USD, APAGUE-O no painel do Supabase.")
        codigo = 130
    except Exception as e:
        saida(f"Erro: {type(e).__name__}: {str(e)[:300]}")
        saida("Se você já criou o segredo SERVICO_TETO_DIARIO_USD, APAGUE-O no painel do Supabase.")
        if _log:
            _log.write(traceback.format_exc())
        codigo = 1
    if _log:
        _log.write(f"----- saiu com código {codigo} -----\n")
        _log.close()
        print(f"(registro desta execução em {ARQ_LOG.name}, na mesma pasta)")
    return codigo


if __name__ == "__main__":
    sys.exit(executar())
