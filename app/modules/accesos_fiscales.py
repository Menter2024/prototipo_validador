"""Gestión de accesos fiscales por cliente/grupo económico y CUIT agente."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

MANIFEST = "accesos_fiscales.json"
ESTADOS = {"pendiente", "autorizado", "credencial_cargada", "exportacion_manual", "login_asistido", "bloqueado", "revocado"}
TIPOS_ACCESO = {"publico", "archivo_manual", "credencial_delegada", "login_asistido", "no_automatizable"}


def _path(salidas_dir: Path) -> Path:
    return salidas_dir / MANIFEST


def _safe(data):
    return json.loads(json.dumps(data, ensure_ascii=False, default=str))


def cargar(salidas_dir: Path) -> dict:
    path = _path(salidas_dir)
    if not path.exists():
        return {"version": 1, "accesos": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "accesos": []}
    data.setdefault("version", 1)
    data.setdefault("accesos", [])
    return data


def guardar(salidas_dir: Path, data: dict) -> None:
    salidas_dir.mkdir(parents=True, exist_ok=True)
    _path(salidas_dir).write_text(json.dumps(_safe(data), ensure_ascii=False, indent=2), encoding="utf-8")


def _resumen(accesos: list[dict]) -> dict:
    return {
        "total": len(accesos),
        "pendientes": sum(1 for a in accesos if a.get("estado") == "pendiente"),
        "autorizados": sum(1 for a in accesos if a.get("estado") in {"autorizado", "credencial_cargada", "exportacion_manual", "login_asistido"}),
        "bloqueados": sum(1 for a in accesos if a.get("estado") == "bloqueado"),
        "revocados": sum(1 for a in accesos if a.get("estado") == "revocado"),
    }


def listar(salidas_dir: Path, cliente: str | None = None, cuit_agente: str | None = None, organismo: str | None = None) -> dict:
    data = cargar(salidas_dir)
    accesos = data.get("accesos", [])
    if cliente:
        accesos = [a for a in accesos if a.get("cliente", "").lower() == cliente.lower()]
    if cuit_agente:
        cuit_norm = "".join(ch for ch in cuit_agente if ch.isdigit())
        accesos = [a for a in accesos if a.get("cuit_agente_limpio") == cuit_norm]
    if organismo:
        accesos = [a for a in accesos if a.get("organismo", "").lower() == organismo.lower()]
    return {"accesos": accesos, "resumen": _resumen(accesos)}


def _dedupe_key(acceso: dict) -> tuple:
    return (
        acceso.get("cliente", "").strip().lower(),
        acceso.get("cuit_agente_limpio", ""),
        acceso.get("organismo", "").strip().lower(),
        acceso.get("servicio", "").strip().lower(),
        acceso.get("fuente_id", "").strip().lower(),
    )


def crear_o_actualizar(
    salidas_dir: Path,
    cliente: str,
    cuit_agente: str,
    organismo: str,
    servicio: str,
    tipo_acceso: str,
    estado: str = "pendiente",
    fuente_id: str = "",
    alcance: str = "",
    responsable: str = "",
    notas: str = "",
    evidencia_path: Path | None = None,
    evidencia_filename: str | None = None,
) -> dict:
    if estado not in ESTADOS:
        raise ValueError(f"Estado inválido: {estado}")
    if tipo_acceso not in TIPOS_ACCESO:
        raise ValueError(f"Tipo de acceso inválido: {tipo_acceso}")
    cuit_limpio = "".join(ch for ch in cuit_agente if ch.isdigit())
    if len(cuit_limpio) != 11:
        raise ValueError("CUIT agente inválido: debe tener 11 dígitos.")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acceso = {
        "id": f"acc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}",
        "cliente": cliente.strip(),
        "cuit_agente": cuit_agente.strip(),
        "cuit_agente_limpio": cuit_limpio,
        "organismo": organismo.strip(),
        "servicio": servicio.strip(),
        "fuente_id": fuente_id.strip(),
        "tipo_acceso": tipo_acceso,
        "estado": estado,
        "alcance": alcance.strip(),
        "responsable": responsable.strip(),
        "notas": notas.strip(),
        "creado_en": now,
        "actualizado_en": now,
        "historial": [{"fecha": now, "estado": estado, "nota": "Alta/actualización de acceso fiscal."}],
        "evidencias": [],
    }

    data = cargar(salidas_dir)
    key = _dedupe_key(acceso)
    for existente in data.get("accesos", []):
        if _dedupe_key(existente) == key:
            existente.update({k: v for k, v in acceso.items() if k not in {"id", "creado_en", "historial", "evidencias"}})
            existente["actualizado_en"] = now
            existente.setdefault("historial", []).insert(0, {"fecha": now, "estado": estado, "nota": "Actualización de acceso fiscal."})
            acceso = existente
            break
    else:
        data.setdefault("accesos", []).insert(0, acceso)

    if evidencia_path and evidencia_filename:
        evid_dir = salidas_dir / "evidencias" / "accesos_fiscales" / acceso["id"]
        evid_dir.mkdir(parents=True, exist_ok=True)
        destino = evid_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(evidencia_filename).name}"
        shutil.copy2(evidencia_path, destino)
        ev = {"fecha": now, "archivo": str(destino), "nombre_original": evidencia_filename}
        acceso.setdefault("evidencias", []).insert(0, ev)
        acceso.setdefault("historial", []).insert(0, {"fecha": now, "estado": estado, "nota": "Evidencia adjuntada.", "evidencia": ev})

    guardar(salidas_dir, data)
    return acceso


def matriz_requisitos(salidas_dir: Path, fuentes_estado: dict | None = None) -> dict:
    accesos = cargar(salidas_dir).get("accesos", [])
    por_fuente = {a.get("fuente_id"): a for a in accesos if a.get("fuente_id")}
    items = []
    for fuente in (fuentes_estado or {}).get("fuentes", []):
        req_cred = fuente.get("automatizacion") in {"requiere_credenciales", "portal_credenciales", "archivo_credenciales"} or fuente.get("tipo_acceso", "").startswith("clave")
        if not req_cred and fuente.get("descarga", {}).get("modo") not in {"portal_credenciales", "requiere_credenciales"}:
            continue
        acceso = por_fuente.get(fuente.get("id"))
        items.append({
            "fuente_id": fuente.get("id"),
            "nombre": fuente.get("nombre"),
            "organismo": fuente.get("organismo"),
            "jurisdiccion": fuente.get("jurisdiccion"),
            "prioridad": fuente.get("prioridad"),
            "tipo_acceso_requerido": fuente.get("tipo_acceso") or fuente.get("descarga", {}).get("modo"),
            "estado_acceso": acceso.get("estado") if acceso else "pendiente",
            "cuit_agente": acceso.get("cuit_agente") if acceso else "",
            "responsable": acceso.get("responsable") if acceso else "",
            "proxima_accion": "Solicitar autorización/exportación a CCU." if not acceso else "Usar evidencia/acceso autorizado según alcance.",
        })
    return {"items": items, "resumen": _resumen(accesos)}
