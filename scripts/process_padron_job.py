#!/usr/bin/env python3
"""Worker Cloud Run Job para procesar una carga async de padrón."""
from __future__ import annotations

import csv
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules import supabase_mvp  # noqa: E402
from app.modules.padrones import PADRONES_PROVINCIAS, _normalizar_row  # noqa: E402
from scripts.importar_padron import importar_padron  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _iter_normalizados(path: Path):
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


def _indexar_rows(job: dict[str, Any], version_id: str, normalizado: Path, batch_size: int) -> int:
    total = 0
    batch = []
    for row in _iter_normalizados(normalizado):
        batch.append({
            "padron_version_id": version_id,
            "tenant_id": job["tenant_id"],
            "jurisdiccion": job["provincia"],
            **row,
        })
        if len(batch) >= batch_size:
            supabase_mvp.insert_rows("padron_registros_demo", batch)
            total += len(batch)
            batch = []
            supabase_mvp.update_padron_import_job(job["id"], {
                "estado": "indexando",
                "registros_insertados": total,
            })
    if batch:
        supabase_mvp.insert_rows("padron_registros_demo", batch)
        total += len(batch)
    return total


def process_padron_import_job(job_id: str, work_dir: Path | None = None) -> dict[str, Any]:
    job = supabase_mvp.get_padron_import_job(job_id)
    if not job:
        raise RuntimeError(f"No existe padron_import_job: {job_id}")
    if job.get("estado") not in {"upload_completo", "pendiente_proceso", "fallido", "procesando"}:
        raise RuntimeError(f"Estado no procesable: {job.get('estado')}")
    cfg = PADRONES_PROVINCIAS.get(job["provincia"], {})
    if cfg.get("tipo") != "archivo":
        raise RuntimeError(f"Provincia no importable por archivo: {job['provincia']}")

    base = work_dir or Path(tempfile.mkdtemp(prefix="padron_job_"))
    original = base / "original" / (job.get("archivo_nombre") or f"{job_id}.dat")
    out_dir = base / "normalizado"
    supabase_mvp.update_padron_import_job(job_id, {"estado": "procesando", "iniciado_en": _now()})

    try:
        descarga = supabase_mvp.download_file(job["storage_original_path"], original)
        resultado = importar_padron(
            job["provincia"],
            original,
            out_dir,
            None,
            False,
            job.get("periodo") or None,
            job.get("vigencia_hasta") or None,
            backup=False,
            aceptar_observado=True,
        )
        normalizado = Path(resultado["destino"])
        remote_norm = supabase_mvp.storage_path(
            supabase_mvp.get_config().tenant_slug,
            "padrones",
            job["provincia"],
            job.get("periodo") or "sin-periodo",
            "normalizado",
            job_id,
            normalizado.name,
        )
        upload_norm = supabase_mvp.upload_file(normalizado, remote_norm, content_type="text/csv", upsert=True)
        estado_calidad = resultado.get("calidad", {}).get("estado", "")
        version = supabase_mvp.insert_row("padron_versiones", {
            "tenant_id": job["tenant_id"],
            "provincia": job["provincia"],
            "fuente_id": job.get("fuente_id"),
            "periodo": job.get("periodo") or "",
            "vigencia_hasta": job.get("vigencia_hasta"),
            "registros": int(resultado.get("registros") or 0),
            "estado": "pendiente_validacion" if estado_calidad != "bloqueado" else "rechazado",
            "storage_original_path": job["storage_original_path"],
            "storage_normalizado_path": remote_norm,
            "sha256_original": descarga.get("sha256", ""),
            "sha256_normalizado": upload_norm.get("sha256", ""),
            "calidad": resultado.get("calidad") or {},
            "evidencia": {
                "job_id": job_id,
                "download": descarga,
                "normalizado": upload_norm,
                "modo": "cloud_run_job",
            },
            "import_job_id": job_id,
        })
        version_id = (version.get("data") or [{}])[0].get("id")
        insertados = 0
        if os.environ.get("PADRON_JOB_INDEX_ROWS", "false").lower() in {"1", "true", "yes"} and version_id:
            insertados = _indexar_rows(job, version_id, normalizado, int(os.environ.get("PADRON_IMPORT_BATCH_SIZE", "1000")))
        final_estado = "observado" if estado_calidad == "observado" else "completado"
        patch = {
            "estado": final_estado,
            "storage_normalizado_path": remote_norm,
            "sha256_original": descarga.get("sha256", ""),
            "sha256_normalizado": upload_norm.get("sha256", ""),
            "registros_raw": int(resultado.get("calidad", {}).get("raw_registros") or 0),
            "registros_validos": int(resultado.get("registros") or 0),
            "registros_insertados": insertados,
            "calidad": resultado.get("calidad") or {},
            "advertencias": resultado.get("calidad", {}).get("advertencias") or [],
            "errores": resultado.get("calidad", {}).get("errores") or [],
            "finalizado_en": _now(),
        }
        supabase_mvp.update_padron_import_job(job_id, patch)
        return {"ok": True, "job_id": job_id, "estado": final_estado, "version_id": version_id, **patch}
    except Exception as exc:
        supabase_mvp.update_padron_import_job(job_id, {
            "estado": "fallido",
            "errores": [str(exc)],
            "finalizado_en": _now(),
        })
        raise


def main() -> int:
    job_id = os.environ.get("PADRON_IMPORT_JOB_ID", "").strip()
    if not job_id:
        raise SystemExit("Falta PADRON_IMPORT_JOB_ID")
    result = process_padron_import_job(job_id)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
