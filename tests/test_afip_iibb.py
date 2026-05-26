from app.modules import afip_arca


def test_parsea_iibb_convenio_multilateral_y_jurisdicciones():
    resp = {
        "personaReturn": {
            "datosGenerales": {
                "razonSocial": "EMPRESA SA",
                "tipoPersona": "JURIDICA",
                "estadoClave": "ACTIVO",
                "domicilioFiscal": {"direccion": "CALLE 1", "localidad": "ROSARIO", "descripcionProvincia": "SANTA FE"},
            },
            "datosRegimenGeneral": {
                "impuesto": [
                    {"descripcionImpuesto": "IVA", "estadoImpuesto": "AC"},
                    {"descripcionImpuesto": "CONVENIO MULTILATERAL", "estadoImpuesto": "AC"},
                ],
                "jurisdicciones": [
                    {"descripcionProvincia": "CORDOBA"},
                    {"descripcionProvincia": "TUCUMAN"},
                ],
            },
        }
    }

    data = afip_arca._parse_persona(resp)

    assert data["inscripciones_iibb"]["regimen"] == "Convenio Multilateral"
    assert "Córdoba" in data["inscripciones_iibb"]["jurisdicciones"]
    assert "Santa Fe" in data["inscripciones_iibb"]["jurisdicciones"]
    assert "Tucumán" in data["inscripciones_iibb"]["jurisdicciones"]


def test_sin_iibb_arca_no_descarta_inscripcion_local():
    resp = {
        "personaReturn": {
            "datosGenerales": {
                "razonSocial": "LOCAL SA",
                "tipoPersona": "JURIDICA",
                "estadoClave": "ACTIVO",
                "domicilioFiscal": {"direccion": "CALLE 1", "localidad": "CABA", "descripcionProvincia": "CAPITAL FEDERAL"},
            },
            "datosRegimenGeneral": {
                "impuesto": [{"descripcionImpuesto": "IVA", "estadoImpuesto": "AC"}],
            },
        }
    }

    data = afip_arca._parse_persona(resp)

    assert data["inscripciones_iibb"]["jurisdicciones"] == []
    assert "no descarta inscripción local" in data["inscripciones_iibb"]["detalle"]


def test_iibb_no_confunde_fecha_con_chaco_y_detecta_santa_fe():
    resp = {
        "personaReturn": {
            "datosGenerales": {
                "razonSocial": "MENTER S. A. S.",
                "tipoPersona": "JURIDICA",
                "estadoClave": "ACTIVO",
                "fechaContratoSocial": "2024-06-28",
                "domicilioFiscal": {"direccion": "CALLE 1", "localidad": "PARANA", "descripcionProvincia": "ENTRE RIOS"},
            },
            "datosRegimenGeneral": {
                "impuesto": [{"descripcionImpuesto": "IIBB CONVENIO MULTILATERAL", "estadoImpuesto": "AC"}],
                "jurisdicciones": [
                    {"codigo": "908", "descripcionProvincia": "ENTRE RIOS"},
                    {"codigo": "921", "descripcionProvincia": "SANTA FE"},
                ],
            },
        }
    }

    data = afip_arca._parse_persona(resp)

    assert data["inscripciones_iibb"]["jurisdicciones"] == ["Entre Ríos", "Santa Fe"]
