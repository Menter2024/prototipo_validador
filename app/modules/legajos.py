"""Persistencia simple de legajos fiscales en JSON."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def _safe_json(data):
    return json.loads(json.dumps(data, ensure_ascii=False, default=str))


def crear_legajo(resultados: list[dict], excel_filename: str, salidas_dir: Path) -> dict:
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
        "excel": excel_filename,
        "total_proveedores": len(resultados),
        "resumen": resumen,
        "resultados": _safe_json(resultados),
    }
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
    return json.loads(path.read_text(encoding="utf-8"))
