from app.modules import regimenes_aplicables


def _resultado_base():
    return {
        "cuit": "30-00000000-0",
        "cuit_limpio": "30000000000",
        "valido": True,
        "afip": {
            "encontrado": True,
            "estado_clave": "ACTIVO",
            "condicion_iva": "RESPONSABLE INSCRIPTO (ACTIVO)",
            "condicion_ganancias": "GANANCIAS SOCIEDADES (ACTIVO)",
            "inscripciones_iibb": {
                "regimen": "Convenio Multilateral",
                "jurisdicciones": ["CABA", "Córdoba"],
                "impuestos": [{"descripcion": "CONVENIO MULTILATERAL", "estado": "ACTIVO"}],
            },
        },
        "georef": {"provincia": "CABA"},
        "padrones": {
            "CABA": {"status": "inscripto", "detalle": "Padrón vigente.", "nombre": "CABA / AGIP"},
            "Cordoba": {"status": "no_disponible", "detalle": "Falta archivo.", "nombre": "Córdoba"},
        },
    }


def test_deriva_regimenes_aplicables_pendientes_y_asistidos():
    data = regimenes_aplicables.generar(_resultado_base())
    por_id = {item["id"]: item for item in data["items"]}

    assert data["jurisdicciones_detectadas"] == ["CABA", "Córdoba"]
    assert por_id["arca_ganancias_rg830"]["clasificacion"] == "aplicable"
    assert por_id["agip_caba_iibb_ret_per"]["clasificacion"] == "aplicable"
    assert por_id["cordoba_iibb_ret_per"]["clasificacion"] == "pendiente_evidencia"
    assert por_id["comarb_sircar"]["clasificacion"] == "no_integrable_cola_asistida"
    assert por_id["municipal_tish_drei_generico"]["clasificacion"] == "pendiente_evidencia"
    assert all(item["evidencia_requerida"] for item in data["items"])
    assert all(item["proxima_accion"] for item in data["items"])


def test_no_deriva_regimenes_para_cuit_invalido():
    data = regimenes_aplicables.generar({"valido": False})

    assert data["items"] == []
    assert data["resumen"]["total"] == 0
    assert "CUIT inválido" in data["criterio"]
