"""Teste real da Edge Function `transcrever` (Etapa 3), rodado no Windows do usuário.

Pede e-mail e senha, faz login no Auth do projeto e roda seis casos contra a função implantada:
  1. sem token                              -> 401
  2. fala-real.wav, sem streaming           -> 200, `transcricao` não vazia, X-Nucleo-Contrato: 2
  3. o mesmo áudio com stream=true          -> pelo menos um `delta` e um `final`
  4. modelo=gpt-4o-transcribe-diarize       -> 422 MODELO_INVALIDO
  5. áudio de 0 byte                        -> 400 AUDIO_VAZIO
  6. as próprias linhas no banco, antes e depois -> +2 em consumo (origem nucleo-remoto) e +2 em
     transcricoes ligadas a esses consumos

Imprime e grava em `testar_transcrever.log` (ao lado deste arquivo, acrescentado a cada execução):
caso, passou/falhou, status, tempo e o TAMANHO do texto — nunca o texto, e-mail, senha ou token.
Os casos 2 e 3 são chamadas pagas à OpenAI (~32 s de áudio cada, centavos de dólar).

Só biblioteca padrão.
"""

import getpass
import json
import re
import sys
import time
import traceback
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

# Públicos por desenho (URL do projeto e chave publicável). Nenhuma chave secreta neste arquivo.
SUPABASE_URL = "https://wqoeoofhuhsdzpkdblbg.supabase.co"
CHAVE_PUBLICAVEL = "sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w"
URL_FUNCAO = f"{SUPABASE_URL}/functions/v1/transcrever"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
AUDIO = RAIZ / "audio-teste" / "fala-real.wav"
ARQ_LOG = AQUI / "testar_transcrever.log"
PRAZO_S = 170  # a função tem 150 s de teto; folga para rede

_log = None
_EMAIL = re.compile(r"[^\s@]+@[^\s@]+")


def saida(*partes):
    linha = " ".join(str(p) for p in partes)
    print(linha, flush=True)
    if _log:
        _log.write(_EMAIL.sub("<e-mail omitido>", linha) + "\n")
        _log.flush()


def multipart(campos, arquivo_nome, arquivo_bytes):
    fronteira = uuid.uuid4().hex
    partes = []
    for nome, valor in campos.items():
        partes.append(
            f'--{fronteira}\r\nContent-Disposition: form-data; name="{nome}"\r\n\r\n{valor}\r\n'.encode()
        )
    partes.append(
        (f'--{fronteira}\r\nContent-Disposition: form-data; name="audio"; filename="{arquivo_nome}"\r\n'
         "Content-Type: audio/wav\r\n\r\n").encode() + arquivo_bytes + b"\r\n"
    )
    partes.append(f"--{fronteira}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={fronteira}"


def requisitar(url, metodo="GET", corpo=None, cabecalhos=None):
    """Devolve (status, cabeçalhos, corpo_bytes, segundos). Erro HTTP também volta como resposta."""
    req = urllib.request.Request(url, data=corpo, method=metodo, headers=cabecalhos or {})
    inicio = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=PRAZO_S) as resp:
            return resp.status, resp.headers, resp.read(), time.monotonic() - inicio
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read(), time.monotonic() - inicio


def resumo_erro(corpo):
    """Só código e mensagem curta do corpo de erro (nunca há texto transcrito num erro)."""
    try:
        d = json.loads(corpo or b"{}")
    except ValueError:
        return f"(corpo não-JSON, {len(corpo or b'')} bytes)"
    if not isinstance(d, dict):
        return "(corpo inesperado)"
    cod = d.get("codigo") or d.get("code") or d.get("error_code") or ""
    msg = d.get("detail") or d.get("message") or d.get("msg") or ""
    return f"{cod} {str(msg)[:160]}".strip()


def login(email, senha):
    corpo = json.dumps({"email": email, "password": senha}).encode()
    st, _, resp, _ = requisitar(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password", "POST", corpo,
        {"apikey": CHAVE_PUBLICAVEL, "Content-Type": "application/json"},
    )
    if st != 200:
        raise RuntimeError(f"login recusado: HTTP {st} {resumo_erro(resp)}")
    return json.loads(resp)["access_token"]


def contar(token, caminho):
    """Conta as próprias linhas (RLS) de um recurso do schema assistente, pela API de dados."""
    st, cab, resp, _ = requisitar(
        f"{SUPABASE_URL}/rest/v1/{caminho}", "HEAD", None,
        {"apikey": CHAVE_PUBLICAVEL, "Authorization": f"Bearer {token}",
         "Accept-Profile": "assistente", "Prefer": "count=exact"},
    )
    if st not in (200, 206):
        raise RuntimeError(f"contagem de {caminho.split('?')[0]} falhou: HTTP {st} {resumo_erro(resp)}")
    total = (cab.get("Content-Range") or "").split("/")[-1]
    if not total.isdigit():
        raise RuntimeError(f"contagem de {caminho.split('?')[0]} sem total no Content-Range")
    return int(total)


def contagens(token):
    return {
        "consumo_nucleo_remoto": contar(token, "consumo?select=id&origem=eq.nucleo-remoto"),
        "consumo_total": contar(token, "consumo?select=id"),
        "transcricoes_nucleo_remoto": contar(
            token, "transcricoes?select=id,consumo!inner(origem)&consumo.origem=eq.nucleo-remoto"),
        "transcricoes_total": contar(token, "transcricoes?select=id"),
    }


RESULTADOS = []


