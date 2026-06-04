# Catálogo de layouts de padrones

El procesamiento de padrones se trata como ETL fiscal por fuente, no como importación genérica de CSV.

## Objetivo

Para cada fuente se debe documentar:

- organismo y jurisdicción;
- tipo de padrón;
- formato físico;
- campos originales;
- traducción a campos canónicos;
- validaciones mínimas;
- casos reales de prueba.

## Campos canónicos iniciales

| Campo | Uso |
|---|---|
| `cuit` | clave principal de lookup |
| `alicuota_retencion` | alícuota aplicable como agente de retención |
| `alicuota_percepcion` | alícuota aplicable como agente de percepción |
| `vigencia_desde` | inicio de vigencia |
| `vigencia_hasta` | fin de vigencia |
| `regimen` | descripción del régimen/categoría |
| `jurisdiccion` | provincia/ámbito |
| `tipo_padron` | retención, percepción, exclusión, riesgo, etc. |
| `fuente_id` | vínculo con catálogo de fuentes |
| `layout_id` | contrato de parsing usado |

## Archivo de configuración

`config/padron_layouts.json`

Cada layout define el contrato de traducción. Ejemplo:

```json
{
  "id": "agip_caba_regimenes_generales_v1",
  "formato": "txt_delimitado_sin_header",
  "separador": ";",
  "campos": {
    "cuit": {"posicion": 3, "tipo": "cuit"},
    "alicuota_percepcion": {"posicion": 7, "tipo": "porcentaje_agip"},
    "alicuota_retencion": {"posicion": 8, "tipo": "porcentaje_agip"}
  }
}
```

## Evolución prevista

1. Cargar layouts prioritarios: AGIP, ARBA, ATER, Córdoba, Santa Fe, COMARB/SIRCREB/SIRCIP.
2. Asociar cada `fuente_id` con su `layout_id`.
3. Agregar fixtures de cada formato.
4. Generar golden sets reales por padrón.
5. Ejecutar Cloud Run Job usando layouts antes de fallback heurístico.

