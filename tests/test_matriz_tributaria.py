"""Tests de la matriz tributaria: tratamiento del CUIT ausente en padrón."""
from app.modules import matriz_tributaria


def _resultado(padrones: dict, jurisdicciones_arca: list[str] | None = None, provincia_geo: str | None = None) -> dict:
    return {
        "valido": True,
        "afip": {
            "condicion_iva": "RESPONSABLE INSCRIPTO",
            "condicion_ganancias": "INSCRIPTO",
            "inscripciones_iibb": {"jurisdicciones": jurisdicciones_arca or [], "impuestos": []},
        },
        "georef": {"provincia": provincia_geo},
        "padrones": padrones,
    }


def test_no_inscripto_en_jurisdiccion_detectada_genera_alerta():
    resultado = _resultado(
        {"Cordoba": {"status": "no_inscripto", "nombre": "Córdoba"}},
        jurisdicciones_arca=["Córdoba"],
    )

    matriz = matriz_tributaria.generar(resultado)

    assert any("Córdoba" in a and "no incluido" in a for a in matriz["alertas"])


def test_georef_caba_se_canoniza_y_genera_alerta():
    resultado = _resultado(
        {"CABA": {"status": "no_inscripto", "nombre": "CABA / AGIP"}},
        provincia_geo="Ciudad Autónoma de Buenos Aires",
    )

    matriz = matriz_tributaria.generar(resultado)

    assert any("CABA" in a and "no incluido" in a for a in matriz["alertas"])


def test_no_inscripto_sin_jurisdiccion_detectada_no_genera_ruido():
    resultado = _resultado({"Jujuy": {"status": "no_inscripto", "nombre": "Jujuy"}})

    matriz = matriz_tributaria.generar(resultado)

    assert not any("Jujuy" in a for a in matriz["alertas"])


def test_ninguna_salida_afirma_que_no_aplica_retencion():
    resultado = _resultado(
        {"Cordoba": {"status": "no_inscripto", "nombre": "Córdoba"}},
        jurisdicciones_arca=["Córdoba"],
    )

    matriz = matriz_tributaria.generar(resultado)

    textos = matriz["alertas"] + [str(i) for i in matriz["items"]]
    assert not any("no aplica retención" in t for t in textos)
