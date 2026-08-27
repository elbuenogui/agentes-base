"""App de desktop — paridade inteira com a interface web (SPEC-002, A a I).

Desenho de referência: transcritor/frontend/index.html (D-27 — o código não se aproveita, só o
desenho e os caminhos SVG dos ícones). Contrato consumido: spec/contrato/NUCLEO.md. Inserção no
campo em foco, três estados de janela e modo ao vivo ficam de fora por decisão — ver
desktop/README.md.
"""
import json
import logging
import os
import sys
import tempfile
import threading
import time
import wave
from collections import deque
from datetime import datetime, timedelta

import keyboard
import numpy as np
import requests
import sounddevice as sd
from PySide6.QtCore import (
    Qt, QTimer, Signal, QThread, QSize, QRectF, QPoint, QPropertyAnimation, QEasingCurve, Property,
)
from PySide6.QtGui import QGuiApplication, QColor, QPainter, QBrush, QPen, QFont, QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPlainTextEdit,
    QComboBox,
    QMenu,
    QFrame,
    QScrollArea,
    QSlider,
    QFileDialog,
    QDialog,
)

PASTA_APP = os.path.dirname(__file__)
CAMINHO_CONFIG = os.path.join(PASTA_APP, "config.json")
CAMINHO_LOG = os.path.join(PASTA_APP, "app.log")

TAXA_AMOSTRAGEM = 16000
CANAIS = 1

# gpt-4o-transcribe-diarize fica fora — qualidade reprovada em 2026-08-18 (mesmo corte da web).
MODELOS_ATIVOS = ["gpt-4o-transcribe", "gpt-4o-mini-transcribe"]

NUM_BARRAS = 80
INTERVALO_AMOSTRA_BARRAS_MS = 60
RMS_TETO_BARRAS = 0.4
PISO_BARRAS = 0.15  # SPEC-002 I: "altura de repouso 15%"
LIMIAR_SILENCIO_PICO = 0.02
LIMITE_GRAVACAO_MS = 300_000  # SPEC-002 A5 (D-30): 5 min — 2min30s cortava fala no meio
INTERVALO_OCIOSIDADE_MS = 800
DURACAO_TOAST_CONFIRMACAO_MS = 3000
DURACAO_TOAST_ERRO_MS = 6000
DURACAO_TOAST_SEM_FALA_MS = 3000
DEBOUNCE_ATALHO_S = 0.4
CICLO_PULSO_GRAVANDO_MS = 1200
CICLO_SPINNER_PROCESSANDO_MS = 800
JANELA_MINUTOS_LINHA_TEMPO = 10  # ver README: simplificação assumida no lugar do gesto de roda
DURACAO_ANIMACAO_INTERRUPTOR_MS = 150

CONFIG_PADRAO = {
    "atalho": "ctrl+alt+space",
    "url_nucleo": "http://127.0.0.1:8000",
    "modelo": "gpt-4o-transcribe",
    "streaming": False,
    "dispositivo_entrada": "",
    "recortar_em_vez_de_copiar": True,  # SPEC-002 F4 (D-30): nasce ligado
}

MENSAGENS_ERRO = {
    "MODELO_INVALIDO": "Modelo de transcrição inválido.",
    "SEM_CHAVE": "O núcleo não tem chave da OpenAI configurada.",
    "AUDIO_VAZIO": "Gravação vazia — nada foi enviado.",
    "ARQUIVO_MUITO_GRANDE": "Gravação muito longa — acima do limite do núcleo (25 MB).",
    "FALHA_AUTENTICACAO": "Chave da OpenAI inválida no núcleo.",
    "SEM_CONEXAO": "Não foi possível conectar à API da OpenAI.",
    "API_RECUSOU": "A API da OpenAI recusou o áudio enviado.",
    "TEMPO_ESGOTADO": "A API da OpenAI não respondeu a tempo.",
}

# SPEC-002 seção I — extrato do CSS de transcritor/frontend/index.html; se divergir, o CSS vence.
PALETA = {
    "fundo_janela": "#f4f6f8",
    "fundo_cartao": "#ffffff",
    "borda_cartao": "#d9e2ec",
    "borda_campo": "#bcccdc",
    "texto": "#1f2933",
    "texto_secundario": "#334155",
    "texto_dica": "#52606d",
    "roxo": "#7c3aed",
    "roxo_hover": "#6d28d9",
    "vermelho": "#dc2626",
    "vermelho_hover": "#b91c1c",
    "cancelar_fundo": "#fee2e2",
    "cancelar_fundo_hover": "#fecaca",
    "cancelar_icone": "#b91c1c",
    "azul": "#2563eb",
    "cinza_botao": "#e4e7eb",
    "cinza_botao_hover": "#cbd2d9",
    "bola_botao": "#eef1f5",  # SPEC-002 I / D-30: bola de botão-ícone, mais leve que a web
    "bola_botao_hover": "#dde3e9",
    "confirmacao": "#047857",
    "erro": "#b91c1c",
    "veu_modal": "rgba(15,23,42,0.45)",
    "interruptor_trilho_off": "#cbd2d9",
    "interruptor_bolinha": "#ffffff",
}

QSS = f"""
QWidget#janelaDitado {{ background-color: {PALETA['fundo_janela']}; }}
QFrame#cartaoGravacao {{
  background-color: {PALETA['fundo_cartao']};
  border: 1px solid {PALETA['borda_cartao']};
  border-radius: 8px;
}}
QFrame#painelConfig, QFrame#painelPopupRequisicao {{
  background-color: {PALETA['fundo_cartao']};
  border-radius: 8px;
}}
QLabel {{ color: {PALETA['texto']}; }}
QLabel.dica {{ color: {PALETA['texto_dica']}; font-size: 12px; }}
QPlainTextEdit {{
  border: 1px solid {PALETA['borda_campo']};
  border-radius: 6px;
  padding: 10px;
  background-color: {PALETA['fundo_cartao']};
  color: {PALETA['texto']};
}}
QPushButton {{
  background-color: {PALETA['cinza_botao']};
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  color: {PALETA['texto']};
}}
QPushButton:hover {{ background-color: {PALETA['cinza_botao_hover']}; }}
QPushButton:disabled {{ color: {PALETA['texto_dica']}; }}
QComboBox {{
  border: 1px solid {PALETA['borda_campo']}; border-radius: 6px; padding: 4px 8px;
}}
"""


def estilizar_botao_circular(botao, diametro, cor_fundo=None, cor_fundo_hover=None):
    """Círculo de verdade (raio = metade do lado), estilo direto no widget — não pela regra
    genérica de QPushButton (que produzia "margem quadrada" nos botões redondos e um retângulo
    cinza atrás do círculo roxo do botão de gravar; achado no uso real, 2026-08-27)."""
    cor_fundo = cor_fundo or PALETA["bola_botao"]
    cor_fundo_hover = cor_fundo_hover or PALETA["bola_botao_hover"]
    raio = diametro // 2
    botao.setFixedSize(diametro, diametro)
    botao.setStyleSheet(
        f"QPushButton {{ background-color: {cor_fundo}; border: none; border-radius: {raio}px; "
        f"padding: 0px; }}"
        f"QPushButton:hover {{ background-color: {cor_fundo_hover}; }}"
        f"QPushButton:disabled {{ background-color: transparent; }}"
    )


def carregar_config():
    if not os.path.exists(CAMINHO_CONFIG):
        return dict(CONFIG_PADRAO)
    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            dados = json.load(f)
        config = dict(CONFIG_PADRAO)
        config.update({chave: dados[chave] for chave in CONFIG_PADRAO if chave in dados})
        return config
    except (json.JSONDecodeError, OSError):
        return dict(CONFIG_PADRAO)


def salvar_config(config):
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def copiar_para_area_de_transferencia(texto):
    """Único ponto de escrita no clipboard (D-11) — é o pedaço que B-22 vai trocar depois."""
    QGuiApplication.clipboard().setText(texto)


def listar_dispositivos_entrada():
    try:
        return [d for d in sd.query_devices() if d.get("max_input_channels", 0) > 0]
    except Exception:
        return []


def resolver_indice_dispositivo(nome_salvo):
    if not nome_salvo:
        return None
    try:
        dispositivos = sd.query_devices()
    except Exception:
        return None
    for indice, d in enumerate(dispositivos):
        if d["name"] == nome_salvo and d.get("max_input_channels", 0) > 0:
            return indice
    return None


