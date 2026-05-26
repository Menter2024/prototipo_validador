from fastapi.testclient import TestClient

from app import main


def test_api_regimenes_devuelve_resumen_y_backlog(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "PADRONES_DIR", tmp_path / "padrones")
    main.PADRONES_DIR.mkdir()
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)

    r = client.get("/api/regimenes")

    assert r.status_code == 200
    data = r.json()
    assert data["resumen"]["total_regimenes"] >= 20
    assert data["resumen"]["criticos_o_prioritarios_pendientes"] >= 1
    assert data["filtros_disponibles"]["nivel"]
    assert any(item["backlog_estado"] for item in data["regimenes"])


def test_api_regimenes_filtra_por_nivel(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "PADRONES_DIR", tmp_path / "padrones")
    main.PADRONES_DIR.mkdir()
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)

    r = client.get("/api/regimenes?nivel=municipal")

    assert r.status_code == 200
    data = r.json()
    assert data["regimenes"]
    assert {item["nivel"] for item in data["regimenes"]} == {"municipal"}


def test_regimenes_page_disponible(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)

    r = client.get("/regimenes")

    assert r.status_code == 200
    assert "Mapa de regímenes fiscales" in r.text
