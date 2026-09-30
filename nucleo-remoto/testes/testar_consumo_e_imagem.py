"""Teste real da Etapa 4 (consumo remoto e imagem registrando no banco), rodado no Windows do usuário.

Pede e-mail e senha, faz login no Auth do projeto e roda cinco passos:
  1. GET /consumo remoto sem token                 -> 401
  2. GET /consumo remoto com token                 -> 200, forma do contrato, nº de requisicoes e soma
     de custo_usd iguais ao que a API de dados conta em assistente.consumo
  3. sobe um SEGUNDO núcleo local na porta 8001 (o da 8000, em uso, não é tocado), com o main.py novo,
     e chama POST /gerar-imagem com o token — mostra o custo aproximado e pede Enter antes
  4. confere pela API: +1 consumo com origem nucleo-local-imagem e +1 transcrição ligada a ele; e que
     os .jsonl não ganharam linha de imagem
  5. encerra o núcleo da porta 8001, mesmo se algo falhar

Imprime e grava em `testar_consumo_e_imagem.log` (ao lado, acrescentado a cada execução): passo,
passou/falhou, status, tempo, contagens e custos — nunca e-mail, senha, token, prompt ou texto.
A saída do núcleo da porta 8001 vai para `nucleo_8001.log` (também ao lado; ele não loga prompt nem token).

Só biblioteca padrão.
"""

import getpass
import json
import os
import re
import socket
import struct
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
import uuid
import zlib
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Públicos por desenho (URL do projeto e chave publicável). Nenhuma chave secreta neste arquivo.
SUPABASE_URL = "https://wqoeoofhuhsdzpkdblbg.supabase.co"
CHAVE_PUBLICAVEL = "sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w"
URL_CONSUMO = f"{SUPABASE_URL}/functions/v1/consumo"

PORTA_LOCAL = 8001
URL_LOCAL = f"http://127.0.0.1:{PORTA_LOCAL}"
ORIGEM_IMAGEM = "nucleo-local-imagem"
# Mais barato aceito pelo núcleo; se a OpenAI recusar (o núcleo pede input_fidelity alta), o teste
# pergunta de novo antes de tentar o padrão da rota.
MODELO_IMAGEM = "gpt-image-1-mini"
CUSTO_APROX = "cerca de US$ 0,01 a 0,03"
MODELO_RESERVA = "gpt-image-1.5"
CUSTO_APROX_RESERVA = "cerca de US$ 0,03 a 0,09"
MODELOS_IMAGEM = {"gpt-image-2", "gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini"}
PROMPT_TESTE = "Um quadrado azul liso, sem texto, fundo branco"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
TRANSCRITOR = RAIZ / "transcritor"
ARQ_CONSUMO = TRANSCRITOR / "consumo.jsonl"
ARQ_TRANSCRICOES = TRANSCRITOR / "transcricoes.jsonl"
ARQ_LOG = AQUI / "testar_consumo_e_imagem.log"
ARQ_LOG_NUCLEO = AQUI / "nucleo_8001.log"

_log = None
_EMAIL = re.compile(r"[^\s@]+@[^\s@]+")
# Para 127.0.0.1, nunca passar por proxy do sistema.
_local = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def saida(*partes):
    linha = " ".join(str(p) for p in partes)
    print(linha, flush=True)
    if _log:
        _log.write(_EMAIL.sub("<e-mail omitido>", linha) + "\n")
        _log.flush()


def requisitar(url, metodo="GET", corpo=None, cabecalhos=None, prazo=60, local=False):
    """Devolve (status, cabeçalhos, corpo_bytes, segundos). Erro HTTP também volta como resposta."""
    req = urllib.request.Request(url, data=corpo, method=metodo, headers=cabecalhos or {})
    abrir = _local.open if local else urllib.request.urlopen
    inicio = time.monotonic()
    try:
        with abrir(req, timeout=prazo) as resp:
            return resp.status, resp.headers, resp.read(), time.monotonic() - inicio
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read(), time.monotonic() - inicio


def resumo_erro(corpo):
    """Só código e mensagem curta (os erros destas rotas não carregam prompt nem texto)."""
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


def cab_api(token):
    return {"apikey": CHAVE_PUBLICAVEL, "Authorization": f"Bearer {token}", "Accept-Profile": "assistente"}


def contar(token, caminho):
    """Conta as próprias linhas (RLS) pela API de dados, sem baixá-las."""
    st, cab, resp, _ = requisitar(
        f"{SUPABASE_URL}/rest/v1/{caminho}", "HEAD", None, {**cab_api(token), "Prefer": "count=exact"})
    total = (cab.get("Content-Range") or "").split("/")[-1]
    if st not in (200, 206) or not total.isdigit():
        raise RuntimeError(f"contagem de {caminho.split('?')[0]} falhou: HTTP {st}")
    return int(total)


