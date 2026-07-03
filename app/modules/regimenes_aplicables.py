"""Derivación de regímenes fiscales potencialmente aplicables por proveedor."""
from __future__ import annotations

import unicodedata
from collections import Counter
from typing import Any

from app.modules import regimenes_catalogo

CLASIFICACIONES = {
    "aplicable",
    "potencial",
    "pendiente_evidencia",
    "no_integrable_cola_asistida",
}

PADRON_STATUS_PENDIENTE = {"no_disponible", "error"}
PADRON_STATUS_ASISTIDO = {"consulta_manual", "requiere_credenciales"}
FUENTES_ASISTIDAS = {
    "requiere_captcha",
    "requiere_credenciales",
    "requiere_navegador",
    "error",
    "revisar",
}

JURISDICCION_BY_PADRON = {
    padron_key: jurisdiccion
    for jurisdiccion, padron_key in regimenes_catalogo.PADRON_BY_JURISDICCION.items()
}
JURISDICCIONES_CANON = {
    "CABA": "CABA",
    "CAPITAL FEDERAL": "CABA",
    "CIUDAD AUTONOMA DE BUENOS AIRES": "CABA",
    "BUENOS AIRES": "Buenos Aires",
    "CORDOBA": "Córdoba",
    "JUJUY": "Jujuy",
    "MENDOZA": "Mendoza",
    "SANTA FE": "Santa Fe",
    "TUCUMAN": "Tucumán",
}
for _jur in regimenes_catalogo.PADRON_BY_JURISDICCION:
    JURISDICCIONES_CANON.setdefault(_jur.upper(), _jur)


def _norm(valor: str | None) -> str:
    texto = unicodedata.normalize("NFKD", valor or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).upper().strip()


def _canon_jurisdiccion(valor: str | None) -> str | None:
    limpio = _norm(valor)
    if not limpio or limpio in {"—", "-"}:
        return None
    return JURISDICCIONES_CANON.get(limpio, valor)


def _hay_dato_fiscal(valor: str | None) -> bool:
    limpio = _norm(valor)
    return bool(limpio and limpio not in {"—", "-", "NO INSCRIPTO", "SIN DATOS"})


def _es_convenio_multilateral(afip: dict[str, Any]) -> bool:
    iibb = afip.get("inscripciones_iibb") or {}
    regimen = _norm(iibb.get("regimen"))
    impuestos = " ".join(_norm(i.get("descripcion")) for i in iibb.get("impuestos", []) if isinstance(i, dict))
    return "CONVENIO MULTILATERAL" in regimen or "CONVENIO MULTILATERAL" in impuestos


def _jurisdicciones_detectadas(resultado: dict[str, Any]) -> list[str]:
    detectadas: set[str] = set()
    afip = resultado.get("afip") or {}
    iibb = afip.get("inscripciones_iibb") or {}
    for jur in iibb.get("jurisdicciones") or []:
        canon = _canon_jurisdiccion(jur)
        if canon:
            detectadas.add(canon)
    geo = (resultado.get("georef") or {}).get("provincia")
    canon_geo = _canon_jurisdiccion(geo)
    if canon_geo:
        detectadas.add(canon_geo)
    for padron_key, info in (resultado.get("padrones") or {}).items():
        if info.get("status") == "inscripto":
            jur = JURISDICCION_BY_PADRON.get(padron_key)
            if jur:
                detectadas.add(jur)
    return sorted(detectadas)


def _fuentes_por_padron(fuentes_estado: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        f.get("padron_key"): f
        for f in (fuentes_estado or {}).get("fuentes", [])
        if f.get("padron_key")
    }


def _item(
    regimen: dict[str, Any],
    clasificacion: str,
    motivos: list[str],
    proxima_accion: str,
    integracion_fuente: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": regimen.get("id"),
        "nombre": regimen.get("nombre"),
        "nivel": regimen.get("nivel"),
        "jurisdiccion": regimen.get("jurisdiccion"),
        "organismo": regimen.get("organismo"),
        "impuesto_tasa": regimen.get("impuesto_tasa"),
        "tipo": regimen.get("tipo"),
        "familia": regimen.get("familia"),
        "prioridad": regimen.get("prioridad"),
        "clasificacion": clasificacion,
        "motivos": motivos,
        "evidencia_requerida": regimen.get("evidencia_requerida"),
        "proxima_accion": proxima_accion,
        "fuentes": regimen.get("fuentes", []),
        "integracion_fuente": integracion_fuente or {},
    }


