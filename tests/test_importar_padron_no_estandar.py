import subprocess
import json
from pathlib import Path

import pytest

from scripts import importar_padron as imp

FIXTURES = Path(__file__).parent / "fixtures" / "padrones_no_estandar"


def _read_csv(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_agip_rar_extrae_txt_y_parsea_layout_oficial(monkeypatch, tmp_path):
    origen = tmp_path / "agip_vigente.rar"
    origen.write_bytes(b"RAR placeholder")
    out_dir = tmp_path / "padrones"

    def fake_which(name):
        return "/usr/bin/unar" if name == "unar" else None

    def fake_run(cmd, check, capture_output, text):
        dest = Path(cmd[cmd.index("-output-directory") + 1])
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "Padron_Regimenes_Generales.txt").write_text(
            "01062026;01072026;31072026;30711111118;C;S;N;3,50;2,00;00;00;ACME SA\n",
            encoding="latin-1",
        )
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(imp.shutil, "which", fake_which)
    monkeypatch.setattr(imp.subprocess, "run", fake_run)

    res = imp.importar_padron("AGIP", origen, out_dir, backup=False)

    assert res["provincia"] == "CABA"
    assert res["registros"] == 1
    assert res["muestra"][0] == {
        "cuit": "30711111118",
        "alicuota_retencion": "2.00",
        "alicuota_percepcion": "3.50",
        "vigencia_desde": "01/07/2026",
        "vigencia_hasta": "31/07/2026",
        "regimen": "AGIP Regímenes Generales · Convenio",
    }
    assert "30711111118,2.00,3.50,01/07/2026,31/07/2026" in _read_csv(out_dir / "PadronCABA.csv")


def test_agip_rar_sin_extractor_informa_accion(monkeypatch, tmp_path):
    origen = tmp_path / "agip_vigente.rar"
    origen.write_bytes(b"RAR placeholder")
    monkeypatch.setattr(imp.shutil, "which", lambda _name: None)

    with pytest.raises(RuntimeError, match="RAR.*unar.*7z.*unrar"):
        imp.importar_padron("AGIP", origen, tmp_path / "padrones", backup=False)


def test_cordoba_zip_headerless_delimitado(tmp_path):
    origen = tmp_path / "cordoba.zip"
    origen.write_bytes((FIXTURES / "cordoba_headerless.zip").read_bytes())

    res = imp.importar_padron("Cordoba", origen, tmp_path / "padrones", backup=False)

    assert res["registros"] == 1
    assert res["muestra"][0]["alicuota_retencion"] == "1.50"
    assert res["muestra"][0]["alicuota_percepcion"] == "2.50"


def test_zip_con_ruta_fuera_de_destino_es_rechazado(tmp_path):
    origen = tmp_path / "cordoba.zip"
    origen.write_bytes((FIXTURES / "zip_path_traversal.zip").read_bytes())

    with pytest.raises(RuntimeError, match="ZIP inválido"):
        imp.importar_padron("Cordoba", origen, tmp_path / "padrones", backup=False)


def test_jujuy_xlsx_cabeceras_no_estandar(tmp_path):
    origen = tmp_path / "jujuy.xlsx"
    origen.write_bytes((FIXTURES / "jujuy_layout.xlsx").read_bytes())

    res = imp.importar_padron("Jujuy", origen, tmp_path / "padrones", backup=False)

    assert res["muestra"][0] == {
        "cuit": "30733333330",
        "alicuota_retencion": "0.75",
        "alicuota_percepcion": "1.25",
        "vigencia_desde": "01/06/2026",
        "vigencia_hasta": "30/06/2026",
        "regimen": "General",
    }


def test_tucuman_csv_abreviaturas(tmp_path):
    origen = tmp_path / "tucuman.csv"
    origen.write_text((FIXTURES / "tucuman_abreviado.csv").read_text(encoding="utf-8"), encoding="utf-8")

    res = imp.importar_padron("Tucuman", origen, tmp_path / "padrones", backup=False)

    assert res["muestra"][0]["cuit"] == "30744444441"
    assert res["muestra"][0]["alicuota_retencion"] == "2.00"
    assert res["muestra"][0]["alicuota_percepcion"] == "3.00"
    assert res["calidad"]["perfil"] == "Tucumán · RG 23/02"


def test_preview_no_escribe_y_reporta_calidad(tmp_path):
    origen = tmp_path / "tucuman.csv"
    origen.write_text(
        "CUIT;Alic. Ret.;Alic. Perc.;Vig. Desde;Vig. Hasta;Regimen\n"
        "30-74444444-1;2,00;3,00;01/06/2026;30/06/2026;RG 23/02\n"
        "30-74444444-1;2,00;3,00;01/06/2026;30/06/2026;Duplicado\n"
        "sin-cuit;2,00;3,00;mal;30/06/2026;Roto\n",
        encoding="utf-8",
    )

    res = imp.importar_padron("Tucuman", origen, tmp_path / "padrones", dry_run=True, backup=False)

    assert res["dry_run"] is True
    assert res["registros"] == 1
    assert res["calidad"]["raw_registros"] == 3
    assert res["calidad"]["duplicados"] == 1
    assert res["calidad"]["descartados_cuit_invalido"] == 1
    assert res["calidad"]["estado"] == "observado"
    assert not (tmp_path / "padrones" / "PadronTucuman.csv").exists()


def test_import_observado_requiere_confirmacion_explicita(tmp_path):
    origen = tmp_path / "tucuman.csv"
    origen.write_text(
        "CUIT;Alic. Ret.;Alic. Perc.;Vig. Desde;Vig. Hasta;Regimen\n"
        "30-74444444-1;2,00;3,00;01/06/2026;30/06/2026;RG 23/02\n"
        "30-74444444-1;2,00;3,00;01/06/2026;30/06/2026;Duplicado\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "padrones"

    with pytest.raises(RuntimeError, match="confirmá explícitamente"):
        imp.importar_padron("Tucuman", origen, out_dir, backup=False, aceptar_observado=False)

    res = imp.importar_padron("Tucuman", origen, out_dir, backup=False, aceptar_observado=True)

    assert res["calidad"]["estado"] == "observado"
    assert (out_dir / "PadronTucuman.csv").exists()


def test_importar_guarda_manifest_con_hash_y_calidad(tmp_path):
    origen = tmp_path / "tucuman.csv"
    origen.write_text(
        "CUIT;Alic. Ret.;Alic. Perc.;Vig. Desde;Vig. Hasta;Regimen\n"
        "30-74444444-1;2,00;3,00;01/06/2026;30/06/2026;RG 23/02\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "padrones"

    res = imp.importar_padron("Tucuman", origen, out_dir, periodo="2026-06", vigencia_hasta="2026-06-30", backup=False)
    manifest = json.loads((out_dir / "padrones_manifest.json").read_text(encoding="utf-8"))
    item = manifest["padrones"]["Tucuman"]

    assert res["evidencia"]["sha256"] == item["sha256"]
    assert item["archivo_original"] == "tucuman.csv"
    assert item["tipo_archivo"] == ".csv"
    assert item["calidad"]["estado"] == "aprobado"
    assert item["periodo"] == "2026-06"
