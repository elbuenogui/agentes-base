"""Testes headless da Etapa 5 — desktop no núcleo remoto, com login (plano "Núcleo centralizado no
Supabase").

Rodam sem tela, sem microfone e sem rede: `QT_QPA_PLATFORM=offscreen`, os mesmos dublês de
`keyboard`/`sounddevice` da suíte da janela, e três servidores falsos locais — o Auth do Supabase,
as funções remotas (`/functions/v1/transcrever` e `/consumo`, que só aceitam o token vigente, como o
gateway) e o núcleo local (`/transcrever`, `/consumo`, `/gerar-imagem`, que aceitam qualquer coisa).
Nada toca o `config.json`, o `app.log` nem a sessão reais: config, `%APPDATA%` e log vão para uma
pasta temporária.

O que cobre:
- migração do config antigo, preservando tudo o que o usuário configurou, com `\\n` e quebra final;
- login, sessão guardada fora do repositório e relida na abertura seguinte, "Sair da conta";
- renovação antes de expirar, renovação por `401` (uma vez, e repete), renovação recusada pedindo
  login sem perder o áudio nem o texto da caixa, e o reenvio automático depois do login;
- o cabeçalho `Authorization` nas três rotas (transcrever, consumo, gerar-imagem);
- a saída de emergência: `url_nucleo` em `http://127.0.0.1:8000` funciona sem login, como antes;
- o log sem token, senha nem e-mail.

Uso: `QT_QPA_PLATFORM=offscreen python desktop/testes_sessao.py`
"""
import io
import json
import logging
import os
import shutil
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Os servidores falsos são locais: nenhum proxy do ambiente pode se meter no caminho.
for _var in ("NO_PROXY", "no_proxy"):
    os.environ[_var] = "127.0.0.1,localhost"
PASTA_TEMP = tempfile.mkdtemp(prefix="testes_sessao_")
os.environ["APPDATA"] = os.path.join(PASTA_TEMP, "appdata")  # a sessão real nunca é tocada

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import testes_janela_compacta as base  # noqa: E402  (dublês de keyboard/sounddevice + helpers)

import numpy as np  # noqa: E402
from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit  # noqa: E402

A = base.A
A.CAMINHO_CONFIG = os.path.join(PASTA_TEMP, "config.json")

# Todo o log do app (e das bibliotecas) desta execução também vai para cá — é o que o teste de
# "nada sensível no log" lê.
LOG_CAPTURADO = io.StringIO()
# E nada desta execução vai para o desktop/app.log de verdade.
for _h in list(logging.getLogger().handlers):
    if isinstance(_h, logging.FileHandler):
        logging.getLogger().removeHandler(_h)
_manipulador = logging.StreamHandler(LOG_CAPTURADO)
_manipulador.setLevel(logging.DEBUG)
logging.getLogger().addHandler(_manipulador)
logging.getLogger().setLevel(logging.INFO)

EMAIL = "pessoa.teste@exemplo.com"
SENHA = "Senha-Secreta-123!"
esperar = base.esperar


# --- servidores falsos ---------------------------------------------------------------------------
class Estado:
    def __init__(self):
        self.lock = threading.Lock()
        self.reiniciar()

    def reiniciar(self):
        self.seq = 0
        self.access_valido = set()
        self.refresh_valido = set()
        self.expira_em_s = 3600
        self.recusar_refresh = False
        self.chamadas = []  # (servidor, caminho, authorization)
        self.logins = 0
        self.renovacoes = 0
        self.revogar_proximo_access = False
        self.todos_tokens = set()

    def emitir(self):
        with self.lock:
            self.seq += 1
            access = f"access-{self.seq}-xyz"
            refresh = f"refresh-{self.seq}-abc"
            self.access_valido = {access}
            self.refresh_valido = {refresh}
            self.todos_tokens |= {access, refresh}
            return {
                "access_token": access, "refresh_token": refresh, "token_type": "bearer",
                "expires_in": self.expira_em_s, "expires_at": int(time.time()) + self.expira_em_s,
                "user": {"id": "u-1", "email": EMAIL},
            }


ESTADO = Estado()


