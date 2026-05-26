from app.modules import georef


def test_georef_normaliza_provincia_sin_acentos(monkeypatch):
    monkeypatch.setattr(georef, "listar_provincias", lambda: ["Entre Ríos", "Santa Fe"])

    data = georef.normalizar_provincia("PARANA, ENTRE RIOS")

    assert data["provincia"] == "Entre Ríos"
