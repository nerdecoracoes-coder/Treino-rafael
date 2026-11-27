"""Gera o catálogo embutido na tela Saúde do app Praticantes (index.html) a partir de catalogo/bloco_*.json.

Uso:  python3 catalogo/build_catalog.py           (na raiz do repositório)

- Traduz os status do catálogo para o vocabulário que o validador do app aceita:
    status_nutri: validado, validado_com_ressalva -> validado; sem_fonte_exata -> pendente
    imagem.status: baixada_conferida, baixada_aproximada -> validada; baixada_revisar -> candidata
- Acrescenta medida caseira, passo e limites de porção de catalogo/medidas.json.
- Só mexe no bloco <script> marcado "gerado por build_catalog.py" da página Saúde e na marca ev-build.
- Não toca em nenhum dado de usuário (diário, planos, alimentos próprios ficam no aparelho/servidor).
"""
import base64, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
CAT = os.path.join(ROOT, "catalogo")

MAP_N = {"validado": "validado", "validado_com_ressalva": "validado", "sem_fonte_exata": "pendente"}
MAP_I = {"baixada_conferida": "validada", "baixada_aproximada": "validada", "baixada_revisar": "candidata"}
KEEP_I = ("arquivo", "arquivo_local", "url", "pagina", "autor", "licenca", "atribuicao", "status", "nota")
KEEP = ("id", "bloco", "nome", "variacao", "sinonimos", "categorias", "subcategoria", "preparo", "kcal100", "p100", "c100",
        "f100", "fibra100", "fonte", "fonte_ref", "fonte_versao", "fonte_obs", "status_nutri", "estimativa")


MEDIDAS = {}
if os.path.exists(os.path.join(CAT, "medidas.json")):
    MEDIDAS = {k: v for k, v in json.load(open(os.path.join(CAT, "medidas.json"), encoding="utf-8")).items() if k.startswith("EVT-")}


def app_item(x):
    o = {k: x.get(k) for k in KEEP}
    o["status_nutri"] = MAP_N.get(x["status_nutri"], x["status_nutri"])
    if x["status_nutri"] == "validado_com_ressalva":
        o["fonte_obs"] = "Ressalva: " + (x.get("fonte_obs") or "")
    im = dict(x.get("imagem") or {})
    im["status"] = MAP_I.get(im.get("status"), im.get("status") or "pendente")
    o["imagem"] = {k: im.get(k) for k in KEEP_I}
    md = MEDIDAS.get(x["id"])
    if md:
        o.update({k: md[k] for k in ("medida", "passo_g", "min_g", "max_g")})
    return o


def blocos():
    out = []
    for b in range(1, 100):
        p = os.path.join(CAT, f"bloco_{b:02d}.json")
        if not os.path.exists(p):
            break
        items = json.load(open(p, encoding="utf-8"))
        out.append({"bloco": b, "versao": "1.1.0", "alimentos": [app_item(x) for x in items]})
    return out


def main():
    t = open(INDEX, encoding="utf-8").read()
    i = t.index("const pageData=") + len("const pageData=")
    pd, _ = json.JSONDecoder().raw_decode(t[i:])
    old_b64 = pd["saude"]
    h = base64.b64decode(old_b64).decode("utf-8")
    novo = "window.EvoCatalogBlocos=" + json.dumps(blocos(), ensure_ascii=False, separators=(",", ":")) + ";"
    h2, n = re.subn(r"(<script>/\* gerado por build_catalog\.py - nao editar \*/\n?)window\.EvoCatalogBlocos=.*?(</script>)",
                    lambda m: m.group(1) + novo + "\n" + m.group(2), h, count=1, flags=re.S)
    if n != 1:
        sys.exit("bloco do catálogo não encontrado na página Saúde")
    new_b64 = base64.b64encode(h2.encode("utf-8")).decode("ascii")
    if t.count(old_b64) != 1:
        sys.exit("página Saúde não encontrada de forma única no index.html")
    t = t.replace(old_b64, new_b64)
    build = hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]
    t = re.sub(r'(<meta name="ev-build" content=")[a-f0-9]+(")', r"\g<1>" + build + r"\2", t, count=1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("catálogo embutido atualizado; ev-build", build)


if __name__ == "__main__":
    main()
