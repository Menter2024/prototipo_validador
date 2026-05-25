#!/usr/bin/env python3
"""Descarga o releva candidatos de fuentes fiscales configuradas."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.modules import descarga_fuentes  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga controlada de fuentes fiscales.")
    parser.add_argument("fuente_id", help="ID de config/fuentes_catalogo.json")
    parser.add_argument("--evidencias-dir", default="./salidas/evidencias/fuentes")
    parser.add_argument("--download", action="store_true", help="Descargar archivo; por defecto solo releva candidato.")
    args = parser.parse_args()

    resultado = descarga_fuentes.ejecutar_descarga(
        args.fuente_id,
        Path(args.evidencias_dir).resolve(),
        dry_run=not args.download,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
