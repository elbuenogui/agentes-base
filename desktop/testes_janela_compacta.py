"""Testes headless da janela compacta/expandida (D-32, segunda volta — 2026-09-05).

Roda sem tela, sem microfone e sem núcleo: `QT_QPA_PLATFORM=offscreen`, `keyboard`/`sounddevice`
substituídos por dublês quando não existirem, e a transcrição trocada por um trabalho falso (nenhuma
chamada paga à OpenAI). O que ele cobre e por quê:

- **dois ciclos completos** (gravar → colocar → mouse fora → encolheu) e mais um terceiro. A suíte da
  primeira volta só cobria um ciclo, e foi por isso que o "parou de encolher depois do primeiro
  ciclo" passou batido;
- caminhos que mexem no texto **por fora** dos dois botões (apagar pelo teclado, editar à mão), que
  eram os que travavam o encolhimento para sempre;
- tamanho do compacto medido contra o `BotaoGravar` de verdade;
- âncora do centro do botão nos dois tamanhos **e em cada quadro** da animação;
- animação nos dois sentidos, com interrupção/reversão no meio;
- (3ª volta) **o botão como ele aparece na tela**, quadro a quadro, contado em pixels do `grab()` —
  a suíte da 2ª volta media só a coordenada do botão, que continua "certa" mesmo quando o botão
  está fora do recorte da janela e não aparece; era esse o defeito que passou batido;
- (3ª volta) a largura do compacto medida em `width()`, `frameGeometry()` e no mínimo/máximo que o
  Qt informa ao sistema de janelas;
- (3ª volta) o item "Sair" do menu ⋮ encerrando um laço de eventos de verdade;
- (5ª volta) **nenhum widget só-expandido visível durante a transição**, a ordem em que
  `_configurar_layout_do_modo` roda (layouts já congelados) e a medição do centro do botão sem o
  conteúdo na tela — os três pontos da ordem nova de `_aplicar_modo`;
- (4ª volta) **quantas vezes a janela NATIVA muda de `frameGeometry()` numa transição inteira** —
  desde a 4ª volta a animação move o cartão dentro de uma janela parada, e o SO só é chamado no
  começo e no fim. O tamanho que "cresce" na tela deixou de ser `width()` da janela e passou a ser
  `_geometria_visivel()`; os testes de tamanho intermediário medem lá.

- (6ª volta) **a altura da janela expandida e a da caixa de transcrição**, medidas no layout
  real: a caixa passou a ter altura declarada (~1/3 dos 480px de antes) e a janela encolheu
  junto, sem mexer na largura (SPEC-002 I) nem no compacto — que ganhou teste próprio de
  não-regressão.

- (7ª volta) **a largura própria da janela expandida** (não mais a coluna de 40rem da SPEC-002
  item I), os seis cortes nos elementos fixos que baixaram a altura, o compacto em 80x80 — e,
  o mais delicado, **o temporizador de pulso da CamadaPulso não rodando durante os quadros da
  transição de modo** (a hipótese de causa do "botão vermelho tentando desaparecer").

- (8ª volta) **sobreposição de geometria real entre os widgets do cartão** — a 7ª volta travava o
  número da altura (`346`) e passou verde com a tela quebrada na máquina do usuário: o número batia
  consigo mesmo, mas ninguém conferia ONDE cada widget desenhava. O teste `[16]` compara pixels
  (fundo da caixa de transcrição contra o topo da linha de ações) e ainda repõe a altura errada da
  7ª volta para provar que o critério acusa o bug. E o `[17]` tranca a tentativa contra o flicker do
  encolhimento (resize nativo com `setUpdatesEnabled(False)` + `repaint()` síncrono).

Uso: `QT_QPA_PLATFORM=offscreen python desktop/testes_janela_compacta.py`
"""
import os
import sys
import types

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:  # este shell não tem teclado global nem placa de áudio; a máquina do usuário tem
    import keyboard  # noqa: F401
except Exception:  # pragma: no cover - só no ambiente de teste
    _kb = types.ModuleType("keyboard")
    _kb.add_hotkey = lambda *a, **k: None
    _kb.remove_hotkey = lambda *a, **k: None
    _kb.read_hotkey = lambda *a, **k: "ctrl+alt+d"
    sys.modules["keyboard"] = _kb
try:
    import sounddevice  # noqa: F401
except Exception:  # pragma: no cover
    _sd = types.ModuleType("sounddevice")

    class _StreamFalso:
        def __init__(self, **kw):
            pass

        def start(self):
            pass

        def stop(self):
            pass

        def close(self):
            pass

    _sd.InputStream = _StreamFalso
    _sd.query_devices = lambda *a: [
        {"name": "dublê", "max_input_channels": 1, "max_output_channels": 0}
    ]
    _sd.default = types.SimpleNamespace(device=(0, 0))
    sys.modules["sounddevice"] = _sd

import numpy as np
from PySide6.QtCore import Qt, QTimer, QEventLoop, QPoint, QPointF, QRect, QEvent, Signal
from PySide6.QtGui import QColor, QCursor, QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel

import app as A

ATRASO_TRABALHO_MS = 40


class TrabalhoFalso(A.QThread):
    """Substitui TrabalhoTranscricao: devolve texto sem rede, sem núcleo e sem custo."""

    progresso = Signal(str)
    concluido = Signal(str)
    falhou = Signal(str, str)

    def __init__(self, **kw):
        super().__init__()
        self.texto_base = kw.get("texto_base") or ""

    def start(self):
        separador = "\n" if self.texto_base and not self.texto_base.endswith("\n") else ""
        QTimer.singleShot(
            ATRASO_TRABALHO_MS,
            lambda: self.concluido.emit(self.texto_base + separador + "frase ditada"),
        )


def _evento_mouse(tipo, widget, pos_global, botoes):
    local = widget.mapFromGlobal(pos_global)
    return QMouseEvent(tipo, QPointF(local), QPointF(pos_global), Qt.LeftButton, botoes, Qt.NoModifier)


def apertar(widget, pos_global):
    QApplication.sendEvent(widget, _evento_mouse(QEvent.MouseButtonPress, widget, pos_global, Qt.LeftButton))


def mover(widget, pos_global):
    QApplication.sendEvent(widget, _evento_mouse(QEvent.MouseMove, widget, pos_global, Qt.LeftButton))


def soltar(widget, pos_global):
    QApplication.sendEvent(widget, _evento_mouse(QEvent.MouseButtonRelease, widget, pos_global, Qt.NoButton))


def esperar(ms):
    laco = QEventLoop()
    QTimer.singleShot(ms, laco.quit)
    laco.exec()


class Resultado:
    def __init__(self):
        self.ok = 0
        self.falhas = []

    def conferir(self, condicao, descricao):
        if condicao:
            self.ok += 1
        else:
            self.falhas.append(descricao)
            print("  FALHOU:", descricao)


def nova_janela(recortar=True):
    # 8ª volta — higiene entre testes: o teste anterior costuma deixar o cursor no centro do botão
    # (79,79), e a janela nova nasce em (40,40) com 80x80 — ou seja, EMBAIXO do cursor. Se o vigia
    # de 100ms tiquear antes da primeira medição (acontece quando a suíte inteira roda e o laço
    # atrasa alguns ms), a janela expande sozinha e o teste seguinte mede o tamanho errado. Era uma
    # corrida latente da suíte, que só aparecia conforme o tempo total mudava; quem quer o mouse em
    # cima chama entrar() de propósito.
    mouse_longe()
    config = dict(A.carregar_config())
    config["recortar_em_vez_de_copiar"] = recortar
    config["streaming"] = False
    janela = A.JanelaDitado(config)
    janela.show()
    esperar(80)
    return janela


def tam_visivel(janela):
    """9ª volta (D-32): a janela nativa tem UM tamanho só (448x366) nos dois modos — quem
    carrega o tamanho do modo passou a ser o retângulo visível (o cartão) e a máscara que o
    recorta. Todo teste que antes perguntava `janela.size()` para saber "em que modo a janela
    está" pergunta aqui; perguntar à janela devolveria 448x366 sempre."""
    return janela._geometria_visivel().size()


def lado_mascara(janela):
    """O retângulo que a máscara recorta, em coordenadas da janela (None se não há máscara)."""
    return janela._mascara_atual


def centrar(janela, ponto):
    """Põe o centro do botão de gravar em `ponto` — longe das bordas, para a âncora não ser
    aparada pelo encaixe na tela (que é comportamento correto, mas atrapalha a medição)."""
    centro = janela.botao_gravar.mapToGlobal(janela.botao_gravar.rect().center())
    janela.move(janela.pos() + (ponto - centro))
    esperar(30)


def mouse_no_botao(janela):
    QCursor.setPos(janela.botao_gravar.mapToGlobal(janela.botao_gravar.rect().center()))


def mouse_longe():
    QCursor.setPos(QPoint(4000, 4000))


def entrar(janela):
    """Mexe o cursor de verdade *e* avisa na hora: o vigia de 100ms lê QCursor.pos(), então um
    _atualizar_ponteiro sem mover o cursor seria desfeito no tique seguinte."""
    mouse_no_botao(janela)
    janela._atualizar_ponteiro(True)


def sair(janela):
    mouse_longe()
    janela._atualizar_ponteiro(False)


def ciclo_completo(janela, colocar="botao"):
    """gravar → transcrever → colocar o texto → tirar o mouse. Devolve True se encolheu."""
    mouse_no_botao(janela)
    esperar(150)
    janela.iniciar_gravacao()
    janela._callback_audio(
        (np.random.rand(2000, 1).astype("float32") - 0.5) * 1.2, 2000, None, None
    )
    esperar(60)
    janela.parar_e_enviar()
    esperar(ATRASO_TRABALHO_MS + 200)
    if colocar == "botao":
        janela._clicar_copiar()
    elif colocar == "teclado":
        # o usuário apaga a caixa por fora dos dois botões (Ctrl+A, Del): era isto que deixava o
        # sinalizador de "resultado pendente" ligado para sempre
        janela.caixa_texto.clear()
    esperar(60)
    mouse_longe()
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 400)
    return not janela._expandido


