"""Valida os arquivos da coleta do radar contra o formato de ROTEIRO_COLETA.md.

Uso: python radar/validar.py radar/coleta/anthropic.json [outros.json ...]
Sai com código 1 se algum arquivo tiver erro.
"""
import json
import re
import sys

DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ENUMS = {
    "grupo": {"laboratorio", "midia", "inferencia", "busca_embeddings", "outro"},
    "canal": {"blog", "changelog", "docs", "precos", "status", "x_oficial", "x_ceo", "x_lider",
              "discord", "youtube", "rss", "github", "outro"},
    "publico_plano": {"individual", "estudante", "equipe", "empresa", "api", "pesquisa"},
    "tipo_modelo": {"texto", "imagem", "video", "audio_stt", "audio_tts", "audio", "musica",
                    "embedding", "rerank", "multimodal"},
    "status_modelo": {"ativo", "legado", "desativacao_anunciada", "desativado", "restrito"},
    "unidade": {"mtok_cache", "imagem", "minuto_audio", "hora_audio", "segundo_video",
                "mil_caracteres", "mil_requisicoes", "outro"},
    "capacidade": {"texto", "codigo", "imagem_gerar", "imagem_editar", "video_gerar", "audio_stt",
                   "audio_tts", "audio_tempo_real", "musica", "embeddings", "rerank", "busca_web",
                   "pesquisa_profunda", "agente_agendado", "agente_nuvem", "computer_use",
                   "cli_headless", "mcp", "notebook"},
    "acesso": {"app", "web", "api", "cli", "ide", "nuvem"},
    "publico_programa": {"estudante", "pesquisador", "educador", "startup", "ong", "todos"},
    "elegivel": {"sim", "nao", "talvez"},
    "status_programa": {"aberto", "fechado", "em_breve", "continuo", "desconhecido"},
    "origem": {"verificado", "a_verificar"},
}