def _evaluar_nacional(regimen: dict[str, Any], resultado: dict[str, Any]) -> dict[str, Any] | None:
    afip = resultado.get("afip") or {}
    if afip.get("encontrado") is False:
        return _item(
            regimen,
            "pendiente_evidencia",
            ["No hay constancia ARCA normalizada para confirmar condición fiscal."],
            "Obtener constancia ARCA vigente y revalidar el proveedor.",
        )

    cond_iva = afip.get("condicion_iva")
    cond_gan = afip.get("condicion_ganancias")
    estado = _norm(afip.get("estado_clave"))
    activo = estado == "ACTIVO"
    regimen_id = regimen.get("id", "")
    motivos_base = [f"Estado ARCA: {afip.get('estado_clave', '—')}."]

    if regimen_id == "arca_siter_financiero":
        return None
    if "ganancias" in regimen_id:
        if activo and _hay_dato_fiscal(cond_gan):
            return _item(
                regimen,
                "aplicable",
                motivos_base + [f"Condición Ganancias informada: {cond_gan}."],
                "Definir concepto de pago y conservar certificado/constancia; alícuota queda fuera de este sprint.",
            )
        return None
    if "iva" in regimen_id:
        if activo and _hay_dato_fiscal(cond_iva):
            return _item(
                regimen,
                "aplicable" if regimen_id == "arca_libro_iva_digital_iva_simple" else "potencial",
                motivos_base + [f"Condición IVA informada: {cond_iva}."],
                "Confirmar tipo de operación/comprobante y certificados de exclusión antes de calcular importes.",
            )
        return None
    if regimen_id in {"arca_sire", "arca_sicore"} and (activo and (_hay_dato_fiscal(cond_iva) or _hay_dato_fiscal(cond_gan))):
        sistema = "SIRE" if regimen_id == "arca_sire" else "SICORE"
        return _item(
            regimen,
            "potencial",
            motivos_base + [f"Hay impuestos nacionales normalizados que pueden requerir certificación {sistema}."],
            f"Usar {sistema} solo si se practica retención/percepción en una operación concreta; el sistema depende del régimen aplicado.",
        )
    return None


def _evaluar_unificado(regimen: dict[str, Any], resultado: dict[str, Any], jurisdicciones: list[str]) -> dict[str, Any] | None:
    afip = resultado.get("afip") or {}
    convenio = _es_convenio_multilateral(afip) or len(jurisdicciones) > 1
    if not convenio:
        return None
    if regimen.get("id") == "comarb_sifere":
        return _item(
            regimen,
            "aplicable",
            ["ARCA informa Convenio Multilateral o múltiples jurisdicciones IIBB."],
            "Conservar constancia ARCA/CM y validar coeficientes/presentaciones fuera del cálculo de alícuotas.",
        )
    return _item(
        regimen,
        "no_integrable_cola_asistida",
        ["Proveedor con señales de Convenio Multilateral; el padrón/sistema unificado no está integrado por CUIT."],
        "Crear tarea asistida para consultar/exportar padrón COMARB/SIRCAR/SIRCREB según corresponda.",
    )