logging.basicConfig(
    filename=CAMINHO_LOG,
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("ditado")

# --- ícones: mesmos caminhos SVG do index.html (D-27 — o desenho se transporta, o código não) -----
ICONES_SVG = {
    "microfone": (
        '<path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"/>'
        '<path d="M19 11a1 1 0 0 0-2 0 5 5 0 0 1-10 0 1 1 0 0 0-2 0 7 7 0 0 0 6 6.93V20H9a1 1 0 0 0 0 2h6a1 1 0 0 0 0-2h-2v-2.07A7 7 0 0 0 19 11Z"/>'
    ),
    "quadrado": '<rect x="6" y="6" width="12" height="12" rx="2"/>',
    "cancelar": '<path d="M6.4 4.98 12 10.59l5.6-5.61L19.02 6.4 13.41 12l5.61 5.6-1.42 1.42L12 13.41l-5.6 5.61-1.42-1.42L10.59 12 4.98 6.4Z"/>',
    "lixeira": (
        '<path d="M9 3a1 1 0 0 0-1 1v1H5a1 1 0 0 0 0 2h1v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7h1a1 1 0 1 0 0-2h-3V4a1 1 0 0 0-1-1H9Zm1 2h4v1h-4V5ZM8 7h8v12H8V7Zm2 2a1 1 0 0 0-1 1v6a1 1 0 1 0 2 0v-6a1 1 0 0 0-1-1Zm4 0a1 1 0 0 0-1 1v6a1 1 0 1 0 2 0v-6a1 1 0 0 0-1-1Z"/>'
    ),
    "desfazer": '<path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8Z"/>',
    "copiar": '<path d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1Zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Zm0 16H8V7h11v14Z"/>',
    "recortar": (
        '<path d="M9.64 7.64c.23-.5.36-1.05.36-1.64 0-2.21-1.79-4-4-4S2 3.79 2 6s1.79 4 4 4c.59 0 1.14-.13 1.64-.36L10 12l-2.36 2.36C7.14 14.13 6.59 14 6 14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4c0-.59-.13-1.14-.36-1.64L12 14l7 7h3v-1L9.64 7.64ZM6 8c-1.1 0-2-.89-2-2s.9-2 2-2 2 .89 2 2-.9 2-2 2Zm0 12c-1.1 0-2-.89-2-2s.9-2 2-2 2 .89 2 2-.9 2-2 2Zm6-7.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5ZM19 3l-6 6 2 2 7-7V3Z"/>'
    ),
    "tres_pontos": '<circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>',
    "engrenagem": (
        '<path d="M12 15.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7Zm8.94-3.5a7.4 7.4 0 0 0-.14-1.4l1.87-1.46a.6.6 0 0 0 .14-.76l-1.77-3.06a.6.6 0 0 0-.72-.26l-2.2.88a7.5 7.5 0 0 0-1.21-.7l-.34-2.34a.6.6 0 0 0-.6-.5h-3.54a.6.6 0 0 0-.6.5l-.33 2.34c-.44.18-.85.41-1.22.7l-2.2-.88a.6.6 0 0 0-.72.26L5.19 8.38a.6.6 0 0 0 .14.76l1.87 1.46c-.09.46-.14.92-.14 1.4s.05.94.14 1.4l-1.87 1.46a.6.6 0 0 0-.14.76l1.77 3.06c.15.25.46.35.72.26l2.2-.88c.37.29.78.52 1.22.7l.33 2.34c.05.29.3.5.6.5h3.54c.3 0 .55-.21.6-.5l.34-2.34c.43-.18.84-.41 1.21-.7l2.2.88c.26.09.57 0 .72-.26l1.77-3.06a.6.6 0 0 0-.14-.76l-1.87-1.46c.1-.46.14-.92.14-1.4Z"/>'
    ),
    "consumo": (
        '<path d="M4 20a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H4Zm7 0a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-2Zm7 0a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1h-2Z"/>'
    ),
    "enviar": '<path d="M5 20h14v-2H5v2Zm7-16-6 6h4v6h4v-6h4l-6-6Z"/>',
}


def pixmap_svg(nome_icone, cor, tamanho=24):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{cor}">'
        f"{ICONES_SVG[nome_icone]}</svg>"
    )
    renderer = QSvgRenderer(bytearray(svg, encoding="utf-8"))
    pixmap = QPixmap(tamanho, tamanho)
    pixmap.fill(Qt.transparent)
    pintor = QPainter(pixmap)
    renderer.render(pintor)
    pintor.end()
    return pixmap


def icone(nome, cor, tamanho=24):
    return QIcon(pixmap_svg(nome, cor, tamanho))


class CapturaAtalho(QThread):
    """Roda keyboard.read_hotkey (bloqueante) fora da thread do Qt."""

    capturado = Signal(str)

    def run(self):
        combinacao = keyboard.read_hotkey(suppress=True)
        self.capturado.emit(combinacao)


class TrabalhoTranscricao(QThread):
    """Chama POST /transcrever fora da thread do Qt; nunca compara o texto de 'detail', só 'codigo'."""

    progresso = Signal(str)
    concluido = Signal(str)
    falhou = Signal(str, str)  # mensagem legível, codigo (pode vir vazio)

    def __init__(self, url_nucleo, caminho_arquivo, nome_arquivo, modelo, streaming, texto_base, apagar_arquivo_depois):
        super().__init__()
        self.url = url_nucleo.rstrip("/") + "/transcrever"
        self.caminho_arquivo = caminho_arquivo
        self.nome_arquivo = nome_arquivo
        self.modelo = modelo
        self.streaming = streaming
        self.texto_base = texto_base
        self.apagar_arquivo_depois = apagar_arquivo_depois

    def run(self):
        try:
            self._executar()
        finally:
            if self.apagar_arquivo_depois:
                try:
                    os.remove(self.caminho_arquivo)
                except OSError:
                    pass

    def _separador(self):
        return "\n" if self.texto_base and not self.texto_base.endswith("\n") else ""

    def _executar(self):
        try:
            with open(self.caminho_arquivo, "rb") as f:
                resposta = requests.post(
                    self.url,
                    files={"audio": (self.nome_arquivo, f, "application/octet-stream")},
                    data={"modelo": self.modelo, "stream": "true" if self.streaming else "false"},
                    timeout=130,
                    stream=self.streaming,
                )
        except requests.exceptions.RequestException:
            self.falhou.emit(f"Não foi possível conectar ao núcleo em {self.url}.", "")
            return

        if resposta.status_code != 200:
            self._emitir_erro_http(resposta)
            return

        if not self.streaming:
            try:
                texto = resposta.json()["transcricao"]
            except (ValueError, KeyError):
                self.falhou.emit("Resposta inesperada do núcleo.", "")
                return
            self.concluido.emit(self.texto_base + self._separador() + texto)
            return

        self._consumir_stream(resposta)

    def _consumir_stream(self, resposta):
        separador = self._separador()
        acumulado = ""
        recebeu_final = False
        try:
            for linha in resposta.iter_lines(decode_unicode=True):
                if not linha:
                    continue
                try:
                    evento = json.loads(linha)
                except ValueError:
                    continue
                tipo = evento.get("tipo")
                if tipo == "delta":
                    acumulado += evento.get("texto", "")
                    self.progresso.emit(self.texto_base + separador + acumulado)
                elif tipo == "final":
                    acumulado = evento.get("texto", acumulado)
                    recebeu_final = True
                    self.concluido.emit(self.texto_base + separador + acumulado)
                elif tipo == "erro":
                    codigo = evento.get("codigo") or ""
                    mensagem = MENSAGENS_ERRO.get(codigo, evento.get("detail") or "Erro desconhecido durante o streaming.")
                    self.falhou.emit(mensagem, codigo)
                    return
        except requests.exceptions.RequestException:
            pass
        if not recebeu_final:
            self.falhou.emit("A conexão de streaming foi interrompida antes da transcrição terminar.", "")

    def _emitir_erro_http(self, resposta):
        try:
            corpo = resposta.json()
        except ValueError:
            self.falhou.emit(f"Erro do núcleo (HTTP {resposta.status_code}).", "")
            return
        codigo = corpo.get("codigo") or ""
        mensagem = MENSAGENS_ERRO.get(codigo, corpo.get("detail") or "Erro desconhecido do núcleo.")
        self.falhou.emit(mensagem, codigo)


class TrabalhoConsumo(QThread):
    """Chama GET /consumo fora da thread do Qt (G1-G5)."""

    sucesso = Signal(dict)
    falhou = Signal(str)

    def __init__(self, url_nucleo):
        super().__init__()
        self.url = url_nucleo.rstrip("/") + "/consumo"

    def run(self):
        try:
            resposta = requests.get(self.url, timeout=10)
        except requests.exceptions.RequestException:
            self.falhou.emit(f"Não foi possível conectar ao núcleo em {self.url}.")
            return
        if resposta.status_code != 200:
            self.falhou.emit(f"O núcleo respondeu com erro (HTTP {resposta.status_code}) ao consultar o consumo.")
            return
        try:
            self.sucesso.emit(resposta.json())
        except ValueError:
            self.falhou.emit("Resposta inesperada do núcleo ao consultar consumo.")


