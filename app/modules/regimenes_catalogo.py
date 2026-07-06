"""Catálogo operativo de regímenes fiscales argentinos."""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent.parent
DEFAULT_CATALOG = ROOT_DIR / "config" / "regimenes_catalogo.json"

PADRON_BY_JURISDICCION = {
    "Buenos Aires": "ARBA",
    "CABA": "CABA",
    "Córdoba": "Cordoba",
    "Entre Ríos": "EntreRios",
    "Formosa": "Formosa",
    "Jujuy": "Jujuy",
    "Tucumán": "Tucuman",
    "Santa Fe": "SantaFe",
    "Mendoza": "Mendoza",
}


def cargar_catalogo(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or Path(os.environ.get("REGIMENES_CATALOGO", DEFAULT_CATALOG))
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data.setdefault("regimenes", [])
    return data


def _matches(regimen: dict[str, Any], filtros: dict[str, str | None]) -> bool:
    for campo, valor in filtros.items():
        if valor and str(regimen.get(campo, "")) != valor:
            return False
    return True


def _integracion_padron(regimen: dict[str, Any], fuentes_por_padron: dict[str, dict[str, Any]]) -> dict[str, Any]:
    padron_key = PADRON_BY_JURISDICCION.get(regimen.get("jurisdiccion", ""))
    if not padron_key:
        return {}
    fuente = fuentes_por_padron.get(padron_key)
    if not fuente:
        return {"padron_key": padron_key, "fuente_estado": "sin_fuente_catalogada"}
    return {
        "padron_key": padron_key,
        "fuente_id": fuente.get("id"),
        "fuente_estado": fuente.get("estado"),
        "fuente_riesgo": fuente.get("riesgo_actualizacion"),
        "archivo_existe": fuente.get("archivo_existe"),
        "registros": fuente.get("registros"),
        "vigencia_estado": fuente.get("vigencia_estado"),
        "proxima_accion_fuente": fuente.get("proxima_accion"),
    }


def _backlog(regimen: dict[str, Any], integracion: dict[str, Any]) -> str:
    estado = regimen.get("estado_integracion")
    auto = regimen.get("automatizacion")
    if estado in {"parcial_importador", "parcial_importador_preview"}:
        if integracion.get("fuente_estado") in {"vigente", "operativa", "automatizada"}:
            return "operar_y_monitorear"
        return "completar_fuente_o_padron"
    if auto in {"portal_credenciales_archivo", "archivo_credenciales"}:
        return "cola_credenciales_exportacion"
    if auto == "priorizar_por_huella_cliente":
        return "relevar_huella_cliente"
    if estado == "monitoreo":
        return "monitoreo_normativo"
    if regimen.get("prioridad") in {"P0", "P1"}:
        return "integracion_prioritaria"
    return "backlog_planificado"


def filtros_disponibles(regimenes: list[dict[str, Any]]) -> dict[str, list[str]]:
    campos = ["nivel", "tipo", "prioridad", "automatizacion", "estado_integracion", "riesgo_operativo"]
    return {campo: sorted({str(r.get(campo, "")) for r in regimenes if r.get(campo)}) for campo in campos}


def resumen(regimenes: list[dict[str, Any]]) -> dict[str, Any]:
    por_nivel = Counter(r["nivel"] for r in regimenes)
    por_prioridad = Counter(r["prioridad"] for r in regimenes)
    por_auto = Counter(r["automatizacion"] for r in regimenes)
    por_backlog = Counter(r.get("backlog_estado", "") for r in regimenes)
    criticos = [r for r in regimenes if r.get("prioridad") in {"P0", "P1"} and r.get("backlog_estado") not in {"operar_y_monitorear"}]
    por_familia = defaultdict(int)
    for r in regimenes:
        por_familia[r["familia"]] += 1
    return {
        "total_regimenes": len(regimenes),
        "por_nivel": dict(por_nivel),
        "por_prioridad": dict(por_prioridad),
        "por_automatizacion": dict(por_auto),
        "por_backlog": dict(por_backlog),
        "por_familia": dict(sorted(por_familia.items())),
        "criticos_o_prioritarios_pendientes": len(criticos),
    }


def evaluar_regimenes(
    fuentes_estado: dict[str, Any] | None = None,
    catalog_path: Path | None = None,
    **filtros: str | None,
) -> dict[str, Any]:
    catalogo = cargar_catalogo(catalog_path)
    fuentes_por_padron = {
        f.get("padron_key"): f
        for f in (fuentes_estado or {}).get("fuentes", [])
        if f.get("padron_key")
    }
    enriquecidos = []
    for regimen in catalogo["regimenes"]:
        integracion = _integracion_padron(regimen, fuentes_por_padron)
        item = {**regimen, "integracion_fuente": integracion}
        item["backlog_estado"] = _backlog(regimen, integracion)
        if _matches(item, filtros):
            enriquecidos.append(item)
    return {
        "version": catalogo.get("version", 1),
        "actualizado": catalogo.get("actualizado", ""),
        "criterio": catalogo.get("criterio", ""),
        "resumen": resumen(enriquecidos),
        "filtros_disponibles": filtros_disponibles(catalogo["regimenes"]),
        "regimenes": enriquecidos,
    }