def testar_dois_ciclos(r):
    print("[1] dois ciclos completos (mais um terceiro)")
    j = nova_janela()
    lado = j.botao_gravar.height() + 2 * A.MARGEM_JANELA_COMPACTA
    r.conferir(tam_visivel(j) == A.QSize(lado, lado),
               f"nasce compacto {lado}x{lado}, veio {tam_visivel(j)}")
    for n in (1, 2, 3):
        encolheu = ciclo_completo(j)
        r.conferir(encolheu, f"ciclo {n}: encolheu depois de colocar o texto e tirar o mouse")
        r.conferir(
            tam_visivel(j) == A.QSize(lado, lado),
            f"ciclo {n}: voltou ao tamanho compacto (veio {tam_visivel(j)})",
        )
    j.close()


def testar_caixa_mexida_por_fora(r):
    print("[2] caixa esvaziada/editada por fora dos botões não trava o encolhimento")
    j = nova_janela()
    r.conferir(ciclo_completo(j, colocar="botao"), "ciclo 1 (colocou pelo botão) encolheu")
    r.conferir(ciclo_completo(j, colocar="teclado"), "ciclo 2 (caixa apagada pelo teclado) encolheu")
    r.conferir(ciclo_completo(j, colocar="botao"), "ciclo 3 depois disso ainda encolhe")
    # editar à mão um texto já colocado volta a segurar (é resultado não colocado) e destravar
    # depois de colocar de novo
    j._escrever_texto("um texto")
    j._clicar_copiar()
    esperar(30)
    r.conferir(not j._resultado_pendente(), "texto colocado não fica pendente")
    j.caixa_texto.setPlainText("um texto editado à mão")
    esperar(30)
    r.conferir(j._resultado_pendente(), "texto editado depois de colocado volta a ser pendente")
    j.caixa_texto.clear()
    esperar(30)
    r.conferir(not j._resultado_pendente(), "caixa vazia nunca fica pendente")
    j.close()


def testar_tamanho_compacto(r):
    print("[3] compacto = botão de gravar + margem pequena")
    j = nova_janela()
    lado_botao = j.botao_gravar.height()
    esperado = lado_botao + 2 * A.MARGEM_JANELA_COMPACTA
    r.conferir(lado_botao == j.botao_gravar.width(), "o botão é quadrado")
    r.conferir(j._lado_compacto() == esperado, f"lado compacto = {lado_botao}+2x{A.MARGEM_JANELA_COMPACTA}")
    r.conferir(4 <= A.MARGEM_JANELA_COMPACTA <= 8, "a margem por lado cabe em 8-16px no total")
    # 7ª volta: o usuário chamou o respiro de 8px de "essa borda ao redor do botão tão grande".
    r.conferir(
        A.MARGEM_JANELA_COMPACTA == 4,
        f"MARGEM_JANELA_COMPACTA 8 -> 4 (veio {A.MARGEM_JANELA_COMPACTA})",
    )
    r.conferir(
        tam_visivel(j) == A.QSize(80, 80),
        f"o compacto passou de 88x88 para 80x80 (veio {tam_visivel(j)})",
    )
    r.conferir(tam_visivel(j) == A.QSize(esperado, esperado),
               f"o cartão compacto mede {esperado}x{esperado}")
    # 9ª volta: a largura do compacto deixou de morar na janela nativa (que é 448x366 sempre) e
    # passou para a MÁSCARA. É ela que o sistema de janelas recorta, e é ela que o usuário vê.
    # O mínimo/máximo do QWindow, que as 3ª e 4ª voltas vigiavam por causa do mínimo próprio do
    # Windows, agora é o tamanho expandido nos dois modos — travado, e por isso já não é porta
    # de entrada para o sistema impor nada.
    mascara = lado_mascara(j)
    folga = A.FOLGA_MASCARA_PX
    r.conferir(
        mascara is not None and mascara.size() == A.QSize(esperado + 2 * folga, esperado + 2 * folga),
        f"a máscara do compacto é {esperado}+2x{folga} de folga (veio {mascara})",
    )
    r.conferir(
        j.size() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        f"e a janela nativa continua no tamanho único (veio {j.size()})",
    )
    r.conferir(
        j.minimumSize() == j.maximumSize() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        f"mínimo e máximo travados no tamanho único (min {j.minimumSize()}, max {j.maximumSize()})",
    )
    janela_qt = j.windowHandle()
    r.conferir(
        janela_qt is not None
        and janela_qt.minimumSize() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        "o QWindow leva o mesmo mínimo para o sistema de janelas",
    )
    # e durante a animação a máscara sai de cena inteira (nunca muda quadro a quadro)
    j._aplicar_modo(True)
    r.conferir(
        lado_mascara(j) is None,
        f"durante a transição a janela fica sem máscara (veio {lado_mascara(j)})",
    )
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 150)
    j.close()


