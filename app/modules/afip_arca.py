"""Consulta a ARCA/AFIP vía afipsdk.com (flujo real de 2 pasos).

Flujo según docs.afipsdk.com:
  1) POST /api/v1/afip/auth      -> obtiene Ticket de Acceso (token + sign)
                                   En modo "prod" se mandan cert y key en el body.
  2) POST /api/v1/afip/requests  -> consulta el padrón usando el TA

Documentación:
  https://docs.afipsdk.com/integracion/api
  https://docs.afipsdk.com/siguientes-pasos/web-services/padron-de-constancia-de-inscripcion

Variables de entorno:
  AFIPSDK_TOKEN    -> access_token de afipsdk.com (obligatorio para live)
  AFIPSDK_ENV      -> "dev" (default) o "prod"
  AFIPSDK_TAX_ID   -> CUIT de la empresa que representa (11 dígitos sin guiones)
  AFIPSDK_CERT     -> path al archivo .crt (solo prod, ej.
                      ~/Documents/menter-certificados-afip/Menter.crt)
  AFIPSDK_KEY      -> path al archivo .key (solo prod)

Si AFIPSDK_TOKEN está vacío, cae a modo demo.
"""
import os
import time
import base64
from pathlib import Path
import httpx
from typing import Optional, Tuple


AFIPSDK_BASE = "https://app.afipsdk.com/api/v1"
PROVINCIAS_AR = {
    "BUENOS AIRES",
    "CABA",
    "CIUDAD AUTONOMA DE BUENOS AIRES",
    "CAPITAL FEDERAL",
    "CATAMARCA",
    "CHACO",
    "CHUBUT",
    "CORDOBA",
    "CORRIENTES",
    "ENTRE RIOS",
    "FORMOSA",
    "JUJUY",
    "LA PAMPA",
    "LA RIOJA",
    "MENDOZA",
    "MISIONES",
    "NEUQUEN",
    "RIO NEGRO",
    "SALTA",
    "SAN JUAN",
    "SAN LUIS",
    "SANTA CRUZ",
    "SANTA FE",
    "SANTIAGO DEL ESTERO",
    "TIERRA DEL FUEGO",
    "TUCUMAN",
}
PROVINCIAS_CANON = {
    "CIUDAD AUTONOMA DE BUENOS AIRES": "CABA",
    "CAPITAL FEDERAL": "CABA",
    "CORDOBA": "Córdoba",
    "ENTRE RIOS": "Entre Ríos",
    "NEUQUEN": "Neuquén",
    "RIO NEGRO": "Río Negro",
    "TUCUMAN": "Tucumán",
}

# Cache del Ticket de Acceso en memoria (TAs duran ~12 hs)
_TA_CACHE: dict = {}

# CUITs con datos predefinidos para fallback de modo demo
DEMO_DATA = {
    "33693450239": {
        "razon_social": "ADMINISTRACION FEDERAL DE INGRESOS PUBLICOS",
        "tipo_persona": "JURIDICA",
        "estado_clave": "ACTIVO",
        "condicion_iva": "RESPONSABLE INSCRIPTO",
        "condicion_ganancias": "INSCRIPTO",
        "domicilio_fiscal": "HIPOLITO YRIGOYEN 370, CABA",
        "actividad_principal": "Administración pública",
        "fecha_inicio": "01/01/1997",
        "en_apoc": False,
    },
    "30500010912": {
        "razon_social": "BANCO DE LA NACION ARGENTINA",
        "tipo_persona": "JURIDICA",
        "estado_clave": "ACTIVO",
        "condicion_iva": "RESPONSABLE INSCRIPTO",
        "condicion_ganancias": "INSCRIPTO",
        "domicilio_fiscal": "BARTOLOME MITRE 326, CABA",
        "actividad_principal": "Intermediación financiera",
        "fecha_inicio": "01/01/1891",
        "en_apoc": False,
    },
    "30546689979": {
        "razon_social": "YPF SOCIEDAD ANONIMA",
        "tipo_persona": "JURIDICA",
        "estado_clave": "ACTIVO",
        "condicion_iva": "RESPONSABLE INSCRIPTO",
        "condicion_ganancias": "INSCRIPTO",
        "domicilio_fiscal": "MACACHA GUEMES 515, CABA",
        "actividad_principal": "Extracción de petróleo crudo",
        "fecha_inicio": "01/01/1922",
        "en_apoc": False,
    },
}

