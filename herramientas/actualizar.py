"""Actualización automática del Tablero Informativo Aranzazu.

Lee las fuentes ya descargadas y actualiza data.json SOLO si algo cambió.

Uso:
  python3 herramientas/actualizar.py \
      --rh  <tablero_rh.html>            (Artifact read del Tablero RH Aranzazu)
      [--nombres <base-personal-nombres.csv>]  (solo si el informe pide nombres)
      [--libro <texto del libro DesaProd>]     (read_resource del .xlsx, hoja Resumen)
      [--avisos <avisos.txt>]                  (read_resource de Avisos.xlsx)
      [--hoy AAAA-MM-DD]

Escribe data.json (si hubo cambios) y deja un informe en herramientas/_informe.json:
  {"cambios": [...], "necesita_nombres": bool, "fotos": [rutas eventos/*.jpg], "fotos_quitar": [...]}
"""
import argparse, datetime, json, os, re, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data.json")
MES3 = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
TEMAS = {1: "ene-feb", 2: "ene-feb", 3: "mar-abr", 4: "mar-abr", 5: "mayo", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}
SMALL = {"de", "del", "la", "las", "los", "y"}


def tc(s):
    out = []
    for i, w in enumerate(str(s or "").strip().split()):
        lw = w.lower()
        out.append(lw if (i > 0 and lw in SMALL) else lw[:1].upper() + lw[1:])
    return " ".join(out)


def num(s):
    s = str(s or "").strip().replace(" ", "")
    if not s or s.startswith("#"):
        return None
    s = s.replace("%", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


# ---------------- Resultados operativos (hoja Resumen) ----------------
def leer_resumen(path):
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"## Sheet: Resumen[^\n]*\n(.*?)(?:\nFormulas:|\n## Sheet:)", txt, re.S)
    if not m:
        raise SystemExit("No encontré la hoja Resumen en el libro.")
    rows = [r.split("\t") for r in m.group(1).split("\n")]
    head = [c.strip() for c in rows[0] if c.strip()]
    mes_txt, dia = head[0], int(float(head[1]))
    mes = [x.lower() for x in MESES].index(mes_txt.lower()) + 1
    lab = lambda r: (r[0].strip() if r else "")
    reals = [r for r in rows if lab(r) == "Real"]
    plans = [r for r in rows if lab(r) == "Plan"]
    secas = [r for r in rows if lab(r) == "SECAS"]
    g = lambda r, i: num(r[i]) if len(r) > i else None
    ext_r, des_r = reals[0], reals[1]
    ext_p, des_p = plans[0], plans[1]
    sec = secas[0]
    disp_p = next((r for r in rows if len(r) > 6 and r[6].strip() == "Planeados"), None)
    disp_r = next((r for r in rows if len(r) > 6 and r[6].strip() == "Reales"), None)
    crf = next((r for r in rows if len(r) > 6 and r[6].strip() == "CRF"), None)
    rf = next((r for r in rows if len(r) > 6 and r[6].strip() == "RF"), None)
    return mes, dia, {
        "dia": {"extraccionSecas": g(sec, 1), "extraccionHumedas": g(ext_r, 1), "planExtraccion": g(ext_p, 1),
                "desarrollo": g(des_r, 1), "planDesarrollo": g(des_p, 1),
                "disparos": g(disp_r, 7) if disp_r else None, "disparosPlan": g(disp_p, 7) if disp_p else None,
                "rellenoRF": g(rf, 7) if rf else 0, "rellenoCRF": g(crf, 7) if crf else 0},
        "mes": {"extraccionSecas": g(sec, 4), "extraccionHumedas": g(ext_r, 4), "planExtraccion": g(ext_p, 4),
                "desarrollo": g(des_r, 4), "planDesarrollo": g(des_p, 4),
                "rellenoRF": g(rf, 9) if rf else 0, "rellenoCRF": g(crf, 9) if crf else 0},
    }


# ---------------- Avisos (columna B) ----------------
def leer_avisos(path):
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"## Sheet:[^\n]*\n(.*?)(?:\nFormulas:|\n## Sheet:|\Z)", txt, re.S)
    body = m.group(1) if m else txt
    out = []
    for r in body.split("\n"):
        c = r.split("\t")
        if len(c) > 1 and c[1].strip():
            out.append(c[1].strip())
    return out


# ---------------- Tablero RH: base de datos y eventos ----------------
def leer_rh(path):
    src = open(path, encoding="utf-8").read()
    snap = json.loads(re.search(r'<script id="snap" type="application/json">(.*?)</script>', src, re.S).group(1))
    events = json.loads(re.search(r"const EVENTS=(\[.*?\]);\s*$", src, re.M).group(1))
    return snap["bd"], events


