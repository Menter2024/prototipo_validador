#!/usr/bin/env python3
"""Convierte padrones provinciales a CSV canónico para el validador.

Uso:
  python scripts/importar_padron.py ARBA archivo_origen.csv --out-dir padrones
  python scripts/importar_padron.py CABA archivo_origen.xlsx
  python scripts/importar_padron.py EntreRios archivo_origen.txt
  python scripts/importar_padron.py SantaFe archivo_origen.csv
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
    "CAPITAL": "CABA",
    "CAPITALFEDERAL": "CABA",
    "ENTRERIOS": "EntreRios",
    "ENTRE_RIOS": "EntreRios",
    "ATER": "EntreRios",
    "CORDOBA": "Cordoba",
    "DGRCORDOBA": "Cordoba",
    "FORMOSA": "Formosa",
    "JUJUY": "Jujuy",
    "MENDOZA": "Mendoza",
    "ATM": "Mendoza",
    "SANTAFE": "SantaFe",
    "SANTA_FE": "SantaFe",
    "APISANTAFE": "SantaFe",
    "TUCUMAN": "Tucuman",
    "TUCUMÁN": "Tucuman",
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
    key = (
        re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", valor or "")
        .upper()
        .translate(str.maketrans("ÁÉÍÓÚÜÑ", "AEIOUUN"))
    )
    if key not in PROVINCIAS_IMPORTABLES:
        opciones = ", ".join(sorted(p for p, cfg in PADRONES_PROVINCIAS.items() if cfg.get("tipo") == "archivo"))
        raise SystemExit(f"Provincia no soportada: {valor}. Opciones: {opciones}")
    provincia = PROVINCIAS_IMPORTABLES[key]
    if PADRONES_PROVINCIAS[provincia].get("tipo") != "archivo":
        raise SystemExit(f"{provincia} no tiene padrón por archivo normalizado; figura como consulta manual/credenciales.")
    return provincia


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


def importar_padron(
    provincia_arg: str,
    origen: Path,
    out_dir: Path,
    sheet: str | None = None,
    dry_run: bool = False,
    periodo: str | None = None,
    vigencia_hasta: str | None = None,
    backup: bool = True,
) -> dict:
    provincia = _norm_provincia(provincia_arg)
    cfg = PADRONES_PROVINCIAS[provincia]
    origen = origen.expanduser().resolve()
    if not origen.exists():
        raise FileNotFoundError(f"No existe el archivo origen: {origen}")

    rows = normalizar_rows(_leer_origen(origen, sheet))
    destino = out_dir / cfg["archivo"]
    backup_path = None
    if not dry_run:
        from app.modules.padron_manifest import backup_si_existe, registrar_carga
        if backup:
            backup_path = backup_si_existe(destino)
        escribir_csv(rows, destino)
        registrar_carga(out_dir, provincia, cfg["archivo"], len(rows), str(origen), periodo, vigencia_hasta, backup_path)
    return {
        "provincia": provincia,
        "nombre": cfg["nombre"],
        "origen": str(origen),
        "destino": str(destino),
        "registros": len(rows),
        "muestra": rows[:3],
        "dry_run": dry_run,
        "periodo": periodo or "",
        "vigencia_hasta": vigencia_hasta or "",
        "backup": backup_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa padrones provinciales al formato canónico del validador.")
    parser.add_argument("provincia", help="Provincia con padrón por archivo: ARBA, CABA, EntreRios, Cordoba, Formosa, Jujuy, Mendoza, SantaFe, Tucuman")
    parser.add_argument("origen", type=Path, help="Archivo origen CSV/TXT/XLSX")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "padrones", help="Carpeta destino")
    parser.add_argument("--sheet", help="Hoja XLSX a leer")
    parser.add_argument("--periodo", help="Período del padrón, ej. 2026-06")
    parser.add_argument("--vigencia-hasta", help="Fecha de vigencia hasta, ej. 2026-06-30")
    parser.add_argument("--sin-backup", action="store_true", help="No respalda el padrón anterior")
    parser.add_argument("--dry-run", action="store_true", help="No escribe archivo; solo informa")
    args = parser.parse_args()

    try:
        resultado = importar_padron(
            args.provincia,
            args.origen,
            args.out_dir,
            args.sheet,
            args.dry_run,
            args.periodo,
            args.vigencia_hasta,
            not args.sin_backup,
        )
    except Exception as e:
        raise SystemExit(str(e)) from e

    print(f"Provincia: {resultado['provincia']} ({resultado['nombre']})")
    print(f"Origen: {resultado['origen']}")
    print(f"Registros normalizados: {resultado['registros']}")
    print(f"Destino: {resultado['destino']}")
    if resultado["muestra"]:
        print("Muestra:")
        for row in resultado["muestra"]:
            print("  " + ", ".join(f"{k}={row[k]}" for k in CANONICAL_HEADERS))
    if not args.dry_run:
        print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
