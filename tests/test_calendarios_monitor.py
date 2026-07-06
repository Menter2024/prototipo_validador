"""Tests del calendario de vencimientos en el monitor de fuentes (D2+D3)."""
from datetime import date

from fastapi.testclient import TestClient

from app import main
from app.modules import regimenes_catalogo


def test_calendarios_expone_los_regimenes_con_calendario():
    resultado = regimenes_catalogo.calendarios(hoy=date(2026, 7, 6))

    ids = {i["id"] for i in resultado["items"]}
    assert {"arca_sire", "arca_sicore", "comarb_sircar"} <= ids
    assert len(resultado["items"]) >= 7
    for item in resultado["items"]:
        assert item["norma_calendario"]
        assert item["fuente"].startswith("https://")


def test_verificacion_reciente_no_alerta_y_vieja_si():
    reciente = regimenes_catalogo.calendarios(hoy=date(2026, 7, 6))
    assert reciente["alertas"] == []
    assert all(not i["reverificacion_requerida"] for i in reciente["items"])

    # Simular que pasaron >120 días sin reverificar.
    viejo = regimenes_catalogo.calendarios(hoy=date(2026, 12, 15))
    assert viejo["alertas"], "debe alertar reverificación pendiente"
    assert all(i["reverificacion_requerida"] for i in viejo["items"])
    assert "sin reverificar" in viejo["alertas"][0]


def test_api_fuentes_incluye_calendarios(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)

    r = client.get("/api/fuentes")

    assert r.status_code == 200
    calendarios = r.json()["calendarios_regimenes"]
    assert calendarios["items"]
    assert "umbral_reverificacion_dias" in calendarios
