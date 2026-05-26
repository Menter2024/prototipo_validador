"""Lectura normalizada de padrones provinciales de Ingresos Brutos."""
import csv
import io
import re
from pathlib import Path
from typing import Optional


PADRONES_PROVINCIAS = {
    "ARBA": {
        "archivo": "PadronARBA.csv",
        "nombre": "Buenos Aires / ARBA",
        "prioridad": "P1",
        "tipo": "archivo",
    },
    "CABA": {
        "archivo": "PadronCABA.csv",
        "nombre": "CABA / AGIP",
        "prioridad": "P1",
        "tipo": "archivo",
    },
    "EntreRios": {
        "archivo": "PadronEntreRios.csv",
        "nombre": "Entre Ríos / ATER",
        "prioridad": "P1",
        "tipo": "archivo",
    },
    "Cordoba": {
        "archivo": "PadronCordoba.csv",
        "nombre": "Córdoba",
        "prioridad": "P2",
        "tipo": "archivo",
    },
    "Formosa": {
        "archivo": "PadronFormosa.csv",
        "nombre": "Formosa",
        "prioridad": "P2",
        "tipo": "archivo",
    },
    "Jujuy": {
        "archivo": "PadronJujuy.csv",
        "nombre": "Jujuy",
        "prioridad": "P2",
        "tipo": "archivo",
    },
    "Mendoza": {
        "archivo": "PadronMendoza.csv",
        "nombre": "Mendoza",
        "prioridad": "P2",
        "tipo": "archivo",
    },
    "SantaFe": {
        "archivo": "PadronSantaFe.csv",
        "nombre": "Santa Fe",
        "prioridad": "P2",
        "tipo": "archivo",
    },
    "Tucuman": {
        "archivo": "PadronTucuman.csv",
        "nombre": "Tucumán",
        "prioridad": "P2",
        "tipo": "archivo",
    },
    "Misiones": {
        "archivo": None,
        "nombre": "Misiones / ATM",
        "prioridad": "P3",
        "tipo": "consulta_manual",
        "url": "https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion",
        "detalle": "Fuente pública relevada sin padrón mensual normalizado. Requiere consulta online por CUIT.",
    },
    "Neuquen": {
        "archivo": None,
        "nombre": "Neuquén / Rentas",
        "prioridad": "P3",
        "tipo": "consulta_manual",
        "url": "https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php",
        "detalle": "Fuente pública relevada sin padrón mensual normalizado. Requiere consulta online por CUIT.",
    },
    "RioNegro": {
        "archivo": None,
        "nombre": "Río Negro / Agencia de Recaudación",
        "prioridad": "P3",
        "tipo": "consulta_manual",
        "url": "https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/",
        "detalle": "Fuente con CAPTCHA relevada. Requiere consulta asistida o integración específica.",
    },
    "Corrientes": {
        "archivo": None,
        "nombre": "Corrientes / DGR",
        "prioridad": "P3",
        "tipo": "requiere_credenciales",
        "url": "https://www.dgrcorrientes.gob.ar/",
        "detalle": "Fuente relevada con acceso por clave. Requiere credenciales o archivo exportado.",
    },
}

ALIASES = {
    "cuit": {"cuit", "cuil", "cuit/cuil", "cuit_contribuyente", "cuit sujeto", "cuit_sujeto", "nro_cuit", "nro cuit", "numero_cuit", "numero de cuit", "número de cuit"},
    "alicuota_retencion": {"alicuota_retencion", "retencion", "retención", "ali_ret", "alic_ret", "alic ret", "alicuota retencion", "alícuota retención", "alicuota de retencion", "alícuota de retención", "alic retencion", "alic. ret.", "ret"},
    "alicuota_percepcion": {"alicuota_percepcion", "percepcion", "percepción", "ali_per", "alic_per", "alic perc", "alicuota percepcion", "alícuota percepción", "alicuota de percepcion", "alícuota de percepción", "alic percepcion", "alic. perc.", "perc"},
    "vigencia_desde": {"vigencia_desde", "desde", "fecha_desde", "fecha desde", "fecha vigencia desde", "vig desde", "vig. desde", "inicio"},
    "vigencia_hasta": {"vigencia_hasta", "hasta", "fecha_hasta", "fecha hasta", "fecha vigencia hasta", "vig hasta", "vig. hasta", "fin"},
    "regimen": {"regimen", "régimen", "tipo", "categoria", "categoría", "categoria fiscal", "categoría fiscal"},
}

