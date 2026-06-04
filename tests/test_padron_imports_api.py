from fastapi.testclient import TestClient

from app import main


def _client(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    return TestClient(main.app)


def test_listar_imports_sin_supabase_devuelve_vacio(monkeypatch):
    client = _client(monkeypatch)
    monkeypatch.setattr(main.supabase_mvp, "enabled", lambda: False)

    r = client.get("/api/padron-imports")

    assert r.status_code == 200
    assert r.json()["enabled"] is False
    assert r.json()["imports"] == []


def test_crear_import_valida_provincia(monkeypatch):
    client = _client(monkeypatch)

    r = client.post("/api/padron-imports", json={"provincia": "NoExiste", "archivo_nombre": "padron.csv"})

    assert r.status_code == 400


def test_crear_import_asistido(monkeypatch):
    client = _client(monkeypatch)
    monkeypatch.setattr(main.supabase_mvp, "create_padron_import_job", lambda **kwargs: {
        "enabled": True,
        "created": True,
        "job": {"id": "job-1", "estado": "pendiente_upload", **kwargs},
        "upload": {"signed": True, "path": "ccu/padrones/CABA/2026-06/original/job-1/padron.csv"},
    })

    r = client.post("/api/padron-imports", json={
        "provincia": "CABA",
        "archivo_nombre": "padron.csv",
        "periodo": "2026-06",
        "tamano_bytes": 100,
    })

    assert r.status_code == 200
    data = r.json()
    assert data["created"] is True
    assert data["job"]["provincia"] == "CABA"


def test_confirmar_upload_actualiza_estado(monkeypatch):
    client = _client(monkeypatch)
    updates = []
    monkeypatch.setattr(main.supabase_mvp, "get_padron_import_job", lambda job_id: {"id": job_id, "estado": "pendiente_upload"})
    monkeypatch.setattr(main.supabase_mvp, "update_padron_import_job", lambda job_id, patch: updates.append((job_id, patch)))

    r = client.post("/api/padron-imports/job-1/confirm-upload", json={"sha256_original": "abc", "tamano_bytes": 123})

    assert r.status_code == 200
    assert updates == [("job-1", {"estado": "upload_completo", "sha256_original": "abc", "tamano_bytes": 123})]


def test_preparar_process_requiere_upload_completo(monkeypatch):
    client = _client(monkeypatch)
    monkeypatch.setattr(main.supabase_mvp, "get_padron_import_job", lambda job_id: {"id": job_id, "estado": "pendiente_upload"})

    r = client.post("/api/padron-imports/job-1/process", json={})

    assert r.status_code == 409


def test_preparar_process_pasa_a_pendiente(monkeypatch):
    client = _client(monkeypatch)
    updates = []
    monkeypatch.setattr(main.supabase_mvp, "get_padron_import_job", lambda job_id: {"id": job_id, "estado": "upload_completo", "job_metadata": {}})
    monkeypatch.setattr(main.supabase_mvp, "update_padron_import_job", lambda job_id, patch: updates.append((job_id, patch)))

    r = client.post("/api/padron-imports/job-1/process", json={})

    assert r.status_code == 200
    assert updates[0][1]["estado"] == "pendiente_proceso"
    assert r.json()["env"]["PADRON_IMPORT_JOB_ID"] == "job-1"
