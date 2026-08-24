"""Harness de validação do protocolo de tempo real, sem navegador/microfone.

Reimplementação em Python, fiel ao protocolo, da lógica de fechamento/corte de segurança/gate de
silêncio do `frontend/index.html` (ver PROXIMA_TAREFA.md, Etapa 1) — usada para validar contra a
API real da OpenAI o que um harness sem navegador/microfone consegue validar: timing de corte de
segurança, a corrida do fechamento (commit periódico + commit final em voo ao mesmo tempo) e o
efeito do gate de silêncio no volume de bytes enviado. NÃO valida o JavaScript em si (é outra
linguagem) nem qualidade de transcrição de fala real (usa tom sintético, não voz) — isso continua
exigindo teste manual no navegador com microfone real, fora do alcance deste agente.

Uso: .venv\\Scripts\\python.exe teste_tempo_real.py <cenario>
Cenários: silencio | fala_com_pausas | corte_seguranca | corrida_dois_commits
"""
import asyncio
import json
import math
import struct
import sys
import time
import urllib.request

import websockets

RAIZ = "http://127.0.0.1:8000"
TAXA = 24000
CHUNK_MS = 100
CHUNK_AMOSTRAS = TAXA * CHUNK_MS // 1000
LIMIAR_SILENCIO = 0.02
MIN_BYTES_COMMIT = 4800


def obter_token():
    with urllib.request.urlopen(RAIZ + "/tempo-real/token", timeout=10) as resp:
        return json.loads(resp.read())["client_secret"]


def gerar_tom(n_amostras, amplitude=0.3, freq=220, fase0=0.0):
    """PCM16 little-endian de um tom senoidal (substituto sintético de fala — sem semântica, só
    energia acima do limiar de silêncio)."""
    amostras = bytearray()
    fase = fase0
    incr = 2 * math.pi * freq / TAXA
    for _ in range(n_amostras):
        v = int(max(-1, min(1, amplitude * math.sin(fase))) * 32767)
        amostras += struct.pack("<h", v)
        fase += incr
    return bytes(amostras), fase


def gerar_silencio(n_amostras):
    return b"\x00\x00" * n_amostras