def testar_altura_expandida(r):
    """D-32, 6ª e 7ª voltas (2026-09-05): a janela expandida encolheu nos dois eixos. Em altura,
    porque a caixa de transcrição passou a ter altura declarada (6ª volta) e porque os elementos
    fixos encolheram (7ª: margens, espaçamentos, barra de amplitude, cronômetro fundido na linha do
    topo). Em largura, porque a janela deixou de seguir a coluna de 40rem da SPEC-002 item I e
    passou a ter LARGURA_EXPANDIDA própria. Mede o layout de verdade em vez de confiar nas
    constantes: se alguém mexer numa margem, num espaçamento ou na linha do topo,
    ALTURA_FIXA_EXPANDIDA para de bater e este teste falha — que é o ponto."""
    print("[13] tamanho da janela expandida: altura medida e largura própria (6ª/7ª voltas)")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()  # sem o vigia a janela fica no modo que o teste pedir
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 200)
    r.conferir(j._expandido, "a janela está expandida para a medição")
    r.conferir(
        j.size() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        f"janela expandida = {A.LARGURA_EXPANDIDA}x{A.ALTURA_EXPANDIDA} (veio {j.size()})",
    )
    # 7ª volta — a largura é própria desta janela e tem de ser VISIVELMENTE menor que os 672px de
    # antes (a 6ª volta cortou 11px de altura e o usuário disse que não mudou nada). O piso é
    # medido no layout real, não escrito à mão: abaixo dele a linha do topo sairia cortada.
    piso = j._layout_externo.minimumSize().width()
    r.conferir(
        A.LARGURA_EXPANDIDA != int(40 * 16) + 32,
        "a largura não é mais a coluna de 40rem da SPEC-002 item I (vínculo revogado em D-32 7ª)",
    )
    r.conferir(
        j.width() <= 672 * 0.75,
        f"a janela expandida ficou ao menos 25% mais estreita que os 672px (veio {j.width()})",
    )
    r.conferir(
        j.width() >= piso,
        f"e ainda cabe a linha do topo inteira (piso medido no layout = {piso})",
    )
    lay_topo = j._layout_cartao.itemAt(0).layout()
    molas = [lay_topo.itemAt(i).geometry().width() for i in (1, lay_topo.count() - 2)]
    r.conferir(
        all(m > 0 for m in molas) and molas[0] == molas[1],
        f"as duas molas da linha do topo sobraram iguais e não-nulas (veio {molas})",
    )
    centro_botao = j.botao_gravar.geometry().center().x()
    centro_cartao = j.cartao.rect().center().x()
    r.conferir(
        abs(centro_botao - centro_cartao) <= 1,
        f"o botão de gravar continua centralizado no cartão ({centro_botao} vs {centro_cartao})",
    )

    caixa = j.caixa_texto
    # 8ª volta: ALTURA_CAIXA_TEXTO é o PISO declarado da caixa, e a janela ganhou
    # FOLGA_ALTURA_EXPANDIDA de sobra contra variação de fonte entre máquinas — a caixa, que é a
    # única com fator de esticar, absorve essa folga. Nunca menos que o piso (era isso que a 7ª
    # volta violava, espremendo a caixa e sobrepondo a linha de baixo).
    r.conferir(
        A.ALTURA_CAIXA_TEXTO <= caixa.height() <= A.ALTURA_CAIXA_TEXTO + A.FOLGA_ALTURA_EXPANDIDA,
        f"a caixa de transcrição ocupa o piso de {A.ALTURA_CAIXA_TEXTO}px + no máximo a folga de "
        f"{A.FOLGA_ALTURA_EXPANDIDA}px (veio {caixa.height()})",
    )
    r.conferir(
        abs(A.ALTURA_CAIXA_TEXTO - 480 // 3) <= 8,
        f"e isso é ~1/3 dos 480px da janela de antes (veio {A.ALTURA_CAIXA_TEXTO})",
    )
    fixo = j.height() - caixa.height()
    r.conferir(
        fixo == A.ALTURA_FIXA_EXPANDIDA + A.FOLGA_ALTURA_EXPANDIDA - (
            caixa.height() - A.ALTURA_CAIXA_TEXTO
        ),
        f"tudo que não é a caixa soma {A.ALTURA_FIXA_EXPANDIDA}px + a folga que a caixa não levou "
        f"(veio {fixo})",
    )
    # 8ª volta — O invariante que faltava: a janela não pode ser MENOR que o mínimo que o layout
    # declara. Era exatamente isso que a 7ª volta fazia (346 contra um mínimo de 362), e como
    # layout_externo usa SetNoConstraint o Qt não recusa: ele sobrepõe os itens.
    minimo_real = j._layout_externo.minimumSize().height()
    r.conferir(
        j.height() >= minimo_real,
        f"a janela é ao menos o mínimo que o layout pede ({minimo_real}px, veio {j.height()})",
    )
    r.conferir(
        j.height() - minimo_real == A.FOLGA_ALTURA_EXPANDIDA,
        f"com exatamente a folga declarada de {A.FOLGA_ALTURA_EXPANDIDA}px de sobra "
        f"(veio {j.height() - minimo_real})",
    )
    r.conferir(
        A.ALTURA_FIXA_EXPANDIDA + A.ALTURA_CAIXA_TEXTO == minimo_real,
        f"e ALTURA_FIXA_EXPANDIDA já inclui as duas margens externas "
        f"({A.ALTURA_FIXA_EXPANDIDA} + {A.ALTURA_CAIXA_TEXTO} = {minimo_real})",
    )
    lay = j._layout_cartao
    soma_itens = sum(lay.itemAt(i).geometry().height() for i in range(lay.count()))
    r.conferir(
        lay.count() == 4,
        f"o cartão tem 4 linhas: o cronômetro virou parte da linha do topo (veio {lay.count()})",
    )
    r.conferir(
        soma_itens == caixa.height() + 72 + A.ALTURA_BARRA_AMPLITUDE + 32,
        f"linha do topo 72 + amplitude {A.ALTURA_BARRA_AMPLITUDE} + ações 32 + caixa "
        f"{caixa.height()} (veio {soma_itens})",
    )
    # 7ª volta — os seis cortes nos elementos fixos, medidos onde eles de fato acontecem
    r.conferir(
        j._layout_cartao.spacing() == A.ESPACAMENTO_CARTAO == 8,
        f"espaçamento do cartão 16 -> 8 (veio {j._layout_cartao.spacing()})",
    )
    r.conferir(
        j._layout_cartao.contentsMargins().left() == A.MARGEM_CARTAO_EXPANDIDA == 16,
        f"margem do cartão 24 -> 16 (veio {j._layout_cartao.contentsMargins().left()})",
    )
    r.conferir(
        j._layout_externo.contentsMargins().left() == A.MARGEM_EXTERNA_EXPANDIDA == 8,
        f"margem externa 16 -> 8 (veio {j._layout_externo.contentsMargins().left()})",
    )
    r.conferir(
        j.barra_amplitude.height() == A.ALTURA_BARRA_AMPLITUDE == 24,
        f"barra de amplitude 40 -> 24 (veio {j.barra_amplitude.height()})",
    )
    r.conferir(
        j.botao_menu.width() == j.botao_cancelar.width() == A.LADO_BOTAO_SECUNDARIO == 32,
        f"⋮ e cancelar 44 -> 32 (veio {j.botao_menu.width()} e {j.botao_cancelar.width()})",
    )
    r.conferir(
        j.botao_gravar.width() == j.botao_gravar.height() == 72,
        f"e o botão de gravar continua 72x72, o alvo visual central (veio {j.botao_gravar.size()})",
    )
    indice_cronometro = [
        i for i in range(lay_topo.count())
        if lay_topo.itemAt(i).widget() is j.rotulo_cronometro
    ]
    r.conferir(
        indice_cronometro == [0],
        f"o cronômetro é o primeiro item da linha do topo, não uma linha própria "
        f"(veio {indice_cronometro})",
    )
    r.conferir(
        j.rotulo_cronometro.y() < j.barra_amplitude.y()
        and j.rotulo_cronometro.geometry().bottom() <= j.botao_gravar.geometry().bottom(),
        "e ele desenha dentro da faixa vertical da linha do topo",
    )
    # 8ª volta: os 25% da 7ª volta (346px) só existiam porque a janela estava menor que o próprio
    # conteúdo — corrigida a conta, a redução real e sustentável é de ~24% (366px). O piso aqui é o
    # layout, não uma meta de porcentagem.
    r.conferir(
        j.height() <= 480 * 0.8,
        f"a janela ficou ao menos 20% mais baixa que os 480px originais (veio {j.height()})",
    )

    # usabilidade: a caixa menor ainda mostra várias linhas sem rolar (item 6 da tarefa)
    linhas = caixa.viewport().height() // caixa.fontMetrics().lineSpacing()
    r.conferir(linhas >= 5, f"a caixa menor ainda mostra {linhas} linhas sem rolar (mínimo 5)")
    caixa.setPlainText("uma frase ditada de tamanho normal, do jeito que sai da transcrição.")
    esperar(30)
    barra = caixa.verticalScrollBar()
    r.conferir(
        barra.maximum() == 0,
        "uma frase normal cabe sem forçar rolagem imediata",
    )
    caixa.clear()
    j.close()


def _retangulo_na_janela(janela, widget):
    """Geometria do widget em coordenadas da JANELA — não do pai dele. Assim a comparação vale
    mesmo que dois widgets estejam em pais diferentes (a caixa é filha do cartão, os botões da
    linha de ações também, mas nada no teste depende disso)."""
    return QRect(widget.mapTo(janela, QPoint(0, 0)), widget.size())


def _sobreposicoes_no_cartao(janela):
    """Todos os pares de widgets do cartão que se sobrepõem de verdade, em pixels da tela.

    Devolve uma lista de (nome_a, nome_b, retângulo_da_interseção) — vazia quando está tudo certo.
    """
    alvos = [
        ("cronometro", janela.rotulo_cronometro),
        ("botao_menu", janela.botao_menu),
        ("botao_gravar", janela.botao_gravar),
        ("botao_cancelar", janela.botao_cancelar),
        ("barra_amplitude", janela.barra_amplitude),
        ("caixa_texto", janela.caixa_texto),
        ("botao_lixeira", janela.botao_lixeira),
        ("botao_copiar", janela.botao_copiar),
    ]
    retangulos = [(nome, _retangulo_na_janela(janela, w)) for nome, w in alvos if w.isVisible()]
    conflitos = []
    for i in range(len(retangulos)):
        for k in range(i + 1, len(retangulos)):
            nome_a, ret_a = retangulos[i]
            nome_b, ret_b = retangulos[k]
            interseccao = ret_a.intersected(ret_b)
            if not interseccao.isEmpty():
                conflitos.append((nome_a, nome_b, interseccao))
    return conflitos


def testar_sem_sobreposicao_no_expandido(r):
    """D-32, 8ª volta (2026-09-05): a REGRESSÃO que chegou ao usuário — "você quebrou o layout e
    colocou o botão de cortar sobrepondo a caixa".

    Por que este teste existe, e por que ele não é mais um teste de altura: a 7ª volta já travava
    o número da altura (`ALTURA_EXPANDIDA == 346`) e passou verde com a tela quebrada. O número
    batia consigo mesmo; o que ninguém conferia era **onde cada widget desenha**. Como
    `layout_externo` usa `SetNoConstraint` (necessário para a animação), o Qt não recusa uma
    janela menor que o conteúdo — ele empilha os itens uns por cima dos outros. Só a geometria
    real dos widgets, comparada em pixels, pega isso.

    A última parte é a prova de que o teste pega o bug: a altura errada da 7ª volta é reposta de
    propósito e o mesmo critério tem de acusar a sobreposição."""
    print("[16] nada se sobrepõe no expandido assentado — geometria real (8ª volta)")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 200)
    r.conferir(j._expandido, "a janela está expandida e assentada para a medição")

    caixa = _retangulo_na_janela(j, j.caixa_texto)
    for nome, widget in (("botao_lixeira", j.botao_lixeira), ("botao_copiar", j.botao_copiar)):
        ret = _retangulo_na_janela(j, widget)
        r.conferir(
            caixa.bottom() < ret.top(),
            f"a caixa de transcrição termina ACIMA de {nome} "
            f"(caixa até y={caixa.bottom()}, {nome} começa em y={ret.top()})",
        )
        r.conferir(
            ret.top() - caixa.bottom() - 1 >= A.ESPACAMENTO_CARTAO,
            f"e ainda com o espaçamento inteiro do cartão entre os dois "
            f"({A.ESPACAMENTO_CARTAO}px; veio {ret.top() - caixa.bottom() - 1})",
        )

    conflitos = _sobreposicoes_no_cartao(j)
    r.conferir(
        not conflitos,
        f"nenhum par de widgets do cartão se sobrepõe (conflitos: {conflitos})",
    )
    r.conferir(
        j.caixa_texto.height() >= A.ALTURA_CAIXA_TEXTO,
        f"a caixa não foi espremida abaixo do mínimo declarado de {A.ALTURA_CAIXA_TEXTO}px "
        f"(veio {j.caixa_texto.height()})",
    )
    cartao = _retangulo_na_janela(j, j.cartao)
    r.conferir(
        cartao.height() >= j.cartao.minimumSizeHint().height(),
        f"o cartão recebeu ao menos o que o próprio mínimo dele pede "
        f"({j.cartao.minimumSizeHint().height()}px; veio {cartao.height()})",
    )
    ultimo = _retangulo_na_janela(j, j.botao_copiar)
    r.conferir(
        ultimo.bottom() <= cartao.bottom() and cartao.bottom() < j.rect().bottom(),
        f"a última linha cabe dentro do cartão, e o cartão dentro da janela "
        f"(ações até {ultimo.bottom()}, cartão até {cartao.bottom()}, janela {j.height()})",
    )

    # --- prova de que este teste pega o bug da 7ª volta -----------------------------------
    # Repõe a altura errada (ALTURA_FIXA_EXPANDIDA sem as duas margens externas, sem folga) e
    # confere que o MESMO critério acusa. Sem isto, "o teste passa" não diria nada.
    altura_da_setima = A.ALTURA_EXPANDIDA - 2 * A.MARGEM_EXTERNA_EXPANDIDA - A.FOLGA_ALTURA_EXPANDIDA
    guardado = A.QSize(j._tamanho_expandido)
    j._tamanho_expandido = A.QSize(A.LARGURA_EXPANDIDA, altura_da_setima)
    # 9ª volta: a janela é fixa, então repor o cenário errado é repor o tamanho FIXO dela.
    j.setFixedSize(j._tamanho_expandido)
    j._aplicar_modo(True, animar=False)
    esperar(60)
    caixa_ruim = _retangulo_na_janela(j, j.caixa_texto)
    acoes_ruim = _retangulo_na_janela(j, j.botao_copiar)
    r.conferir(
        j.height() == altura_da_setima == 346,
        f"cenário da 7ª volta reposto: janela em {altura_da_setima}px (veio {j.height()})",
    )
    r.conferir(
        caixa_ruim.bottom() >= acoes_ruim.top() or bool(_sobreposicoes_no_cartao(j)),
        f"e o critério deste teste ACUSA a sobreposição que chegou ao usuário "
        f"(caixa até y={caixa_ruim.bottom()}, botao_copiar em y={acoes_ruim.top()})",
    )
    j._tamanho_expandido = guardado
    j.setFixedSize(guardado)
    j._aplicar_modo(True, animar=False)
    esperar(60)
    r.conferir(
        not _sobreposicoes_no_cartao(j) and j.height() == A.ALTURA_EXPANDIDA,
        f"e volta a ficar limpo com a altura corrigida de {A.ALTURA_EXPANDIDA}px "
        f"(veio {j.height()})",
    )
    sair(j)
    j.close()


