#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sencillo para limpiar archivos viejos.
Hecho para práctica (2º DAM). No usar en rutas críticas.
"""

import argparse
import os
import sys
import shutil
import fnmatch
from datetime import datetime, timedelta
from pathlib import Path

RUTAS_PELIGROSAS = {Path('/'), Path('C:\\'), Path.home()}

def es_ruta_peligrosa(p: Path) -> bool:
    p = p.resolve()
    if p in RUTAS_PELIGROSAS:
        return True
    if p.anchor and len(p.parts) <= 2:
        return True
    return False

def parsear_argumentos():
    ap = argparse.ArgumentParser(description="Limpia archivos por edad/extensión/patrón. Simulación por defecto.")
    ap.add_argument("--path", required=True, help="Ruta ABSOLUTA a la carpeta objetivo.")
    ap.add_argument("--extensions", help="Extensiones separadas por comas, ej: .log,.tmp")
    ap.add_argument("--pattern", help="Patrón tipo '*.bak' (se aplica además de extensiones).")
    ap.add_argument("--older-than", type=int, default=0, help="Solo afecta archivos con más de N días (0 = ignora edad).")
    ap.add_argument("--keep", type=int, default=0, help="Mantener N archivos más nuevos por carpeta.")
    ap.add_argument("--exclude", action="append", default=[], help="Rutas absolutas a excluir.")
    ap.add_argument("--trash", help="Si se indica, mueve aquí en vez de borrar (se crean subcarpetas).")
    ap.add_argument("--confirm", action="store_true", help="Si lo pones, ejecuta de verdad. Si no, solo simula.")
    return ap.parse_args()

def coincide(f: Path, exts, patron) -> bool:
    if exts and f.suffix.lower() not in exts:
        return False
    if patron and not fnmatch.fnmatch(f.name, patron):
        return False
    return True

def main():
    args = parsear_argumentos()
    raiz = Path(args.path).expanduser().resolve()
    if not raiz.is_absolute():
        print("ERROR: --path debe ser absoluto", file=sys.stderr)
        sys.exit(2)
    if not raiz.exists() or not raiz.is_dir():
        print(f"ERROR: la ruta no existe o no es carpeta: {raiz}", file=sys.stderr)
        sys.exit(2)
    if es_ruta_peligrosa(raiz):
        print(f"RUTA BLOQUEADA por seguridad: {raiz}", file=sys.stderr)
        sys.exit(2)

    exts = None
    if args.extensions:
        exts = set()
        for e in args.extensions.split(","):
            e = e.strip()
            if not e:
                continue
            if not e.startswith("."):
                e = "." + e
            exts.add(e.lower())

    limite = datetime.now() - timedelta(days=args.older_than) if args.older_than > 0 else None

    excluidas = [Path(p).resolve() for p in args.exclude]
    def esta_excluida(p: Path) -> bool:
        rp = p.resolve()
        return any(str(rp).startswith(str(ex)) for ex in excluidas)

    papelera = Path(args.trash).resolve() if args.trash else None
    if papelera:
        papelera.mkdir(parents=True, exist_ok=True)

    plan = []
    for dirpath, _, filenames in os.walk(raiz):
        carpeta = Path(dirpath)
        if esta_excluida(carpeta):
            continue
        candidatos = []
        for nombre in filenames:
            f = carpeta / nombre
            if esta_excluida(f):
                continue
            if not coincide(f, exts, args.pattern):
                continue
            if limite:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > limite:
                    continue
            candidatos.append(f)
        if args.keep > 0 and len(candidatos) > args.keep:
            candidatos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            candidatos = candidatos[args.keep:]
        plan.extend(candidatos)

    accion = "MOVER a papelera" if papelera else "BORRAR"
    print(f"\n== Plan ==")
    print(f"Carpeta: {raiz}")
    print(f"Acción: {accion}")
    print(f"Coincidencias: {len(plan)} archivo(s)")
    for f in plan[:30]:
        print(" -", f)
    if not args.confirm:
        print("\nSimulación activa (no se hace nada). Añade --confirm para ejecutar.")
        return

    hechos = 0
    for f in plan:
        try:
            if papelera:
                rel = f.relative_to(raiz)
                destino = papelera / rel
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), str(destino))
            else:
                f.unlink(missing_ok=True)
            hechos += 1
        except Exception as e:
            print(f"[error] No se pudo procesar {f}: {e}", file=sys.stderr)

    print(f"\nListo. {hechos} archivo(s) procesados.")

if __name__ == "__main__":
    main()
