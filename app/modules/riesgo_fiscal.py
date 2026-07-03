"""Motor de decisión fiscal para alta de proveedores.

Convierte datos consultados en una recomendación operativa para Impuestos/Compras.
"""

SEVERIDAD = {
    "APROBABLE": 0,
    "OBSERVADO": 1,
    "REVISION_MANUAL": 2,
    "BLOQUEAR": 3,
}


def _max_estado(actual: str, nuevo: str) -> str:
    return nuevo if SEVERIDAD[nuevo] > SEVERIDAD[actual] else actual


def evaluar(resultado: dict) -> dict:
    estado = "APROBABLE"
    motivos = []
    recomendaciones = []

    afip = resultado.get("afip", {})
    padrones = resultado.get("padrones", {})
    fuentes = resultado.get("fuentes_online", {})

    if not resultado.get("valido"):
        estado = _max_estado(estado, "BLOQUEAR")
        motivos.append("CUIT inválido: no corresponde avanzar con el alta hasta corregir el identificador fiscal.")
        recomendaciones.append("Solicitar CUIT correcto al proveedor.")

    if resultado.get("modo_afip") == "demo":
        estado = _max_estado(estado, "REVISION_MANUAL")
        motivos.append("AFIP/ARCA respondió en modo demo o fallback; no hay evidencia fiscal productiva suficiente.")
        recomendaciones.append("Revalidar contra AFIP/ARCA live antes de aprobar.")

    if afip.get("encontrado") is False:
        estado = _max_estado(estado, "BLOQUEAR")
        motivos.append("AFIP/ARCA no encontró datos para el CUIT informado.")
        recomendaciones.append("Solicitar constancia de inscripción o revisar CUIT.")

    estado_clave = (afip.get("estado_clave") or "").upper()
    if estado_clave and estado_clave not in {"ACTIVO", "—"}:
        estado = _max_estado(estado, "BLOQUEAR")
        motivos.append(f"Estado de clave fiscal/inscripción AFIP no activo: {estado_clave}.")
        recomendaciones.append("No aprobar hasta regularización fiscal.")

    if afip.get("en_apoc") is True:
        estado = _max_estado(estado, "BLOQUEAR")
        motivos.append("El CUIT figura vinculado a base APOC/facturación apócrifa.")
        recomendaciones.append("Derivar a Impuestos/Compliance antes de cualquier alta o pago.")
    elif resultado.get("valido") and afip.get("encontrado") is not False and afip.get("en_apoc") is None:
        estado = _max_estado(estado, "REVISION_MANUAL")
        motivos.append(
            "Verificación contra base APOC no realizada (integración pendiente); "
            "no hay evidencia para descartar facturación apócrifa."
        )
        recomendaciones.append("Verificar APOC manualmente en ARCA antes de aprobar.")

    condicion_iva = (afip.get("condicion_iva") or "").upper()
    if "MONOTRIBUTO" in condicion_iva:
        estado = _max_estado(estado, "OBSERVADO")
        motivos.append("Proveedor monotributista: requiere controlar categoría, actividad y límites frente al volumen esperado.")
        recomendaciones.append("Validar que la operación sea compatible con categoría y actividad declarada.")

    iibb_arca = afip.get("inscripciones_iibb") or {}
    jurisdicciones_arca = iibb_arca.get("jurisdicciones") or []
    if jurisdicciones_arca:
        estado = _max_estado(estado, "OBSERVADO")
        motivos.append(
            "ARCA informa Convenio Multilateral o jurisdicciones IIBB declaradas en: "
            + ", ".join(jurisdicciones_arca)
            + "."
        )
        recomendaciones.append("Cruzar esas jurisdicciones contra padrones provinciales y aplicar alícuotas vigentes.")
    inscripto_iibb = [prov for prov, p in padrones.items() if p.get("status") == "inscripto"]
    if inscripto_iibb:
        estado = _max_estado(estado, "OBSERVADO")
        motivos.append("Figura en padrones provinciales de IIBB: " + ", ".join(inscripto_iibb) + ".")
        recomendaciones.append("Aplicar alícuotas de retención/percepción vigentes según jurisdicción.")

    vencidos = [prov for prov, p in padrones.items() if p.get("vigencia_estado") == "vencido"]
    if vencidos:
        estado = _max_estado(estado, "OBSERVADO")
        motivos.append("Padrones vencidos utilizados en la consulta: " + ", ".join(vencidos) + ".")
        recomendaciones.append("Recargar padrón vigente y revalidar antes de liquidar retenciones/percepciones.")

    faltantes = [prov for prov, p in padrones.items() if p.get("status") == "no_disponible"]
    if faltantes:
        estado = _max_estado(estado, "OBSERVADO")
        motivos.append("Faltan padrones mensuales cargados para: " + ", ".join(faltantes) + ".")
        recomendaciones.append("Cargar padrones faltantes y revalidar si la jurisdicción es relevante; ARCA no cubre inscripciones locales exclusivas.")

    pendientes = [key for key, f in fuentes.items() if f.get("estado") in {"requiere_captcha", "requiere_credenciales", "requiere_navegador", "error", "revisar"}]
    if pendientes:
        estado = _max_estado(estado, "REVISION_MANUAL")
        motivos.append("Existen fuentes online pendientes o asistidas: " + ", ".join(pendientes) + ".")
        recomendaciones.append("Completar revisión manual/asistida antes de cierre definitivo del legajo.")

    online_encontrado = [key for key, f in fuentes.items() if f.get("estado") == "encontrado"]
    if online_encontrado:
        estado = _max_estado(estado, "OBSERVADO")
        motivos.append("Fuentes online detectaron inscripción o trámite vigente en: " + ", ".join(online_encontrado) + ".")
        recomendaciones.append("Considerar esa jurisdicción en matriz de retenciones/percepciones.")

    if not motivos:
        motivos.append("Sin observaciones fiscales críticas con la información disponible.")
        recomendaciones.append("Alta aprobable, sujeta a controles internos habituales.")

    labels = {
        "APROBABLE": "APROBABLE",
        "OBSERVADO": "OBSERVADO",
        "REVISION_MANUAL": "REVISIÓN MANUAL",
        "BLOQUEAR": "BLOQUEAR",
    }
    return {
        "estado": estado,
        "label": labels[estado],
        "score": SEVERIDAD[estado],
        "motivos": motivos,
        "recomendaciones": recomendaciones,
    }
