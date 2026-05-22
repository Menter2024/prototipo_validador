"""Consulta a ARCA/AFIP vía afipsdk.com (flujo real de 2 pasos).

Flujo según docs.afipsdk.com:
  1) POST /api/v1/afip/auth      -> obtiene Ticket de Acceso (token + sign)
  2) POST /api/v1/afip/requests  -> consulta el padrón usando el TA

Documentación:
  https://docs.afipsdk.com/integracion/api
  https://docs.afipsdk.com/siguientes-pasos/web-services/padron-de-constancia-de-inscripcion

Si AFIPSDK_TOKEN está vacío, cae a modo demo.
Si AFIPSDK_ENV=dev (default), usa el CUIT de prueba 20409378472 de afipsdk.
Si AFIPSDK_ENV=prod, requiere certificado propio cargado en la cuenta afipsdk.com
y el CUIT de la empresa que lo posee en AFIPSDK_TAX_ID.
"""
import os
import time
import httpx
from typing import Optional, Tuple


AFIPSDK_BASE = "https://app.afipsdk.com/api/v1"

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


def _config() -> Tuple[str, str, str]:
    """Devuelve (access_token, environment, tax_id_representada)."""
    token = os.environ.get("AFIPSDK_TOKEN", "").strip()
    env = os.environ.get("AFIPSDK_ENV", "dev").strip() or "dev"
    # En dev, afipsdk permite usar este CUIT de prueba.
    # En prod hay que poner el CUIT de la empresa con certificado.
    default_tax = "20409378472" if env == "dev" else ""
    tax_id = os.environ.get("AFIPSDK_TAX_ID", default_tax).strip() or default_tax
    return token, env, tax_id


def _get_ta(access_token: str, env: str, tax_id: str) -> Optional[dict]:
    """Obtiene (o recupera del cache) el Ticket de Acceso para el WSID."""
    cache_key = f"{env}:{tax_id}:{WSID}"
    cached = _TA_CACHE.get(cache_key)
    # Renovamos si vence en menos de 5 minutos
    if cached and cached.get("expira_ts", 0) > time.time() + 300:
        return cached

    url = f"{AFIPSDK_BASE}/afip/auth"
    body = {"environment": env, "tax_id": tax_id, "wsid": WSID}
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
        # data: {token, sign, expiration}
        ta = {
            "token": data.get("token"),
            "sign": data.get("sign"),
            "expira_ts": time.time() + 11 * 3600,  # asumimos 11h de duración
        }
        _TA_CACHE[cache_key] = ta
        return ta
    except Exception as e:
        print(f"[afip_arca] auth excepcion: {e}")
        return None


def _consultar_padron(access_token: str, env: str, tax_id: str, ta: dict, cuit_limpio: str) -> Optional[dict]:
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


def _parse_persona(resp: dict) -> dict:
    """Normaliza la respuesta de getPersona_v2 al formato interno.

    La estructura real es algo como:
      { "persona": {
          "idPersona": ...,
          "tipoPersona": "FISICA"|"JURIDICA",
          "estadoClave": "ACTIVO",
          "nombre": "...",
          "razonSocial": "...",
          "tipoClave": "CUIT",
          "domicilioFiscal": { "direccion": "...", "localidad": "...", "descripcionProvincia": "..." },
          "impuesto": [{...}],
          "actividad": [{...}],
          "categoriaMonotributo": [...],
          ...
      }}
    """
    persona = resp.get("persona") or resp.get("data") or resp

    # nombre razón social (varía según tipo)
    razon = persona.get("razonSocial") or persona.get("nombre") or "—"
    if isinstance(razon, dict):
        razon = razon.get("razonSocial") or "—"

    # domicilio
    dom = persona.get("domicilioFiscal") or {}
    if isinstance(dom, list) and dom:
        dom = dom[0]
    dom_str = " ".join(filter(None, [
        dom.get("direccion") if isinstance(dom, dict) else None,
        dom.get("localidad") if isinstance(dom, dict) else None,
        dom.get("descripcionProvincia") if isinstance(dom, dict) else None,
    ])) or "—"

    # impuestos: IVA y Ganancias
    cond_iva = "—"
    cond_gan = "—"
    impuestos = persona.get("impuesto") or persona.get("impuestos") or []
    if isinstance(impuestos, dict):
        impuestos = [impuestos]
    for imp in impuestos:
        desc = (imp.get("descripcionImpuesto") or imp.get("descripcion") or "").upper()
        estado = imp.get("descripcionEstado") or imp.get("estado") or "—"
        if "IVA" in desc and cond_iva == "—":
            cond_iva = f"{desc} ({estado})"
        if "GANANCIAS" in desc and cond_gan == "—":
            cond_gan = f"{desc} ({estado})"
    if cond_iva == "—" and persona.get("categoriaMonotributo"):
        cond_iva = "MONOTRIBUTO"

    # actividad principal
    actividad = persona.get("actividad") or []
    if isinstance(actividad, dict):
        actividad = [actividad]
    act_str = "—"
    for a in actividad:
        if a.get("orden") == 1 or len(actividad) == 1:
            act_str = a.get("descripcionActividad") or a.get("descripcion") or "—"
            break

    return {
        "razon_social": razon,
        "tipo_persona": persona.get("tipoPersona", "—"),
        "estado_clave": persona.get("estadoClave", "—"),
        "condicion_iva": cond_iva,
        "condicion_ganancias": cond_gan,
        "domicilio_fiscal": dom_str,
        "actividad_principal": act_str,
        "fecha_inicio": persona.get("fechaInscripcion", "—"),
        "en_apoc": False,  # APOC requiere otro WSID — pendiente fase 1
    }


def consultar_constancia(cuit_limpio: str) -> dict:
    """Consulta la Constancia de Inscripción.

    Estrategia:
      1) Si hay AFIPSDK_TOKEN, hace flujo real auth -> requests.
      2) Si falla la API real, intenta fallback a datos demo.
      3) Si no hay token ni datos demo, devuelve placeholder.
    """
    access_token, env, tax_id = _config()
    modo = "demo"
    datos = None

    if access_token and tax_id:
        ta = _get_ta(access_token, env, tax_id)
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
            "detalle": "Sin datos para este CUIT. Verificá el token, el modo (dev/prod) y el endpoint.",
            "razon_social": "—",
            "estado_clave": "—",
            "condicion_iva": "—",
            "condicion_ganancias": "—",
            "domicilio_fiscal": "—",
            "actividad_principal": "—",
            "fecha_inicio": "—",
            "en_apoc": None,
        }

    return {
        "modo": modo,
        "encontrado": True,
        "detalle": "Datos en tiempo real desde AFIP/ARCA" if modo == "live" else "Datos de demostración",
        **datos,
    }
