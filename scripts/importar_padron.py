#!/usr/bin/env python3
"""Convierte padrones provinciales a CSV canónico para el validador.

Uso:
  python scripts/importar_padron.py ARBA archivo_origen.csv --out-dir padrones
  python scripts/importar_padron.py CABA archivo_origen.xlsx
  python scripts/importar_padron.py EntreRios archivo_origen.txt
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path
from typing import Iterable

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.modules.padrones import PADRONES_PROVINCIAS, _normalizar_row  # noqa: E402

PROVINCIAS_IMPORTABLES = {
    "ARBA": "ARBA",
    "BUENOSAIRES": "ARBA",
    "BSAS": "ARBA",
    "CABA": "CABA",
    "AGIP": "CABA",
    "ENTRERIOS": "EntreRios",
    "ENTRE_RIOS": "EntreRios",
    "ATER": "EntreRios",
}

CANONICAL_HEADERS = [
    "cuit",
    "alicuota_retencion",
    "alicuota_percepcion",
    "vigencia_desde",
    "vigencia_hasta",
    "regimen",
]


def _norm_provincia(valor: str) -> str:
    key = re.sub(r"[^A-Za-z]", "", valor or "").upper()
    if key not in PROVINCIAS_IMPORTABLES:
        opciones = ", ".join(sorted(set(PROVINCIAS_IMPORTABLES.values())))
        raise SystemExit(f"Provincia no soportada: {valor}. Opciones: {opciones}")
    return PROVINCIAS_IMPORTABLES[key]


def _leer_texto(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _rows_csv(path: Path) -> list[dict]:
    texto = _leer_texto(path)
    try:
        dialect = csv.Sniffer().sniff(texto[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(io.StringIO(texto), dialect=dialect))


def _rows_xlsx(path: Path, sheet: str | None = None) -> list[dict]:
    wb = load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    header_idx = None
    for idx, row in enumerate(rows[:20]):
        vals = ["" if v is None else str(v).strip() for v in row]
        joined = " ".join(vals).lower()
        if "cuit" in joined or "nro_cuit" in joined or "numero" in joined:
            header_idx = idx
            break
    if header_idx is None:
        raise SystemExit("No pude detectar fila de cabecera con CUIT en el XLSX.")
    headers = ["" if v is None else str(v).strip() for v in rows[header_idx]]
    out = []
    for row in rows[header_idx + 1:]:
        d = {headers[i]: ("" if v is None else str(v).strip()) for i, v in enumerate(row) if i < len(headers)}
        if any(d.values()):
            out.append(d)
    return out


def _rows_txt_ancho_fijo(path: Path) -> list[dict]:
    """Fallback simple para TXT sin cabecera: busca CUIT y hasta dos porcentajes por línea."""
    out = []
    for line in _leer_texto(path).splitlines():
        cuit_match = re.search(r"\b\d{11}\b", line)
        if not cuit_match:
            continue
        porcentajes = re.findall(r"\d{1,2}(?:[,.]\d{1,4})", line[cuit_match.end():])
        out.append({
            "cuit": cuit_match.group(0),
            "alicuota_retencion": porcentajes[0] if len(porcentajes) > 0 else "",
            "alicuota_percepcion": porcentajes[1] if len(porcentajes) > 1 else "",
            "vigencia_desde": "",
            "vigencia_hasta": "",
            "regimen": "TXT ancho fijo",
        })
    return out


def _leer_origen(path: Path, sheet: str | None) -> list[dict]:
    ext = path.suffix.lower()
    if ext in {".xlsx", ".xlsm"}:
        return _rows_xlsx(path, sheet)
    if ext in {".csv", ".txt", ".tsv", ".psv"}:
        rows = _rows_csv(path)
        if rows and any((k or "").strip() for k in rows[0].keys()):
            norm = [_normalizar_row(r) for r in rows]
            if any(r.get("cuit") for r in norm):
                return rows
        return _rows_txt_ancho_fijo(path)
    raise SystemExit(f"Extensión no soportada: {ext}. Usá CSV, TXT o XLSX.")


def _solo_digitos(valor: str) -> str:
    return "".join(ch for ch in str(valor or "") if ch.isdigit())


def _normalizar_pct(valor: str) -> str:
    valor = str(valor or "").replace("%", "").replace(",", ".").strip()
    return valor


def normalizar_rows(rows: Iterable[dict]) -> list[dict]:
    out = []
    vistos = set()
    for row in rows:
        n = _normalizar_row(row)
        cuit = _solo_digitos(n.get("cuit", ""))
        if len(cuit) != 11 or cuit in vistos:
            continue
        vistos.add(cuit)
        out.append({
            "cuit": cuit,
            "alicuota_retencion": _normalizar_pct(n.get("alicuota_retencion", "")),
            "alicuota_percepcion": _normalizar_pct(n.get("alicuota_percepcion", "")),
            "vigencia_desde": n.get("vigencia_desde", ""),
            "vigencia_hasta": n.get("vigencia_hasta", ""),
            "regimen": n.get("regimen", ""),
        })
    return out


def escribir_csv(rows: list[dict], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa padrones provinciales al formato canónico del validador.")
    parser.add_argument("provincia", help="ARBA, CABA o EntreRios")
    parser.add_argument("origen", type=Path, help="Archivo origen CSV/TXT/XLSX")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "padrones", help="Carpeta destino")
    parser.add_argument("--sheet", help="Hoja XLSX a leer")
    parser.add_argument("--dry-run", action="store_true", help="No escribe archivo; solo informa")
    args = parser.parse_args()

    provincia = _norm_provincia(args.provincia)
    cfg = PADRONES_PROVINCIAS[provincia]
    origen = args.origen.expanduser().resolve()
    if not origen.exists():
        raise SystemExit(f"No existe el archivo origen: {origen}")

    rows = normalizar_rows(_leer_origen(origen, args.sheet))
    destino = args.out_dir / cfg["archivo"]
    print(f"Provincia: {provincia} ({cfg['nombre']})")
    print(f"Origen: {origen}")
    print(f"Registros normalizados: {len(rows)}")
    print(f"Destino: {destino}")
    if rows[:3]:
        print("Muestra:")
        for row in rows[:3]:
            print("  " + ", ".join(f"{k}={row[k]}" for k in CANONICAL_HEADERS))
    if args.dry_run:
        return 0
    escribir_csv(rows, destino)
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