class _Base(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    servidor = "?"

    def log_message(self, *a):
        pass

    def _json(self, status, corpo, tipo="application/json"):
        dados = corpo if isinstance(corpo, bytes) else json.dumps(corpo).encode()
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("X-Nucleo-Contrato", "1")
        self.end_headers()
        self.wfile.write(dados)

    def _ler(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def _registrar(self):
        ESTADO.chamadas.append((self.servidor, urlparse(self.path).path, self.headers.get("Authorization")))


class ServidorSupabase(_Base):
    """Auth + as duas funções remotas (o gateway só aceita o token de acesso vigente)."""

    servidor = "remoto"

    def _autorizado(self):
        valor = self.headers.get("Authorization") or ""
        token = valor[7:] if valor.startswith("Bearer ") else ""
        return token in ESTADO.access_valido

    def do_POST(self):
        corpo = self._ler()
        url = urlparse(self.path)
        if url.path == "/auth/v1/token":
            if self.headers.get("apikey") != "chave-publica-teste":
                return self._json(401, {"message": "No API key found in request"})
            tipo = parse_qs(url.query).get("grant_type", [""])[0]
            dados = json.loads(corpo or b"{}")
            if tipo == "password":
                if dados.get("email") == EMAIL and dados.get("password") == SENHA:
                    ESTADO.logins += 1
                    return self._json(200, ESTADO.emitir())
                return self._json(400, {"code": 400, "error_code": "invalid_credentials",
                                        "msg": "Invalid login credentials"})
            if tipo == "refresh_token":
                if ESTADO.recusar_refresh or dados.get("refresh_token") not in ESTADO.refresh_valido:
                    return self._json(400, {"code": 400, "error_code": "refresh_token_not_found",
                                            "msg": "Invalid Refresh Token"})
                ESTADO.renovacoes += 1
                return self._json(200, ESTADO.emitir())
            return self._json(400, {"msg": "grant_type"})
        if url.path == "/functions/v1/transcrever":
            self._registrar()
            if ESTADO.revogar_proximo_access:
                ESTADO.revogar_proximo_access = False
                ESTADO.access_valido = set()
            if not self._autorizado():
                return self._json(401, {"code": 401, "message": "Invalid JWT"})
            if b'name="stream"\r\n\r\ntrue' in corpo:
                linhas = b'{"tipo":"delta","texto":"ola"}\n{"tipo":"final","texto":"ola remoto"}\n'
                return self._json(200, linhas, "application/x-ndjson")
            return self._json(200, {"transcricao": "ola remoto"})
        return self._json(404, {})

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/functions/v1/consumo":
            self._registrar()
            if not self._autorizado():
                return self._json(401, {"code": 401, "message": "Invalid JWT"})
            return self._json(200, {"sessao": {"requisicoes": 1, "tokens": 10, "custo_usd": 0.001},
                                    "por_dia": [], "requisicoes": []})
        return self._json(404, {})


class ServidorLocal(_Base):
    """Núcleo local: aceita com ou sem cabeçalho, nunca responde 401."""

    servidor = "local"

    def do_POST(self):
        corpo = self._ler()
        self._registrar()
        caminho = urlparse(self.path).path
        if caminho == "/transcrever":
            return self._json(200, {"transcricao": "ola local"})
        if caminho == "/gerar-imagem":
            return self._json(200, {"imagem_b64": "iVBORw0KGgo=", "formato": "png", "custo_usd": 0.01,
                                    "revised_prompt": None})
        del corpo
        return self._json(404, {})

    def do_GET(self):
        self._registrar()
        if urlparse(self.path).path == "/consumo":
            return self._json(200, {"sessao": {"requisicoes": 0, "tokens": 0, "custo_usd": 0},
                                    "por_dia": [], "requisicoes": []})
        return self._json(404, {})


def subir(classe):
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), classe)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor


SRV_REMOTO = subir(ServidorSupabase)
SRV_LOCAL = subir(ServidorLocal)
URL_SUPABASE = f"http://127.0.0.1:{SRV_REMOTO.server_port}"
URL_REMOTO = URL_SUPABASE + "/functions/v1"
URL_LOCAL = f"http://127.0.0.1:{SRV_LOCAL.server_port}"


def config_teste(url_nucleo=URL_REMOTO):
    config = dict(A.CONFIG_PADRAO)
    config.update({
        "url_nucleo": url_nucleo,
        "url_nucleo_imagem": URL_LOCAL,
        "supabase_url": URL_SUPABASE,
        "supabase_chave_publicavel": "chave-publica-teste",
        "streaming": False,
        "pasta_saida_imagens": os.path.join(PASTA_TEMP, "imagens"),
    })
    return config


