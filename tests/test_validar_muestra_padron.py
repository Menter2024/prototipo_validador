import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validar_muestra_padron.py"
FIXTURES = ROOT / "tests" / "fixtures" / "padrones_no_estandar"


def load_module():
    spec = importlib.util.spec_from_file_location("validar_muestra_padron", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_validar_muestra_cordoba_detecta_layout_y_hash(tmp_path):
    module = load_module()
    reporte = module.validar_muestra("Cordoba", FIXTURES / "cordoba_headerless.zip")

    assert reporte["ok"] is True
    assert reporte["layout_detectado"] == "cordoba_iibb_delimitado_v1"
    assert reporte["layout_esperado"] == "cordoba_iibb_delimitado_v1"
    assert len(reporte["sha256"]) == 64
    assert reporte["registros"] == 1


def test_validar_muestra_falla_si_layout_no_coincide():
    module = load_module()
    reporte = module.validar_muestra(
        "Cordoba",
        FIXTURES / "cordoba_headerless.zip",
        expected_layout="layout_incorrecto",
    )

    assert reporte["ok"] is False
    assert "no coincide" in reporte["errores"][0]
