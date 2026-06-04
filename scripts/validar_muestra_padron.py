#!/usr/bin/env python3
"""Valida una muestra oficial real de padrón sin modificar padrones locales."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.importar_padron import importar_padron  # noqa: E402

EXPECTED_LAYOUTS = {
    "ARBA": "arba_iibb_sujeto_csv_v1",
    "CABA": "agip_caba_regimenes_generales_v1",
    "AGIP": "agip_caba_regimenes_generales_v1",
    "EntreRios": "ater_entrerios_iibb_csv_v1",
    "ATER": "ater_entrerios_iibb_csv_v1",
    "SantaFe": "santafe_iibb_csv_v1",
    "Cordoba": "cordoba_iibb_delimitado_v1",
    "Jujuy": "jujuy_iibb_xlsx_alias_v1",
    "Mendoza": "mendoza_iibb_csv_alias_v1",
    "Tucuman": "tucuman_iibb_rg23_csv_v1",
}


def validar_muestra(
    provincia: str,
    origen: Path,
    expected_layout: str | None = None,
    min_registros: int = 1,
    sheet: str | None = None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="padron_validacion_") as tmp:
        resultado = importar_padron(
            provincia,
            origen,
            Path(tmp) / "padrones",
            sheet=sheet,
            dry_run=True,
            backup=False,
            aceptar_observado=True,
        )
    calidad = resultado["calidad"]
    layout_detectado = calidad.get("layout_detectado") or resultado["evidencia"].get("layout_detectado", "")
    esperado = expected_layout or EXPECTED_LAYOUTS.get(provincia, "")
    errores = []
    advertencias = list(calidad.get("advertencias", []))

    if calidad.get("estado") == "bloqueado":
        errores.extend(calidad.get("errores", []))
    if resultado["registros"] < min_registros:
        errores.append(f"Registros válidos {resultado['registros']} menor al mínimo requerido {min_registros}.")
    if esperado and layout_detectado != esperado:
        errores.append(f"Layout detectado '{layout_detectado}' no coincide con esperado '{esperado}'.")
    if not resultado["evidencia"].get("sha256"):
        errores.append("No se pudo calcular hash SHA-256 de evidencia.")

    return {
        "ok": not errores,
        "provincia": resultado["provincia"],
        "origen": resultado["origen"],
        "registros": resultado["registros"],
        "layout_detectado": layout_detectado,
        "layout_esperado": esperado,
        "sha256": resultado["evidencia"].get("sha256", ""),
        "tamano_bytes": resultado["evidencia"].get("tamano_bytes", 0),
        "calidad": calidad,
        "muestra": resultado["muestra"],
        "errores": errores,
        "advertencias": advertencias,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida una muestra oficial real sin escribir padrones locales.")
    parser.add_argument("provincia", help="ARBA, CABA/AGIP, EntreRios/ATER, SantaFe, Cordoba, Jujuy, Mendoza, Tucuman")
    parser.add_argument("origen", type=Path, help="Archivo oficial descargado: CSV/TXT/XLSX/ZIP/RAR")
    parser.add_argument("--expected-layout", help="Layout esperado; si se omite se usa el esperado por provincia.")
    parser.add_argument("--min-registros", type=int, default=1)
    parser.add_argument("--sheet", help="Hoja XLSX si aplica")
    parser.add_argument("--output", type=Path, help="Guardar reporte JSON")
    args = parser.parse_args()

    reporte = validar_muestra(args.provincia, args.origen, args.expected_layout, args.min_registros, args.sheet)
    rendered = json.dumps(reporte, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0 if reporte["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