_PADRON_CACHE: dict = {}


def _norm_header(valor: str) -> str:
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    limpio = (valor or "").translate(reemplazos).strip().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", limpio).split())


def _normalizar_row(row: dict) -> dict:
    normalizado = {}
    headers = {_norm_header(k): v for k, v in row.items()}
    for destino, aliases in ALIASES.items():
        aliases_norm = {_norm_header(a) for a in aliases}
        for header, valor in headers.items():
            if header in aliases_norm:
                normalizado[destino] = (valor or "").strip()
                break
    return normalizado


def _leer_texto(archivo: Path) -> str:
    data = archivo.read_bytes()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _leer_padron(archivo: Path) -> list[dict]:
    stat = archivo.stat()
    cache_key = (str(archivo), stat.st_mtime_ns, stat.st_size)
    if cache_key in _PADRON_CACHE:
        return _PADRON_CACHE[cache_key]

    texto = _leer_texto(archivo)
    try:
        dialect = csv.Sniffer().sniff(texto[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = [_normalizar_row(row) for row in csv.DictReader(io.StringIO(texto), dialect=dialect)]
    rows = [r for r in rows if r.get("cuit")]
    _PADRON_CACHE.clear()
    _PADRON_CACHE[cache_key] = rows
    return rows


def _fmt_pct(valor: str) -> str:
    if not valor:
        return "—"
    return valor.replace(",", ".").replace("%", "").strip()


def buscar_en_padron(cuit_limpio: str, archivo: Path) -> Optional[dict]:
    """Busca un CUIT en un padrón CSV con cabeceras normalizadas."""
    if not archivo.exists():
        return None
    for row in _leer_padron(archivo):
        row_cuit = "".join(filter(str.isdigit, row.get("cuit", "")))
        if row_cuit == cuit_limpio:
            return {
                "encontrado": True,
                "alicuota_retencion": _fmt_pct(row.get("alicuota_retencion", "")),
                "alicuota_percepcion": _fmt_pct(row.get("alicuota_percepcion", "")),
                "vigencia_desde": row.get("vigencia_desde", ""),
                "vigencia_hasta": row.get("vigencia_hasta", ""),
                "regimen": row.get("regimen", ""),
            }
    return {"encontrado": False}


def consultar_todos(cuit_limpio: str, padrones_dir: Path) -> dict:
    """Consulta el CUIT en todos los padrones disponibles en la carpeta."""
    resultados = {}
    for provincia, cfg in PADRONES_PROVINCIAS.items():
        nombre_archivo = cfg["archivo"]
        if cfg.get("tipo") != "archivo":
            resultados[provincia] = {
                "status": cfg["tipo"],
                "detalle": cfg["detalle"],
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
                "url": cfg.get("url"),
            }
            continue

        archivo = padrones_dir / nombre_archivo
        if not archivo.exists():
            resultados[provincia] = {
                "status": "no_disponible",
                "detalle": f"No se encuentra el archivo {nombre_archivo} en la carpeta.",
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
            }
            continue
        res = buscar_en_padron(cuit_limpio, archivo)
        if res and res.get("encontrado"):
            regimen = f" · Régimen: {res['regimen']}" if res.get("regimen") else ""
            resultados[provincia] = {
                "status": "inscripto",
                "detalle": (
                    f"Padrón vigente. Retención: {res['alicuota_retencion']}% · "
                    f"Percepción: {res['alicuota_percepcion']}% · "
                    f"Vigencia: {res['vigencia_desde']} a {res['vigencia_hasta']}{regimen}"
                ),
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
                **res,
            }
        else:
            resultados[provincia] = {
                "status": "no_inscripto",
                "detalle": "El CUIT no figura en este padrón (no aplica retención/percepción).",
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
            }
    return resultados
