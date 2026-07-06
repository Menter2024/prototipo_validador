"""Lectura normalizada de padrones provinciales de Ingresos Brutos."""
import csv
import io
import os
import re
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from app.modules import padron_manifest, supabase_mvp


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

# Cache LRU de índices por CUIT: conserva varios padrones a la vez para que un
# lote de N CUITs parsee cada archivo una sola vez (antes, capacidad 1 → re-parseo).
_INDEX_CACHE: "OrderedDict[tuple, dict[str, dict]]" = OrderedDict()


def _cache_max() -> int:
    try:
        return max(1, int(os.environ.get("PADRONES_CACHE_MAX", "12")))
    except ValueError:
        return 12


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


def _leer_padron(archivo: Path) -> dict[str, dict]:
    """Devuelve un índice {cuit_limpio: fila_normalizada} del padrón (cacheado)."""
    stat = archivo.stat()
    cache_key = (str(archivo), stat.st_mtime_ns, stat.st_size)
    cached = _INDEX_CACHE.get(cache_key)
    if cached is not None:
        _INDEX_CACHE.move_to_end(cache_key)
        return cached

    texto = _leer_texto(archivo)
    try:
        dialect = csv.Sniffer().sniff(texto[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    indice: dict[str, dict] = {}
    for row in csv.DictReader(io.StringIO(texto), dialect=dialect):
        normalizado = _normalizar_row(row)
        cuit = "".join(filter(str.isdigit, normalizado.get("cuit", "")))
        if cuit:
            # Ante CUIT duplicado se conserva la primera aparición (comportamiento histórico).
            indice.setdefault(cuit, normalizado)

    _INDEX_CACHE[cache_key] = indice
    while len(_INDEX_CACHE) > _cache_max():
        _INDEX_CACHE.popitem(last=False)
    return indice


def _fmt_pct(valor: str) -> str:
    if not valor:
        return "—"
    return valor.replace(",", ".").replace("%", "").strip()


def buscar_en_padron(cuit_limpio: str, archivo: Path) -> Optional[dict]:
    """Busca un CUIT en un padrón CSV con cabeceras normalizadas (índice O(1))."""
    if not archivo.exists():
        return None
    row = _leer_padron(archivo).get(cuit_limpio)
    if row is None:
        return {"encontrado": False}
    return {
        "encontrado": True,
        "alicuota_retencion": _fmt_pct(row.get("alicuota_retencion", "")),
        "alicuota_percepcion": _fmt_pct(row.get("alicuota_percepcion", "")),
        "vigencia_desde": row.get("vigencia_desde", ""),
        "vigencia_hasta": row.get("vigencia_hasta", ""),
        "regimen": row.get("regimen", ""),
    }


def _describir_vigencia(vigencia_estado: str, vigencia_hasta: str) -> str:
    return {
        "vigente": "Padrón vigente.",
        "por_vencer": f"Padrón por vencer (hasta {vigencia_hasta}).",
        "vencido": f"PADRÓN VENCIDO (vigencia hasta {vigencia_hasta}) — alícuotas potencialmente desactualizadas.",
        "sin_vigencia": "Padrón cargado sin vigencia registrada.",
    }[vigencia_estado]


def consultar_todos(cuit_limpio: str, padrones_dir: Path) -> dict:
    """Consulta el CUIT en todos los padrones disponibles en la carpeta."""
    resultados = {}
    manifest_padrones = padron_manifest.cargar_manifest(padrones_dir).get("padrones", {})
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
        meta = manifest_padrones.get(provincia, {})
        vigencia_hasta_padron = (meta.get("vigencia_hasta") or "").strip()
        vigencia_estado = padron_manifest.estado_vigencia(vigencia_hasta_padron)
        res = None
        disponible_supabase = False
        try:
            res = supabase_mvp.buscar_padron_registro(cuit_limpio, provincia)
            disponible_supabase = bool(res) or supabase_mvp.provincia_tiene_padron_activo(provincia)
        except Exception:
            res = None

        if not res and archivo.exists():
            res = buscar_en_padron(cuit_limpio, archivo)

        # Sin vigencia en el manifest, usar la del registro (ruta Supabase o padrón con columna propia).
        if vigencia_estado == "sin_vigencia" and res and res.get("vigencia_hasta"):
            vigencia_hasta_padron = res["vigencia_hasta"]
            vigencia_estado = padron_manifest.estado_vigencia(vigencia_hasta_padron)

        if not res and not archivo.exists():
            resultados[provincia] = {
                "status": "no_disponible",
                "detalle": f"No se encuentra el archivo {nombre_archivo} en la carpeta ni padrón activo en Supabase.",
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
            }
            continue

        if not res and disponible_supabase:
            resultados[provincia] = {
                "status": "no_inscripto",
                "detalle": (
                    "El CUIT no figura en este padrón Supabase activo. El tratamiento del sujeto no "
                    "incluido depende del régimen de la jurisdicción (puede corresponder alícuota "
                    "general, residual o máxima); confirmar la norma vigente antes de definir no retener/percibir."
                ),
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
                "fuente": "supabase",
                "vigencia_estado": vigencia_estado,
                "vigencia_hasta_padron": vigencia_hasta_padron,
            }
            continue
        if res and res.get("encontrado"):
            regimen = f" · Régimen: {res['regimen']}" if res.get("regimen") else ""
            resultados[provincia] = {
                "status": "inscripto",
                "detalle": (
                    f"{_describir_vigencia(vigencia_estado, vigencia_hasta_padron)} "
                    f"Retención: {res['alicuota_retencion']}% · "
                    f"Percepción: {res['alicuota_percepcion']}% · "
                    f"Vigencia: {res['vigencia_desde']} a {res['vigencia_hasta']}{regimen}"
                ),
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
                "vigencia_estado": vigencia_estado,
                "vigencia_hasta_padron": vigencia_hasta_padron,
                **res,
            }
        else:
            resultados[provincia] = {
                "status": "no_inscripto",
                "detalle": (
                    "El CUIT no figura en este padrón. El tratamiento del sujeto no incluido depende "
                    "del régimen de la jurisdicción (puede corresponder alícuota general, residual o "
                    "máxima); confirmar la norma vigente antes de definir no retener/percibir."
                ),
                "nombre": cfg["nombre"],
                "prioridad": cfg["prioridad"],
                "vigencia_estado": vigencia_estado,
                "vigencia_hasta_padron": vigencia_hasta_padron,
            }
    return resultados