class BotaoGravar(QPushButton):
    """Um só controle que alterna figura: microfone (parado) / quadrado (gravando) / spinner (A1)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(72, 72)  # SPEC-002 I: círculo de 4.5rem
        self.setCursor(Qt.PointingHandCursor)
        # sem isso, a regra genérica de QPushButton pinta um retângulo cinza atrás do círculo —
        # a "margem quadrada" relatada no uso real (quem desenha o círculo é o paintEvent).
        self.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0px; }")
        self._estado = "parado"
        self._angulo_spinner = 0
        self._fase_pulso = 0.0
        self._icone_microfone = pixmap_svg("microfone", "white", 28)
        self._icone_quadrado = pixmap_svg("quadrado", "white", 28)
        self._timer_spinner = QTimer(self)
        self._timer_spinner.timeout.connect(self._girar)
        self._timer_pulso = QTimer(self)
        self._timer_pulso.timeout.connect(self._pulsar)
        self._realce_arrastar = False
        self.definir_estado("parado")

    def definir_realce_arrastar(self, ativo):
        """E2 — enquanto um arquivo de áudio paira sobre o botão, ele mostra que vai aceitar."""
        self._realce_arrastar = ativo
        self.update()

    def definir_estado(self, estado):
        self._estado = estado
        self._timer_spinner.stop()
        self._timer_pulso.stop()
        if estado == "processando":
            # SPEC-002 I: anel de 1,6rem, volta a cada 0,8s
            self._angulo_spinner = 0
            self._timer_spinner.start(20)
        elif estado == "gravando":
            self._fase_pulso = 0.0
            self._timer_pulso.start(30)
        self.setEnabled(estado != "processando")
        rotulo = {"parado": "Iniciar gravação", "gravando": "Parar gravação", "processando": "Processando…"}[estado]
        self.setToolTip(rotulo)
        self.setAccessibleName(rotulo)
        self.update()

    def _girar(self):
        # 360 graus a cada CICLO_SPINNER_PROCESSANDO_MS, com tick de 20ms
        passo = 360 * 20 / CICLO_SPINNER_PROCESSANDO_MS
        self._angulo_spinner = (self._angulo_spinner + passo) % 360
        self.update()

    def _pulsar(self):
        passo = 30 / CICLO_PULSO_GRAVANDO_MS
        self._fase_pulso = (self._fase_pulso + passo) % 1.0
        self.update()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        raio = min(self.width(), self.height()) / 2 - 2
        cx, cy = self.width() / 2, self.height() / 2

        if self._estado == "gravando":
            raio_pulso = raio * (1 + 0.35 * self._fase_pulso)
            alfa_pulso = max(0, int(160 * (1 - self._fase_pulso)))
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QBrush(QColor(220, 38, 38, alfa_pulso)))
            pintor.drawEllipse(
                int(cx - raio_pulso), int(cy - raio_pulso), int(raio_pulso * 2), int(raio_pulso * 2)
            )

        if self._estado == "gravando":
            cor_fundo = QColor(PALETA["vermelho"])
        elif self._estado == "processando":
            cor_fundo = QColor(PALETA["azul"])
        else:
            cor_fundo = QColor(PALETA["roxo"])
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QBrush(cor_fundo))
        pintor.drawEllipse(int(cx - raio), int(cy - raio), int(raio * 2), int(raio * 2))

        if self._estado == "processando":
            pintor.setBrush(Qt.NoBrush)
            pintor.setPen(QPen(QColor("white"), 3))
            tamanho = raio * 0.9
            pintor.drawArc(
                int(cx - tamanho / 2), int(cy - tamanho / 2), int(tamanho), int(tamanho),
                int(self._angulo_spinner * 16), 120 * 16,
            )
        else:
            pix = self._icone_quadrado if self._estado == "gravando" else self._icone_microfone
            pintor.drawPixmap(int(cx - pix.width() / 2), int(cy - pix.height() / 2), pix)

        if self._realce_arrastar:
            pintor.setBrush(Qt.NoBrush)
            pintor.setPen(QPen(QColor(PALETA["azul"]), 3))
            pintor.drawEllipse(int(cx - raio - 4), int(cy - raio - 4), int((raio + 4) * 2), int((raio + 4) * 2))


class BarraAmplitude(QWidget):
    """80 barras, uma amostra a cada 60ms — cresce dos dois lados a partir do centro (A4 / SPEC-002 I)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)  # 2.5rem
        self._amostras = deque([0.0] * NUM_BARRAS, maxlen=NUM_BARRAS)
        # sempre visível (J1/J2) — em repouso as amostras são todas 0.0, que já desenha a faixa
        # "baixa e parada" (piso de 15%); esconder por setVisible faria a janela mudar de tamanho.

    def reiniciar(self):
        self._amostras = deque([0.0] * NUM_BARRAS, maxlen=NUM_BARRAS)
        self.update()

    def empurrar_amostra(self, rms):
        self._amostras.append(rms)
        self.update()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        n = len(self._amostras)
        largura_barra = 2.0
        vao = 1.0
        largura_total = n * (largura_barra + vao) - vao
        x0 = (self.width() - largura_total) / 2
        centro_y = self.height() / 2
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QBrush(QColor(PALETA["roxo"])))
        for i, rms in enumerate(self._amostras):
            magnitude = min(1.0, rms / RMS_TETO_BARRAS) ** 0.5
            altura_rel = PISO_BARRAS + magnitude * (1 - PISO_BARRAS)
            altura_px = altura_rel * self.height()
            x = x0 + i * (largura_barra + vao)
            pintor.drawRoundedRect(
                x, centro_y - altura_px / 2, largura_barra, altura_px, largura_barra / 2, largura_barra / 2,
            )


class Toast(QLabel):
    """Balão efêmero (B4/J3) — flutua por cima do conteúdo, logo acima do botão de gravar; não
    participa de layout nenhum, então nunca muda o tamanho da janela. Um canal só, nunca empilha
    (B1-B3): cada chamada substitui a anterior na hora."""

    CORES = {"confirmacao": PALETA["confirmacao"], "erro": PALETA["erro"]}

    def __init__(self, ancora):
        super().__init__(ancora.parentWidget())
        self._ancora = ancora  # widget acima do qual o balão aparece (o botão de gravar)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setMaximumWidth(260)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.esconder)

    def mostrar(self, tipo, texto, duracao_ms):
        cor = self.CORES.get(tipo, PALETA["texto"])
        self.setStyleSheet(
            f"QLabel {{ background-color: {cor}; color: white; border-radius: 6px; "
            f"padding: 6px 10px; font-size: 12px; }}"
        )
        self.setText(texto)
        self.adjustSize()
        self._reposicionar()
        self.show()
        self.raise_()
        self._timer.stop()
        self._timer.start(duracao_ms)

    def _reposicionar(self):
        geo_ancora = self._ancora.geometry()  # já nas coordenadas do parent em comum
        x = geo_ancora.center().x() - self.width() // 2
        y = geo_ancora.top() - self.height() - 8
        self.move(max(4, x), max(4, y))

    def esconder(self):
        self._timer.stop()
        self.hide()
        self.setText("")