def pico_amplitude_pcm16(pcm_bytes):
    if not pcm_bytes:
        return 0.0
    amostras = struct.unpack("<%dh" % (len(pcm_bytes) // 2), pcm_bytes)
    return max(abs(a) for a in amostras) / 32768.0


class SessaoTempoReal:
    """Espelha bytesDesdeUltimoCommitTempoReal / commitsPendentesTempoReal / o gate de hangover e
    a sequência pararGravacaoTempoReal -> (espera commits pendentes) -> finalizarFechamentoTempoReal
    do index.html, para exercitar o mesmo protocolo contra o servidor real."""

    def __init__(self, nome, commit_interval_s=2.0, safety_limit_s=None, hangover_s=2.0):
        self.nome = nome
        self.commit_interval_s = commit_interval_s
        self.safety_limit_s = safety_limit_s
        self.hangover_s = hangover_s
        self.ws = None
        self.bytes_desde_commit = 0
        self.commits_pendentes = 0
        self.fim_hangover = 0.0
        self.fechando = False
        self.completed_ids = []
        self.erros = []
        self.bytes_totais_enviados = 0
        self.log = []

    def registrar(self, msg):
        self.log.append(f"[{time.monotonic():.2f}] {msg}")
        print(f"  [{self.nome}] {msg}")

    async def conectar(self):
        token = obter_token()
        self.ws = await websockets.connect(
            "wss://api.openai.com/v1/realtime",
            subprotocols=["realtime", "openai-insecure-api-key." + token],
        )
        self.registrar("conectado")

    async def enviar_chunk(self, pcm_bytes, forcar_envio=False):
        agora = time.monotonic()
        pico = pico_amplitude_pcm16(pcm_bytes)
        if pico >= LIMIAR_SILENCIO:
            self.fim_hangover = agora + self.hangover_s
        se_envia = forcar_envio or agora <= self.fim_hangover
        if not se_envia:
            return False
        import base64
        await self.ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(pcm_bytes).decode("ascii"),
        }))
        self.bytes_desde_commit += len(pcm_bytes)
        self.bytes_totais_enviados += len(pcm_bytes)
        return True

    async def commit_periodico_loop(self):
        try:
            while True:
                await asyncio.sleep(self.commit_interval_s)
                if self.bytes_desde_commit >= MIN_BYTES_COMMIT:
                    await self.ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                    self.bytes_desde_commit = 0
                    self.commits_pendentes += 1
                    self.registrar(f"commit periódico enviado (pendentes={self.commits_pendentes})")
        except asyncio.CancelledError:
            pass

    async def receptor_loop(self):
        try:
            async for bruto in self.ws:
                dado = json.loads(bruto)
                tipo = dado.get("type")
                if tipo == "conversation.item.input_audio_transcription.completed":
                    self.commits_pendentes = max(0, self.commits_pendentes - 1)
                    transcript = dado.get("transcript", "")
                    usage = dado.get("usage")
                    self.completed_ids.append(dado.get("item_id"))
                    self.registrar(
                        f"completed recebido (pendentes restantes={self.commits_pendentes}, "
                        f"usage={usage}, transcript={transcript!r})"
                    )
                    if usage:
                        _reportar_consumo(usage, transcript)
                elif tipo == "error":
                    self.erros.append(dado)
                    self.registrar(f"ERRO do servidor: {dado}")
        except websockets.exceptions.ConnectionClosed:
            pass

    async def parar(self, motivo="manual"):
        """Espelha pararGravacaoTempoReal + finalizarFechamentoTempoReal, já com a correção do
        item 3: entra na espera sempre que commits_pendentes > 0, não só quando há commit final."""
        self.fechando = True
        pode_comitar_final = self.bytes_desde_commit >= MIN_BYTES_COMMIT
        if pode_comitar_final:
            await self.ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
            self.commits_pendentes += 1
            self.registrar(f"commit final enviado (pendentes={self.commits_pendentes}), motivo={motivo}")
        self.bytes_desde_commit = 0

        if self.commits_pendentes > 0:
            self.registrar(f"aguardando {self.commits_pendentes} commit(s) pendente(s)…")
            prazo = time.monotonic() + 5.0
            while self.commits_pendentes > 0 and time.monotonic() < prazo:
                await asyncio.sleep(0.05)
            if self.commits_pendentes > 0:
                self.registrar("TIMEOUT esperando commit pendente — fechando mesmo assim")
            else:
                self.registrar("todos os commits pendentes confirmados antes de fechar")
        await self.ws.close()
        self.registrar("conexão fechada")


def _reportar_consumo(usage, texto):
    import urllib.request as ur
    corpo = json.dumps({**usage, "texto": texto or None}).encode("utf-8")
    req = ur.Request(RAIZ + "/consumo/tempo-real", data=corpo, headers={"Content-Type": "application/json"})
    try:
        ur.urlopen(req, timeout=5).read()
    except Exception as e:
        print(f"  [aviso] falha ao reportar consumo: {e}")


