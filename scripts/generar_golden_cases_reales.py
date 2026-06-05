#!/usr/bin/env python3
"""Genera golden cases reales desde padrones externos sin commitear padrones completos."""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import importar_padron as imp  # noqa: E402
from app.modules import padron_layouts  # noqa: E402

EMPRESA_PREFIXES = ("30", "33", "34")
DEFAULT_MIN_OVERLAP = 3


def _solo_digitos(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _is_empresa_cuit(cuit: str) -> bool:
    return cuit.startswith(EMPRESA_PREFIXES)


def _load_sources(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("sources", [])
    sources = []
    for item in data:
        source = {
            "id": item["id"],
            "provincia": item["provincia"],
            "path": item["path"],
            "expected_layout": item.get("expected_layout", ""),
        }
        sources.append(source)
    return sources


def _normalizar_source(
    source: dict[str, str],
    solo_empresas: bool,
) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    provincia = imp._norm_provincia(source["provincia"])
    parse_meta: dict[str, Any] = {}
    fast = _normalizar_source_delimitada_fast(provincia, Path(source["path"]), solo_empresas)
    if fast:
        return fast
    raw = imp._leer_origen(provincia, Path(source["path"]), None, parse_meta)
    unique: dict[str, dict[str, str]] = {}
    descartados_cuit_invalido = 0
    duplicados = 0
    for row in raw:
        n = imp._normalizar_row(row)
        cuit = _solo_digitos(n.get("cuit", ""))
        if len(cuit) != 11:
            descartados_cuit_invalido += 1
            continue
        if solo_empresas and not _is_empresa_cuit(cuit):
            continue
        if cuit in unique:
            duplicados += 1
            continue
        unique[cuit] = {
            "cuit": cuit,
            "alicuota_retencion": imp._normalizar_pct(n.get("alicuota_retencion", "")),
            "alicuota_percepcion": imp._normalizar_pct(n.get("alicuota_percepcion", "")),
            "vigencia_desde": n.get("vigencia_desde", ""),
            "vigencia_hasta": n.get("vigencia_hasta", ""),
            "regimen": n.get("regimen", ""),
        }
    advertencias = []
    if descartados_cuit_invalido:
        advertencias.append(f"{descartados_cuit_invalido} filas descartadas por CUIT inválido.")
    if duplicados:
        advertencias.append(f"{duplicados} CUITs duplicados descartados.")
    calidad = {
        "estado": "observado" if advertencias else "aprobado",
        "raw_registros": len(raw),
        "registros_validos": len(unique),
        "advertencias": advertencias,
    }
    return unique, {"provincia": provincia, "layout_detectado": parse_meta.get("layout_detectado", ""), "calidad": calidad}


def _lineas_texto(path: Path):
    if path.suffix.lower() == ".gz":
        with gzip.open(path, "rt", encoding="utf-8-sig", errors="replace") as fh:
            yield from fh
        return
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            files = [m for m in zf.infolist() if not m.is_dir() and Path(m.filename).suffix.lower() in {".csv", ".txt", ".tsv", ".psv"}]
            if not files:
                return
            member = sorted(files, key=lambda m: (imp._score_archivo_extraido(Path(m.filename))[0], m.file_size), reverse=True)[0]
            with zf.open(member) as raw:
                for line in raw.read().decode("utf-8-sig", errors="replace").splitlines():
                    yield line
        return
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        yield from fh


def _normalizar_source_delimitada_fast(
    provincia: str,
    path: Path,
    solo_empresas: bool,
) -> tuple[dict[str, dict[str, str]], dict[str, Any]] | None:
    layout = next(
        (
            item
            for item in padron_layouts.layouts_para_padron(provincia)
            if item.get("formato") == "txt_delimitado_sin_header" and item.get("fuente_id")
        ),
        None,
    )
    if not layout:
        return None
    sep = layout.get("separador") or ";"
    cuit_idx = int((layout.get("campos") or {}).get("cuit", {}).get("posicion", -1))
    if cuit_idx < 0:
        return None
    unique: dict[str, dict[str, str]] = {}
    raw_registros = 0
    descartados_cuit_invalido = 0
    duplicados = 0
    for line in _lineas_texto(path):
        if not str(line).strip() or "cuit" in str(line).lower():
            continue
        raw_registros += 1
        cols = str(line).split(sep)
        if cuit_idx >= len(cols):
            descartados_cuit_invalido += 1
            continue
        cuit = _solo_digitos(cols[cuit_idx])
        if len(cuit) != 11:
            descartados_cuit_invalido += 1
            continue
        if solo_empresas and not _is_empresa_cuit(cuit):
            continue
        if cuit in unique:
            duplicados += 1
            continue
        parsed = padron_layouts.traducir_linea_delimitada(line, layout)
        if not parsed:
            descartados_cuit_invalido += 1
            continue
        unique[cuit] = {
            "cuit": cuit,
            "alicuota_retencion": imp._normalizar_pct(parsed.get("alicuota_retencion", "")),
            "alicuota_percepcion": imp._normalizar_pct(parsed.get("alicuota_percepcion", "")),
            "vigencia_desde": parsed.get("vigencia_desde", ""),
            "vigencia_hasta": parsed.get("vigencia_hasta", ""),
            "regimen": parsed.get("regimen", ""),
        }
    advertencias = []
    if descartados_cuit_invalido:
        advertencias.append(f"{descartados_cuit_invalido} filas descartadas por CUIT inválido.")
    if duplicados:
        advertencias.append(f"{duplicados} CUITs duplicados descartados.")
    return unique, {
        "provincia": provincia,
        "layout_detectado": layout["id"],
        "calidad": {
            "estado": "observado" if advertencias else "aprobado",
            "raw_registros": raw_registros,
            "registros_validos": len(unique),
            "advertencias": advertencias,
        },
    }


def generar_golden_cases(
    sources: list[dict[str, str]],
    per_source: int = 10,
    min_overlap: int = DEFAULT_MIN_OVERLAP,
    solo_empresas: bool = True,
) -> dict[str, Any]:
    by_cuit: dict[str, dict[str, Any]] = {}
    source_rows: dict[str, dict[str, dict[str, str]]] = {}
    resumen: dict[str, Any] = {}

    for source in sources:
        unique, meta = _normalizar_source(source, solo_empresas)
        source_id = source["id"]
        source_rows[source_id] = unique
        for cuit, row in unique.items():
            entry = by_cuit.setdefault(cuit, {"cuit": cuit, "sources": [], "evidencia": {}})
            entry["sources"].append(source_id)
            entry["evidencia"][source_id] = {
                "ret": row.get("alicuota_retencion", ""),
                "perc": row.get("alicuota_percepcion", ""),
                "regimen": row.get("regimen", ""),
                "desde": row.get("vigencia_desde", ""),
                "hasta": row.get("vigencia_hasta", ""),
            }
        resumen[source_id] = {
            "provincia": meta["provincia"],
            "archivo": Path(source["path"]).name,
            "layout_detectado": meta["layout_detectado"],
            "registros_validos": meta["calidad"].get("registros_validos", 0),
            "cuits_empresa_unicos": len(unique),
            "calidad_estado": meta["calidad"].get("estado", ""),
            "advertencias": meta["calidad"].get("advertencias", []),
        }

    overlaps = [entry for entry in by_cuit.values() if len(entry["sources"]) >= min_overlap]
    overlaps.sort(key=lambda e: (-len(e["sources"]), e["cuit"]))

    por_padron: dict[str, list[dict[str, Any]]] = {}
    overlap_cuits = {entry["cuit"] for entry in overlaps}
    for source_id, rows in source_rows.items():
        selected = []
        for cuit in sorted(rows, key=lambda c: (c not in overlap_cuits, c)):
            row = rows[cuit]
            selected.append({
                "cuit": cuit,
                "aparece_en": sorted(by_cuit[cuit]["sources"]),
                "cantidad_padrones": len(by_cuit[cuit]["sources"]),
                "ret": row.get("alicuota_retencion", ""),
                "perc": row.get("alicuota_percepcion", ""),
                "regimen": row.get("regimen", ""),
            })
            if len(selected) >= per_source:
                break
        por_padron[source_id] = selected

    return {
        "generado_en": datetime.now().isoformat(timespec="seconds"),
        "criterio": {
            "per_source": per_source,
            "min_overlap": min_overlap,
            "solo_empresas": solo_empresas,
            "prefijos_empresa": list(EMPRESA_PREFIXES),
        },
        "resumen_fuentes": resumen,
        "overlaps": [
            {"cuit": e["cuit"], "aparece_en": sorted(e["sources"]), "cantidad_padrones": len(e["sources"])}
            for e in overlaps[: max(20, per_source)]
        ],
        "por_padron": por_padron,
        "nota_privacidad": "No incluye razón social ni padrones completos; CUITs filtrados a prefijos de personas jurídicas.",
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Golden cases reales de padrones",
        "",
        f"Generado: {data['generado_en']}",
        "",
        data["nota_privacidad"],
        "",
        "## Fuentes procesadas",
        "",
        "| Fuente | Archivo | Layout | Registros válidos | CUIT empresa únicos | Calidad | Advertencias |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for source_id, row in data["resumen_fuentes"].items():
        warnings = "; ".join(row.get("advertencias") or []) or "—"
        lines.append(
            "| " + " | ".join([
                source_id,
                row["archivo"].replace("|", "\\|"),
                f"`{row['layout_detectado']}`",
                str(row["registros_validos"]),
                str(row["cuits_empresa_unicos"]),
                row["calidad_estado"],
                warnings.replace("|", "\\|"),
            ]) + " |"
        )
    lines += ["", "## CUITs empresa presentes en múltiples padrones", "", "| CUIT | Cantidad | Padrones |", "|---|---:|---|"]
    for item in data["overlaps"]:
        lines.append(f"| `{item['cuit']}` | {item['cantidad_padrones']} | {', '.join(item['aparece_en'])} |")
    lines += ["", "## Casos por padrón", ""]
    for source_id, rows in data["por_padron"].items():
        lines += [f"### {source_id}", "", "| CUIT | Cantidad padrones | Aparece en | Ret. | Perc. | Régimen |", "|---|---:|---|---:|---:|---|"]
        for row in rows:
            lines.append(
                "| " + " | ".join([
                    f"`{row['cuit']}`",
                    str(row["cantidad_padrones"]),
                    ", ".join(row["aparece_en"]),
                    row.get("ret", ""),
                    row.get("perc", ""),
                    row.get("regimen", "").replace("|", "\\|"),
                ]) + " |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera golden cases reales desde padrones externos.")
    parser.add_argument("--sources-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--per-source", type=int, default=10)
    parser.add_argument("--min-overlap", type=int, default=DEFAULT_MIN_OVERLAP)
    parser.add_argument("--incluir-personas-humanas", action="store_true")
    args = parser.parse_args()

    data = generar_golden_cases(
        _load_sources(args.sources_json),
        per_source=args.per_source,
        min_overlap=args.min_overlap,
        solo_empresas=not args.incluir_personas_humanas,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(data) + "\n")
    if not args.out_json and not args.out_md:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