def testar_transicao_sem_resize_nativo(r):
    """9ª volta (D-32) — a mudança de arquitetura, trancada aqui.

    A janela nativa passou a ter UM tamanho só (448x366) e não é redimensionada nem movida em
    transição; quem cresce e encolhe na tela é a máscara, trocada uma vez por transição, no
    assentamento. A leitura que levou a isto: das três tentativas anteriores (4ª, 5ª, 8ª), nenhuma
    eliminou o flicker do hover-out, e a assimetria do sintoma (pisca ao sair, não ao entrar) casa
    com o único redimensionamento nativo do encolhimento, que caía no fim da transição.

    O que este teste PROVA: 0 setGeometry/resize/move nativos nos dois sentidos, exatamente 1
    setMask e 1 clearMask por transição (nesta ordem), as duas trocas com as atualizações
    desligadas e um repaint() síncrono depois de religar. O que ele NÃO PROVA: que o flicker
    acabou. Não há compositor no offscreen — o plugin nem aplica máscara de janela ("This plugin
    does not support setting window masks" no stderr), então o efeito VISUAL da máscara aqui é
    zero. Só o uso real no Windows decide."""
    print("[17] transição sem resize/move nativo, com uma troca de máscara (9ª volta)")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()
    registro = []
    nomes_espiados = ("setGeometry", "resize", "move", "setMask", "clearMask", "repaint")
    reais = {nome: getattr(j, nome) for nome in nomes_espiados}

    def espiao(nome):
        def chamada(*a, **k):
            registro.append((nome, j.updatesEnabled()))
            return reais[nome](*a, **k)
        return chamada

    for nome in nomes_espiados:
        setattr(j, nome, espiao(nome))
    for sentido, acao in (("expansão", entrar), ("encolhimento", sair)):
        registro.clear()
        acao(j)
        if acao is sair:
            esperar(A.ATRASO_ENCOLHER_MS + 40)
            j._encolher_se_puder()
        esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
        nomes = [n for n, _ in registro]
        r.conferir(
            nomes.count("setGeometry") == 0 and nomes.count("resize") == 0
            and nomes.count("move") == 0,
            f"{sentido}: 0 redimensionamento e 0 movimento nativos (veio {nomes})",
        )
        r.conferir(nomes.count("setMask") == 1, f"{sentido}: exatamente 1 setMask (veio {nomes})")
        r.conferir(nomes.count("clearMask") == 1,
                   f"{sentido}: e 1 clearMask, no começo (veio {nomes})")
        r.conferir(
            "clearMask" in nomes and "setMask" in nomes
            and nomes.index("clearMask") < nomes.index("setMask"),
            f"{sentido}: a máscara sai no começo e volta no assentamento (veio {nomes})",
        )
        r.conferir(
            all(not ligado for n, ligado in registro if n in ("setMask", "clearMask")),
            f"{sentido}: as duas trocas de máscara rodam com updatesEnabled=False (veio {registro})",
        )
        r.conferir(
            "repaint" in nomes
            and all(ligado for n, ligado in registro if n == "repaint")
            and nomes.index("repaint") > nomes.index("clearMask"),
            f"{sentido}: repaint() síncrono já com as atualizações religadas (veio {registro})",
        )
        r.conferir(j.updatesEnabled(),
                   f"{sentido}: a janela não fica com as atualizações desligadas no fim")
    for nome, real in reais.items():
        setattr(j, nome, real)
    lado = j.botao_gravar.height() + 2 * A.MARGEM_JANELA_COMPACTA
    r.conferir(
        tam_visivel(j) == A.QSize(lado, lado)
        and j.size() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        f"e assentou no compacto de {lado}x{lado} dentro da janela única "
        f"(veio {tam_visivel(j)} em {j.size()})",
    )
    j.close()


def testar_mascara_hover_e_sobrepostos(r):
    """9ª volta (D-32) — o jeito mais provável de a mudança quebrar o app.

    A janela ocupa 448x366 de área quase toda invisível no modo compacto. Se o hover continuasse
    perguntando a `self.geometry()`, o cursor a 200px do botão expandiria a janela sozinho — o
    usuário veria a janela abrir sem nada por perto. E se a máscara recortasse só o cartão, o
    painel de Configurações (que ocupa a janela inteira, ver `resizeEvent`) sairia cortado."""
    print("[18] hover pelo cartão visível, clique-através e sobrepostos dentro da máscara")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()
    centro = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
    longe = QPoint(centro.x() + 200, centro.y())
    r.conferir(
        j.geometry().contains(longe),
        f"o ponto a 200px do botão está DENTRO da janela nativa ({j.geometry()}) — é esta a "
        f"armadilha da arquitetura nova",
    )
    r.conferir(
        not j._geometria_visivel().contains(longe),
        f"mas fora do cartão visível ({j._geometria_visivel()})",
    )
    j._timer_vigia_ponteiro.start(A.INTERVALO_VIGIA_PONTEIRO_MS)
    QCursor.setPos(longe)
    esperar(A.INTERVALO_VIGIA_PONTEIRO_MS * 4)
    r.conferir(not j._expandido, "com o cursor a 200px do botão a janela NÃO expande")
    mouse_no_botao(j)
    esperar(A.INTERVALO_VIGIA_PONTEIRO_MS * 3 + A.DURACAO_ANIMACAO_MODO_MS + 200)
    r.conferir(j._expandido, "e com o cursor em cima do botão ela expande, como sempre")
    j._timer_vigia_ponteiro.stop()

    # --- o que a máscara recorta, no expandido assentado --------------------------------
    mascara = lado_mascara(j)
    cartao = A.QRect(j.cartao.geometry())
    folga = A.FOLGA_MASCARA_PX
    r.conferir(
        mascara is not None and mascara == cartao.adjusted(-folga, -folga, folga, folga),
        f"no expandido a máscara é o cartão + {folga}px de folga (máscara {mascara}, cartão {cartao})",
    )
    r.conferir(
        not mascara.contains(A.QPoint(0, 0)) and not mascara.contains(
            A.QPoint(j.width() - 1, j.height() - 1)),
        "os cantos da janela (área 100% transparente) ficam FORA da máscara — clique passa para a "
        "janela de baixo",
    )
    # A prova acima é sobre o retângulo que este código calcula. A de baixo é sobre o estado do
    # próprio QWidget — a região que o Qt leva ao sistema de janelas. É o máximo que headless
    # entrega: o plugin offscreen NÃO aplica máscara nenhuma na tela ("This plugin does not
    # support setting window masks"), então nada aqui prova que o clique atravessa no Windows.
    regiao = j.mask()
    r.conferir(
        not regiao.isEmpty() and regiao.boundingRect() == mascara,
        f"o QWidget guarda a mesma região ({regiao.boundingRect()}), que é o que o Qt leva ao "
        f"sistema de janelas",
    )
    dentro = j.botao_gravar.mapTo(j, j.botao_gravar.rect().center())
    r.conferir(
        regiao.contains(dentro) and not regiao.contains(dentro + A.QPoint(0, -300))
        and not regiao.contains(A.QPoint(0, 0)),
        "a região aceita o centro do botão e recusa o que está fora do cartão",
    )
    # o anel da CamadaPulso não entra na máscara (110x110 inflaria o compacto de 84 para 96); o
    # que ele DESENHA (raio ~46px em volta do botão) precisa caber no cartão mesmo assim.
    centro_botao = j.botao_gravar.mapTo(j, j.botao_gravar.rect().center())
    raio = int(34 * 1.35) + 2
    anel = A.QRect(centro_botao.x() - raio, centro_botao.y() - raio, 2 * raio, 2 * raio)
    r.conferir(
        mascara.contains(anel),
        f"e o anel de pulso que a CamadaPulso desenha cabe dentro da máscara ({anel} em {mascara})",
    )

    # --- painel sobreposto: a máscara tem de crescer junto -------------------------------
    j.painel_configuracoes.mostrar()
    esperar(60)
    j._aplicar_mascara()
    mascara_painel = lado_mascara(j)
    painel = A.QRect(j.painel_configuracoes.geometry())
    r.conferir(
        mascara_painel.contains(painel),
        f"com Configurações aberto a máscara cobre o painel inteiro "
        f"(painel {painel}, máscara {mascara_painel})",
    )
    j.painel_configuracoes.esconder()
    esperar(60)
    j._aplicar_mascara()
    r.conferir(
        lado_mascara(j) == mascara,
        f"e volta ao cartão quando o painel fecha (veio {lado_mascara(j)})",
    )
    sair(j)
    j.close()


