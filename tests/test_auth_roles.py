"""Tests de multi-usuario con roles y registro del operador en el legajo."""
import base64

from fastapi.testclient import TestClient

from app import main


def _auth(usuario: str, password: str) -> dict:
    token = base64.b64encode(f"{usuario}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _client(monkeypatch, users: str = "") -> TestClient:
    monkeypatch.delenv("BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("BASIC_AUTH_PASS", raising=False)
    if users:
        monkeypatch.setenv("MENTER_USERS", users)
    else:
        monkeypatch.delenv("MENTER_USERS", raising=False)
    return TestClient(main.app)


def test_sin_usuarios_configurados_no_exige_auth(monkeypatch):
    client = _client(monkeypatch)
    assert client.get("/dashboard").status_code == 200


def test_multiusuario_valida_credenciales_y_roles(monkeypatch):
    client = _client(monkeypatch, "ana:clave1:impuestos,juan:clave2:compras")

    assert client.get("/dashboard").status_code == 401
    assert client.get("/dashboard", headers=_auth("ana", "incorrecta")).status_code == 401
    assert client.get("/dashboard", headers=_auth("ana", "clave1")).status_code == 200
    assert client.get("/dashboard", headers=_auth("juan", "clave2")).status_code == 200


def test_rol_invalido_cae_a_admin(monkeypatch):
    monkeypatch.setenv("MENTER_USERS", "root:x:superusuario")
    usuarios = main._usuarios_configurados()
    assert usuarios["root"]["rol"] == "admin"


def test_basic_auth_legacy_sigue_funcionando(monkeypatch):
    monkeypatch.setenv("BASIC_AUTH_USER", "legacy")
    monkeypatch.setenv("BASIC_AUTH_PASS", "clave")
    monkeypatch.delenv("MENTER_USERS", raising=False)
    client = TestClient(main.app)

    assert client.get("/dashboard").status_code == 401
    assert client.get("/dashboard", headers=_auth("legacy", "clave")).status_code == 200
    assert main._usuarios_configurados()["legacy"]["rol"] == "admin"


def test_legajo_registra_operador(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "SALIDAS_DIR", tmp_path)
    client = _client(monkeypatch, "ana:clave1:impuestos")

    r = client.post("/api/validar", json={"cuits": ["30500010912"]}, headers=_auth("ana", "clave1"))

    assert r.status_code == 200
    legajo_id = r.json()["legajo_id"]
    legajo = client.get(f"/api/legajos/{legajo_id}", headers=_auth("ana", "clave1")).json()
    assert legajo["operador"] == {"usuario": "ana", "rol": "impuestos"}
    assert legajo["integridad"]["valido"] is True

    listado = client.get("/api/legajos", headers=_auth("ana", "clave1")).json()["legajos"]
    assert listado[0]["operador"] == "ana"
