import json
from pathlib import Path

import pytest

from app.modules import portal_automation


def test_carga_adapters_y_cubre_flujos_clave():
    data = portal_automation.cargar_adapters()
    adapters = {a["id"]: a for a in data["adapters"]}

    assert "jujuy_iibb_padron_publico" in adapters
    assert "agip_caba_regimenes_generales_publico" in adapters
    assert "arba_iibb_padron_autenticado" in adapters
    assert "rionegro_iibb_captcha_asistido" in adapters
    assert adapters["jujuy_iibb_padron_publico"]["tipo"] == "public_download"
    assert adapters["arba_iibb_padron_autenticado"]["requiere_login"] is True


def test_plan_renderiza_variables_sin_instalar_playwright():
    plan = portal_automation.ejecutar_adapter(
        "jujuy_iibb_padron_publico",
        {"periodo": "2026-06"},
        dry_run=True,
    )

    assert plan["ejecutable"] is True
    assert plan["acciones"][2]["value"] == "2026/06"
    assert plan["acciones"][3]["filename"] == "jujuy_padron_iibb_2026-06.xlsx"


def test_bloquea_adapters_autenticados_sin_autorizacion():
    plan = portal_automation.ejecutar_adapter(
        "arba_iibb_padron_autenticado",
        {"periodo": "2026-06"},
        dry_run=True,
    )

    assert plan["ejecutable"] is False
    assert "autorización" in plan["razon"]


def test_bloquea_captcha_por_defecto():
    plan = portal_automation.ejecutar_adapter(
        "rionegro_iibb_captcha_asistido",
        {"cuit": "30500010912"},
        dry_run=True,
    )

    assert plan["ejecutable"] is False
    assert "CAPTCHA" in plan["razon"]


def test_valida_variables_requeridas():
    with pytest.raises(portal_automation.PortalAutomationError, match="Faltan variables"):
        portal_automation.plan_ejecucion("agip_caba_regimenes_generales_publico", {"periodo": "2026-06"})


def test_sha256(tmp_path: Path):
    f = tmp_path / "archivo.txt"
    f.write_text("demo", encoding="utf-8")

    assert portal_automation._sha256(f) == "2a97516c354b68848cdbd8f54a226a0a55b21ed138e207ad6c5cbb9c00aa5aea"


def test_adapters_tienen_evidencia_y_politica():
    data = json.loads(Path("config/portal_adapters.json").read_text(encoding="utf-8"))

    for adapter in data["adapters"]:
        assert adapter["url"].startswith("https://")
        assert adapter["tipo"] in {"public_download", "public_query", "authenticated_download", "captcha_blocked"}
        assert isinstance(adapter["evidencia"], list) and adapter["evidencia"]
        assert "nota" in adapter
