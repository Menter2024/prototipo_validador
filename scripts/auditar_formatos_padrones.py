#!/usr/bin/env python3
"""Audita cobertura de formatos/layouts de fuentes de padrones."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASSIVE_AUTOMATION = {"archivo_normalizado", "archivo_padron"}
ONLINE_OR_ASSISTED = {
    "automatizada",
    "pendiente_automatizacion",
    "priorizar_por_huella_cliente",
    "requiere_captcha",
    "requiere_credenciales",
    "requiere_navegador",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _landing_url(source: dict[str, Any]) -> str:
    descarga = source.get("descarga") or {}
    return descarga.get("landing_url") or source.get("url") or ""


def _layout_index(layouts: list[dict[str, Any]]) -> dict[str, list[str]]:
    indexed: dict[str, list[str]] = {}
    for layout in layouts:
        fuente_id = layout.get("fuente_id")
        if fuente_id:
            indexed.setdefault(fuente_id, []).append(layout["id"])
    return indexed


def _layout_states(layouts: list[dict[str, Any]]) -> dict[str, list[str]]:
    indexed: dict[str, list[str]] = {}
    for layout in layouts:
        fuente_id = layout.get("fuente_id")
        if fuente_id:
            indexed.setdefault(fuente_id, []).append(layout.get("estado", "sin_estado"))
    return indexed


def audit_sources(
    catalog_path: Path = ROOT / "config" / "fuentes_catalogo.json",
    layouts_path: Path = ROOT / "config" / "padron_layouts.json",
) -> dict[str, Any]:
    catalog = _read_json(catalog_path)
    layouts_catalog = _read_json(layouts_path)
    layouts = layouts_catalog.get("layouts", [])
    layouts_by_source = _layout_index(layouts)
    states_by_source = _layout_states(layouts)
    rows: list[dict[str, Any]] = []

    for source in catalog["fuentes"]:
        fuente_id = source["id"]
        automation = source.get("automatizacion", "")
        source_layouts = layouts_by_source.get(fuente_id, [])
        landing = _landing_url(source)
        url = source.get("url") or ""
        requires_massive_layout = automation in MASSIVE_AUTOMATION

        if source_layouts:
            pending_sample = any(state.startswith("pendiente") for state in states_by_source.get(fuente_id, []))
            layout_status = "layout_especifico_pendiente_muestra" if pending_sample else "layout_especifico"
            next_action = (
                "Validar contra muestra oficial real, conservar hash y recién marcar integrado."
                if pending_sample
                else "Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas."
            )
            blocking = bool(requires_massive_layout and pending_sample)
        elif requires_massive_layout:
            layout_status = "requiere_layout_especifico"
            next_action = "Relevar archivo oficial real, documentar columnas y crear layout específico versionado."
            blocking = True
        elif automation in ONLINE_OR_ASSISTED or source.get("clase") in {"api_oficial", "consulta_online", "portal_captcha", "portal_credenciales", "cola_asistida"}:
            layout_status = "consulta_api_o_asistida"
            next_action = "Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial."
            blocking = False
        else:
            layout_status = "por_clasificar"
            next_action = "Confirmar método de obtención y si entrega archivo masivo o consulta por CUIT."
            blocking = True

        format_info_status = "landing_con_instructivo_a_verificar"
        if landing and url and landing != url:
            format_info_status = "link_descarga_diferente_de_url_base"
        if not landing:
            format_info_status = "sin_link_obtencion"

        rows.append(
            {
                "fuente_id": fuente_id,
                "prioridad": source.get("prioridad", ""),
                "jurisdiccion": source.get("jurisdiccion", ""),
                "organismo": source.get("organismo", ""),
                "clase": source.get("clase", ""),
                "automatizacion": automation,
                "obtencion_url": landing,
                "formato_info_status": format_info_status,
                "layout_status": layout_status,
                "layout_ids": source_layouts,
                "layout_estados": states_by_source.get(fuente_id, []),
                "bloquea_importacion_masiva": blocking,
                "accion_siguiente": next_action,
            }
        )

    counts = Counter(row["layout_status"] for row in rows)
    blocking_by_priority = Counter(
        row["prioridad"] for row in rows if row["bloquea_importacion_masiva"]
    )
    return {
        "version": 1,
        "actualizado": "2026-06-04",
        "source_count": len(rows),
        "layout_status_counts": dict(sorted(counts.items())),
        "blocking_by_priority": dict(sorted(blocking_by_priority.items())),
        "rows": rows,
    }


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Backlog de formatos y layouts de padrones",
        "",
        f"Actualizado: {audit['actualizado']}.",
        "",
        "Este backlog convierte el registro maestro en trabajo verificable: identifica qué fuentes ya tienen layout específico, cuáles requieren relevar archivo real y cuáles son consultas/API/cola asistida.",
        "",
        "## Resumen",
        "",
        f"- Fuentes auditadas: {audit['source_count']}",
    ]
    for status, count in audit["layout_status_counts"].items():
        lines.append(f"- {status}: {count}")
    if audit["blocking_by_priority"]:
        lines.append("- Bloqueos de importación masiva por prioridad: " + ", ".join(f"{p}={c}" for p, c in audit["blocking_by_priority"].items()))
    lines.extend(
        [
            "",
            "## Matriz completa",
            "",
            "| Prioridad | Fuente | Jurisdicción | Tipo | Obtención | Estado formato | Layout | Bloquea masivo | Próxima acción |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in audit["rows"]:
        layout = ", ".join(f"`{layout_id}`" for layout_id in row["layout_ids"]) or row["layout_status"]
        link = f"[link]({row['obtencion_url']})" if row["obtencion_url"] else "pendiente"
        blocks = "sí" if row["bloquea_importacion_masiva"] else "no"
        cells = [
            row["prioridad"],
            f"`{row['fuente_id']}`",
            row["jurisdiccion"],
            row["automatizacion"] or row["clase"],
            link,
            row["formato_info_status"],
            layout,
            blocks,
            row["accion_siguiente"],
        ]
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in cells) + " |")
    lines.extend(
        [
            "",
            "## Orden de trabajo recomendado",
            "",
            "1. P0 masivos sin layout: ARBA, ATER Entre Ríos y Santa Fe.",
            "2. P1 masivos sin layout: Córdoba, Jujuy, Mendoza y Tucumán.",
            "3. P2/P3 masivos: Formosa y nuevas fuentes que el cliente confirme.",
            "4. Consultas/API/portales: documentar playbook, credenciales, evidencia y límites legales/técnicos.",
            "5. Municipales: abrir subregistro por municipios reales del cliente.",
            "",
            "## Criterio de terminado por fuente",
            "",
            "- Link oficial de obtención confirmado.",
            "- Instructivo/layout/norma o muestra real con columnas documentadas.",
            "- `layout_id` específico si hay archivo masivo.",
            "- Test unitario del traductor y golden sample sanitizado.",
            "- Manifest con hash de original y validaciones de calidad.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit = audit_sources()
    rendered = json.dumps(audit, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(audit)
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
