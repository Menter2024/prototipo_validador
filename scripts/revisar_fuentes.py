#!/usr/bin/env python3
"""Revisa el catálogo de fuentes fiscales y emite alertas para schedulers."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.modules import fuentes_catalogo  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Control operativo de fuentes fiscales.")
    parser.add_argument("--padrones-dir", default="./padrones")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()

    estado = fuentes_catalogo.evaluar_fuentes(Path(args.padrones_dir).resolve())
    if args.json:
        print(json.dumps(estado, ensure_ascii=False, indent=2))
    else:
        resumen = estado["resumen"]
        print(
            f"Fuentes: {resumen['total_fuentes']} · "
            f"alertas: {resumen['alertas']} · "
            f"críticas: {resumen['criticas']} · altas: {resumen['altas']} · medias: {resumen['medias']}"
        )
        for alerta in estado["alertas"]:
            print(f"- [{alerta['riesgo']}] {alerta['nombre']}: {alerta['accion']}")
    return 2 if args.fail_on_critical and estado["resumen"]["criticas"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
