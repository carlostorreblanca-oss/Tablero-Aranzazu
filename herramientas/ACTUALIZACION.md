# Actualización automática del tablero

La tarea programada **Tablero INFORMATIVO Aranzazu** (6:45, 8:45 y 18:45, hora del centro de México) sigue estos pasos. **Solo publica cuando algo cambió.**

> **Regla de oro:** cada fuente es independiente. Si una no se puede leer (archivo movido, sin permiso, error), **sigue con las demás**: corre `actualizar.py` sin el argumento de esa fuente, publica lo que sí cambió y en el informe final di qué fuente falló y por qué. Nunca detengas toda la actualización por una sola fuente.

## 0. Preparar
- Repositorio clonado en `REPO` (por ejemplo `/home/claude/Tablero-Aranzazu`). Trabaja siempre ahí.
- Carpeta temporal para fuentes: `FUENTES=/tmp/fuentes` (créala).
- Fecha de hoy en America/Mexico_City → `HOY` (AAAA-MM-DD).

## 1. Descargar fuentes (solo lectura, nunca modificar los originales)
1. **Resultados operativos**: `read_resource` **sin** startPage/endPage de `file:///b!FZeGuCKJckKNup0XdY6V_vvupZKY1mZGlNF7ZrWKU2FwEEfxXPYCSKRZgxtDJIGm/0177JFFEYI5GXXE226T5AJQUSOOJ32XKEQ` (`Reporte_Octubre_DesaProd 2026.xlsx`, OneDrive de Gibrán Ochoa, carpeta `Desarrollo`; dirección vigente desde el 24 oct 2026). El resultado es grande: si se guardó solo en un archivo, usa esa ruta como `--libro` (el script acepta el JSON tal cual); si llega en línea, guárdalo en `$FUENTES/libro.txt`. Solo se usa la hoja **Resumen**. Al cambiar de mes, busca con `sharepoint_search` `Reporte_<Mes>_DesaProd <año>` (xlsx) y toma el del mes en curso. Si no se puede leer, omite `--libro`, deja los resultados como están y repórtalo.
2. **Avisos**: `read_resource` de `file:///b!Bza5sahU602uuqM08-zTWI6bkkAClr1GrNJV-zb2vLRGO5ByzSSyRrQAsRh48i1m/Tablero/Avisos.xlsx`. Guarda el texto tal cual en `$FUENTES/avisos.txt`. Solo cuenta la **columna B** con texto.
3. **CCRM** (reporte diario de verificaciones): `read_resource` de `file:///b!8JKnVbHVc0u3Dfvfx4FcYDtc1j0CEhxBrLlkuBjmDAvlPLT6dF6vRI6-v5wwGbFt/01WRBESYQQPNFOIM6BHVF3LQYG4VRFGSKG` (`CCRM DIARIO (OCTUBRE 2026).xlsx`, OneDrive de Luis Murillo) con `startPage=1` y `endPage=1` (solo la hoja **CCRM**). Guarda el texto tal cual en `$FUENTES/ccrm.txt` (si el resultado se guardó solo en un archivo, usa esa ruta). Al cambiar de mes el libro se llama `CCRM DIARIO (<MES> <AÑO>).xlsx`: si el de octubre ya no tiene el mes en curso o no se encuentra, búscalo con `sharepoint_search` (`CCRM DIARIO <MES> <AÑO>`, xlsx) y toma el del mes actual. El script toma el bloque **"CCRM AL DIA N DE <MES> <AÑO>"** más reciente que ya tenga verificaciones y revisa que gerentes + supervisores + operadores sumen el total.
4. **Tablero RH** (eventos y base de datos): Artifact `read` de `https://claude.ai/artifact/N15fPuqdapJp7YvSRH2Nxb`. El resultado indica el archivo local donde guardó la página completa: úsalo como `--rh`.

## 2. Calcular cambios
```
cd $REPO
python3 herramientas/actualizar.py --rh <rh.html> --libro <libro> --archivo-libro "Reporte_Octubre_DesaProd 2026.xlsx" --avisos $FUENTES/avisos.txt --ccrm $FUENTES/ccrm.txt --hoy $HOY
```
Lee el informe (`herramientas/_informe.json`):
- Si `necesita_nombres` es `true`: la base de datos del Tablero RH cambió. Lee `file:///b!Bza5sahU602uuqM08-zTWI6bkkAClr1GrNJV-zb2vLRGO5ByzSSyRrQAsRh48i1m/Tablero RH temporal/base-personal-nombres.csv` con `read_resource`, guarda el texto exacto en `$FUENTES/nombres.csv` y vuelve a correr el comando agregando `--nombres $FUENTES/nombres.csv`.
- `cambios`: lista de lo que cambió. Si está vacía y `git status --porcelain` no muestra cambios, **termina**: informa "Sin cambios" y no publiques nada.

## 3. Fotos de eventos
Para cada ruta de `fotos` que no exista en `$REPO/eventos/`, descárgala con Artifact `read` del Tablero RH (`url` del Tablero RH, `paths`: las rutas, `out_dir`: `$REPO`). Borra del repositorio las rutas de `fotos_quitar`.

## 4. Publicar en GitHub (sitio web)
```
python3 herramientas/build.py
python3 herramientas/build_artefactos.py
git add -A
git commit -m "Actualización automática <HOY HH:MM>: <cambios>"
git push origin main
```
GitHub Pages se publica solo en 1–2 minutos: https://carlostorreblanca-oss.github.io/Tablero-Aranzazu/

**Confirma el push antes de seguir:** corre `git fetch origin main && git status -sb`; la primera línea **no** debe decir `ahead`. Si el push falló (por ejemplo, porque otra persona subió cambios), haz `git pull --rebase origin main`, vuelve a correr `build.py` y `build_artefactos.py`, y repite el push. **No publiques en el tablero de TV hasta que el push haya llegado**: la web y el tablero de TV deben quedar siempre con el mismo `data.json`.

## 5. Publicar en los tableros de claude.ai (solo si `cambios` no está vacía)
Primero genera las páginas limpias: `python3 herramientas/build_artefactos.py` (crea `herramientas/artefactos/tv.html` y `movil.html`; inclúyelas en el commit del paso 4).

| Tablero | url | file_path |
|---|---|---|
| TV | `https://claude.ai/artifact/1bXCkxbXbZb3BX752mhAn5` | `<REPO>/herramientas/artefactos/tv.html` |

El tablero de celular (`7AfrvoektHiDxuq8UwgiSs`) ya no existe (23 oct 2026): no lo publiques. Para el tablero de TV:
1. Artifact `read` del `url` (sin `path`) para que cuente como leído.
2. Artifact `publish` con ese `url`, el `file_path` de la tabla (**nunca** el archivo que guarda el read: ese trae la envoltura del visor y se duplicaría) y `files`:
   - `"data.json": "<REPO>/data.json"`
   - por cada foto nueva: `"eventos/x.jpg": {"artifact": "https://claude.ai/artifact/N15fPuqdapJp7YvSRH2Nxb", "path": "eventos/x.jpg"}`
   - por cada ruta de `fotos_quitar`: `null`
   Si el publish pide leer archivos antes, lista los archivos del artefacto (`list`, `scope: "files"`) y vuelve a publicar.

Las pantallas toman el nuevo `data.json` en menos de 5 minutos, sin recargar.

## 6. Informe final
Una línea por cambio publicado (por ejemplo: "Resultados → día 22 oct · Avisos (5) · Tema del mes → nov"). Si algo falló, di qué fuente y por qué; no inventes datos.
