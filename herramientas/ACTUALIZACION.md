# Actualización automática del tablero

La tarea programada (6:45, 7:25 y 17:45, hora del centro de México) sigue estos pasos. **Solo publica cuando algo cambió.**

## 0. Preparar
- Repositorio clonado en `REPO` (por ejemplo `/home/claude/Tablero-Aranzazu`). Trabaja siempre ahí.
- Carpeta temporal para fuentes: `FUENTES=/tmp/fuentes` (créala).
- Fecha de hoy en America/Mexico_City → `HOY` (AAAA-MM-DD).

## 1. Descargar fuentes (solo lectura, nunca modificar los originales)
1. **Resultados operativos**: con Microsoft 365 `sharepoint_search` busca `DesaProd` (xlsx) y toma el `Reporte_<Mes>_DesaProd <año>.xlsx` modificado más recientemente (hoy: `Reporte_Octubre_DesaProd 2026.xlsx`, uri `file:///b!FZeGuCKJckKNup0XdY6V_vvupZKY1mZGlNF7ZrWKU2FwEEfxXPYCSKRZgxtDJIGm/0177JFFE3AW357ZH22DFA3HCXX4SRDWLLW`). Léelo completo con `read_resource` **sin** startPage/endPage: el resultado es grande y se guarda en un archivo; usa esa ruta como `--libro`. Si el resultado llega en línea, guárdalo tal cual en `$FUENTES/libro.txt` (debe incluir el bloque `## Sheet: Resumen`). Solo se usa la hoja **Resumen**.
2. **Avisos**: `read_resource` de `file:///b!Bza5sahU602uuqM08-zTWI6bkkAClr1GrNJV-zb2vLRGO5ByzSSyRrQAsRh48i1m/Tablero/Avisos.xlsx`. Guarda el texto tal cual en `$FUENTES/avisos.txt`. Solo cuenta la **columna B** con texto.
3. **Tablero RH** (eventos y base de datos): Artifact `read` de `https://claude.ai/artifact/N15fPuqdapJp7YvSRH2Nxb`. El resultado indica el archivo local donde guardó la página completa: úsalo como `--rh`.

## 2. Calcular cambios
```
cd $REPO
python3 herramientas/actualizar.py --rh <rh.html> --libro <libro.txt> --archivo-libro "<nombre del xlsx>" --avisos $FUENTES/avisos.txt --hoy $HOY
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

## 5. Publicar en los tableros de claude.ai (solo si `cambios` no está vacía)
Primero genera las páginas limpias: `python3 herramientas/build_artefactos.py` (crea `herramientas/artefactos/tv.html` y `movil.html`; inclúyelas en el commit del paso 4).

| Tablero | url | file_path |
|---|---|---|
| TV | `https://claude.ai/artifact/1bXCkxbXbZb3BX752mhAn5` | `<REPO>/herramientas/artefactos/tv.html` |
| Celular | `https://claude.ai/artifact/7AfrvoektHiDxuq8UwgiSs` | `<REPO>/herramientas/artefactos/movil.html` |

Para cada uno:
1. Artifact `read` del `url` (sin `path`) para que cuente como leído.
2. Artifact `publish` con ese `url`, el `file_path` de la tabla (**nunca** el archivo que guarda el read: ese trae la envoltura del visor y se duplicaría) y `files`:
   - `"data.json": "<REPO>/data.json"`
   - por cada foto nueva: `"eventos/x.jpg": {"artifact": "https://claude.ai/artifact/N15fPuqdapJp7YvSRH2Nxb", "path": "eventos/x.jpg"}`
   - por cada ruta de `fotos_quitar`: `null`
   Si el publish pide leer archivos antes, lista los archivos del artefacto (`list`, `scope: "files"`) y vuelve a publicar.

Las pantallas toman el nuevo `data.json` en menos de 5 minutos, sin recargar.

## 6. Informe final
Una línea por cambio publicado (por ejemplo: "Resultados → día 22 oct · Avisos (5) · Tema del mes → nov"). Si algo falló, di qué fuente y por qué; no inventes datos.