def personal_desde(bd, names_csv):
    lines = [l.strip() for l in open(names_csv, encoding="utf-8").read().lstrip("﻿").splitlines()]
    lines = [l for l in lines if l and not l.startswith("[")]
    ver = lines[0].split(",")[1]
    names = lines[1:]
    if ver != bd["csvh"] or len(names) != len(bd["P"]):
        raise SystemExit(f"La lista de nombres ({ver}, {len(names)}) no corresponde a la base ({bd['csvh']}, {len(bd['P'])}).")
    out = []
    for i, (p, n) in enumerate(zip(bd["P"], names)):
        if p[0] != "A":
            continue
        out.append({"id": i + 1, "nombre": tc(n), "puesto": tc(p[11]), "unidad": tc(p[3]),
                    "cumpleanos": f"{int(p[9]):02d}-{int(p[10]):02d}" if p[9] and p[10] else "",
                    "ingreso": p[12] or "", "foto": ""})
    return out


def eventos_desde(events):
    events = sorted(events, key=lambda e: e["d"], reverse=True)[:3]
    slides = []
    for e in events:
        y, mo, d = map(int, e["d"].split("-"))
        desc = (e.get("txt") or "").split("\n")[0].strip()
        if len(desc) > 150:
            desc = desc[:147].rsplit(" ", 1)[0] + "…"
        fotos = e.get("fotos") or []
        for k, f in enumerate(fotos[:8]):
            slides.append({"id": f"{e['id']}-{k}", "evento": e["id"], "categoria": e.get("cat", ""), "titulo": e["t"],
                           "fecha": f"{d} {MES3[mo-1]}", "lugar": e.get("lugar", ""), "descripcion": desc,
                           "imagen": f"eventos/{f}.jpg", "foto": k + 1, "fotosEvento": min(len(fotos), 8)})
    return slides


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rh"); ap.add_argument("--nombres"); ap.add_argument("--libro"); ap.add_argument("--avisos")
    ap.add_argument("--archivo-libro", default="")
    ap.add_argument("--hoy", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    hoy = datetime.date.fromisoformat(a.hoy)
    data = json.load(open(DATA, encoding="utf-8"))
    antes = json.dumps(data, sort_keys=True, ensure_ascii=False)
    cambios, informe = [], {"necesita_nombres": False, "fotos": [], "fotos_quitar": []}
    meta = data.setdefault("meta", {})

    if a.libro:
        mes, dia, res = leer_resumen(a.libro)
        r0 = data.get("resultados", {})
        dd = res["dia"]
        dd["extraccionPendiente"] = bool(dd.get("extraccionSecas") is None and not dd.get("extraccionHumedas"))
        nuevo = dict(res, corte=f"{dia} {MES3[mes-1]} {hoy.year}", diaReporte=dia,
                     fuente=f"{a.archivo_libro or 'Reporte DesaProd'} · hoja Resumen")
        if r0.get("diaReporte") != dia or r0.get("corte", "").split(" ")[1:2] != [MES3[mes-1]] or r0.get("dia") != nuevo["dia"] or r0.get("mes") != nuevo["mes"]:
            data["resultados"] = nuevo
            cambios.append(f"resultados → día {dia} {MES3[mes-1]}")

    if a.avisos:
        av = leer_avisos(a.avisos)
        if av and av != data.get("avisosTicker"):
            data["avisosTicker"] = av
            cambios.append(f"avisos ({len(av)})")

    if a.rh:
        bd, events = leer_rh(a.rh)
        fr = meta.get("fuenteRH") or {}
        if bd.get("csvh") != fr.get("csvh") or bd.get("at") != fr.get("baseDatos"):
            if a.nombres:
                per = personal_desde(bd, a.nombres)
                if per != data.get("personal"):
                    data["personal"] = per
                    cambios.append(f"cumpleaños ({len(per)} activos)")
                meta["fuenteRH"] = {"tablero": "Tablero RH Aranzazu", "baseDatos": bd.get("at"), "csvh": bd.get("csvh")}
            else:
                informe["necesita_nombres"] = True
        ev = eventos_desde(events)
        viejas = {s["imagen"] for s in data.get("eventosFotos", [])}
        nuevas = [s["imagen"] for s in ev]
        if ev != data.get("eventosFotos"):
            data["eventosFotos"] = ev
            cambios.append("eventos: " + ", ".join(dict.fromkeys(s["titulo"] for s in ev)))
        informe["fotos"] = nuevas
        informe["fotos_quitar"] = sorted(viejas - set(nuevas))

    tema = TEMAS.get(hoy.month, "core")
    if meta.get("tema") != tema:
        meta["tema"] = tema
        cambios.append(f"tema del mes → {tema}")

    meta["esDemo"] = False
    despues = json.dumps(data, sort_keys=True, ensure_ascii=False)
    if despues != antes:
        if cambios:
            meta["actualizado"] = datetime.datetime.now(ZoneInfo("America/Mexico_City")).strftime("%Y-%m-%d %H:%M")
        json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    informe["cambios"] = cambios
    json.dump(informe, open(os.path.join(HERE, "_informe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(informe, ensure_ascii=False))


if __name__ == "__main__":
    main()
