#!/usr/bin/env python3
"""Gera o kit portátil a partir dos arquivos vivos deste repositório.

Por que um script e não uma pasta com cópias: cópia envelhece em paralelo com o original, que é
exatamente a deriva que a regra de dono único (`.claude/metodo/CONSISTENCIA.md`) existe para
impedir. O kit é *gerado*, então nunca diverge — e exportar de novo daqui a um mês traz junto tudo
que tiver melhorado no meio-tempo.

Blocos marcados com <!-- kit:projeto:inicio --> ... <!-- kit:projeto:fim --> são removidos da cópia
exportada (são específicos deste projeto). Blocos <!-- kit:modelo ... kit:modelo --> entram no lugar,
com os `< >` para quem instalar preencher.

Uso:  python3 .claude/kit/exportar.py [pasta-de-saida]
      (padrão: .claude/tmp/kit-agentes-base_<data>)
"""
import os, re, shutil, sys, zipfile
from datetime import date

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Arquivos que vão no kit. Caminho relativo à raiz do repositório.
INCLUIR = [
    "README.md",
    "GUIA_AGENTES_BASE.md",
    "CLAUDE.md",
    "_RETOMADA_TEMPLATE.md",
    ".claude/CEREBRO.md",
    ".claude/PM.md",
    ".claude/EXECUTOR.md",
    ".claude/metodo/CONSISTENCIA.md",
    ".claude/metodo/HIGIENE.md",
    ".claude/metodo/PLANOS.md",
    ".claude/metodo/COMMIT.md",
    ".claude/estado/README.md",
    ".claude/skills/coleta-consolidacao/SKILL.md",
    ".claude/skills/revisao-acionada/SKILL.md",
    ".claude/skills/encerrar-chat/SKILL.md",
    ".claude/skills/diagnostico-geral/SKILL.md",
    ".claude/skills/diagnostico-geral/README.md",
    ".claude/skills/diagnostico-geral/referencias/painel-modelo.md",
]

# Fora do kit, com o motivo — aparece no relatório da exportação.
EXCLUIDOS = {
    ".claude/metodo/DECISOES_METODO.md":
        "registra o que ESTA instalação decidiu; projeto novo começa com ledger vazio",
    ".claude/painel.md":
        "diz quais arquivos o painel lê, com que cores e em que endereço — é de cada projeto;\n     a skill que o usa vai junto, a configuração não",
    ".claude/estado/PLANO.md, PROXIMA_TAREFA.md, PROGRESSO.md":
        "nascem no primeiro uso real; stub vazio confunde quem chega",
    "spec/, coleta/, transcritor/":
        "são o produto e o diário deste projeto, não o método",
}

RE_PROJETO = re.compile(r"<!-- kit:projeto:inicio -->.*?<!-- kit:projeto:fim -->\n?", re.S)
RE_MODELO = re.compile(r"<!-- kit:modelo\n(.*?)kit:modelo -->\n?", re.S)


def transformar(texto: str) -> str:
    """Tira o que é deste projeto e promove o bloco-modelo, se houver."""
    texto = RE_PROJETO.sub("", texto)
    texto = RE_MODELO.sub(lambda m: m.group(1), texto)
    # a remoção deixa linhas em branco encostadas; colapsa para no máximo uma
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto


def coletar() -> dict:
    """Devolve {caminho_relativo: conteudo_transformado} — sem tocar em disco."""
    faltando = [c for c in INCLUIR if not os.path.isfile(os.path.join(RAIZ, c))]
    if faltando:
        raise SystemExit("Arquivos do kit não encontrados:\n  " + "\n  ".join(faltando))

    arquivos = {}
    for rel in INCLUIR:
        with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
            arquivos[rel] = transformar(f.read())

    arquivos[".gitignore"] = ".claude/tmp/\n.fuse_hidden*\n_to_delete/\n.DS_Store\nThumbs.db\n"
    for pasta in (".claude/estado/historico", ".claude/tmp"):
        arquivos[pasta + "/.gitkeep"] = ""
    return arquivos


def escrever_zip(arquivos: dict, caminho_zip: str, nome_base: str) -> str:
    """O zip é o entregável: montado direto da memória, sem depender de apagar nada.

    Motivo de não passar por uma pasta intermediária: em sessão remota o repositório é acessado por
    pasta montada, que recusa remoção ("Operation not permitted"). Um script que precise apagar a
    saída anterior só funcionaria rodando local — e este precisa funcionar nos dois lugares.
    """
    # modo "w" já trunca o arquivo: não se apaga nada antes, de propósito — a pasta montada
    # de uma sessão remota recusa remoção, e o script precisa rodar nos dois contextos.
    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, conteudo in sorted(arquivos.items()):
            z.writestr(os.path.join(nome_base, rel), conteudo)
    return caminho_zip


def escrever_pasta(arquivos: dict, destino: str) -> str:
    """Opcional: a mesma coisa descompactada, para quem quer olhar antes de copiar."""
    existia = os.path.isdir(destino)
    for rel, conteudo in arquivos.items():
        alvo = os.path.join(destino, rel)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(conteudo)
    if existia:
        print("  (a pasta já existia: os arquivos foram sobrescritos, nada foi apagado —")
        print("   se a lista de arquivos do kit encolheu, pode haver sobra de uma exportação antiga)")
    return destino


def exportar_skill(nome: str, destino_zip: str) -> str:
    """Empacota UMA skill sozinha, para salvar na conta ou levar para outro projeto.

    Mesma razão da exportação do kit (ver `metodo/DECISOES_METODO.md`, M-07 e M-09): a cópia é
    **gerada** do arquivo vivo, nunca editada à mão no destino. Skill de conta é destino de
    exportação, não segunda fonte — e é a pior cópia de perceber quando envelhece, porque some do
    repositório.
    """
    base = os.path.join(RAIZ, ".claude", "skills", nome)
    if not os.path.isdir(base):
        raise SystemExit("Skill não encontrada: " + base)

    arquivos = {}
    for raiz_, _, nomes in os.walk(base):
        for a in sorted(nomes):
            caminho = os.path.join(raiz_, a)
            rel = os.path.relpath(caminho, base)
            with open(caminho, encoding="utf-8") as f:
                arquivos[rel] = transformar(f.read())

    with zipfile.ZipFile(destino_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, conteudo in sorted(arquivos.items()):
            z.writestr(os.path.join(nome, rel), conteudo)
    return destino_zip


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--skill":
        alvo = sys.argv[2]
        saida = os.path.join(RAIZ, ".claude", "tmp", alvo + ".skill")
        print("Skill empacotada:", exportar_skill(alvo, saida))
        print("  Salve na conta para valer em qualquer chat, ou descompacte em")
        print("  .claude/skills/ de outro projeto. A fonte continua sendo este repositório.")
        raise SystemExit(0)

    nome = "kit-agentes-base_" + date.today().isoformat()
    saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, ".claude", "tmp", nome)

    arquivos = coletar()
    caminho_zip = escrever_zip(arquivos, saida.rstrip("/") + ".zip", nome)
    pasta = escrever_pasta(arquivos, saida)

    print("Kit exportado —", len(arquivos), "arquivos")
    print("  zip:  ", caminho_zip)
    print("  pasta:", pasta)
    print("\nDeixados de fora, de propósito:")
    for k, v in EXCLUIDOS.items():
        print("  -", k, "→", v)