WSID = "ws_sr_constancia_inscripcion"


def _config() -> Tuple[str, str, str, Optional[str], Optional[str]]:
    """Devuelve (access_token, env, tax_id, cert_path, key_path)."""
    token = os.environ.get("AFIPSDK_TOKEN", "").strip()
    env = os.environ.get("AFIPSDK_ENV", "dev").strip() or "dev"
    default_tax = "20409378472" if env == "dev" else ""
    tax_id = os.environ.get("AFIPSDK_TAX_ID", default_tax).strip() or default_tax
    cert = os.environ.get("AFIPSDK_CERT", "").strip() or None
    key = os.environ.get("AFIPSDK_KEY", "").strip() or None
    # Expandir ~ a $HOME
    if cert:
        cert = str(Path(cert).expanduser())
    if key:
        key = str(Path(key).expanduser())
    return token, env, tax_id, cert, key


def _normalizar_pem(valor: str) -> str:
    """Normaliza PEM pegado en variables de entorno."""
    return valor.strip().replace("\\n", "\n").replace("\\r", "\r")


def _leer_cert_o_key(path: Optional[str], env_var_pem: str) -> Optional[str]:
    """Obtiene el contenido del cert o key.

    Prioridad:
      1) Variable de entorno con contenido PEM directo (para deploys cloud).
         Ej.: AFIPSDK_CERT_PEM="-----BEGIN CERTIFICATE-----\\nMIIDRDCC..."
      2) Variable de entorno base64 (AFIPSDK_CERT_B64/AFIPSDK_KEY_B64).
      3) AFIPSDK_CERT/AFIPSDK_KEY con contenido PEM directo (compatibilidad).
      4) Archivo local en `path` (para desarrollo en la Mac de Berna).

    Devuelve None si ninguno está disponible.
    """
    # 1) Probar env var con contenido directo (Railway, Fly.io, etc.)
    pem = os.environ.get(env_var_pem, "").strip()
    if pem:
        # Soportar \n literal por si lo pegaron así en el dashboard del host
        return _normalizar_pem(pem)

    # 2) Probar base64 (más seguro para dashboards que rompen saltos de línea)
    b64_var = env_var_pem.replace("_PEM", "_B64")
    b64 = os.environ.get(b64_var, "").strip()
    if b64:
        try:
            return base64.b64decode(b64).decode("utf-8")
        except Exception as e:
            print(f"[afip_arca] error decodificando {b64_var}: {e}")
            return None

    # 3) Compatibilidad: AFIPSDK_CERT/AFIPSDK_KEY pueden traer PEM directo
    if path and "-----BEGIN" in path:
        return _normalizar_pem(path)

    # 4) Fallback a archivo en disco
    if not path:
        return None
    try:
        p = Path(path)
        if not p.exists():
            print(f"[afip_arca] archivo no encontrado: {path}  (tampoco hay env var {env_var_pem})")
            return None
        return p.read_text()
    except Exception as e:
        print(f"[afip_arca] error leyendo {path}: {e}")
        return None


