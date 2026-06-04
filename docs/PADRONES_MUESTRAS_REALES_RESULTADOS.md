# Resultados de validación de muestras reales de padrones

Actualizado: 2026-06-04.

Resumen sanitizado: no incluye padrones completos ni filas de muestra; los reportes JSON completos quedan fuera de Git en `/private/tmp/padrones_reales/reportes/`.

| Fuente | Archivo | Layout detectado | OK | Registros | Calidad | Advertencias | SHA-256 | Tamaño bytes |
|---|---|---|---|---:|---|---|---|---:|
| SantaFe | Sta Fe_PARP_202606.csv | `santafe_iibb_parp_delimitado_v1` | sí | 593359 | aprobado | — | 6e5f60b46ccaf544b92b183bed088bc10a2face245e1d08829c3dc50b215d136 | 69203024 |
| Cordoba | Cordoba Ret.txt | `cordoba_iibb_delimitado_v1` | sí | 782592 | aprobado | — | 300629c18f4444c0957a40dc805892e84910710fd3e317d4fe29f7880d74dab1 | 42259968 |
| Jujuy | Jujuy PADRONRETPER202606.txt | `jujuy_iibb_xlsx_alias_v1` | sí | 106319 | aprobado | — | e25cd6519cec0c5fd4b3f61f9b672b3a849fe005a0dfb9bdb21cca8d30770ca2 | 3189780 |
| Mendoza | Mendoza Ret_ib_2026_06_01.txt.gz | `mendoza_iibb_retib_delimitado_v1` | sí | 143567 | observado | 185158 CUITs duplicados descartados. | 959e5913857234e1d3652bd801ac8ba4852f9a2b6348f4fa6b2e44a4143bdfef | 2692125 |
| Tucumán padrón | Tucum_padroncontribuyente_2606_270520260921 (1).zip | `tucuman_padron_contribuyente_txt_v1` | sí | 76900 | aprobado | — | 792738d0039a0f8d5a37a44dc31bf076dd049d69d30d38d790b8a4b7a8b171ad | 1559964 |
| Tucumán coeficiente | Tucum_Coefic.zip | `tucuman_coef_rg116_txt_v1` | sí | 47095 | aprobado | — | f560cfbbc9640c1659d9986fdf59e7288ff7a1db2e5f4f63e950fcc26971336c | 983996 |

## Decisiones

- Santa Fe, Córdoba, Jujuy y Tucumán validaron sin advertencias.
- Mendoza validó con observación esperada: el archivo trae múltiples filas por CUIT/actividad; el importador conserva un registro por CUIT y reporta duplicados descartados.
- Los layouts correspondientes fueron marcados como `validado_muestra_oficial` o `validado_muestra_oficial_con_observaciones` en `config/padron_layouts.json`.

## Reportes fuera de Git

```text
/private/tmp/padrones_reales/reportes/santafe.json
/private/tmp/padrones_reales/reportes/cordoba.json
/private/tmp/padrones_reales/reportes/jujuy.json
/private/tmp/padrones_reales/reportes/mendoza.json
/private/tmp/padrones_reales/reportes/tucuman_padron.json
/private/tmp/padrones_reales/reportes/tucuman_coef.json
```
