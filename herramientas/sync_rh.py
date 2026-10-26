"""Sincroniza cumpleañeros (Base de datos) y eventos del Tablero RH Aranzazu hacia data.json.
Uso: python3 sync_rh.py <rh_index.html> <nombres.csv> <data.json> <files_map.json>
"""
import json, re, sys, datetime

rh_html, names_csv, data_path, files_out = sys.argv[1:5]
RH_URL = "https://claude.ai/artifact/N15fPuqdapJp7YvSRH2Nxb"
src = open(rh_html, encoding="utf-8").read()

# --- Base de datos ---
snap = json.loads(re.search(r'<script id="snap" type="application/json">(.*?)</script>', src, re.S).group(1))
bd = snap["bd"]
lines = [l.strip() for l in open(names_csv, encoding="utf-8").read().lstrip("﻿").splitlines()]
ver = lines[0].split(",")[1]
names = [l for l in lines[1:] if l]
assert ver == bd["csvh"], f"La lista de nombres ({ver}) no corresponde a la base ({bd['csvh']})"
assert len(names) == len(bd["P"]), f"{len(names)} nombres vs {len(bd['P'])} registros"

SMALL = {"de", "del", "la", "las", "los", "y"}
def tc(s):
    out = []
    for i, w in enumerate(str(s or "").strip().split()):
        lw = w.lower()
        out.append(lw if (i > 0 and lw in SMALL) else lw[:1].upper() + lw[1:])
    return " ".join(out)

personal = []
for i, (p, n) in enumerate(zip(bd["P"], names)):
    if p[0] != "A":
        continue
    cumple = f"{int(p[9]):02d}-{int(p[10]):02d}" if p[9] and p[10] else ""
    personal.append({
        "id": i + 1,
        "nombre": tc(n),
        "puesto": tc(p[11]),
        "unidad": tc(p[3]),
        "cumpleanos": cumple,
        "ingreso": p[12] or "",
        "foto": "",
    })

# --- Eventos ---
m = re.search(r"const EVENTS=(\[.*?\]);\s*$", src, re.M)
events = json.loads(m.group(1))
events.sort(key=lambda e: e["d"], reverse=True)
MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
today = datetime.date.today()
cut = today - datetime.timedelta(days=75)
recent = events[:4]
slides, files = [], {}
for e in recent:
    y, mo, d = map(int, e["d"].split("-"))
    desc = (e.get("txt") or "").split("\n")[0].strip()
    if len(desc) > 150:
        desc = desc[:147].rsplit(" ", 1)[0] + "…"
    fotos = e.get("fotos") or []
    for k, f in enumerate(fotos[:8]):
        path = f"eventos/{f}.jpg"
        files[path] = {"artifact": RH_URL, "path": path}
        slides.append({
            "id": f"{e['id']}-{k}",
            "evento": e["id"],
            "categoria": e.get("cat", ""),
            "titulo": e["t"],
            "fecha": f"{d} {MES[mo-1]}",
            "lugar": e.get("lugar", ""),
            "descripcion": desc,
            "imagen": path,
            "foto": k + 1,
            "fotosEvento": min(len(fotos), 8),
        })

data = json.load(open(data_path, encoding="utf-8"))
data["personal"] = personal
data["eventosFotos"] = slides
meta = data.setdefault("meta", {})
meta["esDemo"] = False
meta["fuenteRH"] = {"tablero": "Tablero RH Aranzazu", "baseDatos": bd.get("at"), "sincronizado": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
json.dump(data, open(data_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(files, open(files_out, "w"), indent=0)
print(f"activos={len(personal)} eventos={len(recent)} fotos={len(slides)} base_at={bd.get('at')}")
