"""Importa o histórico local do transcritor para o schema `assistente` do Supabase.

Lê `transcritor/consumo.jsonl` e `transcritor/transcricoes.jsonl` (caminhos relativos a este
arquivo), faz login no Auth do projeto com e-mail e senha do próprio usuário e grava pela API de
dados **como esse usuário** — sem chave de administrador. As linhas ficam com `user_id` = o usuário
logado (default `auth.uid()` da tabela) e só ele as enxerga (RLS).

Idempotente: cada linha tem um id fixo (o `id` do consumo quando existe; uuid5 determinístico nos
demais casos) e a gravação é um upsert que ignora duplicata. Rodar duas vezes não duplica nada.

Uso:
    python importar_historico.py             importa (pede e-mail e senha)
    python importar_historico.py --simular   só lê, monta os lotes e imprime os totais; sem rede

Só biblioteca padrão. Nunca imprime a senha, o token nem texto de transcrição.

A saída da tela também vai para `importar_historico.log`, ao lado deste arquivo (acrescentada a cada
execução, com data e hora), com e-mails mascarados — para ler o motivo de uma falha sem print de tela.
"""

import argparse
import getpass
import json
import re
import sys
import traceback
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Públicos por desenho (URL do projeto e chave publicável). Nenhuma chave secreta neste arquivo.
SUPABASE_URL = "https://wqoeoofhuhsdzpkdblbg.supabase.co"
CHAVE_PUBLICAVEL = "sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w"
SCHEMA = "assistente"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
ARQ_CONSUMO = RAIZ / "transcritor" / "consumo.jsonl"
ARQ_TRANSCRICOES = RAIZ / "transcritor" / "transcricoes.jsonl"
ARQ_LOG = AQUI / "importar_historico.log"

# Namespace fixo dos uuid5. Nunca mude: mudar gera ids novos e a reimportação duplicaria tudo.
NAMESPACE = uuid.UUID("5d6b0a8e-3f2c-5b1e-9a47-2c8f1e6d4b30")
ORIGEM = "importado-jsonl"
TAMANHO_LOTE = 500

CAMPOS_CONSUMO = ("timestamp", "modelo", "custo_usd", "tipo_usage",
                  "input_tokens", "output_tokens", "total_tokens", "segundos")


_log = None
_EMAIL = re.compile(r"[^\s@]+@[^\s@]+")


def abrir_log():
    """Abre o log em modo de acréscimo. Se não der (pasta só leitura, arquivo aberto), segue sem log."""
    global _log
    try:
        _log = open(ARQ_LOG, "a", encoding="utf-8")
    except OSError as e:
        print(f"(aviso: não consegui abrir {ARQ_LOG.name}: {e}; seguindo sem log)")


def saida(*partes):
    """Imprime na tela e grava no log. O log nunca recebe e-mail (mascarado), senha, token nem texto."""
    linha = " ".join(str(p) for p in partes)
    print(linha, flush=True)
    if _log:
        _log.write(_EMAIL.sub("<e-mail omitido>", linha) + "\n")
        _log.flush()


def ler_jsonl(caminho):
    """Devolve (registros, numeros_de_linhas_invalidas, linhas_vazias).

    Números decimais são lidos como o texto literal do arquivo (parse_float=str), para chegarem ao
    `numeric` do banco sem arredondamento de float e para a soma de custo ser exata.
    """
    registros, invalidas, vazias = [], [], 0
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            if not linha.strip():
                vazias += 1
                continue
            try:
                reg = json.loads(linha, parse_float=str)
            except json.JSONDecodeError:
                invalidas.append(n)
                continue
            if not isinstance(reg, dict):
                invalidas.append(n)
                continue
            registros.append((n, reg))
    return registros, invalidas, vazias