def _get_ta(access_token: str, env: str, tax_id: str,
            cert_path: Optional[str], key_path: Optional[str]) -> Optional[dict]:
    """Obtiene (o recupera del cache) el Ticket de Acceso para el WSID."""
    cache_key = f"{env}:{tax_id}:{WSID}"
    cached = _TA_CACHE.get(cache_key)
    if cached and cached.get("expira_ts", 0) > time.time() + 300:
        return cached

    url = f"{AFIPSDK_BASE}/afip/auth"
    body = {"environment": env, "tax_id": tax_id, "wsid": WSID}

    # En modo prod, afipsdk necesita el certificado y la clave en cada auth
    if env == "prod":
        cert_content = _leer_cert_o_key(cert_path, "AFIPSDK_CERT_PEM")
        key_content = _leer_cert_o_key(key_path, "AFIPSDK_KEY_PEM")
        if not cert_content or not key_content:
            print(f"[afip_arca] modo prod requiere certificado y clave. "
                  f"Configurá AFIPSDK_CERT_PEM/AFIPSDK_KEY_PEM (deploy) o AFIPSDK_CERT/AFIPSDK_KEY (local).")
            return None
        body["cert"] = cert_content
        body["key"] = key_content

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        if r.status_code != 200:
            print(f"[afip_arca] auth fallo status={r.status_code} body={r.text[:300]}")
            return None
        data = r.json()
        ta = {
            "token": data.get("token"),
            "sign": data.get("sign"),
            "expira_ts": time.time() + 11 * 3600,
        }
        _TA_CACHE[cache_key] = ta
        return ta
    except Exception as e:
        print(f"[afip_arca] auth excepcion: {e}")
        return None