def testar_encaixe_nas_bordas(r):
    """10ª volta (D-32): a janela volta a caber na tela ao expandir, ao preço de UM move nativo.

    A 9ª volta tirou o encaixe na tela junto com o resize nativo, e isso trocou um problema por
    outro: com a janela fixa em 448x366 e o cartão compacto morando a 184px das laterais e 21px do
    topo dela, um botão arrastado para um canto — que é onde um botão flutuante de ditado mora —
    deixava o cartão expandido cortado pela borda. O PM revogou o "0 movimento nativo" com essa
    medição: quem causa flicker numa janela layered é o RE-DIMENSIONAMENTO, que realoca a
    superfície, não o deslocamento. Então: 0 resize continua absoluto, 1 move por transição é
    permitido e só quando necessário.

    Este teste tranca as duas metades: perto de cada uma das quatro bordas, exatamente 1 move e o
    retângulo visível inteiro dentro da área útil; longe das bordas, 0 move — o caso comum não
    regride. E o botão desliza, em vez de saltar: sem o quadro zero recolocando o cartão logo
    depois do move, ele pularia a distância inteira do deslocamento num quadro só."""
    print("[20] perto da borda a janela se move uma vez; longe dela, nenhuma (10ª volta)")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()
    area = A.QGuiApplication.primaryScreen().availableGeometry()
    registro = []
    reais = {nome: getattr(j, nome) for nome in ("move", "resize", "setGeometry")}

    def espiao(nome):
        def chamada(*a, **k):
            registro.append(nome)
            return reais[nome](*a, **k)
        return chamada

    for nome in reais:
        setattr(j, nome, espiao(nome))

    def por_o_botao_em(ponto):
        # reposiciona sem passar pelo espião: quem está sendo contado é a transição, não o setup
        centro = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
        reais["move"](j.pos() + (ponto - centro))
        esperar(30)

    casos = (
        ("esquerda", A.QPoint(area.left() + 10, area.center().y()), 1),
        ("direita", A.QPoint(area.right() - 10, area.center().y()), 1),
        ("topo", A.QPoint(area.center().x(), area.top() + 10), 1),
        ("base", A.QPoint(area.center().x(), area.bottom() - 10), 1),
        ("longe das bordas", A.QPoint(area.center().x(), area.center().y()), 0),
    )
    for nome, ponto, moves_esperados in casos:
        j._aplicar_modo(False, animar=False)
        esperar(60)
        por_o_botao_em(ponto)
        registro.clear()
        centros = []
        relogio = QTimer()
        relogio.timeout.connect(
            lambda: centros.append(j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()))
        )
        relogio.start(4)
        j._atualizar_ponteiro(True)
        esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
        relogio.stop()
        r.conferir(
            registro.count("move") == moves_esperados,
            f"{nome}: {moves_esperados} move(s) nativo(s) na expansão (veio {registro.count('move')})",
        )
        r.conferir(
            registro.count("resize") == 0 and registro.count("setGeometry") == 0,
            f"{nome}: e nenhum redimensionamento nativo (veio {registro})",
        )
        r.conferir(
            area.contains(j._geometria_visivel()),
            f"{nome}: o cartão expandido fica inteiro dentro da área útil "
            f"({j._geometria_visivel()} em {area})",
        )
        # deslizar, não saltar: monótono nos dois eixos, e o primeiro quadro não pode carregar o
        # deslocamento inteiro (era assim que o move apareceria como pulo).
        xs = [c.x() for c in centros]
        ys = [c.y() for c in centros]
        monotono = (
            (all(a <= b for a, b in zip(xs, xs[1:])) or all(a >= b for a, b in zip(xs, xs[1:])))
            and (all(a <= b for a, b in zip(ys, ys[1:])) or all(a >= b for a, b in zip(ys, ys[1:])))
        )
        total = abs(xs[-1] - xs[0]) + abs(ys[-1] - ys[0])
        passos = [abs(xs[i + 1] - xs[i]) + abs(ys[i + 1] - ys[i]) for i in range(len(xs) - 1)]
        maior = max(passos) if passos else 0
        r.conferir(monotono, f"{nome}: o centro do botão desliza em um sentido só (sem vaivém)")
        if moves_esperados == 0:
            r.conferir(total == 0 and maior == 0,
                       f"{nome}: e não sai do lugar — desvio {total}px (alvo: 0)")
        else:
            r.conferir(
                maior * 3 < total,
                f"{nome}: nenhum quadro carrega o deslocamento inteiro "
                f"(maior passo {maior}px de {total}px no total)",
            )
        # e o caminho de volta nunca precisa de move: a janela já está encaixada
        registro.clear()
        sair(j)
        esperar(A.ATRASO_ENCOLHER_MS + 40)
        j._encolher_se_puder()
        esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
        r.conferir(
            registro.count("move") == 0 and registro.count("resize") == 0,
            f"{nome}: o encolhimento não move nem redimensiona nada (veio {registro})",
        )
    for nome, real in reais.items():
        setattr(j, nome, real)
    j.close()


def testar_arrastar_ate_a_borda(r):
    """10ª volta (D-32): o gesto que motivou a rodada, ponta a ponta. O usuário arrasta o botão até
    encostar num canto (é o uso normal de um botão flutuante), solta, e passa o mouse por cima."""
    print("[21] arrastar até o canto, soltar e expandir: sem corte e sem pulo ao soltar")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()
    area = A.QGuiApplication.primaryScreen().availableGeometry()
    alvo = A.QPoint(area.left() + 12, area.bottom() - 12)
    centro = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
    agarrar = A.QPoint(j._geometria_visivel().center())
    j.arraste_iniciar(agarrar)
    j.arraste_mover(agarrar + (alvo - centro))
    j.arraste_fim()
    esperar(60)
    depois_de_soltar = A.QRect(j._geometria_visivel())
    centro_solto = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
    r.conferir(
        abs(centro_solto.x() - alvo.x()) <= 1 and abs(centro_solto.y() - alvo.y()) <= 1,
        f"o botão parou onde o gesto o deixou, no canto (veio {centro_solto}, pedido {alvo})",
    )
    esperar(A.INTERVALO_VIGIA_PONTEIRO_MS * 3)
    r.conferir(
        j._geometria_visivel() == depois_de_soltar,
        f"e não pula de volta depois de soltar o mouse (veio {j._geometria_visivel()})",
    )
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
    visivel = j._geometria_visivel()
    r.conferir(
        area.contains(visivel),
        f"ao expandir, o cartão inteiro cabe na área útil ({visivel} em {area})",
    )
    cartao = j.cartao.mapTo(j, A.QPoint(0, 0))
    r.conferir(
        j._expandido and j.size() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        f"a janela continua no tamanho único (veio {j.size()})",
    )
    r.conferir(
        area.contains(A.QRect(j.mapToGlobal(cartao), j.cartao.size())),
        "e o cartão branco não fica cortado por nenhuma borda",
    )
    sair(j)
    j.close()


def testar_arrasto_nos_dois_modos(r):
    """9ª volta (D-32): a janela só se move quando o usuário arrasta (ou na abertura). Como o
    cartão compacto mora num offset fixo dentro da janela, arrastar tem de mover os dois juntos —
    nos dois modos e no meio de uma transição, onde o arrasto ainda translada os retângulos
    guardados da animação."""
    print("[19] arrastar continua funcionando nos dois modos e no meio da transição")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()
    for modo, expandido in (("compacto", False), ("expandido", True)):
        if expandido:
            j._aplicar_modo(True, animar=False)
            esperar(60)
        pos_janela = A.QPoint(j.pos())
        visivel_antes = A.QRect(j._geometria_visivel())
        centro_antes = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
        agarrar = A.QPoint(visivel_antes.center())
        j.arraste_iniciar(agarrar)
        j.arraste_mover(agarrar + A.QPoint(60, 40))
        j.arraste_fim()
        esperar(40)
        centro_depois = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
        r.conferir(
            j.pos() == pos_janela + A.QPoint(60, 40),
            f"{modo}: a janela nativa acompanhou o gesto (veio {j.pos()})",
        )
        r.conferir(
            j._geometria_visivel() == visivel_antes.translated(60, 40),
            f"{modo}: e o cartão visível foi junto (veio {j._geometria_visivel()})",
        )
        r.conferir(
            centro_depois == centro_antes + A.QPoint(60, 40),
            f"{modo}: o botão andou exatamente o que o gesto pediu (veio {centro_depois})",
        )
    # e no meio de uma transição
    j._aplicar_modo(False)
    esperar(A.DURACAO_ANIMACAO_MODO_MS // 3)
    r.conferir(j._geo_transicao is not None, "o arrasto abaixo acontece no meio de uma transição")
    pos_meio = A.QPoint(j.pos())
    agarrar = A.QPoint(j._geometria_visivel().center())
    j.arraste_iniciar(agarrar)
    j.arraste_mover(agarrar + A.QPoint(-30, 25))
    j.arraste_fim()
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 250)
    r.conferir(
        j.pos() == pos_meio + A.QPoint(-30, 25),
        f"arrastar no meio da transição move a janela (veio {j.pos()}, era {pos_meio})",
    )
    lado = j._lado_compacto()
    r.conferir(
        tam_visivel(j) == A.QSize(lado, lado)
        and j.geometry().contains(j._geometria_visivel()),
        f"e o assentamento não devolve a janela para o lugar de antes "
        f"(visível {j._geometria_visivel()} dentro de {j.geometry()})",
    )
    j.close()


def testar_compacto_independe_do_expandido(r):
    """A 6ª volta mudou a altura do expandido; o compacto (confirmado certo por print real do
    usuário) não pode ter mudado nada. Aqui a prova é direta: mexer em _tamanho_expandido não pode
    alterar o tamanho compacto, que é medido contra o BotaoGravar."""
    print("[14] a nova altura do expandido não toca no compacto (6ª volta)")
    j = nova_janela()
    esperado = j.botao_gravar.height() + 2 * A.MARGEM_JANELA_COMPACTA
    r.conferir(tam_visivel(j) == A.QSize(esperado, esperado),
               f"nasce compacto em {esperado}x{esperado}")
    r.conferir(
        j._tamanho_do_modo(False) == A.QSize(esperado, esperado),
        "o tamanho do modo compacto é o botão + margem",
    )
    guardado = A.QSize(j._tamanho_expandido)
    for altura in (480, 700, 200):
        j._tamanho_expandido = A.QSize(guardado.width(), altura)
        r.conferir(
            j._lado_compacto() == esperado and j._tamanho_do_modo(False) == A.QSize(esperado, esperado),
            f"com _tamanho_expandido de altura {altura} o compacto continua {esperado}x{esperado}",
        )
    j._tamanho_expandido = guardado

    # e um ciclo real de expandir/encolher devolve exatamente o mesmo compacto
    j._timer_vigia_ponteiro.stop()
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 150)
    sair(j)
    j._aplicar_modo(expandido=False)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 250)
    r.conferir(
        tam_visivel(j) == A.QSize(esperado, esperado),
        f"depois de expandir e encolher volta a {esperado}x{esperado} (veio {tam_visivel(j)})",
    )
    j.close()


