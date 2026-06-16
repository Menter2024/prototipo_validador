from fastapi.testclient import TestClient

from app import main
from app.modules import clientes_agentes


def test_listar_cliente_cicsa_modulo():
    data = clientes_agentes.listar()
    assert data["total_clientes"] >= 1
    cicsa = clientes_agentes.obtener("30-50577985-8")
    assert cicsa is not None
    assert cicsa["razon_social"] == "CIA INDUSTRIAL CERVECERA S A"
    # Debe haber regímenes que genera (retención/percepción) y que responde (información).
    roles = cicsa["resumen"]["por_rol"]
    assert roles.get("genera", 0) >= 1
    assert roles.get("responde", 0) >= 1


def test_obtener_por_nombre_cliente():
    cicsa = clientes_agentes.obtener("CCU")
    assert cicsa is not None
    assert clientes_agentes._norm_cuit(cicsa["cuit"]) == "30505779858"


def test_api_clientes_agentes(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)

    r = client.get("/api/clientes-agentes")
    assert r.status_code == 200
    body = r.json()
    assert body["total_clientes"] >= 1

    # Filtro por CUIT con guiones debe normalizar y encontrar a CICSA.
    r2 = client.get("/api/clientes-agentes", params={"cuit": "30-50577985-8"})
    assert r2.status_code == 200
    clientes = r2.json()["clientes"]
    assert len(clientes) == 1
    assert clientes[0]["cuit_limpio"] == "30505779858"
    assert "resumen" in clientes[0]


def test_pagina_clientes_agentes_resuelve(monkeypatch):
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    client = TestClient(main.app)
    r = client.get("/clientes-agentes")
    assert r.status_code == 200
    assert "Regímenes del cliente" in r.text
