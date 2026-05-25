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
