#!/usr/bin/env python3
"""Puerta de proceso: una tarea NO se cierra sin su ronda de revisión.

Por qué existe (LEC-006: un gate que ninguna puerta ejecuta es una declaración):
la regla dice que una tarea se cierra con la revisión independiente de los
subagentes y que su confirmación queda registrada en `docs/LOG-PROCESO.md` ("si
no está en el log, no hay confirmación"). Sin esta puerta depende de que el
agente se acuerde: en el piloto se saltó más de una vez.

Esta puerta lo comprueba de forma mecánica:
  * mira las tareas que el commit MARCA como hechas (`- [x]`) en los changes;
  * para cada una, exige una fila de tipo «revisión» en el log que la cite (el
    id de la tarea y el del cambio), esté CERRADA y mencione a un subagente;
  * desde `revision.corte_fuente` (2026-10-23 por defecto), la fila debe citar
    además `subagente <id>` (no basta el nombre del subagente: eso era
    auto-atestación);
  * una fila malformada no se ignora: se rechaza y se dice qué línea es.

Inactivación declarada: si el proyecto NO tiene el log, la puerta lo dice (aviso
explícito con la cabecera para crearlo) y pasa — ese archivo es el interruptor.
Y si el log está en el árbol de trabajo pero NO en el índice, la puerta FALLA
diciendo que hay que versionarlo: una confirmación que no viaja con el commit
no está en el log. Nunca se aprueba en silencio.

Configuración (`sgp.yaml`, todas opcionales; actúan los valores por defecto):
    rutas:
      cambios: changes
      log_proceso: docs/LOG-PROCESO.md
    revision:
      corte_fuente: 2026-10-23
      subagentes: senior-reviewer, independent-verifier, docs-syncer

Exenciones: tareas cerradas antes de instalar la puerta se listan en
`tools/revisiones-baseline.txt` (una por línea, `CHG-NNN TNNN`; con `#` se comenta).

Uso:  python tools/sgp_review.py [--root RAIZ]
Devuelve 1 (y explica qué falta) si hay una tarea cerrada sin su ronda.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import sgp_check

LOG_DEFECTO = "docs/LOG-PROCESO.md"
CORTE_DEFECTO = "2026-10-23"
SUBAGENTES_DEFECTO = "senior-reviewer, independent-verifier, docs-syncer"
# Tareas cerradas ANTES de que existiera esta puerta: no se vuelven a pedir (la
# línea base vive en `tools/revisiones-baseline.txt`; la puerta solo vigila lo de
# aquí en adelante, que es lo que se puede corregir).
RUTA_BASE = "tools/revisiones-baseline.txt"

# Una fila del log tiene 6 columnas: | fecha | # | tipo | qué | estado | referencia |.
# Los pipes dentro del texto van escapados como `\|` (los escribe quien añade la
# fila); el parser los respeta y no los confunde con separadores de columna.
CAMPOS = 6
ESTADOS_CIERRE = ("cerrada", "cerrado", "hecha", "resuelta", "aprobada", "cumplida")
FUENTE_RE = re.compile(r"subagente\s*:?\s*[A-Za-z0-9_.:-]+", re.IGNORECASE)
CABECERA_LOG = ("| Fecha | # | Tipo | Qué | Estado | Referencia |\n"
                "|---|---|---|---|---|---|")


class FilaMalformada(ValueError):
    """Una fila de la tabla del log no se puede leer con seguridad."""


def leer_config(raiz: Path) -> dict:
    """Valores de `sgp.yaml` que usa la puerta, con sus defectos.

    Reutiliza el lector del verificador: una sola gramática de `sgp.yaml` en el
    kit. Solo se lleva las claves que aquí se consultan.
    """
    cfg, _ = sgp_check.read_config(raiz)
    return {
        "cambios": cfg.get("cambios") or "changes",
        "log": cfg.get("log_proceso") or LOG_DEFECTO,
        "corte": cfg.get("corte_fuente") or CORTE_DEFECTO,
        "subagentes": [s.strip() for s in
                       (cfg.get("subagentes") or SUBAGENTES_DEFECTO).split(",") if s.strip()],
    }


def linea_base(raiz: Path) -> set:
    """Las tareas ya cerradas antes de la puerta (exentas)."""
    ruta = raiz / RUTA_BASE
    if not ruta.exists():
        return set()
    tareas = set()
    for linea in ruta.read_text(encoding="utf-8").split("\n"):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        tareas.add(linea)
    return tareas


def contenido_indexado(raiz: Path, ruta: str, rev=None) -> str:
    """El contenido de un fichero: del índice (staged) o del commit indicado."""
    args = ["git", "show", (f"{rev}:" if rev else ":") + ruta]
    res = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", cwd=str(raiz))
    return res.stdout if res.returncode == 0 else ""


def ficheros_cambiados(raiz: Path, patron: str) -> list:
    res = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", patron],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(raiz), check=True,
    )
    return [line.strip() for line in res.stdout.split("\n") if line.strip()]


def tareas_por_id(texto: str) -> dict:
    """id de tarea -> línea completa (las tareas `- [x] T123 ...`)."""
    tareas = {}
    for linea in texto.split("\n"):
        m = re.match(r"^\s*-\s*\[( |x|X)\]\s*(T\d+[a-z]?)\b", linea)
        if m:
            tareas[m.group(2)] = linea
    return tareas


def _celdas(linea: str) -> list:
    """Celdas de una fila markdown; `\\|` es un pipe literal, no un separador."""
    partes = re.split(r"(?<!\\)\|", linea.strip().strip("|"))
    return [p.replace("\\|", "|").strip() for p in partes]


def parse_fila_log(linea: str):
    """Devuelve la fila de revisión, None si no es una fila, o falla si está rota.

    No se ignoran las filas malformadas: una fila de tipo revisión con distinto
    número de columnas es un error, no un silencio (era el agujero que dejaba
    pasar R18 y R6 en el piloto). Los pipes del texto deben ir escapados.
    """
    if not linea.lstrip().startswith("|"):
        return None
    celdas = _celdas(linea)
    if len(celdas) < 3:
        return None
    if not celdas[2].lower().startswith("revisi"):
        return None
    if len(celdas) != CAMPOS:
        raise FilaMalformada(
            f"fila de revisión con {len(celdas)} columnas (se esperan {CAMPOS}); "
            f"usa `\\|` para los pipes dentro del texto: {linea.strip()[:120]}"
        )
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", celdas[0]):
        raise FilaMalformada(
            f"fila de revisión con fecha inválida '{celdas[0]}' (se espera YYYY-MM-DD): "
            f"{linea.strip()[:120]}"
        )
    return {
        "fecha": celdas[0],
        "id": celdas[1],
        "tipo": celdas[2],
        "que": celdas[3],
        "estado": celdas[4],
        "ref": celdas[5],
        "linea": linea.strip(),
    }


def filas_de_revision(log: str) -> list:
    """Filas de revisión del log. Falla si alguna está malformada."""
    filas = []
    for n, linea in enumerate(log.split("\n"), 1):
        try:
            fila = parse_fila_log(linea)
        except FilaMalformada as exc:
            raise FilaMalformada(f"línea {n}: {exc}") from exc
        if fila:
            filas.append(fila)
    return filas


def es_cierre(estado: str) -> bool:
    """Una revisión solo cuenta si su estado es de cierre, no 'pendiente'."""
    return estado.strip().lower().startswith(ESTADOS_CIERRE)


def fuente_ok(fila: dict, corte: str) -> bool:
    """Desde el corte, la fila debe citar `subagente <id>`."""
    if fila["fecha"] < corte:
        return True
    return bool(FUENTE_RE.search(fila["que"] + " " + fila["ref"]))


def revisar(raiz: Path, cfg: dict) -> int:
    cambios = ficheros_cambiados(raiz, f"{cfg['cambios']}/*.md")
    if not cambios:
        print("[revisión] este commit no toca changes/: nada que comprobar.")
        return 0

    log_ruta = cfg["log"]
    log_staged = contenido_indexado(raiz, log_ruta, None)
    if not log_staged:
        if (raiz / log_ruta).exists():
            print(f"[revisión] FALLA: {log_ruta} existe pero NO está en el índice; "
                  "la confirmación no viaja con el commit.")
            print(f"  Versiónalo primero:  git add {log_ruta}")
            return 1
        print(f"[revisión] AVISO: no existe {log_ruta}: la puerta de revisión está "
              "INACTIVA para este proyecto.")
        print("  Si este proyecto cierra tareas con revisión, crea el archivo con "
              "esta cabecera:")
        for linea in CABECERA_LOG.split("\n"):
            print(f"    {linea}")
        print("  (si no está en el log, no hay confirmación).")
        return 0

    try:
        revisiones = filas_de_revision(log_staged)
    except FilaMalformada as exc:
        print(f"[revisión] FALLA: no se puede leer el log: {exc}")
        return 1

    corte = cfg["corte"]
    subagentes = cfg["subagentes"]
    exentas = linea_base(raiz)
    faltantes = []
    for cambio in cambios:
        texto_staged = contenido_indexado(raiz, cambio, None)
        texto_head = contenido_indexado(raiz, cambio, "HEAD")
        tareas_staged = tareas_por_id(texto_staged)
        tareas_head = tareas_por_id(texto_head)
        # Las tareas que este commit cierra (marcadas aquí y no antes).
        cerradas = [
            (tid, linea)
            for tid, linea in tareas_staged.items()
            if re.match(r"^\s*-\s*\[x\]", linea)
            and not re.match(r"^\s*-\s*\[x\]", tareas_head.get(tid, ""))
        ]
        if not cerradas:
            continue
        id_cambio = re.search(r"^id:\s*(CHG-\d+)", texto_staged, re.MULTILINE)
        id_cambio = id_cambio.group(1) if id_cambio else ""
        for tid, _linea in cerradas:
            if f"{id_cambio} {tid}" in exentas:
                continue
            citadas = [
                fila for fila in revisiones
                if tid in (fila["que"] + " " + fila["ref"])
                and (not id_cambio or id_cambio in (fila["que"] + " " + fila["ref"]))
            ]
            if not citadas:
                faltantes.append(f"{cambio}: {tid} se marca como hecha sin fila de "
                                 f"revisión en {log_ruta}")
                continue
            cerradas_filas = [fila for fila in citadas if es_cierre(fila["estado"])]
            if not cerradas_filas:
                estados = ", ".join(sorted({fila["estado"] for fila in citadas}))
                faltantes.append(
                    f"{cambio}: la fila de revisión de {tid} está pendiente "
                    f"(estado: {estados}); no cuenta como revisión"
                )
                continue
            fila = cerradas_filas[0]
            if not any(s in fila["que"] for s in subagentes):
                faltantes.append(
                    f"{cambio}: la fila de revisión de {tid} no menciona a ningún "
                    f"subagente ({', '.join(subagentes)})"
                )
            elif not fuente_ok(fila, corte):
                faltantes.append(
                    f"{cambio}: la fila de revisión de {tid} no cita `subagente <id>` "
                    f"(obligatorio desde {corte})"
                )
            else:
                for otro in subagentes:
                    if otro not in fila["que"]:
                        print(f"[revisión] aviso: la fila de {tid} no menciona a "
                              f"«{otro}».")

    if faltantes:
        print("[revisión] FALLA: hay tareas cerradas sin su ronda de revisión:")
        for f in faltantes:
            print(f"  - {f}")
        print(f"  (una tarea se cierra con {', '.join(subagentes)} y su confirmación "
              f"queda en {log_ruta}:")
        print("   fila de tipo «revisión» CERRADA, que cite la tarea y el cambio,")
        print(f"   y desde {corte} cite `subagente <id>`).")
        return 1

    print("[revisión] OK: toda tarea cerrada por este commit tiene su fila de "
          "revisión cerrada.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Puerta: ninguna tarea se cierra sin su ronda de revisión.")
    ap.add_argument("--root", default=".",
                    help="raíz del proyecto (por defecto, el directorio actual)")
    args = ap.parse_args()
    raiz = Path(args.root).resolve()
    return revisar(raiz, leer_config(raiz))


if __name__ == "__main__":
    sys.exit(main())