def _evaluar_provincial(
    regimen: dict[str, Any],
    resultado: dict[str, Any],
    jurisdicciones: list[str],
    fuentes_padron: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    jurisdiccion = regimen.get("jurisdiccion")
    padron_key = regimenes_catalogo.PADRON_BY_JURISDICCION.get(jurisdiccion)
    if not padron_key:
        return None
    padron_info = (resultado.get("padrones") or {}).get(padron_key, {})
    fuente = fuentes_padron.get(padron_key, {})
    status = padron_info.get("status")
    detectada = jurisdiccion in jurisdicciones
    integracion = {
        "padron_key": padron_key,
        "padron_status": status,
        "fuente_estado": fuente.get("estado"),
        "vigencia_estado": fuente.get("vigencia_estado"),
        "proxima_accion_fuente": fuente.get("proxima_accion"),
    }

    if status == "inscripto":
        return _item(
            regimen,
            "aplicable",
            [f"El proveedor figura en padrón {padron_key}.", padron_info.get("detalle", "")],
            "Conservar archivo original, hash/manifest y evidencia del cruce; no calcular alícuotas todavía.",
            integracion,
        )
    if not detectada:
        return None
    if status in PADRON_STATUS_ASISTIDO or regimen.get("automatizacion") in {"portal_credenciales_archivo", "archivo_credenciales"}:
        return _item(
            regimen,
            "no_integrable_cola_asistida",
            [f"Jurisdicción detectada: {jurisdiccion}.", "La fuente requiere credenciales/exportación o revisión manual."],
            padron_info.get("detalle") or fuente.get("proxima_accion") or "Abrir tarea asistida y adjuntar evidencia.",
            integracion,
        )
    if status in PADRON_STATUS_PENDIENTE or not status:
        return _item(
            regimen,
            "pendiente_evidencia",
            [f"Jurisdicción detectada: {jurisdiccion}.", "No hay padrón vigente/disponible para confirmar inclusión."],
            fuente.get("proxima_accion") or "Cargar padrón vigente y revalidar.",
            integracion,
        )
    if status == "no_inscripto":
        return _item(
            regimen,
            "potencial",
            [f"Jurisdicción detectada: {jurisdiccion}.", "El CUIT no figura en el padrón cargado actual."],
            "Mantener monitoreo de padrón y revisar por tipo de operación antes de retener/percibir.",
            integracion,
        )
    return None


def _evaluar_municipal(regimen: dict[str, Any], jurisdicciones: list[str]) -> dict[str, Any]:
    ambito = ", ".join(jurisdicciones) if jurisdicciones else "sin jurisdicción provincial concluyente"
    return _item(
        regimen,
        "pendiente_evidencia",
        [f"Huella territorial del proveedor/cliente: {ambito}.", "Los regímenes municipales son fragmentados por ordenanza."],
        "Relevar municipios donde el cliente opera/compra y adjuntar ordenanza, constancia o captura del portal local.",
    )


def generar(
    resultado: dict[str, Any],
    fuentes_estado: dict[str, Any] | None = None,
    catalog_path=None,
) -> dict[str, Any]:
    if not resultado.get("valido"):
        return {
            "items": [],
            "jurisdicciones_detectadas": [],
            "resumen": {"total": 0, "por_clasificacion": {}, "requieren_accion": 0},
            "criterio": "No se derivan regímenes para CUIT inválido.",
        }

    catalogo = regimenes_catalogo.cargar_catalogo(catalog_path)
    fuentes_padron = _fuentes_por_padron(fuentes_estado)
    jurisdicciones = _jurisdicciones_detectadas(resultado)
    items: list[dict[str, Any]] = []

    for regimen in catalogo["regimenes"]:
        nivel = regimen.get("nivel")
        item = None
        if nivel == "nacional":
            item = _evaluar_nacional(regimen, resultado)
        elif nivel == "provincial_unificado":
            item = _evaluar_unificado(regimen, resultado, jurisdicciones)
        elif nivel == "provincial":
            item = _evaluar_provincial(regimen, resultado, jurisdicciones, fuentes_padron)
        elif nivel == "municipal":
            item = _evaluar_municipal(regimen, jurisdicciones)
        if item:
            items.append(item)

    orden = {"aplicable": 0, "potencial": 1, "pendiente_evidencia": 2, "no_integrable_cola_asistida": 3}
    items.sort(key=lambda i: (orden.get(i["clasificacion"], 99), i.get("prioridad", "P9"), i.get("id", "")))
    por_clasificacion = Counter(i["clasificacion"] for i in items)
    return {
        "items": items,
        "jurisdicciones_detectadas": jurisdicciones,
        "resumen": {
            "total": len(items),
            "por_clasificacion": dict(por_clasificacion),
            "requieren_accion": sum(1 for i in items if i["clasificacion"] != "aplicable"),
        },
        "criterio": "Clasificación operativa sin cálculo de alícuotas; cada item conserva evidencia requerida y próxima acción.",
    }