def testar_pulso_espera_a_transicao(r):
    """D-32, 7ª volta (2026-09-05): dois sistemas de animação com relógios próprios não podem
    disputar a mesma região da tela. Quando a gravação começa a partir do modo compacto,
    `_definir_estado_botao` trocava o estado do botão — o que ligava na hora o temporizador de 30ms
    do anel de pulso da CamadaPulso — e só então chamava `_aplicar_modo(True)`, a transição de
    240ms. Os dois passavam a repintar a mesma área desde o primeiro instante (a camada fica atrás
    do botão e é reposicionada a cada quadro). É a hipótese de causa do "botão vermelho tentando
    desaparecer" relatado no Windows real desde a 4ª volta.

    O que este teste prova: a cor/ícone continuam mudando na hora, mas o temporizador de pulso só
    fica ATIVO depois que a transição assenta — em nenhum dos quadros intermediários."""
    print("[15] o pulso do gravando espera a transição de modo assentar (7ª volta)")
    j = nova_janela()
    j._timer_vigia_ponteiro.stop()  # senão o vigia expande/encolhe por conta do cursor
    camada = j.camada_pulso
    r.conferir(not j._expandido, "a janela nasce compacta")
    r.conferir(not camada._timer_pulso.isActive(), "parada, não há pulso rodando")
    r.conferir(
        camada._timer_pulso.isActive() is False and not j.esta_em_transicao_de_modo(),
        "e não há transição de modo em andamento",
    )

    # (a) gravação iniciada a partir do compacto: expande E pulsa — o conflito da hipótese
    j._definir_estado_botao("gravando")
    r.conferir(j.botao_gravar._estado == "gravando", "a cor/ícone do botão mudam na hora")
    r.conferir(camada._estado == "gravando", "a camada de pulso também já está em gravando")
    r.conferir(j.esta_em_transicao_de_modo(), "a transição compacto->expandido começou")
    r.conferir(
        not camada._timer_pulso.isActive(),
        "e o temporizador de pulso NÃO começou junto com ela",
    )
    r.conferir(camada._pulso_adiado, "o pulso ficou pendente, não perdido")

    amostras = []
    for _ in range(10):
        esperar(max(1, A.DURACAO_ANIMACAO_MODO_MS // 10))
        if j.esta_em_transicao_de_modo():
            amostras.append(camada._timer_pulso.isActive())
    r.conferir(
        len(amostras) >= 3,
        f"a transição durou o bastante para ser amostrada ({len(amostras)} quadros)",
    )
    r.conferir(
        not any(amostras),
        f"em nenhum quadro da transição o pulso estava rodando (amostras: {amostras})",
    )

    esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
    r.conferir(not j.esta_em_transicao_de_modo(), "a transição terminou")
    r.conferir(j._expandido and j.size() == j._tamanho_expandido, "e a janela assentou expandida")
    r.conferir(
        camada._timer_pulso.isActive(),
        "só então o pulso começou (o anel do gravando não some, só chega depois)",
    )
    r.conferir(
        camada._timer_pulso.interval() == A.INTERVALO_PULSO_MS,
        f"com o intervalo de sempre ({A.INTERVALO_PULSO_MS}ms, veio "
        f"{camada._timer_pulso.interval()})",
    )
    r.conferir(not camada._pulso_adiado, "e a pendência foi consumida")

    # (b) sem transição nenhuma (a janela já está expandida), nada é adiado
    j._definir_estado_botao("parado")
    esperar(30)
    r.conferir(not camada._timer_pulso.isActive(), "parou de gravar: o pulso para na hora")
    j._aplicar_modo(True, animar=False)
    j._definir_estado_botao("gravando")
    r.conferir(
        camada._timer_pulso.isActive() and not camada._pulso_adiado,
        "já expandida e sem transição, o pulso começa na hora (nada é adiado à toa)",
    )

    # (c) parar de gravar no MEIO da transição não deixa pulso pendente para depois
    j._definir_estado_botao("parado")
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 300)
    j._aplicar_modo(False, animar=False)
    j._definir_estado_botao("gravando")
    r.conferir(camada._pulso_adiado, "de novo compacto: o pulso voltou a ficar pendente")
    j._definir_estado_botao("parado")
    r.conferir(
        not camada._pulso_adiado and not camada._timer_pulso.isActive(),
        "parar no meio da transição cancela a pendência",
    )
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
    r.conferir(
        not camada._timer_pulso.isActive(),
        "e o fim da transição não ressuscita um pulso de uma gravação que já acabou",
    )
    j.close()


def testar_posicao_inicial(r):
    """A janela nasce dentro de um monitor de verdade (correção de 2026-09-05, entre a 1ª e a 2ª
    volta: no desktop de três monitores do usuário ela nascia num vão sem tela nenhuma). Aqui só dá
    para conferir a regra — a tela deste ambiente é uma só e virtual."""
    print("[8] posição inicial dentro da tela (correção anterior, não pode ter se perdido)")
    j = nova_janela()
    area = A.QGuiApplication.primaryScreen().availableGeometry()
    r.conferir(area.contains(j.frameGeometry()), f"a janela nasce dentro da área visível ({j.frameGeometry()})")
    r.conferir(
        j.pos() == QPoint(area.x() + 40, area.y() + 40),
        f"nasce no canto declarado em _montar_ui, +40/+40 (veio {j.pos()})",
    )
    j.close()


def circulo_desenhado(janela):
    """Onde o círculo roxo do BotaoGravar aparece DE VERDADE nos pixels da janela.

    Medir `mapToGlobal(centro)` não basta: a coordenada continua certa mesmo quando o botão está
    fora do recorte da janela (ou do cartão) e não é desenhado — que era exatamente o defeito
    relatado pelo usuário na 2ª volta ("o botão muda de tamanho/pula durante a animação")."""
    roxo = QColor(A.PALETA["roxo"]).rgb() & 0xFFFFFF
    img = janela.grab().toImage()
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    for y in range(0, img.height(), 2):
        for x in range(0, img.width(), 2):
            if (img.pixel(x, y) & 0xFFFFFF) == roxo:
                x0 = min(x0, x)
                x1 = max(x1, x)
                y0 = min(y0, y)
                y1 = max(y1, y)
    if x1 < 0:
        return (0, 0)
    return (x1 - x0 + 1, y1 - y0 + 1)


def testar_botao_em_pixels(r):
    print("[9] o botão como ele aparece na tela, quadro a quadro (3ª volta)")
    j = nova_janela()
    inteiro = None
    for longe_da_borda in (QPoint(400, 300),):
        centrar(j, longe_da_borda)
    ancora = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
    inteiro = circulo_desenhado(j)
    r.conferir(inteiro[0] >= 60 and inteiro[1] >= 60, f"no repouso o círculo aparece inteiro {inteiro}")

    for sentido, alvo in (("expansão", True), ("encolhimento", False)):
        amostras = []

        def amostrar():
            amostras.append(
                (j._geometria_visivel().width(),
                 j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()),
                 circulo_desenhado(j))
            )

        relogio = QTimer()
        relogio.timeout.connect(amostrar)
        relogio.start(8)
        if alvo:
            entrar(j)
        else:
            sair(j)
        esperar(A.ATRASO_ENCOLHER_MS * (0 if alvo else 1) + A.DURACAO_ANIMACAO_MODO_MS + 200)
        relogio.stop()
        intermediarias = [
            a for a in amostras if j._lado_compacto() < a[0] < j._tamanho_expandido.width()
        ]
        r.conferir(len(intermediarias) >= 2, f"a {sentido} passou por quadros intermediários")
        menor = min(a[2] for a in amostras)
        r.conferir(
            menor[0] >= inteiro[0] - 1 and menor[1] >= inteiro[1] - 1,
            f"na {sentido} o círculo nunca aparece cortado (menor visto: {menor}, inteiro: {inteiro})",
        )
        desvio = max(abs(c.x() - ancora.x()) + abs(c.y() - ancora.y()) for _, c, _ in amostras)
        r.conferir(desvio == 0, f"na {sentido} o centro do botão não sai do pixel (desvio {desvio}px)")

    # no canto da tela a âncora não cabe: o botão precisa andar, mas continua inteiro em todos os
    # quadros — o recorte era metade do defeito relatado
    j._aplicar_modo(False, animar=False)
    j.move(40, 40)
    esperar(120)
    amostras = []
    relogio = QTimer()
    relogio.timeout.connect(lambda: amostras.append(circulo_desenhado(j)))
    relogio.start(8)
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 200)
    relogio.stop()
    menor = min(amostras)
    r.conferir(
        menor[0] >= inteiro[0] - 1 and menor[1] >= inteiro[1] - 1,
        f"no canto da tela o círculo também nunca aparece cortado (menor visto: {menor})",
    )
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 200)
    j.close()


