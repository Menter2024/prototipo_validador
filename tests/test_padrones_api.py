from pathlib import Path

from fastapi.testclient import TestClient

from app import main

FIXTURES = Path(__file__).parent / "fixtures" / "padrones_no_estandar"


def _client(tmp_path, monkeypatch):
    padrones_dir = tmp_path / "padrones"
    uploads_dir = tmp_path / "uploads"
    padrones_dir.mkdir()
    uploads_dir.mkdir()
    monkeypatch.setattr(main, "PADRONES_DIR", padrones_dir)
    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    return TestClient(main.app), padrones_dir


def _upload(path: Path, content_type: str = "text/csv"):
    return {"archivo": (path.name, path.read_bytes(), content_type)}


def test_previsualizar_padron_no_escribe_archivo(tmp_path, monkeypatch):
    client, padrones_dir = _client(tmp_path, monkeypatch)
    origen = FIXTURES / "tucuman_abreviado.csv"

    r = client.post(
        "/api/padrones/previsualizar",
        data={"provincia": "Tucuman", "periodo": "2026-06", "vigencia_hasta": "2026-06-30"},
        files=_upload(origen),
    )

    assert r.status_code == 200
    data = r.json()
    assert data["dry_run"] is True
    assert data["calidad"]["perfil"] == "Tucumán · RG 23/02"
    assert data["evidencia"]["sha256"]
    assert not (padrones_dir / "PadronTucuman.csv").exists()


def test_importar_observado_sin_confirmacion_devuelve_400(tmp_path, monkeypatch):
    client, padrones_dir = _client(tmp_path, monkeypatch)
    origen = FIXTURES / "cordoba_headerless.zip"

    r = client.post(
        "/api/padrones/importar",
        data={"provincia": "Cordoba"},
        files=_upload(origen, "application/zip"),
    )

    assert r.status_code == 400
    assert "confirm" in r.json()["detail"].lower()
    assert not (padrones_dir / "PadronCordoba.csv").exists()


def test_importar_observado_con_confirmacion_escribe_manifest(tmp_path, monkeypatch):
    client, padrones_dir = _client(tmp_path, monkeypatch)
    origen = FIXTURES / "cordoba_headerless.zip"

    r = client.post(
        "/api/padrones/importar",
        data={"provincia": "Cordoba", "confirmar_advertencias": "true", "periodo": "2026-06"},
        files=_upload(origen, "application/zip"),
    )

    assert r.status_code == 200
    data = r.json()
    assert data["calidad"]["estado"] == "observado"
    assert data["evidencia"]["extractor"] == "zipfile"
    assert (padrones_dir / "PadronCordoba.csv").exists()
    assert (padrones_dir / "padrones_manifest.json").exists()


def test_importar_aprobado_no_requiere_confirmacion(tmp_path, monkeypatch):
    client, padrones_dir = _client(tmp_path, monkeypatch)
    origen = FIXTURES / "jujuy_layout.xlsx"

    r = client.post(
        "/api/padrones/importar",
        data={"provincia": "Jujuy", "periodo": "2026-06", "vigencia_hasta": "2026-06-30"},
        files=_upload(origen, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    )

    assert r.status_code == 200
    data = r.json()
    assert data["calidad"]["estado"] == "aprobado"
    assert (padrones_dir / "PadronJujuy.csv").exists()
