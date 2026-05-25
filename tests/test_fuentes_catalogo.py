from pathlib import Path

from app.modules import fuentes_catalogo, padron_manifest


def test_evalua_padron_faltante_como_alerta_critica(tmp_path: Path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        """
        {
          "version": 1,
          "fuentes": [{
            "id": "arba_iibb",
            "padron_key": "ARBA",
            "nombre": "ARBA",
            "jurisdiccion": "Buenos Aires",
            "organismo": "ARBA",
            "regimenes": ["iibb"],
            "clase": "padron_descargable",
            "prioridad": "P1",
            "frecuencia": "mensual",
            "dias_alerta": 7,
            "url": "https://web.arba.gov.ar/"
          }]
        }
        """,
        encoding="utf-8",
    )

    estado = fuentes_catalogo.evaluar_fuentes(tmp_path, catalog)

    assert estado["resumen"]["criticas"] == 1
    assert estado["fuentes"][0]["estado"] == "pendiente_carga"
    assert estado["alertas"][0]["riesgo"] == "critico"


def test_evalua_padron_cargado_y_vigente(tmp_path: Path):
    (tmp_path / "PadronARBA.csv").write_text(
        "cuit,alicuota_retencion,alicuota_percepcion\n30500010912,1,2\n",
        encoding="utf-8",
    )
    padron_manifest.registrar_carga(
        tmp_path,
        "ARBA",
        "PadronARBA.csv",
        1,
        "test",
        "2026-05",
        "2099-12-31",
        None,
    )
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        """
        {
          "version": 1,
          "fuentes": [{
            "id": "arba_iibb",
            "padron_key": "ARBA",
            "nombre": "ARBA",
            "jurisdiccion": "Buenos Aires",
            "organismo": "ARBA",
            "regimenes": ["iibb"],
            "clase": "padron_descargable",
            "prioridad": "P1",
            "frecuencia": "mensual",
            "dias_alerta": 7,
            "url": "https://web.arba.gov.ar/"
          }]
        }
        """,
        encoding="utf-8",
    )

    estado = fuentes_catalogo.evaluar_fuentes(tmp_path, catalog)

    assert estado["resumen"]["criticas"] == 0
    assert estado["fuentes"][0]["estado"] == "vigente"
    assert estado["fuentes"][0]["registros"] == 1
