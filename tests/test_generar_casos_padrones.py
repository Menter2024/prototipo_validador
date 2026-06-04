import csv

from scripts.generar_casos_padrones import generar_casos


def _csv(path, cuits):
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["cuit", "alicuota_retencion", "alicuota_percepcion"])
        writer.writeheader()
        for cuit in cuits:
            writer.writerow({"cuit": cuit, "alicuota_retencion": "1.00", "alicuota_percepcion": "2.00"})


def test_generar_casos_detecta_muestras_y_overlaps(tmp_path):
    padrones_dir = tmp_path / "padrones"
    padrones_dir.mkdir()
    _csv(padrones_dir / "PadronCABA.csv", ["30718869966", "30500000001", "30500000002"])
    _csv(padrones_dir / "PadronARBA.csv", ["30718869966", "30600000001"])

    data = generar_casos(padrones_dir, por_padron=2, min_overlap=2)

    assert data["por_padron"]["CABA"] == ["30718869966", "30500000001"]
    assert data["por_padron"]["ARBA"] == ["30718869966", "30600000001"]
    assert data["overlaps"][0]["cuit"] == "30718869966"
    assert data["overlaps"][0]["padrones"] == ["ARBA", "CABA"]