def validar(caminho):
    erros = []

    def err(onde, msg):
        erros.append(f"{onde}: {msg}")

    def url(onde, v, obrigatorio=True):
        if v is None and not obrigatorio:
            return
        if not isinstance(v, str) or not v.startswith(("http://", "https://")):
            err(onde, f"URL inválida: {v!r}")

    def data(onde, v, obrigatorio=False):
        if v is None and not obrigatorio:
            return
        if not isinstance(v, str) or not DATA.match(v):
            err(onde, f"data fora do formato AAAA-MM-DD: {v!r}")

    def enum(onde, v, nome):
        if v not in ENUMS[nome]:
            err(onde, f"valor {v!r} não está em {sorted(ENUMS[nome])}")

    def num(onde, v):
        if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))):
            err(onde, f"deveria ser número ou null: {v!r}")

    try:
        d = json.load(open(caminho, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"{caminho}: JSON inválido ({e})"]

    p = d.get("provedor") or {}
    for campo in ("id", "nome", "grupo", "resumo"):
        if not p.get(campo):
            err("provedor", f"falta '{campo}'")
    if p.get("grupo"):
        enum("provedor.grupo", p["grupo"], "grupo")
    url("provedor.site", p.get("site"), obrigatorio=False)
    for i, f in enumerate(p.get("fontes") or []):
        url(f"provedor.fontes[{i}]", f)
    data("coletado_em", d.get("coletado_em"), obrigatorio=True)

    for i, c in enumerate(d.get("canais") or []):
        enum(f"canais[{i}].tipo", c.get("tipo"), "canal")
        url(f"canais[{i}].url", c.get("url"))

    for i, pl in enumerate(d.get("planos") or []):
        o = f"planos[{i}]"
        if not pl.get("nome"):
            err(o, "falta 'nome'")
        enum(o + ".publico", pl.get("publico"), "publico_plano")
        num(o + ".preco_mensal_usd", pl.get("preco_mensal_usd"))
        num(o + ".preco_anual_usd", pl.get("preco_anual_usd"))
        url(o + ".fonte_url", pl.get("fonte_url"))
        data(o + ".conferido_em", pl.get("conferido_em"), obrigatorio=True)

    ids = set()
    for i, m in enumerate(d.get("modelos") or []):
        o = f"modelos[{i}]"
        if not m.get("id") or not m.get("nome"):
            err(o, "falta 'id' ou 'nome'")
        if m.get("id") in ids:
            err(o, f"id repetido: {m.get('id')}")
        ids.add(m.get("id"))
        enum(o + ".tipo", m.get("tipo"), "tipo_modelo")
        enum(o + ".status", m.get("status", "ativo"), "status_modelo")
        data(o + ".lancado_em", m.get("lancado_em"))
        data(o + ".desativa_em", m.get("desativa_em"))
        if m.get("status") == "desativacao_anunciada" and not m.get("desativa_em"):
            err(o, "status desativacao_anunciada exige 'desativa_em'")
        pr = m.get("preco")
        if pr:
            num(o + ".preco.entrada_usd_mtok", pr.get("entrada_usd_mtok"))
            num(o + ".preco.saida_usd_mtok", pr.get("saida_usd_mtok"))
            if pr.get("entrada_usd_mtok") is not None or pr.get("saida_usd_mtok") is not None:
                url(o + ".preco.fonte_url", pr.get("fonte_url"))
        for j, op in enumerate(m.get("outros_precos") or []):
            enum(f"{o}.outros_precos[{j}].unidade", op.get("unidade"), "unidade")
            if op.get("valor_usd") is None:
                err(f"{o}.outros_precos[{j}]", "falta 'valor_usd'")
            num(f"{o}.outros_precos[{j}].valor_usd", op.get("valor_usd"))
            url(f"{o}.outros_precos[{j}].fonte_url", op.get("fonte_url"))
        for j, n in enumerate(m.get("notas") or []):
            oo = f"{o}.notas[{j}]"
            if not n.get("benchmark"):
                err(oo, "falta 'benchmark'")
            if n.get("valor") is None:
                err(oo, "falta 'valor' (se não há nota, não inclua a linha)")
            num(oo + ".valor", n.get("valor"))
            data(oo + ".medido_em", n.get("medido_em"), obrigatorio=True)
            url(oo + ".fonte_url", n.get("fonte_url"))

    for i, c in enumerate(d.get("capacidades") or []):
        o = f"capacidades[{i}]"
        enum(o + ".capacidade", c.get("capacidade"), "capacidade")
        if not c.get("produto"):
            err(o, "falta 'produto'")
        for a in c.get("como_acessar") or []:
            enum(o + ".como_acessar", a, "acesso")
        url(o + ".fonte_url", c.get("fonte_url"))

    for i, g in enumerate(d.get("gratis") or []):
        o = f"gratis[{i}]"
        if not g.get("titulo"):
            err(o, "falta 'titulo'")
        url(o + ".url", g.get("url"))
        data(o + ".valido_ate", g.get("valido_ate"))
        enum(o + ".origem", g.get("origem"), "origem")

    for i, pg in enumerate(d.get("programas") or []):
        o = f"programas[{i}]"
        if not pg.get("nome"):
            err(o, "falta 'nome'")
        enum(o + ".publico", pg.get("publico"), "publico_programa")
        if pg.get("elegivel") is not None:
            enum(o + ".elegivel", pg.get("elegivel"), "elegivel")
        enum(o + ".status", pg.get("status"), "status_programa")
        num(o + ".valor_usd", pg.get("valor_usd"))
        url(o + ".url", pg.get("url"))
        data(o + ".prazo", pg.get("prazo"))
        data(o + ".verificado_em", pg.get("verificado_em"), obrigatorio=True)

    for i, ind in enumerate(d.get("indicadores") or []):
        o = f"indicadores[{i}]"
        if not ind.get("nome"):
            err(o, "falta 'nome'")
        num(o + ".valor", ind.get("valor"))
        data(o + ".medido_em", ind.get("medido_em"), obrigatorio=True)
        url(o + ".fonte_url", ind.get("fonte_url"))

    return [f"{caminho} → {e}" for e in erros]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    todos = []
    for arq in sys.argv[1:]:
        e = validar(arq)
        todos += e
        print(f"{'OK ' if not e else 'ERRO'} {arq}" + (f" ({len(e)} problemas)" if e else ""))
    for e in todos:
        print("  - " + e)
    sys.exit(1 if todos else 0)
