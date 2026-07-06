"""Tests de la persistencia durable de legajos (dual-write local + Supabase)."""
import json

from app.modules import legajos


def _resultados() -> list[dict]:
    return [{
        "cuit": "30-50577985-8", "cuit_limpio": "30505779858", "valido": True,
        "modo_afip": "live",
        "afip": {"razon_social": "CICSA", "estado_clave": "ACTIVO"},
        "decision_fiscal": {"label": "OBSERVADO", "estado": "OBSERVADO"},
        "padrones": {},
    }]


def test_crear_legajo_sincroniza_a_supabase(tmp_path, monkeypatch):
    capturado = {}

    def fake_sync(legajo):
        capturado.update(legajo)
        return {"enabled": True, "synced": True}

    monkeypatch.setattr(legajos.supabase_mvp, "sync_legajo", fake_sync)

    creado = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)

    assert creado["supabase_sync"]["synced"] is True
    assert capturado["id"] == creado["id"]
    assert capturado["sha256"] == creado["sha256"]
    assert capturado["estado"] == "cerrado"


def test_fallo_de_sync_no_rompe_el_flujo_local(tmp_path, monkeypatch):
    def explota(_legajo):
        raise RuntimeError("supabase caído")

    monkeypatch.setattr(legajos.supabase_mvp, "sync_legajo", explota)

    creado = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)

    assert creado["supabase_sync"]["synced"] is False
    assert "supabase caído" in creado["supabase_sync"]["error"]
    assert (tmp_path / "legajos" / f"{creado['id']}.json").exists()


def test_listado_fusiona_local_y_remoto_sin_duplicar(tmp_path, monkeypatch):
    creado = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)

    remotos = [
        {"id": creado["id"], "creado_en": creado["creado_en"], "estado": "cerrado",
         "operador": {"usuario": "remoto"}, "sha256": "x", "excel": "", "total_proveedores": 1, "resumen": []},
        {"id": "legajo_20260101_000000_deadbeef", "creado_en": "2026-01-01 00:00:00", "estado": "cerrado",
         "operador": {"usuario": "ana"}, "sha256": "y", "excel": "viejo.xlsx", "total_proveedores": 2, "resumen": []},
    ]
    monkeypatch.setattr(legajos.supabase_mvp, "list_legajos_remotos", lambda: remotos)

    items = legajos.listar_legajos(tmp_path)

    assert len(items) == 2
    por_id = {i["id"]: i for i in items}
    assert por_id[creado["id"]]["fuente"] == "local"  # el local gana sobre el remoto duplicado
    assert por_id["legajo_20260101_000000_deadbeef"]["fuente"] == "supabase"
    assert items[0]["id"] == creado["id"]  # orden descendente por fecha


def test_obtener_cae_a_supabase_con_integridad_valida(tmp_path, monkeypatch):
    """Simula el redeploy: el archivo local desaparece y el legajo vuelve de Supabase intacto."""
    creado = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)
    path = tmp_path / "legajos" / f"{creado['id']}.json"
    persistido = json.loads(path.read_text(encoding="utf-8"))
    path.unlink()  # el disco efímero se llevó el archivo

    monkeypatch.setattr(legajos.supabase_mvp, "get_legajo_remoto", lambda _id: dict(persistido))

    legajo = legajos.obtener_legajo(tmp_path, creado["id"])

    assert legajo is not None
    assert legajo["fuente"] == "supabase"
    assert legajo["integridad"]["valido"] is True

    # Un remoto adulterado tiene que quedar en evidencia.
    adulterado = dict(persistido)
    adulterado["resumen"] = [{"cuit": "30-50577985-8", "decision": "APROBABLE"}]
    monkeypatch.setattr(legajos.supabase_mvp, "get_legajo_remoto", lambda _id: adulterado)
    assert legajos.obtener_legajo(tmp_path, creado["id"])["integridad"]["valido"] is False


def test_sin_supabase_todo_sigue_local(tmp_path, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    creado = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)

    assert creado["supabase_sync"]["synced"] is False
    assert legajos.listar_legajos(tmp_path)[0]["fuente"] == "local"
    assert legajos.obtener_legajo(tmp_path, creado["id"])["integridad"]["valido"] is True