def canonico(reg):
    return json.dumps(reg, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def normalizar_uuid(valor):
    """O .jsonl guarda uuid sem hífens (uuid.hex); o banco recebe a forma canônica."""
    return str(uuid.UUID(str(valor)))


def montar_consumo(registros):
    linhas, ids, sem_id, repetidas, rejeitadas = [], set(), 0, 0, []
    soma = Decimal(0)
    for n, reg in registros:
        try:
            if reg.get("id"):
                id_ = normalizar_uuid(reg["id"])
            else:
                id_ = str(uuid.uuid5(NAMESPACE, "consumo|" + canonico(reg)))
                sem_id += 1
            custo = Decimal(str(reg["custo_usd"]))
            if not reg.get("timestamp") or not reg.get("modelo") or not reg.get("tipo_usage"):
                raise ValueError("campo obrigatório vazio")
        except (KeyError, ValueError, ArithmeticError):
            rejeitadas.append(n)
            continue
        if id_ in ids:
            repetidas += 1
            continue
        ids.add(id_)
        soma += custo
        linha = {"id": id_}
        for campo in CAMPOS_CONSUMO:
            linha[campo] = reg.get(campo)
        linha["origem"] = ORIGEM
        linhas.append(linha)
    return linhas, ids, sem_id, repetidas, rejeitadas, soma


def montar_transcricoes(registros, ids_consumo):
    linhas, ids, repetidas, rejeitadas, pendentes = [], set(), 0, [], 0
    for n, reg in registros:
        try:
            id_consumo = normalizar_uuid(reg["id_consumo"])
            if not reg.get("timestamp") or not reg.get("modelo") or reg.get("texto") is None:
                raise ValueError("campo obrigatório vazio")
        except (KeyError, ValueError, TypeError):
            rejeitadas.append(n)
            continue
        if id_consumo not in ids_consumo:
            # Consumo ainda não lido (o transcritor pode estar gravando agora). Fica para a próxima
            # execução, que é idempotente; sem isso a chave estrangeira recusaria o lote inteiro.
            pendentes += 1
            continue
        id_ = str(uuid.uuid5(NAMESPACE, "transcricao|" + id_consumo + "|" + reg["timestamp"]))
        if id_ in ids:
            repetidas += 1
            continue
        ids.add(id_)
        linhas.append({
            "id": id_,
            "id_consumo": id_consumo,
            "timestamp": reg["timestamp"],
            "modelo": reg["modelo"],
            "texto": reg["texto"],
        })
    return linhas, repetidas, rejeitadas, pendentes


def lotes(linhas):
    for i in range(0, len(linhas), TAMANHO_LOTE):
        yield linhas[i:i + TAMANHO_LOTE]


def requisicao(url, corpo, cabecalhos):
    dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=dados, method="POST", headers=cabecalhos)
    with urllib.request.urlopen(req, timeout=120) as resp:
        conteudo = resp.read()
    return json.loads(conteudo) if conteudo else None


def mensagem_de_erro(erro):
    """Só código e mensagem curta — nunca o `details`, que pode repetir a linha recusada."""
    try:
        corpo = json.loads(erro.read() or b"{}")
    except (ValueError, OSError):
        corpo = {}
    partes = [str(corpo.get(k)) for k in ("code", "error", "error_code") if corpo.get(k)]
    msg = corpo.get("message") or corpo.get("msg") or corpo.get("error_description") or ""
    return f"HTTP {erro.code} {' '.join(partes)} {str(msg)[:200]}".strip()


def login(email, senha):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    cab = {"apikey": CHAVE_PUBLICAVEL, "Content-Type": "application/json"}
    resp = requisicao(url, {"email": email, "password": senha}, cab)
    return resp["access_token"]


