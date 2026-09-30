"""App de desktop — paridade inteira com a interface web (SPEC-002, A a I).

Desenho de referência: transcritor/frontend/index.html (D-27 — o código não se aproveita, só o
desenho e os caminhos SVG dos ícones). Contrato consumido: spec/contrato/NUCLEO.md. Inserção no
campo em foco, três estados de janela e modo ao vivo ficam de fora por decisão — ver
desktop/README.md.
"""
import base64
import json
import logging
import math
import os
import sys
import tempfile
import threading
import time
import wave
from collections import deque
from datetime import datetime, time as hora_minima, timedelta

import keyboard
import numpy as np
import requests
import sounddevice as sd
from PySide6.QtCore import (
    Qt, QTimer, Signal, QThread, QSize, QRect, QRectF, QPoint, QUrl, QEvent, QPropertyAnimation, QEasingCurve,
    Property,
    QAbstractAnimation,
)
from PySide6.QtGui import (
    QGuiApplication, QColor, QPainter, QBrush, QPen, QFont, QIcon, QPixmap, QDesktopServices, QCursor,
    QRegion,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLayout,
    QLineEdit,
    QPlainTextEdit,
    QComboBox,
    QMenu,
    QWidgetAction,
    QFrame,
    QScrollArea,
    QSlider,
    QFileDialog,
    QDialog,
)

PASTA_APP = os.path.dirname(__file__)
CAMINHO_CONFIG = os.path.join(PASTA_APP, "config.json")
CAMINHO_LOG = os.path.join(PASTA_APP, "app.log")
# Menu ⋮ → Abrir planejamento (pedido direto do usuário, 2026-09-25, fora do plano da Fase 2): a
# página do Sistema de Organização (ARQUIVO-PESSOAL/02_PROJETOS/SISTEMA-DE-ORGANIZACAO). O endereço
# é fixo: a página é sempre republicada no mesmo link.
URL_PLANEJAMENTO = "https://claude.ai/artifact/Do6KoH3PAY3BEPkd946Cow"

# Núcleo no Supabase, Etapa 5 — ditado e consumo vão para o núcleo remoto (Edge Functions
# `transcrever` e `consumo`, que só atendem quem fez login no Supabase Auth); a geração de imagem
# continua no núcleo local, que recebe o mesmo token e registra o consumo no banco (Etapa 4).
# Os quatro valores são públicos por desenho (URL do projeto e chave publicável) — nenhuma chave
# secreta mora no app. A sessão (token de renovação) fica fora do repositório, em
# %APPDATA%\agentes-base\sessao.json; a senha nunca é gravada.
SUPABASE_URL_PADRAO = "https://wqoeoofhuhsdzpkdblbg.supabase.co"
SUPABASE_CHAVE_PUBLICAVEL_PADRAO = "sb_publishable_2bvFHk0139ioveDrSmNpEw_JRhmaD9w"
URL_NUCLEO_REMOTO_PADRAO = SUPABASE_URL_PADRAO + "/functions/v1"
URL_NUCLEO_LOCAL_PADRAO = "http://127.0.0.1:8000"  # também a saída de emergência para `url_nucleo`
RENOVAR_SESSAO_ANTES_S = 120  # renova o token de acesso quando faltar menos que isto para expirar
TIMEOUT_AUTH_S = 15
TIMEOUT_CONSUMO_S = 30  # era 10 no núcleo local; o remoto lê ~2 mil linhas do banco a cada abertura
MENSAGEM_SESSAO_EXPIRADA = "Sessão expirada — entre de novo."

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
INTERVALO_PULSO_MS = 30  # quadro do anel de pulso da CamadaPulso (era literal, D-32 7ª volta)
CICLO_SPINNER_PROCESSANDO_MS = 800
DURACAO_ANIMACAO_INTERRUPTOR_MS = 150

# D-32 — janela flutuante compacta (só o botão de gravar) que expande no hover e nos estados
# gravando/processando.
MARGEM_JANELA_COMPACTA = 4  # D-32 7ª volta: respiro em volta do BotaoGravar — o compacto é
                            # 72 + 2x4 = 80px. Era 8 (88x88) até a 6ª volta; o usuário chamou o
                            # sobrando de "essa borda ao redor do botão tão grande".
ATRASO_ENCOLHER_MS = 250  # debounce: micro-saída do mouse pela borda não pode encolher na hora
INTERVALO_VIGIA_PONTEIRO_MS = 100
DURACAO_ANIMACAO_MODO_MS = 240  # D-32 7ª volta: era 160. Pedido direto do usuário ("bota uma
                                # transição maior, ele não sumir") — a transição curta lia como
                                # sumiço abrupto do botão, não como movimento.
LIMIAR_ARRASTE_PX = 6  # abaixo disso é clique (tremida da mão), acima é arrastar a janela
TAMANHO_MAXIMO_QT = 16777215  # QWIDGETSIZE_MAX — sem uso desde a 9ª volta (a janela é fixa)
FOLGA_MASCARA_PX = 2  # D-32 9ª volta: a máscara é o retângulo do cartão visível mais esta
                      # folga. setMask é 1 bit — a folga existe para a máscara nunca comer a
                      # borda do cartão (o arredondado continua vindo do alfa por pixel).

# D-32 7ª volta (2026-09-05) — métricas de layout da janela EXPANDIDA. Vivem aqui porque
# _montar_ui e _configurar_layout_do_modo precisam declarar exatamente as mesmas: se as duas
# saírem de sincronia, a janela muda de altura ao voltar do compacto (o gate J1/J2).
MARGEM_EXTERNA_EXPANDIDA = 8   # era 16 — borda transparente em volta do cartão
MARGEM_CARTAO_EXPANDIDA = 16   # era 24 (1.5rem) — respiro interno do cartão branco
ESPACAMENTO_CARTAO = 8         # era 16 (1rem) — entre as linhas do cartão
ALTURA_BARRA_AMPLITUDE = 24    # era 40 (2.5rem) — ver BarraAmplitude
LADO_BOTAO_SECUNDARIO = 32     # ⋮ e cancelar; eram 44. O BotaoGravar continua 72 (alvo central).

# D-32 7ª volta — LARGURA da janela expandida. Este valor é PRÓPRIO desta janela flutuante e não
# segue mais o item I da SPEC-002 (coluna de 40rem/672px): aquele vínculo era reaproveitamento de
# medida, nunca exigência de paridade, e foi revogado só para esta janela (as outras — painel de
# configurações, consumo — continuam em 40rem).
#
# Piso absoluto, MEDIDO no layout real (offscreen), não somado à mão: a linha do topo é quem manda.
#   cronômetro 49 + 10 + [mola] + ⋮ 32 + 10 + gravar 72 + 10 + cancelar 32 + 10 + [mola] +
#   espelho 49 = 274 de linha do topo
#   + 2x16 margem do cartão = 306 · + 2x1 borda do QSS = 308 · + 2x8 margem externa = 324.
# Em 324 as duas molas ficam em 0px (cronômetro colado no ⋮), ou seja: cabe, mas sem respiro.
#
# Escolha entre 324 e 672, por medição de leitura da caixa de transcrição (fonte real, offscreen):
#   324 -> 30 caracteres por linha · 384 -> 38 · 432 -> 44 · 448 -> 46 · 672 -> 74.
# 448 é o menor valor medido em que a caixa ainda fica na faixa legível de ~45+ caracteres por
# linha (abaixo disso a transcrição vira coluna de jornal, quebrando quase toda frase ditada), e
# ainda sobram 62px em cada mola da linha do topo. Corta 224px (-33%) dos 672 anteriores — a 6ª
# volta cortou 11px e o usuário disse, com razão, que não mudou nada.
LARGURA_EXPANDIDA = 448  # 672 -> 448 (-224px, -33%); piso medido = 324

# D-32 6ª volta — altura da caixa de transcrição, a pedido do usuário ("o box de copiar tem de
# ficar num terço do total"). NÃO muda na 7ª volta.
ALTURA_CAIXA_TEXTO = 160  # ~1/3 dos 480px que a janela expandida tinha antes (480/3 = 160)
# D-32 7ª volta — tudo que NÃO é a caixa de transcrição, depois dos cortes nos elementos fixos
# (a 6ª volta tinha medido 309 e só encolhido a caixa, o que deu 11px de diferença total e foi
# rejeitado pelo usuário). Medido no layout real, não somado à mão — testar_altura_expandida
# refaz a conta contra o layout e falha se alguém mexer numa margem:
#   8+8 margem externa · 1+1 borda do cartão · 16+16 margem do cartão · 3x8 espaçamento ·
#   72 linha do topo (cronômetro + ⋮ + gravar + cancelar, fundidos numa linha só) ·
#   24 barra de amplitude · 32 linha de ações.
# Essa lista soma 202 — a 7ª volta escreveu 186, que é a mesma lista SEM os 8+8 da margem
# externa; foi exatamente esse esquecimento que produziu a sobreposição corrigida na 8ª volta.
# Desvio registrado: a 6ª volta previa a linha do topo em 56px (⋮/cancelar 44->32), mas a linha é
# tão alta quanto o widget mais alto dela, e o BotaoGravar continua 72 por ordem explícita — os
# 16px previstos ali não existem sem encolher o botão central, o que a tarefa proíbe.
# D-32 8ª volta — a conta da 7ª volta esquecia os 2x MARGEM_EXTERNA_EXPANDIDA (16px) que ficam
# POR FORA do cartão: o cartão sozinho já pedia 346px (minimumSizeHint), mas recebia 346-16=330.
# Como layout_externo usa SetNoConstraint (necessário para a animação), o Qt não recusa o tamanho
# pequeno demais — ele empilha os itens sobrepostos, e a linha de ações (lixeira/copiar) subia
# para dentro da caixa de transcrição (medido: 7px de sobreposição, relatado pelo usuário).
# Novo valor MEDIDO no layout real (offscreen), não somado à mão:
#   j._layout_externo.minimumSize().height() = 362  <- mínimo real da JANELA (cartão + margem
#   externa + a borda de 1px do QSS, que uma conta manual erra)
#   362 - ALTURA_CAIXA_TEXTO(160) = 202  <- tudo que não é a caixa
# = os 186 da 7ª volta + os 16 da margem externa que faltavam.
ALTURA_FIXA_EXPANDIDA = 202  # medida, não estimada — testar_altura_expandida refaz a conta
# Folga pequena contra variação de métrica de fonte entre máquinas (a caixa de transcrição, que é
# quem tem fator de esticar, absorve estes 4px e fica em 164 em vez de 160 — ALTURA_CAIXA_TEXTO
# continua sendo o PISO declarado da caixa, que o usuário confirmou como bom).
FOLGA_ALTURA_EXPANDIDA = 4
ALTURA_EXPANDIDA = ALTURA_FIXA_EXPANDIDA + ALTURA_CAIXA_TEXTO + FOLGA_ALTURA_EXPANDIDA  # 366

# SPEC-002 G3 — transcritos de transcritor/frontend/index.html (constantes calibradas por medição,
# comentário "--- Linha do tempo das requisições ---"). A escala "minuto" é uma janela móvel de
# largura fixa dentro das últimas 24h (não o histórico inteiro) — sem isso, 24h a 15px/s dariam
# 1,3 milhão de pixels de largura.
PX_POR_SEGUNDO_ESCALA_MINUTO = 15
LARGURA_JANELA_MINUTO_MS = 3 * 60 * 1000
JANELA_24H_MS = 24 * 60 * 60 * 1000
# Folga nas duas pontas do recorte desenhado (não da janela "real" que filtra os pontos): sem ela,
# o ponto exatamente na borda fica com metade do alvo de clique cortada pelo container.
MARGEM_BORDA_JANELA_MS = 3000
DURACAO_DIA_MS = 24 * 60 * 60 * 1000
MARGEM_BORDA_DIA_MS = 3000
ESPACAMENTO_MINIMO_PX_ROTULO_EIXO = 80  # mira ~80-120px por rótulo
# Escada de passos "redondos" para as marcas do eixo — sempre em fronteira de tempo local legível
# (minuto/hora/dia cheios), nunca múltiplo cru de epoch.
ESCADA_PASSOS_EIXO_TEMPO = [
    {"ms": 10_000, "unidade": "segundo", "multiplo": 10},
    {"ms": 30_000, "unidade": "segundo", "multiplo": 30},
    {"ms": 60_000, "unidade": "minuto", "multiplo": 1},
    {"ms": 5 * 60_000, "unidade": "minuto", "multiplo": 5},
    {"ms": 15 * 60_000, "unidade": "minuto", "multiplo": 15},
    {"ms": 30 * 60_000, "unidade": "minuto", "multiplo": 30},
    {"ms": 60 * 60_000, "unidade": "hora", "multiplo": 1},
    {"ms": 3 * 60 * 60_000, "unidade": "hora", "multiplo": 3},
    {"ms": 6 * 60 * 60_000, "unidade": "hora", "multiplo": 6},
    {"ms": 12 * 60 * 60_000, "unidade": "hora", "multiplo": 12},
    {"ms": 24 * 60 * 60_000, "unidade": "dia", "multiplo": 1},
]

CONFIG_PADRAO = {
    "atalho": "ctrl+alt+space",
    # Etapa 5: ditado e consumo no núcleo remoto; imagem no local. Voltar `url_nucleo` para
    # http://127.0.0.1:8000 é a saída de emergência — o núcleo local ignora o cabeçalho de login.
    "url_nucleo": URL_NUCLEO_REMOTO_PADRAO,
    "url_nucleo_imagem": URL_NUCLEO_LOCAL_PADRAO,
    "supabase_url": SUPABASE_URL_PADRAO,
    "supabase_chave_publicavel": SUPABASE_CHAVE_PUBLICAVEL_PADRAO,
    "modelo": "gpt-4o-transcribe",
    "streaming": False,
    "dispositivo_entrada": "",
    "recortar_em_vez_de_copiar": True,  # SPEC-002 F4 (D-30): nasce ligado
    # D-31 — Gerar imagem (fora do plano da Fase 2, ver desktop/README.md e NUCLEO.md Operação 3).
    "modelo_imagem": "gpt-image-1.5",
    "tamanho_imagem": "auto",
    "qualidade_imagem": "medium",
    "pasta_saida_imagens": os.path.join(PASTA_APP, "imagens-geradas"),
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
    "NAO_AUTENTICADO": MENSAGEM_SESSAO_EXPIRADA,
    "REQUISICAO_INVALIDA": "O núcleo recusou a requisição (formato inesperado).",
}

# D-31 — Gerar imagem. Espelha (do lado do cliente) a tabela de preços e a lista de modelos do
# núcleo (transcritor/backend/main.py) — os dois processos não compartilham código, então esta
# cópia precisa ser atualizada manualmente se os preços da OpenAI mudarem (mesmo padrão já usado
# para MODELOS_ATIVOS de transcrição). dall-e-2 fica fora: removido da API em 2026-05-12
# (confirmado por busca em 2026-08-27) — ver NUCLEO.md.
MODELOS_IMAGEM_ATIVOS = ["gpt-image-2", "gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini"]
TAMANHOS_IMAGEM_ATIVOS = ["auto", "1024x1024", "1536x1024", "1024x1536"]
QUALIDADES_IMAGEM_ATIVAS = ["low", "medium", "high", "auto"]
# Só o preço de saída — a estimativa mostrada antes de gerar não inclui as imagens de referência
# (o custo real, que inclui isso, só é conhecido depois da chamada; ver NUCLEO.md Operação 3).
PRECOS_SAIDA_IMAGEM_POR_TOKEN_USD = {
    "gpt-image-2": 30.00 / 1_000_000,
    "gpt-image-1.5": 32.00 / 1_000_000,
    "gpt-image-1": 40.00 / 1_000_000,
    "gpt-image-1-mini": 8.00 / 1_000_000,
}
# Tokens de saída típicos por qualidade, em 1024x1024 (mesmo valor usado nos 4 modelos — a
# diferença de custo entre eles já está no preço por token, não neste número).
TOKENS_SAIDA_ESTIMADOS_POR_QUALIDADE = {"low": 272, "medium": 1056, "high": 4160, "auto": 1056}
MAX_IMAGENS_REFERENCIA = 16
FORMATOS_IMAGEM_ACEITOS = (".png", ".jpg", ".jpeg", ".webp")
TIMEOUT_GERAR_IMAGEM_S = 320  # gerar imagem demora bem mais que transcrever (núcleo usa 300s)

