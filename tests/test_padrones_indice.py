"""Tests del índice de padrones por CUIT y su cache multi-archivo."""
from app.modules import padrones


def _crear_padron(path, filas: list[str]) -> None:
    path.write_text("cuit;retencion;percepcion;desde;hasta;regimen\n" + "\n".join(filas), encoding="utf-8")


def test_busqueda_por_indice_encuentra_y_normaliza(tmp_path):
    archivo = tmp_path / "PadronARBA.csv"
    _crear_padron(archivo, ["30-50577985-8;1,50;0,75;2026-01-01;2026-12-31;General"])

    res = padrones.buscar_en_padron("30505779858", archivo)

    assert res["encontrado"] is True
    assert res["alicuota_retencion"] == "1.50"
    assert res["alicuota_percepcion"] == "0.75"

    assert padrones.buscar_en_padron("30500010912", archivo) == {"encontrado": False}


def test_cuit_duplicado_conserva_primera_aparicion(tmp_path):
    archivo = tmp_path / "PadronCABA.csv"
    _crear_padron(archivo, [
        "30505779858;1,00;0,50;2026-01-01;2026-12-31;Primero",
        "30505779858;9,99;9,99;2026-01-01;2026-12-31;Segundo",
    ])

    res = padrones.buscar_en_padron("30505779858", archivo)

    assert res["regimen"] == "Primero"


def test_cache_conserva_varios_padrones_a_la_vez(tmp_path, monkeypatch):
    """Regresión: el cache tenía capacidad 1 y re-parseaba al alternar padrones."""
    a = tmp_path / "PadronARBA.csv"
    b = tmp_path / "PadronCABA.csv"
    _crear_padron(a, ["30505779858;1,00;0,50;;;A"])
    _crear_padron(b, ["30505779858;2,00;0,75;;;B"])

    lecturas = {"n": 0}
    original = padrones._leer_texto

    def contador(archivo):
        lecturas["n"] += 1
        return original(archivo)

    monkeypatch.setattr(padrones, "_leer_texto", contador)
    padrones._INDEX_CACHE.clear()

    for _ in range(3):
        padrones.buscar_en_padron("30505779858", a)
        padrones.buscar_en_padron("30505779858", b)

    assert lecturas["n"] == 2, "cada padrón debe parsearse una sola vez"


def test_cache_respeta_limite_configurado(tmp_path, monkeypatch):
    monkeypatch.setenv("PADRONES_CACHE_MAX", "2")
    padrones._INDEX_CACHE.clear()
    archivos = []
    for i in range(3):
        p = tmp_path / f"Padron{i}.csv"
        _crear_padron(p, [f"3050577985{i};1,00;0,50;;;X"])
        archivos.append(p)

    for p in archivos:
        padrones.buscar_en_padron("30505779858", p)

    assert len(padrones._INDEX_CACHE) == 2
