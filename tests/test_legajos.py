"""Tests de sellado, integridad y versionado de reglas del legajo fiscal."""
import json

from app.modules import legajos, padron_manifest


def _resultados() -> list[dict]:
    return [{
        "cuit": "30-50577985-8",
        "cuit_limpio": "30505779858",
        "valido": True,
        "modo_afip": "live",
        "afip": {"razon_social": "CICSA", "estado_clave": "ACTIVO"},
        "decision_fiscal": {"label": "OBSERVADO", "estado": "OBSERVADO"},
        "padrones": {"ARBA": {"status": "inscripto"}},
    }]


def _armar_manifest(padrones_dir) -> None:
    padron_manifest.guardar_manifest(padrones_dir, {
        "version": 1,
        "padrones": {"ARBA": {
            "periodo": "2026-06", "sha256": "abc123",
            "vigencia_hasta": "2026-07-31", "cargado_en": "2026-06-01 10:00:00",
        }},
        "historial": [],
    })


def test_legajo_se_sella_con_hash_y_estado_cerrado(tmp_path):
    _armar_manifest(tmp_path)

    legajo = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path, tmp_path)

    assert legajo["estado"] == "cerrado"
    assert len(legajo["sha256"]) == 64
    assert legajo["reglas_aplicadas"]["regimenes_catalogo"]["version"] is not None
    assert legajo["reglas_aplicadas"]["clientes_agentes"]["version"] is not None
    assert legajo["padrones_snapshot"]["ARBA"]["periodo"] == "2026-06"
    assert legajo["padrones_snapshot"]["ARBA"]["sha256"] == "abc123"


def test_integridad_valida_y_detecta_adulteracion(tmp_path):
    creado = legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)

    legajo = legajos.obtener_legajo(tmp_path, creado["id"])
    assert legajo["integridad"]["valido"] is True

    # Adulterar el archivo: la verificación tiene que fallar.
    path = tmp_path / "legajos" / f"{creado['id']}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["resumen"][0]["decision"] = "APROBABLE"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    adulterado = legajos.obtener_legajo(tmp_path, creado["id"])
    assert adulterado["integridad"]["valido"] is False


def test_listado_expone_estado_y_hash(tmp_path):
    legajos.crear_legajo(_resultados(), "salida.xlsx", tmp_path)

    items = legajos.listar_legajos(tmp_path)

    assert items[0]["estado"] == "cerrado"
    assert items[0]["sha256"]
