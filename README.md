# Tablero Informativo Aranzazu · CoMinVi

Cartelera digital para las pantallas de la Unidad Aranzazu (Informativa, Mina, RH y Oficinas).

| Página | Para qué |
|---|---|
| `index.html` | Tablero completo 16:9 para TV. Se ajusta al tamaño de cualquier pantalla. |
| `data.json` | **Todos los datos del tablero.** Las pantallas lo vuelven a leer cada 5 minutos. |
| `eventos/` | Fotos del carrusel de eventos. |

## Cómo actualizar los datos (sin programar)

1. En GitHub abre `data.json` y pulsa el lápiz (**Edit this file**).
2. Cambia solo los números o textos que necesites. Secciones principales:
   - `seguridad.fechaUltimoAccidente`: fecha del último accidente con tiempo perdido (`AAAA-MM-DD`). Los días se cuentan solos.
   - `seguridad.ccrm`: reporte diario de CCRM (total y niveles gerentes, supervisores, operadores; `pctProgramado`).
   - `resultados`: hoja *Resumen* del reporte de Desarrollo y Producción (día y acumulado del mes).
   - `eventosFotos`: fotos del carrusel (la imagen va en `eventos/`).
   - `personal`: base de cumpleaños (`cumpleanos` = `MM-DD`).
   - `cultura`: textos de Misión, Visión y Ética (`**texto**` se resalta en dorado).
   - `avisosTicker`: frases de la cintilla de avisos.
   - `clima.dias`: pronóstico diario de Concepción del Oro.
3. Pulsa **Commit changes**. En 1 a 2 minutos GitHub publica el sitio y las TVs toman los datos nuevos en menos de 5 minutos, sin recargar.

## Publicación automática

Cada cambio en la rama `main` ejecuta `.github/workflows/pages.yml`, que reconstruye `index.html` con el `data.json` actual y publica en GitHub Pages.

Activación (una sola vez): **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Actualización automática

La tarea programada **Tablero INFORMATIVO Aranzazu** corre a las **6:45, 8:45 y 18:45** (hora del centro de México) y publica solo si algo cambió:

| Sección | Fuente |
|---|---|
| Resultados operativos | `Reporte_<Mes>_DesaProd <año>.xlsx` (OneDrive de Gibrán Ochoa, `Desarrollo`), hoja **Resumen** |
| Eventos (3 más recientes, máx. 8 fotos c/u) | Tablero RH Aranzazu, módulo Eventos |
| Cumpleaños del mes | Tablero RH Aranzazu, módulo Base de datos |
| Avisos | `Tablero/Avisos.xlsx`, columna **B** (solo celdas con texto) |
| CCRM | `CCRM DIARIO (<MES> <AÑO>).xlsx`, hoja **CCRM**, bloque "CCRM AL DIA" más reciente |
| Tema del mes | Calendario de temas (octubre rosa, noviembre Día de Muertos, etc.) |

Los pasos están en `herramientas/ACTUALIZACION.md` y el cálculo en `herramientas/actualizar.py`.

## Herramientas (`herramientas/`)

- `template.html`: diseño del tablero.
- `build.py`: genera `index.html` (`python3 herramientas/build.py`).
- `vendor/`: React y htm incluidos en la página, sin depender de internet.
- `sync_rh.py`: copia cumpleaños y eventos desde el Tablero RH Aranzazu.

## Aviso de privacidad

Este sitio es público en GitHub Pages: cualquiera con la dirección puede ver los nombres, puestos y fechas de cumpleaños del personal, y los resultados operativos.
