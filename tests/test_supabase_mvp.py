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