def soma_custo_api(token):
    """Soma exata de custo_usd das próprias linhas, lendo em páginas de 1000 (limite da API)."""
    soma, lidas, inicio = Decimal(0), 0, 0
    while True:
        st, _, resp, _ = requisitar(
            f"{SUPABASE_URL}/rest/v1/consumo?select=custo_usd&order=id.asc&limit=1000&offset={inicio}",
            "GET", None, cab_api(token))
        if st != 200:
            raise RuntimeError(f"leitura de custo_usd falhou: HTTP {st} {resumo_erro(resp)}")
        pagina = json.loads(resp, parse_float=Decimal)
        soma += sum((Decimal(str(l["custo_usd"] or 0)) for l in pagina), Decimal(0))
        lidas += len(pagina)
        if len(pagina) < 1000:
            return soma, lidas
        inicio += 1000


def contagens_imagem(token):
    return {
        "consumo_imagem": contar(token, f"consumo?select=id&origem=eq.{ORIGEM_IMAGEM}"),
        "transcricoes_imagem": contar(
            token, f"transcricoes?select=id,consumo!inner(origem)&consumo.origem=eq.{ORIGEM_IMAGEM}"),
        "transcricoes_total": contar(token, "transcricoes?select=id"),
    }


def linhas_de_imagem_nos_jsonl():
    """Linhas cujo modelo é de imagem, em cada .jsonl — o núcleo da 8000 pode gravar transcrições
    durante o teste, então só as de imagem contam para a conferência."""
    resultado = {}
    for nome, arq in (("consumo.jsonl", ARQ_CONSUMO), ("transcricoes.jsonl", ARQ_TRANSCRICOES)):
        total = imagem = 0
        if arq.is_file():
            with open(arq, encoding="utf-8") as f:
                for linha in f:
                    if not linha.strip():
                        continue
                    total += 1
                    try:
                        if json.loads(linha).get("modelo") in MODELOS_IMAGEM:
                            imagem += 1
                    except ValueError:
                        pass
        resultado[nome] = {"linhas": total, "de_imagem": imagem}
    return resultado


def png_pequeno(lado=64, cor=(40, 90, 200)):
    """PNG liso gerado aqui mesmo (referência mínima, para o custo de entrada ficar baixo)."""
    bruto = b"".join(b"\x00" + bytes(cor) * lado for _ in range(lado))

    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", lado, lado, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(bruto)) + bloco(b"IEND", b""))


