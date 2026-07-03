"""Persistencia de legajos fiscales en JSON, con sellado e integridad.

Cada legajo se cierra al crearse: registra las versiones de los catálogos de
reglas y un snapshot del manifest de padrones usados, y se sella con SHA256
del contenido completo para poder verificar integridad a posteriori.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.modules import clientes_agentes, padron_manifest, regimenes_catalogo

HASH_FIELD = "sha256"


def _safe_json(data):
    return json.loads(json.dumps(data, ensure_ascii=False, default=str))


def calcular_hash(legajo: dict) -> str:
    """SHA256 del legajo canónico (excluye el propio campo de hash)."""
    contenido = {k: v for k, v in legajo.items() if k != HASH_FIELD}
    canonico = json.dumps(contenido, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def verificar_integridad(legajo: dict) -> dict:
    registrado = legajo.get(HASH_FIELD, "")
    recalculado = calcular_hash(legajo)
    return {
        "valido": bool(registrado) and registrado == recalculado,
        "sha256_registrado": registrado,
        "sha256_recalculado": recalculado,
    }


def _version_catalogo(cargar) -> dict:
    try:
        data = cargar()
        return {"version": data.get("version"), "actualizado": data.get("actualizado", "")}
    except Exception as e:
        return {"version": None, "actualizado": "", "error": f"catálogo no disponible: {e}"}


def _snapshot_padrones(resultados: list[dict], padrones_dir: Path | None) -> dict:
    """Metadata (período, hash, vigencia) de los padrones vigentes al decidir."""
    if not padrones_dir:
        return {}
    manifest = padron_manifest.cargar_manifest(padrones_dir).get("padrones", {})
    provincias: set[str] = set()
    for r in resultados:
        provincias.update((r.get("padrones") or {}).keys())
    snapshot = {}
    for prov in sorted(provincias):
        meta = manifest.get(prov)
        if meta:
            snapshot[prov] = {
                "periodo": meta.get("periodo", ""),
                "sha256": meta.get("sha256", ""),
                "vigencia_hasta": meta.get("vigencia_hasta", ""),
                "cargado_en": meta.get("cargado_en", ""),
            }
    return snapshot


def crear_legajo(
    resultados: list[dict],
    excel_filename: str,
    salidas_dir: Path,
    padrones_dir: Path | None = None,
) -> dict:
    legajos_dir = salidas_dir / "legajos"
    legajos_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    legajo_id = f"legajo_{now.strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    resumen = []
    for r in resultados:
        afip = r.get("afip", {})
        decision = r.get("decision_fiscal", {})
        resumen.append({
            "cuit": r.get("cuit"),
            "cuit_limpio": r.get("cuit_limpio"),
            "razon_social": afip.get("razon_social", "—"),
            "estado_afip": afip.get("estado_clave", "—"),
            "modo_afip": r.get("modo_afip", "demo"),
            "decision": decision.get("label", "—"),
            "decision_estado": decision.get("estado", "REVISION_MANUAL"),
        })
    legajo = {
        "id": legajo_id,
        "creado_en": now.strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "cerrado",
        "excel": excel_filename,
        "total_proveedores": len(resultados),
        "reglas_aplicadas": {
            "regimenes_catalogo": _version_catalogo(regimenes_catalogo.cargar_catalogo),
            "clientes_agentes": _version_catalogo(clientes_agentes.cargar_catalogo),
        },
        "padrones_snapshot": _snapshot_padrones(resultados, padrones_dir),
        "resumen": resumen,
        "resultados": _safe_json(resultados),
    }
    legajo[HASH_FIELD] = calcular_hash(legajo)
    path = legajos_dir / f"{legajo_id}.json"
    path.write_text(json.dumps(legajo, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": legajo_id, "path": str(path), **legajo}


def listar_legajos(salidas_dir: Path) -> list[dict]:
    legajos_dir = salidas_dir / "legajos"
    if not legajos_dir.exists():
        return []
    items = []
    for path in sorted(legajos_dir.glob("legajo_*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items.append({
            "id": data.get("id", path.stem),
            "creado_en": data.get("creado_en"),
            "estado": data.get("estado", "sin_sellar"),
            "sha256": data.get(HASH_FIELD, ""),
            "excel": data.get("excel"),
            "total_proveedores": data.get("total_proveedores", 0),
            "resumen": data.get("resumen", []),
        })
    return items


def obtener_legajo(salidas_dir: Path, legajo_id: str) -> dict | None:
    if "/" in legajo_id or ".." in legajo_id:
        return None
    path = salidas_dir / "legajos" / f"{legajo_id}.json"
    if not path.exists():
        return None
    legajo = json.loads(path.read_text(encoding="utf-8"))
    legajo["integridad"] = verificar_integridad(legajo)
    return legajo
