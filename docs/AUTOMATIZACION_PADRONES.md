# Plan de automatización de padrones y fuentes fiscales

## Objetivo

Mantener actualizado el universo de fuentes que una empresa mediana/grande necesita para operar como agente de retención, percepción e información en Argentina, con trazabilidad suficiente para auditoría interna y soporte ante reclamos.

## Sprint 1 implementado

- Catálogo versionado de fuentes en `config/fuentes_catalogo.json`.
- Evaluador operativo en `app/modules/fuentes_catalogo.py`.
- API `GET /api/fuentes`.
- Monitor web `/fuentes`.
- Script scheduler-friendly `scripts/revisar_fuentes.py`.

## Clasificación operativa

| Clase | Ejemplo | Automatización objetivo |
| --- | --- | --- |
| `api_oficial` | ARCA constancia | Consulta online por alta/revalidación |
| `padron_descargable` | ARBA, AGIP, ATER, Córdoba, Santa Fe | Descarga mensual + importador + manifiesto |
| `consulta_online` | Neuquén, Misiones | Consulta por CUIT con evidencia |
| `portal_captcha` | Río Negro | Cola asistida + captura |
| `portal_credenciales` | Corrientes | Credenciales cliente o exportación controlada |

## Cadencia mínima

- **ARCA inscripción:** en cada alta y revalidación.
- **Padrones mensuales provinciales:** revisión diaria de estado y carga mensual del período vigente.
- **Fuentes sin archivo mensual:** consulta por CUIT en altas nuevas y revalidación periódica por riesgo.
- **Fuentes con CAPTCHA o credenciales:** workflow asistido con responsable, evidencia y vencimiento.

## Próximos desarrollos

1. Automatizar descarga ARBA/AGIP/ATER donde exista archivo público estable.
2. Incorporar historial de ejecuciones de jobs y evidencias descargadas.
3. Crear cola `/fuentes-pendientes` para consultas asistidas de Misiones/Río Negro/Corrientes.
4. Persistir resultados en base de datos multiempresa.
5. Agregar alertas por mail/Slack/Teams cuando una fuente crítica esté vencida o sin carga.
