from pathlib import Path

import pytest

from app.modules import accesos_fiscales


def test_crea_y_actualiza_acceso_por_clave_logica(tmp_path: Path):
    acceso = accesos_fiscales.crear_o_actualizar(
        tmp_path,
        "CCU",
        "30-50001091-2",
        "COMARB",
        "SIRCREB",
        "credencial_delegada",
        "pendiente",
        "comarb_sircreb",
        "Sólo descarga padrones",
        "Impuestos CCU",
        "Solicitar autorización",
    )
    actualizado = accesos_fiscales.crear_o_actualizar(
        tmp_path,
        "CCU",
        "30500010912",
        "COMARB",
        "SIRCREB",
        "credencial_delegada",
        "autorizado",
        "comarb_sircreb",
        "Sólo descarga padrones",
        "Impuestos CCU",
        "Autorizado por piloto",
    )

    data = accesos_fiscales.listar(tmp_path)
    assert len(data["accesos"]) == 1
    assert actualizado["id"] == acceso["id"]
    assert data["accesos"][0]["estado"] == "autorizado"
    assert data["resumen"]["autorizados"] == 1


def test_rechaza_cuit_y_estado_invalidos(tmp_path: Path):
    with pytest.raises(ValueError, match="CUIT"):
        accesos_fiscales.crear_o_actualizar(tmp_path, "CCU", "123", "ARBA", "RGS", "archivo_manual")

    with pytest.raises(ValueError, match="Estado"):
        accesos_fiscales.crear_o_actualizar(tmp_path, "CCU", "30500010912", "ARBA", "RGS", "archivo_manual", "mal")


def test_matriz_requisitos_detecta_fuentes_con_credenciales(tmp_path: Path):
    fuentes_estado = {
        "fuentes": [
            {"id": "arba_iibb", "nombre": "ARBA", "organismo": "ARBA", "jurisdiccion": "Buenos Aires", "prioridad": "P0", "tipo_acceso": "portal_credenciales", "descarga": {"modo": "portal_credenciales"}},
            {"id": "agip_caba_iibb", "nombre": "AGIP", "organismo": "AGIP", "jurisdiccion": "CABA", "prioridad": "P0", "tipo_acceso": "pagina_publica_links", "descarga": {"modo": "pagina_publica_links"}},
        ]
    }

    matriz = accesos_fiscales.matriz_requisitos(tmp_path, fuentes_estado)

    assert len(matriz["items"]) == 1
    assert matriz["items"][0]["fuente_id"] == "arba_iibb"
    assert matriz["items"][0]["estado_acceso"] == "pendiente"
