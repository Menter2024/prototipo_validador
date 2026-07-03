"""Tests de la vigilancia de certificados propios."""
import json
from datetime import date

from fastapi.testclient import TestClient

from app import main
from app.modules import certificados

HOY = date(2026, 7, 3)


def _catalogo(tmp_path, items):
    path = tmp_path / "clientes.json"
    path.write_text(json.dumps({
        "version": 2,
        "clientes": [{
            "cliente": "CCU", "cuit": "30-50577985-8",
            "certificados_propios": {"items": items},
        }],
    }), encoding="utf-8")
    return path


def test_clasifica_vencido_por_vencer_y_vigente(tmp_path):
    path = _catalogo(tmp_path, [
        {"concepto": "Mendoza constancia agente", "vigencia_hasta": "2026-04-09"},
        {"concepto": "Sgo del Estero no ret", "vigencia_hasta": "2026-07-13"},
        {"concepto": "Ganancias RG830 exclusión", "vigencia_hasta": "2027-03-31"},
        {"concepto": "Nota bienes de uso"},
    ])

    resultado = certificados.evaluar(path, hoy=HOY)

    por_concepto = {i["concepto"]: i for i in resultado["items"]}
    assert por_concepto["Mendoza constancia agente"]["estado"] == "vencido"
    assert por_concepto["Sgo del Estero no ret"]["estado"] == "por_vencer"
    assert por_concepto["Sgo del Estero no ret"]["dias_restantes"] == 10
    assert por_concepto["Ganancias RG830 exclusión"]["estado"] == "vigente"
    assert por_concepto["Nota bienes de uso"]["estado"] == "sin_vigencia_registrada"
    assert resultado["resumen"]["vencidos"] == 1
    assert resultado["resumen"]["por_vencer"] == 1
    # Ordenados: vencidos primero.
    assert resultado["items"][0]["estado"] == "vencido"
    assert len(resultado["alertas"]) == 2


def test_catalogo_real_evalua_sin_errores():
    resultado = certificados.evaluar()
    assert resultado["resumen"]["total"] >= 1


def test_api_certificados(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)

    r = client.get("/api/certificados")

    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "alertas" in body and "resumen" in body
