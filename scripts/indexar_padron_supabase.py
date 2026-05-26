#!/usr/bin/env python3
"""Indexa un CSV canónico de padrón en Supabase por lotes."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules import supabase_mvp  # noqa: E402
from app.modules.padrones import _normalizar_row  # noqa: E402


def _solo_digitos(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _fecha(value: str) -> str | None:
    value = str(value or "").strip()
    if not value or value == "—":
        return None
    if len(value) == 10 and value[4] == "-":
        return value
    if len(value) == 10 and value[2] in {"/", "-"}:
        return f"{value[6:10]}-{value[3:5]}-{value[0:2]}"
    return None


def _leer_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        for row in csv.DictReader(fh, dialect=dialect):
            normal = _normalizar_row(row)
            cuit = _solo_digitos(normal.get("cuit", ""))
            if len(cuit) != 11:
                continue
            yield {
                "cuit": cuit,
                "regimen": normal.get("regimen", ""),
                "alicuota_retencion": normal.get("alicuota_retencion", ""),
                "alicuota_percepcion": normal.get("alicuota_percepcion", ""),
                "vigencia_desde": _fecha(normal.get("vigencia_desde", "")),
                "vigencia_hasta": _fecha(normal.get("vigencia_hasta", "")),
                "datos": normal,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Indexa padrón normalizado en Supabase")
    parser.add_argument("provincia")
    parser.add_argument("archivo", type=Path)
    parser.add_argument("--periodo", required=True)
    parser.add_argument("--vigencia-hasta", default="")
    parser.add_argument("--fuente-id", default="")
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    if not supabase_mvp.enabled():
        raise SystemExit("Supabase no configurado: cargar SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY")
    if not args.archivo.exists():
        raise SystemExit(f"Archivo no encontrado: {args.archivo}")

    tenant_id = supabase_mvp.tenant_id()
    if not tenant_id:
        raise SystemExit("No pude resolver tenant Supabase")

    version_payload = {
        "tenant_id": tenant_id,
        "provincia": args.provincia,
        "fuente_id": args.fuente_id or None,
        "periodo": args.periodo,
        "vigencia_hasta": args.vigencia_hasta or None,
        "registros": 0,
        "estado": "activo",
        "storage_original_path": "",
        "sha256_original": supabase_mvp.sha256_file(args.archivo),
        "calidad": {"estado": "indexado_desde_csv", "origen": str(args.archivo)},
        "evidencia": {"modo": "indexacion_local", "archivo": args.archivo.name},
    }
    version = supabase_mvp.insert_row("padron_versiones", version_payload)["data"][0]
    version_id = version["id"]

    total = 0
    batch = []
    for row in _leer_rows(args.archivo):
        batch.append({
            "padron_version_id": version_id,
            "tenant_id": tenant_id,
            "jurisdiccion": args.provincia,
            **row,
        })
        if len(batch) >= args.batch_size:
            supabase_mvp.insert_rows("padron_registros_demo", batch)
            total += len(batch)
            print(f"indexados={total}", flush=True)
            batch = []
    if batch:
        supabase_mvp.insert_rows("padron_registros_demo", batch)
        total += len(batch)

    print(f"OK padron_version_id={version_id} registros={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