def limpar_sessao():
    try:
        os.remove(A.caminho_sessao())
    except FileNotFoundError:
        pass


def esperar_ate(condicao, ms=5000):
    fim = time.monotonic() + ms / 1000
    while time.monotonic() < fim:
        if condicao():
            return True
        esperar(20)
    return condicao()


def chamadas(servidor=None, caminho=None):
    return [c for c in ESTADO.chamadas if (servidor is None or c[0] == servidor)
            and (caminho is None or c[1].endswith(caminho))]


def ultimo_auth(servidor, caminho):
    """Authorization da última chamada àquela rota — "(nenhuma chamada)" se não houve nenhuma."""
    lista = chamadas(servidor, caminho)
    return lista[-1][2] if lista else "(nenhuma chamada)"


def rodar(trabalho, sinais=("concluido", "falhou", "sessao_expirada", "sucesso")):
    """Roda um QThread de trabalho do app até ele emitir um sinal final; devolve (sinal, args)."""
    recebido = []
    for nome in sinais:
        sinal = getattr(trabalho, nome, None)
        if sinal is not None:
            sinal.connect(lambda *args, n=nome: recebido.append((n, args)))
    trabalho.start()
    esperar_ate(lambda: bool(recebido) and not trabalho.isRunning(), 8000)
    esperar(30)
    return recebido[0] if recebido else (None, ())


def wav_temporario():
    caminho = os.path.join(PASTA_TEMP, f"audio_{time.monotonic_ns()}.wav")
    with open(caminho, "wb") as f:
        f.write(b"RIFF" + b"\0" * 64)
    return caminho


# --- testes --------------------------------------------------------------------------------------
def testar_migracao_config(r):
    print("[S1] migração do config antigo")
    antigo = {
        "atalho": "shift+Ç", "url_nucleo": "http://127.0.0.1:8000", "modelo": "gpt-4o-mini-transcribe",
        "streaming": True, "dispositivo_entrada": "Microfone USB", "recortar_em_vez_de_copiar": False,
        "modelo_imagem": "gpt-image-2", "tamanho_imagem": "1024x1536", "qualidade_imagem": "low",
        "pasta_saida_imagens": "C:\\\\Users\\\\x\\\\imagens",
    }
    with open(A.CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(antigo, f, ensure_ascii=False)
    config = A.carregar_config()
    r.conferir(config["url_nucleo"] == A.URL_NUCLEO_REMOTO_PADRAO,
               f"url_nucleo vira o remoto (veio {config['url_nucleo']})")
    r.conferir(config["url_nucleo_imagem"] == "http://127.0.0.1:8000",
               f"o url_nucleo antigo vai para url_nucleo_imagem (veio {config['url_nucleo_imagem']})")
    preservados = [k for k in antigo if k != "url_nucleo" and config.get(k) != antigo[k]]
    r.conferir(not preservados, f"tudo o que o usuário configurou fica igual (mudou: {preservados})")
    r.conferir(config["supabase_url"] == A.SUPABASE_URL_PADRAO
               and config["supabase_chave_publicavel"] == A.SUPABASE_CHAVE_PUBLICAVEL_PADRAO,
               "ganha supabase_url e a chave publicável padrão")
    bruto = open(A.CAMINHO_CONFIG, "rb").read()
    r.conferir(b"\r" not in bruto and bruto.endswith(b"}\n"), "gravado com \\n e quebra de linha final")
    no_disco = json.loads(bruto)
    r.conferir(no_disco.get("url_nucleo_imagem") == "http://127.0.0.1:8000" and no_disco.get("atalho") == "shift+Ç",
               "a migração foi gravada no config.json")
    antes = bruto
    A.carregar_config()
    r.conferir(open(A.CAMINHO_CONFIG, "rb").read() == antes, "abrir de novo não migra de novo (idempotente)")

    with open(A.CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"url_nucleo": "http://127.0.0.1:8005"}, f)
    r.conferir(A.carregar_config()["url_nucleo_imagem"] == "http://127.0.0.1:8005",
               "um url_nucleo antigo fora do padrão também é levado para a imagem")

    emergencia = dict(config)
    emergencia["url_nucleo"] = "http://127.0.0.1:8000"
    A.salvar_config(emergencia)
    r.conferir(A.carregar_config()["url_nucleo"] == "http://127.0.0.1:8000",
               "config já migrado com url_nucleo local (saída de emergência) não é desfeito")
    os.remove(A.CAMINHO_CONFIG)
    r.conferir(A.carregar_config()["url_nucleo"] == A.URL_NUCLEO_REMOTO_PADRAO, "sem config.json, nasce no remoto")


