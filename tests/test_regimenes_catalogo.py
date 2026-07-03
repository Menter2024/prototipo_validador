import json
from pathlib import Path

CATALOGO = Path("config/regimenes_catalogo.json")

REQUIRED_FIELDS = {
    "id",
    "nivel",
    "jurisdiccion",
    "organismo",
    "impuesto_tasa",
    "tipo",
    "familia",
    "nombre",
    "hecho_disparador",
    "sujeto_agente",
    "sujeto_pasible",
    "base_calculo",
    "alicuota_fuente",
    "padron_fuente",
    "periodicidad",
    "sistema_presentacion",
    "credenciales_requeridas",
    "automatizacion",
    "evidencia_requerida",
    "riesgo_operativo",
    "estado_integracion",
    "prioridad",
    "fuentes",
}


def _catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def test_regimenes_catalogo_es_json_valido_y_con_ids_unicos():
    data = _catalogo()
    regimenes = data["regimenes"]
    ids = [r["id"] for r in regimenes]

    assert isinstance(data["version"], int) and data["version"] >= 2
    assert len(regimenes) >= 20
    assert len(ids) == len(set(ids))


def test_regimenes_tienen_esquema_operativo_minimo():
    for regimen in _catalogo()["regimenes"]:
        assert REQUIRED_FIELDS <= set(regimen), regimen["id"]
        for field in REQUIRED_FIELDS - {"credenciales_requeridas", "fuentes"}:
            assert regimen[field], f"{regimen['id']} missing {field}"
        assert isinstance(regimen["credenciales_requeridas"], bool)
        assert regimen["fuentes"] and all(str(f).startswith("https://") for f in regimen["fuentes"])


def test_regimenes_cubren_niveles_y_familias_clave():
    regimenes = _catalogo()["regimenes"]
    niveles = {r["nivel"] for r in regimenes}
    ids = {r["id"] for r in regimenes}

    assert {"nacional", "provincial_unificado", "provincial", "municipal"} <= niveles
    assert {
        "arca_ganancias_rg830",
        "arca_sire",
        "arca_libro_iva_digital_iva_simple",
        "comarb_sircar",
        "comarb_sircreb",
        "comarb_sirtac",
        "comarb_sircupa",
        "comarb_sirpei",
        "comarb_sifere",
        "municipal_tish_drei_generico",
    } <= ids


def test_prioridades_y_automatizacion_son_controladas():
    prioridades = {"P0", "P1", "P2", "P3"}
    automatizaciones = {
        "parcialmente_automatizable",
        "portal_credenciales_api_si_disponible",
        "asistido_archivo_exportable",
        "portal_credenciales_archivo",
        "archivo_credenciales",
        "descarga_publica_importador",
        "pagina_publica_importador_asistido",
        "priorizar_por_huella_cliente",
    }

    for regimen in _catalogo()["regimenes"]:
        assert regimen["prioridad"] in prioridades
        assert regimen["automatizacion"] in automatizaciones
