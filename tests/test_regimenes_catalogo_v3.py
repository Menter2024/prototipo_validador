"""Tests del catálogo v3: normas verificadas y huella CICSA completa."""
from app.modules import regimenes_aplicables, regimenes_catalogo


def _por_id() -> dict:
    return {r["id"]: r for r in regimenes_catalogo.cargar_catalogo()["regimenes"]}


def test_nacionales_p0_quedaron_catalogados_con_norma_base():
    regimenes = _por_id()
    for rid in ("arca_ganancias_rg830", "arca_iva_retenciones", "arca_iva_percepciones",
                "arca_libro_iva_digital_iva_simple", "arca_sire", "arca_sicore"):
        assert regimenes[rid]["estado_integracion"] != "pendiente_catalogado", rid
        assert regimenes[rid].get("norma_base"), rid
        assert regimenes[rid].get("norma_verificada_al"), rid


def test_rg830_referencia_minimos_sin_importes_hardcodeados():
    rg830 = _por_id()["arca_ganancias_rg830"]
    assert "830" in rg830["norma_base"]
    assert rg830["minimos_referencia"]["importes_hardcodeados"] is False
    assert "Anexo VIII" in rg830["minimos_referencia"]["ubicacion"]


def test_comarb_catalogados_salvo_los_no_verificados():
    regimenes = _por_id()
    for rid in ("comarb_sircar", "comarb_sircreb", "comarb_sirtac", "comarb_sircupa", "comarb_sifere"):
        assert regimenes[rid]["estado_integracion"] == "catalogado_no_integrado", rid
        assert regimenes[rid].get("norma_base"), rid
    # Los no verificados quedan pendientes CON nota que lo explicita.
    for rid in ("comarb_sirpei", "comarb_sircip"):
        assert regimenes[rid]["estado_integracion"] == "pendiente_catalogado"
        assert "no se" in regimenes[rid]["nota_verificacion"].lower() or "no confirm" in regimenes[rid]["nota_verificacion"].lower()


def test_jurisdicciones_huella_cicsa_presentes():
    regimenes = _por_id()
    for rid in ("entrerios_iibb_ret_per", "neuquen_iibb_percepcion", "santiago_estero_iibb_percepcion",
                "sanluis_iibb_percepcion", "salta_iibb_ret_per", "formosa_iibb_ret_per"):
        assert rid in regimenes, rid
        assert regimenes[rid].get("norma_base"), rid


def test_padron_entre_rios_y_formosa_mapeados():
    assert regimenes_catalogo.PADRON_BY_JURISDICCION["Entre Ríos"] == "EntreRios"
    assert regimenes_catalogo.PADRON_BY_JURISDICCION["Formosa"] == "Formosa"


def test_entre_rios_se_deriva_por_padron_en_regimenes_aplicables():
    resultado = {
        "valido": True,
        "afip": {
            "encontrado": True,
            "estado_clave": "ACTIVO",
            "condicion_iva": "IVA (ACTIVO)",
            "inscripciones_iibb": {"jurisdicciones": ["Entre Ríos"], "impuestos": []},
        },
        "georef": {"provincia": None},
        "padrones": {"EntreRios": {"status": "inscripto", "detalle": "Padrón vigente."}},
    }

    data = regimenes_aplicables.generar(resultado)

    entrerios = [i for i in data["items"] if i["id"] == "entrerios_iibb_ret_per"]
    assert entrerios, "Entre Ríos no derivado"
    assert entrerios[0]["clasificacion"] == "aplicable"
    assert "Entre Ríos" in data["jurisdicciones_detectadas"]
