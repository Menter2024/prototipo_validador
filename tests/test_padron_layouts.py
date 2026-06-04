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



def test_traducir_row_arba_con_cabeceras_canonicas():
    layout = padron_layouts.obtener_layout("arba_iibb_sujeto_csv_v1")

    row = padron_layouts.traducir_row_con_cabeceras(
        {
            "cuit": "30-50001091-2",
            "alicuota_retencion": "2,00",
            "alicuota_percepcion": "3.00%",
            "vigencia_desde": "2026-05-01",
            "vigencia_hasta": "2026-05-31",
        },
        layout,
    )

    assert row["cuit"] == "30500010912"
    assert row["alicuota_retencion"] == "2.00"
    assert row["alicuota_percepcion"] == "3.00"
    assert row["vigencia_desde"] == "01/05/2026"
    assert row["vigencia_hasta"] == "31/05/2026"
    assert row["regimen"] == "ARBA Régimen por sujeto"
    assert row["layout_id"] == "arba_iibb_sujeto_csv_v1"


def test_traducir_row_ater_con_muestra_local_normalizada():
    layout = padron_layouts.obtener_layout("ater_entrerios_iibb_csv_v1")

    row = padron_layouts.traducir_row_con_cabeceras(
        {
            "cuit": "20000033481",
            "alicuota_retencion": "3.00",
            "alicuota_percepcion": "3.00",
            "vigencia_desde": "2026-05-01",
            "vigencia_hasta": "2026-05-31",
            "regimen": "",
        },
        layout,
    )

    assert row["cuit"] == "20000033481"
    assert row["vigencia_desde"] == "01/05/2026"
    assert row["regimen"] == "ATER IIBB retención/percepción"
    assert row["layout_id"] == "ater_entrerios_iibb_csv_v1"


def test_layout_santafe_queda_marcado_pendiente_muestra_real():
    layout = padron_layouts.obtener_layout("santafe_iibb_csv_v1")

    assert layout["estado"] == "pendiente_muestra_real"



def test_traducir_linea_cordoba_delimitado_sin_cabecera():
    layout = padron_layouts.obtener_layout("cordoba_iibb_delimitado_v1")

    row = padron_layouts.traducir_linea_delimitada(
        "30722222229;CORDOBA SA;1,50;2,50;01/06/2026;30/06/2026",
        layout,
    )

    assert row["cuit"] == "30722222229"
    assert row["alicuota_retencion"] == "1.50"
    assert row["alicuota_percepcion"] == "2.50"
    assert row["vigencia_desde"] == "01/06/2026"
    assert row["regimen"] == "Córdoba IIBB retención/percepción"
    assert row["layout_id"] == "cordoba_iibb_delimitado_v1"


def test_layouts_p1_quedan_pendientes_de_muestra_real():
    for layout_id in [
        "cordoba_iibb_delimitado_v1",
        "jujuy_iibb_xlsx_alias_v1",
        "mendoza_iibb_csv_alias_v1",
        "tucuman_iibb_rg23_csv_v1",
    ]:
        assert padron_layouts.obtener_layout(layout_id)["estado"] == "pendiente_muestra_real"
