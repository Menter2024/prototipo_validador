"""Tests del motor de decisión fiscal: verificación APOC honesta."""
from app.modules import afip_arca, riesgo_fiscal


def _resultado_base(**afip_extra) -> dict:
    afip = {
        "encontrado": True,
        "razon_social": "PROVEEDOR TEST SA",
        "estado_clave": "ACTIVO",
        "condicion_iva": "RESPONSABLE INSCRIPTO",
        "inscripciones_iibb": {"jurisdicciones": [], "impuestos": []},
    }
    afip.update(afip_extra)
    return {
        "valido": True,
        "modo_afip": "live",
        "afip": afip,
        "padrones": {},
        "fuentes_online": {},
    }


def test_apoc_no_verificado_deriva_a_revision_manual():
    decision = riesgo_fiscal.evaluar(_resultado_base(en_apoc=None))

    assert decision["estado"] == "REVISION_MANUAL"
    assert any("APOC" in m for m in decision["motivos"])
    assert not any("figura vinculado a base APOC" in m for m in decision["motivos"])


def test_apoc_positivo_sigue_bloqueando():
    decision = riesgo_fiscal.evaluar(_resultado_base(en_apoc=True))

    assert decision["estado"] == "BLOQUEAR"
    assert any("APOC/facturación apócrifa" in m for m in decision["motivos"])


def test_apoc_verificado_negativo_no_agrega_motivo_apoc():
    decision = riesgo_fiscal.evaluar(_resultado_base(en_apoc=False))

    assert decision["estado"] == "APROBABLE"
    assert not any("APOC" in m for m in decision["motivos"])


def test_cuit_invalido_no_suma_motivo_apoc():
    resultado = _resultado_base(en_apoc=None)
    resultado["valido"] = False

    decision = riesgo_fiscal.evaluar(resultado)

    assert decision["estado"] == "BLOQUEAR"
    assert not any("APOC" in m for m in decision["motivos"])


def test_parse_persona_live_reporta_apoc_no_verificado():
    resp = {
        "personaReturn": {
            "datosGenerales": {
                "razonSocial": "EMPRESA SA",
                "tipoPersona": "JURIDICA",
                "estadoClave": "ACTIVO",
                "domicilioFiscal": {"direccion": "CALLE 1", "localidad": "CBA", "descripcionProvincia": "CORDOBA"},
            },
            "datosRegimenGeneral": {
                "impuesto": [{"descripcionImpuesto": "IVA", "estadoImpuesto": "AC"}],
            },
        }
    }

    data = afip_arca._parse_persona(resp)

    assert data["en_apoc"] is None


def test_demo_data_no_afirma_apoc_verificado():
    assert all(d["en_apoc"] is None for d in afip_arca.DEMO_DATA.values())