def multipart(campos, arquivos):
    fronteira = uuid.uuid4().hex
    partes = [f'--{fronteira}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
              for k, v in campos.items()]
    for campo, nome, tipo, dados in arquivos:
        partes.append((f'--{fronteira}\r\nContent-Disposition: form-data; name="{campo}"; filename="{nome}"\r\n'
                       f"Content-Type: {tipo}\r\n\r\n").encode() + dados + b"\r\n")
    partes.append(f"--{fronteira}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={fronteira}"


def porta_ocupada(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", porta)) == 0


def python_do_transcritor():
    for candidato in (TRANSCRITOR / ".venv" / "Scripts" / "python.exe", TRANSCRITOR / ".venv" / "bin" / "python"):
        if candidato.is_file():
            return str(candidato)
    return None


RESULTADOS = []


def registrar_passo(numero, nome, passou, status, segundos, extra=""):
    RESULTADOS.append(passou)
    rotulo = {True: "PASSOU", False: "FALHOU", None: "PULADO"}[passou]
    saida(f"passo {numero} — {nome}: {rotulo} | status {status} | {segundos:.1f} s{' | ' + extra if extra else ''}")


def passo_1():
    st, cab, resp, seg = requisitar(URL_CONSUMO)
    registrar_passo(1, "GET /consumo remoto sem token -> 401", st == 401, st, seg, resumo_erro(resp))


def passo_2(token):
    st, cab, resp, seg = requisitar(URL_CONSUMO, cabecalhos={"apikey": CHAVE_PUBLICAVEL, "Authorization": f"Bearer {token}"},
                                    prazo=120)
    if st != 200:
        registrar_passo(2, "GET /consumo remoto com token -> 200", False, st, seg, resumo_erro(resp))
        return
    d = json.loads(resp, parse_float=Decimal)
    problemas = []
    if cab.get("X-Nucleo-Contrato") != "2":
        problemas.append(f"X-Nucleo-Contrato={cab.get('X-Nucleo-Contrato')}")
    if sorted(d) != ["por_dia", "requisicoes", "sessao"]:
        problemas.append(f"chaves {sorted(d)}")
    if sorted(d.get("sessao") or {}) != ["custo_usd", "requisicoes", "tokens"]:
        problemas.append("forma de sessao")
    reqs = d.get("requisicoes") or []
    dias = d.get("por_dia") or []
    if any(sorted(r) != ["custo_usd", "id", "modelo", "texto", "timestamp"] for r in reqs):
        problemas.append("forma de requisicoes")
    if any(sorted(x) != ["custo_usd", "data", "requisicoes", "tokens"] for x in dias):
        problemas.append("forma de por_dia")
    total_api = contar(token, "consumo?select=id")
    soma_api, _ = soma_custo_api(token)
    soma_funcao = sum((Decimal(str(r.get("custo_usd") or 0)) for r in reqs), Decimal(0))
    soma_dias = sum(int(x.get("requisicoes") or 0) for x in dias)
    if len(reqs) != total_api:
        problemas.append(f"requisicoes {len(reqs)} != {total_api} na API")
    if soma_dias != total_api:
        problemas.append(f"soma de por_dia {soma_dias} != {total_api}")
    if abs(soma_funcao - soma_api) > Decimal("0.000000001"):
        problemas.append("soma de custo_usd diferente")
    com_texto = sum(1 for r in reqs if r.get("texto"))
    extra = (f"{len(reqs)} requisicoes (API: {total_api}) | {len(dias)} dias | soma custo_usd função "
             f"{soma_funcao:.10f} x API {soma_api:.10f} | {com_texto} com texto | sessao de hoje: "
             f"{d['sessao'].get('requisicoes')} req, US$ {Decimal(str(d['sessao'].get('custo_usd') or 0)):.6f}")
    if problemas:
        extra += " | PROBLEMAS: " + "; ".join(problemas)
    registrar_passo(2, "GET /consumo remoto com token -> 200 e totais batem", not problemas, st, seg, extra)


def chamar_gerar_imagem(token, modelo):
    corpo, ctype = multipart(
        {"prompt": PROMPT_TESTE, "modelo": modelo, "tamanho": "1024x1024", "qualidade": "low"},
        [("imagens", "referencia.png", "image/png", png_pequeno())],
    )
    return requisitar(f"{URL_LOCAL}/gerar-imagem", "POST", corpo,
                      {"Content-Type": ctype, "Authorization": f"Bearer {token}"}, prazo=330, local=True)


def passos_3_a_5(token):
    processo = None
    log_nucleo = None
    try:
        if porta_ocupada(PORTA_LOCAL):
            registrar_passo(3, "segundo núcleo na porta 8001", False, "-", 0,
                            "a porta 8001 já está em uso; feche o que estiver nela e rode de novo")
            registrar_passo(4, "imagem no banco e não nos .jsonl", None, "-", 0, "depende do passo 3")
            return
        python = python_do_transcritor()
        if not python:
            registrar_passo(3, "segundo núcleo na porta 8001", False, "-", 0,
                            "transcritor\\.venv não encontrado")
            registrar_passo(4, "imagem no banco e não nos .jsonl", None, "-", 0, "depende do passo 3")
            return

        ambiente = dict(os.environ)
        ambiente["SUPABASE_URL"] = SUPABASE_URL          # o .env real não precisa ter estes dois
        ambiente["SUPABASE_CHAVE_PUBLICAVEL"] = CHAVE_PUBLICAVEL
        log_nucleo = open(ARQ_LOG_NUCLEO, "a", encoding="utf-8")
        log_nucleo.write(f"\n===== {datetime.now().isoformat(timespec='seconds')} =====\n")
        log_nucleo.flush()
        inicio = time.monotonic()
        processo = subprocess.Popen(
            [python, "-m", "uvicorn", "main:app", "--app-dir", "backend",
             "--host", "127.0.0.1", "--port", str(PORTA_LOCAL)],
            cwd=str(TRANSCRITOR), env=ambiente, stdout=log_nucleo, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        pronto = False
        while time.monotonic() - inicio < 60 and processo.poll() is None:
            try:
                st, _, _, _ = requisitar(f"{URL_LOCAL}/favicon.ico", prazo=2, local=True)
                if st == 200:
                    pronto = True
                    break
            except (urllib.error.URLError, OSError):
                pass
            time.sleep(0.5)
        if not pronto:
            registrar_passo(3, "segundo núcleo na porta 8001", False, "-", time.monotonic() - inicio,
                            f"não respondeu em 60 s (veja {ARQ_LOG_NUCLEO.name})")
            registrar_passo(4, "imagem no banco e não nos .jsonl", None, "-", 0, "depende do passo 3")
            return
        saida(f"Núcleo da porta 8001 respondeu em {time.monotonic() - inicio:.1f} s.")

        antes_banco = contagens_imagem(token)
        antes_jsonl = linhas_de_imagem_nos_jsonl()
        saida(f"Antes — banco: {json.dumps(antes_banco)} | jsonl: {json.dumps(antes_jsonl)}")

        saida(f"\nO passo 3 gera UMA imagem de verdade: {MODELO_IMAGEM}, qualidade low, 1024x1024, "
              f"referência de 64x64 — custo aproximado {CUSTO_APROX}.")
        if input("Enter para seguir (ou digite n para pular): ").strip().lower().startswith("n"):
            registrar_passo(3, "POST /gerar-imagem com token na porta 8001", None, "-", 0, "pulado pelo usuário")
            registrar_passo(4, "imagem no banco e não nos .jsonl", None, "-", 0, "depende do passo 3")
            return

        modelo = MODELO_IMAGEM
        st, cab, resp, seg = chamar_gerar_imagem(token, modelo)
        if st == 502 and b"API_RECUSOU" in resp:
            saida(f"A OpenAI recusou {modelo} ({resumo_erro(resp)}) — recusa não gera cobrança.")
            saida(f"Posso tentar {MODELO_RESERVA} (padrão da rota), custo aproximado {CUSTO_APROX_RESERVA}.")
            if not input("Enter para tentar (ou digite n para parar): ").strip().lower().startswith("n"):
                modelo = MODELO_RESERVA
                st, cab, resp, seg = chamar_gerar_imagem(token, modelo)

        ok3 = False
        extra = f"modelo {modelo}"
        if st == 200:
            try:
                d = json.loads(resp)
                ok3 = bool(d.get("imagem_b64"))
                extra += (f" | imagem_b64 com {len(d.get('imagem_b64') or '')} caracteres | formato "
                          f"{d.get('formato')} | custo_usd {d.get('custo_usd')} | X-Nucleo-Contrato="
                          f"{cab.get('X-Nucleo-Contrato')}")
            except ValueError:
                extra += " | resposta não-JSON"
        else:
            extra += " | " + resumo_erro(resp)
        registrar_passo(3, "POST /gerar-imagem com token na porta 8001 -> 200", ok3, st, seg, extra)
        if not ok3:
            registrar_passo(4, "imagem no banco e não nos .jsonl", None, "-", 0, "depende do passo 3")
            return

        inicio4 = time.monotonic()
        depois_banco = contagens_imagem(token)
        depois_jsonl = linhas_de_imagem_nos_jsonl()
        saida(f"Depois — banco: {json.dumps(depois_banco)} | jsonl: {json.dumps(depois_jsonl)}")
        dif_banco = {k: depois_banco[k] - antes_banco[k] for k in antes_banco}
        dif_jsonl_imagem = {k: depois_jsonl[k]["de_imagem"] - antes_jsonl[k]["de_imagem"] for k in antes_jsonl}
        dif_jsonl_total = {k: depois_jsonl[k]["linhas"] - antes_jsonl[k]["linhas"] for k in antes_jsonl}
        ok4 = all(v == 1 for v in dif_banco.values()) and all(v == 0 for v in dif_jsonl_imagem.values())
        registrar_passo(4, "+1 consumo nucleo-local-imagem e +1 transcrição no banco; nada de imagem nos .jsonl",
                        ok4, "-", time.monotonic() - inicio4,
                        f"banco {json.dumps(dif_banco)} | jsonl de imagem {json.dumps(dif_jsonl_imagem)} | "
                        f"jsonl no total (inclui o uso normal da porta 8000) {json.dumps(dif_jsonl_total)}")
    finally:
        if processo is not None:
            inicio5 = time.monotonic()
            if processo.poll() is None:
                processo.terminate()
                try:
                    processo.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    processo.kill()
                    processo.wait(timeout=15)
            time.sleep(0.5)
            livre = not porta_ocupada(PORTA_LOCAL)
            registrar_passo(5, "núcleo da porta 8001 encerrado", processo.poll() is not None and livre, "-",
                            time.monotonic() - inicio5, f"código de saída {processo.poll()} | porta 8001 livre: {livre}")
        if log_nucleo is not None:
            log_nucleo.close()


def main():
    saida(f"Função: {URL_CONSUMO} | segundo núcleo: {URL_LOCAL}")
    email = input("E-mail do Supabase: ").strip()
    senha = getpass.getpass("Senha (não aparece na tela): ")
    try:
        token = login(email, senha)
    finally:
        senha = None
    saida("Login ok.")

    passo_1()
    passo_2(token)
    passos_3_a_5(token)

    passou = sum(1 for r in RESULTADOS if r is True)
    saida(f"\nResultado: {passou} de {len(RESULTADOS)} passos passaram.")
    return 0 if all(r is True for r in RESULTADOS) else 1


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
