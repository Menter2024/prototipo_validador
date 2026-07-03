"""Tests del validador matemático de CUIT/CUIL (algoritmo oficial ARCA)."""
from app.modules import validador

CUITS_REALES_VALIDOS = [
    "33693450239",  # AFIP/ARCA
    "30500010912",  # Banco Nación
    "30546689979",  # YPF
    "30505779858",  # CICSA
]


def _dv_bruto(cuerpo: str) -> int:
    """11 - (suma ponderada % 11), sin normalizar: puede dar 10 u 11."""
    suma = sum(int(cuerpo[i]) * validador.COEFICIENTES[i] for i in range(10))
    return 11 - (suma % 11)


def _cuerpo_con_dv(objetivo: int) -> str:
    for n in range(10_000_000_000):
        cuerpo = f"{n:010d}"
        if _dv_bruto(cuerpo) == objetivo:
            return cuerpo
    raise AssertionError(f"no se encontró cuerpo con DV bruto {objetivo}")


def test_cuits_reales_validos():
    for cuit in CUITS_REALES_VALIDOS:
        assert validador.validar(cuit)["valido"], cuit


def test_normaliza_guiones_y_espacios():
    assert validador.validar("33-69345023-9")["valido"]
    assert validador.validar(" 33 69345023 9 ")["valido"]


def test_dv_incorrecto_es_invalido():
    resultado = validador.validar("33693450231")
    assert not resultado["valido"]
    assert "Dígito verificador incorrecto" in resultado["mensaje"]


def test_cuerpo_con_dv_10_es_invalido_con_cualquier_final():
    """Regresión del bug: DV calculado 10 se mapeaba a 9 y aceptaba CUITs inexistentes."""
    cuerpo = _cuerpo_con_dv(10)
    for final in range(10):
        resultado = validador.validar(f"{cuerpo}{final}")
        assert not resultado["valido"], f"{cuerpo}{final} no debería ser válido"
    assert "no admite dígito verificador válido" in validador.validar(f"{cuerpo}9")["mensaje"]


def test_dv_11_se_normaliza_a_0():
    cuerpo = _cuerpo_con_dv(11)
    assert validador.validar(f"{cuerpo}0")["valido"]


def test_longitud_invalida():
    assert not validador.validar("123")["valido"]
    assert not validador.validar("")["valido"]