MENSAGENS_ERRO_IMAGEM = {
    "MODELO_INVALIDO": "Modelo de imagem inválido.",
    "TAMANHO_INVALIDO": "Tamanho de imagem inválido.",
    "QUALIDADE_INVALIDA": "Qualidade de imagem inválida.",
    "PROMPT_VAZIO": "Escreva um prompt antes de gerar.",
    "IMAGEM_AUSENTE": "Adicione ao menos uma imagem de referência.",
    "IMAGEM_VAZIA": "Uma das imagens de referência está vazia.",
    "IMAGENS_DEMAIS": f"No máximo {MAX_IMAGENS_REFERENCIA} imagens de referência.",
    "FORMATO_NAO_ACEITO": "Formato não aceito — use PNG, JPG ou WEBP.",
    "ARQUIVO_MUITO_GRANDE": "Uma das imagens passa do limite de 50 MB.",
    "SEM_CHAVE": "O núcleo não tem chave da OpenAI configurada.",
    "FALHA_AUTENTICACAO": "Chave da OpenAI inválida no núcleo.",
    "SEM_CONEXAO": "Não foi possível conectar à API da OpenAI.",
    "API_RECUSOU": "A API da OpenAI recusou a geração — revise o prompt e as imagens.",
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
/* D-32: sem moldura e com fundo translúcido — no modo compacto só o círculo do botão aparece na
   tela; quem pinta o fundo visível na janela cheia é o cartão. */
QWidget#janelaDitado {{ background: transparent; }}
QFrame#cartaoGravacao {{
  background-color: {PALETA['fundo_cartao']};
  border: 1px solid {PALETA['borda_cartao']};
  border-radius: 8px;
}}
QFrame#painelConfig, QFrame#painelPopupRequisicao, QFrame#painelLogin {{
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
  background-color: {PALETA['fundo_cartao']}; color: {PALETA['texto']};
}}
QComboBox:disabled {{ color: {PALETA['texto_dica']}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
  background-color: {PALETA['fundo_cartao']};
  color: {PALETA['texto']};
  border: 1px solid {PALETA['borda_campo']};
  selection-background-color: {PALETA['azul']};
  selection-color: white;
  outline: none;
}}
QComboBox QAbstractItemView:disabled {{ color: {PALETA['texto_dica']}; }}
QMenu {{
  background-color: {PALETA['fundo_cartao']};
  color: {PALETA['texto']};
  border: 1px solid {PALETA['borda_campo']};
}}
QMenu::item {{ padding: 6px 16px; }}
QMenu::item:selected {{ background-color: {PALETA['azul']}; color: white; }}
QScrollArea {{ background-color: {PALETA['fundo_cartao']}; border: none; }}
QScrollArea > QWidget > QWidget {{ background-color: {PALETA['fundo_cartao']}; }}
QScrollBar:vertical {{ background: {PALETA['fundo_cartao']}; width: 10px; margin: 0px; }}
QScrollBar::handle:vertical {{ background: {PALETA['borda_campo']}; border-radius: 5px; min-height: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ background: {PALETA['fundo_cartao']}; height: 10px; margin: 0px; }}
QScrollBar::handle:horizontal {{ background: {PALETA['borda_campo']}; border-radius: 5px; min-width: 20px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
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


def migrar_config(dados):
    """Etapa 5: um config de antes do núcleo remoto (sem `url_nucleo_imagem`) vira o novo. O
    `url_nucleo` antigo — o núcleo local — passa a ser o da imagem, e o de ditado/consumo vira o
    remoto. Tudo o mais que o usuário configurou (atalho, dispositivo, modelo, pasta de imagens…)
    fica como está. Devolve (dados, migrou)."""
    if not isinstance(dados, dict) or "url_nucleo_imagem" in dados:
        return dados, False
    novos = dict(dados)
    novos["url_nucleo_imagem"] = dados.get("url_nucleo") or URL_NUCLEO_LOCAL_PADRAO
    novos["url_nucleo"] = URL_NUCLEO_REMOTO_PADRAO
    return novos, True


def carregar_config():
    if not os.path.exists(CAMINHO_CONFIG):
        return dict(CONFIG_PADRAO)
    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados, migrou = migrar_config(dados)
        config = dict(CONFIG_PADRAO)
        config.update({chave: dados[chave] for chave in CONFIG_PADRAO if chave in dados})
    except (json.JSONDecodeError, OSError, AttributeError, TypeError):
        return dict(CONFIG_PADRAO)
    if migrou:
        try:
            salvar_config(config)
            log.info("config: migrado para o núcleo remoto (url_nucleo_imagem = o url_nucleo antigo)")
        except OSError:
            log.info("config: migrado só em memória — não foi possível gravar config.json")
    return config


def salvar_config(config):
    # newline="\n": sem isto, o modo texto do Windows troca \n por \r\n na escrita — e o
    # `config.json` versionado é LF, então todo `git status` mostrava uma diferença fantasma
    # (conteúdo idêntico, só o fim de linha). A quebra de linha final depois do `json.dump` (que
    # não escreve uma sozinho) fecha a mesma regra que `.gitattributes` passa a exigir dos `.json`.
    with open(CAMINHO_CONFIG, "w", encoding="utf-8", newline="\n") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")


class ErroSessao(Exception):
    """Não há sessão válida: é preciso entrar de novo (sem login, ou renovação recusada pelo Auth)."""


class ErroRedeSessao(Exception):
    """O Auth do Supabase não respondeu — a sessão guardada continua valendo."""


def caminho_sessao():
    """Fora do repositório, de propósito: %APPDATA%\\agentes-base\\sessao.json no Windows."""
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "agentes-base", "sessao.json")


def url_exige_login(config, url):
    """Só o núcleo remoto (as funções do Supabase) exige login; o local aceita sem cabeçalho."""
    base = (config.get("supabase_url") or SUPABASE_URL_PADRAO).rstrip("/")
    return bool(url) and url.startswith(base)


def _cabecalho_autorizacao(token):
    return {"Authorization": f"Bearer {token}"} if token else {}


class Sessao:
    """Login no Supabase Auth, guardado entre aberturas do app e renovado sozinho.

    Guarda em disco só o que a API devolve (token de acesso, token de renovação, validade) e o
    e-mail para mostrar em Configurações — a senha nunca. Usada pelas threads de rede: um lock
    serializa renovações (o Supabase troca o token de renovação a cada uso, e duas renovações
    simultâneas com o mesmo token derrubariam a sessão). Nada daqui vai para o log além do
    evento e do código HTTP."""

    def __init__(self, config, caminho=None):
        self._config = config
        self.caminho = caminho or caminho_sessao()
        self._lock = threading.RLock()
        self._access = ""
        self._refresh = ""
        self._expira_em = 0.0
        self.email = ""
        self._carregar()

    # --- disco ---
    def _carregar(self):
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except FileNotFoundError:
            return
        except (OSError, ValueError):
            log.info("sessao: arquivo de sessão ilegível — ignorado, será pedido login")
            return
        if not isinstance(dados, dict):
            return
        self._access = dados.get("access_token") or ""
        self._refresh = dados.get("refresh_token") or ""
        try:
            self._expira_em = float(dados.get("expira_em") or 0)
        except (TypeError, ValueError):
            self._expira_em = 0.0
        self.email = dados.get("email") or ""

    def _salvar(self):
        pasta = os.path.dirname(self.caminho)
        os.makedirs(pasta, exist_ok=True)
        temporario = self.caminho + ".tmp"
        with open(temporario, "w", encoding="utf-8", newline="\n") as f:
            json.dump(
                {
                    "access_token": self._access, "refresh_token": self._refresh,
                    "expira_em": self._expira_em, "email": self.email,
                },
                f, ensure_ascii=False, indent=2,
            )
            f.write("\n")
        try:
            os.chmod(temporario, 0o600)  # no Windows é quase inócuo; a pasta já é do usuário
        except OSError:
            pass
        os.replace(temporario, self.caminho)

    def _limpar(self, manter_email=False):
        self._access = ""
        self._refresh = ""
        self._expira_em = 0.0
        if not manter_email:
            self.email = ""
        try:
            os.remove(self.caminho)
        except FileNotFoundError:
            pass
        except OSError:
            log.info("sessao: não foi possível apagar o arquivo de sessão")

    # --- estado ---
    @property
    def ativa(self):
        with self._lock:
            return bool(self._refresh)

    # --- Auth ---
    def _post_token(self, tipo, corpo):
        base = (self._config.get("supabase_url") or SUPABASE_URL_PADRAO).rstrip("/")
        chave = self._config.get("supabase_chave_publicavel") or SUPABASE_CHAVE_PUBLICAVEL_PADRAO
        try:
            return requests.post(
                f"{base}/auth/v1/token?grant_type={tipo}",
                json=corpo,
                headers={"apikey": chave, "Content-Type": "application/json"},
                timeout=TIMEOUT_AUTH_S,
            )
        except requests.exceptions.RequestException:
            raise ErroRedeSessao() from None

    def _aplicar(self, resposta, email_digitado=""):
        try:
            dados = resposta.json()
        except ValueError:
            raise ErroSessao("Resposta inesperada do Supabase ao entrar.") from None
        access = dados.get("access_token") if isinstance(dados, dict) else None
        refresh = dados.get("refresh_token") if isinstance(dados, dict) else None
        if not access or not refresh:
            raise ErroSessao("Resposta inesperada do Supabase ao entrar.")
        try:
            expira_em = float(dados.get("expires_at") or 0) or time.time() + float(dados.get("expires_in") or 3600)
        except (TypeError, ValueError):
            expira_em = time.time() + 3600
        usuario = dados.get("user") if isinstance(dados.get("user"), dict) else {}
        self._access, self._refresh, self._expira_em = access, refresh, expira_em
        self.email = usuario.get("email") or email_digitado or self.email
        try:
            self._salvar()
        except OSError:
            log.info("sessao: não foi possível gravar o arquivo de sessão — vale só até fechar o app")

    def entrar(self, email, senha):
        resposta = self._post_token("password", {"email": email, "password": senha})
        if resposta.status_code == 200:
            with self._lock:
                self._aplicar(resposta, email)
            log.info("sessao: login ok")
            return
        try:
            corpo = resposta.json()
            codigo = (corpo.get("error_code") or corpo.get("code") or "") if isinstance(corpo, dict) else ""
        except ValueError:
            codigo = ""
        log.info("sessao: login recusado http=%s codigo=%s", resposta.status_code, codigo)
        if codigo == "email_not_confirmed":
            raise ErroSessao("Este e-mail ainda não foi confirmado no Supabase.")
        if resposta.status_code == 429:
            raise ErroSessao("Muitas tentativas — espere um pouco e tente de novo.")
        if resposta.status_code in (400, 401, 422):
            raise ErroSessao("E-mail ou senha incorretos.")
        raise ErroSessao(f"O Supabase recusou o login (HTTP {resposta.status_code}).")

    def token(self):
        """Token de acesso válido; renova antes, se faltar menos de RENOVAR_SESSAO_ANTES_S."""
        with self._lock:
            if not self._refresh:
                raise ErroSessao("sem sessão")
            if self._access and self._expira_em - time.time() > RENOVAR_SESSAO_ANTES_S:
                return self._access
            return self._renovar()

    def renovar(self, token_rejeitado=None):
        """Renova já (depois de um 401). Se outra thread renovou enquanto esta esperava o lock, o
        token novo dela serve — não gasta mais uma renovação."""
        with self._lock:
            if not self._refresh:
                raise ErroSessao("sem sessão")
            if (
                token_rejeitado is not None and self._access and self._access != token_rejeitado
                and self._expira_em - time.time() > RENOVAR_SESSAO_ANTES_S
            ):
                return self._access
            return self._renovar()

    def _renovar(self):
        resposta = self._post_token("refresh_token", {"refresh_token": self._refresh})
        if resposta.status_code == 200:
            self._aplicar(resposta)
            log.info("sessao: renovada")
            return self._access
        if resposta.status_code in (400, 401, 403):
            log.info("sessao: renovação recusada http=%s — pedir login", resposta.status_code)
            self._limpar(manter_email=True)
            raise ErroSessao(MENSAGEM_SESSAO_EXPIRADA)
        log.info("sessao: renovação falhou http=%s — sessão mantida", resposta.status_code)
        raise ErroRedeSessao()

    def sair(self):
        with self._lock:
            self._limpar()
        log.info("sessao: saiu da conta")


def chamar_com_sessao(sessao, exigir, enviar):
    """Faz a chamada com `Authorization: Bearer <token>` quando há sessão. Se ela voltar 401,
    renova uma vez e repete (`enviar` é chamado de novo — ele reabre os arquivos que envia).

    `exigir` = a URL só atende com login (núcleo remoto): sem sessão, ou com renovação recusada,
    levanta ErroSessao; com o Auth fora do ar, ErroRedeSessao. Sem `exigir` (núcleo local), a
    chamada segue sem cabeçalho nesses casos — exatamente como era antes da Etapa 5."""
    token = None
    if sessao is not None:
        try:
            token = sessao.token()
        except (ErroSessao, ErroRedeSessao):
            if exigir:
                raise
    resposta = enviar(_cabecalho_autorizacao(token))
    if resposta.status_code == 401 and token and sessao is not None:
        try:
            novo = sessao.renovar(token_rejeitado=token)
        except (ErroSessao, ErroRedeSessao):
            if exigir:
                raise
            return resposta
        resposta.close()
        resposta = enviar(_cabecalho_autorizacao(novo))
    return resposta


class TrabalhoLogin(QThread):
    """Login fora da thread do Qt. A senha vive só aqui, e só até a chamada terminar."""

    ok = Signal()
    falhou = Signal(str)

    def __init__(self, sessao, email, senha):
        super().__init__()
        self.sessao = sessao
        self.email = email
        self._senha = senha

    def run(self):
        try:
            self.sessao.entrar(self.email, self._senha)
        except ErroSessao as erro:
            self.falhou.emit(str(erro))
            return
        except ErroRedeSessao:
            self.falhou.emit("Não foi possível conectar ao Supabase — verifique a rede.")
            return
        finally:
            self._senha = None
        self.ok.emit()


def copiar_para_area_de_transferencia(texto):
    """Único ponto de escrita no clipboard (D-11) — é o pedaço que B-22 vai trocar depois."""
    QGuiApplication.clipboard().setText(texto)


def formatar_usd(valor):
    """SPEC-002 G1: sempre com quatro casas — mesmo formato de transcritor/frontend/index.html."""
    return f"US$ {valor or 0:.4f}"


def formatar_usd_compacto(valor):
    """G3: preço acima do ponto, na escala 'minuto' — versão sem o 'US' do formatarUsd do JS."""
    return f"${valor or 0:.4f}"


def listar_dispositivos_entrada():
    try:
        return [d for d in sd.query_devices() if d.get("max_input_channels", 0) > 0]
    except Exception:
        return []


def _escolher_passo_eixo(px_por_ms):
    """Menor passo da escada cujo espaçamento em pixels já respeita o alvo (SPEC-002 G3)."""
    for passo in ESCADA_PASSOS_EIXO_TEMPO:
        if passo["ms"] * px_por_ms >= ESPACAMENTO_MINIMO_PX_ROTULO_EIXO:
            return passo
    return ESCADA_PASSOS_EIXO_TEMPO[-1]


def _primeira_marca_alinhada(data, passo):
    """Primeira marca >= data, alinhada a uma fronteira de tempo local (nunca múltiplo cru de
    epoch — ver ESCADA_PASSOS_EIXO_TEMPO). O carry entre unidades (ex.: segundo 51 + passo 10 vira
    o minuto seguinte) fica a cargo da soma de timedelta, que já normaliza."""
    d = data.replace(microsecond=0)
    unidade, multiplo = passo["unidade"], passo["multiplo"]
    if unidade == "segundo":
        base = d.replace(second=0)
        n = math.ceil((d - base).total_seconds() / multiplo)
        return base + timedelta(seconds=n * multiplo)
    if unidade == "minuto":
        base = d.replace(second=0, minute=0)
        n = math.ceil((d.replace(second=0) - base).total_seconds() / 60 / multiplo)
        return base + timedelta(minutes=n * multiplo)
    if unidade == "hora":
        base = d.replace(second=0, minute=0, hour=0)
        n = math.ceil((d.replace(second=0, minute=0) - base).total_seconds() / 3600 / multiplo)
        return base + timedelta(hours=n * multiplo)
    base = d.replace(hour=0, minute=0, second=0)
    if base < d:
        base += timedelta(days=1)
    return base


def _proxima_marca_eixo(marca, passo):
    unidade, multiplo = passo["unidade"], passo["multiplo"]
    if unidade == "segundo":
        return marca + timedelta(seconds=multiplo)
    if unidade == "minuto":
        return marca + timedelta(minutes=multiplo)
    if unidade == "hora":
        return marca + timedelta(hours=multiplo)
    return marca + timedelta(days=multiplo)


def _formatar_data_curta_eixo(d):
    return f"{d.day:02d}/{d.month:02d}"


def _rotulo_horario_eixo(d, passo):
    """Precisão do horário acompanha o passo — evita rótulo repetido quando o passo é mais fino
    que um minuto (ex.: '18:02' idêntico em vários ticks de 10s)."""
    if passo["unidade"] == "segundo":
        return f"{d.hour:02d}:{d.minute:02d}:{d.second:02d}"
    if passo["unidade"] == "minuto":
        return f"{d.hour:02d}:{d.minute:02d}"
    return f"{d.hour:02d}h"


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
    # D-32 3a volta — "Sair" no menu 3 pontos: sem moldura nao existe X para fechar. Icone proprio
    # (mesmo caso ja aberto por "enviar" e "imagem"), simbolo de energia.
    "sair": (
        '<path d="M13 3h-2v10h2V3Zm4.83 2.17-1.42 1.42A6.92 6.92 0 0 1 19 12a7 7 0 0 1-14 0 '
        '6.92 6.92 0 0 1 2.59-5.41L6.17 5.17A8.93 8.93 0 0 0 3 12a9 9 0 0 0 18 0 8.93 8.93 0 0 '
        '0-3.17-6.83Z"/>'
    ),
    # Etapa 5 — "Sair da conta" no menu ⋮: ícone próprio (mesmo caso de "sair" e "imagem"), pessoa.
    "conta": (
        '<path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4Z"/>'
    ),
    # Abrir planejamento (2026-09-25, pedido direto): barras escalonadas, como uma linha do tempo.
    "planejamento": '<path d="M3 5h10v3H3V5Zm4 5.5h12v3H7v-3ZM11 16h10v3H11v-3Z"/>',
    # D-31 — Gerar imagem: fora da paridade (D-27), ícone próprio (mesmo caso já aberto por "enviar").
    "imagem": (
        '<path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2Z'
        'M8.5 13.5 11 16.51 14.5 12l4.5 6H5l3.5-4.5Z"/>'
    ),
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
    # Etapa 5: sem sessão válida para o núcleo remoto. O áudio NÃO é apagado — a janela guarda o
    # pedido e o reenvia depois do login.
    sessao_expirada = Signal()

    def __init__(self, url_nucleo, caminho_arquivo, nome_arquivo, modelo, streaming, texto_base, apagar_arquivo_depois,
                 sessao=None, exigir_login=False):
        super().__init__()
        self.url = url_nucleo.rstrip("/") + "/transcrever"
        self.caminho_arquivo = caminho_arquivo
        self.nome_arquivo = nome_arquivo
        self.modelo = modelo
        self.streaming = streaming
        self.texto_base = texto_base
        self.apagar_arquivo_depois = apagar_arquivo_depois
        self.sessao = sessao
        self.exigir_login = exigir_login
        self._manter_arquivo = False

    def run(self):
        try:
            self._executar()
        finally:
            if self.apagar_arquivo_depois and not self._manter_arquivo:
                try:
                    os.remove(self.caminho_arquivo)
                except OSError:
                    pass

    def _separador(self):
        return "\n" if self.texto_base and not self.texto_base.endswith("\n") else ""

    def _enviar(self, cabecalhos):
        with open(self.caminho_arquivo, "rb") as f:
            return requests.post(
                self.url,
                files={"audio": (self.nome_arquivo, f, "application/octet-stream")},
                data={"modelo": self.modelo, "stream": "true" if self.streaming else "false"},
                headers=cabecalhos,
                timeout=130,
                stream=self.streaming,
            )

    def _sessao_expirou(self):
        self._manter_arquivo = True
        self.sessao_expirada.emit()

    def _executar(self):
        try:
            resposta = chamar_com_sessao(self.sessao, self.exigir_login, self._enviar)
        except ErroSessao:
            self._sessao_expirou()
            return
        except (requests.exceptions.RequestException, ErroRedeSessao):
            self.falhou.emit(f"Não foi possível conectar ao núcleo em {self.url}.", "")
            return

        if resposta.status_code == 401 and self.exigir_login:
            self._sessao_expirou()  # 401 do gateway ou NAO_AUTENTICADO, mesmo depois de renovar
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
    sessao_expirada = Signal()  # Etapa 5 — ver TrabalhoTranscricao

    def __init__(self, url_nucleo, sessao=None, exigir_login=False):
        super().__init__()
        self.url = url_nucleo.rstrip("/") + "/consumo"
        self.sessao = sessao
        self.exigir_login = exigir_login

    def run(self):
        try:
            resposta = chamar_com_sessao(
                self.sessao, self.exigir_login,
                lambda cabecalhos: requests.get(self.url, headers=cabecalhos, timeout=TIMEOUT_CONSUMO_S),
            )
        except ErroSessao:
            self.sessao_expirada.emit()
            return
        except (requests.exceptions.RequestException, ErroRedeSessao):
            self.falhou.emit(f"Não foi possível conectar ao núcleo em {self.url}.")
            return
        if resposta.status_code == 401 and self.exigir_login:
            self.sessao_expirada.emit()
            return
        if resposta.status_code != 200:
            self.falhou.emit(f"O núcleo respondeu com erro (HTTP {resposta.status_code}) ao consultar o consumo.")
            return
        try:
            self.sucesso.emit(resposta.json())
        except ValueError:
            self.falhou.emit("Resposta inesperada do núcleo ao consultar consumo.")


def _mime_da_imagem(caminho):
    extensao = os.path.splitext(caminho)[1].lower()
    return {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
    }.get(extensao, "application/octet-stream")


class TrabalhoGeracaoImagem(QThread):
    """Chama POST /gerar-imagem fora da thread do Qt (D-31) — igual timeout generoso do núcleo
    (gerar imagem demora bem mais que transcrever).

    Decodifica o base64 e **salva o arquivo em disco aqui dentro**, antes de emitir qualquer
    sinal — achado no uso real: o app derrubou duas vezes com uma falha nativa do Qt
    (`Qt6Core.dll`, sempre no mesmo endereço, fora do alcance de um `try/except` Python) bem na
    janela de tempo em que a thread de rede termina e entrega o resultado à thread da GUI. Salvar
    aqui, com E/S pura de arquivo (sem nenhuma chamada a widget), tira a persistência do que já foi
    pago da dependência de a GUI sobreviver para processar o sinal — e o sinal de sucesso passa a
    carregar só strings/números pequenos, não a imagem inteira em base64 (que para uma imagem
    1024×1024 real passa de 1 MB), reduzindo o que atravessa a fila entre as duas threads."""

    sucesso = Signal(str, str, float)  # caminho_salvo ("" se não deu para salvar), formato, custo_usd
    falhou = Signal(str, str)  # mensagem legível, codigo (pode vir vazio)
    sessao_expirada = Signal()  # Etapa 5 — só se `url_nucleo_imagem` apontar para o remoto

    def __init__(self, url_nucleo, caminhos_imagens, prompt, modelo, tamanho, qualidade, pasta_saida,
                 sessao=None, exigir_login=False):
        super().__init__()
        self.url = url_nucleo.rstrip("/") + "/gerar-imagem"
        # Etapa 5: com sessão, a chamada leva o token — e o núcleo local registra o consumo da
        # imagem no banco, como o usuário, em vez dos .jsonl. Sem sessão, segue como antes.
        self.sessao = sessao
        self.exigir_login = exigir_login
        self.caminhos_imagens = list(caminhos_imagens)
        self.prompt = prompt
        self.modelo = modelo
        self.tamanho = tamanho
        self.qualidade = qualidade
        self.pasta_saida = pasta_saida
        # Lido pela GUI depois do sinal `sucesso` (não é parâmetro do sinal — não passa pela fila
        # entre threads): só precisa dos bytes se o salvamento automático abaixo falhar, para
        # "Salvar como…" ainda funcionar; no caminho comum (salvou), a GUI relê do próprio arquivo.
        self.imagem_bytes = None

    def _enviar(self, cabecalhos):
        arquivos_abertos = []
        try:
            arquivos_multipart = []
            for caminho in self.caminhos_imagens:
                f = open(caminho, "rb")
                arquivos_abertos.append(f)
                arquivos_multipart.append(
                    ("imagens", (os.path.basename(caminho), f, _mime_da_imagem(caminho)))
                )
            return requests.post(
                self.url,
                files=arquivos_multipart,
                data={
                    "prompt": self.prompt, "modelo": self.modelo,
                    "tamanho": self.tamanho, "qualidade": self.qualidade,
                },
                headers=cabecalhos,
                timeout=TIMEOUT_GERAR_IMAGEM_S,
            )
        finally:
            for f in arquivos_abertos:
                f.close()

    def run(self):
        try:
            resposta = chamar_com_sessao(self.sessao, self.exigir_login, self._enviar)
        except ErroSessao:
            self.sessao_expirada.emit()
            self.falhou.emit(MENSAGEM_SESSAO_EXPIRADA, "NAO_AUTENTICADO")
            return
        except (requests.exceptions.RequestException, ErroRedeSessao):
            self.falhou.emit(f"Não foi possível conectar ao núcleo em {self.url}.", "")
            return
        if resposta.status_code == 401 and self.exigir_login:
            self.sessao_expirada.emit()
            self.falhou.emit(MENSAGEM_SESSAO_EXPIRADA, "NAO_AUTENTICADO")
            return

        if resposta.status_code != 200:
            self._emitir_erro_http(resposta)
            return
        try:
            dados = resposta.json()
        except ValueError:
            self.falhou.emit("Resposta inesperada do núcleo.", "")
            return

        try:
            imagem_bytes = base64.b64decode(dados.get("imagem_b64") or "")
        except (ValueError, TypeError):
            self.falhou.emit("Resposta inesperada do núcleo — imagem inválida.", "")
            return
        formato = dados.get("formato") or "png"
        custo_usd = float(dados.get("custo_usd") or 0.0)

        caminho_salvo = ""
        try:
            os.makedirs(self.pasta_saida, exist_ok=True)
            nome = datetime.now().strftime("%Y-%m-%d_%H%M%S") + "." + formato
            caminho_tentativa = os.path.join(self.pasta_saida, nome)
            with open(caminho_tentativa, "wb") as arquivo:
                arquivo.write(imagem_bytes)
            caminho_salvo = caminho_tentativa
        except OSError:
            self.imagem_bytes = imagem_bytes  # só guarda em memória se não deu para salvar sozinho

        self.sucesso.emit(caminho_salvo, formato, custo_usd)

    def _emitir_erro_http(self, resposta):
        try:
            corpo = resposta.json()
        except ValueError:
            self.falhou.emit(f"Erro do núcleo (HTTP {resposta.status_code}).", "")
            return
        codigo = corpo.get("codigo") or ""
        mensagem = MENSAGENS_ERRO_IMAGEM.get(codigo, corpo.get("detail") or "Erro desconhecido do núcleo.")
        self.falhou.emit(mensagem, codigo)


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
        self._icone_microfone = pixmap_svg("microfone", "white", 28)
        self._icone_quadrado = pixmap_svg("quadrado", "white", 28)
        self._timer_spinner = QTimer(self)
        self._timer_spinner.timeout.connect(self._girar)
        self.camada_pulso = None  # anexada por fora (B.2) — quem desenha pulso/realce é ela
        # D-32: no modo compacto o botão é a janela inteira; sem barra de título, arrastar a janela
        # tem de sair daqui — e o arrasto não pode virar clique (que alternaria a gravação).
        self._pos_press_arraste = None
        self._arrastando = False
        self.definir_estado("parado")

    def anexar_camada_pulso(self, camada):
        """B.2 — o pulso do gravando e o realce do arrastar crescem além do círculo de 72px;
        num widget de tamanho fixo o Qt corta o que passa da borda. Quem desenha isso é uma camada
        própria, sobreposta e maior, por baixo deste botão no empilhamento (ver CamadaPulso)."""
        self.camada_pulso = camada

    def definir_realce_arrastar(self, ativo):
        """E2 — enquanto um arquivo de áudio paira sobre o botão, ele mostra que vai aceitar."""
        if self.camada_pulso is not None:
            self.camada_pulso.definir_realce_arrastar(ativo)

    def definir_estado(self, estado):
        self._estado = estado
        self._timer_spinner.stop()
        if estado == "processando":
            # SPEC-002 I: anel de 1,6rem, volta a cada 0,8s
            self._angulo_spinner = 0
            self._timer_spinner.start(20)
        self.setEnabled(estado != "processando")
        rotulo = {"parado": "Iniciar gravação", "gravando": "Parar gravação", "processando": "Processando…"}[estado]
        self.setToolTip(rotulo)
        self.setAccessibleName(rotulo)
        if self.camada_pulso is not None:
            self.camada_pulso.definir_estado(estado)
        self.update()

    # --- arrastar a janela pelo próprio botão (D-32) ------------------------------
    def _janela_arrastavel(self):
        janela = self.window()
        return janela if hasattr(janela, "arraste_iniciar") else None

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self._pos_press_arraste = evento.globalPosition().toPoint()
            self._arrastando = False
        super().mousePressEvent(evento)

    def mouseMoveEvent(self, evento):
        if self._pos_press_arraste is not None and (evento.buttons() & Qt.LeftButton):
            pos = evento.globalPosition().toPoint()
            janela = self._janela_arrastavel()
            if janela is not None and (
                self._arrastando
                or (pos - self._pos_press_arraste).manhattanLength() >= LIMIAR_ARRASTE_PX
            ):
                if not self._arrastando:
                    # ancora no ponto do press, não no de agora: a janela não dá o pulo do limiar
                    janela.arraste_iniciar(self._pos_press_arraste)
                    self._arrastando = True
                janela.arraste_mover(pos)
                evento.accept()
                return
        super().mouseMoveEvent(evento)

    def mouseReleaseEvent(self, evento):
        if self._arrastando:
            # arrastou: solta a janela onde está e engole o clique (não alterna a gravação)
            self._arrastando = False
            self._pos_press_arraste = None
            janela = self._janela_arrastavel()
            if janela is not None:
                janela.arraste_fim()
            self.setDown(False)
            evento.accept()
            return
        self._pos_press_arraste = None
        super().mouseReleaseEvent(evento)

    def _girar(self):
        # 360 graus a cada CICLO_SPINNER_PROCESSANDO_MS, com tick de 20ms
        passo = 360 * 20 / CICLO_SPINNER_PROCESSANDO_MS
        self._angulo_spinner = (self._angulo_spinner + passo) % 360
        self.update()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        raio = min(self.width(), self.height()) / 2 - 2
        cx, cy = self.width() / 2, self.height() / 2

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


class CamadaPulso(QWidget):
    """B.2 — pulso do gravando e realce do arrastar, numa camada própria sobre o BotaoGravar.

    O anel cresce a 34 x 1,35 ≈ 46px de raio — precisaria de ~92px de widget; o botão continua
    72 x 72 (o trio não se mexe). Filho do cartão (não do botão), WA_TransparentForMouseEvents,
    centralizado sobre o botão a cada resize, por baixo dele no empilhamento — só assim o anel tem
    espaço para crescer sem inflar o botão nem disparar o gate J1/J2."""

    TAMANHO = 110

    def __init__(self, botao, parent):
        super().__init__(parent)
        self._botao = botao
        self.setFixedSize(self.TAMANHO, self.TAMANHO)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # Sem isto, esta camada aparece como uma caixa quadrada opaca por cima do botão vizinho
        # (⋮) no Windows real — o mesmo "retângulo atrás do círculo" do BotaoGravar, mas aqui numa
        # camada 110x110: uma vez que a janela tem QSS aplicado, um QWidget puro sem stylesheet
        # próprio deixa de ser transparente por padrão (achado no uso real, 2026-08-27).
        self.setStyleSheet("background: transparent;")
        self._estado = "parado"
        self._fase_pulso = 0.0
        self._realce_arrastar = False
        # D-32 7ª volta: "o pulso está pedido, mas a troca de modo ainda não assentou". Ver
        # definir_estado e liberar_pulso_adiado.
        self._pulso_adiado = False
        self._timer_pulso = QTimer(self)
        self._timer_pulso.timeout.connect(self._pulsar)
        self.lower()

    def reposicionar(self):
        centro = self._botao.geometry().center()
        self.move(centro.x() - self.TAMANHO // 2, centro.y() - self.TAMANHO // 2)
        self.lower()

    def _janela_do_modo(self):
        """A JanelaDitado dona, quando ela existe e sabe responder sobre a transição de modo."""
        janela = self.window()
        return janela if hasattr(janela, "esta_em_transicao_de_modo") else None

    def definir_estado(self, estado):
        """D-32 7ª volta — a cor/ícone mudam na hora (quem faz isso é o BotaoGravar, já chamado);
        o que é ADIADO aqui é só o temporizador do anel pulsante.

        Por quê: este temporizador tem relógio próprio (30ms) e nasce no mesmo instante em que a
        transição compacto→expandido (240ms) começa, quando a gravação é iniciada a partir do
        compacto — `_definir_estado_botao` troca o estado do botão e logo em seguida chama
        `_aplicar_modo(True)`. Os dois repintam a mesma região da tela (a camada fica atrás do
        botão e é reposicionada a cada quadro da transição por `reposicionar()`), com relógios não
        sincronizados. É a explicação mais concreta encontrada por leitura de código para o "botão
        vermelho tentando desaparecer" que o usuário relata desde a 4ª volta. Agora o pulso só
        começa quando a transição assenta (`_assentar_modo` → `liberar_pulso_adiado`)."""
        self._estado = estado
        if estado != "gravando":
            # parar é seguro em qualquer momento — quem compete por quadro é começar.
            self._pulso_adiado = False
            self._timer_pulso.stop()
            self.update()
            return
        self._fase_pulso = 0.0
        janela = self._janela_do_modo()
        if janela is not None and janela.esta_em_transicao_de_modo():
            self._pulso_adiado = True
            self._timer_pulso.stop()
        else:
            self._pulso_adiado = False
            self._timer_pulso.start(INTERVALO_PULSO_MS)
        self.update()

    def liberar_pulso_adiado(self):
        """Chamado pela janela quando a troca de modo assenta (fim da animação, ou troca sem
        animação). Só liga o pulso se ele continua fazendo sentido — se a gravação já parou no meio
        da transição, não há nada para retomar."""
        if not self._pulso_adiado:
            return
        self._pulso_adiado = False
        if self._estado == "gravando" and not self._timer_pulso.isActive():
            self._timer_pulso.start(INTERVALO_PULSO_MS)
            self.update()

    def definir_realce_arrastar(self, ativo):
        self._realce_arrastar = ativo
        self.update()

    def _pulsar(self):
        passo = 30 / CICLO_PULSO_GRAVANDO_MS
        self._fase_pulso = (self._fase_pulso + passo) % 1.0
        self.update()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        raio_botao = min(self._botao.width(), self._botao.height()) / 2 - 2
        cx, cy = self.width() / 2, self.height() / 2

        if self._estado == "gravando":
            raio_pulso = raio_botao * (1 + 0.35 * self._fase_pulso)
            alfa_pulso = max(0, int(160 * (1 - self._fase_pulso)))
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QBrush(QColor(220, 38, 38, alfa_pulso)))
            pintor.drawEllipse(
                int(cx - raio_pulso), int(cy - raio_pulso), int(raio_pulso * 2), int(raio_pulso * 2)
            )

        if self._realce_arrastar:
            pintor.setBrush(Qt.NoBrush)
            pintor.setPen(QPen(QColor(PALETA["azul"]), 3))
            pintor.drawEllipse(
                int(cx - raio_botao - 4), int(cy - raio_botao - 4),
                int((raio_botao + 4) * 2), int((raio_botao + 4) * 2),
            )


class BarraAmplitude(QWidget):
    """80 barras, uma amostra a cada 60ms — cresce dos dois lados a partir do centro (A4 / SPEC-002 I)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # D-32 7ª volta: era 40 (2.5rem). O desenho das barras é proporcional à altura do
        # widget, então encolher aqui não corta nada — só deixa a faixa mais baixa.
        self.setFixedHeight(ALTURA_BARRA_AMPLITUDE)
        self._amostras = deque([0.0] * NUM_BARRAS, maxlen=NUM_BARRAS)
        # J2: o *espaço* fica reservado (setFixedHeight, sempre) — mas parada, o conteúdo some de
        # verdade (A4): uma fileira de pontinhos parada no repouso virou ruído permanente na tela,
        # relatado no uso em 2026-08-27. self._gravando é o que diferencia "reservar o lugar" de
        # "manter o desenho".
        self._gravando = False

    def reiniciar(self, gravando):
        self._gravando = gravando
        self._amostras = deque([0.0] * NUM_BARRAS, maxlen=NUM_BARRAS)
        self.update()

    def empurrar_amostra(self, rms):
        self._amostras.append(rms)
        self.update()

    def paintEvent(self, evento):
        if not self._gravando:
            return
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
    (B1-B3): cada chamada substitui a anterior na hora.

    B.5 — uma linha só, ancorada no centro do botão (cresce para os dois lados, então a âncora
    nunca sai do lugar): sem isso, quebrar em duas linhas empurraria o balão para cima a cada
    mensagem mais longa, e a posição passaria a depender do tamanho do texto."""

    CORES = {"confirmacao": PALETA["confirmacao"], "erro": PALETA["erro"]}
    ALTURA = 32
    MARGEM_JANELA = 16
    PADDING_HORIZONTAL = 20

    def __init__(self, ancora):
        super().__init__(ancora.parentWidget())
        self._ancora = ancora  # widget acima do qual o balão aparece (o botão de gravar)
        self._texto_completo = ""
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(False)
        self.setFixedHeight(self.ALTURA)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.esconder)

    def mostrar(self, tipo, texto, duracao_ms):
        cor = self.CORES.get(tipo, PALETA["texto"])
        self.setStyleSheet(
            f"QLabel {{ background-color: {cor}; color: white; border-radius: 6px; "
            f"padding: 0px {self.PADDING_HORIZONTAL // 2}px; font-size: 12px; }}"
        )
        self._texto_completo = texto
        self.setToolTip(texto)  # texto inteiro na dica, mesmo cortado com reticências na tela
        self._reposicionar()
        self.show()
        self.raise_()
        self._timer.stop()
        self._timer.start(duracao_ms)

    def _reposicionar(self):
        # O limite de largura tem de estar no mesmo referencial da posição: self.move() usa
        # coordenadas do parent em comum com a âncora (o cartão, não a janela) — usar a largura da
        # janela aqui faria o balão encostar nas bordas do cartão em vez de sobrar margem (achado
        # na conferência visual desta tarefa: o balão longo tocava os cantos arredondados do cartão).
        largura_disponivel = self.parentWidget().width() if self.parentWidget() else self._ancora.window().width()
        largura_maxima = max(60, largura_disponivel - self.MARGEM_JANELA)
        metrica = self.fontMetrics()
        largura_texto = metrica.horizontalAdvance(self._texto_completo) + self.PADDING_HORIZONTAL
        largura = min(largura_texto, largura_maxima)
        self.setText(metrica.elidedText(self._texto_completo, Qt.ElideRight, int(largura) - self.PADDING_HORIZONTAL))
        self.setFixedWidth(int(largura))

        geo_ancora = self._ancora.geometry()  # já nas coordenadas do parent em comum
        x = geo_ancora.center().x() - self.width() // 2
        y = geo_ancora.top() - self.height() - 8
        self.move(max(4, x), max(4, y))

    def esconder(self):
        self._timer.stop()
        self.hide()
        self._texto_completo = ""
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
        # Sem isto, um QWidget puro ignora "background-color" do QSS — o véu nunca escurecia o
        # conteúdo atrás (achado no uso real, confirmado por amostra de pixel: fundo ficava
        # (255,255,255) atrás do popup). Mesma regra que o comentário abaixo já explicava para
        # justificar por que o painel branco é QFrame, só que não tinha sido aplicada aqui.
        self.setAttribute(Qt.WA_StyledBackground, True)
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


