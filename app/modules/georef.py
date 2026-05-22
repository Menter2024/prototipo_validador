"""Consulta a la API pública de georef de datos.gob.ar.

Esta sí es una API real del gobierno argentino que responde sin auth.
La usamos para validar/normalizar la provincia del domicilio fiscal.

Endpoint: https://apis.datos.gob.ar/georef/api/provincias
"""
import httpx


def listar_provincias() -> list:
    """Devuelve la lista oficial de provincias argentinas."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get("https://apis.datos.gob.ar/georef/api/provincias")
        if r.status_code == 200:
            return [p["nombre"] for p in r.json().get("provincias", [])]
    except Exception:
        pass
    return []


def normalizar_provincia(texto: str) -> dict:
    """Busca en el texto del domicilio si menciona alguna provincia oficial."""
    if not texto:
        return {"provincia": None, "fuente": "georef.datos.gob.ar"}
    provincias = listar_provincias()
    texto_up = texto.upper()
    for p in provincias:
        if p.upper() in texto_up:
            return {"provincia": p, "fuente": "georef.datos.gob.ar"}
    # CABA aparece a veces como "CIUDAD AUTONOMA"
    if "CABA" in texto_up or "CIUDAD AUTONOMA" in texto_up or "CIUDAD AUTÓNOMA" in texto_up:
        return {"provincia": "Ciudad Autónoma de Buenos Aires", "fuente": "georef.datos.gob.ar"}
    return {"provincia": None, "fuente": "georef.datos.gob.ar"}
