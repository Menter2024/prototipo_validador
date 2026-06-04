"""Catálogo y traductor de layouts de padrones fiscales."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LAYOUTS_PATH = ROOT / "config" / "padron_layouts.json"


def cargar_catalogo(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_LAYOUTS_PATH
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def listar_layouts(path: Path | None = None) -> list[dict[str, Any]]:
    return cargar_catalogo(path).get("layouts", [])


def obtener_layout(layout_id: str, path: Path | None = None) -> dict[str, Any] | None:
    return next((layout for layout in listar_layouts(path) if layout.get("id") == layout_id), None)


def layouts_para_padron(padron_key: str, path: Path | None = None) -> list[dict[str, Any]]:
    return [layout for layout in listar_layouts(path) if layout.get("padron_key") in {padron_key, "*"}]


def _solo_digitos(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _fecha_ddmmaaaa(value: str) -> str:
    digitos = _solo_digitos(value)
    if len(digitos) == 8:
        return f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"
    if len(digitos) == 7:
        return f"0{digitos[:1]}/{digitos[1:3]}/{digitos[3:]}"
    return str(value or "").strip()


def _fecha_yyyy_mm_dd(value: str) -> str:
    raw = str(value or "").strip()
    digitos = _solo_digitos(raw)
    if len(digitos) == 8 and raw[:4].isdigit():
        return f"{digitos[6:8]}/{digitos[4:6]}/{digitos[:4]}"
    return raw


def _porcentaje(value: str) -> str:
    raw = str(value or "").replace("%", "").strip()
    if "," in raw or "." in raw:
        return raw.replace(",", ".")
    digitos = _solo_digitos(raw)
    if len(digitos) in {3, 4}:
        return f"{int(digitos) / 100:.2f}"
    return raw


def _transform(value: str, spec: dict[str, Any]) -> str:
    tipo = spec.get("tipo", "texto")
    if tipo == "cuit":
        return _solo_digitos(value)
    if tipo == "fecha_ddmmaaaa":
        return _fecha_ddmmaaaa(value)
    if tipo == "fecha_yyyy_mm_dd":
        return _fecha_yyyy_mm_dd(value)
    if tipo in {"porcentaje", "porcentaje_agip"}:
        return _porcentaje(value)
    if tipo == "codigo":
        raw = str(value or "").strip()
        return (spec.get("map") or {}).get(raw.upper(), raw)
    return str(value or "").strip()


def _norm_header(value: str) -> str:
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    limpio = str(value or "").translate(reemplazos).strip().lower()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in limpio).split())


def traducir_row_con_cabeceras(row: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any] | None:
    headers = {_norm_header(key): value for key, value in row.items()}
    values: dict[str, str] = {}
    for field, spec in (layout.get("campos") or {}).items():
        aliases = spec.get("aliases") or []
        for alias in aliases:
            header = _norm_header(alias)
            if header in headers:
                values[field] = _transform(headers[header], spec)
                break

    if "cuit" not in values:
        return None
    cuit = values.get("cuit", "")

    return {
        "cuit": cuit,
        "alicuota_retencion": values.get("alicuota_retencion", ""),
        "alicuota_percepcion": values.get("alicuota_percepcion", ""),
        "vigencia_desde": values.get("vigencia_desde", ""),
        "vigencia_hasta": values.get("vigencia_hasta", ""),
        "regimen": values.get("regimen") or (layout.get("salida") or {}).get("regimen_default", ""),
        "jurisdiccion": layout.get("jurisdiccion", ""),
        "tipo_padron": layout.get("tipo_padron", ""),
        "fuente_id": layout.get("fuente_id", ""),
        "layout_id": layout.get("id", ""),
    }


def traducir_linea_delimitada(line: str, layout: dict[str, Any]) -> dict[str, Any] | None:
    separador = layout.get("separador") or ";"
    cols = [col.strip() for col in str(line or "").split(separador)]
    min_columnas = int((layout.get("validaciones") or {}).get("min_columnas") or 1)
    if len(cols) < min_columnas:
        return None

    values: dict[str, str] = {}
    for field, spec in (layout.get("campos") or {}).items():
        if "posicion" not in spec:
            continue
        idx = int(spec["posicion"])
        if idx >= len(cols):
            continue
        values[field] = _transform(cols[idx], spec)

    cuit = values.get("cuit", "")
    cuit_len = int((layout.get("validaciones") or {}).get("cuit_longitud") or 0)
    if cuit_len and len(cuit) != cuit_len:
        return None

    regimen = values.get("regimen", "")
    template = (layout.get("salida") or {}).get("regimen_template")
    if template:
        try:
            regimen = template.format(**values).strip(" ·")
        except KeyError:
            regimen = regimen.strip()
    if not regimen:
        regimen = (layout.get("salida") or {}).get("regimen_default", "")

    return {
        "cuit": cuit,
        "alicuota_retencion": values.get("alicuota_retencion", ""),
        "alicuota_percepcion": values.get("alicuota_percepcion", ""),
        "vigencia_desde": values.get("vigencia_desde", ""),
        "vigencia_hasta": values.get("vigencia_hasta", ""),
        "regimen": regimen,
        "jurisdiccion": layout.get("jurisdiccion", ""),
        "tipo_padron": layout.get("tipo_padron", ""),
        "fuente_id": layout.get("fuente_id", ""),
        "layout_id": layout.get("id", ""),
    }