class ItemMenuAvancado(QWidget):
    """Um item do menu ⋮, com espaço de verdade entre ícone e texto.

    O `QAction` nativo com ícone reserva uma coluna de largura fixa (dada pelo estilo/plataforma,
    não pelo tamanho do pixmap) — nem preencher o pixmap com margem transparente nem estilizar
    `QMenu::item` abrem esse espaço; o primeiro só faz o ícone reamostrar menor dentro da mesma
    coluna fixa (achado no uso real, 2026-08-27, depois de uma tentativa que piorou o ícone em vez
    de abrir a margem). Um `QWidgetAction` com este widget dá controle de verdade sobre o layout."""

    clicado = Signal()

    def __init__(self, nome_icone, texto, parent=None):
        super().__init__(parent)
        self.setObjectName("itemMenuAvancado")
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QWidget#itemMenuAvancado { background: transparent; }"
            f"QWidget#itemMenuAvancado:hover {{ background-color: {PALETA['bola_botao_hover']}; }}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 20, 8)
        layout.setSpacing(10)
        rotulo_icone = QLabel()
        rotulo_icone.setPixmap(pixmap_svg(nome_icone, PALETA["texto_secundario"], 18))
        layout.addWidget(rotulo_icone)
        layout.addWidget(QLabel(texto))
        layout.addStretch()

    def mousePressEvent(self, evento):
        self.clicado.emit()


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

        # Etapa 5 — com que conta o núcleo remoto está sendo usado ("Sair da conta" fica no menu ⋮).
        self.rotulo_conta = QLabel()
        self.rotulo_conta.setProperty("class", "dica")
        self.rotulo_conta.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout_form.addRow("Conta", self.rotulo_conta)
        self.atualizar_conta()

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

    def atualizar_conta(self):
        sessao = self.janela.sessao
        self.rotulo_conta.setText(sessao.email if sessao.ativa and sessao.email else "não conectado")

    def mostrar(self):
        self._popular_dispositivos()
        self.atualizar_conta()
        super().mostrar()


class PainelLogin(OverlayModal):
    """Etapa 5 — entrar no Supabase Auth, uma vez. Mesmo estilo dos sobrepostos que já existem
    (véu + painel branco centralizado, cabeçalho com ✕, clicar fora e Esc fecham): é um
    OverlayModal como Configurações. A senha é mascarada, sai do campo assim que o login é
    disparado e nunca é gravada."""

    entrou = Signal()

    def __init__(self, janela):
        super().__init__(janela)
        self.janela = janela
        self.painel.setObjectName("painelLogin")
        self.definir_largura_alvo(int(24 * 16))  # 24rem, igual a Configurações

        estilo_campo = (
            f"QLineEdit {{ border: 1px solid {PALETA['borda_campo']}; border-radius: 6px; padding: 6px 8px; "
            f"background-color: {PALETA['fundo_cartao']}; color: {PALETA['texto']}; "
            f"selection-background-color: {PALETA['azul']}; selection-color: white; }}"
            f"QLineEdit:disabled {{ color: {PALETA['texto_dica']}; }}"
        )
        self.rotulo_dica = QLabel(
            "O ditado e o consumo agora usam o núcleo remoto. Entre com a sua conta do Supabase — "
            "a senha não é guardada."
        )
        self.rotulo_dica.setProperty("class", "dica")
        self.rotulo_dica.setWordWrap(True)

        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("seu e-mail")
        self.campo_email.setStyleSheet(estilo_campo)
        self.campo_senha = QLineEdit()
        self.campo_senha.setPlaceholderText("senha")
        self.campo_senha.setEchoMode(QLineEdit.Password)
        self.campo_senha.setStyleSheet(estilo_campo)
        self.campo_email.returnPressed.connect(self.campo_senha.setFocus)
        self.campo_senha.returnPressed.connect(self._entrar)

        layout_form = QFormLayout()
        layout_form.addRow("E-mail", self.campo_email)
        layout_form.addRow("Senha", self.campo_senha)

        self.botao_entrar = QPushButton("Entrar")
        self.botao_entrar.clicked.connect(self._entrar)
        linha_botao = QHBoxLayout()
        linha_botao.addStretch()
        linha_botao.addWidget(self.botao_entrar)

        # Espaço da mensagem já reservado (J2): um erro não faz o painel pular de tamanho.
        self.rotulo_erro = QLabel("")
        self.rotulo_erro.setWordWrap(True)
        self.rotulo_erro.setMinimumHeight(34)
        self.rotulo_erro.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.rotulo_erro.setStyleSheet(f"color: {PALETA['erro']};")

        layout_painel = QVBoxLayout(self.painel)
        layout_painel.setContentsMargins(20, 20, 20, 20)
        layout_painel.setSpacing(10)
        layout_painel.addLayout(_cabecalho_painel("Entrar", self.esconder))
        layout_painel.addWidget(self.rotulo_dica)
        layout_painel.addLayout(layout_form)
        layout_painel.addLayout(linha_botao)
        layout_painel.addWidget(self.rotulo_erro)

        self._trabalho = None

    def mostrar(self, motivo=""):
        if not self.campo_email.text().strip():
            self.campo_email.setText(self.janela.sessao.email or "")
        self.campo_senha.clear()
        self.rotulo_erro.setText(motivo or "")
        self._liberar_botao()
        super().mostrar()
        self.janela.activateWindow()
        (self.campo_senha if self.campo_email.text().strip() else self.campo_email).setFocus()

    def _liberar_botao(self):
        if self._trabalho is None or not self._trabalho.isRunning():
            self.botao_entrar.setEnabled(True)
            self.botao_entrar.setText("Entrar")

    def _entrar(self):
        if self._trabalho is not None and self._trabalho.isRunning():
            return
        email = self.campo_email.text().strip()
        senha = self.campo_senha.text()
        if not email or not senha:
            self.rotulo_erro.setText("Preencha e-mail e senha.")
            return
        self.campo_senha.clear()  # a senha não fica nem no widget
        self.rotulo_erro.setText("")
        self.botao_entrar.setEnabled(False)
        self.botao_entrar.setText("Entrando…")
        self._trabalho = TrabalhoLogin(self.janela.sessao, email, senha)
        self._trabalho.ok.connect(self._ao_entrar)
        self._trabalho.falhou.connect(self._ao_falhar)
        self._trabalho.start()

    def _ao_entrar(self):
        self._trabalho = None
        self._liberar_botao()
        self.esconder()
        self.entrou.emit()

    def _ao_falhar(self, mensagem):
        self._trabalho = None
        self._liberar_botao()
        self.rotulo_erro.setText(mensagem)
        self.campo_senha.setFocus()


class GraficoBarrasDiario(QWidget):
    """G2 — uma coluna por dia: altura proporcional ao custo (normalizada pelo maior dia, mínimo
    de 4px para o dia quase-zero não sumir), rótulo 'mm-dd' embaixo, dica de foco com a data e o
    custo inteiro. Larguras e altura transcritas de transcritor/frontend/index.html (.barra-grafico-
    consumo, .coluna-grafico-consumo): barra 0.9rem arredondada só em cima, coluna 1.75rem, altura
    total 6rem."""

    ALTURA_BARRAS = int(6 * 16)  # 6rem
    ALTURA_ROTULO = 16
    LARGURA_BARRA = int(0.9 * 16)
    LARGURA_COLUNA = int(1.75 * 16)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(6)
        layout.addStretch(1)
        self._layout = layout
        self.setFixedHeight(self.ALTURA_BARRAS + self.ALTURA_ROTULO + 8)

    def definir_dias(self, por_dia):
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not por_dia:
            return
        maior_custo = max((float(d.get("custo_usd") or 0) for d in por_dia), default=0.0) or 0.000001
        for indice, dia in enumerate(por_dia):
            custo = float(dia.get("custo_usd") or 0)
            altura = max(4, round((custo / maior_custo) * self.ALTURA_BARRAS))

            coluna = QWidget()
            coluna.setFixedWidth(self.LARGURA_COLUNA)
            layout_coluna = QVBoxLayout(coluna)
            layout_coluna.setContentsMargins(0, 0, 0, 0)
            layout_coluna.setSpacing(4)
            layout_coluna.addStretch(1)

            barra = QFrame()
            barra.setFixedSize(self.LARGURA_BARRA, altura)
            raio = self.LARGURA_BARRA // 2
            barra.setStyleSheet(
                f"background-color: {PALETA['azul']}; border-top-left-radius: {raio}px; "
                f"border-top-right-radius: {raio}px;"
            )
            barra.setToolTip(f"{dia.get('data', '')}: {formatar_usd(custo)}")
            layout_coluna.addWidget(barra, alignment=Qt.AlignHCenter)

            rotulo = QLabel((dia.get("data") or "")[5:] or dia.get("data", ""))
            rotulo.setProperty("class", "dica")
            rotulo.setStyleSheet(f"color: {PALETA['texto_dica']}; font-size: 10px;")
            rotulo.setAlignment(Qt.AlignHCenter)
            layout_coluna.addWidget(rotulo)

            self._layout.insertWidget(indice, coluna)