def testar_sessao_login_e_disco(r):
    print("[S2] login, sessão guardada fora do repositório, sair da conta")
    ESTADO.reiniciar()
    limpar_sessao()
    config = config_teste()
    sessao = A.Sessao(config)
    r.conferir(not sessao.ativa, "sem arquivo de sessão, não há sessão")
    try:
        sessao.entrar(EMAIL, "senha-errada")
        r.conferir(False, "senha errada deveria falhar")
    except A.ErroSessao as erro:
        r.conferir(str(erro) == "E-mail ou senha incorretos.", f"senha errada: mensagem clara (veio {erro})")
    r.conferir(not os.path.exists(A.caminho_sessao()), "login recusado não grava nada")

    sessao.entrar(EMAIL, SENHA)
    caminho = A.caminho_sessao()
    r.conferir(sessao.ativa and sessao.email == EMAIL, "login certo: sessão ativa, e-mail conhecido")
    r.conferir(caminho.startswith(os.environ["APPDATA"]) and caminho.endswith(os.path.join("agentes-base", "sessao.json")),
               f"a sessão mora em %APPDATA%\\agentes-base\\sessao.json (veio {caminho})")
    raiz_repo = os.path.dirname(os.path.dirname(os.path.abspath(A.__file__)))
    r.conferir(not os.path.abspath(caminho).startswith(raiz_repo), "fora do repositório")
    bruto = open(caminho, encoding="utf-8").read()
    r.conferir(SENHA not in bruto and "password" not in bruto and "senha" not in bruto,
               "a senha nunca é gravada")
    r.conferir("refresh-1-abc" in bruto, "o token de renovação é gravado")

    outra = A.Sessao(config)
    r.conferir(outra.ativa and outra.email == EMAIL and outra.token() == "access-1-xyz",
               "abrir o app de novo reaproveita a sessão (sem pedir login e sem renovar)")
    r.conferir(ESTADO.renovacoes == 0, "token ainda válido: nenhuma renovação")

    outra.sair()
    r.conferir(not outra.ativa and not os.path.exists(caminho), "Sair da conta apaga a sessão do disco")
    try:
        outra.token()
        r.conferir(False, "sem sessão, token() deveria pedir login")
    except A.ErroSessao:
        r.conferir(True, "")


def testar_renovacao(r):
    print("[S3] renovação antes de expirar, recusada e com o Auth fora do ar")
    ESTADO.reiniciar()
    limpar_sessao()
    ESTADO.expira_em_s = 60  # abaixo da margem de RENOVAR_SESSAO_ANTES_S (120 s)
    sessao = A.Sessao(config_teste())
    sessao.entrar(EMAIL, SENHA)
    ESTADO.expira_em_s = 3600
    token = sessao.token()
    r.conferir(token == "access-2-xyz" and ESTADO.renovacoes == 1,
               f"faltando menos de {A.RENOVAR_SESSAO_ANTES_S}s, renova antes de usar (token {token}, renovações {ESTADO.renovacoes})")
    r.conferir("refresh-2-abc" in open(A.caminho_sessao(), encoding="utf-8").read(),
               "o token de renovação novo (o Supabase troca a cada uso) foi gravado")
    sessao.token()
    r.conferir(ESTADO.renovacoes == 1, "com o token novo e longe de expirar, não renova de novo")

    # Auth fora do ar: a sessão continua guardada (não é "sessão expirada")
    sessao._expira_em = time.time()  # força precisar renovar
    original = sessao._config["supabase_url"]
    sessao._config["supabase_url"] = "http://127.0.0.1:9"  # porta fechada
    try:
        sessao.token()
        r.conferir(False, "Auth inalcançável deveria dar erro de rede")
    except A.ErroRedeSessao:
        r.conferir(sessao.ativa and os.path.exists(A.caminho_sessao()),
                   "Auth fora do ar: erro de rede, e a sessão continua guardada")
    sessao._config["supabase_url"] = original

    ESTADO.recusar_refresh = True
    try:
        sessao.token()
        r.conferir(False, "renovação recusada deveria pedir login")
    except A.ErroSessao as erro:
        r.conferir(str(erro) == A.MENSAGEM_SESSAO_EXPIRADA, f"renovação recusada: '{erro}'")
    r.conferir(not sessao.ativa and not os.path.exists(A.caminho_sessao()) and sessao.email == EMAIL,
               "renovação recusada apaga a sessão, mas lembra o e-mail para o próximo login")
    ESTADO.recusar_refresh = False


