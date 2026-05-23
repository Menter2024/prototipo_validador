"""Consultas online complementarias para fuentes sin padrón mensual.

Implementa adaptadores seguros cuando existe endpoint público sin CAPTCHA.
Las fuentes con CAPTCHA, credenciales o bloqueo anti-bot quedan como asistidas.
"""
from datetime import datetime
import httpx


FUENTES_ONLINE = {
    "Misiones": {
        "nombre": "Misiones / ATM",
        "url": "https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion",
        "endpoint": "https://sinclavefiscal.atm.misiones.gob.ar/bff/iibb/exentasygravadas/{cuit}/contribuyentes",
        "modo": "consulta_online",
        "automatizable": False,
        "detalle": "La página pública consulta por CUIT, pero el endpoint directo devuelve 403. Requiere adaptador con navegador o consulta asistida.",
    },
    "Neuquen": {
        "nombre": "Neuquén / Rentas",
        "url": "https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php",
        "endpoint": "https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion/php/ajax_cons_inscripcion.php",
        "modo": "consulta_online",
        "automatizable": True,
        "detalle": "Consulta automática contra endpoint público de constancia de inscripción.",
    },
    "RioNegro": {
        "nombre": "Río Negro / Agencia de Recaudación",
        "url": "https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/",
        "modo": "captcha",
        "automatizable": False,
        "detalle": "Fuente con CAPTCHA. Requiere consulta asistida/evidencia manual.",
    },
    "Corrientes": {
        "nombre": "Corrientes / DGR",
        "url": "https://www.dgrcorrientes.gob.ar/",
        "modo": "credenciales",
        "automatizable": False,
        "detalle": "Fuente con acceso por clave. Requiere credenciales o exportación.",
    },
}


def _formatear_cuit(cuit_limpio: str) -> str:
    return f"{cuit_limpio[:2]}-{cuit_limpio[2:10]}-{cuit_limpio[10:]}"


def _base_resultado(fuente_key: str, cuit_limpio: str, estado: str, detalle: str) -> dict:
    cfg = FUENTES_ONLINE[fuente_key]
    return {
        "fuente": fuente_key,
        "nombre": cfg["nombre"],
        "estado": estado,
        "detalle": detalle,
        "url_consulta": cfg["url"],
        "automatizable": cfg["automatizable"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cuit_limpio": cuit_limpio,
    }


def _consultar_neuquen(cuit_limpio: str) -> dict:
    cfg = FUENTES_ONLINE["Neuquen"]
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            r = client.post(
                cfg["endpoint"],
                data={"p_n_cuit": _formatear_cuit(cuit_limpio)},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Referer": cfg["url"],
                    "User-Agent": "Mozilla/5.0",
                },
            )
        if r.status_code != 200:
            return _base_resultado("Neuquen", cuit_limpio, "error", f"Neuquén respondió HTTP {r.status_code}.")
        data = r.json()
    except Exception as e:
        return _base_resultado("Neuquen", cuit_limpio, "error", f"No se pudo consultar Neuquén: {e}")

    if data.get("p_error") or data.get("p_d_mensaje"):
        return _base_resultado("Neuquen", cuit_limpio, "error", data.get("p_error") or data.get("p_d_mensaje"))

    tipo = data.get("p_c_tipo_tramite")
    tramite = data.get("p_id_tramite")
    if tipo == "CONS_INSC":
        return {
            **_base_resultado("Neuquen", cuit_limpio, "encontrado", "Figura inscripto en Neuquén."),
            "id_tramite": tramite,
            "tipo_tramite": tipo,
        }
    if tipo == "CONS_NINSC":
        return {
            **_base_resultado("Neuquen", cuit_limpio, "no_encontrado", "No figura inscripto en Neuquén."),
            "id_tramite": tramite,
            "tipo_tramite": tipo,
        }
    return {
        **_base_resultado("Neuquen", cuit_limpio, "revisar", f"Respuesta Neuquén no clasificada: {tipo or 'sin tipo'}."),
        "respuesta": data,
    }


def consultar_fuente(fuente_key: str, cuit_limpio: str) -> dict:
    cfg = FUENTES_ONLINE[fuente_key]
    if fuente_key == "Neuquen":
        return _consultar_neuquen(cuit_limpio)

    estado = {
        "consulta_online": "requiere_navegador",
        "captcha": "requiere_captcha",
        "credenciales": "requiere_credenciales",
    }[cfg["modo"]]
    return _base_resultado(fuente_key, cuit_limpio, estado, cfg["detalle"])


def consultar_todas(cuit_limpio: str) -> dict:
    return {key: consultar_fuente(key, cuit_limpio) for key in FUENTES_ONLINE}
