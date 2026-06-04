from pathlib import Path

from app.modules import supabase_mvp


def test_supabase_status_disabled(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    status = supabase_mvp.status()

    assert status["enabled"] is False
    assert status["bucket"] == "menter-fiscal"
    assert status["service_role_configurado"] is False


def test_storage_path_sanitizes_segments():
    assert supabase_mvp.storage_path("ccu", "../padrones", "ARBA", "file.csv") == "ccu/padrones/ARBA/file.csv"


def test_sha256_file(tmp_path: Path):
    archivo = tmp_path / "demo.txt"
    archivo.write_text("abc", encoding="utf-8")

    assert supabase_mvp.sha256_file(archivo) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_migration_has_rls_and_private_bucket():
    sql = Path("supabase/migrations/001_mvp_ccu_schema.sql").read_text(encoding="utf-8")

    assert "enable row level security" in sql
    assert "menter-fiscal" in sql
    assert "public, file_size_limit" in sql
    assert "No se crean políticas públicas" in sql


def test_padron_import_jobs_migration_schema():
    sql = Path("supabase/migrations/002_padron_import_jobs.sql").read_text(encoding="utf-8")

    assert "create table if not exists public.padron_import_jobs" in sql
    assert "pendiente_upload" in sql
    assert "upload_completo" in sql
    assert "procesando" in sql
    assert "completado" in sql
    assert "enable row level security" in sql
    assert "import_job_id" in sql


def test_create_padron_import_job_builds_storage_path(monkeypatch):
    cfg = supabase_mvp.SupabaseConfig("https://demo.supabase.co", "secret", tenant_slug="ccu")
    inserted = {}

    monkeypatch.setattr(supabase_mvp, "get_config", lambda: cfg)
    monkeypatch.setattr(supabase_mvp, "tenant_id", lambda: "tenant-1")
    monkeypatch.setattr(supabase_mvp, "insert_row", lambda table, payload: inserted.setdefault("value", {"data": [payload]}))
    monkeypatch.setattr(supabase_mvp, "create_signed_upload_url", lambda remote: {"enabled": True, "signed": True, "path": remote})

    res = supabase_mvp.create_padron_import_job(
        provincia="CABA",
        archivo_nombre="padron.zip",
        periodo="2026-06",
        tamano_bytes=123,
    )

    assert res["created"] is True
    job = res["job"]
    assert job["estado"] == "pendiente_upload"
    assert job["storage_original_path"].startswith("ccu/padrones/CABA/2026-06/original/")
    assert job["storage_original_path"].endswith("/padron.zip")
    assert res["upload"]["path"] == job["storage_original_path"]


def test_padrones_uses_supabase_when_local_file_missing(monkeypatch, tmp_path):
    from app.modules import padrones

    def fake_buscar(cuit, provincia):
        if provincia != "EntreRios":
            return None
        return {
            "encontrado": True,
            "alicuota_retencion": "1.00",
            "alicuota_percepcion": "2.00",
            "vigencia_desde": "2026-05-01",
            "vigencia_hasta": "2026-05-31",
            "regimen": "ATER",
            "fuente": "supabase",
        }

    monkeypatch.setattr(padrones.supabase_mvp, "buscar_padron_registro", fake_buscar)
    monkeypatch.setattr(padrones.supabase_mvp, "provincia_tiene_padron_activo", lambda provincia: provincia == "EntreRios")

    res = padrones.consultar_todos("30546689979", tmp_path)

    assert res["EntreRios"]["status"] == "inscripto"
    assert res["EntreRios"]["fuente"] == "supabase"
    assert res["ARBA"]["status"] == "no_disponible"


def test_padrones_prefers_supabase_over_local_file(monkeypatch, tmp_path):
    from app.modules import padrones

    (tmp_path / "PadronEntreRios.csv").write_text(
        "cuit,alicuota_retencion,alicuota_percepcion\n20999999999,1,1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(padrones.supabase_mvp, "buscar_padron_registro", lambda cuit, provincia: {
        "encontrado": True,
        "alicuota_retencion": "3,00",
        "alicuota_percepcion": "3,00",
        "vigencia_desde": "2026-05-01",
        "vigencia_hasta": "2026-05-31",
        "regimen": "",
        "fuente": "supabase",
    } if provincia == "EntreRios" else None)
    monkeypatch.setattr(padrones.supabase_mvp, "provincia_tiene_padron_activo", lambda provincia: provincia == "EntreRios")

    res = padrones.consultar_todos("30718869966", tmp_path)

    assert res["EntreRios"]["status"] == "inscripto"
    assert res["EntreRios"]["fuente"] == "supabase"
    assert "3,00" in res["EntreRios"]["detalle"]
