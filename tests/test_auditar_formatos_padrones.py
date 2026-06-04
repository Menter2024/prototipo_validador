import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "auditar_formatos_padrones.py"


def load_module():
    spec = importlib.util.spec_from_file_location("auditar_formatos_padrones", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_auditoria_cubre_todas_las_fuentes_y_detecta_bloqueos_masivos():
    module = load_module()
    audit = module.audit_sources()

    assert audit["source_count"] == 34
    fuente_ids = {row["fuente_id"] for row in audit["rows"]}
    assert "agip_caba_iibb" in fuente_ids
    assert "municipal_padrones_huella_cliente" in fuente_ids

    by_id = {row["fuente_id"]: row for row in audit["rows"]}
    assert by_id["agip_caba_iibb"]["layout_status"] == "layout_especifico"
    assert by_id["agip_caba_iibb"]["layout_ids"] == ["agip_caba_regimenes_generales_v1"]
    assert by_id["arba_iibb"]["layout_status"] == "layout_especifico"
    assert by_id["arba_iibb"]["bloquea_importacion_masiva"] is False
    assert by_id["ater_entrerios_iibb"]["layout_status"] == "layout_especifico"
    assert by_id["ater_entrerios_iibb"]["bloquea_importacion_masiva"] is False
    assert by_id["santafe_iibb"]["layout_status"] == "layout_especifico_pendiente_muestra"
    assert by_id["santafe_iibb"]["bloquea_importacion_masiva"] is True
    for fuente_id in ["cordoba_iibb", "jujuy_iibb", "mendoza_iibb", "tucuman_iibb"]:
        assert by_id[fuente_id]["layout_status"] == "layout_especifico_pendiente_muestra"
        assert by_id[fuente_id]["bloquea_importacion_masiva"] is True
    assert by_id["formosa_iibb"]["layout_status"] == "requiere_layout_especifico"


def test_markdown_backlog_incluye_resumen_y_criterio_de_terminado():
    module = load_module()
    markdown = module.render_markdown(module.audit_sources())

    assert "# Backlog de formatos y layouts de padrones" in markdown
    assert "Fuentes auditadas: 34" in markdown
    assert "Bloqueos de importación masiva" in markdown
    assert "Criterio de terminado por fuente" in markdown
    assert "`arba_iibb`" in markdown
    assert "`agip_caba_iibb`" in markdown
    assert "Validar layouts pendientes con muestra oficial real" in markdown