def testar_janela_nativa_parada(r):
    """4ª volta (D-32): a hipótese de causa do tremor relatado no Windows é o redimensionamento
    NATIVO repetido de uma janela translúcida/layered (~10 por transição, um por quadro). O
    headless não reproduz o tremor (não há compositor), mas reproduz a causa: dá para contar
    quantas vezes `frameGeometry()` muda. O alvo é no máximo 2 — o retângulo-união no começo e o
    tamanho final no fim."""
    print("[11] a janela nativa não é redimensionada quadro a quadro (4ª volta)")
    j = nova_janela()
    centrar(j, QPoint(400, 300))
    ancora = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())

    for sentido, alvo in (("expansão", True), ("encolhimento", False)):
        nativas = [A.QRect(j.frameGeometry())]
        visiveis = []
        centros = []

        def amostrar():
            atual = A.QRect(j.frameGeometry())
            if atual != nativas[-1]:
                nativas.append(atual)
            visiveis.append(j._geometria_visivel().width())
            centros.append(j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()))

        relogio = QTimer()
        relogio.timeout.connect(amostrar)
        relogio.start(4)
        if alvo:
            entrar(j)
        else:
            sair(j)
        esperar((0 if alvo else A.ATRASO_ENCOLHER_MS) + A.DURACAO_ANIMACAO_MODO_MS + 250)
        relogio.stop()
        trocas = len(nativas) - 1
        r.conferir(
            trocas <= 2,
            f"na {sentido} a janela nativa mudou de geometria {trocas}x (alvo: no máximo 2)",
        )
        print(f"    {sentido}: {trocas} troca(s) de frameGeometry(), "
              f"{len(visiveis)} amostras do retângulo visível")
        # e a janela nativa nunca fica menor que o retângulo visível: é ela que recorta o cartão
        uniao = nativas[0].united(nativas[-1])
        r.conferir(
            all(n.width() >= 1 and uniao.contains(n) or n == uniao for n in nativas),
            f"na {sentido} os tamanhos nativos ficam dentro da união ({[n.size() for n in nativas]})",
        )
        # o cartão realmente passou por tamanhos intermediários (a animação não virou um pulo)
        meio = [w for w in visiveis if j._lado_compacto() < w < j._tamanho_expandido.width()]
        r.conferir(len(meio) >= 2, f"na {sentido} o cartão passou por tamanhos intermediários")
        desvio = max(abs(c.x() - ancora.x()) + abs(c.y() - ancora.y()) for c in centros)
        r.conferir(desvio == 0, f"na {sentido} o botão continua com desvio {desvio}px (alvo: 0)")

    r.conferir(not j._expandido and tam_visivel(j).width() == j._lado_compacto(),
               f"terminou compacto de verdade (veio {tam_visivel(j)})")
    r.conferir(j._geo_transicao is None and j._geo_visivel is None,
               "fora da transição os retângulos auxiliares voltam a ser None")
    # 9ª volta: fora da transição o retângulo visível é o cartão do modo DENTRO da janela fixa —
    # não a janela, que continua 448x366 com o compacto de 80x80 em cima do botão.
    r.conferir(j._geometria_visivel() != j.geometry() and j.geometry().contains(j._geometria_visivel()),
               f"e _geometria_visivel() é o cartão dentro da janela "
               f"({j._geometria_visivel()} dentro de {j.geometry()})")
    j.close()


def testar_conteudo_escondido_na_transicao(r):
    """5ª volta (D-32): o usuário relatou que o botão some por um instante exatamente quando a
    transição COMEÇA (o mouse entra) ou quando ela começa no sentido inverso (o mouse sai) — não
    no meio, que a 3ª e a 4ª volta já mediram em 0px de desvio. A suspeita é a ORDEM dentro de
    `_aplicar_modo`: até a 4ª volta, `_configurar_layout_do_modo` (margens, mola e folha de estilo
    do cartão) e um `setVisible(expandido)` sobre o conteúdo só-expandido rodavam com os dois
    layouts ainda **habilitados** e a janela nativa ainda no tamanho do modo antigo — na expansão,
    isso mostrava caixa de texto, ⋮, copiar e lixeira dentro da janela de 88px, disputando espaço
    com o botão, para escondê-los de novo duas linhas depois.

    Este teste prende as três garantias da ordem nova (e o preço de errar cada uma):
    1. nenhum widget só-expandido fica visível em nenhum quadro da transição, nos dois sentidos;
    2. `_configurar_layout_do_modo` só é chamado com os DOIS layouts já desabilitados;
    3. a medição do centro do botão continua certa mesmo com o conteúdo escondido — sem o escopo
       de visibilidade dentro de `_centro_local_do_botao`, o layout expandido devolve o botão
       centrado na vertical (y=239 em vez de y=76): 163px de erro, que vira um pulo do botão no
       assentamento. É o que aconteceria ao simplesmente apagar o `setVisible(expandido)` antigo.
    """
    print("[12] conteúdo só-expandido nunca aparece durante a transição (5ª volta)")
    j = nova_janela()
    centrar(j, QPoint(400, 300))
    ancora = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())

    chamadas_layout = []
    original = j._configurar_layout_do_modo

    def espiao(expandido):
        chamadas_layout.append(
            (expandido, j._layout_externo.isEnabled(), j._layout_cartao.isEnabled())
        )
        return original(expandido)

    j._configurar_layout_do_modo = espiao

    for sentido, alvo in (("expansão", True), ("encolhimento", False)):
        vistos = set()
        centros = []
        quadros = []
        nativas = [A.QRect(j.frameGeometry())]

        def amostrar():
            atual = A.QRect(j.frameGeometry())
            if atual != nativas[-1]:
                nativas.append(atual)
            centros.append(j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()))
            if j._geo_transicao is None:  # fora da transição a visibilidade é a do modo assentado
                return
            quadros.append(j._progresso_modo)
            for i, w in enumerate(j._widgets_so_expandido):
                if w.isVisible():
                    vistos.add(f"{i}:{type(w).__name__}")

        relogio = QTimer()
        relogio.timeout.connect(amostrar)
        relogio.start(4)
        if alvo:
            entrar(j)
        else:
            sair(j)
        esperar((0 if alvo else A.ATRASO_ENCOLHER_MS) + A.DURACAO_ANIMACAO_MODO_MS + 250)
        relogio.stop()

        r.conferir(len(quadros) >= 5,
                   f"na {sentido} a transição foi amostrada ({len(quadros)} quadros dentro dela)")
        r.conferir(not vistos,
                   f"na {sentido} apareceu conteúdo só-expandido durante a transição: {sorted(vistos)}")
        desvio = max(abs(c.x() - ancora.x()) + abs(c.y() - ancora.y()) for c in centros)
        r.conferir(desvio == 0,
                   f"na {sentido} o botão desviou {desvio}px do ponto de partida (alvo: 0)")
        r.conferir(len(nativas) - 1 <= 2,
                   f"na {sentido} a janela nativa mudou {len(nativas) - 1}x de geometria (alvo: <=2)")
        print(f"    {sentido}: {len(quadros)} quadros dentro da transição, "
              f"{len(vistos)} widget(s) visível(is) indevidamente, desvio {desvio}px, "
              f"{len(nativas) - 1} redimensionamento(s) nativo(s)")
        esperados = alvo
        r.conferir(
            all(w.isVisible() == esperados for w in j._widgets_so_expandido),
            f"depois de assentar a {sentido} a visibilidade do conteúdo é {esperados}",
        )

    r.conferir(bool(chamadas_layout), "_configurar_layout_do_modo foi mesmo chamado")
    fora_de_ordem = [c for c in chamadas_layout if c[1] or c[2]]
    r.conferir(
        not fora_de_ordem,
        f"_configurar_layout_do_modo rodou com layout ainda habilitado: {fora_de_ordem}",
    )
    print(f"    {len(chamadas_layout)} chamada(s) de _configurar_layout_do_modo, "
          f"todas com os dois layouts congelados")
    j._configurar_layout_do_modo = original

    # (3) a medição do centro não pode depender de o conteúdo estar visível na hora
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 150)
    r.conferir(j._expandido, "voltou para o expandido para medir o centro")
    com_conteudo = j._centro_local_do_botao(j._tamanho_expandido)
    for w in j._widgets_so_expandido:
        w.setVisible(False)
    sem_conteudo = j._centro_local_do_botao(j._tamanho_expandido)
    r.conferir(
        sem_conteudo == com_conteudo,
        f"centro do botão medido sem o conteúdo na tela: {sem_conteudo} != {com_conteudo}",
    )
    r.conferir(
        all(w.isHidden() for w in j._widgets_so_expandido),
        "a medição devolve a visibilidade de antes (não deixa nada ligado)",
    )
    print(f"    centro local do botão no expandido: {com_conteudo} com conteúdo visível, "
          f"{sem_conteudo} com ele escondido")
    for w in j._widgets_so_expandido:
        w.setVisible(True)
    j._reassentar_layout()
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 200)
    j.close()


def testar_sair(r):
    """Vai por último: encerra o laço de eventos da aplicação de verdade."""
    print("[10] Sair no menu ⋮ (3ª volta)")
    j = nova_janela()
    itens = [acao.defaultWidget() for acao in j.menu_avancado.actions()]
    rotulos = [item.findChildren(QLabel)[-1].text() for item in itens]
    r.conferir(
        rotulos == [
            "Abrir planejamento", "Configurações", "Consumo", "Enviar arquivo", "Gerar imagem",
            "Sair da conta", "Sair",
        ],
        f"o menu tem os sete itens na ordem certa — 'Sair da conta' entrou na Etapa 5 (veio {rotulos})",
    )
    # "Abrir planejamento" (pedido direto, 2026-09-25): abre o link da página, sem abrir navegador aqui.
    abertas = []
    original_servicos = A.QDesktopServices

    class ServicosFalsos:
        @staticmethod
        def openUrl(url):
            abertas.append(url.toString())
            return True

    A.QDesktopServices = ServicosFalsos
    try:
        itens[0].clicado.emit()
    finally:
        A.QDesktopServices = original_servicos
    r.conferir(abertas == [A.URL_PLANEJAMENTO], f"Abrir planejamento abre o link da página (abriu {abertas})")
    soltas = []
    original = A.keyboard.remove_hotkey

    def espiao(*args, **kwargs):
        soltas.append(1)
        try:
            return original(*args, **kwargs)
        except Exception:
            return None

    A.keyboard.remove_hotkey = espiao
    app = QApplication.instance()
    estado = {"saiu": False, "guarda": False}
    app.aboutToQuit.connect(lambda: estado.__setitem__("saiu", True))
    guarda = QTimer()
    guarda.setSingleShot(True)

    def estourou():
        estado["guarda"] = True
        app.quit()

    guarda.timeout.connect(estourou)
    guarda.start(3000)
    QTimer.singleShot(50, itens[-1].clicado.emit)
    app.exec()
    guarda.stop()
    A.keyboard.remove_hotkey = original
    r.conferir(not estado["guarda"], "Sair encerrou o laço de eventos (não estourou a guarda de 3s)")
    r.conferir(estado["saiu"], "a aplicação emitiu aboutToQuit")
    r.conferir(not j.isVisible(), "a janela principal foi fechada")
    r.conferir(bool(soltas), "o atalho global foi solto no caminho (closeEvent)")