class BotaoLixeiraDesfazer(QPushButton):
    """Troca de função conforme o estado da caixa; o lugar dele na linha nunca some (C3)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        estilizar_botao_circular(self, 32)  # 2rem
        self.setIconSize(QSize(17, 17))

    def atualizar(self, tem_texto, tem_snapshot):
        if tem_texto:
            self.setIcon(icone("lixeira", PALETA["texto_secundario"], 17))
            self.setToolTip("Apagar transcrição")
            self.setEnabled(True)
        elif tem_snapshot:
            self.setIcon(icone("desfazer", PALETA["texto_secundario"], 17))
            self.setToolTip("Desfazer — restaurar texto apagado")
            self.setEnabled(True)
        else:
            self.setIcon(QIcon())
            self.setToolTip("")
            self.setEnabled(False)


class Interruptor(QWidget):
    """Trilho + bolinha branca que desliza (SPEC-002 I) — um QCheckBox estilizado só troca de cor,
    e foi reprovado no uso real: "não é um interruptor". Desenhado à mão, com animação de 0,15s."""

    alternado = Signal(bool)

    LARGURA = 44
    ALTURA = 24
    DIAMETRO_BOLINHA = 19
    MARGEM = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.LARGURA, self.ALTURA)
        self.setCursor(Qt.PointingHandCursor)
        self._ligado = False
        self._pos_bolinha = float(self.MARGEM)
        self._anim = QPropertyAnimation(self, b"posBolinha", self)
        self._anim.setDuration(DURACAO_ANIMACAO_INTERRUPTOR_MS)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)

    def _get_pos_bolinha(self):
        return self._pos_bolinha

    def _set_pos_bolinha(self, valor):
        self._pos_bolinha = valor
        self.update()

    posBolinha = Property(float, _get_pos_bolinha, _set_pos_bolinha)

    def isChecked(self):
        return self._ligado

    def setChecked(self, ligado, animar=True):
        self._ligado = ligado
        destino = float(self.LARGURA - self.DIAMETRO_BOLINHA - self.MARGEM) if ligado else float(self.MARGEM)
        if animar:
            self._anim.stop()
            self._anim.setStartValue(self._pos_bolinha)
            self._anim.setEndValue(destino)
            self._anim.start()
        else:
            self._pos_bolinha = destino
            self.update()

    def mousePressEvent(self, evento):
        self.setChecked(not self._ligado)
        self.alternado.emit(self._ligado)

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        cor_trilho = QColor(PALETA["azul"]) if self._ligado else QColor(PALETA["interruptor_trilho_off"])
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QBrush(cor_trilho))
        pintor.drawRoundedRect(
            QRectF(0, 0, self.LARGURA, self.ALTURA), self.ALTURA / 2, self.ALTURA / 2
        )
        pintor.setBrush(QBrush(QColor(PALETA["interruptor_bolinha"])))
        y = (self.ALTURA - self.DIAMETRO_BOLINHA) / 2
        pintor.drawEllipse(QRectF(self._pos_bolinha, y, self.DIAMETRO_BOLINHA, self.DIAMETRO_BOLINHA))


class OverlayModal(QWidget):
    """Fundo semitransparente com um painel centralizado — clicar fora fecha (H2), como a web.

    Usado em vez de QDialog nativo porque QDialog não fecha ao clicar fora (H2 não teria como
    funcionar de verdade).
    """

    def __init__(self, parent):
        super().__init__(parent)
        # Seletor por objectName, não regra "solta": uma regra sem seletor vaza para os filhos na
        # cascata do Qt (o painel branco herdava o véu escuro do próprio pai) — visto e corrigido
        # na conferência visual desta tarefa (ver PROGRESSO.md).
        self.setObjectName("veuModal")
        self.setStyleSheet(f"QWidget#veuModal {{ background-color: {PALETA['veu_modal']}; }}")
        self.hide()
        # QFrame aplica "background-color" do QSS nativamente; QWidget puro precisaria de
        # WA_StyledBackground — mais simples usar QFrame direto para o painel branco por cima do véu.
        self.painel = QFrame(self)
        self._largura_alvo = None  # subclasse define via definir_largura_alvo

    def definir_largura_alvo(self, largura):
        self._largura_alvo = largura

    def mostrar(self):
        self.setGeometry(self.parentWidget().rect())
        if self._largura_alvo is not None:
            # nunca mais largo que a janela (a janela é um utilitário pequeno, não a página web
            # inteira de onde a medida em rem foi extraída) — achado na conferência visual.
            self.painel.setFixedWidth(min(self._largura_alvo, self.width() - 40))
        self.painel.adjustSize()
        self.painel.move(
            (self.width() - self.painel.width()) // 2,
            max(10, (self.height() - self.painel.height()) // 2),
        )
        self.show()
        self.raise_()

    def esconder(self):
        self.hide()

    def mousePressEvent(self, evento):
        if not self.painel.geometry().contains(evento.position().toPoint()):
            self.esconder()


def _cabecalho_painel(titulo, ao_fechar):
    layout = QHBoxLayout()
    rotulo = QLabel(f"<b>{titulo}</b>")
    botao_fechar = QPushButton()
    botao_fechar.setIcon(icone("cancelar", PALETA["texto_secundario"], 14))
    estilizar_botao_circular(botao_fechar, 28)
    botao_fechar.clicked.connect(ao_fechar)
    layout.addWidget(rotulo)
    layout.addStretch()
    layout.addWidget(botao_fechar)
    return layout


class PainelConfiguracoes(OverlayModal):
    def __init__(self, janela):
        super().__init__(janela)
        self.janela = janela
        self.painel.setObjectName("painelConfig")
        self.definir_largura_alvo(int(24 * 16))  # 24rem

        layout_form = QFormLayout()

        self.combo_modelo = QComboBox()
        self.combo_modelo.addItems(MODELOS_ATIVOS)
        self.combo_modelo.setCurrentText(janela.config["modelo"])
        self.combo_modelo.currentTextChanged.connect(self._mudou_modelo)
        layout_form.addRow("Modelo de transcrição", self.combo_modelo)

        self.check_streaming = Interruptor()
        self.check_streaming.setChecked(janela.config["streaming"], animar=False)
        self.check_streaming.alternado.connect(self._mudou_streaming)
        layout_form.addRow("Streaming do transcript", self.check_streaming)

        self.combo_dispositivo = QComboBox()
        self.combo_dispositivo.currentIndexChanged.connect(self._mudou_dispositivo)
        layout_form.addRow("Dispositivo de entrada", self.combo_dispositivo)

        self.check_recortar = Interruptor()
        self.check_recortar.setChecked(janela.config["recortar_em_vez_de_copiar"], animar=False)
        self.check_recortar.alternado.connect(self._mudou_recortar)
        layout_form.addRow("Recortar em vez de copiar", self.check_recortar)

        self.botao_atalho = QPushButton(janela.config["atalho"])
        self.botao_atalho.clicked.connect(self._iniciar_captura_atalho)
        layout_form.addRow("Atalho global (alterna)", self.botao_atalho)

        layout_painel = QVBoxLayout(self.painel)
        layout_painel.setContentsMargins(20, 20, 20, 20)
        layout_painel.setSpacing(10)
        layout_painel.addLayout(_cabecalho_painel("Configurações", self.esconder))
        layout_painel.addLayout(layout_form)

        self._thread_captura = None

    def _mudou_modelo(self, texto):
        self.janela.config["modelo"] = texto
        salvar_config(self.janela.config)

    def _mudou_streaming(self, ligado):
        self.janela.config["streaming"] = ligado
        salvar_config(self.janela.config)

    def _mudou_dispositivo(self, _indice):
        self.janela.config["dispositivo_entrada"] = self.combo_dispositivo.currentData()
        salvar_config(self.janela.config)

    def _mudou_recortar(self, ligado):
        self.janela.config["recortar_em_vez_de_copiar"] = ligado
        salvar_config(self.janela.config)
        self.janela.atualizar_botao_copiar()

    def _iniciar_captura_atalho(self):
        self.janela.desregistrar_atalho_global()
        self.botao_atalho.setText("Pressione a combinação desejada…")
        self.botao_atalho.setEnabled(False)
        self._thread_captura = CapturaAtalho()
        self._thread_captura.capturado.connect(self._ao_capturar_atalho)
        self._thread_captura.start()

    def _ao_capturar_atalho(self, combinacao):
        self.janela.config["atalho"] = combinacao
        salvar_config(self.janela.config)
        self.botao_atalho.setText(combinacao)
        self.botao_atalho.setEnabled(True)
        self.janela.registrar_atalho_global()

    def _popular_dispositivos(self):
        self.combo_dispositivo.blockSignals(True)
        self.combo_dispositivo.clear()
        self.combo_dispositivo.addItem("Padrão do sistema", "")
        nome_salvo = self.janela.config.get("dispositivo_entrada") or ""
        indice_selecionar = 0
        for d in listar_dispositivos_entrada():
            self.combo_dispositivo.addItem(d["name"], d["name"])
            if d["name"] == nome_salvo:
                indice_selecionar = self.combo_dispositivo.count() - 1
        self.combo_dispositivo.setCurrentIndex(indice_selecionar)
        self.combo_dispositivo.blockSignals(False)

    def mostrar(self):
        self._popular_dispositivos()
        super().mostrar()


class GraficoBarrasDiario(QWidget):
    """G2 — gráfico de barras simples do custo por dia."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._valores = []

    def definir_valores(self, valores):
        self._valores = valores
        self.update()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        # widget desenhado à mão pinta o próprio fundo — sem isso, herda o fundo escuro por trás
        # (achado no uso real: "o fundo ficou preto e não dá pra ver nada que tá escrito").
        pintor.fillRect(self.rect(), QColor(PALETA["fundo_cartao"]))
        if not self._valores:
            return
        maximo = max(self._valores) or 1.0
        n = len(self._valores)
        largura_barra = max(2.0, self.width() / n * 0.6)
        passo = self.width() / n
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QBrush(QColor(PALETA["azul"])))
        for i, valor in enumerate(self._valores):
            altura = (valor / maximo) * (self.height() - 4)
            x = i * passo + (passo - largura_barra) / 2
            pintor.drawRect(int(x), int(self.height() - altura), int(largura_barra), int(altura))


