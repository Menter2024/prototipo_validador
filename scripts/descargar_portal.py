"""Ejecuta adaptadores Playwright para portales fiscales oficiales."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules import portal_automation  # noqa: E402


def _vars(args) -> dict:
    variables = {}
    for item in args.var or []:
        if "=" not in item:
            raise SystemExit(f"--var inválido: {item}. Usá clave=valor.")
        k, v = item.split("=", 1)
        variables[k] = v
    if args.periodo:
        variables["periodo"] = args.periodo
        variables.setdefault("periodo_slash", args.periodo.replace("-", "/"))
    if args.periodo_slash:
        variables["periodo_slash"] = args.periodo_slash
    if args.vigencia_text:
        variables["vigencia_text"] = args.vigencia_text
    if args.cuit:
        variables["cuit"] = args.cuit
    return variables


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga/captura evidencia de portales fiscales oficiales con Playwright.")
    parser.add_argument("adapter_id", help="ID en config/portal_adapters.json")
    parser.add_argument("--periodo", help="Período ISO, ej. 2026-06")
    parser.add_argument("--periodo-slash", help="Período para formularios, ej. 2026/06")
    parser.add_argument("--vigencia-text", help="Texto de vigencia visible, ej. 01/06/2026")
    parser.add_argument("--cuit", help="CUIT para consultas por sujeto")
    parser.add_argument("--var", action="append", help="Variable adicional clave=valor")
    parser.add_argument("--output-dir", type=Path, default=portal_automation.DEFAULT_OUTPUT_DIR)
    parser.add_argument("--adapters", type=Path, default=portal_automation.DEFAULT_ADAPTERS)
    parser.add_argument("--headed", action="store_true", help="Abre navegador visible")
    parser.add_argument("--allow-authenticated", action="store_true", help="Permite ejecutar adaptadores que requieren login autorizado")
    parser.add_argument("--allow-captcha", action="store_true", help="Sólo para evidencia manual; no resuelve CAPTCHA automáticamente")
    parser.add_argument("--storage-state", type=Path, help="Archivo storage_state de Playwright fuera del repo")
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--dry-run", action="store_true", help="Muestra plan sin abrir navegador")
    args = parser.parse_args()

    try:
        res = portal_automation.ejecutar_adapter(
            args.adapter_id,
            variables=_vars(args),
            adapters_path=args.adapters,
            output_dir=args.output_dir,
            headless=not args.headed,
            allow_authenticated=args.allow_authenticated,
            allow_captcha=args.allow_captcha,
            storage_state_path=args.storage_state,
            timeout_ms=args.timeout_ms,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
