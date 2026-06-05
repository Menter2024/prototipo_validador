import zipfile
from pathlib import Path

from scripts.generar_golden_cases_reales import generar_golden_cases, render_markdown


def test_golden_cases_filtra_empresas_y_detecta_overlap(tmp_path):
    cordoba = tmp_path / "cordoba.txt"
    cordoba.write_text(
        "R;22052026;01062026;30062026;30722222229;C;X;N;02,75\n"
        "R;22052026;01062026;30062026;20111111112;C;X;N;02,75\n",
        encoding="utf-8",
    )
    formosa = tmp_path / "formosa.csv"
    formosa.write_text(
        "30722222229;ACME SA;202606;B;ALTO RIESGO FISCAL;2.50;2.25;;;2.25;1.500;;;CONVENIO MULTILATERAL;NO\n"
        "33733333339;OTRA SA;202606;B;ALTO RIESGO FISCAL;2.50;2.25;;;2.25;1.500;;;REGIMEN GENERAL;NO\n",
        encoding="utf-8",
    )
    tucuman = tmp_path / "tucuman.zip"
    with zipfile.ZipFile(tucuman, "w") as zf:
        zf.writestr(
            "ACREDITAN.TXT",
            "CUIT                DESDE     HASTA     DENOMINACION   PORCENTAJE\n"
            "30722222229     CM  20260601  20260630  ACME SA        5\n",
        )

    data = generar_golden_cases(
        [
            {"id": "cordoba", "provincia": "Cordoba", "path": str(cordoba)},
            {"id": "formosa", "provincia": "Formosa", "path": str(formosa)},
            {"id": "tucuman", "provincia": "Tucuman", "path": str(tucuman)},
        ],
        per_source=5,
        min_overlap=2,
    )

    assert data["overlaps"][0]["cuit"] == "30722222229"
    assert data["overlaps"][0]["cantidad_padrones"] == 3
    assert all(not item["cuit"].startswith("20") for rows in data["por_padron"].values() for item in rows)
    markdown = render_markdown(data)
    assert "Golden cases reales" in markdown
    assert "30722222229" in markdown