class LinhaDoTempoConsumo(QWidget):
    """G3 — um ponto por requisição; escala 'hora' (um dia) ou 'minuto' (janela deslizante de 24h)."""

    ponto_clicado = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setMouseTracking(True)
        self.requisicoes = []  # [{"quando": datetime, ...dados}]
        self.escala = "hora"
        self.dia_selecionado = None
        self.offset_minutos = 0  # minutos desde o inicio da janela de 24h (0 = mais antigo)
        self._pontos_desenhados = []  # [(x, y, dados)]

    def definir_requisicoes(self, lista):
        self.requisicoes = []
        for item in lista:
            try:
                quando = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
            except (KeyError, ValueError):
                continue
            self.requisicoes.append({**item, "quando": quando})
        self.requisicoes.sort(key=lambda r: r["quando"])
        if self.requisicoes:
            self.dia_selecionado = self.requisicoes[-1]["quando"].date()
            self.offset_minutos = max(0, 24 * 60 - JANELA_MINUTOS_LINHA_TEMPO)
        self.update()

    def alternar_escala(self):
        self.escala = "minuto" if self.escala == "hora" else "hora"
        self.update()

    def dia_anterior(self):
        if self.dia_selecionado:
            self.dia_selecionado -= timedelta(days=1)
            self.update()

    def dia_seguinte(self):
        if self.dia_selecionado:
            self.dia_selecionado += timedelta(days=1)
            self.update()

    def limites_dia(self):
        if not self.requisicoes:
            return None, None
        return self.requisicoes[0]["quando"].date(), self.requisicoes[-1]["quando"].date()

    def definir_offset_minutos(self, minutos):
        self.offset_minutos = minutos
        self.update()

    def _requisicoes_visiveis(self):
        if self.escala == "hora":
            if not self.dia_selecionado:
                return []
            return [r for r in self.requisicoes if r["quando"].date() == self.dia_selecionado]
        if not self.requisicoes:
            return []
        ancora = self.requisicoes[-1]["quando"]
        inicio_24h = ancora - timedelta(hours=24)
        inicio_janela = inicio_24h + timedelta(minutes=self.offset_minutos)
        fim_janela = inicio_janela + timedelta(minutes=JANELA_MINUTOS_LINHA_TEMPO)
        return [r for r in self.requisicoes if inicio_janela <= r["quando"] <= fim_janela]

    def periodo_visivel_texto(self):
        if self.escala == "hora":
            if not self.dia_selecionado:
                return "Sem requisições"
            return self.dia_selecionado.strftime("%d/%m/%Y")
        if not self.requisicoes:
            return "Sem requisições"
        ancora = self.requisicoes[-1]["quando"]
        inicio_24h = ancora - timedelta(hours=24)
        inicio_janela = inicio_24h + timedelta(minutes=self.offset_minutos)
        fim_janela = inicio_janela + timedelta(minutes=JANELA_MINUTOS_LINHA_TEMPO)
        return f"{inicio_janela.strftime('%d/%m %H:%M')} — {fim_janela.strftime('%H:%M')}"

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(PALETA["fundo_cartao"]))  # ver GraficoBarrasDiario
        self._pontos_desenhados = []

        margem = 10
        eixo_y = self.height() - 25
        pintor.setPen(QPen(QColor(PALETA["borda_campo"]), 1))
        pintor.drawLine(margem, eixo_y, self.width() - margem, eixo_y)

        if not self.requisicoes:
            pintor.setPen(QColor(PALETA["texto_dica"]))
            pintor.drawText(self.rect(), Qt.AlignCenter, "Nenhuma requisição neste recorte.")
            return

        if self.escala == "hora":
            inicio = datetime.combine(self.dia_selecionado, datetime.min.time())
            fim = inicio + timedelta(days=1)
            passo_rotulo = timedelta(hours=3)
        else:
            ancora = self.requisicoes[-1]["quando"]
            inicio_24h = ancora - timedelta(hours=24)
            inicio = inicio_24h + timedelta(minutes=self.offset_minutos)
            fim = inicio + timedelta(minutes=JANELA_MINUTOS_LINHA_TEMPO)
            passo_rotulo = timedelta(minutes=2)

        largura_util = self.width() - 2 * margem
        duracao_total = max(1.0, (fim - inicio).total_seconds())

        # marcas de hora no eixo, como a linha do tempo da web (3:00h, 06h, 12h, ...)
        pintor.setPen(QPen(QColor(PALETA["texto_dica"]), 1))
        marca = inicio
        while marca <= fim:
            fracao = (marca - inicio).total_seconds() / duracao_total
            x = margem + fracao * largura_util
            pintor.drawLine(int(x), eixo_y - 3, int(x), eixo_y + 3)
            rotulo = marca.strftime("%Hh") if self.escala == "hora" else marca.strftime("%H:%M")
            pintor.drawText(int(x - 15), eixo_y + 16, 30, 12, Qt.AlignCenter, rotulo)
            marca += passo_rotulo

        visiveis = self._requisicoes_visiveis()
        if not visiveis:
            return

        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QBrush(QColor(PALETA["azul"])))
        for req in visiveis:
            fracao = (req["quando"] - inicio).total_seconds() / duracao_total
            x = margem + fracao * largura_util
            y = eixo_y
            pintor.drawEllipse(int(x - 4), int(y - 4), 8, 8)
            self._pontos_desenhados.append((x, y, req))

    def mousePressEvent(self, evento):
        pos = evento.position()
        for x, y, dados in self._pontos_desenhados:
            if (pos.x() - x) ** 2 + (pos.y() - y) ** 2 <= 10 ** 2:
                self.ponto_clicado.emit(dados)
                return


class PopupRequisicao(OverlayModal):
    def __init__(self, parent):
        super().__init__(parent)
        self.painel.setObjectName("painelPopupRequisicao")
        self.definir_largura_alvo(int(24 * 16))  # 24rem

        self.rotulo_meta = QLabel()
        self.rotulo_meta.setProperty("class", "dica")
        self.rotulo_meta.setWordWrap(True)
        self.texto = QPlainTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setFixedHeight(120)

        layout_painel = QVBoxLayout(self.painel)
        layout_painel.setContentsMargins(20, 20, 20, 20)
        layout_painel.setSpacing(10)
        layout_painel.addLayout(_cabecalho_painel("Transcrição", self.esconder))
        layout_painel.addWidget(self.rotulo_meta)
        layout_painel.addWidget(self.texto)

    def mostrar_requisicao(self, dados):
        quando = dados["quando"].strftime("%d/%m/%Y %H:%M:%S")
        custo = dados.get("custo_usd", 0.0)
        modelo = dados.get("modelo", "?")
        self.rotulo_meta.setText(f"{quando} · {modelo} · US$ {custo:.5f}")
        texto = dados.get("texto")
        self.texto.setPlainText(texto if texto else "Não há transcrição guardada para esta requisição.")
        self.mostrar()