def testar_cabecalho_nas_tres_rotas(r):
    print("[S4] Authorization nas três rotas; renovação por 401")
    ESTADO.reiniciar()
    limpar_sessao()
    config = config_teste()
    sessao = A.Sessao(config)
    sessao.entrar(EMAIL, SENHA)

    for streaming in (False, True):
        trabalho = A.TrabalhoTranscricao(
            url_nucleo=config["url_nucleo"], caminho_arquivo=wav_temporario(), nome_arquivo="gravacao.wav",
            modelo="gpt-4o-transcribe", streaming=streaming, texto_base="", apagar_arquivo_depois=True,
            sessao=sessao, exigir_login=A.url_exige_login(config, config["url_nucleo"]),
        )
        sinal, args = rodar(trabalho)
        r.conferir(sinal == "concluido" and args[0] == "ola remoto",
                   f"transcrever remoto ({'streaming' if streaming else 'sem streaming'}) conclui ({sinal} {args})")
    tr = chamadas("remoto", "/transcrever")
    r.conferir(len(tr) == 2 and all(c[2] == "Bearer access-1-xyz" for c in tr),
               f"POST /transcrever remoto leva Authorization: Bearer <token> ({[c[2] for c in tr]})")

    sinal, args = rodar(A.TrabalhoConsumo(config["url_nucleo"], sessao=sessao, exigir_login=True))
    r.conferir(sinal == "sucesso" and "sessao" in args[0], f"consumo remoto responde ({sinal})")
    r.conferir(ultimo_auth("remoto", "/consumo") == "Bearer access-1-xyz", "GET /consumo remoto leva o cabeçalho")

    imagem = os.path.join(PASTA_TEMP, "ref.png")
    with open(imagem, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
    trabalho = A.TrabalhoGeracaoImagem(URL_LOCAL, [imagem], "um teste", "gpt-image-1.5", "auto", "low",
                                       config["pasta_saida_imagens"], sessao=sessao,
                                       exigir_login=A.url_exige_login(config, URL_LOCAL))
    sinal, args = rodar(trabalho)
    r.conferir(sinal == "sucesso", f"gerar-imagem no núcleo local conclui ({sinal} {args})")
    r.conferir(ultimo_auth("local", "/gerar-imagem") == "Bearer access-1-xyz",
               "POST /gerar-imagem no núcleo local leva o cabeçalho (é o que manda a imagem para o banco)")
    r.conferir(not A.url_exige_login(config, URL_LOCAL) and A.url_exige_login(config, URL_REMOTO),
               "só o remoto exige login")

    # 401 no meio do uso: renova uma vez e repete
    ESTADO.chamadas.clear()
    ESTADO.revogar_proximo_access = True
    trabalho = A.TrabalhoTranscricao(
        url_nucleo=config["url_nucleo"], caminho_arquivo=wav_temporario(), nome_arquivo="gravacao.wav",
        modelo="gpt-4o-transcribe", streaming=False, texto_base="antes", apagar_arquivo_depois=True,
        sessao=sessao, exigir_login=True,
    )
    sinal, args = rodar(trabalho)
    tr = chamadas("remoto", "/transcrever")
    r.conferir(sinal == "concluido" and args[0] == "antes\nola remoto",
               f"com 401, renova e repete — e conclui ({sinal} {args})")
    r.conferir([c[2] for c in tr] == ["Bearer access-1-xyz", "Bearer access-2-xyz"] and ESTADO.renovacoes == 1,
               f"exatamente uma renovação e uma repetição ({[c[2] for c in tr]}, renovações {ESTADO.renovacoes})")

    # renovação recusada depois de um 401: sessão expirada, e o áudio fica
    ESTADO.revogar_proximo_access = True
    ESTADO.recusar_refresh = True
    audio = wav_temporario()
    trabalho = A.TrabalhoTranscricao(
        url_nucleo=config["url_nucleo"], caminho_arquivo=audio, nome_arquivo="gravacao.wav",
        modelo="gpt-4o-transcribe", streaming=False, texto_base="", apagar_arquivo_depois=True,
        sessao=sessao, exigir_login=True,
    )
    sinal, _ = rodar(trabalho)
    r.conferir(sinal == "sessao_expirada", f"renovação recusada vira 'sessão expirada' (veio {sinal})")
    r.conferir(os.path.exists(audio), "e o áudio NÃO é apagado (vai ser reenviado depois do login)")
    ESTADO.recusar_refresh = False


def testar_saida_de_emergencia(r):
    print("[S5] saída de emergência: url_nucleo no núcleo local")
    ESTADO.reiniciar()
    limpar_sessao()
    config = config_teste(url_nucleo=URL_LOCAL)
    sessao = A.Sessao(config)
    r.conferir(not A.url_exige_login(config, config["url_nucleo"]), "núcleo local não exige login")
    trabalho = A.TrabalhoTranscricao(
        url_nucleo=config["url_nucleo"], caminho_arquivo=wav_temporario(), nome_arquivo="gravacao.wav",
        modelo="gpt-4o-transcribe", streaming=False, texto_base="", apagar_arquivo_depois=True,
        sessao=sessao, exigir_login=False,
    )
    sinal, args = rodar(trabalho)
    r.conferir(sinal == "concluido" and args[0] == "ola local", f"sem login, transcreve no local ({sinal} {args})")
    r.conferir(ultimo_auth("local", "/transcrever") is None, "sem sessão, vai sem cabeçalho — exatamente como antes")
    sinal, args = rodar(A.TrabalhoConsumo(config["url_nucleo"], sessao=sessao, exigir_login=False))
    r.conferir(sinal == "sucesso" and ultimo_auth("local", "/consumo") is None, "consumo local também, sem cabeçalho")
    sessao.entrar(EMAIL, SENHA)
    rodar(A.TrabalhoTranscricao(
        url_nucleo=config["url_nucleo"], caminho_arquivo=wav_temporario(), nome_arquivo="gravacao.wav",
        modelo="gpt-4o-transcribe", streaming=False, texto_base="", apagar_arquivo_depois=True,
        sessao=sessao, exigir_login=False,
    ))
    r.conferir(ultimo_auth("local", "/transcrever") == "Bearer access-1-xyz",
               "com sessão, o local recebe o cabeçalho e ignora (responde normal)")
    ESTADO.recusar_refresh = True
    sessao._expira_em = time.time()
    sinal, args = rodar(A.TrabalhoTranscricao(
        url_nucleo=config["url_nucleo"], caminho_arquivo=wav_temporario(), nome_arquivo="gravacao.wav",
        modelo="gpt-4o-transcribe", streaming=False, texto_base="", apagar_arquivo_depois=True,
        sessao=sessao, exigir_login=False,
    ))
    r.conferir(sinal == "concluido", f"no local, sessão perdida não impede o ditado ({sinal})")
    ESTADO.recusar_refresh = False

    # a janela inteira, no local e sem sessão: não pede login
    limpar_sessao()
    j = A.JanelaDitado(config_teste(url_nucleo=URL_LOCAL))
    j.show()
    esperar(80)
    j.pedir_login_se_preciso()
    esperar(80)
    r.conferir(not j.painel_login.isVisible(), "com url_nucleo local, a janela não pede login na abertura")
    j.close()


def _gravar_e_enviar(j):
    base.mouse_no_botao(j)
    esperar(120)
    j.iniciar_gravacao()
    j._callback_audio((np.random.rand(2000, 1).astype("float32") - 0.5) * 1.2, 2000, None, None)
    esperar(60)
    j.parar_e_enviar()


def testar_janela_login_e_reenvio(r):
    print("[S6] janela: sem sessão pede login, guarda o áudio e reenvia depois de entrar")
    ESTADO.reiniciar()
    limpar_sessao()
    base.mouse_longe()
    j = A.JanelaDitado(config_teste())
    j.show()
    esperar(80)
    r.conferir(not j.painel_login.isVisible(), "montar a janela não abre o login sozinho (é o main() que pede)")
    j.pedir_login_se_preciso()
    esperar(60)
    r.conferir(j.painel_login.isVisible() and j._expandido,
               "remoto sem sessão: pedir_login_se_preciso expande a janela e mostra o login")
    r.conferir(j.painel_login.campo_senha.echoMode() == QLineEdit.Password, "a senha é mascarada")
    r.conferir(not j._pode_encolher(), "com o login aberto a janela não encolhe")
    j.keyPressEvent(_tecla_esc())
    r.conferir(not j.painel_login.isVisible(), "Esc fecha o login")

    j.caixa_texto.setPlainText("texto que já estava na caixa")
    _gravar_e_enviar(j)
    esperar_ate(lambda: j.painel_login.isVisible(), 5000)
    r.conferir(j.painel_login.isVisible(), "ditado sem sessão: o login abre")
    r.conferir(j.painel_login.rotulo_erro.text() == A.MENSAGEM_SESSAO_EXPIRADA,
               f"com o motivo escrito no painel (veio '{j.painel_login.rotulo_erro.text()}')")
    r.conferir(len(j._pendentes_login) == 1 and os.path.exists(j._pendentes_login[0][0]),
               "o áudio ficou guardado, em disco, na fila de reenvio")
    r.conferir(j.caixa_texto.toPlainText() == "texto que já estava na caixa", "o texto da caixa não foi tocado")
    r.conferir(not j.processando, "o botão volta a 'parado' (não fica girando esperando o login)")
    audio_guardado = j._pendentes_login[0][0]

    # senha errada, depois certa, pelo painel
    j.painel_login.campo_email.setText(EMAIL)
    j.painel_login.campo_senha.setText("errada")
    j.painel_login.botao_entrar.click()
    r.conferir(j.painel_login.campo_senha.text() == "", "a senha sai do campo assim que o login é disparado")
    esperar_ate(lambda: j.painel_login.rotulo_erro.text() == "E-mail ou senha incorretos.", 5000)
    r.conferir(j.painel_login.rotulo_erro.text() == "E-mail ou senha incorretos." and j.painel_login.isVisible(),
               "senha errada: o painel continua aberto, com a mensagem")
    r.conferir(len(j._pendentes_login) == 1, "e o áudio continua guardado")
    j.painel_login.campo_senha.setText(SENHA)
    j.painel_login.botao_entrar.click()
    esperar_ate(lambda: "frase" in j.caixa_texto.toPlainText() or "ola remoto" in j.caixa_texto.toPlainText(), 6000)
    r.conferir(not j.painel_login.isVisible(), "login certo fecha o painel")
    r.conferir(j.caixa_texto.toPlainText() == "texto que já estava na caixa\nola remoto",
               f"o áudio guardado foi reenviado sozinho e somado à caixa (veio {j.caixa_texto.toPlainText()!r})")
    esperar_ate(lambda: not os.path.exists(audio_guardado), 2000)
    r.conferir(not j._pendentes_login and not os.path.exists(audio_guardado),
               "fila vazia e o áudio temporário apagado depois de transcrito")
    r.conferir(ultimo_auth("remoto", "/transcrever") == "Bearer access-1-xyz", "o reenvio foi com o token novo")

    # Configurações mostra a conta; Sair da conta
    j.painel_configuracoes.mostrar()
    esperar(40)
    r.conferir(j.painel_configuracoes.rotulo_conta.text() == EMAIL, "Configurações mostra o e-mail logado")
    j.painel_configuracoes.esconder()
    itens = [acao.defaultWidget() for acao in j.menu_avancado.actions()]
    rotulos = [item.findChildren(QLabel)[-1].text() for item in itens]
    r.conferir("Sair da conta" in rotulos and rotulos.index("Sair da conta") == len(rotulos) - 2,
               f"'Sair da conta' no menu ⋮, antes de 'Sair' ({rotulos})")
    itens[rotulos.index("Sair da conta")].clicado.emit()
    esperar(40)
    r.conferir(not j.sessao.ativa and not os.path.exists(A.caminho_sessao()), "Sair da conta apaga a sessão")
    j.painel_configuracoes.atualizar_conta()
    r.conferir(j.painel_configuracoes.rotulo_conta.text() == "não conectado", "e Configurações passa a 'não conectado'")
    j.close()


def testar_janela_renovacao_recusada(r):
    print("[S7] janela: renovação recusada no meio do uso")
    ESTADO.reiniciar()
    limpar_sessao()
    base.mouse_longe()
    sessao = A.Sessao(config_teste())
    sessao.entrar(EMAIL, SENHA)
    j = A.JanelaDitado(config_teste())
    j.show()
    esperar(80)
    r.conferir(j.sessao.ativa, "a janela abre com a sessão guardada, sem pedir login")
    j.pedir_login_se_preciso()
    esperar(40)
    r.conferir(not j.painel_login.isVisible(), "com sessão, a abertura não pede login")
    j.caixa_texto.setPlainText("rascunho")
    ESTADO.revogar_proximo_access = True
    ESTADO.recusar_refresh = True
    _gravar_e_enviar(j)
    esperar_ate(lambda: j.painel_login.isVisible(), 5000)
    r.conferir(j.painel_login.isVisible() and len(j._pendentes_login) == 1,
               "401 + renovação recusada: pede login e guarda o áudio")
    r.conferir(j.caixa_texto.toPlainText() == "rascunho", "o rascunho da caixa continua lá")
    r.conferir(j.painel_login.campo_email.text() == EMAIL, "o e-mail já vem preenchido")
    ESTADO.recusar_refresh = False
    j.painel_login.campo_senha.setText(SENHA)
    j.painel_login.botao_entrar.click()
    esperar_ate(lambda: "ola remoto" in j.caixa_texto.toPlainText(), 6000)
    r.conferir(j.caixa_texto.toPlainText() == "rascunho\nola remoto", "depois do login, o ditado chega na caixa")

    # consumo com sessão expirada: mensagem no painel e login na janela de ditado
    j.sessao.sair()
    j.painel_consumo.mostrar()
    esperar_ate(lambda: j.painel_login.isVisible() and j.painel_consumo.rotulo_erro.isVisible(), 5000)
    r.conferir(A.MENSAGEM_SESSAO_EXPIRADA in j.painel_consumo.rotulo_erro.text(),
               f"Consumo sem sessão mostra 'sessão expirada' (veio '{j.painel_consumo.rotulo_erro.text()}')")
    r.conferir(j.painel_login.isVisible(), "e o login abre na janela de ditado")
    j.painel_login.campo_senha.setText(SENHA)
    j.painel_login.botao_entrar.click()
    esperar_ate(lambda: not j.painel_consumo.rotulo_erro.isVisible() and not j.painel_consumo.rotulo_carregando.isVisible(), 6000)
    r.conferir(not j.painel_consumo.rotulo_erro.isVisible(), "depois do login, o Consumo recarrega sozinho")
    r.conferir(ultimo_auth("remoto", "/consumo") == f"Bearer access-{ESTADO.seq}-xyz", "com o token novo")
    j.painel_consumo.esconder()
    j.close()


def _tecla_esc():
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent
    return QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)


