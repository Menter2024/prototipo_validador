from pathlib import Path

from app.modules import supabase_mvp
from scripts.process_padron_job import process_padron_import_job


def test_process_padron_import_job_normaliza_y_registra_version(monkeypatch, tmp_path):
    job = {
        "id": "job-1",
        "tenant_id": "tenant-1",
        "provincia": "Tucuman",
        "periodo": "2026-06",
        "vigencia_hasta": None,
        "fuente_id": None,
        "estado": "upload_completo",
        "storage_original_path": "ccu/padrones/Tucuman/2026-06/original/job-1/padron.csv",
        "archivo_nombre": "padron.csv",
    }
    updates = []
    versions = []

    def fake_download(_remote, local_path: Path):
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(
            "cuit,alicuota_retencion,alicuota_percepcion\n30718869966,1.00,2.00\n",
            encoding="utf-8",
        )
        return {"sha256": supabase_mvp.sha256_file(local_path), "size": local_path.stat().st_size}

    def fake_insert(table, payload):
        if table == "padron_versiones":
            payload = {"id": "version-1", **payload}
            versions.append(payload)
            return {"data": [payload]}
        raise AssertionError(table)

    monkeypatch.setattr(supabase_mvp, "get_config", lambda: supabase_mvp.SupabaseConfig("https://demo.supabase.co", "secret", tenant_slug="ccu"))
    monkeypatch.setattr(supabase_mvp, "get_padron_import_job", lambda job_id: job)
    monkeypatch.setattr(supabase_mvp, "update_padron_import_job", lambda job_id, patch: updates.append((job_id, patch)))
    monkeypatch.setattr(supabase_mvp, "download_file", fake_download)
    monkeypatch.setattr(supabase_mvp, "upload_file", lambda local_path, remote, **kwargs: {"sha256": supabase_mvp.sha256_file(local_path), "path": remote})
    monkeypatch.setattr(supabase_mvp, "insert_row", fake_insert)

    result = process_padron_import_job("job-1", tmp_path)

    assert result["ok"] is True
    assert result["version_id"] == "version-1"
    assert result["registros_validos"] == 1
    assert versions[0]["estado"] == "pendiente_validacion"
    assert versions[0]["storage_normalizado_path"].endswith("/PadronTucuman.csv")
    assert updates[-1][1]["estado"] == "completado"


def test_process_padron_import_job_marca_fallido(monkeypatch, tmp_path):
    job = {
        "id": "job-1",
        "tenant_id": "tenant-1",
        "provincia": "Tucuman",
        "estado": "upload_completo",
        "storage_original_path": "missing",
        "archivo_nombre": "padron.csv",
    }
    updates = []
    monkeypatch.setattr(supabase_mvp, "get_padron_import_job", lambda job_id: job)
    monkeypatch.setattr(supabase_mvp, "update_padron_import_job", lambda job_id, patch: updates.append((job_id, patch)))
    monkeypatch.setattr(supabase_mvp, "download_file", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("storage error")))

    try:
        process_padron_import_job("job-1", tmp_path)
    except RuntimeError:
        pass

    assert updates[-1][1]["estado"] == "fallido"
    assert updates[-1][1]["errores"] == ["storage error"]
