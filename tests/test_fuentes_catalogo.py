from pathlib import Path
import json

from app.modules import fuentes_catalogo, padron_manifest

CATALOGO_PATH = Path(__file__).parent.parent / "config" / "fuentes_catalogo.json"


def _catalogo_oficial():
    return json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))


def test_evalua_padron_faltante_como_alerta_critica(tmp_path: Path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        """
        {
          "version": 1,
          "fuentes": [{
            "id": "arba_iibb",
            "padron_key": "ARBA",
            "nombre": "ARBA",
            "jurisdiccion": "Buenos Aires",
            "organismo": "ARBA",
            "regimenes": ["iibb"],
            "clase": "padron_descargable",
            "prioridad": "P1",
            "frecuencia": "mensual",
            "dias_alerta": 7,
            "url": "https://web.arba.gov.ar/"
          }]
        }
        """,
        encoding="utf-8",
    )

    estado = fuentes_catalogo.evaluar_fuentes(tmp_path, catalog)

    assert estado["resumen"]["criticas"] == 1
    assert estado["fuentes"][0]["estado"] == "pendiente_carga"
    assert estado["alertas"][0]["riesgo"] == "critico"


def test_evalua_padron_cargado_y_vigente(tmp_path: Path):
    (tmp_path / "PadronARBA.csv").write_text(
        "cuit,alicuota_retencion,alicuota_percepcion\n30500010912,1,2\n",
        encoding="utf-8",
    )
    padron_manifest.registrar_carga(
        tmp_path,
        "ARBA",
        "PadronARBA.csv",
        1,
        "test",
        "2026-05",
        "2099-12-31",
        None,
    )
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        """
        {
          "version": 1,
          "fuentes": [{
            "id": "arba_iibb",
            "padron_key": "ARBA",
            "nombre": "ARBA",
            "jurisdiccion": "Buenos Aires",
            "organismo": "ARBA",
            "regimenes": ["iibb"],
            "clase": "padron_descargable",
            "prioridad": "P1",
            "frecuencia": "mensual",
            "dias_alerta": 7,
            "url": "https://web.arba.gov.ar/"
          }]
        }
        """,
        encoding="utf-8",
    )

    estado = fuentes_catalogo.evaluar_fuentes(tmp_path, catalog)

    assert estado["resumen"]["criticas"] == 0
    assert estado["fuentes"][0]["estado"] == "vigente"
    assert estado["fuentes"][0]["registros"] == 1


def test_catalogo_fuentes_oficiales_cubre_p0_a_p3_y_campos_operativos():
    fuentes = _catalogo_oficial()["fuentes"]
    ids = [f["id"] for f in fuentes]

    assert len(ids) == len(set(ids))
    assert {f["prioridad"] for f in fuentes} >= {"P0", "P1", "P2", "P3"}
    for fuente in fuentes:
        assert fuente["url"].startswith("https://")
        assert fuente["tipo_acceso"]
        assert fuente["evidencia_requerida"]
        assert fuente["estado_integracion"]
        assert isinstance(fuente["requisitos_obtencion"], list) and fuente["requisitos_obtencion"]
        assert isinstance(fuente["condiciones_automatizacion"], list) and fuente["condiciones_automatizacion"]
        assert isinstance(fuente["mantenimiento_seguro"], list) and fuente["mantenimiento_seguro"]
        assert fuente.get("descarga", {}).get("landing_url", "").startswith("https://")


def test_catalogo_prioriza_fuentes_criticas_y_comarb():
    fuentes = {f["id"]: f for f in _catalogo_oficial()["fuentes"]}
    requeridas = {
        "arca_constancia",
        "arca_sire",
        "arca_apoc",
        "arba_iibb",
        "agip_caba_iibb",
        "ater_entrerios_iibb",
        "santafe_iibb",
        "comarb_sircreb",
        "comarb_sircupa",
        "comarb_sircip",
        "municipal_padrones_huella_cliente",
    }

    assert requeridas <= set(fuentes)
    assert fuentes["arba_iibb"]["prioridad"] == "P0"
    assert fuentes["comarb_sircreb"]["tipo_acceso"] == "clave_fiscal_afip_portal_federal"
    assert fuentes["municipal_padrones_huella_cliente"]["automatizacion"] == "priorizar_por_huella_cliente"


def test_catalogo_incluye_relevamiento_resto_pais():
    jurisdicciones = {f["jurisdiccion"] for f in _catalogo_oficial()["fuentes"]}

    esperadas = {
        "Catamarca",
        "Chaco",
        "Chubut",
        "Formosa",
        "La Pampa",
        "La Rioja",
        "Salta",
        "San Juan",
        "San Luis",
        "Santa Cruz",
        "Santiago del Estero",
        "Tierra del Fuego",
    }
    assert esperadas <= jurisdicciones