def _consultar_padron(access_token: str, env: str, tax_id: str,
                      ta: dict, cuit_limpio: str) -> Optional[dict]:
    """Hace la consulta real al padrón usando el TA."""
    url = f"{AFIPSDK_BASE}/afip/requests"
    body = {
        "environment": env,
        "method": "getPersona_v2",
        "wsid": WSID,
        "params": {
            "token": ta["token"],
            "sign": ta["sign"],
            "cuitRepresentada": tax_id,
            "idPersona": int(cuit_limpio),
        },
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        if r.status_code != 200:
            print(f"[afip_arca] padron fallo status={r.status_code} body={r.text[:300]}")
            return None
        return r.json()
    except Exception as e:
        print(f"[afip_arca] padron excepcion: {e}")
        return None


def _map_estado_impuesto(codigo: str) -> str:
    """Convierte el código de estado de impuesto a texto legible."""
    return {
        "AC": "ACTIVO",
        "EX": "EXENTO",
        "BA": "BAJA",
        "NA": "NO ALCANZADO",
    }.get(codigo, codigo or "—")


def _sin_acentos(valor: str) -> str:
    return (valor or "").translate(str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")).upper()


def _iter_textos(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            yield from _iter_textos(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_textos(item)
    elif obj is not None:
        yield str(obj)


def _canon_provincia(valor: str) -> str:
    limpio = _sin_acentos(valor)
    return PROVINCIAS_CANON.get(limpio, valor.title())


def _extraer_iibb(pr: dict, impuestos_total: list[dict]) -> dict:
    """Extrae señales de IIBB/Convenio Multilateral desde constancia ARCA.

    La constancia de inscripción ARCA puede incluir inscripción en Convenio
    Multilateral y jurisdicciones declaradas. El WS puede variar nombres de
    campos; por eso combinamos impuestos normalizados y búsqueda defensiva de
    jurisdicciones/provincias en la respuesta.
    """
    impuestos_iibb = []
    regimen = "—"
    for imp in impuestos_total:
        desc = imp.get("descripcionImpuesto") or imp.get("descripcion") or ""
        desc_norm = _sin_acentos(desc)
        if "INGRESOS BRUTOS" in desc_norm or "IIBB" in desc_norm or "CONVENIO MULTILATERAL" in desc_norm:
            estado = _map_estado_impuesto(imp.get("estadoImpuesto") or imp.get("estado"))
            impuestos_iibb.append({"descripcion": desc, "estado": estado})
            if "CONVENIO MULTILATERAL" in desc_norm:
                regimen = "Convenio Multilateral"
            elif regimen == "—":
                regimen = "Ingresos Brutos"

    textos = [_sin_acentos(t) for t in _iter_textos(pr)]
    jurisdicciones = set()
    hay_iibb_contexto = any(
        "INGRESOS BRUTOS" in t or "IIBB" in t or "CONVENIO MULTILATERAL" in t or "JURISDICC" in t
        for t in textos
    )
    if hay_iibb_contexto:
        joined = " | ".join(textos)
        for provincia in PROVINCIAS_AR:
            if provincia in joined:
                jurisdicciones.add(_canon_provincia(provincia))

    return {
        "regimen": regimen,
        "jurisdicciones": sorted(jurisdicciones),
        "impuestos": impuestos_iibb,
        "fuente": "ARCA Constancia de Inscripción",
        "detalle": (
            "La constancia ARCA puede informar Convenio Multilateral y jurisdicciones declaradas; "
            "las inscripciones locales exclusivas pueden no figurar allí y requieren padrón/consulta provincial."
        ) if impuestos_iibb or jurisdicciones else "Sin señales de IIBB/Convenio Multilateral en la respuesta ARCA normalizada; no descarta inscripción local provincial.",
    }


def _parse_persona(resp: dict) -> dict:
    """Normaliza la respuesta de getPersona_v2 al formato interno.

    Estructura real de afipsdk / WS_SR_PADRON_A13:
      {
        "personaReturn": {
          "datosGenerales": {
            "razonSocial" / "apellido" + "nombre",
            "tipoPersona": "FISICA" | "JURIDICA",
            "estadoClave": "ACTIVO",
            "domicilioFiscal": { direccion, localidad, descripcionProvincia, ... },
            "fechaContratoSocial" / "fechaNacimiento",
            ...
          },
          "datosRegimenGeneral": {
            "actividad": [...],
            "impuesto": [{ descripcionImpuesto, estadoImpuesto: "AC"|"EX"|"BA", ... }]
          },
          "datosMonotributo": {  # solo si es monotributista
            "actividad": [...],
            "categoriaMonotributo": {...},
            "impuesto": [...]
          },
          "errorMonotributo" / "errorConstancia": ...  # si hay errores
        }
      }
    """
    pr = resp.get("personaReturn") or resp.get("persona") or resp.get("data") or resp
    if not isinstance(pr, dict) or not (pr.get("datosGenerales") or pr.get("razonSocial") or pr.get("apellido")):
        err = resp.get("error") or resp.get("fault") or resp.get("message") or resp.get("faultstring") or "respuesta sin datosGenerales"
        raise ValueError(f"respuesta AFIP sin datos de persona: {err}")
    dg = pr.get("datosGenerales") or pr
    drg = pr.get("datosRegimenGeneral") or {}
    dmo = pr.get("datosMonotributo") or {}

    tipo = dg.get("tipoPersona", "—")

    # Nombre / razón social según tipo
    if tipo == "FISICA":
        apellido = dg.get("apellido", "")
        nombre = dg.get("nombre", "")
        razon = f"{apellido}, {nombre}".strip(", ") or "—"
    else:
        razon = dg.get("razonSocial") or "—"

    # Domicilio fiscal
    dom = dg.get("domicilioFiscal") or {}
    if isinstance(dom, list) and dom:
        dom = dom[0]
    dom_str = ", ".join(filter(None, [
        dom.get("direccion") if isinstance(dom, dict) else None,
        dom.get("localidad") if isinstance(dom, dict) else None,
        dom.get("descripcionProvincia") if isinstance(dom, dict) else None,
    ])) or "—"

    # Impuestos: combinamos régimen general y monotributo
    impuestos_total = []
    for fuente in (drg.get("impuesto"), dmo.get("impuesto")):
        if isinstance(fuente, dict):
            impuestos_total.append(fuente)
        elif isinstance(fuente, list):
            impuestos_total.extend(fuente)

    cond_iva = "—"
    cond_gan = "—"
    for imp in impuestos_total:
        desc = (imp.get("descripcionImpuesto") or imp.get("descripcion") or "").upper()
        estado = _map_estado_impuesto(imp.get("estadoImpuesto") or imp.get("estado"))
        # IVA puro o IVA + algo (SIRE-IVA, etc.)
        if "IVA" in desc and "MONOTRIBUTO" not in desc and cond_iva == "—":
            cond_iva = f"{desc} ({estado})"
        # Ganancias (GANANCIAS SOCIEDADES, IMPTO.A LAS GANANCIAS, etc.)
        if "GANANCIAS" in desc and cond_gan == "—":
            cond_gan = f"{desc} ({estado})"

    # Si tiene categoría de monotributo, eso sobreescribe IVA
    cat_mono = dmo.get("categoriaMonotributo")
    if cat_mono:
        cat_desc = cat_mono.get("descripcionCategoria", "") if isinstance(cat_mono, dict) else ""
        cond_iva = f"MONOTRIBUTO — Categoría {cat_desc}".strip(" —")

    # Actividad principal: prioridad régimen general, fallback monotributo
    act_str = "—"
    for fuente in (drg.get("actividad"), dmo.get("actividad")):
        if not fuente:
            continue
        actividades = [fuente] if isinstance(fuente, dict) else fuente
        for a in actividades:
            if a.get("orden") == 1 or len(actividades) == 1:
                desc = a.get("descripcionActividad") or a.get("descripcion")
                if desc:
                    act_str = desc
                    break
        if act_str != "—":
            break

    # Fecha de inicio: contrato social (jurídicas) o nacimiento/inscripción (físicas)
    fecha = dg.get("fechaContratoSocial") or dg.get("fechaNacimiento") or dg.get("fechaInscripcion") or "—"
    # Acortar timestamp ISO si vino con hora
    if isinstance(fecha, str) and "T" in fecha:
        fecha = fecha.split("T")[0]

    return {
        "razon_social": razon,
        "tipo_persona": tipo,
        "estado_clave": dg.get("estadoClave", "—"),
        "condicion_iva": cond_iva,
        "condicion_ganancias": cond_gan,
        "inscripciones_iibb": _extraer_iibb(pr, impuestos_total),
        "domicilio_fiscal": dom_str,
        "actividad_principal": act_str,
        "fecha_inicio": fecha,
        "en_apoc": False,  # APOC requiere otro WSID — pendiente fase 1
    }


def consultar_constancia(cuit_limpio: str) -> dict:
    """Consulta la Constancia de Inscripción.

    Estrategia:
      1) Si hay AFIPSDK_TOKEN, hace flujo real auth -> requests.
      2) Si falla la API real, fallback a datos demo.
      3) Si no hay token ni datos demo, devuelve placeholder.
    """
    access_token, env, tax_id, cert_path, key_path = _config()
    modo = "demo"
    datos = None

    if access_token and tax_id:
        ta = _get_ta(access_token, env, tax_id, cert_path, key_path)
        if ta:
            resp = _consultar_padron(access_token, env, tax_id, ta, cuit_limpio)
            if resp:
                try:
                    datos = _parse_persona(resp)
                    modo = "live"
                except Exception as e:
                    print(f"[afip_arca] parse error: {e}")
                    datos = None

    if datos is None:
        datos = DEMO_DATA.get(cuit_limpio)

    if datos is None:
        return {
            "modo": "demo",
            "encontrado": False,
            "detalle": "Sin datos para este CUIT. Verificá token, modo (dev/prod), cert/key y endpoint.",
            "razon_social": "—",
            "estado_clave": "—",
            "condicion_iva": "—",
            "condicion_ganancias": "—",
            "inscripciones_iibb": {
                "regimen": "—",
                "jurisdicciones": [],
                "impuestos": [],
                "fuente": "ARCA Constancia de Inscripción",
                "detalle": "Sin datos ARCA para determinar inscripción IIBB/Convenio Multilateral.",
            },
            "domicilio_fiscal": "—",
            "actividad_principal": "—",
            "fecha_inicio": "—",
            "en_apoc": None,
        }

    datos.setdefault("inscripciones_iibb", {
        "regimen": "—",
        "jurisdicciones": [],
        "impuestos": [],
        "fuente": "ARCA Constancia de Inscripción",
        "detalle": "No normalizado en datos demo/fallback.",
    })

    return {
        "modo": modo,
        "encontrado": True,
        "detalle": "Datos en tiempo real desde AFIP/ARCA" if modo == "live" else "Datos de demostración",
        **datos,
    }