def testar_log_limpo(r):
    print("[S8] nada sensível no log")
    for handler in logging.getLogger().handlers:
        handler.flush()
    capturado = LOG_CAPTURADO.getvalue()
    tokens = sorted(t for t in ESTADO.todos_tokens if t in capturado)
    r.conferir(bool(capturado.strip()), f"o log capturou eventos ({capturado.count(chr(10))} linhas)")
    r.conferir("sessao: login ok" in capturado and "sessao: renovada" in capturado,
               "os eventos de sessão aparecem no log (sem dados)")
    r.conferir(not tokens, f"nenhum token no log (achados: {tokens})")
    r.conferir(SENHA not in capturado and "errada" not in capturado, "nenhuma senha no log")
    r.conferir(EMAIL not in capturado and "pessoa.teste" not in capturado, "nenhum e-mail no log")
    r.conferir("chave-publica-teste" not in capturado, "nem a chave publicável")


def main():
    app = QApplication(sys.argv)
    del app
    r = base.Resultado()
    filtros = [a for a in sys.argv[1:] if not a.startswith("-")]
    try:
        for teste in (
            testar_migracao_config,
            testar_sessao_login_e_disco,
            testar_renovacao,
            testar_cabecalho_nas_tres_rotas,
            testar_saida_de_emergencia,
            testar_janela_login_e_reenvio,
            testar_janela_renovacao_recusada,
            testar_log_limpo,  # por último: lê o log de tudo o que rodou antes
        ):
            if filtros and not any(f in teste.__name__ for f in filtros):
                continue
            teste(r)
    finally:
        SRV_REMOTO.shutdown()
        SRV_LOCAL.shutdown()
        shutil.rmtree(PASTA_TEMP, ignore_errors=True)
    print(f"\n{r.ok} verificações passaram, {len(r.falhas)} falharam")
    for f in r.falhas:
        print(" -", f)
    return 1 if r.falhas else 0


if __name__ == "__main__":
    sys.exit(main())
