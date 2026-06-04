# Validación de muestras reales oficiales de padrones

Actualizado: 2026-06-04.

Este procedimiento valida archivos reales descargados desde fuentes oficiales sin sobrescribir los padrones locales del repo. Sirve para validar o revalidar layouts con evidencia oficial reproducible.

## Fuentes recibidas y validadas

| Jurisdicción | Fuente | Layout esperado | Fuente oficial / acceso | Estado |
|---|---|---|---|---|
| Santa Fe | API Santa Fe | `santafe_iibb_parp_delimitado_v1` | https://www.santafe.gob.ar/index.php/web/content/view/full/221362/(subtema)/102284 | validado con muestra real recibida |
| Córdoba | Rentas Córdoba | `cordoba_iibb_delimitado_v1` | https://www.rentascordoba.gob.ar/cms/ms-agentes/ | validado con muestra real recibida |
| Jujuy | DPR Jujuy | `jujuy_iibb_xlsx_alias_v1` | https://rentasjujuy.gob.ar/agentes-ingresos-brutos/ | validado con muestra real recibida |
| Mendoza | ATM Mendoza | `mendoza_iibb_retib_delimitado_v1` | https://www.atm.mendoza.gov.ar/ | validado con muestra real recibida |
| Tucumán | DGR Tucumán | `tucuman_padron_contribuyente_txt_v1` / `tucuman_coef_rg116_txt_v1` | https://www.rentastucuman.gob.ar/ | validado con muestra real recibida |

## Relevamiento público inicial

- Santa Fe publica el régimen PARP y describe que el padrón de alícuotas de retención/percepción asigna alícuotas a sujetos IIBB; también existe trámite/servicio de descarga de padrones para agentes.
- Córdoba publica sección de agentes con descarga de listados, consulta de alícuotas y padrón de agentes.
- Jujuy publica sección de agentes IIBB con instructivo ARPIB y padrón con alícuotas de retención/percepción RG 1510/2018.
- Mendoza publica información SIRCAR/ATM; el relevamiento público menciona agentes de retención/percepción y padrón de riesgo fiscal, pero el archivo masivo requiere confirmación operativa.
- Tucumán publica padrones y nóminas, incluyendo agentes de retención RG 23/02 y agentes de percepción RG 86/00.

## Qué archivo necesito para cerrar la validación

Para cada jurisdicción, descargar desde el portal oficial el archivo vigente de padrón/listado/alícuotas para agentes de retención/percepción de Ingresos Brutos. Guardarlo fuera de Git, por ejemplo en `/private/tmp/padrones_reales/`.

No subir a Git padrones completos reales. El reporte conserva hash, tamaño, layout detectado y primeras filas normalizadas.

## Comando de validación

```bash
.venv/bin/python3.13 scripts/validar_muestra_padron.py SantaFe /private/tmp/padrones_reales/santafe_padron.xlsx --output /private/tmp/padrones_reales/reportes/santafe.json
.venv/bin/python3.13 scripts/validar_muestra_padron.py Cordoba /private/tmp/padrones_reales/cordoba_padron.zip --output /private/tmp/padrones_reales/reportes/cordoba.json
.venv/bin/python3.13 scripts/validar_muestra_padron.py Jujuy /private/tmp/padrones_reales/jujuy_padron.xlsx --output /private/tmp/padrones_reales/reportes/jujuy.json
.venv/bin/python3.13 scripts/validar_muestra_padron.py Mendoza /private/tmp/padrones_reales/mendoza_padron.txt.gz --output /private/tmp/padrones_reales/reportes/mendoza.json
.venv/bin/python3.13 scripts/validar_muestra_padron.py Tucuman /private/tmp/padrones_reales/tucuman_padron.csv --output /private/tmp/padrones_reales/reportes/tucuman.json
.venv/bin/python3.13 scripts/validar_muestra_padron.py Tucuman /private/tmp/padrones_reales/tucuman_coef.zip --expected-layout tucuman_coef_rg116_txt_v1 --output /private/tmp/padrones_reales/reportes/tucuman_coef.json
```

## Criterio para aprobar una muestra

- `ok: true` en el reporte.
- `layout_detectado` igual al layout esperado.
- `registros` mayor a cero y razonable contra el período publicado.
- `sha256` calculado y guardado.
- Sin errores de calidad; advertencias revisadas y justificadas.
- URL oficial, fecha de descarga, período/vigencia y usuario/medio de obtención registrados en evidencia operativa.

## Qué hacer si falla

- Si el layout detectado es genérico o distinto: relevar cabeceras/columnas reales y crear `layout_id` nuevo versionado.
- Si hay CUITs inválidos masivos: revisar codificación, separador, hoja XLSX o archivo interno del ZIP/RAR.
- Si faltan alícuotas/vigencia: confirmar si el padrón oficial publica esos campos o si se deben derivar de otra fuente normativa.
- Si el portal exige credenciales/CAPTCHA: usar cola asistida; no automatizar bypass.

## Próximo paso después de aprobar una nueva muestra

1. Cambiar `estado` del layout en `config/padron_layouts.json` de `pendiente_muestra_real` a `validado_muestra_oficial`.
2. Guardar reporte JSON sanitizado o resumen de evidencia en documentación, sin padrón completo.
3. Regenerar backlog:

```bash
.venv/bin/python3.13 scripts/auditar_formatos_padrones.py --format markdown --output docs/PADRONES_FORMATOS_BACKLOG.md
```

4. Ejecutar tests y commit.