class LinhaDoTempoConsumo(QWidget):
    """G3 — um ponto por requisição num eixo de tempo (não é gráfico de barras nem lista).

    Duas escalas com domínios diferentes, cada uma com navegação própria — "hora" mostra um dia
    civil por vez (largura = a do painel, nunca rola) e "minuto" é uma janela móvel de 3 min dentro
    das últimas 24h (largura fixa, sempre a mesma, rola horizontalmente). Transcrito de
    transcritor/frontend/index.html, comentário "--- Linha do tempo das requisições ---"
    (SPEC-002 G3) — inclusive os números calibrados (raio do ponto, alvo de clique, escada de
    passos do eixo)."""

    ALTURA = 110
    Y_PONTO = 68
    RAIO_PONTO = 4
    RAIO_ALVO = 14
    LARGURA_MINIMA_HORA = 480

    ponto_clicado = Signal(dict)
    estado_mudou = Signal()  # nav (dia/janela/roda) mudou — quem escuta atualiza os controles

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.ALTURA)
        self.setMouseTracking(True)
        # G4: o widget inteiro é um único ponto de tabulação (Tab entra/sai normalmente); dentro
        # dele, ←/→ movem um "ponto focado" próprio — não é o tabindex por ponto do SVG original,
        # que não existe num único QWidget pintado à mão (adaptação combinada com o PM).
        self.setFocusPolicy(Qt.StrongFocus)
        self._area = None
        self.requisicoes = []  # [{"quando": datetime, ...dados}], ordenadas
        self.escala = "hora"
        self.dia_selecionado = None  # date — só na escala "hora"
        self.ancora_fim_janela = None  # datetime — fim das últimas 24h, só na escala "minuto"
        self.deslocamento_janela = timedelta(0)
        self.ativada = False
        self._rolar_para_fim = True
        self._layout = None  # cache do último cálculo de desenho, para o paintEvent reusar
        self._indice_focado = None  # índice em layout["pontos"] (ordem de tempo) do ponto focado

    def anexar_area(self, area):
        """A QScrollArea que hospeda este widget — usada para medir a largura visível (escala
        'hora') e para rolar/ler a posição de rolagem (escala 'minuto')."""
        self._area = area

    # --- entrada de dados --------------------------------------------------------
    def definir_requisicoes(self, lista):
        requisicoes = []
        for item in lista or []:
            timestamp = item.get("timestamp")
            if not timestamp:
                continue
            try:
                quando = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
            except ValueError:
                continue
            requisicoes.append({**item, "quando": quando})
        requisicoes.sort(key=lambda r: r["quando"])
        self.requisicoes = requisicoes
        self.atualizar()

    def reiniciar_abertura(self):
        """Chamado a cada abertura do painel (equivalente a abrirConsumo no JS): recalcula a
        âncora da janela de 24h e o dia mostrado, e desativa a roda."""
        self.ancora_fim_janela = None
        self.dia_selecionado = None
        self.ativada = False
        self._rolar_para_fim = True

    # --- janela móvel de 24h (escala "minuto") ------------------------------------
    def _garantir_ancora_janela(self):
        if self.ancora_fim_janela is not None:
            return
        self.ancora_fim_janela = self.requisicoes[-1]["quando"] if self.requisicoes else datetime.now()
        self.deslocamento_janela = self._deslocamento_maximo()  # começa no trecho mais recente

    def _deslocamento_maximo(self):
        return timedelta(milliseconds=JANELA_24H_MS - LARGURA_JANELA_MINUTO_MS)

    def _limites_janela_24h(self):
        return self.ancora_fim_janela - timedelta(milliseconds=JANELA_24H_MS), self.ancora_fim_janela

    def _limites_janela_atual(self):
        inicio_24h, _ = self._limites_janela_24h()
        inicio = inicio_24h + self.deslocamento_janela
        return inicio, inicio + timedelta(milliseconds=LARGURA_JANELA_MINUTO_MS)

    def mover_janela_para(self, novo_deslocamento):
        maximo = self._deslocamento_maximo()
        novo_deslocamento = max(timedelta(0), min(maximo, novo_deslocamento))
        self.deslocamento_janela = novo_deslocamento
        self.atualizar()

    def deslocamento_maximo_segundos(self):
        return int(self._deslocamento_maximo().total_seconds())

    def pedir_ir_para_fim(self):
        """Botão 'Mais recente': um dos poucos casos em que o salto de rolagem é o que o usuário
        pediu de propósito (ver a flag _rolar_para_fim e o comentário em atualizar())."""
        self._rolar_para_fim = True
        self.mover_janela_para(self._deslocamento_maximo())

    # --- navegação por dia (escala "hora") ----------------------------------------
    def _garantir_dia_selecionado(self):
        if self.dia_selecionado is not None:
            return
        mais_recente = self.requisicoes[-1]["quando"] if self.requisicoes else datetime.now()
        self.dia_selecionado = mais_recente.date()

    def limites_dias_com_dados(self):
        if not self.requisicoes:
            return None, None
        dias = [r["quando"].date() for r in self.requisicoes]
        return min(dias), max(dias)

    def navegar_dia(self, delta_dias):
        if self.dia_selecionado is None:
            return
        alvo = self.dia_selecionado + timedelta(days=delta_dias)
        minimo, maximo = self.limites_dias_com_dados()
        if minimo is None or alvo < minimo or alvo > maximo:
            return  # fora do intervalo com dados: não navega
        self.dia_selecionado = alvo
        self.atualizar()

    # --- concordância entre as duas escalas sobre o período -----------------------
    def _sincronizar_minuto_com_dia(self):
        if self.dia_selecionado is None:
            return
        do_dia = [r for r in self.requisicoes if r["quando"].date() == self.dia_selecionado]
        if do_dia:
            self.ancora_fim_janela = do_dia[-1]["quando"]
        else:
            self.ancora_fim_janela = datetime.combine(self.dia_selecionado, hora_minima.min) + timedelta(
                milliseconds=DURACAO_DIA_MS
            )
        self.deslocamento_janela = self._deslocamento_maximo()

    def _sincronizar_dia_com_minuto(self):
        if self.ancora_fim_janela is None:
            return
        inicio, _ = self._limites_janela_atual()
        dia_da_janela = inicio.date()
        minimo, maximo = self.limites_dias_com_dados()
        self.dia_selecionado = dia_da_janela if minimo is None else min(maximo, max(minimo, dia_da_janela))

    def trocar_escala(self, nova_escala):
        if nova_escala == self.escala:
            return
        if nova_escala == "minuto":
            self._sincronizar_minuto_com_dia()
        else:
            self._sincronizar_dia_com_minuto()
        self.escala = nova_escala
        self._rolar_para_fim = True
        self.atualizar()

    # --- estado "ativada" (o que a roda faz sobre a linha do tempo) ---------------
    def ativar(self):
        if self.ativada:
            return
        self.ativada = True
        self.update()
        self.estado_mudou.emit()

    def desativar(self):
        if not self.ativada:
            return
        self.ativada = False
        self.update()
        self.estado_mudou.emit()

    def deslizar_janela(self, delta_y_estilo_web):
        """delta_y positivo avança no tempo, nas duas escalas (mesmo sentido de gesto)."""
        if self.escala == "minuto":
            px_por_ms = PX_POR_SEGUNDO_ESCALA_MINUTO / 1000
            self.mover_janela_para(self.deslocamento_janela + timedelta(milliseconds=delta_y_estilo_web / px_por_ms))
        else:
            self.navegar_dia(1 if delta_y_estilo_web > 0 else -1)

    # --- período visível, para os rótulos de navegação ----------------------------
    def periodo_dia_texto(self):
        if self.dia_selecionado is None:
            return ""
        return "Dia: " + self.dia_selecionado.strftime("%d/%m/%Y")

    def periodo_janela_texto(self):
        if self.ancora_fim_janela is None:
            return ""
        inicio_24h, fim_24h = self._limites_janela_24h()
        inicio, fim = self._limites_janela_atual()
        minutos = round(LARGURA_JANELA_MINUTO_MS / 60000)
        return (
            f"Janela: {inicio.strftime('%H:%M:%S')} – {fim.strftime('%H:%M:%S')} (recorte de {minutos} min) "
            f"— dentro das últimas 24h, de {inicio_24h.strftime('%d/%m/%Y %H:%M:%S')} a "
            f"{fim_24h.strftime('%d/%m/%Y %H:%M:%S')}."
        )

    def texto_estado_roda(self):
        if self.ativada:
            return (
                "Roda: deslizando a janela (Esc ou clique fora para sair)" if self.escala == "minuto"
                else "Roda: navegando entre dias (Esc ou clique fora para sair)"
            )
        return "Roda: trocando de escala (clique na linha do tempo para deslizar a janela)"

    # --- layout/desenho ------------------------------------------------------------
    def _largura_viewport(self):
        if self._area is not None:
            return self._area.viewport().width()
        return self.LARGURA_MINIMA_HORA

    def atualizar(self):
        # O recorte visível mudou (escala, dia, janela, dados) — um índice de foco antigo
        # apontaria para outro ponto sem o usuário pedir; melhor recomeçar do que focar errado.
        self._indice_focado = None
        if not self.requisicoes:
            self._layout = {"vazio_geral": True}
            self.setFixedWidth(max(self._largura_viewport(), self.LARGURA_MINIMA_HORA))
            self.update()
            self.estado_mudou.emit()
            return

        self._garantir_ancora_janela()
        self._garantir_dia_selecionado()

        if self.escala == "hora":
            inicio_dia = datetime.combine(self.dia_selecionado, hora_minima.min)
            fim_dia = inicio_dia + timedelta(milliseconds=DURACAO_DIA_MS)
            inicio = inicio_dia - timedelta(milliseconds=MARGEM_BORDA_DIA_MS)
            fim = fim_dia + timedelta(milliseconds=MARGEM_BORDA_DIA_MS)
            largura = max(self._largura_viewport(), self.LARGURA_MINIMA_HORA)
            visiveis = [r for r in self.requisicoes if inicio_dia <= r["quando"] < fim_dia]
        else:
            janela_inicio, janela_fim = self._limites_janela_atual()
            inicio = janela_inicio - timedelta(milliseconds=MARGEM_BORDA_JANELA_MS)
            fim = janela_fim + timedelta(milliseconds=MARGEM_BORDA_JANELA_MS)
            largura = ((LARGURA_JANELA_MINUTO_MS + 2 * MARGEM_BORDA_JANELA_MS) / 1000) * PX_POR_SEGUNDO_ESCALA_MINUTO
            visiveis = [r for r in self.requisicoes if janela_inicio <= r["quando"] <= janela_fim]

        duracao_ms = max(1.0, (fim - inicio).total_seconds() * 1000)
        px_por_ms = largura / duracao_ms

        passo = _escolher_passo_eixo(px_por_ms)
        marcas = []
        marca = _primeira_marca_alinhada(inicio, passo)
        dia_anterior_rotulado = None
        seguranca = 400  # a escada garante ~80px por marca; isto é só uma trava contra bug futuro
        while marca <= fim and seguranca > 0:
            x = (marca - inicio).total_seconds() * 1000 * px_por_ms
            dia_chave = (marca.year, marca.month, marca.day)
            mostrar_data = dia_chave != dia_anterior_rotulado
            dia_anterior_rotulado = dia_chave
            rotulo = (_formatar_data_curta_eixo(marca) + " " if mostrar_data else "") + _rotulo_horario_eixo(marca, passo)
            marcas.append((x, rotulo))
            marca = _proxima_marca_eixo(marca, passo)
            seguranca -= 1

        pontos = []
        x_ultimo = 0.0
        for req in sorted(visiveis, key=lambda r: r["quando"]):
            x = (req["quando"] - inicio).total_seconds() * 1000 * px_por_ms
            x_ultimo = max(x_ultimo, x)
            pontos.append((x, req))

        self._layout = {
            "vazio_geral": False,
            "marcas": marcas,
            "pontos": pontos,
            "vazio_visivel": len(visiveis) == 0,
        }
        self.setFixedWidth(int(largura))
        self.update()

        # Rolar para o último ponto só faz sentido em poucos momentos (abrir o painel, trocar de
        # escala, "Mais recente") — nos demais redesenhos (deslizar a janela) o container abre pelo
        # início do recorte novo; como o recorte se desloca de forma equivalente ao gesto, o
        # resultado visual é uma rolagem contínua, nunca um salto para o fim (bug clássico).
        if self._area is not None:
            barra = self._area.horizontalScrollBar()
            if self._rolar_para_fim:
                largura_visivel = max(self._area.viewport().width(), 1)
                barra.setValue(int(max(0.0, x_ultimo - largura_visivel + 40)))
                self._rolar_para_fim = False
            else:
                barra.setValue(0)

        self.estado_mudou.emit()

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(PALETA["fundo_cartao"]))  # G6: todo widget à mão pinta o próprio fundo

        if self.ativada:
            pintor.setPen(QPen(QColor(PALETA["roxo"]), 2))
            pintor.setBrush(Qt.NoBrush)
            pintor.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 4, 4)

        layout = self._layout
        if not layout or layout.get("vazio_geral"):
            pintor.setPen(QColor(PALETA["texto_dica"]))
            pintor.drawText(self.rect(), Qt.AlignCenter, "Nenhuma requisição registrada ainda.")
            return

        pintor.setPen(QPen(QColor("#e4e7eb"), 1))
        pintor.drawLine(0, self.Y_PONTO, self.width(), self.Y_PONTO)

        fonte = pintor.font()
        fonte.setPointSize(7)
        pintor.setFont(fonte)
        for x, rotulo in layout["marcas"]:
            pintor.setPen(QPen(QColor("#c3c2b7"), 1))
            pintor.drawLine(int(x), self.Y_PONTO, int(x), self.Y_PONTO + 5)
            pintor.setPen(QColor("#898781"))
            pintor.drawText(int(x - 30), self.Y_PONTO + 8, 60, 12, Qt.AlignCenter, rotulo)

        pontos = layout["pontos"]
        for indice, (x, req) in enumerate(pontos):
            if self.escala == "minuto":
                pintor.setPen(QColor(PALETA["texto_dica"]))
                pintor.drawText(
                    int(x - 30), self.Y_PONTO - 24, 60, 12, Qt.AlignCenter,
                    formatar_usd_compacto(req.get("custo_usd")),
                )
            pintor.setPen(QPen(QColor("white"), 2))
            pintor.setBrush(QBrush(QColor(PALETA["azul"])))
            pintor.drawEllipse(
                int(x - self.RAIO_PONTO), int(self.Y_PONTO - self.RAIO_PONTO),
                self.RAIO_PONTO * 2, self.RAIO_PONTO * 2,
            )

            # G4 — foco pelo teclado: contorno de 2px em #2563eb com 2px de folga, só visível com
            # o foco de verdade no widget (Tab), não só com um índice guardado.
            if self.hasFocus() and indice == self._indice_focado:
                raio_foco = self.RAIO_PONTO + 2
                pintor.setPen(QPen(QColor(PALETA["azul"]), 2))
                pintor.setBrush(Qt.NoBrush)
                pintor.drawEllipse(
                    int(x - raio_foco), int(self.Y_PONTO - raio_foco), raio_foco * 2, raio_foco * 2,
                )

        if layout["vazio_visivel"]:
            pintor.setPen(QColor(PALETA["texto_dica"]))
            texto = (
                "Nenhuma requisição neste recorte — deslize a janela para outro trecho das 24h."
                if self.escala == "minuto" else "Nenhuma requisição neste dia."
            )
            pintor.drawText(self.rect(), Qt.AlignCenter, texto)

    def mousePressEvent(self, evento):
        layout = self._layout
        pos = evento.position()
        if layout and not layout.get("vazio_geral"):
            for x, req in layout["pontos"]:
                dx, dy = pos.x() - x, pos.y() - self.Y_PONTO
                if dx * dx + dy * dy <= self.RAIO_ALVO ** 2:
                    self.ponto_clicado.emit(req)
                    return
        self.ativar()

    def wheelEvent(self, evento):
        if evento.modifiers() & Qt.ShiftModifier:
            # Shift+roda é o gesto nativo de rolagem horizontal — a roda pura fica reservada para
            # o zoom/deslizar abaixo (mesma divisão de papéis do index.html).
            if self._area is not None:
                barra = self._area.horizontalScrollBar()
                barra.setValue(barra.value() - evento.angleDelta().y())
            evento.accept()
            return
        # Qt.angleDelta().y() é positivo girando para longe do usuário — sinal invertido do
        # "deltaY" do evento "wheel" do navegador (positivo = rolando para baixo/na direção do
        # usuário); negar aqui mantém a mesma convenção usada no index.html.
        delta_y = -evento.angleDelta().y()
        if self.ativada:
            self.deslizar_janela(delta_y)
        else:
            self.trocar_escala("minuto" if delta_y > 0 else "hora")
        evento.accept()

    def _pontos_atuais(self):
        layout = self._layout
        if not layout or layout.get("vazio_geral"):
            return []
        return layout["pontos"]

    def focusInEvent(self, evento):
        super().focusInEvent(evento)
        pontos = self._pontos_atuais()
        if pontos and self._indice_focado is None:
            self._indice_focado = 0
        self.update()

    def focusOutEvent(self, evento):
        super().focusOutEvent(evento)
        self.update()  # some o anel de foco ao sair (Tab continua sem interferência nossa)

    def keyPressEvent(self, evento):
        pontos = self._pontos_atuais()
        if not pontos:
            super().keyPressEvent(evento)
            return

        if evento.key() in (Qt.Key_Left, Qt.Key_Right):
            n = len(pontos)  # já em ordem de tempo (G4: "←/→ movem o ponto focado, ordem de tempo")
            if self._indice_focado is None:
                self._indice_focado = n - 1 if evento.key() == Qt.Key_Left else 0
            else:
                delta = -1 if evento.key() == Qt.Key_Left else 1
                self._indice_focado = max(0, min(n - 1, self._indice_focado + delta))
            self.update()
            evento.accept()
            return

        if evento.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if self._indice_focado is not None and 0 <= self._indice_focado < len(pontos):
                _, req = pontos[self._indice_focado]
                self.ponto_clicado.emit(req)
                evento.accept()
                return

        super().keyPressEvent(evento)


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
        modelo = dados.get("modelo") or "modelo desconhecido"
        self.rotulo_meta.setText(f"{modelo} — {formatar_usd(dados.get('custo_usd'))} — {quando}")
        texto = dados.get("texto")
        self.texto.setPlainText(texto if texto else "Não há transcrição guardada para esta requisição.")
        self.mostrar()


