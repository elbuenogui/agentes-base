"""Gera o SQL que importa a coleta do radar no esquema `radar` do Supabase.

Uso: python radar/importar.py radar/coleta/*.json > saida.sql
     python radar/importar.py --por-provedor DIR radar/coleta/*.json   (um .sql por provedor)

Tudo é upsert: rodar de novo atualiza em vez de duplicar. Modelos novos entram com
`acompanhado = false` (não aparecem na tabela curada do painel); os que já existem mantêm
o valor que têm. Preços e preços por unidade entram com `vigente_desde = coletado_em`.
O item `gratis` da coleta vira `radar.novidades` com tipo 'gratis'.
"""
import json
import os
import sys


def q(v):
    """Literal SQL de um valor Python."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (list, dict)):
        return q(json.dumps(v, ensure_ascii=False)) + "::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def arr(v):
    return "array[" + ",".join(q(x) for x in (v or [])) + "]::text[]" if v else "'{}'::text[]"


def upsert(tabela, cols, linhas, conflito, atualizar=None):
    if not linhas:
        return ""
    atualizar = [c for c in cols if c not in conflito] if atualizar is None else atualizar
    valores = ",\n  ".join("(" + ",".join(l) + ")" for l in linhas)
    acao = ("do update set " + ", ".join(f"{c}=excluded.{c}" for c in atualizar)) if atualizar else "do nothing"
    return (f"insert into radar.{tabela} ({','.join(cols)}) values\n  {valores}\n"
            f"on conflict ({','.join(conflito)}) {acao};\n")


def unicos(linhas, chave):
    """Remove linhas repetidas pela chave de conflito (a última vence), senão o upsert falha."""
    vistos = {}
    for l in linhas:
        vistos[chave(l)] = l
    return list(vistos.values())


def sql_provedor(d):
    p = d["provedor"]
    pid, em = p["id"], d["coletado_em"]
    out = [f"-- {pid}\n"]
    out.append(upsert("provedores", ["id", "nome", "grupo", "site", "resumo", "pais", "fontes", "coletado_em", "atualizado_em"],
                      [[q(pid), q(p["nome"]), q(p["grupo"]), q(p.get("site")), q(p.get("resumo")), q(p.get("pais")),
                        q(p.get("fontes") or []), q(em), "now()"]], ["id"]))
    out.append(upsert("canais", ["provedor_id", "tipo", "nome", "url", "handle", "observacao"],
                      unicos([[q(pid), q(c["tipo"]), q(c.get("nome")), q(c["url"]), q(c.get("handle")), q(c.get("observacao"))]
                              for c in d.get("canais") or [] if c.get("url")], lambda l: l[3]), ["provedor_id", "url"]))
    out.append(upsert("planos", ["provedor_id", "nome", "publico", "preco_mensal_usd", "preco_anual_usd", "inclui", "limites", "fonte_url", "conferido_em"],
                      unicos([[q(pid), q(x["nome"]), q(x["publico"]), q(x.get("preco_mensal_usd")), q(x.get("preco_anual_usd")),
                               q(x.get("inclui")), q(x.get("limites")), q(x["fonte_url"]), q(x.get("conferido_em") or em)]
                              for x in d.get("planos") or []], lambda l: l[1]), ["provedor_id", "nome"]))
    modelos, precos, unid, notas = [], [], [], []
    for m in d.get("modelos") or []:
        mid = q(m["id"])
        modelos.append([mid, q(p["nome"]), q(pid), q(m["nome"]), q(m["tipo"]), q(m.get("pesos_abertos")), q(m.get("lancado_em")),
                        q(m.get("status") or "ativo"), q(m.get("desativa_em")), q(m.get("contexto_tokens")), "false"])
        pr = m.get("preco") or {}
        if pr.get("fonte_url") and (pr.get("entrada_usd_mtok") is not None or pr.get("saida_usd_mtok") is not None):
            precos.append([mid, q(em), q(pr.get("entrada_usd_mtok")), q(pr.get("saida_usd_mtok")), q(pr["fonte_url"]), "now()"])
        for u in m.get("outros_precos") or []:
            if u.get("valor_usd") is not None and u.get("fonte_url"):
                unid.append([mid, q(u["unidade"]), q(u["valor_usd"]), q(u.get("condicao") or ""), q(em), q(u["fonte_url"])])
        for n in m.get("notas") or []:
            if n.get("valor") is not None and n.get("fonte_url"):
                notas.append([mid, q(n["benchmark"]), q(n["valor"]), q(n.get("medido_em") or em), q(n["fonte_url"])])
    out.append(upsert("modelos", ["id", "provedor", "provedor_id", "nome", "tipo", "pesos_abertos", "lancado_em", "status", "desativa_em", "contexto_tokens", "acompanhado"],
                      modelos, ["id"], ["provedor", "provedor_id", "nome", "tipo", "pesos_abertos", "lancado_em", "status", "desativa_em", "contexto_tokens"]))
    out.append(upsert("precos", ["modelo_id", "vigente_desde", "entrada_usd_mtok", "saida_usd_mtok", "fonte_url", "conferido_em"],
                      unicos(precos, lambda l: l[0]), ["modelo_id", "vigente_desde"]))
    out.append(upsert("precos_unidade", ["modelo_id", "unidade", "valor_usd", "condicao", "vigente_desde", "fonte_url"],
                      unicos(unid, lambda l: (l[0], l[1], l[3])), ["modelo_id", "unidade", "condicao", "vigente_desde"]))
    out.append(upsert("notas", ["modelo_id", "benchmark", "valor", "medido_em", "fonte_url"],
                      unicos(notas, lambda l: (l[0], l[1], l[3])), ["modelo_id", "benchmark", "medido_em"]))
    out.append(upsert("capacidades", ["provedor_id", "capacidade", "produto", "como_acessar", "plano_minimo", "gratis", "headless", "comando", "limites", "fonte_url"],
                      unicos([[q(pid), q(c["capacidade"]), q(c["produto"]), arr(c.get("como_acessar")), q(c.get("plano_minimo")), q(c.get("gratis")),
                               q(c.get("headless")), q(c.get("comando")), q(c.get("limites")), q(c["fonte_url"])]
                              for c in d.get("capacidades") or []], lambda l: (l[1], l[2])), ["provedor_id", "capacidade", "produto"]))
    out.append(upsert("programas", ["provedor_id", "nome", "publico", "beneficio", "valor_usd", "requisitos", "elegivel", "elegivel_motivo", "como_aplicar", "url", "status", "prazo", "verificado_em"],
                      unicos([[q(pid), q(x["nome"]), q(x["publico"]), q(x.get("beneficio")), q(x.get("valor_usd")), q(x.get("requisitos")), q(x.get("elegivel")),
                               q(x.get("elegivel_motivo")), q(x.get("como_aplicar")), q(x["url"]), q(x["status"]), q(x.get("prazo")), q(x.get("verificado_em") or em)]
                              for x in d.get("programas") or []], lambda l: l[1]), ["provedor_id", "nome"]))
    out.append(upsert("novidades", ["tipo", "titulo", "provedor", "resumo", "por_que_importa", "url", "valido_ate"],
                      unicos([["'gratis'", q(g["titulo"]), q(p["nome"]), q(g.get("resumo")),
                               q(" · ".join(x for x in [g.get("limites") and "Limites: " + g["limites"],
                                                        "chamável por agente" if g.get("chamavel_por_agente") else None,
                                                        "a verificar" if g.get("origem") == "a_verificar" else None] if x) or None),
                               q(g["url"]), q(g.get("valido_ate"))]
                              for g in d.get("gratis") or [] if g.get("url")], lambda l: l[5]), ["url"]))
    # indicadores não têm chave única: apaga os desta coleta e regrava
    ind = d.get("indicadores") or []
    if ind:
        out.append(f"delete from radar.indicadores where provedor_id={q(pid)} and medido_em={q(em)};\n")
        out.append(upsert("indicadores", ["provedor_id", "modelo_id", "nome", "valor", "unidade", "descricao", "medido_em", "fonte_url"],
                          [[q(pid), q(i.get("modelo_id")), q(i["nome"]), q(i.get("valor")), q(i.get("unidade")), q(i.get("descricao")),
                            q(i.get("medido_em") or em), q(i["fonte_url"])] for i in ind], ["id"], []).replace(
                              "on conflict (id) do nothing", ""))
    return "".join(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    destino = None
    if args[:1] == ["--por-provedor"]:
        destino, args = args[1], args[2:]
        os.makedirs(destino, exist_ok=True)
    for caminho in args:
        d = json.load(open(caminho, encoding="utf-8"))
        sql = sql_provedor(d)
        if destino:
            open(os.path.join(destino, d["provedor"]["id"] + ".sql"), "w", encoding="utf-8").write(sql)
        else:
            sys.stdout.write(sql)