def testar_ancora_e_animacao(r):
    print("[4] âncora e animação nos dois sentidos")
    j = nova_janela()
    centrar(j, QPoint(400, 200))
    ancora = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())

    amostras = []

    def amostrar():
        # 4ª volta: quem cresce/encolhe na tela é o cartão (_geometria_visivel), não mais a
        # janela nativa — que fica parada no retângulo-união durante toda a transição.
        amostras.append(
            (j._geometria_visivel().width(), j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()))
        )

    relogio = QTimer()
    relogio.timeout.connect(amostrar)
    relogio.start(15)

    entrar(j)  # expande
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 120)
    relogio.stop()
    larguras = [w for w, _ in amostras]
    intermediarias = [w for w in larguras if j._lado_compacto() < w < j._tamanho_expandido.width()]
    r.conferir(len(intermediarias) >= 2, f"a expansão passa por tamanhos intermediários ({larguras})")
    desvio = max(abs(c.x() - ancora.x()) + abs(c.y() - ancora.y()) for _, c in amostras)
    r.conferir(desvio <= 1, f"o centro do botão não sai do lugar durante a expansão (desvio {desvio}px)")
    r.conferir(j.size() == j._tamanho_expandido, "terminou no tamanho expandido")
    r.conferir(
        j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()) == ancora,
        "âncora preservada no fim da expansão",
    )

    amostras.clear()
    relogio.start(15)
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 250)
    relogio.stop()
    larguras = [w for w, _ in amostras]
    intermediarias = [w for w in larguras if j._lado_compacto() < w < j._tamanho_expandido.width()]
    r.conferir(len(intermediarias) >= 2, f"o encolhimento passa por tamanhos intermediários ({larguras})")
    desvio = max(abs(c.x() - ancora.x()) + abs(c.y() - ancora.y()) for _, c in amostras)
    r.conferir(desvio <= 1, f"o centro do botão não sai do lugar ao encolher (desvio {desvio}px)")
    r.conferir(not j._expandido and tam_visivel(j).width() == j._lado_compacto(),
               "terminou compacto")
    r.conferir(
        j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()) == ancora,
        "âncora preservada no fim do encolhimento",
    )
    # 7ª volta: a faixa de 120-200ms da 2ª volta foi revogada por pedido direto do usuário
    # ("bota uma transição maior, ele não sumir") — a transição curta lia como sumiço, não
    # como movimento. O teto de 400ms é o que ainda não atrasa o clique seguinte.
    r.conferir(
        A.DURACAO_ANIMACAO_MODO_MS == 240,
        f"a transição de modo passou de 160 para 240ms (veio {A.DURACAO_ANIMACAO_MODO_MS})",
    )
    r.conferir(
        200 < A.DURACAO_ANIMACAO_MODO_MS <= 400,
        "mais longa que a faixa antiga de 120-200ms, e ainda curta o bastante para o clique",
    )
    j.close()


def testar_interrupcao(r):
    print("[5] mouse muda de lado no meio da animação")
    j = nova_janela()
    centrar(j, QPoint(400, 200))
    ancora = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())

    # expandindo → mouse sai no meio
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS // 2)
    r.conferir(j._animando_modo(), "a expansão ainda estava em curso quando o mouse saiu")
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 300)
    r.conferir(not j._expandido, "reverteu para compacto sem travar no meio")
    r.conferir(tam_visivel(j).width() == j._lado_compacto(),
               f"tamanho final compacto (veio {tam_visivel(j)})")

    # encolhendo → mouse volta no meio
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 150)
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS // 2)
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 300)
    r.conferir(j._expandido and j.size() == j._tamanho_expandido, "voltou ao expandido inteiro")
    r.conferir(
        j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center()) == ancora,
        "âncora sobreviveu às duas reversões",
    )
    j.close()


def testar_debounce_e_estado(r):
    print("[6] debounce de 250ms, gravando/processando e travas de painel")
    j = nova_janela()
    entrar(j)
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 80)
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS // 2)
    r.conferir(j._expandido, "não encolhe antes do debounce")
    entrar(j)
    esperar(A.ATRASO_ENCOLHER_MS + 120)
    r.conferir(j._expandido, "voltar antes do debounce cancela o encolhimento")

    # gravando expande sozinho com o mouse longe
    sair(j)
    esperar(A.ATRASO_ENCOLHER_MS + A.DURACAO_ANIMACAO_MODO_MS + 250)
    r.conferir(not j._expandido, "encolheu com o mouse fora")
    j.iniciar_gravacao()
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 120)
    r.conferir(j._expandido and j.size() == j._tamanho_expandido, "gravando expande sozinho")
    r.conferir(not j._pode_encolher(), "gravando não encolhe")
    j._callback_audio((np.random.rand(2000, 1).astype("float32") - 0.5) * 1.2, 2000, None, None)
    j.parar_e_enviar()
    esperar(ATRASO_TRABALHO_MS + 250)
    r.conferir(not j._pode_encolher(), "resultado na tela sem colocar não encolhe")
    j._clicar_copiar()
    esperar(60)
    r.conferir(j._pode_encolher(), "depois de colocado, pode encolher")

    j.painel_configuracoes.mostrar()
    esperar(40)
    r.conferir(not j._pode_encolher(), "Configurações aberto trava o encolhimento")
    j.painel_configuracoes.esconder()
    esperar(40)
    r.conferir(j._pode_encolher(), "fechar Configurações destrava")
    j.close()


def testar_arrastar_e_rede_de_seguranca(r):
    print("[7] arrastar no compacto e rede de segurança do vigia")
    j = nova_janela()
    esperar(150)
    pos_antes = j.pos()
    j.arraste_iniciar(j.pos() + QPoint(20, 20))
    j.arraste_mover(j.pos() + QPoint(60, 45))
    j.arraste_fim()
    esperar(30)
    r.conferir(j.pos() == pos_antes + QPoint(40, 25), f"arrastou o compacto (de {pos_antes} para {j.pos()})")

    # arrastar pelo próprio BotaoGravar, que no compacto é quase a janela inteira: acima do limiar
    # o gesto move a janela e engole o clique (não pode disparar a gravação)
    pos_antes = j.pos()
    inicio = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
    apertar(j.botao_gravar, inicio)
    mover(j.botao_gravar, inicio + QPoint(30, 18))
    soltar(j.botao_gravar, inicio + QPoint(30, 18))
    esperar(40)
    r.conferir(j.pos() != pos_antes, f"o gesto no botão arrastou a janela compacta (para {j.pos()})")
    r.conferir(not j.gravando, "o arrasto pelo botão não virou clique de gravar")
    # e um clique parado continua gravando
    parado = j.botao_gravar.mapToGlobal(j.botao_gravar.rect().center())
    apertar(j.botao_gravar, parado)
    soltar(j.botao_gravar, parado)
    esperar(60)
    r.conferir(j.gravando, "clique parado no botão ainda inicia a gravação")
    j.cancelar_gravacao()
    esperar(A.DURACAO_ANIMACAO_MODO_MS + 200)

    # simula uma máscara que "não pegou" (9ª volta: quem carrega o tamanho do modo é ela) e um
    # tamanho de janela que o sistema teria mexido — o vigia tem de consertar os dois sozinho.
    j.clearMask()
    j._mascara_atual = None
    esperar(A.INTERVALO_VIGIA_PONTEIRO_MS * 4)
    r.conferir(
        lado_mascara(j) is not None
        and lado_mascara(j).width() == j._lado_compacto() + 2 * A.FOLGA_MASCARA_PX,
        f"o vigia repôs a máscara do modo (veio {lado_mascara(j)})",
    )
    j.setMinimumSize(0, 0)
    j.setMaximumSize(A.TAMANHO_MAXIMO_QT, A.TAMANHO_MAXIMO_QT)
    j.resize(A.QSize(300, 300))
    esperar(A.INTERVALO_VIGIA_PONTEIRO_MS * 4)
    r.conferir(
        j.size() == A.QSize(A.LARGURA_EXPANDIDA, A.ALTURA_EXPANDIDA),
        f"e devolveu a janela ao tamanho único quando o sistema mexeu (veio {j.size()})",
    )
    r.conferir(
        tam_visivel(j).width() == j._lado_compacto(),
        f"sem tirar o modo compacto do lugar (veio {tam_visivel(j)})",
    )
    j.close()


def main():
    app = QApplication(sys.argv)
    A.TrabalhoTranscricao = TrabalhoFalso
    r = Resultado()
    # Filtro opcional por nome (`python testes_janela_compacta.py ancora nativa`): a suíte inteira
    # passou de 4 minutos e o shell desta sessão corta antes; rodar um teste de cada vez é o que
    # permite iterar. Sem argumento roda tudo, como sempre.
    filtros = [a for a in sys.argv[1:] if not a.startswith("-")]
    for teste in (
        testar_dois_ciclos,
        testar_caixa_mexida_por_fora,
        testar_tamanho_compacto,
        testar_ancora_e_animacao,
        testar_interrupcao,
        testar_debounce_e_estado,
        testar_arrastar_e_rede_de_seguranca,
        testar_posicao_inicial,
        testar_altura_expandida,
        testar_sem_sobreposicao_no_expandido,
        testar_transicao_sem_resize_nativo,
        testar_mascara_hover_e_sobrepostos,
        testar_arrasto_nos_dois_modos,
        testar_encaixe_nas_bordas,
        testar_arrastar_ate_a_borda,
        testar_compacto_independe_do_expandido,
        testar_pulso_espera_a_transicao,
        testar_botao_em_pixels,
        testar_janela_nativa_parada,
        testar_conteudo_escondido_na_transicao,
        testar_sair,  # por último: encerra o laço de eventos
    ):
        if filtros and not any(f in teste.__name__ for f in filtros):
            continue
        teste(r)
    print(f"\n{r.ok} verificações passaram, {len(r.falhas)} falharam")
    for f in r.falhas:
        print(" -", f)
    return 1 if r.falhas else 0


if __name__ == "__main__":
    sys.exit(main())
