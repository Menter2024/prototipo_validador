from app.modules import descarga_fuentes


def test_candidate_links_filtra_por_texto_y_extension():
    html = """
    <a href="/padrones/diseno.xls">Diseño</a>
    <a href="/padrones/padron-vigente.rar">Padrón de Regímenes Generales - Vigencia 01/06/2026</a>
    <a href="/padrones/historico.zip">Padrón de Regímenes Generales - Histórico</a>
    """
    cfg = {
        "link_text_regex": "Padrón de Regímenes Generales - Vigencia",
        "extensiones": [".zip", ".txt", ".rar"],
    }

    candidates = descarga_fuentes._candidate_links(html, "https://www.agip.gob.ar/base", cfg)

    assert candidates == [{
        "url": "https://www.agip.gob.ar/padrones/padron-vigente.rar",
        "text": "Padrón de Regímenes Generales - Vigencia 01/06/2026",
        "extension": ".rar",
    }]


def test_plan_descarga_reconoce_credenciales_arba():
    plan = descarga_fuentes.plan_descarga("arba_iibb")

    assert plan["status"] == "requiere_credenciales"
    assert plan["descargable"] is False
