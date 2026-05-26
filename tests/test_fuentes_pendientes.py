from pathlib import Path

from app.modules import fuentes_pendientes


def test_crea_tareas_desde_fuentes_asistidas_y_deduplica(tmp_path: Path):
    resultados = [{
        "valido": True,
        "cuit": "30-50001091-2",
        "cuit_limpio": "30500010912",
        "afip": {"razon_social": "PROVEEDOR SA"},
        "fuentes_online": {
            "RioNegro": {
                "estado": "requiere_captcha",
                "nombre": "Río Negro",
                "detalle": "CAPTCHA",
                "url_consulta": "https://example.com",
            }
        },
        "padrones": {},
    }]

    creadas_1 = fuentes_pendientes.crear_desde_resultados(tmp_path, resultados, "legajo_1")
    creadas_2 = fuentes_pendientes.crear_desde_resultados(tmp_path, resultados, "legajo_1")
    listado = fuentes_pendientes.listar(tmp_path)

    assert len(creadas_1) == 1
    assert len(creadas_2) == 1
    assert listado["resumen"]["total"] == 1
    assert listado["items"][0]["tipo_requerimiento"] == "requiere_captcha"


def test_actualiza_tarea_con_estado_y_nota(tmp_path: Path):
    item = {
        "id": "fp_test",
        "estado": "pendiente",
        "prioridad": "P3",
        "cuit_limpio": "30500010912",
        "fuente": "RioNegro",
        "tipo_requerimiento": "requiere_captcha",
        "historial": [],
        "evidencias": [],
    }
    fuentes_pendientes.crear_item(tmp_path, item)

    actualizado = fuentes_pendientes.actualizar(tmp_path, "fp_test", "resuelto", "Se adjunta constancia.")

    assert actualizado["estado"] == "resuelto"
    assert actualizado["historial"][0]["nota"] == "Se adjunta constancia."