class PainelConsumo(QDialog):
    """Janela própria, redimensionável — não um overlay dentro da janela pequena de ditado.

    SPEC-002 G / D-30: um painel de 42rem (pensado pra página web inteira) dentro da janela do
    ditado (40rem) "ficou desproporcional, não dá pra ler direito, tá até vazando da tela" — achado
    no uso real em 2026-08-27. Consumo passou a abrir numa janela própria; só Configurações
    continua como painel sobreposto (são cinco linhas, cabe)."""

    def __init__(self, janela):
        super().__init__(janela, Qt.Window)
        self.janela = janela
        self.setWindowTitle("Consumo")
        self.resize(900, 600)
        self.setStyleSheet(f"QDialog {{ background-color: {PALETA['fundo_cartao']}; }}")
        self._dados = None
        self._baseline_sessao = None
        self._trabalho = None
        self.popup_requisicao = PopupRequisicao(self)  # overlay dentro DESTA janela, não da de ditado

        self.rotulo_carregando = QLabel("Carregando…")
        self.rotulo_erro = QLabel()
        self.rotulo_erro.setWordWrap(True)
        self.rotulo_erro.hide()

        self.rotulo_sessao = QLabel()
        self.botao_resetar = QPushButton("Resetar sessão")
        self.botao_resetar.clicked.connect(self._resetar_sessao)

        self.rotulo_diario_titulo = QLabel("Histórico diário")
        self.lista_diaria = QLabel()
        self.lista_diaria.setWordWrap(True)
        self.area_lista_diaria = QScrollArea()
        self.area_lista_diaria.setWidget(self.lista_diaria)
        self.area_lista_diaria.setWidgetResizable(True)
        self.area_lista_diaria.setFixedHeight(120)

        self.grafico = GraficoBarrasDiario()

        self.rotulo_periodo_linha_tempo = QLabel()
        self.botao_zoom = QPushButton("Zoom: Hora")
        self.botao_zoom.clicked.connect(self._alternar_zoom)
        self.botao_dia_anterior = QPushButton("◀ Dia anterior")
        self.botao_dia_anterior.clicked.connect(self._dia_anterior)
        self.botao_dia_seguinte = QPushButton("Dia seguinte ▶")
        self.botao_dia_seguinte.clicked.connect(self._dia_seguinte)
        self.slider_janela = QSlider(Qt.Horizontal)
        self.slider_janela.valueChanged.connect(self._mudou_slider)
        self.botao_inicio_janela = QPushButton("Início (24h atrás)")
        self.botao_inicio_janela.clicked.connect(lambda: self.slider_janela.setValue(0))
        self.botao_fim_janela = QPushButton("Mais recente")
        self.botao_fim_janela.clicked.connect(lambda: self.slider_janela.setValue(self.slider_janela.maximum()))
        self.linha_tempo = LinhaDoTempoConsumo()
        self.linha_tempo.ponto_clicado.connect(self._abrir_popup_requisicao)

        linha_nav_dia = QHBoxLayout()
        linha_nav_dia.addWidget(self.botao_dia_anterior)
        linha_nav_dia.addStretch()
        linha_nav_dia.addWidget(self.botao_dia_seguinte)
        self.widget_nav_dia = QWidget()
        self.widget_nav_dia.setLayout(linha_nav_dia)

        linha_nav_janela = QHBoxLayout()
        linha_nav_janela.addWidget(self.botao_inicio_janela)
        linha_nav_janela.addWidget(self.slider_janela, 1)
        linha_nav_janela.addWidget(self.botao_fim_janela)
        self.widget_nav_janela = QWidget()
        self.widget_nav_janela.setLayout(linha_nav_janela)
        self.widget_nav_janela.hide()

        layout_cabecalho_lt = QHBoxLayout()
        layout_cabecalho_lt.addWidget(QLabel("Linha do tempo das requisições"))
        layout_cabecalho_lt.addStretch()
        layout_cabecalho_lt.addWidget(self.botao_zoom)

        corpo = QWidget()
        layout_corpo = QVBoxLayout(corpo)
        layout_corpo.setContentsMargins(0, 0, 0, 0)
        layout_corpo.setSpacing(10)
        layout_corpo.addWidget(self.rotulo_carregando)
        layout_corpo.addWidget(self.rotulo_erro)
        layout_corpo.addWidget(self.rotulo_sessao)
        layout_corpo.addWidget(self.botao_resetar)
        layout_corpo.addWidget(self.rotulo_diario_titulo)
        layout_corpo.addWidget(self.area_lista_diaria)
        layout_corpo.addWidget(self.grafico)
        layout_corpo.addLayout(layout_cabecalho_lt)
        layout_corpo.addWidget(self.rotulo_periodo_linha_tempo)
        layout_corpo.addWidget(self.widget_nav_dia)
        layout_corpo.addWidget(self.widget_nav_janela)
        layout_corpo.addWidget(self.linha_tempo)
        layout_corpo.addWidget(QLabel("O reset zera só esta tela; o histórico salvo no backend não é apagado."))

        # janela própria e redimensionável: o corpo rola dentro da área disponível, que agora pode
        # crescer com a janela — não fica mais preso a uma altura fixa dentro de um overlay pequeno.
        area_rolagem = QScrollArea()
        area_rolagem.setWidget(corpo)
        area_rolagem.setWidgetResizable(True)
        area_rolagem.setFrameShape(QFrame.NoFrame)
        area_rolagem.setStyleSheet(f"QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: {PALETA['fundo_cartao']}; }}")
        corpo.setStyleSheet(f"background-color: {PALETA['fundo_cartao']};")

        layout_janela = QVBoxLayout(self)
        layout_janela.setContentsMargins(20, 20, 20, 20)
        layout_janela.addWidget(area_rolagem)

        self._mostrar_conteudo(False)

    def _mostrar_conteudo(self, visivel):
        for w in (
            self.rotulo_sessao, self.botao_resetar, self.rotulo_diario_titulo, self.area_lista_diaria,
            self.grafico, self.rotulo_periodo_linha_tempo, self.linha_tempo,
        ):
            w.setVisible(visivel)
        self.widget_nav_dia.setVisible(visivel and self.linha_tempo.escala == "hora")
        self.widget_nav_janela.setVisible(visivel and self.linha_tempo.escala == "minuto")

    def esconder(self):
        self.hide()

    def mostrar(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.rotulo_carregando.show()
        self.rotulo_erro.hide()
        self._mostrar_conteudo(False)
        self._trabalho = TrabalhoConsumo(self.janela.config["url_nucleo"])
        self._trabalho.sucesso.connect(self._ao_obter_sucesso)
        self._trabalho.falhou.connect(self._ao_falhar)
        self._trabalho.start()

    def _ao_falhar(self, mensagem):
        self.rotulo_carregando.hide()
        self.rotulo_erro.setText(mensagem)
        self.rotulo_erro.show()
        self._mostrar_conteudo(False)
        log.info("erro_consumo mensagem=%s", mensagem)

    def _ao_obter_sucesso(self, dados):
        self.rotulo_carregando.hide()
        self.rotulo_erro.hide()
        self._dados = dados
        self._mostrar_conteudo(True)
        self._renderizar_sessao()
        self._renderizar_diario()
        self.linha_tempo.definir_requisicoes(dados.get("requisicoes", []))
        self._atualizar_slider_janela()
        self._atualizar_periodo_texto()

    def _renderizar_sessao(self):
        sessao = dict(self._dados.get("sessao", {"requisicoes": 0, "tokens": 0, "custo_usd": 0.0}))
        base = self._baseline_sessao or {"requisicoes": 0, "tokens": 0, "custo_usd": 0.0}
        requisicoes = sessao.get("requisicoes", 0) - base.get("requisicoes", 0)
        tokens = sessao.get("tokens", 0) - base.get("tokens", 0)
        custo = sessao.get("custo_usd", 0.0) - base.get("custo_usd", 0.0)
        self.rotulo_sessao.setText(
            f"Sessão: {requisicoes} requisições · {tokens} tokens · US$ {custo:.5f}"
        )

    def _resetar_sessao(self):
        if self._dados:
            self._baseline_sessao = dict(self._dados.get("sessao", {}))
            self._renderizar_sessao()

    def _renderizar_diario(self):
        por_dia = self._dados.get("por_dia", [])
        linhas = [
            f"{item['data']} · {item['requisicoes']} req · {item['tokens']} tokens · US$ {item['custo_usd']:.5f}"
            for item in por_dia
        ]
        self.lista_diaria.setText("\n".join(linhas) if linhas else "Sem histórico salvo ainda.")
        self.grafico.definir_valores([item["custo_usd"] for item in por_dia])

    def _alternar_zoom(self):
        self.linha_tempo.alternar_escala()
        self.botao_zoom.setText("Zoom: Hora" if self.linha_tempo.escala == "hora" else "Zoom: Minuto")
        self.widget_nav_dia.setVisible(self.linha_tempo.escala == "hora")
        self.widget_nav_janela.setVisible(self.linha_tempo.escala == "minuto")
        self._atualizar_periodo_texto()

    def _dia_anterior(self):
        self.linha_tempo.dia_anterior()
        self._atualizar_botoes_dia()
        self._atualizar_periodo_texto()

    def _dia_seguinte(self):
        self.linha_tempo.dia_seguinte()
        self._atualizar_botoes_dia()
        self._atualizar_periodo_texto()

    def _atualizar_botoes_dia(self):
        minimo, maximo = self.linha_tempo.limites_dia()
        atual = self.linha_tempo.dia_selecionado
        self.botao_dia_anterior.setEnabled(bool(minimo) and atual is not None and atual > minimo)
        self.botao_dia_seguinte.setEnabled(bool(maximo) and atual is not None and atual < maximo)

    def _atualizar_slider_janela(self):
        maximo = max(0, 24 * 60 - JANELA_MINUTOS_LINHA_TEMPO)
        self.slider_janela.blockSignals(True)
        self.slider_janela.setRange(0, maximo)
        self.slider_janela.setValue(self.linha_tempo.offset_minutos)
        self.slider_janela.blockSignals(False)
        self._atualizar_botoes_dia()

    def _mudou_slider(self, valor):
        self.linha_tempo.definir_offset_minutos(valor)
        self._atualizar_periodo_texto()

    def _atualizar_periodo_texto(self):
        self.rotulo_periodo_linha_tempo.setText(self.linha_tempo.periodo_visivel_texto())

    def _abrir_popup_requisicao(self, dados):
        self.popup_requisicao.mostrar_requisicao(dados)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if self.popup_requisicao.isVisible():
            self.popup_requisicao.setGeometry(self.rect())

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Escape and self.popup_requisicao.isVisible():
            self.popup_requisicao.esconder()
            return
        super().keyPressEvent(evento)


class JanelaDitado(QWidget):
    sinal_atalho_disparado = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.gravando = False
        self.processando = False
        self.stream_audio = None
        self._lock_audio = threading.Lock()
        self._quadros_completos = []
        self._quadros_pendentes_barra = []
        self._pico_gravacao = 0.0
        self._inicio_gravacao = None
        self.snapshot_texto = None
        self._trabalho = None
        self._ultimo_disparo_atalho = 0.0

        self._montar_ui()
        self.sinal_atalho_disparado.connect(self.alternar_gravacao)
        self.registrar_atalho_global()

        log.info(
            "abertura dispositivo=%s taxa_amostragem=%s atalho=%s",
            self._nome_dispositivo_para_log(), TAXA_AMOSTRAGEM, self.config["atalho"],
        )

    # --- montagem da interface -------------------------------------------------
    def _montar_ui(self):
        self.setObjectName("janelaDitado")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle("Ditado")
        self.setStyleSheet(QSS)
        self.resize(int(40 * 16) + 32, 480)  # SPEC-002 I: coluna principal 40rem + respiro

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(16, 16, 16, 16)

        cartao = QFrame()
        cartao.setObjectName("cartaoGravacao")
        layout = QVBoxLayout(cartao)
        layout.setContentsMargins(24, 24, 24, 24)  # 1.5rem
        layout.setSpacing(16)  # 1rem
        layout_externo.addWidget(cartao)

        # trio encostado e centralizado (não uma barra espalhada — achado no uso real: os dois
        # addStretch nas pontas empurravam ⋮ e cancelar para as bordas). Vão de 10px (0.6rem) entre
        # os três; o botão de gravar não se move porque o trio inteiro é um bloco só, centralizado
        # por stretches simétricos nas duas pontas.
        linha_topo = QHBoxLayout()
        linha_topo.setSpacing(10)
        linha_topo.addStretch(1)

        self.botao_menu = QPushButton()
        self.botao_menu.setIcon(icone("tres_pontos", PALETA["texto_secundario"], 20))
        estilizar_botao_circular(self.botao_menu, 44)
        linha_topo.addWidget(self.botao_menu)

        self.botao_gravar = BotaoGravar()
        self.botao_gravar.clicked.connect(self.alternar_gravacao)
        linha_topo.addWidget(self.botao_gravar)

        self.botao_cancelar = QPushButton()
        estilizar_botao_circular(self.botao_cancelar, 44, PALETA["cancelar_fundo"], PALETA["cancelar_fundo_hover"])
        self.botao_cancelar.setEnabled(False)
        self.botao_cancelar.clicked.connect(self.cancelar_gravacao)
        linha_topo.addWidget(self.botao_cancelar)

        linha_topo.addStretch(1)
        layout.addLayout(linha_topo)

        self.rotulo_cronometro = QLabel("")
        self.rotulo_cronometro.setAlignment(Qt.AlignCenter)
        fonte_mono = QFont("Consolas")
        fonte_mono.setStyleHint(QFont.Monospace)
        fonte_mono.setPointSize(12)
        self.rotulo_cronometro.setFont(fonte_mono)
        self.rotulo_cronometro.setText("00:00")
        self.rotulo_cronometro.setMinimumHeight(self.rotulo_cronometro.sizeHint().height())
        self.rotulo_cronometro.setText("")
        # nunca some (J1/J2): o espaço da linha fica reservado desde a abertura, só o texto muda.
        layout.addWidget(self.rotulo_cronometro)

        self.barra_amplitude = BarraAmplitude()
        layout.addWidget(self.barra_amplitude)

        self.caixa_texto = QPlainTextEdit()
        self.caixa_texto.setPlaceholderText("A transcrição aparece aqui — editável, soma cada gravação.")
        self.caixa_texto.setMinimumHeight(128)  # 8rem
        self.caixa_texto.textChanged.connect(self._ao_editar_texto)
        layout.addWidget(self.caixa_texto, 1)

        linha_acoes = QHBoxLayout()
        self.botao_lixeira = BotaoLixeiraDesfazer()
        self.botao_lixeira.clicked.connect(self._clicar_lixeira)
        linha_acoes.addWidget(self.botao_lixeira)
        linha_acoes.addStretch()
        self.botao_copiar = QPushButton()
        estilizar_botao_circular(self.botao_copiar, 32)
        self.botao_copiar.setIconSize(QSize(17, 17))
        self.botao_copiar.clicked.connect(self._clicar_copiar)
        linha_acoes.addWidget(self.botao_copiar)
        layout.addLayout(linha_acoes)

        # balão flutuante (B4/J3): filho do cartão, fora do layout — nunca muda o tamanho da janela.
        self.toast = Toast(self.botao_gravar)

        self.painel_configuracoes = PainelConfiguracoes(self)
        self.painel_consumo = PainelConsumo(self)

        self.menu_avancado = QMenu(self)
        acao_config = self.menu_avancado.addAction(icone("engrenagem", PALETA["texto_secundario"]), "Configurações")
        acao_config.triggered.connect(self.painel_configuracoes.mostrar)
        acao_consumo = self.menu_avancado.addAction(icone("consumo", PALETA["texto_secundario"]), "Consumo")
        acao_consumo.triggered.connect(self.painel_consumo.mostrar)
        acao_upload = self.menu_avancado.addAction(icone("enviar", PALETA["texto_secundario"]), "Enviar arquivo")
        acao_upload.triggered.connect(self._clicar_enviar_arquivo)
        # clicked + popup() em vez de setMenu(): setMenu() acrescenta um chevron que não existe no
        # desenho de referência (achado no uso real).
        self.botao_menu.clicked.connect(self._abrir_menu_avancado)

        self._atualizar_icone_cancelar(ativo=False)
        self.setAcceptDrops(True)  # E2 — arrastar e soltar áudio no botão de gravar

        self._timer_cronometro = QTimer(self)
        self._timer_cronometro.timeout.connect(self._atualizar_cronometro)
        self._timer_barra = QTimer(self)
        self._timer_barra.timeout.connect(self._amostrar_nivel)
        self._timer_ociosidade = QTimer(self)
        self._timer_ociosidade.setSingleShot(True)
        self._timer_ociosidade.timeout.connect(self._registrar_snapshot_se_ocioso)
        self._timer_corte_seguranca = QTimer(self)
        self._timer_corte_seguranca.setSingleShot(True)
        self._timer_corte_seguranca.timeout.connect(self._cortar_por_seguranca)

        self.atualizar_botao_copiar()
        self._atualizar_botao_lixeira()

    def _atualizar_icone_cancelar(self, ativo):
        # slot do cancelar sempre ocupado (grade de 3 colunas fixa) — só o ícone/estado mudam (A2)
        if ativo:
            self.botao_cancelar.setIcon(icone("cancelar", PALETA["cancelar_icone"], 20))
        else:
            self.botao_cancelar.setIcon(QIcon())
        self.botao_cancelar.setEnabled(ativo)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        # Consumo agora é janela própria (QDialog) — só Configurações é overlay desta janela.
        if self.painel_configuracoes.isVisible():
            self.painel_configuracoes.setGeometry(self.rect())
        if self.toast.isVisible():
            self.toast._reposicionar()

    def keyPressEvent(self, evento):
        # H1: dentro da janela de Consumo, o popup de requisição tem prioridade sobre ela mesma
        # (ver PainelConsumo.keyPressEvent) — aqui só sobra Configurações.
        if evento.key() == Qt.Key_Escape and self.painel_configuracoes.isVisible():
            self.painel_configuracoes.esconder()
            return
        super().keyPressEvent(evento)

    def dragEnterEvent(self, evento):
        if evento.mimeData().hasUrls() and any(
            u.toLocalFile().lower().endswith((".m4a", ".wav", ".mp3")) for u in evento.mimeData().urls()
        ):
            evento.acceptProposedAction()
            self.botao_gravar.definir_realce_arrastar(True)

    def dragLeaveEvent(self, evento):
        self.botao_gravar.definir_realce_arrastar(False)

    def dropEvent(self, evento):
        self.botao_gravar.definir_realce_arrastar(False)
        urls = evento.mimeData().urls()
        if not urls:
            return
        if len(urls) > 1:
            self.toast.mostrar("erro", "Só um arquivo por vez — os demais foram ignorados.", DURACAO_TOAST_ERRO_MS)
        caminho = urls[0].toLocalFile()
        if not caminho.lower().endswith((".m4a", ".wav", ".mp3")):
            self.toast.mostrar("erro", "Formato não aceito — use .m4a, .wav ou .mp3.", DURACAO_TOAST_ERRO_MS)
            return
        if self.gravando or self.processando:
            return
        nome_arquivo = os.path.basename(caminho)
        self.processando = True
        self.botao_gravar.definir_estado("processando")
        self._disparar_transcricao(caminho, nome_arquivo, apagar_arquivo_depois=False)

    def _abrir_menu_avancado(self):
        self.menu_avancado.popup(self.botao_menu.mapToGlobal(QPoint(0, self.botao_menu.height() + 4)))

    def closeEvent(self, evento):
        self.desregistrar_atalho_global()
        if self.stream_audio is not None:
            try:
                self.stream_audio.stop()
                self.stream_audio.close()
            except Exception:
                pass
        super().closeEvent(evento)

    # --- atalho global (D-28: alterna, configurável pela interface) ------------
    def registrar_atalho_global(self):
        try:
            keyboard.add_hotkey(self.config["atalho"], self._ao_disparar_atalho, suppress=False, trigger_on_release=False)
        except Exception as erro:
            log.info("falha_ao_registrar_atalho atalho=%s erro=%s", self.config["atalho"], erro)

    def desregistrar_atalho_global(self):
        try:
            keyboard.remove_hotkey(self.config["atalho"])
        except (KeyError, ValueError):
            pass

    def _ao_disparar_atalho(self):
        # Roda na thread do hook da lib keyboard — nunca mexe em widget aqui, só emite o sinal
        # (validado antes de construir a interface: ver PROGRESSO.md da tarefa anterior).
        agora = time.monotonic()
        if agora - self._ultimo_disparo_atalho < DEBOUNCE_ATALHO_S:
            return
        self._ultimo_disparo_atalho = agora
        self.sinal_atalho_disparado.emit()

    # --- fluxo de gravação (A) ---------------------------------------------------
    def alternar_gravacao(self):
        if self.processando:
            return
        if self.gravando:
            self.parar_e_enviar()
        else:
            self.iniciar_gravacao()

    def _dispositivo_indice_atual(self):
        return resolver_indice_dispositivo(self.config.get("dispositivo_entrada"))

    def _nome_dispositivo_para_log(self):
        indice = self._dispositivo_indice_atual()
        if indice is None:
            return "padrão do sistema"
        try:
            return sd.query_devices()[indice]["name"]
        except Exception:
            return "padrão do sistema"

    def iniciar_gravacao(self):
        if self.processando:
            return
        self.gravando = True
        self._quadros_completos = []
        self._quadros_pendentes_barra = []
        self._pico_gravacao = 0.0

        self.botao_gravar.definir_estado("gravando")
        self._atualizar_icone_cancelar(ativo=True)
        self.rotulo_cronometro.setText("00:00")
        self.barra_amplitude.reiniciar()

        self._inicio_gravacao = time.monotonic()
        self._timer_cronometro.start(1000)
        self._timer_barra.start(INTERVALO_AMOSTRA_BARRAS_MS)
        self._timer_corte_seguranca.start(LIMITE_GRAVACAO_MS)

        try:
            self.stream_audio = sd.InputStream(
                samplerate=TAXA_AMOSTRAGEM,
                channels=CANAIS,
                dtype="float32",
                device=self._dispositivo_indice_atual(),
                callback=self._callback_audio,
            )
            self.stream_audio.start()
        except Exception as erro:
            self.gravando = False
            self._parar_temporizadores_e_stream()
            self.botao_gravar.definir_estado("parado")
            self._atualizar_icone_cancelar(ativo=False)
            self.toast.mostrar("erro", f"Não foi possível abrir o microfone: {erro}", DURACAO_TOAST_ERRO_MS)

    def _callback_audio(self, indata, frames, tempo, status):
        dados = indata.copy()
        with self._lock_audio:
            self._quadros_completos.append(dados)
            self._quadros_pendentes_barra.append(dados)
        pico = float(np.max(np.abs(dados))) if dados.size else 0.0
        if pico > self._pico_gravacao:
            self._pico_gravacao = pico

    def _amostrar_nivel(self):
        with self._lock_audio:
            pendentes, self._quadros_pendentes_barra = self._quadros_pendentes_barra, []
        if pendentes:
            bloco = np.concatenate(pendentes, axis=0)
            rms = float(np.sqrt(np.mean(bloco.astype(np.float64) ** 2))) if bloco.size else 0.0
        else:
            rms = 0.0
        self.barra_amplitude.empurrar_amostra(rms)

    def _atualizar_cronometro(self):
        decorrido_ms = int((time.monotonic() - self._inicio_gravacao) * 1000)
        total_segundos = decorrido_ms // 1000
        minutos, segundos = divmod(total_segundos, 60)
        self.rotulo_cronometro.setText(f"{minutos:02d}:{segundos:02d}")

    def _parar_temporizadores_e_stream(self):
        self._timer_cronometro.stop()
        self._timer_barra.stop()
        self._timer_corte_seguranca.stop()
        self.rotulo_cronometro.setText("")  # J1/J2: some o conteúdo, não a caixa
        self.barra_amplitude.reiniciar()
        if self.stream_audio is not None:
            self.stream_audio.stop()
            self.stream_audio.close()
            self.stream_audio = None

    def cancelar_gravacao(self):
        if not self.gravando:
            return
        self.gravando = False
        self._parar_temporizadores_e_stream()
        self.botao_gravar.definir_estado("parado")
        self._atualizar_icone_cancelar(ativo=False)
        self.toast.mostrar("confirmacao", "Gravação cancelada.", DURACAO_TOAST_CONFIRMACAO_MS)

    def _cortar_por_seguranca(self):
        self.parar_e_enviar(aviso_corte=True)

    def parar_e_enviar(self, aviso_corte=False):
        if not self.gravando:
            return
        self.gravando = False
        self._parar_temporizadores_e_stream()
        self._atualizar_icone_cancelar(ativo=False)

        with self._lock_audio:
            quadros, self._quadros_completos = self._quadros_completos, []
        pico = self._pico_gravacao

        if pico < LIMIAR_SILENCIO_PICO:
            self.botao_gravar.definir_estado("parado")
            log.info("descarte_por_silencio pico=%.4f limiar=%.4f", pico, LIMIAR_SILENCIO_PICO)
            self.toast.mostrar("erro", "Não foi identificado nenhuma fala", DURACAO_TOAST_SEM_FALA_MS)
            return

        self.botao_gravar.definir_estado("processando")
        self.processando = True

        if aviso_corte:
            self.toast.mostrar(
                "erro",
                "Gravação interrompida automaticamente por segurança ao atingir o limite de 5 minutos. "
                "Enviando o áudio gravado até aqui para transcrição…",
                DURACAO_TOAST_ERRO_MS,
            )

        caminho_wav = self._salvar_wav(quadros)
        self._disparar_transcricao(caminho_wav, "gravacao.wav", apagar_arquivo_depois=True)

    def _salvar_wav(self, quadros):
        audio = np.concatenate(quadros, axis=0) if quadros else np.zeros((0,), dtype=np.float32)
        inteiros = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
        fd, caminho = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with wave.open(caminho, "wb") as wf:
            wf.setnchannels(CANAIS)
            wf.setsampwidth(2)
            wf.setframerate(TAXA_AMOSTRAGEM)
            wf.writeframes(inteiros.tobytes())
        return caminho

    # --- enviar arquivo (E1 — mesmo caminho da gravação) --------------------------
    def _clicar_enviar_arquivo(self):
        if self.gravando or self.processando:
            return
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar áudio", "", "Áudio (*.m4a *.wav *.mp3);;Todos os arquivos (*)"
        )
        if not caminho:
            return
        nome_arquivo = os.path.basename(caminho)
        self.processando = True
        self.botao_gravar.definir_estado("processando")
        self._disparar_transcricao(caminho, nome_arquivo, apagar_arquivo_depois=False)

    # --- transcrição (chamada ao núcleo) -----------------------------------------
    def _disparar_transcricao(self, caminho_arquivo, nome_arquivo, apagar_arquivo_depois):
        self.toast.esconder()  # "andamento" não mostra texto — o spinner já conta a história (B1)
        texto_base = self.caixa_texto.toPlainText()
        self._trabalho = TrabalhoTranscricao(
            url_nucleo=self.config["url_nucleo"],
            caminho_arquivo=caminho_arquivo,
            nome_arquivo=nome_arquivo,
            modelo=self.config["modelo"],
            streaming=self.config["streaming"],
            texto_base=texto_base,
            apagar_arquivo_depois=apagar_arquivo_depois,
        )
        self._trabalho.progresso.connect(self._ao_progresso_transcricao)
        self._trabalho.concluido.connect(self._ao_concluir_transcricao)
        self._trabalho.falhou.connect(self._ao_falhar_transcricao)
        self._trabalho.start()

    def _ao_progresso_transcricao(self, texto_acumulado):
        self._escrever_texto(texto_acumulado)

    def _ao_concluir_transcricao(self, texto_final):
        self._escrever_texto(texto_final)
        self.processando = False
        self.botao_gravar.definir_estado("parado")
        self.toast.mostrar("confirmacao", "Transcrição adicionada ao texto abaixo.", DURACAO_TOAST_CONFIRMACAO_MS)

    def _ao_falhar_transcricao(self, mensagem, codigo):
        self.processando = False
        self.botao_gravar.definir_estado("parado")
        if codigo:
            log.info("erro_nucleo codigo=%s", codigo)
        self.toast.mostrar("erro", mensagem, DURACAO_TOAST_ERRO_MS)

    # --- caixa de transcrição: acumula, editável, desfazer (C) ---------------------
    def _escrever_texto(self, valor):
        self.caixa_texto.blockSignals(True)
        self.caixa_texto.setPlainText(valor)
        cursor = self.caixa_texto.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.caixa_texto.setTextCursor(cursor)
        self.caixa_texto.blockSignals(False)
        self._atualizar_botao_lixeira()
        self._agendar_snapshot()

    def _ao_editar_texto(self):
        self._atualizar_botao_lixeira()
        self._agendar_snapshot()

    def _agendar_snapshot(self):
        self._timer_ociosidade.start(INTERVALO_OCIOSIDADE_MS)

    def _registrar_snapshot_se_ocioso(self):
        valor_atual = self.caixa_texto.toPlainText()
        if valor_atual.strip():
            self.snapshot_texto = valor_atual

    def _atualizar_botao_lixeira(self):
        tem_texto = bool(self.caixa_texto.toPlainText().strip())
        self.botao_lixeira.atualizar(tem_texto, bool(self.snapshot_texto))

    def _apagar_com_snapshot(self):
        valor_antes = self.caixa_texto.toPlainText()
        if valor_antes.strip():
            self.snapshot_texto = valor_antes
        self._timer_ociosidade.stop()
        self.caixa_texto.blockSignals(True)
        self.caixa_texto.clear()
        self.caixa_texto.blockSignals(False)
        self._atualizar_botao_lixeira()

    def _clicar_lixeira(self):
        tem_texto = bool(self.caixa_texto.toPlainText().strip())
        if tem_texto:
            self._apagar_com_snapshot()
        elif self.snapshot_texto:
            valor_restaurado = self.snapshot_texto
            self.snapshot_texto = None
            self._timer_ociosidade.stop()
            self._escrever_texto(valor_restaurado)

    # --- copiar/recortar (D) ------------------------------------------------------
    def atualizar_botao_copiar(self):
        recortar = self.config["recortar_em_vez_de_copiar"]
        self.botao_copiar.setIcon(icone("recortar" if recortar else "copiar", PALETA["texto_secundario"], 17))
        self.botao_copiar.setToolTip("Recortar texto" if recortar else "Copiar texto")

    def _clicar_copiar(self):
        texto = self.caixa_texto.toPlainText()
        recortar = self.config["recortar_em_vez_de_copiar"]
        acao = "recortar" if recortar else "copiar"
        if not texto.strip():
            self.toast.mostrar("erro", f"Nada para {acao} — a caixa de transcrição está vazia.", DURACAO_TOAST_ERRO_MS)
            return
        copiar_para_area_de_transferencia(texto)
        if recortar:
            self._apagar_com_snapshot()
            self.toast.mostrar("confirmacao", "Texto recortado para a área de transferência.", DURACAO_TOAST_CONFIRMACAO_MS)
        else:
            self.toast.mostrar("confirmacao", "Texto copiado para a área de transferência.", DURACAO_TOAST_CONFIRMACAO_MS)


def main():
    config = carregar_config()
    app = QApplication(sys.argv)
    janela = JanelaDitado(config)
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
