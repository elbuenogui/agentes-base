"""App de desktop mínimo: atalho global -> grava -> transcreve -> clipboard.

Consome só o contrato em spec/contrato/NUCLEO.md. Não inseri no campo em foco
(fora de escopo, B-22) — só copia para a área de transferência e mostra numa
janela pequena.
"""
import json
import os
import queue
import tempfile
import threading
import wave

import keyboard
import numpy as np
import pyperclip
import requests
import sounddevice as sd
import tkinter as tk

CAMINHO_CONFIG = os.path.join(os.path.dirname(__file__), "config.json")
TAXA_AMOSTRAGEM = 16000
CANAIS = 1

MENSAGENS_ERRO = {
    "MODELO_INVALIDO": "Modelo de transcrição inválido — confira config.json.",
    "SEM_CHAVE": "O núcleo não tem chave da OpenAI configurada (transcritor/.env).",
    "AUDIO_VAZIO": "Gravação vazia — nada foi enviado.",
    "ARQUIVO_MUITO_GRANDE": "Gravação muito longa — acima do limite do núcleo (25 MB).",
    "FALHA_AUTENTICACAO": "Chave da OpenAI inválida no núcleo.",
    "SEM_CONEXAO": "Não foi possível conectar à API da OpenAI.",
    "API_RECUSOU": "A API da OpenAI recusou o áudio enviado.",
    "TEMPO_ESGOTADO": "A API da OpenAI não respondeu a tempo.",
}


class ErroNucleo(Exception):
    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


def carregar_config():
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def mensagem_para_codigo(codigo, detail):
    return MENSAGENS_ERRO.get(codigo, detail or "Erro desconhecido do núcleo.")


class AppDitado:
    def __init__(self, config):
        self.config = config
        self.gravando = False
        self.quadros = []
        self.stream = None
        self.fila_ui = queue.Queue()
        self._montar_janela()
        self._registrar_atalho()

    # --- janela ---------------------------------------------------------
    def _montar_janela(self):
        self.janela = tk.Tk()
        self.janela.title("Ditado")
        self.janela.geometry("380x240")
        self.rotulo_estado = tk.Label(
            self.janela,
            text=f"Pronto — segure [{self.config['atalho']}] para gravar",
            fg="gray20",
        )
        self.rotulo_estado.pack(pady=6)
        self.caixa_texto = tk.Text(self.janela, wrap="word", height=9)
        self.caixa_texto.pack(fill="both", expand=True, padx=8, pady=8)
        self.janela.protocol("WM_DELETE_WINDOW", self._encerrar)
        self.janela.after(80, self._processar_fila)

    def _processar_fila(self):
        try:
            while True:
                item = self.fila_ui.get_nowait()
                tipo = item[0]
                if tipo == "estado":
                    _, texto, cor = item
                    self.rotulo_estado.config(text=texto, fg=cor)
                elif tipo == "texto":
                    self.caixa_texto.delete("1.0", "end")
                    self.caixa_texto.insert("1.0", item[1])
                    self.rotulo_estado.config(text="Copiado para a área de transferência", fg="dark green")
                elif tipo == "erro":
                    self.rotulo_estado.config(text=item[1], fg="red")
        except queue.Empty:
            pass
        self.janela.after(80, self._processar_fila)

    def _encerrar(self):
        keyboard.unhook_all()
        self.janela.destroy()

    # --- atalho e gravação -----------------------------------------------
    def _registrar_atalho(self):
        tecla = self.config["atalho"]
        keyboard.on_press_key(tecla, self._ao_pressionar, suppress=False)
        keyboard.on_release_key(tecla, self._ao_soltar, suppress=False)

    def _ao_pressionar(self, evento):
        if self.gravando:
            return
        self.gravando = True
        self.quadros = []
        self.fila_ui.put(("estado", "Gravando...", "red"))
        self.stream = sd.InputStream(
            samplerate=TAXA_AMOSTRAGEM, channels=CANAIS, dtype="int16", callback=self._callback_audio
        )
        self.stream.start()

    def _callback_audio(self, indata, frames, tempo, status):
        self.quadros.append(indata.copy())

    def _ao_soltar(self, evento):
        if not self.gravando:
            return
        self.gravando = False
        self.stream.stop()
        self.stream.close()
        self.fila_ui.put(("estado", "Processando...", "dark orange"))
        threading.Thread(target=self._processar_gravacao, daemon=True).start()

    # --- pós-gravação ------------------------------------------------------
    def _processar_gravacao(self):
        estado_pronto = f"Pronto — segure [{self.config['atalho']}] para gravar"
        if not self.quadros:
            self.fila_ui.put(("estado", estado_pronto, "gray20"))
            return

        audio = np.concatenate(self.quadros, axis=0)
        amplitude = audio.astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(amplitude ** 2)))
        if rms < self.config["limiar_silencio_rms"]:
            self.fila_ui.put(("estado", "Silêncio — nada enviado ao núcleo", "gray40"))
            return

        caminho_wav = self._salvar_wav(audio)
        try:
            texto = self._transcrever(caminho_wav)
        except ErroNucleo as erro:
            self.fila_ui.put(("erro", erro.mensagem))
            return
        finally:
            os.remove(caminho_wav)

        pyperclip.copy(texto)
        self.fila_ui.put(("texto", texto))

    def _salvar_wav(self, audio):
        fd, caminho = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with wave.open(caminho, "wb") as wf:
            wf.setnchannels(CANAIS)
            wf.setsampwidth(2)
            wf.setframerate(TAXA_AMOSTRAGEM)
            wf.writeframes(audio.tobytes())
        return caminho

    def _transcrever(self, caminho_wav):
        url = self.config["url_nucleo"].rstrip("/") + "/transcrever"
        try:
            with open(caminho_wav, "rb") as f:
                resp = requests.post(
                    url,
                    files={"audio": ("gravacao.wav", f, "audio/wav")},
                    data={"modelo": self.config["modelo"]},
                    timeout=130,
                )
        except requests.exceptions.RequestException:
            raise ErroNucleo("Não foi possível conectar ao núcleo em " + url)

        if resp.status_code != 200:
            try:
                corpo = resp.json()
            except ValueError:
                raise ErroNucleo(f"Erro do núcleo (HTTP {resp.status_code}).")
            raise ErroNucleo(mensagem_para_codigo(corpo.get("codigo"), corpo.get("detail")))

        return resp.json()["transcricao"]

    def executar(self):
        self.janela.mainloop()


def main():
    config = carregar_config()
    app = AppDitado(config)
    app.executar()


if __name__ == "__main__":
    main()
