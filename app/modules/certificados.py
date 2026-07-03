"""Vigilancia de certificados fiscales propios de los clientes-agentes.

Lee la sección certificados_propios de config/clientes_agentes.json y calcula
el estado de vigencia de cada certificado (exclusiones, no retención/percepción,
exenciones). Un certificado vencido implica que los agentes de terceros vuelven
a retener/percibir al cliente: el vencimiento es una alerta operativa concreta.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.modules import clientes_agentes

POR_VENCER_DIAS = 30


def _parse_fecha(valor: str | None) -> date | None:
    if not valor:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(valor.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _estado_vigencia(vigencia_hasta: str | None, hoy: date) -> tuple[str, int | None]:
    hasta = _parse_fecha(vigencia_hasta)
    if not hasta:
        return "sin_vigencia_registrada", None
    dias = (hasta - hoy).days
    if dias < 0:
        return "vencido", dias
    if dias <= POR_VENCER_DIAS:
        return "por_vencer", dias
    return "vigente", dias


def evaluar(path: Path | None = None, hoy: date | None = None) -> dict[str, Any]:
    """Estado de vigencia de todos los certificados propios por cliente."""
    hoy = hoy or date.today()
    catalogo = clientes_agentes.cargar_catalogo(path)
    items: list[dict[str, Any]] = []
    for cliente in catalogo.get("clientes", []):
        certificados = (cliente.get("certificados_propios") or {}).get("items", [])
        for cert in certificados:
            estado, dias = _estado_vigencia(cert.get("vigencia_hasta"), hoy)
            items.append({
                "cliente": cliente.get("cliente", ""),
                "cuit": cliente.get("cuit", ""),
                "concepto": cert.get("concepto", ""),
                "organismo": cert.get("organismo", ""),
                "numero": cert.get("numero", ""),
                "vigencia_desde": cert.get("vigencia_desde", ""),
                "vigencia_hasta": cert.get("vigencia_hasta", ""),
                "estado": estado,
                "dias_restantes": dias,
                "fuente": cert.get("fuente", ""),
                "nota": cert.get("nota", ""),
            })

    orden = {"vencido": 0, "por_vencer": 1, "sin_vigencia_registrada": 2, "vigente": 3}
    items.sort(key=lambda i: (orden.get(i["estado"], 9), i["dias_restantes"] if i["dias_restantes"] is not None else 9999))

    alertas = [
        (
            f"{i['cliente']} · {i['concepto']}: "
            + (f"VENCIDO hace {-i['dias_restantes']} día(s)." if i["estado"] == "vencido"
               else f"vence en {i['dias_restantes']} día(s) ({i['vigencia_hasta']}).")
            + " Al vencer, los agentes vuelven a retener/percibir: gestionar renovación."
        )
        for i in items
        if i["estado"] in {"vencido", "por_vencer"}
    ]
    resumen = {
        "total": len(items),
        "vencidos": sum(1 for i in items if i["estado"] == "vencido"),
        "por_vencer": sum(1 for i in items if i["estado"] == "por_vencer"),
        "vigentes": sum(1 for i in items if i["estado"] == "vigente"),
        "sin_vigencia_registrada": sum(1 for i in items if i["estado"] == "sin_vigencia_registrada"),
    }
    return {
        "fecha_evaluacion": hoy.strftime("%Y-%m-%d"),
        "umbral_por_vencer_dias": POR_VENCER_DIAS,
        "items": items,
        "alertas": alertas,
        "resumen": resumen,
    }
