"""Catálogo operativo de fuentes fiscales y alertas de actualización."""
from __future__ import annotations

import json
import os
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from app.modules import padron_manifest, padrones

ROOT_DIR = Path(__file__).parent.parent.parent
DEFAULT_CATALOG = ROOT_DIR / "config" / "fuentes_catalogo.json"


def cargar_catalogo(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or Path(os.environ.get("FUENTES_CATALOGO", DEFAULT_CATALOG))
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data.setdefault("fuentes", [])
    return data


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


def _file_metadata(padrones_dir: Path, padron_key: str | None) -> dict[str, Any]:
    if not padron_key:
        return {}
    cfg = padrones.PADRONES_PROVINCIAS.get(padron_key, {})
    archivo_nombre = cfg.get("archivo")
    if not archivo_nombre:
        return {"padron_key": padron_key}
    archivo = padrones_dir / archivo_nombre
    if not archivo.exists():
        return {"padron_key": padron_key, "archivo": archivo_nombre, "archivo_existe": False}
    registros = None
    try:
        registros = len(padrones._leer_padron(archivo))
    except Exception:
        registros = None
    return {
        "padron_key": padron_key,
        "archivo": archivo_nombre,
        "archivo_existe": True,
        "actualizado": datetime.fromtimestamp(archivo.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "registros": registros,
    }


def _evaluar_padron_descargable(fuente: dict[str, Any], padrones_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    padron_key = fuente.get("padron_key")
    meta = manifest.get("padrones", {}).get(padron_key, {})
    file_meta = _file_metadata(padrones_dir, padron_key)
    vigencia_hasta = meta.get("vigencia_hasta", "")
    vigencia_estado = padron_manifest.estado_vigencia(vigencia_hasta)
    if not file_meta.get("archivo_existe"):
        estado = "pendiente_carga"
        accion = "Cargar o automatizar descarga del archivo mensual."
    elif vigencia_estado == "vencido":
        estado = "vencido"
        accion = "Descargar período vigente, importar y conservar evidencia."
    elif vigencia_estado == "por_vencer":
        estado = "por_vencer"
        accion = "Programar descarga del próximo período antes del vencimiento."
    elif vigencia_estado == "vigente":
        estado = "vigente"
        accion = "Sin acción inmediata; monitoreo diario."
    else:
        estado = "sin_vigencia"
        accion = "Registrar período y vigencia normativa del archivo cargado."
    return {
        **file_meta,
        "estado": estado,
        "periodo": meta.get("periodo", ""),
        "vigencia_hasta": vigencia_hasta,
        "vigencia_estado": vigencia_estado,
        "ultima_carga": meta.get("cargado_en", ""),
        "proxima_accion": accion,
    }


def _evaluar_fuente_online(fuente: dict[str, Any]) -> dict[str, Any]:
    automatizacion = fuente.get("automatizacion", "")
    if automatizacion == "automatizada":
        return {
            "estado": "automatizada",
            "vigencia_estado": "online",
            "proxima_accion": "Usar consulta online en cada alta y guardar evidencia por CUIT.",
        }
    if automatizacion == "requiere_navegador":
        return {
            "estado": "pendiente_navegador",
            "vigencia_estado": "online_asistida",
            "proxima_accion": "Implementar adaptador Playwright o cola asistida con captura.",
        }
    if automatizacion == "requiere_captcha":
        return {
            "estado": "requiere_captcha",
            "vigencia_estado": "online_asistida",
            "proxima_accion": "Crear flujo asistido para resolver CAPTCHA y guardar captura.",
        }
    if automatizacion == "requiere_credenciales":
        return {
            "estado": "requiere_credenciales",
            "vigencia_estado": "cliente",
            "proxima_accion": "Solicitar credenciales o archivo exportado al cliente.",
        }
    return {
        "estado": "pendiente_automatizacion",
        "vigencia_estado": "online_asistida",
        "proxima_accion": "Relevar flujo y definir adaptador.",
    }


def _evaluar_api_oficial(fuente: dict[str, Any]) -> dict[str, Any]:
    if fuente["id"] == "arca_constancia" and os.environ.get("AFIPSDK_TOKEN"):
        return {
            "estado": "operativa",
            "vigencia_estado": "online",
            "proxima_accion": "Monitorear errores de WS y vencimiento de certificado.",
        }
    return {
        "estado": "demo_o_sin_token",
        "vigencia_estado": "online",
        "proxima_accion": "Configurar credenciales productivas antes de uso enterprise.",
    }


def _riesgo(fuente: dict[str, Any], estado: str) -> str:
    prioridad = fuente.get("prioridad", "P3")
    if estado in {"vencido", "pendiente_carga"} and prioridad in {"P0", "P1"}:
        return "critico"
    if estado in {"vencido", "pendiente_carga", "error"}:
        return "alto"
    if estado in {"por_vencer", "sin_vigencia", "requiere_credenciales", "requiere_captcha"}:
        return "medio"
    if estado in {"pendiente_navegador", "pendiente_automatizacion"}:
        return "medio"
    return "bajo"


def _proxima_revision(fuente: dict[str, Any], evaluacion: dict[str, Any]) -> str:
    hoy = date.today()
    frecuencia = fuente.get("frecuencia")
    hasta = _parse_fecha(evaluacion.get("vigencia_hasta"))
    if hasta:
        dias_alerta = int(fuente.get("dias_alerta", 7))
        return max(hoy, hasta - timedelta(days=dias_alerta)).isoformat()
    if frecuencia == "mensual":
        primero_mes_siguiente = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1)
        return primero_mes_siguiente.isoformat()
    if frecuencia in {"online_en_cada_alta", "alta_y_revalidacion"}:
        return "en_cada_consulta"
    return "definir"


def evaluar_fuentes(padrones_dir: Path, catalog_path: Path | None = None) -> dict[str, Any]:
    catalogo = cargar_catalogo(catalog_path)
    manifest = padron_manifest.cargar_manifest(padrones_dir)
    fuentes = []
    for fuente in catalogo["fuentes"]:
        clase = fuente.get("clase")
        if clase == "padron_descargable":
            evaluacion = _evaluar_padron_descargable(fuente, padrones_dir, manifest)
        elif clase == "api_oficial":
            evaluacion = _evaluar_api_oficial(fuente)
        else:
            evaluacion = _evaluar_fuente_online(fuente)
        riesgo = _riesgo(fuente, evaluacion["estado"])
        fuentes.append({
            **fuente,
            **evaluacion,
            "riesgo_actualizacion": riesgo,
            "proxima_revision": _proxima_revision(fuente, evaluacion),
        })
    estados = Counter(f["estado"] for f in fuentes)
    riesgos = Counter(f["riesgo_actualizacion"] for f in fuentes)
    alertas = [
        {
            "id": f["id"],
            "nombre": f["nombre"],
            "estado": f["estado"],
            "riesgo": f["riesgo_actualizacion"],
            "accion": f["proxima_accion"],
        }
        for f in fuentes
        if f["riesgo_actualizacion"] in {"critico", "alto", "medio"}
    ]
    return {
        "version": catalogo.get("version", 1),
        "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "resumen": {
            "total_fuentes": len(fuentes),
            "por_estado": dict(estados),
            "por_riesgo": dict(riesgos),
            "alertas": len(alertas),
            "criticas": riesgos.get("critico", 0),
            "altas": riesgos.get("alto", 0),
            "medias": riesgos.get("medio", 0),
        },
        "alertas": alertas,
        "fuentes": fuentes,
    }