class PainelConsumo(QDialog):
    """Janela própria, redimensionável — não um overlay dentro da janela pequena de ditado.

    SPEC-002 G / D-30: um painel de 42rem (pensado pra página web inteira) dentro da janela do
    ditado (40rem) "ficou desproporcional, não dá pra ler direito, tá até vazando da tela" — achado
    no uso real em 2026-08-27. Consumo passou a abrir numa janela própria; só Configurações
    continua como painel sobreposto (são cinco linhas, cabe).

    G1-G6 transcritos de transcritor/frontend/index.html — ver LinhaDoTempoConsumo para a G3."""

    def __init__(self, janela):
        super().__init__(janela, Qt.Window)
        self.janela = janela
        self.setWindowTitle("Consumo")
        self.resize(900, 640)
        self.setStyleSheet(QSS + f"QDialog {{ background-color: {PALETA['fundo_cartao']}; }}")
        self._dados = None
        self._baseline_sessao = None
        self._trabalho = None
        self.popup_requisicao = PopupRequisicao(self)  # overlay dentro DESTA janela, não da de ditado

        self.rotulo_carregando = QLabel("Carregando…")
        self.rotulo_carregando.setStyleSheet("color: #1e40af;")
        self.rotulo_erro = QLabel()
        self.rotulo_erro.setWordWrap(True)
        self.rotulo_erro.setStyleSheet(f"color: {PALETA['erro']};")
        self.rotulo_erro.hide()

        # G1 — três linhas, nesta ordem: Requisições, Tokens, Custo estimado.
        self.rotulo_sessao = QLabel()
        self.botao_resetar = QPushButton("Resetar sessão")
        self.botao_resetar.clicked.connect(self._resetar_sessao)

        # G2 — histórico diário (lista com filete) + gráfico de barras proporcional ao custo.
        self.rotulo_diario_titulo = QLabel("Histórico diário")
        self.rotulo_diario_titulo.setProperty("class", "dica")
        self.area_lista_diaria = QScrollArea()
        self.area_lista_diaria.setWidgetResizable(True)
        self.area_lista_diaria.setFixedHeight(int(8 * 16))  # ~8rem
        self.area_lista_diaria.setFrameShape(QFrame.NoFrame)

        self.grafico = GraficoBarrasDiario()
        self.area_grafico = QScrollArea()
        self.area_grafico.setWidget(self.grafico)
        self.area_grafico.setWidgetResizable(True)
        self.area_grafico.setFrameShape(QFrame.NoFrame)
        self.area_grafico.setFixedHeight(GraficoBarrasDiario.ALTURA_BARRAS + GraficoBarrasDiario.ALTURA_ROTULO + 8)
        self.area_grafico.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # G3 — linha do tempo das requisições (ver LinhaDoTempoConsumo).
        self.rotulo_titulo_linha_tempo = QLabel("Linha do tempo das requisições")
        self.rotulo_titulo_linha_tempo.setProperty("class", "dica")
        self.rotulo_estado_roda = QLabel()
        self.rotulo_estado_roda.setStyleSheet(f"color: {PALETA['texto_dica']}; font-size: 11px;")
        self.botao_zoom = QPushButton("Zoom: Hora")
        self.botao_zoom.clicked.connect(self._alternar_zoom)

        self.rotulo_periodo_dia = QLabel()
        self.rotulo_periodo_dia.setProperty("class", "dica")
        self.botao_dia_anterior = QPushButton("◀ Dia anterior")
        self.botao_dia_anterior.clicked.connect(lambda: self.linha_tempo.navegar_dia(-1))
        self.botao_dia_seguinte = QPushButton("Dia seguinte ▶")
        self.botao_dia_seguinte.clicked.connect(lambda: self.linha_tempo.navegar_dia(1))

        self.rotulo_periodo_janela = QLabel()
        self.rotulo_periodo_janela.setProperty("class", "dica")
        self.slider_janela = QSlider(Qt.Horizontal)
        self.slider_janela.setAccessibleName("Posição da janela dentro das últimas 24 horas")
        self.slider_janela.valueChanged.connect(self._mudou_slider)
        self.botao_inicio_janela = QPushButton("Início (24h atrás)")
        self.botao_inicio_janela.clicked.connect(lambda: self.linha_tempo.mover_janela_para(timedelta(0)))
        self.botao_fim_janela = QPushButton("Mais recente")
        self.botao_fim_janela.clicked.connect(lambda: self.linha_tempo.pedir_ir_para_fim())

        self.linha_tempo = LinhaDoTempoConsumo()
        self.linha_tempo.ponto_clicado.connect(self._abrir_popup_requisicao)
        self.linha_tempo.estado_mudou.connect(self._atualizar_nav_linha_tempo)
        self.area_linha_tempo = QScrollArea()
        self.area_linha_tempo.setWidget(self.linha_tempo)
        self.area_linha_tempo.setWidgetResizable(False)
        self.area_linha_tempo.setFrameShape(QFrame.NoFrame)
        self.area_linha_tempo.setFixedHeight(LinhaDoTempoConsumo.ALTURA + 14)
        self.area_linha_tempo.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # G4: Tab precisa alcançar a linha do tempo — sem isto, o QScrollArea (que não aceita foco
        # por si) quebrava a cadeia de tabulação antes de chegar no widget de verdade.
        self.area_linha_tempo.setFocusProxy(self.linha_tempo)
        self.linha_tempo.anexar_area(self.area_linha_tempo)

        linha_nav_dia = QHBoxLayout()
        linha_nav_dia.addWidget(self.botao_dia_anterior)
        linha_nav_dia.addStretch()
        linha_nav_dia.addWidget(self.botao_dia_seguinte)
        self.widget_nav_dia = QWidget()
        layout_nav_dia_externo = QVBoxLayout(self.widget_nav_dia)
        layout_nav_dia_externo.setContentsMargins(0, 0, 0, 0)
        layout_nav_dia_externo.setSpacing(4)
        layout_nav_dia_externo.addWidget(self.rotulo_periodo_dia)
        layout_nav_dia_externo.addLayout(linha_nav_dia)

        linha_nav_janela = QHBoxLayout()
        linha_nav_janela.addWidget(self.botao_inicio_janela)
        linha_nav_janela.addWidget(self.slider_janela, 1)
        linha_nav_janela.addWidget(self.botao_fim_janela)
        self.widget_nav_janela = QWidget()
        layout_nav_janela_externo = QVBoxLayout(self.widget_nav_janela)
        layout_nav_janela_externo.setContentsMargins(0, 0, 0, 0)
        layout_nav_janela_externo.setSpacing(4)
        layout_nav_janela_externo.addWidget(self.rotulo_periodo_janela)
        layout_nav_janela_externo.addLayout(linha_nav_janela)

        layout_cabecalho_lt = QHBoxLayout()
        layout_cabecalho_lt.addWidget(self.rotulo_titulo_linha_tempo)
        layout_cabecalho_lt.addStretch()
        layout_cabecalho_lt.addWidget(self.rotulo_estado_roda)
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
        layout_corpo.addWidget(self.area_grafico)
        layout_corpo.addLayout(layout_cabecalho_lt)
        layout_corpo.addWidget(self.widget_nav_dia)
        layout_corpo.addWidget(self.widget_nav_janela)
        layout_corpo.addWidget(self.area_linha_tempo)
        rotulo_aviso_reset = QLabel("O reset zera só esta tela; o histórico salvo no backend não é apagado.")
        rotulo_aviso_reset.setProperty("class", "dica")
        layout_corpo.addWidget(rotulo_aviso_reset)

        # janela própria e redimensionável: o corpo rola dentro da área disponível, que agora pode
        # crescer com a janela — não fica mais preso a uma altura fixa dentro de um overlay pequeno.
        area_rolagem = QScrollArea()
        area_rolagem.setWidget(corpo)
        area_rolagem.setWidgetResizable(True)
        area_rolagem.setFrameShape(QFrame.NoFrame)

        layout_janela = QVBoxLayout(self)
        layout_janela.setContentsMargins(20, 20, 20, 20)
        layout_janela.addWidget(area_rolagem)

        self._mostrar_conteudo(False)
        # H1/G3: clique fora da linha do tempo desativa a roda — "fora" pode ser qualquer lugar do
        # app (outro botão, o popup, fora da janela de Consumo), não só dentro deste QDialog.
        QApplication.instance().installEventFilter(self)

    def _mostrar_conteudo(self, visivel):
        for w in (
            self.rotulo_sessao, self.botao_resetar, self.rotulo_diario_titulo, self.area_lista_diaria,
            self.area_grafico, self.rotulo_titulo_linha_tempo, self.rotulo_estado_roda, self.botao_zoom,
            self.area_linha_tempo,
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
        self.linha_tempo.reiniciar_abertura()
        url = self.janela.config["url_nucleo"]
        self._trabalho = TrabalhoConsumo(
            url, sessao=self.janela.sessao, exigir_login=url_exige_login(self.janela.config, url)
        )
        self._trabalho.sucesso.connect(self._ao_obter_sucesso)
        self._trabalho.falhou.connect(self._ao_falhar)
        self._trabalho.sessao_expirada.connect(self._ao_expirar_sessao)
        self._trabalho.start()

    def _ao_expirar_sessao(self):
        # A mensagem fica aqui; o login abre na janela de ditado e, ao entrar, este painel recarrega.
        self._ao_falhar(MENSAGEM_SESSAO_EXPIRADA + " O login abriu na janela de ditado.")
        self.janela.pedir_login(MENSAGEM_SESSAO_EXPIRADA)

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
        # Desoculta antes de renderizar: a escala "hora" mede a largura real do container
        # (viewport().width()) — um widget escondido mede 0 (mesma ordem do carregarConsumo no JS).
        self._mostrar_conteudo(True)
        self._renderizar_sessao()
        self._renderizar_diario()
        self.linha_tempo.definir_requisicoes(dados.get("requisicoes", []))

    def _renderizar_sessao(self):
        sessao = dict(self._dados.get("sessao") or {})
        base = self._baseline_sessao or {}
        requisicoes = max(0, (sessao.get("requisicoes") or 0) - (base.get("requisicoes") or 0))
        tokens = max(0, (sessao.get("tokens") or 0) - (base.get("tokens") or 0))
        custo = max(0.0, (sessao.get("custo_usd") or 0.0) - (base.get("custo_usd") or 0.0))
        linhas = [("Requisições", str(requisicoes)), ("Tokens", str(tokens)), ("Custo estimado", formatar_usd(custo))]
        self.rotulo_sessao.setText(
            "".join(f"<p style='margin:2px 0;'><b>{rotulo}:</b> {valor}</p>" for rotulo, valor in linhas)
        )

    def _resetar_sessao(self):
        if self._dados:
            self._baseline_sessao = dict(self._dados.get("sessao") or {})
            self._renderizar_sessao()

    def _renderizar_diario(self):
        por_dia = self._dados.get("por_dia") or []
        self.area_lista_diaria.setWidget(self._construir_lista_diaria(por_dia))
        self.grafico.definir_dias(por_dia)

    def _construir_lista_diaria(self, por_dia):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if not por_dia:
            vazio = QLabel("Nenhum consumo registrado ainda.")
            vazio.setProperty("class", "dica")
            layout.addWidget(vazio)
            return container
        for indice, dia in enumerate(por_dia):
            linha = QWidget()
            layout_linha = QHBoxLayout(linha)
            layout_linha.setContentsMargins(0, 4, 0, 4)
            rotulo_data = QLabel(str(dia.get("data", "")))
            rotulo_valor = QLabel(f"{dia.get('tokens', 0)} tokens — {formatar_usd(dia.get('custo_usd'))}")
            layout_linha.addWidget(rotulo_data)
            layout_linha.addStretch()
            layout_linha.addWidget(rotulo_valor)
            if indice < len(por_dia) - 1:
                linha.setStyleSheet("border-bottom: 1px solid #f0f4f8;")
            layout.addWidget(linha)
        return container

    def _alternar_zoom(self):
        self.linha_tempo.trocar_escala("minuto" if self.linha_tempo.escala == "hora" else "hora")

    def _mudou_slider(self, valor_segundos):
        self.linha_tempo.mover_janela_para(timedelta(seconds=valor_segundos))

    def _atualizar_nav_linha_tempo(self):
        lt = self.linha_tempo
        painel_visivel = self.area_linha_tempo.isVisible()
        tem_dados = bool(lt.requisicoes)
        self.widget_nav_dia.setVisible(painel_visivel and tem_dados and lt.escala == "hora")
        self.widget_nav_janela.setVisible(painel_visivel and tem_dados and lt.escala == "minuto")
        self.botao_zoom.setText("Zoom: Hora" if lt.escala == "hora" else "Zoom: Minuto")

        minimo, maximo = lt.limites_dias_com_dados()
        atual = lt.dia_selecionado
        self.botao_dia_anterior.setEnabled(minimo is not None and atual is not None and atual > minimo)
        self.botao_dia_seguinte.setEnabled(maximo is not None and atual is not None and atual < maximo)
        self.rotulo_periodo_dia.setText(lt.periodo_dia_texto())

        self.slider_janela.blockSignals(True)
        self.slider_janela.setRange(0, max(0, lt.deslocamento_maximo_segundos()))
        self.slider_janela.setValue(int(lt.deslocamento_janela.total_seconds()))
        self.slider_janela.blockSignals(False)
        self.rotulo_periodo_janela.setText(lt.periodo_janela_texto())

        self.rotulo_estado_roda.setText(lt.texto_estado_roda())
        cor = PALETA["roxo"] if lt.ativada else PALETA["texto_dica"]
        peso = "600" if lt.ativada else "400"
        self.rotulo_estado_roda.setStyleSheet(f"color: {cor}; font-size: 11px; font-weight: {peso};")

    def _abrir_popup_requisicao(self, dados):
        self.popup_requisicao.mostrar_requisicao(dados)

    def eventFilter(self, obj, evento):
        if evento.type() == QEvent.MouseButtonPress and self.linha_tempo.ativada and self.isVisible():
            pos_global = evento.globalPosition().toPoint()
            cantos = self.linha_tempo.mapToGlobal(QPoint(0, 0))
            dentro = (
                cantos.x() <= pos_global.x() <= cantos.x() + self.linha_tempo.width()
                and cantos.y() <= pos_global.y() <= cantos.y() + self.linha_tempo.height()
            )
            if not dentro:
                self.linha_tempo.desativar()
        return super().eventFilter(obj, evento)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if self.popup_requisicao.isVisible():
            self.popup_requisicao.setGeometry(self.rect())
        if self.linha_tempo.escala == "hora":
            self.linha_tempo.atualizar()

    def keyPressEvent(self, evento):
        # H1: popup de requisição > linha do tempo ativada > o próprio painel (Escape padrão do
        # QDialog fecha a janela).
        if evento.key() == Qt.Key_Escape and self.popup_requisicao.isVisible():
            self.popup_requisicao.esconder()
            return
        if evento.key() == Qt.Key_Escape and self.linha_tempo.ativada:
            self.linha_tempo.desativar()
            return
        super().keyPressEvent(evento)


class MiniaturaReferencia(QFrame):
    """D-31 — uma imagem de referência escolhida, com botão de remover embutido no canto."""

    removida = Signal(str)  # caminho

    TAMANHO = 72

    def __init__(self, caminho, parent=None):
        super().__init__(parent)
        self.caminho = caminho
        self.setFixedSize(self.TAMANHO, self.TAMANHO)
        self.setStyleSheet(
            f"QFrame {{ border: 1px solid {PALETA['borda_campo']}; border-radius: 6px; "
            f"background-color: {PALETA['fundo_cartao']}; }}"
        )

        rotulo = QLabel(self)
        rotulo.setGeometry(0, 0, self.TAMANHO, self.TAMANHO)
        rotulo.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(caminho)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.TAMANHO, self.TAMANHO, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        rotulo.setPixmap(pixmap)

        self.botao_remover = QPushButton(self)
        self.botao_remover.setIcon(icone("cancelar", "white", 10))
        estilizar_botao_circular(self.botao_remover, 18, "rgba(15,23,42,0.55)", "rgba(15,23,42,0.75)")
        self.botao_remover.move(self.TAMANHO - 20, 2)
        self.botao_remover.setToolTip(os.path.basename(caminho))
        self.botao_remover.clicked.connect(lambda: self.removida.emit(self.caminho))


class JanelaGeracaoImagem(QDialog):
    """Menu ⋮ → Gerar imagem (D-31, fora do plano da Fase 2 — pedido direto do usuário, "priorize
    funcionar hoje sobre ficar bonito"). Escolhe imagens de referência (arquivos, pasta ou
    arrastar-soltar), escreve um prompt, e o núcleo devolve uma imagem nova via POST
    /gerar-imagem (Operação 3, NUCLEO.md) — a chave da OpenAI mora só no núcleo."""

    def __init__(self, janela):
        super().__init__(janela, Qt.Window)
        self.janela = janela
        self.setWindowTitle("Gerar imagem")
        self.resize(640, 760)
        self.setStyleSheet(QSS + f"QDialog {{ background-color: {PALETA['fundo_cartao']}; }}")
        self.setAcceptDrops(True)

        self.caminhos_referencia = []
        self._trabalho = None
        self._ultima_imagem_bytes = None
        self._ultimo_caminho_salvo = None

        self.rotulo_titulo_referencia = QLabel("Imagens de referência")
        self.rotulo_contagem = QLabel()
        self.rotulo_contagem.setProperty("class", "dica")

        self.botao_escolher_arquivos = QPushButton("Escolher arquivos…")
        self.botao_escolher_arquivos.clicked.connect(self._escolher_arquivos)
        self.botao_escolher_pasta = QPushButton("Escolher pasta…")
        self.botao_escolher_pasta.clicked.connect(self._escolher_pasta)

        self.widget_miniaturas = QWidget()
        self.layout_miniaturas = QHBoxLayout(self.widget_miniaturas)
        self.layout_miniaturas.setContentsMargins(4, 4, 4, 4)
        self.layout_miniaturas.setSpacing(6)
        self.layout_miniaturas.addStretch(1)
        self.area_miniaturas = QScrollArea()
        self.area_miniaturas.setWidget(self.widget_miniaturas)
        self.area_miniaturas.setWidgetResizable(True)
        self.area_miniaturas.setFixedHeight(90)
        self.area_miniaturas.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.area_miniaturas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.area_miniaturas.setFrameShape(QFrame.NoFrame)

        self.caixa_prompt = QPlainTextEdit()
        self.caixa_prompt.setPlaceholderText("Descreva a imagem que você quer gerar…")
        self.caixa_prompt.setMinimumHeight(96)
        self.caixa_prompt.textChanged.connect(self._atualizar_botao_gerar)

        self.combo_modelo = QComboBox()
        self.combo_modelo.addItems(MODELOS_IMAGEM_ATIVOS)
        self.combo_modelo.setCurrentText(janela.config["modelo_imagem"])
        self.combo_modelo.currentTextChanged.connect(self._mudou_modelo)

        self.combo_tamanho = QComboBox()
        self.combo_tamanho.addItems(TAMANHOS_IMAGEM_ATIVOS)
        self.combo_tamanho.setCurrentText(janela.config["tamanho_imagem"])
        self.combo_tamanho.currentTextChanged.connect(self._mudou_tamanho)

        self.combo_qualidade = QComboBox()
        self.combo_qualidade.addItems(QUALIDADES_IMAGEM_ATIVAS)
        self.combo_qualidade.setCurrentText(janela.config["qualidade_imagem"])
        self.combo_qualidade.currentTextChanged.connect(self._mudou_qualidade)

        self.rotulo_custo_estimado = QLabel()
        self.rotulo_custo_estimado.setProperty("class", "dica")

        self.botao_gerar = QPushButton("Gerar")
        self.botao_gerar.clicked.connect(self._gerar)

        self.rotulo_carregando = QLabel("Gerando imagem — pode demorar bem mais que uma transcrição…")
        self.rotulo_carregando.setProperty("class", "dica")
        self.rotulo_carregando.hide()

        self.rotulo_preview = QLabel()
        self.rotulo_preview.setAlignment(Qt.AlignCenter)
        self.rotulo_preview.setMinimumHeight(280)
        self.rotulo_preview.hide()
        self.rotulo_custo_real = QLabel()
        self.rotulo_custo_real.hide()
        self.rotulo_caminho_salvo = QLabel()
        self.rotulo_caminho_salvo.setProperty("class", "dica")
        self.rotulo_caminho_salvo.setWordWrap(True)
        self.rotulo_caminho_salvo.hide()
        self.botao_salvar_como = QPushButton("Salvar como…")
        self.botao_salvar_como.clicked.connect(self._salvar_como)
        self.botao_salvar_como.hide()
        self.botao_abrir_pasta = QPushButton("Abrir a pasta")
        self.botao_abrir_pasta.clicked.connect(self._abrir_pasta)
        self.botao_abrir_pasta.hide()

        linha_titulo_ref = QHBoxLayout()
        linha_titulo_ref.addWidget(self.rotulo_titulo_referencia)
        linha_titulo_ref.addStretch()
        linha_titulo_ref.addWidget(self.rotulo_contagem)

        linha_botoes_ref = QHBoxLayout()
        linha_botoes_ref.addWidget(self.botao_escolher_arquivos)
        linha_botoes_ref.addWidget(self.botao_escolher_pasta)
        linha_botoes_ref.addStretch()

        linha_opcoes = QHBoxLayout()
        linha_opcoes.addWidget(QLabel("Modelo"))
        linha_opcoes.addWidget(self.combo_modelo)
        linha_opcoes.addWidget(QLabel("Tamanho"))
        linha_opcoes.addWidget(self.combo_tamanho)
        linha_opcoes.addWidget(QLabel("Qualidade"))
        linha_opcoes.addWidget(self.combo_qualidade)
        linha_opcoes.addStretch()
        linha_opcoes.addWidget(self.rotulo_custo_estimado)

        linha_botoes_resultado = QHBoxLayout()
        linha_botoes_resultado.addWidget(self.botao_salvar_como)
        linha_botoes_resultado.addWidget(self.botao_abrir_pasta)
        linha_botoes_resultado.addStretch()

        corpo = QWidget()
        layout_corpo = QVBoxLayout(corpo)
        layout_corpo.setContentsMargins(0, 0, 0, 0)
        layout_corpo.setSpacing(14)
        layout_corpo.addLayout(linha_titulo_ref)
        layout_corpo.addLayout(linha_botoes_ref)
        layout_corpo.addWidget(self.area_miniaturas)
        layout_corpo.addWidget(QLabel("Prompt"))
        layout_corpo.addWidget(self.caixa_prompt)
        layout_corpo.addLayout(linha_opcoes)
        layout_corpo.addWidget(self.botao_gerar)
        layout_corpo.addWidget(self.rotulo_carregando)
        layout_corpo.addWidget(self.rotulo_preview)
        layout_corpo.addWidget(self.rotulo_custo_real)
        layout_corpo.addWidget(self.rotulo_caminho_salvo)
        layout_corpo.addLayout(linha_botoes_resultado)
        layout_corpo.addStretch(1)

        area_rolagem = QScrollArea()
        area_rolagem.setWidget(corpo)
        area_rolagem.setWidgetResizable(True)
        area_rolagem.setFrameShape(QFrame.NoFrame)

        layout_janela = QVBoxLayout(self)
        layout_janela.setContentsMargins(20, 20, 20, 20)
        layout_janela.addWidget(area_rolagem)

        # balão efêmero (B4), mesmo estilo do resto do app — ancorado no botão Gerar.
        self.toast = Toast(self.botao_gerar)

        self._atualizar_contagem_referencia()
        self._atualizar_custo_estimado()
        self._atualizar_botao_gerar()

    # --- imagens de referência (escolher arquivos / pasta / arrastar-soltar) -----------------
    def dragEnterEvent(self, evento):
        if evento.mimeData().hasUrls():
            evento.acceptProposedAction()

    def dropEvent(self, evento):
        caminhos = [u.toLocalFile() for u in evento.mimeData().urls() if u.isLocalFile()]
        self._adicionar_imagens(caminhos)

    def _escolher_arquivos(self):
        caminhos, _ = QFileDialog.getOpenFileNames(
            self, "Escolher imagens de referência", "",
            "Imagens (*.png *.jpg *.jpeg *.webp);;Todos os arquivos (*)",
        )
        if caminhos:
            self._adicionar_imagens(caminhos)

    def _escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Escolher pasta de imagens de referência")
        if not pasta:
            return
        try:
            nomes = sorted(os.listdir(pasta))
        except OSError:
            return
        caminhos = [
            os.path.join(pasta, nome) for nome in nomes
            if os.path.splitext(nome)[1].lower() in FORMATOS_IMAGEM_ACEITOS
        ]
        self._adicionar_imagens(caminhos)

    def _adicionar_imagens(self, caminhos):
        aceitos, recusados = [], []
        for caminho in caminhos:
            if os.path.splitext(caminho)[1].lower() not in FORMATOS_IMAGEM_ACEITOS:
                recusados.append(os.path.basename(caminho))
                continue
            if caminho in self.caminhos_referencia or caminho in aceitos:
                continue
            aceitos.append(caminho)

        vagas = MAX_IMAGENS_REFERENCIA - len(self.caminhos_referencia)
        excedentes = len(aceitos) - vagas
        aceitos = aceitos[: max(0, vagas)]

        for caminho in aceitos:
            self._acrescentar_miniatura(caminho)

        if recusados:
            self.toast.mostrar(
                "erro", "Formato não aceito — use PNG, JPG ou WEBP.", DURACAO_TOAST_ERRO_MS
            )
        elif excedentes > 0:
            self.toast.mostrar(
                "erro", f"Limite de {MAX_IMAGENS_REFERENCIA} imagens — {excedentes} não entraram.",
                DURACAO_TOAST_ERRO_MS,
            )
        self._atualizar_contagem_referencia()
        self._atualizar_botao_gerar()

    def _acrescentar_miniatura(self, caminho):
        self.caminhos_referencia.append(caminho)
        miniatura = MiniaturaReferencia(caminho)
        miniatura.removida.connect(self._remover_imagem)
        self.layout_miniaturas.insertWidget(self.layout_miniaturas.count() - 1, miniatura)

    def _remover_imagem(self, caminho):
        if caminho in self.caminhos_referencia:
            self.caminhos_referencia.remove(caminho)
        for indice in range(self.layout_miniaturas.count()):
            item = self.layout_miniaturas.itemAt(indice)
            widget = item.widget() if item else None
            if isinstance(widget, MiniaturaReferencia) and widget.caminho == caminho:
                self.layout_miniaturas.removeWidget(widget)
                widget.deleteLater()
                break
        self._atualizar_contagem_referencia()
        self._atualizar_botao_gerar()

    def _atualizar_contagem_referencia(self):
        self.rotulo_contagem.setText(f"{len(self.caminhos_referencia)} de {MAX_IMAGENS_REFERENCIA}")

    # --- opções e custo estimado -------------------------------------------------------------
    def _mudou_modelo(self, texto):
        self.janela.config["modelo_imagem"] = texto
        salvar_config(self.janela.config)
        self._atualizar_custo_estimado()

    def _mudou_tamanho(self, texto):
        self.janela.config["tamanho_imagem"] = texto
        salvar_config(self.janela.config)

    def _mudou_qualidade(self, texto):
        self.janela.config["qualidade_imagem"] = texto
        salvar_config(self.janela.config)
        self._atualizar_custo_estimado()

    def _atualizar_custo_estimado(self):
        modelo = self.combo_modelo.currentText()
        qualidade = self.combo_qualidade.currentText()
        preco_saida = PRECOS_SAIDA_IMAGEM_POR_TOKEN_USD.get(modelo)
        if preco_saida is None:
            self.rotulo_custo_estimado.setText("")
            return
        tokens = TOKENS_SAIDA_ESTIMADOS_POR_QUALIDADE.get(qualidade, 1056)
        estimado = tokens * preco_saida
        self.rotulo_custo_estimado.setText(
            f"Custo estimado (só a saída, sem as referências): ~{formatar_usd(estimado)}/imagem"
        )

    # --- gerar --------------------------------------------------------------------------------
    def _atualizar_botao_gerar(self):
        tem_prompt = bool(self.caixa_prompt.toPlainText().strip())
        tem_imagem = bool(self.caminhos_referencia)
        self.botao_gerar.setEnabled(tem_prompt and tem_imagem and self._trabalho is None)

    def _gerar(self):
        prompt = self.caixa_prompt.toPlainText().strip()
        if not prompt or not self.caminhos_referencia:
            return
        self.botao_gerar.setEnabled(False)
        self.rotulo_carregando.show()
        self.rotulo_preview.hide()
        self.rotulo_custo_real.hide()
        self.rotulo_caminho_salvo.hide()
        self.botao_salvar_como.hide()
        self.botao_abrir_pasta.hide()

        pasta_saida = self.janela.config.get("pasta_saida_imagens") or CONFIG_PADRAO["pasta_saida_imagens"]
        # Etapa 5: a imagem continua no núcleo LOCAL (`url_nucleo_imagem`) — `url_nucleo` agora é o
        # remoto, que não gera imagem. O token vai junto: é ele que faz o consumo cair no banco.
        url = self.janela.config.get("url_nucleo_imagem") or URL_NUCLEO_LOCAL_PADRAO
        self._trabalho = TrabalhoGeracaoImagem(
            url,
            list(self.caminhos_referencia),
            prompt,
            self.combo_modelo.currentText(),
            self.combo_tamanho.currentText(),
            self.combo_qualidade.currentText(),
            pasta_saida,
            sessao=self.janela.sessao,
            exigir_login=url_exige_login(self.janela.config, url),
        )
        self._trabalho.sucesso.connect(self._ao_gerar_sucesso)
        self._trabalho.falhou.connect(self._ao_gerar_falhar)
        self._trabalho.sessao_expirada.connect(lambda: self.janela.pedir_login(MENSAGEM_SESSAO_EXPIRADA))
        self._trabalho.start()

    def _ao_gerar_sucesso(self, caminho_salvo, formato, custo_usd):
        # A thread já decodificou e salvou o arquivo (ver TrabalhoGeracaoImagem) — o que já foi
        # pago está em disco antes mesmo deste método rodar, independente do que acontecer daqui
        # em diante (achado no uso real: um crash nativo do Qt bem nesta janela de tempo).
        trabalho = self._trabalho
        self.rotulo_carregando.hide()
        self._trabalho = None
        self._atualizar_botao_gerar()

        self._ultimo_caminho_salvo = caminho_salvo or None
        if caminho_salvo:
            self.rotulo_caminho_salvo.setText(f"Salva automaticamente em: {caminho_salvo}")
            self.rotulo_caminho_salvo.show()
            self.botao_abrir_pasta.show()
        else:
            self.rotulo_caminho_salvo.setText("Não foi possível salvar automaticamente — use \"Salvar como…\".")
            self.rotulo_caminho_salvo.show()
            self.toast.mostrar(
                "erro", "Imagem gerada, mas não foi possível salvar em disco — use \"Salvar como…\".",
                DURACAO_TOAST_ERRO_MS,
            )
        self.botao_salvar_como.show()

        self.rotulo_custo_real.setText(f"Custo real: {formatar_usd(custo_usd)}")
        self.rotulo_custo_real.show()

        # Bytes para a pré-visualização e o "Salvar como…": relidos do arquivo que a thread já
        # salvou (caminho comum) ou, se não deu para salvar, os que a thread guardou em memória.
        imagem_bytes = None
        if caminho_salvo:
            try:
                with open(caminho_salvo, "rb") as arquivo:
                    imagem_bytes = arquivo.read()
            except OSError:
                imagem_bytes = None
        elif trabalho is not None:
            imagem_bytes = trabalho.imagem_bytes
        self._ultima_imagem_bytes = imagem_bytes

        if imagem_bytes:
            pixmap = QPixmap()
            pixmap.loadFromData(imagem_bytes)
            if not pixmap.isNull():
                self.rotulo_preview.setPixmap(
                    pixmap.scaled(560, 560, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.rotulo_preview.show()

        if caminho_salvo:
            self.toast.mostrar("confirmacao", "Imagem gerada e salva.", DURACAO_TOAST_CONFIRMACAO_MS)

    def _ao_gerar_falhar(self, mensagem, codigo):
        self.rotulo_carregando.hide()
        self._trabalho = None
        self._atualizar_botao_gerar()
        if codigo:
            log.info("erro_gerar_imagem codigo=%s", codigo)
        self.toast.mostrar("erro", mensagem, DURACAO_TOAST_ERRO_MS)

    def _salvar_como(self):
        if self._ultima_imagem_bytes is None:
            return
        sugestao = self._ultimo_caminho_salvo or "imagem.png"
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar imagem como", sugestao, "PNG (*.png);;JPEG (*.jpg);;WEBP (*.webp)"
        )
        if not caminho:
            return
        with open(caminho, "wb") as arquivo:
            arquivo.write(self._ultima_imagem_bytes)
        self.toast.mostrar("confirmacao", "Cópia salva.", DURACAO_TOAST_CONFIRMACAO_MS)

    def _abrir_pasta(self):
        if not self._ultimo_caminho_salvo:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self._ultimo_caminho_salvo)))

    # --- janela ---------------------------------------------------------------------------------
    def mostrar(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.caixa_prompt.setFocus()

    def esconder(self):
        self.hide()

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if self.toast.isVisible():
            self.toast._reposicionar()


class JanelaDitado(QWidget):
    sinal_atalho_disparado = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        # Etapa 5 — login no Supabase para o núcleo remoto. Criada antes da interface (o painel de
        # login e o de Configurações leem dela). `_pendentes_login` guarda os áudios que voltaram
        # sem sessão: nada se perde, e eles são reenviados em ordem depois do login.
        self.sessao = Sessao(self.config)
        self._pendentes_login = []
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
        # D-32 — janela compacta: _montar_ui monta a janela cheia e encolhe no final.
        self._expandido = True
        self._ponteiro_dentro = False
        # D-32 item 4 — o que já foi colocado (copiado/recortado). "Tem resultado pendente na
        # tela?" é derivado disto e da caixa, nunca guardado num sinalizador próprio: ver
        # _resultado_pendente().
        self._texto_colocado = ""
        self._progresso_modo = 1.0
        # D-32 3a volta — a animacao interpola a janela INTEIRA (posicao e tamanho) e a posicao do
        # botao dentro dela, com os layouts congelados; ver _aplicar_modo.
        self._geo_inicial = None
        self._geo_final = None
        # D-32 4a volta — retangulo em que a janela NATIVA fica parada durante a transicao (a
        # uniao das duas pontas) e o retangulo que o usuario de fato enxerga em cada quadro (o
        # cartao dentro dela). Fora de uma transicao os dois sao None: manda self.geometry().
        self._geo_transicao = None
        self._geo_visivel = None
        self._centro_inicial_global = QPoint(0, 0)
        self._centro_final_global = QPoint(0, 0)
        self._margem_inicial = 0
        self._margem_final = 0
        # D-32 9ª volta — a janela nativa tem UM tamanho só (o expandido) e não se mexe em
        # transição: o que cresce e encolhe é a máscara. `_offset_visivel` é onde o retângulo
        # do modo mora dentro da janela (0,0 no expandido; ancorado no botão no compacto), e
        # `_mascara_atual` evita chamar setMask de novo com a mesma região.
        # O retângulo do modo ASSENTADO, em coordenada da janela: onde ele mora e que tamanho
        # tem. Os dois vêm do assentamento, e não de `self._expandido`, porque `_aplicar_modo`
        # troca `_expandido` logo no começo — perguntar o tamanho pelo modo faria a transição
        # começar já no retângulo de destino (medido: a expansão só animava os últimos 16px).
        self._offset_visivel = QPoint(0, 0)
        self._tamanho_visivel = QSize(LARGURA_EXPANDIDA, ALTURA_EXPANDIDA)
        self._mascara_atual = None
        self._ultima_marca_compacta = None
        self._ultimo_log_correcao = 0.0
        self._mola_compacta = None  # ver _prender_botao_no_topo
        self._offset_arraste = None
        # D-32 7ª volta — "a transição de modo vai começar agora, neste mesmo turno do laço de
        # eventos": ver _definir_estado_botao e esta_em_transicao_de_modo.
        self._transicao_de_modo_pendente = False
        # D-32 7ª volta: largura e altura próprias desta janela flutuante — a largura deixou
        # de ser a coluna de 40rem da SPEC-002 item I (vínculo revogado só aqui), ver
        # LARGURA_EXPANDIDA/ALTURA_EXPANDIDA.
        self._tamanho_expandido = QSize(LARGURA_EXPANDIDA, ALTURA_EXPANDIDA)

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
        # D-32: sem moldura (o compacto é só o círculo) — o preço é arrastar à mão, ver arraste_*.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Ditado")
        self.setStyleSheet(QSS)
        # D-32 9ª volta — tamanho ÚNICO da janela nativa, para sempre. Redimensionar uma
        # janela layered/translúcida no Windows realoca a superfície do UpdateLayeredWindow, e
        # é o suspeito que sobrou depois de três rodadas (4ª, 5ª e 8ª) atacarem quantos
        # resizes existem, em que ordem e como são publicados. Aqui não existe mais nenhum:
        # quem cresce e encolhe na tela é a máscara (ver _aplicar_mascara).
        self.setFixedSize(self._tamanho_expandido)
        # Sem isto, a posição inicial fica por conta do SO — e num desktop virtual com monitores
        # em layout irregular (vão sem cobertura entre eles) a janela pode nascer nesse vão, longe
        # de qualquer tela de verdade (achado no uso real, 2026-09). `_geometria_do_modo` já
        # resolve isso nas trocas de modo (D-32), mas só depois de já haver uma posição válida —
        # aqui é a primeira, antes de qualquer show().
        tela_inicial = QGuiApplication.primaryScreen()
        if tela_inicial is not None:
            area_inicial = tela_inicial.availableGeometry()
            # 9ª volta: a janela nasce com 448x366 (antes nascia e logo virava 80x80), então o
            # canto de +40,+40 já não cabe em qualquer tela — `_encaixar_na_tela` empurra o
            # retângulo inteiro para dentro da área visível. É o único lugar onde ela ainda é
            # usada: nas trocas de modo a janela não se mexe mais.
            topo_inicial = QPoint(area_inicial.x() + 40, area_inicial.y() + 40)
            self.move(self._encaixar_na_tela(
                topo_inicial, self._tamanho_expandido, topo_inicial))

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(*(4 * [MARGEM_EXTERNA_EXPANDIDA]))
        # Quem manda no tamanho da janela é o modo (compacto/expandido) e os quadros da
        # animação — não o mínimo do layout. Com a restrição padrão, QLayout.activate() empurra
        # o mínimo da janela para o mínimo do conteúdo expandido, e todo resize menor que isso
        # (todos os quadros do encolhimento) sairia grudado nesse piso.
        layout_externo.setSizeConstraint(QLayout.SetNoConstraint)
        self._layout_externo = layout_externo

        cartao = QFrame()
        cartao.setObjectName("cartaoGravacao")
        self.cartao = cartao
        layout = QVBoxLayout(cartao)
        self._layout_cartao = layout
        layout.setContentsMargins(*(4 * [MARGEM_CARTAO_EXPANDIDA]))
        layout.setSpacing(ESPACAMENTO_CARTAO)
        layout_externo.addWidget(cartao)

        # D-32 7ª volta — o cronômetro deixou de ser uma linha própria e entrou nesta linha, à
        # esquerda: uma linha só a menos vale 19px de rótulo + 8px de espaçamento na altura da
        # janela. Ele é criado antes do trio porque agora é o primeiro item da linha do topo.
        self.rotulo_cronometro = QLabel("")
        self.rotulo_cronometro.setAlignment(Qt.AlignCenter)
        fonte_mono = QFont("Consolas")
        fonte_mono.setStyleHint(QFont.Monospace)
        fonte_mono.setPointSize(12)
        self.rotulo_cronometro.setFont(fonte_mono)
        self.rotulo_cronometro.setText("00:00")
        # largura e altura travadas no maior texto que ele exibe (a gravação para em 5 min, então
        # "00:00" já é o pior caso): assim o rótulo não empurra o trio de botões quando o
        # cronômetro liga/desliga — J1/J2, o espaço fica reservado desde a abertura.
        dimensao_cronometro = self.rotulo_cronometro.sizeHint()
        self.rotulo_cronometro.setFixedWidth(dimensao_cronometro.width())
        self.rotulo_cronometro.setMinimumHeight(dimensao_cronometro.height())
        self.rotulo_cronometro.setText("")

        # trio encostado e centralizado (não uma barra espalhada — achado no uso real: os dois
        # addStretch nas pontas empurravam ⋮ e cancelar para as bordas). Vão de 10px (0.6rem) entre
        # os três; o botão de gravar não se move porque o trio inteiro é um bloco só, centralizado
        # por stretches simétricos nas duas pontas — e, desde a 7ª volta, porque à direita há um
        # espelho invisível da largura do cronômetro (senão o rótulo à esquerda empurraria o trio
        # inteiro para a direita, e o botão de gravar é o alvo visual central desta janela).
        linha_topo = QHBoxLayout()
        linha_topo.setSpacing(10)
        linha_topo.addWidget(self.rotulo_cronometro)
        linha_topo.addStretch(1)

        self.botao_menu = QPushButton()
        self.botao_menu.setIcon(icone("tres_pontos", PALETA["texto_secundario"], 20))
        estilizar_botao_circular(self.botao_menu, LADO_BOTAO_SECUNDARIO)
        linha_topo.addWidget(self.botao_menu)

        self.botao_gravar = BotaoGravar()
        self.botao_gravar.clicked.connect(self.alternar_gravacao)
        linha_topo.addWidget(self.botao_gravar)

        # B.2 — camada própria para o pulso do gravando e o realce do arrastar (ver CamadaPulso);
        # filha do cartão, não do botão, para não herdar o recorte do widget de tamanho fixo.
        self.camada_pulso = CamadaPulso(self.botao_gravar, cartao)
        self.botao_gravar.anexar_camada_pulso(self.camada_pulso)
        QTimer.singleShot(0, self.camada_pulso.reposicionar)

        self.botao_cancelar = QPushButton()
        estilizar_botao_circular(
            self.botao_cancelar, LADO_BOTAO_SECUNDARIO,
            PALETA["cancelar_fundo"], PALETA["cancelar_fundo_hover"],
        )
        self.botao_cancelar.setEnabled(False)
        self.botao_cancelar.clicked.connect(self.cancelar_gravacao)
        linha_topo.addWidget(self.botao_cancelar)

        linha_topo.addStretch(1)
        # espelho do cronômetro: um widget vazio da mesma largura, do outro lado, só para o trio
        # continuar centralizado. É um WIDGET (não um addSpacing) de propósito — no modo compacto
        # ele entra em _widgets_so_expandido e some junto com o resto; um espaçador de layout não
        # some, e os 49px dele empurrariam o botão para fora da janela de 80px (foi exatamente
        # esse tipo de "botão fora do recorte" que a 3ª volta corrigiu).
        self.espelho_cronometro = QWidget()
        self.espelho_cronometro.setFixedWidth(dimensao_cronometro.width())
        self.espelho_cronometro.setAttribute(Qt.WA_TransparentForMouseEvents)
        linha_topo.addWidget(self.espelho_cronometro)
        layout.addLayout(linha_topo)

        self.barra_amplitude = BarraAmplitude()
        layout.addWidget(self.barra_amplitude)

        self.caixa_texto = QPlainTextEdit()
        self.caixa_texto.setPlaceholderText("A transcrição aparece aqui — editável, soma cada gravação.")
        self.caixa_texto.setMinimumHeight(ALTURA_CAIXA_TEXTO)  # D-32 6ª volta: 160px, ~1/3 da
        # janela de antes. Com o fator de esticar 1 abaixo e a janela em ALTURA_EXPANDIDA,
        # a caixa fica exatamente nesses 160px — o mínimo é o que ela ocupa, não um piso solto.
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
        self.painel_login = PainelLogin(self)  # Etapa 5 — sobreposto, como Configurações
        self.painel_login.entrou.connect(self._ao_entrar_na_conta)
        self.painel_consumo = PainelConsumo(self)
        self.janela_gerar_imagem = JanelaGeracaoImagem(self)  # D-31, fora do plano da Fase 2

        # Itens do menu ⋮ são ItemMenuAvancado dentro de QWidgetAction (não addAction com ícone
        # direto) — ver o docstring de ItemMenuAvancado para o porquê.
        self.menu_avancado = QMenu(self)
        for nome_icone, texto, callback in (
            ("planejamento", "Abrir planejamento", self._abrir_planejamento),
            ("engrenagem", "Configurações", self.painel_configuracoes.mostrar),
            ("consumo", "Consumo", self.painel_consumo.mostrar),
            ("enviar", "Enviar arquivo", self._clicar_enviar_arquivo),
            ("imagem", "Gerar imagem", self.janela_gerar_imagem.mostrar),
            ("conta", "Sair da conta", self._sair_da_conta),  # Etapa 5
            ("sair", "Sair", self._sair),
        ):
            item = ItemMenuAvancado(nome_icone, texto, self.menu_avancado)
            item.clicado.connect(callback)
            item.clicado.connect(self.menu_avancado.close)
            acao = QWidgetAction(self.menu_avancado)
            acao.setDefaultWidget(item)
            self.menu_avancado.addAction(acao)
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

        # D-32 — tudo que só existe na janela cheia; no compacto sobra o botão de gravar.
        self._widgets_so_expandido = (
            self.botao_menu, self.botao_cancelar, self.rotulo_cronometro,
            self.espelho_cronometro, self.barra_amplitude,
            self.caixa_texto, self.botao_lixeira, self.botao_copiar,
        )
        self._timer_encolher = QTimer(self)
        self._timer_encolher.setSingleShot(True)
        self._timer_encolher.timeout.connect(self._encolher_se_puder)
        self._anim_modo = QPropertyAnimation(self, b"progressoModo", self)
        self._anim_modo.setDuration(DURACAO_ANIMACAO_MODO_MS)
        self._anim_modo.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim_modo.finished.connect(self._ao_terminar_animacao_modo)
        self._timer_vigia_ponteiro = QTimer(self)
        self._timer_vigia_ponteiro.timeout.connect(self._vigiar_ponteiro)
        self._timer_vigia_ponteiro.start(INTERVALO_VIGIA_PONTEIRO_MS)
        # Sem isto o botão ainda está em (0,0) quando a âncora abaixo o mede, e o cartão
        # compacto nasce no canto da janela em vez de em cima do botão — na primeira expansão o
        # botão saltava 184x21px (medido em headless, 9ª volta).
        self._layout_externo.activate()
        self._layout_cartao.activate()
        # 9ª volta: ancorado, ao contrário das voltas anteriores. Ancorar deixou de mover a
        # janela (`_geometria_do_modo` não encaixa mais nada na tela e o expandido é a própria
        # janela), e é a âncora que põe o cartão compacto no offset em que o botão da janela
        # expandida já está — sem ela o cartão nasceria em (0,0) e o botão saltaria na primeira
        # expansão. A posição inicial escolhida acima continua intacta.
        self._aplicar_modo(expandido=False, ancorar=True, animar=False)

    # --- janela compacta: expandir por hover e por estado (D-32) ------------------
    def _lado_compacto(self):
        """O compacto abraça o BotaoGravar de verdade (72px hoje) mais uma margem pequena — medido
        contra o botão, não escolhido redondo: se o botão mudar de tamanho, a janela acompanha."""
        return self.botao_gravar.height() + 2 * MARGEM_JANELA_COMPACTA

    def _tamanho_do_modo(self, expandido):
        if expandido:
            return QSize(self._tamanho_expandido)
        lado = self._lado_compacto()
        return QSize(lado, lado)

    def _configurar_layout_do_modo(self, expandido):
        """Só as escolhas de layout do modo (margens, mola, estilo do cartão, balão) — nada de
        tamanho nem de posição, que são responsabilidade de _aplicar_modo."""
        if expandido:
            self.cartao.setStyleSheet("")  # volta ao cartão branco do QSS
            self._layout_externo.setContentsMargins(*(4 * [MARGEM_EXTERNA_EXPANDIDA]))
            self._layout_cartao.setContentsMargins(*(4 * [MARGEM_CARTAO_EXPANDIDA]))
            self._layout_cartao.setSpacing(ESPACAMENTO_CARTAO)
            self._prender_botao_no_topo(False)
            return
        self.toast.esconder()  # o balão é mais largo que o compacto — sairia cortado
        self.cartao.setStyleSheet("QFrame#cartaoGravacao { background: transparent; border: none; }")
        self._layout_externo.setContentsMargins(0, 0, 0, 0)
        margem = MARGEM_JANELA_COMPACTA
        self._layout_cartao.setContentsMargins(margem, margem, margem, margem)
        self._layout_cartao.setSpacing(0)
        self._prender_botao_no_topo(True)

    def esta_em_transicao_de_modo(self):
        """D-32 7ª volta — a troca compacto⇄expandido está em andamento (ou começa neste mesmo
        turno do laço de eventos). Quem pergunta é a CamadaPulso, para não ligar o temporizador de
        pulso de 30ms em cima dos quadros da transição; ver CamadaPulso.definir_estado."""
        return (
            self._transicao_de_modo_pendente
            or self._anim_modo.state() == QAbstractAnimation.Running
        )

    def _aplicar_modo(self, expandido, ancorar=True, animar=True):
        """Troca o layout na hora e leva a janela inteira — posição e tamanho — até o retângulo do
        modo, animada. Chamar de novo no meio de uma animação reverte: o alvo novo é recalculado a
        partir do retângulo atual (é o caso do mouse que muda de lado no meio do caminho).

        Terceira volta (2026-09-05): a animação **não reflui mais o layout a cada quadro**. O
        reflow por quadro pedia ao layout do tamanho cheio que se acomodasse em larguras
        intermediárias: nos primeiros quadros da expansão ele punha o botão a ~47px da borda de uma
        janela de 88px, ou seja, fora do recorte — o círculo aparecia como um pedaço de 21x25px de
        um círculo de 65x65 (medido quadro a quadro por grab(), ver PROGRESSO). E como a âncora era
        refeita a cada quadro contra esse layout, perto da borda da tela o encaixe na área visível
        empurrava o centro do botão em até ~250px durante a expansão. Agora os dois layouts ficam
        congelados durante a transição e quem posiciona o cartão e o botão é esta classe, por
        coordenada absoluta interpolada entre as duas pontas: o botão fica parado na tela (ou
        desliza suave, quando a borda da tela obriga a janela cheia a se deslocar) e nunca sai do
        recorte. O conteúdo do cartão só reaparece no fim — com o layout congelado ele estaria com
        a geometria do tamanho final dentro de uma janela menor, isto é, cortado e fora do lugar.

        Quarta volta (2026-09-05): a animação **não redimensiona mais a janela nativa a cada
        quadro**. Esta janela é `FramelessWindowHint | WindowStaysOnTopHint | Tool` com
        `WA_TranslucentBackground` — no Windows isso é uma janela *layered* de verdade, e pedir ao
        sistema ~10 redimensionamentos em 160ms é fonte conhecida de tremor/flicker (e o suspeito
        de a janela às vezes ficar presa num tamanho intermediário). Agora a janela do SO é levada
        **uma única vez** ao retângulo-união das duas pontas (`_geo_transicao`) e fica parada ali
        até `_assentar_modo` dar o tamanho final exato — dois redimensionamentos nativos na
        transição inteira, no pior caso; um só quando a união já é o retângulo expandido, que é o
        caso normal. Como a janela é translúcida, a área que sobra é invisível: quem "cresce" e
        "encolhe" na tela é o cartão, posicionado por `_set_progresso_modo` dentro dessa janela
        fixa. Nada disso é observável em teste headless (não há compositor), então a confirmação do
        flicker continua sendo do uso real no Windows.

        Quinta volta (2026-09-05): **a ordem**. Até aqui, `_configurar_layout_do_modo` (margens,
        mola e folha de estilo do cartão) e um `setVisible(expandido)` sobre o conteúdo
        só-expandido rodavam com os dois layouts ainda **habilitados** e a janela nativa ainda no
        tamanho do modo *antigo* — ou seja, mexiam ao vivo num layout que ainda mandava na
        geometria, dentro de uma janela pequena demais (na expansão) ou grande demais (no
        encolhimento). É o suspeito do "o botão some por um instante" bem no começo/fim da
        transição relatado no Windows. Agora nada é reconfigurado antes de os layouts saírem do
        comando, e o conteúdo só-expandido é escondido **uma vez, para os dois sentidos** (na
        expansão ele só reaparece em `_assentar_modo`, no fim). O `setVisible(expandido)` antigo
        era desfeito duas linhas adiante, antes do primeiro quadro: nunca teve função, só efeito
        colateral.

        O que **não** deu para adiantar, e por quê (medido, não suposto): a janela nativa não pode
        crescer para a união antes de `_configurar_layout_do_modo`, porque a união depende de
        `geo_final` e `geo_final` depende das margens **e da folha de estilo** já aplicadas — a
        borda de 1px do QSS do cartão desloca o centro medido do botão em 1px (76 vs 75 na janela
        expandida). Adiantar o resize exigiria ou um redimensionamento nativo a mais por transição
        (justo o que a 4ª volta eliminou) ou aceitar 1px de erro de âncora no assentamento. Com os
        layouts já congelados, `_configurar_layout_do_modo` não reflui nada e não há volta ao laço
        de eventos entre ele e `_set_progresso_modo(0.0)` — nenhum quadro chega a ser pintado no
        tamanho antigo."""
        self._anim_modo.stop()
        centro_inicial_global = self.botao_gravar.mapToGlobal(self.botao_gravar.rect().center())
        centro_antes = centro_inicial_global if ancorar else None
        margem_inicial = self._layout_externo.contentsMargins().left()
        self._expandido = expandido
        self._timer_encolher.stop()
        # 5ª volta: os dois layouts saem do comando ANTES de qualquer reconfiguração, e o conteúdo
        # só-expandido é escondido aqui, de uma vez, para os dois sentidos. Ver o docstring.
        self._layout_externo.setEnabled(False)
        self._layout_cartao.setEnabled(False)
        for widget in self._widgets_so_expandido:
            widget.setVisible(False)
        self._configurar_layout_do_modo(expandido)
        # 9ª volta: nada de mínimo/máximo por modo — a janela é fixa no tamanho expandido desde
        # _montar_ui e não muda mais. Com isso o mínimo que o Qt informa ao sistema de janelas
        # também para de oscilar entre os modos.
        # Uma medição só para a transição inteira: `_geometria_do_modo` e o centro final abaixo
        # pedem o mesmo número (o mesmo tamanho de modo), e cada medição roda um activate() do
        # layout cheio e liga/desliga a visibilidade do conteúdo — trabalho ao vivo justamente no
        # instante em que o usuário relata o botão sumindo. Medir uma vez e reaproveitar.
        centro_local_final = None
        if centro_antes is not None:
            centro_local_final = self._centro_local_do_botao(self._tamanho_do_modo(expandido))
        geo_final = self._geometria_do_modo(expandido, centro_antes, centro_local_final)
        # No meio de uma transição a janela nativa está no retângulo-união, que não é o que se vê:
        # o ponto de partida de uma reversão é o retângulo visível (o cartão), não self.geometry().
        geo_atual = self._geometria_visivel()
        if not animar or not self.isVisible() or geo_atual == geo_final:
            self._assentar_modo(geo_final)
            return
        self._geo_inicial = geo_atual
        self._geo_final = geo_final
        # Os dois centros do botão em coordenada de TELA, medidos antes de a janela sair do lugar:
        # é entre eles que _set_progresso_modo interpola, e assim o botão não depende mais de onde
        # a janela nativa está.
        self._centro_inicial_global = centro_inicial_global
        if centro_local_final is None:  # sem âncora (abertura) ninguém mediu ainda
            centro_local_final = self._centro_local_do_botao(geo_final.size())
        self._centro_final_global = geo_final.topLeft() + centro_local_final
        # A margem externa também é interpolada: o cartão recorta os filhos, e um cartão já com a
        # margem do modo final dentro de uma janela ainda pequena corta o próprio botão (medido:
        # círculo de 55x55 em vez de 65x65 no primeiro quadro da expansão).
        self._margem_inicial = margem_inicial
        self._margem_final = self._layout_externo.contentsMargins().left()
        # ÚNICO redimensionamento nativo do começo da transição: a união das duas pontas cabe os
        # dois extremos (e, por ser retângulo e a interpolação ser linear, cabe todo quadro do
        # meio também — cartão e botão inclusive). Daqui até _assentar_modo o SO não é mais
        # incomodado com o tamanho da janela.
        # 9ª volta: a base da transição é a própria janela — nenhum setGeometry, nunca.
        # `_geo_transicao` continua existindo porque é ele que diz a `_set_progresso_modo` em
        # que retângulo o cartão está sendo desenhado, e é ele que o arrasto translada quando o
        # usuário arrasta no meio da transição.
        # 10ª volta: o ÚNICO movimento nativo permitido, e só quando ele é necessário — a
        # expansão perto de uma borda da tela, em que a janela de 448x366 não caberia. O que
        # causa o flicker da janela layered é o RE-DIMENSIONAMENTO (realoca a superfície do
        # UpdateLayeredWindow), não o deslocamento; esse invariante — zero resize — continua
        # absoluto. Longe das bordas, `destino_janela` é a posição atual e nada se move.
        destino_janela = geo_final.topLeft() if expandido else self.pos()
        # A base é a janela JÁ MOVIDA: `_set_progresso_modo` põe o cartão por coordenada de
        # tela descontando `base.topLeft()`, então é isto que faz o cartão ficar parado na tela
        # no instante em que a janela se desloca — e o botão deslizar suave até o lugar novo em
        # vez de saltar. Trocar esta ordem é o jeito de quebrar a rodada.
        self._geo_transicao = QRect(destino_janela, self.size())
        # D-32 8ª volta, mantido: tirar a máscara e pôr o quadro zero saem juntos, sem pintura
        # parcial no meio, e o repaint() síncrono publica o primeiro quadro já pronto.
        atualizacoes_ligadas = self.updatesEnabled()
        self.setUpdatesEnabled(False)
        try:
            # Durante a transição a janela fica INTEIRA (sem máscara), como era o retângulo-união
            # da 4ª volta. A máscara do modo volta em _assentar_modo: um setMask por transição,
            # nunca quadro a quadro — SetWindowRgn por quadro seria o mesmo erro da 3ª/4ª volta
            # com outro nome.
            self._limpar_mascara()
            if destino_janela != self.pos():
                self.move(destino_janela)
            # o quadro zero é aplicado aqui, e não no primeiro tique da animação: entre trocar o
            # layout e o primeiro tique o botão ficaria um quadro inteiro na posição velha. Com
            # a janela recém-movida ele tem um segundo papel: o move arrasta o cartão junto (é
            # filho), e é este quadro zero que o devolve ao ponto de tela em que ele estava.
            self._set_progresso_modo(0.0)
        finally:
            self.setUpdatesEnabled(atualizacoes_ligadas)
        if atualizacoes_ligadas and self.isVisible():
            self.repaint()
        self._anim_modo.setStartValue(0.0)
        self._anim_modo.setEndValue(1.0)
        self._anim_modo.start()

    def _prender_botao_no_topo(self, prender):
        """No modo compacto o botão fica encostado no topo do cartão, não centrado na vertical.

        Em repouso dá no mesmo (a janela tem a altura do botão), mas isso é o que faz o centro do
        botão no compacto ficar a 44px do topo em vez de no meio de um cartão alto — e é desse
        número que sai a posição da janela compacta ancorada pelo botão."""
        if prender:
            if self._mola_compacta is None:
                self._layout_cartao.addStretch(1)
                self._mola_compacta = self._layout_cartao.itemAt(self._layout_cartao.count() - 1)
            return
        if self._mola_compacta is not None:
            self._layout_cartao.removeItem(self._mola_compacta)
            self._mola_compacta = None

    def _reassentar_layout(self):
        """Os dois layouts, na ordem: o de fora dá a geometria do cartão, o de dentro recoloca o
        botão. Só é chamado quando os layouts estão no comando de novo (fim da animação)."""
        self.layout().activate()
        self._layout_cartao.activate()
        self.camada_pulso.reposicionar()

    def _centro_local_do_botao(self, tamanho):
        """Onde o layout do modo já configurado põe o centro do botão numa janela deste tamanho, em
        coordenadas da janela — sem redimensionar a janela de verdade.

        A medição roda o layout do cartão **do mesmo jeito que o assentamento final roda**: põe o
        cartão no retângulo que ele terá e chama `activate()`. Chamar `setGeometry()` direto no
        layout dá outro número quando o layout foi congelado no meio de uma animação (medido: botão
        em x=35 em vez de x=8 numa janela de 88px), e um erro aqui vira erro de posição da janela
        inteira, porque é deste centro que sai a âncora. Como nada volta ao laço de eventos entre
        isto e o quadro seguinte — quem chama sempre reposiciona logo depois —, nada disso chega a
        ser pintado.

        5ª volta: a medição também impõe, **só durante o `activate()`**, a visibilidade que o
        conteúdo só-expandido terá no modo `self._expandido`, e devolve a de antes. Um layout só
        conta widget visível: medido nesta suíte, o centro do botão na janela expandida sai em
        y=76 com esse conteúdo visível e em y=239 com ele escondido — 163px de erro, que viraria
        um pulo do botão no assentamento. Antes da 5ª volta quem garantia isso era um
        `setVisible(expandido)` ao vivo dentro de `_aplicar_modo`, que mostrava a caixa de texto e
        os botões dentro da janela de 88px por um instante; aqui a mesma condição vale só pelo
        tempo da conta, sem nunca voltar ao laço de eventos (nada é pintado)."""
        margens = self._layout_externo.contentsMargins()
        largura = max(0, tamanho.width() - margens.left() - margens.right())
        altura = max(0, tamanho.height() - margens.top() - margens.bottom())
        estava_ligado = self._layout_cartao.isEnabled()
        # isHidden(), não isVisible(): antes do primeiro show() da janela todo filho é "invisível"
        # sem estar escondido, e restaurar por isVisible() esconderia tudo para sempre.
        escondidos_antes = [widget.isHidden() for widget in self._widgets_so_expandido]
        geometria_anterior = QRect(self.cartao.geometry())
        for widget in self._widgets_so_expandido:
            widget.setVisible(self._expandido)
        self._layout_cartao.setEnabled(True)
        self.cartao.setGeometry(margens.left(), margens.top(), largura, altura)
        self._layout_cartao.invalidate()
        self._layout_cartao.activate()
        centro = self.botao_gravar.geometry().center()
        self.cartao.setGeometry(geometria_anterior)
        self._layout_cartao.setEnabled(estava_ligado)
        for widget, escondido in zip(self._widgets_so_expandido, escondidos_antes):
            widget.setVisible(not escondido)
        return QPoint(centro.x() + margens.left(), centro.y() + margens.top())

    def _encaixar_na_tela(self, topo, tamanho, referencia):
        """Empurra o retângulo para dentro da área visível da tela onde está a referência."""
        tela = QGuiApplication.screenAt(referencia) or self.screen() or QGuiApplication.primaryScreen()
        if tela is None:
            return QPoint(topo)
        area = tela.availableGeometry()
        return QPoint(
            min(max(topo.x(), area.left()), max(area.left(), area.right() - tamanho.width() + 1)),
            min(max(topo.y(), area.top()), max(area.top(), area.bottom() - tamanho.height() + 1)),
        )

    def _geometria_do_modo(self, expandido, centro_global, centro_local=None):
        """Retângulo final da janela no modo: o tamanho do modo, posicionado para o centro do botão
        de gravar cair em `centro_global` (a âncora — os dois tamanhos giram em torno do mesmo ponto
        da tela), encaixado na área visível. Com `centro_global` nulo a janela não se move: é o caso
        da abertura, cuja posição inicial é escolhida em _montar_ui e não pode ser desfeita aqui.

        `centro_local` é o resultado de `_centro_local_do_botao` para este mesmo tamanho, quando
        quem chama já mediu (5ª volta: `_aplicar_modo` reaproveita a medição em vez de repeti-la)."""
        tamanho = self._tamanho_do_modo(expandido)
        if expandido:
            # 9ª volta: o modo expandido É a janela — ela tem esse tamanho sempre, então não há
            # o que ancorar aqui; quem mantém o botão parado é o offset do compacto, medido
            # contra este mesmo layout.
            # 10ª volta: mas o encaixe na tela VOLTOU, e só para este modo. Sem ele, um botão
            # arrastado para perto de uma borda deixa a janela de 448x366 pela metade fora da
            # tela e o cartão expandido aparece cortado — medido pelo PM: o botão precisaria
            # ficar a 223px das laterais e 305px da base, o que é o canto onde um botão
            # flutuante de ditado mora. Quem move a janela (uma vez, no começo da transição) é
            # `_aplicar_modo`; aqui só se diz para onde.
            referencia = centro_global if centro_global is not None else self.geometry().center()
            return QRect(self._encaixar_na_tela(self.pos(), tamanho, referencia), tamanho)
        if centro_global is None:
            return QRect(self.pos(), tamanho)
        if centro_local is None:
            centro_local = self._centro_local_do_botao(tamanho)
        # Sem `_encaixar_na_tela`: encaixar o retângulo compacto empurraria o botão na tela ao
        # encolher (o desvio de 0px das rodadas 3-5 é invariante) e, como a janela não se mexe,
        # o encaixe teria de mover a janela — justamente o que esta volta elimina. A janela
        # nasce dentro da tela em _montar_ui e o usuário a arrasta a partir dali.
        return QRect(centro_global - centro_local, tamanho)

    def _offset_do_retangulo(self, geo):
        """Onde o retângulo do modo mora DENTRO da janela fixa (9ª volta, D-32).

        No expandido é sempre (0,0) — o modo expandido é a janela inteira. No compacto é a
        diferença entre o retângulo ancorado no botão e o canto da janela, presa aos limites da
        janela: um offset fora deles poria o cartão para fora do recorte e sumiria com o botão."""
        if self._expandido:
            return QPoint(0, 0)
        offset = geo.topLeft() - self.pos()
        limite_x = max(0, self.width() - geo.width())
        limite_y = max(0, self.height() - geo.height())
        preso = QPoint(
            min(max(offset.x(), 0), limite_x),
            min(max(offset.y(), 0), limite_y),
        )
        if preso != offset:
            log.info(
                "offset_compacto_preso pedido=%d,%d virou=%d,%d janela=%dx%d",
                offset.x(), offset.y(), preso.x(), preso.y(), self.width(), self.height(),
            )
        return preso

    def _retangulo_mascara(self):
        """A parte da janela que fica visível e clicável — o resto passa clique para a janela de
        baixo (9ª volta, D-32).

        É o retângulo do cartão do modo com `FOLGA_MASCARA_PX` de folga, unido ao de qualquer
        sobreposto que passe dele. **Retangular de propósito**: `setMask` é 1 bit e uma região
        arredondada serrilharia os cantos do cartão; dentro da máscara o alfa por pixel de
        `WA_TranslucentBackground` continua valendo, então o arredondado segue suave — a máscara só
        corta área que já era 100% transparente. O preço são os quatro cantinhos externos do
        retângulo, que seguem não-clicáveis-através.

        Os sobrepostos entram na conta porque o painel de Configurações ocupa a janela inteira (ver
        `resizeEvent`): recortar só o cartão o cortaria junto. Popups de janela própria (menu ⋮,
        Consumo, Gerar imagem) não entram — não são recortados pela máscara desta janela."""
        area = QRect(self.cartao.geometry())
        # A CamadaPulso NÃO entra: ela é um widget de 110x110 em volta de um botão de 72 (só
        # para o anel ter espaço para crescer), e no compacto isso inflaria a máscara de 84
        # para 96 — área invisível clicável de novo, que é o que esta volta veio tirar. O anel
        # que ela de fato desenha (raio ~46px) cabe dentro do cartão expandido, e no compacto
        # ele nunca chega a existir: gravar expande a janela antes de pulsar.
        if self.toast is not None and self.toast.isVisible():
            area = area.united(QRect(self.toast.mapTo(self, QPoint(0, 0)), self.toast.size()))
        for filho in self.children():
            if not isinstance(filho, QWidget) or filho is self.cartao:
                continue
            if filho.isWindow() or not filho.isVisible():
                continue
            area = area.united(filho.geometry())
        folga = FOLGA_MASCARA_PX
        return area.adjusted(-folga, -folga, folga, folga).intersected(self.rect())

    def _aplicar_mascara(self):
        """Põe a máscara do modo. Devolve True se ela mudou de fato — é o que garante *um* setMask
        por transição: o vigia de 100ms chama isto toda hora e não chama o sistema à toa."""
        retangulo = self._retangulo_mascara()
        if self._mascara_atual is not None and self._mascara_atual == retangulo:
            return False
        self._mascara_atual = QRect(retangulo)
        self.setMask(QRegion(retangulo))
        return True

    def _limpar_mascara(self):
        """Tira a máscara: a janela inteira volta a aparecer, como o retângulo-união da 4ª volta.
        É o que roda no começo de cada transição — a máscara não muda quadro a quadro."""
        if self._mascara_atual is None:
            return False
        self._mascara_atual = None
        self.clearMask()
        return True

    def _assentar_modo(self, geo):
        """Fim da animação (ou troca sem animação): layouts de volta no comando, cartão no
        retângulo do modo e máscara do modo aplicada.

        9ª volta (D-32): `geo` é o retângulo do MODO em coordenada de tela — o que o usuário
        enxerga —, não mais a geometria da janela nativa, que é fixa e não se mexe. O que se faz
        com ele é guardar onde ele mora dentro da janela (`_offset_visivel`) e recortar a janela
        nessa área com `setMask`. No expandido o retângulo do modo é a janela inteira e quem
        posiciona o cartão continua sendo o layout externo; no compacto o layout externo fica
        FORA do comando (ele encheria os 448x366 com o cartão) e o cartão de 80x80 é posto à mão
        no offset ancorado — o mesmo ponto em que a animação o deixou, então nada salta na tela
        no instante do assentamento."""
        self._geo_inicial = None
        self._geo_final = None
        self._geo_transicao = None
        self._geo_visivel = None
        self._offset_visivel = self._offset_do_retangulo(geo)
        self._tamanho_visivel = QSize(geo.size())
        self._layout_cartao.setEnabled(True)
        self._layout_externo.setEnabled(self._expandido)
        for widget in self._widgets_so_expandido:
            widget.setVisible(self._expandido)
        # D-32 9ª volta — aqui NÃO há mais redimensionamento nativo nenhum (era o único que
        # sobrava, e é o suspeito que explicava a assimetria do sintoma: no encolhimento ele
        # caía no fim da transição, que é exatamente onde o usuário via o pisca). O envelope da
        # 8ª volta continua valendo para o que sobrou — reflow do cartão e troca de máscara sem
        # pintura parcial no meio, com repaint() SÍNCRONO (não update(), que é assíncrono) para
        # publicar o quadro já correto antes de devolver o controle ao laço de eventos.
        atualizacoes_ligadas = self.updatesEnabled()
        self.setUpdatesEnabled(False)
        try:
            if self._expandido:
                # 10ª volta: assentamento sem animação (abertura, reversão instantânea, rede de
                # segurança) — aqui não passou ninguém para mover a janela antes, então o
                # encaixe na tela é aplicado agora. Na transição animada este move nunca
                # dispara: `_aplicar_modo` já pôs a janela em `geo_final.topLeft()`.
                if geo.topLeft() != self.pos():
                    self.move(geo.topLeft())
                self._reassentar_layout()
            else:
                # sem layout externo no comando: o cartão do compacto é um retângulo posto à mão
                # dentro da janela grande, no offset que mantém o botão onde ele estava.
                self.cartao.setGeometry(QRect(self._offset_visivel, geo.size()))
                self._layout_cartao.activate()
                self.camada_pulso.reposicionar()
            self._aplicar_mascara()
        finally:
            self.setUpdatesEnabled(atualizacoes_ligadas)
        if atualizacoes_ligadas and self.isVisible():
            self.repaint()
        # D-32 7ª volta: agora que a transição assentou, o anel de pulso pode começar sem disputar
        # quadro com ela (ver CamadaPulso.definir_estado).
        self.camada_pulso.liberar_pulso_adiado()
        self._registrar_geometria_compacta()

    def _ao_terminar_animacao_modo(self):
        if self._geo_final is None:
            return
        self._assentar_modo(self._geo_final)

    def _get_progresso_modo(self):
        return self._progresso_modo

    def _set_progresso_modo(self, valor):
        self._progresso_modo = valor
        inicial, final = self._geo_inicial, self._geo_final
        if inicial is None or final is None:
            return

        def entre(a, b):
            return round(a + (b - a) * valor)

        # O retângulo VISÍVEL do quadro — o que a janela nativa mostrava a cada quadro até a 3ª
        # volta. Da 4ª volta em diante a janela do SO não se mexe mais aqui (ficou parada em
        # _geo_transicao, ver _aplicar_modo): quem cresce e encolhe na tela é o cartão.
        geo = QRect(
            entre(inicial.x(), final.x()), entre(inicial.y(), final.y()),
            entre(inicial.width(), final.width()), entre(inicial.height(), final.height()),
        )
        self._geo_visivel = geo
        base = self._geo_transicao if self._geo_transicao is not None else geo
        # Com os dois layouts congelados, quem põe o cartão e o botão no lugar é isto — por
        # coordenada absoluta. Quando a âncora é respeitada nas duas pontas (o caso normal), os
        # dois centros são o mesmo ponto da tela e o botão fica parado quadro a quadro; quando a
        # borda da tela obriga a janela cheia a se deslocar, ele desliza em vez de saltar.
        margem = entre(self._margem_inicial, self._margem_final)
        # O cartão vai para onde a janela iria: mesmo lugar na TELA de antes, só que expresso em
        # coordenada da janela-união (por isso o desconto de base.topLeft()).
        self.cartao.setGeometry(
            geo.x() - base.x() + margem, geo.y() - base.y() + margem,
            max(0, geo.width() - 2 * margem), max(0, geo.height() - 2 * margem),
        )
        # O centro do botão é interpolado em coordenadas de TELA e só então convertido para
        # dentro do cartão já arredondado — assim, quando as duas pontas são o mesmo ponto (âncora
        # respeitada), todo quadro dá exatamente esse ponto, sem o 1px de erro que apareceria ao
        # arredondar a posição do cartão e a do botão em separado.
        global_ini = self._centro_inicial_global
        global_fim = self._centro_final_global
        centro = QPoint(entre(global_ini.x(), global_fim.x()), entre(global_ini.y(), global_fim.y()))
        meio = self.botao_gravar.rect().center()  # (35,35) num botão de 72: não é width()//2
        # o cartão está, na tela, em geo.topLeft() + margem — a conta não muda com a janela-união
        self.botao_gravar.move(
            centro.x() - geo.x() - margem - meio.x(),
            centro.y() - geo.y() - margem - meio.y(),
        )
        self.camada_pulso.reposicionar()

    progressoModo = Property(float, _get_progresso_modo, _set_progresso_modo)

    def _animando_modo(self):
        return self._anim_modo.state() == QAbstractAnimation.Running

    def _geometria_visivel(self):
        """O retângulo do modo que o usuário enxerga, em coordenada de tela.

        9ª volta (D-32): `self.geometry()` deixou de ser o que aparece **também fora da
        transição** — a janela nativa é 448x366 nos dois modos, e no compacto quase tudo isso é
        área invisível em volta de um cartão de 80x80. Por aqui passam o hover
        (`_vigiar_ponteiro`), a reversão no meio da animação, a âncora e a rede de segurança:
        quem perguntasse a `self.geometry()` acharia que o usuário enxerga 448x366 e expandiria
        a janela com o mouse a 200px do botão.

        Durante a transição vale o retângulo interpolado (`_geo_visivel`), que é o cartão
        desenhado naquele quadro; fora dela, o retângulo do modo no offset em que ele mora
        dentro da janela. Sobra uma diferença conhecida no expandido: o retângulo do modo
        inclui os 8px de `MARGEM_EXTERNA_EXPANDIDA` (borda transparente), enquanto a máscara
        para no cartão + folga — ou seja, o hover ainda pega essa borda, como sempre pegou."""
        if self._geo_visivel is not None:
            return QRect(self._geo_visivel)
        return QRect(self.pos() + self._offset_visivel, self._tamanho_visivel)

    def _registrar_geometria_compacta(self):
        """Evidência para a próxima rodada, escrita uma vez por valor novo (não a cada troca de
        modo): o que o Qt entrega depois de assentar o compacto.

        9ª volta (D-32): quem tem o tamanho do modo agora é a MÁSCARA — a janela é 448x366 nos
        dois modos. Então a linha passa a trazer a região aplicada (posição e tamanho dentro da
        janela) ao lado do alvo e do tamanho nativo. Se no Windows real a máscara não pegar, é
        aqui que se vê: alvo 80x80 com região de outro tamanho, ou nenhuma região."""
        if self._expandido:
            return
        regiao = self._mascara_atual
        marca = (
            (regiao.x(), regiao.y(), regiao.width(), regiao.height()) if regiao is not None
            else None,
            self.width(), self.height(),
            round(self.devicePixelRatioF(), 2),
        )
        if marca == self._ultima_marca_compacta:
            return
        self._ultima_marca_compacta = marca
        lado = self._lado_compacto()
        log.info(
            "compacto alvo=%dx%d mascara=%s janela=%dx%d dpr=%s",
            lado, lado,
            "%dx%d+%d+%d" % (marca[0][2], marca[0][3], marca[0][0], marca[0][1])
            if marca[0] is not None else "nenhuma",
            marca[1], marca[2], marca[3],
        )

    def _vigiar_ponteiro(self):
        if not self.isVisible():
            return
        self._atualizar_ponteiro(self._geometria_visivel().contains(QCursor.pos()))
        self._corrigir_tamanho_do_modo()

    def _corrigir_tamanho_do_modo(self):
        """Rede de segurança do vigia (10x/s), agora sobre a MÁSCARA (9ª volta, D-32).

        Até a 8ª volta isto comparava `self.width()/height()` com o tamanho do modo. Não serve
        mais: a janela nativa é 448x366 nos dois modos, então a comparação antiga acusaria
        "fora do modo" 10 vezes por segundo, para sempre, no compacto. Quem carrega o tamanho
        do modo hoje é a região da máscara — e é ela que este vigia mantém em dia.

        Duas coisas, por ordem de gravidade: (1) se o sistema de janelas mexeu no tamanho fixo
        da janela, reassenta o modo inteiro (é o caso que a 2ª volta pegou no uso real, janela
        presa no tamanho errado); (2) se só a região divergiu — um sobreposto abriu ou fechou —,
        reaplica a máscara, que é barato e não mexe em layout. `_aplicar_mascara` só chama o
        sistema quando a região mudou de verdade, então isto não vira um SetWindowRgn por tique.

        O log é limitado a uma linha a cada 5s: se o sistema estiver recusando o tamanho, esta
        rede dispara 10 vezes por segundo e sem o limite encheria o app.log — mas a primeira
        linha já é a prova de que a recusa vem de fora deste código."""
        if self._animando_modo() or self._geo_transicao is not None:
            return
        destino = QSize(self._tamanho_expandido)
        if abs(self.width() - destino.width()) > 2 or abs(self.height() - destino.height()) > 2:
            agora = time.monotonic()
            if agora - self._ultimo_log_correcao >= 5.0:
                self._ultimo_log_correcao = agora
                log.info(
                    "tamanho_fora_do_modo expandido=%s alvo=%dx%d real=%dx%d",
                    self._expandido, destino.width(), destino.height(),
                    self.width(), self.height(),
                )
            self.setFixedSize(destino)
            centro = self.botao_gravar.mapToGlobal(self.botao_gravar.rect().center())
            self._assentar_modo(self._geometria_do_modo(self._expandido, centro))
            return
        if self._aplicar_mascara():
            agora = time.monotonic()
            if agora - self._ultimo_log_correcao >= 5.0:
                self._ultimo_log_correcao = agora
                log.info(
                    "mascara_fora_do_modo expandido=%s regiao=%s",
                    self._expandido, self._mascara_atual,
                )

    def _atualizar_ponteiro(self, dentro):
        """Vigia a posição do cursor em vez de usar enterEvent/leaveEvent: num widget cheio de
        filhos o leaveEvent dispara toda vez que o mouse entra num filho — era a receita do
        flicker. Sair de verdade só encolhe depois do debounce, cancelado se o mouse voltar."""
        self._ponteiro_dentro = dentro
        if dentro:
            self._timer_encolher.stop()
            if not self._expandido:
                self._aplicar_modo(True)
            return
        if self._pode_encolher():
            if not self._timer_encolher.isActive():
                self._timer_encolher.start(ATRASO_ENCOLHER_MS)
        else:
            self._timer_encolher.stop()

    def _resultado_pendente(self):
        """D-32 item 4 — há resultado na tela que ainda não foi colocado? Derivado da caixa de
        texto e do último texto colocado, e não de um sinalizador guardado à parte: o sinalizador
        só era desligado em dois cliques (copiar/recortar e apagar pela lixeira), então qualquer
        outro caminho que mexesse no texto — apagar pelo teclado, editar à mão, Ctrl+X dentro da
        caixa — o deixava ligado para sempre e a janela nunca mais encolhia (bug de 2026-09-05)."""
        atual = self.caixa_texto.toPlainText().strip()
        return bool(atual) and atual != self._texto_colocado

    def _pode_encolher(self):
        if not self._expandido or self.gravando or self.processando:
            return False
        if self._resultado_pendente():
            return False  # D-32 item 4: resultado na tela e ainda não colocado — não encolhe
        if self.menu_avancado.isVisible() or self.painel_configuracoes.isVisible():
            return False
        if self.painel_login.isVisible():
            return False  # Etapa 5: o login é um sobreposto desta janela, como Configurações
        if self.painel_consumo.isVisible() or self.janela_gerar_imagem.isVisible():
            return False
        return True

    def _encolher_se_puder(self):
        if self._ponteiro_dentro or not self._pode_encolher():
            return
        self._aplicar_modo(False)

    def _definir_estado_botao(self, estado):
        """Um lugar só troca o estado do botão — e é por aqui que gravando/processando expandem a
        janela sozinhos, com o mouse longe (D-32 item 3)."""
        vai_expandir = estado in ("gravando", "processando") and not self._expandido
        # D-32 7ª volta — a troca de estado do botão (cor/ícone, imediata) acontece ANTES de
        # _aplicar_modo, então, no instante em que a CamadaPulso pergunta se há transição em
        # andamento, ela ainda não começou. Este sinalizador é o "vai começar agora" que a
        # pergunta sozinha não enxerga — sem ele o temporizador de 30ms do pulso nasceria junto
        # com os quadros da transição, que é a hipótese de causa do pisca-pisca do botão vermelho.
        self._transicao_de_modo_pendente = vai_expandir
        try:
            self.botao_gravar.definir_estado(estado)
        finally:
            self._transicao_de_modo_pendente = False
        if estado in ("gravando", "processando"):
            if vai_expandir:
                self._aplicar_modo(True)
            return
        # voltou a parado: reavalia na hora (o vigia do ponteiro também reavalia, 100ms depois)
        self._atualizar_ponteiro(self._ponteiro_dentro)

    # --- arrastar sem moldura (D-32) ---------------------------------------------
    def arraste_iniciar(self, pos_global):
        self._offset_arraste = pos_global - self.frameGeometry().topLeft()

    def arraste_mover(self, pos_global):
        if self._offset_arraste is None:
            return False
        destino = pos_global - self._offset_arraste
        if self._geo_transicao is not None:
            # A transição guarda retângulos e centros em coordenada de TELA; arrastar no meio dela
            # move a janela por fora da animação, então todos acompanham o deslocamento — senão o
            # assentamento final devolveria a janela para onde ela estava antes do arrasto.
            delta = destino - self.pos()
            self._geo_inicial.translate(delta)
            self._geo_final.translate(delta)
            self._geo_transicao.translate(delta)
            self._centro_inicial_global += delta
            self._centro_final_global += delta
        self.move(destino)
        return True

    def arraste_fim(self):
        self._offset_arraste = None

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self.arraste_iniciar(evento.globalPosition().toPoint())
            evento.accept()
            return
        super().mousePressEvent(evento)

    def mouseMoveEvent(self, evento):
        if self._offset_arraste is not None and (evento.buttons() & Qt.LeftButton):
            self.arraste_mover(evento.globalPosition().toPoint())
            evento.accept()
            return
        super().mouseMoveEvent(evento)

    def mouseReleaseEvent(self, evento):
        self.arraste_fim()
        super().mouseReleaseEvent(evento)

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
        if self.painel_login.isVisible():
            self.painel_login.setGeometry(self.rect())
        if self.toast.isVisible():
            self.toast._reposicionar()
        self.camada_pulso.reposicionar()

    def keyPressEvent(self, evento):
        # H1: dentro da janela de Consumo, o popup de requisição tem prioridade sobre ela mesma
        # (ver PainelConsumo.keyPressEvent) — aqui só sobra Configurações.
        if evento.key() == Qt.Key_Escape and self.painel_configuracoes.isVisible():
            self.painel_configuracoes.esconder()
            return
        if evento.key() == Qt.Key_Escape and self.painel_login.isVisible():
            self.painel_login.esconder()
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
        self._definir_estado_botao("processando")
        self._disparar_transcricao(caminho, nome_arquivo, apagar_arquivo_depois=False)

    def _abrir_menu_avancado(self):
        # Alinha a borda DIREITA do menu com a do botão ⋮ — ele é o mais à esquerda do trio; abrir
        # a partir da borda esquerda (padrão do Qt) faria o menu crescer para a direita, por cima
        # do botão de gravar e do cancelar (achado no uso real, 2026-08-27).
        largura_menu = self.menu_avancado.sizeHint().width()
        x = self.botao_menu.width() - largura_menu
        self.menu_avancado.popup(self.botao_menu.mapToGlobal(QPoint(x, self.botao_menu.height() + 4)))

    # --- sessão do núcleo remoto (Etapa 5) ------------------------------------------
    def pedir_login_se_preciso(self):
        """Na abertura: o núcleo configurado exige login e não há sessão guardada → pede agora,
        uma vez, em vez de deixar para o primeiro ditado."""
        if url_exige_login(self.config, self.config["url_nucleo"]) and not self.sessao.ativa:
            self.pedir_login()

    def pedir_login(self, motivo=""):
        if self.painel_configuracoes.isVisible():
            self.painel_configuracoes.esconder()
        if not self._expandido:
            self._aplicar_modo(True)
        self.painel_login.mostrar(motivo)

    def _ao_entrar_na_conta(self):
        self.toast.mostrar("confirmacao", "Conta conectada.", DURACAO_TOAST_CONFIRMACAO_MS)
        self.painel_configuracoes.atualizar_conta()
        if self.painel_consumo.isVisible():
            self.painel_consumo.mostrar()  # recarrega o que tinha voltado com sessão expirada
        self._retomar_pendentes_login()

    def _sair_da_conta(self):
        self.sessao.sair()
        self.painel_configuracoes.atualizar_conta()
        self.toast.mostrar(
            "confirmacao", "Você saiu da conta — o próximo ditado pede login.", DURACAO_TOAST_CONFIRMACAO_MS
        )

    def _ao_expirar_sessao_na_transcricao(self, caminho_arquivo, nome_arquivo, apagar_arquivo_depois):
        """O áudio (ou o arquivo enviado) fica guardado e é reenviado depois do login — o texto da
        caixa não é tocado."""
        self._pendentes_login.append((caminho_arquivo, nome_arquivo, apagar_arquivo_depois))
        log.info("sessao_expirada pendentes=%d", len(self._pendentes_login))
        self.pedir_login(MENSAGEM_SESSAO_EXPIRADA)
        self.processando = False
        self._definir_estado_botao("parado")

    def _retomar_pendentes_login(self):
        if self.gravando or self.processando or not self.sessao.ativa:
            return
        while self._pendentes_login:
            caminho, nome, apagar = self._pendentes_login.pop(0)
            if not os.path.exists(caminho):
                continue
            self.processando = True
            self._definir_estado_botao("processando")
            self._disparar_transcricao(caminho, nome, apagar)
            return

    def _abrir_planejamento(self):
        """Abre a página de Planejamento e Execução no navegador padrão (pedido direto, 2026-09-25)."""
        log.info("menu: abrir planejamento")
        QDesktopServices.openUrl(QUrl(URL_PLANEJAMENTO))

    def _sair(self):
        """D-32 3a volta — encerramento normal pela interface. Sem moldura nao ha X para fechar, e
        sobrava so o Alt+F4. Fecha a janela (o closeEvent solta o atalho global e o stream de audio)
        e derruba o laco de eventos: as janelas filhas escondidas (Consumo, Gerar imagem) segurariam
        a aplicacao viva se o fechamento da janela principal fosse o unico gesto."""
        self.close()
        QApplication.quit()

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

        self._definir_estado_botao("gravando")
        self._atualizar_icone_cancelar(ativo=True)
        self.rotulo_cronometro.setText("00:00")
        self.barra_amplitude.reiniciar(gravando=True)

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
            self._definir_estado_botao("parado")
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
        self.barra_amplitude.reiniciar(gravando=False)
        if self.stream_audio is not None:
            self.stream_audio.stop()
            self.stream_audio.close()
            self.stream_audio = None

    def cancelar_gravacao(self):
        if not self.gravando:
            return
        self.gravando = False
        self._parar_temporizadores_e_stream()
        self._definir_estado_botao("parado")
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
            self._definir_estado_botao("parado")
            log.info("descarte_por_silencio pico=%.4f limiar=%.4f", pico, LIMIAR_SILENCIO_PICO)
            self.toast.mostrar("erro", "Não foi identificado nenhuma fala", DURACAO_TOAST_SEM_FALA_MS)
            return

        self._definir_estado_botao("processando")
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
        self._definir_estado_botao("processando")
        self._disparar_transcricao(caminho, nome_arquivo, apagar_arquivo_depois=False)

    # --- transcrição (chamada ao núcleo) -----------------------------------------
    def _disparar_transcricao(self, caminho_arquivo, nome_arquivo, apagar_arquivo_depois):
        self.toast.esconder()  # "andamento" não mostra texto — o spinner já conta a história (B1)
        texto_base = self.caixa_texto.toPlainText()
        url = self.config["url_nucleo"]
        self._trabalho = TrabalhoTranscricao(
            url_nucleo=url,
            caminho_arquivo=caminho_arquivo,
            nome_arquivo=nome_arquivo,
            modelo=self.config["modelo"],
            streaming=self.config["streaming"],
            texto_base=texto_base,
            apagar_arquivo_depois=apagar_arquivo_depois,
            sessao=self.sessao,
            exigir_login=url_exige_login(self.config, url),
        )
        self._trabalho.progresso.connect(self._ao_progresso_transcricao)
        self._trabalho.concluido.connect(self._ao_concluir_transcricao)
        self._trabalho.falhou.connect(self._ao_falhar_transcricao)
        sinal_sessao = getattr(self._trabalho, "sessao_expirada", None)
        if sinal_sessao is not None:
            sinal_sessao.connect(
                lambda: self._ao_expirar_sessao_na_transcricao(caminho_arquivo, nome_arquivo, apagar_arquivo_depois)
            )
        self._trabalho.start()

    def _ao_progresso_transcricao(self, texto_acumulado):
        self._escrever_texto(texto_acumulado)

    def _ao_concluir_transcricao(self, texto_final):
        self._escrever_texto(texto_final)
        self.processando = False
        self._definir_estado_botao("parado")
        self.toast.mostrar("confirmacao", "Transcrição adicionada ao texto abaixo.", DURACAO_TOAST_CONFIRMACAO_MS)
        if self._pendentes_login:
            QTimer.singleShot(0, self._retomar_pendentes_login)

    def _ao_falhar_transcricao(self, mensagem, codigo):
        self.processando = False
        self._definir_estado_botao("parado")
        if codigo:
            log.info("erro_nucleo codigo=%s", codigo)
        self.toast.mostrar("erro", mensagem, DURACAO_TOAST_ERRO_MS)
        if self._pendentes_login:
            QTimer.singleShot(0, self._retomar_pendentes_login)

    # --- caixa de transcrição: acumula, editável, desfazer (C) ---------------------
    def _escrever_texto(self, valor):
        self.caixa_texto.blockSignals(True)
        self.caixa_texto.setPlainText(valor)
        cursor = self.caixa_texto.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.caixa_texto.setTextCursor(cursor)
        self.caixa_texto.blockSignals(False)
        # D-32 item 4: nada a marcar aqui — texto novo na caixa já é "pendente" por definição,
        # porque difere do último texto colocado (ver _resultado_pendente()).
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
        self._atualizar_botao_lixeira()  # caixa vazia já não é pendente (ver _resultado_pendente)

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
        self._texto_colocado = texto.strip()  # colocado — agora o mouse sair pode encolher (D-32)
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
    # Etapa 5 — sem sessão e com o núcleo remoto configurado, o login aparece já na abertura.
    # Fica em main(), e não em JanelaDitado.__init__, para quem monta a janela (os testes
    # headless) não herdar um sobreposto que não pediu.
    QTimer.singleShot(400, janela.pedir_login_se_preciso)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
