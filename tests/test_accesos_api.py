from pathlib import Path

from fastapi.testclient import TestClient

from app import main


def _client(tmp_path, monkeypatch):
    salidas_dir = tmp_path / "salidas"
    uploads_dir = tmp_path / "uploads"
    padrones_dir = tmp_path / "padrones"
    salidas_dir.mkdir()
    uploads_dir.mkdir()
    padrones_dir.mkdir()
    monkeypatch.setattr(main, "SALIDAS_DIR", salidas_dir)
    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(main, "PADRONES_DIR", padrones_dir)
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    return TestClient(main.app)


def test_api_accesos_crea_y_lista(monkeypatch, tmp_path):
    client = _client(tmp_path, monkeypatch)

    r = client.post("/api/accesos", data={
        "cliente": "CCU",
        "cuit_agente": "30-50001091-2",
        "organismo": "COMARB",
        "servicio": "SIRCREB",
        "tipo_acceso": "credencial_delegada",
        "estado": "pendiente",
        "fuente_id": "comarb_sircreb",
        "alcance": "Sólo descarga padrones",
        "responsable": "Impuestos",
        "notas": "Piloto",
    })

    assert r.status_code == 200
    assert r.json()["acceso"]["cliente"] == "CCU"

    listado = client.get("/api/accesos")

    assert listado.status_code == 200
    data = listado.json()
    assert data["resumen"]["total"] == 1
    assert data["accesos"][0]["fuente_id"] == "comarb_sircreb"
    assert data["requisitos"]["items"]


def test_accesos_page_disponible(monkeypatch, tmp_path):
    client = _client(tmp_path, monkeypatch)

    r = client.get("/accesos")

    assert r.status_code == 200
    assert "Accesos fiscales" in r.text


def test_importar_padron_registra_acceso_manual(monkeypatch, tmp_path):
    client = _client(tmp_path, monkeypatch)
    origen = tmp_path / "padron.csv"
    origen.write_text("cuit,alicuota_retencion,alicuota_percepcion\n30500010912,1,2\n", encoding="utf-8")

    r = client.post(
        "/api/padrones/importar",
        data={
            "provincia": "ARBA",
            "periodo": "2026-06",
            "vigencia_hasta": "2026-06-30",
            "cliente": "CCU",
            "cuit_agente": "30-50001091-2",
            "fuente_id": "arba_iibb",
        },
        files={"archivo": ("padron.csv", origen.read_bytes(), "text/csv")},
    )

    assert r.status_code == 200
    accesos = client.get("/api/accesos").json()["accesos"]
    assert accesos[0]["estado"] == "exportacion_manual"
    assert accesos[0]["fuente_id"] == "arba_iibb"
