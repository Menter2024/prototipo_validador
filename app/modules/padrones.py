"""Lectura de padrones provinciales de Ingresos Brutos.

Lee archivos depositados en la carpeta `padrones/`. Por simplicidad del
prototipo, soporta dos formatos:
  - CSV: cuit, alicuota_retencion, alicuota_percepcion, vigencia_desde, vigencia_hasta
  - TXT ancho fijo de ARBA (especificación oficial)

Cada provincia es un archivo. Para esta demo, hay un ejemplo de ARBA.
"""
from pathlib import Path
import csv
from typing import Optional


# Mapeo: nombre lógico -> archivo esperado en la carpeta de padrones
PADRONES_PROVINCIAS = {
    "ARBA":     "PadronARBA.csv",
    "CABA":     "PadronCABA.csv",
    "Cordoba":  "PadronCordoba.csv",
    "EntreRios":"PadronEntreRios.csv",
    "Formosa":  "PadronFormosa.csv",
    "Jujuy":    "PadronJujuy.csv",
    "Mendoza":  "PadronMendoza.csv",
    "SantaFe":  "PadronSantaFe.csv",
    "Tucuman":  "PadronTucuman.csv",
}


def buscar_en_padron(cuit_limpio: str, archivo: Path) -> Optional[dict]:
    """Busca un CUIT en un padrón CSV.

    Devuelve None si no está, o un dict con alícuotas si está.
    """
    if not archivo.exists():
        return None
    with archivo.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_cuit = "".join(filter(str.isdigit, row.get("cuit", "")))
            if row_cuit == cuit_limpio:
                return {
                    "encontrado": True,
                    "alicuota_retencion": row.get("alicuota_retencion", ""),
                    "alicuota_percepcion": row.get("alicuota_percepcion", ""),
                    "vigencia_desde": row.get("vigencia_desde", ""),
                    "vigencia_hasta": row.get("vigencia_hasta", ""),
                }
    return {"encontrado": False}


def consultar_todos(cuit_limpio: str, padrones_dir: Path) -> dict:
    """Consulta el CUIT en todos los padrones disponibles en la carpeta.

    Para cada provincia, devuelve:
      - 'no_disponible': si no hay archivo del padrón
      - 'no_inscripto': si hay archivo pero el CUIT no figura
      - 'inscripto' + alícuotas: si lo encuentra
    """
    resultados = {}
    for provincia, nombre_archivo in PADRONES_PROVINCIAS.items():
        archivo = padrones_dir / nombre_archivo
        if not archivo.exists():
            resultados[provincia] = {
                "status": "no_disponible",
                "detalle": f"No se encuentra el archivo {nombre_archivo} en la carpeta.",
            }
            continue
        res = buscar_en_padron(cuit_limpio, archivo)
        if res and res.get("encontrado"):
            resultados[provincia] = {
                "status": "inscripto",
                "detalle": (
                    f"Padrón vigente. Retención: {res['alicuota_retencion']}% · "
                    f"Percepción: {res['alicuota_percepcion']}% · "
                    f"Vigencia: {res['vigencia_desde']} a {res['vigencia_hasta']}"
                ),
                **res,
            }
        else:
            resultados[provincia] = {
                "status": "no_inscripto",
                "detalle": "El CUIT no figura en este padrón (no aplica retención/percepción).",
            }
    return resultados
