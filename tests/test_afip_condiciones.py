"""El parser debe informar el impuesto propio, no el régimen de agente (SIRE/SICORE)."""
from app.modules import afip_arca


def _resp(impuestos: list[dict]) -> dict:
    return {
        "personaReturn": {
            "datosGenerales": {
                "razonSocial": "AGENTE SA",
                "tipoPersona": "JURIDICA",
                "estadoClave": "ACTIVO",
                "domicilioFiscal": {"direccion": "CALLE 1", "localidad": "STA FE", "descripcionProvincia": "SANTA FE"},
            },
            "datosRegimenGeneral": {"impuesto": impuestos},
        }
    }


def test_prefiere_iva_propio_sobre_regimen_sire():
    data = afip_arca._parse_persona(_resp([
        {"descripcionImpuesto": "SIRE -  IVA", "estadoImpuesto": "AC"},
        {"descripcionImpuesto": "IVA", "estadoImpuesto": "AC"},
        {"descripcionImpuesto": "SICORE - RETENCIONES Y PERCEPC", "estadoImpuesto": "AC"},
    ]))

    assert data["condicion_iva"] == "IVA (ACTIVO)"


def test_prefiere_ganancias_propio_sobre_sicore():
    data = afip_arca._parse_persona(_resp([
        {"descripcionImpuesto": "SICORE-IMPTO.A LAS GANANCIAS", "estadoImpuesto": "AC"},
        {"descripcionImpuesto": "GANANCIAS SOCIEDADES", "estadoImpuesto": "AC"},
    ]))

    assert data["condicion_ganancias"] == "GANANCIAS SOCIEDADES (ACTIVO)"


def test_sin_impuesto_propio_informa_el_regimen_disponible():
    data = afip_arca._parse_persona(_resp([
        {"descripcionImpuesto": "SIRE -  IVA", "estadoImpuesto": "AC"},
    ]))

    assert data["condicion_iva"] == "SIRE -  IVA (ACTIVO)"
