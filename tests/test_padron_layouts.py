from app.modules import padron_layouts


def test_catalogo_declara_campos_canonicos_y_layouts():
    catalog = padron_layouts.cargar_catalogo()

    assert catalog["version"] == 1
    assert "cuit" in catalog["canonical_fields"]
    ids = {layout["id"] for layout in catalog["layouts"]}
    assert "agip_caba_regimenes_generales_v1" in ids
    assert "cabeceras_alias_iibb_v1" in ids


def test_traducir_linea_agip_a_canonico():
    layout = padron_layouts.obtener_layout("agip_caba_regimenes_generales_v1")

    row = padron_layouts.traducir_linea_delimitada(
        "01062026;01072026;31072026;30711111118;C;S;N;3,50;2,00;00;00;ACME SA",
        layout,
    )

    assert row == {
        "cuit": "30711111118",
        "alicuota_retencion": "2.00",
        "alicuota_percepcion": "3.50",
        "vigencia_desde": "01/07/2026",
        "vigencia_hasta": "31/07/2026",
        "regimen": "AGIP Regímenes Generales · Convenio",
        "jurisdiccion": "CABA",
        "tipo_padron": "iibb_retencion_percepcion",
        "fuente_id": "agip_caba_iibb",
        "layout_id": "agip_caba_regimenes_generales_v1",
    }


def test_traducir_linea_agip_rechaza_cuit_invalido():
    layout = padron_layouts.obtener_layout("agip_caba_regimenes_generales_v1")

    assert padron_layouts.traducir_linea_delimitada(
        "01062026;01072026;31072026;sin-cuit;C;S;N;3,50;2,00;00;00;ACME SA",
        layout,
    ) is None


def test_layouts_para_padron_incluye_especifico_y_genericos():
    ids = {layout["id"] for layout in padron_layouts.layouts_para_padron("CABA")}

    assert "agip_caba_regimenes_generales_v1" in ids
    assert "cabeceras_alias_iibb_v1" in ids
    assert "delimitado_sin_cabecera_generico_v1" in ids
