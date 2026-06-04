import json
from pathlib import Path


def test_registro_maestro_incluye_todas_las_fuentes_catalogadas():
    root = Path(__file__).resolve().parents[1]
    catalogo = json.loads((root / "config" / "fuentes_catalogo.json").read_text())
    registro = (root / "docs" / "REGISTRO_MAESTRO_PADRONES.md").read_text()

    faltantes = [f["id"] for f in catalogo["fuentes"] if f'`{f["id"]}`' not in registro]
    assert faltantes == []


def test_registro_maestro_documenta_obtencion_formato_y_mantenimiento():
    root = Path(__file__).resolve().parents[1]
    registro = (root / "docs" / "REGISTRO_MAESTRO_PADRONES.md").read_text()

    assert "Obtención oficial" in registro
    assert "Formato / instructivo" in registro
    assert "Reglas de mantenimiento" in registro
    assert "Checklist por fuente antes de automatizar" in registro
    assert "config/fuentes_catalogo.json" in registro
    assert "config/padron_layouts.json" in registro
