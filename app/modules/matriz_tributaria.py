"""Matriz inicial de retenciones/percepciones sugeridas.

No liquida impuestos; consolida información fiscal para que Impuestos decida.
"""
from app.modules import regimenes_catalogo

# georef/ARCA pueden nombrar CABA con su denominación larga.
_JURISDICCION_CANON = {
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Capital Federal": "CABA",
}


def _jurisdicciones_detectadas(resultado: dict) -> set[str]:
    afip = resultado.get("afip", {})
    detectadas = set((afip.get("inscripciones_iibb") or {}).get("jurisdicciones") or [])
    provincia_geo = (resultado.get("georef") or {}).get("provincia")
    if provincia_geo:
        detectadas.add(provincia_geo)
    return {_JURISDICCION_CANON.get(j, j) for j in detectadas}


def generar(resultado: dict) -> dict:
    afip = resultado.get("afip", {})
    padrones = resultado.get("padrones", {})
    items = []
    alertas = []

    condicion_iva = afip.get("condicion_iva", "—")
    condicion_ganancias = afip.get("condicion_ganancias", "—")
    iibb_arca = afip.get("inscripciones_iibb") or {}

    items.append({
        "jurisdiccion": "Nacional",
        "impuesto": "IVA",
        "condicion": condicion_iva,
        "retencion": "Según régimen aplicable",
        "percepcion": "Según régimen aplicable",
        "fuente": "AFIP/ARCA",
        "accion": "Validar certificados de exclusión/no retención si corresponde.",
    })
    items.append({
        "jurisdiccion": "Nacional",
        "impuesto": "Ganancias",
        "condicion": condicion_ganancias,
        "retencion": "Según RG aplicable",
        "percepcion": "—",
        "fuente": "AFIP/ARCA",
        "accion": "Controlar certificado de no retención Ganancias antes del pago.",
    })

    jurisdicciones_arca = iibb_arca.get("jurisdicciones") or []
    if jurisdicciones_arca:
        for jurisdiccion in jurisdicciones_arca:
            items.append({
                "jurisdiccion": jurisdiccion,
                "impuesto": "Ingresos Brutos",
                "condicion": iibb_arca.get("regimen") or "Inscripción IIBB informada por ARCA",
                "retencion": "A determinar por padrón provincial",
                "percepcion": "A determinar por padrón provincial",
                "fuente": "ARCA Constancia",
                "accion": "Validar padrón local de la jurisdicción antes de liquidar retención/percepción.",
            })
    elif (iibb_arca.get("impuestos") or []):
        alertas.append("ARCA informa inscripción IIBB/Convenio Multilateral, pero no se pudieron normalizar jurisdicciones.")
    else:
        alertas.append("ARCA no descarta inscripción local en IIBB: validar padrones/consultas provinciales relevantes.")

    for prov, p in padrones.items():
        if p.get("status") == "inscripto":
            items.append({
                "jurisdiccion": p.get("nombre", prov),
                "impuesto": "Ingresos Brutos",
                "condicion": p.get("regimen") or "Inscripto en padrón",
                "retencion": p.get("alicuota_retencion", "—") + "%",
                "percepcion": p.get("alicuota_percepcion", "—") + "%",
                "fuente": prov,
                "accion": "Aplicar alícuotas vigentes del padrón provincial.",
            })
        elif p.get("status") == "no_disponible":
            alertas.append(f"Sin padrón cargado para {prov}; no se puede confirmar inscripción local ni determinar alícuota IIBB.")
        elif p.get("status") in {"consulta_manual", "requiere_credenciales"}:
            alertas.append(f"{prov}: fuente requiere consulta manual/credenciales para confirmar inscripción IIBB y alícuotas.")

    # Jurisdicciones con presencia detectada donde el CUIT no figura en padrón:
    # la ausencia NO implica "no retener"; el tratamiento depende del régimen local.
    for jurisdiccion in sorted(_jurisdicciones_detectadas(resultado)):
        padron_key = regimenes_catalogo.PADRON_BY_JURISDICCION.get(jurisdiccion)
        if padron_key and padrones.get(padron_key, {}).get("status") == "no_inscripto":
            alertas.append(
                f"{jurisdiccion}: el CUIT no figura en el padrón cargado; definir el tratamiento del "
                "sujeto no incluido según el régimen local (puede corresponder alícuota general, "
                "residual o máxima) antes de liquidar."
            )

    if "MONOTRIBUTO" in str(condicion_iva).upper():
        alertas.append("Proveedor monotributista: controlar categoría y compatibilidad con monto/actividad antes de aplicar tratamiento fiscal.")

    return {
        "items": items,
        "alertas": alertas,
        "resumen": f"{len(items)} reglas/condiciones consolidadas · {len(alertas)} alerta(s)",
    }