def registrar_caso(numero, nome, passou, status, segundos, extra=""):
    RESULTADOS.append(passou)
    saida(f"caso {numero} — {nome}: {'PASSOU' if passou else 'FALHOU'} | status {status} | "
          f"{segundos:.1f} s{' | ' + extra if extra else ''}")


def main():
    if not AUDIO.is_file():
        saida(f"Áudio de teste não encontrado: {AUDIO.name} (esperado em audio-teste/)")
        return 2
    audio = AUDIO.read_bytes()
    saida(f"Função: {URL_FUNCAO}")
    saida(f"Áudio: {AUDIO.name}, {len(audio)} bytes")

    email = input("E-mail do Supabase: ").strip()
    senha = getpass.getpass("Senha (não aparece na tela): ")
    try:
        token = login(email, senha)
    finally:
        senha = None
    saida("Login ok.")
    autenticado = {"apikey": CHAVE_PUBLICAVEL, "Authorization": f"Bearer {token}"}

    antes = contagens(token)
    saida(f"Contagem antes: {json.dumps(antes)}")

    # 1. sem token
    corpo, ctype = multipart({}, "fala-real.wav", audio)
    st, cab, resp, seg = requisitar(URL_FUNCAO, "POST", corpo, {"Content-Type": ctype})
    registrar_caso(1, "sem token -> 401", st == 401, st, seg, resumo_erro(resp))

    # 2. sem streaming
    st, cab, resp, seg = requisitar(URL_FUNCAO, "POST", corpo, {**autenticado, "Content-Type": ctype})
    tamanho = 0
    ok = False
    extra = ""
    if st == 200:
        try:
            tamanho = len(json.loads(resp).get("transcricao") or "")
        except ValueError:
            tamanho = 0
        contrato = cab.get("X-Nucleo-Contrato")
        ok = tamanho > 0 and contrato == "2"
        extra = f"transcricao com {tamanho} caracteres | X-Nucleo-Contrato={contrato}"
    else:
        extra = resumo_erro(resp)
    registrar_caso(2, "fala-real.wav sem streaming -> 200", ok, st, seg, extra)

    # 3. streaming
    corpo_s, ctype_s = multipart({"stream": "true"}, "fala-real.wav", audio)
    st, cab, resp, seg = requisitar(URL_FUNCAO, "POST", corpo_s, {**autenticado, "Content-Type": ctype_s})
    deltas, finais, tamanho_final, erros = 0, 0, 0, []
    if st == 200:
        for linha in resp.decode("utf-8", "replace").splitlines():
            if not linha.strip():
                continue
            try:
                ev = json.loads(linha)
            except ValueError:
                continue
            if ev.get("tipo") == "delta":
                deltas += 1
            elif ev.get("tipo") == "final":
                finais += 1
                tamanho_final = len(ev.get("texto") or "")
            elif ev.get("tipo") == "erro":
                erros.append(f"{ev.get('codigo')} {str(ev.get('detail'))[:160]}")
        extra = (f"{deltas} delta(s), {finais} final, texto final com {tamanho_final} caracteres | "
                 f"X-Nucleo-Contrato={cab.get('X-Nucleo-Contrato')} | Content-Type={cab.get('Content-Type')}")
        if erros:
            extra += " | evento erro: " + "; ".join(erros)
    else:
        extra = resumo_erro(resp)
    registrar_caso(3, "mesmo áudio com stream=true -> delta + final", st == 200 and deltas >= 1 and finais >= 1
                   and not erros, st, seg, extra)

    # 4. modelo diarize
    corpo_d, ctype_d = multipart({"modelo": "gpt-4o-transcribe-diarize"}, "fala-real.wav", audio)
    st, cab, resp, seg = requisitar(URL_FUNCAO, "POST", corpo_d, {**autenticado, "Content-Type": ctype_d})
    registrar_caso(4, "modelo=gpt-4o-transcribe-diarize -> 422 MODELO_INVALIDO",
                   st == 422 and b"MODELO_INVALIDO" in resp, st, seg, resumo_erro(resp))

    # 5. áudio vazio
    corpo_v, ctype_v = multipart({}, "vazio.wav", b"")
    st, cab, resp, seg = requisitar(URL_FUNCAO, "POST", corpo_v, {**autenticado, "Content-Type": ctype_v})
    registrar_caso(5, "áudio de 0 byte -> 400 AUDIO_VAZIO", st == 400 and b"AUDIO_VAZIO" in resp, st, seg,
                   resumo_erro(resp))

    # 6. contagem depois
    inicio = time.monotonic()
    depois = contagens(token)
    saida(f"Contagem depois: {json.dumps(depois)}")
    dif = {k: depois[k] - antes[k] for k in antes}
    ok6 = all(v == 2 for v in dif.values())
    registrar_caso(6, "linhas próprias no banco: +2 em cada, origem nucleo-remoto", ok6, "-",
                   time.monotonic() - inicio, f"diferenças {json.dumps(dif)}")

    passou = sum(RESULTADOS)
    saida(f"\nResultado: {passou} de {len(RESULTADOS)} casos passaram.")
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
        codigo = 130
    except Exception as e:
        saida(f"Erro: {type(e).__name__}: {str(e)[:300]}")
        if _log:
            _log.write(_EMAIL.sub("<e-mail omitido>", traceback.format_exc()))
        codigo = 1
    if _log:
        _log.write(f"----- saiu com código {codigo} -----\n")
        _log.close()
        print(f"(registro desta execução em {ARQ_LOG.name}, na mesma pasta)")
    return codigo


if __name__ == "__main__":
    sys.exit(executar())
