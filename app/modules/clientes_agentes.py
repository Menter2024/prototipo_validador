"""Catálogo de clientes-agentes y su huella de regímenes fiscales.

Lee config/clientes_agentes.json y expone la huella fiscal de cada cliente:
qué regímenes de información, retención y percepción debe responder o generar.
A diferencia de regimenes_catalogo (universo general), esto describe un cliente concreto.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent.parent
DEFAULT_CATALOG = ROOT_DIR / "config" / "clientes_agentes.json"


def _norm_cuit(valor: str | None) -> str:
    return "".join(ch for ch in (valor or "") if ch.isdigit())


def cargar_catalogo(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or Path(os.environ.get("CLIENTES_AGENTES_CATALOGO", DEFAULT_CATALOG))
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data.setdefault("clientes", [])
    return data


def resumen_regimenes(regimenes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(regimenes),
        "por_nivel": dict(Counter(r.get("nivel", "") for r in regimenes)),
        "por_tipo": dict(Counter(r.get("tipo", "") for r in regimenes)),
        "por_rol": dict(Counter(r.get("rol", "") for r in regimenes)),
        "por_confirmacion": dict(Counter(r.get("estado_confirmacion", "") for r in regimenes)),
        "a_confirmar": sum(
            1 for r in regimenes
            if str(r.get("estado_confirmacion", "")).startswith("a_confirmar")
            or r.get("estado_confirmacion") in {"a_confirmar", "a_relevar_por_huella"}
        ),
    }


def _enriquecer_cliente(cliente: dict[str, Any]) -> dict[str, Any]:
    regimenes = cliente.get("regimenes", [])
    return {**cliente, "resumen": resumen_regimenes(regimenes)}


def listar(
    cliente: str | None = None,
    cuit: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    catalogo = cargar_catalogo(path)
    clientes = catalogo.get("clientes", [])
    if cliente:
        clientes = [c for c in clientes if c.get("cliente", "").lower() == cliente.lower()]
    if cuit:
        cuit_norm = _norm_cuit(cuit)
        clientes = [c for c in clientes if _norm_cuit(c.get("cuit_limpio") or c.get("cuit")) == cuit_norm]
    enriquecidos = [_enriquecer_cliente(c) for c in clientes]
    return {
        "version": catalogo.get("version", 1),
        "actualizado": catalogo.get("actualizado", ""),
        "criterio": catalogo.get("criterio", ""),
        "advertencia": catalogo.get("advertencia", ""),
        "total_clientes": len(enriquecidos),
        "clientes": enriquecidos,
    }


def obtener(cliente_o_cuit: str, path: Path | None = None) -> dict[str, Any] | None:
    por_cliente = listar(cliente=cliente_o_cuit, path=path)["clientes"]
    if por_cliente:
        return por_cliente[0]
    por_cuit = listar(cuit=cliente_o_cuit, path=path)["clientes"]
    return por_cuit[0] if por_cuit else None
