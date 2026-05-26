"""Cola asistida para fuentes fiscales que requieren intervención humana."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

MANIFEST = "fuentes_pendientes.json"
ESTADOS_ABIERTOS = {"pendiente", "en_proceso"}
ESTADOS_VALIDOS = {"pendiente", "en_proceso", "resuelto", "descartado", "error"}
FUENTES_ONLINE_PENDIENTES = {"requiere_captcha", "requiere_credenciales", "requiere_navegador", "error", "revisar"}
PADRONES_ASISTIDOS = {"consulta_manual", "requiere_credenciales"}


def _path(salidas_dir: Path) -> Path:
    return salidas_dir / MANIFEST


def _safe(data):
    return json.loads(json.dumps(data, ensure_ascii=False, default=str))


def cargar(salidas_dir: Path) -> dict:
    path = _path(salidas_dir)
    if not path.exists():
        return {"version": 1, "items": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "items": []}


def guardar(salidas_dir: Path, data: dict) -> None:
    salidas_dir.mkdir(parents=True, exist_ok=True)
    _path(salidas_dir).write_text(json.dumps(_safe(data), ensure_ascii=False, indent=2), encoding="utf-8")


def listar(salidas_dir: Path, estado: str | None = None) -> dict:
    data = cargar(salidas_dir)
    items = data.get("items", [])
    if estado:
        items = [i for i in items if i.get("estado") == estado]
    resumen = {
        "total": len(data.get("items", [])),
        "pendientes": sum(1 for i in data.get("items", []) if i.get("estado") == "pendiente"),
        "en_proceso": sum(1 for i in data.get("items", []) if i.get("estado") == "en_proceso"),
        "resueltos": sum(1 for i in data.get("items", []) if i.get("estado") == "resuelto"),
        "descartados": sum(1 for i in data.get("items", []) if i.get("estado") == "descartado"),
        "errores": sum(1 for i in data.get("items", []) if i.get("estado") == "error"),
    }
    return {"items": items, "resumen": resumen}


def _dedupe_key(item: dict) -> str:
    return "|".join([
        item.get("cuit_limpio") or "",
        item.get("fuente") or "",
        item.get("tipo_requerimiento") or "",
    ])


def _crear_item_base(
    cuit: str,
    cuit_limpio: str,
    razon_social: str,
    fuente: str,
    nombre: str,
    tipo_requerimiento: str,
    detalle: str,
    url: str | None,
    prioridad: str,
    origen: str,
    legajo_id: str | None,
) -> dict:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": f"fp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}",
        "estado": "pendiente",
        "prioridad": prioridad,
        "cuit": cuit,
        "cuit_limpio": cuit_limpio,
        "razon_social": razon_social,
        "fuente": fuente,
        "nombre": nombre,
        "tipo_requerimiento": tipo_requerimiento,
        "detalle": detalle,
        "url": url,
        "origen": origen,
        "legajo_id": legajo_id,
        "creado_en": now,
        "actualizado_en": now,
        "historial": [{
            "fecha": now,
            "estado": "pendiente",
            "nota": "Alta automática desde validación fiscal.",
        }],
        "evidencias": [],
    }


def crear_item(salidas_dir: Path, item: dict) -> dict:
    data = cargar(salidas_dir)
    key = _dedupe_key(item)
    for existente in data.get("items", []):
        if existente.get("estado") in ESTADOS_ABIERTOS and _dedupe_key(existente) == key:
            existente["actualizado_en"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existente.setdefault("historial", []).insert(0, {
                "fecha": existente["actualizado_en"],
                "estado": existente["estado"],
                "nota": "Detectado nuevamente en validación; se mantiene tarea abierta.",
            })
            guardar(salidas_dir, data)
            return existente
    data.setdefault("items", []).insert(0, item)
    guardar(salidas_dir, data)
    return item


def crear_desde_resultados(salidas_dir: Path, resultados: list[dict], legajo_id: str | None = None) -> list[dict]:
    creados = []
    for r in resultados:
        if not r.get("valido"):
            continue
        afip = r.get("afip", {})
        razon = afip.get("razon_social", "—")
        for fuente, info in (r.get("fuentes_online") or {}).items():
            estado = info.get("estado")
            if estado not in FUENTES_ONLINE_PENDIENTES:
                continue
            item = _crear_item_base(
                r.get("cuit", ""),
                r.get("cuit_limpio", ""),
                razon,
                fuente,
                info.get("nombre", fuente),
                estado,
                info.get("detalle", ""),
                info.get("url_consulta"),
                "P3",
                "fuentes_online",
                legajo_id,
            )
            creados.append(crear_item(salidas_dir, item))
        for fuente, info in (r.get("padrones") or {}).items():
            status = info.get("status")
            if status not in PADRONES_ASISTIDOS:
                continue
            item = _crear_item_base(
                r.get("cuit", ""),
                r.get("cuit_limpio", ""),
                razon,
                fuente,
                info.get("nombre", fuente),
                status,
                info.get("detalle", ""),
                info.get("url"),
                info.get("prioridad", "P3"),
                "padrones",
                legajo_id,
            )
            creados.append(crear_item(salidas_dir, item))
    return creados


def actualizar(
    salidas_dir: Path,
    item_id: str,
    estado: str,
    nota: str,
    evidencia_path: Path | None = None,
    evidencia_filename: str | None = None,
) -> dict | None:
    if estado not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado inválido: {estado}")
    data = cargar(salidas_dir)
    for item in data.get("items", []):
        if item.get("id") != item_id:
            continue
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item["estado"] = estado
        item["actualizado_en"] = now
        hist = {"fecha": now, "estado": estado, "nota": nota or ""}
        if evidencia_path and evidencia_filename:
            evid_dir = salidas_dir / "evidencias" / "fuentes_pendientes" / item_id
            evid_dir.mkdir(parents=True, exist_ok=True)
            destino = evid_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(evidencia_filename).name}"
            shutil.copy2(evidencia_path, destino)
            ev = {"fecha": now, "archivo": str(destino), "nombre_original": evidencia_filename}
            item.setdefault("evidencias", []).insert(0, ev)
            hist["evidencia"] = ev
        item.setdefault("historial", []).insert(0, hist)
        guardar(salidas_dir, data)
        return item
    return None
