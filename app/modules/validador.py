"""Validador matemático de CUIT/CUIL argentino.

Verifica el dígito verificador (DV) según el algoritmo oficial de AFIP.
Es 100% offline — no requiere internet ni credenciales.
"""
import re

# Coeficientes oficiales del algoritmo de validación
COEFICIENTES = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def limpiar(cuit: str) -> str:
    """Quita guiones, espacios y puntos."""
    return re.sub(r"[^0-9]", "", cuit or "")


def formatear(cuit: str) -> str:
    """Formatea como XX-XXXXXXXX-X."""
    c = limpiar(cuit)
    if len(c) != 11:
        return cuit
    return f"{c[:2]}-{c[2:10]}-{c[10]}"


def tipo_persona(cuit: str) -> str:
    """A partir del prefijo del CUIT, devuelve el tipo de persona."""
    c = limpiar(cuit)
    if len(c) != 11:
        return "Desconocido"
    pref = c[:2]
    if pref in ("20", "23", "24", "25", "26", "27"):
        return "Persona Humana"
    if pref in ("30", "33", "34"):
        return "Persona Jurídica"
    return "Otro"


def validar(cuit: str) -> dict:
    """Devuelve un dict con el resultado de la validación matemática.

    Estructura:
      {
        "cuit": "20-12345678-9",
        "cuit_limpio": "20123456789",
        "valido": True/False,
        "tipo": "Persona Humana" | "Persona Jurídica" | ...,
        "mensaje": "OK" o detalle del problema
      }
    """
    c = limpiar(cuit)
    if len(c) != 11:
        return {
            "cuit": cuit,
            "cuit_limpio": c,
            "valido": False,
            "tipo": "Desconocido",
            "mensaje": f"Longitud inválida: tiene {len(c)} dígitos, se esperaban 11.",
        }
    if not c.isdigit():
        return {
            "cuit": cuit,
            "cuit_limpio": c,
            "valido": False,
            "tipo": "Desconocido",
            "mensaje": "El CUIT contiene caracteres no numéricos.",
        }

    # Cálculo del dígito verificador
    suma = sum(int(c[i]) * COEFICIENTES[i] for i in range(10))
    resto = suma % 11
    dv_calculado = 11 - resto
    if dv_calculado == 11:
        dv_calculado = 0
    elif dv_calculado == 10:
        # Regla ARCA: si el cálculo da 10, no existe CUIT válido con ese
        # cuerpo (en la asignación se cambia el prefijo a 23 y se recalcula).
        return {
            "cuit": formatear(c),
            "cuit_limpio": c,
            "valido": False,
            "tipo": tipo_persona(c),
            "mensaje": (
                "El cuerpo del CUIT no admite dígito verificador válido "
                "(el cálculo da 10); el CUIT es inexistente según el algoritmo de ARCA."
            ),
        }

    dv_real = int(c[10])
    valido = dv_calculado == dv_real

    return {
        "cuit": formatear(c),
        "cuit_limpio": c,
        "valido": valido,
        "tipo": tipo_persona(c),
        "mensaje": "CUIT válido" if valido else f"Dígito verificador incorrecto (esperado {dv_calculado}, recibido {dv_real}).",
    }
