"""Manifiesto e historial de cargas de padrones."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, date
from pathlib import Path

MANIFEST = "padrones_manifest.json"
BACKUP_DIR = "backups"


def _manifest_path(padrones_dir: Path) -> Path:
    return padrones_dir / MANIFEST


def cargar_manifest(padrones_dir: Path) -> dict:
    path = _manifest_path(padrones_dir)
    if not path.exists():
        return {"version": 1, "padrones": {}, "historial": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "padrones": {}, "historial": []}


def guardar_manifest(padrones_dir: Path, manifest: dict) -> None:
    padrones_dir.mkdir(parents=True, exist_ok=True)
    _manifest_path(padrones_dir).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def backup_si_existe(archivo: Path) -> str | None:
    if not archivo.exists():
        return None
    backup_dir = archivo.parent / BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"{archivo.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{archivo.suffix}"
    shutil.copy2(archivo, backup)
    return str(backup)


def registrar_carga(padrones_dir: Path, provincia: str, archivo: str, registros: int, origen: str, periodo: str | None, vigencia_hasta: str | None, backup: str | None) -> dict:
    manifest = cargar_manifest(padrones_dir)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = {
        "provincia": provincia,
        "archivo": archivo,
        "registros": registros,
        "origen": origen,
        "periodo": periodo or "",
        "vigencia_hasta": vigencia_hasta or "",
        "backup": backup,
        "cargado_en": now,
    }
    manifest.setdefault("padrones", {})[provincia] = item
    manifest.setdefault("historial", []).insert(0, item)
    manifest["historial"] = manifest["historial"][:100]
    guardar_manifest(padrones_dir, manifest)
    return item


def _parse_fecha(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def estado_vigencia(vigencia_hasta: str | None) -> str:
    hasta = _parse_fecha(vigencia_hasta)
    if not hasta:
        return "sin_vigencia"
    delta = (hasta - date.today()).days
    if delta < 0:
        return "vencido"
    if delta <= 7:
        return "por_vencer"
    return "vigente"