def gravar(tabela, linhas, token):
    """Envia em lotes, um depois do outro. Devolve (enviadas, novas)."""
    url = f"{SUPABASE_URL}/rest/v1/{tabela}?on_conflict=id&select=id"
    cab = {
        "apikey": CHAVE_PUBLICAVEL,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept-Profile": SCHEMA,
        "Content-Profile": SCHEMA,
        # Upsert que ignora duplicata (ON CONFLICT DO NOTHING); a resposta traz só as linhas novas.
        "Prefer": "resolution=ignore-duplicates,return=representation",
    }
    enviadas = novas = 0
    total = (len(linhas) + TAMANHO_LOTE - 1) // TAMANHO_LOTE
    for i, lote in enumerate(lotes(linhas), 1):
        resp = requisicao(url, lote, cab)
        enviadas += len(lote)
        novas += len(resp or [])
        saida(f"  {tabela}: lote {i}/{total} — {len(lote)} enviadas, {len(resp or [])} novas")
    return enviadas, novas


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--simular", action="store_true",
                        help="só lê e monta os lotes; não pede senha nem chama a rede")
    args = parser.parse_args()

    for arq in (ARQ_CONSUMO, ARQ_TRANSCRICOES):
        if not arq.is_file():
            saida(f"Arquivo não encontrado: {arq}")
            return 2

    reg_c, inv_c, vaz_c = ler_jsonl(ARQ_CONSUMO)
    reg_t, inv_t, vaz_t = ler_jsonl(ARQ_TRANSCRICOES)
    consumo, ids_consumo, sem_id, rep_c, rej_c, soma = montar_consumo(reg_c)
    transcricoes, rep_t, rej_t, pendentes = montar_transcricoes(reg_t, ids_consumo)

    saida(f"consumo.jsonl:      {len(reg_c)} linhas lidas "
          f"({sem_id} sem id -> uuid5; {vaz_c} vazias ignoradas; inválidas: {inv_c or 'nenhuma'}; "
          f"rejeitadas: {rej_c or 'nenhuma'}; ids repetidos: {rep_c})")
    saida(f"transcricoes.jsonl: {len(reg_t)} linhas lidas "
          f"({vaz_t} vazias ignoradas; inválidas: {inv_t or 'nenhuma'}; rejeitadas: {rej_t or 'nenhuma'}; "
          f"repetidas: {rep_t}; sem consumo correspondente, ficam para a próxima: {pendentes})")
    saida(f"A enviar: {len(consumo)} consumos em {-(-len(consumo) // TAMANHO_LOTE)} lote(s), "
          f"{len(transcricoes)} transcrições em {-(-len(transcricoes) // TAMANHO_LOTE)} lote(s)")
    saida(f"Soma de custo_usd (arquivo): {soma} (~ US$ {soma.quantize(Decimal('0.000001'))})")

    if args.simular:
        saida("Modo --simular: nada foi enviado.")
        return 0

    saida()
    email = input("E-mail do Supabase: ").strip()
    senha = getpass.getpass("Senha (não aparece na tela): ")
    try:
        token = login(email, senha)
    except urllib.error.HTTPError as e:
        saida("Falha no login:", mensagem_de_erro(e))
        saida("Confira e-mail e senha, e se o usuário foi criado com confirmação automática (README, passo 1).")
        return 1
    except urllib.error.URLError as e:
        saida("Sem conexão com o Supabase:", e.reason)
        return 1
    finally:
        senha = None
    saida("Login ok.\n")

    try:
        env_c, novas_c = gravar("consumo", consumo, token)
        env_t, novas_t = gravar("transcricoes", transcricoes, token)
    except urllib.error.HTTPError as e:
        saida("Falha ao gravar:", mensagem_de_erro(e))
        saida("Se a mensagem citar 'schema' (PGRST106), falta expor `assistente` na Data API "
              "(README, passo 3). Pode rodar de novo depois: nada duplica.")
        return 1
    except urllib.error.URLError as e:
        saida("Conexão caiu:", e.reason, "— pode rodar de novo: nada duplica.")
        return 1

    saida()
    saida(f"consumo:      {len(reg_c)} lidas, {env_c} enviadas, {novas_c} novas no banco "
          f"({env_c - novas_c} já existiam)")
    saida(f"transcricoes: {len(reg_t)} lidas, {env_t} enviadas, {novas_t} novas no banco "
          f"({env_t - novas_t} já existiam)")
    saida(f"Soma de custo_usd (arquivo): {soma}")
    return 0


def executar():
    abrir_log()
    modo = "--simular" if "--simular" in sys.argv[1:] else "importação"
    if _log:
        _log.write(f"\n===== {datetime.now().isoformat(timespec='seconds')} — {modo} — "
                   f"Python {sys.version.split()[0]} =====\n")
    try:
        codigo = main()
    except SystemExit as e:  # argparse (--help, argumento inválido)
        codigo = e.code if isinstance(e.code, int) else 0
    except KeyboardInterrupt:
        saida("Interrompido pelo usuário. Pode rodar de novo: nada duplica.")
        codigo = 130
    except Exception as e:
        # Erro inesperado: tipo e mensagem na tela; o traceback (linhas de código, sem valores de
        # variáveis) vai para o log para diagnóstico.
        saida(f"Erro inesperado: {type(e).__name__}: {str(e)[:300]}")
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
