"""Consultas online complementarias para fuentes sin padrón mensual.

P0 implementa la arquitectura y estados normalizados. Para evitar consultas frágiles
o CAPTCHA-breaking, las fuentes quedan como consulta asistida con URL directa hasta
implementar adaptadores específicos con Playwright o API oficial.
"""
from datetime import datetime


FUENTES_ONLINE = {
    "Misiones": {
        "nombre": "Misiones / ATM",
        "url": "https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion",
        "modo": "consulta_online",
        "automatizable": True,
        "detalle": "Consulta pública online por CUIT. Pendiente adaptador automático.",
    },
    "Neuquen": {
        "nombre": "Neuquén / Rentas",
        "url": "https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php",
        "modo": "consulta_online",
        "automatizable": True,
        "detalle": "Consulta pública online por CUIT. Pendiente adaptador automático.",
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


def consultar_fuente(fuente_key: str, cuit_limpio: str) -> dict:
    cfg = FUENTES_ONLINE[fuente_key]
    estado = {
        "consulta_online": "pendiente_automatizacion",
        "captcha": "requiere_captcha",
        "credenciales": "requiere_credenciales",
    }[cfg["modo"]]
    return {
        "fuente": fuente_key,
        "nombre": cfg["nombre"],
        "estado": estado,
        "detalle": cfg["detalle"],
        "url_consulta": cfg["url"],
        "automatizable": cfg["automatizable"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cuit_limpio": cuit_limpio,
    }


def consultar_todas(cuit_limpio: str) -> dict:
    return {key: consultar_fuente(key, cuit_limpio) for key in FUENTES_ONLINE}
