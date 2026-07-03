"""Tests de vigencia de padrones en la consulta y la decisión fiscal."""
from datetime import date, timedelta

from app.modules import matriz_tributaria, padron_manifest, padrones, riesgo_fiscal

CUIT = "30505779858"


def _armar_padron(tmp_path, vigencia_hasta: str) -> None:
    (tmp_path / "PadronARBA.csv").write_text(
        "cuit;retencion;percepcion;desde;hasta;regimen\n"
        f"{CUIT};1,00;0,50;2026-01-01;2026-12-31;General\n",
        encoding="utf-8",
    )
    padron_manifest.guardar_manifest(tmp_path, {
        "version": 1,
        "padrones": {"ARBA": {"vigencia_hasta": vigencia_hasta}},
        "historial": [],
    })


def test_padron_vencido_no_se_declara_vigente(tmp_path):
    ayer = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    _armar_padron(tmp_path, ayer)

    resultado = padrones.consultar_todos(CUIT, tmp_path)["ARBA"]

    assert resultado["status"] == "inscripto"
    assert resultado["vigencia_estado"] == "vencido"
    assert "VENCIDO" in resultado["detalle"]
    assert "Padrón vigente." not in resultado["detalle"]


def test_padron_vigente_se_declara_vigente(tmp_path):
    futuro = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")
    _armar_padron(tmp_path, futuro)

    resultado = padrones.consultar_todos(CUIT, tmp_path)["ARBA"]

    assert resultado["vigencia_estado"] == "vigente"
    assert resultado["detalle"].startswith("Padrón vigente.")


def test_no_inscripto_tambien_propaga_vigencia(tmp_path):
    ayer = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    _armar_padron(tmp_path, ayer)

    resultado = padrones.consultar_todos("30500010912", tmp_path)["ARBA"]

    assert resultado["status"] == "no_inscripto"
    assert resultado["vigencia_estado"] == "vencido"


def test_riesgo_degrada_a_observado_con_padron_vencido():
    decision = riesgo_fiscal.evaluar({
        "valido": True,
        "afip": {"encontrado": True, "estado_clave": "ACTIVO", "en_apoc": False},
        "padrones": {
            "ARBA": {"status": "inscripto", "vigencia_estado": "vencido", "nombre": "Buenos Aires / ARBA"},
        },
        "fuentes_online": {},
    })

    assert decision["estado"] != "APROBABLE"
    assert any("vencidos" in m for m in decision["motivos"])


def test_matriz_alerta_alicuotas_de_padron_vencido():
    matriz = matriz_tributaria.generar({
        "valido": True,
        "afip": {"condicion_iva": "RESPONSABLE INSCRIPTO", "inscripciones_iibb": {"jurisdicciones": []}},
        "georef": {"provincia": None},
        "padrones": {
            "ARBA": {
                "status": "inscripto",
                "nombre": "Buenos Aires / ARBA",
                "vigencia_estado": "vencido",
                "vigencia_hasta_padron": "2026-05-31",
                "alicuota_retencion": "1.00",
                "alicuota_percepcion": "0.50",
            },
        },
    })

    assert any("padrón vencido" in a for a in matriz["alertas"])
