#!/usr/bin/env python3
"""Genera casos reales de prueba desde padrones canónicos cargados."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.padrones import PADRONES_PROVINCIAS, _normalizar_row  # noqa: E402


def _solo_digitos(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _iter_cuits(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        for row in csv.DictReader(fh, dialect=dialect):
            cuit = _solo_digitos(_normalizar_row(row).get("cuit", ""))
            if len(cuit) == 11:
                yield cuit


def generar_casos(padrones_dir: Path, por_padron: int = 10, min_overlap: int = 2) -> dict:
    por_jurisdiccion: dict[str, list[str]] = {}
    apariciones: dict[str, set[str]] = defaultdict(set)
    totales: dict[str, int] = {}

    for provincia, cfg in PADRONES_PROVINCIAS.items():
        if cfg.get("tipo") != "archivo" or not cfg.get("archivo"):
            continue
        path = padrones_dir / cfg["archivo"]
        if not path.exists():
            continue
        muestra: list[str] = []
        total = 0
        vistos_local = set()
        for cuit in _iter_cuits(path):
            total += 1
            if cuit not in vistos_local:
                apariciones[cuit].add(provincia)
                vistos_local.add(cuit)
            if len(muestra) < por_padron:
                muestra.append(cuit)
        por_jurisdiccion[provincia] = muestra
        totales[provincia] = total

    overlaps = [
        {"cuit": cuit, "padrones": sorted(provs), "cantidad_padrones": len(provs)}
        for cuit, provs in apariciones.items()
        if len(provs) >= min_overlap
    ]
    overlaps.sort(key=lambda x: (-x["cantidad_padrones"], x["cuit"]))

    return {
        "generado_en": datetime.now().isoformat(timespec="seconds"),
        "padrones_dir": str(padrones_dir),
        "criterio": {"por_padron": por_padron, "min_overlap": min_overlap},
        "totales": totales,
        "por_padron": por_jurisdiccion,
        "overlaps": overlaps[: max(por_padron, 10)],
        "uso": "Usar estos CUITs como golden set real. No commitear salidas con padrones/cuits sensibles si el cliente lo restringe.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera casos de prueba reales desde padrones canónicos locales.")
    parser.add_argument("--padrones-dir", type=Path, default=ROOT / "padrones")
    parser.add_argument("--por-padron", type=int, default=10)
    parser.add_argument("--min-overlap", type=int, default=2)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    data = generar_casos(args.padrones_dir, args.por_padron, args.min_overlap)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