def ler_jsonl(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except FileNotFoundError:
        return []


CONSUMO_PATH = "c:/Users/Guilherme Bueno/Desktop/projetinhos/agentes-base/transcritor/consumo.jsonl"
TRANSCRICOES_PATH = "c:/Users/Guilherme Bueno/Desktop/projetinhos/agentes-base/transcritor/transcricoes.jsonl"


async def cenario_silencio():
    print("\n=== Cenário: sessão inteira em silêncio (~30s, bate com o critério de pronto) ===")
    antes = ler_jsonl(CONSUMO_PATH)
    s = SessaoTempoReal("silencio", commit_interval_s=2.0, hangover_s=2.0)
    await s.conectar()
    recv = asyncio.ensure_future(s.receptor_loop())
    commit_task = asyncio.ensure_future(s.commit_periodico_loop())
    for _ in range(300):  # 30s em blocos de 100ms
        pcm = gerar_silencio(CHUNK_AMOSTRAS)
        await s.enviar_chunk(pcm)
        await asyncio.sleep(CHUNK_MS / 1000)
    commit_task.cancel()
    await s.parar("fim do cenário silêncio")
    recv.cancel()
    depois = ler_jsonl(CONSUMO_PATH)
    print(f"  bytes totais enviados ao servidor: {s.bytes_totais_enviados} (esperado 0)")
    print(f"  commits enviados: {s.bytes_desde_commit=} pendentes finais={s.commits_pendentes}")
    print(f"  consumo.jsonl: {len(antes)} -> {len(depois)} linhas (esperado: sem mudança)")
    return s


async def cenario_fala_com_pausas():
    print("\n=== Cenário: fala sintética com pausas curtas entre 'frases' (~14s) ===")
    antes = ler_jsonl(CONSUMO_PATH)
    s = SessaoTempoReal("fala_com_pausas", commit_interval_s=6.0, hangover_s=2.0)
    await s.conectar()
    recv = asyncio.ensure_future(s.receptor_loop())
    commit_task = asyncio.ensure_future(s.commit_periodico_loop())
    fase = 0.0
    # padrão: 3s de tom, 1.2s de pausa (menor que o hangover de 2s), repetido 3x
    padrao = [("tom", 30), ("pausa", 12)] * 3
    for tipo, n_chunks in padrao:
        for _ in range(n_chunks):
            if tipo == "tom":
                pcm, fase = gerar_tom(CHUNK_AMOSTRAS, fase0=fase)
            else:
                pcm = gerar_silencio(CHUNK_AMOSTRAS)
            enviado = await s.enviar_chunk(pcm)
            if tipo == "pausa" and not enviado:
                s.registrar("AVISO: pausa curta cortou o envio antes do hangover expirar")
            await asyncio.sleep(CHUNK_MS / 1000)
    commit_task.cancel()
    await s.parar("fim do cenário fala_com_pausas")
    recv.cancel()
    depois = ler_jsonl(CONSUMO_PATH)
    print(f"  bytes totais enviados: {s.bytes_totais_enviados} (esperado > 0, cobrindo tom + pausas curtas)")
    print(f"  turnos completed recebidos: {len(s.completed_ids)}")
    print(f"  consumo.jsonl: {len(antes)} -> {len(depois)} linhas")
    return s


async def cenario_corte_seguranca():
    print("\n=== Cenário: corte de segurança por tempo (limite de teste encurtado: 8s) ===")
    antes_consumo = ler_jsonl(CONSUMO_PATH)
    antes_transc = ler_jsonl(TRANSCRICOES_PATH)
    s = SessaoTempoReal("corte_seguranca", commit_interval_s=6.0, safety_limit_s=8.0, hangover_s=2.0)
    await s.conectar()
    recv = asyncio.ensure_future(s.receptor_loop())
    commit_task = asyncio.ensure_future(s.commit_periodico_loop())
    inicio = time.monotonic()
    fase = 0.0
    cortado = False
    while True:
        decorrido = time.monotonic() - inicio
        if decorrido >= s.safety_limit_s and not cortado:
            cortado = True
            s.registrar(f"LIMITE DE SEGURANÇA atingido em {decorrido:.2f}s — acionando parar() pelo mesmo caminho normal")
            break
        pcm, fase = gerar_tom(CHUNK_AMOSTRAS, fase0=fase)
        await s.enviar_chunk(pcm)
        await asyncio.sleep(CHUNK_MS / 1000)
    commit_task.cancel()
    await s.parar("corte de segurança (mesmo caminho de pararGravacaoTempoReal)")
    recv.cancel()
    depois_consumo = ler_jsonl(CONSUMO_PATH)
    depois_transc = ler_jsonl(TRANSCRICOES_PATH)
    print(f"  turnos completed recebidos (deveria incluir o último turno em voo): {len(s.completed_ids)}")
    print(f"  consumo.jsonl: {len(antes_consumo)} -> {len(depois_consumo)} linhas")
    print(f"  transcricoes.jsonl: {len(antes_transc)} -> {len(depois_transc)} linhas")
    return s


async def cenario_corrida_dois_commits():
    print("\n=== Cenário: parar dentro de ~100ms de um commit periódico (dois commits em voo) ===")
    antes_consumo = ler_jsonl(CONSUMO_PATH)
    antes_transc = ler_jsonl(TRANSCRICOES_PATH)
    # intervalo de commit curto (1.5s) para conseguir cronometrar a parada logo depois de um commit
    s = SessaoTempoReal("corrida_dois_commits", commit_interval_s=1.5, hangover_s=2.0)
    await s.conectar()
    recv = asyncio.ensure_future(s.receptor_loop())
    fase = 0.0

    async def commit_loop_manual():
        # replica commit_periodico_loop mas devolve controle pra gente cronometrar a parada
        while True:
            await asyncio.sleep(s.commit_interval_s)
            if s.bytes_desde_commit >= MIN_BYTES_COMMIT:
                await s.ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                s.bytes_desde_commit = 0
                s.commits_pendentes += 1
                s.registrar(f"commit periódico enviado (pendentes={s.commits_pendentes}) -- vai parar em ~80ms")
                return  # sinaliza que acabou de comitar

    commit_task = asyncio.ensure_future(commit_loop_manual())
    # manda tom continuamente até o commit periódico dessa rodada disparar
    while not commit_task.done():
        pcm, fase = gerar_tom(CHUNK_AMOSTRAS, fase0=fase)
        await s.enviar_chunk(pcm)
        await asyncio.sleep(CHUNK_MS / 1000)
    # PARA IMEDIATAMENTE, sem mandar mais nenhum byte — reproduz o cenário exato do bug (item 3):
    # bytes_desde_commit == 0 logo após o commit periódico (podeComitarFinal == False), mas o
    # commit periódico que acabou de sair ainda está em voo (commits_pendentes == 1). O código
    # antigo (`podeComitarFinal && commitsPendentesTempoReal > 0`) pularia direto para
    # finalizarFechamentoTempoReal() aqui e perderia o "completed" desse commit periódico.
    s.registrar(f"parando IMEDIATAMENTE após o commit periódico — bytes_desde_commit={s.bytes_desde_commit}, commits_pendentes antes do parar()={s.commits_pendentes}")
    await s.parar("parada <100ms depois do commit periódico, sem áudio novo (bug do item 3)")
    recv.cancel()
    depois_consumo = ler_jsonl(CONSUMO_PATH)
    depois_transc = ler_jsonl(TRANSCRICOES_PATH)
    print(f"  turnos completed recebidos (esperado: 1 — só o periódico, sem commit final já que bytes_desde_commit=0): {len(s.completed_ids)}")
    print(f"  consumo.jsonl: {len(antes_consumo)} -> {len(depois_consumo)} linhas (esperado +1; +0 seria o bug do item 3 voltando)")
    print(f"  transcricoes.jsonl: {len(antes_transc)} -> {len(depois_transc)} linhas")
    return s


CENARIOS = {
    "silencio": cenario_silencio,
    "fala_com_pausas": cenario_fala_com_pausas,
    "corte_seguranca": cenario_corte_seguranca,
    "corrida_dois_commits": cenario_corrida_dois_commits,
}

if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else None
    if nome not in CENARIOS:
        print("Uso: python teste_tempo_real.py <" + "|".join(CENARIOS) + ">")
        sys.exit(1)
    asyncio.run(CENARIOS[nome]())
