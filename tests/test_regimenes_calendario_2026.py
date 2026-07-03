"""Tests de la separación SIRE/SICORE y el calendario 2026 del catálogo."""
from app.modules import regimenes_aplicables, regimenes_catalogo


def _por_id() -> dict:
    catalogo = regimenes_catalogo.cargar_catalogo()
    return {r["id"]: r for r in catalogo["regimenes"]}


def test_sire_y_sicore_son_sistemas_separados():
    regimenes = _por_id()

    assert "arca_sire" in regimenes and "arca_sicore" in regimenes
    assert regimenes["arca_sire"]["norma_base"].startswith("RG (AFIP) 3726")
    assert regimenes["arca_sicore"]["norma_base"].startswith("RG (AFIP) 2233")
    assert regimenes["arca_sire"]["sistema_presentacion"] == "SIRE"
    assert regimenes["arca_sicore"]["sistema_presentacion"] == "SICORE"


def test_calendario_2026_referenciado_sin_fechas_hardcodeadas():
    regimenes = _por_id()

    con_calendario = ["arca_sire", "arca_sicore", "comarb_sircar", "comarb_sircreb",
                      "comarb_sirtac", "comarb_sircupa", "comarb_sifere"]
    for rid in con_calendario:
        cal = regimenes[rid].get("calendario_2026")
        assert cal, f"{rid} sin calendario_2026"
        assert cal["fechas_hardcodeadas"] is False
        assert cal["fuente"].startswith("https://")
        assert regimenes[rid]["norma_verificada_al"] == "2026-07-03"

    # SIRCAR: la reprogramación 2026 tiene que estar citada.
    sircar = regimenes["comarb_sircar"]["calendario_2026"]
    assert "21/2025" in sircar["norma_calendario"]
    assert "1/2026" in sircar["norma_calendario"]


def test_regimenes_aplicables_evalua_ambos_sistemas():
    resultado = {
        "valido": True,
        "afip": {
            "encontrado": True,
            "estado_clave": "ACTIVO",
            "condicion_iva": "IVA (ACTIVO)",
            "condicion_ganancias": "GANANCIAS SOCIEDADES (ACTIVO)",
            "inscripciones_iibb": {"jurisdicciones": [], "impuestos": []},
        },
        "georef": {"provincia": None},
        "padrones": {},
    }

    data = regimenes_aplicables.generar(resultado)

    ids = {i["id"] for i in data["items"]}
    assert "arca_sire" in ids
    assert "arca_sicore" in ids
    por_id = {i["id"]: i for i in data["items"]}
    assert "SICORE" in por_id["arca_sicore"]["proxima_accion"]
    assert "SIRE" in por_id["arca_sire"]["proxima_accion"]
